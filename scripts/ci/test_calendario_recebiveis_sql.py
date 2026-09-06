#!/usr/bin/env python3
"""Executa a CTE de recebíveis do calendário contra PostgreSQL descartável.

Motivação
---------
As vendas do calendário vêm de ``public.recebimento_stone_net``, que filtra por
``COALESCE(sc.ativa AND sc.entra_faturamento, true)`` sobre ``public.stone_conta``.
A CTE ``recebiveis`` lia ``public.raw_stone_recebiveis`` sem filtro nenhum, então
realizado e projetado podiam sair de universos diferentes. Hoje nenhuma conta
excluída do faturamento tem recebíveis importados, o que torna o risco latente e
invisível para qualquer teste que use apenas os dados atuais.

Este teste força o cenário com dados sintéticos: cria uma conta fora do
faturamento e comprova que os recebíveis dela não entram, enquanto um stonecode
sem mapeamento continua entrando.

Exige banco descartável: ``CALENDARIO_SQL_DISPOSABLE=1``.
"""

from __future__ import annotations

import os
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRACAO = (
    ROOT
    / "supabase"
    / "migrations"
    / "20260906050000_calendario_filtra_conta_stone_recebiveis.sql"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pg_descartavel import exigir_banco_descartavel  # noqa: E402

VARIAVEL_AUTORIZACAO = "CALENDARIO_SQL_DISPOSABLE"
MES = "2026-01-01"

ESQUEMA = """
create table public.raw_stone_recebiveis (
  id bigserial primary key,
  stonecode text,
  data_vencimento date not null,
  produto text,
  valor_liquido numeric not null
);

create table public.stone_conta (
  stonecode text primary key,
  ativa boolean not null,
  entra_faturamento boolean not null
);

create function public.unaccent(text) returns text
language sql immutable as $$ select $1 $$;
"""

# Conta dentro do faturamento, conta fora, e um stonecode sem mapeamento.
DADOS = [
    ("770398216", "2026-01-10", "Credito a vista", Decimal("100.00")),
    ("140366173", "2026-01-10", "Credito a vista", Decimal("999.00")),
    ("770398216", "2026-01-11", "Debito", Decimal("50.00")),
    ("999999999", "2026-01-11", "Debito", Decimal("7.00")),
]

CONTAS = [
    ("770398216", True, True),
    ("140366173", True, False),   # ativa, mas fora do faturamento
]


def _cte_da_migration() -> str:
    """Extrai a CTE `recebiveis` literal e a torna executável fora da função."""
    sql = MIGRACAO.read_text(encoding="utf-8")
    achado = re.search(
        r"\), recebiveis as \((.*?)\n  \), movimento_real", sql, re.S
    )
    if not achado:
        raise AssertionError("CTE recebiveis não localizada na migration")

    corpo = achado.group(1)
    if "public.stone_conta sc" not in corpo:
        raise AssertionError(
            "a CTE extraída não contém o filtro de conta Stone; "
            "a migration não aplica a correção"
        )

    # p_mes é parâmetro da função; aqui vira literal. A janela, que na função
    # vem de outra CTE, também é fixada no início do mês em teste.
    corpo = corpo.replace("p_mes", f"date '{MES}'")
    corpo = corpo.replace(
        "(select j.inicio from janela j)", f"date '{MES}'"
    )
    return corpo


def _conectar():
    import psycopg2

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "postgres"),
        user=os.environ.get("PGUSER", "postgres"),
        application_name="sirfisher_calendario_sql",
    )
    exigir_banco_descartavel(conn, VARIAVEL_AUTORIZACAO)
    conn.autocommit = True
    return conn


def main() -> int:
    corpo = _cte_da_migration()
    conn = _conectar()
    try:
        with conn.cursor() as cur:
            cur.execute(ESQUEMA)
            cur.executemany(
                "insert into public.raw_stone_recebiveis"
                " (stonecode, data_vencimento, produto, valor_liquido)"
                " values (%s, %s, %s, %s)",
                DADOS,
            )
            cur.executemany(
                "insert into public.stone_conta"
                " (stonecode, ativa, entra_faturamento) values (%s, %s, %s)",
                CONTAS,
            )

            cur.execute(f"with recebiveis as ({corpo}) select dia, credito, debito"
                        " from recebiveis order by dia")
            linhas = {str(d): (c, deb) for d, c, deb in cur.fetchall()}

        esperado = {
            # 999.00 da conta fora do faturamento não pode aparecer.
            "2026-01-10": (Decimal("100.00"), Decimal("0")),
            # 7.00 de stonecode sem mapeamento continua entrando.
            "2026-01-11": (Decimal("0"), Decimal("57.00")),
        }

        if set(linhas) != set(esperado):
            raise AssertionError(f"dias inesperados: {sorted(linhas)}")

        for dia, (credito, debito) in esperado.items():
            obtido_credito, obtido_debito = linhas[dia]
            if obtido_credito != credito:
                raise AssertionError(
                    f"{dia}: crédito {obtido_credito}, esperado {credito}. "
                    "Recebível de conta fora do faturamento vazou para o calendário."
                )
            if obtido_debito != debito:
                raise AssertionError(
                    f"{dia}: débito {obtido_debito}, esperado {debito}"
                )
    finally:
        conn.close()

    print(
        "CALENDARIO_RECEBIVEIS_SQL_OK conta_fora_do_faturamento=excluida "
        "stonecode_sem_mapeamento=incluido cte=literal_da_migration"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
