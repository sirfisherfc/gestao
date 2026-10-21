-- =====================================================================
-- Snapshots do corte de caixa e das vendas Stone por dia
-- =====================================================================
--
-- PROBLEMA (medido em 21/10/2026, docs/DESEMPENHO_PAINEL.md)
--   O painel recalcula a cada leitura duas bases que só mudam com uma carga:
--   - public.corte_caixa faz max(data_caixa) sobre public.fato_financeiro
--     (56 mil lançamentos reclassificados ao vivo): 0,3 s sozinha e 1,4 s
--     dentro do Calendário. Entra em 12 views e 8 funções.
--   - public.venda_diaria refaz a parte Stone (44 mil vendas, mapa de
--     terminais e cancelamentos) a cada avaliação, 0,2 s; é avaliada 3 vezes
--     em projecao_venda_diaria, 4 em painel_resumo_mensal e ~5 no Calendário.
--   Resultado: Calendário 3,3-8,8 s (acima do teto de 8 s às vezes), resumo
--   0,9 s, projeções ~1 s cada, cartão do gerente 2,4 s.
--
-- SOLUÇÃO
--   - private.mv_corte_caixa_base guarda só max(data_caixa). corte_caixa
--     continua calculando "ontem" ao vivo, então a virada do dia segue
--     igual e não precisa de job novo.
--   - private.mv_venda_stone_dia guarda as vendas Stone líquidas de
--     cancelamento por dia, stonecode e produto (mesma regra de
--     recebimento_stone_net). venda_diaria e o Calendário leem dela e aplicam
--     ao vivo as flags de fonte e de conta. Dinheiro (venda_especie),
--     Fundopay e Pix do BB continuam ao vivo.
--   - private.refresh_painel_resiliente() atualiza os dois snapshots antes
--     de tudo e passa a usar work_mem de 16 MB só na própria execução.
--
-- ATRASO DE DADO
--   O corte e as vendas Stone avançam quando o refresh disparado pela própria
--   carga termina (importação web, scripts e "Atualizar tudo agora"), como
--   já acontece com DRE, saldo e fluxo. Lançamentos manuais não mudam.
--
-- RESULTADO MEDIDO (transação descartada, md5 de cada view idêntico)
--   Calendário 6,7 s -> 0,8 s; painel_resumo_mensal 0,93 -> 0,14 s;
--   projecao_despesa_direta 0,99 -> 0,06 s; recebimento_projetado 1,0 ->
--   0,06 s; painel_saldo_atual 0,97 -> 0,07 s; cartão do gerente 2,4 ->
--   0,85 s (junto com os índices de 20261021050000).
--
-- OBJETOS
--   + private.mv_corte_caixa_base, private.mv_venda_stone_dia (+ índices
--     únicos para refresh concurrently; sem grant para o navegador)
--   ~ public.corte_caixa, public.venda_diaria (create or replace; mesmas
--     colunas e tipos, dono e grants; sem reloptions)
--   ~ public.listar_calendario_financeiro(date): só a CTE vendas_stone muda
--   ~ private.refresh_painel_resiliente(): +2 refreshes isolados e work_mem;
--     o resto é o texto de 20261006000000, conferido igual ao banco
--
-- VALIDAÇÃO
--   A migration calcula o md5 de nove views antes da troca e aborta se
--   qualquer uma mudar depois dela.
--
-- REVERSÃO
--   Recriar corte_caixa (20260818110000), venda_diaria (20260818010000), a
--   função do Calendário (20260906050000) e a resiliente (20261006000000);
--   depois, drop das duas materialized views.
-- =====================================================================

begin;

-- Não esperar indefinidamente por um refresh em andamento: falhar e tentar
-- de novo depois é melhor do que travar as páginas atrás desta migration.
set local lock_timeout = '5s';

