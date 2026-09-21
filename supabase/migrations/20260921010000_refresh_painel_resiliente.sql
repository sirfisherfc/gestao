-- =====================================================================
-- Falha de um objeto nao derruba mais a atualizacao inteira do painel
-- =====================================================================
--
-- PROBLEMA
--   refresh_painel() atualiza cinco materialized views em sequencia, numa
--   transacao so. A primeira falha aborta as demais, e como o worker da fila
--   envolve tudo em begin/exception, o rollback ainda desfaz o que ja tinha
--   dado certo - inclusive o recalcular_saldo_fechamento e o refresh do saldo
--   por conta, que rodam antes.
--
--   Em 21/09/2026 isso transformou um indice faltando (20260921000000) em
--   estrago em cascata: o erro no segundo objeto (mv_fluxo_caixa_diario)
--   desfazia o refresh do primeiro (private.mv_saldo_conta_diario), que ficou
--   parado em 15/09. Com o corte de caixa em 20/09, saldo_anchor nao achava a
--   linha do dia e devolvia 0,00, e a curva inteira de fluxo_caixa_diario -
--   nao so o snapshot - saia deslocada. Uma peca ausente cegou o painel todo.
--
-- SOLUCAO
--   private.refresh_painel_resiliente(): cada objeto na propria subtransacao,
--   o que falha fica registrado e o que deu certo permanece. O resultado volta
--   como jsonb, nao como excecao, para que o chamador possa gravar o estado
--   sem desfazer o trabalho bom. O worker da fila passa a usa-la.
--
--   public.refresh_painel() mantem nome, assinatura, grants e contrato: ainda
--   levanta excecao quando algo falha. Seis RPCs (admin_salvar_conta_com_saldo,
--   admin_salvar_fonte_financeira_com_vigencia, admin_salvar_saldo_inicial,
--   decidir_conciliacao_contabil, desfazer_decisao_conciliacao_contabil,
--   solicitar_refresh_painel) e os importadores Python dependem disso - para
--   eles, desfazer a gravacao junto com o derivado e o certo. O que muda e a
--   mensagem: agora nomeia todos os objetos que falharam, em vez de morrer no
--   primeiro.
--
-- ORDEM E DEPENDENCIA
--   mv_fluxo_caixa_diario e ancorado em saldo_anchor, que le
--   private.mv_saldo_conta_diario. Se o saldo por conta nao atualizar, o fluxo
--   e deliberadamente ignorado: publicar a curva com ancora velha seria pior
--   que deixar o snapshot anterior, e nenhum validador pegaria - os dois lados
--   da comparacao leriam a mesma ancora velha. Os snapshots de despesa e
--   conciliacao sao independentes e seguem normalmente.
--
--   Cada validador so roda se o objeto que ele confere foi atualizado. Sem
--   isso, um objeto ignorado geraria uma segunda falha, redundante.
--
--   query_canceled continua subindo sem ser capturado por objeto: cancelamento
--   e ordem de parar, nao defeito de um objeto. O worker segue tratando esse
--   caso no nivel da tarefa.
--
-- OBJETOS
--   + private.refresh_painel_resiliente()        (nova)
--   ~ public.refresh_painel()                    (vira casca que levanta)
--   ~ private.processar_fila_recalculo_saldo()   (usa a resiliente)
--
-- SEGURANCA / RISCO
--   - Nenhuma regra, valor financeiro ou permissao muda. create or replace
--     preserva os grants existentes de public.refresh_painel().
--   - A funcao nova fica em private, sem grant para anon/authenticated.
--   - Risco conhecido: pelo caminho que levanta excecao, agora tentamos os
--     cinco objetos antes de falhar, em vez de parar no primeiro. Custa alguns
--     segundos a mais num cenario que ja e de erro.
--   - Idempotente: so create or replace.
-- =====================================================================

begin;

create or replace function private.refresh_painel_resiliente()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_falhas jsonb := '[]'::jsonb;
  v_ignorados jsonb := '[]'::jsonb;
  v_atualizados text[] := array[]::text[];
  v_saldo_ok boolean;
  v_fluxo_ok boolean;
  v_despesas_ok boolean := true;
