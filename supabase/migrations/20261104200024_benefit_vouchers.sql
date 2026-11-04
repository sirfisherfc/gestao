begin;

-- Vouchers de benefício: objetos novos e privados, sem relação com rv_bookings.
-- Regras confirmadas pelo proprietário em 04/11/2026. Escrita somente por RPC.
create table if not exists private.benefit_vouchers (
  id uuid primary key default gen_random_uuid(),
  request_id uuid not null unique,
  code text not null unique check (code ~ '^[0-9A-HJKMNP-TV-Z]{12}$'),
  beneficiary_name text not null check (char_length(btrim(beneficiary_name)) between 1 and 160),
  phone text not null check (phone ~ '^[0-9]{10,15}$'),
  benefit_type text not null check (benefit_type in ('fixed','percent')),
  benefit_value numeric(12,2) not null check (benefit_value > 0 and benefit_value <> 'NaN'::numeric),
  expires_on date not null,
  internal_note text check (char_length(internal_note) <= 2000),
  issue_reason text not null check (issue_reason in ('recovery','friend','commercial','photo_production','staff_birthday','loyalty','promotion','influencer','other')),
  issue_reason_detail text check (char_length(issue_reason_detail) <= 1000),
  constraint benefit_voucher_reason_detail check (issue_reason <> 'other' or char_length(btrim(issue_reason_detail)) >= 3 and issue_reason_detail is not null),
  conditions text[] not null,
  unit_name text not null default 'Sir Fisher',
  created_at timestamptz not null default clock_timestamp(),
  issued_by uuid not null,
  issued_by_name text not null,
  used_at timestamptz,
  used_by uuid,
  used_by_name text,
  cancelled_at timestamptz,
  cancelled_by uuid,
  cancelled_by_name text,
  cancellation_reason text,
  constraint benefit_voucher_percent_range check (benefit_type <> 'percent' or benefit_value <= 100),
  constraint benefit_voucher_state check (
    (used_at is null and used_by is null and used_by_name is null or
     used_at is not null and used_by is not null and used_by_name is not null)
    and (cancelled_at is null and cancelled_by is null and cancelled_by_name is null and cancellation_reason is null or
     cancelled_at is not null and cancelled_by is not null and cancelled_by_name is not null and cancellation_reason is not null)
    and not (used_at is not null and cancelled_at is not null)
  )
);
create index if not exists benefit_vouchers_created_idx on private.benefit_vouchers(created_at desc,id);
create index if not exists benefit_vouchers_expiry_idx on private.benefit_vouchers(expires_on) where used_at is null and cancelled_at is null;

create table if not exists private.benefit_voucher_events (
  id bigint generated always as identity primary key,
  voucher_id uuid not null references private.benefit_vouchers(id),
  event_type text not null check (event_type in ('issued','used','cancelled')),
  occurred_at timestamptz not null default clock_timestamp(),
  actor_id uuid not null,
  actor_name text not null,
  reason text
);
create index if not exists benefit_voucher_events_voucher_idx on private.benefit_voucher_events(voucher_id,id);
create unique index if not exists benefit_voucher_single_use_idx on private.benefit_voucher_events(voucher_id) where event_type='used';
create table if not exists private.benefit_voucher_rate_limits (
  actor_id uuid not null,
  operation text not null,
  window_started timestamptz not null,
  attempts integer not null,
  primary key(actor_id,operation)
);
alter table private.benefit_vouchers enable row level security;
alter table private.benefit_voucher_events enable row level security;
alter table private.benefit_voucher_rate_limits enable row level security;
revoke all on private.benefit_vouchers,private.benefit_voucher_events,private.benefit_voucher_rate_limits from public,anon,authenticated,service_role;
revoke all on sequence private.benefit_voucher_events_id_seq from public,anon,authenticated,service_role;
-- Nenhum papel da Data API acessa tabelas: RPCs restritas fazem as operações.

create or replace function private.bv_can_manage() returns boolean
language sql stable security definer set search_path=pg_catalog,pg_temp as $$
  select auth.uid() is not null
    and public.usuario_tem_papel(array['admin','socio']::text[])
    and public.usuario_pode_acessar_pagina('vouchers.html');
