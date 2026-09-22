# Cardápio — o que falta conferir

Documento **gerado** por `scripts/cardapio/gerar_conferencia.py` a partir
de `scripts/cardapio/catalogo_inicial.json`. Não editar à mão: corrija o
catálogo (ou o próprio cardápio, em Gestão → Rotinas → Cardápio) e gere
de novo.

O catálogo foi reconciliado em 2026-09-22 a partir de três fontes:

| Fonte | O que é | Peso que recebeu |
|---|---|---|
| **TXT** | `site/cardapio/cardapio.txt`, o cadastro com 81 registros | Lista fechada. Nada entra no cardápio publicado sem estar aqui. |
| **HTML** | `site/cardapio/index.html`, a página antiga | Completa nomes truncados, descrições e variantes. Declara preços “conferidos em 07/09/2026”. |
| **Impresso** | `Sir Fisher Praia.pdf` | Autorizado só como fonte de texto e de declarações alimentares. Preços do impresso **não** substituíram o cadastro. |

**Nada nesta lista foi validado pela cozinha ou pela operação.** Enquanto
isso não acontecer, o portal mostra o aviso *“Cardápio em conferência”* e
cada campo duvidoso sai como *“em conferência”*, nunca como número.

Regras que o catálogo aplicou, sem exceção:

1. Divergência entre fontes nunca foi resolvida por automatismo. O campo
   deixa de ser exibido como fato.
2. Omissão numa fonte não apagou o dado de outra.
3. Adicional nunca virou preço do produto.
4. Símbolo alimentar só foi transcrito quando visível e com legenda clara.
   Ausência de símbolo não virou ausência de alérgeno.
5. Peso nunca virou número de pessoas.

## 1. Divergências entre as fontes

Cada linha é uma pergunta para a cozinha ou para o caixa. Enquanto não
houver resposta, o portal não mostra o dado.

| Produto | Assunto | O que cada fonte diz | O que o cliente vê hoje |
|---|---|---|---|
| Sir Fisher — Fish & Chips | Porção | Cardápio HTML: 150 g. Cardápio impresso: 200 g. | “Porção em conferência” |
| London — Fish & Chips | Porção | Cardápio HTML: 150 g. Cardápio impresso: 200 g. | “Porção em conferência” |
| Bolinha de Peixe Cremosa | Porção | Peso divergente — TXT e HTML: 300 g. Cardápio impresso: 200 g. | “6 unidades” |
| Crispy Spicy Chicken | Porção | O impresso descreve “4 grandes rolinhos” e não informa peso. As duas informações podem se somar; confirmar a apresentação vigente. | “200 g” |
| Fisher Burger | Porção | As fontes citam 120 g sem dizer se é o total das duas fatias ou o peso de cada uma. | “—” |
| Spaten Longneck | Porção | Volume divergente — HTML: 355 mL. Cardápio impresso: 300 mL. | “Porção em conferência” |
| London — Fish & Chips | Nome | Cadastro e HTML: “London”. Impresso: “Original”. A descrição coincide. | “London — Fish & Chips” |
| Patinha de Caranguejo | Nome | Cadastro: “Patinha de caranguejo”. Impresso: “PATA DE CARANGUEJO”. | “Patinha de Caranguejo” |
| Sherlock Holmes Gin | Receita | HTML: Monster. Impresso: Red Bull Zero e xarope de gengibre. | “gin com energético e gengibre”, sem marca |
| Moscow Mule | Receita | O impresso acrescenta refrigerante de limão, que o cadastro não cita. | a descrição do cadastro |
| Marine Sandwich | Ingrediente | Cadastro e HTML citam pepino; o impresso não cita. Omissão não retira ingrediente. | com pepino |
| NewCastle | Acompanhamento | Cadastro e HTML citam batatas; o impresso não cita acompanhamento. | com porção de batatas |
| Budweiser 600 | Vigência | Está no cadastro e no HTML, mas não foi encontrado no impresso. | publicado normalmente |
| Margarita | Vigência | Está no cadastro e no HTML, mas não foi encontrado no impresso. | publicado normalmente |
| Corona Zero Longneck | Classificação | O impresso escreve “CORONA ZERO%”. Se for sem álcool, merece etiqueta própria. | só entre as cervejas |
| Sumo de Limão | Classificação | O impresso lista em BEBIDAS com 50 mL, mas pode ser complemento de drink. | entre as bebidas sem álcool |
| Pasteizinhos | Opções | Nenhuma fonte diz se dá para misturar os três sabores numa porção. | “Sabor a escolher”, sem dizer se mistura |
| Café Expresso | Porção | Os 50 mL vêm do cadastro; o impresso não informa volume. | “50 mL” |
| Os seis pratos para compartilhar | Rendimento | O impresso declara 300 g de proteína e “peso in natura”. Nenhuma fonte diz quantas pessoas o prato serve. | “300 g de proteína”, sem número de pessoas |

