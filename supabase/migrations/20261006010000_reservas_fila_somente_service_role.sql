-- =====================================================================
-- Fila de e-mail e conversoes do sistema de reservas: so service_role
-- =====================================================================
--
-- PROBLEMA
--   Conferido no catalogo em 06/10/2026: quatro funcoes SECURITY DEFINER da
--   fila de notificacoes/conversoes tem EXECUTE explicito para anon e
--   authenticated, sem checagem interna de papel:
--     fn_claim_pending_notifications(int)   devolve as linhas da fila de
--                                           e-mail (dados de clientes) e as
--                                           marca 'processing'
--     fn_finalize_notification(uuid,text,text)
--     fn_finalize_openai_ads_conversion(uuid,text,text)
--     fn_enqueue_reservation_reminders(date)
--   Pela Data API, qualquer pessoa com a chave publica dos sites poderia
--   ler a fila e travar ou marcar envios. A fonte do sistema de reservas
--   (reservas/supabase/functions.sql) ja declara essas funcoes restritas a
--   service_role, e as irmas fn_claim_pending_{openai_ads,ga4,meta}_* estao
--   corretas no banco: o grant extra e um desvio, provavelmente da
--   unificacao dos bancos no projeto portal.
--
-- SOLUCAO
--   Reaplicar o que a fonte declara: revogar de public/anon/authenticated e
--   manter service_role.
--
-- CHAMADORES (conferidos)
--   - Edge Functions send-notifications e send-openai-ads-conversions usam
--     SUPABASE_SERVICE_ROLE_KEY.
--   - O cron enqueue-reservation-reminders roda como postgres (dono).
--   Nenhum front-end chama essas funcoes.
--
-- RISCO: baixo. So permissoes; nenhuma tabela, dado ou corpo de funcao muda.
-- Idempotente: revoke/grant podem ser repetidos.
-- =====================================================================

begin;

revoke all on function public.fn_claim_pending_notifications(int)
  from public, anon, authenticated;
grant execute on function public.fn_claim_pending_notifications(int)
  to service_role;

revoke all on function public.fn_finalize_notification(uuid, text, text)
  from public, anon, authenticated;
grant execute on function public.fn_finalize_notification(uuid, text, text)
  to service_role;

revoke all on function public.fn_finalize_openai_ads_conversion(uuid, text, text)
  from public, anon, authenticated;
grant execute on function public.fn_finalize_openai_ads_conversion(uuid, text, text)
  to service_role;

revoke all on function public.fn_enqueue_reservation_reminders(date)
  from public, anon, authenticated;
grant execute on function public.fn_enqueue_reservation_reminders(date)
  to service_role;

notify pgrst, 'reload schema';

commit;
