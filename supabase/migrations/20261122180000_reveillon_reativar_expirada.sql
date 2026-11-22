-- Reativar pela ficha uma reserva expirada do Réveillon (ex.: cliente que pagou
-- depois do prazo do sinal). Cria a RPC administrativa rv_admin_reactivate.
-- A definição de instalação também está em reservas/supabase/reveillon-functions.sql
-- e o grant em reservas/supabase/reveillon-rls.sql.
-- Instalações sem o módulo de Réveillon não recebem objetos novos.
-- Não altera dados existentes; reaplicar só recria a função e os grants.
begin;

do $migration$
begin
  if to_regclass('public.rv_bookings') is null
     or to_regclass('public.rv_tables') is null
     or to_regprocedure('public.rv_require_admin()') is null
     or to_regprocedure('public.rv_recalc_booking(uuid)') is null
     or to_regprocedure('public.rv_booking_detail(uuid)') is null
     or to_regprocedure('public.rv_seat_limit_error(uuid,uuid,integer,integer,uuid)') is null then
    raise notice 'Módulo de Réveillon ausente; reativação não se aplica.';
    return;
  end if;

  execute $ddl$
create or replace function public.rv_admin_reactivate(
  p_booking_id uuid,
  p_until timestamptz,
  p_unblock boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  b public.rv_bookings%rowtype;
  t public.rv_tables%rowtype;
  v_starts timestamptz;
  v_err text;
begin
  perform public.rv_require_admin();
  if p_until is null or p_until <= now() + interval '5 minutes' then
    raise exception 'INVALID_INPUT: Escolha uma data e hora no futuro.';
  end if;
  select * into b from public.rv_bookings where id = p_booking_id;
  if not found then
    raise exception 'BOOKING_NOT_FOUND: Reserva não encontrada.';
  end if;
  -- mesma ordem das outras ações: mesa, depois reserva, depois evento
  select * into t from public.rv_tables where id = b.table_id for update;
  select * into b from public.rv_bookings where id = p_booking_id for update;
  if b.status <> 'expirada' then
    raise exception 'INVALID_STATUS: Só reservas expiradas podem ser reativadas.';
  end if;
  select starts_at into v_starts from public.rv_events where id = b.event_id;
  if p_until > v_starts then
    raise exception 'INVALID_INPUT: O prazo não pode passar do início do evento.';
  end if;
  if not t.active then
    raise exception 'TABLE_NOT_FOUND: A mesa % foi desativada. Crie uma reserva manual em outra mesa.', t.label;
  end if;
  if t.blocked and not coalesce(p_unblock, false) then
    raise exception 'TABLE_BLOCKED: A mesa % está bloqueada. Confirme a retirada do bloqueio para reativar.', t.label;
  end if;
  perform public.rv_expire_due(t.id);
  if exists (select 1 from public.rv_bookings x
             where x.table_id = t.id and x.id <> b.id
               and x.status in ('pre_reserva', 'sinal_pago', 'quitada')) then
    raise exception 'TABLE_TAKEN: A mesa % já tem outra reserva. Crie uma reserva manual em outra mesa.', t.label;
  end if;
  perform 1 from public.rv_events where id = b.event_id for update;
  v_err := public.rv_seat_limit_error(b.event_id, t.table_type_id, b.adults, b.children, b.id);
  if v_err is not null then
    raise exception '%', v_err;
  end if;

  if t.blocked or t.negotiating then
    update public.rv_tables set blocked = false, block_reason = null,
      negotiating = false, negotiation_note = null
    where id = t.id;
  end if;
  update public.rv_bookings set status = 'pre_reserva', hold_expires_at = p_until, expired_at = null
  where id = b.id;
  -- novo prazo = pode avisar de novo antes de expirar
  delete from public.notification_queue q
   where q.rv_booking_id = b.id and q.type = 'rv_expiry_warning' and q.status in ('sent', 'failed', 'skipped');
  perform public.rv_log(b.id, 'reativada', 'expirada', 'pre_reserva', jsonb_build_object(
    'prazo', p_until, 'mesa', t.label, 'expirada_em', b.expired_at,
    'desbloqueou', t.blocked, 'motivo_bloqueio', t.block_reason,
    'saiu_de_negociacao', t.negotiating));
  perform public.rv_recalc_booking(b.id);
  return public.rv_booking_detail(b.id);
end;
$$;
$ddl$;

  execute 'revoke all on function public.rv_admin_reactivate(uuid, timestamptz, boolean) from public, anon, authenticated';
  execute 'grant execute on function public.rv_admin_reactivate(uuid, timestamptz, boolean) to authenticated';
end;
$migration$;

commit;
