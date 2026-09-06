-- =====================================================================
-- Migration: 20260906020000_cascata_dre_subtotais_mutuamente_exclusivos.sql
-- Passo 4 da Auditoria Financeira / Risco 1:
-- 1. Substitui o literal fixo 'PRAIA'::text por public.unidade_principal_nome().
-- 2. Elimina o risco de sobreposição de grupos e mascaramento por 'outros':
--    cada lançamento de dre_mensal é particionado em EXATAMENTE UM componente
--    econômico mutuamente exclusivo (receita, cmv, impostos, outras_variaveis,
--    pessoal, infraestrutura, marketing, nao_operacional, contabil, capex,
--    nao_categorizado, outros).
-- 3. 'outros' passa a ser o somatório direto dos grupos residuais não-mapeados,
--    garantindo que qualquer novo grupo apareça com transparência sem mascarar
--    duplicidades nos subtotais de Margem de Contribuição ou Resultado Operacional.
-- 4. Adiciona constraint de integridade em public.grupo_variavel impedindo que
--    grupos operacionais fixos, não-operacionais ou de capital sejam marcados
--    indevidamente como variáveis.
-- =====================================================================

begin;

-- 1) Blindagem da tabela de configuração grupo_variavel
do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'ck_grupo_variavel_mutuamente_exclusivo'
      and conrelid = 'public.grupo_variavel'::regclass
  ) then
    alter table public.grupo_variavel
      add constraint ck_grupo_variavel_mutuamente_exclusivo
      check (
        not (variavel and grupo in (
          'RECEITAS', 'PESSOAL', 'INFRAESTRUTURA', 'MARKETING E PUBLICIDADE',
          'NÃO OPERACIONAL', 'CONTABIL', 'BENS DURÁVEIS'
        ))
      );
  end if;
end $$;

-- 2) View canônica da cascata com componentes mutuamente exclusivos
create or replace view public.painel_dre_cascata as
with base as (
  select dre_mensal.mes,
    dre_mensal.ano_mes,
    dre_mensal.dre_grupo,
    dre_mensal.natureza,
    sum(dre_mensal.total) as total
  from dre_mensal
  where dre_mensal.entra_dre = true
    and dre_mensal.unidade = public.unidade_principal_nome()
  group by dre_mensal.mes, dre_mensal.ano_mes, dre_mensal.dre_grupo, dre_mensal.natureza
), flags as (
  select grupo_variavel.grupo, grupo_variavel.variavel from grupo_variavel
), categorizado as (
  select b.mes,
    b.ano_mes,
    b.total,
    case
      when b.dre_grupo = 'RECEITAS' then 'receita'
      when b.dre_grupo = 'DESPESA DIRETA DE VENDA' then 'cmv'
      when b.dre_grupo = 'IMPOSTOS' then 'impostos'
      when coalesce(f.variavel, false) = true
           and b.dre_grupo not in ('RECEITAS', 'PESSOAL', 'INFRAESTRUTURA', 'MARKETING E PUBLICIDADE', 'NÃO OPERACIONAL', 'CONTABIL', 'BENS DURÁVEIS')
           then 'outras_variaveis'
      when b.dre_grupo = 'PESSOAL' then 'pessoal'
      when b.dre_grupo = 'INFRAESTRUTURA' then 'infraestrutura'
      when b.dre_grupo = 'MARKETING E PUBLICIDADE' then 'marketing'
      when b.dre_grupo = 'NÃO OPERACIONAL' then 'nao_operacional'
      when b.dre_grupo = 'CONTABIL' then 'contabil'
      when b.dre_grupo = 'BENS DURÁVEIS' then 'capex'
      when b.dre_grupo is null or b.dre_grupo in ('#N/A', '') then 'nao_categorizado'
      else 'outros'
    end as componente
  from base b
    left join flags f on f.grupo = b.dre_grupo
), agg as (
  select c.mes,
    c.ano_mes,
    sum(c.total) as total_geral,
    sum(case when c.componente = 'receita' then c.total else 0::numeric end) as receita,
    sum(case when c.componente in ('cmv', 'impostos', 'outras_variaveis') then c.total else 0::numeric end) as variaveis,
    sum(case when c.componente = 'cmv' then c.total else 0::numeric end) as cmv,
    sum(case when c.componente = 'impostos' then c.total else 0::numeric end) as impostos,
    sum(case when c.componente = 'outras_variaveis' then c.total else 0::numeric end) as outras_variaveis,
    sum(case when c.componente = 'pessoal' then c.total else 0::numeric end) as pessoal,
    sum(case when c.componente = 'infraestrutura' then c.total else 0::numeric end) as infraestrutura,
    sum(case when c.componente = 'marketing' then c.total else 0::numeric end) as marketing,
    sum(case when c.componente = 'nao_operacional' then c.total else 0::numeric end) as nao_operacional,
    sum(case when c.componente = 'contabil' then c.total else 0::numeric end) as contabil,
    sum(case when c.componente = 'capex' then c.total else 0::numeric end) as capex,
    sum(case when c.componente = 'nao_categorizado' then c.total else 0::numeric end) as nao_categorizado,
    sum(case when c.componente = 'outros' then c.total else 0::numeric end) as outros
  from categorizado c
  group by c.mes, c.ano_mes
)
select mes,
  ano_mes,
  round(receita, 2) as receita,
  round(cmv, 2) as cmv,
  round(impostos, 2) as impostos,
  round(receita + variaveis, 2) as margem_contribuicao,
  case when receita > 0::numeric then round((receita + variaveis) / receita * 100::numeric, 1) else null::numeric end as mc_perc,
  round(pessoal, 2) as pessoal,
  round(infraestrutura, 2) as infraestrutura,
  round(marketing, 2) as marketing,
  round(receita + variaveis + pessoal + infraestrutura + marketing, 2) as resultado_operacional,
  case when receita > 0::numeric then round((receita + variaveis + pessoal + infraestrutura + marketing) / receita * 100::numeric, 1) else null::numeric end as margem_op_perc,
  round(nao_operacional, 2) as nao_operacional,
  round(contabil, 2) as contabil,
  round(capex, 2) as capex,
  round(nao_categorizado, 2) as nao_categorizado,
  round(total_geral, 2) as resultado_liquido,
  case when receita > 0::numeric then round(total_geral / receita * 100::numeric, 1) else null::numeric end as margem_liq_perc,
  case when receita > 0::numeric then round((- cmv) / receita * 100::numeric, 1) else null::numeric end as cmv_perc,
  case when receita > 0::numeric then round((- pessoal) / receita * 100::numeric, 1) else null::numeric end as pessoal_perc,
  round(outros, 2) as outros
from agg
order by mes;

comment on view public.painel_dre_cascata is
  'Cascata da DRE por mês com componentes mutuamente exclusivos. Impede sobreposição de despesas operacionais e garante integridade dos subtotais e do resultado líquido.';

commit;
