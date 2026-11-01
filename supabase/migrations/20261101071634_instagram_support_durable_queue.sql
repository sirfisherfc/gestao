-- Agente Instagram: fila duravel, pausa humana e limite de gasto por servidor.
-- Objetos novos e isolados; nao altera tabelas de reservas ou financeiras.
-- Instala desligado. RPCs SECURITY INVOKER, somente service_role.
-- Um envio de resultado incerto fica para revisao humana, sem retry automatico.
begin;
set local lock_timeout = '2s';

create schema if not exists instagram_support;
revoke all on schema instagram_support from public, anon, authenticated;
grant usage on schema instagram_support to service_role;

create table if not exists instagram_support.settings (
  singleton boolean primary key default true check (singleton),
  mode text not null default 'off' check (mode in ('off','test','live')),
  paused boolean not null default true,
  test_sender_ids text[] not null default '{}',
  app_id text not null default '224912007567636' check (app_id = '224912007567636'),
  page_id text not null default '107690041045934' check (page_id = '107690041045934'),
  ig_user_id text not null default '17841439937145607' check (ig_user_id = '17841439937145607'),
  model text not null default 'gemini-3.5-flash-lite',
  model_usage_allowed boolean not null default false,
  billing_verified boolean not null default false,
  pricing_valid_until timestamptz,
  max_input_tokens integer not null default 4096 check (max_input_tokens between 1 and 4096),
  max_output_tokens integer not null default 96 check (max_output_tokens between 1 and 96),
  max_text_chars integer not null default 1200 check (max_text_chars between 1 and 1200),
  monthly_budget_cents integer not null default 4500 check (monthly_budget_cents between 0 and 4500),
  monthly_generation_limit integer not null default 2000 check (monthly_generation_limit between 0 and 2000),
  request_reserve_cents integer not null default 2 check (request_reserve_cents between 2 and 25),
  global_per_minute integer not null default 10 check (global_per_minute between 1 and 10),
  thread_per_ten_minutes integer not null default 3 check (thread_per_ten_minutes between 1 and 3),
  manager_auth_user_id uuid,
  alerts_enabled boolean not null default false,
  alerts_activation_after timestamptz,
  alerts_monthly_limit integer not null default 60 check (alerts_monthly_limit between 0 and 60),
  cron_enabled boolean not null default false,
  updated_at timestamptz not null default now()
);
insert into instagram_support.settings(singleton) values(true) on conflict do nothing;

