# -*- coding: utf-8 -*-
"""
Exporta a copia publica do cardapio.

Esta e a UNICA funcao que decide o que o cliente enxerga. Tudo o que nao
estiver montado aqui simplesmente nao existe para o portal: notas internas,
fontes, pendencias, estados de revisao, alegacoes a conferir, produtos em
rascunho e custos.

Dois modos, mesma saida:

  --de-arquivo   le catalogo_inicial.json (a semente). Usado enquanto o banco
                 ainda nao foi populado.
  --do-banco     le a publicacao ativa em cardapio_publicacao via API REST do
                 Supabase, com a chave anonima. E o modo de producao: a copia
                 estatica passa a ser uma saida derivada da publicacao, nunca
                 uma segunda base editada a mao.

A copia estatica existe para a primeira pintura e para o cliente com conexao
ruim. O portal sempre tenta a leitura ao vivo depois e troca o conteudo se a
versao publicada for mais nova.
"""

import argparse
import json
import os
import sys
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SEMENTE = os.path.join(AQUI, "catalogo_inicial.json")

SUPABASE_URL = "https://lucpxoynpvogkvzepagi.supabase.co"

# Estados de porcao internos -> o que o cliente le.
PORCAO_PUBLICA = {
    "declarado": "informada",
    "parcial": "informada",
    "divergente": "em_conferencia",
    "ausente": "nao_informada",
}

# Estados alimentares internos -> o que o cliente le.
ALIMENTAR_PUBLICA = {
    "declarado_no_impresso": "declarado",
    "sem_simbolos": "sem_marcacoes",
    "nao_revisado": "nao_revisado",
}

TEXTO_ALIMENTAR = {
    "declarado": (
        "Marcações transcritas do cardápio impresso, ainda não conferidas com "
        "a cozinha. Consulte a equipe sobre alérgenos."
    ),
    "sem_marcacoes": (
        "Este item não tem marcações no cardápio impresso. Isso não significa "
        "ausência de alérgenos. Consulte a equipe."
    ),
    "nao_revisado": (
        "Informação alimentar ainda não revisada para este item. Consulte a "
        "equipe."
    ),
}


def porcao_publica(porcao):
    estado = PORCAO_PUBLICA.get(porcao.get("estado"), "nao_informada")
    # Porcao divergente nunca vira numero na tela: as fontes se contradizem e
    # escolher uma delas seria inventar um fato.
    texto = porcao.get("texto") if estado == "informada" else None
    # Caso do Fisher Burger: a medida existe na fonte (120 g) mas nenhuma
    # fonte diz se e o total ou o peso de cada fatia, entao o catalogo guarda
    # a divergencia e deixa o texto vazio. Sem texto nao ha o que informar --
    # o cliente le "em conferencia" e pergunta ao garcom.
    if estado == "informada" and not texto:
        estado = "em_conferencia" if porcao.get("divergencia") else "nao_informada"
    detalhes = []
    principal = porcao.get("principal")
    total = porcao.get("total")
    unidades = porcao.get("unidades")
    if unidades:
        detalhes.append("%d %s" % (unidades["quantidade"], unidades["rotulo"]))
    if principal:
        rotulo = {"proteina": "de proteína", "conjunto": "do prato montado"}
        detalhes.append(("%s %s %s" % (
            principal["valor"], principal["unidade"],
            rotulo.get(principal["alcance"], ""))).strip())
    if total:
        detalhes.append("%s %s no total" % (total["valor"], total["unidade"]))
    # O detalhamento so aparece quando diz algo alem da linha principal.
    # Repetir "250 g" logo abaixo de "250 g" nao informa nada e ainda faz o
    # cliente reler para conferir se ha diferenca.
    if estado != "informada" or len(detalhes) < 2:
        detalhes = []
    return {
        "texto": texto,
        "detalhes": detalhes,
        "nota": porcao.get("nota"),
        "estado": estado,
    }


def alimentar_publica(alimentar):
    estado = ALIMENTAR_PUBLICA.get(alimentar.get("estado"), "nao_revisado")
    return {
        "declarados": list(alimentar.get("declarados") or []),
        "estado": estado,
        "texto": TEXTO_ALIMENTAR[estado],
        # confirmado_cozinha so aparece quando a cozinha tiver validado. Ate la
        # a lista e vazia e o portal nao afirma compatibilidade nenhuma.
        "confirmado": list(alimentar.get("confirmado_cozinha") or []),
        "contato_cruzado": list(alimentar.get("contato_cruzado") or []),
    }


