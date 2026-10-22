# Cardápio — o que falta conferir

Documento **gerado** por `scripts/cardapio/gerar_conferencia.py` a partir
de `scripts/cardapio/catalogo_inicial.json`. Não editar à mão: corrija o
catálogo (ou o próprio cardápio, em Gestão → Rotinas → Cardápio) e gere
de novo.

O catálogo foi reconciliado em 2026-10-22 a partir de três fontes:

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
| London — Fish & Chips | Nome | Cadastro e HTML: “London”. Impresso: “Original”. A descrição coincide. | “London — Fish & Chips” |
| Patinha de Caranguejo | Nome | Cadastro: “Patinha de caranguejo”. Impresso: “PATA DE CARANGUEJO”. | “Patinha de Caranguejo” |
| Sherlock Holmes Gin | Receita | HTML: Monster. Impresso: Red Bull Zero e xarope de gengibre. | “gin com energético e gengibre”, sem marca |
| Moscow Mule | Receita | O impresso acrescenta refrigerante de limão, que o cadastro não cita. | a descrição do cadastro |
| NewCastle | Acompanhamento | Cadastro e HTML citam batatas; o impresso não cita acompanhamento. | com porção de batatas |
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

23 produtos têm ao menos um campo a confirmar.

| Campo | Produtos | Quantos |
|---|---|---:|
| Porção | Sir Fisher — Fish & Chips, London — Fish & Chips, NewCastle, Filé Mignon Trinchado, Camarão alho e óleo, Calabresa Acebolada com Fritas, Margarita, Pacote de Gelo | 8 |
| Rendimento | Filé Mignon, Picanha Importada, Filé de Peixe Grelhado, Carne de Sol Acebolada, Peito de Frango com Ervas, Picanha Suína | 6 |
| Opções | Pasteizinhos, Macaxeira Frita ou Batata Frita | 2 |
| Classificação | Corona Zero Longneck, Sumo de Limão | 2 |
| Descrição | Sherlock Holmes Gin, Moscow Mule | 2 |
| Foto | Sir Fisher — Fish & Chips | 1 |
| Alegação a conferir | Stella Pure Gold 600 | 1 |
| Informação alimentar | Molho Extra | 1 |
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
| Patinha de Caranguejo | GLÚTEN, LACTOSE, CRUSTÁCEOS | declarado no impresso | — |
| Bolinha de Peixe Cremosa | GLÚTEN, LACTOSE, PEIXE | declarado no impresso | — |
| NewCastle | CRUSTÁCEOS, GLÚTEN, OVO | declarado no impresso | — |
| Crocante de Carne de Sol com Abóbora | GLÚTEN, OVO, LACTOSE | declarado no impresso | — |
| Crocante de Calabresa e Alho Poró | GLÚTEN, OVO, LACTOSE | declarado no impresso | — |
| Big Ben Fries | GLÚTEN, OVO, CORANTES | declarado no impresso | — |
| Pasteizinhos | LACTOSE, CRUSTÁCEOS, GLÚTEN | declarado no impresso | Os símbolos são do bloco com os três sabores. O impresso não separa as marcações por sabor. |
| Filé Mignon Trinchado | GLÚTEN | declarado no impresso | — |
| Caldo de Peixe | GLÚTEN, PEIXE, OVO | declarado no impresso | — |
| Camarão alho e óleo | GLÚTEN, CRUSTÁCEOS | declarado no impresso | — |
| Dadinho de Tapioca | GLÚTEN, LACTOSE | declarado no impresso | — |
| Calabresa Acebolada com Fritas | GLÚTEN | declarado no impresso | — |
| Macaxeira Frita ou Batata Frita | GLÚTEN | declarado no impresso | — |
| Isca de Peixe | GLÚTEN, PEIXE, OVO, LACTOSE | declarado no impresso | — |
| Fisher Burger | GLÚTEN, PEIXE, OVO, LACTOSE | declarado no impresso | — |
| Edimburger | GLÚTEN, OVO, LACTOSE | declarado no impresso | — |
| Filé Mignon | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Picanha Importada | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Filé de Peixe Grelhado | GLÚTEN, OVO, PEIXE | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Carne de Sol Acebolada | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Peito de Frango com Ervas | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Picanha Suína | GLÚTEN, OVO | declarado no impresso | Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento. |
| Molho Extra | — | não revisado | — |
| Arroz Extra | — | não revisado | — |
| Adicional Salada | — | não revisado | — |
| Rolha | — | não revisado | — |
| Pacote de Gelo | — | não revisado | — |
| Embalagem para Viagem | — | não revisado | — |

