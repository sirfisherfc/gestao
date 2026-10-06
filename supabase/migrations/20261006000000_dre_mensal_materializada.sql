-- =====================================================================
-- Painel: dre_mensal passa a ler um snapshot em vez de recalcular tudo
-- =====================================================================
--
-- PROBLEMA
--   public.dre_mensal agrega public.fato_financeiro, que reclassifica ao vivo
--   os ~56 mil lancamentos brutos (de-para, fontes, vigencias, ajustes). So
--   esse agregado custa ~2,2 s por leitura, e painel_resumo_mensal o le duas
--   vezes. Medido em 06/10/2026 (pg_stat_statements, role authenticated):
--     app_painel_resumo_mensal       media 6,7 s, pico 7,6 s
--     app_gerente_gasto_grupo        media 4,9 s, pico 7,5 s
--     app_gerente_resumo_mensal      media 4,5 s
--     app_gerente_dre_cascata_perc   media 4,1 s
--     app_painel_dre_cascata         media 3,7 s
--     app_painel_margem_contribuicao media 3,5 s
--     app_painel_composicao_despesa  media 2,0 s
--   EXPLAIN ANALYZE de painel_resumo_mensal: 5,7 a 11,3 s. O teto do role
--   authenticated e 8 s, entao a visao geral ja roda no limite do timeout,
--   e as leituras simultaneas de uma mesma pagina disputam CPU entre si.
--
-- SOLUCAO
--   private.mv_dre_mensal guarda o mesmo agregado (mesma consulta, mesmas
--   colunas e tipos). public.dre_mensal vira um select simples sobre ele, via
--   create or replace: nome, colunas, dono e grants continuam iguais, e as
--   quatro views dependentes (painel_resumo_mensal, painel_dre_cascata,
--   painel_composicao_despesa, painel_margem_contribuicao) e as sete app_*
--   acima delas nao precisam ser recriadas. Nenhuma funcao le dre_mensal.
--
--   O snapshot entra em private.refresh_painel_resiliente(), na mesma
--   subtransacao isolada dos demais. Ele ja e chamado:
--     - ao fim de cada importacao (refresh_painel);
--     - pelo worker da fila, que todas as RPCs de classificacao manual
--       acionam (agendar_refresh_classificacoes) - ~1 min hoje;
--     - pelo botao "Atualizar tudo agora" do Status.
--   E o mesmo comportamento que Despesas ja tem com mv_despesa_mensal.
--
-- OBJETOS
--   + private.mv_dre_mensal (materialized view) + indice unico p/ concurrently
--   ~ public.dre_mensal (create or replace, mesma assinatura)
--   ~ private.refresh_painel_resiliente() (+1 refresh isolado; resto igual a
--     20260921010000, conferido contra o banco em 06/10/2026)
--
-- RISCOS
--   - Defasagem: uma classificacao manual aparece no painel quando o worker
--     terminar (~1 min), nao no mesmo instante. Antes era imediato.
--   - refresh_painel() levanta se algum objeto falhar; um objeto a mais e uma
--     chance a mais de falha. Mitigacao: a consulta e a mesma que roda hoje ao
--     vivo, e o refresh fica isolado na resiliente.
--   - Sem mudanca de regra, valor ou permissao. O snapshot fica em private,
--     sem grant para anon/authenticated; dre_mensal continua sem SELECT para
--     eles (o acesso segue pelas app_* com gate de pagina).
--   - Idempotente: if not exists / create or replace.
-- =====================================================================

begin;

create materialized view if not exists private.mv_dre_mensal as
select date_trunc('month', f.data_competencia::timestamptz)::date as mes,
       f.empresa,
       f.unidade,
       f.dre_grupo,
       f.categoria,
       f.natureza,
       f.entra_dre,
       sum(f.valor) as total,
       count(*) as qtd,
       extract(year from f.data_competencia)::integer as ano,
       to_char(f.data_competencia::timestamptz, 'YYYY-MM') as ano_mes
from public.fato_financeiro f
where f.data_competencia is not null
group by date_trunc('month', f.data_competencia::timestamptz)::date,
         f.empresa, f.unidade, f.dre_grupo, f.categoria, f.natureza,
         f.entra_dre,
         extract(year from f.data_competencia)::integer,
         to_char(f.data_competencia::timestamptz, 'YYYY-MM');

-- Indice unico exigido pelo refresh concurrently. ano e ano_mes derivam do mes.
create unique index if not exists mv_dre_mensal_chave_uidx
  on private.mv_dre_mensal
  (mes, empresa, unidade, dre_grupo, categoria, natureza, entra_dre);

