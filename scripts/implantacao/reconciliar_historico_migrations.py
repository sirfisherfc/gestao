#!/usr/bin/env python3
"""Reconcilia supabase_migrations.schema_migrations com o catálogo local.

Contexto
--------
As migrations deste projeto foram aplicadas fora do executor do Supabase: os
objetos existem no banco, mas o histórico só registrava a cadeia do sistema de
reservas. Sem baseline, qualquer ``supabase db push`` futuro tentaria reaplicar
toda a cadeia sobre um banco que já a contém.

Este script registra as versões ausentes como já aplicadas. Ele **não executa
SQL das migrations** e não altera nenhum objeto: escreve apenas linhas de
histórico.

Segurança
---------
- Dry-run é o padrão; gravar exige ``--aplicar``.
- ``--conferir-objetos`` valida antes que os objetos criados pelas migrations
  locais existem de fato no banco. Marcar como aplicada uma migration que nunca
  rodou faria com que ela nunca mais rodasse, então a conferência é o pré-requisito.
- A gravação roda em transação única, com ``on conflict do nothing``: nenhuma
  linha existente é sobrescrita.
- ``statements`` fica nulo de propósito. É um baseline: o SQL autoritativo vive
  no repositório, e a linha existente ``20260905000000`` já seguia esse formato.

Uso
---
    python scripts/implantacao/reconciliar_historico_migrations.py
    python scripts/implantacao/reconciliar_historico_migrations.py --conferir-objetos
    python scripts/implantacao/reconciliar_historico_migrations.py --aplicar
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRACOES = ROOT / "supabase" / "migrations"
sys.path.insert(0, str(ROOT / "scripts" / "importacao"))

NOME_ARQUIVO = re.compile(r"^(\d{14})_(.+)\.sql$")

CREATE_REL = re.compile(
    r"create\s+(?:or\s+replace\s+)?"
    r"(?:materialized\s+view|view|table)\s+(?:if\s+not\s+exists\s+)?"
    r"((?:public|private)\.[a-z0-9_]+)",
    re.I,
)
CREATE_FN = re.compile(
    r"create\s+(?:or\s+replace\s+)?function\s+((?:public|private)\.[a-z0-9_]+)",
    re.I,
)
DROP_ANY = re.compile(
    r"drop\s+(?:materialized\s+view|view|table|function)\s+(?:if\s+exists\s+)?"
    r"((?:public|private)\.[a-z0-9_]+)",
    re.I,
)


def catalogo_local() -> dict[str, str]:
    """Mapeia versão -> nome, a partir dos arquivos de migration."""
    catalogo: dict[str, str] = {}
    for arquivo in sorted(MIGRACOES.glob("*.sql")):
        achado = NOME_ARQUIVO.match(arquivo.name)
        if not achado:
            raise SystemExit(f"nome de migration fora do padrão: {arquivo.name}")
        versao, nome = achado.groups()
        if versao in catalogo:
            raise SystemExit(f"versão duplicada no catálogo local: {versao}")
        catalogo[versao] = nome
    return catalogo


def objetos_esperados() -> tuple[dict[str, str], dict[str, str]]:
    """Objetos criados pelas migrations e não derrubados depois."""
    relacoes: dict[str, str] = {}
    funcoes: dict[str, str] = {}
    derrubados: dict[str, str] = {}

    for arquivo in sorted(MIGRACOES.glob("*.sql")):
        sql = arquivo.read_text(encoding="utf-8", errors="replace")
        for m in CREATE_REL.finditer(sql):
            relacoes[m.group(1).lower()] = arquivo.name
        for m in CREATE_FN.finditer(sql):
            funcoes[m.group(1).lower()] = arquivo.name
        for m in DROP_ANY.finditer(sql):
            derrubados[m.group(1).lower()] = arquivo.name

    def sobreviveu(nome: str, criado_em: str) -> bool:
        derrubado_em = derrubados.get(nome)
        return derrubado_em is None or derrubado_em < criado_em

    return (
        {n: o for n, o in relacoes.items() if sobreviveu(n, o)},
        {n: o for n, o in funcoes.items() if sobreviveu(n, o)},
    )


def conferir_objetos(cur) -> list[str]:
    """Retorna a lista de objetos esperados que não existem no banco."""
    relacoes, funcoes = objetos_esperados()
    ausentes: list[str] = []

    for nome in sorted(relacoes):
        cur.execute("select to_regclass(%s) is not null", (nome,))
        if not cur.fetchone()[0]:
            ausentes.append(f"relação {nome} (de {relacoes[nome]})")

    for nome in sorted(funcoes):
        cur.execute(
            "select exists(select 1 from pg_proc p"
            " join pg_namespace n on n.oid = p.pronamespace"
            " where n.nspname || '.' || p.proname = %s)",
            (nome,),
        )
        if not cur.fetchone()[0]:
            ausentes.append(f"função {nome} (de {funcoes[nome]})")

    print(
        f"Conferência: {len(relacoes)} relações e {len(funcoes)} funções esperadas, "
        f"{len(ausentes)} ausentes."
    )
    return ausentes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="grava as versões ausentes; sem esta flag apenas exibe o plano",
    )
    parser.add_argument(
        "--conferir-objetos",
        action="store_true",
        help="valida que os objetos das migrations existem antes de gravar",
    )
    args = parser.parse_args()

    import psycopg2

    import importacao_core

    catalogo = catalogo_local()

    conn = psycopg2.connect(
        importacao_core._database_url(),
        application_name="sirfisher_reconciliar_historico",
    )
    try:
        # Leitura do estado atual sempre em transação somente leitura.
        conn.set_session(readonly=True, autocommit=True)
        cur = conn.cursor()
        cur.execute("set statement_timeout = '30s'")
        cur.execute("select version from supabase_migrations.schema_migrations")
        registradas = {linha[0] for linha in cur.fetchall()}

        ausentes = sorted(set(catalogo) - registradas)
        orfas = sorted(registradas - set(catalogo))

        print(f"Catálogo local              : {len(catalogo)} migrations")
        print(f"Histórico no banco          : {len(registradas)} versões")
        print(f"Ausentes no histórico       : {len(ausentes)}")
        print(f"No histórico sem arquivo    : {len(orfas)}")
        if orfas:
            print(f"  {', '.join(orfas)}")
            print("  (não são tocadas por este script)")

        if not ausentes:
            print("\nHistórico já reconciliado; nada a fazer.")
            return 0

        print(f"\nPrimeira ausente: {ausentes[0]}   última: {ausentes[-1]}")

        if args.conferir_objetos or args.aplicar:
            faltando = conferir_objetos(cur)
            if faltando:
                print("\nABORTADO: objetos abaixo não existem no banco.")
                for item in faltando[:20]:
                    print(f"   {item}")
                print(
                    "\nMarcar essas migrations como aplicadas faria com que nunca "
                    "mais rodassem. Investigue antes de reconciliar."
                )
                return 1

        if not args.aplicar:
            print("\nDry-run. Linhas que seriam inseridas (amostra de 5):")
            for versao in ausentes[:5]:
                print(f"   {versao} | {catalogo[versao]}")
            print(f"   ... e mais {max(0, len(ausentes) - 5)}")
            print("\nUse --aplicar para gravar.")
            return 0

        # Gravação: transação única, sem sobrescrever nada.
        conn.set_session(readonly=False, autocommit=False)
        with conn.cursor() as escrita:
            escrita.executemany(
                "insert into supabase_migrations.schema_migrations (version, name)"
                " values (%s, %s) on conflict (version) do nothing",
                [(versao, catalogo[versao]) for versao in ausentes],
            )
            inseridas = escrita.rowcount
            escrita.execute(
                "select count(*) from supabase_migrations.schema_migrations"
            )
            total = escrita.fetchone()[0]
        conn.commit()

        print(f"\nInseridas {len(ausentes)} versões (rowcount {inseridas}).")
        print(f"Histórico agora com {total} versões.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