create table if not exists instagram_support.threads (
  id uuid primary key default gen_random_uuid(),
  sender_id text not null unique check (sender_id ~ '^[0-9]{5,30}$'),
  human_paused boolean not null default false,
  pause_reason text,
  version bigint not null default 0,
  clarify_count integer not null default 0 check (clarify_count between 0 and 2),
  last_inbound_at timestamptz,
  last_bot_sent_at timestamptz,
  lease uuid,
  worker uuid,
  lease_until timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists instagram_support.events (
  id uuid primary key default gen_random_uuid(),
  mid text not null unique check (length(mid) between 1 and 512),
  thread_id uuid not null references instagram_support.threads(id),
  kind text not null check (kind in ('incoming','echo')),
  text text not null default '' check (length(text) <= 1200),
  message_at timestamptz not null,
  received_at timestamptz not null default now(),
  mode_at_ingest text not null check (mode_at_ingest in ('off','test','live')),
  status text not null check (status in ('ignored','pending','processing','completed','sending','sent','human','failed','uncertain','superseded','expired')),
  reason text,
  lease uuid,
  worker uuid,
  lease_until timestamptz,
  thread_version bigint,
  intent text,
  reply_key text,
  usage_input_tokens integer check (usage_input_tokens between 0 and 4096),
  usage_output_tokens integer check (usage_output_tokens between 0 and 96),
  allow_handoff_ack boolean not null default false,
  updated_at timestamptz not null default now()
);
create index if not exists ig_support_events_pending_idx on instagram_support.events(received_at,id) where status = 'pending';
create index if not exists ig_support_events_thread_idx on instagram_support.events(thread_id,received_at desc);
create index if not exists ig_support_events_lease_idx on instagram_support.events(lease_until) where status in ('processing','completed','sending');

create table if not exists instagram_support.budget_months (
  month date primary key,
  reserved_cents integer not null default 0 check (reserved_cents >= 0),
  spent_cents integer not null default 0 check (spent_cents >= 0),
  generations integer not null default 0 check (generations >= 0),
  updated_at timestamptz not null default now()
);
create table if not exists instagram_support.budget_reservations (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null unique references instagram_support.events(id),
  thread_id uuid not null references instagram_support.threads(id),
  lease uuid not null,
  month date not null references instagram_support.budget_months(month),
  amount_cents integer not null check (amount_cents between 2 and 25),
  charged_cents integer check (charged_cents >= 0),
  status text not null default 'reserved' check (status in ('reserved','settled')),
  created_at timestamptz not null default now(),
  settled_at timestamptz
);
create index if not exists ig_support_budget_recent_idx on instagram_support.budget_reservations(created_at desc);
create index if not exists ig_support_budget_thread_idx on instagram_support.budget_reservations(thread_id,created_at desc);

create table if not exists instagram_support.outbox (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null unique references instagram_support.events(id),
  thread_id uuid not null references instagram_support.threads(id),
  lease uuid not null,
  text text not null check (length(text) between 1 and 700),
  status text not null default 'sending' check (status in ('sending','sent','failed','uncertain')),
  provider_mid text unique check (provider_mid is null or length(provider_mid) between 1 and 512),
  created_at timestamptz not null default now(),
  send_deadline timestamptz not null default now() + interval '60 seconds',
  finished_at timestamptz
);
create index if not exists ig_support_outbox_deadline_idx on instagram_support.outbox(send_deadline) where status = 'sending';
create table if not exists instagram_support.cases (
  id uuid primary key default gen_random_uuid(),
  thread_id uuid not null references instagram_support.threads(id),
  event_id uuid references instagram_support.events(id),
  status text not null default 'open' check (status in ('open','closed')),
  reason text not null check (length(reason) between 1 and 80),
  summary text not null default '' check (length(summary) <= 400),
  assigned_to uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  closed_at timestamptz
);
create unique index if not exists ig_support_one_open_case_idx on instagram_support.cases(thread_id) where status = 'open';
create table if not exists instagram_support.control_audit (
  id bigint generated by default as identity primary key,
  actor_id uuid not null,
  action text not null,
  thread_id uuid references instagram_support.threads(id),
  created_at timestamptz not null default now()
);
create table if not exists instagram_support.alert_months (
  month date primary key,
  attempts integer not null default 0 check (attempts between 0 and 60)
);
create table if not exists instagram_support.alerts (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null unique references instagram_support.cases(id),
  revision integer not null default 1 check (revision=1),
  reason text not null check (length(reason) between 1 and 80),
  status text not null check (status in ('suppressed','pending','retry_wait','sending','sent','failed','uncertain')),
  error_code text,
  attempts integer not null default 0 check (attempts between 0 and 2),
  lease uuid,
  worker uuid,
  send_deadline timestamptz,
  next_attempt_at timestamptz,
  provider_id text,
  manager_auth_user_id uuid,
  created_at timestamptz not null default now(),
  finished_at timestamptz
);
create index if not exists ig_support_alerts_pending_idx on instagram_support.alerts(created_at) where status in ('pending','retry_wait','sending');

-- Privado fora da Data API, RLS como segunda barreira. service_role tem BYPASSRLS.
do $permissions$
declare v_table text;
begin
  foreach v_table in array array['settings','threads','events','budget_months','budget_reservations','outbox','cases','control_audit','alert_months','alerts'] loop
    execute format('alter table instagram_support.%I enable row level security',v_table);
    execute format('revoke all on instagram_support.%I from public, anon, authenticated',v_table);
    execute format('grant select, insert, update, delete on instagram_support.%I to service_role',v_table);
  end loop;
end;
$permissions$;
revoke all on all sequences in schema instagram_support from public, anon, authenticated;
grant usage, select on all sequences in schema instagram_support to service_role;

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
    set reason=excluded.reason,summary=excluded.summary,event_id=coalesce(excluded.event_id,instagram_support.cases.event_id),updated_at=now()
  returning id into v_case;
  if v_created then
    -- A habilitacao futura nao transforma casos antigos em e-mails retroativos.
    insert into instagram_support.alerts(case_id,reason,status,error_code)
    values(v_case,left(coalesce(nullif(p_reason,''),'needs_human'),80),case when v_settings.alerts_enabled and v_settings.alerts_activation_after is not null
      and now()>=v_settings.alerts_activation_after then 'pending' else 'suppressed' end,
      case when v_settings.alerts_enabled and v_settings.alerts_activation_after is not null and now()>=v_settings.alerts_activation_after then null else 'not_enabled_at_creation' end)
    on conflict(case_id) do nothing;
  end if;
  return v_case;
end;
$function$;

create or replace function instagram_support.settle_budget(p_event_id uuid,p_actual_cost_cents integer default null,p_usage_known boolean default false)
returns void language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_res instagram_support.budget_reservations%rowtype; v_charge integer;
begin
  select * into v_res from instagram_support.budget_reservations where event_id=p_event_id for update;
  if not found or v_res.status='settled' then return; end if;
  -- Metadata ausente/erro/timeout conserva a reserva maxima inteira.
  v_charge := case when p_usage_known and p_actual_cost_cents between 0 and v_res.amount_cents then greatest(1,p_actual_cost_cents) else v_res.amount_cents end;
  update instagram_support.budget_months set reserved_cents=reserved_cents-v_res.amount_cents,spent_cents=spent_cents+v_charge,updated_at=now() where month=v_res.month;
  update instagram_support.budget_reservations set status='settled',charged_cents=v_charge,settled_at=now() where id=v_res.id;
  if p_usage_known and p_actual_cost_cents > v_res.amount_cents then
    update instagram_support.settings set paused=true,mode='off',updated_at=now() where singleton;
    perform instagram_support.pause_thread(v_res.thread_id,'billing_bound_exceeded','Custo informado excedeu a reserva conservadora; conferir cobranca e tarifa.',p_event_id);
  end if;
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
    update instagram_support.outbox set status='uncertain',finished_at=now() where id=v_out.id and status='sending' and send_deadline<now();
    if found then
      update instagram_support.events set status='uncertain',text='',reason='send_timeout',updated_at=now() where id=v_out.event_id;
      perform instagram_support.pause_thread(v_out.thread_id,'delivery_unknown','Envio sem resultado verificavel. Conferir a conversa antes de responder novamente.',v_out.event_id);
    end if;
  end loop;
  for v_event in select * from instagram_support.events where status in ('processing','completed') and lease_until<now() order by lease_until limit 20 loop
    select * into v_thread from instagram_support.threads where id=v_event.thread_id;
    if not pg_try_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0)) then continue; end if;
    select * into strict v_event from instagram_support.events where id=v_event.id for update;
    if v_event.status not in ('processing','completed') or v_event.lease_until>=now() then continue; end if;
    if exists(select 1 from instagram_support.budget_reservations where event_id=v_event.id) or v_event.status='completed' then
      perform instagram_support.settle_budget(v_event.id);
      update instagram_support.events set status='human',text='',reason='worker_timeout',updated_at=now() where id=v_event.id and status in ('processing','completed');
      perform instagram_support.pause_thread(v_event.thread_id,'worker_timeout','Processamento interrompido; verificar atendimento pendente.',v_event.id);
    else
      update instagram_support.events set status='pending',lease=null,worker=null,lease_until=null,updated_at=now() where id=v_event.id and status='processing';
    end if;
    update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_event.thread_id and lease=v_event.lease;
  end loop;
  update instagram_support.events set status='expired',text='',reason='outside_window',updated_at=now() where status='pending' and message_at<now()-interval '24 hours';
  update instagram_support.events set text='' where text<>'' and status not in ('pending','processing');
  update instagram_support.alerts set status='uncertain',error_code='alert_send_timeout',finished_at=now() where status='sending' and send_deadline<now();
