# -*- coding: utf-8 -*-
"""
Gera docs/CARDAPIO_CONFERENCIA.md a partir de catalogo_inicial.json.

E a lista de tudo o que o restaurante precisa confirmar antes de o cardapio
deixar de ser "em conferencia": divergencias entre as fontes, campos pendentes,
matriz alimentar com a proveniencia de cada declaracao e as fotos que faltam.

O documento e gerado, nao escrito a mao. Assim ele nunca diverge do catalogo
que alimenta o portal: mudou o dado, roda de novo.
"""

import json
import os
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEM = os.path.join(AQUI, "catalogo_inicial.json")
DESTINO = os.path.join(AQUI, "..", "..", "docs", "CARDAPIO_CONFERENCIA.md")

ROTULO_PENDENCIA = {
    "porcao": "Porção", "preco": "Preço", "foto": "Foto", "nome": "Nome",
    "alimentar": "Informação alimentar", "opcoes": "Opções",
    "vigencia": "Vigência do produto", "rendimento": "Rendimento",
    "classificacao": "Classificação", "descricao": "Descrição",
    "alegacao": "Alegação a conferir", "regra": "Regra de cobrança",
}


def dinheiro(centavos):
    if centavos is None:
        return "—"
    return "R$ %s" % ("%.2f" % (centavos / 100.0)).replace(".", ",")


