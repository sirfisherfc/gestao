#!/usr/bin/env python3
"""Transações reais de baixas em tabelas temporárias e banco descartável."""
from dataclasses import replace
from datetime import timedelta
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_stone_fechamento import b, XML, DIA

ROOT=Path(__file__).resolve().parents[2]
MIGRATION=ROOT/'supabase/migrations/20261022200001_stone_fechamento_e_baixas.sql'


def verificar(cur):
    # Nomes temporários escondem as tabelas reais SOMENTE nesta sessão.
    # Pode também ser usado no ensaio de migration com ROLLBACK no portal.
    cur.execute('set local search_path=pg_temp,public')
    cur.execute('''create temp table stone_conta(stonecode text,ativa boolean,entra_faturamento boolean) on commit drop;
      create temp table fonte_financeira(chave text,ativa boolean,conta_id integer) on commit drop;
      create temp table raw_stone_recebiveis(conta_id integer,stonecode text,stone_id text,n_parcela integer,categoria text,
        valor_bruto numeric(16,6),valor_liquido numeric(16,6),ultimo_status text,data_ultimo_status timestamp,
        data_vencimento date,data_vencimento_original date,unique(stone_id,n_parcela,categoria)) on commit drop;
      insert into stone_conta values ('123',true,true);
      insert into fonte_financeira values ('stone_recebiveis',true,1);''')
    cur.execute("select c.relnamespace::regnamespace::text from pg_class c where c.oid='raw_stone_recebiveis'::regclass")
    assert cur.fetchone()[0].startswith('pg_temp_'), 'recusado: fixture precisa estar em tabela temporária'
    e=b.ler_baixas(XML,'123',DIA)[0]
    def inserir(chave):
        cur.execute("insert into raw_stone_recebiveis values(1,'123',%s,1,'Venda',10,9.812345,'Aberto',null,%s,%s)",
                    (chave,DIA+timedelta(days=1),DIA+timedelta(days=1)))
    inserir('0001')
    primeiro=b.processar(cur,[e]);assert primeiro['atualizadas']==1 and primeiro['pendentes']==0
    segundo=b.processar(cur,[e]);assert segundo['atualizadas']==0 and segundo['pendentes']==0
    cur.execute('select count(*),min(antes->>\'ultimo_status\') from private.stone_baixa_evento where chave=%s',(e.chave,))
    assert cur.fetchone()==(1,'Aberto'), 'auditoria original deve ser preservada'
    cur.execute('select ultimo_status,data_vencimento,valor_liquido from raw_stone_recebiveis where stone_id=%s',('0001',))
    row=cur.fetchone();assert row[0]=='Pago' and row[1]==DIA and str(row[2])=='9.812345'
    velho=replace(e,pagamento_id='arquivo-antigo',referencia=DIA-timedelta(days=1),pagamento=DIA-timedelta(days=1))
    assert b.processar(cur,[velho])['obsoletas']==1
    conflito=replace(e,liquido=e.liquido-1)
    assert b.processar(cur,[conflito])['pendentes']==1
    assert b.processar(cur,[e])['pendentes']==1, 'conflito não se resolve sozinho com outro replay'
    cur.execute('select estado,conflito from private.stone_baixa_evento where chave=%s and referencia=%s',(e.chave,e.referencia))
    assert cur.fetchone()==('aplicado',True), 'manter watermark mesmo com conflito'
    ausente=replace(e,stone_id='0002')
    assert b.processar(cur,[ausente])['pendentes']==1
    inserir('0002')
    assert b.processar(cur,[ausente])['atualizadas']==1
    cur.execute('select antes->>\'ultimo_status\' from private.stone_baixa_evento where chave=%s',(ausente.chave,))
    assert cur.fetchone()[0]=='Aberto'
    inserir('0003')
    terceiro=replace(e,stone_id='0003')
    cur.execute('savepoint falha_apos_baixa')
    assert b.processar(cur,[terceiro])['atualizadas']==1
    cur.execute('rollback to savepoint falha_apos_baixa')
    cur.execute("select ultimo_status from raw_stone_recebiveis where stone_id='0003'")
    assert cur.fetchone()[0]=='Aberto'
    cur.execute('select count(*) from private.stone_baixa_evento where chave=%s',(terceiro.chave,))
    assert cur.fetchone()[0]==0
    return 8


def main():
    if os.environ.get('STONE_SQL_DISPOSABLE')!='1' or os.environ.get('PGDATABASE')!='sirfisher_stone_test' or os.environ.get('PGHOST')!='127.0.0.1':
        raise SystemExit('Teste SQL exige PostgreSQL local descartável explícito')
    import psycopg2
    conn=psycopg2.connect('')
    try:
        with conn,conn.cursor() as cur:
            cur.execute('''create schema if not exists private;
            do $$begin
              if not exists(select from pg_roles where rolname='anon') then create role anon; end if;
              if not exists(select from pg_roles where rolname='authenticated') then create role authenticated; end if;
              if not exists(select from pg_roles where rolname='service_role') then create role service_role; end if;
            end$$;
            create table stone_conta(stonecode text,ativa boolean,entra_faturamento boolean);
            create table stone_pix_arquivo(id uuid primary key);
            create function usuario_tem_papel(text[]) returns boolean language sql as $$select false$$;''')
        sql=MIGRATION.read_text(encoding='utf-8-sig').strip()
        assert sql.startswith('begin;') and sql.endswith('commit;')
        # A conexão controla o commit. Executar COMMIT dentro da string deixa
        # o estado do psycopg diferente do servidor e derruba as tabelas temp.
        with conn,conn.cursor() as cur:
            cur.execute(sql[len('begin;'):-len('commit;')])
        with conn,conn.cursor() as cur:
            casos=verificar(cur)
        print(f'STONE_BAIXAS_SQL_OK cases={casos} production=0')
    finally: conn.close()


if __name__=='__main__': main()