end;
$function$;

create or replace function public.ig_support_settings()
returns jsonb language sql stable security invoker set search_path = pg_catalog, pg_temp
as $function$
  select to_jsonb(s) - 'singleton' from instagram_support.settings s where singleton;
$function$;

create or replace function public.ig_support_ingest(p_event jsonb)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare
  v_settings instagram_support.settings%rowtype; v_thread instagram_support.threads%rowtype;
  v_id uuid; v_case uuid; v_status text; v_reason text; v_at timestamptz;
  v_sender text := p_event->>'sender_id'; v_mid text := p_event->>'mid'; v_kind text := p_event->>'kind';
  v_safety text := upper(nullif(p_event->>'safety_intent',''));
begin
  select * into strict v_settings from instagram_support.settings where singleton;
  if jsonb_typeof(p_event)<>'object' or v_sender is null or v_sender !~ '^[0-9]{5,30}$'
     or v_mid is null or length(v_mid) not between 1 and 512 or v_kind is null or v_kind not in ('incoming','echo')
     or p_event->>'recipient_id' is distinct from v_settings.ig_user_id or length(coalesce(p_event->>'text',''))>v_settings.max_text_chars
     or coalesce(p_event->>'timestamp_ms','') !~ '^[0-9]{10,16}$' then
    raise exception using errcode='22023',message='Evento Instagram invalido.';
  end if;
  if v_safety is not null and v_safety not in ('URGENCY','ALLERGY','PAYMENT_DISPUTE','COMPLAINT','HUMAN','RESERVATION_CHANGE','LOST_ITEM','GROUP_EVENT') then
    raise exception using errcode='22023',message='Roteamento de seguranca invalido.';
  end if;
  v_at := to_timestamp((p_event->>'timestamp_ms')::numeric/1000);
  if v_at > now()+interval '5 minutes' then return jsonb_build_object('status','ignored','reason','future_timestamp','queued',false); end if;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_sender,0));
  if exists(select 1 from instagram_support.events where mid=v_mid) then
    return jsonb_build_object('status','duplicate','queued',false);
  end if;
  insert into instagram_support.threads(sender_id) values(v_sender) on conflict(sender_id) do nothing;
  select * into strict v_thread from instagram_support.threads where sender_id=v_sender for update;
  v_status := 'ignored'; v_reason := 'disabled';
  if v_kind='incoming' and v_at >= now()-interval '24 hours' and not v_thread.human_paused and not v_settings.paused
    and (v_settings.mode='live' or (v_settings.mode='test' and v_sender=any(v_settings.test_sender_ids))) then
    v_status := 'pending'; v_reason := null;
  elsif v_kind='incoming' and v_at < now()-interval '24 hours' then v_reason := 'outside_window';
  elsif v_thread.human_paused then v_reason := 'human_paused';
  elsif v_settings.mode='test' and not(v_sender=any(v_settings.test_sender_ids)) then v_reason := 'not_allowlisted'; end if;
  insert into instagram_support.events(mid,thread_id,kind,text,message_at,mode_at_ingest,status,reason)
    values(v_mid,v_thread.id,v_kind,case when v_status='pending' then coalesce(p_event->>'text','') else '' end,v_at,v_settings.mode,v_status,v_reason) returning id into v_id;
  if v_kind='echo' then
    if exists(select 1 from instagram_support.outbox where provider_mid=v_mid and status='sent') then
      update instagram_support.events set reason='known_bot_echo' where id=v_id;
    else
      v_case := instagram_support.pause_thread(v_thread.id,'manual_or_unknown_echo','Resposta humana ou origem ainda nao reconciliada. Automacao pausada.',v_id);
      update instagram_support.events set status='human',reason='manual_or_unknown_echo' where id=v_id;
      update instagram_support.events set status='superseded',text='',reason='human_intervention',updated_at=now() where thread_id=v_thread.id and status='pending';
    end if;
  else
    if v_safety is not null and v_status='pending' then
      update instagram_support.threads set last_inbound_at=greatest(last_inbound_at,v_at),updated_at=now() where id=v_thread.id;
      v_case := instagram_support.pause_thread(v_thread.id,v_safety,'Solicitacao requer atendimento humano: '||v_safety||'.',v_id);
      update instagram_support.events set status='human',text='',reason=v_safety,updated_at=now() where id=v_id;
      update instagram_support.events set status='superseded',text='',reason='sensitive_message',updated_at=now() where thread_id=v_thread.id and status='pending';
      v_status := 'human';
    else
    -- Eventos fora de ordem sao registrados, sem substituir o contexto mais novo.
    if v_thread.last_inbound_at is not null and v_at < v_thread.last_inbound_at then
      update instagram_support.events set status='superseded',text='',reason='older_event' where id=v_id;
      v_status := 'superseded';
    else
      update instagram_support.threads set last_inbound_at=v_at,version=version+1,updated_at=now() where id=v_thread.id;
      update instagram_support.events set status='superseded',text='',reason='newer_message',updated_at=now() where thread_id=v_thread.id and status='pending' and id<>v_id;
      if v_thread.human_paused then
        update instagram_support.cases set updated_at=now() where thread_id=v_thread.id and status='open';
      end if;
    end if;
    end if;
  end if;
  return jsonb_build_object('status',case when v_case is not null then 'human' else v_status end,'queued',v_status='pending','event_id',v_id,'case_id',v_case,'case_saved',v_case is not null);
