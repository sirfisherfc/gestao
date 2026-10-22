#!/usr/bin/env python3
"""Publica somente stone-webhook no portal; sem flag, apenas confere o destino."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import urllib.error
from urllib.request import Request, urlopen
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/importacao"))
sys.path.insert(0, str(ROOT.parent / "site/tools/analytics"))
from api_cliente import carregar_env, variavel
from api_stone_pix import FilaPix
from importacao_core import ErroOperacional, executar_com_saida
from supabase_credentials import PORTAL_REF, access_token, verify_portal


def api(rota, *, metodo="GET", corpo=None, tipo="application/json"):
    req = Request(f"https://api.supabase.com/v1/projects/{PORTAL_REF}/{rota}",
                  method=metodo, data=corpo,
                  headers={"Authorization": "Bearer " + access_token(), "Content-Type": tipo})
    try:
        with urlopen(req, timeout=60) as resposta:
            dados = resposta.read()
            return json.loads(dados) if dados else None
    except urllib.error.HTTPError as exc:
        raise ErroOperacional(f"Management API recusou {rota.split('?')[0]} (HTTP {exc.code})") from None


def pacote():
    # A API recebe os arquivos-fonte em partes separadas, não um ZIP.
    arquivo = (ROOT / "supabase/functions/stone-webhook/index.ts").read_bytes()
    limite = "sirfisher-" + uuid.uuid4().hex
    metadata = json.dumps({"name": "stone-webhook", "entrypoint_path": "index.ts", "verify_jwt": False}).encode()
    corpo = (f'--{limite}\r\nContent-Disposition: form-data; name="metadata"\r\nContent-Type: application/json\r\n\r\n'.encode()
             + metadata + f'\r\n--{limite}\r\nContent-Disposition: form-data; name="file"; filename="index.ts"\r\nContent-Type: application/typescript\r\n\r\n'.encode()
             + arquivo + f"\r\n--{limite}--\r\n".encode())
    return corpo, f"multipart/form-data; boundary={limite}"


def fluxo():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--aplicar", action="store_true")
    op = p.parse_args()
    carregar_env()
    verify_portal()
    if variavel("SUPABASE_URL").rstrip("/") != f"https://{PORTAL_REF}.supabase.co":
        raise ErroOperacional("SUPABASE_URL não aponta para o portal")
    token = variavel("STONE_WEBHOOK_TOKEN")
    if len(token) < 24:
        raise ErroOperacional("STONE_WEBHOOK_TOKEN precisa de pelo menos 24 caracteres")
    fila = FilaPix()
    try:
        documentos = fila.documentos()
    finally:
        fila.fechar()
    if len(documentos) != 1 or len(documentos[0]) != 14:
        raise ErroOperacional("é necessário um único CNPJ validado dos stonecodes ativos")
    print("Destino portal confirmado; somente stone-webhook e seus dois segredos serão publicados.")
    if not op.aplicar:
        print("Dry-run: nenhuma alteração externa.")
        return
    segredos = [{"name": "STONE_WEBHOOK_TOKEN", "value": token}, {"name": "STONE_PIX_DOCUMENT", "value": documentos[0]}]
    api("secrets", metodo="POST", corpo=json.dumps(segredos).encode())
    corpo, tipo = pacote()
    resultado = api("functions/deploy?slug=stone-webhook", metodo="POST", corpo=corpo, tipo=tipo)
    if not resultado or resultado.get("slug") != "stone-webhook":
        raise ErroOperacional("implantação sem confirmação de stone-webhook")
    print("STONE_WEBHOOK_DEPLOY_OK", resultado.get("status"), "version=" + str(resultado.get("version")))


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
