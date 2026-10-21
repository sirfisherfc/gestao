-- =====================================================================
-- Snapshots da Conciliação Stone (base por stone_id e resumo mensal)
-- =====================================================================
--
-- PROBLEMA (logs da API e EXPLAIN em 21/10/2026)
--   public.conciliacao_stone agrega as ~44 mil vendas e ~34 mil parcelas
--   Stone por stone_id a cada leitura (0,3-0,4 s; 3,0 s em produção num
--   momento de CPU disputada). A página lê pelo resumo mensal, que refaz a
--   base inteira (0,36 s), e pelo detalhe via private.ler_conciliacao_stone(),
--   função SECURITY DEFINER que impede o filtro de mês de entrar na consulta.
--
-- SOLUÇÃO
--   private.mv_conciliacao_stone (mesma consulta, índice único por stone_id e
--   índice por mes_referencia) e private.mv_conciliacao_stone_resumo_mensal
--   (mesma agregação). As duas views públicas leem os snapshots; a função
--   ler_* e as app_* não mudam. O refresh resiliente atualiza base e resumo
--   juntos, logo depois dos snapshots Stone.
--
-- ATRASO DE DADO
--   A conciliação passa a refletir uma carga Stone quando o refresh que a
--   carga dispara termina, como DRE, saldo e vendas. Não há entrada manual
--   nessas views.
--
-- RESULTADO MEDIDO (transação descartada, conteúdo com md5 idêntico)
--   resumo mensal 364 ms -> 0,7 ms; detalhe do mês 335 ms -> ~1 ms;
--   conciliacao_stone_resumo 272 ms -> 28 ms.
--
-- ORDEM
--   O resumo mensal ordenava só por mês; a ordem entre situações do mesmo mês
--   dependia do plano. Agora é por mês (decrescente) e situação. A página
--   procura cada situação pelo nome e ordena o gráfico por quantidade.
--
-- REVERSÃO
--   Recriar as duas views de 20260714000000 e a resiliente de
--   20261021070000; depois, drop dos dois snapshots.
-- =====================================================================

begin;

set local lock_timeout = '5s';

create temp table _hash_antes_conc on commit drop as
  select 'conciliacao_stone' as objeto, md5(string_agg(t::text, '|' order by t::text)) as hash from public.conciliacao_stone t
  union all select 'conciliacao_stone_resumo_mensal', md5(string_agg(t::text, '|' order by t::text)) from public.conciliacao_stone_resumo_mensal t
  union all select 'conciliacao_stone_resumo', md5(string_agg(t::text, '|' order by t::text)) from public.conciliacao_stone_resumo t;

create materialized view if not exists private.mv_conciliacao_stone as
with v as (
  select
    stone_id,
    sum(valor_bruto) as bruto_venda,
    count(*) as n_venda,
    max(data_venda::date) as data_venda,
    max(produto) as produto
  from public.raw_stone_vendas
  where stone_id is not null
  group by stone_id
), r as (
  select
    stone_id,
    sum(valor_bruto) as bruto_receb,
    sum(valor_liquido) as liquido_receb,
    count(*) as n_parcelas,
    min(data_vencimento) as primeiro_venc,
    max(data_vencimento) as ultimo_venc,
    bool_or(categoria ilike '%cancelamento%') as tem_cancelamento
  from public.raw_stone_recebiveis
  where stone_id is not null
  group by stone_id
)
select
  coalesce(v.stone_id, r.stone_id) as stone_id,
  v.data_venda,
  v.bruto_venda,
  v.n_venda,
  r.bruto_receb,
  r.liquido_receb,
  r.n_parcelas,
  r.primeiro_venc,
  round((coalesce(v.bruto_venda, 0::numeric) - coalesce(r.bruto_receb, 0::numeric)), 2) as diferenca_bruto,
  case
    when coalesce(r.tem_cancelamento, false) then 'cancelado/estornado'
    when v.stone_id is null then 'recebível sem venda'
    when r.stone_id is null and v.produto in ('Pix QRcode', 'Voucher') then 'sem recebível esperado (Pix/Voucher)'
    when r.stone_id is null then 'venda sem recebível'
    when abs(coalesce(v.bruto_venda, 0::numeric) - coalesce(r.bruto_receb, 0::numeric)) > 0.01 then 'valor diverge'
    else 'ok'
  end as situacao,
  coalesce(v.data_venda, r.primeiro_venc) as mes_referencia,
  v.produto
from v full join r on v.stone_id = r.stone_id;

create unique index if not exists mv_conciliacao_stone_id_uidx
  on private.mv_conciliacao_stone (stone_id);
create index if not exists mv_conciliacao_stone_mes_idx
  on private.mv_conciliacao_stone (mes_referencia);

