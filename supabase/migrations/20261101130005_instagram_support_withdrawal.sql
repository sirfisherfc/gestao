-- Cancelamento de uma mensagem pelo remetente. Instala em OFF.
begin;
set local lock_timeout='2s';
alter table instagram_support.events add column if not exists withdrawn_at timestamptz;
alter table instagram_support.events add column if not exists routing_reason text check(routing_reason is null or length(routing_reason)<=80);
alter table instagram_support.events add column if not exists case_id uuid references instagram_support.cases(id) on delete set null;
alter table instagram_support.cases add column if not exists notice_attempted boolean not null default false;
alter table instagram_support.events drop constraint if exists events_kind_check;
alter table instagram_support.events add constraint events_kind_check check(kind in ('incoming','echo','withdrawal'));
alter table instagram_support.outbox drop constraint if exists outbox_text_check;
alter table instagram_support.outbox add constraint outbox_text_check check(length(text)<=700);
create index if not exists ig_support_events_case_source_idx on instagram_support.events(case_id) where case_id is not null;
grant select,insert,update,delete on instagram_support.events to service_role;
grant select,update on instagram_support.cases,instagram_support.outbox to service_role;
update instagram_support.cases c set notice_attempted=true
  where not notice_attempted and exists(select 1 from instagram_support.outbox o where o.event_id=c.handoff_notice_event_id);
update instagram_support.settings set mode='off',paused=true,model_usage_allowed=false,billing_verified=false,
  manager_auth_user_id=null,alerts_enabled=false,cron_enabled=false,updated_at=now() where singleton;
do $cron$ declare j bigint;begin
  select jobid into j from cron.job where jobname='sirfisher-instagram-support-drain' and username=current_user;
  if j is not null then perform cron.alter_job(j,active:=false);end if;
end $cron$;

create or replace function instagram_support.withdraw_message(p_event jsonb)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,pg_temp
as $function$
declare
 s instagram_support.settings%rowtype;t instagram_support.threads%rowtype;e instagram_support.events%rowtype;
 n instagram_support.events%rowtype;c instagram_support.cases%rowtype;r instagram_support.events%rowtype;
 v_sender text:=p_event->>'sender_id';v_mid text:=p_event->>'mid';v_at timestamptz;
 v_out boolean;v_notice_active boolean;v_queued boolean:=false;v_id uuid;v_version bigint;v_case_reason text;
