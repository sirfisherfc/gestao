-- =====================================================================
-- Migration: 20260906080000_cascata_expoe_outras_variaveis.sql
-- Etapa 5 da auditoria / apresentação da cascata
--
-- Problema
-- --------
-- A view da cascata já agregava o componente `outras_variaveis` e o somava
-- dentro de `margem_contribuicao`, mas nunca o publicava como coluna. Quem lia
-- a DRE via a margem cair sem conseguir ver o desconto que a derrubou: para
-- configurações em que esse componente é diferente de zero, a apresentação
-- ficava incompleta e o valor só podia ser obtido por subtração.
--
-- Correção
-- --------
-- Publica `outras_variaveis` em public.painel_dre_cascata e propaga para
-- public.app_painel_dre_cascata, que é a view lida pela aplicação. A coluna vai
-- ao final em ambas, para que `create or replace view` seja aceito e nenhum
-- consumidor atual quebre.
--
-- O front-end já está preparado: dre.html testa a presença da propriedade
-- (`temOutrasVariaveis`) e, quando ela existe, acrescenta a linha "Outras
-- despesas variáveis" à cascata e ao detalhamento. Nenhuma mudança de
-- aplicação é necessária.
--
-- Nenhum número muda: o componente já estava dentro dos subtotais. Esta
-- migration apenas torna visível o que já era computado.
-- =====================================================================

begin;