begin
  set local statement_timeout = 0;

  -- 1. Saldo por conta: base da ancora que o fluxo usa. Vai primeiro.
  begin
    refresh materialized view concurrently private.mv_saldo_conta_diario;
    v_saldo_ok := true;
    v_atualizados := v_atualizados || 'private.mv_saldo_conta_diario'::text;
  exception when others then
    v_saldo_ok := false;
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'private.mv_saldo_conta_diario', 'erro', sqlerrm);
  end;

  -- 2. Fluxo: so faz sentido com a ancora fresca (ver ORDEM E DEPENDENCIA).
  if v_saldo_ok then
    begin
      refresh materialized view concurrently public.mv_fluxo_caixa_diario;
      v_fluxo_ok := true;
      v_atualizados := v_atualizados || 'public.mv_fluxo_caixa_diario'::text;
    exception when others then
      v_fluxo_ok := false;
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'public.mv_fluxo_caixa_diario', 'erro', sqlerrm);
    end;
  else
    v_fluxo_ok := false;
    v_ignorados := v_ignorados || jsonb_build_object(
      'objeto', 'public.mv_fluxo_caixa_diario',
      'motivo', 'o saldo por conta nao atualizou; a ancora ficaria velha');
  end if;

  -- 3. Despesas e conciliacao: independentes do saldo.
  begin
    refresh materialized view concurrently public.mv_despesa_mensal;
    v_atualizados := v_atualizados || 'public.mv_despesa_mensal'::text;
  exception when others then
    v_despesas_ok := false;
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'public.mv_despesa_mensal', 'erro', sqlerrm);
  end;

  begin
    refresh materialized view concurrently public.mv_despesa_diaria;
    v_atualizados := v_atualizados || 'public.mv_despesa_diaria'::text;
  exception when others then
    v_despesas_ok := false;
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'public.mv_despesa_diaria', 'erro', sqlerrm);
  end;

  begin
    refresh materialized view concurrently public.mv_conciliacao_contabil;
    v_atualizados := v_atualizados || 'public.mv_conciliacao_contabil'::text;
  exception when others then
    v_falhas := v_falhas || jsonb_build_object(
      'objeto', 'public.mv_conciliacao_contabil', 'erro', sqlerrm);
  end;

  -- 4. Validadores: cada um so confere o que foi atualizado de fato.
  if v_saldo_ok then
    begin
      perform private.validar_saldo_diario_materializado();
    exception when others then
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'private.validar_saldo_diario_materializado()', 'erro', sqlerrm);
    end;
  end if;

  if v_fluxo_ok then
    begin
      perform private.validar_fluxo_materializado();
    exception when others then
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'private.validar_fluxo_materializado()', 'erro', sqlerrm);
    end;
  end if;

  if v_despesas_ok then
    begin
      perform private.validar_despesas_materializadas();
    exception when others then
      v_falhas := v_falhas || jsonb_build_object(
        'objeto', 'private.validar_despesas_materializadas()', 'erro', sqlerrm);
    end;
  end if;

  return jsonb_build_object(
    'ok', jsonb_array_length(v_falhas) = 0 and jsonb_array_length(v_ignorados) = 0,
    'atualizados', to_jsonb(v_atualizados),
    'ignorados', v_ignorados,
    'falhas', v_falhas,
    'em', clock_timestamp()
  );
end;
$function$;

revoke all privileges on function private.refresh_painel_resiliente()
  from public, anon, authenticated;

-- Mesmo nome, assinatura, grants e contrato de antes: levanta se algo falhou.
-- A diferenca esta na mensagem, que agora nomeia todos os objetos.
create or replace function public.refresh_painel()
returns void
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_relatorio jsonb;
  v_resumo text;
begin
  v_relatorio := private.refresh_painel_resiliente();

  if coalesce((v_relatorio->>'ok')::boolean, false) then
    return;
  end if;

  select string_agg(
    coalesce(item->>'objeto', '?') || ': '
      || coalesce(item->>'erro', item->>'motivo', 'motivo nao informado'),
    '; ' order by ordinalidade)
  into v_resumo
  from jsonb_array_elements(
    coalesce(v_relatorio->'falhas', '[]'::jsonb)
    || coalesce(v_relatorio->'ignorados', '[]'::jsonb)
  ) with ordinality as t(item, ordinalidade);

  raise exception using errcode = 'XX000',
    message = 'Atualizacao do painel incompleta - '
      || coalesce(v_resumo, 'motivo nao informado');
end;
$function$;

-- O worker grava o estado da tarefa sem desfazer o que ja foi atualizado.
create or replace function private.processar_fila_recalculo_saldo()
returns void
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_id bigint;
  v_data_min date;
  v_data_max date;
  v_somente_refresh boolean;
  v_mensagem text;
  v_relatorio jsonb;
  v_resumo text;
  v_falhas text[] := array[]::text[];
  v_jobid bigint;
begin
  if not pg_try_advisory_xact_lock(58000000::bigint) then
    return;
  end if;

  select f.id, f.data_min, f.data_max, f.somente_refresh
  into v_id, v_data_min, v_data_max, v_somente_refresh
  from private.fila_recalculo_saldo f
  where f.situacao = 'pendente'
  order by f.id
  for update skip locked
  limit 1;

  if v_id is not null then
    update private.fila_recalculo_saldo
    set situacao = 'processando', iniciado_em = clock_timestamp(), mensagem = null
    where id = v_id;

    begin
      -- Recalculo em subtransacao propria: se ele falhar, ainda vale atualizar
      -- os snapshots com o que existe hoje.
      if not v_somente_refresh then
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
              when v_somente_refresh then 'Painel atualizado.'
              else coalesce(v_mensagem, 'Saldo recalculado e painel atualizado.')
            end
        where id = v_id;
      else
        update private.fila_recalculo_saldo
        set situacao = 'erro',
            concluido_em = clock_timestamp(),
            mensagem = array_to_string(v_falhas, '; ')
        where id = v_id;
      end if;
    exception
      when query_canceled then
        update private.fila_recalculo_saldo
        set situacao = 'erro', concluido_em = clock_timestamp(),
            mensagem = 'Tempo limite excedido no processamento em background.'
        where id = v_id;
      when others then
        update private.fila_recalculo_saldo
        set situacao = 'erro', concluido_em = clock_timestamp(), mensagem = sqlerrm
        where id = v_id;
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
