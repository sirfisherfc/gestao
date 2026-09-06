-- =====================================================================
-- Migration: 20260906030000_bonificacao_neutraliza_fluxos_financiamento.sql
-- Passo 5 da Auditoria Financeira / Risco 5:
-- 1. Neutraliza fluxos de financiamento e investimentos na base de bonificação
--    do gerente (categoria_dre.neutra_bonificacao = true).
-- 2. Amortizações de empréstimos, captações de financiamento e aportes/aplicações
--    financeiras são decisões societárias/de capital e não devem penalizar
--    nem favorecer artificialmente a remuneração operacional do gestor.
-- 3. Custos de manutenção ordinária de equipamentos e infraestrutura permanecem
--    como despesa operacional gerenciável (neutra_bonificacao = false).
-- =====================================================================

begin;

update public.categoria_dre
   set neutra_bonificacao = true
 where categoria in (
   'Empréstimo',
   'Pagamento de Empréstimo',
   'Investimento Financeiro',
   'Investimento negócio'
 )
 and neutra_bonificacao is distinct from true;

comment on column public.categoria_dre.neutra_bonificacao is
  'Quando true, a categoria é somada de volta na base da bonificação do gerente: decisões societárias de financiamento, distribuição de lucros e investimentos de capital não penalizam nem inflam artificialmente a gestão operacional.';

commit;
