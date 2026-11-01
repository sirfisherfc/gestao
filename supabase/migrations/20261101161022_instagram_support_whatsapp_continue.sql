-- Automatic WhatsApp guidance leaves later FAQs eligible. Existing pauses are preserved.
-- No customer content, secret, financial object or reservations object is changed.
begin;
alter table instagram_support.settings add column if not exists public_data_approved boolean not null default false;
alter table instagram_support.settings add column if not exists public_delivery_verified boolean not null default false;
comment on column instagram_support.settings.public_data_approved is 'Separate production consent; owner TEST consent does not enable this flag.';
comment on column instagram_support.settings.public_delivery_verified is 'Separate official transport proof outside app roles; no inferred approval from mode.';

create or replace function instagram_support.register_case(p_thread_id uuid,p_reason text,p_summary text,p_event_id uuid,p_pause boolean)
returns uuid language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_case uuid; v_created boolean := false; v_settings instagram_support.settings%rowtype;
begin
  update instagram_support.threads set human_paused=human_paused or p_pause,pause_reason=case when p_pause then left(p_reason,80) else pause_reason end,version=version+1,updated_at=now()
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

create or replace function instagram_support.pause_thread(p_thread_id uuid,p_reason text,p_summary text,p_event_id uuid default null)
returns uuid language sql security invoker set search_path=pg_catalog,pg_temp
as $function$ select instagram_support.register_case(p_thread_id,p_reason,p_summary,p_event_id,true); $function$;
create or replace function instagram_support.route_whatsapp(p_thread_id uuid,p_reason text,p_summary text,p_event_id uuid)
returns uuid language sql security invoker set search_path=pg_catalog,pg_temp
as $function$ select instagram_support.register_case(p_thread_id,p_reason,p_summary,p_event_id,false); $function$;

-- The sender lock is held by ingest/complete. A new FAQ preserves the first unsent
-- notice and invalidates its old worker lease before reusing the current version.
create or replace function instagram_support.refresh_notice(p_thread_id uuid)
returns void language plpgsql security invoker set search_path=pg_catalog,pg_temp
as $function$
declare n instagram_support.events%rowtype;c instagram_support.cases%rowtype;t instagram_support.threads%rowtype;
begin
 select * into strict t from instagram_support.threads where id=p_thread_id for update;
 select * into c from instagram_support.cases where thread_id=p_thread_id and status='open' for update;
 if not found or c.notice_attempted or t.human_paused then return;end if;
 select * into n from instagram_support.events where id=c.handoff_notice_event_id for update;
 if not found or n.withdrawn_at is not null or not n.allow_handoff_ack or n.status not in ('pending','completed')
   or exists(select 1 from instagram_support.outbox where event_id=n.id) then return;end if;
 update instagram_support.events set status='pending',reply_key=case when c.reason in ('unresolved_question','unknown_after_clarification') then 'UNKNOWN' else upper(c.reason) end,intent=c.reason,
   thread_version=t.version,lease=null,worker=null,lease_until=null,updated_at=now() where id=n.id;
 update instagram_support.threads set lease=null,worker=null,lease_until=null where id=t.id and lease=n.lease;
