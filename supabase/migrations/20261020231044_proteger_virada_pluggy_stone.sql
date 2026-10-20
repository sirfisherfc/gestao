-- Impede que CSV e Pluggy dupliquem movimentos depois da virada da conta.
-- Duplicatas com o mesmo hash continuam chegando ao ON CONFLICT existente.
-- Nenhuma linha historica e alterada; o bloqueio so existe em contas que
-- efetivamente receberam ao menos uma linha Pluggy.
begin;

create index if not exists ix_raw_stone_extrato_pluggy_corte
  on public.raw_stone_extrato (conta_id, data_hora)
  where origem_carga = 'pluggy';

create or replace function private.proteger_virada_pluggy_stone()
returns trigger
language plpgsql
set search_path = pg_catalog, pg_temp
as $$
begin
  if new.origem_carga is distinct from 'pluggy'
     and not exists (
       select 1 from public.raw_stone_extrato e
       where e.dedup_hash = new.dedup_hash
     )
     and exists (
       select 1 from public.raw_stone_extrato e
       where e.conta_id = new.conta_id
         and e.origem_carga = 'pluggy'
         and e.data_hora < new.data_hora::date + interval '1 day'
     ) then
    raise exception using
      errcode = '23514',
      message = 'Extrato Stone deste periodo ja usa Pluggy. CSV recusado para evitar duplicidade; confira a integracao na pagina Status.';
  end if;
  return new;
end;
$$;

revoke all on function private.proteger_virada_pluggy_stone() from public, anon, authenticated;
grant execute on function private.proteger_virada_pluggy_stone() to service_role;

drop trigger if exists trg_proteger_virada_pluggy_stone on public.raw_stone_extrato;
create trigger trg_proteger_virada_pluggy_stone
before insert on public.raw_stone_extrato
for each row execute function private.proteger_virada_pluggy_stone();

comment on function private.proteger_virada_pluggy_stone() is
  'Bloqueia CSV novo apos a primeira data Pluggy da conta; permite hashes historicos ja importados.';

commit;