begin
 select * into strict s from instagram_support.settings where singleton for share;
 if v_sender is null or v_sender!~'^[0-9]{5,30}$' or v_mid is null or length(v_mid) not between 1 and 512
   or p_event->>'recipient_id' is distinct from s.ig_user_id or coalesce(p_event->>'timestamp_ms','')!~'^[0-9]{10,16}$'
   then raise exception using errcode='22023',message='Cancelamento Instagram invalido.';end if;
 v_at:=to_timestamp((p_event->>'timestamp_ms')::numeric/1000);
 if v_at>now()+interval '5 minutes' then return jsonb_build_object('status','ignored','queued',false);end if;
 perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_sender,0));
 insert into instagram_support.threads(sender_id) values(v_sender) on conflict(sender_id) do nothing;
 select * into strict t from instagram_support.threads where sender_id=v_sender for update;
 select * into e from instagram_support.events where mid=v_mid for update;
 if found then
   if e.thread_id<>t.id or e.kind='echo' then return jsonb_build_object('status','ignored','reason','mid_sender_mismatch','queued',false);end if;
   if e.withdrawn_at is not null then return jsonb_build_object('status','withdrawn_duplicate','queued',false);end if;
 else
   insert into instagram_support.events(mid,thread_id,kind,text,message_at,mode_at_ingest,status,reason,withdrawn_at)
     values(v_mid,t.id,'withdrawal','',v_at,s.mode,'ignored','message_withdrawn',now()) returning id into v_id;
   return jsonb_build_object('status','withdrawn','queued',false);
 end if;
 -- Captura o aviso antes de retirar a elegibilidade do evento cancelado.
 for c in select * from instagram_support.cases where thread_id=t.id
   and (id=e.case_id or event_id=e.id or handoff_notice_event_id=e.id) for update loop
   select * into n from instagram_support.events where id=c.handoff_notice_event_id for update;
   v_notice_active:=found and n.allow_handoff_ack and n.status in ('pending','completed') and not c.notice_attempted
     and not exists(select 1 from instagram_support.outbox o where o.event_id=n.id)
     and not exists(select 1 from instagram_support.outbox o join instagram_support.events x on x.id=o.event_id where x.case_id=c.id);
   select * into r from instagram_support.events where case_id=c.id and id<>e.id and withdrawn_at is null and routing_reason is not null
     order by instagram_support.handoff_priority(routing_reason) desc,received_at desc,id limit 1;
   if found then
     v_case_reason:=r.routing_reason;
     update instagram_support.cases set reason=r.routing_reason,summary='Pedido remanescente requer atendimento humano.',event_id=r.id,updated_at=now() where id=c.id;
   else
     v_case_reason:=case when c.assigned_to is not null then 'human_assumed' else 'message_withdrawn' end;
     update instagram_support.cases set reason=case when assigned_to is not null then 'human_assumed' else 'message_withdrawn' end,
       summary=case when assigned_to is not null then 'Atendimento humano em andamento.' else '' end,event_id=null,updated_at=now() where id=c.id;
   end if;
   -- Retira os rotulos derivados da fonte sem desfazer controle humano ou auditoria.
   update instagram_support.alerts set reason=v_case_reason where case_id=c.id;
   update instagram_support.threads set pause_reason=v_case_reason,updated_at=now()
     where id=t.id and (pause_reason=c.reason or pause_reason=e.routing_reason)
       and not exists(select 1 from instagram_support.cases x where x.thread_id=t.id and x.status='open' and x.id<>c.id);
   if c.event_id=e.id or (c.reason=e.routing_reason and c.reason is distinct from v_case_reason) then
     update instagram_support.events set intent=null,reply_key=null where id=c.handoff_notice_event_id;
     update instagram_support.outbox set text='' where event_id=c.handoff_notice_event_id;
   end if;
   -- Uma nova fonte so substitui aviso ainda nao tentado. A pausa humana fica como estava.
   if v_notice_active then
     update instagram_support.events set status='superseded',text='',allow_handoff_ack=false,lease=null,worker=null,lease_until=null,
       reason='source_withdrawn',updated_at=now() where id=n.id;
     update instagram_support.threads set lease=null,worker=null,lease_until=null,version=version+1
       where id=t.id and (lease is not distinct from n.lease or lease is null) returning version into v_version;
     select version into v_version from instagram_support.threads where id=t.id;
     if r.id is not null and c.status='open' and not s.paused
       and (s.mode='live' or (s.mode='test' and v_sender=any(s.test_sender_ids)))
       and r.message_at>=now()-interval '24 hours' and r.status in ('pending','human','ignored','completed')
       and not exists(select 1 from instagram_support.outbox where event_id=r.id) then
       update instagram_support.cases set handoff_notice_event_id=r.id where id=c.id;
       update instagram_support.events set status='pending',text='',allow_handoff_ack=true,reply_key=upper(r.routing_reason),intent=r.routing_reason,
         thread_version=v_version,lease=null,worker=null,lease_until=null,reason='handoff_notice',updated_at=now() where id=r.id;
       v_queued:=true;
     end if;
   end if;
 end loop;
 select exists(select 1 from instagram_support.outbox where event_id=e.id) into v_out;
 perform instagram_support.settle_budget(e.id);
 update instagram_support.outbox set text='' where event_id=e.id;
 update instagram_support.events set withdrawn_at=now(),text='',intent=null,reply_key=null,routing_reason=null,
   allow_handoff_ack=false,status=case when v_out then status else 'superseded' end,
   reason='message_withdrawn',lease=case when v_out then lease else null end,
   worker=case when v_out then worker else null end,lease_until=case when v_out then lease_until else null end,updated_at=now() where id=e.id;
 if not v_out then
   update instagram_support.threads set lease=null,worker=null,lease_until=null,version=version+1
     where id=t.id and lease is not null and lease=e.lease;
 end if;
 return jsonb_build_object('status','withdrawn','queued',v_queued);
end;
$function$;
-- RECREATED CONTRACTS

