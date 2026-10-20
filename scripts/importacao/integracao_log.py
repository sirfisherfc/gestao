"""Registro das execuções das integrações por API em ``integracao_execucao``.

A página Status lê esse registro para mostrar o que falhou e quais dias ficaram
sem carga. Uma falha ao registrar não pode esconder o erro da importação, então
vira só um aviso no terminal.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import date


LIMITE_MENSAGEM = 500


@dataclass(frozen=True)
class Execucao:
    fonte: str
    dia_referencia: date | None
    stonecode: str | None
    situacao: str
    linhas_novas: int | None = None
    mensagem: str | None = None


def origem() -> str:
    return "github" if os.environ.get("GITHUB_ACTIONS") == "true" else "manual"


def url_execucao() -> str | None:
    partes = [os.environ.get(nome) for nome in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID")]
    return "{}/{}/actions/runs/{}".format(*partes) if all(partes) else None


def registrar(execucoes: list[Execucao]) -> None:
    if not execucoes:
        return
    linhas = [
        (
            origem(), item.fonte, item.dia_referencia, item.stonecode, item.situacao,
            item.linhas_novas, (item.mensagem or "")[:LIMITE_MENSAGEM] or None, url_execucao(),
        )
        for item in execucoes
    ]
    try:
        import psycopg2

        from importacao_core import _database_url

        conn = psycopg2.connect(_database_url())
        try:
            with conn, conn.cursor() as cur:
                cur.executemany(
                    "insert into integracao_execucao (origem, fonte, dia_referencia, stonecode, "
                    "situacao, linhas_novas, mensagem, execucao_url) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                    linhas,
                )
        finally:
            conn.close()
    except Exception as exc:  # o erro da importação continua sendo o principal
        print(f"AVISO: execução não registrada no painel ({exc.__class__.__name__})", file=sys.stderr)
