-- =====================================================================
-- Migration: 20260906070000_estoque_contagem_semanal_e_revisoes.sql
-- Etapa 5 da auditoria / estoque
--
-- Problemas corrigidos
-- --------------------
-- 1. private.fechamento_consumo_estoque tinha chave primária (unidade, mes) e
--    exigia mês truncado, então guardava um único registro por mês. Não cabiam
--    contagens semanais, e `escopo` ficava fora da chave: nem mesmo um fechamento
--    'curva_a' e um 'integral' do mesmo mês coexistiam.
-- 2. A RPC sobrescrevia o registro mensal sem deixar rastro: não havia histórico
--    de revisões nem de reaberturas.
-- 3. public.app_fechamento_consumo_estoque publicava apenas o consumo apurado e
--    o selo de fechamento. Os quatro valores de entrada e a memória ficavam
--    invisíveis, impedindo reedição administrativa.
--
-- Contagem semanal e fechamento mensal passam a ser coisas distintas: a
-- contagem é um evento datado, o fechamento é a apuração do mês que consome
-- essas contagens. Não existe catálogo de itens no banco, então a contagem é
-- registrada por valor e escopo, não item a item; a curva A é representada pelo
-- escopo 'curva_a'.
--
-- A tabela de fechamento está vazia em produção, então a troca de chave
-- primária não migra dado nenhum.
-- =====================================================================

begin;

-- ---------------------------------------------------------------------
-- 1) Escopo entra na chave primária do fechamento mensal
-- ---------------------------------------------------------------------
do $$
begin
  if exists (
    select 1 from pg_constraint
    where conname = 'fechamento_consumo_estoque_pkey'
      and conrelid = 'private.fechamento_consumo_estoque'::regclass
      and array_length(conkey, 1) = 2
  ) then
    if exists (select 1 from private.fechamento_consumo_estoque) then
      raise exception
        'Fechamento deixou de estar vazio: migre os dados antes de trocar a chave.';
    end if;

    alter table private.fechamento_consumo_estoque
      drop constraint fechamento_consumo_estoque_pkey;
    alter table private.fechamento_consumo_estoque
      add constraint fechamento_consumo_estoque_pkey
      primary key (unidade, mes, escopo);
  end if;
end $$;

-- ---------------------------------------------------------------------
-- 2) Contagens de estoque: evento datado, várias por mês
-- ---------------------------------------------------------------------
create table if not exists private.contagem_estoque (
  id bigint generated always as identity primary key,
  unidade text not null,
  data_contagem date not null,
  escopo text not null,
  valor numeric not null,
  memoria text,
  contado_em timestamptz not null default now(),
  contado_por uuid,
  constraint contagem_estoque_unidade_check check (btrim(unidade) <> ''),
  constraint contagem_estoque_escopo_check
    check (escopo = any (array['curva_a', 'integral'])),
  constraint contagem_estoque_valor_check
    check (valor >= 0 and valor <> 'NaN'::numeric),
  constraint contagem_estoque_memoria_check
    check (memoria is null or btrim(memoria) <> ''),
  -- Uma contagem por unidade, data e escopo: recontagem do mesmo dia corrige a
  -- anterior em vez de duplicar.
  constraint contagem_estoque_evento_unico
    unique (unidade, data_contagem, escopo)
);

comment on table private.contagem_estoque is
  'Contagens de estoque por data e escopo. Suporta cadência semanal; o fechamento mensal é apuração separada.';

create index if not exists ix_contagem_estoque_unidade_data
  on private.contagem_estoque (unidade, data_contagem desc);

