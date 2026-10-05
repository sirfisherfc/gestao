#!/usr/bin/env python3
"""Executa a consulta de pendencias em PostgreSQL descartavel, com dados ficticios."""
from __future__ import annotations

from pathlib import Path
import psycopg2
from pg_descartavel import exigir_banco_descartavel

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase/migrations/20261005000000_pendencias_recorrentes_anteriores.sql"

SETUP = """
create schema if not exists private;
do $$begin
  if not exists (select 1 from pg_roles where rolname='anon') then create role anon; end if;
  if not exists (select 1 from pg_roles where rolname='authenticated') then create role authenticated; end if;
end$$;
create function public.usuario_pode_acessar_pagina(text) returns boolean language sql as
  $$select coalesce(current_setting('test.acesso',true),'sim')='sim'$$;
create function public.parametro_valor(text,numeric) returns numeric language sql as $$select 2::numeric$$;
create function public.unidade_principal_nome() returns text language sql as $$select 'TESTE'::text$$;
create table public.conta_recorrente (
  id bigint primary key, nome text, dia_vencimento smallint, unidade text,
  ativa boolean, criado_em timestamptz
);
create table public.conta_recorrente_pagamento (
  id bigint generated always as identity, conta_id bigint, competencia date,
  situacao text, valor numeric, unique(conta_id,competencia)
);
create view referencia as select
  (current_timestamp at time zone 'America/Fortaleza')::date as hoje,
  date_trunc('month',current_timestamp at time zone 'America/Fortaleza')::date as mes;
insert into public.conta_recorrente
select id,'Conta ficticia '||id,31,case when id=6 then 'OUTRA' else 'TESTE' end,
  id<>3,case when id in (2,4,6) then mes::timestamp at time zone 'America/Fortaleza'
    when id=5 then (mes-interval '1 month')::timestamp at time zone 'America/Fortaleza'
    else (mes-interval '3 months')::timestamp at time zone 'America/Fortaleza' end
from referencia cross join generate_series(1,6) id;
insert into public.conta_recorrente_pagamento(conta_id,competencia,situacao,valor)
select 1,(mes-interval '3 months')::date,'pago',100 from referencia union all
select 1,(mes-interval '2 months')::date,'pago',200 from referencia union all
select 1,mes,'pago',10000 from referencia union all
select 4,(mes-interval '3 months')::date,'pago',100 from referencia union all
select 4,(mes-interval '2 months')::date,'sem_movimento',null from referencia union all
select 6,(mes-interval '3 months')::date,'pago',100 from referencia;
"""

ASSERTIONS = """
do $$declare mes date; anterior date; n integer;
begin
  select r.mes into mes from referencia r;
  anterior:=(mes-interval '1 month')::date;
  select count(*) into n from public.listar_pendencias_recorrentes(mes);
  assert n=3, 'Esperadas apenas tres competencias pendentes';
  assert exists(select 1 from public.listar_pendencias_recorrentes(mes) p
    where p.conta_id=1 and p.competencia=anterior and p.media_3=150),
    'Pagamento do mes atual nao baixa anterior nem contamina media historica';
  assert exists(select 1 from public.listar_pendencias_recorrentes(mes) p
    where p.conta_id=4 and p.competencia=anterior and p.media_3=100),
    'Historico legado anterior ao cadastro deve iniciar acompanhamento';
  assert exists(select 1 from public.listar_pendencias_recorrentes(mes) p
    where p.conta_id=5 and p.media_3 is null), 'Sem historico segue pendente sem valor inventado';
  assert not exists(select 1 from public.listar_pendencias_recorrentes(mes) p
    where p.conta_id in (2,3,6)), 'Nao inventar cobrancas antes do cadastro, inativas ou de outra unidade';
  assert not exists(select 1 from public.listar_pendencias_recorrentes(mes) p
    where p.vencimento<>(p.competencia+interval '1 month - 1 day')::date),
    'Dia 31 deve ser limitado ao ultimo dia de cada mes';
  assert not exists(select 1 from public.listar_pendencias_recorrentes((mes+interval '2 months')::date) p
    where p.vencimento>=(select hoje from referencia)), 'Nao tratar vencimentos futuros como atraso';
  assert (select count(*) from public.conta_recorrente_pagamento)=6, 'Leitura nao deve materializar pagamentos';
  insert into public.conta_recorrente_pagamento(conta_id,competencia,situacao,valor)
    values(1,anterior,'pago',150);
  assert not exists(select 1 from public.listar_pendencias_recorrentes(mes) p where p.conta_id=1),
    'Baixa de setembro remove apenas a pendencia de setembro';
  insert into public.conta_recorrente_pagamento(conta_id,competencia,situacao,valor)
    values(4,anterior,'sem_movimento',null);
  assert not exists(select 1 from public.listar_pendencias_recorrentes(mes) p where p.conta_id=4),
    'Sem movimento encerra pendencia da competencia';
  delete from public.conta_recorrente_pagamento where conta_id=1 and competencia=anterior;
  assert exists(select 1 from public.listar_pendencias_recorrentes(mes) p where p.conta_id=1),
    'Limpar baixa reabre a competencia anterior';
  begin
    perform public.listar_pendencias_recorrentes(null); raise exception 'Aceitou competencia nula';
  exception when invalid_parameter_value then null; end;
  begin
    perform public.listar_pendencias_recorrentes(mes+1); raise exception 'Aceitou competencia invalida';
  exception when invalid_parameter_value then null; end;
  perform set_config('test.acesso','nao',false);
  begin
    perform public.listar_pendencias_recorrentes(mes); raise exception 'Aceitou usuario sem permissao';
  exception when insufficient_privilege then null; end;
  perform set_config('test.acesso','sim',false);
  assert has_function_privilege('authenticated','public.listar_pendencias_recorrentes(date)','execute'),
    'Usuario autenticado deve ter grant';
  assert not has_function_privilege('anon','public.listar_pendencias_recorrentes(date)','execute'),
    'Anonimo nao deve ter grant';
end$$;
"""

def main() -> None:
    with psycopg2.connect("") as conn:
        exigir_banco_descartavel(conn, "RECORRENTES_SQL_DISPOSABLE")
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(SETUP)
            sql = MIGRATION.read_text(encoding="utf-8")
            cur.execute(sql)
            cur.execute(sql)
            cur.execute(ASSERTIONS)
    print("RECURRING_SQL_OK history=1 forecast=1 settlement=1 no_charge=1 dates=1 access=1 idempotence=1")

if __name__ == "__main__":
    main()