Já resolvidos pelas fontes, sem pendência: os dois nomes truncados no
cadastro (“Crocante de Carne de Sol com…” e “Crocante de Calabresa e
Alho…”) foram completados pelo HTML e pelo impresso, que coincidem.

## 2. Campos pendentes, por produto

33 produtos têm ao menos um campo a confirmar.

| Campo | Produtos | Quantos |
|---|---|---:|
| Porção | Sir Fisher — Fish & Chips, London — Fish & Chips, Bolinha de Peixe Cremosa, NewCastle, Crispy Spicy Chicken, Filé Mignon Trinchado, Camarão alho e óleo, Calabresa Acebolada com Fritas… | 13 |
| Rendimento | Filé Mignon, Picanha Importada, Filé de Peixe Grelhado, Carne de Sol Acebolada, Peito de Frango com Ervas, Picanha Suína | 6 |
| Vigência do produto | Budweiser 600, Margarita, Adicional Salada, Corona 600 | 4 |
| Informação alimentar | Patinha de Caranguejo, Bolinha de Peixe Cremosa, Molho Extra | 3 |
| Opções | Pasteizinhos, Macaxeira Frita ou Batata Frita, Cachaça Premium | 3 |
| Nome | London — Fish & Chips, Patinha de Caranguejo | 2 |
| Classificação | Corona Zero Longneck, Sumo de Limão | 2 |
| Descrição | Sherlock Holmes Gin, Moscow Mule | 2 |
| Preço | Adicional Salada, Corona 600 | 2 |
| Foto | Sir Fisher — Fish & Chips | 1 |
| Alegação a conferir | Stella Pure Gold 600 | 1 |
| Regra de cobrança | Rolha | 1 |

## 3. Matriz de declarações alimentares, com proveniência

A legenda do cardápio impresso tem dez rótulos: **LACTOSE, CASTANHAS,
PEIXE, CORANTES, GLÚTEN, SOJA, LEITE, OVO, CRUSTÁCEOS e AMÊNDOAS**.
LACTOSE e LEITE são rótulos distintos no documento e continuam distintos
aqui: não foram fundidos numa taxonomia regulatória de alérgenos.

CASTANHAS, SOJA, LEITE e AMÊNDOAS aparecem na legenda mas não foram
identificados junto a nenhum dos 26 pratos da página 1. Isso **não**
indica que esses componentes estejam ausentes das receitas.

O rodapé traz o aviso geral **“ALÉRGICOS: PODE CONTER CAMARÃO E
GLÚTEN”**. Ele ficou guardado como aviso do documento e **não** foi
transformado em presença confirmada nem em contato cruzado de item algum.

Estado de cada declaração:

- `declarado no impresso` — símbolo visível no cardápio físico, transcrito.
- `sem marcações` — o produto aparece no impresso sem símbolos. **Não**
  significa ausência de alérgenos.
- `não revisado` — nenhuma fonte trouxe informação alimentar.

Nenhum item tem, hoje, `confirmado pela cozinha` ou `contato cruzado
confirmado`. Essas duas colunas só se preenchem com ficha técnica e
ingredientes dos fornecedores.