-- ---------------------------------------------------------------------
-- 3) Histórico de revisões e reaberturas do fechamento
-- ---------------------------------------------------------------------
create table if not exists private.fechamento_consumo_estoque_revisao (
  id bigint generated always as identity primary key,
  unidade text not null,
  mes date not null,
  escopo text not null,
  acao text not null,
  estoque_inicial numeric,
  compras_liquidas numeric,
  transferencias_liquidas numeric,
  estoque_final numeric,
  memoria text,
  estava_fechado boolean not null,
  ficou_fechado boolean not null,
  registrado_em timestamptz not null default now(),
  registrado_por uuid,
  constraint fechamento_revisao_acao_check
    check (acao = any (array['criado', 'alterado', 'fechado', 'reaberto', 'removido']))
);

comment on table private.fechamento_consumo_estoque_revisao is
  'Trilha de auditoria do fechamento de consumo: toda gravação, fechamento e reabertura fica registrada.';

create index if not exists ix_fechamento_revisao_chave
  on private.fechamento_consumo_estoque_revisao (unidade, mes, escopo, registrado_em desc);

-- A trilha é escrita por trigger, então qualquer caminho de escrita fica
-- registrado, não apenas a RPC conhecida.
create or replace function private.fn_registrar_revisao_fechamento()
returns trigger
language plpgsql
set search_path = pg_catalog, pg_temp
as $fn$
declare
  v_estava_fechado boolean := false;
  v_ficou_fechado boolean := false;
  v_acao text;
  v_linha private.fechamento_consumo_estoque;
begin
  if tg_op = 'DELETE' then
    v_linha := old;
    v_estava_fechado := old.fechado_em is not null;
    v_acao := 'removido';
  else
    v_linha := new;
    v_ficou_fechado := new.fechado_em is not null;
    if tg_op = 'INSERT' then
      v_acao := case when v_ficou_fechado then 'fechado' else 'criado' end;
    else
      v_estava_fechado := old.fechado_em is not null;
      v_acao := case
        when not v_estava_fechado and v_ficou_fechado then 'fechado'
        when v_estava_fechado and not v_ficou_fechado then 'reaberto'
        else 'alterado'
      end;
    end if;
  end if;

  insert into private.fechamento_consumo_estoque_revisao (
    unidade, mes, escopo, acao,
    estoque_inicial, compras_liquidas, transferencias_liquidas, estoque_final,
    memoria, estava_fechado, ficou_fechado, registrado_por
  ) values (
    v_linha.unidade, v_linha.mes, v_linha.escopo, v_acao,
    v_linha.estoque_inicial, v_linha.compras_liquidas,
    v_linha.transferencias_liquidas, v_linha.estoque_final,
    v_linha.memoria, v_estava_fechado, v_ficou_fechado,
    nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
  );

  return null;
end;
$fn$;

drop trigger if exists tg_registrar_revisao_fechamento
  on private.fechamento_consumo_estoque;

create trigger tg_registrar_revisao_fechamento
  after insert or update or delete on private.fechamento_consumo_estoque
  for each row execute function private.fn_registrar_revisao_fechamento();

-- ---------------------------------------------------------------------
-- 4) A view publica os valores de entrada e a memória
-- ---------------------------------------------------------------------
-- Colunas existentes preservadas na mesma ordem; as novas vão ao final, para
-- que create or replace seja aceito e nenhum consumidor atual quebre.
create or replace view public.app_fechamento_consumo_estoque as
select f.unidade,
  f.mes,
  f.escopo,
  case
    when f.fechado_em is not null
      then f.estoque_inicial + f.compras_liquidas
           + f.transferencias_liquidas - f.estoque_final
    else null::numeric
  end as consumo_apurado,
  f.fechado_em is not null and f.escopo = 'integral'::text
    as inventario_integral_fechado,
  f.fechado_em,
  f.estoque_inicial,
  f.compras_liquidas,
  f.transferencias_liquidas,
  f.estoque_final,
  f.memoria
from private.fechamento_consumo_estoque f
where f.unidade = public.unidade_principal_nome()
  and public.usuario_pode_acessar_pagina('dre.html'::text);

comment on view public.app_fechamento_consumo_estoque is
  'Fechamento de consumo do mês, com os quatro valores de entrada e a memória expostos para reedição administrativa.';

