#!/usr/bin/env python3
"""Aplica as migrations que ainda não constam do histórico do Supabase.

Faz o que ``supabase db push`` faria, sem depender da CLI: executa cada arquivo
pendente em ordem de versão e registra a versão no mesmo passo.

Segurança
---------
- Dry-run é o padrão; executar exige ``--aplicar``.
- Cada migration roda na própria transação, junto com o registro no histórico:
  ou a migration inteira vale e fica registrada, ou nada dela permanece. Não
  existe estado intermediário em que o SQL rodou mas o histórico não sabe.
- Para na primeira falha, sem tentar as seguintes.
- Só considera versões ausentes do histórico, então rodar de novo é inofensivo.
- ``begin;`` e ``commit;`` do arquivo são removidos porque a transação é
  controlada aqui; qualquer outro ``commit`` no meio do arquivo é recusado, já
  que quebraria a atomicidade.

Uso
---
    python scripts/implantacao/aplicar_migrations_pendentes.py
    python scripts/implantacao/aplicar_migrations_pendentes.py --aplicar
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
BEGIN_INICIAL = re.compile(r"\A\s*begin\s*;", re.I)
COMMIT_FINAL = re.compile(r"commit\s*;\s*\Z", re.I)
COMMIT_QUALQUER = re.compile(r"^\s*commit\s*;", re.I | re.M)


def preparar_sql(caminho: Path) -> str:
    """Devolve o corpo da migration sem o begin/commit externos."""
    sql = caminho.read_text(encoding="utf-8")

    corpo = BEGIN_INICIAL.sub("", sql, count=1)
    corpo = COMMIT_FINAL.sub("", corpo)

    if COMMIT_QUALQUER.search(corpo):
        raise SystemExit(
            f"{caminho.name}: há um commit no meio do arquivo. "
            "Isso quebraria a atomicidade; aplique essa migration à mão."
        )
    return corpo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="executa as migrations; sem esta flag apenas lista o que falta",
    )
    args = parser.parse_args()

    import psycopg2

    import importacao_core

    conn = psycopg2.connect(
        importacao_core._database_url(),
        application_name="sirfisher_aplicar_migrations",
    )
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("select version from supabase_migrations.schema_migrations")
            registradas = {linha[0] for linha in cur.fetchall()}

        pendentes = []
        for arquivo in sorted(MIGRACOES.glob("*.sql")):
            achado = NOME_ARQUIVO.match(arquivo.name)
            if not achado:
                raise SystemExit(f"nome fora do padrão: {arquivo.name}")
            versao, nome = achado.groups()
            if versao not in registradas:
                pendentes.append((versao, nome, arquivo))

        print(f"Histórico no banco : {len(registradas)} versões")
        print(f"Pendentes          : {len(pendentes)}")
        for versao, nome, _ in pendentes:
            print(f"   {versao} | {nome}")

        if not pendentes:
            print("\nNada a aplicar.")
            return 0

        if not args.aplicar:
            print("\nDry-run. Use --aplicar para executar.")
            return 0

        conn.autocommit = False
        for versao, nome, arquivo in pendentes:
            corpo = preparar_sql(arquivo)
            print(f"\n>>> aplicando {versao} | {nome}")
            try:
                with conn.cursor() as cur:
                    cur.execute("set local statement_timeout = '120s'")
                    cur.execute(corpo)
                    cur.execute(
                        "insert into supabase_migrations.schema_migrations"
                        " (version, name) values (%s, %s)",
                        (versao, nome),
                    )
                conn.commit()
                print(f"    ok, registrada")
            except Exception as erro:
                conn.rollback()
                print(f"    FALHOU: {str(erro).strip()}")
                print("    Nada desta migration permaneceu. Interrompendo.")
                return 1

        with conn.cursor() as cur:
            cur.execute("select count(*) from supabase_migrations.schema_migrations")
            total = cur.fetchone()[0]
        conn.commit()
        print(f"\nConcluído. Histórico agora com {total} versões.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
