begin;

create index if not exists benefit_vouchers_used_at_idx on private.benefit_vouchers(used_at desc,id desc) where used_at is not null;

create or replace function private.benefit_voucher_recent(p_offset integer default 0,p_limit integer default 20) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v_now timestamptz:=clock_timestamp(); v_today date; v_from timestamptz; v_result jsonb;
begin
  if not private.bv_can_redeem() then raise exception 'Acesso não permitido.' using errcode='42501';end if;
  if p_offset is null or p_offset<0 or p_limit is null or p_limit not between 1 and 100 then
    raise exception 'Página inválida.' using errcode='22023';
  end if;
  if not private.bv_rate_limit('recent',60) then return jsonb_build_object('ok',false,'reason','rate_limited');end if;
  v_today:=(v_now at time zone 'America/Fortaleza')::date;
  v_from:=(v_today-2)::timestamp at time zone 'America/Fortaleza';
  with eligible as materialized (
    select id,short_code,beneficiary_name,benefit_type,benefit_value,used_at,used_by_name
    from private.benefit_vouchers where used_at>=v_from and used_at<=v_now
  ), page as (
    select * from eligible order by used_at desc,id desc limit p_limit offset p_offset
  )
  select jsonb_build_object('ok',true,'from_date',v_today-2,'through_date',v_today,
    'total',(select count(*) from eligible),
    'items',(select coalesce(jsonb_agg(jsonb_build_object('code',short_code,'beneficiary_name',beneficiary_name,
      'benefit_type',benefit_type,'benefit_value',benefit_value,'used_at',used_at,'used_by_name',used_by_name)
      order by used_at desc,id desc),'[]'::jsonb) from page)) into v_result;
  return v_result;
end;
$$;

create or replace function public.benefit_voucher_recent(p_offset integer default 0,p_limit integer default 20) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_recent(p_offset,p_limit);
$$;
revoke all on function private.benefit_voucher_recent(integer,integer),public.benefit_voucher_recent(integer,integer)
  from public,anon,authenticated,service_role;
grant execute on function private.benefit_voucher_recent(integer,integer),public.benefit_voucher_recent(integer,integer) to authenticated;
notify pgrst,'reload schema';
commit;
