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
from datetime import timedelta
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
EDIT = ROOT / 'supabase/migrations/20261104205451_benefit_voucher_edit.sql'
SHORT_CODES = ROOT / 'supabase/migrations/20261105130459_benefit_voucher_short_codes.sql'
RECENT = ROOT / 'supabase/migrations/20261105141504_benefit_voucher_recent.sql'
RENEW = ROOT / 'supabase/migrations/20261105145812_benefit_voucher_renew.sql'
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
    edit_sql=EDIT.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    edit_sql=edit_sql.replace('private.',private+'.').replace('public.',public+'.').replace('auth.uid()',auth+'.uid()::uuid')
    cur.execute(edit_sql)
    cur.execute(edit_sql)
    # Existing vouchers get an alias without changing the old code or beneficiary.
    cur.execute(f"""insert into {private}.benefit_vouchers(request_id,code,beneficiary_name,phone,benefit_type,benefit_value,
      expires_on,issue_reason,conditions,issued_by,issued_by_name)
      values(%s,'0123456789AB','Legacy fixture','85999990000','percent',1,'2000-01-01','friend',array['Uso único.'],%s,'Ator sintético')""",(str(uuid.uuid4()),SOCIO))
    short_sql=SHORT_CODES.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    short_sql=short_sql.replace('private.',private+'.').replace('public.',public+'.').replace('auth.uid()',auth+'.uid()::uuid')
    short_sql=short_sql.replace('extensions.gen_random_bytes(',auth+'.gen_bytes(')
    cur.execute(short_sql)
    cur.execute(short_sql)
    cur.execute(f"select code,beneficiary_name,length(short_code) from {private}.benefit_vouchers where code='0123456789AB'")
    assert cur.fetchone()==('0123456789AB','Legacy fixture',6)
    recent_sql=RECENT.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    recent_sql=recent_sql.replace('private.',private+'.').replace('public.',public+'.')
    cur.execute(recent_sql)
    cur.execute(recent_sql)
    renew_sql=RENEW.read_text(encoding='utf8').strip()[len('begin;'):-len('commit;')]
    renew_sql=renew_sql.replace('private.',private+'.').replace('public.',public+'.').replace('auth.uid()',auth+'.uid()::uuid')
    cur.execute(renew_sql)
    cur.execute(renew_sql)


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


def edit(cur, public, voucher, **changes):
    data={key:voucher.get(key) for key in ('beneficiary_name','phone','benefit_type','benefit_value','expires_on','issue_reason','issue_reason_detail','internal_note')}
    data.update(changes)
    return rpc(cur,public,'edit',(voucher['id'],voucher['revision'],*(data[key] for key in
      ('beneficiary_name','phone','benefit_type','benefit_value','expires_on','issue_reason','issue_reason_detail','internal_note'))))


def verify(cur, schemas):
    public, private, _ = schemas
    identity(cur, SOCIO)
    nonce = str(uuid.uuid4())
    created = issue(cur, public, nonce=nonce)
    assert created['ok']
    v = created['voucher']; vid = v['id']; code = v['code']
    assert re.fullmatch(r'[0-9A-HJKMNP-TV-Z]{6}', code)
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
    assert rpc(cur, public, 'list', (v['legacy_code'], '', 0, 50, ''))['total'] == 1
    assert rpc(cur, public, 'list', ('', '', 0, 50, 'other'))['total'] == 1
    awards=rpc(cur, public, 'list', ('', '', 0, 50, 'award'))
    assert awards['total']==1 and awards['rows'][0]['issue_reason']=='award'
    cur.execute("select set_config('bv_test.crypto','zero',true)")
    assert issue(cur, public)['voucher']['code'] == '000000'
    denied(cur, lambda: issue(cur, public), 'P0001')
    cur.execute("select set_config('bv_test.crypto','once',true)")
    assert issue(cur, public)['voucher']['code'] != '000000'
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
    legacy=rpc(cur,public,'lookup',(v['legacy_code'],))
    assert legacy['ok'] and legacy['voucher']['id']==vid and legacy['voucher']['short_code']==code
    assert legacy['voucher']['code']==v['legacy_code']
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
    rows = cur.fetchall(); assert len(rows) == 9 and not any(r[1] for r in rows)
    cur.execute("select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname=%s and proname like 'benefit_voucher_%%' and prosecdef", (public,))
    assert cur.fetchone()[0]==0,'Public RPC wrappers must run as invoker'
    cur.execute('set local role anon')
    denied(cur, lambda: rpc(cur, public, 'lookup', (code,)))
    cur.execute('reset role')
    return 56


