-- Pendencias operacionais de competencias anteriores, sem criar pagamentos.
begin;

create or replace function public.listar_pendencias_recorrentes(p_competencia date)
returns table (conta_id bigint, competencia date, vencimento date, media_3 numeric)
language plpgsql stable security definer set search_path = pg_catalog, public
as $function$
declare
  v_hoje date := (current_timestamp at time zone 'America/Fortaleza')::date;
  v_meses integer := greatest(1, public.parametro_valor('meses_media_fixa', 3)::integer);
begin
  if not public.usuario_pode_acessar_pagina('contas_recorrentes.html') then
    raise exception using errcode = '42501', message = 'Acesso nao autorizado.';
  end if;
  if p_competencia is null or p_competencia <> date_trunc('month', p_competencia)::date then
    raise exception using errcode = '22023', message = 'Competencia invalida.';
  end if;

  return query
  select c.id, meses.mes::date, prazo.dia, media.valor
  from public.conta_recorrente c
  left join lateral (
    select min(p.competencia) as primeira
    from public.conta_recorrente_pagamento p where p.conta_id = c.id
  ) historico on true
  cross join lateral generate_series(
    least(historico.primeira,
      date_trunc('month', c.criado_em at time zone 'America/Fortaleza')::date)::timestamp,
    least(p_competencia - interval '1 month', date_trunc('month', v_hoje))::timestamp,
    interval '1 month'
  ) meses(mes)
  cross join lateral (
    select (meses.mes::date + (least(c.dia_vencimento::integer,
      extract(day from meses.mes + interval '1 month - 1 day')::integer) - 1)) as dia
  ) prazo
  left join lateral (
    select round(avg(ultimos.valor), 2) as valor
    from (
      select p.valor from public.conta_recorrente_pagamento p
      where p.conta_id = c.id and p.competencia < meses.mes::date
        and p.situacao = 'pago' and p.valor > 0
      order by p.competencia desc limit v_meses
    ) ultimos
  ) media on true
  where c.ativa and c.unidade = public.unidade_principal_nome()
    and prazo.dia < v_hoje
    and not exists (
      select 1 from public.conta_recorrente_pagamento p
      where p.conta_id = c.id and p.competencia = meses.mes::date
    )
  order by meses.mes, c.dia_vencimento, c.nome, c.id;
end;
$function$;

comment on function public.listar_pendencias_recorrentes(date) is
  'Meses anteriores vencidos sem baixa, desde o cadastro ou primeiro historico legado. Somente contas ativas da unidade principal; media de pagamentos anteriores a cada competencia. Ausencia de baixa nao comprova divida.';

revoke all privileges on function public.listar_pendencias_recorrentes(date) from public, anon, authenticated;
grant execute on function public.listar_pendencias_recorrentes(date) to authenticated;
commit;
