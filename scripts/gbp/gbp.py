# -*- coding: utf-8 -*-
"""
Ferramenta do Perfil da Empresa no Google (Google Business Profile).

Cuida da ficha "Sir Fisher" (Av. Beira Mar, 3421). As fichas antigas
"Sir Fisher - PUB" e "Sir Fisher - Impresa" foram encerradas e ficam de fora.

Tudo e simulacao por padrao: o comando mostra o antes e o depois e so publica
com --publicar. Cada publicacao e lida de volta pela API para conferir e fica
registrada em tmp/gbp/publicacoes.jsonl (ignorado pelo Git), junto com o
retrato da ficha tirado antes da mudanca.

Comandos:

  backup      retrato completo da ficha em tmp/gbp/retratos/
  checar      lista o que a rotina precisa fazer hoje
  pendentes   avaliacoes sem resposta (padrao: desde 2025-01-01)
  responder   publica ou edita a resposta de uma avaliacao (ou um lote)
  aplicar     aplica um plano JSON de cadastro e atributos
  feriados    sincroniza os horarios de feriado dos proximos meses
  instagram   fotos recentes do @sirfisherfc (API da Meta) que faltam na ficha
  preparar-fotos  leva fotos novas de site/Fotos para a pasta publica do site
  descartar-foto  tira uma foto preparada que nao serve (e nao a traz de volta)
  publicar-fotos  faz commit/push so da pasta publica, espera o deploy e importa
  fotos       importa na ficha, por URL, as fotos publicas que ainda nao estao la
  post        cria uma postagem na ficha
  metricas    buscas, visualizacoes e acoes (API de desempenho)

Credenciais: GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET e
GOOGLE_OAUTH_REFRESH_TOKEN, lidas das variaveis de ambiente (rotina na nuvem)
ou de gestao/.env (PC). Nada disso e impresso.
A rotina de uso esta em docs/ROTINA_PERFIL_GOOGLE.md.
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ENV = RAIZ / ".env"
SAIDA = RAIZ / "tmp" / "gbp"
# Caixa de entrada das fotos (ignorada pelo Git do site) e a pasta publica de
# onde o Google importa as fotos por URL.
PASTA_FOTOS = RAIZ.parent / "site" / "Fotos"
PASTA_PUBLICA = RAIZ.parent / "site" / "assets" / "img" / "perfil-google"
URL_PUBLICA = "https://www.sirfisher.com.br/assets/img/perfil-google/"

CONTA = "accounts/107942180782668171719"
LOCAL = "locations/12889581244809183683"
BI = "https://mybusinessbusinessinformation.googleapis.com/v1"
V4 = "https://mybusiness.googleapis.com/v4"
DESEMPENHO = "https://businessprofileperformance.googleapis.com/v1"

TELEFONE = "(85) 98854-4274"
# Numero pessoal do proprietario: nunca publicar.
TELEFONES_PROIBIDOS = ("98899-3449", "988993449", "98899 3449")
# Pedir mudanca de nota ou oferecer vantagem por avaliacao fere a politica do Google.
# Agradecer as estrelas pode; pedir mais estrelas, nao.
FRASES_PROIBIDAS = (
    "5ª estrela", "quinta estrela", "merecer as 5", "merecer 5",
    "atualizar sua avaliação", "atualizar a avaliação", "mudar a nota",
    "alterar a nota", "rever a nota", "desconto", "brinde",
)
NOTA = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
MASCARA_LOCAL = (
    "name,title,phoneNumbers,categories,storefrontAddress,websiteUri,regularHours,"
    "specialHours,serviceArea,openInfo,metadata,profile,moreHours"
)

# Dias em que a casa fecha. Nos demais feriados abre no horario normal.
FECHADO_MES_DIA = {(12, 24), (12, 25)}
FERIADOS_FIXOS = {
    (1, 1): "Confraternizacao universal",
    (3, 19): "Sao Jose (CE)",
    (3, 25): "Data Magna do Ceara",
    (4, 13): "Aniversario de Fortaleza",
    (4, 21): "Tiradentes",
    (5, 1): "Dia do Trabalho",
    (8, 15): "Nossa Senhora da Assuncao (Fortaleza)",
    (9, 7): "Independencia",
    (10, 12): "Nossa Senhora Aparecida",
    (11, 2): "Finados",
    (11, 15): "Proclamacao da Republica",
    (11, 20): "Consciencia Negra",
    (12, 24): "Vespera de Natal",
    (12, 25): "Natal",
    (12, 31): "Vespera de Ano-Novo",
}


# ----------------------------------------------------------------- infra

CHAVES = ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN")


def credencial(chave):
    """Valor da variavel de ambiente (nuvem) ou, na falta dela, do gestao/.env (PC)."""
    if os.environ.get(chave):
        return os.environ[chave]
    if ENV.exists():
        for linha in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.lstrip().startswith("#"):
                nome, valor = linha.split("=", 1)
                if nome.strip() == chave:
                    return valor.strip().strip('"').strip("'")
    return ""


def carregar_env():
    env = {k: credencial(k) for k in CHAVES}
    faltando = [k for k in CHAVES if not env[k]]
    if faltando:
        sys.exit("Credenciais ausentes (gestao/.env ou variaveis de ambiente): " + ", ".join(faltando))
    return env


class ErroApi(Exception):
    def __init__(self, status, corpo):
        super().__init__(f"HTTP {status}: {corpo}")
        self.status = status
        self.corpo = corpo


_TOKEN = None


def token():
    global _TOKEN
    if _TOKEN is None:
        env = carregar_env()
        dados = urllib.parse.urlencode({
            "client_id": env["GOOGLE_OAUTH_CLIENT_ID"],
            "client_secret": env["GOOGLE_OAUTH_CLIENT_SECRET"],
            "refresh_token": env["GOOGLE_OAUTH_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        }).encode()
        with urllib.request.urlopen("https://oauth2.googleapis.com/token", dados, timeout=30) as r:
            _TOKEN = json.load(r)["access_token"]
    return _TOKEN


def api(metodo, url, corpo=None, bruto=None, tipo=None):
    cabecalhos = {"Authorization": f"Bearer {token()}"}
    dados = None
    if corpo is not None:
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        cabecalhos["Content-Type"] = "application/json; charset=utf-8"
    elif bruto is not None:
        dados = bruto
        cabecalhos["Content-Type"] = tipo or "application/octet-stream"
    pedido = urllib.request.Request(url, data=dados, headers=cabecalhos, method=metodo)
    try:
        with urllib.request.urlopen(pedido, timeout=120) as r:
            texto = r.read().decode("utf-8")
            return json.loads(texto) if texto.strip() else {}
    except urllib.error.HTTPError as e:
        try:
            erro = json.load(e).get("error", {})
            corpo_erro = {"status": erro.get("status"), "mensagem": erro.get("message"),
                          "detalhes": erro.get("details")}
        except Exception:
            corpo_erro = {}
        raise ErroApi(e.code, corpo_erro) from None


def paginado(url, chave, max_paginas=None):
    itens, pagina, extra, lidas = [], None, {}, 0
    while True:
        sep = "&" if "?" in url else "?"
        js = api("GET", url + (f"{sep}pageToken={urllib.parse.quote(pagina, safe='')}" if pagina else ""))
        itens += js.get(chave, [])
        extra = {k: v for k, v in js.items() if k not in (chave, "nextPageToken")}
        pagina = js.get("nextPageToken")
        lidas += 1
        if not pagina or (max_paginas and lidas >= max_paginas):
            return itens, extra


def registrar(acao, antes, depois, extra=None):
    SAIDA.mkdir(parents=True, exist_ok=True)
    linha = {"quando": dt.datetime.now().isoformat(timespec="seconds"), "acao": acao,
             "antes": antes, "depois": depois}
    if extra:
        linha.update(extra)
    with open(SAIDA / "publicacoes.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def mostrar(rotulo, antes, depois):
    print(f"\n--- {rotulo}")
    print("antes :", json.dumps(antes, ensure_ascii=False, indent=1) if not isinstance(antes, str) else antes)
    print("depois:", json.dumps(depois, ensure_ascii=False, indent=1) if not isinstance(depois, str) else depois)


# ----------------------------------------------------------------- leitura

def ler_local():
    return api("GET", f"{BI}/{LOCAL}?readMask={MASCARA_LOCAL}")


def ler_atributos():
    return api("GET", f"{BI}/{LOCAL}/attributes").get("attributes", [])


def ler_avaliacoes():
    itens, extra = paginado(f"{V4}/{CONTA}/{LOCAL}/reviews?pageSize=50", "reviews")
    return itens, extra


def ler_fotos():
    itens, _ = paginado(f"{V4}/{CONTA}/{LOCAL}/media?pageSize=100", "mediaItems")
    return itens


def ler_posts():
    itens, _ = paginado(f"{V4}/{CONTA}/{LOCAL}/localPosts?pageSize=100", "localPosts")
    return itens


def cmd_backup(_args=None):
    pasta = SAIDA / "retratos" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    pasta.mkdir(parents=True, exist_ok=True)
    avaliacoes, resumo = ler_avaliacoes()
    partes = {
        "local": ler_local(),
        "atributos": ler_atributos(),
        "avaliacoes": {"itens": avaliacoes, **resumo},
        "fotos": ler_fotos(),
        "posts": ler_posts(),
    }
    for nome, conteudo in partes.items():
        (pasta / f"{nome}.json").write_text(json.dumps(conteudo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Retrato salvo em {pasta}")
    return pasta


# ----------------------------------------------------------------- avaliacoes

def texto_cliente(comentario):
    comentario = (comentario or "").strip()
    if "(Original)" in comentario:
        return comentario.split("(Original)", 1)[1].strip()
    return comentario.split("(Translated by Google)", 1)[0].strip()


def cmd_pendentes(args):
    avaliacoes, _ = ler_avaliacoes()
    agora = dt.datetime.now(dt.timezone.utc)
    pend = [a for a in avaliacoes if not a.get("reviewReply") and a["createTime"][:10] >= args.desde]
    pend.sort(key=lambda a: a["createTime"])
    saida = []
    for a in pend:
        criada = dt.datetime.fromisoformat(a["createTime"].replace("Z", "+00:00"))
        saida.append({
            "id": a["reviewId"],
            "data": a["createTime"][:10],
            "horas": round((agora - criada).total_seconds() / 3600),
            "nota": NOTA.get(a.get("starRating"), 0),
            "nome": a.get("reviewer", {}).get("displayName", ""),
            "texto": texto_cliente(a.get("comment")),
        })
    if args.json:
        print(json.dumps(saida, ensure_ascii=False, indent=1))
    else:
        print(f"{len(saida)} avaliacao(oes) sem resposta desde {args.desde}")
        for s in saida:
            print(f"- [{s['data']}, {s['horas']}h] {s['nota']}* {s['nome']} | {s['id']}\n  {s['texto'] or '(sem texto)'}")


def validar_resposta(texto):
    problemas = []
    if not texto.strip():
        problemas.append("resposta vazia")
    if len(texto) > 4000:
        problemas.append(f"resposta longa demais ({len(texto)} caracteres)")
    baixo = texto.lower()
    for tel in TELEFONES_PROIBIDOS:
        if tel in texto:
            problemas.append(f"telefone pessoal {tel}: use o corporativo {TELEFONE}")
    for frase in FRASES_PROIBIDAS:
        if frase in baixo:
            problemas.append(f"frase proibida pela politica do Google: '{frase}'")
    if re.search(r"https?://", texto):
        problemas.append("link na resposta: o Google costuma bloquear")
    return problemas


def cmd_responder(args):
    if args.lote:
        pedidos = json.loads(Path(args.lote).read_text(encoding="utf-8"))
    else:
        texto = Path(args.arquivo).read_text(encoding="utf-8") if args.arquivo else args.texto
        pedidos = [{"id": args.id, "texto": texto}]
    avaliacoes, _ = ler_avaliacoes()
    por_id = {a["reviewId"]: a for a in avaliacoes}
    erros = 0
    for p in pedidos:
        a = por_id.get(p["id"].split("/")[-1])
        texto = (p.get("texto") or "").strip()
        if not a:
            print(f"\n!! avaliacao nao encontrada: {p['id']}")
            erros += 1
            continue
        problemas = validar_resposta(texto)
        nome = a.get("reviewer", {}).get("displayName", "")
        rotulo = f"{a['createTime'][:10]} {NOTA.get(a.get('starRating'))}* {nome}"
        antes = (a.get("reviewReply") or {}).get("comment", "(sem resposta)")
        print(f"\n=== {rotulo}\ncliente: {texto_cliente(a.get('comment')) or '(sem texto)'}")
        mostrar("resposta", antes, texto)
        if problemas:
            print("!! bloqueada: " + "; ".join(problemas))
            erros += 1
            continue
        if not args.publicar:
            continue
        # A leitura (GET) das avaliacoes leva alguns minutos para refletir a
        # edicao; quem confirma na hora e o retorno do proprio PUT.
        devolvida = api("PUT", f"{V4}/{a['name']}/reply", {"comment": texto})
        ok = devolvida.get("comment", "").strip() == texto
        registrar("resposta", antes, texto, {"avaliacao": a["name"], "conferido": ok,
                                             "atualizada_em": devolvida.get("updateTime")})
        print("publicada (confirmada pelo Google)" if ok else "!! o Google devolveu um texto diferente")
        erros += 0 if ok else 1
    if not args.publicar:
        print("\n(simulacao: nada publicado; use --publicar)")
    return 1 if erros else 0


# ----------------------------------------------------------------- cadastro

def horas_do_dia(local, data):
    nome = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"][data.weekday()]
    for p in local.get("regularHours", {}).get("periods", []):
        if p["openDay"] == nome:
            return p["openTime"], p["closeTime"]
    return None, None


def pascoa(ano):
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(ano, mes, dia)


def feriados(inicio, fim):
    dias = {}
    for ano in range(inicio.year, fim.year + 1):
        for (mes, dia), nome in FERIADOS_FIXOS.items():
            dias[dt.date(ano, mes, dia)] = nome
        p = pascoa(ano)
        dias[p - dt.timedelta(days=48)] = "Carnaval (segunda)"
        dias[p - dt.timedelta(days=47)] = "Carnaval (terca)"
        dias[p - dt.timedelta(days=2)] = "Sexta-feira Santa"
        dias[p + dt.timedelta(days=60)] = "Corpus Christi"
    return {d: n for d, n in sorted(dias.items()) if inicio <= d <= fim}


def data_api(d):
    return {"year": d.year, "month": d.month, "day": d.day}


def horarios_especiais(local, dias):
    hoje = dt.date.today()
    fim = hoje + dt.timedelta(days=dias)
    calculados = {}
    for d in feriados(hoje, fim):
        if (d.month, d.day) in FECHADO_MES_DIA:
            calculados[d] = {"startDate": data_api(d), "endDate": data_api(d), "closed": True}
        else:
            abre, fecha = horas_do_dia(local, d)
            if abre:
                calculados[d] = {"startDate": data_api(d), "endDate": data_api(d),
                                 "openTime": abre, "closeTime": fecha}
    # Preserva excecoes futuras lancadas a mao que nao sejam feriados calculados.
    manter = []
    for p in local.get("specialHours", {}).get("specialHourPeriods", []):
        s = p["startDate"]
        d = dt.date(s["year"], s["month"], s["day"])
        if d >= hoje and d not in calculados:
            manter.append(p)
    periodos = manter + [calculados[d] for d in sorted(calculados)]
    periodos.sort(key=lambda p: (p["startDate"]["year"], p["startDate"]["month"], p["startDate"]["day"]))
    return {"specialHourPeriods": periodos}


def publicar_local(local, novo, mascara, publicar):
    atual = {campo: local.get(campo.split(".")[0]) for campo in mascara}
    url = f"{BI}/{LOCAL}?updateMask={','.join(mascara)}"
    api("PATCH", url + "&validateOnly=true", novo)
    print("\n(validado pelo Google sem publicar)")
    if not publicar:
        return
    api("PATCH", url, novo)
    depois = ler_local()
    registrar("cadastro", atual, {c: depois.get(c.split(".")[0]) for c in mascara}, {"mascara": mascara})
    print("cadastro publicado e relido")


def publicar_atributos(definir, remover, publicar):
    atuais = {a["name"]: a for a in ler_atributos()}
    nomes = [a["name"] for a in definir] + [f"attributes/{n}" for n in remover]
    for a in definir:
        mostrar(a["name"], atuais.get(a["name"], "(nao definido)"), a)
    for n in remover:
        mostrar(f"attributes/{n}", atuais.get(f"attributes/{n}", "(nao definido)"), "(remover)")
    if not publicar or not nomes:
        return
    url = f"{BI}/{LOCAL}/attributes?attributeMask=" + ",".join(nomes)
    api("PATCH", url, {"name": f"{LOCAL}/attributes", "attributes": definir})
    depois = {a["name"]: a for a in ler_atributos()}
    divergentes = [a["name"] for a in definir if depois.get(a["name"]) != a]
    divergentes += [f"attributes/{n}" for n in remover if f"attributes/{n}" in depois]
    registrar("atributos", {n: atuais.get(n) for n in nomes}, {n: depois.get(n) for n in nomes})
    print("atributos publicados e relidos" + (f"; conferir: {divergentes}" if divergentes else ""))


def cmd_aplicar(args):
    plano = json.loads(Path(args.plano).read_text(encoding="utf-8"))
    if args.publicar:
        cmd_backup()
    local = ler_local()
    novo, mascara = {}, []
    for campo, valor in plano.get("local", {}).items():
        raiz = campo.split(".")[0]
        if campo == "profile.description":
            novo.setdefault("profile", {})["description"] = valor
            mostrar(campo, local.get("profile", {}).get("description"), valor)
        elif campo == "categories":
            novo[raiz] = valor
            nomes = lambda c: [c.get("primaryCategory", {}).get("name")] + [
                a["name"] for a in c.get("additionalCategories", [])]
            mostrar(campo, nomes(local.get(raiz, {})), nomes(valor))
        else:
            novo[raiz] = valor
            mostrar(campo, local.get(raiz), valor)
        mascara.append(campo)
    if plano.get("feriados_dias"):
        novo["specialHours"] = horarios_especiais(local, plano["feriados_dias"])
        mostrar("specialHours", local.get("specialHours"), novo["specialHours"])
        mascara.append("specialHours")
    if mascara:
        publicar_local(local, novo, mascara, args.publicar)
    publicar_atributos(plano.get("atributos", []), plano.get("remover_atributos", []), args.publicar)
    if not args.publicar:
        print("\n(simulacao: nada publicado; use --publicar)")


def cmd_feriados(args):
    local = ler_local()
    novo = {"specialHours": horarios_especiais(local, args.dias)}
    atual = local.get("specialHours", {}).get("specialHourPeriods", [])
    if json.dumps(atual, sort_keys=True) == json.dumps(novo["specialHours"]["specialHourPeriods"], sort_keys=True):
        print("Horarios de feriado ja estao em dia.")
        return
    mostrar("specialHours", local.get("specialHours"), novo["specialHours"])
    publicar_local(local, novo, ["specialHours"], args.publicar)


# ----------------------------------------------------------------- fotos

def dhash(imagem, lado=16):
    from PIL import Image
    cinza = imagem.convert("L").resize((lado + 1, lado), Image.LANCZOS)
    px = cinza.load()
    bits = 0
    for y in range(lado):
        for x in range(lado):
            bits = (bits << 1) | (px[x, y] > px[x + 1, y])
    return bits


def hashes_publicados():
    """Hash de cada foto ja publicada na ficha, para nao repetir foto.

    Baixa miniaturas pequenas, com pausa entre elas: a partir de servidores na
    nuvem o Google responde 429 a rajadas. Miniatura que falhar mesmo apos as
    novas tentativas e pulada, com aviso, em vez de derrubar o comando.
    """
    from PIL import Image
    cache_arq = SAIDA / "hashes-ficha.json"
    try:
        cache = json.loads(cache_arq.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    hashes, falhas = [], 0
    for m in ler_fotos():
        if m.get("mediaFormat") != "PHOTO" or not m.get("googleUrl"):
            continue
        nome = m["name"].split("/")[-1]
        if nome in cache:
            hashes.append(cache[nome])
            continue
        pedido = urllib.request.Request(m["googleUrl"].split("=")[0] + "=s128",
                                        headers={"User-Agent": "Mozilla/5.0"})
        for espera in (0.3, 5, 20, 60):
            time.sleep(espera)
            try:
                with urllib.request.urlopen(pedido, timeout=60) as r:
                    cache[nome] = dhash(Image.open(io.BytesIO(r.read())))
                hashes.append(cache[nome])
                break
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    break
            except urllib.error.URLError:
                break
        if nome not in cache:
            falhas += 1
    if falhas:
        print(f"aviso: {falhas} miniatura(s) da ficha nao baixaram; a checagem de repetidas ficou parcial")
    try:
        SAIDA.mkdir(parents=True, exist_ok=True)
        cache_arq.write_text(json.dumps(cache), encoding="utf-8")
    except OSError:
        pass
    return hashes


def imagens(pasta):
    return [p for p in sorted(Path(pasta).iterdir())
            if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]


def parecida(h, hashes):
    return min((bin(h ^ p).count("1") for p in hashes), default=256) <= 40


DESCARTADAS = SAIDA / "fotos-descartadas.json"


def hashes_descartados():
    return json.loads(DESCARTADAS.read_text(encoding="utf-8")) if DESCARTADAS.exists() else []


def cmd_descartar_foto(args):
    """Tira da pasta publica uma foto preparada e ainda nao publicada, e nao a traz de volta."""
    from PIL import Image
    arq = PASTA_PUBLICA / Path(args.nome).name
    if not arq.exists():
        sys.exit(f"nao encontrada: {arq}")
    rastreada = subprocess.run(["git", "-C", str(PASTA_PUBLICA.parents[2]), "ls-files", "--error-unmatch",
                                str(arq)], capture_output=True).returncode == 0
    if rastreada:
        sys.exit("essa foto ja foi publicada no site; remova a mao se for o caso")
    lista = hashes_descartados() + [dhash(Image.open(arq))]
    SAIDA.mkdir(parents=True, exist_ok=True)
    DESCARTADAS.write_text(json.dumps(lista), encoding="utf-8")
    destino = SAIDA / "descartadas"
    destino.mkdir(exist_ok=True)
    arq.replace(destino / arq.name)
    registrar("foto-descartada", arq.name, None, {"motivo": args.motivo})
    print(f"descartada: {arq.name} ({args.motivo})")


def cmd_publicar_fotos(args):
    """Publica no site as fotos preparadas, espera o deploy e importa na ficha."""
    site = PASTA_PUBLICA.parents[2]
    alvo = str(PASTA_PUBLICA.relative_to(site)).replace("\\", "/")
    novas = subprocess.run(["git", "-C", str(site), "status", "--porcelain", "--", alvo],
                           capture_output=True, text=True, check=True).stdout.strip()
    if novas:
        print("fotos novas no site:\n" + novas)
        if not args.publicar:
            print("\n(simulacao: nada publicado; use --publicar)")
            return
        for cmd in (["pull", "--ff-only", "-q", "origin", "main"], ["add", "--", alvo],
                    ["commit", "-q", "-m", "img: fotos novas para o Perfil do Google\n\n"
                     "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", "--", alvo],
                    ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", str(site)] + cmd, check=True)
        print("site publicado; aguardando o deploy")
        limite = time.time() + 600
        ultimo = sorted(imagens(PASTA_PUBLICA), key=lambda p: p.stat().st_mtime)[-1]
        while time.time() < limite:
            try:
                urllib.request.urlopen(urllib.request.Request(URL_PUBLICA + urllib.parse.quote(ultimo.name),
                                                              method="HEAD"), timeout=30)
                break
            except urllib.error.URLError:
                time.sleep(20)
    args.pasta, args.url_base, args.limite = str(PASTA_PUBLICA), URL_PUBLICA, 0
    cmd_fotos(args)


def cmd_preparar_fotos(args):
    """Copia fotos novas da caixa de entrada (site/Fotos) para a pasta publica do site."""
    from PIL import Image, ImageOps
    destino = Path(args.destino)
    destino.mkdir(parents=True, exist_ok=True)
    conhecidas = hashes_publicados() + hashes_descartados() + [dhash(Image.open(p)) for p in imagens(destino)]
    novas = 0
    for arq in imagens(args.origem):
        img = ImageOps.exif_transpose(Image.open(arq)).convert("RGB")
        h = dhash(img)
        if parecida(h, conhecidas):
            continue
        if min(img.size) < 400:
            print(f"pequena demais {img.size}: {arq.name}")
            continue
        img.thumbnail((1600, 1600))
        nome = f"sir-fisher-{dt.datetime.fromtimestamp(arq.stat().st_mtime):%Y%m%d}-{h & 0xFFFFFF:06x}.jpg"
        img.save(destino / nome, "JPEG", quality=86, optimize=True, progressive=True)
        conhecidas.append(h)
        novas += 1
        print(f"preparada: {nome} ({img.size[0]}x{img.size[1]}) <- {arq.name}")
    print(f"{novas} foto(s) nova(s) em {destino}"
          + ("\nRevise, faca commit e push do site e depois rode: gbp.py fotos --publicar" if novas else ""))


def cmd_fotos(args):
    """Importa na ficha as fotos da pasta publica do site que ainda nao estao la.

    O envio direto de bytes (media:startUpload + dataRef) responde HTTP 500 no
    Google; a importacao por URL publica (sourceUrl) funciona. Por isso a foto
    precisa estar publicada no site antes.
    """
    from PIL import Image
    publicadas = hashes_publicados()
    enviados = 0
    for arq in imagens(args.pasta):
        h = dhash(Image.open(arq))
        if parecida(h, publicadas):
            print(f"ja na ficha: {arq.name}")
            continue
        url = args.url_base.rstrip("/") + "/" + urllib.parse.quote(arq.name)
        try:
            urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30)
        except urllib.error.URLError:
            print(f"ainda nao publicada no site (faca push e espere o deploy): {url}")
            continue
        print(f"nova: {arq.name}")
        if not args.publicar or (args.limite and enviados >= args.limite):
            continue
        criado = api("POST", f"{V4}/{CONTA}/{LOCAL}/media", {
            "mediaFormat": "PHOTO",
            "locationAssociation": {"category": args.categoria},
            "sourceUrl": url,
        })
        registrar("foto", None, {"arquivo": arq.name, "url": url, "midia": criado.get("name"),
                                 "categoria": args.categoria})
        publicadas.append(h)
        enviados += 1
        print(f"   publicada: {criado.get('name', '?').split('/')[-1]}")
    if not args.publicar:
        print("\n(simulacao: nada publicado; use --publicar)")


# ----------------------------------------------------------------- instagram

# API oficial da Meta (Instagram Graph API). Token de usuario do sistema do
# Business Manager, so leitura, em META_IG_TOKEN. META_IG_USER_ID e opcional:
# sem ele a conta @sirfisherfc e descoberta pelas paginas do token.
GRAPH = "https://graph.facebook.com/v23.0"
USUARIO_IG = "sirfisherfc"


def graph(caminho, **params):
    tok = credencial("META_IG_TOKEN")
    if not tok:
        sys.exit("META_IG_TOKEN ausente (gestao/.env ou variavel de ambiente)")
    params["access_token"] = tok
    url = f"{GRAPH}/{caminho}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            erro = json.load(e).get("error", {})
        except Exception:
            erro = {}
        # Nunca repassa a URL: ela carrega o token.
        raise ErroApi(e.code, {"mensagem": erro.get("message"), "codigo": erro.get("code"),
                               "tipo": erro.get("type")}) from None


def conta_instagram():
    fixo = credencial("META_IG_USER_ID")
    if fixo:
        return fixo
    paginas = graph("me/accounts", fields="name,instagram_business_account{id,username}").get("data", [])
    contas = [p["instagram_business_account"] for p in paginas if p.get("instagram_business_account")]
    for c in contas:
        if c.get("username") == USUARIO_IG:
            return c["id"]
    if not contas:
        sys.exit("O token nao enxerga nenhuma conta do Instagram ligada a uma pagina.")
    return contas[0]["id"]


def fotos_instagram(dias):
    desde = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=dias)).isoformat()
    campos = "id,caption,media_type,media_url,permalink,timestamp,children{id,media_type,media_url}"
    posts = graph(f"{conta_instagram()}/media", fields=campos, limit=50).get("data", [])
    for p in posts:
        if p.get("timestamp", "") < desde[:19]:
            continue
        if p.get("media_type") == "IMAGE":
            itens = [p]
        elif p.get("media_type") == "CAROUSEL_ALBUM":
            itens = [c for c in p.get("children", {}).get("data", []) if c.get("media_type") == "IMAGE"]
        else:
            continue  # videos e reels ficam de fora
        for i in itens:
            if i.get("media_url"):
                yield {"id": i["id"], "url": i["media_url"], "post": p.get("permalink"),
                       "data": p.get("timestamp", "")[:10],
                       "legenda": (p.get("caption") or "").replace("\n", " ")[:160]}


def cmd_instagram(args):
    """Lista as fotos recentes do Instagram que ainda nao estao na ficha e publica as escolhidas.

    Sem --publicar: baixa cada foto nova em tmp/gbp/instagram/ para ser olhada.
    Com --publicar --itens ID[:CATEGORIA],...: importa na ficha pela URL da Meta.
    """
    from PIL import Image
    pasta = SAIDA / "instagram"
    pasta.mkdir(parents=True, exist_ok=True)
    publicadas = hashes_publicados() + hashes_descartados()
    escolhidas = {}
    for item in filter(None, (args.itens or "").split(",")):
        ident, _, cat = item.strip().partition(":")
        escolhidas[ident] = cat or "FOOD_AND_DRINK"
    novas = 0
    for f in fotos_instagram(args.dias):
        arq = pasta / f"{f['id']}.jpg"
        pedido = urllib.request.Request(f["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(pedido, timeout=60) as r:
            arq.write_bytes(r.read())
        img = Image.open(arq)
        h = dhash(img)
        if parecida(h, publicadas):
            print(f"ja na ficha: {f['id']} ({f['data']})")
            continue
        novas += 1
        print(f"nova: {f['id']} ({f['data']}, {img.size[0]}x{img.size[1]}) arquivo={arq}\n"
              f"   post: {f['post']}\n   legenda: {f['legenda']}")
        if args.publicar and f["id"] in escolhidas:
            if min(img.size) < 400:
                print("   pequena demais: nao publicada")
                continue
            criado = api("POST", f"{V4}/{CONTA}/{LOCAL}/media", {
                "mediaFormat": "PHOTO",
                "locationAssociation": {"category": escolhidas[f["id"]]},
                "sourceUrl": f["url"],
            })
            registrar("foto", None, {"instagram": f["id"], "post": f["post"], "midia": criado.get("name"),
                                     "categoria": escolhidas[f["id"]]})
            publicadas.append(h)
            print(f"   publicada: {criado.get('name', '?').split('/')[-1]}")
    print(f"\n{novas} foto(s) nova(s) do Instagram nos ultimos {args.dias} dias")
    if not args.publicar:
        print("(simulacao: olhe os arquivos e publique com --publicar --itens ID[:CATEGORIA],...)")


# ----------------------------------------------------------------- posts

def cmd_post(args):
    texto = Path(args.arquivo).read_text(encoding="utf-8").strip() if args.arquivo else args.texto.strip()
    problemas = [p for p in validar_resposta(texto) if not p.startswith("link")]
    if len(texto) > 1500:
        problemas.append(f"texto longo demais ({len(texto)} de 1500)")
    corpo = {"languageCode": "pt-BR", "summary": texto, "topicType": "STANDARD"}
    if args.link:
        corpo["callToAction"] = {"actionType": args.acao, "url": args.link}
    if args.foto_url:
        corpo["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": args.foto_url}]
    mostrar("post", "(novo)", corpo)
    if problemas:
        sys.exit("bloqueado: " + "; ".join(problemas))
    if not args.publicar:
        print("\n(simulacao: nada publicado; use --publicar)")
        return
    criado = api("POST", f"{V4}/{CONTA}/{LOCAL}/localPosts", corpo)
    registrar("post", None, corpo, {"post": criado.get("name"), "estado": criado.get("state")})
    print(f"post criado: {criado.get('state')} {criado.get('searchUrl', '')}")


# ----------------------------------------------------------------- metricas

METRICAS = {
    "BUSINESS_IMPRESSIONS_MOBILE_MAPS": "visualizacoes no Maps (celular)",
    "BUSINESS_IMPRESSIONS_DESKTOP_MAPS": "visualizacoes no Maps (computador)",
    "BUSINESS_IMPRESSIONS_MOBILE_SEARCH": "visualizacoes na Busca (celular)",
    "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH": "visualizacoes na Busca (computador)",
    "BUSINESS_DIRECTION_REQUESTS": "pedidos de rota",
    "CALL_CLICKS": "ligacoes",
    "WEBSITE_CLICKS": "cliques no site",
    "BUSINESS_CONVERSATIONS": "conversas",
    "BUSINESS_BOOKINGS": "reservas pelo Google",
    "BUSINESS_FOOD_MENU_CLICKS": "cliques no cardapio",
}


def somar_metricas(inicio, fim):
    faixa = (f"dailyRange.startDate.year={inicio.year}&dailyRange.startDate.month={inicio.month}"
             f"&dailyRange.startDate.day={inicio.day}&dailyRange.endDate.year={fim.year}"
             f"&dailyRange.endDate.month={fim.month}&dailyRange.endDate.day={fim.day}")
    consulta = "&".join(f"dailyMetrics={m}" for m in METRICAS)
    js = api("GET", f"{DESEMPENHO}/{LOCAL}:fetchMultiDailyMetricsTimeSeries?{consulta}&{faixa}")
    totais = {}
    for serie in js.get("multiDailyMetricTimeSeries", []):
        for s in serie.get("dailyMetricTimeSeries", []):
            valores = s.get("timeSeries", {}).get("datedValues", [])
            totais[s["dailyMetric"]] = sum(int(v.get("value", 0)) for v in valores)
    return totais


def cmd_metricas(args):
    fim = dt.date.today() - dt.timedelta(days=3)  # os ultimos dias chegam incompletos
    inicio = fim - dt.timedelta(days=args.dias - 1)
    fim_ant = inicio - dt.timedelta(days=1)
    inicio_ant = fim_ant - dt.timedelta(days=args.dias - 1)
    try:
        atual = somar_metricas(inicio, fim)
        anterior = somar_metricas(inicio_ant, fim_ant)
    except ErroApi as e:
        sys.exit(f"API de desempenho indisponivel: {e}")
    print(f"{inicio:%d/%m} a {fim:%d/%m} (contra {inicio_ant:%d/%m} a {fim_ant:%d/%m})")
    for m, rotulo in METRICAS.items():
        a, b = atual.get(m, 0), anterior.get(m, 0)
        var = f"{(a - b) / b:+.0%}" if b else "  —"
        print(f"  {rotulo:38s} {a:7d}  {var:>6s}")
    if args.palavras:
        mes = fim.replace(day=1)
        ini = (mes - dt.timedelta(days=62)).replace(day=1)
        faixa = (f"monthlyRange.startMonth.year={ini.year}&monthlyRange.startMonth.month={ini.month}"
                 f"&monthlyRange.endMonth.year={mes.year}&monthlyRange.endMonth.month={mes.month}")
        itens, _ = paginado(f"{DESEMPENHO}/{LOCAL}/searchkeywords/impressions/monthly?pageSize=100&{faixa}",
                            "searchKeywordsCounts", max_paginas=1)
        print(f"\nBuscas que mostraram a ficha ({ini:%m/%Y} a {mes:%m/%Y}):")
        for k in itens[:args.palavras]:
            v = k.get("insightsValue", {})
            print(f"  {v.get('value') or ('< ' + str(v.get('threshold'))):>8}  {k.get('searchKeyword')}")


# ----------------------------------------------------------------- checagem

def cmd_checar(args):
    hoje = dt.date.today()
    agora = dt.datetime.now(dt.timezone.utc)
    local = ler_local()
    atributos = {a["name"].split("/")[-1]: a for a in ler_atributos()}
    avaliacoes, resumo = ler_avaliacoes()
    posts = ler_posts()
    fotos = ler_fotos()
    tarefas = []

    pend = [a for a in avaliacoes if not a.get("reviewReply") and a["createTime"][:10] >= "2025-01-01"]
    for a in pend:
        horas = (agora - dt.datetime.fromisoformat(a["createTime"].replace("Z", "+00:00"))).total_seconds() / 3600
        tarefas.append(f"RESPONDER avaliacao {NOTA.get(a.get('starRating'))}* de "
                       f"{a.get('reviewer', {}).get('displayName', '')} ({horas:.0f}h) | {a['reviewId']}")
    for a in avaliacoes:
        resposta = (a.get("reviewReply") or {}).get("comment", "")
        if any(t in resposta for t in TELEFONES_PROIBIDOS):
            tarefas.append(f"CORRIGIR resposta com telefone pessoal | {a['reviewId']}")

    datas_post = sorted(p.get("createTime", "")[:10] for p in posts)
    ultimo_post = datas_post[-1] if datas_post else None
    if not ultimo_post or (hoje - dt.date.fromisoformat(ultimo_post)).days >= 7:
        tarefas.append(f"POSTAR: ultimo post em {ultimo_post or 'nunca'}")
    datas_foto = sorted(m.get("createTime", "")[:10] for m in fotos if m.get("createTime"))
    ultima_foto = datas_foto[-1] if datas_foto else None
    if not ultima_foto or (hoje - dt.date.fromisoformat(ultima_foto)).days >= 30:
        tarefas.append(f"FOTOS: ultima foto em {ultima_foto or 'nunca'}")

    especiais = {(p["startDate"]["year"], p["startDate"]["month"], p["startDate"]["day"])
                 for p in local.get("specialHours", {}).get("specialHourPeriods", [])}
    faltando = [f"{d:%d/%m} {n}" for d, n in feriados(hoje, hoje + dt.timedelta(days=45)).items()
                if (d.year, d.month, d.day) not in especiais]
    if faltando:
        tarefas.append("FERIADOS sem horario: " + ", ".join(faltando))

    if "utm_source" not in local.get("websiteUri", ""):
        tarefas.append("SITE sem UTM na ficha")
    if "url_reservations" not in atributos:
        tarefas.append("RESERVA: link de reserva ausente")
    if local.get("phoneNumbers", {}).get("primaryPhone") != TELEFONE:
        tarefas.append(f"TELEFONE da ficha diferente de {TELEFONE}")
    if local.get("openInfo", {}).get("status") != "OPEN":
        tarefas.append(f"ATENCAO: ficha com status {local.get('openInfo', {}).get('status')}")

    print(f"Ficha: {local.get('title')} | {resumo.get('totalReviewCount')} avaliacoes, "
          f"media {resumo.get('averageRating', 0):.2f}")
    recentes = [a for a in avaliacoes if a["createTime"][:10] >= (hoje - dt.timedelta(days=30)).isoformat()]
    print(f"Ultimos 30 dias: {len(recentes)} avaliacoes novas (meta: 50/mes)")
    print(f"Ultimo post: {ultimo_post or 'nunca'} | ultima foto: {ultima_foto or 'nunca'}")
    for p in sorted(posts, key=lambda p: p.get("createTime", ""))[-4:]:
        print(f"  post {p.get('createTime', '')[:10]} [{p.get('state')}]: {p.get('summary', '')[:90]}")
    print("\nTarefas de hoje:" if tarefas else "\nNada pendente hoje.")
    for t in tarefas:
        print(f"- {t}")


# ----------------------------------------------------------------- main

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Perfil da Empresa no Google (Sir Fisher)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("backup")
    sub.add_parser("checar")

    s = sub.add_parser("pendentes")
    s.add_argument("--desde", default="2025-01-01")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("responder")
    s.add_argument("id", nargs="?")
    s.add_argument("--texto")
    s.add_argument("--arquivo")
    s.add_argument("--lote", help="JSON com [{id, texto}]")
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("aplicar")
    s.add_argument("plano")
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("feriados")
    s.add_argument("--dias", type=int, default=120)
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("preparar-fotos")
    s.add_argument("--origem", default=str(PASTA_FOTOS))
    s.add_argument("--destino", default=str(PASTA_PUBLICA))

    s = sub.add_parser("instagram")
    s.add_argument("--dias", type=int, default=8)
    s.add_argument("--itens", help="IDs escolhidos, com categoria opcional: ID[:CATEGORIA],...")
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("descartar-foto")
    s.add_argument("nome")
    s.add_argument("--motivo", required=True)

    s = sub.add_parser("publicar-fotos")
    s.add_argument("--categoria", default="FOOD_AND_DRINK",
                   choices=["FOOD_AND_DRINK", "EXTERIOR", "INTERIOR", "AT_WORK", "TEAMS",
                            "COMMON_AREA", "ADDITIONAL", "MENU"])
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("fotos")
    s.add_argument("pasta", nargs="?", default=str(PASTA_PUBLICA))
    s.add_argument("--url-base", default=URL_PUBLICA)
    s.add_argument("--categoria", default="FOOD_AND_DRINK",
                   choices=["FOOD_AND_DRINK", "EXTERIOR", "INTERIOR", "AT_WORK", "TEAMS",
                            "COMMON_AREA", "ADDITIONAL", "MENU"])
    s.add_argument("--limite", type=int, default=0)
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("post")
    s.add_argument("--texto")
    s.add_argument("--arquivo")
    s.add_argument("--link")
    s.add_argument("--acao", default="LEARN_MORE", choices=["LEARN_MORE", "BOOK", "ORDER", "CALL"])
    s.add_argument("--foto-url")
    s.add_argument("--publicar", action="store_true")

    s = sub.add_parser("metricas")
    s.add_argument("--dias", type=int, default=28)
    s.add_argument("--palavras", type=int, default=0)

    args = p.parse_args()
    if args.cmd == "responder" and not (args.lote or (args.id and (args.texto or args.arquivo))):
        p.error("responder: informe id com --texto/--arquivo, ou --lote")
    if args.cmd == "post" and not (args.texto or args.arquivo):
        p.error("post: informe --texto ou --arquivo")
    comandos = {
        "backup": cmd_backup, "checar": cmd_checar, "pendentes": cmd_pendentes,
        "responder": cmd_responder, "aplicar": cmd_aplicar, "feriados": cmd_feriados,
        "instagram": cmd_instagram,
        "preparar-fotos": cmd_preparar_fotos, "descartar-foto": cmd_descartar_foto,
        "publicar-fotos": cmd_publicar_fotos, "fotos": cmd_fotos,
        "post": cmd_post, "metricas": cmd_metricas,
    }
    try:
        return comandos[args.cmd](args) or 0
    except ErroApi as e:
        print(f"\nERRO da API: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