create or replace view public.painel_dre_cascata as
WITH base AS (
         SELECT dre_mensal.mes,
            dre_mensal.ano_mes,
            dre_mensal.dre_grupo,
            dre_mensal.natureza,
            sum(dre_mensal.total) AS total
           FROM dre_mensal
          WHERE dre_mensal.entra_dre = true AND dre_mensal.unidade = unidade_principal_nome()
          GROUP BY dre_mensal.mes, dre_mensal.ano_mes, dre_mensal.dre_grupo, dre_mensal.natureza
        ), flags AS (
         SELECT grupo_variavel.grupo,
            grupo_variavel.variavel
           FROM grupo_variavel
        ), categorizado AS (
         SELECT b.mes,
            b.ano_mes,
            b.total,
                CASE
                    WHEN b.dre_grupo = 'RECEITAS'::text THEN 'receita'::text
                    WHEN b.dre_grupo = 'DESPESA DIRETA DE VENDA'::text THEN 'cmv'::text
                    WHEN b.dre_grupo = 'IMPOSTOS'::text THEN 'impostos'::text
                    WHEN COALESCE(f.variavel, false) = true AND (b.dre_grupo <> ALL (ARRAY['RECEITAS'::text, 'PESSOAL'::text, 'INFRAESTRUTURA'::text, 'MARKETING E PUBLICIDADE'::text, 'NÃO OPERACIONAL'::text, 'CONTABIL'::text, 'BENS DURÁVEIS'::text])) THEN 'outras_variaveis'::text
                    WHEN b.dre_grupo = 'PESSOAL'::text THEN 'pessoal'::text
                    WHEN b.dre_grupo = 'INFRAESTRUTURA'::text THEN 'infraestrutura'::text
                    WHEN b.dre_grupo = 'MARKETING E PUBLICIDADE'::text THEN 'marketing'::text
                    WHEN b.dre_grupo = 'NÃO OPERACIONAL'::text THEN 'nao_operacional'::text
                    WHEN b.dre_grupo = 'CONTABIL'::text THEN 'contabil'::text
                    WHEN b.dre_grupo = 'BENS DURÁVEIS'::text THEN 'capex'::text
                    WHEN b.dre_grupo IS NULL OR (b.dre_grupo = ANY (ARRAY['#N/A'::text, ''::text])) THEN 'nao_categorizado'::text
                    ELSE 'outros'::text
                END AS componente
           FROM base b
             LEFT JOIN flags f ON f.grupo = b.dre_grupo
        ), agg AS (
         SELECT c.mes,
            c.ano_mes,
            sum(c.total) AS total_geral,
            sum(
                CASE
                    WHEN c.componente = 'receita'::text THEN c.total
                    ELSE 0::numeric
                END) AS receita,
            sum(
                CASE
                    WHEN c.componente = ANY (ARRAY['cmv'::text, 'impostos'::text, 'outras_variaveis'::text]) THEN c.total
                    ELSE 0::numeric
                END) AS variaveis,
            sum(
                CASE
                    WHEN c.componente = 'cmv'::text THEN c.total
                    ELSE 0::numeric
                END) AS cmv,
            sum(
                CASE
                    WHEN c.componente = 'impostos'::text THEN c.total
                    ELSE 0::numeric
                END) AS impostos,
            sum(
                CASE
                    WHEN c.componente = 'outras_variaveis'::text THEN c.total
                    ELSE 0::numeric
                END) AS outras_variaveis,
            sum(
                CASE
                    WHEN c.componente = 'pessoal'::text THEN c.total
                    ELSE 0::numeric
                END) AS pessoal,
            sum(
                CASE
                    WHEN c.componente = 'infraestrutura'::text THEN c.total
                    ELSE 0::numeric
                END) AS infraestrutura,
            sum(
                CASE
                    WHEN c.componente = 'marketing'::text THEN c.total
                    ELSE 0::numeric
                END) AS marketing,
            sum(
                CASE
                    WHEN c.componente = 'nao_operacional'::text THEN c.total
                    ELSE 0::numeric
                END) AS nao_operacional,
            sum(
                CASE
                    WHEN c.componente = 'contabil'::text THEN c.total
                    ELSE 0::numeric
                END) AS contabil,
            sum(
                CASE
                    WHEN c.componente = 'capex'::text THEN c.total
                    ELSE 0::numeric
                END) AS capex,
            sum(
                CASE
                    WHEN c.componente = 'nao_categorizado'::text THEN c.total
                    ELSE 0::numeric
                END) AS nao_categorizado,
            sum(
                CASE
                    WHEN c.componente = 'outros'::text THEN c.total
                    ELSE 0::numeric
                END) AS outros
           FROM categorizado c
          GROUP BY c.mes, c.ano_mes
        )
 SELECT mes,
    ano_mes,
    round(receita, 2) AS receita,
    round(cmv, 2) AS cmv,
    round(impostos, 2) AS impostos,
    round(receita + variaveis, 2) AS margem_contribuicao,
        CASE
            WHEN receita > 0::numeric THEN round((receita + variaveis) / receita * 100::numeric, 1)
            ELSE NULL::numeric
        END AS mc_perc,
    round(pessoal, 2) AS pessoal,
    round(infraestrutura, 2) AS infraestrutura,
    round(marketing, 2) AS marketing,
    round(receita + variaveis + pessoal + infraestrutura + marketing, 2) AS resultado_operacional,
        CASE
            WHEN receita > 0::numeric THEN round((receita + variaveis + pessoal + infraestrutura + marketing) / receita * 100::numeric, 1)
            ELSE NULL::numeric
        END AS margem_op_perc,
    round(nao_operacional, 2) AS nao_operacional,
    round(contabil, 2) AS contabil,
    round(capex, 2) AS capex,
    round(nao_categorizado, 2) AS nao_categorizado,
    round(total_geral, 2) AS resultado_liquido,
        CASE
            WHEN receita > 0::numeric THEN round(total_geral / receita * 100::numeric, 1)
            ELSE NULL::numeric
        END AS margem_liq_perc,
        CASE
            WHEN receita > 0::numeric THEN round((- cmv) / receita * 100::numeric, 1)
            ELSE NULL::numeric
        END AS cmv_perc,
        CASE
            WHEN receita > 0::numeric THEN round((- pessoal) / receita * 100::numeric, 1)
            ELSE NULL::numeric
        END AS pessoal_perc,
    round(outros, 2) AS outros,
  round(outras_variaveis, 2) AS outras_variaveis
   FROM agg
  ORDER BY mes;

comment on view public.painel_dre_cascata is
  'Cascata da DRE por mês com componentes mutuamente exclusivos. Publica outras_variaveis para que o desconto embutido na margem de contribuição seja visível.';

create or replace view public.app_painel_dre_cascata as
SELECT mes,
    ano_mes,
    receita,
    cmv,
    impostos,
    margem_contribuicao,
    mc_perc,
    pessoal,
    infraestrutura,
    marketing,
    resultado_operacional,
    margem_op_perc,
    nao_operacional,
    contabil,
    capex,
    nao_categorizado,
    resultado_liquido,
    margem_liq_perc,
    cmv_perc,
    pessoal_perc,
    outros,
    outras_variaveis
   FROM painel_dre_cascata s
  WHERE usuario_pode_acessar_alguma_pagina(ARRAY['index.html'::text, 'dre.html'::text]);

do $validacao$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'painel_dre_cascata'
      and column_name = 'outras_variaveis'
  ) then
    raise exception 'Validacao falhou: painel_dre_cascata nao expoe outras_variaveis.';
  end if;

  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'app_painel_dre_cascata'
      and column_name = 'outras_variaveis'
  ) then
    raise exception 'Validacao falhou: app_painel_dre_cascata nao propagou a coluna.';
  end if;
end;
$validacao$;

commit;
