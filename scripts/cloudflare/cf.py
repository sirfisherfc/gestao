# -*- coding: utf-8 -*-
"""
Ferramenta do Cloudflare para a zona sirfisher.com.br.

O dominio usa os nameservers do Cloudflare (love/memphis.ns.cloudflare.com).
Tudo e simulacao por padrao: o comando mostra o que faria e so altera a zona
com --aplicar. Nunca mexe no e-mail (Hostinger, Amazon SES/Resend), em
reservas/admin (GitHub Pages) nem em reparos (Worker).

Comandos:

  diagnostico      token, registros DNS, configuracoes, certificados e regras
  site             proxy + cache de /assets/ + redirecionamento sem www -> www
  purgar           esvazia o cache do Cloudflare (depois de trocar um asset)
  desfazer-proxy   volta www e o dominio sem www para "somente DNS" (rollback)

Credencial: CLOUDFLARE_API_TOKEN, da variavel de ambiente ou do gestao/.env
(ignorado pelo Git). Nunca exibir, copiar para paginas nem versionar o valor.

Uso:
  python scripts/cloudflare/cf.py diagnostico
  python scripts/cloudflare/cf.py site             # simula
  python scripts/cloudflare/cf.py site --aplicar
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENV = Path(__file__).resolve().parents[2] / ".env"
BASE = "https://api.cloudflare.com/client/v4"
ZONA = "sirfisher.com.br"
WWW = "www.sirfisher.com.br"
UM_ANO = 31536000

# Ordem segura: configuracoes e regras antes do proxy, para o primeiro acesso
# pela borda ja sair com o cache e o redirecionamento certos.
CONFIGURACOES = {
    "ssl": "full",               # GitHub Pages tem HTTPS; "full" nao derruba o site se o certificado de la atrasar
    "always_use_https": "on",
    "rocket_loader": "off",      # reescreveria os scripts da pagina
    "email_obfuscation": "off",  # injetaria script no HTML
    "browser_cache_ttl": 0,      # respeita o max-age da origem: HTML segue com 10 min
}
REGRA_CACHE = {
    "description": "Site: /assets/ com 1 ano no navegador (CSS/JS com ?v=; imagem alterada = nome novo)",
    "expression": f'(http.host eq "{WWW}" and starts_with(http.request.uri.path, "/assets/"))',
    "action": "set_cache_settings",
    "action_parameters": {"cache": True, "edge_ttl": {"mode": "respect_origin"},
                          "browser_ttl": {"mode": "override_origin", "default": UM_ANO}},
}
REGRA_REDIRECIONAMENTO = {
    "description": "Site: sirfisher.com.br -> www.sirfisher.com.br na borda",
    "expression": f'(http.host eq "{ZONA}")',
    "action": "redirect",
    "action_parameters": {"from_value": {
        "status_code": 301, "preserve_query_string": True,
        "target_url": {"expression": f'concat("https://{WWW}", http.request.uri.path)'}}},
}


def credencial(chave):
    """Valor da variavel de ambiente ou, na falta dela, do gestao/.env."""
    if os.environ.get(chave):
        return os.environ[chave]
    if ENV.exists():
        for linha in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.lstrip().startswith("#"):
                nome, valor = linha.split("=", 1)
                if nome.strip() == chave:
                    return valor.strip().strip('"').strip("'")
    return ""


def api(metodo, caminho, corpo=None):
    token = credencial("CLOUDFLARE_API_TOKEN")
    if not token:
        sys.exit("CLOUDFLARE_API_TOKEN ausente (gestao/.env ou variavel de ambiente).")
    dados = json.dumps(corpo).encode() if corpo is not None else None
    # Todas as chamadas daqui sao idempotentes (PUT/PATCH/GET/purga), entao uma
    # conexao derrubada no meio (visto: SSL UNEXPECTED_EOF) pode ser repetida.
    for tentativa in range(1, 5):
        req = urllib.request.Request(BASE + caminho, data=dados, method=metodo, headers={
            "Authorization": "Bearer " + token, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            corpo_erro = e.read() or b"{}"
            try:
                erros = json.loads(corpo_erro).get("errors")
            except ValueError:
                erros = corpo_erro[:200]
            return {"success": False, "http": e.code, "errors": erros}
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            if tentativa == 4:
                return {"success": False, "http": None, "errors": f"rede: {e}"}
            print(f"  rede falhou ({e}); tentando de novo em {2 ** tentativa} s...")
            time.sleep(2 ** tentativa)


def conferir(rotulo, resposta):
    if resposta.get("success"):
        print(f"  OK  {rotulo}")
        return True
    print(f"  ERRO {rotulo}: HTTP {resposta.get('http')} {resposta.get('errors')}")
    return False


def zona_id():
    r = api("GET", f"/zones?name={ZONA}")
    if not r.get("success") or not r.get("result"):
        sys.exit(f"Zona {ZONA} inacessivel com este token: {r.get('errors')}")
    return r["result"][0]["id"]


def registros_do_site(zid):
    """Registros que servem o site: A/AAAA do dominio sem www e o CNAME do www."""
    resposta = api("GET", f"/zones/{zid}/dns_records?per_page=200")
    if not resposta.get("success"):
        sys.exit(f"Nao consegui ler os registros DNS: {resposta.get('errors')}")
    todos = resposta["result"]
    return [r for r in todos if (r["name"] == ZONA and r["type"] in ("A", "AAAA"))
            or (r["name"] == WWW and r["type"] == "CNAME")]


def cmd_diagnostico(_args):
    v = api("GET", "/user/tokens/verify")
    print("token:", (v.get("result") or {}).get("status"), "" if v.get("success") else v.get("errors"))
    zid = zona_id()
    for r in api("GET", f"/zones/{zid}/dns_records?per_page=200")["result"]:
        print(f"  dns {r['type']:5} {r['name']:45} proxied={r.get('proxied')}")
    for nome in CONFIGURACOES:
        res = api("GET", f"/zones/{zid}/settings/{nome}")
        print(f"  conf {nome} = {(res.get('result') or {}).get('value')}")
    for c in api("GET", f"/zones/{zid}/ssl/certificate_packs?status=all").get("result") or []:
        print(f"  cert {c.get('type')} {c.get('status')} {c.get('hosts')}")
    for fase in ("http_request_cache_settings", "http_request_dynamic_redirect"):
        r = api("GET", f"/zones/{zid}/rulesets/phases/{fase}/entrypoint")
        regras = (r.get("result") or {}).get("rules") or []
        print(f"  regras {fase}: {[x.get('description') for x in regras] or 'nenhuma'}")


def cmd_site(args):
    zid = zona_id()
    registros = registros_do_site(zid)
    print("Plano:")
    for nome, valor in CONFIGURACOES.items():
        print(f"  configuracao {nome} -> {valor}")
    print("  regra de cache:", REGRA_CACHE["expression"])
    print("  redirecionamento:", REGRA_REDIRECIONAMENTO["expression"], "-> https://" + WWW)
    for r in registros:
        print(f"  proxy {r['type']} {r['name']} {r['content']}: {r.get('proxied')} -> True")
    if not args.aplicar:
        print("Simulacao. Rode de novo com --aplicar para alterar a zona.")
        return
    print("Aplicando:")
    tudo_ok = True
    for nome, valor in CONFIGURACOES.items():
        tudo_ok &= conferir(f"{nome} = {valor}", api("PATCH", f"/zones/{zid}/settings/{nome}", {"value": valor}))
    tudo_ok &= conferir("regra de cache /assets/", api(
        "PUT", f"/zones/{zid}/rulesets/phases/http_request_cache_settings/entrypoint", {"rules": [REGRA_CACHE]}))
    tudo_ok &= conferir("redirecionamento sem www", api(
        "PUT", f"/zones/{zid}/rulesets/phases/http_request_dynamic_redirect/entrypoint", {"rules": [REGRA_REDIRECIONAMENTO]}))
    if not tudo_ok:
        sys.exit("Algo falhou antes do proxy; o proxy NAO foi ligado.")
    for r in registros:
        conferir(f"proxy {r['type']} {r['name']} {r['content']}",
                 api("PATCH", f"/zones/{zid}/dns_records/{r['id']}", {"proxied": True}))
    conferir("purga do cache", api("POST", f"/zones/{zid}/purge_cache", {"purge_everything": True}))
    print("Pronto. Confira: curl -sI https://www.sirfisher.com.br/assets/fonts/fraunces.woff2")


def cmd_purgar(args):
    if not args.aplicar:
        print("Simulacao: esvaziaria todo o cache da zona. Use --aplicar.")
        return
    conferir("purga do cache", api("POST", f"/zones/{zona_id()}/purge_cache", {"purge_everything": True}))


def cmd_desfazer_proxy(args):
    zid = zona_id()
    for r in registros_do_site(zid):
        print(f"  {r['type']} {r['name']}: proxied {r.get('proxied')} -> False")
        if args.aplicar:
            conferir("somente DNS", api("PATCH", f"/zones/{zid}/dns_records/{r['id']}", {"proxied": False}))
    if not args.aplicar:
        print("Simulacao. Use --aplicar.")


def main():
    parser = argparse.ArgumentParser(description="Cloudflare da zona sirfisher.com.br (simula por padrao).")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("diagnostico").set_defaults(func=cmd_diagnostico)
    for nome, func in (("site", cmd_site), ("purgar", cmd_purgar), ("desfazer-proxy", cmd_desfazer_proxy)):
        p = sub.add_parser(nome)
        p.add_argument("--aplicar", action="store_true", help="Altera a zona de verdade.")
        p.set_defaults(func=func)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