create or replace function instagram_support.pause_thread(p_thread_id uuid,p_reason text,p_summary text,p_event_id uuid default null)
returns uuid language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_case uuid; v_created boolean := false; v_settings instagram_support.settings%rowtype;
begin
  update instagram_support.threads set human_paused=true,pause_reason=left(p_reason,80),version=version+1,updated_at=now()
  where id=p_thread_id;
  select * into v_settings from instagram_support.settings where singleton;
  select id into v_case from instagram_support.cases where thread_id=p_thread_id and status='open';
  v_created := not found;
  insert into instagram_support.cases(thread_id,event_id,reason,summary)
  values(p_thread_id,p_event_id,left(coalesce(nullif(p_reason,''),'needs_human'),80),left(coalesce(p_summary,''),400))
  on conflict(thread_id) where status='open' do update
    set reason=case when instagram_support.handoff_priority(excluded.reason)>instagram_support.handoff_priority(instagram_support.cases.reason) then excluded.reason else instagram_support.cases.reason end,
      summary=case when instagram_support.handoff_priority(excluded.reason)>instagram_support.handoff_priority(instagram_support.cases.reason) then excluded.summary else instagram_support.cases.summary end,
      event_id=case when instagram_support.handoff_priority(excluded.reason)>instagram_support.handoff_priority(instagram_support.cases.reason) then coalesce(excluded.event_id,instagram_support.cases.event_id) else instagram_support.cases.event_id end,updated_at=now()
  returning id into v_case;
  if p_event_id is not null then
    update instagram_support.events set case_id=v_case,routing_reason=coalesce(routing_reason,left(p_reason,80))
      where id=p_event_id and thread_id=p_thread_id and withdrawn_at is null;
  end if;
  if v_created then
    -- A habilitacao futura nao transforma casos antigos em e-mails retroativos.
    insert into instagram_support.alerts(case_id,reason,status,error_code)
    values(v_case,left(coalesce(nullif(p_reason,''),'needs_human'),80),case when v_settings.alerts_enabled and v_settings.alerts_activation_after is not null
      and now()>=v_settings.alerts_activation_after then 'pending' else 'suppressed' end,
      case when v_settings.alerts_enabled and v_settings.alerts_activation_after is not null and now()>=v_settings.alerts_activation_after then null else 'not_enabled_at_creation' end)
    on conflict(case_id) do nothing;
  end if;
  -- Cancela trabalho normal anterior sem tocar em um POST ja iniciado.
  perform instagram_support.settle_budget(e.id) from instagram_support.events e
    where e.thread_id=p_thread_id and e.id is distinct from p_event_id and e.status in ('pending','processing','completed')
      and not e.allow_handoff_ack and not exists(select 1 from instagram_support.outbox o where o.event_id=e.id);
  update instagram_support.events e set status='superseded',text='',reason='case_pause',updated_at=now()
    where e.thread_id=p_thread_id and e.id is distinct from p_event_id and e.status in ('pending','processing','completed')
      and not e.allow_handoff_ack and not exists(select 1 from instagram_support.outbox o where o.event_id=e.id);
  update instagram_support.threads t set lease=null,worker=null,lease_until=null where t.id=p_thread_id
    and exists(select 1 from instagram_support.events e where e.thread_id=t.id and e.status='superseded' and e.reason='case_pause' and e.lease=t.lease);
  return v_case;
end;
$function$;

create or replace function instagram_support.recover_expired()
returns void language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_event instagram_support.events%rowtype; v_thread instagram_support.threads%rowtype; v_out instagram_support.outbox%rowtype;
begin
  for v_out in select * from instagram_support.outbox where status='sending' and send_deadline<now() order by send_deadline limit 20 loop
    select * into v_thread from instagram_support.threads where id=v_out.thread_id;
    if not pg_try_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0)) then continue; end if;
    select * into strict v_thread from instagram_support.threads where id=v_out.thread_id for update;
    update instagram_support.outbox set status='uncertain',finished_at=now() where id=v_out.id and status='sending' and send_deadline<now();
    if found then
      update instagram_support.events set status='uncertain',text='',reason='send_timeout',updated_at=now() where id=v_out.event_id;
      perform instagram_support.pause_thread(v_out.thread_id,'delivery_unknown','Envio sem resultado verificavel. Conferir a conversa antes de responder novamente.',v_out.event_id);
    end if;
  end loop;
  for v_event in select * from instagram_support.events where status in ('processing','completed') and lease_until<now() order by lease_until limit 20 loop
    select * into v_thread from instagram_support.threads where id=v_event.thread_id;
    if not pg_try_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0)) then continue; end if;
    select * into strict v_thread from instagram_support.threads where id=v_event.thread_id for update;
    select * into strict v_event from instagram_support.events where id=v_event.id for update;
    if v_event.status not in ('processing','completed') or v_event.lease_until>=now() then continue; end if;
    if v_event.withdrawn_at is not null and not exists(select 1 from instagram_support.outbox where event_id=v_event.id) then
      perform instagram_support.settle_budget(v_event.id);
      update instagram_support.events set status='superseded',text='',intent=null,reply_key=null,routing_reason=null,allow_handoff_ack=false,lease=null,worker=null,lease_until=null,reason='message_withdrawn',updated_at=now() where id=v_event.id;
    elsif v_event.allow_handoff_ack and v_event.thread_version=v_thread.version
      and exists(select 1 from instagram_support.cases c where c.handoff_notice_event_id=v_event.id and c.status='open')
      and not exists(select 1 from instagram_support.outbox where event_id=v_event.id) then
      update instagram_support.events set status='pending',lease=null,worker=null,lease_until=null,updated_at=now() where id=v_event.id;
    elsif exists(select 1 from instagram_support.budget_reservations where event_id=v_event.id) or v_event.status='completed' then
      perform instagram_support.settle_budget(v_event.id);
      update instagram_support.events set status='human',text='',reason='worker_timeout',updated_at=now() where id=v_event.id and status in ('processing','completed');
      perform instagram_support.pause_thread(v_event.thread_id,'worker_timeout','Processamento interrompido; verificar atendimento pendente.',v_event.id);
    else
      update instagram_support.events set status='pending',lease=null,worker=null,lease_until=null,updated_at=now() where id=v_event.id and status='processing';
    end if;
    update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_event.thread_id and lease=v_event.lease;
  end loop;
  update instagram_support.events set status='expired',text='',reason='outside_window',updated_at=now() where status='pending' and withdrawn_at is null and message_at<now()-interval '24 hours';
  update instagram_support.events set text='' where text<>'' and status not in ('pending','processing');
  update instagram_support.alerts set status='uncertain',error_code='alert_send_timeout',finished_at=now() where status='sending' and send_deadline<now();
