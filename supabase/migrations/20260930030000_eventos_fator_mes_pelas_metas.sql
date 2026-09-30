-- Fator do mês dos eventos passa a vir das metas (meta_mensal), não do realizado.
--
-- As metas são a leitura do proprietário para cada mês e não sofrem com dias
-- fechados nem com o crescimento de um ano para o outro. Fator = meta por dia
-- aberto ÷ média dos 12 meses mais recentes com meta. Dezembro conta 28 dias
-- abertos (24/12 e 25/12 fechado; 31/12 é o Réveillon, faturado à parte).
--
-- O cache passa a ser recalculado uma vez por mês (dia 1º), pois a curva de
-- horários e as metas mudam pouco.

create or replace function public.refresh_event_demand_cache()
returns void
language plpgsql
security definer
set search_path = public, pg_temp
as $function$
declare
  v_end date := date_trunc('month', current_date)::date;
  v_start date := (date_trunc('month', current_date) - interval '12 months')::date;
  v_hourly jsonb;
  v_peak numeric;
  v_months jsonb;
  v_cmv numeric;
begin
  select coalesce(jsonb_agg(jsonb_build_object(
           'd', b.dia_semana, 'h', b.hora, 'v', round(b.valor_hora, 2))), '[]'::jsonb),
         coalesce(max(b.valor_hora), 0)
    into v_hourly, v_peak
    from public.escala_demanda_base b;

  with metas as (
    select date_trunc('month', m.mes)::date as mes, sum(m.meta_bruta) as meta
      from public.meta_mensal m
     where m.meta_bruta > 0
     group by 1
     order by 1 desc
     limit 12
  ), por_dia as (
    select extract(month from mes)::int as mes_num,
           meta / (extract(day from (mes + interval '1 month - 1 day'))
                   - case when extract(month from mes) = 12 then 3 else 0 end) as meta_dia
      from metas
  ), geral as (
    select avg(meta_dia) as media from por_dia
  )
  select coalesce(jsonb_object_agg(p.mes_num::text,
           round(least(1.5, greatest(0.6, p.meta_dia / nullif(g.media, 0))), 3)), '{}'::jsonb)
    into v_months
    from por_dia p cross join geral g;

  select avg(case when r.cmv_perc > 1 then r.cmv_perc / 100 else r.cmv_perc end)
    into v_cmv
    from (
      select cmv_perc from public.painel_resumo_mensal
       where faturamento > 0 and cmv_perc > 0
         and ano_mes < to_char(current_date, 'YYYY-MM')
       order by ano_mes desc
       limit 6
    ) r;

  insert into public.event_demand_cache
    (id, hourly, peak_hour_revenue, month_factors, cmv_rate, window_start, window_end, refreshed_at)
  values (1, v_hourly, coalesce(v_peak, 0), v_months,
          case when v_cmv between 0.15 and 0.6 then round(v_cmv, 5) end,
          v_start, v_end, now())
  on conflict (id) do update set
    hourly = excluded.hourly,
    peak_hour_revenue = excluded.peak_hour_revenue,
    month_factors = excluded.month_factors,
    cmv_rate = excluded.cmv_rate,
    window_start = excluded.window_start,
    window_end = excluded.window_end,
    refreshed_at = excluded.refreshed_at;
end;
$function$;

revoke all privileges on function public.refresh_event_demand_cache()
  from public, anon, authenticated;

comment on column public.event_demand_cache.month_factors is
  'Fator por mês (1-12): meta por dia aberto ÷ média dos 12 meses mais recentes com meta.';

select public.refresh_event_demand_cache();

do $cron$
declare
  v_jobid bigint;
begin
  for v_jobid in
    select j.jobid from cron.job j where j.jobname = 'sirfisher-eventos-demanda'
  loop
    perform cron.unschedule(v_jobid);
  end loop;

  perform cron.schedule(
    'sirfisher-eventos-demanda',
    '20 7 1 * *',
    'select public.refresh_event_demand_cache();'
  );
end;
$cron$;