-- ---------------------------------------------------------------------
-- 5) Contagens visíveis para a aplicação
-- ---------------------------------------------------------------------
create or replace view public.app_contagem_estoque as
select c.unidade,
  c.data_contagem,
  c.escopo,
  c.valor,
  c.memoria,
  c.contado_em,
  date_trunc('month', c.data_contagem)::date as mes
from private.contagem_estoque c
where c.unidade = public.unidade_principal_nome()
  and public.usuario_pode_acessar_pagina('dre.html'::text);

comment on view public.app_contagem_estoque is
  'Contagens de estoque por data e escopo da unidade principal.';

-- ---------------------------------------------------------------------
-- 6) RPC de registro de contagem
-- ---------------------------------------------------------------------
create or replace function public.admin_registrar_contagem_estoque(
  p_data_contagem date,
  p_escopo text,
  p_valor numeric,
  p_memoria text default null
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $fn$
declare
  v_unidade text;
begin
  if not public.usuario_pode_acessar_pagina('dre.html'::text) then
    raise exception using errcode = '42501', message = 'Acesso nao autorizado.';
  end if;

  if p_data_contagem is null or p_data_contagem > current_date then
    raise exception using errcode = '22023',
      message = 'Data de contagem invalida.';
  end if;

  v_unidade := public.unidade_principal_nome();

  insert into private.contagem_estoque (
    unidade, data_contagem, escopo, valor, memoria, contado_por
  ) values (
    v_unidade, p_data_contagem, p_escopo, p_valor, nullif(btrim(p_memoria), ''),
    nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
  )
  on conflict (unidade, data_contagem, escopo) do update
    set valor = excluded.valor,
        memoria = excluded.memoria,
        contado_em = now(),
        contado_por = excluded.contado_por;
end;
$fn$;

grant select on public.app_contagem_estoque to authenticated;
grant execute on function public.admin_registrar_contagem_estoque(date, text, numeric, text)
  to authenticated;

-- ---------------------------------------------------------------------
-- Validação
-- ---------------------------------------------------------------------
do $validacao$
declare
  v_cols int;
  v_pk int;
  v_faltando text;
begin
  select count(*) into v_pk
  from pg_constraint
  where conname = 'fechamento_consumo_estoque_pkey'
    and conrelid = 'private.fechamento_consumo_estoque'::regclass
    and array_length(conkey, 1) = 3;
  if v_pk <> 1 then
    raise exception 'Validacao falhou: escopo nao entrou na chave do fechamento.';
  end if;

  select count(*) into v_cols
  from information_schema.columns
  where table_schema = 'public'
    and table_name = 'app_fechamento_consumo_estoque'
    and column_name in ('estoque_inicial', 'compras_liquidas',
                        'transferencias_liquidas', 'estoque_final', 'memoria');
  if v_cols <> 5 then
    raise exception 'Validacao falhou: a view nao expoe os valores de entrada.';
  end if;

  if to_regclass('private.contagem_estoque') is null then
    raise exception 'Validacao falhou: tabela de contagem ausente.';
  end if;

  if not exists (
    select 1 from pg_trigger
    where tgname = 'tg_registrar_revisao_fechamento'
      and tgrelid = 'private.fechamento_consumo_estoque'::regclass
  ) then
    raise exception 'Validacao falhou: trilha de revisao nao instalada.';
  end if;

  -- Mantém a garantia da migration 20260906060000.
  select string_agg(n.nspname || '.' || p.proname, ', ') into v_faltando
  from pg_catalog.pg_proc p
  join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where p.prosecdef
    and n.nspname in ('public', 'private')
    and not exists (
      select 1 from unnest(coalesce(p.proconfig, '{}')) cfg
      where cfg like 'search_path=%'
    );
  if v_faltando is not null then
    raise exception
      'Validacao falhou: security definer sem search_path: %', v_faltando;
  end if;
end;
$validacao$;

commit;