end;
$function$;
-- A fresh request may supply the first notice if the old source was cancelled
-- before any attempt. Old events and external effects stay terminal.
create or replace function instagram_support.bind_first_notice(p_thread_id uuid,p_event_id uuid)
returns boolean language plpgsql security invoker set search_path=pg_catalog,pg_temp
as $function$
declare c instagram_support.cases%rowtype;
begin
 select * into c from instagram_support.cases where thread_id=p_thread_id and status='open' for update;
 if not found or c.notice_attempted or exists(select 1 from instagram_support.threads where id=p_thread_id and human_paused)
   or not exists(select 1 from instagram_support.events where id=p_event_id and thread_id=p_thread_id and case_id=c.id
     and withdrawn_at is null and kind='incoming' and status in ('pending','processing'))
   or exists(select 1 from instagram_support.events e join instagram_support.outbox o on o.event_id=e.id where e.case_id=c.id)
   or exists(select 1 from instagram_support.events where id=c.handoff_notice_event_id and withdrawn_at is null
     and allow_handoff_ack and status in ('pending','completed')) then return false;end if;
 update instagram_support.cases set handoff_notice_event_id=p_event_id,updated_at=now() where id=c.id and not notice_attempted;
 return found;
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
   and ((v_settings.mode='live' and v_settings.public_data_approved and v_settings.public_delivery_verified) or (v_settings.mode='test' and v_sender=any(v_settings.test_sender_ids))) then
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
   v_case:=instagram_support.route_whatsapp(v_thread.id,lower(v_safety),'Solicitacao requer atendimento humano: '||v_safety||'.',v_id);
   select * into strict v_thread from instagram_support.threads where id=v_thread.id;
   if instagram_support.bind_first_notice(v_thread.id,v_id) then
     update instagram_support.events set status='pending',text='',reason='handoff_notice',intent=lower(v_safety),reply_key=v_safety,
       allow_handoff_ack=true,thread_version=v_thread.version,updated_at=now() where id=v_id;
     v_queued:=true;
   else
     update instagram_support.events set status='human',text='',reason=lower(v_safety),updated_at=now() where id=v_id;
     v_queued:=false;
   end if;
   perform instagram_support.refresh_notice(v_thread.id);
   v_queued:=v_queued or exists(select 1 from instagram_support.events where thread_id=v_thread.id and allow_handoff_ack and status='pending');
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
   perform instagram_support.refresh_notice(v_thread.id);
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
 if v_settings.mode='off' or v_settings.paused or (v_settings.mode='live' and not(v_settings.public_data_approved and v_settings.public_delivery_verified)) then return v_result;end if;
 for v_row in select e.id,e.thread_id,t.sender_id from instagram_support.events e join instagram_support.threads t on t.id=e.thread_id
   left join instagram_support.cases c on c.handoff_notice_event_id=e.id and c.status='open'
   where e.status='pending' and e.withdrawn_at is null and not t.human_paused
   and (t.lease_until is null or t.lease_until<now()) order by e.allow_handoff_ack desc,e.received_at,e.id limit 40 loop
   exit when v_count>=p_limit;
   if not pg_try_advisory_xact_lock(hashtextextended('ig-support:'||v_row.sender_id,0)) then continue;end if;
   select * into strict v_thread from instagram_support.threads where id=v_row.thread_id for update;
   select * into strict v_event from instagram_support.events where id=v_row.id for update;
   select id into v_case from instagram_support.cases where handoff_notice_event_id=v_event.id and status='open';
   v_ack:=v_event.allow_handoff_ack and v_case is not null and v_event.thread_version=v_thread.version;
   if v_event.status<>'pending' or v_event.withdrawn_at is not null or v_thread.human_paused or v_thread.lease_until>now() then continue;end if;
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
  if (v_settings.mode='live' and not(v_settings.public_data_approved and v_settings.public_delivery_verified)) or v_settings.mode='off' or v_settings.paused or v_event.mode_at_ingest<>v_settings.mode or
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
  if v_settings.mode='off' or v_settings.paused or (v_settings.mode='live' and not(v_settings.public_data_approved and v_settings.public_delivery_verified)) or v_event.mode_at_ingest<>v_settings.mode
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
    v_reason := coalesce(v_reason,'unresolved_question');
  elsif v_reason is null then update instagram_support.threads set clarify_count=0 where id=v_thread.id; end if;
  if v_reason is not null then
    v_case := instagram_support.route_whatsapp(v_thread.id,v_reason,left(coalesce(p_result->>'summary','Atendimento humano necessario.'),400),p_event_id);
    select * into strict v_thread from instagram_support.threads where id=v_thread.id;
    v_decision := 'handoff';
    v_new_case:=p_result->>'policy_error' is distinct from 'usage_bound_exceeded'
      and instagram_support.bind_first_notice(v_thread.id,p_event_id);
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
  if v_thread.version is distinct from p_expected_version or v_event.thread_version<>v_thread.version or v_thread.human_paused then
    return jsonb_build_object('allowed',false,'reason','stale_or_paused'); end if;
  if v_event.allow_handoff_ack and not exists(select 1 from instagram_support.cases c
      where c.handoff_notice_event_id=v_event.id and c.thread_id=v_thread.id and c.status='open') then
    return jsonb_build_object('allowed',false,'reason','notice_cancelled');
  end if;
  if v_settings.mode='off' or v_settings.paused or (v_settings.mode='live' and not(v_settings.public_data_approved and v_settings.public_delivery_verified)) or v_event.mode_at_ingest<>v_settings.mode or
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
create or replace function public.ig_support_control(p_action text,p_thread_id uuid default null,p_args jsonb default '{}')
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_actor uuid; v_thread instagram_support.threads%rowtype; v_case uuid; v_rows jsonb; v_settings jsonb; v_notice_thread uuid;
begin
  -- O endpoint exige getUser + fn_is_admin do JWT. A RPC continua service_role-only.
  if p_action='status' then
    select public.ig_support_settings() - 'manager_auth_user_id' into v_settings;
    return jsonb_build_object('settings',v_settings,'open_cases',(select count(*) from instagram_support.cases where status='open'),
      'pending_events',(select count(*) from instagram_support.events where status='pending'),
      'budget',(select to_jsonb(b) from instagram_support.budget_months b where month=date_trunc('month',now() at time zone 'America/Fortaleza')::date),
      'alert_budget',(select to_jsonb(a) from instagram_support.alert_months a where month=date_trunc('month',now() at time zone 'America/Fortaleza')::date));
  elsif p_action='cases' then
    select coalesce(jsonb_agg(q order by q.updated_at desc),'[]'::jsonb) into v_rows from (
      select latest.* from (
        select distinct on(c.thread_id) c.id as case_id,c.thread_id,t.sender_id,c.reason,c.summary,c.status,c.assigned_to,c.updated_at,t.last_inbound_at,t.human_paused,
          a.status as alert_status,a.error_code as alert_error_code,
          case when c.handoff_notice_event_id is null then 'not_queued'
            when o.status='sent' then 'sent' when o.status in ('sending','failed','uncertain') then o.status
            when e.allow_handoff_ack and e.status in ('pending','completed') then 'pending' else 'cancelled' end as handoff_notice_status
        from instagram_support.cases c join instagram_support.threads t on t.id=c.thread_id left join instagram_support.alerts a on a.case_id=c.id
        left join instagram_support.events e on e.id=c.handoff_notice_event_id
        left join instagram_support.outbox o on o.event_id=e.id where c.status='open' or t.human_paused
        order by c.thread_id,(c.status='open') desc,c.updated_at desc
      ) latest order by latest.updated_at desc limit 100
    ) q;
    return jsonb_build_object('cases',v_rows);
  end if;
  v_actor := (p_args->>'actor_id')::uuid;
  if v_actor is null then raise exception using errcode='22023',message='Ator administrativo ausente.'; end if;
  perform 1 from instagram_support.settings where singleton for update;
  perform instagram_support.recover_expired();
  if p_action='pause_global' then
    if jsonb_typeof(p_args->'paused')<>'boolean' then raise exception using errcode='22023',message='Estado de pausa invalido.'; end if;
    update instagram_support.settings set paused=(p_args->>'paused')::boolean,updated_at=now() where singleton;
    if (p_args->>'paused')::boolean then
      for v_notice_thread in select thread_id from instagram_support.cases where status='open' and handoff_notice_event_id is not null loop
        perform instagram_support.cancel_handoff_notice(v_notice_thread,'global_pause');
      end loop;
    end if;
  elsif p_action in ('assume','close','resume') then
    select * into strict v_thread from instagram_support.threads where id=p_thread_id;
    perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
    select * into strict v_thread from instagram_support.threads where id=p_thread_id for update;
    if p_action='assume' then
      perform instagram_support.cancel_handoff_notice(p_thread_id,'human_assumed');
      v_case := instagram_support.pause_thread(p_thread_id,'human_assumed','Atendimento assumido pelo administrador.');
      update instagram_support.cases set assigned_to=v_actor,updated_at=now() where id=v_case;
    elsif p_action='close' then
      perform instagram_support.cancel_handoff_notice(p_thread_id,'case_closed');
      update instagram_support.cases set status='closed',closed_at=now(),updated_at=now() where thread_id=p_thread_id and status='open';
      -- Closing the record preserves the current explicit pause, including a later echo/assume.
      update instagram_support.threads set version=version+1,updated_at=now() where id=p_thread_id;
    elsif p_action='resume' then
      if p_args->>'confirm' is distinct from 'true' then raise exception using errcode='22023',message='Retomada exige confirmacao explicita.'; end if;
      if exists(select 1 from instagram_support.outbox where thread_id=p_thread_id and status='sending') then
        return jsonb_build_object('changed',false,'reason','send_in_progress_or_unreconciled');
      end if;
      perform instagram_support.cancel_handoff_notice(p_thread_id,'manual_resume');
      perform instagram_support.settle_budget(e.id) from instagram_support.events e
        where e.thread_id=p_thread_id and e.status in ('pending','processing','completed');
      update instagram_support.cases set status='closed',closed_at=now(),updated_at=now() where thread_id=p_thread_id and status='open';
      update instagram_support.threads set human_paused=false,pause_reason=null,clarify_count=0,version=version+1,lease=null,worker=null,lease_until=null,updated_at=now() where id=p_thread_id;
      update instagram_support.events set status='superseded',text='',reason='manual_resume_requires_new_message',updated_at=now() where thread_id=p_thread_id and status in ('pending','processing','completed');
    end if;
  else raise exception using errcode='22023',message='Acao administrativa invalida.'; end if;
  insert into instagram_support.control_audit(actor_id,action,thread_id) values(v_actor,p_action,p_thread_id);
  return jsonb_build_object('changed',true,'action',p_action,'case_id',v_case);