| Produto | Declarado no impresso | Estado | Divergência registrada |
|---|---|---|---|
| Sir Fisher — Fish & Chips | PEIXE, GLÚTEN, OVO | declarado no impresso | — |
| London — Fish & Chips | PEIXE, GLÚTEN, OVO | declarado no impresso | — |
| Patinha de Caranguejo | GLÚTEN, LACTOSE | declarado no impresso | O nome e a descrição citam caranguejo, mas o impresso não traz o símbolo de CRUSTÁCEOS neste bloco. Divergência registrada para conferência: a ausência do símbolo não indica ausência do ingrediente. |
| Bolinha de Peixe Cremosa | GLÚTEN, LACTOSE | declarado no impresso | A descrição cita pescada amarela, mas o impresso não traz o símbolo de PEIXE neste bloco. Divergência registrada para conferência. |
| NewCastle | CRUSTÁCEOS, GLÚTEN, OVO | declarado no impresso | — |
| Crocante de Carne de Sol com Abóbora | GLÚTEN, OVO, LACTOSE | declarado no impresso | — |
| Crocante de Calabresa e Alho Poró | GLÚTEN, OVO, LACTOSE | declarado no impresso | — |
| Big Ben Fries | GLÚTEN, OVO, CORANTES | declarado no impresso | — |
| Pasteizinhos | LACTOSE, CRUSTÁCEOS, GLÚTEN | declarado no impresso | Os símbolos são do bloco com os três sabores. O impresso não separa as marcações por sabor. |
| Crispy Spicy Chicken | GLÚTEN, LACTOSE | declarado no impresso | — |
| Filé Mignon Trinchado | GLÚTEN | declarado no impresso | — |
| Caldo de Peixe | GLÚTEN, PEIXE, OVO | declarado no impresso | — |
| Camarão alho e óleo | GLÚTEN, CRUSTÁCEOS | declarado no impresso | — |
| Dadinho de Tapioca | GLÚTEN, LACTOSE | declarado no impresso | — |
| Calabresa Acebolada com Fritas | GLÚTEN | declarado no impresso | — |
| Macaxeira Frita ou Batata Frita | GLÚTEN | declarado no impresso | — |
| Isca de Peixe | GLÚTEN, PEIXE, OVO, LACTOSE | declarado no impresso | — |
| Fisher Burger | GLÚTEN, PEIXE, OVO, LACTOSE | declarado no impresso | — |
| Edimburger | GLÚTEN, OVO, LACTOSE | declarado no impresso | — |
| Marine Sandwich | GLÚTEN, CRUSTÁCEOS, OVO, LACTOSE | declarado no impresso | — |
| Filé Mignon | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Picanha Importada | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Filé de Peixe Grelhado | GLÚTEN, OVO, PEIXE | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Carne de Sol Acebolada | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Peito de Frango com Ervas | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Picanha Suína | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Molho Extra | — | não revisado | — |
| Arroz Extra | — | não revisado | — |
| Rolha | — | não revisado | — |
| Pacote de Gelo | — | não revisado | — |
| Embalagem para Viagem | — | não revisado | — |
| Adicional Salada | — | não revisado | — |

Sem marcações no impresso (51 itens, quase todos bebidas e sobremesas): Brownie de Chocolate, Brownie com Sorvete, Café Expresso, Chope Brahma, Spaten Longneck, Stella Artois Longneck, Corona Longneck, Corona Zero Longneck, Spaten 600, Original 600, Budweiser 600, Stella Artois 600, Stella Pure Gold 600, Caipirinha, Caipiroska, Caipifruta, Gin Tônica, Melancita, Sherlock Holmes Gin, Tropicall, Margarita, Fitzgerald, Moscow Mule, Smirnoff Ice, Água sem gás, Água com gás, Água de Coco, Água Tônica, Refrigerante lata, Suco Copo, Energético Red Bull, Soda Italiana, Sumo de Limão, Teacher's, Black & White, Red Label, Black Label, Rum, Campari, Martini, Vodka Nacional, Vodka Sky, Vodka Absolut, Gin Nacional, Gin Gordon's, Aperol, Conhaque, Cachaça Nacional, Cachaça Ypioca 150, Cachaça Premium, Corona 600.

### Alegações do impresso que **não** foram publicadas

