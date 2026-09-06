-- Infraestrutura minima para instalar parsers em PostgreSQL descartavel.
-- O executor aplica esta fixture somente depois de validar, por ambiente e
-- pelo catalogo, que o destino e local e tem nome sirfisher_*_test.

create schema if not exists private;

do $roles$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role;
  end if;
end;
$roles$;

create table if not exists public.saldo_inicial (
  conta text,
  saldo numeric,
  data_base date
);

create table if not exists public.raw_bb (
  data date,
  valor numeric,
  dedup_hash text
);
