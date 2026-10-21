-- =====================================================================
-- Configuração da empresa volta a ser lida (403 em toda página)
-- =====================================================================
--
-- PROBLEMA (logs da API em 21/10/2026)
--   Toda abertura de página chama rpc/app_configuracao_empresa e recebe 403
--   ("permission denied for table configuracao_empresa"). A função é
--   SECURITY INVOKER por contrato (respeita a política RLS singleton = true)
--   e depende do SELECT por coluna (nome, subtitulo) concedido a anon e
--   authenticated em 20260816000000. Esses grants por coluna não existem mais
--   no portal; nenhuma migration os revoga (provavelmente se perderam na
--   migração do projeto). Efeitos:
--   - o nome configurado nunca aparece (cabeçalho e login mostram "Painel");
--   - assets/app-config.js só guarda a configuração quando as duas RPCs
--     respondem, então nunca guarda: toda página paga uma rodada de rede a
--     mais antes de liberar o acesso, e o console registra o 403.
--
-- SOLUÇÃO
--   Restaura exatamente o acesso desenhado em 20260816000000 e mantido pela
--   allowlist de 20260818090000: SELECT apenas em nome e subtitulo, para anon
--   (tela de login) e authenticated, sob a política existente. A função não
--   muda. O EXECUTE para PUBLIC, que voltou a existir sem migration que o
--   concedesse, é retirado, como em 20260816000000; anon, authenticated e
--   service_role continuam com EXECUTE.
--
-- OBJETOS
--   ~ grants de public.configuracao_empresa (colunas nome, subtitulo)
--   ~ grants de public.app_configuracao_empresa()
--
-- RISCOS
--   Baixo. Nenhum dado além do que o desenho original já expunha (nome e
--   subtítulo da empresa, linha única). Reversão: revoke select (nome,
--   subtitulo) on public.configuracao_empresa from anon, authenticated.
-- =====================================================================

begin;

grant select (nome, subtitulo) on table public.configuracao_empresa to anon, authenticated;

revoke all privileges on function public.app_configuracao_empresa() from public;
grant execute on function public.app_configuracao_empresa() to anon, authenticated, service_role;

do $validacao$
declare
  v_nome text;
begin
  if has_function_privilege('public', 'public.app_configuracao_empresa()', 'EXECUTE') then
    raise exception 'Validacao falhou: PUBLIC ainda executa app_configuracao_empresa';
  end if;

  set local role anon;
  select e.nome into v_nome from public.app_configuracao_empresa() e;
  reset role;
  if v_nome is null then
    raise exception 'Validacao falhou: anon nao le o nome da empresa';
  end if;

  v_nome := null;
  set local role authenticated;
  select e.nome into v_nome from public.app_configuracao_empresa() e;
  reset role;
  if v_nome is null then
    raise exception 'Validacao falhou: authenticated nao le o nome da empresa';
  end if;

  -- Só nome e subtitulo: as demais colunas e a tabela inteira continuam fechadas.
  if has_table_privilege('anon', 'public.configuracao_empresa', 'SELECT')
     or has_table_privilege('authenticated', 'public.configuracao_empresa', 'SELECT')
     or has_column_privilege('anon', 'public.configuracao_empresa', 'atualizado_por', 'SELECT')
     or has_column_privilege('authenticated', 'public.configuracao_empresa', 'atualizado_por', 'SELECT')
     or has_column_privilege('anon', 'public.configuracao_empresa', 'singleton', 'SELECT') then
    raise exception 'Validacao falhou: configuracao_empresa ficou exposta alem de nome e subtitulo';
  end if;
end;
$validacao$;

commit;