revoke all privileges on private.mv_dre_mensal from public, anon, authenticated;

create or replace view public.dre_mensal as
select mes, empresa, unidade, dre_grupo, categoria, natureza, entra_dre,
       total, qtd, ano, ano_mes
from private.mv_dre_mensal;

create or replace function private.refresh_painel_resiliente()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_falhas jsonb := '[]'::jsonb;
  v_ignorados jsonb := '[]'::jsonb;
  v_atualizados text[] := array[]::text[];
  v_saldo_ok boolean;
  v_fluxo_ok boolean;
  v_despesas_ok boolean := true;
begin
  set local statement_timeout = 0;

  -- 1. Saldo por conta: base da ancora que o fluxo usa. Vai primeiro.
  begin
    refresh materialized view concurrently private.mv_saldo_conta_diario;
    v_saldo_ok := true;
    v_atualizados := v_atualizados || 'private.mv_saldo_conta_diario'::text;
  exception when others then
    v_saldo_ok := false;
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'private.mv_saldo_conta_diario', 'erro', sqlerrm);
  end;

  -- 2. Fluxo: so faz sentido com a ancora fresca (ver ORDEM E DEPENDENCIA).
  if v_saldo_ok then
    begin
      refresh materialized view concurrently public.mv_fluxo_caixa_diario;
      v_fluxo_ok := true;
      v_atualizados := v_atualizados || 'public.mv_fluxo_caixa_diario'::text;
    exception when others then
      v_fluxo_ok := false;
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'public.mv_fluxo_caixa_diario', 'erro', sqlerrm);
    end;
  else
    v_fluxo_ok := false;
    v_ignorados := v_ignorados || jsonb_build_object(
      'objeto', 'public.mv_fluxo_caixa_diario',
      'motivo', 'o saldo por conta nao atualizou; a ancora ficaria velha');
  end if;

  -- 3. Despesas e conciliacao: independentes do saldo.
  begin
    refresh materialized view concurrently public.mv_despesa_mensal;
    v_atualizados := v_atualizados || 'public.mv_despesa_mensal'::text;
  exception when others then
    v_despesas_ok := false;
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'public.mv_despesa_mensal', 'erro', sqlerrm);
  end;

  begin
    refresh materialized view concurrently public.mv_despesa_diaria;
    v_atualizados := v_atualizados || 'public.mv_despesa_diaria'::text;
  exception when others then
    v_despesas_ok := false;
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'public.mv_despesa_diaria', 'erro', sqlerrm);
  end;

  begin
    refresh materialized view concurrently public.mv_conciliacao_contabil;
    v_atualizados := v_atualizados || 'public.mv_conciliacao_contabil'::text;
  exception when others then
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'public.mv_conciliacao_contabil', 'erro', sqlerrm);
  end;

  -- DRE mensal: agregado de fato_financeiro lido por public.dre_mensal e,
  -- por ela, pelas views do painel (visao geral, vendas, DRE, despesas e
  -- gerente). Independente do saldo. Se falhar, o snapshot anterior segue
  -- valendo e a falha aparece no relatorio, como nos demais objetos.
  begin
    refresh materialized view concurrently private.mv_dre_mensal;
    v_atualizados := v_atualizados || 'private.mv_dre_mensal'::text;
  exception when others then
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'private.mv_dre_mensal', 'erro', sqlerrm);
  end;

  -- 4. Validadores: cada um so confere o que foi atualizado de fato.
  if v_saldo_ok then
    begin
      perform private.validar_saldo_diario_materializado();
    exception when others then
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'private.validar_saldo_diario_materializado()', 'erro', sqlerrm);
    end;
  end if;

  if v_fluxo_ok then
    begin
      perform private.validar_fluxo_materializado();
    exception when others then
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'private.validar_fluxo_materializado()', 'erro', sqlerrm);
    end;
  end if;

  if v_despesas_ok then
    begin
      perform private.validar_despesas_materializadas();
    exception when others then
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'private.validar_despesas_materializadas()', 'erro', sqlerrm);
    end;
  end if;

  return jsonb_build_object(
    'ok', jsonb_array_length(v_falhas) = 0 and jsonb_array_length(v_ignorados) = 0,
    'atualizados', to_jsonb(v_atualizados),
    'ignorados', v_ignorados,
    'falhas', v_falhas,
    'em', clock_timestamp()
  );
end;
$function$;

revoke all privileges on function private.refresh_painel_resiliente()
  from public, anon, authenticated;

notify pgrst, 'reload schema';

commit;
