-- =====================================================================
-- Fila de recálculo: todas as tarefas pendentes numa execução só
-- =====================================================================
--
-- PROBLEMA (medido em 21/10/2026 em private.fila_recalculo_saldo)
--   A importação pela web cria uma tarefa por arquivo. O worker processava
--   uma por vez, e cada uma refazia o recálculo do fechamento e o refresh
--   completo do painel (~50-65 s). Com 4 arquivos de uma vez (19/10), o
--   último só chegou ao painel ~4 min depois; em 06/10, ~6,5 min.
--
-- SOLUÇÃO
--   O worker trava e processa todas as tarefas pendentes juntas:
--   - recálculo uma vez, a partir da menor data entre as tarefas que pedem
--     recálculo (o recálculo grava por upsert até o mês corrente, então o
--     resultado final é o mesmo da execução uma a uma, que também lia os
--     dados já gravados); tarefas só de refresh não ampliam o período;
--   - refresh resiliente uma vez;
--   - cada tarefa recebe a própria situação e mensagem, consultável por id
--     como antes (consultar_recalculo_saldo e importar.html não mudam).
--   Tarefas que chegam durante a execução ficam para a próxima chamada.
--
-- OBJETOS
--   ~ private.processar_fila_recalculo_saldo() (create or replace; mesma
--     assinatura, dono, grants e search_path; resto igual a 20260921010000,
--     conferido contra o banco em 21/10/2026)
--
-- RISCOS
--   Baixo. Mesmo lock consultivo, mesma limpeza e mesmo desagendamento.
--   Uma falha marca todas as tarefas do lote com a mesma mensagem, como
--   aconteceria com cada uma ao reprocessar o mesmo refresh. Reversão:
--   recriar a função de 20260921010000.
-- =====================================================================

begin;

create or replace function private.processar_fila_recalculo_saldo()
returns void
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_ids bigint[];
  v_data_min date;
  v_data_max date;
  v_recalcular boolean;
  v_mensagem text;
  v_relatorio jsonb;
  v_resumo text;
  v_falhas text[] := array[]::text[];
  v_jobid bigint;
begin
  if not pg_try_advisory_xact_lock(58000000::bigint) then
    return;
  end if;

  -- Todas as tarefas pendentes numa execução. Cada arquivo importado cria uma
  -- tarefa, e processá-las uma a uma repetia o mesmo recálculo e refresh
  -- (~1 min cada) em fila. O recálculo grava por upsert do mês da data
  -- inicial até o mês corrente, com os dados do momento: rodar uma vez a
  -- partir da menor data das tarefas que pedem recálculo deixa o mesmo
  -- resultado final. Tarefas só de refresh não ampliam esse período.
  with pendentes as (
    select f.id, f.data_min, f.data_max, f.somente_refresh
    from private.fila_recalculo_saldo f
    where f.situacao = 'pendente'
    order by f.id
    for update skip locked
  )
  select array_agg(p.id order by p.id),
         min(p.data_min) filter (where not p.somente_refresh),
         max(p.data_max) filter (where not p.somente_refresh),
         coalesce(bool_or(not p.somente_refresh), false)
  into v_ids, v_data_min, v_data_max, v_recalcular
  from pendentes p;

  if v_ids is not null then
    update private.fila_recalculo_saldo
    set situacao = 'processando', iniciado_em = clock_timestamp(), mensagem = null
    where id = any (v_ids);

    begin
      -- Recalculo em subtransacao propria: se ele falhar, ainda vale atualizar
      -- os snapshots com o que existe hoje.
      if v_recalcular then
        begin
          select r.mensagem into v_mensagem
          from public.recalcular_saldo_fechamento(v_data_min, v_data_max, 0) r
          limit 1;
        exception when others then
          v_falhas := v_falhas || ('recalculo do saldo: ' || sqlerrm)::text;
        end;
      end if;

      -- Sem excecao: o relatorio volta como valor, entao o que deu certo fica.
      v_relatorio := private.refresh_painel_resiliente();

      select string_agg(
        coalesce(item->>'objeto', '?') || ': '
          || coalesce(item->>'erro', item->>'motivo', 'motivo nao informado'),
        '; ' order by ordinalidade)
      into v_resumo
      from jsonb_array_elements(
        coalesce(v_relatorio->'falhas', '[]'::jsonb)
        || coalesce(v_relatorio->'ignorados', '[]'::jsonb)
      ) with ordinality as t(item, ordinalidade);

      if v_resumo is not null then
        v_falhas := v_falhas || v_resumo;
      end if;

      if array_length(v_falhas, 1) is null then
        update private.fila_recalculo_saldo
        set situacao = 'concluido',
            concluido_em = clock_timestamp(),
            mensagem = case
              when somente_refresh then 'Painel atualizado.'
              else coalesce(v_mensagem, 'Saldo recalculado e painel atualizado.')
            end
        where id = any (v_ids);
      else
        update private.fila_recalculo_saldo
        set situacao = 'erro',
            concluido_em = clock_timestamp(),
            mensagem = array_to_string(v_falhas, '; ')
        where id = any (v_ids);
      end if;
    exception
      when query_canceled then
        update private.fila_recalculo_saldo
        set situacao = 'erro', concluido_em = clock_timestamp(),
            mensagem = 'Tempo limite excedido no processamento em background.'
        where id = any (v_ids);
      when others then
        update private.fila_recalculo_saldo
        set situacao = 'erro', concluido_em = clock_timestamp(), mensagem = sqlerrm
        where id = any (v_ids);
    end;
  end if;

  delete from private.fila_recalculo_saldo
  where situacao = any (array['concluido', 'erro'])
    and criado_em < clock_timestamp() - interval '30 days';

  if not exists (
    select 1 from private.fila_recalculo_saldo where situacao = 'pendente'
  ) then
    for v_jobid in
      select j.jobid
      from cron.job j
      where j.jobname = 'sirfisher-processar-recalculo-saldo'
    loop
      perform cron.unschedule(v_jobid);
    end loop;
  end if;
end;
$function$;

commit;