end;
$function$;

create or replace function public.ig_support_claim(p_worker uuid,p_limit integer default 1)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare
  v_settings instagram_support.settings%rowtype; v_event instagram_support.events%rowtype;
  v_thread instagram_support.threads%rowtype; v_out instagram_support.outbox%rowtype;
  v_row record; v_lease uuid; v_result jsonb := '[]'::jsonb; v_count integer := 0;
begin
  if p_worker is null or p_limit is null or p_limit not between 1 and 5 then raise exception using errcode='22023',message='Claim invalido.'; end if;
  select * into strict v_settings from instagram_support.settings where singleton;
  -- Recupera efeitos incertos, sem reenviar. Faz isso mesmo quando desligado.
  perform instagram_support.recover_expired();
  if v_settings.mode='off' or v_settings.paused then return v_result; end if;
  for v_row in select e.id,e.thread_id,t.sender_id from instagram_support.events e join instagram_support.threads t on t.id=e.thread_id
    where e.status='pending' and not t.human_paused and (t.lease_until is null or t.lease_until<now()) order by e.received_at,e.id limit 40 loop
    exit when v_count>=p_limit;
    if not pg_try_advisory_xact_lock(hashtextextended('ig-support:'||v_row.sender_id,0)) then continue; end if;
    select * into strict v_thread from instagram_support.threads where id=v_row.thread_id for update;
    select * into strict v_event from instagram_support.events where id=v_row.id for update;
    if v_event.status<>'pending' or v_thread.human_paused or v_thread.lease_until>now() then continue; end if;
    if v_event.message_at<now()-interval '24 hours' then
      update instagram_support.events set status='expired',text='',reason='outside_window',updated_at=now() where id=v_event.id;
      continue;
    end if;
    if v_event.mode_at_ingest<>v_settings.mode or (v_settings.mode='test' and not(v_thread.sender_id=any(v_settings.test_sender_ids))) then
      update instagram_support.events set status='ignored',text='',reason='mode_changed',updated_at=now() where id=v_event.id;
      continue;
    end if;
    v_lease := gen_random_uuid();
    update instagram_support.events set status='processing',lease=v_lease,worker=p_worker,lease_until=now()+interval '120 seconds',thread_version=v_thread.version,updated_at=now() where id=v_event.id;
    update instagram_support.threads set lease=v_lease,worker=p_worker,lease_until=now()+interval '120 seconds' where id=v_thread.id;
    v_result := v_result || jsonb_build_array(jsonb_build_object('event_id',v_event.id,'lease',v_lease,'thread_id',v_thread.id,'sender_id',v_thread.sender_id,
      'text',v_event.text,'message_at',v_event.message_at,'clarify_count',v_thread.clarify_count,'thread_version',v_thread.version,
      'first_reply',not exists(select 1 from instagram_support.outbox where thread_id=v_thread.id and status='sent')));
    v_count := v_count+1;
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
declare v_event instagram_support.events%rowtype; v_thread instagram_support.threads%rowtype;
  v_case uuid; v_reason text := nullif(left(p_result->>'handoff_reason',80),''); v_intent text := lower(left(p_result->>'intent',60)); v_decision text := 'reply';
  v_known boolean := coalesce((p_result->>'usage_known')::boolean,false); v_actual integer := (p_result->>'actual_cost_cents')::integer;