def verify_edit(cur,schemas):
    public,private,_=schemas
    cur.execute('reset role');cur.execute(f'delete from {private}.benefit_voucher_rate_limits');identity(cur,SOCIO)
    original=issue(cur,public)['voucher'];assert original['revision']==1
    assert edit(cur,public,original)['unchanged']
    assert edit(cur,public,{**original,'revision':99},benefit_value=300)['reason']=='changed'
    changed=edit(cur,public,original,beneficiary_name='Nome corrigido',phone='85988880000',benefit_type='percent',benefit_value=17.5,issue_reason='award')['voucher']
    assert changed['revision']==2 and changed['code']==original['code'] and changed['created_at']==original['created_at']
    assert changed['issued_by_name']==original['issued_by_name'] and changed['benefit_value']==17.5
    assert 'conta inteira' in changed['conditions'][0]
    assert edit(cur,public,original,benefit_value=300)['reason']=='changed'  # Lost-response retry never writes twice.
    details=rpc(cur,public,'detail',(original['id'],))
    edits=[e for e in details['events'] if e['event_type']=='edited'];assert len(edits)==1
    assert edits[0]['changes']['before']['beneficiary_name']==original['beneficiary_name']
    assert edits[0]['changes']['after']['phone']=='85988880000'
    assert details['events'][0]['reason']=='friend'  # Historical reason remains original.
    for uid in (MANAGER,UNKNOWN,INACTIVE):
        identity(cur,uid);denied(cur,lambda:edit(cur,public,changed,benefit_value=20))
    identity(cur,MANAGER)
    looked=rpc(cur,public,'lookup',(original['code'],))['voucher'];assert looked['revision']==2
    assert not {'changes','phone','issue_reason','internal_note'} & looked.keys()
    assert rpc(cur,public,'redeem',(original['id'],True))['reason']=='changed'
    assert rpc(cur,public,'redeem',(original['id'],True,1))['reason']=='changed'
    assert rpc(cur,public,'redeem',(original['id'],True,2))['ok']
    identity(cur,SOCIO)
    assert edit(cur,public,changed,benefit_value=20)['reason']=='used'
    available=issue(cur,public)['voucher']
    for value in (0,-1,101,'NaN','Infinity',1.001):denied(cur,lambda value=value:edit(cur,public,available,benefit_type='percent',benefit_value=value),'22023')
    denied(cur,lambda:edit(cur,public,available,issue_reason='other',issue_reason_detail=None),'22023')
    denied(cur,lambda:edit(cur,public,available,expires_on='2000-01-01'),'22023')
    percentage=edit(cur,public,available,benefit_type='percent',benefit_value=15)['voucher']
    fixed=edit(cur,public,percentage,benefit_type='fixed',benefit_value=50)['voucher']
    assert len(fixed['conditions'])==3 and fixed['revision']==3
    assert rpc(cur,public,'cancel',(fixed['id'],'Teste',True))['ok']
    assert edit(cur,public,fixed,benefit_value=30)['reason']=='cancelled'
    expired=issue(cur,public)['voucher']
    cur.execute('reset role');cur.execute(f"update {private}.benefit_vouchers set expires_on='2000-01-01' where id=%s",(expired['id'],));identity(cur,SOCIO)
    expired=rpc(cur,public,'detail',(expired['id'],))['voucher']
    denied(cur,lambda:edit(cur,public,expired),'22023')
    renewal_date=available['expires_on']
    identity(cur,MANAGER);denied(cur,lambda:edit(cur,public,expired,expires_on=renewal_date))
    identity(cur,SOCIO)
    renewed=edit(cur,public,expired,expires_on=renewal_date)['voucher']
    assert renewed['status']=='available' and renewed['revision']==expired['revision']+1
    assert all(renewed[key]==expired[key] for key in ('id','code','legacy_code','created_at','issued_by_name','benefit_type','benefit_value','phone'))
    audit=rpc(cur,public,'detail',(expired['id'],))['events'][-1]
    assert audit['reason']=='Renovação de validade'
    assert audit['changes']['before']['expires_on']=='2000-01-01' and audit['changes']['after']['expires_on']==renewal_date
    assert edit(cur,public,expired,expires_on=renewal_date)['reason']=='changed'
    identity(cur,MANAGER)
    assert rpc(cur,public,'lookup',(expired['code'],))['voucher']['status']=='available'
    assert rpc(cur,public,'redeem',(expired['id'],True,expired['revision']))['reason']=='changed'
    assert rpc(cur,public,'redeem',(expired['id'],True,renewed['revision']))['ok']
    identity(cur,SOCIO);assert edit(cur,public,renewed,expires_on=renewal_date)['reason']=='used'
    # An audit failure must roll back the edited fields as well.
    atomic=issue(cur,public)['voucher'];cur.execute('reset role')
    cur.execute(f"""create function {private}.reject_edit_event() returns trigger language plpgsql as $$begin
      if new.event_type='edited' then raise exception 'Synthetic audit failure'; end if;return new;end$$;
      create trigger reject_edit_event before insert on {private}.benefit_voucher_events for each row execute function {private}.reject_edit_event();""")
    identity(cur,SOCIO);denied(cur,lambda:edit(cur,public,atomic,benefit_value=300),'P0001')
    assert rpc(cur,public,'detail',(atomic['id'],))['voucher']['revision']==1
    cur.execute('reset role');cur.execute(f'drop trigger reject_edit_event on {private}.benefit_voucher_events')
    return 30


