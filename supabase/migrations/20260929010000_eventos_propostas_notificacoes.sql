-- Completa o fluxo comercial de eventos sem alterar tabelas de reservas.

alter table public.event_requests
  add column if not exists proposal_terms jsonb not null default jsonb_build_object(
    'validityDays', 5,
    'depositPercent', 20,
    'balanceDaysBefore', 7,
    'additionalNotes', ''
  ),
  add column if not exists proposal_version int not null default 0,
  add column if not exists proposal_generated_at timestamptz,
  add column if not exists last_adjusted_at timestamptz,
  add column if not exists notification_sent_at timestamptz,
  add column if not exists notification_error text;

comment on column public.event_requests.proposal_terms is
  'Condições comerciais editáveis incluídas na proposta definitiva.';
comment on column public.event_requests.proposal_version is
  'Número sequencial da proposta definitiva gerada.';
comment on column public.event_requests.notification_sent_at is
  'Confirma o aviso interno por e-mail após a solicitação pública.';
