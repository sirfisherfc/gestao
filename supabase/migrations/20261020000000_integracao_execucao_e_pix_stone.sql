-- =====================================================================
-- Integrações por API: registro de execuções e fila dos arquivos Pix Stone
-- =====================================================================
-- integracao_execucao: cada rodada dos importadores por API (GitHub Actions
-- ou manual) grava uma linha por fonte, dia e stonecode, com sucesso ou
-- erro. A página Status lê a view app_integracao_execucao, só para admin,
-- e mostra os dias que falharam ou ficaram sem execução.
--
-- stone_pix_arquivo: a Stone entrega o arquivo Pix de conciliação por
-- webhook. A Edge Function stone-webhook grava aqui o aviso e o CSV
-- baixado do link pré-assinado; o importador Python lê e marca o
-- processamento. Escrita da função via service_role; os scripts Python
-- conectam como dono e não dependem de grant.
--
-- Grants explícitos, regra de 30/10/2026: authenticated só lê a view;
-- anon não recebe nada; service_role só a fila do Pix.
-- =====================================================================

begin;

create table if not exists public.integracao_execucao (
  id uuid primary key default gen_random_uuid(),
  executado_em timestamptz not null default now(),
  origem text not null,
  fonte text not null,
  dia_referencia date,
  stonecode text,
  situacao text not null check (situacao in ('ok', 'sem_movimento', 'erro')),
  linhas_novas integer,
  mensagem text,
  execucao_url text
);

create index if not exists ix_integracao_execucao_executado_em
  on public.integracao_execucao (executado_em desc);
create index if not exists ix_integracao_execucao_fonte_dia
  on public.integracao_execucao (fonte, dia_referencia);

alter table public.integracao_execucao enable row level security;
revoke all on public.integracao_execucao from anon, authenticated;

create or replace view public.app_integracao_execucao
with (security_barrier = true, security_invoker = false) as
select
  e.id,
  e.executado_em,
  e.origem,
  e.fonte,
  e.dia_referencia,
  e.stonecode,
  e.situacao,
  e.linhas_novas,
  e.mensagem,
  e.execucao_url
from public.integracao_execucao e
where public.usuario_tem_papel(array['admin']::text[]);

revoke all on public.app_integracao_execucao from anon;
grant select on public.app_integracao_execucao to authenticated;

create table if not exists public.stone_pix_arquivo (
  id uuid primary key default gen_random_uuid(),
  recebido_em timestamptz not null default now(),
  tipo text,
  documento text,
  data_referencia date,
  url_arquivo text,
  aviso jsonb not null,
  conteudo text,
  baixado_em timestamptz,
  processado_em timestamptz,
  erro text
);

create index if not exists ix_stone_pix_arquivo_documento_data
  on public.stone_pix_arquivo (documento, data_referencia);

alter table public.stone_pix_arquivo enable row level security;
revoke all on public.stone_pix_arquivo from anon, authenticated;
grant select, insert, update on public.stone_pix_arquivo to service_role;

commit;
