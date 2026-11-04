begin;
-- Move somente as implementações privilegiadas para schema não exposto.
-- Contratos HTTP, gates de perfis e transações permanecem iguais.
do $migration$
declare v_function regprocedure; v_definition text;
begin
  foreach v_function in array array[
    'public.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text)'::regprocedure,
    'public.benefit_voucher_list(text,text,integer,integer,text)'::regprocedure,
    'public.benefit_voucher_detail(uuid)'::regprocedure,
    'public.benefit_voucher_lookup(text)'::regprocedure,
    'public.benefit_voucher_redeem(uuid,boolean)'::regprocedure,
    'public.benefit_voucher_cancel(uuid,text,boolean)'::regprocedure
  ] loop
    select pg_get_functiondef(v_function) into v_definition;
    -- Reexecutar a migration não substitui implementação por wrapper recursivo.
    if v_definition like '%SECURITY DEFINER%' then
      execute replace(v_definition,'FUNCTION public.benefit_voucher_','FUNCTION private.benefit_voucher_');
    end if;
  end loop;
end;
$migration$;

create or replace function public.benefit_voucher_issue(p_request_id uuid,p_beneficiary_name text,p_phone text,
  p_benefit_type text,p_benefit_value numeric,p_expires_on date,p_issue_reason text,p_issue_reason_detail text default null,p_internal_note text default null) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_issue(p_request_id,p_beneficiary_name,p_phone,p_benefit_type,p_benefit_value,p_expires_on,p_issue_reason,p_issue_reason_detail,p_internal_note);
$$;
create or replace function public.benefit_voucher_list(p_search text default '',p_status text default '',p_offset integer default 0,p_limit integer default 50,p_reason text default '') returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_list(p_search,p_status,p_offset,p_limit,p_reason);
$$;
create or replace function public.benefit_voucher_detail(p_id uuid) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_detail(p_id);
$$;
create or replace function public.benefit_voucher_lookup(p_code text) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_lookup(p_code);
$$;
create or replace function public.benefit_voucher_redeem(p_id uuid,p_confirm boolean) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_redeem(p_id,p_confirm);
$$;
create or replace function public.benefit_voucher_cancel(p_id uuid,p_reason text,p_confirm boolean) returns jsonb
language sql volatile security invoker set search_path=pg_catalog,pg_temp as $$
  select private.benefit_voucher_cancel(p_id,p_reason,p_confirm);
$$;

-- private já tem USAGE para authenticated no portal. Não ampliar outros grants.
revoke all on function private.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),private.benefit_voucher_list(text,text,integer,integer,text),
  private.benefit_voucher_detail(uuid),private.benefit_voucher_lookup(text),private.benefit_voucher_redeem(uuid,boolean),private.benefit_voucher_cancel(uuid,text,boolean)
  from public,anon,authenticated,service_role;
grant execute on function private.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),private.benefit_voucher_list(text,text,integer,integer,text),
  private.benefit_voucher_detail(uuid),private.benefit_voucher_lookup(text),private.benefit_voucher_redeem(uuid,boolean),private.benefit_voucher_cancel(uuid,text,boolean)
  to authenticated;
revoke all on function public.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),public.benefit_voucher_list(text,text,integer,integer,text),
  public.benefit_voucher_detail(uuid),public.benefit_voucher_lookup(text),public.benefit_voucher_redeem(uuid,boolean),public.benefit_voucher_cancel(uuid,text,boolean)
  from public,anon,authenticated,service_role;
grant execute on function public.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),public.benefit_voucher_list(text,text,integer,integer,text),
  public.benefit_voucher_detail(uuid),public.benefit_voucher_lookup(text),public.benefit_voucher_redeem(uuid,boolean),public.benefit_voucher_cancel(uuid,text,boolean)
  to authenticated;
notify pgrst,'reload schema';
commit;
