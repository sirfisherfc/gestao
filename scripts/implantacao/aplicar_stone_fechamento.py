#!/usr/bin/env python3
"""Ensaia com rollback ou aplica somente a migration do fechamento Stone."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/importacao'))
from api_cliente import carregar_env
from importacao_core import executar_com_saida,ErroOperacional
from stone_fechamento import conectar

VERSAO='20261022200001'
NOME='stone_fechamento_e_baixas'


def fluxo():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--aplicar',action='store_true')
    p.add_argument('--env',type=Path,help='arquivo privado opcional; ambiente existente tem precedência')
    p.add_argument('--conferir-dia',type=date.fromisoformat,help='apenas comparar liquidações reais no ensaio, sem aplicar baixas')
    p.add_argument('--pasta',type=Path,help='cache privado dos XML para a conferência opcional')
    op=p.parse_args()
    if op.env:
        from dotenv import load_dotenv
        load_dotenv(op.env)
    carregar_env()
    sql=(ROOT/f'supabase/migrations/{VERSAO}_{NOME}.sql').read_text(encoding='utf-8-sig').strip()
    if not sql.startswith('begin;') or not sql.endswith('commit;'):
        raise ErroOperacional('migration precisa de fronteira transacional conhecida')
    body=sql[len('begin;'):-len('commit;')]
    conn=conectar()
    try:
        with conn.cursor() as cur:
            cur.execute("set local statement_timeout='90s'")
            cur.execute(body)
            if op.aplicar:
                cur.execute('insert into supabase_migrations.schema_migrations(version,name,statements) values(%s,%s,%s) on conflict(version) do nothing',
                            (VERSAO,NOME,[sql]))
                conn.commit()
                print('STONE_FECHAMENTO_MIGRATION_OK '+VERSAO)
            else:
                sys.path.insert(0,str(ROOT/'scripts/ci'))
                from test_stone_baixas_sql import verificar
                casos=verificar(cur)
                print('STONE_FECHAMENTO_SQL_ROLLBACK_OK '+str(casos))
                cur.execute("select has_table_privilege('anon','public.app_stone_fechamento','select'),"
                            "has_table_privilege('authenticated','public.app_stone_fechamento','select'),"
                            "has_table_privilege('authenticated','private.stone_baixa_evento','select')")
                assert cur.fetchone()==(False,True,False), 'grants precisam preservar dados privados'
                print('STONE_FECHAMENTO_GRANTS_OK')
                if op.conferir_dia:
                    if not op.pasta:
                        raise ErroOperacional('--conferir-dia precisa do cache privado em --pasta')
                    import api_stone_baixas as b
                    cur.execute('set local search_path=public,pg_catalog,pg_temp')
                    cur.execute("select stonecode from public.stone_conta where ativa and entra_faturamento and stonecode <> '173835323'")
                    codigos=[str(r[0]) for r in cur.fetchall()]
                    eventos=[]
                    for codigo in codigos:
                        eventos.extend(b.ler_baixas((op.pasta/codigo/f'{op.conferir_dia}.xml').read_bytes(),codigo,op.conferir_dia))
                    print('STONE_BAIXAS_REAL_DRY_RUN '+json.dumps(b.processar(cur,eventos,dry_run=True)))
    finally:
        conn.rollback();conn.close()


if __name__=='__main__': sys.exit(executar_com_saida(fluxo))