- **Stella Pure Gold 600** — “PURO MALTE, SEM GLÚTEN E COM 17% MENOS CALORIAS” (Sir Fisher Praia.pdf, página 2). Alegação do impresso sobre esta cerveja. Não publicada como informação alimentar: exige conferência com embalagem e fabricante. Não vale para as demais cervejas.

## 4. Preço, variantes e adicionais

O caso que motivou a trava: no HTML antigo, a primeira oferta estruturada
dos três sanduíches é a batata de R$ 9,90, e o preço do sanduíche vem
depois. Um importador que pegasse a primeira ou a menor oferta anunciaria
um sanduíche de R$ 37,00 por R$ 9,90. O catálogo separa os dois e o editor
recusa salvar um adicional que custe igual ou mais que o produto.

| Produto | Preço do produto | Adicionais (cobrados à parte) |
|---|---|---|
| Fisher Burger | R$ 37,00 | Adicionar batata frita R$ 9,90 |
| Edimburger | R$ 37,00 | Adicionar batata frita R$ 9,90 |
| Marine Sandwich | R$ 46,00 | Adicionar batata frita R$ 9,90 |
| Filé Mignon | R$ 90,00 | Arroz extra R$ 12,00 |
| Picanha Importada | R$ 99,00 | Arroz extra R$ 12,00 |
| Filé de Peixe Grelhado | R$ 80,00 | Arroz extra R$ 12,00 |
| Carne de Sol Acebolada | R$ 88,00 | Arroz extra R$ 12,00 |
| Peito de Frango com Ervas | R$ 62,00 | Arroz extra R$ 12,00 |
| Picanha Suína | R$ 67,00 | Arroz extra R$ 12,00 |

| Produto com variantes | Faixa exibida na lista | Opções |
|---|---|---|
| Caipirinha | R$ 18,00 a R$ 22,00 | Cachaça nacional R$ 18,00, Ypioca 150 R$ 22,00 |
| Caipiroska | R$ 20,00 a R$ 28,00 | Vodka nacional R$ 20,00, Sky R$ 22,00, Absolut R$ 28,00 |
| Caipifruta | R$ 22,00 a R$ 30,00 | Vodka nacional R$ 22,00, Sky R$ 24,00, Absolut R$ 30,00 |
| Gin Tônica | R$ 21,00 a R$ 23,00 | Gin nacional R$ 21,00, Gordon's R$ 23,00 |

## 5. Produtos que existem só numa fonte

Não foram excluídos nem promovidos. Ficam como decisão da operação.

| Produto | Situação | Encaminhamento |
|---|---|---|
| Adicional Salada | Rascunho, fora do portal | Aparece apenas no cardápio impresso (R$ 19,00, página 1). Não está entre os 81 registros do cadastro. Fica em rascunho até a operação confirmar existência e preço vigente. |
| Corona 600 | Rascunho, fora do portal | Aparece no grupo de garrafas 600 mL do impresso, mas não consta no cadastro, que tem Budweiser 600 nessa faixa. Preço não importado do impresso. Fica em rascunho para decisão da operação. |
| Budweiser 600 | Publicado | Consta no TXT e no HTML, mas não foi encontrado no cardápio impresso. Ausência em uma fonte não retira o produto do cadastro. |
| Margarita | Publicado | Consta no TXT e no HTML, mas não foi encontrado no cardápio impresso. Ausência em uma fonte não retira o produto. |

## 6. Fotografias

Das 12 fotos de produto disponíveis em `site/assets/img/`, 12 foram
atribuídas depois de inspeção visual. Nenhum prato recebeu a foto de
outro para tapar buraco: quem não tem foto aparece com o brasão, num
tratamento igual para todos.

### Atribuídas

