# -*- coding: utf-8 -*-
"""
Catalogo inicial do cardapio do Sir Fisher.

Este arquivo e a reconciliacao auditavel das tres fontes disponiveis em
22/09/2026. Ele NAO e um cardapio validado: nenhum preco, porcao ou
declaracao alimentar aqui foi confirmado pela cozinha ou pela operacao.
Todo registro carrega a origem do dado e o seu estado de revisao.

Fontes e o peso de cada uma:

  TXT   site/cardapio/cardapio.txt ....... inventario inicial (81 registros
                                           com preco). E a lista fechada: nada
                                           entra no catalogo publicado sem
                                           estar aqui.
  HTML  site/cardapio/index.html ......... completa nomes truncados, descricoes
                                           e variantes. Declara precos
                                           "conferidos em 07/09/2026" e remete
                                           ao Hubt para a versao operacional.
  PDF   "Sir Fisher Praia.pdf" ........... cardapio impresso. Autorizado apenas
                                           como fonte de texto e de declaracoes
                                           alimentares. Precos do impresso NAO
                                           substituem o cadastro.

Regras aplicadas, sem excecao:

  1. Divergencia entre fontes nunca e resolvida por automatismo. Fica marcada
     como `divergente` e o campo deixa de ser exibido como fato.
  2. Omissao em uma fonte nao apaga o dado de outra (o impresso nao citar o
     pepino do Marine Sandwich nao retira o pepino).
  3. Adicional nunca vira preco do produto.
  4. Simbolo alimentar so e transcrito quando visivel e com legenda clara.
     Ausencia de simbolo nao vira ausencia de alergeno.
  5. Produto que so existe em uma fonte complementar entra como candidato em
     rascunho (`publicar=False`), fora dos 81.

Saida: catalogo_inicial.json, consumido por gerar_migration.py (semente do
banco) e por exportar_snapshot.py (copia publica derivada da publicacao).
"""

import json
import os
import unicodedata

HOJE = "2026-09-22"

# --------------------------------------------------------------------------
# Avisos do catalogo
# --------------------------------------------------------------------------

AVISO_ALERGENOS_IMPRESSO = (
    "ALÉRGICOS: PODE CONTER CAMARÃO E GLÚTEN."
)

NOTA_PESO_IN_NATURA = (
    "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em "
    "conferência."
)

AVISOS = [
    {
        "id": "alergenos",
        "tipo": "alimentar",
        "titulo": "Sobre alérgenos",
        "texto": (
            "As marcações de cada prato foram transcritas do cardápio impresso "
            "e ainda não foram conferidas com a cozinha. Elas não substituem "
            "uma ficha técnica. Antes de pedir, fale com a equipe sobre "
            "alergias e restrições."
        ),
        "fonte": "Sir Fisher Praia.pdf, rodapé da página 1",
        "citacao": AVISO_ALERGENOS_IMPRESSO,
        "estado": "declarado_no_impresso",
    },
]

# Sinonimos de linguagem, nao de produto. Servem so para a busca encontrar o
# mesmo ingrediente escrito de outro jeito. Nenhum deles afirma nada sobre uma
# receita; sao variantes regionais e de grafia. Editavel na gestao.
SINONIMOS = {
    "macaxeira": ["mandioca", "aipim"],
    "camarao": ["camarões", "camarao"],
    "fish and chips": ["fish n chips", "fish chips", "peixe com batata"],
    "chope": ["chopp", "chopinho"],
    "refrigerante": ["refri"],
    "batata frita": ["fritas", "batatas"],
    "pescada amarela": ["peixe"],
    "agua de coco": ["coco"],
}

# --------------------------------------------------------------------------
# Categorias
# --------------------------------------------------------------------------

CATEGORIAS = [
    {
        "id": "fish-and-chips",
        "nome": "Fish & Chips",
        "resumo": "O prato da casa, em duas massas diferentes.",
        "grupo": "comer",
        "subgrupos": [],
    },
    {
        "id": "petiscos",
        "nome": "Petiscos e porções",
        "resumo": "Para dividir na mesa enquanto a conversa corre.",
        "grupo": "comer",
        "subgrupos": [
            {"id": "mar", "nome": "Do mar"},
            {"id": "terra", "nome": "Da terra"},
            {"id": "fritas", "nome": "Fritas e acompanhamentos"},
        ],
    },
    {
        "id": "sanduiches",
        "nome": "Sanduíches",
        "resumo": "Em pão brioche, servidos individualmente.",
        "grupo": "comer",
        "subgrupos": [],
    },
    {
        "id": "para-dividir",
        "nome": "Pratos para compartilhar",
        "resumo": (
            "Servidos na travessa, com arroz, batata frita (ou macaxeira), "
            "salada, farota e molho artesanal."
        ),
        "grupo": "comer",
        "subgrupos": [],
    },
    {
        "id": "sobremesas",
        "nome": "Sobremesas e café",
        "resumo": "Para fechar a conta com doce.",
        "grupo": "comer",
        "subgrupos": [],
    },
    {
        "id": "cervejas",
        "nome": "Cervejas e chope",
        "resumo": "Long neck, garrafa 600 e chope.",
        "grupo": "beber",
        "subgrupos": [],
    },
    {
        "id": "coqueteis",
        "nome": "Coquetéis",
        "resumo": "Clássicos e criações da casa.",
        "grupo": "beber",
        "subgrupos": [],
    },
    {
        "id": "sem-alcool",
        "nome": "Bebidas sem álcool",
        "resumo": "Águas, sucos, refrigerantes e energético.",
        "grupo": "beber",
        "subgrupos": [],
    },
    {
        "id": "doses",
        "nome": "Doses e aperitivos",
        "resumo": "Destilados em dose de 50 mL.",
        "grupo": "beber",
        "subgrupos": [],
    },
    {
        "id": "extras",
        "nome": "Extras e serviços",
        "resumo": "Adicionais, itens de apoio e cobranças da casa.",
        "grupo": "extras",
        "subgrupos": [
            {"id": "comestiveis", "nome": "Adicionais do prato"},
            {"id": "apoio", "nome": "Itens de apoio"},
            {"id": "cobrancas", "nome": "Cobranças"},
        ],
    },
]

# --------------------------------------------------------------------------
# Helpers de construcao
# --------------------------------------------------------------------------


def porcao(texto=None, principal=None, total=None, unidades=None,
           estado="declarado", divergencia=None, nota=None, fontes=None):
    """Porcao com as medidas separadas e o seu estado de revisao.

    `principal` e o ingrediente principal; `total` e o prato inteiro. As duas
    coisas quase nunca sao iguais e o cardapio impresso so distingue as duas
    nos pratos para dividir. Rendimento em pessoas nao e deduzido de peso:
    fica None ate a cozinha confirmar.
    """
    return {
        "texto": texto,
        "principal": principal,
        "total": total,
        "unidades": unidades,
        "rende_pessoas": None,
        "estado": estado,
        "divergencia": divergencia,
        "nota": nota,
        "fontes": fontes or [],
    }


def alimentar(declarados=None, estado="declarado_no_impresso", pagina=1,
              divergencias=None, alegacoes=None):
    """Declaracoes alimentares, separadas por grau de confianca.

    `declarados` sao os simbolos transcritos do impresso. `confirmado_cozinha`
    e `contato_cruzado` nascem vazios de proposito: nada foi validado ainda, e
    lista vazia aqui significa "nao revisado", nunca "nao contem".
    """
    return {
        "declarados": declarados or [],
        "fonte": "Sir Fisher Praia.pdf, página %d" % pagina if declarados or estado == "sem_simbolos" else None,
        "estado": estado,
        "divergencias": divergencias or [],
        "alegacoes": alegacoes or [],
        "confirmado_cozinha": [],
        "contato_cruzado": [],
    }


