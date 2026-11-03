# -*- coding: utf-8 -*-
"""
Ferramenta do Cloudflare para a zona sirfisher.com.br.

O dominio usa os nameservers do Cloudflare (love/memphis.ns.cloudflare.com).
Tudo e simulacao por padrao: o comando mostra o que faria e so altera a zona
com --aplicar. Os comandos de site alteram DNS apenas do dominio sem www e
do www. As configuracoes TLS da zona alcancam todos os hosts com proxy.
O estado de admin, reservas, webmail e e-mail esta em
docs/CLOUDFLARE_SEGURANCA.md. As regras existentes de outros servicos sao
preservadas ao atualizar as regras do site.

Comandos:

  diagnostico      token, DNS, TLS, certificados, regras WAF e alertas
  site             proxy + cache de /assets/ + redirecionamento sem www -> www
  purgar           esvazia o cache da borda (raramente necessario: os assets
                   levam ?v=<hash> e o HTML expira em 10 min)
  desfazer-proxy   volta www e o dominio sem www para "somente DNS" (rollback)
  robots           desliga o robots.txt gerenciado do Cloudflare; quem publica
                   o robots.txt (com os mesmos rastreadores bloqueados)
                   e o site. --religar devolve o bloco do Cloudflare (rollback)

Credencial: CLOUDFLARE_API_TOKEN, da variavel de ambiente ou do gestao/.env
(ignorado pelo Git). Nunca exibir, copiar para paginas nem versionar o valor.
O comando robots precisa da permissao Zone > Bot Management > Edit no token.

Uso:
  python scripts/cloudflare/cf.py diagnostico
  python scripts/cloudflare/cf.py site             # simula
  python scripts/cloudflare/cf.py site --aplicar
"""

from __future__ import annotations

