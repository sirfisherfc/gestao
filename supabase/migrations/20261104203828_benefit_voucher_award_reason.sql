begin;
-- Inclusão autorizada de motivo interno; preserva os motivos e registros existentes.
alter table private.benefit_vouchers drop constraint if exists benefit_vouchers_issue_reason_check;
alter table private.benefit_vouchers add constraint benefit_vouchers_issue_reason_check
  check (issue_reason in ('recovery','friend','commercial','photo_production','staff_birthday','loyalty','promotion','influencer','award','other'));

do $migration$
declare
  v_function regprocedure;
  v_definition text;
  v_old text := $old$'loyalty','promotion','influencer','other'$old$;
  v_new text := $new$'loyalty','promotion','influencer','award','other'$new$;
begin
  foreach v_function in array array[
    'private.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text)'::regprocedure,
    'private.benefit_voucher_list(text,text,integer,integer,text)'::regprocedure
  ] loop
    select pg_get_functiondef(v_function) into v_definition;
    if position(v_new in v_definition)>0 then continue; end if;
    if position(v_old in v_definition)=0 then
      raise exception 'Validação de motivo esperada não encontrada em %.',v_function;
    end if;
    execute replace(v_definition,v_old,v_new);
  end loop;
end;
$migration$;

-- CREATE OR REPLACE preserva ACL; declarar o mínimo explicitamente também no complemento.
revoke all on function private.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),
  private.benefit_voucher_list(text,text,integer,integer,text) from public,anon,authenticated,service_role;
grant execute on function private.benefit_voucher_issue(uuid,text,text,text,numeric,date,text,text,text),
  private.benefit_voucher_list(text,text,integer,integer,text) to authenticated;
notify pgrst,'reload schema';
commit;