def verify_recent(cur,schemas):
    public,private,_=schemas
    cur.execute('reset role')
    cur.execute("select ((clock_timestamp() at time zone 'America/Fortaleza')::date-2)::timestamp at time zone 'America/Fortaleza', (clock_timestamp() at time zone 'America/Fortaleza')::date,clock_timestamp()")
    start,today,now=cur.fetchone()
    # All fixtures and this history shift belong exclusively to the isolated schema.
    cur.execute(f'update {private}.benefit_vouchers set used_at=%s where used_at is not null',(start-timedelta(days=1),))
    cur.execute(f'delete from {private}.benefit_voucher_rate_limits')
    vouchers=[]
    for used in (start,start-timedelta(microseconds=1),now-timedelta(seconds=1),start+timedelta(days=1,hours=12),now+timedelta(days=1)):
        identity(cur,SOCIO);v=issue(cur,public)['voucher'];vouchers.append(v)
        cur.execute('reset role')
        cur.execute(f'update {private}.benefit_vouchers set used_at=%s,used_by=%s,used_by_name=%s where id=%s',(used,MANAGER,'Equipe sintética',v['id']))
    cur.execute("set local timezone='Pacific/Auckland'")
    for uid in (SOCIO,ADMIN,INACTIVE,UNKNOWN,None):
        identity(cur,uid);denied(cur,lambda:rpc(cur,public,'recent',(0,20)))
    identity(cur,MANAGER)
    result=rpc(cur,public,'recent',(0,20));assert result['ok'] and result['total']==3
    assert result['from_date']==(today-timedelta(days=2)).isoformat() and result['through_date']==today.isoformat()
    assert [item['code'] for item in result['items']]==[vouchers[i]['code'] for i in (2,3,0)]
    assert all(set(item)=={'code','beneficiary_name','benefit_type','benefit_value','used_at','used_by_name'} for item in result['items'])
    assert rpc(cur,public,'recent',(1,1))['items'][0]['code']==vouchers[3]['code']
    assert rpc(cur,public,'recent',(100,20))['items']==[]
    for params in ((-1,20),(None,20),(0,0),(0,101),(0,None)):
        denied(cur,lambda params=params:rpc(cur,public,'recent',params),'22023')
    cur.execute('reset role')
    cur.execute(f"insert into {public}.app_users values(%s,'Admin sintético','admin',true)",(ADMIN,))
    identity(cur,ADMIN);assert rpc(cur,public,'recent',(0,20))['total']==3
    identity(cur,None,'anon');denied(cur,lambda:rpc(cur,public,'recent',(0,20)))
    identity(cur,MANAGER)
    for _ in range(61):last=rpc(cur,public,'recent',(0,20))
    assert last=={'ok':False,'reason':'rate_limited'}
    cur.execute('reset role');cur.execute("set local timezone='UTC'")
    return 16


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
    def edit_race(operations):
        vid=create()
        with conn.cursor() as cur:
            identity(cur,SOCIO);snapshot=rpc(cur,public,'detail',(vid,))['voucher']
        conn.commit();barrier=threading.Barrier(2)
        def worker(pair):
            index,operation=pair;c=connection(portal)
            try:
                with c.cursor() as cur:
                    cur.execute("set local statement_timeout='15s'");identity(cur,MANAGER if operation=='redeem' else SOCIO)
                    barrier.wait(timeout=10)
                    result=edit(cur,public,snapshot,benefit_value=310+index*10) if operation=='edit' else rpc(cur,public,'redeem',(vid,True,1))
                c.commit();return result
            finally:c.rollback();c.close()
        with ThreadPoolExecutor(2) as executor:results=list(executor.map(worker,enumerate(operations)))
        assert sum(bool(r['ok']) for r in results)==1
        with conn.cursor() as cur:
            cur.execute('reset role');cur.execute(f"select count(*) from {private}.benefit_voucher_events where voucher_id=%s and event_type in ('edited','used')",(vid,));assert cur.fetchone()[0]==1
        conn.commit()
    edit_race(('edit','edit'));edit_race(('edit','redeem'))
    return 5


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
            count += verify_edit(cur,schemas)
            count += verify_recent(cur,schemas)
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