revoke all privileges on private.mv_conciliacao_stone from public, anon, authenticated;

create or replace view public.conciliacao_stone as
select stone_id, data_venda, bruto_venda, n_venda, bruto_receb, liquido_receb,
       n_parcelas, primeiro_venc, diferenca_bruto, situacao, mes_referencia, produto
from private.mv_conciliacao_stone;

-- Criado depois da troca acima, então já agrega a partir do snapshot base.
create materialized view if not exists private.mv_conciliacao_stone_resumo_mensal as
select
  date_trunc('month', mes_referencia)::date as mes,
  to_char(date_trunc('month', mes_referencia), 'YYYY-MM') as ano_mes,
  situacao,
  count(*) as qtd,
  round(sum(coalesce(bruto_venda, 0::numeric)), 2) as total_venda,
  round(sum(coalesce(bruto_receb, 0::numeric)), 2) as total_recebivel
from public.conciliacao_stone
where mes_referencia is not null
group by 1, 2, 3;

create unique index if not exists mv_conciliacao_stone_resumo_mensal_uidx
  on private.mv_conciliacao_stone_resumo_mensal (mes, situacao);

revoke all privileges on private.mv_conciliacao_stone_resumo_mensal from public, anon, authenticated;

create or replace view public.conciliacao_stone_resumo_mensal as
select mes, ano_mes, situacao, qtd, total_venda, total_recebivel
from private.mv_conciliacao_stone_resumo_mensal
order by mes desc, situacao;

create or replace function private.refresh_painel_resiliente()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
-- Só nesta sessão de fundo: com o padrão de 2 MB, mv_conciliacao_contabil
-- gravava ~470 MB em disco temporário a cada refresh (medido em 21/10/2026).
set work_mem = '16MB'
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

  -- 0. Snapshots-base lidos pelos objetos seguintes (20261021070000): o corte
  -- de caixa (saldo por conta, fluxo e projeções) e as vendas Stone por dia
  -- (fluxo e projeções). Vão primeiro; se um falhar, o snapshot anterior
  -- continua valendo e a falha aparece no relatório.
  begin
    refresh materialized view concurrently private.mv_corte_caixa_base;
    v_atualizados := v_atualizados || 'private.mv_corte_caixa_base'::text;
  exception when others then
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'private.mv_corte_caixa_base', 'erro', sqlerrm);
  end;

  begin
    refresh materialized view concurrently private.mv_venda_stone_dia;
    v_atualizados := v_atualizados || 'private.mv_venda_stone_dia'::text;
  exception when others then
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'private.mv_venda_stone_dia', 'erro', sqlerrm);
  end;

  -- Conciliação Stone (20261021110000): base por stone_id e resumo mensal,
  -- no mesmo bloco para nunca ficarem em versões diferentes. Só dependem das
  -- tabelas Stone.
  begin
    refresh materialized view concurrently private.mv_conciliacao_stone;
    refresh materialized view concurrently private.mv_conciliacao_stone_resumo_mensal;
    v_atualizados := v_atualizados || 'private.mv_conciliacao_stone'::text
      || 'private.mv_conciliacao_stone_resumo_mensal'::text;
  exception when others then
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'private.mv_conciliacao_stone', 'erro', sqlerrm);
  end;

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

do $validacao$
declare
  v_dif text;
  v_src text;
begin
  select string_agg(a.objeto, ', ' order by a.objeto)
  into v_dif
  from _hash_antes_conc a
  join (
  select 'conciliacao_stone' as objeto, md5(string_agg(t::text, '|' order by t::text)) as hash from public.conciliacao_stone t
  union all select 'conciliacao_stone_resumo_mensal', md5(string_agg(t::text, '|' order by t::text)) from public.conciliacao_stone_resumo_mensal t
  union all select 'conciliacao_stone_resumo', md5(string_agg(t::text, '|' order by t::text)) from public.conciliacao_stone_resumo t
  ) d using (objeto)
  where a.hash is distinct from d.hash;

  if v_dif is not null then
    raise exception 'Snapshots da conciliacao mudaram o resultado de: %', v_dif;
  end if;

  select lower(p.prosrc) into v_src
  from pg_catalog.pg_proc p
  where p.oid = 'private.refresh_painel_resiliente()'::regprocedure;

  if position('private.mv_conciliacao_stone_resumo_mensal' in v_src) = 0
     or position('private.mv_venda_stone_dia' in v_src) = 0
     or position('private.mv_corte_caixa_base' in v_src) = 0 then
    raise exception 'Validacao falhou: refresh nao atualiza todos os snapshots.';
  end if;
end;
$validacao$;

notify pgrst, 'reload schema';

commit;
