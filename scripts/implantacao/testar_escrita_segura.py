#!/usr/bin/env python3
"""Verifica escrita transacional no Supabase canônico sem tocar em dados reais.

O teste recusa qualquer projeto diferente do portal do SirFisher. Ele cria uma
tabela temporária, exercita INSERT, UPDATE e DELETE e executa rollback antes de
encerrar a sessão; logo, nenhum objeto ou registro permanece no banco.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REF_ESPERADA = "lucpxoynpvogkvzepagi"
sys.path.insert(0, str(ROOT / "scripts" / "importacao"))


def validar_destino(url: str) -> None:
    """Impede que este teste seja executado em qualquer projeto não canônico."""
    import importacao_core

    ref = importacao_core._referencia_projeto(url)
    if ref != REF_ESPERADA:
        raise RuntimeError(
            "destino recusado: a verificacao de escrita so pode usar o "
            "Supabase canônico do SirFisher"
        )


def main() -> int:
    import psycopg2
    import importacao_core

    url = importacao_core._database_url()
    validar_destino(url)
    conn = psycopg2.connect(url, application_name="sirfisher_teste_escrita_segura")
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("set local statement_timeout = '30s'")
            cur.execute(
                "create temp table sirfisher_verificacao_escrita "
                "(id bigint primary key, estado text not null) on commit drop"
            )
            cur.execute(
                "insert into sirfisher_verificacao_escrita (id, estado) values (1, 'criado')"
            )
            cur.execute(
                "update sirfisher_verificacao_escrita set estado = 'atualizado' where id = 1"
            )
            if cur.rowcount != 1:
                raise RuntimeError("UPDATE transacional não afetou o registro de teste")
            cur.execute("delete from sirfisher_verificacao_escrita where id = 1")
            if cur.rowcount != 1:
                raise RuntimeError("DELETE transacional não removeu o registro de teste")
        conn.rollback()
    finally:
        conn.close()

    print("ESCRITA_TRANSACIONAL_OK destino=sirfisher rollback=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
