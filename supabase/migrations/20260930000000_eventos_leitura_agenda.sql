-- A Edge Function event-quote (service_role) recebia "permission denied" ao ler
-- a agenda de reservas, e nenhum orçamento conferia bloqueios e lotação.
-- Enquanto esta migration não for aplicada, a função usa como alternativa a
-- rotina pública get_available_time_slots. Somente leitura; nada muda para
-- anon ou authenticated.

grant select on public.blocked_dates,
                public.blocked_time_slots,
                public.availability_rules,
                public.restaurant_settings,
                public.reservations
  to service_role;