end;
$function$;

create or replace function public.ig_support_ingest(p_event jsonb)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,pg_temp
as $function$
declare
 v_settings instagram_support.settings%rowtype;v_thread instagram_support.threads%rowtype;
 v_id uuid;v_case uuid;v_existing uuid;v_notice instagram_support.events%rowtype;
 v_status text:='ignored';v_reason text:='disabled';v_at timestamptz;v_queued boolean:=false;
 v_sender text:=p_event->>'sender_id';v_mid text:=p_event->>'mid';v_kind text:=p_event->>'kind';
 v_safety text:=upper(nullif(p_event->>'safety_intent',''));v_case_reason text;
begin
 -- Ordem comum: settings -> remetente -> evento. A pausa global inclui esta ingesta.
 select * into strict v_settings from instagram_support.settings where singleton for share;
 if jsonb_typeof(p_event)<>'object' or v_sender is null or v_sender !~ '^[0-9]{5,30}$'
   or v_mid is null or length(v_mid) not between 1 and 512 or v_kind is null or v_kind not in ('incoming','echo','withdrawal')
   or p_event->>'recipient_id' is distinct from v_settings.ig_user_id
   or length(coalesce(p_event->>'text',''))>v_settings.max_text_chars
   or coalesce(p_event->>'timestamp_ms','') !~ '^[0-9]{10,16}$' then
   raise exception using errcode='22023',message='Evento Instagram invalido.';
 end if;
 if v_safety is not null and v_safety not in ('URGENCY','ALLERGY','PAYMENT_DISPUTE','COMPLAINT','HUMAN','RESERVATION_CHANGE','LOST_ITEM','GROUP_EVENT') then
   raise exception using errcode='22023',message='Roteamento de seguranca invalido.';
 end if;
 if v_kind='withdrawal' then return instagram_support.withdraw_message(p_event);end if;
 v_at:=to_timestamp((p_event->>'timestamp_ms')::numeric/1000);
 if v_at>now()+interval '5 minutes' then return jsonb_build_object('status','ignored','reason','future_timestamp','queued',false);end if;
 perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_sender,0));
 if exists(select 1 from instagram_support.events where mid=v_mid) then return jsonb_build_object('status','duplicate','queued',false);end if;
 insert into instagram_support.threads(sender_id) values(v_sender) on conflict(sender_id) do nothing;
 select * into strict v_thread from instagram_support.threads where sender_id=v_sender for update;
 if v_kind='incoming' and v_at>=now()-interval '24 hours' and not v_thread.human_paused and not v_settings.paused
   and (v_settings.mode='live' or (v_settings.mode='test' and v_sender=any(v_settings.test_sender_ids))) then
   v_status:='pending';v_reason:=null;v_queued:=true;
 elsif v_kind='incoming' and v_at<now()-interval '24 hours' then v_reason:='outside_window';
 elsif v_thread.human_paused then v_reason:='human_paused';
 elsif v_settings.mode='test' and not(v_sender=any(v_settings.test_sender_ids)) then v_reason:='not_allowlisted';end if;
 insert into instagram_support.events(mid,thread_id,kind,text,message_at,mode_at_ingest,status,reason)
   values(v_mid,v_thread.id,v_kind,case when v_status='pending' then coalesce(p_event->>'text','') else '' end,v_at,v_settings.mode,v_status,v_reason) returning id into v_id;
 if v_kind='echo' then
   if exists(select 1 from instagram_support.outbox where provider_mid=v_mid and status='sent') then
     update instagram_support.events set reason='known_bot_echo' where id=v_id;
   else
     v_case:=instagram_support.pause_thread(v_thread.id,'manual_or_unknown_echo','Resposta humana ou origem ainda nao reconciliada. Automacao pausada.',v_id);
     perform instagram_support.cancel_handoff_notice(v_thread.id,'manual_intervention');
     update instagram_support.events set status='human',reason='manual_or_unknown_echo' where id=v_id;
     update instagram_support.events set status='superseded',text='',reason='human_intervention',updated_at=now()
       where thread_id=v_thread.id and status='pending' and not allow_handoff_ack;
   end if;
 elsif v_safety is not null and v_status='pending' then
   select id into v_existing from instagram_support.cases where thread_id=v_thread.id and status='open';
   update instagram_support.threads set last_inbound_at=greatest(last_inbound_at,v_at),updated_at=now() where id=v_thread.id;
   v_case:=instagram_support.pause_thread(v_thread.id,lower(v_safety),'Solicitacao requer atendimento humano: '||v_safety||'.',v_id);
   select * into strict v_thread from instagram_support.threads where id=v_thread.id;
   if v_existing is null then
     update instagram_support.cases set handoff_notice_event_id=v_id where id=v_case and handoff_notice_event_id is null;
     update instagram_support.events set status='pending',text='',reason='handoff_notice',intent=lower(v_safety),reply_key=v_safety,
       allow_handoff_ack=true,thread_version=v_thread.version,updated_at=now() where id=v_id;
     v_queued:=true;
   else
     update instagram_support.events set status='human',text='',reason=lower(v_safety),updated_at=now() where id=v_id;
     v_queued:=false;
   end if;
   update instagram_support.events set status='superseded',text='',reason='sensitive_message',updated_at=now()
     where thread_id=v_thread.id and status='pending' and id<>v_id and not allow_handoff_ack;
 elsif v_thread.human_paused then
   -- A rajada nao cancela o aviso. Apenas uma prioridade maior renova o lease.
   update instagram_support.threads set last_inbound_at=greatest(last_inbound_at,v_at),updated_at=now() where id=v_thread.id;
   select id,reason into v_case,v_case_reason from instagram_support.cases where thread_id=v_thread.id and status='open' for update;
   if v_case is not null then
     update instagram_support.cases set updated_at=now() where id=v_case;
     if v_safety is not null then update instagram_support.events set case_id=v_case,routing_reason=lower(v_safety) where id=v_id;end if;
     if v_safety is not null and instagram_support.handoff_priority(v_safety)>instagram_support.handoff_priority(v_case_reason) then
       update instagram_support.cases set reason=lower(v_safety),summary='Solicitacao requer atendimento humano: '||v_safety||'.',event_id=v_id where id=v_case;
       select e.* into v_notice from instagram_support.events e join instagram_support.cases c on c.handoff_notice_event_id=e.id
         where c.id=v_case and e.allow_handoff_ack and e.status in ('pending','completed')
         and not exists(select 1 from instagram_support.outbox where event_id=e.id) for update of e;
       if found then
         update instagram_support.threads set version=version+1,lease=null,worker=null,lease_until=null where id=v_thread.id returning * into v_thread;
         update instagram_support.events set status='pending',reply_key=v_safety,intent=lower(v_safety),thread_version=v_thread.version,
           lease=null,worker=null,lease_until=null,updated_at=now() where id=v_notice.id;
         v_queued:=true;
       end if;
     end if;
   end if;
 elsif v_thread.last_inbound_at is not null and v_at<v_thread.last_inbound_at then
   update instagram_support.events set status='superseded',text='',reason='older_event' where id=v_id;v_queued:=false;
 else
   update instagram_support.threads set last_inbound_at=v_at,version=version+1,updated_at=now() where id=v_thread.id;
   update instagram_support.events set status='superseded',text='',reason='newer_message',updated_at=now()
     where thread_id=v_thread.id and status='pending' and id<>v_id and not allow_handoff_ack;
 end if;
 return jsonb_build_object('status',case when v_case is not null then 'human' else v_status end,'queued',v_queued,
   'event_id',v_id,'case_id',v_case,'case_saved',v_case is not null);
