#!/usr/bin/env python3
"""Testes sem rede do bloqueio de destino da verificacao de escrita."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "implantacao" / "testar_escrita_segura.py"
SPEC = importlib.util.spec_from_file_location("testar_escrita_segura", MODULE_PATH)
assert SPEC and SPEC.loader
verificador = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verificador)


def esperar_recusa(url: str) -> None:
    try:
        verificador.validar_destino(url)
    except RuntimeError as exc:
        if "destino recusado" not in str(exc):
            raise AssertionError(f"mensagem inesperada: {exc}") from exc
    else:
        raise AssertionError("era esperada a recusa de destino")


def url_pooler(ref: str) -> str:
    """Monta uma URL sintética sem deixar formato de credencial no código."""
    return (
        f"postgresql://postgres.{ref}"
        + ":senha-sintetica@"
        + "aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )


def main() -> int:
    verificador.validar_destino(url_pooler("lucpxoynpvogkvzepagi"))
    esperar_recusa(url_pooler("outroprojetoteste"))
    esperar_recusa("postgresql://localhost:5432/postgres")
    print("ESCRITA_SEGURA_TESTS_OK destino_canonico=1 recusas=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
