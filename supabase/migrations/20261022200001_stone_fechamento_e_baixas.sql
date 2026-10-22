begin;
set local lock_timeout = '5s';

-- Somente metadados de conclusão. Não replica arquivos ou dados bancários.
create table if not exists private.stone_fechamento_dia (
  dia date not null,
  etapa text not null check (etapa in ('vendas','recebiveis','baixas','painel','extrato')),
  identificador text not null default '',
  estado text not null check (estado in ('pendente','aguardando','concluido','erro')),
  quantidade integer not null default 0,
  mensagem text,
  origem_em timestamptz,
  atualizado_em timestamptz not null default now(),
  primary key (dia,etapa,identificador)
);
alter table private.stone_fechamento_dia enable row level security;
revoke all on private.stone_fechamento_dia from public, anon, authenticated;

-- Identidade lógica + referência documentam versões. Hash e antes/depois são
-- privados; a atualização da parcela e este histórico usam a mesma transação.
create table if not exists private.stone_baixa_evento (
  chave text not null,
  referencia date not null,
  hash_payload text not null,
  arquivo_sha256 text not null,
  stonecode text not null,
  stone_id text not null,
  n_parcela integer not null check (n_parcela > 0),
  pagamento date not null,
  estado text not null check (estado in ('aplicado','pendente','obsoleto')),
  conflito boolean not null default false,
  mensagem text,
  antes jsonb,
  depois jsonb,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  primary key (chave,referencia)
);
create index if not exists stone_baixa_evento_parcela_idx
  on private.stone_baixa_evento(stonecode,stone_id,n_parcela,referencia desc);
alter table private.stone_baixa_evento enable row level security;
revoke all on private.stone_baixa_evento from public, anon, authenticated;

-- Retomada limitada do GET do endereço já recebido: nunca outro POST Pix.
alter table public.stone_pix_arquivo add column if not exists tentativas_download integer not null default 0;
alter table public.stone_pix_arquivo add column if not exists ultima_tentativa_download timestamptz;
-- A função precisa conservar seu acesso mesmo após mudanças de schema.
grant select, insert, update on public.stone_pix_arquivo to service_role;

create or replace view public.app_stone_fechamento
with (security_barrier = true, security_invoker = false) as
with dias as (
  select g::date as dia
  from generate_series(date '2026-10-21', (now() at time zone 'America/Fortaleza')::date-1, interval '1 day') g
), etapas as (
  select e.etapa, ''::text as identificador
  from (values ('vendas'::text),('painel'),('extrato')) e(etapa)
  union all
  select e.etapa, c.stonecode
  from public.stone_conta c cross join (values ('recebiveis'::text),('baixas')) e(etapa)
  where c.ativa and c.entra_faturamento and c.stonecode <> '173835323'
)
select d.dia,e.etapa,e.identificador,
       coalesce(f.estado,'pendente') as estado,
       coalesce(f.quantidade,0) as quantidade,
       coalesce(f.mensagem,'Etapa ainda não concluída.') as mensagem,
       f.origem_em,f.atualizado_em,
       (d.dia+2)::timestamp at time zone 'America/Fortaleza' as prazo_exclusivo,
       coalesce(f.estado,'pendente') <> 'concluido'
         and now() >= ((d.dia+2)::timestamp at time zone 'America/Fortaleza') as atrasado
from dias d cross join etapas e
left join private.stone_fechamento_dia f
  on f.dia=d.dia and f.etapa=e.etapa and f.identificador=e.identificador
where (select public.usuario_tem_papel(array['admin']::text[]));
revoke all on public.app_stone_fechamento from public, anon;
grant select on public.app_stone_fechamento to authenticated, service_role;

comment on table private.stone_baixa_evento is 'Liquidações por parcela, com proveniência, precedência e auditoria privada.';
comment on table private.stone_fechamento_dia is 'Etapas confirmadas do fechamento Stone; ausência não significa dia sem movimento.';
comment on view public.app_stone_fechamento is 'Resumo administrativo desde 21/10; D+1 até 23h59 de Fortaleza. Voucher e link fora do escopo.';
commit;