$$;
create or replace function private.bv_can_redeem() returns boolean
language sql stable security definer set search_path=pg_catalog,pg_temp as $$
  select auth.uid() is not null and exists (
    select 1 from public.app_users where auth_user_id=auth.uid() and active and role in ('admin','operator')
  );
$$;
create or replace function private.bv_actor_name() returns text
language sql stable security definer set search_path=pg_catalog,pg_temp as $$
  select coalesce((select nullif(btrim(name),'') from public.app_users where auth_user_id=auth.uid() and active limit 1),
    nullif(private.nome_exibicao_usuario(auth.uid()),''),'Equipe Sir Fisher');
$$;
create or replace function private.bv_rate_limit(p_operation text,p_limit integer) returns boolean
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v_attempts integer; v_now timestamptz:=clock_timestamp();
begin
  if auth.uid() is null then return false; end if;
  insert into private.benefit_voucher_rate_limits(actor_id,operation,window_started,attempts)
  values(auth.uid(),p_operation,v_now,1)
  on conflict(actor_id,operation) do update set
    attempts=case when private.benefit_voucher_rate_limits.window_started <= v_now-interval '1 minute'
      then 1 else least(private.benefit_voucher_rate_limits.attempts+1,p_limit+1) end,
    window_started=case when private.benefit_voucher_rate_limits.window_started <= v_now-interval '1 minute'
      then v_now else private.benefit_voucher_rate_limits.window_started end
  returning attempts into v_attempts;
  return v_attempts<=p_limit;
end;
$$;
create or replace function private.bv_status(p_v private.benefit_vouchers) returns text
language sql volatile set search_path=pg_catalog,pg_temp as $$
  select case when p_v.used_at is not null then 'used' when p_v.cancelled_at is not null then 'cancelled'
    when p_v.expires_on < (clock_timestamp() at time zone 'America/Fortaleza')::date then 'expired' else 'available' end;
$$;
create or replace function private.bv_payload(p_v private.benefit_vouchers,p_internal boolean default false) returns jsonb
language sql volatile set search_path=pg_catalog,pg_temp as $$
  select jsonb_build_object('id',p_v.id,'code','SF-'||substr(p_v.code,1,4)||'-'||substr(p_v.code,5,4)||'-'||substr(p_v.code,9,4),
    'beneficiary_name',p_v.beneficiary_name,'benefit_type',p_v.benefit_type,'benefit_value',p_v.benefit_value,
    'expires_on',p_v.expires_on,'status',private.bv_status(p_v),'conditions',p_v.conditions,'unit_name',p_v.unit_name,
    'created_at',p_v.created_at,'used_at',p_v.used_at,'used_by_name',p_v.used_by_name,'cancelled_at',p_v.cancelled_at)
    || case when p_internal then jsonb_build_object('phone',p_v.phone,'internal_note',p_v.internal_note,
      'issued_by_name',p_v.issued_by_name,'cancelled_by_name',p_v.cancelled_by_name,'cancellation_reason',p_v.cancellation_reason,
      'issue_reason',p_v.issue_reason,'issue_reason_detail',p_v.issue_reason_detail) else '{}'::jsonb end;
$$;
revoke all on function private.bv_can_manage(),private.bv_can_redeem(),private.bv_actor_name(),private.bv_rate_limit(text,integer),
  private.bv_status(private.benefit_vouchers),private.bv_payload(private.benefit_vouchers,boolean) from public,anon,authenticated,service_role;

insert into public.pagina_permissao(pagina,papeis) values('vouchers.html',array['admin','socio']::text[])
on conflict(pagina) do nothing;

create or replace function public.benefit_voucher_issue(p_request_id uuid,p_beneficiary_name text,p_phone text,
  p_benefit_type text,p_benefit_value numeric,p_expires_on date,p_issue_reason text,p_issue_reason_detail text default null,p_internal_note text default null) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers; v_code text; v_bytes bytea; i integer; j integer;
  v_today date:=(clock_timestamp() at time zone 'America/Fortaleza')::date;
  v_conditions text[]:=array['Uso único. Saldo não utilizado é perdido.',
    'Não cumulativo com promoções ou outro voucher na mesma conta.','Válido na unidade Sir Fisher até a data indicada.'];
