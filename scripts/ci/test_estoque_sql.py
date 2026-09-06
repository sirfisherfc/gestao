#!/usr/bin/env python3
"""Executa a migration de estoque contra PostgreSQL descartável.

Verifica o que a etapa 5 precisa garantir:

1. Contagens semanais convivem no mesmo mês; recontagem do mesmo dia corrige a
   anterior em vez de duplicar.
2. O fechamento aceita 'curva_a' e 'integral' no mesmo mês, o que a chave antiga
   (unidade, mes) impedia.
3. Toda gravação, fechamento e reabertura deixa rastro na trilha de revisões.
4. A view publica os quatro valores de entrada e a memória.

Exige banco descartável: ``ESTOQUE_SQL_DISPOSABLE=1``.
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
    / "20260906070000_estoque_contagem_semanal_e_revisoes.sql"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pg_descartavel import exigir_banco_descartavel  # noqa: E402

VARIAVEL_AUTORIZACAO = "ESTOQUE_SQL_DISPOSABLE"
UNIDADE = "PRAIA"

# Estado anterior à migration: a tabela como estava, com a chave de dois campos.
ESTADO_ANTERIOR = f"""
create schema if not exists private;

create table private.fechamento_consumo_estoque (
  unidade text not null,
  mes date not null,
  escopo text not null,
  estoque_inicial numeric,
  compras_liquidas numeric,
  transferencias_liquidas numeric,
  estoque_final numeric,
  memoria text,
  fechado_em timestamptz,
  fechado_por uuid,
  primary key (unidade, mes)
);

create function public.unidade_principal_nome() returns text
language sql immutable as $$ select '{UNIDADE}'::text $$;