end;
$function$;

revoke all on function instagram_support.register_case(uuid,text,text,uuid,boolean),instagram_support.route_whatsapp(uuid,text,text,uuid),instagram_support.refresh_notice(uuid) from public,anon,authenticated;
grant execute on function instagram_support.register_case(uuid,text,text,uuid,boolean),instagram_support.route_whatsapp(uuid,text,text,uuid),instagram_support.refresh_notice(uuid) to service_role;
revoke all on function instagram_support.bind_first_notice(uuid,uuid) from public,anon,authenticated;
grant execute on function instagram_support.bind_first_notice(uuid,uuid) to service_role;
revoke all on function instagram_support.pause_thread(uuid,text,text,uuid),public.ig_support_ingest(jsonb),public.ig_support_claim(uuid,integer),public.ig_support_reserve_budget(uuid,uuid,integer),public.ig_support_complete(uuid,uuid,jsonb),public.ig_support_prepare_send(uuid,uuid,text,bigint),public.ig_support_control(text,uuid,jsonb) from public,anon,authenticated;
grant execute on function instagram_support.pause_thread(uuid,text,text,uuid),public.ig_support_ingest(jsonb),public.ig_support_claim(uuid,integer),public.ig_support_reserve_budget(uuid,uuid,integer),public.ig_support_complete(uuid,uuid,jsonb),public.ig_support_prepare_send(uuid,uuid,text,bigint),public.ig_support_control(text,uuid,jsonb) to service_role;
commit;