end;
$function$;

create or replace function public.ig_support_claim(p_worker uuid,p_limit integer default 1)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,pg_temp
as $function$
declare v_settings instagram_support.settings%rowtype;v_event instagram_support.events%rowtype;
 v_thread instagram_support.threads%rowtype;v_row record;v_lease uuid;v_result jsonb:='[]'::jsonb;v_count integer:=0;v_ack boolean;v_case uuid;
begin
 if p_worker is null or p_limit is null or p_limit not between 1 and 5 then raise exception using errcode='22023',message='Claim invalido.';end if;
 select * into strict v_settings from instagram_support.settings where singleton for share;
 perform instagram_support.recover_expired();
 if v_settings.mode='off' or v_settings.paused then return v_result;end if;
 for v_row in select e.id,e.thread_id,t.sender_id from instagram_support.events e join instagram_support.threads t on t.id=e.thread_id
   left join instagram_support.cases c on c.handoff_notice_event_id=e.id and c.status='open'
   where e.status='pending' and e.withdrawn_at is null and (not t.human_paused or (e.allow_handoff_ack and c.id is not null and e.thread_version=t.version))
   and (t.lease_until is null or t.lease_until<now()) order by e.allow_handoff_ack desc,e.received_at,e.id limit 40 loop
   exit when v_count>=p_limit;
   if not pg_try_advisory_xact_lock(hashtextextended('ig-support:'||v_row.sender_id,0)) then continue;end if;
   select * into strict v_thread from instagram_support.threads where id=v_row.thread_id for update;
   select * into strict v_event from instagram_support.events where id=v_row.id for update;
   select id into v_case from instagram_support.cases where handoff_notice_event_id=v_event.id and status='open';
   v_ack:=v_event.allow_handoff_ack and v_case is not null and v_event.thread_version=v_thread.version;
   if v_event.status<>'pending' or v_event.withdrawn_at is not null or (v_thread.human_paused and not v_ack) or v_thread.lease_until>now() then continue;end if;
   if v_event.message_at<now()-interval '24 hours' then update instagram_support.events set status='expired',text='',allow_handoff_ack=false,reason='outside_window' where id=v_event.id;continue;end if;
   if v_event.mode_at_ingest<>v_settings.mode or (v_settings.mode='test' and not(v_thread.sender_id=any(v_settings.test_sender_ids))) then
     update instagram_support.events set status='ignored',text='',allow_handoff_ack=false,reason='mode_changed' where id=v_event.id;continue;
   end if;
   v_lease:=gen_random_uuid();
   update instagram_support.events set status=case when v_ack then 'completed' else 'processing' end,lease=v_lease,worker=p_worker,
     lease_until=now()+interval '120 seconds',thread_version=v_thread.version,updated_at=now() where id=v_event.id;
   update instagram_support.threads set lease=v_lease,worker=p_worker,lease_until=now()+interval '120 seconds' where id=v_thread.id;
   v_result:=v_result||jsonb_build_array(jsonb_build_object('event_id',v_event.id,'lease',v_lease,'thread_id',v_thread.id,'sender_id',v_thread.sender_id,
     'text',v_event.text,'message_at',v_event.message_at,'clarify_count',v_thread.clarify_count,'thread_version',v_thread.version,
     'handoff_ack',v_ack,'reply_key',v_event.reply_key,'case_id',v_case,
     'first_reply',not exists(select 1 from instagram_support.outbox where thread_id=v_thread.id and status='sent')));
   v_count:=v_count+1;
 end loop;
 return v_result;
