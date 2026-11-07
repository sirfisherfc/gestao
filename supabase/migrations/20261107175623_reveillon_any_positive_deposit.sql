-- Pagamento positivo confirma o sinal; o percentual do evento segue como sugestão.
-- As definições completas do módulo continuam em reservas/supabase/reveillon-functions.sql.
-- Instalações sem o módulo de Réveillon não recebem objetos nem dados novos.
-- Reaplicação preserva pagamentos e só ajusta pré-reservas ainda elegíveis.
begin;

do $migration$
declare
  b record;
  v_price jsonb;
  v_new text;
  v_first_paid_at timestamptz;
begin
  if to_regclass('public.rv_bookings') is null
     or to_regclass('public.rv_payments') is null
     or to_regprocedure('public.rv_recalc_booking(uuid)') is null
     or to_regprocedure('public.rv_admin_register_payment(uuid,numeric,text,timestamptz,text,text)') is null then
    raise notice 'Módulo de Réveillon ausente; ajuste de sinal não se aplica.';
    return;
  end if;

  execute $ddl$
create or replace function public.rv_recalc_booking(p_booking_id uuid)
returns text
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  b public.rv_bookings%rowtype;
  v_price jsonb;
  v_total numeric;
  v_balance numeric;
  v_dep numeric;
  v_paid numeric;
  v_new text;
  v_hold_hours int;
begin
  select * into b from public.rv_bookings where id = p_booking_id for update;
  if not found then
    raise exception 'BOOKING_NOT_FOUND: Reserva não encontrada.';
  end if;

  v_price := public.rv_price_for_booking(b.id);
  v_total := (v_price->>'total')::numeric;
  v_balance := (v_price->>'balance')::numeric;
  v_dep := (v_price->>'deposit_min')::numeric;
  v_paid := (v_price->>'paid_gross')::numeric;

  v_new := b.status;
  if b.status in ('pre_reserva', 'sinal_pago', 'quitada') then
    if v_total > 0 and v_balance = 0 then
      v_new := 'quitada';
    -- O admin confirma o sinal ao registrar qualquer pagamento positivo.
    -- O percentual do evento continua sendo a sugestão de valor.
    elsif v_paid > 0 then
      v_new := 'sinal_pago';
    else
      v_new := 'pre_reserva';
    end if;
    -- "Marcada como quitada" manualmente (cortesia/arredondamento) é
    -- preservada enquanto nada que mexe em valor mudar: só rebaixa se o saldo
    -- aumentou em relação ao momento em que foi marcada.
    if b.status = 'quitada' and v_new <> 'quitada'
       and coalesce((select (h.details->>'balance')::numeric
                     from public.rv_booking_history h
                     where h.booking_id = b.id and h.action = 'marcada_quitada'
                     order by h.created_at desc limit 1), -1) >= v_balance then
      v_new := 'quitada';
    end if;
  end if;

  select e.hold_hours into v_hold_hours from public.rv_events e where e.id = b.event_id;

  update public.rv_bookings set
    total_amount = v_total,
    total_pix_amount = (v_price->>'total_pix')::numeric,
    consumption_total = (v_price->>'consumption_total')::numeric,
    deposit_min_amount = v_dep,
    status = v_new,
    deposit_paid_at = case
      when v_new in ('sinal_pago', 'quitada') then coalesce(deposit_paid_at, now())
      else null end,
    paid_in_full_at = case when v_new = 'quitada' then coalesce(paid_in_full_at, now()) else null end,
    -- voltou para pré-reserva (ex.: estorno): ganha um prazo novo se o antigo já venceu
    hold_expires_at = case
      when v_new = 'pre_reserva' and b.status <> 'pre_reserva'
        then greatest(coalesce(hold_expires_at, now()), now() + make_interval(hours => v_hold_hours))
      else hold_expires_at end
  where id = b.id;

  if v_new <> b.status then
    perform public.rv_log(b.id, 'status_automatico', b.status, v_new,
      jsonb_build_object('paid_gross', v_paid, 'total', v_total, 'deposit_min', v_dep));
    if v_new = 'sinal_pago' and b.status = 'pre_reserva' then
      perform public.rv_enqueue_email(b.id, 'rv_deposit_received');
    elsif v_new = 'quitada' then
      perform public.rv_enqueue_email(b.id, 'rv_paid_in_full');
    end if;
  end if;

  return v_new;