PRODUTOS = []


def p(id, cat, nome, preco, sub=None, nome_original=None, descritor=None,
      descricao=None, detalhe=None, variantes=None, adicionais=None,
      inclui=None, opcoes=None, porcao_=None, alimentar_=None, foto=None,
      termos=None, etiquetas=None, pendencias=None, fontes=None, notas=None,
      publicar=True, preco_estado="declarado"):
    PRODUTOS.append({
        "id": id,
        "categoria": cat,
        "subgrupo": sub,
        "nome": nome,
        "nome_original": nome_original or nome,
        "descritor": descritor,
        "descricao": descricao,
        "detalhe": detalhe,
        "preco_centavos": preco,
        "preco_estado": preco_estado,
        "variantes": variantes or [],
        "adicionais": adicionais or [],
        "inclui": inclui or [],
        "opcoes": opcoes or [],
        "porcao": porcao_ or porcao(estado="ausente"),
        "alimentar": alimentar_ or alimentar(estado="nao_revisado"),
        "foto": foto,
        "termos": termos or [],
        "etiquetas": etiquetas or [],
        "pendencias": pendencias or [],
        "fontes": fontes or ["TXT", "HTML"],
        "notas_internas": notas or [],
        "publicar": publicar,
        "disponivel": True,
    })


# Adicional compartilhado pelos tres sanduiches. Aparece SEMPRE como adicional,
# nunca como preco do sanduiche: no HTML ele e a primeira oferta estruturada e
# um importador ingenuo anunciaria um sanduiche de R$ 37,00 por R$ 9,90.
ADICIONAL_BATATA = [{
    "nome": "Adicionar batata frita",
    "preco_centavos": 990,
    "fontes": ["HTML", "PDF"],
    "estado": "declarado",
}]

ACOMPANHA_DIVIDIR = [
    "Arroz", "Batata frita ou macaxeira", "Salada", "Farota",
    "Molho artesanal",
]

OPCAO_BATATA_MACAXEIRA = [{
    "texto": "Batata frita ou macaxeira",
    "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.",
    "estado": "a_confirmar",
}]


def porcao_dividir():
    return porcao(
        texto="300 g de proteína",
        principal={"valor": 300, "unidade": "g", "alcance": "proteina"},
        nota=NOTA_PESO_IN_NATURA + " O impresso não informa quantas pessoas o "
             "prato serve.",
        fontes=["PDF"],
    )


def alimentar_dividir(extra=None):
    return alimentar(declarados=["GLÚTEN", "OVO"] + (extra or []),
                     divergencias=[
                         "Os símbolos estão no prato completo. O impresso não "
                         "diz se vêm da proteína, do molho ou de um "
                         "acompanhamento."
                     ])


# ==========================================================================
# 1. Fish & Chips (2 registros do TXT)
# ==========================================================================

PORCAO_FISH_DIVERGENTE = porcao(
    texto=None,
    estado="divergente",
    divergencia="Cardápio HTML: 150 g. Cardápio impresso: 200 g.",
    nota="Peso em conferência com a cozinha.",
    fontes=["HTML", "PDF"],
)

p("sir-fisher-fish-n-chips", "fish-and-chips",
  "Sir Fisher — Fish & Chips",
  4500,
  nome_original="Sir Fisher - Fish N’ Chips",
  descritor="pescada amarela em crosta de panko, com batatas",
  descricao="Pescada amarela envolta em farinha panko, crocante por fora e "
            "suculenta por dentro. Acompanha batatas palito.",
  detalhe="Nossa interpretação do clássico Fish & Chips: a pescada amarela é "
          "envolta em uma crosta de farinha panko, garantindo textura crocante "
          "por fora e suculência por dentro. Acompanhado de batatas palito.",
  porcao_=PORCAO_FISH_DIVERGENTE,
  alimentar_=alimentar(["PEIXE", "GLÚTEN", "OVO"]),
  foto={"base": "prato", "larguras": [800, 1200],
        "alt": "Filés de peixe empanados com batatas fritas, servidos em uma "
               "tábua com a bandeira britânica",
        "estado": "a_confirmar",
        "nota": "A foto mostra peixe empanado ao estilo panko. Confirmar com a "
                "operação se corresponde a esta versão ou à London."},
  termos=["peixe", "pescada amarela", "panko", "empanado", "batata frita",
          "fish and chips"],
  etiquetas=["do-mar", "classico-da-casa"],
  pendencias=["porcao", "foto"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O TXT e o HTML trazem o selo “Mais Pedido!”. É uma alegação de "
         "popularidade sem dado de vendas: não foi publicada."])

p("london-fish-n-chips", "fish-and-chips",
  "London — Fish & Chips",
  4500,
  nome_original="London - Fish N’ Chips",
  descritor="peixe em massa fermentada na cerveja, com batatas",
  descricao="Peixe envolto em leve massa fermentada na cerveja e frito até "
            "dourar. Acompanha batatas crocantes.",
  detalhe="Autêntico Fish & Chips: o peixe é envolto em uma leve massa "
          "fermentada na cerveja e frito até atingir a perfeição dourada. "
          "Acompanhado de batatas crocantes, inspirado nas barracas à "
          "beira-mar das praias inglesas.",
  porcao_=PORCAO_FISH_DIVERGENTE,
  alimentar_=alimentar(["PEIXE", "GLÚTEN", "OVO"]),
  termos=["peixe", "cerveja", "massa", "batata frita", "fish and chips",
          "original"],
  etiquetas=["do-mar", "classico-da-casa"],
  pendencias=["porcao", "nome"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O cardápio impresso chama esta versão de “Original — Fish N’ "
         "Chips”. A descrição coincide, mas o nome não foi trocado sem "
         "confirmação da operação."])

# ==========================================================================
# 2. Petiscos e porcoes (15 registros do TXT)
# ==========================================================================

p("patinha-de-caranguejo", "petiscos",
  "Patinha de Caranguejo", 5500, sub="mar",
  nome_original="Patinha de caranguejo",
  descricao="Patas empanadas e crocantes. Acompanha batata frita e molho da "
            "casa.",
  inclui=["Batata frita", "Molho da casa"],
  porcao_=porcao(texto="10 unidades",
                 unidades={"quantidade": 10, "rotulo": "patas"},
                 fontes=["TXT", "PDF"]),
  alimentar_=alimentar(
      ["GLÚTEN", "LACTOSE"],
      divergencias=["O nome e a descrição citam caranguejo, mas o impresso "
                    "não traz o símbolo de CRUSTÁCEOS neste bloco. "
                    "Divergência registrada para conferência: a ausência do "
                    "símbolo não indica ausência do ingrediente."]),
  termos=["caranguejo", "patinha", "empanado", "frutos do mar"],
  etiquetas=["do-mar"],
  pendencias=["alimentar", "nome"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso usa “PATA DE CARANGUEJO”; o cadastro usa “Patinha de "
         "caranguejo”. Nome de exibição mantido conforme o cadastro."])