end;
$function$;

create or replace function public.ig_support_reserve_budget(p_event_id uuid,p_lease uuid,p_max_cost_cents integer default 2)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare
  v_settings instagram_support.settings%rowtype; v_event instagram_support.events%rowtype; v_thread instagram_support.threads%rowtype;
  v_month date := date_trunc('month',now() at time zone 'America/Fortaleza')::date;
  v_budget instagram_support.budget_months%rowtype; v_res uuid;
begin
  select * into strict v_settings from instagram_support.settings where singleton;
  select * into v_event from instagram_support.events where id=p_event_id;
  if not found then return jsonb_build_object('allowed',false,'reason','event_missing'); end if;
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id for update;
  select * into strict v_event from instagram_support.events where id=p_event_id for update;
  if v_event.withdrawn_at is not null then return jsonb_build_object('allowed',false,'reason','message_withdrawn');end if;
  if v_event.lease is distinct from p_lease or v_event.status<>'processing' or v_event.lease_until<now() or v_thread.version<>v_event.thread_version or v_thread.human_paused then
    return jsonb_build_object('allowed',false,'reason','stale_or_paused'); end if;
  if v_settings.mode='off' or v_settings.paused or v_event.mode_at_ingest<>v_settings.mode or
    (v_settings.mode='test' and not(v_thread.sender_id=any(v_settings.test_sender_ids))) then return jsonb_build_object('allowed',false,'reason','disabled'); end if;
  if not v_settings.model_usage_allowed or not v_settings.billing_verified or v_settings.pricing_valid_until is null or v_settings.pricing_valid_until<now() then
    return jsonb_build_object('allowed',false,'reason','model_not_approved'); end if;
  if p_max_cost_cents is null or p_max_cost_cents<v_settings.request_reserve_cents then return jsonb_build_object('allowed',false,'reason','cost_bound_too_small'); end if;
  if exists(select 1 from instagram_support.budget_reservations where event_id=p_event_id) then return jsonb_build_object('allowed',false,'reason','already_started'); end if;
  insert into instagram_support.budget_months(month) values(v_month) on conflict do nothing;
  select * into strict v_budget from instagram_support.budget_months where month=v_month for update;
  if v_budget.spent_cents+v_budget.reserved_cents+v_settings.request_reserve_cents>v_settings.monthly_budget_cents or v_budget.generations>=v_settings.monthly_generation_limit then
    return jsonb_build_object('allowed',false,'reason','monthly_limit'); end if;
  if (select count(*) from instagram_support.budget_reservations where created_at>=now()-interval '1 minute')>=v_settings.global_per_minute then
    return jsonb_build_object('allowed',false,'reason','global_rate'); end if;
  if (select count(*) from instagram_support.budget_reservations where thread_id=v_thread.id and created_at>=now()-interval '10 minutes')>=v_settings.thread_per_ten_minutes then
    return jsonb_build_object('allowed',false,'reason','thread_rate'); end if;
  insert into instagram_support.budget_reservations(event_id,thread_id,lease,month,amount_cents)
    values(p_event_id,v_thread.id,p_lease,v_month,v_settings.request_reserve_cents) returning id into v_res;
  update instagram_support.budget_months set reserved_cents=reserved_cents+v_settings.request_reserve_cents,generations=generations+1,updated_at=now() where month=v_month;
  return jsonb_build_object('allowed',true,'reservation_id',v_res,'reserved_cents',v_settings.request_reserve_cents);