def produto_publico(prod):
    return {
        "id": prod["id"],
        "categoria": prod["categoria"],
        "subgrupo": prod["subgrupo"],
        "ordem": prod["ordem"],
        "nome": prod["nome"],
        "descritor": prod["descritor"],
        "descricao": prod["descricao"],
        "detalhe": prod["detalhe"],
        "preco": prod["preco"],
        "variantes": [{"nome": v["nome"], "preco_centavos": v["preco_centavos"]}
                      for v in prod["variantes"]],
        "adicionais": [{"nome": a["nome"], "preco_centavos": a["preco_centavos"]}
                       for a in prod["adicionais"]],
        "inclui": prod["inclui"],
        "opcoes": [{"texto": o["texto"]} for o in prod["opcoes"] if o.get("texto")],
        "porcao": porcao_publica(prod["porcao"]),
        "alimentar": alimentar_publica(prod["alimentar"]),
        "foto": ({"base": prod["foto"]["base"],
                  "larguras": prod["foto"]["larguras"],
                  "alt": prod["foto"]["alt"]} if prod.get("foto") else None),
        "etiquetas": prod["etiquetas"],
        "busca": prod["indice_busca"],
        "disponivel": prod["disponivel"],
    }


def resumo_categoria(cat, produtos):
    """Cabecalho factual da categoria: quantas opcoes e de quanto a quanto.

    Ajuda quem chega com um orcamento em mente. Sai inteiro dos precos
    cadastrados; nao classifica nada como barato, caro ou vantajoso.
    """
    da_cat = [x for x in produtos if x["categoria"] == cat["id"]
              and x["preco"]["centavos"] is not None]
    if not da_cat:
        return None
    valores = []
    for x in da_cat:
        if x["preco"]["tipo"] == "faixa":
            valores += [x["preco"]["min"], x["preco"]["max"]]
        else:
            valores.append(x["preco"]["centavos"])
    return {"itens": len(da_cat), "min": min(valores), "max": max(valores)}


def montar(catalogo, versao, publicado_em):
    publicados = [x for x in catalogo["produtos"] if x["publicar"]]
    produtos = [produto_publico(x) for x in publicados]
    categorias = []
    for cat in catalogo["categorias"]:
        item = {
            "id": cat["id"],
            "nome": cat["nome"],
            "resumo": cat["resumo"],
            "grupo": cat["grupo"],
            "subgrupos": cat["subgrupos"],
        }
        item["faixa"] = resumo_categoria(cat, produtos)
        categorias.append(item)

    return {
        "versao": versao,
        "publicado_em": publicado_em,
        "estado": catalogo["estado_catalogo"],
        # Curto de proposito: ocupa a primeira tela do celular e precisa caber
        # em duas linhas sem empurrar os produtos para baixo da dobra.
        "aviso_estado": (
            "Cardápio em conferência. Confirme preços e porções com a equipe."
        ) if catalogo["estado_catalogo"] != "vigente" else None,
        "moeda": catalogo["moeda"],
        "avisos": [{"id": a["id"], "titulo": a["titulo"], "texto": a["texto"]}
                   for a in catalogo["avisos"]],
        "categorias": categorias,
        "produtos": produtos,
    }