begin
  select * into v_event from instagram_support.events where id=p_event_id;
  if not found then return jsonb_build_object('allowed',false,'decision','cancelled','reason','event_missing'); end if;
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id for update;
  select * into strict v_event from instagram_support.events where id=p_event_id for update;
  if v_event.lease is distinct from p_lease or v_event.status<>'processing' then return jsonb_build_object('allowed',false,'decision','cancelled','reason','lease_or_status'); end if;
  perform instagram_support.settle_budget(p_event_id,v_actual,v_known);
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
    v_case := instagram_support.pause_thread(v_thread.id,v_reason,left(coalesce(p_result->>'summary','Atendimento humano necessario.'),400),p_event_id);
    select * into strict v_thread from instagram_support.threads where id=v_thread.id;
    v_decision := 'handoff';
  end if;
  update instagram_support.events set status='completed',text='',intent=v_intent,reply_key=left(p_result->>'reply_key',80),allow_handoff_ack=v_decision='handoff',thread_version=v_thread.version,
    usage_input_tokens=case when p_result#>>'{usage,input}' ~ '^[0-9]+$' and (p_result#>>'{usage,input}')::numeric<=4096 then (p_result#>>'{usage,input}')::integer end,
    usage_output_tokens=case when p_result#>>'{usage,output}' ~ '^[0-9]+$' and (p_result#>>'{usage,output}')::numeric<=96 then (p_result#>>'{usage,output}')::integer end,
    updated_at=now() where id=p_event_id;
  return jsonb_build_object('allowed',true,'decision',v_decision,'thread_version',v_thread.version,'case_id',v_case,'case_saved',v_case is not null);
end;
$function$;

create or replace function public.ig_support_prepare_send(p_event_id uuid,p_lease uuid,p_text text,p_expected_version bigint)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_settings instagram_support.settings%rowtype; v_event instagram_support.events%rowtype; v_thread instagram_support.threads%rowtype; v_out uuid;
begin
  if length(coalesce(p_text,'')) not between 1 and 700 then raise exception using errcode='22023',message='Resposta invalida.'; end if;
  select * into strict v_settings from instagram_support.settings where singleton;
  select * into v_event from instagram_support.events where id=p_event_id;
  if not found then return jsonb_build_object('allowed',false,'reason','event_missing'); end if;
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
  select * into strict v_thread from instagram_support.threads where id=v_event.thread_id for update;
  select * into strict v_event from instagram_support.events where id=p_event_id for update;
  if v_event.lease is distinct from p_lease or v_event.status<>'completed' or v_event.lease_until<now() then return jsonb_build_object('allowed',false,'reason','lease_or_status'); end if;
  if v_thread.version is distinct from p_expected_version or v_event.thread_version<>v_thread.version or (v_thread.human_paused and not v_event.allow_handoff_ack) then
    return jsonb_build_object('allowed',false,'reason','stale_or_paused'); end if;
  if v_settings.mode='off' or v_settings.paused or v_event.mode_at_ingest<>v_settings.mode or
    (v_settings.mode='test' and not(v_thread.sender_id=any(v_settings.test_sender_ids))) then return jsonb_build_object('allowed',false,'reason','disabled'); end if;
  if v_event.message_at<now()-interval '24 hours' or v_thread.last_inbound_at<now()-interval '24 hours' then return jsonb_build_object('allowed',false,'reason','outside_window'); end if;
  if exists(select 1 from instagram_support.outbox where event_id=p_event_id) then return jsonb_build_object('allowed',false,'reason','already_prepared'); end if;
  insert into instagram_support.outbox(event_id,thread_id,lease,text) values(p_event_id,v_thread.id,p_lease,p_text) returning id into v_out;
  update instagram_support.events set status='sending',updated_at=now() where id=p_event_id;
  return jsonb_build_object('allowed',true,'outbox_id',v_out);