p("bolinha-de-peixe-cremosa", "petiscos",
  "Bolinha de Peixe Cremosa", 4400, sub="mar",
  descricao="Seis bolinhas de pescada amarela com recheio cremoso de cream "
            "cheese.",
  porcao_=porcao(texto="6 unidades",
                 unidades={"quantidade": 6, "rotulo": "bolinhas"},
                 estado="parcial",
                 divergencia="Peso divergente — TXT e HTML: 300 g. Cardápio "
                             "impresso: 200 g.",
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(
      ["GLÚTEN", "LACTOSE"],
      divergencias=["A descrição cita pescada amarela, mas o impresso não traz "
                    "o símbolo de PEIXE neste bloco. Divergência registrada "
                    "para conferência."]),
  termos=["peixe", "pescada amarela", "cream cheese", "bolinha"],
  etiquetas=["do-mar"],
  pendencias=["porcao", "alimentar"],
  fontes=["TXT", "HTML", "PDF"])

p("newcastle", "petiscos",
  "NewCastle", 6000, sub="mar",
  descritor="camarões empanados com batatas",
  descricao="Crocantes por fora, em farinha panko. Inspirado nas ruas de Londres.",
  detalhe="Camarões empanados com uma mistura crocante de farinha panko. "
          "Acompanha porção de batatas. Uma explosão de sabores inspirada nas "
          "vibrantes ruas londrinas.",
  inclui=["Porção de batatas"],
  porcao_=porcao(texto="250 g",
                 principal={"valor": 250, "unidade": "g",
                            "alcance": "indefinido"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["CRUSTÁCEOS", "GLÚTEN", "OVO"]),
  foto={"base": "newcastle-camarao-empanado-sir-fisher", "larguras": [440, 660],
        "alt": "Camarões empanados dourados servidos com batatas fritas e "
               "molho, em tábua de madeira", "estado": "conferido"},
  termos=["camarao", "camarões", "empanado", "panko", "batata frita",
          "frutos do mar"],
  etiquetas=["do-mar"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso não cita o acompanhamento de batatas. Omissão não retira "
         "o acompanhamento declarado no cadastro."])

p("crocante-carne-de-sol", "petiscos",
  "Crocante de Carne de Sol com Abóbora", 3800, sub="terra",
  nome_original="Crocante de Carne de Sol com...",
  descricao="Seis bolinhos crocantes em leve massa de abóbora, com recheio "
            "cremoso de carne de sol.",
  porcao_=porcao(texto="6 unidades / 360 g",
                 total={"valor": 360, "unidade": "g"},
                 unidades={"quantidade": 6, "rotulo": "bolinhos"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "OVO", "LACTOSE"]),
  termos=["carne de sol", "abobora", "bolinho", "crocante"],
  etiquetas=["da-terra"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Nome truncado no TXT (“Crocante de Carne de Sol com...”). "
         "Completado pelo HTML e pelo impresso, que coincidem."])

p("crocante-calabresa", "petiscos",
  "Crocante de Calabresa e Alho Poró", 3800, sub="terra",
  nome_original="Crocante de Calabresa e Alho...",
  descricao="Seis bolinhos crocantes recheados com calabresa frita e "
            "alho-poró.",
  porcao_=porcao(texto="6 unidades / 360 g",
                 total={"valor": 360, "unidade": "g"},
                 unidades={"quantidade": 6, "rotulo": "bolinhos"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "OVO", "LACTOSE"]),
  termos=["calabresa", "alho poro", "bolinho", "crocante"],
  etiquetas=["da-terra"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Nome truncado no TXT. Completado pelo HTML e pelo impresso."])

p("big-ben-fries", "petiscos",
  "Big Ben Fries", 3300, sub="fritas",
  descritor="batata frita com cheddar cremoso e bacon",
  descricao=None,
  porcao_=porcao(texto="200 g",
                 total={"valor": 200, "unidade": "g"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "OVO", "CORANTES"]),
  termos=["batata frita", "cheddar", "bacon", "fritas"],
  etiquetas=["da-terra", "para-compartilhar"],
  fontes=["TXT", "HTML", "PDF"])

p("pasteizinhos", "petiscos",
  "Pasteizinhos", 3700, sub="terra",
  descricao="Dez pastéis crocantes com molho especial. Sabor a escolher.",
  inclui=["Molho especial"],
  opcoes=[{"texto": "2 queijos", "estado": "declarado"},
          {"texto": "Carne", "estado": "declarado"},
          {"texto": "Camarão", "estado": "declarado"}],
  porcao_=porcao(texto="10 unidades",
                 unidades={"quantidade": 10, "rotulo": "pastéis"},
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(
      ["LACTOSE", "CRUSTÁCEOS", "GLÚTEN"],
      divergencias=["Os símbolos são do bloco com os três sabores. O impresso "
                    "não separa as marcações por sabor."]),
  termos=["pastel", "pasteizinho", "queijo", "carne", "camarao"],
  etiquetas=["da-terra", "para-compartilhar"],
  pendencias=["opcoes"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Nenhuma fonte informa se é possível misturar sabores em uma mesma "
         "porção. Pendente de confirmação com a operação.",
         "Os três sabores são opções de um mesmo registro, com preço único. "
         "Não foram desdobrados em produtos separados."])

p("crispy-spicy-chicken", "petiscos",
  "Crispy Spicy Chicken", 3700, sub="terra",
  descritor="rolinhos de frango empanados recheados com queijo",
  descricao="Marinado em especiarias e frito na hora. Acompanha molho cremoso.",
  inclui=["Molho cremoso"],
  porcao_=porcao(texto="200 g",
                 total={"valor": 200, "unidade": "g"},
                 estado="parcial",
                 divergencia="O impresso descreve “4 grandes rolinhos” e não "
                             "informa peso. As duas informações podem se "
                             "somar; confirmar a apresentação vigente.",
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "LACTOSE"]),
  termos=["frango", "queijo", "empanado", "apimentado", "rolinho"],
  etiquetas=["da-terra"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"])

p("file-mignon-trinchado", "petiscos",
  "Filé Mignon Trinchado", 8400, sub="terra",
  descricao="Filé mignon acebolado, servido com batata frita ou macaxeira "
            "dourada.",
  opcoes=OPCAO_BATATA_MACAXEIRA,
  porcao_=porcao(texto="300 g",
                 principal={"valor": 300, "unidade": "g",
                            "alcance": "indefinido"},
                 nota=NOTA_PESO_IN_NATURA + " O impresso não delimita se os "
                      "300 g são da carne ou do prato montado.",
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN"]),
  termos=["file mignon", "carne", "acebolado", "batata frita", "macaxeira"],
  etiquetas=["da-terra", "para-compartilhar"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Produto distinto do “Filé Mignon” dos pratos para compartilhar "
         "(R$ 90,00), que vem com arroz, salada, farota e molho."])

p("caldo-de-peixe", "petiscos",
  "Caldo de Peixe", 1800, sub="mar",
  descricao="Caldo de pescada amarela, leve e cheio de sabor.",
  porcao_=porcao(texto="200 mL",
                 total={"valor": 200, "unidade": "mL"},
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "PEIXE", "OVO"]),
  termos=["caldo", "peixe", "pescada amarela", "sopa"],
  etiquetas=["do-mar"],
  fontes=["TXT", "HTML", "PDF"])

p("camarao-alho-e-oleo", "petiscos",
  "Camarão alho e óleo", 4700, sub="mar",
  descricao="Camarão G salteado no alho e óleo.",
  porcao_=porcao(texto="300 g",
                 principal={"valor": 300, "unidade": "g",
                            "alcance": "indefinido"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "CRUSTÁCEOS"]),
  foto={"base": "camarao-alho-e-oleo-sir-fisher", "larguras": [440, 660],
        "alt": "Camarões inteiros salteados com alho, servidos em travessa "
               "com limão", "estado": "conferido"},
  termos=["camarao", "alho", "frutos do mar", "salteado"],
  etiquetas=["do-mar"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"])

p("dadinho-de-tapioca", "petiscos",
  "Dadinho de Tapioca", 2900, sub="terra",
  descricao="Doze dadinhos de tapioca crocantes por fora e macios por dentro, "
            "com molho especial.",
  inclui=["Molho especial"],
  porcao_=porcao(texto="12 unidades",
                 unidades={"quantidade": 12, "rotulo": "dadinhos"},
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "LACTOSE"]),
  foto={"base": "dadinho-de-tapioca-sir-fisher", "larguras": [440, 660],
        "alt": "Cubos de tapioca dourados servidos com molho em tigela",
        "estado": "conferido"},
  termos=["tapioca", "dadinho", "queijo coalho", "petisco"],
  etiquetas=["da-terra", "para-compartilhar"],
  fontes=["TXT", "HTML", "PDF"])

p("calabresa-acebolada-com-fritas", "petiscos",
  "Calabresa Acebolada com Fritas", 4600, sub="terra",
  descricao="Calabresa acebolada com porção generosa de batata frita ou "
            "macaxeira crocante.",
  opcoes=OPCAO_BATATA_MACAXEIRA,
  porcao_=porcao(texto="250 g",
                 principal={"valor": 250, "unidade": "g",
                            "alcance": "indefinido"},
                 nota=NOTA_PESO_IN_NATURA + " O impresso não delimita se os "
                      "250 g são da calabresa ou do prato montado.",
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN"]),
  termos=["calabresa", "linguica", "acebolada", "batata frita", "macaxeira"],
  etiquetas=["da-terra", "para-compartilhar"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"])

p("macaxeira-ou-batata-frita", "petiscos",
  "Macaxeira Frita ou Batata Frita", 2700, sub="fritas",
  descricao="Macaxeira ou batata frita, douradinhas. Escolha uma das duas.",
  opcoes=[{"texto": "Macaxeira frita", "estado": "declarado"},
          {"texto": "Batata frita", "estado": "declarado"}],
  porcao_=porcao(texto="250 g",
                 total={"valor": 250, "unidade": "g"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN"]),
  termos=["macaxeira", "mandioca", "aipim", "batata frita", "fritas"],
  etiquetas=["da-terra", "para-compartilhar"],
  pendencias=["opcoes"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Registro único com duas opções de escolha. Não foi desdobrado em "
         "dois produtos: nenhuma fonte dá preço separado para cada uma."])

p("isca-de-peixe", "petiscos",
  "Isca de Peixe", 4200, sub="mar",
  descricao="Tiras de pescada amarela empanadas ao panko, com molho especial.",
  inclui=["Molho especial"],
  porcao_=porcao(texto="250 g",
                 total={"valor": 250, "unidade": "g"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "PEIXE", "OVO", "LACTOSE"]),
  foto={"base": "isca-de-peixe-sir-fisher", "larguras": [440, 660],
        "alt": "Tiras de peixe empanadas servidas em tábua com limão e molho",
        "estado": "conferido"},
  termos=["peixe", "pescada amarela", "isca", "empanado", "panko"],
  etiquetas=["do-mar", "para-compartilhar"],
  fontes=["TXT", "HTML", "PDF"])

# ==========================================================================
# 3. Sanduiches (3 registros do TXT)
# ==========================================================================

p("fisher-burger", "sanduiches",
  "Fisher Burger", 3700,
  descritor="hambúrguer de pescada amarela empanada",
  descricao="Em pão brioche, com picles e molho especial.",
  detalhe="O Fisher Burger é uma criação inspirada nas delícias do mar. Duas "
          "fatias de filé de pescada amarela, empanadas para uma crocância "
          "perfeita, dispostas em pão brioche. Complementado por picles e um "
          "molho especial.",
  adicionais=ADICIONAL_BATATA,
  porcao_=porcao(texto=None,
                 estado="parcial",
                 divergencia="As fontes citam 120 g sem dizer se é o total das "
                             "duas fatias ou o peso de cada uma.",
                 nota="Peso em conferência com a cozinha.",
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "PEIXE", "OVO", "LACTOSE"]),
  termos=["hamburguer", "sanduiche", "peixe", "pescada amarela", "brioche",
          "empanado"],
  etiquetas=["do-mar"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O sanduíche custa R$ 37,00. O adicional de batata (R$ 9,90) é a "
         "primeira oferta estruturada no HTML e nunca deve ser lido como "
         "preço do produto."])

p("edimburger", "sanduiches",
  "Edimburger", 3700,
  descritor="blend de 120 g de bovino com bacon",
  descricao="Em pão brioche, com alface, tomate, maionese especial e cheddar.",
  detalhe="O Edimburger presta homenagem à capital da Escócia com um blend de "
          "120 g de carne, composto por bovino e bacon. Servido em pão brioche "
          "macio, com alface crocante, tomate fresco, maionese especial e "
          "fatias generosas de cheddar.",
  adicionais=ADICIONAL_BATATA,
  porcao_=porcao(texto="120 g de carne",
                 principal={"valor": 120, "unidade": "g",
                            "alcance": "proteina"},
                 nota=NOTA_PESO_IN_NATURA,
                 fontes=["TXT", "HTML", "PDF"]),
  alimentar_=alimentar(["GLÚTEN", "OVO", "LACTOSE"]),
  termos=["hamburguer", "sanduiche", "carne", "bovino", "bacon", "cheddar",
          "brioche"],
  etiquetas=["da-terra"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Preço do sanduíche: R$ 37,00. O adicional de batata é informação "
         "separada."])

p("marine-sandwich", "sanduiches",
  "Marine Sandwich", 4600,
  descritor="camarões salteados com cream cheese empanado",
  descricao="Com molho aioli, alface e pepino, em pão brioche.",
  adicionais=ADICIONAL_BATATA,
  porcao_=porcao(estado="ausente",
                 nota="Nenhuma fonte informa peso ou quantidade."),
  alimentar_=alimentar(["GLÚTEN", "CRUSTÁCEOS", "OVO", "LACTOSE"]),
  foto={"base": "marine-sandwich-sir-fisher", "larguras": [440, 660],
        "alt": "Sanduíche em pão brioche coberto de camarões salteados",
        "estado": "conferido"},
  termos=["camarao", "sanduiche", "cream cheese", "aioli", "brioche",
          "frutos do mar"],
  etiquetas=["do-mar"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso não cita o pepino presente no cadastro. Omissão não "
         "retira o ingrediente.",
         "Preço do sanduíche: R$ 46,00. Adicional de batata em separado."])

# ==========================================================================
# 4. Pratos para compartilhar (6 registros do TXT)
# ==========================================================================

DIVIDIR = [
    ("file-mignon-dividir", "Filé Mignon", 9000,
     "filé mignon com molho madeira ou ao alho e óleo",
     "Filé mignon suculento, com molho madeira ou preparado ao alho e óleo.",
     "file-mignon-sir-fisher",
     "Travessa com filé mignon ao molho, arroz, batata frita e farofa",
     ["file mignon", "carne", "molho madeira", "alho e oleo"], []),
    ("picanha-importada", "Picanha Importada", 9900,
     "picanha importada grelhada no charbroil",
     "Picanha importada, grelhada no charbroil para realçar sabor e "
     "suculência.",
     "picanha-importada-sir-fisher",
     "Travessa com fatias de picanha grelhada, arroz, batata frita e farofa",
     ["picanha", "carne", "importada", "grelhada", "charbroil"], []),
    ("file-de-peixe-grelhado", "Filé de Peixe Grelhado", 8000,
     "pescada amarela grelhada",
     "Filé de pescada amarela grelhado, leve e cheio de sabor.",
     "peixe-grelhado-sir-fisher",
     "Travessa com filé de peixe grelhado, arroz, batata frita e farofa",
     ["peixe", "pescada amarela", "grelhado", "leve"], ["PEIXE"]),
    ("carne-de-sol-acebolada", "Carne de Sol Acebolada", 8800,
     "carne de sol com cebolas douradas",
     "Carne de sol de primeira, acompanhada de cebolas douradas.",
     "carne-de-sol-sir-fisher",
     "Travessa com carne de sol acebolada, arroz, batata frita e farofa",
     ["carne de sol", "acebolada", "cebola"], []),
    ("peito-de-frango-com-ervas", "Peito de Frango com Ervas", 6200,
     "frango grelhado no charbroil com ervas finas",
     "Peito de frango temperado com ervas finas e grelhado no charbroil.",
     "peito-de-frango-sir-fisher",
     "Travessa com peito de frango grelhado, arroz, batata frita e farofa",
     ["frango", "peito", "ervas", "grelhado", "charbroil"], []),
    ("picanha-suina", "Picanha Suína", 6700,
     "picanha suína grelhada no charbroil",
     "Picanha suína grelhada no charbroil.",
     "picanha-suina-sir-fisher",
     "Travessa com picanha suína grelhada, arroz, batata frita e farofa",
     ["picanha suina", "porco", "suina", "grelhada", "charbroil"], []),
]

for _id, _nome, _preco, _desc_curto, _desc, _foto, _alt, _termos, _extra in DIVIDIR:
    p(_id, "para-dividir", _nome, _preco,
      descricao=_desc,
      inclui=list(ACOMPANHA_DIVIDIR),
      opcoes=OPCAO_BATATA_MACAXEIRA,
      adicionais=[
          {"nome": "Arroz extra", "preco_centavos": 1200,
           "fontes": ["TXT", "PDF"], "estado": "declarado"},
      ],
      porcao_=porcao_dividir(),
      alimentar_=alimentar_dividir(_extra),
      foto={"base": _foto, "larguras": [440, 660], "alt": _alt,
            "estado": "conferido"},
      termos=_termos + ["para dividir", "compartilhar", "arroz", "farota"],
      etiquetas=["para-compartilhar"],
      pendencias=["rendimento"],
      fontes=["TXT", "HTML", "PDF"],
      notas=["O impresso declara 300 g de proteína e o rodapé informa peso in "
             "natura. Nenhuma fonte informa quantas pessoas o prato serve: o "
             "rendimento não foi deduzido do peso."])

# ==========================================================================
# 5. Sobremesas e cafe (3 registros do TXT)
# ==========================================================================

p("brownie-de-chocolate", "sobremesas", "Brownie de Chocolate", 1000,
  descricao="Brownie macio, feito com chocolate de alta qualidade.",
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["brownie", "chocolate", "doce", "sobremesa"],
  fontes=["TXT", "HTML", "PDF"])

p("brownie-com-sorvete", "sobremesas", "Brownie com Sorvete", 1800,
  descricao="Brownie de chocolate com sorvete de creme e calda de chocolate.",
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["brownie", "sorvete", "chocolate", "doce", "sobremesa"],
  fontes=["TXT", "HTML", "PDF"])

p("cafe-expresso", "sobremesas", "Café Expresso", 500,
  porcao_=porcao(texto="50 mL", total={"valor": 50, "unidade": "mL"},
                 fontes=["TXT", "HTML"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["cafe", "expresso", "cafezinho"],
  etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso lista o café entre as sobremesas e não informa volume. "
         "Os 50 mL vêm do cadastro."])

# ==========================================================================
# 6. Cervejas e chope (10 registros do TXT)
# ==========================================================================

CERVEJAS = [
    ("chope-brahma", "Chope Brahma", 1090, 300, "chope", None),
    ("spaten-longneck", "Spaten Longneck", 1190, None, "long neck",
     "Volume divergente — HTML: 355 mL. Cardápio impresso: 300 mL."),
    ("stella-artois-longneck", "Stella Artois Longneck", 1290, 330,
     "long neck", None),
    ("corona-longneck", "Corona Longneck", 1490, 330, "long neck", None),
    ("corona-zero-longneck", "Corona Zero Longneck", 1490, 330, "long neck",
     None),
    ("spaten-600", "Spaten 600", 1940, 600, "garrafa", None),
    ("original-600", "Original 600", 1940, 600, "garrafa", None),
    ("budweiser-600", "Budweiser 600", 1840, 600, "garrafa", None),
    ("stella-artois-600", "Stella Artois 600", 2140, 600, "garrafa", None),
    ("stella-pure-gold-600", "Stella Pure Gold 600", 2390, 600, "garrafa",
     None),
]

for _id, _nome, _preco, _ml, _formato, _div in CERVEJAS:
    _pend = []
    _notas = []
    _aleg = []
    if _div:
        _porcao = porcao(texto=None, estado="divergente", divergencia=_div,
                         fontes=["HTML", "PDF"])
        _pend.append("porcao")
    else:
        _porcao = porcao(texto="%d mL" % _ml,
                         total={"valor": _ml, "unidade": "mL"},
                         fontes=["HTML", "PDF"])
    if _id == "stella-pure-gold-600":
        _aleg = [{
            "texto": "PURO MALTE, SEM GLÚTEN E COM 17% MENOS CALORIAS",
            "fonte": "Sir Fisher Praia.pdf, página 2",
            "estado": "a_conferir",
            "nota": "Alegação do impresso sobre esta cerveja. Não publicada "
                    "como informação alimentar: exige conferência com "
                    "embalagem e fabricante. Não vale para as demais "
                    "cervejas.",
        }]
        _pend.append("alegacao")
    if _id == "budweiser-600":
        _notas.append("Consta no TXT e no HTML, mas não foi encontrado no "
                      "cardápio impresso. Ausência em uma fonte não retira o "
                      "produto do cadastro.")
        _pend.append("vigencia")
    if _id == "corona-zero-longneck":
        _notas.append("O impresso escreve “CORONA ZERO% LONGNECK”. A "
                      "classificação como bebida sem álcool depende de "
                      "conferência do produto e não foi aplicada como "
                      "etiqueta.")
        _pend.append("classificacao")
    p(_id, "cervejas", _nome, _preco,
      descritor=_formato,
      descricao=None,
      porcao_=_porcao,
      alimentar_=alimentar(estado="sem_simbolos", pagina=2, alegacoes=_aleg),
      termos=[_nome.lower(), "cerveja", _formato],
      etiquetas=["bebida"],
      pendencias=_pend,
      fontes=["TXT", "HTML", "PDF"],
      notas=_notas)

# ==========================================================================
# 7. Coqueteis (11 registros do TXT)
# ==========================================================================

def var(nome, centavos):
    return {"nome": nome, "preco_centavos": centavos,
            "fontes": ["HTML", "PDF"], "estado": "declarado"}


P300 = lambda: porcao(texto="300 mL", total={"valor": 300, "unidade": "mL"},
                      fontes=["PDF"])

p("caipirinha", "coqueteis", "Caipirinha", 1800,
  descritor="limão, açúcar e cachaça",
  detalhe="Clássica combinação de limão, açúcar e cachaça, refrescante e cheia de sabor. Escolha a cachaça.",
  variantes=[var("Cachaça nacional", 1800), var("Ypioca 150", 2200)],
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["caipirinha", "cachaca", "limao", "ypioca", "drink", "coquetel"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O preço do TXT (R$ 18,00) corresponde à variante nacional."])

p("caipiroska", "coqueteis", "Caipiroska", 2000,
  descritor="limão, açúcar e vodka",
  detalhe="Releitura da caipirinha, com limão, açúcar e vodka. Escolha a vodka.",
  variantes=[var("Vodka nacional", 2000), var("Sky", 2200),
             var("Absolut", 2800)],
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["caipiroska", "vodka", "limao", "absolut", "sky", "drink",
          "coquetel"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"])

p("caipifruta", "coqueteis", "Caipifruta", 2200,
  descritor="vodka, açúcar e polpa de fruta",
  detalhe="Vodka, açúcar e o sabor de fruta da sua escolha. Escolha a vodka e a fruta.",
  variantes=[var("Vodka nacional", 2200), var("Sky", 2400),
             var("Absolut", 3000)],
  opcoes=[{"texto": "Abacaxi, acerola, caju, cajá, maracujá, morango ou "
                    "manga (polpa)", "estado": "declarado"}],
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["caipifruta", "vodka", "fruta", "polpa", "abacaxi", "acerola",
          "caju", "caja", "maracuja", "morango", "manga", "drink"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"])

p("gin-tonica", "coqueteis", "Gin Tônica", 2100,
  descritor="gin, água tônica e toque cítrico",
  detalhe="O clássico refrescante: gin, água tônica e um toque cítrico para equilibrar. Escolha o gin.",
  variantes=[var("Gin nacional", 2100), var("Gordon's", 2300)],
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["gin", "tonica", "gordons", "drink", "coquetel", "citrico"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"])

p("melancita", "coqueteis", "Melancita", 2700,
  descritor="gin, energético de melancia e limão siciliano",
  detalhe="Gin harmonizado com Red Bull melancia e finalizado com fatias de limão siciliano.",
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["melancia", "gin", "red bull", "energetico", "limao siciliano",
          "drink"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"])

p("sherlock-holmes-gin", "coqueteis", "Sherlock Holmes Gin", 2900,
  descritor="gin com energético e gengibre",
  detalhe="Gin com energético e um toque sutil de gengibre. A marca do energético está em conferência com o bar.",
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["sherlock", "gin", "gengibre", "energetico", "drink"],
  etiquetas=["bebida", "com-alcool"],
  pendencias=["descricao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Receita divergente: o HTML cita Monster; o impresso cita Red Bull "
         "Zero e xarope de gengibre. A marca do energético não foi publicada "
         "até a confirmação da ficha."])

p("tropicall", "coqueteis", "Tropicall", 2700,
  descritor="vodka, energético tropical e limão siciliano",
  detalhe="Vodka com Red Bull Tropical e um toque cítrico de limão siciliano.",
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["tropicall", "vodka", "red bull", "tropical", "limao siciliano",
          "drink"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"])

p("margarita", "coqueteis", "Margarita", 2900,
  descritor="tequila, triple sec e limão",
  detalhe="Tequila, triple sec e o toque cítrico marcante do limão.",
  porcao_=porcao(estado="ausente",
                 nota="Nenhuma fonte informa o volume deste coquetel."),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["margarita", "tequila", "triple sec", "limao", "drink"],
  etiquetas=["bebida", "com-alcool"],
  pendencias=["porcao", "vigencia"],
  fontes=["TXT", "HTML"],
  notas=["Consta no TXT e no HTML, mas não foi encontrado no cardápio "
         "impresso. Ausência em uma fonte não retira o produto."])

p("fitzgerald", "coqueteis", "Fitzgerald", 2300,
  descritor="gin, limão, açúcar e bitter artesanal",
  detalhe="Gin, suco de limão, açúcar e um toque sutil de bitter artesanal.",
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["fitzgerald", "gin", "limao", "bitter", "drink"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"])

p("moscow-mule", "coqueteis", "Moscow Mule", 2600,
  nome_original="Moscow mule",
  descritor="vodka, gengibre e limão",
  detalhe="Vodka, suco de limão e espuma de gengibre.",
  porcao_=P300(),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["moscow mule", "vodka", "gengibre", "limao", "drink"],
  etiquetas=["bebida", "com-alcool"],
  pendencias=["descricao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso acrescenta refrigerante de limão à composição. Ficha a "
         "confirmar antes de alterar a descrição."])

p("smirnoff-ice", "coqueteis", "Smirnoff Ice", 1500,
  porcao_=porcao(texto="275 mL", total={"valor": 275, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["smirnoff", "ice", "vodka", "long neck"],
  etiquetas=["bebida", "com-alcool"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["Bebida pronta listada entre os coquetéis nas fontes. Mantida na "
         "mesma categoria do cadastro."])

# ==========================================================================
# 8. Bebidas sem alcool (9 registros do TXT)
# ==========================================================================

p("agua-sem-gas", "sem-alcool", "Água sem gás", 500,
  porcao_=porcao(texto="500 mL", total={"valor": 500, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["agua", "sem gas"], etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("agua-com-gas", "sem-alcool", "Água com gás", 600,
  porcao_=porcao(texto="500 mL", total={"valor": 500, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["agua", "com gas", "gaseificada"], etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("agua-de-coco-copo", "sem-alcool", "Água de Coco", 500,
  nome_original="Água de Coco copo",
  porcao_=porcao(texto="Copo 300 mL", total={"valor": 300, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["agua de coco", "coco", "natural"], etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("agua-tonica", "sem-alcool", "Água Tônica", 600,
  porcao_=porcao(texto="350 mL", total={"valor": 350, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["agua tonica", "tonica"], etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("refrigerante-lata", "sem-alcool", "Refrigerante lata", 800,
  descritor="sabor a escolher",
  descricao=None,
  opcoes=[{"texto": "Guaraná, Guaraná Zero, Pepsi, Pepsi Black, laranja, uva "
                    "ou soda", "estado": "declarado"}],
  porcao_=porcao(texto="350 mL", total={"valor": 350, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["refrigerante", "refri", "lata", "guarana", "pepsi", "laranja",
          "uva", "soda", "zero"],
  etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("suco-copo", "sem-alcool", "Suco Copo", 1100,
  descritor="feito com polpa, sabor a escolher",
  descricao=None,
  opcoes=[{"texto": "Acerola, abacaxi, cajá, caju, limão, maracujá, morango "
                    "ou manga (polpa)", "estado": "declarado"}],
  porcao_=porcao(texto="330 mL", total={"valor": 330, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["suco", "polpa", "acerola", "abacaxi", "caja", "caju", "limao",
          "maracuja", "morango", "manga", "natural"],
  etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("energetico-red-bull", "sem-alcool", "Energético Red Bull", 1600,
  porcao_=porcao(texto="269 mL", total={"valor": 269, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["red bull", "energetico"], etiquetas=["bebida"],
  fontes=["TXT", "HTML", "PDF"])

p("soda-italiana", "sem-alcool", "Soda Italiana", 1500,
  nome_original="Soda Italiana (sem alcool)",
  descritor="sem álcool, sabor a escolher",
  descricao=None,
  opcoes=[{"texto": "Maçã verde, tangerina, gengibre, granadine ou cranberry",
           "estado": "declarado"}],
  porcao_=porcao(texto="300 mL", total={"valor": 300, "unidade": "mL"},
                 fontes=["PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["soda italiana", "sem alcool", "maca verde", "tangerina",
          "gengibre", "granadine", "cranberry"],
  etiquetas=["bebida", "sem-alcool"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso marca explicitamente este item como SEM ÁLCOOL."])

p("sumo-de-limao", "sem-alcool", "Sumo de Limão", 300,
  descritor="50 mL",
  porcao_=porcao(texto="50 mL", total={"valor": 50, "unidade": "mL"},
                 fontes=["HTML", "PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["sumo de limao", "limao", "suco de limao"],
  etiquetas=["bebida"],
  pendencias=["classificacao"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso lista o item na seção BEBIDAS, com 50 mL. Se na operação "
         "ele funciona como complemento de drink, e não como bebida servida, "
         "deve ser movido para Extras. Pendente de confirmação."])

# ==========================================================================
# 9. Doses e aperitivos (17 registros do TXT)
# ==========================================================================

DOSES = [
    ("teachers", "Teacher's", 800, None, ["whisky", "teachers", "escoces"]),
    ("black-white", "Black & White", 800, None, ["whisky", "black white"]),
    ("red-label", "Red Label", 1200, None, ["whisky", "red label",
                                            "johnnie walker"]),
    ("black-label", "Black Label", 1700, None, ["whisky", "black label",
                                                "johnnie walker"]),
    ("rum", "Rum", 800, "Bacardi ou Montila", ["rum", "bacardi", "montila"]),
    ("campari", "Campari", 800, None, ["campari", "aperitivo", "bitter"]),
    ("martini", "Martini", 700, "Bianco ou Rosato", ["martini", "bianco",
                                                     "rosato", "vermute"]),
    ("vodka-nacional", "Vodka Nacional", 700, None, ["vodka", "nacional"]),
    ("vodka-sky", "Vodka Sky", 900, None, ["vodka", "sky"]),
    ("vodka-absolut", "Vodka Absolut", 1500, None, ["vodka", "absolut"]),
    ("gin-nacional", "Gin Nacional", 1000, None, ["gin", "nacional"]),
    ("gin-gordons", "Gin Gordon's", 1200, None, ["gin", "gordons",
                                                 "britanico"]),
    ("aperol", "Aperol", 800, None, ["aperol", "aperitivo", "spritz"]),
    ("conhaque", "Conhaque", 700, None, ["conhaque"]),
    ("cachaca-nacional", "Cachaça Nacional", 600, None, ["cachaca",
                                                         "nacional"]),
    ("cachaca-ypioca-150", "Cachaça Ypioca 150", 1000, None,
     ["cachaca", "ypioca"]),
    ("cachaca-premium", "Cachaça Premium", 1200,
     "Batista (3 anos em barril de carvalho, MG), Gogó da Ema (2 anos em "
     "barril de bálsamo, AL), Matriarca (2 anos em barril de umburana, BA) ou "
     "Caipira 5 Estrelas (1 ano em barril de cerejeira, ES)",
     ["cachaca", "premium", "batista", "gogo da ema", "matriarca",
      "caipira 5 estrelas", "envelhecida"]),
]

for _id, _nome, _preco, _opcao, _termos in DOSES:
    _notas = []
    _pend = []
    if _id == "cachaca-ypioca-150":
        _notas.append("O “150” faz parte do nome comercial da cachaça. Não é "
                      "a medida da dose, que é de 50 mL como nas demais.")
    if _id == "cachaca-premium":
        _notas.append("Quatro rótulos sob um mesmo preço, conforme o cadastro. "
                      "Disponibilidade por rótulo a confirmar com o bar.")
        _pend.append("opcoes")
    p(_id, "doses", _nome, _preco,
      descricao=None,
      opcoes=[{"texto": _opcao, "estado": "declarado"}] if _opcao else [],
      porcao_=porcao(texto="Dose de 50 mL",
                     total={"valor": 50, "unidade": "mL"},
                     fontes=["HTML", "PDF"]),
      alimentar_=alimentar(estado="sem_simbolos", pagina=2),
      termos=_termos + ["dose", "destilado"],
      etiquetas=["bebida", "com-alcool"],
      pendencias=_pend,
      fontes=["TXT", "HTML", "PDF"],
      notas=_notas)

# ==========================================================================
# 10. Extras e servicos (5 registros do TXT)
# ==========================================================================

p("molho-extra", "extras", "Molho Extra", 300, sub="comestiveis",
  descritor="porção adicional de molho",
  alimentar_=alimentar(estado="nao_revisado"),
  termos=["molho", "extra", "adicional"],
  etiquetas=["adicional"],
  pendencias=["alimentar"],
  fontes=["TXT", "HTML"],
  notas=["Nenhuma fonte informa qual molho, nem a quantidade."])

p("arroz-extra", "extras", "Arroz Extra", 1200, sub="comestiveis",
  descritor="porção adicional de arroz",
  alimentar_=alimentar(estado="nao_revisado"),
  termos=["arroz", "extra", "adicional"],
  etiquetas=["adicional"],
  fontes=["TXT", "HTML", "PDF"],
  notas=["O impresso traz o mesmo item como “ADICIONAL ARROZ R$ 12,00”, na "
         "página dos pratos. Mesmo registro, não duplicado."])

p("rolha", "extras", "Rolha", 3000, sub="cobrancas",
  descritor="taxa para consumir bebida trazida pelo cliente",
  alimentar_=alimentar(estado="nao_revisado"),
  termos=["rolha", "taxa", "servico"],
  etiquetas=["servico"],
  pendencias=["regra"],
  fontes=["TXT", "HTML"],
  notas=["Cobrança de serviço, não é produto. Regras de aplicação (por "
         "garrafa, por mesa) não constam nas fontes."])

p("pacote-gelo", "extras", "Pacote de Gelo", 2000, sub="apoio",
  nome_original="Pacote Gelo",
  descritor="pacote de gelo",
  alimentar_=alimentar(estado="nao_revisado"),
  termos=["gelo", "pacote"],
  etiquetas=["servico"],
  pendencias=["porcao"],
  fontes=["TXT", "HTML"],
  notas=["Nenhuma fonte informa o peso do pacote."])

p("embalagem-viagem", "extras", "Embalagem para Viagem", 300, sub="apoio",
  nome_original="Embalagem Viagem",
  descritor="embalagem para levar",
  alimentar_=alimentar(estado="nao_revisado"),
  termos=["embalagem", "viagem", "levar", "marmita", "delivery"],
  etiquetas=["servico"],
  fontes=["TXT", "HTML"])

# ==========================================================================
# Candidatos: existem no impresso, nao estao nos 81 registros do cadastro.
# Entram como rascunho, fora da publicacao, para a operacao decidir.
# ==========================================================================

p("adicional-salada", "extras", "Adicional Salada", 1900, sub="comestiveis",
  descritor="porção adicional de salada",
  alimentar_=alimentar(estado="nao_revisado"),
  termos=["salada", "adicional", "extra"],
  etiquetas=["adicional"],
  pendencias=["vigencia", "preco"],
  fontes=["PDF"],
  publicar=False,
  preco_estado="somente_impresso",
  notas=["Aparece apenas no cardápio impresso (R$ 19,00, página 1). Não está "
         "entre os 81 registros do cadastro. Fica em rascunho até a operação "
         "confirmar existência e preço vigente."])

p("corona-600", "cervejas", "Corona 600", None,
  descritor="garrafa",
  porcao_=porcao(texto="600 mL", total={"valor": 600, "unidade": "mL"},
                 fontes=["PDF"]),
  alimentar_=alimentar(estado="sem_simbolos", pagina=2),
  termos=["corona", "cerveja", "garrafa"],
  etiquetas=["bebida"],
  pendencias=["vigencia", "preco"],
  fontes=["PDF"],
  publicar=False,
  preco_estado="ausente",
  notas=["Aparece no grupo de garrafas 600 mL do impresso, mas não consta no "
         "cadastro, que tem Budweiser 600 nessa faixa. Preço não importado do "
         "impresso. Fica em rascunho para decisão da operação."])

# ==========================================================================
# Fotografias sem produto correspondente
# ==========================================================================

FOTOS_SEM_DESTINO = [
    {
        "arquivo": "peixe-empanado-sir-fisher",
        "observado": "Travessa de compartilhar com filés de peixe empanados, "
                     "arroz, batata frita e farota.",
        "motivo": "Nenhum prato do cadastro corresponde: o peixe dos pratos "
                  "para compartilhar é grelhado, não empanado. Não foi "
                  "atribuída a nenhum produto para não ilustrar um prato com "
                  "a foto de outro.",
        "encaminhamento": "Confirmar com a operação se existe (ou existiu) "
                          "uma versão empanada do prato para compartilhar.",
    },
    {
        "arquivo": "almoco-executivo-sir-fisher",
        "observado": "Cliente à mesa com prato de almoço executivo.",
        "motivo": "Pertence ao almoço executivo, que tem página própria e não "
                  "faz parte destes 81 registros.",
        "encaminhamento": "Manter fora do catálogo do cardápio.",
    },
]

# --------------------------------------------------------------------------
# Normalizacao para busca
# --------------------------------------------------------------------------


def sem_acento(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", (texto or "").lower())
        if unicodedata.category(c) != "Mn"
    )


def indice_busca(prod):
    """Texto normalizado que a busca do portal percorre.

    So entra o que esta cadastrado: nome, descritor, descricao, opcoes,
    variantes, acompanhamentos e os termos registrados. Nada e inferido a
    partir do nome comercial.
    """
    partes = [prod["nome"], prod["nome_original"], prod["descritor"],
              prod["descricao"], prod["detalhe"]]
    partes += [v["nome"] for v in prod["variantes"]]
    partes += [a["nome"] for a in prod["adicionais"]]
    partes += [o.get("texto") for o in prod["opcoes"]]
    partes += prod["inclui"]
    partes += prod["termos"]
    base = " ".join(x for x in partes if x)
    normal = sem_acento(base)
    for chave, alternativas in SINONIMOS.items():
        alvo = sem_acento(chave)
        if alvo in normal:
            normal += " " + " ".join(sem_acento(a) for a in alternativas)
        for alt in alternativas:
            if sem_acento(alt) in normal and alvo not in normal:
                normal += " " + alvo
    return " ".join(sorted(set(normal.split())))


def faixa_preco(prod):
    """Preco exibido na listagem.

    Com variantes, vira faixa do menor ao maior. Adicional NUNCA entra nesta
    conta: ele nao e um jeito mais barato de pedir o produto.
    """
    if prod["variantes"]:
        valores = [v["preco_centavos"] for v in prod["variantes"]]
        menor, maior = min(valores), max(valores)
        if menor != maior:
            return {"tipo": "faixa", "min": menor, "max": maior,
                    "centavos": menor}
        return {"tipo": "exato", "centavos": menor}
    if prod["preco_centavos"] is None:
        return {"tipo": "ausente", "centavos": None}
    return {"tipo": "exato", "centavos": prod["preco_centavos"]}


# --------------------------------------------------------------------------
# Verificacoes de integridade
# --------------------------------------------------------------------------


def verificar():
    erros = []
    publicados = [x for x in PRODUTOS if x["publicar"]]

    if len(publicados) != 81:
        erros.append("Esperados 81 registros publicáveis, encontrados %d."
                     % len(publicados))

    ids = [x["id"] for x in PRODUTOS]
    if len(ids) != len(set(ids)):
        erros.append("Identificadores repetidos no catálogo.")

    validas = {c["id"] for c in CATEGORIAS}
    for x in PRODUTOS:
        if x["categoria"] not in validas:
            erros.append("%s: categoria inexistente %s"
                         % (x["id"], x["categoria"]))
        subs = {s["id"] for c in CATEGORIAS if c["id"] == x["categoria"]
                for s in c["subgrupos"]}
        if x["subgrupo"] and x["subgrupo"] not in subs:
            erros.append("%s: subgrupo inexistente %s"
                         % (x["id"], x["subgrupo"]))
        if x["publicar"] and x["preco_centavos"] is None and not x["variantes"]:
            erros.append("%s: publicado sem preço." % x["id"])
        # A regra que motivou a auditoria: adicional nunca pode ser o menor
        # preco exibido do produto.
        for ad in x["adicionais"]:
            if x["preco_centavos"] and ad["preco_centavos"] >= x["preco_centavos"]:
                erros.append("%s: adicional %s custa mais que o produto."
                             % (x["id"], ad["nome"]))
        if x["porcao"]["estado"] in ("divergente",) and x["porcao"]["texto"]:
            erros.append("%s: porção divergente não pode ter texto exibido."
                         % x["id"])
        if x["alimentar"]["declarados"] and not x["alimentar"]["fonte"]:
            erros.append("%s: declaração alimentar sem fonte." % x["id"])

    contagem = {}
    for x in publicados:
        contagem[x["categoria"]] = contagem.get(x["categoria"], 0) + 1
    return erros, contagem


def montar():
    erros, contagem = verificar()
    if erros:
        raise SystemExit("Catálogo inconsistente:\n  - " + "\n  - ".join(erros))

    produtos = []
    for i, x in enumerate(PRODUTOS):
        y = dict(x)
        y["ordem"] = i
        y["preco"] = faixa_preco(x)
        y["indice_busca"] = indice_busca(x)
        produtos.append(y)

    return {
        "gerado_em": HOJE,
        "estado_catalogo": "em_conferencia",
        "nota_estado": (
            "Catálogo reconciliado a partir do cadastro, do cardápio HTML e do "
            "cardápio impresso. Nenhum preço, porção ou declaração alimentar "
            "foi confirmado pela cozinha ou pela operação até esta data."
        ),
        "moeda": "BRL",
        "avisos": AVISOS,
        "sinonimos": SINONIMOS,
        "categorias": CATEGORIAS,
        "produtos": produtos,
        "fotos_sem_destino": FOTOS_SEM_DESTINO,
        "contagem_por_categoria": contagem,
        "total_publicavel": len([x for x in PRODUTOS if x["publicar"]]),
        "total_rascunho": len([x for x in PRODUTOS if not x["publicar"]]),
    }


if __name__ == "__main__":
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "catalogo_inicial.json")
    dados = montar()
    with open(destino, "w", encoding="utf-8") as saida:
        json.dump(dados, saida, ensure_ascii=False, indent=1)
    print("Catálogo gerado: %s" % destino)
    print("Publicáveis: %d | Rascunho: %d"
          % (dados["total_publicavel"], dados["total_rascunho"]))
    for cat in CATEGORIAS:
        print("  %-16s %d" % (cat["id"],
                              dados["contagem_por_categoria"].get(cat["id"], 0)))