begin
  if not private.bv_can_manage() then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  if p_request_id is null then raise exception 'Identificador da emissão obrigatório.' using errcode='22023'; end if;
  select * into v from private.benefit_vouchers where request_id=p_request_id;
  if found then
    if v.issued_by<>auth.uid() then raise exception 'Identificador de emissão indisponível.' using errcode='22023'; end if;
    if row(v.beneficiary_name,v.phone,v.benefit_type,v.benefit_value,v.expires_on,v.issue_reason,v.issue_reason_detail,v.internal_note)
      is distinct from row(btrim(p_beneficiary_name),regexp_replace(p_phone,'[^0-9]','','g'),p_benefit_type,p_benefit_value,p_expires_on,
        p_issue_reason,nullif(btrim(p_issue_reason_detail),''),nullif(btrim(p_internal_note),'')) then
      return jsonb_build_object('ok',false,'reason','request_conflict','voucher',private.bv_payload(v,true));
    end if;
    return jsonb_build_object('ok',true,'voucher',private.bv_payload(v,true));
  end if;
  if not private.bv_rate_limit('issue',10) then return jsonb_build_object('ok',false,'reason','rate_limited'); end if;
  if p_beneficiary_name is null or char_length(btrim(p_beneficiary_name)) not between 1 and 160
    or p_phone is null or regexp_replace(p_phone,'[^0-9]','','g') !~ '^[0-9]{10,15}$'
    or p_benefit_type is null or p_benefit_type not in ('fixed','percent')
    or p_benefit_value is null or p_benefit_value<=0 or p_benefit_value='NaN'::numeric
    or p_benefit_value<>round(p_benefit_value,2) or p_benefit_value>9999999999.99
    or (p_benefit_type='percent' and p_benefit_value>100)
    or p_expires_on is null or p_expires_on<v_today or not isfinite(p_expires_on)
    or p_issue_reason is null or p_issue_reason not in ('recovery','friend','commercial','photo_production','staff_birthday','loyalty','promotion','influencer','other')
    or char_length(coalesce(p_issue_reason_detail,''))>1000
    or (p_issue_reason='other' and char_length(btrim(coalesce(p_issue_reason_detail,'')))<3)
    or char_length(coalesce(p_internal_note,''))>2000 then
    raise exception 'Confira nome, telefone, benefício e validade.' using errcode='22023';
  end if;
  if p_benefit_type='percent' then v_conditions:=array_prepend('Desconto sobre a conta inteira. Taxa de serviço opcional. Sem teto em reais.',v_conditions); end if;
  for i in 1..5 loop
    v_bytes:=extensions.gen_random_bytes(12); v_code:='';
    for j in 0..11 loop v_code:=v_code||substr('0123456789ABCDEFGHJKMNPQRSTVWXYZ',(get_byte(v_bytes,j)&31)+1,1); end loop;
    begin
      insert into private.benefit_vouchers(request_id,code,beneficiary_name,phone,benefit_type,benefit_value,expires_on,
        internal_note,issue_reason,issue_reason_detail,conditions,issued_by,issued_by_name)
      values(p_request_id,v_code,btrim(p_beneficiary_name),regexp_replace(p_phone,'[^0-9]','','g'),p_benefit_type,p_benefit_value,
        p_expires_on,nullif(btrim(p_internal_note),''),p_issue_reason,nullif(btrim(p_issue_reason_detail),''),v_conditions,auth.uid(),private.bv_actor_name()) returning * into v;
      insert into private.benefit_voucher_events(voucher_id,event_type,actor_id,actor_name,reason)
        values(v.id,'issued',auth.uid(),v.issued_by_name,p_issue_reason||coalesce(': '||nullif(btrim(p_issue_reason_detail),''),''));
      return jsonb_build_object('ok',true,'voucher',private.bv_payload(v,true));
    exception when unique_violation then
      select * into v from private.benefit_vouchers where request_id=p_request_id;
      if found then
        if v.issued_by<>auth.uid() then raise exception 'Identificador de emissão indisponível.' using errcode='22023'; end if;
        if row(v.beneficiary_name,v.phone,v.benefit_type,v.benefit_value,v.expires_on,v.issue_reason,v.issue_reason_detail,v.internal_note)
          is distinct from row(btrim(p_beneficiary_name),regexp_replace(p_phone,'[^0-9]','','g'),p_benefit_type,p_benefit_value,p_expires_on,
            p_issue_reason,nullif(btrim(p_issue_reason_detail),''),nullif(btrim(p_internal_note),'')) then
          return jsonb_build_object('ok',false,'reason','request_conflict','voucher',private.bv_payload(v,true));
        end if;
        return jsonb_build_object('ok',true,'voucher',private.bv_payload(v,true));
      end if;
    end;
  end loop;
  raise exception 'Não foi possível gerar o código. Tente novamente.';
