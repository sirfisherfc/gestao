-- =====================================================================
-- Repoe o indice unico de mv_fluxo_caixa_diario e destrava o painel
-- =====================================================================
--
-- PROBLEMA
--   Desde 15/09/2026 toda tarefa da fila de recalculo termina em erro com
--   'cannot refresh materialized view "public.mv_fluxo_caixa_diario"
--   concurrently'. O indice unico mv_fluxo_caixa_diario_dia_idx, criado em
--   20260702120000 e exigido por REFRESH ... CONCURRENTLY, nao existe mais no
--   banco portal: a migration consta como aplicada no historico, mas o objeto
--   nao veio junto na restauracao/migracao do Supabase. Dos 50 indices
--   declarados nas migrations, esse e o unico ausente que ainda tem dono vivo
--   (o outro, de mv_saldo_caixa_diario_detalhado, saiu de proposito em
--   20260818200000).
--
--   O estrago passa do painel velho. refresh_painel() atualiza cinco MVs em
--   sequencia e mv_fluxo_caixa_diario e a segunda; como o worker roda tudo em
--   uma transacao so, o erro desfaz tambem o recalculo do saldo e o refresh de
--   private.mv_saldo_conta_diario que ja tinham dado certo. Resultado: o
--   snapshot do fluxo parou em 06/09 (433 dias contra 448 da view real) e
--   private.mv_saldo_conta_diario parou em 15/09. Com o corte de caixa em
--   20/09, saldo_anchor nao acha a linha do dia e devolve 0,00 - entao nem a
--   leitura ao vivo de fluxo_caixa_diario fica certa enquanto isto durar.
--   Nenhum dado importado se perdeu: as gravacoes sempre foram confirmadas.
--
-- SOLUCAO
--   Recriar o indice e enfileirar um recalculo do ano corrente, que o worker
--   ja existente processa em segundo plano (o watchdog de 2 min reagenda o job
--   sozinho quando ha linha pendente).
--
-- OBJETOS
--   + index public.mv_fluxo_caixa_diario_dia_idx (unique, dia)
--   + 1 linha em private.fila_recalculo_saldo (chave migration-20260921000000)
--
-- SEGURANCA / RISCO
--   - Nenhuma regra, valor financeiro, permissao ou grant muda.
--   - dia ja e unico no snapshot (433 linhas, 433 dias distintos), entao o
--     indice entra sem conflito; a criacao levou 0,1 s.
--   - Ensaiado em transacao desfeita com rollback: com o indice no lugar,
--     recalcular_saldo_fechamento + refresh_painel() rodaram inteiros em ~87 s,
--     os tres validadores passaram, o snapshot ficou identico a view (zero dias
--     divergentes) e saldo_anchor de 20/09 voltou a ter valor.
--   - Efeito visivel: ao voltar a atualizar, o painel salta - os saldos caem
--     em relacao ao que estava na tela, que era de 06/09.
--   - Idempotente: create index if not exists e seed com chave unica.
-- =====================================================================

begin;

-- Exigido por REFRESH MATERIALIZED VIEW CONCURRENTLY (1 linha por dia).
create unique index if not exists mv_fluxo_caixa_diario_dia_idx
  on public.mv_fluxo_caixa_diario (dia);

-- Recompoe o atraso acumulado. O recorte do inicio do ano refaz tambem os
-- fechamentos mensais que ficaram sem gravacao desde 06/09. A chave deixa o
-- seed idempotente se o arquivo for reexecutado.
insert into private.fila_recalculo_saldo (chave, data_min, data_max, mensagem)
values (
  'migration-20260921000000',
  make_date(extract(year from current_date)::integer, 1, 1),
  current_date,
  'Recalculo apos repor o indice unico do snapshot do fluxo.'
)
on conflict (chave) do nothing;

commit;
