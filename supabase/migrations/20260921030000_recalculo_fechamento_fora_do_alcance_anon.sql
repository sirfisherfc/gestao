-- =====================================================================
-- recalcular_saldo_fechamento() sai do alcance de quem nao esta logado
-- =====================================================================
--
-- PROBLEMA
--   Continuacao de 20260921020000, que fechou o mesmo buraco em
--   refresh_painel(). A outra metade do par de manutencao ficou aberta, e e a
--   mais grave das duas: public.recalcular_saldo_fechamento(date,date,integer)
--   **grava** em saldo_fechamento_mensal - apaga as gravacoes futuras alem do
--   limite e reescreve os fechamentos mensais a partir de
--   saldo_mensal_calculado.
--
--   O ACL tem EXECUTE para PUBLIC (=X) e grant explicito para anon. Com o
--   schema public exposto pelo PostgREST e USAGE para anon, qualquer um com a
--   chave anon - que e publica, vai no front-end - podia reescrever os
--   fechamentos pela API. A funcao e security definer e nao tem portao no
--   corpo: nao chama exigir_admin, usuario_tem_papel nem
--   usuario_pode_acessar_pagina, porque nasceu para ser chamada pelos
--   importadores e pelo worker da fila.
--
--   Nada indica que isso tenha sido explorado. E exposicao, nao incidente.
--
-- SOLUCAO
--   Tirar EXECUTE de PUBLIC e de anon, como em 20260921020000. Quem precisa
--   continua podendo:
--
--   - Os importadores Python conectam como postgres, dono da funcao
--     (importacao_core chama "select * from recalcular_saldo_fechamento(...)").
--   - private.processar_fila_recalculo_saldo() e security definer: roda com o
--     privilegio do dono, nao o de quem chamou.
--   - Nenhuma pagina chama a funcao direto. status.html vai por
--     solicitar_recalculo_saldo, que tem o proprio gate de permissao.
--
-- FICA DE FORA, DE PROPOSITO
--   authenticated mantem o EXECUTE. Tirar dele tambem seria defensavel - a
--   funcao nao tem portao, entao hoje qualquer usuario logado, de qualquer
--   papel, alcanca a reescrita dos fechamentos. Mas isso muda o alcance de
--   quem ja passou pelo login e merece decisao propria, nao carona nesta
--   migration.
--
-- OBJETOS
--   ~ grants de public.recalcular_saldo_fechamento(date, date, integer)
--     (nenhuma definicao muda)
--
-- SEGURANCA / RISCO
--   - Nao muda regra, valor, definicao de funcao ou dado.
--   - Idempotente: revoke de privilegio ausente e no-op.
--   - Mesma armadilha da anterior: create or replace preserva ACL, mas
--     drop + create devolveria EXECUTE a PUBLIC pelo padrao do PostgreSQL e a
--     anon pelo default privileges do Supabase. Quem recriar precisa repetir
--     este revoke.
-- =====================================================================

begin;

revoke execute on function public.recalcular_saldo_fechamento(date, date, integer)
  from public;
revoke execute on function public.recalcular_saldo_fechamento(date, date, integer)
  from anon;

grant execute on function public.recalcular_saldo_fechamento(date, date, integer)
  to authenticated, service_role;

commit;
