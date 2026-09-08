#!/usr/bin/env python3
"""Testa SQL real da importacao e reparo de sequencias em banco descartavel.

Sem argumentos, usa psql e PGHOST/PGDATABASE/PGUSER (somente localhost e banco
sirfisher_outbox_test). --write-sql permite executar a mesma fixture em outro
PostgreSQL isolado. Nao conecta ao Supabase nem le configuracao do projeto.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / 'supabase/migrations'
OUTBOX = '20260905000000_importacao_recalculo_duravel.sql'
SEQUENCE_REPAIR = '20260908000000_repara_sequencias_pos_migracao.sql'


def read(name: str) -> str:
    return (MIGRATIONS / name).read_text(encoding='utf-8-sig')


def build_sql() -> str:
    # Detecta mudanca posterior dos objetos cobertos: nao aprovar apenas uma
    # definicao historica se a cadeia efetiva passar a ter outra versao.
    for path in sorted(MIGRATIONS.glob('*.sql')):
        if path.name > OUTBOX and any(name in path.read_text(encoding='utf-8-sig') for name in (
            'importar_csv_stone', 'processar_fila_recalculo_saldo', 'garantir_worker_recalculo_saldo'
        )):
            raise AssertionError('Atualizar a fixture com a migration posterior: ' + path.name)
    parsers = read('20260751000000_importacao_web_stone.sql')
    parsers = parsers[parsers.index('create or replace function private.campo_csv'):]
    parsers = parsers[:parsers.index('create or replace function private.parse_stone_vendas')]
    fila = read('20260758000000_recalculo_saldo_assincrono.sql')
    fila = fila[fila.index('create table if not exists private.fila_recalculo_saldo'):]
    fila = fila[:fila.index('-- Mesmo nome e assinatura')]
    worker = read('20260808000000_conciliacao_estorno_assincrona.sql')
    worker = worker[worker.index('create or replace function private.processar_fila_recalculo_saldo'):]
    worker = worker[:worker.index('do $migration$')]
    fixture = (ROOT / 'scripts/ci/fixtures/importacao_outbox.sql').read_text(encoding='utf-8')
    setup, checks = fixture.split('-- TESTES APOS INSTALAR A CADEIA', 1)
    raw = """
create table public.raw_stone_extrato as
select p.*, null::smallint conta_id, null::text data_hora_raw, null::text origem_carga
from private.parse_stone_extrato('[]') p;
alter table public.raw_stone_extrato add unique (dedup_hash);
alter table private.fila_recalculo_saldo
  add column somente_refresh boolean not null default false;
"""
    migration = read(OUTBOX)
    return '\n'.join([
        setup, parsers, fila, raw, worker,
        read('20260784000000_importacao_web_protecoes_do_python.sql'),
        read('20260818050000_importacao_web_usa_fontes.sql'),
        # Rodar duas vezes valida idempotencia pelo catalogo efetivo.
        migration, migration, checks,
    ])


def build_sequence_repair_sql() -> str:
    """Exercita a reparacao em PostgreSQL real, sem dados do projeto."""
    migration = read(SEQUENCE_REPAIR)
    return '\n'.join([
        """
create table public.venda_especie (
  id bigint generated always as identity primary key,
  descricao text not null default 'sintetico'
);
create table public.conta_recorrente_pagamento (
  id bigint generated always as identity primary key,
  descricao text not null default 'sintetico'
);
create table public.outra_tabela_serial (
  id bigserial primary key,
  descricao text not null default 'sintetico'
);
create table public.tabela_vazia (
  id bigint generated always as identity primary key
);
create schema if not exists private;
create table private.fila_operacional (
  id bigint generated always as identity primary key,
  descricao text not null default 'sintetico'
);

-- Simula uma restauracao que preservou IDs, mas nao avancou as sequencias.
insert into public.venda_especie (id) overriding system value values (41);
insert into public.conta_recorrente_pagamento (id) overriding system value values (84);
insert into public.outra_tabela_serial (id) values (13);
insert into private.fila_operacional (id) overriding system value values (25);
""",
        # A segunda execucao garante que a migration seja reexecutavel.
        migration,
        migration,
        """
insert into public.venda_especie default values;
insert into public.conta_recorrente_pagamento default values;
insert into public.outra_tabela_serial default values;
insert into public.tabela_vazia default values;
insert into private.fila_operacional default values;

do $$
begin
  assert exists (select 1 from public.venda_especie where id = 42),
    'Sequencia de venda_especie nao foi reparada';
  assert exists (select 1 from public.conta_recorrente_pagamento where id = 85),
    'Sequencia de conta_recorrente_pagamento nao foi reparada';
  assert exists (select 1 from public.outra_tabela_serial where id = 14),
    'Sequencia serial fora das tabelas conhecidas nao foi reparada';
  assert exists (select 1 from public.tabela_vazia where id = 1),
    'Sequencia de tabela vazia nao preservou o primeiro ID';
  assert exists (select 1 from private.fila_operacional where id = 26),
    'Sequencia de tabela tecnica privada nao foi reparada';
end;
$$;
""",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-sql', type=Path)
    args = parser.parse_args()
    sql = build_sql()
    if args.write_sql:
        args.write_sql.write_text(sql, encoding='utf-8')
        print('OUTBOX_FIXTURE_GENERATED')
        return
    if os.environ.get('PGHOST') not in {'localhost', '127.0.0.1', '::1'}:
        raise SystemExit('Teste permitido somente com PGHOST local explicito.')
    if os.environ.get('PGDATABASE') != 'sirfisher_outbox_test':
        raise SystemExit('Use o banco descartavel sirfisher_outbox_test.')
    with tempfile.TemporaryDirectory(prefix='sirfisher-outbox-') as tmp:
        target = Path(tmp) / 'fixture.sql'
        target.write_text(sql, encoding='utf-8')
        result = subprocess.run(['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1', '-f', str(target)],
                                capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            # Fixtures sao sinteticas; nao imprimir consultas/valores em erros.
            raise AssertionError('OUTBOX_SQL_FAILED: ' + '\n'.join(
                line for line in result.stderr.splitlines() if 'ERROR:' in line))
        sequence_target = Path(tmp) / 'sequence-repair.sql'
        sequence_target.write_text(build_sequence_repair_sql(), encoding='utf-8')
        sequence_result = subprocess.run(
            ['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1', '-f', str(sequence_target)],
            capture_output=True, text=True, encoding='utf-8'
        )
        if sequence_result.returncode:
            raise AssertionError('SEQUENCE_REPAIR_SQL_FAILED: ' + '\n'.join(
                line for line in sequence_result.stderr.splitlines() if 'ERROR:' in line))
    print('OUTBOX_SQL_OK: atomicidade, dedup, dry-run, rollback, watchdog, grants, idempotencia e sequencias')


if __name__ == '__main__':
    main()