create function public.usuario_pode_acessar_pagina(text) returns boolean
language sql immutable as $$ select true $$;
"""


def _corpo_da_migration() -> str:
    """Remove begin/commit: a transação é controlada pelo teste."""
    sql = MIGRACAO.read_text(encoding="utf-8")
    sql = re.sub(r"^\s*begin;\s*$", "", sql, count=1, flags=re.M)
    sql = re.sub(r"^\s*commit;\s*$", "", sql, count=1, flags=re.M)
    return sql


def _conectar():
    import psycopg2

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "postgres"),
        user=os.environ.get("PGUSER", "postgres"),
        application_name="sirfisher_estoque_sql",
    )
    exigir_banco_descartavel(conn, VARIAVEL_AUTORIZACAO)
    conn.autocommit = True
    return conn


def verificar_contagens_semanais(cur) -> None:
    for dia, valor in [("2026-01-05", 1000), ("2026-01-12", 1100), ("2026-01-19", 900)]:
        cur.execute(
            "select public.admin_registrar_contagem_estoque(%s::date, 'curva_a', %s)",
            (dia, valor),
        )

    cur.execute(
        "select count(*) from private.contagem_estoque where escopo = 'curva_a'"
    )
    total = cur.fetchone()[0]
    if total != 3:
        raise AssertionError(
            f"esperava 3 contagens semanais no mesmo mês, guardou {total}"
        )

    # Recontagem do mesmo dia corrige, não duplica.
    cur.execute(
        "select public.admin_registrar_contagem_estoque"
        "(date '2026-01-12', 'curva_a', 1250, 'recontagem')"
    )
    cur.execute(
        "select valor, memoria from private.contagem_estoque"
        " where data_contagem = date '2026-01-12' and escopo = 'curva_a'"
    )
    linhas = cur.fetchall()
    if len(linhas) != 1:
        raise AssertionError(f"recontagem duplicou o dia: {len(linhas)} linhas")
    if linhas[0][0] != Decimal("1250") or linhas[0][1] != "recontagem":
        raise AssertionError(f"recontagem não corrigiu o registro: {linhas[0]}")

    # Escopos diferentes no mesmo dia são contagens distintas.
    cur.execute(
        "select public.admin_registrar_contagem_estoque"
        "(date '2026-01-12', 'integral', 5000)"
    )
    cur.execute("select count(*) from private.contagem_estoque")
    if cur.fetchone()[0] != 4:
        raise AssertionError("escopo integral não coexistiu com curva_a no mesmo dia")


def verificar_escopos_no_mesmo_mes(cur) -> None:
    for escopo in ("curva_a", "integral"):
        cur.execute(
            "insert into private.fechamento_consumo_estoque"
            " (unidade, mes, escopo, estoque_inicial, compras_liquidas,"
            "  transferencias_liquidas, estoque_final, memoria)"
            " values (%s, date '2026-01-01', %s, 1000, 500, 0, 900, 'inicial')",
            (UNIDADE, escopo),
        )
    cur.execute("select count(*) from private.fechamento_consumo_estoque")
    if cur.fetchone()[0] != 2:
        raise AssertionError(
            "curva_a e integral não coexistiram no mesmo mês; a chave não mudou"
        )


def verificar_trilha_de_revisoes(cur) -> None:
    # Fecha, reabre e altera, conferindo a ação registrada em cada passo.
    cur.execute(
        "update private.fechamento_consumo_estoque set fechado_em = now(),"
        " fechado_por = null where escopo = 'curva_a'"
    )
    cur.execute(
        "update private.fechamento_consumo_estoque set fechado_em = null"
        " where escopo = 'curva_a'"
    )
    cur.execute(
        "update private.fechamento_consumo_estoque set estoque_final = 850"
        " where escopo = 'curva_a'"
    )

    cur.execute(
        "select acao from private.fechamento_consumo_estoque_revisao"
        " where escopo = 'curva_a' order by id"
    )
    acoes = [linha[0] for linha in cur.fetchall()]
    esperado = ["criado", "fechado", "reaberto", "alterado"]
    if acoes != esperado:
        raise AssertionError(f"trilha de revisões {acoes}, esperado {esperado}")

    cur.execute(
        "select estava_fechado, ficou_fechado"
        " from private.fechamento_consumo_estoque_revisao"
        " where escopo = 'curva_a' and acao = 'reaberto'"
    )
    estava, ficou = cur.fetchone()
    if not estava or ficou:
        raise AssertionError("reabertura registrou estado errado")


def verificar_view(cur) -> None:
    cur.execute(
        "select estoque_inicial, compras_liquidas, transferencias_liquidas,"
        " estoque_final, memoria, consumo_apurado"
        " from public.app_fechamento_consumo_estoque where escopo = 'integral'"
    )
    linha = cur.fetchone()
    if linha is None:
        raise AssertionError("view não devolveu o fechamento")
    if linha[:5] != (
        Decimal("1000"),
        Decimal("500"),
        Decimal("0"),
        Decimal("900"),
        "inicial",
    ):
        raise AssertionError(f"view não expõe os valores de entrada: {linha[:5]}")
    if linha[5] is not None:
        raise AssertionError("consumo_apurado deveria ser nulo enquanto aberto")

    # Fórmula preservada: 1000 + 500 + 0 - 900 = 600.
    cur.execute(
        "update private.fechamento_consumo_estoque set fechado_em = now()"
        " where escopo = 'integral'"
    )
    cur.execute(
        "select consumo_apurado, inventario_integral_fechado"
        " from public.app_fechamento_consumo_estoque where escopo = 'integral'"
    )
    consumo, integral_fechado = cur.fetchone()
    if consumo != Decimal("600"):
        raise AssertionError(f"consumo_apurado {consumo}, esperado 600")
    if not integral_fechado:
        raise AssertionError("selo de inventário integral não acendeu")

    cur.execute("select count(*) from public.app_contagem_estoque")
    if cur.fetchone()[0] != 4:
        raise AssertionError("view de contagens não publicou os registros")


def main() -> int:
    conn = _conectar()
    try:
        with conn.cursor() as cur:
            cur.execute(ESTADO_ANTERIOR)
            cur.execute(_corpo_da_migration())
            verificar_contagens_semanais(cur)
            verificar_escopos_no_mesmo_mes(cur)
            verificar_trilha_de_revisoes(cur)
            verificar_view(cur)
    finally:
        conn.close()

    print(
        "ESTOQUE_SQL_OK contagens_semanais=3 recontagem=corrige "
        "escopos_no_mesmo_mes=2 trilha=criado,fechado,reaberto,alterado "
        "view=expoe_entradas migration=literal"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
