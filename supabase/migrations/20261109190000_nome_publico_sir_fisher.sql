-- Nome público só "Sir Fisher" (decisão do proprietário em 09/11/2026).
-- Troca o rótulo antigo "Sir Fisher Praia" nos textos que o público vê:
-- local do Réveillon, modelos de WhatsApp do Réveillon e a mensagem padrão
-- do WhatsApp das reservas. Não cria nem remove objetos.
-- Idempotente: só altera linhas que ainda contêm o rótulo antigo.
-- Instalações sem as tabelas do portal ou do Réveillon não recebem mudança.
begin;

do $migration$
begin
  if to_regclass('public.rv_events') is not null then
    update public.rv_events
       set venue_name = replace(venue_name, 'Sir Fisher Praia', 'Sir Fisher')
     where venue_name like '%Sir Fisher Praia%';

    update public.rv_events
       set whatsapp_templates = replace(whatsapp_templates::text, 'Sir Fisher Praia', 'Sir Fisher')::jsonb
     where whatsapp_templates::text like '%Sir Fisher Praia%';

    update public.rv_events
       set texts = replace(texts::text, 'Sir Fisher Praia', 'Sir Fisher')::jsonb
     where texts::text like '%Sir Fisher Praia%';
  else
    raise notice 'Módulo de Réveillon ausente; nada a ajustar em rv_events.';
  end if;

  if to_regclass('public.restaurant_settings') is not null then
    update public.restaurant_settings
       set value = replace(value::text, 'Sir Fisher Praia', 'Sir Fisher')::jsonb
     where value::text like '%Sir Fisher Praia%';
  else
    raise notice 'Tabela restaurant_settings ausente; nada a ajustar.';
  end if;
end
$migration$;

commit;
