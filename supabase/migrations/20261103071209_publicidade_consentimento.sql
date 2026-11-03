-- Publicidade opcional por reserva. GA4 estatistico e regras operacionais preservados.
-- O comprovante aleatorio permite revogar envios futuros no mesmo navegador.
create schema if not exists private;
create table if not exists private.advertising_revocations (
  receipt uuid primary key,
  revoked_at timestamptz not null default now()
);
alter table private.advertising_revocations enable row level security;
revoke all on private.advertising_revocations from public, anon, authenticated;
grant select on private.advertising_revocations to service_role;
alter table public.reservations
  add column if not exists advertising_consent_receipt uuid,
  add column if not exists advertising_consent_at timestamptz,
  add column if not exists advertising_consent_version text;
comment on column public.reservations.advertising_consent_receipt is
  'Comprovante aleatorio de publicidade opcional; ausente significa sem autorizacao. Nao e o opt-in de mensagens.';

create or replace function private.advertising_allowed(p_receipt uuid, p_at timestamptz)
returns boolean language sql stable security definer set search_path = pg_catalog, private
as $$ select p_receipt is not null and p_at > now() - interval '180 days' and p_at <= now() + interval '5 minutes'
  and not exists (select 1 from private.advertising_revocations v where v.receipt = p_receipt) $$;
revoke all on function private.advertising_allowed(uuid,timestamptz) from public, anon, authenticated;

create or replace function public.fn_revoke_advertising_consent(p_receipt uuid)
returns boolean language plpgsql security definer set search_path = pg_catalog, private, public
as $$
begin
  if p_receipt is null then return false; end if;
  insert into private.advertising_revocations(receipt) values(p_receipt) on conflict do nothing;
  update public.ad_conversion_events e set status='failed', attempts=10,
    last_error='advertising_consent_revoked'
  from public.reservations r
  where r.id=e.reservation_id and r.advertising_consent_receipt=p_receipt
    and e.provider in ('meta','openai_ads') and e.status in ('pending','failed','processing');
  return true;
end $$;
revoke all on function public.fn_revoke_advertising_consent(uuid) from public;
-- Unica operacao anonima nova: revoga pelo comprovante imprevisivel, sem ler clientes.
grant execute on function public.fn_revoke_advertising_consent(uuid) to anon, authenticated, service_role;

create or replace function public.fn_advertising_event_allowed(p_queue_id uuid)
returns boolean language sql stable security definer set search_path = pg_catalog, public, private
as $$ select exists (select 1 from public.ad_conversion_events e join public.reservations r on r.id=e.reservation_id
  where e.id=p_queue_id and e.provider in ('meta','openai_ads')
  and private.advertising_allowed(r.advertising_consent_receipt,r.advertising_consent_at)) $$;
revoke all on function public.fn_advertising_event_allowed(uuid) from public, anon, authenticated;
grant execute on function public.fn_advertising_event_allowed(uuid) to service_role;


CREATE OR REPLACE FUNCTION public.fn_create_reservation(p_name text, p_email text, p_phone text, p_date date, p_time time without time zone, p_party_size integer, p_attribution jsonb DEFAULT '{}'::jsonb, p_notes text DEFAULT NULL::text, p_marketing_opt_in boolean DEFAULT false, p_accepted_policy boolean DEFAULT false, p_honeypot text DEFAULT NULL::text, p_internal_notes text DEFAULT NULL::text)
 RETURNS TABLE(id uuid, public_code text, cancellation_token text, reservation_date date, reservation_time time without time zone, party_size integer, status text)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare
  v_is_staff boolean;
  v_actor_app_user_id uuid;
  v_source text;
  v_min_party int;
  v_max_party int;
  v_cutoff time;
  v_advance_days int;
  v_duration_minutes int;
  v_pre_buffer_minutes int;
  v_weekday int;
  v_rule public.availability_rules%rowtype;
  v_people_booked int;
  v_reservations_booked int;
  v_customer_id uuid;
  v_public_code text;
  v_token text;
  v_token_hash text;
  v_reservation_id uuid;
  v_recent_count int;
  v_phone_digits text;
  v_oppref text;
  v_utm_source text;
  v_utm_medium text;
  v_utm_campaign text;
  v_utm_content text;
  v_utm_term text;
  v_campaign_id text;
  v_ad_group_id text;
  v_ad_id text;
  v_landing_url text;
  v_referrer text;
  v_ga_client_id text;
  v_ga_session_id text;
  v_meta_fbp text;
  v_meta_fbc text;
  v_captured_at timestamptz;
  v_lang text;
  v_ads_receipt uuid;
  v_ads_at timestamptz;
