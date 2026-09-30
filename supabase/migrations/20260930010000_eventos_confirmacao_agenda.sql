-- Confirmação de evento (sinal recebido) bloqueia os horários de reserva do
-- período; cancelamento libera. Somente a Edge Function event-quote
-- (service_role) grava esses bloqueios.

alter table public.event_requests
  drop constraint if exists event_requests_status_check;
alter table public.event_requests
  add constraint event_requests_status_check check (status in (
    'pending', 'approved', 'adjustment_requested', 'rejected',
    'information_requested', 'alternative_offered', 'final_proposal_ready',
    'confirmed', 'cancelled'
  ));

alter table public.event_requests
  add column if not exists confirmed_at timestamptz,
  add column if not exists agenda_blocks jsonb not null default '[]'::jsonb;

comment on column public.event_requests.confirmed_at is
  'Quando a equipe registrou o sinal e confirmou o evento.';
comment on column public.event_requests.agenda_blocks is
  'Bloqueios criados em blocked_time_slots pela confirmação: [{id, time_slot}]. Removidos no cancelamento.';

grant select on public.blocked_dates,
                public.blocked_time_slots,
                public.availability_rules,
                public.restaurant_settings,
                public.reservations
  to service_role;
grant insert, delete on public.blocked_time_slots to service_role;
