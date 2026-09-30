-- Histórico de demanda dos eventos calculado uma vez por dia.
--
-- A Edge Function event-quote lia escala_demanda_base e painel_resumo_mensal a
-- cada orçamento: ~9 s por cotação e, quando uma consulta estourava o tempo,
-- o mesmo pedido saía com outro preço (fator do mês 1,0 e CMV 35% padrão).
-- Agora a função lê só esta linha, recalculada diariamente pelo pg_cron.
--
-- Fator do mês = média de venda por DIA ABERTO do mês ÷ média geral, nos
-- últimos 12 meses fechados (um ano de cada mês, sem inflar os meses com dois
-- anos de dados). Ficam fora 24/12 e 25/12 (casa fechada) e 31/12 (faturamento
-- do Réveillon entra em 01/01 ou por fora).

create table if not exists public.event_demand_cache (
  id smallint primary key default 1 check (id = 1),
  hourly jsonb not null,
  peak_hour_revenue numeric(14,2) not null,
  month_factors jsonb not null,
  cmv_rate numeric(6,5),
  window_start date not null,
  window_end date not null,
  refreshed_at timestamptz not null default now()
);

comment on table public.event_demand_cache is
  'Uma linha: faturamento médio por dia da semana × hora, fator por mês e CMV real, para o configurador de eventos.';

alter table public.event_demand_cache enable row level security;
revoke all on public.event_demand_cache from public, anon, authenticated;
grant select on public.event_demand_cache to service_role;

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

  with dias as (
    select extract(month from p.dia)::int as mes, p.venda_dia
      from public.painel_diario p
     where p.dia >= v_start and p.dia < v_end
       and p.venda_dia > 0
       and to_char(p.dia, 'MM-DD') not in ('12-24', '12-25', '12-31')
  ), geral as (
    select avg(venda_dia) as media from dias
  )
  select coalesce(jsonb_object_agg(m.mes::text,
           round(least(1.5, greatest(0.6, m.media / nullif(g.media, 0))), 3)), '{}'::jsonb)
    into v_months
    from (select mes, avg(venda_dia) as media from dias group by mes) m
    cross join geral g;

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
    '20 7 * * *',
    'select public.refresh_event_demand_cache();'
  );
end;
$cron$;