begin
  if p_honeypot is not null and length(trim(p_honeypot)) > 0 then
    raise exception 'HONEYPOT: Não foi possível concluir sua reserva.';
  end if;

  select au.id into v_actor_app_user_id from public.app_users au
  where au.auth_user_id = auth.uid() and au.active = true;
  v_is_staff := v_actor_app_user_id is not null;
  v_source := case when v_is_staff then 'admin' else 'public_site' end;

  if p_name is null or length(trim(p_name)) = 0 then
    raise exception 'INVALID_INPUT: Informe o nome.';
  end if;
  if length(p_name) > 120 then
    raise exception 'INVALID_INPUT: Nome muito longo.';
  end if;
  if p_email is null or p_email !~* '^[^@\s]+@[^@\s]+\.[^@\s]+$' then
    raise exception 'INVALID_INPUT: Informe um e-mail válido.';
  end if;
  if p_phone is null or length(trim(p_phone)) < 8 then
    raise exception 'INVALID_INPUT: Informe um telefone válido.';
  end if;
  if not p_accepted_policy then
    raise exception 'INVALID_INPUT: É necessário aceitar as regras da reserva.';
  end if;
  if p_notes is not null and length(p_notes) > 500 then
    raise exception 'INVALID_INPUT: Observação muito longa.';
  end if;
  if p_party_size is null or p_party_size <= 0 or p_party_size > 1000 then
    raise exception 'INVALID_PARTY_SIZE: Quantidade de pessoas inválida.';
  end if;

  if p_attribution is null or jsonb_typeof(p_attribution) <> 'object' then
    p_attribution := '{}'::jsonb;
  end if;
  v_oppref := nullif(trim(p_attribution->>'oppref'), '');
  v_utm_source := nullif(trim(p_attribution->>'utm_source'), '');
  v_utm_medium := nullif(trim(p_attribution->>'utm_medium'), '');
  v_utm_campaign := nullif(trim(p_attribution->>'utm_campaign'), '');
  v_utm_content := nullif(trim(p_attribution->>'utm_content'), '');
  v_utm_term := nullif(trim(p_attribution->>'utm_term'), '');
  v_campaign_id := nullif(trim(p_attribution->>'campaign_id'), '');
  v_ad_group_id := nullif(trim(p_attribution->>'ad_group_id'), '');
  v_ad_id := nullif(trim(p_attribution->>'ad_id'), '');
  v_landing_url := nullif(trim(p_attribution->>'landing_url'), '');
  v_referrer := nullif(trim(p_attribution->>'referrer'), '');
  v_ga_client_id := nullif(trim(p_attribution->>'ga_client_id'), '');
  v_ga_session_id := nullif(trim(p_attribution->>'ga_session_id'), '');

  -- Identificadores do GA4 sao curtos por natureza ("1393530077.1788738227").
  -- Truncar em vez de rejeitar: um valor estranho no cookie nao pode derrubar
  -- uma reserva legitima.
  v_meta_fbp := nullif(trim(p_attribution->>'meta_fbp'), '');
  v_meta_fbc := nullif(trim(p_attribution->>'meta_fbc'), '');

  v_ga_client_id := left(v_ga_client_id, 64);
  v_ga_session_id := left(v_ga_session_id, 64);
  v_referrer := left(v_referrer, 2000);
  v_meta_fbp := left(v_meta_fbp, 255);
  v_meta_fbc := left(v_meta_fbc, 512);

  -- Autorizacao opcional da janela de publicidade; nao altera regras da reserva.
  if p_attribution->'advertising_consent' = 'true'::jsonb
    and p_attribution->>'advertising_consent_version' = '2026-11-03' then
    begin
      v_ads_receipt := (p_attribution->>'advertising_consent_receipt')::uuid;
      v_ads_at := (p_attribution->>'advertising_consent_at')::timestamptz;
    exception when invalid_text_representation or invalid_datetime_format or datetime_field_overflow then
      v_ads_receipt := null; v_ads_at := null;
    end;
    if not coalesce(private.advertising_allowed(v_ads_receipt,v_ads_at),false) then
      v_ads_receipt := null;
    end if;
  end if;
  v_landing_url := regexp_replace(v_landing_url, '[?#].*$', '');
  v_referrer := regexp_replace(v_referrer, '[?#].*$', '');
  if v_ads_receipt is null then
    v_oppref := null; v_meta_fbp := null; v_meta_fbc := null;
    v_campaign_id := null; v_ad_group_id := null; v_ad_id := null;
  end if;


  -- Idioma em que o cliente reservou (portal em ingles envia lang=en). So
  -- 'pt' ou 'en': qualquer outro valor vira 'pt'.
  v_lang := case when lower(left(trim(coalesce(p_attribution->>'lang', '')), 2)) = 'en' then 'en' else 'pt' end;

  if coalesce(length(v_oppref), 0) > 1024
    or greatest(coalesce(length(v_utm_source), 0), coalesce(length(v_utm_medium), 0),
      coalesce(length(v_utm_campaign), 0), coalesce(length(v_utm_content), 0),
      coalesce(length(v_utm_term), 0), coalesce(length(v_campaign_id), 0),
      coalesce(length(v_ad_group_id), 0), coalesce(length(v_ad_id), 0)) > 255
    or coalesce(length(v_landing_url), 0) > 2000 then
    raise exception 'INVALID_INPUT: Dados de origem invalidos.';
  end if;

  begin
    v_captured_at := nullif(trim(p_attribution->>'captured_at'), '')::timestamptz;
  exception when invalid_datetime_format then
    v_captured_at := null;
  end;

  if not v_is_staff then
    p_internal_notes := null;
  elsif p_internal_notes is not null and length(p_internal_notes) > 2000 then
    raise exception 'INVALID_INPUT: Observação interna muito longa.';
  end if;

  select
    coalesce((select value from public.restaurant_settings where key = 'min_party_size') #>> '{}', '2')::int,
    coalesce((select value from public.restaurant_settings where key = 'max_party_size') #>> '{}', '10')::int,
    coalesce((select value from public.restaurant_settings where key = 'same_day_cutoff_time') #>> '{}', '12:00')::time,
    coalesce((select value from public.restaurant_settings where key = 'advance_booking_days') #>> '{}', '60')::int,
    coalesce((select value from public.restaurant_settings where key = 'table_duration_minutes') #>> '{}', '120')::int,
    coalesce((select value from public.restaurant_settings where key = 'pre_buffer_minutes') #>> '{}', '60')::int
  into v_min_party, v_max_party, v_cutoff, v_advance_days, v_duration_minutes, v_pre_buffer_minutes;

  if not v_is_staff then
    if p_party_size < v_min_party then
      raise exception 'INVALID_PARTY_SIZE: A quantidade mínima é de % pessoas.', v_min_party;
    end if;
    if p_party_size > v_max_party then
      raise exception 'PARTY_TOO_LARGE: Para grupos acima de % pessoas, fale conosco pelo WhatsApp.', v_max_party;
    end if;
    if p_date < current_date or p_date > current_date + v_advance_days then
      raise exception 'DATE_NOT_ALLOWED: Não é possível reservar para essa data.';
    end if;
    if p_date = current_date and localtime > v_cutoff then
      raise exception 'SAME_DAY_CUTOFF: Reservas para o mesmo dia são aceitas somente até %. Após esse horário, o atendimento funciona por ordem de chegada.', to_char(v_cutoff, 'HH24:MI');
    end if;

    v_phone_digits := regexp_replace(p_phone, '\D', '', 'g');
    select count(*) into v_recent_count
    from public.reservations
    where created_at > now() - interval '10 minutes'
      and (
        customer_email_snapshot = p_email::citext
        or regexp_replace(coalesce(customer_phone_snapshot, ''), '\D', '', 'g') = v_phone_digits
      );
    if v_recent_count >= 3 then
      raise exception 'DUPLICATE_REQUEST: Identificamos várias solicitações recentes com esses dados. Aguarde alguns minutos e tente novamente.';
    end if;
  else
    if p_date < current_date then
      raise exception 'DATE_NOT_ALLOWED: Não é possível reservar para uma data passada.';
    end if;
  end if;

  if exists (select 1 from public.blocked_dates where date = p_date and active = true) then
    raise exception 'DATE_BLOCKED: Este dia não está disponível para reservas.';
  end if;

  if exists (select 1 from public.blocked_time_slots where date = p_date and time_slot = p_time and active = true) then
    raise exception 'SLOT_BLOCKED: Este horário não está disponível nesta data.';
  end if;

  v_weekday := extract(dow from p_date);

  if not exists (select 1 from public.availability_rules where weekday = v_weekday and enabled = true) then
    raise exception 'DATE_NOT_ALLOWED: Não aceitamos reservas neste dia da semana.';
  end if;

  select * into v_rule from public.availability_rules
  where weekday = v_weekday and time_slot = p_time and enabled = true;

  if not found then
    raise exception 'SLOT_BLOCKED: Este horário não está disponível.';
  end if;

  -- Trava por dia inteiro: uma reserva pode afetar o cômputo de vários horários
  -- vizinhos ao mesmo tempo (janela de ocupação abaixo), então a serialização
  -- precisa ser por data, não mais só pelo horário exato.
  perform pg_advisory_xact_lock(hashtext(p_date::text));

  -- Mesma lógica de janela de ocupação (margem antes + duração depois) do
  -- get_available_time_slots, usando aritmética de timestamp para não quebrar
  -- perto da meia-noite.
  select coalesce(sum(res.party_size), 0), count(*)
    into v_people_booked, v_reservations_booked
  from public.reservations res
  where res.reservation_date = p_date
    and res.status = 'confirmada'
    and (p_date + p_time) between
        ((p_date + res.reservation_time) - (v_pre_buffer_minutes || ' minutes')::interval)
        and ((p_date + res.reservation_time) + (v_duration_minutes || ' minutes')::interval);

  if v_people_booked + p_party_size > v_rule.max_people then
    raise exception 'SLOT_FULL_PEOPLE: Este horário já atingiu o limite de pessoas.';
  end if;
  if v_reservations_booked + 1 > v_rule.max_reservations then
    raise exception 'SLOT_FULL_RESERVATIONS: Este horário já atingiu o limite de reservas.';
  end if;

  v_phone_digits := regexp_replace(p_phone, '\D', '', 'g');

  select c.id into v_customer_id from public.customers c
  where regexp_replace(coalesce(c.phone, ''), '\D', '', 'g') = v_phone_digits and v_phone_digits <> ''
  limit 1;

  if v_customer_id is null and p_email is not null then
    select c.id into v_customer_id from public.customers c
    where c.email = p_email::citext
    limit 1;
  end if;

  if v_customer_id is null then
    insert into public.customers (name, email, phone, marketing_opt_in, marketing_opt_in_at, first_reservation_at, last_reservation_at)
    values (p_name, p_email, p_phone, p_marketing_opt_in, case when p_marketing_opt_in then now() else null end, now(), now())
    returning customers.id into v_customer_id;
  else
    update public.customers set
      name = p_name,
      email = coalesce(p_email, email),
      phone = coalesce(p_phone, phone),
      marketing_opt_in = marketing_opt_in or p_marketing_opt_in,
      marketing_opt_in_at = case when p_marketing_opt_in and marketing_opt_in_at is null then now() else marketing_opt_in_at end,
      last_reservation_at = now()
    where customers.id = v_customer_id;
  end if;

  loop
    v_public_code := 'SF-' || upper(substr(encode(extensions.gen_random_bytes(4), 'hex'), 1, 6));
    exit when not exists (select 1 from public.reservations rc where rc.public_code = v_public_code);
  end loop;

  v_token := encode(extensions.gen_random_bytes(32), 'base64');
  v_token := replace(replace(replace(v_token, '/', '_'), '+', '-'), '=', '');
  v_token_hash := encode(extensions.digest(v_token, 'sha256'), 'hex');

  insert into public.reservations (
    public_code, customer_id, customer_name_snapshot, customer_email_snapshot, customer_phone_snapshot,
    reservation_date, reservation_time, party_size, status, customer_notes, internal_notes,
    cancellation_token_hash, source, openai_oppref, utm_source, utm_medium, utm_campaign,
    utm_content, utm_term, chatgpt_campaign_id, chatgpt_ad_group_id, chatgpt_ad_id,
    attribution_landing_url, attribution_captured_at, attribution_referrer,
    ga_client_id, ga_session_id, meta_fbp, meta_fbc,
    created_by_user_id, accepted_policy, marketing_opt_in, customer_language,
    advertising_consent_receipt, advertising_consent_at, advertising_consent_version
  ) values (
    v_public_code, v_customer_id, p_name, p_email, p_phone,
    p_date, p_time, p_party_size, 'confirmada', p_notes, p_internal_notes,
    v_token_hash, v_source, v_oppref, v_utm_source, v_utm_medium, v_utm_campaign,
    v_utm_content, v_utm_term, v_campaign_id, v_ad_group_id, v_ad_id,
    v_landing_url, v_captured_at, v_referrer,
    v_ga_client_id, v_ga_session_id, v_meta_fbp, v_meta_fbc,
    v_actor_app_user_id, p_accepted_policy, p_marketing_opt_in, v_lang,
    v_ads_receipt, case when v_ads_receipt is not null then v_ads_at end,
    case when v_ads_receipt is not null then '2026-11-03' end
  ) returning reservations.id into v_reservation_id;

  -- Enfileira a confirmação por e-mail (enviada pela Edge Function send-notifications).
  -- O token de cancelamento vai no payload para montar o link "Cancelar reserva" no
  -- e-mail. Só o hash fica em reservations; o token cru existe aqui até o envio.
  -- A fila é admin/service_role apenas (ver rls.sql), inacessível ao anon.
  insert into public.notification_queue (reservation_id, type, channel, status, payload)
  values (
    v_reservation_id, 'reservation_confirmation', 'email', 'pending',
    jsonb_build_object(
      'public_code', v_public_code, 'name', p_name, 'email', p_email,
      'date', p_date, 'time', p_time, 'party_size', p_party_size,
      'cancel_token', v_token, 'lang', v_lang
    )
  );

  return query select
    r.id, r.public_code, v_token, r.reservation_date, r.reservation_time, r.party_size, r.status
  from public.reservations r where r.id = v_reservation_id;
end;
$function$
;

CREATE OR REPLACE FUNCTION public.fn_enqueue_meta_schedule()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
begin
  if new.source = 'public_site'
    and private.advertising_allowed(new.advertising_consent_receipt,new.advertising_consent_at) then
    insert into public.ad_conversion_events (reservation_id, provider, event_name, event_id)
    values (new.id, 'meta', 'schedule', 'sf-sched-' || new.id::text)
    on conflict (reservation_id, provider, event_name) do nothing;
  end if;
  return new;
end;
$function$
;
revoke all on function public.fn_enqueue_meta_schedule() from public, anon, authenticated;

CREATE OR REPLACE FUNCTION public.fn_enqueue_openai_ads_schedule()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
begin
  if new.source = 'public_site' and new.accepted_policy
    and private.advertising_allowed(new.advertising_consent_receipt,new.advertising_consent_at) then
    insert into public.ad_conversion_events (reservation_id, provider, event_name, event_id)
    values (new.id, 'openai_ads', 'schedule', 'sf-oai-sched-' || new.id::text)
    on conflict (reservation_id, provider, event_name) do nothing;
  end if;
  return new;
end;
$function$
;
revoke all on function public.fn_enqueue_openai_ads_schedule() from public, anon, authenticated;

CREATE OR REPLACE FUNCTION public.fn_enqueue_openai_ads_visit()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
begin
  if new.status = 'compareceu'
    and old.status is distinct from new.status
    and new.openai_oppref is not null
    and private.advertising_allowed(new.advertising_consent_receipt,new.advertising_consent_at) then
    insert into public.ad_conversion_events (reservation_id, provider, event_name, event_id)
    values (new.id, 'openai_ads', 'visit_realized', 'sf-vr-' || new.id::text)
    on conflict (reservation_id, provider, event_name) do nothing;
  end if;
  return new;
end;
$function$
;
revoke all on function public.fn_enqueue_openai_ads_visit() from public, anon, authenticated;

CREATE OR REPLACE FUNCTION public.fn_claim_pending_meta_conversions(p_limit integer DEFAULT 25)
 RETURNS TABLE(queue_id uuid, event_id text, email text, phone text, fbp text, fbc text, party_size integer, landing_url text, occurred_at timestamp with time zone)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
begin
  return query
  with candidates as (
    select e.id from public.ad_conversion_events e
    where e.provider = 'meta' and e.status in ('pending', 'failed') and e.attempts < 10
      and exists (select 1 from public.reservations r where r.id=e.reservation_id
        and private.advertising_allowed(r.advertising_consent_receipt,r.advertising_consent_at))
    order by e.created_at
    limit greatest(1, least(coalesce(p_limit, 25), 1000))
    for update skip locked
  )
  update public.ad_conversion_events e
  set status = 'processing', attempts = e.attempts + 1, last_attempt_at = now(), last_error = null
  from public.reservations r
  where e.id in (select id from candidates) and r.id = e.reservation_id
  returning e.id, e.event_id, r.customer_email_snapshot::text, r.customer_phone_snapshot,
            r.meta_fbp, r.meta_fbc, r.party_size, r.attribution_landing_url, e.created_at;
end;
$function$
;
revoke all on function public.fn_claim_pending_meta_conversions(integer) from public, anon, authenticated;
grant execute on function public.fn_claim_pending_meta_conversions(integer) to service_role;

CREATE OR REPLACE FUNCTION public.fn_claim_pending_openai_ads_conversions(p_limit integer DEFAULT 25)
 RETURNS TABLE(queue_id uuid, event_id text, event_name text, oppref text, email text, phone text, external_id text, party_size integer, landing_url text, occurred_at timestamp with time zone)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
begin
  return query
  with candidates as (
    select e.id
    from public.ad_conversion_events e
    where e.provider = 'openai_ads'
      and e.status in ('pending', 'failed')
      and e.attempts < 10
      and exists (select 1 from public.reservations r where r.id=e.reservation_id
        and private.advertising_allowed(r.advertising_consent_receipt,r.advertising_consent_at))
    order by e.created_at
    limit greatest(1, least(coalesce(p_limit, 25), 1000))
    for update skip locked
  )
  update public.ad_conversion_events e
  set status = 'processing',
      attempts = e.attempts + 1,
      last_attempt_at = now(),
      last_error = null
  from public.reservations r
  where e.id in (select id from candidates)
    and r.id = e.reservation_id
  returning e.id,
            e.event_id,
            e.event_name,
            r.openai_oppref,
            r.customer_email_snapshot::text,
            r.customer_phone_snapshot,
            r.customer_id::text,
            r.party_size,
            r.attribution_landing_url,
            e.created_at;
end;
$function$
;
revoke all on function public.fn_claim_pending_openai_ads_conversions(integer) from public, anon, authenticated;
grant execute on function public.fn_claim_pending_openai_ads_conversions(integer) to service_role;

-- Reservas anteriores nao receberam a nova escolha. Impede retry publicitario,
-- mantendo o historico e a fila GA4. Nenhuma reserva ou mensagem operacional e removida.
update public.ad_conversion_events e set status='failed', attempts=10,
 last_error='advertising_consent_required'
from public.reservations r where r.id=e.reservation_id
 and e.provider in ('meta','openai_ads') and e.status in ('pending','failed','processing')
 and r.advertising_consent_receipt is null;
notify pgrst, 'reload schema';
