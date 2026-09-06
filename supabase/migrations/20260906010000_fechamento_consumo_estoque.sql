-- Fechamento gerencial de consumo de estoque (Passo 2 / Bloco A da Auditoria).
--
-- Problema: pagamento de fornecedor nao mede consumo; cobertura parcial
-- deve permanecer explicita. Uma linha por unidade/mes, em rascunho ou fechada.
-- Risco mitigado: armazenamento isolado em private com RLS sem grants diretos;
-- view publica app_fechamento_consumo_estoque com security_barrier=true,
-- security_invoker=false e gate de acesso restrito a dre.html.
-- RPC administrativa permite salvar rascunho e realizar fechamento auditado.

begin;
set local lock_timeout = '2s';

create table if not exists private.fechamento_consumo_estoque (
  unidade text not null check (btrim(unidade) <> ''),
  mes date not null check (mes = date_trunc('month', mes)::date),
  escopo text not null check (escopo in ('curva_a', 'integral')),
  estoque_inicial numeric(16,2),
  compras_liquidas numeric(16,2),
  transferencias_liquidas numeric(16,2),
  estoque_final numeric(16,2),
  memoria text not null check (btrim(memoria) <> ''),
  fechado_em timestamptz,
  fechado_por uuid,
  primary key (unidade, mes),
  check (estoque_inicial >= 0 and estoque_inicial <> 'NaN'::numeric),
  check (estoque_final >= 0 and estoque_final <> 'NaN'::numeric),
  check (compras_liquidas <> 'NaN'::numeric),
  check (transferencias_liquidas <> 'NaN'::numeric),
  check ((fechado_em is null) = (fechado_por is null)),
  check (fechado_em is null or (
    estoque_inicial is not null and compras_liquidas is not null
    and transferencias_liquidas is not null and estoque_final is not null
    and estoque_inicial + compras_liquidas
        + transferencias_liquidas - estoque_final >= 0
  ))
);

alter table private.fechamento_consumo_estoque enable row level security;
revoke all on private.fechamento_consumo_estoque
  from public, anon, authenticated, service_role;

comment on table private.fechamento_consumo_estoque is
  'Fechamento mensal auxiliar de consumo; escopo curva_a nao representa CMV integral. Nulos indicam ausencia de apuracao; pagamentos nao alimentam compras automaticamente.';
comment on column private.fechamento_consumo_estoque.compras_liquidas is
  'Entradas recebidas e avaliadas pelo custo, liquidas de devolucoes e ajustes de aquisicao; independem da data de pagamento.';
comment on column private.fechamento_consumo_estoque.transferencias_liquidas is
  'Transferencias de estoque recebidas menos enviadas, ao custo. Zero exige confirmacao.';

create or replace view public.app_fechamento_consumo_estoque
with (security_barrier = true, security_invoker = false) as
select f.unidade, f.mes, f.escopo,
  case when f.fechado_em is not null then
    f.estoque_inicial + f.compras_liquidas
    + f.transferencias_liquidas - f.estoque_final
  end as consumo_apurado,
  (f.fechado_em is not null and f.escopo = 'integral') as inventario_integral_fechado,
  f.fechado_em
from private.fechamento_consumo_estoque f
where f.unidade = public.unidade_principal_nome()
  and public.usuario_pode_acessar_pagina('dre.html');

revoke all on public.app_fechamento_consumo_estoque
  from public, anon, authenticated, service_role;
grant select on public.app_fechamento_consumo_estoque to authenticated;
comment on view public.app_fechamento_consumo_estoque is
  'Consumo de estoque fechado e seu escopo. Conciliar perdas e consumos fora da venda antes de classificar o CMV na DRE; nao somar este valor aos pagamentos de insumos.';

create or replace function public.admin_salvar_fechamento_consumo_estoque(
  p_mes date,
  p_escopo text,
  p_estoque_inicial numeric default null,
  p_compras_liquidas numeric default null,
  p_transferencias_liquidas numeric default null,
  p_estoque_final numeric default null,
  p_memoria text default 'Registro manual de fechamento de estoque',
  p_fechar boolean default false
)
returns public.app_fechamento_consumo_estoque
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_unidade text := public.unidade_principal_nome();
  v_fechado_em timestamptz := null;
  v_fechado_por uuid := null;
  v_row public.app_fechamento_consumo_estoque;
begin
  if not public.usuario_tem_papel(array['admin', 'socio']::text[]) then
    raise exception using errcode = '42501', message = 'Apenas administradores ou socios podem gerenciar fechamento de estoque.';
  end if;

  if p_mes is null or p_mes <> date_trunc('month', p_mes)::date then
    raise exception using errcode = '22023', message = 'Mes invalido.';
  end if;

  if p_escopo not in ('curva_a', 'integral') then
    raise exception using errcode = '22023', message = 'Escopo invalido. Escolha curva_a ou integral.';
  end if;

  if btrim(coalesce(p_memoria, '')) = '' then
    raise exception using errcode = '22023', message = 'Memoria de calculo e obrigatoria.';
  end if;

  if p_fechar then
    v_fechado_em := clock_timestamp();
    v_fechado_por := auth.uid();
  end if;

  insert into private.fechamento_consumo_estoque (
    unidade, mes, escopo, estoque_inicial, compras_liquidas,
    transferencias_liquidas, estoque_final, memoria, fechado_em, fechado_por
  ) values (
    v_unidade, p_mes, p_escopo, p_estoque_inicial, p_compras_liquidas,
    p_transferencias_liquidas, p_estoque_final, p_memoria, v_fechado_em, v_fechado_por
  )
  on conflict (unidade, mes) do update set
    escopo = excluded.escopo,
    estoque_inicial = excluded.estoque_inicial,
    compras_liquidas = excluded.compras_liquidas,
    transferencias_liquidas = excluded.transferencias_liquidas,
    estoque_final = excluded.estoque_final,
    memoria = excluded.memoria,
    fechado_em = excluded.fechado_em,
    fechado_por = excluded.fechado_por;

  select * into v_row
  from public.app_fechamento_consumo_estoque v
  where v.mes = p_mes and v.unidade = v_unidade;

  return v_row;
end;
$function$;

revoke all on function public.admin_salvar_fechamento_consumo_estoque(date, text, numeric, numeric, numeric, numeric, text, boolean)
  from public, anon;
grant execute on function public.admin_salvar_fechamento_consumo_estoque(date, text, numeric, numeric, numeric, numeric, text, boolean)
  to authenticated, service_role;

comment on function public.admin_salvar_fechamento_consumo_estoque(date, text, numeric, numeric, numeric, numeric, text, boolean) is
  'Grava rascunho ou fechamento do consumo mensal auxiliar de estoque da unidade principal.';

do $validacao$
begin
  if not exists (
    select 1 from pg_tables
    where schemaname = 'private' and tablename = 'fechamento_consumo_estoque'
  ) then
    raise exception 'Validacao falhou: private.fechamento_consumo_estoque ausente.';
  end if;

  if not exists (
    select 1 from pg_views
    where schemaname = 'public' and viewname = 'app_fechamento_consumo_estoque'
  ) then
    raise exception 'Validacao falhou: public.app_fechamento_consumo_estoque ausente.';
  end if;
end;
$validacao$;

commit;
