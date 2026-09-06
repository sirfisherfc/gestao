-- Otimização e Consolidação do Calendário Financeiro (Passo 1 / Risco 2 & Bloco D).
--
-- 1. Restaura o CTE consolidado movimento_real AS MATERIALIZED, agregando
--    entradas (crédito) e saídas (débito) em uma única passada sobre fato_financeiro,
--    preservando as regras de fontes configuradas (20260818100000).
-- 2. Lê vendas de public.recebimento_stone_net em vez de consultar
--    public.raw_stone_vendas diretamente com deduplicação avulsa de cancelamentos.
-- 3. Preserva o encadeamento de saldo projetado entre meses futuros (20260814000000).
-- 4. Preserva o snapshot vigente private.saldo_caixa_diario.
-- 5. Preserva assinatura exata de retorno, checagem de autorização e grants.

begin;

create or replace function public.listar_calendario_financeiro(p_mes date)
 returns table(
   dia date,
   dia_semana smallint,
   modo text,
   meta_dia numeric,
   meta_acumulada numeric,
   faturamento_dia numeric,
   faturamento_acumulado numeric,
   venda_credito numeric,
   venda_debito numeric,
   venda_pix numeric,
   venda_extras numeric,
   venda_dinheiro numeric,
   recebimento_total numeric,
   recebimento_credito numeric,
   recebimento_debito numeric,
   recebimento_pix numeric,
   recebimento_projetado numeric,
   despesa_total numeric,
   despesa_recorrente numeric,
   despesa_nao_recorrente numeric,
   despesa_recorrente_registrada numeric,
   despesa_recorrente_nao_conciliada numeric,
   saldo_caixa numeric
 )
 language plpgsql
 stable security definer
 set search_path to 'pg_catalog', 'public'
as $function$
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
    select s.data_venda::date as dia,
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
    from public.recebimento_stone_net s
    where s.data_venda::date >= p_mes
      and s.data_venda::date < p_mes + interval '1 month'
    group by s.data_venda::date
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
    where r.data_vencimento >= (select j.inicio from janela j)
      and r.data_vencimento < p_mes + interval '1 month'
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
$function$;

revoke all privileges on function public.listar_calendario_financeiro(date) from public, anon;
grant execute on function public.listar_calendario_financeiro(date) to authenticated, service_role;

comment on function public.listar_calendario_financeiro(date) is
  'Calendario financeiro da unidade unica; movimento_real consolidado em passada unica e vendas Stone alimentadas pela view canonica de recebimento liquido.';

do $validacao$
declare
  v_src text;
begin
  select lower(p.prosrc) into v_src
  from pg_catalog.pg_proc p
  where p.oid = 'public.listar_calendario_financeiro(date)'::regprocedure;

  if position('movimento_real as materialized' in v_src) = 0 then
    raise exception 'Validacao falhou: movimento_real as materialized ausente.';
  end if;

  if position('from public.raw_stone_vendas v' in v_src) > 0 then
    raise exception 'Validacao falhou: leitura bruta de raw_stone_vendas ainda presente.';
  end if;

  if position('private.saldo_caixa_diario' in v_src) = 0 then
    raise exception 'Validacao falhou: private.saldo_caixa_diario ausente.';
  end if;
end;
$validacao$;

commit;
