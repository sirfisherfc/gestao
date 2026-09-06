#!/usr/bin/env python3
"""Executa a view da cascata da DRE contra PostgreSQL descartável.

Motivação
---------
O teste em ``test_dre_apresentacao.mjs`` valida a aritmética de uma fixture já
pronta: ele nunca executa o SQL da view nem tenta uma classificação sobreposta.
Ou seja, a exclusividade mútua dos componentes era afirmada, não comprovada.

Este teste extrai o SQL **literal** da migration, cria o mínimo de esquema para
executá-lo e verifica no banco:

1. Os componentes particionam o total: a soma de todos eles é exatamente o
   resultado líquido, sem sobreposição e sem resíduo mascarado.
2. Um grupo residual novo aparece em ``outros``, com transparência, em vez de
   ser absorvido por subtração.
3. A constraint rejeita de fato uma classificação sobreposta (um grupo
   operacional fixo marcado como variável).
4. Os subtotais publicados batem com os componentes que os compõem.

Exige um banco descartável: ``CASCATA_SQL_DISPOSABLE=1``, PGHOST de loopback e
PGDATABASE no padrão ``sirfisher_*_test``.
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
    / "20260906020000_cascata_dre_subtotais_mutuamente_exclusivos.sql"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pg_descartavel import exigir_banco_descartavel  # noqa: E402

VARIAVEL_AUTORIZACAO = "CASCATA_SQL_DISPOSABLE"

UNIDADE = "PRAIA"
MES = "2026-01-01"


def _sql_da_migration() -> tuple[str, str]:
    """Extrai, sem reescrever, a constraint e a view do arquivo de migration."""
    sql = MIGRACAO.read_text(encoding="utf-8")

    bloco_constraint = re.search(
        r"(alter table public\.grupo_variavel\s+add constraint .*?\);)",
        sql,
        re.S | re.I,
    )
    if not bloco_constraint:
        raise AssertionError("constraint não localizada na migration")

    bloco_view = re.search(
        r"(create or replace view public\.painel_dre_cascata as.*?order by mes;)",
        sql,
        re.S | re.I,
    )
    if not bloco_view:
        raise AssertionError("view da cascata não localizada na migration")

    return bloco_constraint.group(1), bloco_view.group(1)


ESQUEMA_MINIMO = """
create table public.dre_mensal (
  mes date not null,
  ano_mes text not null,
  unidade text not null,
  dre_grupo text,
  natureza text,
  total numeric not null,
  entra_dre boolean not null default true
);

create table public.grupo_variavel (
  grupo text primary key,
  variavel boolean not null default false
);

