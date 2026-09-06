-- PROPOSTAS PARA REVISAO. NAO APLICADAS. PostgreSQL 15 / Supabase.
-- Fora de supabase/migrations: este arquivo nao participa do deploy.
-- Base auditada: a252141, migrations locais ate 20260819020000.
-- Executar pelo fluxo de migration, com owner administrativo, apos revisao.
-- DDL nao deve ser executado pela Data API / role authenticated.
-- Sintaxe e transformacao verificadas localmente; sem execucao no servidor.

-- A. Fechamento gerencial de consumo de estoque, sem alterar a DRE vigente.
-- Problema: pagamento de fornecedor nao mede consumo; cobertura parcial
-- deve permanecer explicita. Uma linha por unidade/mes, em rascunho ou fechada.
-- Risco: este armazenamento nao implementa inventario por item, custo medio,
-- conciliacao com compras ou trilha de revisoes. A futura RPC de fechamento
-- deve validar esses requisitos e registrar cada revisao antes de atualizar.
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
commit;

-- B. Recuperacao do agendamento perdido. Nao retenta tarefas em erro.
-- Problema: produtor e worker nao compartilham a decisao de ligar/desligar.
-- Risco: adiciona verificacao a cada dois minutos. Pausar tambem este job em
-- manutencao. Cadencia nao e SLA; depends de pg_cron e banco disponiveis.
-- Instalar sob o mesmo owner do worker e da RPC que agenda o job atual.
begin;
set local lock_timeout = '2s';

do $precondicoes$
begin
  if exists (
    select 1 from pg_catalog.pg_proc p
    where p.oid in (
      'private.processar_fila_recalculo_saldo()'::regprocedure,
      'public.solicitar_recalculo_saldo(date,date)'::regprocedure
    ) and p.proowner <> current_user::regrole
  ) then
    raise exception 'Instalar sob o mesmo owner do worker e da RPC de agendamento.';
  end if;
  if exists (
    select 1 from cron.job j
    where j.jobname in (
      'sirfisher-processar-recalculo-saldo',
      'sirfisher-garantir-worker-recalculo-saldo'
    ) and j.username <> current_user
  ) then
    raise exception 'Job homonimo de outro owner; revisar antes de instalar.';
  end if;
end;
$precondicoes$;

create index if not exists fila_recalculo_pendente_id_idx
  on private.fila_recalculo_saldo (id) where situacao = 'pendente';
comment on index private.fila_recalculo_pendente_id_idx is
  'Localiza tarefas pendentes em ordem sem percorrer todo o historico retido.';

create or replace function private.garantir_worker_recalculo_saldo()
returns void language plpgsql security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_jobid bigint;
begin
  if not pg_catalog.pg_try_advisory_xact_lock(58000000::bigint) then
    return;
  end if;
  if exists (
    select 1 from private.fila_recalculo_saldo where situacao = 'pendente'
  ) then
    v_jobid := cron.schedule(
      'sirfisher-processar-recalculo-saldo', '5 seconds',
      'select private.processar_fila_recalculo_saldo();'
    );
    perform cron.alter_job(v_jobid, active := true);
  end if;
end;
$function$;

revoke all on function private.garantir_worker_recalculo_saldo()
  from public, anon, authenticated, service_role;
comment on function private.garantir_worker_recalculo_saldo() is
  'Rearma o worker para pendencias sem esperar pelo lock do processamento. Nao altera tarefas nem desagenda jobs.';

do $instalacao$
declare v_jobid bigint;
begin
  v_jobid := cron.schedule(
    'sirfisher-garantir-worker-recalculo-saldo', '*/2 * * * *',
    'select private.garantir_worker_recalculo_saldo();'
  );
  perform cron.alter_job(v_jobid, active := true);
end;
$instalacao$;
commit;

-- C. Outbox transacional no importador vigente.
-- Dependencia: instalar B primeiro. A tarefa entra na mesma transacao das
-- linhas raw; o watchdog acorda o worker mesmo se a aba fechar ou a rede cair.
-- Nao muda parsers/hashes; nao executa refresh/recalculo na requisicao.
-- Alteracao coordenada necessaria em importar.html: guardar recalculo_id de
-- CADA arquivo, acompanhar os IDs devolvidos e retirar a segunda solicitacao
-- de recalculo. O front antigo continua gravando, mas enfileira trabalho
-- redundante. A interface nova deve tolerar a janela de rollout do banco.
-- Cirurgia com ancoras exatas, padrao ja usado no repo. Definicao diferente
-- aborta, em vez de editar silenciosamente a funcao errada.
begin;
set local lock_timeout = '2s';

do $outbox$
declare
  v_def text := pg_catalog.pg_get_functiondef(
    'public.importar_csv_stone(text,jsonb,boolean)'::regprocedure
  );
  v_nova text;
  v_ancora text;
begin
  if position('v_auditoria_recalculo_id' in v_def) > 0 then
    if position('returning id into v_auditoria_recalculo_id' in v_def) = 0
       or position($anchor$'recalculo_id', v_auditoria_recalculo_id$anchor$ in v_def) = 0 then
      raise exception 'Outbox parcialmente instalada; revisar a definicao.';
    end if;
    return;
  end if;

  foreach v_ancora in array array[
    'v_recalc_fim date;',
    'insert into public.log_carga (fontes) values (v_fonte_log);',
    $anchor$'recalculo_fim', v_recalc_fim,$anchor$
  ] loop
    if (length(v_def) - length(replace(v_def, v_ancora, '')))
        / length(v_ancora) <> 1 then
      raise exception 'Definicao inesperada do importador; outbox nao instalada.';
    end if;
  end loop;

  v_nova := replace(v_def, 'v_recalc_fim date;',
    E'v_recalc_fim date;\n  v_auditoria_recalculo_id bigint;');
  v_nova := replace(v_nova,
    'insert into public.log_carga (fontes) values (v_fonte_log);',
    $new$if v_inseridos > 0 and v_recalc_inicio is not null then
    insert into private.fila_recalculo_saldo (data_min, data_max)
    values (v_recalc_inicio, coalesce(v_recalc_fim, v_recalc_inicio))
    returning id into v_auditoria_recalculo_id;
  end if;
  insert into public.log_carga (fontes) values (v_fonte_log);$new$);
  v_nova := replace(v_nova,
    $anchor$'recalculo_fim', v_recalc_fim,$anchor$,
    $new$'recalculo_fim', v_recalc_fim,
    'recalculo_id', v_auditoria_recalculo_id,$new$);
  execute v_nova;
end;
$outbox$;
comment on function public.importar_csv_stone(text,jsonb,boolean) is
  'Importacao com parsers e deduplicacao existentes. No modo real, grava a tarefa de recalculo na mesma transacao das linhas inseridas e devolve recalculo_id; execucao pesada fica no worker.';
commit;

-- D. Diagnostico somente de catalogo: nenhum valor financeiro no resultado.
-- Rodar depois de toda a cadeia de migrations, nao procurar so em arquivos
-- antigos. Esses sinais orientam a revisao; nao substituem EXPLAIN do corpo.
select
  position('movimento_real as materialized' in lower(p.prosrc)) > 0
    as usa_movimento_consolidado_materializado,
  position('from public.raw_stone_vendas v' in lower(p.prosrc)) > 0
    as le_vendas_brutas_diretamente,
  position('private.saldo_caixa_diario' in lower(p.prosrc)) > 0
    as usa_snapshot_vigente
from pg_catalog.pg_proc p
where p.oid = 'public.listar_calendario_financeiro(date)'::regprocedure;