def ler_do_banco():
    """Le a publicacao ativa pela API publica, com a chave anonima.

    So enxerga a view cardapio_publico, que por construcao devolve apenas o
    conteudo publicado. Nenhuma chave privilegiada entra aqui.
    """
    chave = os.environ.get("SUPABASE_ANON_KEY")
    if not chave:
        sys.exit("Defina SUPABASE_ANON_KEY para exportar do banco.")
    url = "%s/rest/v1/cardapio_publico?select=versao,publicado_em,conteudo" % SUPABASE_URL
    req = urllib.request.Request(url, headers={
        "apikey": chave,
        "Authorization": "Bearer %s" % chave,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        linhas = json.loads(resp.read().decode("utf-8"))
    if not linhas:
        sys.exit("Nenhuma publicação ativa encontrada.")
    linha = linhas[0]
    return linha["conteudo"], linha["versao"], linha["publicado_em"]


def jsonld(publico):
    """Dados estruturados do cardapio, derivados da mesma publicacao.

    So entra o que ja esta publico na pagina. Variante vira uma oferta com
    nome; adicional NAO vira oferta, senao um agregador poderia anunciar o
    sanduiche de R$ 37,00 pelos R$ 9,90 da batata. Item indisponivel sai com
    availability SoldOut em vez de sumir.
    """
    por_categoria = {}
    for prod in publico["produtos"]:
        por_categoria.setdefault(prod["categoria"], []).append(prod)

    secoes = []
    for cat in publico["categorias"]:
        itens = []
        for prod in por_categoria.get(cat["id"], []):
            disp = ("https://schema.org/InStock" if prod["disponivel"]
                    else "https://schema.org/SoldOut")
            if prod["variantes"]:
                ofertas = [{
                    "@type": "Offer",
                    "name": v["nome"],
                    "price": "%.2f" % (v["preco_centavos"] / 100.0),
                    "priceCurrency": publico["moeda"],
                    "availability": disp,
                } for v in prod["variantes"]]
            elif prod["preco"]["centavos"] is not None:
                ofertas = [{
                    "@type": "Offer",
                    "price": "%.2f" % (prod["preco"]["centavos"] / 100.0),
                    "priceCurrency": publico["moeda"],
                    "availability": disp,
                }]
            else:
                ofertas = []

            item = {"@type": "MenuItem", "name": prod["nome"]}
            descricao = " ".join(x for x in [prod.get("descricao"),
                                             prod["porcao"].get("texto")] if x)
            if descricao:
                item["description"] = descricao
            if ofertas:
                item["offers"] = ofertas if len(ofertas) > 1 else ofertas[0]
            itens.append(item)
        if itens:
            secoes.append({"@type": "MenuSection", "name": cat["nome"],
                           "description": cat.get("resumo"),
                           "hasMenuItem": itens})

    return {
        "@context": "https://schema.org",
        "@type": "Menu",
        "name": "Cardápio do Sir Fisher",
        "inLanguage": "pt-BR",
        "hasMenuSection": secoes,
    }


def trocar_bloco(html, marcador, conteudo):
    inicio = "<!-- %s:INICIO -->" % marcador
    fim = "<!-- %s:FIM -->" % marcador
    a = html.find(inicio)
    b = html.find(fim)
    if a == -1 or b == -1 or b < a:
        sys.exit("Marcador %s não encontrado em index.html." % marcador)
    return html[:a + len(inicio)] + "\n" + conteudo + "\n  " + html[b:]


def escrever_pagina(caminho, publico):
    """Escreve o catálogo e o Schema.org dentro do index.html do portal.

    A página passa a servir o catálogo já embutido: uma requisição a menos
    antes da primeira pintura. Continua sendo uma saída derivada da
    publicação, nunca uma segunda base que alguém edita a mão.
    """
    with open(caminho, encoding="utf-8") as arq:
        html = arq.read()

    dados = json.dumps(publico, ensure_ascii=False, separators=(",", ":"))
    # </script> dentro de JSON fecharia a tag cedo demais.
    dados = dados.replace("</", "<\\/")
    html = trocar_bloco(
        html, "CARDAPIO-DADOS",
        '  <script type="application/json" id="cardapio-dados">%s</script>' % dados)
    html = trocar_bloco(
        html, "MENU-JSONLD",
        '  <script type="application/ld+json">%s</script>'
        % json.dumps(jsonld(publico), ensure_ascii=False,
                     separators=(",", ":")).replace("</", "<\\/"))

    with open(caminho, "w", encoding="utf-8", newline="\n") as arq:
        arq.write(html)
    return os.path.getsize(caminho)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--do-banco", action="store_true",
                    help="lê a publicação ativa no Supabase")
    ap.add_argument("--versao", type=int, default=1)
    ap.add_argument("--saida", default=os.path.join(
        AQUI, "..", "..", "..", "site", "cardapio", "dados", "cardapio.json"))
    ap.add_argument("--pagina", default=os.path.join(
        AQUI, "..", "..", "..", "site", "cardapio", "index.html"))
    args = ap.parse_args()

    if args.do_banco:
        conteudo, versao, publicado_em = ler_do_banco()
        # A publicacao ja e a copia publica: o banco aplica o mesmo recorte.
        saida = conteudo
        saida["versao"] = versao
        saida["publicado_em"] = publicado_em
    else:
        with open(SEMENTE, encoding="utf-8") as arq:
            catalogo = json.load(arq)
        saida = montar(catalogo, args.versao,
                       catalogo["gerado_em"] + "T12:00:00-03:00")

    destino = os.path.abspath(args.saida)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as arq:
        json.dump(saida, arq, ensure_ascii=False, separators=(",", ":"))

    proibidos = ("notas_internas", "fontes", "pendencias", "alegacoes",
                 "preco_estado", "divergencia", "confirmado_cozinha",
                 "publicar", "nome_original", "termos")
    bruto = json.dumps(saida, ensure_ascii=False)
    vazados = [c for c in proibidos if '"%s"' % c in bruto]
    if vazados:
        sys.exit("Campos internos vazaram para a cópia pública: %s"
                 % ", ".join(vazados))

    print("Snapshot: %s (%d KB)" % (destino, os.path.getsize(destino) // 1024))

    pagina = os.path.abspath(args.pagina)
    if os.path.exists(pagina):
        tamanho = escrever_pagina(pagina, saida)
        print("Página:   %s (%d KB)" % (pagina, tamanho // 1024))

    print("Versão %s · %d produtos publicados" % (saida["versao"], len(saida["produtos"])))


if __name__ == "__main__":
    main()
