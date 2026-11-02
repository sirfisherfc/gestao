"""Verifica gates e revisoes em transacao revertida; nao cria reserva nem envio."""
from portal import query,verify_portal

SQL="""
begin;
create function pg_temp.check_marketing(ok boolean) returns void language plpgsql as $$
begin if not coalesce(ok,false) then raise exception 'Contrato marketing falhou'; end if; end $$;
select pg_temp.check_marketing(not has_table_privilege('anon','public.marketing_snapshots','select'));
select pg_temp.check_marketing(not has_table_privilege('authenticated','public.marketing_editorial','update'));
select pg_temp.check_marketing(not has_function_privilege('anon','public.marketing_review(uuid,text,integer)','execute'));
select set_config('request.jwt.claim.sub',(select owner_id::text from marketing_private.settings where singleton),true);
set local role authenticated;
select pg_temp.check_marketing(public.marketing_is_owner());
select pg_temp.check_marketing(public.marketing_reservations(current_date-29,current_date)->'rows' is not null);
select pg_temp.check_marketing((select count(*)>=0 from public.marketing_dashboard_snapshots(current_date-31,current_date-2)));
do $$
declare v_id uuid; rejected boolean:=false;
begin
 v_id:=public.marketing_save_draft(jsonb_build_object('target','facebook','format','TEXT','caption','Fixture transacional privada',
   'scheduled_at',now()+interval '1 day','rights_confirmed',true,'quality_confirmed',true));
 perform public.marketing_review(v_id,'review',1);
 begin perform public.marketing_review(v_id,'approve',0); exception when raise_exception then rejected:=true; end;
 perform pg_temp.check_marketing(rejected);
 perform public.marketing_review(v_id,'approve',1);
 perform pg_temp.check_marketing((select status='approved' from public.marketing_editorial e where e.id=v_id));
 perform public.marketing_save_draft(jsonb_build_object('target','facebook','format','TEXT','caption','Revisao dois','expected_revision',1),v_id);
 perform pg_temp.check_marketing((select e.revision=2 and approved_revision is null and status='draft' from public.marketing_editorial e where e.id=v_id));
end $$;
reset role;
select set_config('request.jwt.claim.sub','00000000-0000-4000-8000-000000000000',true);
set local role authenticated;
select pg_temp.check_marketing(not public.marketing_is_owner());
select pg_temp.check_marketing((select count(*)=0 from public.marketing_snapshots));
do $$
declare rejected boolean:=false;
begin
 begin perform public.marketing_reservations(current_date-29,current_date); exception when raise_exception then rejected:=true; end;
 perform pg_temp.check_marketing(rejected);
end $$;
rollback;
"""

if __name__=='__main__':
    verify_portal()
    query(SQL,write=True)
    print('MARKETING_SQL_CONTRACTS_OK rollback=true customer_writes=0 external_sends=0')