-- 1. Resultado atual, antes de qualquer troca (só leitura).
create temp table _hash_antes on commit drop as
  select 'corte_caixa' as objeto, md5(string_agg(t::text, '|' order by t::text)) as hash from public.corte_caixa t
  union all select 'venda_diaria', md5(string_agg(t::text, '|' order by t::text)) from public.venda_diaria t
  union all select 'projecao_venda_diaria', md5(string_agg(t::text, '|' order by t::text)) from public.projecao_venda_diaria t
  union all select 'painel_resumo_mensal', md5(string_agg(t::text, '|' order by t::text)) from public.painel_resumo_mensal t
  union all select 'painel_diario', md5(string_agg(t::text, '|' order by t::text)) from public.painel_diario t
  union all select 'recebimento_conhecido', md5(string_agg(t::text, '|' order by t::text)) from public.recebimento_conhecido t
  union all select 'recebimento_projetado', md5(string_agg(t::text, '|' order by t::text)) from public.recebimento_projetado t
  union all select 'projecao_despesa_direta', md5(string_agg(t::text, '|' order by t::text)) from public.projecao_despesa_direta t
  union all select 'projecao_despesa_fixa', md5(string_agg(t::text, '|' order by t::text)) from public.projecao_despesa_fixa t;

-- 2. Snapshots novos (objetos novos: não bloqueiam ninguém).
create materialized view if not exists private.mv_corte_caixa_base as
select 1::smallint as id,
       max(f.data_caixa) as max_data_caixa
from public.fato_financeiro f;

create unique index if not exists mv_corte_caixa_base_id_uidx
  on private.mv_corte_caixa_base (id);

revoke all privileges on private.mv_corte_caixa_base from public, anon, authenticated;

create materialized view if not exists private.mv_venda_stone_dia as
with mapa_terminal as (
  select v.n_serie, min(v.stonecode) as stonecode
  from public.raw_stone_vendas v
  where v.stonecode is not null and v.n_serie is not null
  group by v.n_serie
), cancelado as (
  select r.stone_id, sum(abs(r.valor_bruto)) as cancelado
  from public.raw_stone_recebiveis r
  where r.categoria ilike '%cancelamento%'
  group by r.stone_id
)
select v.data_venda::date as dia,
       coalesce(v.stonecode, m.stonecode) as stonecode,
       v.produto,
       sum(v.valor_bruto - coalesce(c.cancelado, 0::numeric)) as bruto_net,
       count(*)::integer as qtd
from public.raw_stone_vendas v
left join mapa_terminal m on m.n_serie = v.n_serie
left join cancelado c on c.stone_id = v.stone_id
where v.data_venda is not null
group by v.data_venda::date, coalesce(v.stonecode, m.stonecode), v.produto;

-- Índice único exigido pelo refresh concurrently; o group by garante a chave.
create unique index if not exists mv_venda_stone_dia_chave_uidx
  on private.mv_venda_stone_dia (dia, stonecode, produto);

revoke all privileges on private.mv_venda_stone_dia from public, anon, authenticated;

-- 3. Leitores passam a usar os snapshots (bloqueio curto, até o commit).
create or replace view public.corte_caixa as
with cfg as (
  select coalesce(
    (select c.fuso_horario
       from public.configuracao_operacional c
      where c.singleton
      limit 1),
    current_setting('TimeZone')
  ) as fuso
)
select least(
  (select b.max_data_caixa from private.mv_corte_caixa_base b),
  (now() at time zone (select cfg.fuso from cfg))::date - 1
) as dia;

create or replace view public.venda_diaria as
select dia, sum(bruto) as bruto, sum(qtd) as qtd_vendas
from (
  -- Vendas Stone líquidas de cancelamento, já somadas por dia, stonecode e
  -- produto em private.mv_venda_stone_dia. As flags de fonte e de conta
  -- continuam lidas ao vivo, como em public.recebimento_stone_net.
  select s.dia, s.bruto_net as bruto, s.qtd
  from private.mv_venda_stone_dia s
  left join public.stone_conta sc on sc.stonecode = s.stonecode
  where exists (
      select 1 from public.fonte_financeira f
      where f.chave = 'stone_vendas' and f.ativa and f.entra_faturamento
    )
    and coalesce(sc.ativa and sc.entra_faturamento, true)

  union all

  select e.data, e.valor, 0
  from public.venda_especie e
  where e.unidade = public.unidade_principal_nome()
    and exists (
      select 1 from public.fonte_financeira f
      where f.chave = 'venda_especie' and f.ativa and f.entra_faturamento
    )

  union all

  select f.data_venda::date, f.valor_venda::numeric, 1
  from public.raw_fundopay_vendas f
  where lower(btrim(f.situacao)) = 'aprovada'
    and exists (
      select 1 from public.fonte_financeira x
      where x.chave = 'fundopay' and x.ativa and x.entra_faturamento
    )

  union all

  select (b.data - 1), b.valor::numeric, 1
  from public.raw_bb b
  where b.lancamento = 'Pix-Recebido QR Code'
    and b.valor > 0
    and exists (
      select 1 from public.fonte_financeira f
      where f.chave = 'bb_pix_qr' and f.ativa and f.entra_faturamento
    )
) x
group by dia;

