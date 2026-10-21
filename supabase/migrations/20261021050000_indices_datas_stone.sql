-- =====================================================================
-- Índices de data nas tabelas Stone usadas pelos cortes e projeções
-- =====================================================================
--
-- PROBLEMA
--   Várias views do painel fazem max()/min() ou recortes por data em tabelas
--   Stone sem índice na coluna, e cada uma varre a tabela inteira a cada
--   leitura (medido em 21/10/2026, docs/DESEMPENHO_PAINEL.md):
--     - corte_venda: max(raw_stone_vendas.data_venda), 44 mil linhas;
--     - recebimento_projetado: max(raw_stone_recebiveis.data_venda);
--     - recebimento_conhecido e o Calendário: data_vencimento após o corte
--       (~20 de 34 mil linhas), 0,3 s por leitura;
--     - fato_financeiro: min(raw_stone_extrato.data_hora), em toda leitura.
--
-- SOLUÇÃO
--   Um índice btree em cada coluna. O planner passa a resolver max()/min()
--   lendo uma ponta do índice e os recortes por faixa de data.
--
-- OBJETOS
--   + 4 índices (if not exists). Nenhuma view, função ou dado muda.
--
-- RISCOS
--   Baixo. Escrita um pouco mais cara nas importações (tabelas de dezenas de
--   milhares de linhas; ~1 MB por índice). Criação sem CONCURRENTLY porque o
--   aplicador roda cada migration numa transação; nessas tabelas leva menos
--   de 1 s. Reversão: drop index.
-- =====================================================================

begin;

create index if not exists raw_stone_vendas_data_venda_idx
  on public.raw_stone_vendas (data_venda);

create index if not exists raw_stone_recebiveis_data_vencimento_idx
  on public.raw_stone_recebiveis (data_vencimento);

create index if not exists raw_stone_recebiveis_data_venda_idx
  on public.raw_stone_recebiveis (data_venda);

create index if not exists raw_stone_extrato_data_hora_idx
  on public.raw_stone_extrato (data_hora);

commit;