def main():
    with open(ORIGEM, encoding="utf-8") as arq:
        cat = json.load(arq)

    prods = cat["produtos"]
    por_id = {p["id"]: p for p in prods}
    linhas = []
    w = linhas.append

    w("# Cardápio — o que falta conferir")
    w("")
    w("Documento **gerado** por `scripts/cardapio/gerar_conferencia.py` a partir")
    w("de `scripts/cardapio/catalogo_inicial.json`. Não editar à mão: corrija o")
    w("catálogo (ou o próprio cardápio, em Gestão → Rotinas → Cardápio) e gere")
    w("de novo.")
    w("")
    w("O catálogo foi reconciliado em %s a partir de três fontes:" % cat["gerado_em"])
    w("")
    w("| Fonte | O que é | Peso que recebeu |")
    w("|---|---|---|")
    w("| **TXT** | `site/cardapio/cardapio.txt`, o cadastro com 81 registros | Lista fechada. Nada entra no cardápio publicado sem estar aqui. |")
    w("| **HTML** | `site/cardapio/index.html`, a página antiga | Completa nomes truncados, descrições e variantes. Declara preços “conferidos em 07/09/2026”. |")
    w("| **Impresso** | `Sir Fisher Praia.pdf` | Autorizado só como fonte de texto e de declarações alimentares. Preços do impresso **não** substituíram o cadastro. |")
    w("")
    w("**Nada nesta lista foi validado pela cozinha ou pela operação.** Enquanto")
    w("isso não acontecer, o portal mostra o aviso *“Cardápio em conferência”* e")
    w("cada campo duvidoso sai como *“em conferência”*, nunca como número.")
    w("")
    w("Regras que o catálogo aplicou, sem exceção:")
    w("")
    w("1. Divergência entre fontes nunca foi resolvida por automatismo. O campo")
    w("   deixa de ser exibido como fato.")
    w("2. Omissão numa fonte não apagou o dado de outra.")
    w("3. Adicional nunca virou preço do produto.")
    w("4. Símbolo alimentar só foi transcrito quando visível e com legenda clara.")
    w("   Ausência de símbolo não virou ausência de alérgeno.")
    w("5. Peso nunca virou número de pessoas.")
    w("")

    # ------------------------------------------------------------------
    w("## 1. Divergências entre as fontes")
    w("")
    w("Cada linha é uma pergunta para a cozinha ou para o caixa. Enquanto não")
    w("houver resposta, o portal não mostra o dado.")
    w("")
    w("| Produto | Assunto | O que cada fonte diz | O que o cliente vê hoje |")
    w("|---|---|---|---|")

    def visivel(p, assunto):
        if assunto == "Porção":
            est = p["porcao"]["estado"]
            if est == "divergente":
                return "“Porção em conferência”"
            if est == "parcial" and p["porcao"]["texto"]:
                return "“%s”" % p["porcao"]["texto"]
            if est == "ausente":
                return "nada sobre porção"
            return "“%s”" % (p["porcao"]["texto"] or "—")
        return "—"

    for p in prods:
        if p["porcao"].get("divergencia"):
            w("| %s | Porção | %s | %s |" % (
                p["nome"], p["porcao"]["divergencia"].replace("|", "/"),
                visivel(p, "Porção")))
    # Só entra aqui o que ainda é uma decisão em aberto. Nome truncado que o
    # HTML e o impresso completam do mesmo jeito já está resolvido: vira ruído
    # numa pauta de cozinha. Fica registrado no produto, não nesta lista.
    ABERTAS = [
        ("london-fish-n-chips", "Nome",
         "Cadastro e HTML: “London”. Impresso: “Original”. A descrição coincide.",
         "“London — Fish & Chips”"),
        ("patinha-de-caranguejo", "Nome",
         "Cadastro: “Patinha de caranguejo”. Impresso: “PATA DE CARANGUEJO”.",
         "“Patinha de Caranguejo”"),
        ("sherlock-holmes-gin", "Receita",
         "HTML: Monster. Impresso: Red Bull Zero e xarope de gengibre.",
         "“gin com energético e gengibre”, sem marca"),
        ("moscow-mule", "Receita",
         "O impresso acrescenta refrigerante de limão, que o cadastro não cita.",
         "a descrição do cadastro"),
        ("marine-sandwich", "Ingrediente",
         "Cadastro e HTML citam pepino; o impresso não cita. Omissão não retira ingrediente.",
         "com pepino"),
        ("newcastle", "Acompanhamento",
         "Cadastro e HTML citam batatas; o impresso não cita acompanhamento.",
         "com porção de batatas"),
        ("budweiser-600", "Vigência",
         "Está no cadastro e no HTML, mas não foi encontrado no impresso.",
         "publicado normalmente"),
        ("margarita", "Vigência",
         "Está no cadastro e no HTML, mas não foi encontrado no impresso.",
         "publicado normalmente"),
        ("corona-zero-longneck", "Classificação",
         "O impresso escreve “CORONA ZERO%”. Se for sem álcool, merece etiqueta própria.",
         "só entre as cervejas"),
        ("sumo-de-limao", "Classificação",
         "O impresso lista em BEBIDAS com 50 mL, mas pode ser complemento de drink.",
         "entre as bebidas sem álcool"),
        ("pasteizinhos", "Opções",
         "Nenhuma fonte diz se dá para misturar os três sabores numa porção.",
         "“Sabor a escolher”, sem dizer se mistura"),
        ("cafe-expresso", "Porção",
         "Os 50 mL vêm do cadastro; o impresso não informa volume.",
         "“50 mL”"),
    ]
    for pid, assunto, texto, hoje in ABERTAS:
        prod = por_id.get(pid)
        if prod:
            w("| %s | %s | %s | %s |"
              % (prod["nome"], assunto, texto.replace("|", "/"), hoje))
    w("| Os seis pratos para compartilhar | Rendimento | O impresso declara "
      "300 g de proteína e “peso in natura”. Nenhuma fonte diz quantas pessoas "
      "o prato serve. | “300 g de proteína”, sem número de pessoas |")
    w("")
    w("Já resolvidos pelas fontes, sem pendência: os dois nomes truncados no")
    w("cadastro (“Crocante de Carne de Sol com…” e “Crocante de Calabresa e")
    w("Alho…”) foram completados pelo HTML e pelo impresso, que coincidem.")
    w("")

    # ------------------------------------------------------------------
    w("## 2. Campos pendentes, por produto")
    w("")
    pend = [p for p in prods if p["pendencias"]]
    w("%d produtos têm ao menos um campo a confirmar." % len(pend))
    w("")
    agrupado = defaultdict(list)
    for p in pend:
        for x in p["pendencias"]:
            agrupado[x].append(p["nome"])
    w("| Campo | Produtos | Quantos |")
    w("|---|---|---:|")
    for campo in sorted(agrupado, key=lambda k: -len(agrupado[k])):
        nomes = agrupado[campo]
        mostra = ", ".join(nomes[:8]) + ("…" if len(nomes) > 8 else "")
        w("| %s | %s | %d |" % (ROTULO_PENDENCIA.get(campo, campo), mostra,
                                len(nomes)))
    w("")

    # ------------------------------------------------------------------
    w("## 3. Matriz de declarações alimentares, com proveniência")
    w("")
    w("A legenda do cardápio impresso tem dez rótulos: **LACTOSE, CASTANHAS,")
    w("PEIXE, CORANTES, GLÚTEN, SOJA, LEITE, OVO, CRUSTÁCEOS e AMÊNDOAS**.")
    w("LACTOSE e LEITE são rótulos distintos no documento e continuam distintos")
    w("aqui: não foram fundidos numa taxonomia regulatória de alérgenos.")
    w("")
    w("CASTANHAS, SOJA, LEITE e AMÊNDOAS aparecem na legenda mas não foram")
    w("identificados junto a nenhum dos 26 pratos da página 1. Isso **não**")
    w("indica que esses componentes estejam ausentes das receitas.")
    w("")
    w("O rodapé traz o aviso geral **“ALÉRGICOS: PODE CONTER CAMARÃO E")
    w("GLÚTEN”**. Ele ficou guardado como aviso do documento e **não** foi")
    w("transformado em presença confirmada nem em contato cruzado de item algum.")
    w("")
    w("Estado de cada declaração:")
    w("")
    w("- `declarado no impresso` — símbolo visível no cardápio físico, transcrito.")
    w("- `sem marcações` — o produto aparece no impresso sem símbolos. **Não**")
    w("  significa ausência de alérgenos.")
    w("- `não revisado` — nenhuma fonte trouxe informação alimentar.")
    w("")
    w("Nenhum item tem, hoje, `confirmado pela cozinha` ou `contato cruzado")
    w("confirmado`. Essas duas colunas só se preenchem com ficha técnica e")
    w("ingredientes dos fornecedores.")
    w("")
    w("| Produto | Declarado no impresso | Estado | Divergência registrada |")
    w("|---|---|---|---|")
    estados = {"declarado_no_impresso": "declarado no impresso",
               "sem_simbolos": "sem marcações", "nao_revisado": "não revisado"}
    for p in prods:
        a = p["alimentar"]
        if a["estado"] == "sem_simbolos" and not a["divergencias"]:
            continue
        w("| %s | %s | %s | %s |" % (
            p["nome"], ", ".join(a["declarados"]) or "—",
            estados.get(a["estado"], a["estado"]),
            " ".join(a["divergencias"]).replace("|", "/") or "—"))
    w("")
    semsimbolo = [p["nome"] for p in prods
                  if p["alimentar"]["estado"] == "sem_simbolos"
                  and not p["alimentar"]["divergencias"]]
    w("Sem marcações no impresso (%d itens, quase todos bebidas e sobremesas): %s."
      % (len(semsimbolo), ", ".join(semsimbolo)))
    w("")
    w("### Alegações do impresso que **não** foram publicadas")
    w("")
    for p in prods:
        for al in p["alimentar"].get("alegacoes", []):
            w("- **%s** — “%s” (%s). %s" % (p["nome"], al["texto"], al["fonte"],
                                            al["nota"]))
    w("")

    # ------------------------------------------------------------------
    w("## 4. Preço, variantes e adicionais")
    w("")
    w("O caso que motivou a trava: no HTML antigo, a primeira oferta estruturada")
    w("dos três sanduíches é a batata de R$ 9,90, e o preço do sanduíche vem")
    w("depois. Um importador que pegasse a primeira ou a menor oferta anunciaria")
    w("um sanduíche de R$ 37,00 por R$ 9,90. O catálogo separa os dois e o editor")
    w("recusa salvar um adicional que custe igual ou mais que o produto.")
    w("")
    w("| Produto | Preço do produto | Adicionais (cobrados à parte) |")
    w("|---|---|---|")
    for p in prods:
        if p["adicionais"]:
            w("| %s | %s | %s |" % (
                p["nome"], dinheiro(p["preco_centavos"]),
                ", ".join("%s %s" % (a["nome"], dinheiro(a["preco_centavos"]))
                          for a in p["adicionais"])))
    w("")
    w("| Produto com variantes | Faixa exibida na lista | Opções |")
    w("|---|---|---|")
    for p in prods:
        if p["variantes"]:
            vals = [v["preco_centavos"] for v in p["variantes"]]
            faixa = (dinheiro(min(vals)) if min(vals) == max(vals)
                     else "%s a %s" % (dinheiro(min(vals)), dinheiro(max(vals))))
            w("| %s | %s | %s |" % (p["nome"], faixa,
                                    ", ".join("%s %s" % (v["nome"], dinheiro(v["preco_centavos"]))
                                              for v in p["variantes"])))
    w("")

    # ------------------------------------------------------------------
    w("## 5. Produtos que existem só numa fonte")
    w("")
    w("Não foram excluídos nem promovidos. Ficam como decisão da operação.")
    w("")
    w("| Produto | Situação | Encaminhamento |")
    w("|---|---|---|")
    for p in prods:
        if not p["publicar"]:
            w("| %s | Rascunho, fora do portal | %s |" % (
                p["nome"], " ".join(p["notas_internas"]).replace("|", "/")))
    for p in prods:
        if "vigencia" in p["pendencias"] and p["publicar"]:
            w("| %s | Publicado | %s |" % (
                p["nome"], " ".join(p["notas_internas"]).replace("|", "/")))
    w("")

    # ------------------------------------------------------------------
    w("## 6. Fotografias")
    w("")
    com = [p for p in prods if p.get("foto")]
    comer = [p for p in prods
             if p["categoria"] in ("fish-and-chips", "petiscos", "sanduiches",
                                   "para-dividir", "sobremesas")]
    sem = [p for p in comer if not p.get("foto")]
    w("Das %d fotos de produto disponíveis em `site/assets/img/`, %d foram"
      % (12, len(com)))
    w("atribuídas depois de inspeção visual. Nenhum prato recebeu a foto de")
    w("outro para tapar buraco: quem não tem foto aparece com o brasão, num")
    w("tratamento igual para todos.")
    w("")
    w("### Atribuídas")
    w("")
    w("| Produto | Arquivo | Estado |")
    w("|---|---|---|")
    for p in prods:
        if p.get("foto"):
            f = p["foto"]
            w("| %s | `%s` | %s |" % (
                p["nome"], f["base"],
                "conferida" if f.get("estado") == "conferido"
                else "**a confirmar** — " + f.get("nota", "")))
    w("")
    w("### Fotos existentes sem produto correspondente")
    w("")
    for f in cat["fotos_sem_destino"]:
        w("- **`%s`** — %s %s *%s*" % (f["arquivo"], f["observado"],
                                       f["motivo"], f["encaminhamento"]))
    w("")
    w("### Pratos a fotografar (%d)" % len(sem))
    w("")
    w("Só pratos; bebidas e doses não precisam de foto no portal.")
    w("")
    for p in sem:
        w("- %s (%s)" % (p["nome"], dinheiro(p["preco_centavos"])))
    w("")
    w("**Orientação de captura**, para as novas combinarem com as 12 que já")
    w("existem: luz natural, prato montado como sai para a mesa, fundo de")
    w("madeira escura ou o papel da casa, câmera a 45° para prato fundo e a 90°")
    w("para travessa, mesmo enquadramento do conjunto atual. Enviar em JPEG ou")
    w("WebP com pelo menos 1320 px no lado maior — o portal recorta em quadrado")
    w("na listagem e em 4:3 no detalhe. A foto entra pelo próprio editor, em")
    w("Gestão → Rotinas → Cardápio.")
    w("")

    # ------------------------------------------------------------------
    w("## 7. Ordem sugerida para a conferência")
    w("")
    w("1. **Preços.** São 81. É o que impede o cardápio de ir ao ar. Conferir")
    w("   contra o PDV, não contra o impresso.")
    w("2. **Disponibilidade.** Marcar o que não existe mais. A ação é imediata e")
    w("   não precisa de publicação.")
    w("3. **As %d divergências de porção.** Principalmente os dois Fish & Chips"
      % len([p for p in prods if p["porcao"].get("divergencia")]))
    w("   (150 g × 200 g) e a Bolinha de Peixe (300 g × 200 g).")
    w("4. **Alcance dos pesos.** “300 g” é da proteína, do prato montado, cru ou")
    w("   pronto? O rodapé do impresso diz “peso in natura”; confirmar onde vale.")
    w("5. **Rendimento dos pratos para compartilhar.** Nenhuma fonte diz quantas")
    w("   pessoas servem. Enquanto não houver resposta, o portal não afirma nada.")
    w("6. **Informação alimentar.** Ficha técnica e ingredientes dos")
    w("   fornecedores, incluindo óleo e equipamento compartilhados. Resolver as")
    w("   duas divergências de símbolo (Patinha de Caranguejo sem CRUSTÁCEOS,")
    w("   Bolinha de Peixe sem PEIXE).")
    w("7. **Fotos** dos %d pratos que faltam." % len(sem))
    w("8. **Marcar como conferido** no editor. O aviso sai do portal.")
    w("")

    destino = os.path.abspath(DESTINO)
    with open(destino, "w", encoding="utf-8", newline="\n") as arq:
        arq.write("\n".join(linhas))
    print("Conferência: %s (%d KB)" % (destino, os.path.getsize(destino) // 1024))


if __name__ == "__main__":
    main()