end;
$$;

create or replace function public.benefit_voucher_list(p_search text default '',p_status text default '',p_offset integer default 0,p_limit integer default 50,p_reason text default '') returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v_rows jsonb; v_summary jsonb; v_count integer;
begin
  if not private.bv_can_manage() then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  if not private.bv_rate_limit('list',60) then return jsonb_build_object('ok',false,'reason','rate_limited'); end if;
  if p_search is null or char_length(p_search)>160 or p_status is null or p_status not in ('','available','used','expired','cancelled')
    or p_reason is null or p_reason not in ('','recovery','friend','commercial','photo_production','staff_birthday','loyalty','promotion','influencer','other')
    or p_offset is null or p_offset<0 or p_limit is null or p_limit not between 1 and 100 then raise exception 'Filtro inválido.' using errcode='22023'; end if;
  select jsonb_build_object('issued',count(*),'available',count(*) filter(where status='available'),
    'used',count(*) filter(where status='used'),'expired',count(*) filter(where status='expired'),
    'cancelled',count(*) filter(where status='cancelled'),
    'fixed_available_total',coalesce(sum(benefit_value) filter(where status='available' and benefit_type='fixed'),0),
    'percent_available_count',count(*) filter(where status='available' and benefit_type='percent')) into v_summary
    from (select benefit_value,benefit_type,private.bv_status(v) as status from private.benefit_vouchers v) s;
  select count(*) into v_count from private.benefit_vouchers v where (p_status='' or private.bv_status(v)=p_status) and (p_reason='' or v.issue_reason=p_reason)
    and (p_search='' or position(lower(p_search) in lower(v.beneficiary_name||' '||v.phone||' '||v.code||' '||(private.bv_payload(v)->>'code')))>0);
  select coalesce(jsonb_agg(row order by created_at desc,id desc),'[]'::jsonb) into v_rows from (
    select private.bv_payload(v,true) as row,v.created_at,v.id from private.benefit_vouchers v
    where (p_status='' or private.bv_status(v)=p_status) and (p_reason='' or v.issue_reason=p_reason)
      and (p_search='' or position(lower(p_search) in lower(v.beneficiary_name||' '||v.phone||' '||v.code||' '||(private.bv_payload(v)->>'code')))>0)
    order by v.created_at desc,v.id desc limit p_limit offset p_offset
  ) s;
  return jsonb_build_object('ok',true,'rows',v_rows,'total',v_count,'summary',v_summary);
end;
$$;

create or replace function public.benefit_voucher_detail(p_id uuid) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers; v_events jsonb;
begin
  if not private.bv_can_manage() then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  select * into v from private.benefit_vouchers where id=p_id;
  if not found then return jsonb_build_object('ok',false,'reason','not_found'); end if;
  select coalesce(jsonb_agg(jsonb_build_object('event_type',event_type,'occurred_at',occurred_at,'actor_name',actor_name,'reason',reason) order by id),'[]'::jsonb)
    into v_events from private.benefit_voucher_events where voucher_id=p_id;
  return jsonb_build_object('ok',true,'voucher',private.bv_payload(v,true),'events',v_events);
end;
$$;

create or replace function public.benefit_voucher_lookup(p_code text) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers; v_code text;
begin
  if not (private.bv_can_redeem() or private.bv_can_manage()) then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  if not private.bv_rate_limit('lookup',30) then return jsonb_build_object('ok',false,'reason','rate_limited'); end if;
  if p_code is null or char_length(p_code)>40 then return jsonb_build_object('ok',false,'reason','invalid_code'); end if;
  v_code:=regexp_replace(upper(btrim(p_code)),'[[:space:]-]','','g');
  if left(v_code,2)='SF' and char_length(v_code)=14 then v_code:=substr(v_code,3); end if;
  v_code:=translate(v_code,'OIL','011');
  if v_code !~ '^[0-9A-HJKMNP-TV-Z]{12}$' then return jsonb_build_object('ok',false,'reason','invalid_code'); end if;
  select * into v from private.benefit_vouchers where code=v_code;
  if not found then return jsonb_build_object('ok',false,'reason','not_found'); end if;
  return jsonb_build_object('ok',true,'voucher',private.bv_payload(v));