end;
$function$;

create or replace function public.ig_support_complete(p_event_id uuid,p_lease uuid,p_result jsonb)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_event instagram_support.events%rowtype; v_thread instagram_support.threads%rowtype;v_settings instagram_support.settings%rowtype;
  v_case uuid; v_reason text := nullif(left(p_result->>'handoff_reason',80),''); v_intent text := lower(left(p_result->>'intent',60)); v_decision text := 'reply';
  v_new_case boolean := false; v_known boolean := coalesce((p_result->>'usage_known')::boolean,false); v_actual integer := (p_result->>'actual_cost_cents')::integer;
begin
  select * into strict v_settings from instagram_support.settings where singleton for update;
  select * into v_event from instagram_support.events where id=p_event_id;
  if not found then return jsonb_build_object('allowed',false,'decision','cancelled','reason','event_missing'); end if;
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id for update;
  select * into strict v_event from instagram_support.events where id=p_event_id for update;
  if v_event.withdrawn_at is not null then
    perform instagram_support.settle_budget(p_event_id);
    if p_result->>'policy_error'='usage_bound_exceeded' then update instagram_support.settings set mode='off',paused=true,updated_at=now() where singleton;end if;
    return jsonb_build_object('allowed',false,'decision','cancelled','reason','message_withdrawn');
  end if;
  if v_event.lease=p_lease and v_event.status='completed' and v_event.allow_handoff_ack and coalesce((p_result->>'skip')::boolean,false) then
    perform instagram_support.cancel_handoff_notice(v_thread.id,'runtime_gate_denied');
    return jsonb_build_object('allowed',false,'decision','cancelled','reason','runtime_gate_denied');
  end if;
  if v_event.lease is distinct from p_lease or v_event.status<>'processing' then return jsonb_build_object('allowed',false,'decision','cancelled','reason','lease_or_status'); end if;
  perform instagram_support.settle_budget(p_event_id,v_actual,v_known);
  if v_settings.mode='off' or v_settings.paused or v_event.mode_at_ingest<>v_settings.mode
    or (v_settings.mode='test' and not(v_thread.sender_id=any(v_settings.test_sender_ids))) then
    update instagram_support.events set status='superseded',text='',allow_handoff_ack=false,reason='disabled_at_completion',updated_at=now() where id=p_event_id;
    update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_thread.id and lease=p_lease;
    return jsonb_build_object('allowed',false,'decision','cancelled','reason','disabled_at_completion');
  end if;
  if p_result->>'policy_error'='usage_bound_exceeded' then
    update instagram_support.settings set paused=true,mode='off',updated_at=now() where singleton;
    v_reason := 'usage_bound_exceeded';
  end if;
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id;
  if v_thread.human_paused or v_thread.version<>v_event.thread_version or v_event.lease_until<now() then
    update instagram_support.events set status='superseded',text='',reason='stale_or_paused',updated_at=now() where id=p_event_id;
    update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_thread.id and lease=p_lease;
    return jsonb_build_object('allowed',false,'decision','cancelled','reason','stale_or_paused');
  end if;
  if coalesce((p_result->>'skip')::boolean,false) then
    update instagram_support.events set status='ignored',text='',reason='skip',intent=v_intent,updated_at=now() where id=p_event_id;
    update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_thread.id and lease=p_lease;
    return jsonb_build_object('allowed',false,'decision','cancelled','reason','skip');
  end if;
  if v_intent='unknown' then
    update instagram_support.threads set clarify_count=least(2,clarify_count+1) where id=v_thread.id returning * into v_thread;
    if v_thread.clarify_count>=2 then v_reason := coalesce(v_reason,'unresolved_question'); else v_decision := 'clarify'; end if;
  elsif v_reason is null then update instagram_support.threads set clarify_count=0 where id=v_thread.id; end if;
  if v_reason is not null then
    select not exists(select 1 from instagram_support.cases where thread_id=v_thread.id and status='open') into v_new_case;
    v_case := instagram_support.pause_thread(v_thread.id,v_reason,left(coalesce(p_result->>'summary','Atendimento humano necessario.'),400),p_event_id);
    select * into strict v_thread from instagram_support.threads where id=v_thread.id;
    v_decision := 'handoff';
    if v_new_case and p_result->>'policy_error' is distinct from 'usage_bound_exceeded' then
      update instagram_support.cases set handoff_notice_event_id=p_event_id where id=v_case and handoff_notice_event_id is null;
    end if;
  end if;
  update instagram_support.events set status=case when v_decision='handoff' and (not v_new_case or p_result->>'policy_error'='usage_bound_exceeded') then 'human' else 'completed' end,text='',intent=v_intent,reply_key=left(p_result->>'reply_key',80),allow_handoff_ack=v_decision='handoff' and v_new_case and p_result->>'policy_error' is distinct from 'usage_bound_exceeded',thread_version=v_thread.version,
    usage_input_tokens=case when p_result#>>'{usage,input}' ~ '^[0-9]+$' and (p_result#>>'{usage,input}')::numeric<=4096 then (p_result#>>'{usage,input}')::integer end,
    usage_output_tokens=case when p_result#>>'{usage,output}' ~ '^[0-9]+$' and (p_result#>>'{usage,output}')::numeric<=96 then (p_result#>>'{usage,output}')::integer end,
    updated_at=now() where id=p_event_id;
  if v_decision='handoff' and not v_new_case then
    update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_thread.id and lease=p_lease;
  end if;
  return jsonb_build_object('allowed',v_decision<>'handoff' or v_new_case,'decision',v_decision,'thread_version',v_thread.version,'case_id',v_case,'case_saved',v_case is not null);
