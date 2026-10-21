-- =====================================================================
-- Saipos x Stone: índice para as vendas Stone casadas por soma
-- =====================================================================
-- A view base procurava cada venda Stone em stone_ids_extra com "= any()",
-- que varre saipos_pagamento inteira para cada linha (0,8 s no resumo do
-- mês). Com "@>" e um índice GIN a busca usa o índice. Mesmo resultado;
-- não destrutiva; grants preservados por create or replace.
-- =====================================================================

begin;

create index if not exists ix_saipos_pagamento_stone_ids_extra
  on public.saipos_pagamento using gin (stone_ids_extra);

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
    (select p.id_sale from public.saipos_pagamento p where p.stone_ids_extra @> array[v.stone_id] limit 1)
  ) as id_sale
from public.raw_stone_vendas v
where v.ultimo_status = 'Aprovada'
  and (v.stonecode is null
       or v.stonecode in (select c.stonecode from public.stone_conta c where c.ativa and c.entra_faturamento))
  and (v.data_venda - interval '8 hours')::date >= (select min(s.data_turno) from public.saipos_venda s)
  and public.usuario_pode_acessar_pagina('conciliacao.html');

revoke all on public.conciliacao_saipos_stone_base from anon, authenticated;

commit;