create function public.unidade_principal_nome()
returns text language sql immutable as $$ select %s::text $$;
"""


def _conectar():
    import psycopg2

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "postgres"),
        user=os.environ.get("PGUSER", "postgres"),
        application_name="sirfisher_cascata_sql",
    )
    exigir_banco_descartavel(conn, VARIAVEL_AUTORIZACAO)
    conn.autocommit = True
    return conn


# Cada linha cobre um componente distinto. Valores sintéticos, escolhidos para
# que nenhum subtotal coincida por acaso com outro.
LANCAMENTOS = [
    ("RECEITAS", Decimal("1000.00"), "receita"),
    ("DESPESA DIRETA DE VENDA", Decimal("-300.00"), "cmv"),
    ("IMPOSTOS", Decimal("-70.00"), "impostos"),
    ("TAXAS DE CARTAO", Decimal("-25.00"), "outras_variaveis"),
    ("PESSOAL", Decimal("-200.00"), "pessoal"),
    ("INFRAESTRUTURA", Decimal("-110.00"), "infraestrutura"),
    ("MARKETING E PUBLICIDADE", Decimal("-40.00"), "marketing"),
    ("NÃO OPERACIONAL", Decimal("-17.00"), "nao_operacional"),
    ("CONTABIL", Decimal("-13.00"), "contabil"),
    ("BENS DURÁVEIS", Decimal("-500.00"), "capex"),
    (None, Decimal("-7.00"), "nao_categorizado"),
    ("GRUPO RESIDUAL NOVO", Decimal("-3.00"), "outros"),
]


def preparar(cur, constraint_sql: str, view_sql: str) -> None:
    cur.execute(ESQUEMA_MINIMO % f"'{UNIDADE}'")
    cur.execute(constraint_sql)
    cur.execute(view_sql)

    for grupo, total, _ in LANCAMENTOS:
        cur.execute(
            "insert into public.dre_mensal"
            " (mes, ano_mes, unidade, dre_grupo, natureza, total, entra_dre)"
            " values (%s, %s, %s, %s, 'x', %s, true)",
            (MES, "2026-01", UNIDADE, grupo, total),
        )

    # Uma linha excluída da DRE e uma de outra unidade não podem vazar.
    cur.execute(
        "insert into public.dre_mensal"
        " (mes, ano_mes, unidade, dre_grupo, natureza, total, entra_dre)"
        " values (%s, '2026-01', %s, 'RECEITAS', 'x', 9999, false)",
        (MES, UNIDADE),
    )
    cur.execute(
        "insert into public.dre_mensal"
        " (mes, ano_mes, unidade, dre_grupo, natureza, total, entra_dre)"
        " values (%s, '2026-01', 'OUTRA UNIDADE', 'RECEITAS', 'x', 8888, true)",
        (MES,),
    )

    # 'TAXAS DE CARTAO' é o único grupo legitimamente variável.
    cur.execute(
        "insert into public.grupo_variavel (grupo, variavel)"
        " values ('TAXAS DE CARTAO', true), ('GRUPO RESIDUAL NOVO', false)"
    )


def linha_da_cascata(cur) -> dict:
    cur.execute("select * from public.painel_dre_cascata")
    linhas = cur.fetchall()
    if len(linhas) != 1:
        raise AssertionError(f"esperava 1 mês na cascata, veio {len(linhas)}")
    colunas = [d[0] for d in cur.description]
    return dict(zip(colunas, linhas[0]))


def verificar_particao(linha: dict) -> None:
    """Os componentes somam o resultado líquido, sem sobreposição nem resíduo."""
    esperado = sum(total for _, total, _ in LANCAMENTOS)
    if linha["resultado_liquido"] != esperado:
        raise AssertionError(
            f"resultado_liquido {linha['resultado_liquido']} != esperado {esperado}"
        )

    # outras_variaveis não é publicada como coluna; deriva do subtotal.
    outras_variaveis = (
        linha["margem_contribuicao"]
        - linha["receita"]
        - linha["cmv"]
        - linha["impostos"]
    )
    componentes = (
        linha["receita"]
        + linha["cmv"]
        + linha["impostos"]
        + outras_variaveis
        + linha["pessoal"]
        + linha["infraestrutura"]
        + linha["marketing"]
        + linha["nao_operacional"]
        + linha["contabil"]
        + linha["capex"]
        + linha["nao_categorizado"]
        + linha["outros"]
    )
    if componentes != linha["resultado_liquido"]:
        raise AssertionError(
            f"componentes somam {componentes}, resultado_liquido "
            f"{linha['resultado_liquido']}: há sobreposição ou resíduo"
        )

    if outras_variaveis != Decimal("-25.00"):
        raise AssertionError(f"outras_variaveis derivada errada: {outras_variaveis}")

    # O grupo residual novo aparece com transparência, não absorvido.
    if linha["outros"] != Decimal("-3.00"):
        raise AssertionError(f"grupo residual não exposto em outros: {linha['outros']}")
    if linha["nao_categorizado"] != Decimal("-7.00"):
        raise AssertionError(
            f"linha sem dre_grupo deveria virar nao_categorizado: "
            f"{linha['nao_categorizado']}"
        )


def verificar_subtotais(linha: dict) -> None:
    mc = Decimal("1000.00") - Decimal("300.00") - Decimal("70.00") - Decimal("25.00")
    if linha["margem_contribuicao"] != mc:
        raise AssertionError(f"margem_contribuicao {linha['margem_contribuicao']} != {mc}")

    op = mc - Decimal("200.00") - Decimal("110.00") - Decimal("40.00")
    if linha["resultado_operacional"] != op:
        raise AssertionError(
            f"resultado_operacional {linha['resultado_operacional']} != {op}"
        )

    # Linhas fora da DRE e de outra unidade não entraram.
    if linha["receita"] != Decimal("1000.00"):
        raise AssertionError(f"receita contaminada: {linha['receita']}")


def verificar_constraint(cur) -> None:
    """Uma classificação sobreposta precisa ser rejeitada pelo banco."""
    import psycopg2

    proibidos = [
        "PESSOAL",
        "INFRAESTRUTURA",
        "MARKETING E PUBLICIDADE",
        "RECEITAS",
        "NÃO OPERACIONAL",
        "CONTABIL",
        "BENS DURÁVEIS",
    ]
    for grupo in proibidos:
        try:
            cur.execute(
                "insert into public.grupo_variavel (grupo, variavel)"
                " values (%s, true)",
                (grupo,),
            )
        except psycopg2.errors.CheckViolation:
            cur.execute("rollback")
        else:
            cur.execute("rollback")
            raise AssertionError(
                f"grupo '{grupo}' foi aceito como variável; a constraint não protege"
            )

    # Um grupo legitimamente variável continua aceito.
    cur.execute(
        "insert into public.grupo_variavel (grupo, variavel)"
        " values ('OUTRA TAXA VARIAVEL', true)"
    )
    cur.execute("delete from public.grupo_variavel where grupo = 'OUTRA TAXA VARIAVEL'")


def main() -> int:
    conn = _conectar()
    try:
        constraint_sql, view_sql = _sql_da_migration()
        with conn.cursor() as cur:
            preparar(cur, constraint_sql, view_sql)
            linha = linha_da_cascata(cur)
            verificar_particao(linha)
            verificar_subtotais(linha)
            verificar_constraint(cur)
    finally:
        conn.close()

    print(
        f"CASCATA_SQL_OK componentes={len(LANCAMENTOS)} "
        "particao=exata constraint=rejeita_sobreposicao view=sql_literal_da_migration"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
