begin;

create or replace function private.benefit_voucher_edit(p_id uuid,p_expected_revision integer,
  p_beneficiary_name text,p_phone text,p_benefit_type text,p_benefit_value numeric,p_expires_on date,
  p_issue_reason text,p_issue_reason_detail text default null,p_internal_note text default null) returns jsonb
language plpgsql volatile security definer set search_path=pg_catalog,pg_temp as $$
declare v private.benefit_vouchers; v_status text; v_now timestamptz; v_before jsonb; v_after jsonb;
  v_conditions text[]:=array['Uso único. Saldo não utilizado é perdido.',
    'Não cumulativo com promoções ou outro voucher na mesma conta.','Válido na unidade Sir Fisher até a data indicada.'];
begin
  if not private.bv_can_manage() then raise exception 'Acesso não permitido.' using errcode='42501'; end if;
  if p_expected_revision is null or p_expected_revision<1 then raise exception 'Consulte o voucher antes de editar.' using errcode='22023'; end if;
  if not private.bv_rate_limit('edit',20) then return jsonb_build_object('ok',false,'reason','rate_limited'); end if;
  select * into v from private.benefit_vouchers where id=p_id for update;
  if not found then return jsonb_build_object('ok',false,'reason','not_found'); end if;
  v_now:=clock_timestamp();
  v_status:=case when v.used_at is not null then 'used' when v.cancelled_at is not null then 'cancelled'
    when v.expires_on<(v_now at time zone 'America/Fortaleza')::date then 'expired' else 'available' end;
  if v_status not in ('available','expired') then return jsonb_build_object('ok',false,'reason',v_status,'voucher',private.bv_payload(v,true)); end if;
  if p_expected_revision<>v.revision then return jsonb_build_object('ok',false,'reason','changed','voucher',private.bv_payload(v,true)); end if;
  if p_beneficiary_name is null or char_length(btrim(p_beneficiary_name)) not between 1 and 160
    or p_phone is null or regexp_replace(p_phone,'[^0-9]','','g') !~ '^[0-9]{10,15}$'
    or p_benefit_type is null or p_benefit_type not in ('fixed','percent')
    or p_benefit_value is null or p_benefit_value<=0 or p_benefit_value='NaN'::numeric
    or p_benefit_value<>round(p_benefit_value,2) or p_benefit_value>9999999999.99
    or (p_benefit_type='percent' and p_benefit_value>100)
    or p_expires_on is null or p_expires_on<(v_now at time zone 'America/Fortaleza')::date or not isfinite(p_expires_on)
    or p_issue_reason is null or p_issue_reason not in ('recovery','friend','commercial','photo_production','staff_birthday','loyalty','promotion','influencer','award','other')
    or char_length(coalesce(p_issue_reason_detail,''))>1000
    or (p_issue_reason='other' and char_length(btrim(coalesce(p_issue_reason_detail,'')))<3)
    or char_length(coalesce(p_internal_note,''))>2000 then
    raise exception 'Confira nome, telefone, benefício, motivo e validade.' using errcode='22023';
  end if;
  v_before:=private.bv_editable_payload(v);
  v_after:=jsonb_build_object('beneficiary_name',btrim(p_beneficiary_name),'phone',regexp_replace(p_phone,'[^0-9]','','g'),
    'benefit_type',p_benefit_type,'benefit_value',p_benefit_value,'expires_on',p_expires_on,
    'issue_reason',p_issue_reason,'issue_reason_detail',nullif(btrim(p_issue_reason_detail),''),'internal_note',nullif(btrim(p_internal_note),''));
  if v_before=v_after then return jsonb_build_object('ok',true,'unchanged',true,'voucher',private.bv_payload(v,true)); end if;
  if p_benefit_type='percent' then v_conditions:=array_prepend('Desconto sobre a conta inteira. Taxa de serviço opcional. Sem teto em reais.',v_conditions); end if;
  update private.benefit_vouchers set beneficiary_name=btrim(p_beneficiary_name),phone=regexp_replace(p_phone,'[^0-9]','','g'),
    benefit_type=p_benefit_type,benefit_value=p_benefit_value,expires_on=p_expires_on,issue_reason=p_issue_reason,
    issue_reason_detail=nullif(btrim(p_issue_reason_detail),''),internal_note=nullif(btrim(p_internal_note),''),
    conditions=v_conditions,revision=revision+1 where id=p_id returning * into v;
  insert into private.benefit_voucher_events(voucher_id,event_type,occurred_at,actor_id,actor_name,reason,changes)
    values(p_id,'edited',v_now,auth.uid(),private.bv_actor_name(),case when v_status='expired' then 'Renovação de validade' else 'Correção de cadastro' end,jsonb_build_object('before',v_before,'after',v_after));
  return jsonb_build_object('ok',true,'voucher',private.bv_payload(v,true));
end;
$$;

revoke all on function private.benefit_voucher_edit(uuid,integer,text,text,text,numeric,date,text,text,text) from public,anon,authenticated,service_role;
grant execute on function private.benefit_voucher_edit(uuid,integer,text,text,text,numeric,date,text,text,text) to authenticated;
notify pgrst,'reload schema';
commit;
