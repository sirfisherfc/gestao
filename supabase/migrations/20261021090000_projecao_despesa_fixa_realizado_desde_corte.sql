-- =====================================================================
-- projecao_despesa_fixa: realizado só a partir do mês do corte
-- =====================================================================
--
-- PROBLEMA (medido em 21/10/2026, depois de 20261021070000)
--   A projeção de despesa fixa lê public.fato_financeiro duas vezes; a CTE
--   realizado_mes agrega a história inteira (59 meses), embora a junção
--   final só use meses com dias depois do corte. Custava ~0,37 s por
--   leitura e entra no Início, Caixa, DRE, Despesas, Calendário e no cartão
--   do gerente, onde levava o pior caso acima de 1 s.
--
-- SOLUÇÃO
--   realizado_mes passa a filtrar data_competencia a partir do primeiro dia
--   do mês do corte. Os meses descartados nunca casavam na junção final
--   (dias depois do corte pertencem ao mês do corte ou aos seguintes), então
--   o resultado é o mesmo. Medido em transação descartada: 0,37 s -> 0,22 s,
--   md5 idêntico.
--
-- OBJETOS
--   ~ public.projecao_despesa_fixa (create or replace; mesmas colunas, dono e
--     grants; resto igual a 20260818180000, conferido contra o banco)
--
-- VALIDAÇÃO
--   md5 da projeção e de painel_colchao_despesa_fixa antes e depois; aborta
--   se mudar.
--
-- REVERSÃO
--   Recriar a view de 20260818180000.
-- =====================================================================

begin;

set local lock_timeout = '5s';

create temp table _hash_antes_fixa on commit drop as
  select 'projecao_despesa_fixa' as objeto, md5(string_agg(t::text, '|' order by t::text)) as hash from public.projecao_despesa_fixa t
  union all select 'painel_colchao_despesa_fixa', md5(string_agg(t::text, '|' order by t::text)) from public.painel_colchao_despesa_fixa t;

create or replace view public.projecao_despesa_fixa as
with cfg as (
  select greatest(1, public.parametro_valor('meses_media_fixa', 3)::integer) as meses
), corte as (
  select dia from public.corte_caixa
), media as (
  select coalesce(avg(m.total), 0::numeric) as media_mensal
  from (
    select date_trunc('month', f.data_competencia) as mes, sum(abs(f.valor)) as total
    from public.fato_financeiro f cross join cfg
    where f.movimentacao like 'D%'
      and f.dre_grupo = any (array['PESSOAL', 'INFRAESTRUTURA', 'MARKETING E PUBLICIDADE', 'IMPOSTOS'])
      and f.data_competencia >= date_trunc('month', current_date) - make_interval(months => cfg.meses)
      and f.data_competencia < date_trunc('month', current_date)
    group by 1
  ) m
), realizado_mes as (
  -- Só entra como realizado o que o Calendário já mostra como realizado, ou
  -- seja, o que tem data de caixa dentro do corte. Lançamento com data de
  -- caixa posterior continua sendo projeção.
  select date_trunc('month', f.data_competencia) as mes, sum(abs(f.valor)) as realizado
  from public.fato_financeiro f cross join corte ct
  where f.movimentacao like 'D%'
    and f.dre_grupo = any (array['PESSOAL', 'INFRAESTRUTURA', 'MARKETING E PUBLICIDADE', 'IMPOSTOS'])
    and f.data_caixa <= ct.dia
    -- Só os meses que a projeção usa: a junção final pega meses com dias
    -- depois do corte, todos a partir do mês do corte. O limite como
    -- subconsulta escalar deixa o Postgres filtrar cedo, sem reclassificar
    -- os lançamentos de toda a história (20261021090000).
    and f.data_competencia >= (
      select date_trunc('month', cc.dia::timestamp)::date from public.corte_caixa cc
    )
  group by 1
), dias_restantes as (
  select c.mes, count(*) as n
  from public.calendario c cross join corte ct
  where c.dia > ct.dia group by c.mes
), contas_abertas as (
  select dr.mes,
    case when cp.id is not null
              and cp.data_pagamento >= dr.mes
              and cp.data_pagamento < (dr.mes + interval '1 month')::date
           then cp.data_pagamento
         when v.vencimento > ct.dia then v.vencimento
         else (select min(c.dia) from public.calendario c where c.mes = dr.mes and c.dia > ct.dia)
    end as dia,
    case when cp.id is not null then cp.valor else m.media_periodo end as valor
  from dias_restantes dr
  cross join corte ct
  cross join cfg
  join public.conta_recorrente cr on cr.ativa and cr.tipo = 'despesa' and cr.incluir_totais
  cross join lateral (
    select least((dr.mes + (cr.dia_vencimento - 1) * interval '1 day')::date,
                 (dr.mes + interval '1 month - 1 day')::date) as vencimento
  ) v
  -- Pagamento já registrado mas com data posterior ao corte: o caixa ainda
  -- não o absorveu, então ele permanece projetado pelo valor real e no dia
  -- em que foi pago.
  left join public.conta_recorrente_pagamento cp
    on cp.conta_id = cr.id and cp.competencia = dr.mes
   and cp.situacao = 'pago' and cp.data_pagamento > ct.dia and cp.valor > 0
  cross join lateral (
    select round(avg(h.valor), 2) as media_periodo
    from (
      select p.valor from public.conta_recorrente_pagamento p
      where p.conta_id = cr.id and p.competencia < dr.mes
        and p.situacao = 'pago' and p.valor > 0
      order by p.competencia desc limit (select meses from cfg)
    ) h
  ) m
  where (
      cp.id is not null
      or not exists (
        select 1 from public.conta_recorrente_pagamento cx
        where cx.conta_id = cr.id and cx.competencia = dr.mes
      )
    )
    and (case when cp.id is not null then cp.valor else m.media_periodo end) > 0
), contas_abertas_mes as (
  select mes, sum(valor) as total from contas_abertas group by mes
), contas_abertas_dia as (
  select dia, sum(valor) as total from contas_abertas where dia is not null group by dia
)
select c.dia,
  round(greatest((select media_mensal from media) - coalesce(rm.realizado, 0)
                 - coalesce(cam.total, 0), 0) / dr.n::numeric
        + coalesce(cad.total, 0), 2) as valor
from public.calendario c
join dias_restantes dr on dr.mes = c.mes
left join realizado_mes rm on rm.mes = c.mes
left join contas_abertas_mes cam on cam.mes = c.mes
left join contas_abertas_dia cad on cad.dia = c.dia
cross join corte ct
where c.dia > ct.dia;

do $validacao$
declare
  v_dif text;
begin
  select string_agg(a.objeto, ', ' order by a.objeto)
  into v_dif
  from _hash_antes_fixa a
  join (
  select 'projecao_despesa_fixa' as objeto, md5(string_agg(t::text, '|' order by t::text)) as hash from public.projecao_despesa_fixa t
  union all select 'painel_colchao_despesa_fixa', md5(string_agg(t::text, '|' order by t::text)) from public.painel_colchao_despesa_fixa t
  ) d using (objeto)
  where a.hash is distinct from d.hash;

  if v_dif is not null then
    raise exception 'Limite do realizado mudou o resultado de: %', v_dif;
  end if;
end;
$validacao$;

commit;
