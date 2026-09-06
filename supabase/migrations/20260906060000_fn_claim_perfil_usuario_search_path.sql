-- =====================================================================
-- Migration: 20260906060000_fn_claim_perfil_usuario_search_path.sql
-- Etapa 4 da auditoria / claims
--
-- Problema
-- --------
-- public.fn_claim_perfil_usuario() é SECURITY DEFINER e era a única função
-- desse tipo em public/private sem search_path fixo. Ela roda como trigger na
-- criação de usuário e é justamente o caminho que atribui papel e situação de
-- acesso, então é o pior lugar do esquema para deixar resolução de nomes
-- dependente da sessão que dispara a trigger.
--
-- As tabelas já eram referenciadas com schema explícito, então o risco
-- concreto estava na resolução de funções e operadores: um schema à frente de
-- pg_catalog no search_path da sessão poderia sombrear `lower()` e alterar a
-- correspondência de e-mail que decide qual papel o usuário recebe.
--
-- Correção
-- --------
-- Fixa search_path = pg_catalog, pg_temp, o mesmo padrão já usado pelas demais
-- funções security definer do projeto. O corpo permanece idêntico: nenhuma
-- regra de negócio muda.
-- =====================================================================

begin;

create or replace function public.fn_claim_perfil_usuario()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, pg_temp
as $function$
DECLARE
    v_papel text;
    v_ativo boolean;
BEGIN
    SELECT papel, ativo INTO v_papel, v_ativo
    FROM public.convite_perfil_usuario
    WHERE lower(email) = lower(NEW.email);

    IF FOUND THEN
        INSERT INTO public.perfil_usuario (user_id, papel, ativo)
        VALUES (NEW.id, v_papel, v_ativo)
        ON CONFLICT (user_id) DO UPDATE SET papel = v_papel, ativo = v_ativo;
    END IF;

    RETURN NEW;
END;
$function$;

comment on function public.fn_claim_perfil_usuario() is
  'Atribui papel e situação ao perfil na criação do usuário. SECURITY DEFINER com search_path fixo: a resolução de nomes não depende da sessão que dispara a trigger.';

-- Validação: nenhuma função security definer de public/private pode ficar sem
-- search_path fixo. Esta checagem cobre também as que vierem depois.
do $validacao$
declare
  v_sem_search_path text;
begin
  select string_agg(n.nspname || '.' || p.proname, ', ' order by p.proname)
    into v_sem_search_path
  from pg_catalog.pg_proc p
  join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where p.prosecdef
    and n.nspname in ('public', 'private')
    and not exists (
      select 1 from unnest(coalesce(p.proconfig, '{}')) cfg
      where cfg like 'search_path=%'
    );

  if v_sem_search_path is not null then
    raise exception
      'Validacao falhou: funcoes security definer sem search_path fixo: %',
      v_sem_search_path;
  end if;
end;
$validacao$;

commit;