CREATE OR REPLACE FUNCTION public.listar_calendario_financeiro(p_mes date)
 RETURNS TABLE(dia date, dia_semana smallint, modo text, meta_dia numeric, meta_acumulada numeric, faturamento_dia numeric, faturamento_acumulado numeric, venda_credito numeric, venda_debito numeric, venda_pix numeric, venda_extras numeric, venda_dinheiro numeric, recebimento_total numeric, recebimento_credito numeric, recebimento_debito numeric, recebimento_pix numeric, recebimento_projetado numeric, despesa_total numeric, despesa_recorrente numeric, despesa_nao_recorrente numeric, despesa_recorrente_registrada numeric, despesa_recorrente_nao_conciliada numeric, saldo_caixa numeric)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'public'
AS $function$
begin
  if not public.usuario_pode_acessar_pagina('calendario.html') then
    raise exception using errcode = '42501', message = 'Acesso nao autorizado.';
  end if;
  if p_mes is null or p_mes <> date_trunc('month', p_mes)::date then
    raise exception using errcode = '22023', message = 'Mes invalido.';
  end if;

  return query
  with cortes as (
    select (select cv.dia from public.corte_venda cv) as venda,
           (select cc.dia from public.corte_caixa cc) as caixa
  ), janela as (
    -- Comeca no dia seguinte ao corte quando o mes pedido e futuro, para o
    -- acumulado do saldo atravessar os meses intermediarios.
    select least(p_mes, coalesce(ct.caixa, p_mes) + 1) as inicio,
           (p_mes + interval '1 month - 1 day')::date as fim
    from cortes ct
  ), dias as (
    select gs::date as dia
    from janela j,
      generate_series(j.inicio::timestamp, j.fim::timestamp, interval '1 day') gs
  ), vendas_stone as (
    -- Mesma soma de public.recebimento_stone_net, lida do snapshot diário por
    -- stonecode e produto, com as mesmas flags de fonte e de conta ao vivo.
    select s.dia,
      sum(case when public.unaccent(lower(s.produto)) like 'credito%'
        then s.bruto_net else 0 end) as credito,
      sum(case when public.unaccent(lower(s.produto)) like 'debito%'
        then s.bruto_net else 0 end) as debito,
      sum(case when lower(s.produto) like 'pix%'
        then s.bruto_net else 0 end) as pix,
      sum(case when public.unaccent(lower(s.produto)) not like 'credito%'
                    and public.unaccent(lower(s.produto)) not like 'debito%'
                    and lower(s.produto) not like 'pix%'
        then s.bruto_net else 0 end) as extras
    from private.mv_venda_stone_dia s
    left join public.stone_conta sc on sc.stonecode = s.stonecode
    where s.dia >= p_mes
      and s.dia < p_mes + interval '1 month'
      and exists (
        select 1 from public.fonte_financeira f
        where f.chave = 'stone_vendas' and f.ativa and f.entra_faturamento
      )
      and coalesce(sc.ativa and sc.entra_faturamento, true)
    group by s.dia
  ), vendas_dinheiro as (
    select v.data as dia, sum(v.valor) as dinheiro
    from public.venda_especie v
    where v.data >= p_mes and v.data < p_mes + interval '1 month'
    group by v.data
  ), metas as (
    select p.dia, p.meta_dia from public.painel_diario p
    where p.dia >= p_mes and p.dia < p_mes + interval '1 month'
  ), vendas_total as (
    select p.dia, p.venda, p.tipo from public.projecao_venda_diaria p
    where p.dia >= p_mes and p.dia < p_mes + interval '1 month'
  ), recebiveis as (
    select r.data_vencimento as dia,
      sum(case when public.unaccent(lower(r.produto)) like 'credito%'
        then r.valor_liquido else 0 end) as credito,
      sum(case when public.unaccent(lower(r.produto)) like 'debito%'
        then r.valor_liquido else 0 end) as debito
    from public.raw_stone_recebiveis r
    left join public.stone_conta sc on sc.stonecode = r.stonecode
    where r.data_vencimento >= (select j.inicio from janela j)
      and r.data_vencimento < p_mes + interval '1 month'
      and coalesce(sc.ativa and sc.entra_faturamento, true)
    group by r.data_vencimento
  ), movimento_real as materialized (
    -- Credito e debito na mesma passada: antes eram dois scans completos
    -- do fato_financeiro para o mesmo recorte.
    select
      f.data_caixa as dia,
      sum(case
        when f.movimentacao = 'Crédito'
         and f.origem = 'stone_extrato' and f.tipo = 'Recebível de Cartão'
          then abs(f.valor) else 0 end) as cartoes,
      sum(case
        when f.movimentacao = 'Crédito'
         and f.origem = 'stone_extrato' and f.tipo = 'Transação'
          then abs(f.valor) else 0 end) as qr_code,
      sum(case
        when f.movimentacao = 'Crédito'
         and (f.origem is distinct from 'stone_extrato'
              or coalesce(f.tipo, '') <> all(
                array['Recebível de Cartão', 'Transação']::text[]
              ))
          then abs(f.valor) else 0 end) as outras,
      sum(case when f.movimentacao = 'Crédito' then abs(f.valor) else 0 end) as total_credito,
      sum(case when f.movimentacao = 'Débito' then abs(f.valor) else 0 end) as total_debito
    from public.fato_financeiro f
    where f.data_caixa >= p_mes
      and f.data_caixa < p_mes + interval '1 month'
      and f.movimentacao in ('Crédito', 'Débito')
      and (
        exists (
          select 1
          from public.fonte_financeira cfg_fonte
          where cfg_fonte.chave = f.origem
            and cfg_fonte.ativa
            and cfg_fonte.entra_caixa
        )
        or (
          not exists (
            select 1
            from public.fonte_financeira cfg_conhecida
            where cfg_conhecida.chave = f.origem
          )
          and (
            upper(coalesce(f.empresa, '')) = upper(public.unidade_principal_nome())
            or exists (
              select 1
              from public.fonte_financeira cfg_historica
              left join public.conta conta_historica
                on conta_historica.id = cfg_historica.conta_id
              where cfg_historica.ativa
                and cfg_historica.entra_caixa
                and cfg_historica.entra_caixa_historico
                and regexp_replace(
                      lower(coalesce(f.empresa, '')),
                      '[^a-z0-9]+', '', 'g'
                    ) = any (array[
                      regexp_replace(lower(cfg_historica.chave), '[^a-z0-9]+', '', 'g'),
                      regexp_replace(lower(cfg_historica.nome), '[^a-z0-9]+', '', 'g'),
                      regexp_replace(lower(coalesce(conta_historica.nome, '')), '[^a-z0-9]+', '', 'g'),
                      regexp_replace(lower(coalesce(conta_historica.banco, '')), '[^a-z0-9]+', '', 'g')
                    ])
            )
          )
        )
      )
    group by f.data_caixa
  ), entradas_reais as (
    select m.dia, m.cartoes, m.qr_code, m.outras, m.total_credito as total
    from movimento_real m
  ), recebimentos_projetados as (
    select r.dia, sum(r.valor) as valor from public.recebimento_projetado r
    where r.dia >= (select j.inicio from janela j)
      and r.dia < p_mes + interval '1 month' group by r.dia
  ), saidas_reais as (
    select m.dia, m.total_debito as total
    from movimento_real m
  ), recorrentes_reais as (
    select p.data_pagamento as dia, sum(p.valor) as total
    from public.conta_recorrente_pagamento p
    join public.conta_recorrente c on c.id = p.conta_id
    where p.data_pagamento >= p_mes
      and p.data_pagamento < p_mes + interval '1 month'
      and p.situacao = 'pago' and c.tipo = 'despesa' and c.incluir_totais
    group by p.data_pagamento
  ), despesas_fixas_projetadas as (
    select p.dia, sum(p.valor) as total from public.projecao_despesa_fixa p
    where p.dia >= (select j.inicio from janela j)
      and p.dia < p_mes + interval '1 month' group by p.dia
  ), despesas_diretas_projetadas as (
    select p.dia, sum(p.valor) as total from public.projecao_despesa_direta p
    where p.dia >= (select j.inicio from janela j)
      and p.dia < p_mes + interval '1 month' group by p.dia
  ), saldos as (
    select p.dia, p.saldo from public.painel_fluxo_caixa p
    where p.dia >= p_mes and p.dia < p_mes + interval '1 month'
  ), saldos_detalhados as (
    select
      s.dia,
      s.saldo_total,
      s.variacao_dinheiro_pendente
    from private.saldo_caixa_diario s
    where s.dia >= p_mes and s.dia < p_mes + interval '1 month'
  ), base as (
    select d.dia, extract(isodow from d.dia)::smallint as dia_semana,
      ct.caixa as corte_caixa,
      case when d.dia <= least(coalesce(ct.venda, d.dia), coalesce(ct.caixa, d.dia)) then 'real'
           when d.dia > greatest(coalesce(ct.venda, d.dia - 1), coalesce(ct.caixa, d.dia - 1)) then 'projetado'
           else 'parcial' end as modo,
      m.meta_dia, vt.venda as faturamento_dia,
      case when vt.tipo = 'real' then vs.credito end as venda_credito,
      case when vt.tipo = 'real' then vs.debito end as venda_debito,
      case when vt.tipo = 'real' then vs.pix end as venda_pix,
      case when vt.tipo = 'real' then vs.extras end as venda_extras,
      case when vt.tipo = 'real' then vd.dinheiro end as venda_dinheiro,
      case when d.dia <= ct.caixa then coalesce(er.cartoes, 0)
           else coalesce(r.credito, 0) end as recebimento_credito,
      case when d.dia <= ct.caixa then null::numeric
           else coalesce(r.debito, 0) end as recebimento_debito,
      case when d.dia <= ct.caixa then coalesce(er.qr_code, 0)
           else 0::numeric end as recebimento_pix,
      case when d.dia <= ct.caixa then
             coalesce(er.outras, 0)
               + greatest(coalesce(sd.variacao_dinheiro_pendente, 0), 0)
           else coalesce(rp.valor, 0) end as recebimento_projetado,
      case when d.dia <= ct.caixa then
             coalesce(er.total, 0)
               + greatest(coalesce(sd.variacao_dinheiro_pendente, 0), 0)
           else coalesce(r.credito, 0) + coalesce(r.debito, 0) + coalesce(rp.valor, 0)
      end as recebimento_total,
      case when d.dia <= ct.caixa then
             coalesce(sr.total, 0)
               + greatest(-coalesce(sd.variacao_dinheiro_pendente, 0), 0)
           else coalesce(dfp.total, 0) + coalesce(ddp.total, 0) end as despesa_total,
      case when d.dia <= ct.caixa then least(coalesce(rr.total, 0), coalesce(sr.total, 0))
           else coalesce(dfp.total, 0) end as despesa_recorrente,
      case when d.dia <= ct.caixa then
             greatest(coalesce(sr.total, 0) - coalesce(rr.total, 0), 0)
               + greatest(-coalesce(sd.variacao_dinheiro_pendente, 0), 0)
           else coalesce(ddp.total, 0) end as despesa_nao_recorrente,
      coalesce(rr.total, 0) as despesa_recorrente_registrada,
      case when d.dia <= ct.caixa then greatest(coalesce(rr.total, 0) - coalesce(sr.total, 0), 0)
           else 0 end as despesa_recorrente_nao_conciliada,
      coalesce(sd.saldo_total, s.saldo) as saldo_real
    from dias d cross join cortes ct
    left join metas m on m.dia = d.dia
    left join vendas_total vt on vt.dia = d.dia
    left join vendas_stone vs on vs.dia = d.dia
    left join vendas_dinheiro vd on vd.dia = d.dia
    left join recebiveis r on r.dia = d.dia
    left join entradas_reais er on er.dia = d.dia
    left join recebimentos_projetados rp on rp.dia = d.dia
    left join saidas_reais sr on sr.dia = d.dia
    left join recorrentes_reais rr on rr.dia = d.dia
    left join despesas_fixas_projetadas dfp on dfp.dia = d.dia
    left join despesas_diretas_projetadas ddp on ddp.dia = d.dia
    left join saldos s on s.dia = d.dia
    left join saldos_detalhados sd on sd.dia = d.dia
  ), calculado as (
    select b.*, coalesce(
      (select s.saldo_total
       from private.saldo_caixa_diario s
       where s.dia <= b.corte_caixa
       order by s.dia desc
       limit 1),
      (select p.saldo
       from public.painel_fluxo_caixa p
       where p.dia <= b.corte_caixa
       order by p.dia desc
       limit 1),
      0::numeric
    ) + sum(case when b.dia > b.corte_caixa
          then b.recebimento_total - b.despesa_total else 0::numeric end)
        over (order by b.dia rows between unbounded preceding and current row) as saldo_projetado
    from base b
  )
  select b.dia, b.dia_semana, b.modo, round(b.meta_dia, 2),
    case when max(b.meta_dia) over () is null then null
      else round(sum(coalesce(b.meta_dia, 0)) over (order by b.dia), 2) end,
    round(b.faturamento_dia, 2),
    case when max(b.faturamento_dia) over () is null then null
      else round(sum(coalesce(b.faturamento_dia, 0)) over (order by b.dia), 2) end,
    round(b.venda_credito, 2), round(b.venda_debito, 2), round(b.venda_pix, 2),
    round(b.venda_extras, 2), round(b.venda_dinheiro, 2), round(b.recebimento_total, 2),
    round(b.recebimento_credito, 2), round(b.recebimento_debito, 2),
    round(b.recebimento_pix, 2), round(b.recebimento_projetado, 2),
    round(b.despesa_total, 2), round(b.despesa_recorrente, 2),
    round(b.despesa_nao_recorrente, 2), round(b.despesa_recorrente_registrada, 2),
    round(b.despesa_recorrente_nao_conciliada, 2),
    round(case when b.dia <= b.corte_caixa then b.saldo_real else b.saldo_projetado end, 2)
  from calculado b
  where b.dia >= p_mes
  order by b.dia;