end;
$function$;

create or replace function public.ig_support_finish_send(p_outbox_id uuid,p_lease uuid,p_status text,p_provider_message_id text default null)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_out instagram_support.outbox%rowtype; v_thread instagram_support.threads%rowtype; v_case uuid;
begin
  if p_status is null or p_status not in ('sent','failed','uncertain') or (p_status='sent' and length(coalesce(p_provider_message_id,'')) not between 1 and 512) then
    raise exception using errcode='22023',message='Resultado de envio invalido.'; end if;
  select * into v_out from instagram_support.outbox where id=p_outbox_id;
  if not found then return jsonb_build_object('changed',false,'reason','outbox_missing'); end if;
  select * into strict v_thread from instagram_support.threads where id=v_out.thread_id;
  perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
  select * into strict v_out from instagram_support.outbox where id=p_outbox_id for update;
  if v_out.lease is distinct from p_lease then return jsonb_build_object('changed',false,'reason','lease'); end if;
  if v_out.status<>'sending' then return jsonb_build_object('changed',false,'status',v_out.status,'reason','already_final'); end if;
  update instagram_support.outbox set status=p_status,provider_mid=case when p_status='sent' then p_provider_message_id else null end,finished_at=now() where id=p_outbox_id;
  update instagram_support.events set status=p_status,reason=case when p_status='sent' then null else 'delivery_'||p_status end,updated_at=now() where id=v_out.event_id;
  if p_status='sent' then update instagram_support.threads set last_bot_sent_at=now(),updated_at=now() where id=v_out.thread_id;
  else v_case := instagram_support.pause_thread(v_out.thread_id,'delivery_'||p_status,'Envio interrompido. Conferir a conversa antes de nova resposta.',v_out.event_id); end if;
  update instagram_support.threads set lease=null,worker=null,lease_until=null where id=v_out.thread_id and lease=p_lease;
  return jsonb_build_object('changed',true,'status',p_status,'case_id',v_case,'case_saved',v_case is not null);
end;
$function$;

create or replace function public.ig_support_control(p_action text,p_thread_id uuid default null,p_args jsonb default '{}')
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_actor uuid; v_thread instagram_support.threads%rowtype; v_case uuid; v_rows jsonb; v_settings jsonb;
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
          a.status as alert_status,a.error_code as alert_error_code
        from instagram_support.cases c join instagram_support.threads t on t.id=c.thread_id left join instagram_support.alerts a on a.case_id=c.id where c.status='open' or t.human_paused
        order by c.thread_id,(c.status='open') desc,c.updated_at desc
      ) latest order by latest.updated_at desc limit 100
    ) q;
    return jsonb_build_object('cases',v_rows);
  end if;
  v_actor := (p_args->>'actor_id')::uuid;
  if v_actor is null then raise exception using errcode='22023',message='Ator administrativo ausente.'; end if;
  perform instagram_support.recover_expired();
  if p_action='pause_global' then
    if jsonb_typeof(p_args->'paused')<>'boolean' then raise exception using errcode='22023',message='Estado de pausa invalido.'; end if;
    update instagram_support.settings set paused=(p_args->>'paused')::boolean,updated_at=now() where singleton;
  elsif p_action in ('assume','close','resume') then
    select * into strict v_thread from instagram_support.threads where id=p_thread_id;
    perform pg_advisory_xact_lock(hashtextextended('ig-support:'||v_thread.sender_id,0));
    select * into strict v_thread from instagram_support.threads where id=p_thread_id for update;
    if p_action='assume' then
      v_case := instagram_support.pause_thread(p_thread_id,'human_assumed','Atendimento assumido pelo administrador.');
      update instagram_support.cases set assigned_to=v_actor,updated_at=now() where id=v_case;
    elsif p_action='close' then
      update instagram_support.cases set status='closed',closed_at=now(),updated_at=now() where thread_id=p_thread_id and status='open';
      -- Fechar um caso nao retoma o robo.
      update instagram_support.threads set human_paused=true,pause_reason='case_closed',version=version+1,updated_at=now() where id=p_thread_id;
    elsif p_action='resume' then
      if p_args->>'confirm' is distinct from 'true' then raise exception using errcode='22023',message='Retomada exige confirmacao explicita.'; end if;
      if exists(select 1 from instagram_support.outbox where thread_id=p_thread_id and status='sending') then
        return jsonb_build_object('changed',false,'reason','send_in_progress_or_unreconciled');
      end if;
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

