#!/usr/bin/env python3
"""Exercita a migration real com dados sintéticos e rollback obrigatório.

O modo padrão exige PostgreSQL local descartável. --portal-rollback usa a
conexão canônica, mas cria apenas dois schemas isolados dentro da transação;
as referências da fixture/migration são redirecionadas a esses schemas.
Nenhuma tabela do aplicativo é modificada nesse modo.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / 'supabase/migrations'
MIGRATION = '20261104180315_bb_rende_facil_no_caixa.sql'


def body(sql):
    sql = sql.strip()
    # Comentários iniciais podem preceder o BEGIN.
    start = sql.index('begin;') + len('begin;')
    assert sql.endswith('commit;')
    return sql[start:-len('commit;')]


def build_sql():
    fixture = (ROOT / 'scripts/ci/fixtures/bb_rende_facil_setup.sql').read_text(encoding='utf8')
    generic = (MIGRATIONS / '20260818120000_saldo_generico_por_conta.sql').read_text(encoding='utf8')
    start = generic.index('create or replace view private.movimento_saldo_conta as')
    end = generic.index('-- Salvar uma conta passa')
    # Somente view de movimentos e snapshot originais: os demais consumidores
    # são dependências de produção, verificadas no ensaio separado da migration.
    movement = generic[start:generic.index('revoke all privileges on table private.movimento_saldo_conta', start)]
    snapshot_start = generic.index('create materialized view if not exists private.mv_saldo_conta_diario')
    snapshot_end = generic.index('revoke all privileges on table private.mv_saldo_conta_diario', snapshot_start)
    assert snapshot_end < end
    snapshot = generic[snapshot_start:snapshot_end]
    migration = body((MIGRATIONS / MIGRATION).read_text(encoding='utf8'))
    return fixture + movement + snapshot, migration


def verify(cur, schema='public', private='private'):
    cur.execute(f"""select s.dia::text,s.saldo from {private}.mv_saldo_conta_diario s
      join {schema}.fonte_financeira f on f.conta_id=s.conta_id
      where f.saldo_adaptador='bb_rende_facil' order by s.dia""")
    balances = {day: value for day, value in cur.fetchall()}
    assert balances['2026-09-30'] == 0, 'Saldo anterior deve permanecer zero'
    assert balances['2026-10-05'] == 100, 'Aplicação precisa aumentar a aplicação'
    assert balances['2026-10-06'] == 60, 'Resgate precisa reduzir a aplicação'
    assert balances['2026-10-08'] == 60, 'Pix, outro fundo e outra conta não entram'
    cur.execute(f"select count(*) from {private}.movimento_saldo_conta where adaptador='bb_rende_facil'")
    assert cur.fetchone() == (2,), 'Uma contrapartida por movimento do produto'
    cur.execute(f"select count(*) from {schema}.fato_financeiro where lower(btrim(tipo))='bb rende fácil' and entra_dre")
    assert cur.fetchone() == (0,), 'Aplicação/resgate não são resultado operacional'
    cur.execute(f"select count(*) from {schema}.fato_financeiro where tipo='Pix-Envio' and entra_dre")
    assert cur.fetchone() == (2,), 'Operação comum precisa manter sua classificação'
    cur.execute(f"""select has_function_privilege('anon',
      '{schema}.admin_salvar_fonte_financeira_com_vigencia(text,text,smallint,boolean,boolean,boolean,boolean,boolean,text,date,date)', 'execute'),
      has_function_privilege('authenticated',
      '{schema}.admin_salvar_fonte_financeira_com_vigencia(text,text,smallint,boolean,boolean,boolean,boolean,boolean,text,date,date)', 'execute'),
      has_table_privilege('authenticated','{private}.movimento_saldo_conta','select')""")
    assert cur.fetchone() == (False, True, False), 'Grants mínimos devem ser preservados'
    return 8


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portal-rollback', action='store_true')
    args = parser.parse_args()
    import psycopg2
    if args.portal_rollback:
        sys.path.insert(0, str(ROOT / 'scripts/importacao'))
        from stone_fechamento import conectar
        conn = conectar()
        public, private = 'sirfisher_rf_test_public', 'sirfisher_rf_test_private'
    else:
        assert os.environ.get('PGHOST') in ('localhost', '127.0.0.1', '::1')
        assert os.environ.get('PGDATABASE') == 'sirfisher_rende_facil_test'
        conn = psycopg2.connect('')
        public, private = 'public', 'private'
    setup, migration = build_sql()
    try:
        with conn.cursor() as cur:
            cur.execute("set local statement_timeout='60s'")
            if args.portal_rollback:
                cur.execute('select to_regnamespace(%s),to_regnamespace(%s)', (public, private))
                assert cur.fetchone() == (None, None), 'Schemas isolados já existem; recusar reutilização'
                setup = setup.replace('create schema if not exists auth;', '')
                setup = setup.replace("create or replace function auth.uid() returns uuid language sql as 'select null::uuid';", '')
                setup = setup.replace('public', public).replace('private', private)
                migration = migration.replace('public.', public + '.').replace('private.', private + '.')
            cur.execute(setup)
            cur.execute(migration)
            count = verify(cur, public, private)
            # O DROP simula o descarte ON COMMIT DROP entre reexecuções.
            cur.execute('drop table bb_rende_saldos_antes')
            cur.execute(migration)
            verify(cur, public, private)
            cur.execute(f"select count(*) from {public}.conta where nome='BB Rende Fácil'")
            assert cur.fetchone() == (1,), 'Reexecução não pode duplicar conta'
            # Exclusão de resgate da cobertura precisa acionar a proteção,
            # em vez de publicar saldo negativo silenciosamente.
            cur.execute('savepoint negative_balance')
            cur.execute(f"update {public}.raw_bb set valor=140 where id=3")
            cur.execute(f'refresh materialized view {private}.mv_saldo_conta_diario')
            cur.execute('drop table bb_rende_saldos_antes')
            try:
                cur.execute(migration)
            except psycopg2.Error as exc:
                assert 'Resgates Rende Fácil excedem' in str(exc)
                cur.execute('rollback to savepoint negative_balance')
            else:
                raise AssertionError('Saldo negativo deveria bloquear a migration')
            print(f'BB_RENDE_FACIL_SQL_OK checks={count + 2} idempotencia=1 rollback=1')
    finally:
        conn.rollback()
        conn.close()


if __name__ == '__main__':
    main()
