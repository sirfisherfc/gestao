begin;

-- Código curto vira a identificação exibida. O código anterior permanece como alias.
alter table private.benefit_vouchers add column if not exists short_code text;
alter table private.benefit_vouchers drop constraint if exists benefit_vouchers_short_code_check;
alter table private.benefit_vouchers add constraint benefit_vouchers_short_code_check check(short_code ~ '^[0-9A-HJKMNP-TV-Z]{6}$');
create unique index if not exists benefit_vouchers_short_code_idx on private.benefit_vouchers(short_code);

create or replace function private.bv_assign_short_code() returns trigger
language plpgsql volatile security invoker set search_path=pg_catalog,pg_temp as $$
declare v_code text; v_bytes bytea; i integer; j integer;
begin
  if tg_op='UPDATE' and old.short_code is not null and new.short_code is distinct from old.short_code then
    raise exception 'O código do voucher não pode ser alterado.' using errcode='22023';
  end if;
  if new.short_code is not null then return new; end if;
  for i in 1..10 loop
    v_bytes:=extensions.gen_random_bytes(6);v_code:='';
    for j in 0..5 loop v_code:=v_code||substr('0123456789ABCDEFGHJKMNPQRSTVWXYZ',(get_byte(v_bytes,j)&31)+1,1);end loop;
    if not exists(select 1 from private.benefit_vouchers where short_code=v_code) then
      new.short_code:=v_code;return new;
    end if;
  end loop;
  raise exception 'Não foi possível gerar um código curto. Tente novamente.';
end;
$$;
revoke all on function private.bv_assign_short_code() from public,anon,authenticated,service_role;
drop trigger if exists benefit_voucher_assign_short_code on private.benefit_vouchers;
create trigger benefit_voucher_assign_short_code before insert or update of short_code on private.benefit_vouchers
  for each row execute function private.bv_assign_short_code();
do $migration$
declare v_id uuid;
begin
  for v_id in select id from private.benefit_vouchers where short_code is null loop
    update private.benefit_vouchers set short_code=null where id=v_id;
  end loop;
end;
$migration$;
alter table private.benefit_vouchers alter column short_code set not null;

create or replace function private.bv_payload(p_v private.benefit_vouchers,p_internal boolean default false) returns jsonb
language sql volatile set search_path=pg_catalog,pg_temp as $$
  select jsonb_build_object('id',p_v.id,'revision',p_v.revision,'code',p_v.short_code,
    'legacy_code','SF-'||substr(p_v.code,1,4)||'-'||substr(p_v.code,5,4)||'-'||substr(p_v.code,9,4),
    'beneficiary_name',p_v.beneficiary_name,'benefit_type',p_v.benefit_type,'benefit_value',p_v.benefit_value,
    'expires_on',p_v.expires_on,'status',private.bv_status(p_v),'conditions',p_v.conditions,'unit_name',p_v.unit_name,
    'created_at',p_v.created_at,'used_at',p_v.used_at,'used_by_name',p_v.used_by_name,'cancelled_at',p_v.cancelled_at)
    || case when p_internal then jsonb_build_object('phone',p_v.phone,'internal_note',p_v.internal_note,
      'issued_by_name',p_v.issued_by_name,'cancelled_by_name',p_v.cancelled_by_name,'cancellation_reason',p_v.cancellation_reason,
      'issue_reason',p_v.issue_reason,'issue_reason_detail',p_v.issue_reason_detail) else '{}'::jsonb end;
$$;
revoke all on function private.bv_payload(private.benefit_vouchers,boolean) from public,anon,authenticated,service_role;

create or replace function private.benefit_voucher_lookup(p_code text) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers;v_code text;v_payload jsonb;
begin
  if not(private.bv_can_redeem() or private.bv_can_manage()) then raise exception 'Acesso não permitido.' using errcode='42501';end if;
  if not private.bv_rate_limit('lookup',30) then return jsonb_build_object('ok',false,'reason','rate_limited');end if;
  if p_code is null or char_length(p_code)>40 then return jsonb_build_object('ok',false,'reason','invalid_code');end if;
  v_code:=regexp_replace(upper(btrim(p_code)),'[[:space:]-]','','g');
  if left(v_code,2)='SF' and char_length(v_code)=14 then v_code:=substr(v_code,3);end if;
  v_code:=translate(v_code,'OIL','011');
  if v_code ~ '^[0-9A-HJKMNP-TV-Z]{6}$' then
    select * into v from private.benefit_vouchers where short_code=v_code;
  elsif v_code ~ '^[0-9A-HJKMNP-TV-Z]{12}$' then
    select * into v from private.benefit_vouchers where code=v_code;
  else return jsonb_build_object('ok',false,'reason','invalid_code');end if;
  if not found then return jsonb_build_object('ok',false,'reason','not_found');end if;
  v_payload:=private.bv_payload(v);
  -- Páginas antigas ainda entendem a resposta do código longo que consultaram.
  if char_length(v_code)=12 then
    v_payload:=v_payload||jsonb_build_object('short_code',v.short_code,'code',v_payload->>'legacy_code');
  end if;
  return jsonb_build_object('ok',true,'voucher',v_payload);
end;
$$;

-- Inclui o alias antigo na busca da gestão sem mudar os gates ou os filtros.
do $migration$
declare v_definition text;v_old text:=$old$||(private.bv_payload(v)->>'code')$old$;
begin
  select pg_get_functiondef('private.benefit_voucher_list(text,text,integer,integer,text)'::regprocedure) into v_definition;
  if position($marker$->>'legacy_code'$marker$ in v_definition)=0 then
    if position(v_old in v_definition)=0 then raise exception 'Busca de vouchers inesperada.';end if;
    execute replace(v_definition,v_old,v_old||$new$||' '||(private.bv_payload(v)->>'legacy_code')$new$);
  end if;
end;
$migration$;

create or replace function private.benefit_voucher_redeem(p_id uuid,p_confirm boolean) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select case when r.data->'voucher' is not null then jsonb_set(r.data,'{voucher,code}',r.data#>'{voucher,legacy_code}') else r.data end
    from (select private.benefit_voucher_redeem(p_id,p_confirm,null) as data) r;
$$;
revoke all on function private.benefit_voucher_lookup(text),private.benefit_voucher_list(text,text,integer,integer,text),private.benefit_voucher_redeem(uuid,boolean)
  from public,anon,authenticated,service_role;
grant execute on function private.benefit_voucher_lookup(text),private.benefit_voucher_list(text,text,integer,integer,text),private.benefit_voucher_redeem(uuid,boolean)
  to authenticated;
notify pgrst,'reload schema';
commit;
