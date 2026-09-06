-- Auditoria 2026-09-05: importacao e tarefa na mesma transacao.
-- Objetos: importar_csv_stone, indice da fila, watchdog privado e job cron.
-- Nao altera parsers, hashes, regras financeiras, worker ou grants da RPC.
-- Riscos: uma tarefa por arquivo; espera de ate a proxima verificacao do cron
-- (cadencia de 2 minutos nao e SLA). Erros nao sao retentados automaticamente.
-- Em manutencao, pausar tambem sirfisher-garantir-worker-recalculo-saldo.
-- Uma unica transacao: outbox nunca fica instalada sem sua recuperacao.
begin;
set local lock_timeout = '2s';

do $precondicoes$
begin
  if exists (
    select 1 from pg_catalog.pg_proc p
    where p.oid in (
      'private.processar_fila_recalculo_saldo()'::regprocedure,
      'public.solicitar_recalculo_saldo(date,date)'::regprocedure,
      'public.importar_csv_stone(text,jsonb,boolean)'::regprocedure
    ) and p.proowner <> current_user::regrole
  ) then
    raise exception 'Instalar sob o mesmo owner do worker e das RPCs.';
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
  -- Mesmo lock do worker: nao disputa sua decisao de desagendar. O produtor
  -- nao adquire este lock e nao espera pelo processamento pesado.
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
  'Rearma o worker para pendencias sem esperar pelo lock do processamento. Nao altera tarefas nem desagenda jobs; nao retenta erros.';

do $outbox$
declare
  v_def text := pg_catalog.pg_get_functiondef(
    'public.importar_csv_stone(text,jsonb,boolean)'::regprocedure
  );
  v_nova text;
  v_ancora text;
  v_declaracao constant text := 'v_auditoria_recalculo_id bigint;';
  v_retorno constant text := $anchor$'recalculo_id', v_auditoria_recalculo_id,$anchor$;
  v_insercao constant text := $new$if v_inseridos > 0 then
    if v_recalc_inicio is null then
      raise exception 'Importacao sem periodo de recalculo; nenhuma linha foi salva.';
    end if;
    insert into private.fila_recalculo_saldo (data_min, data_max)
    values (v_recalc_inicio, coalesce(v_recalc_fim, v_recalc_inicio))
    returning id into v_auditoria_recalculo_id;
  end if;
  insert into public.log_carga (fontes) values (v_fonte_log);$new$;
begin
  if position('v_auditoria_recalculo_id' in v_def) > 0 then
    foreach v_ancora in array array[v_declaracao, v_insercao, v_retorno] loop
      if (length(v_def) - length(replace(v_def, v_ancora, '')))
          / length(v_ancora) <> 1 then
        raise exception 'Outbox parcialmente instalada; revisar a definicao.';
      end if;
    end loop;
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
    E'v_recalc_fim date;\n  ' || v_declaracao);
  v_nova := replace(v_nova,
    'insert into public.log_carga (fontes) values (v_fonte_log);', v_insercao);
  v_nova := replace(v_nova,
    $anchor$'recalculo_fim', v_recalc_fim,$anchor$,
    $anchor$'recalculo_fim', v_recalc_fim,$anchor$ || E'\n    ' || v_retorno);
  v_nova := replace(v_nova,
    '-- authenticated. A tela chama os dois, uma unica vez, ao fim do lote.',
    '-- authenticated. A tarefa acima e duravel; o worker executa ambos.');
  execute v_nova;
end;
$outbox$;
comment on function public.importar_csv_stone(text,jsonb,boolean) is
  'Importacao com parsers e deduplicacao existentes. Grava a tarefa de recalculo na mesma transacao das linhas inseridas e devolve recalculo_id; dry-run e zero insercoes nao enfileiram. Execucao pesada fica no worker.';

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