end;
$function$
;

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

-- 4. Mesmo resultado, ou nada desta migration permanece.
do $validacao$
declare
  v_dif text;
  v_src text;
begin
  select string_agg(a.objeto, ', ' order by a.objeto)
  into v_dif
  from _hash_antes a
  join (
  select 'corte_caixa' as objeto, md5(string_agg(t::text, '|' order by t::text)) as hash from public.corte_caixa t
  union all select 'venda_diaria', md5(string_agg(t::text, '|' order by t::text)) from public.venda_diaria t
  union all select 'projecao_venda_diaria', md5(string_agg(t::text, '|' order by t::text)) from public.projecao_venda_diaria t
  union all select 'painel_resumo_mensal', md5(string_agg(t::text, '|' order by t::text)) from public.painel_resumo_mensal t
  union all select 'painel_diario', md5(string_agg(t::text, '|' order by t::text)) from public.painel_diario t
  union all select 'recebimento_conhecido', md5(string_agg(t::text, '|' order by t::text)) from public.recebimento_conhecido t
  union all select 'recebimento_projetado', md5(string_agg(t::text, '|' order by t::text)) from public.recebimento_projetado t
  union all select 'projecao_despesa_direta', md5(string_agg(t::text, '|' order by t::text)) from public.projecao_despesa_direta t
  union all select 'projecao_despesa_fixa', md5(string_agg(t::text, '|' order by t::text)) from public.projecao_despesa_fixa t
  ) d using (objeto)
  where a.hash is distinct from d.hash;

  if v_dif is not null then
    raise exception 'Snapshots mudaram o resultado de: %', v_dif;
  end if;

  select lower(p.prosrc) into v_src
  from pg_catalog.pg_proc p
  where p.oid = 'public.listar_calendario_financeiro(date)'::regprocedure;

  if position('private.mv_venda_stone_dia' in v_src) = 0
     or position('public.stone_conta sc' in v_src) = 0
     or position('movimento_real as materialized' in v_src) = 0
     or position('private.saldo_caixa_diario' in v_src) = 0
     or position('from public.raw_stone_vendas v' in v_src) > 0 then
    raise exception 'Validacao falhou: Calendario perdeu uma garantia anterior.';
  end if;

  select lower(p.prosrc) into v_src
  from pg_catalog.pg_proc p
  where p.oid = 'private.refresh_painel_resiliente()'::regprocedure;

  if position('private.mv_corte_caixa_base' in v_src) = 0
     or position('private.mv_venda_stone_dia' in v_src) = 0
     or position('private.mv_dre_mensal' in v_src) = 0 then
    raise exception 'Validacao falhou: refresh nao atualiza os snapshots.';
  end if;
end;
$validacao$;

notify pgrst, 'reload schema';

commit;