end;
$function$;

create or replace function public.ig_support_prepare_send(p_event_id uuid,p_lease uuid,p_text text,p_expected_version bigint)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_settings instagram_support.settings%rowtype; v_event instagram_support.events%rowtype; v_thread instagram_support.threads%rowtype; v_out uuid;
begin
  if length(coalesce(p_text,'')) not between 1 and 700 then raise exception using errcode='22023',message='Resposta invalida.'; end if;
  select * into strict v_settings from instagram_support.settings where singleton for share;
  select * into v_event from instagram_support.events where id=p_event_id;
  if not found then return jsonb_build_object('allowed',false,'reason','event_missing'); end if;
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id for update;
  select * into strict v_event from instagram_support.events where id=p_event_id for update;
  if v_event.withdrawn_at is not null then return jsonb_build_object('allowed',false,'reason','message_withdrawn');end if;
  if v_event.lease is distinct from p_lease or v_event.status<>'completed' or v_event.lease_until<now() then return jsonb_build_object('allowed',false,'reason','lease_or_status'); end if;
  if v_thread.version is distinct from p_expected_version or v_event.thread_version<>v_thread.version or (v_thread.human_paused and not v_event.allow_handoff_ack) then
    return jsonb_build_object('allowed',false,'reason','stale_or_paused'); end if;
  if v_event.allow_handoff_ack and not exists(select 1 from instagram_support.cases c
      where c.handoff_notice_event_id=v_event.id and c.thread_id=v_thread.id and c.status='open') then
    return jsonb_build_object('allowed',false,'reason','notice_cancelled');
  end if;
  if v_settings.mode='off' or v_settings.paused or v_event.mode_at_ingest<>v_settings.mode or
    (v_settings.mode='test' and not(v_thread.sender_id=any(v_settings.test_sender_ids))) then return jsonb_build_object('allowed',false,'reason','disabled'); end if;
  if v_event.message_at<now()-interval '24 hours' or v_thread.last_inbound_at<now()-interval '24 hours' then return jsonb_build_object('allowed',false,'reason','outside_window'); end if;
  if exists(select 1 from instagram_support.outbox where event_id=p_event_id) then return jsonb_build_object('allowed',false,'reason','already_prepared'); end if;
  if v_event.allow_handoff_ack then
    update instagram_support.cases set notice_attempted=true where handoff_notice_event_id=v_event.id and status='open' and not notice_attempted;
    if not found then return jsonb_build_object('allowed',false,'reason','notice_already_attempted');end if;
  end if;
  insert into instagram_support.outbox(event_id,thread_id,lease,text) values(p_event_id,v_thread.id,p_lease,p_text) returning id into v_out;
  update instagram_support.events set status='sending',updated_at=now() where id=p_event_id;
  return jsonb_build_object('allowed',true,'outbox_id',v_out);
end;
$function$;
revoke all on function instagram_support.withdraw_message(jsonb) from public,anon,authenticated;
grant execute on function instagram_support.withdraw_message(jsonb) to service_role;
revoke all on function instagram_support.pause_thread(uuid,text,text,uuid),instagram_support.recover_expired() from public,anon,authenticated;
grant execute on function instagram_support.pause_thread(uuid,text,text,uuid),instagram_support.recover_expired() to service_role;
revoke all on function public.ig_support_ingest(jsonb),public.ig_support_claim(uuid,integer),public.ig_support_reserve_budget(uuid,uuid,integer),public.ig_support_complete(uuid,uuid,jsonb),public.ig_support_prepare_send(uuid,uuid,text,bigint) from public,anon,authenticated;
grant execute on function public.ig_support_ingest(jsonb),public.ig_support_claim(uuid,integer),public.ig_support_reserve_budget(uuid,uuid,integer),public.ig_support_complete(uuid,uuid,jsonb),public.ig_support_prepare_send(uuid,uuid,text,bigint) to service_role;
notify pgrst,'reload schema';
commit;
