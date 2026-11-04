#!/usr/bin/env python3
"""Real PostgreSQL tests with synthetic identities and isolated schemas.

Default: disposable local database. --portal-rollback uses the canonical
connection, creates only UUID-named isolated schemas and always rolls back.
--portal-concurrency commits ONLY those synthetic schemas to permit separate
connections, then removes exactly the schemas created by this invocation.
No live application table, user or voucher is modified by either mode.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import sys
import threading
import uuid

ROOT = Path(__file__).resolve().parents[2]
VERSION = '20261104200024'
MIGRATION = ROOT / f'supabase/migrations/{VERSION}_benefit_vouchers.sql'
HARDENING = ROOT / 'supabase/migrations/20261104202352_benefit_voucher_private_rpc.sql'
AWARD = ROOT / 'supabase/migrations/20261104203828_benefit_voucher_award_reason.sql'
SOCIO, ADMIN, MANAGER, INACTIVE, UNKNOWN = [str(uuid.UUID(int=i)) for i in range(1, 6)]


def connection(portal=False):
    if portal:
        sys.path.insert(0, str(ROOT / 'scripts/importacao'))
        from stone_fechamento import conectar
        return conectar()
    import psycopg2
    assert os.environ.get('PGHOST') in ('localhost', '127.0.0.1', '::1')
    assert os.environ.get('PGDATABASE') == 'sirfisher_vouchers_test'
    return psycopg2.connect('')


def setup(cur, schemas):
    public, private, auth = schemas
    for schema in schemas:
        assert re.fullmatch(r'sirfisher_bv_[0-9a-f]{16}_(public|private|auth)', schema)
        cur.execute(f'create schema {schema}')
        cur.execute(f'grant usage on schema {schema} to authenticated')
    cur.execute(f"""
      create function {auth}.uid() returns uuid language sql stable as
      $$select nullif(current_setting('request.jwt.claims',true),'')::jsonb->>'sub'$$;
    """.replace("returns uuid", "returns text"))
    # Explicit cast at every transformed auth.uid() call retains UUID semantics.
    cur.execute(f"""
      create table {public}.perfil_usuario(user_id uuid primary key,papel text,ativo boolean);
      create table {public}.app_users(auth_user_id uuid primary key,name text,role text,active boolean);
      create table {public}.pagina_permissao(pagina text primary key,papeis text[]);
      create function {public}.usuario_tem_papel(p text[]) returns boolean language sql stable security definer as
      $$select exists(select 1 from {public}.perfil_usuario where user_id={auth}.uid()::uuid and ativo and papel=any(p))$$;
      create function {public}.usuario_pode_acessar_pagina(p text) returns boolean language sql stable security definer as
      $$select {public}.usuario_tem_papel(array['admin']) or exists(select 1 from {public}.perfil_usuario u join {public}.pagina_permissao pp on pp.pagina=p where user_id={auth}.uid()::uuid and ativo and papel=any(pp.papeis))$$;
      create function {private}.nome_exibicao_usuario(p uuid) returns text language sql as $$select 'Ator sintético'::text$$;
      create function {auth}.gen_bytes(p integer) returns bytea language plpgsql as $$begin
        if current_setting('bv_test.crypto',true)='once' then
          perform set_config('bv_test.crypto','random',true); return decode(repeat('00',p),'hex');
        elsif current_setting('bv_test.crypto',true)='zero' then return decode(repeat('00',p),'hex');
        end if;
        return extensions.gen_random_bytes(p);
      end$$;
    """)
    cur.execute(f'insert into {public}.perfil_usuario values (%s,\'socio\',true),(%s,\'admin\',true),(%s,\'gerente\',true),(%s,\'socio\',false)', (SOCIO, ADMIN, MANAGER, INACTIVE))
    cur.execute(f'insert into {public}.app_users values (%s,\'Gerente sintético\',\'operator\',true),(%s,\'Inativo\',\'operator\',false)', (MANAGER, INACTIVE))
    sql = MIGRATION.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    sql = sql.replace('private.', private + '.').replace('public.', public + '.').replace('auth.uid()', auth + '.uid()::uuid')
    sql = sql.replace('extensions.gen_random_bytes(', auth + '.gen_bytes(')
    cur.execute(sql)
    cur.execute(sql)  # Exact migration must be re-executable.
    hardening=HARDENING.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    hardening=hardening.replace('private.',private+'.').replace('public.',public+'.')
    cur.execute(hardening)
    cur.execute(hardening)
    award=AWARD.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    award=award.replace('private.',private+'.').replace('public.',public+'.')
    cur.execute(award)
    cur.execute(award)


def identity(cur, uid, role='authenticated'):
    assert role in ('authenticated', 'anon')
    cur.execute(f'set local role {role}')
    cur.execute("select set_config('request.jwt.claims',%s,true)", (json.dumps({'sub': uid, 'role': role}),))


def rpc(cur, public, name, values):
    cur.execute(f'select {public}.benefit_voucher_{name}(' + ','.join(['%s'] * len(values)) + ')', values)
    return cur.fetchone()[0]


def issue(cur, public, reason='friend', detail=None, kind='fixed', value=250, expiry=None, nonce=None):
    if expiry is None:
        cur.execute("select (clock_timestamp() at time zone 'America/Fortaleza')::date+30")
        expiry = cur.fetchone()[0]
    return rpc(cur, public, 'issue', (nonce or str(uuid.uuid4()), 'Beneficiário sintético', '85999990000', kind, value, expiry, reason, detail, 'Nota privada de teste'))


def denied(cur, call, code='42501'):
    cur.execute('savepoint expected_error')
    try:
        call()
    except Exception as error:
        assert getattr(error, 'pgcode', None) == code, f'Unexpected SQLSTATE {getattr(error,"pgcode",None)}'
        cur.execute('rollback to savepoint expected_error')
    else:
        raise AssertionError('Operation unexpectedly allowed')
    finally:
        cur.execute('release savepoint expected_error')


def verify(cur, schemas):
    public, private, _ = schemas
    identity(cur, SOCIO)
    nonce = str(uuid.uuid4())
    created = issue(cur, public, nonce=nonce)
    assert created['ok']
    v = created['voucher']; vid = v['id']; code = v['code']
    assert re.fullmatch(r'SF-[0-9A-HJKMNP-TV-Z]{4}(-[0-9A-HJKMNP-TV-Z]{4}){2}', code)
    assert v['issue_reason'] == 'friend' and v['internal_note']
    assert issue(cur, public, nonce=nonce)['voucher']['id'] == vid
    conflict=issue(cur, public, nonce=nonce, reason='loyalty')
    assert not conflict['ok'] and conflict['reason']=='request_conflict' and conflict['voucher']['id']==vid
    for reason in ('recovery', 'commercial', 'photo_production', 'staff_birthday', 'loyalty', 'promotion', 'influencer', 'award', 'other'):
        # Reset limiter as owner only; this is a synthetic schema.
        cur.execute('reset role'); cur.execute(f'delete from {private}.benefit_voucher_rate_limits'); identity(cur, SOCIO)
        assert issue(cur, public, reason=reason, detail='Texto livre')['voucher']['issue_reason'] == reason
    denied(cur, lambda: issue(cur, public, reason='other'), '22023')
    denied(cur, lambda: issue(cur, public, reason='invalid'), '22023')
    for value in (0, -1, 101, 'NaN', 'Infinity', 1.001):
        denied(cur, lambda value=value: issue(cur, public, kind='percent', value=value), '22023')
    denied(cur, lambda: issue(cur, public, expiry='2000-01-01'), '22023')
    denied(cur, lambda: issue(cur, public, expiry='infinity'), '22023')
    pct = issue(cur, public, kind='percent', value=15.5)['voucher']
    result = rpc(cur, public, 'list', ('', '', 0, 50, ''))
    assert result['summary']['fixed_available_total'] == 2500
    assert result['summary']['percent_available_count'] == 1
    assert rpc(cur, public, 'list', (code, '', 0, 50, ''))['total'] == 1
    assert rpc(cur, public, 'list', ('', '', 0, 50, 'other'))['total'] == 1
    awards=rpc(cur, public, 'list', ('', '', 0, 50, 'award'))
    assert awards['total']==1 and awards['rows'][0]['issue_reason']=='award'
    cur.execute("select set_config('bv_test.crypto','zero',true)")
    assert issue(cur, public)['voucher']['code'] == 'SF-0000-0000-0000'
    denied(cur, lambda: issue(cur, public), 'P0001')
    cur.execute("select set_config('bv_test.crypto','once',true)")
    assert issue(cur, public)['voucher']['code'] != 'SF-0000-0000-0000'
    cur.execute("select set_config('bv_test.crypto','random',true)")
    identity(cur, ADMIN)
    denied(cur, lambda: issue(cur, public, nonce=nonce), '22023')
    for uid in (MANAGER, INACTIVE, UNKNOWN):
        identity(cur, uid)
        for call in (lambda: issue(cur, public), lambda: rpc(cur, public, 'list', ('', '', 0, 10, '')),
                     lambda: rpc(cur, public, 'detail', (vid,)), lambda: rpc(cur, public, 'cancel', (vid, 'Teste', True))):
            denied(cur, call)
    identity(cur, SOCIO)
    denied(cur, lambda: rpc(cur, public, 'redeem', (vid, True)))  # Socio alone is not reservation staff.
    identity(cur, MANAGER)
    looked = rpc(cur, public, 'lookup', (code.lower().replace('-', ' '),))
    assert looked['ok'] and looked['voucher']['id'] == vid
    for key in ('phone', 'internal_note', 'issue_reason', 'issue_reason_detail', 'cancellation_reason'):
        assert key not in looked['voucher']
    assert rpc(cur, public, 'lookup', ('SF-ZZZZ-ZZZZ-ZZZZ',))['reason'] == 'not_found'
    assert rpc(cur, public, 'lookup', ('bad',))['reason'] == 'invalid_code'
    denied(cur, lambda: rpc(cur, public, 'redeem', (vid, False)), '22023')
    denied(cur, lambda: rpc(cur, public, 'redeem', (vid, None)), '22023')
    used = rpc(cur, public, 'redeem', (vid, True))
    assert used['ok'] and used['voucher']['used_by_name'] == 'Gerente sintético'
    assert rpc(cur, public, 'redeem', (vid, True))['reason'] == 'used'
    identity(cur, SOCIO)
    assert rpc(cur, public, 'cancel', (vid, 'Teste', True))['reason'] == 'used'
    cancelled = rpc(cur, public, 'cancel', (pct['id'], 'Teste de cancelamento', True))
    assert cancelled['ok'] and cancelled['voucher']['status'] == 'cancelled'
    identity(cur, MANAGER)
    assert rpc(cur, public, 'redeem', (pct['id'], True))['reason'] == 'cancelled'
    # Expiry boundary in Fortaleza, and an artificially expired synthetic record.
    cur.execute('reset role')
    cur.execute(f"update {private}.benefit_vouchers set expires_on=(clock_timestamp() at time zone 'America/Fortaleza')::date-1 where request_id<>%s and used_at is null and cancelled_at is null returning id", (nonce,))
    expired = str(cur.fetchone()[0])
    identity(cur, MANAGER)
    assert rpc(cur, public, 'redeem', (expired, True))['reason'] == 'expired'
    for uid in (INACTIVE, UNKNOWN):
        identity(cur, uid)
        denied(cur, lambda: rpc(cur, public, 'lookup', (code,)))
        denied(cur, lambda: rpc(cur, public, 'redeem', (vid, True)))
    identity(cur, None)
    denied(cur, lambda: rpc(cur, public, 'lookup', (code,)))
    identity(cur, MANAGER)
    for _ in range(30): result = rpc(cur, public, 'lookup', ('bad',))
    assert result['reason'] == 'rate_limited'
    cur.execute('reset role')
    cur.execute(f"select count(*) from {private}.benefit_voucher_events where voucher_id=%s and event_type='used'", (vid,))
    assert cur.fetchone()[0] == 1
    cur.execute(f"select count(*) from {private}.benefit_vouchers where request_id=%s", (nonce,))
    assert cur.fetchone()[0] == 1
    for role in ('anon', 'authenticated', 'service_role'):
        for table in ('benefit_vouchers', 'benefit_voucher_events', 'benefit_voucher_rate_limits'):
            cur.execute('select has_table_privilege(%s,%s,\'select,insert,update,delete\')', (role, private + '.' + table))
            assert not cur.fetchone()[0]
    cur.execute("select proname,has_function_privilege('anon',p.oid,'execute') from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname=%s and proname like 'benefit_voucher_%%'", (public,))
    rows = cur.fetchall(); assert len(rows) == 6 and not any(r[1] for r in rows)
    cur.execute("select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname=%s and proname like 'benefit_voucher_%%' and prosecdef", (public,))
    assert cur.fetchone()[0]==0,'Public RPC wrappers must run as invoker'
    cur.execute('set local role anon')
    denied(cur, lambda: rpc(cur, public, 'lookup', (code,)))
    cur.execute('reset role')
    return 56


def concurrency(conn, schemas, portal):
    public, private, _ = schemas
    def create():
        with conn.cursor() as cur:
            identity(cur, SOCIO)
            cur.execute('reset role'); cur.execute(f'delete from {private}.benefit_voucher_rate_limits'); identity(cur, SOCIO)
            result = issue(cur, public)['voucher']['id']
        conn.commit(); return result
    def race(operations):
        barrier = threading.Barrier(2)
        def worker(operation):
            c = connection(portal)
            try:
                with c.cursor() as cur:
                    cur.execute("set local statement_timeout='15s'")
                    identity(cur, MANAGER if operation == 'redeem' else SOCIO)
                    barrier.wait(timeout=10)
                    result = rpc(cur, public, operation, (vid, True) if operation == 'redeem' else (vid, 'Concorrência sintética', True))
                c.commit(); return result
            finally: c.rollback(); c.close()
        with ThreadPoolExecutor(2) as executor:
            results = list(executor.map(worker, operations))
        assert sum(bool(x['ok']) for x in results) == 1
        with conn.cursor() as cur:
            cur.execute('reset role')
            cur.execute(f"select count(*) from {private}.benefit_voucher_events where voucher_id=%s and event_type in ('used','cancelled')", (vid,))
            assert cur.fetchone()[0] == 1
        conn.commit()
    vid = create(); race(('redeem', 'redeem'))
    vid = create(); race(('redeem', 'cancel'))
    # Lost-response retry is idempotent even from independent concurrent issuers.
    nonce = str(uuid.uuid4()); barrier = threading.Barrier(2)
    def issuer(_):
        c = connection(portal)
        try:
            with c.cursor() as cur:
                identity(cur, SOCIO); barrier.wait(timeout=10); result = issue(cur, public, nonce=nonce)
            c.commit(); return result['voucher']['id']
        finally: c.rollback(); c.close()
    with ThreadPoolExecutor(2) as executor: ids = list(executor.map(issuer, (1, 2)))
    assert ids[0] == ids[1]
    return 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--portal-rollback', action='store_true')
    group.add_argument('--portal-concurrency', action='store_true')
    args = parser.parse_args()
    portal = args.portal_rollback or args.portal_concurrency
    suffix = uuid.uuid4().hex[:16]
    schemas = tuple(f'sirfisher_bv_{suffix}_{kind}' for kind in ('public', 'private', 'auth'))
    conn = connection(portal)
    committed = False
    try:
        with conn.cursor() as cur:
            if not portal:
                cur.execute("""do $$begin
                  if not exists(select from pg_roles where rolname='anon') then create role anon; end if;
                  if not exists(select from pg_roles where rolname='authenticated') then create role authenticated; end if;
                  if not exists(select from pg_roles where rolname='service_role') then create role service_role; end if;
                end$$; create schema if not exists extensions; create extension if not exists pgcrypto with schema extensions;""")
            cur.execute("set local statement_timeout='30s'")
            setup(cur, schemas)
            count = verify(cur, schemas)
        if args.portal_concurrency or not portal:
            conn.commit(); committed = True
            count += concurrency(conn, schemas, portal)
        print(f'BENEFIT_VOUCHERS_SQL_OK checks={count} isolated=1')
    finally:
        conn.rollback()
        if committed:
            with conn.cursor() as cur:
                for schema in reversed(schemas):
                    assert schema.startswith('sirfisher_bv_' + suffix + '_')
                    cur.execute(f'drop schema {schema} cascade')
            conn.commit()
        with conn.cursor() as cur:
            cur.execute('select count(*) from pg_namespace where nspname=any(%s)', (list(schemas),))
            assert cur.fetchone()[0] == 0, 'Isolated test schemas must not remain'
        conn.rollback(); conn.close()
        print('BENEFIT_VOUCHERS_CLEANUP_OK')


if __name__ == '__main__':
    main()