end;
$$;

create or replace function public.benefit_voucher_redeem(p_id uuid,p_confirm boolean) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers; v_status text; v_now timestamptz; v_actor text;
begin
  if not private.bv_can_redeem() then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  if p_confirm is distinct from true then raise exception 'Confirme explicitamente a utilização.' using errcode='22023'; end if;
  if not private.bv_rate_limit('redeem',20) then return jsonb_build_object('ok',false,'reason','rate_limited'); end if;
  select * into v from private.benefit_vouchers where id=p_id for update;
  if not found then return jsonb_build_object('ok',false,'reason','not_found'); end if;
  v_now:=clock_timestamp();
  v_status:=case when v.used_at is not null then 'used' when v.cancelled_at is not null then 'cancelled'
    when v.expires_on < (v_now at time zone 'America/Fortaleza')::date then 'expired' else 'available' end;
  if v_status<>'available' then return jsonb_build_object('ok',false,'reason',v_status,'voucher',private.bv_payload(v)); end if;
  -- Relógio é consultado depois do lock: uma espera cruzando meia-noite não usa validade antiga.
  v_actor:=private.bv_actor_name();
  update private.benefit_vouchers set used_at=v_now,used_by=auth.uid(),used_by_name=v_actor where id=p_id returning * into v;
  insert into private.benefit_voucher_events(voucher_id,event_type,occurred_at,actor_id,actor_name) values(p_id,'used',v_now,auth.uid(),v_actor);
  return jsonb_build_object('ok',true,'voucher',private.bv_payload(v));
end;
$$;

create or replace function public.benefit_voucher_cancel(p_id uuid,p_reason text,p_confirm boolean) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers; v_status text; v_now timestamptz; v_actor text;
begin
  if not private.bv_can_manage() then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  if p_confirm is distinct from true or p_reason is null or char_length(btrim(p_reason)) not between 3 and 500 then
    raise exception 'Confirme o cancelamento e informe o motivo.' using errcode='22023'; end if;
  select * into v from private.benefit_vouchers where id=p_id for update;
  if not found then return jsonb_build_object('ok',false,'reason','not_found'); end if;
  v_status:=private.bv_status(v);
  if v_status in ('used','cancelled') then return jsonb_build_object('ok',false,'reason',v_status,'voucher',private.bv_payload(v,true)); end if;
  v_now:=clock_timestamp(); v_actor:=private.bv_actor_name();
  update private.benefit_vouchers set cancelled_at=v_now,cancelled_by=auth.uid(),cancelled_by_name=v_actor,cancellation_reason=btrim(p_reason)
    where id=p_id returning * into v;
  insert into private.benefit_voucher_events(voucher_id,event_type,occurred_at,actor_id,actor_name,reason) values(p_id,'cancelled',v_now,auth.uid(),v_actor,btrim(p_reason));
  return jsonb_build_object('ok',true,'voucher',private.bv_payload(v,true));
end;
$$;

revoke all on function public.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),public.benefit_voucher_list(text,text,integer,integer,text),
  public.benefit_voucher_detail(uuid),public.benefit_voucher_lookup(text),public.benefit_voucher_redeem(uuid,boolean),
  public.benefit_voucher_cancel(uuid,text,boolean) from public,anon,authenticated,service_role;
grant execute on function public.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),public.benefit_voucher_list(text,text,integer,integer,text),
  public.benefit_voucher_detail(uuid),public.benefit_voucher_lookup(text),public.benefit_voucher_redeem(uuid,boolean),
  public.benefit_voucher_cancel(uuid,text,boolean) to authenticated;
comment on table private.benefit_vouchers is 'Vouchers de benefício de uso único. Sem acesso direto da Data API; não são reservas de Réveillon.';
comment on function public.benefit_voucher_redeem(uuid,boolean) is 'Equipe ativa; confirmação explícita, lock da linha, uso e auditoria na mesma transação. Validade inclusiva em Fortaleza.';
notify pgrst,'reload schema';
commit;
