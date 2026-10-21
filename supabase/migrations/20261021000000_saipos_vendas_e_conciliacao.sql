-- =====================================================================
-- Saipos: vendas do PDV e conciliação com as vendas Stone
-- =====================================================================
-- saipos_venda / saipos_pagamento: cópia das vendas da API de Dados Saipos
-- (search_sales), gravada por scripts/importacao/api_saipos_vendas.py, que
-- conecta como dono. Um pagamento é uma transação da maquininha integrada
-- (origem 'pos') ou uma forma de pagamento lançada no caixa sem transação
-- correspondente (origem 'forma').
--
-- O importador casa cada pagamento com raw_stone_vendas: pelo código de
-- autorização (cartão na maquininha = stone_id) ou, sem código, por valor,
-- categoria e horário. O resultado fica em stone_id/casamento. Dinheiro,
-- Fiado e vendas canceladas não entram na conciliação.
--
-- O dia de comparação é a data do turno da Saipos: o primeiro turno começa
-- às 08:00, então a venda Stone da madrugada pertence ao dia anterior.
--
-- Grants explícitos, regra de 30/10/2026: authenticated só lê as views;
-- anon e service_role não recebem nada.
-- =====================================================================

begin;

create table if not exists public.saipos_venda (
  id_sale bigint primary key,
  id_store integer not null,
  data_turno date not null,
  turno text,
  criada_em timestamp not null,
  atualizada_em timestamp,
  cancelada boolean not null default false,
  tipo_venda smallint,
  total numeric(12,2),
  importado_em timestamptz not null default now()
);

create index if not exists ix_saipos_venda_data_turno
  on public.saipos_venda (data_turno);

create table if not exists public.saipos_pagamento (
  id_sale bigint not null references public.saipos_venda (id_sale) on delete cascade,
  origem text not null check (origem in ('pos', 'forma')),
  ordem smallint not null,
  forma text not null,
  categoria text not null check (categoria in ('credito', 'debito', 'pix', 'dinheiro', 'fiado', 'outro')),
  valor numeric(12,2) not null,
  criado_em timestamp not null,
  codigo_autorizacao text,
  id_transacao text,
  entra_conciliacao boolean not null,
  stone_id text,
  casamento text check (casamento in ('codigo', 'valor_horario')),
  diferenca_min integer,
  primary key (id_sale, origem, ordem),
  check ((stone_id is null) = (casamento is null))
);

create unique index if not exists uq_saipos_pagamento_stone_id
  on public.saipos_pagamento (stone_id) where stone_id is not null;

alter table public.saipos_venda enable row level security;
alter table public.saipos_pagamento enable row level security;
revoke all on public.saipos_venda from anon, authenticated;
revoke all on public.saipos_pagamento from anon, authenticated;

-- Vendas Stone da casa no período coberto pela Saipos, já no dia do turno.
create or replace view public.conciliacao_saipos_stone_base
with (security_barrier = true, security_invoker = false) as
select
  v.stone_id,
  v.data_venda,
  (v.data_venda - interval '8 hours')::date as data_turno,
  v.produto,
  v.valor_bruto,
  p.id_sale
from public.raw_stone_vendas v
left join public.saipos_pagamento p on p.stone_id = v.stone_id
where v.ultimo_status = 'Aprovada'
  and (v.stonecode is null
       or v.stonecode in (select c.stonecode from public.stone_conta c where c.ativa and c.entra_faturamento))
  and (v.data_venda - interval '8 hours')::date >= (select min(s.data_turno) from public.saipos_venda s)
  and public.usuario_pode_acessar_pagina('conciliacao.html');

revoke all on public.conciliacao_saipos_stone_base from anon, authenticated;

create or replace view public.app_conciliacao_saipos_dia
with (security_barrier = true, security_invoker = false) as
with saipos as (
  select
    s.data_turno,
    count(*) filter (where p.entra_conciliacao) as qtd_conciliavel,
    coalesce(sum(p.valor) filter (where p.entra_conciliacao), 0) as valor_conciliavel,
    count(*) filter (where p.casamento = 'codigo') as qtd_por_codigo,
    count(*) filter (where p.casamento = 'valor_horario') as qtd_por_valor_horario,
    count(*) filter (where p.entra_conciliacao and p.stone_id is null) as qtd_saipos_sem_stone,
    coalesce(sum(p.valor) filter (where p.entra_conciliacao and p.stone_id is null), 0) as valor_saipos_sem_stone,
    coalesce(sum(p.valor) filter (where p.categoria in ('dinheiro', 'fiado') and not s.cancelada), 0) as valor_dinheiro_fiado
  from public.saipos_venda s
  join public.saipos_pagamento p on p.id_sale = s.id_sale
  group by s.data_turno
), stone as (
  select
    b.data_turno,
    count(*) as qtd_stone,
    sum(b.valor_bruto) as valor_stone,
    count(*) filter (where b.id_sale is null) as qtd_stone_sem_saipos,
    coalesce(sum(b.valor_bruto) filter (where b.id_sale is null), 0) as valor_stone_sem_saipos
  from public.conciliacao_saipos_stone_base b
  group by b.data_turno
)
select
  coalesce(s.data_turno, t.data_turno) as data_turno,
  coalesce(s.qtd_conciliavel, 0) as qtd_conciliavel,
  coalesce(s.valor_conciliavel, 0) as valor_conciliavel,
  coalesce(s.qtd_por_codigo, 0) as qtd_por_codigo,
  coalesce(s.qtd_por_valor_horario, 0) as qtd_por_valor_horario,
  coalesce(s.qtd_saipos_sem_stone, 0) as qtd_saipos_sem_stone,
  coalesce(s.valor_saipos_sem_stone, 0) as valor_saipos_sem_stone,
  coalesce(t.qtd_stone, 0) as qtd_stone,
  coalesce(t.valor_stone, 0) as valor_stone,
  coalesce(t.qtd_stone_sem_saipos, 0) as qtd_stone_sem_saipos,
  coalesce(t.valor_stone_sem_saipos, 0) as valor_stone_sem_saipos,
  coalesce(s.valor_dinheiro_fiado, 0) as valor_dinheiro_fiado
from saipos s
full join stone t on t.data_turno = s.data_turno
where public.usuario_pode_acessar_pagina('conciliacao.html');

revoke all on public.app_conciliacao_saipos_dia from anon;
grant select on public.app_conciliacao_saipos_dia to authenticated;

create or replace view public.app_conciliacao_saipos_pendencia
with (security_barrier = true, security_invoker = false) as
select
  s.data_turno,
  'Saipos sem Stone'::text as lado,
  p.criado_em as horario,
  p.forma,
  p.valor,
  s.id_sale::text as referencia
from public.saipos_venda s
join public.saipos_pagamento p on p.id_sale = s.id_sale
where p.entra_conciliacao and p.stone_id is null
  and public.usuario_pode_acessar_pagina('conciliacao.html')
union all
select
  b.data_turno,
  'Stone sem Saipos'::text,
  b.data_venda,
  b.produto,
  b.valor_bruto,
  b.stone_id
from public.conciliacao_saipos_stone_base b
where b.id_sale is null;

revoke all on public.app_conciliacao_saipos_pendencia from anon;
grant select on public.app_conciliacao_saipos_pendencia to authenticated;

commit;