Sem marcações no impresso (49 itens, quase todos bebidas e sobremesas): Brownie de Chocolate, Brownie com Sorvete, Café Expresso, Chope Brahma, Spaten Longneck, Stella Artois Longneck, Corona Longneck, Corona Zero Longneck, Spaten 600, Original 600, Stella Artois 600, Corona 600, Stella Pure Gold 600, Caipirinha, Caipiroska, Caipifruta, Gin Tônica, Melancita, Sherlock Holmes Gin, Tropicall, Margarita, Fitzgerald, Moscow Mule, Smirnoff Ice, Água sem gás, Água com gás, Água de Coco, Água Tônica, Refrigerante lata, Suco Copo, Energético Red Bull, Soda Italiana, Sumo de Limão, Teacher's, Black & White, Red Label, Black Label, Rum, Campari, Martini, Vodka Nacional, Vodka Skyy, Vodka Absolut, Gin Nacional, Gin Gordon's, Aperol, Conhaque, Cachaça Nacional, Cachaça Ypióca 150.

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
| Filé Mignon | R$ 90,00 | Arroz extra R$ 12,00 |
| Picanha Importada | R$ 99,00 | Arroz extra R$ 12,00 |
| Filé de Peixe Grelhado | R$ 80,00 | Arroz extra R$ 12,00 |
| Carne de Sol Acebolada | R$ 88,00 | Arroz extra R$ 12,00 |
| Peito de Frango com Ervas | R$ 62,00 | Arroz extra R$ 12,00 |
| Picanha Suína | R$ 67,00 | Arroz extra R$ 12,00 |

| Produto com variantes | Faixa exibida na lista | Opções |
|---|---|---|
| Caipirinha | R$ 18,00 a R$ 22,00 | Cachaça nacional R$ 18,00, Ypióca 150 R$ 22,00 |
| Caipiroska | R$ 20,00 a R$ 28,00 | Vodka nacional R$ 20,00, Skyy R$ 22,00, Absolut R$ 28,00 |
| Caipifruta | R$ 22,00 a R$ 30,00 | Vodka nacional R$ 22,00, Skyy R$ 24,00, Absolut R$ 30,00 |
| Gin Tônica | R$ 21,00 a R$ 23,00 | Gin nacional R$ 21,00, Gordon's R$ 23,00 |

## 5. Produtos que existem só numa fonte

Não foram excluídos nem promovidos. Ficam como decisão da operação.

| Produto | Situação | Encaminhamento |
|---|---|---|

## 6. Fotografias

Das 12 fotos de produto disponíveis em `site/assets/img/`, 32 foram
atribuídas depois de inspeção visual. Nenhum prato recebeu a foto de
outro para tapar buraco: quem não tem foto aparece com o brasão, num
tratamento igual para todos.

### Atribuídas

