-- =====================================================================
-- Saipos x Stone: casamento por soma e por janela ampla
-- =====================================================================
-- A primeira carga (20261021000000) deixou sem par lançamentos do caixa
-- que existem na Stone:
--   * vale ou conta dividida em vários cartões: um lançamento Saipos é a
--     soma de 2 a 4 vendas Stone (ex.: 117,70 = 3 x 39,23 em Voucher);
--   * conta fechada no caixa até 3 h depois da cobrança na maquininha.
-- stone_ids_extra guarda as demais vendas Stone de um casamento 'soma'
-- (stone_id continua com a primeira). As views passam a considerá-las e o
-- resumo diário ganha as contagens dos dois casamentos novos.
-- Não destrutiva; grants preservados por create or replace.
-- =====================================================================

begin;

alter table public.saipos_pagamento add column if not exists stone_ids_extra text[];

alter table public.saipos_pagamento drop constraint if exists saipos_pagamento_casamento_check;
alter table public.saipos_pagamento add constraint saipos_pagamento_casamento_check
  check (casamento in ('codigo', 'valor_horario', 'janela_ampla', 'soma'));

create or replace view public.conciliacao_saipos_stone_base
with (security_barrier = true, security_invoker = false) as
select
  v.stone_id,
  v.data_venda,
  (v.data_venda - interval '8 hours')::date as data_turno,
  v.produto,
  v.valor_bruto,
  coalesce(
    (select p.id_sale from public.saipos_pagamento p where p.stone_id = v.stone_id),
    (select p.id_sale from public.saipos_pagamento p where v.stone_id = any(p.stone_ids_extra) limit 1)
  ) as id_sale
from public.raw_stone_vendas v
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
    coalesce(sum(p.valor) filter (where p.categoria in ('dinheiro', 'fiado') and not s.cancelada), 0) as valor_dinheiro_fiado,
    count(*) filter (where p.casamento = 'janela_ampla') as qtd_janela_ampla,
    count(*) filter (where p.casamento = 'soma') as qtd_soma
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
  coalesce(s.valor_dinheiro_fiado, 0) as valor_dinheiro_fiado,
  coalesce(s.qtd_janela_ampla, 0) as qtd_janela_ampla,
  coalesce(s.qtd_soma, 0) as qtd_soma
from saipos s
full join stone t on t.data_turno = s.data_turno
where public.usuario_pode_acessar_pagina('conciliacao.html');

revoke all on public.app_conciliacao_saipos_dia from anon;
grant select on public.app_conciliacao_saipos_dia to authenticated;

commit;