| Produto | Arquivo | Estado |
|---|---|---|
| Sir Fisher — Fish & Chips | `prato` | **a confirmar** — A foto mostra peixe empanado ao estilo panko. Confirmar com a operação se corresponde a esta versão ou à London. |
| NewCastle | `newcastle-camarao-empanado-sir-fisher` | conferida |
| Camarão alho e óleo | `camarao-alho-e-oleo-sir-fisher` | conferida |
| Dadinho de Tapioca | `dadinho-de-tapioca-sir-fisher` | conferida |
| Isca de Peixe | `isca-de-peixe-sir-fisher` | conferida |
| Marine Sandwich | `marine-sandwich-sir-fisher` | conferida |
| Filé Mignon | `file-mignon-sir-fisher` | conferida |
| Picanha Importada | `picanha-importada-sir-fisher` | conferida |
| Filé de Peixe Grelhado | `peixe-grelhado-sir-fisher` | conferida |
| Carne de Sol Acebolada | `carne-de-sol-sir-fisher` | conferida |
| Peito de Frango com Ervas | `peito-de-frango-sir-fisher` | conferida |
| Picanha Suína | `picanha-suina-sir-fisher` | conferida |

### Fotos existentes sem produto correspondente

- **`peixe-empanado-sir-fisher`** — Travessa de compartilhar com filés de peixe empanados, arroz, batata frita e farota. Nenhum prato do cadastro corresponde: o peixe dos pratos para compartilhar é grelhado, não empanado. Não foi atribuída a nenhum produto para não ilustrar um prato com a foto de outro. *Confirmar com a operação se existe (ou existiu) uma versão empanada do prato para compartilhar.*
- **`almoco-executivo-sir-fisher`** — Cliente à mesa com prato de almoço executivo. Pertence ao almoço executivo, que tem página própria e não faz parte destes 81 registros. *Manter fora do catálogo do cardápio.*

### Pratos a fotografar (17)

Só pratos; bebidas e doses não precisam de foto no portal.

- London — Fish & Chips (R$ 45,00)
- Patinha de Caranguejo (R$ 55,00)
- Bolinha de Peixe Cremosa (R$ 44,00)
- Crocante de Carne de Sol com Abóbora (R$ 38,00)
- Crocante de Calabresa e Alho Poró (R$ 38,00)
- Big Ben Fries (R$ 33,00)
- Pasteizinhos (R$ 37,00)
- Crispy Spicy Chicken (R$ 37,00)
- Filé Mignon Trinchado (R$ 84,00)
- Caldo de Peixe (R$ 18,00)
- Calabresa Acebolada com Fritas (R$ 46,00)
- Macaxeira Frita ou Batata Frita (R$ 27,00)
- Fisher Burger (R$ 37,00)
- Edimburger (R$ 37,00)
- Brownie de Chocolate (R$ 10,00)
- Brownie com Sorvete (R$ 18,00)
- Café Expresso (R$ 5,00)

**Orientação de captura**, para as novas combinarem com as 12 que já
existem: luz natural, prato montado como sai para a mesa, fundo de
madeira escura ou o papel da casa, câmera a 45° para prato fundo e a 90°
para travessa, mesmo enquadramento do conjunto atual. Enviar em JPEG ou
WebP com pelo menos 1320 px no lado maior — o portal recorta em quadrado
na listagem e em 4:3 no detalhe. A foto entra pelo próprio editor, em
Gestão → Rotinas → Cardápio.

## 7. Ordem sugerida para a conferência

1. **Preços.** São 81. É o que impede o cardápio de ir ao ar. Conferir
   contra o PDV, não contra o impresso.
2. **Disponibilidade.** Marcar o que não existe mais. A ação é imediata e
   não precisa de publicação.
3. **As 6 divergências de porção.** Principalmente os dois Fish & Chips
   (150 g × 200 g) e a Bolinha de Peixe (300 g × 200 g).
4. **Alcance dos pesos.** “300 g” é da proteína, do prato montado, cru ou
   pronto? O rodapé do impresso diz “peso in natura”; confirmar onde vale.
5. **Rendimento dos pratos para compartilhar.** Nenhuma fonte diz quantas
   pessoas servem. Enquanto não houver resposta, o portal não afirma nada.
6. **Informação alimentar.** Ficha técnica e ingredientes dos
   fornecedores, incluindo óleo e equipamento compartilhados. Resolver as
   duas divergências de símbolo (Patinha de Caranguejo sem CRUSTÁCEOS,
   Bolinha de Peixe sem PEIXE).
7. **Fotos** dos 17 pratos que faltam.
8. **Marcar como conferido** no editor. O aviso sai do portal.
