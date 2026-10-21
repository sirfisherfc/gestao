-- =====================================================================
-- saldo_mensal_calculado: CTEs mensais avaliadas uma vez só
-- =====================================================================
--
-- PROBLEMA
--   O worker da fila de recálculo (cada importação pela web cria uma tarefa)
--   grava o fechamento mensal lendo public.saldo_mensal_calculado. Nela, as
--   CTEs real_mes (soma de caixa_real_diario, ~2 s) e projecao_mes ficam
--   dentro de subconsultas por mês. Referenciadas uma vez só, o Postgres as
--   expande em cada mês: medido em 21/10/2026, 55 s para os 24 meses e
--   17-22 s mesmo filtrando um ou dois meses. É a mesma armadilha registrada
--   em 26/07/2026 (CANAL_IA) para o Calendário.
--
-- SOLUÇÃO
--   real_mes e projecao_mes passam a ser AS MATERIALIZED: cada uma é
--   calculada uma vez por leitura. O restante da definição é a vigente no
--   banco em 21/10/2026, sem outra mudança (a view não constava das
--   migrations; passa a ficar versionada aqui).
--
-- RESULTADO MEDIDO (transação descartada, md5 do resultado idêntico)
--   55 s -> 14,7 s; 2,7 s junto com os snapshots de 20261021070000.
--
-- OBJETOS
--   ~ public.saldo_mensal_calculado (create or replace; mesmas colunas, dono
--     e grants; a view não tem reloptions).
--
-- RISCOS
--   Baixo. MATERIALIZED não muda o resultado de uma consulta determinística;
--   now()/current_date são fixos na mesma consulta. Reversão: recriar sem
--   MATERIALIZED.
-- =====================================================================

begin;

create or replace view public.saldo_mensal_calculado as
 WITH corte AS (
         SELECT corte_caixa.dia
           FROM corte_caixa
         LIMIT 1
        ), mes_corte AS (
         SELECT date_trunc('month'::text, (( SELECT corte.dia
                   FROM corte))::timestamp with time zone)::date AS mes
        ), horizonte AS (
         SELECT GREATEST(( SELECT mes_corte.mes
                   FROM mes_corte), COALESCE(( SELECT max(meta_mensal.mes) AS max
                   FROM meta_mensal
                  WHERE meta_mensal.unidade = 'PRAIA'::text), ( SELECT mes_corte.mes
                   FROM mes_corte)), COALESCE(( SELECT date_trunc('month'::text, max(recebimento_conhecido.dia)::timestamp with time zone)::date AS date_trunc
                   FROM recebimento_conhecido), ( SELECT mes_corte.mes
                   FROM mes_corte)), COALESCE(( SELECT date_trunc('month'::text, max(recebimento_projetado.dia)::timestamp with time zone)::date AS date_trunc
                   FROM recebimento_projetado), ( SELECT mes_corte.mes
                   FROM mes_corte)), COALESCE(( SELECT date_trunc('month'::text, max(projecao_despesa_direta.dia)::timestamp with time zone)::date AS date_trunc
                   FROM projecao_despesa_direta), ( SELECT mes_corte.mes
                   FROM mes_corte)), COALESCE(( SELECT date_trunc('month'::text, max(projecao_despesa_fixa.dia)::timestamp with time zone)::date AS date_trunc
                   FROM projecao_despesa_fixa), ( SELECT mes_corte.mes
                   FROM mes_corte))) AS mes
        ), anchor AS (
         SELECT ( SELECT saldo_anchor.saldo_total
                   FROM saldo_anchor) AS saldo
        ), real_mes AS MATERIALIZED (
         SELECT date_trunc('month'::text, caixa_real_diario.dia::timestamp with time zone)::date AS mes,
            sum(caixa_real_diario.resultado_real) AS net
           FROM caixa_real_diario
          WHERE caixa_real_diario.dia <= (( SELECT corte.dia
                   FROM corte))
          GROUP BY (date_trunc('month'::text, caixa_real_diario.dia::timestamp with time zone)::date)
        ), projecao_mes AS MATERIALIZED (
         SELECT date_trunc('month'::text, p.dia::timestamp with time zone)::date AS mes,
            sum(p.valor) AS net
           FROM ( SELECT recebimento_conhecido.dia,
                    recebimento_conhecido.valor
                   FROM recebimento_conhecido
                UNION ALL
                 SELECT recebimento_projetado.dia,
                    recebimento_projetado.valor
                   FROM recebimento_projetado
                UNION ALL
                 SELECT projecao_despesa_direta.dia,
                    - projecao_despesa_direta.valor
                   FROM projecao_despesa_direta
                UNION ALL
                 SELECT projecao_despesa_fixa.dia,
                    - projecao_despesa_fixa.valor
                   FROM projecao_despesa_fixa) p
          WHERE p.dia > (( SELECT corte.dia
                   FROM corte))
          GROUP BY (date_trunc('month'::text, p.dia::timestamp with time zone)::date)
        ), meses AS (
         SELECT generate_series(date_trunc('month'::text, (( SELECT min(saldo_inicial.data_base) AS min
                   FROM saldo_inicial))::timestamp with time zone)::date::timestamp with time zone, (( SELECT horizonte.mes
                   FROM horizonte))::timestamp with time zone, '1 mon'::interval)::date AS mes
        ), meses_fim AS (
         SELECT meses.mes,
            (meses.mes + '1 mon'::interval - '1 day'::interval)::date AS fim_mes
           FROM meses
        )
 SELECT mes,
    to_char(mes::timestamp with time zone, 'YYYY-MM'::text) AS ano_mes,
    round(
        CASE
            WHEN fim_mes <= (( SELECT corte.dia
               FROM corte)) THEN (( SELECT anchor.saldo
               FROM anchor)) - COALESCE(( SELECT sum(r.net) AS sum
               FROM real_mes r
              WHERE r.mes > mf.mes AND r.mes <= (( SELECT mes_corte.mes
                       FROM mes_corte))), 0::numeric)
            ELSE (( SELECT anchor.saldo
               FROM anchor)) + COALESCE(( SELECT sum(p.net) AS sum
               FROM projecao_mes p
              WHERE p.mes >= (( SELECT mes_corte.mes
                       FROM mes_corte)) AND p.mes <= mf.mes), 0::numeric)
        END, 2) AS saldo_fim,
        CASE
            WHEN fim_mes <= (( SELECT corte.dia
               FROM corte)) THEN 'Real'::text
            ELSE 'Projetado'::text
        END AS situacao
   FROM meses_fim mf
  ORDER BY mes;

commit;