create or replace function public.ig_support_claim_alerts(p_worker uuid,p_limit integer default 1)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare
  v_settings instagram_support.settings%rowtype; v_email text; v_alert instagram_support.alerts%rowtype;
  v_month date := date_trunc('month',now() at time zone 'America/Fortaleza')::date;
  v_budget instagram_support.alert_months%rowtype; v_lease uuid; v_result jsonb := '[]'::jsonb;
begin
  if p_worker is null or p_limit is null or p_limit not between 1 and 5 then raise exception using errcode='22023',message='Claim de alerta invalido.'; end if;
  select * into strict v_settings from instagram_support.settings where singleton;
  update instagram_support.alerts set status='uncertain',error_code='alert_send_timeout',finished_at=now() where status='sending' and send_deadline<now();
  if v_settings.mode='off' or not v_settings.alerts_enabled or v_settings.manager_auth_user_id is null or v_settings.alerts_activation_after is null then return v_result; end if;
  -- Destino sempre resolvido no cadastro interno; nenhum e-mail em settings/UI.
  select u.email::text into v_email from public.app_users u
    where u.auth_user_id=v_settings.manager_auth_user_id and u.active and u.role='admin';
  if v_email is null or length(v_email) not between 3 and 254 then return v_result; end if;
  update instagram_support.alerts a set status='suppressed',error_code='case_closed_or_before_activation',finished_at=now()
    from instagram_support.cases c where a.case_id=c.id and a.status in ('pending','retry_wait')
      and (c.status<>'open' or c.created_at<v_settings.alerts_activation_after);
  if v_settings.mode='test' then
    update instagram_support.alerts a set status='suppressed',error_code='not_allowlisted',finished_at=now()
      from instagram_support.cases c join instagram_support.threads t on t.id=c.thread_id
      where a.case_id=c.id and a.status in ('pending','retry_wait') and not(t.sender_id=any(v_settings.test_sender_ids));
  end if;
  update instagram_support.alerts set status='failed',error_code='manager_changed',finished_at=now()
    where status='retry_wait' and manager_auth_user_id is distinct from v_settings.manager_auth_user_id;
  insert into instagram_support.alert_months(month) values(v_month) on conflict do nothing;
  select * into strict v_budget from instagram_support.alert_months where month=v_month for update;
  for v_alert in select a.* from instagram_support.alerts a join instagram_support.cases c on c.id=a.case_id
    where c.status='open' and (a.status='pending' or (a.status='retry_wait' and a.next_attempt_at<=now())) and a.attempts<2
    order by a.created_at limit p_limit for update of a skip locked loop
    exit when v_budget.attempts>=v_settings.alerts_monthly_limit;
    v_lease := gen_random_uuid();
    update instagram_support.alerts set status='sending',lease=v_lease,worker=p_worker,attempts=attempts+1,
      manager_auth_user_id=v_settings.manager_auth_user_id,send_deadline=now()+interval '60 seconds',error_code=null where id=v_alert.id;
    update instagram_support.alert_months set attempts=attempts+1 where month=v_month;
    v_budget.attempts := v_budget.attempts+1;
    v_result := v_result || jsonb_build_array(jsonb_build_object('alert_id',v_alert.id,'lease',v_lease,'case_id',v_alert.case_id,
      'revision',v_alert.revision,'reason',v_alert.reason,'manager_email',v_email));
  end loop;
  return v_result;
end;
$function$;

create or replace function public.ig_support_finish_alert(p_alert_id uuid,p_lease uuid,p_status text,p_provider_id text default null,p_retryable boolean default false)
returns jsonb language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_alert instagram_support.alerts%rowtype; v_status text := p_status;
begin
  if p_status is null or p_status not in ('sent','failed','uncertain') or
    (p_status='sent' and length(coalesce(p_provider_id,'')) not between 1 and 512) then
    raise exception using errcode='22023',message='Resultado de alerta invalido.';
  end if;
  select * into v_alert from instagram_support.alerts where id=p_alert_id for update;
  if not found then return jsonb_build_object('changed',false,'reason','alert_missing'); end if;
  if v_alert.lease is distinct from p_lease then return jsonb_build_object('changed',false,'reason','lease'); end if;
  if v_alert.status<>'sending' then return jsonb_build_object('changed',false,'reason','already_final','status',v_alert.status); end if;
  if p_status='failed' and p_retryable and v_alert.attempts<2 and v_alert.created_at>now()-interval '23 hours' then v_status := 'retry_wait'; end if;
  update instagram_support.alerts set status=v_status,provider_id=case when p_status='sent' then p_provider_id else null end,
    error_code=case when p_status='sent' then null when p_status='uncertain' then 'delivery_unknown' else 'provider_rejected' end,
    next_attempt_at=case when v_status='retry_wait' then now()+interval '5 minutes' else null end,
    finished_at=case when v_status='retry_wait' then null else now() end where id=p_alert_id;
  return jsonb_build_object('changed',true,'status',v_status);
