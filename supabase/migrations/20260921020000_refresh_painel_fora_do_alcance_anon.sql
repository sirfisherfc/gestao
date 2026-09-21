-- =====================================================================
-- refresh_painel() sai do alcance de quem nao esta logado
-- =====================================================================
--
-- PROBLEMA
--   public.refresh_painel() esta com EXECUTE para PUBLIC (=X no ACL) e um
--   grant explicito para anon. Como o schema public tem USAGE para anon e o
--   PostgREST expoe esse schema, qualquer um com a chave anon - que e publica,
--   vai no front-end - podia disparar pela API um refresh das cinco
--   materialized views. Hoje esse trabalho leva ~55 s e roda com
--   statement_timeout zerado, em serie, sem portao de permissao no corpo: a
--   funcao nao chama exigir_admin, usuario_tem_papel nem
--   usuario_pode_acessar_pagina, porque nasceu para ser chamada pelos
--   importadores e por outras RPCs.
--
--   Nada indica que isso tenha sido explorado. E exposicao, nao incidente.
--
-- SOLUCAO
--   Tirar EXECUTE de PUBLIC e de anon. Quem precisa continua podendo:
--
--   - Os importadores Python conectam como postgres (dono da funcao).
--   - As seis RPCs que a chamam por dentro (admin_salvar_conta_com_saldo,
--     admin_salvar_fonte_financeira_com_vigencia, admin_salvar_saldo_inicial,
--     decidir_conciliacao_contabil, desfazer_decisao_conciliacao_contabil,
--     solicitar_refresh_painel) sao security definer: rodam com o privilegio
--     do dono, nao o de quem chamou.
--   - authenticated e service_role mantem o EXECUTE que ja tinham; o grant
--     abaixo apenas reafirma, para o caso de reexecucao em banco novo.
--
--   Nenhuma pagina chama refresh_painel direto: status.html vai por
--   solicitar_refresh_painel, que tem o proprio gate.
--
-- OBJETOS
--   ~ grants de public.refresh_painel()   (nenhuma definicao muda)
--
-- SEGURANCA / RISCO
--   - Nao muda regra, valor, definicao de funcao ou dado.
--   - Idempotente: revoke de privilegio ausente e no-op.
--   - Atencao para o futuro: create or replace preserva ACL, mas um
--     drop + create devolveria o EXECUTE para PUBLIC pelo padrao do
--     PostgreSQL e para anon pelo default privileges do Supabase. Quem
--     recriar esta funcao precisa repetir este revoke.
-- =====================================================================

begin;

revoke execute on function public.refresh_painel() from public;
revoke execute on function public.refresh_painel() from anon;

grant execute on function public.refresh_painel() to authenticated, service_role;

commit;
