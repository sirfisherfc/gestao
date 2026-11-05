#!/usr/bin/env python3
"""Rehearse or apply only the voucher migration; never prints identities/secrets."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/importacao'))
from stone_fechamento import conectar

VERSION='20261104200024'
NAME='benefit_vouchers'
VERSIONS=[(VERSION,NAME),('20261104202352','benefit_voucher_private_rpc'),('20261104203828','benefit_voucher_award_reason'),('20261104205451','benefit_voucher_edit'),('20261105130459','benefit_voucher_short_codes')]


def identity(cur,uid):
    cur.execute('set local role authenticated')
    cur.execute("select set_config('request.jwt.claims',%s,true)",(json.dumps({'sub':str(uid),'role':'authenticated'}),))


def verify(cur):
    # The savepoint guarantees no test voucher/rate counter survives even when
    # the migration itself is committed afterwards.
    cur.execute('savepoint voucher_verification')
    cur.execute("select user_id from public.perfil_usuario where ativo and papel='socio' limit 1")
    socio=cur.fetchone(); assert socio,'Missing active partner profile'
    cur.execute("select auth_user_id from public.app_users where active and role in ('admin','operator') and auth_user_id is not null limit 1")
    staff=cur.fetchone(); assert staff,'Missing linked active reservation staff'
    identity(cur,socio[0])
    cur.execute("select public.benefit_voucher_issue(%s,'TESTE TÉCNICO TRANSACIONAL','85999990000','percent',12.5,(clock_timestamp() at time zone 'America/Fortaleza')::date,'award','Teste com rollback obrigatório','Privado')",(str(uuid.uuid4()),))
    result=cur.fetchone()[0]; assert result['ok']; voucher=result['voucher']
    assert len(voucher['code'])==6 and not voucher['code'].startswith('SF-')
    assert voucher['issue_reason']=='award'
    cur.execute("select public.benefit_voucher_list(%s,'',0,10,'award')",(voucher['code'],))
    result=cur.fetchone()[0]; assert result['ok'] and result['total']==1
    cur.execute("select public.benefit_voucher_edit(%s,%s,'TESTE CORRIGIDO','85999990000','percent',15,%s,'award','Teste com rollback obrigatório','Privado')",(voucher['id'],voucher['revision'],voucher['expires_on']))
    result=cur.fetchone()[0];assert result['ok'] and result['voucher']['revision']==2
    assert result['voucher']['code']==voucher['code'];voucher=result['voucher']
    identity(cur,staff[0])
    cur.execute('select public.benefit_voucher_lookup(%s)',(voucher['code'],))
    result=cur.fetchone()[0]; assert result['ok']
    assert not {'phone','internal_note','issue_reason','issue_reason_detail'} & result['voucher'].keys()
    cur.execute('select public.benefit_voucher_lookup(%s)',(voucher['legacy_code'],))
    result=cur.fetchone()[0];assert result['ok'] and result['voucher']['short_code']==voucher['code']
    cur.execute('select public.benefit_voucher_redeem(%s,true)',(voucher['id'],))
    assert cur.fetchone()[0]['reason']=='changed'
    cur.execute('select public.benefit_voucher_redeem(%s,true,%s)',(voucher['id'],voucher['revision']))
    result=cur.fetchone()[0]; assert result['ok'] and result['voucher']['status']=='used'
    cur.execute('select public.benefit_voucher_redeem(%s,true,%s)',(voucher['id'],voucher['revision']))
    assert cur.fetchone()[0]['reason']=='used'
    cur.execute('reset role')
    cur.execute("select count(*) from private.benefit_voucher_events where voucher_id=%s and event_type='used'",(voucher['id'],))
    assert cur.fetchone()[0]==1
    cur.execute('rollback to savepoint voucher_verification')
    cur.execute('release savepoint voucher_verification')
    cur.execute('reset role')
    cur.execute("select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname like 'benefit_voucher_%%' and has_function_privilege('anon',p.oid,'execute')")
    assert cur.fetchone()[0]==0
    cur.execute("select count(*) from private.benefit_vouchers where id=%s",(voucher['id'],))
    assert cur.fetchone()[0]==0,'Transactional fixture survived rollback'
    print('VOUCHER_REAL_ROLE_VERIFICATION_OK fixture_rollback=1')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar',action='store_true')
    args=parser.parse_args()
    conn=conectar()
    try:
        with conn.cursor() as cur:
            cur.execute("set local statement_timeout='60s'")
            pending=[]
            for version,name in VERSIONS:
                sql=(ROOT/f'supabase/migrations/{version}_{name}.sql').read_text(encoding='utf8').strip()
                assert sql.startswith('begin;') and sql.endswith('commit;')
                cur.execute('select version from supabase_migrations.schema_migrations where version=%s',(version,))
                if cur.fetchone() is None:
                    cur.execute(sql[len('begin;'):-len('commit;')]);pending.append((version,name,sql))
            verify(cur)
            if args.aplicar:
                for version,name,sql in pending:
                    cur.execute('insert into supabase_migrations.schema_migrations(version,name,statements) values(%s,%s,%s)',(version,name,[sql]))
        if args.aplicar:
            conn.commit();print('VOUCHER_MIGRATIONS_APPLIED_OK '+','.join(v for v,_ in VERSIONS)+' new='+str(len(pending)))
        else:
            conn.rollback();print('VOUCHER_MIGRATION_REHEARSAL_OK rollback=1')
    finally:
        conn.rollback();conn.close()


if __name__=='__main__': main()