end;
$function$;

-- O cron executa como seu owner; service_role nao recebe acesso ao Vault.
-- A Edge Function precisa validar x-instagram-drain-secret. Nao usar anon key.
create or replace function instagram_support.nudge_worker()
returns void language plpgsql security invoker set search_path = pg_catalog, pg_temp
as $function$
declare v_secret text;
begin
  perform instagram_support.recover_expired();
  if not exists(select 1 from instagram_support.settings where singleton and cron_enabled and mode<>'off') then return; end if;
  if not (
    exists(select 1 from instagram_support.settings s where singleton and not paused and exists(select 1 from instagram_support.events where status='pending'))
    or exists(select 1 from instagram_support.settings s where singleton and alerts_enabled and manager_auth_user_id is not null
      and coalesce((select attempts from instagram_support.alert_months where month=date_trunc('month',now() at time zone 'America/Fortaleza')::date),0)<s.alerts_monthly_limit
      and exists(select 1 from instagram_support.alerts a join instagram_support.cases c on c.id=a.case_id
        where c.status='open' and c.created_at>=s.alerts_activation_after and (a.status='pending' or (a.status='retry_wait' and a.next_attempt_at<=now()))))
  ) then return; end if;
  select case when count(*)=1 then max(decrypted_secret) end into v_secret
    from vault.decrypted_secrets where name='instagram_support_drain_secret';
  if v_secret is null or length(v_secret)<32 then return; end if;
  perform net.http_post(url:='https://lucpxoynpvogkvzepagi.supabase.co/functions/v1/instagram-support/drain',
    headers:=jsonb_build_object('Content-Type','application/json','x-instagram-drain-secret',v_secret),body:='{}'::jsonb,timeout_milliseconds:=10000);
exception when others then
  raise warning 'Instagram worker nudge falhou (%).',sqlstate;
end;
$function$;

-- Retira o EXECUTE padrao de PUBLIC inclusive dos helpers privados.
revoke all on all functions in schema instagram_support from public, anon, authenticated, service_role;
grant execute on function instagram_support.pause_thread(uuid,text,text,uuid), instagram_support.settle_budget(uuid,integer,boolean),instagram_support.recover_expired() to service_role;
revoke all on function public.ig_support_settings(), public.ig_support_ingest(jsonb), public.ig_support_claim(uuid,integer),
  public.ig_support_reserve_budget(uuid,uuid,integer), public.ig_support_complete(uuid,uuid,jsonb), public.ig_support_prepare_send(uuid,uuid,text,bigint),
  public.ig_support_finish_send(uuid,uuid,text,text), public.ig_support_control(text,uuid,jsonb),
  public.ig_support_claim_alerts(uuid,integer),public.ig_support_finish_alert(uuid,uuid,text,text,boolean) from public, anon, authenticated;
grant execute on function public.ig_support_settings(), public.ig_support_ingest(jsonb), public.ig_support_claim(uuid,integer),
  public.ig_support_reserve_budget(uuid,uuid,integer), public.ig_support_complete(uuid,uuid,jsonb), public.ig_support_prepare_send(uuid,uuid,text,bigint),
  public.ig_support_finish_send(uuid,uuid,text,text), public.ig_support_control(text,uuid,jsonb),
  public.ig_support_claim_alerts(uuid,integer),public.ig_support_finish_alert(uuid,uuid,text,text,boolean) to service_role;

do $cron$
declare v_job bigint;
begin
  if to_regnamespace('cron') is null then return; end if;
  if exists(select 1 from cron.job where jobname='sirfisher-instagram-support-drain' and username<>current_user) then
    raise exception 'Job Instagram existente de outro owner; revisar antes de instalar.';
  end if;
  if not exists(select 1 from cron.job where jobname='sirfisher-instagram-support-drain') then
    v_job := cron.schedule('sirfisher-instagram-support-drain','* * * * *','select instagram_support.nudge_worker();');
    perform cron.alter_job(v_job,active:=false);
  end if;
end;
$cron$;

comment on schema instagram_support is 'Atendimento Instagram privado: RLS, RPCs service_role-only, sem tabelas de reservas ou financeiro.';
comment on table instagram_support.settings is 'Instalacao off/paused, modelo e faturamento bloqueados; nenhum segredo. Habilitar somente depois de testes e review Meta.';
comment on table instagram_support.outbox is 'sending e efeito externo de resultado potencialmente incerto; nunca reenviar automaticamente.';
comment on table instagram_support.budget_reservations is 'Reserva antes de Gemini; erro/metadata ausente cobra reserva inteira. Limite exclusivo desta integracao.';
notify pgrst, 'reload schema';
commit;