| Produto | Arquivo | Estado |
|---|---|---|
| Sir Fisher — Fish & Chips | `prato` | **a confirmar** — A foto mostra peixe empanado ao estilo panko. Confirmar com a operação se corresponde a esta versão ou à London. |
| London — Fish & Chips | `london-fish-and-chips-sir-fisher` | conferida |
| Patinha de Caranguejo | `patinha-de-caranguejo-sir-fisher` | conferida |
| Bolinha de Peixe Cremosa | `bolinha-de-peixe-cremosa-sir-fisher` | conferida |
| NewCastle | `newcastle-camarao-empanado-sir-fisher` | conferida |
| Crocante de Carne de Sol com Abóbora | `crocante-carne-de-sol-sir-fisher` | conferida |
| Crocante de Calabresa e Alho Poró | `crocante-calabresa-sir-fisher` | conferida |
| Big Ben Fries | `big-ben-fries-sir-fisher` | conferida |
| Pasteizinhos | `pasteizinhos-sir-fisher` | conferida |
| Filé Mignon Trinchado | `file-mignon-trinchado-sir-fisher` | conferida |
| Caldo de Peixe | `caldo-de-peixe-sir-fisher` | conferida |
| Camarão alho e óleo | `camarao-alho-e-oleo-sir-fisher` | conferida |
| Dadinho de Tapioca | `dadinho-de-tapioca-sir-fisher` | conferida |
| Calabresa Acebolada com Fritas | `calabresa-acebolada-com-fritas-sir-fisher` | conferida |
| Macaxeira Frita ou Batata Frita | `macaxeira-ou-batata-frita-sir-fisher` | conferida |
| Isca de Peixe | `isca-de-peixe-sir-fisher` | conferida |
| Fisher Burger | `fisher-burger-sir-fisher` | conferida |
| Edimburger | `edimburger-sir-fisher` | conferida |
| Filé Mignon | `file-mignon-para-dividir-sir-fisher` | conferida |
| Picanha Importada | `picanha-importada-para-dividir-sir-fisher` | conferida |
| Filé de Peixe Grelhado | `peixe-grelhado-para-dividir-sir-fisher` | conferida |
| Carne de Sol Acebolada | `carne-de-sol-para-dividir-sir-fisher` | conferida |
| Peito de Frango com Ervas | `peito-de-frango-para-dividir-sir-fisher` | conferida |
| Picanha Suína | `picanha-suina-para-dividir-sir-fisher` | conferida |
| Brownie de Chocolate | `brownie-de-chocolate-sir-fisher` | conferida |
| Brownie com Sorvete | `brownie-com-sorvete-sir-fisher` | conferida |
| Café Expresso | `cafe-expresso-sir-fisher` | conferida |
| Molho Extra | `molho-extra-sir-fisher` | conferida |
| Arroz Extra | `arroz-extra-sir-fisher` | conferida |
| Rolha | `rolha-sir-fisher` | conferida |
| Pacote de Gelo | `pacote-gelo-sir-fisher` | conferida |
| Embalagem para Viagem | `embalagem-viagem-sir-fisher` | conferida |

### Fotos existentes sem produto correspondente

- **`peixe-empanado-sir-fisher`** — Travessa de compartilhar com filés de peixe empanados, arroz, batata frita e farofa. Nenhum prato do cadastro corresponde: o peixe dos pratos para compartilhar é grelhado, não empanado. Não foi atribuída a nenhum produto para não ilustrar um prato com a foto de outro. *Confirmar com a operação se existe (ou existiu) uma versão empanada do prato para compartilhar.*
- **`almoco-executivo-sir-fisher`** — Cliente à mesa com prato de almoço executivo. Pertence ao almoço executivo, que tem página própria e não faz parte destes 81 registros. *Manter fora do catálogo do cardápio.*

### Pratos a fotografar (0)

Só pratos; bebidas e doses não precisam de foto no portal.


**Orientação de captura**, para as novas combinarem com as 12 que já
existem: luz natural, prato montado como sai para a mesa, fundo de
madeira escura ou o papel da casa, câmera a 45° para prato fundo e a 90°
para travessa, mesmo enquadramento do conjunto atual. Enviar em JPEG ou
WebP com pelo menos 1320 px no lado maior — o portal recorta em quadrado
na listagem e em 4:3 no detalhe. A foto entra pelo próprio editor, em
Gestão → Rotinas → Cardápio.

## 7. Ordem sugerida para a conferência

1. **Preços.** São 79. É o que impede o cardápio de ir ao ar. Conferir
   contra o PDV, não contra o impresso.
2. **Disponibilidade.** Marcar o que não existe mais. A ação é imediata e
   não precisa de publicação.
3. **As 2 divergências de porção.** Principalmente os dois Fish & Chips
   (150 g × 200 g).
4. **Alcance dos pesos.** “300 g” é da proteína, do prato montado, cru ou
   pronto? O rodapé do impresso diz “peso in natura”; confirmar onde vale.
5. **Rendimento dos pratos para compartilhar.** Nenhuma fonte diz quantas
   pessoas servem. Enquanto não houver resposta, o portal não afirma nada.
6. **Informação alimentar.** Ficha técnica e ingredientes dos
   fornecedores, incluindo óleo e equipamento compartilhados.
7. **Fotos** dos 0 pratos que faltam.
8. **Marcar como conferido** no editor. O aviso sai do portal.
