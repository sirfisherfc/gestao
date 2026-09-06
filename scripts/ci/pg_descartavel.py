"""Guarda compartilhada para testes que criam objetos em PostgreSQL.

Um teste que executa DDL precisa de um banco que possa ser destruído. Marcar o
banco errado como alvo criaria objetos em produção, então a autorização é
explícita e cumulativa: variável de ambiente ligada, host de loopback, nome de
banco no padrão descartável e servidor local ou privado.
"""

from __future__ import annotations

import ipaddress
import os
import re

NOME_DESCARTAVEL = re.compile(r"^sirfisher_[a-z0-9_]*_test$")
VERSAO_MINIMA = 150000


def exigir_banco_descartavel(conn, variavel: str) -> None:
    """Interrompe se a conexão não for um banco descartável autorizado."""
    if os.environ.get(variavel) != "1":
        raise AssertionError(f"Este teste exige {variavel}=1")

    host = os.environ.get("PGHOST", "")
    banco = os.environ.get("PGDATABASE", "")
    if host not in {"localhost", "127.0.0.1", "::1"}:
        raise AssertionError("Permitido somente com PGHOST local explícito")
    if not NOME_DESCARTAVEL.fullmatch(banco):
        raise AssertionError("Exige banco descartável chamado sirfisher_*_test")

    with conn.cursor() as cur:
        cur.execute(
            "select current_database(), host(inet_server_addr()), "
            "current_setting('server_version_num')::integer"
        )
        banco_atual, endereco, versao = cur.fetchone()
    conn.rollback()

    if banco_atual != banco:
        raise AssertionError("PGDATABASE não corresponde ao banco conectado")
    if endereco is None:
        raise AssertionError("Servidor conectado não identificado")

    # O Postgres do CI roda em container e se enxerga num endereço privado,
    # ainda que o cliente chegue por 127.0.0.1. Qualquer endereço roteável na
    # internet, como o banco de produção, continua bloqueado.
    ip = ipaddress.ip_address(endereco)
    if not (ip.is_loopback or ip.is_private):
        raise AssertionError(f"Servidor {endereco} não é local nem privado")

    if versao < VERSAO_MINIMA:
        raise AssertionError("Estes testes exigem PostgreSQL 15 ou superior")