end;
$$;

create or replace function public.rv_admin_register_payment(
  p_booking_id uuid,
  p_amount numeric,
  p_method text,
  p_paid_at timestamptz default null,
  p_payer_name text default null,
  p_notes text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_actor uuid;
  v_status text;
  v_payment_id uuid;
begin
  v_actor := public.rv_require_admin();
  if p_amount is null or p_amount < 0.01
     or p_amount::text in ('NaN', 'Infinity', '-Infinity') then
    raise exception 'INVALID_INPUT: Informe um valor a partir de R$ 0,01.';
  end if;
  if p_method not in ('pix', 'debito', 'credito') then
    raise exception 'INVALID_INPUT: Forma de pagamento inválida.';
  end if;

  select b.status into v_status from public.rv_bookings b where b.id = p_booking_id for update;
  if not found then
    raise exception 'BOOKING_NOT_FOUND: Reserva não encontrada.';
  end if;
  if v_status not in ('pre_reserva', 'sinal_pago', 'quitada') then
    raise exception 'INVALID_STATUS: Não é possível registrar pagamento em reserva %.', v_status;
  end if;

  insert into public.rv_payments (booking_id, paid_at, amount, method, payer_name, notes, created_by_user_id)
  values (p_booking_id, coalesce(p_paid_at, now()), round(p_amount, 2), p_method,
          nullif(trim(coalesce(p_payer_name, '')), ''), nullif(trim(coalesce(p_notes, '')), ''), v_actor)
  returning id into v_payment_id;

  perform public.rv_log(p_booking_id, 'pagamento', v_status, v_status,
    jsonb_build_object('payment_id', v_payment_id, 'valor', round(p_amount, 2), 'forma', p_method,
                       'pagador', p_payer_name, 'data', coalesce(p_paid_at, now())));
  perform public.rv_recalc_booking(p_booking_id);
  return public.rv_booking_detail(p_booking_id);
end;
$$;

  $ddl$;

  -- Helpers continuam internos; somente a RPC administrativa recebe execução.
  revoke all on function public.rv_recalc_booking(uuid) from public, anon, authenticated;
  revoke all on function public.rv_admin_register_payment(uuid, numeric, text, timestamptz, text, text) from public, anon;
  grant execute on function public.rv_admin_register_payment(uuid, numeric, text, timestamptz, text, text) to authenticated;

  -- Ajusta pagamentos já aceitos sem reenviar e-mails retroativos.
  for b in
    select booking.*
    from public.rv_bookings booking
    where booking.status = 'pre_reserva'
      and exists (
        select 1 from public.rv_payments payment
        where payment.booking_id = booking.id
          and payment.voided_at is null and payment.amount >= 0.01
      )
    order by booking.id
    for update of booking
  loop
    -- Confere os pagamentos novamente depois de obter o lock da reserva.
    select min(payment.paid_at) into v_first_paid_at
    from public.rv_payments payment
    where payment.booking_id = b.id
      and payment.voided_at is null and payment.amount >= 0.01;
    if v_first_paid_at is null then
      continue;
    end if;

    v_price := public.rv_price_for_booking(b.id);
    v_new := case
      when (v_price->>'total')::numeric > 0 and (v_price->>'balance')::numeric = 0
        then 'quitada'
      else 'sinal_pago'
    end;

    update public.rv_bookings set
      status = v_new,
      deposit_paid_at = coalesce(deposit_paid_at, v_first_paid_at),
      paid_in_full_at = case when v_new = 'quitada'
        then coalesce(paid_in_full_at, now()) else paid_in_full_at end
    where id = b.id;

    perform public.rv_log(b.id, 'status_automatico', 'pre_reserva', v_new,
      jsonb_build_object('origem', 'regra_sinal_valor_positivo',
        'paid_gross', (v_price->>'paid_gross')::numeric,
        'total', (v_price->>'total')::numeric,
        'deposit_min', (v_price->>'deposit_min')::numeric));
  end loop;
end;
$migration$;

commit;