import argparse
from collections import Counter
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
    "ssl": "strict",             # Exige certificado valido na origem; GitHub Pages conferido em 03/11/2026
    "min_tls_version": "1.2",     # TLS 1.0/1.1 recusados na borda desde 02/11/2026
    "always_use_https": "on",
    "rocket_loader": "off",      # reescreveria os scripts da pagina
    "email_obfuscation": "off",  # injetaria script no HTML
    "browser_cache_ttl": 0,      # respeita o max-age da origem: HTML segue com 10 min
    # HSTS de 1 ano com subdominios (todos respondem em HTTPS; o e-mail nao usa HSTS).
    # Sem "preload": entrar na lista dos navegadores e um compromisso dificil de desfazer.
    "security_header": {"strict_transport_security": {
        "enabled": True, "max_age": 31536000, "include_subdomains": True, "preload": False, "nosniff": True}},
}
# So o que tem ?v= ganha um ano: o site grava ali o hash do conteudo
# (site/tools/cache/versionar_assets.py, no pre-commit), entao arquivo novo =
# endereco novo. Sem ?v= (fotos que o cardapio.js monta) fica o cache da origem.
REGRA_CACHE = {
    "description": "Site: /assets/ com ?v= (hash do conteudo) fica 1 ano no navegador",
    "expression": (f'(http.host eq "{WWW}" and starts_with(http.request.uri.path, "/assets/")'
                   ' and http.request.uri.query contains "v=")'),
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
# A politica de scripts fica no <meta> de cada pagina (site/tools/seguranca/csp.py);
# aqui vai o que so funciona por cabecalho.
REGRA_CABECALHOS = {
    "description": "Site: cabecalhos de seguranca (quadro, origem, referencia, permissoes)",
    "expression": f'(http.host eq "{WWW}")',
    "action": "rewrite",
    "action_parameters": {"headers": {
        "X-Frame-Options": {"operation": "set", "value": "SAMEORIGIN"},
        "Content-Security-Policy": {"operation": "set", "value": "frame-ancestors 'self'; upgrade-insecure-requests"},
        "Cross-Origin-Opener-Policy": {"operation": "set", "value": "same-origin"},
        "Referrer-Policy": {"operation": "set", "value": "strict-origin-when-cross-origin"},
        "Permissions-Policy": {"operation": "set", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=()"},
    }},
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
    # POST que cria uma regra pode ter sido aceito antes de uma queda de rede.
    # Nesse caso, conferir o destino antes de tentar outra criacao.
    pode_repetir = metodo in ("GET", "PUT", "PATCH") or caminho.endswith("/purge_cache")
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
            if not pode_repetir:
                return {"success": False, "http": None,
                        "errors": "Resultado incerto apos falha de rede; releia o destino antes de repetir."}
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


def gravar_regra(zid, fase, regra):
    """Altera somente a regra identificada pela descricao; preserva as demais."""
    caminho = f"/zones/{zid}/rulesets/phases/{fase}/entrypoint"
    resposta = api("GET", caminho)
    if not resposta.get("success"):
        if resposta.get("http") == 404:
            return api("PUT", caminho, {"rules": [regra]})
        return resposta
    conjunto = resposta.get("result")
    if not isinstance(conjunto, dict) or not conjunto.get("id") or not isinstance(conjunto.get("rules"), list):
        return {"success": False, "errors": "Conjunto de regras incompleto; nenhuma escrita realizada."}
    existentes = [r for r in conjunto["rules"] if r.get("description") == regra["description"]]
    if len(existentes) > 1 or (existentes and not existentes[0].get("id")):
        return {"success": False, "errors": "Identificacao ambigua da regra; nenhuma escrita realizada."}
    base = f'/zones/{zid}/rulesets/{conjunto["id"]}/rules'
    if existentes:
        return api("PATCH", f'{base}/{existentes[0]["id"]}', regra)
    return api("POST", base, regra)


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
    for fase in ("http_request_cache_settings", "http_request_dynamic_redirect", "http_response_headers_transform",
                 "http_request_firewall_custom"):
        r = api("GET", f"/zones/{zid}/rulesets/phases/{fase}/entrypoint")
        if not r.get("success"):
            print(f"  regras {fase}: indisponivel (HTTP {r.get('http')})")
            continue
        regras = (r.get("result") or {}).get("rules") or []
        print(f"  regras {fase}: {[x.get('description') for x in regras] or 'nenhuma'}")
    resposta = api("GET", f"/zones/{zid}/security-center/insights?dismissed=false&per_page=1000")
    resultado = resposta.get("result")
    if not resposta.get("success") or not isinstance(resultado, dict):
        print(f"  alertas: indisponivel (HTTP {resposta.get('http')})")
        return
    ocorrencias = resultado.get("issues")
    if not isinstance(ocorrencias, list):
        print("  alertas: resposta incompleta; contagem indisponivel")
        return
    contagens = Counter((o.get("status"), o.get("issue_class")) for o in ocorrencias)
    print(f"  alertas: {len(ocorrencias)} retornados; total informado {resultado.get('count')}")
    for (estado, classe), quantidade in sorted(contagens.items(), key=lambda item: str(item[0])):
        print(f"    {estado} {classe}: {quantidade}")


def cmd_site(args):
    zid = zona_id()
    registros = registros_do_site(zid)
    print("Plano:")
    for nome, valor in CONFIGURACOES.items():
        print(f"  configuracao {nome} -> {valor}")
    print("  regra de cache:", REGRA_CACHE["expression"])
    print("  redirecionamento:", REGRA_REDIRECIONAMENTO["expression"], "-> https://" + WWW)
    print("  cabecalhos:", ", ".join(REGRA_CABECALHOS["action_parameters"]["headers"]))
    for r in registros:
        print(f"  proxy {r['type']} {r['name']} {r['content']}: {r.get('proxied')} -> True")
    if not args.aplicar:
        print("Simulacao. Rode de novo com --aplicar para alterar a zona.")
        return
    print("Aplicando:")
    tudo_ok = True
    for nome, valor in CONFIGURACOES.items():
        tudo_ok &= conferir(f"{nome} = {valor}", api("PATCH", f"/zones/{zid}/settings/{nome}", {"value": valor}))
    tudo_ok &= conferir("regra de cache /assets/", gravar_regra(zid, "http_request_cache_settings", REGRA_CACHE))
    tudo_ok &= conferir("redirecionamento sem www", gravar_regra(zid, "http_request_dynamic_redirect", REGRA_REDIRECIONAMENTO))
    tudo_ok &= conferir("cabecalhos de seguranca", gravar_regra(zid, "http_response_headers_transform", REGRA_CABECALHOS))
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


def cmd_robots(args):
    # O site publica a lista de rastreadores bloqueados. Os dois campos abaixo
    # controlam a geracao do robots.txt; as preferencias e outras protecoes da
    # zona devem permanecer como estavam. Publique o site antes de desligar.
    zid = zona_id()
    antes = api("GET", f"/zones/{zid}/bot_management")
    if not antes.get("success") or not isinstance(antes.get("result"), dict):
        sys.exit(f"Sem acesso ao Bot Management (permissao no token?): {antes.get('errors')}")
    antes = antes["result"]
    alvo = bool(args.religar)
    campos = ("is_robots_txt_managed", "bot_preference_sync_enabled")
    for campo in campos:
        print(f"  {campo}: {antes.get(campo)} -> {alvo}")
    if not args.aplicar:
        print("Simulacao. Use --aplicar.")
        return
    corpo = {c: alvo for c in campos if antes.get(c) != alvo}
    if corpo:
        if not conferir("robots.txt do Cloudflare", api("PUT", f"/zones/{zid}/bot_management", corpo)):
            sys.exit("Nao foi possivel alterar o robots.txt gerenciado.")
    resposta = api("GET", f"/zones/{zid}/bot_management")
    if not resposta.get("success") or not isinstance(resposta.get("result"), dict):
        sys.exit(f"Nao foi possivel conferir o robots.txt gerenciado: {resposta.get('errors')}")
    depois = resposta["result"]
    if any(depois.get(c) is not alvo for c in campos):
        sys.exit("O robots.txt gerenciado nao ficou no estado solicitado; confira a zona.")
    mudou = {k: (antes.get(k), depois.get(k)) for k in set(antes) | set(depois)
             if k not in campos and antes.get(k) != depois.get(k)}
    if mudou:
        sys.exit(f"Outras configuracoes mudaram junto; confira a zona antes de continuar: {mudou}")
    if not conferir("purga do robots.txt", api("POST", f"/zones/{zid}/purge_cache",
                                            {"files": [f"https://{WWW}/robots.txt", f"https://{ZONA}/robots.txt"]})):
        sys.exit("Configuracao conferida, mas a purga do robots.txt falhou; confira a resposta publica.")
    print(f"Configuracao e purga conferidas. Confira a resposta publica: https://{WWW}/robots.txt")


def main():
    parser = argparse.ArgumentParser(description="Cloudflare da zona sirfisher.com.br (simula por padrao).")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("diagnostico").set_defaults(func=cmd_diagnostico)
    for nome, func in (("site", cmd_site), ("purgar", cmd_purgar), ("desfazer-proxy", cmd_desfazer_proxy),
                       ("robots", cmd_robots)):
        p = sub.add_parser(nome)
        p.add_argument("--aplicar", action="store_true", help="Altera a zona de verdade.")
        p.set_defaults(func=func)
    sub.choices["robots"].add_argument("--religar", action="store_true",
                                       help="Devolve o robots.txt gerenciado do Cloudflare.")
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
