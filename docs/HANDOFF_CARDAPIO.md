# Handoff — Cardápio próprio e conferência operacional

Atualizado em 23/10/2026. Este documento registra o estado real do cardápio em `https://www.sirfisher.com.br/cardapio/` e substitui o handoff anterior que tratava dados não confirmados como definitivamente validados.

## Estado atual

- O cardápio próprio está publicado e substitui a dependência do Hubt para consulta do cliente.
- O catálogo contém 78 produtos e usa como fontes o inventário interno, o HTML anterior e o cardápio impresso.
- Revisão do impresso (Canva "Sir Fisher Praia") com o proprietário em 22/10/2026: saíram Crispy Spicy Chicken, Marine Sandwich, Budweiser 600, Cachaça Premium e Smirnoff Ice; entraram Corona 600 (R$ 23,90) e Adicional Salada (R$ 19,00). Ficaram confirmados Spaten Longneck 355 mL e Bolinha de Peixe 300 g. Nos empanados, o proprietário decidiu publicar o mesmo número em todos os canais, sempre o peso do peixe empanado: 200 g nos dois Fish & Chips (são 150 g de peixe; decisão de 23/10/2026, migration `20261023160000_cardapio_fish_200g_empanado.sql`) e 120 g no Fisher Burger (são 100 g de peixe). Em 25/10/2026 o proprietário corrigiu a Big Ben Fries para 250 g, a mesma porção da Macaxeira Frita ou Batata Frita (TXT, HTML antigo e impresso diziam 200 g); site, banco (migration `20261025170000_cardapio_big_ben_250g.sql`) e Google atualizados, impresso no Canva ainda com 200 g. No site, o alerta de alergia diz que todos os fritos usam o mesmo óleo e que a cozinha frita em panela separada a pedido. No impresso, por decisão do proprietário, o rodapé ficou curto: "ALERGIA? AVISE ANTES DO PEDIDO: PODE TER CONTAMINAÇÃO CRUZADA. 10% OPCIONAL · NÃO ACEITAMOS CHEQUES · PESOS APROXIMADOS · DECON-CE 0800 275 8001 · PROCON FORTALEZA 151". Patinha de Caranguejo ganhou CRUSTÁCEOS e a Bolinha, PEIXE. “Farota” era erro de digitação de “farofa”.
- Designs no Canva em uso, por decisão do proprietário em 23/10/2026: na mesa, a proposta da auditoria `DAHYx8a8mAI` ("Sir Fisher Praia — PROPOSTA", com ícones de alérgenos ao lado do nome e escolhas de acompanhamento); na entrada, o A3 vertical com Google `DAHY1RSheg4`. Os demais ficam como histórico: o impresso anterior da mesa `DAGyLOfkRJI` e o A3 da entrada `DAHYyJfmU3g` (lista de preços para a porta, Decreto 5.903/2006). O A3 da entrada não traz almoço executivo nem extras, nem legenda de alérgenos (os itens não têm ícones; o cardápio da mesa tem). O cabeçalho dos três A3 traz o logo horizontal em versão clara (letras em creme para o fundo marrom; emblema e bandeirinha nas cores originais) e o título "Cardápio" na Fraunces, a fonte de títulos do cardápio digital, como imagem, porque a API do Canva não troca a família da fonte. Não há endereço (o cliente já está no local); ficam o horário e a nota do Google. Para evitar questionamento da fiscalização, cada prato com peso registrado no catálogo mostra a gramatura numa coluna menor, à esquerda do preço, e cada cerveja ou bebida sem álcool mostra o volume na mesma coluna (coquetéis e doses trazem o volume único ao lado do título da seção, no mesmo estilo); só brownie, adicional de arroz e adicional de salada continuam sem peso, por não haver medida registrada. A faixa de fotos tem três pratos do site: Fish & Chips Sir Fisher no panko (`prato-1200.jpg`), NewCastle e Edimburger. São três proteínas diferentes, e o Edimburger vendeu mais que o camarão alho e óleo e o Fisher Burger nos 12 meses até out/2026. Por decisão do proprietário em 23/10/2026, não há foto do local, já que o cliente já está na porta, nem do London, que não ficou nítida, nem duas fotos de camarão. Tem também o selo Sebrae Diamante, com a frase "Referência em qualidade na Beira-Mar" junto do selo (superlativos como "melhor da orla" ficam fora por exigirem comprovação), e um QR para `https://www.sirfisher.com.br/cardapio/?utm_source=qr_code&utm_medium=offline&utm_campaign=cardapio_entrada`, que no Analytics aparece separado do QR das mesas (`cardapio_restaurante`). Há também a versão em pé, `DAHY1ZXHEN0` ("A3 entrada vertical"), e uma variante dela com cartão no estilo Google Maps e logo do Google, `DAHY1RSheg4`, que só deve ir para impressão com o material oficial do Google ou com autorização de uso da marca (o cartão diz só "Avaliação dos clientes no Google"; nenhum slogan próprio vai dentro dele); as outras usam estrelas próprias e o texto "4,7 no Google · 813 avaliações (out/2026)". O site usa o mesmo aviso curto do impresso na legenda de alérgenos (PT e EN). Ícones e cores dos alérgenos são fixos. Na proposta da mesa, por decisão do proprietário em 23/10/2026, o rodapé da página 2 tem dois blocos colados, sem sobreposição. O de cima é marrom (922,85 a 1073), com endereço, site e telefone centralizados em três colunas iguais. O de baixo é preto (#000000, de 1073 até a borda inferior, da coluna dos coquetéis até a borda direita), com 12 px de folga acima e abaixo dos dez ícones de 100×50, centralizados e espaçados por igual. Em 23/10/2026, a proposta também ganhou uma revisão de alinhamento nas duas páginas. Os itens de cada coluna começam no mesmo x (23, 800, 1200 e 24,13). O preço fica na altura do nome. Os ícones de alérgenos ficam centrados na altura do título. O espaço entre itens é igual dentro de cada seção, e as divisas entre blocos coloridos caem numa linha só. Fotos com moldura "recortada à mão" do Canva tinham bordas onduladas de 1 a 4 px. Elas foram endireitadas com a borda reta de um bloco vizinho por cima, porque a API não troca a moldura. Quem editar no Canva deve manter essas sobreposições. As bandeiras de cartão saíram da mesa: nenhuma lei obriga a exibi-las, e o A3 da entrada já as mostra. O preto foi escolhido pelo critério que ele definiu: a cor de fundo cujo pior contraste é o mais alto. As cores dos rótulos, medidas na exportação, vão do azul-marinho de LEITE (#04306b) ao azul-claro de LACTOSE (#b9dee6); por isso nenhuma cor única deixa os dez legíveis. No preto, o pior caso é LEITE com 1,64:1 e o segundo é AMÊNDOAS com 2,27:1; os outros oito ficam acima de 4:1. No creme, o pior seria LACTOSE com 1,40:1; no marrom do rodapé, LEITE com 1,11:1. Faixas de duas cores e quadros com contorno foram testados e recusados pelo proprietário. Decisões do proprietário para o impresso: a macaxeira não ganha destaque (tem margem menor e o garçom já pergunta o acompanhamento), os pratos para dividir não dizem "servem 2 pessoas" e os destilados ficam até acabar o estoque. Na cópia e no A3 da entrada, as bebidas sem álcool seguem a margem: suco, refrigerante e energético antes das águas (no A3 da entrada, a soda italiana vem logo após o suco).
- O rascunho do banco (`cardapio_produto`) foi realinhado ao catálogo em 22/10/2026 pela migration `20261022200000_cardapio_realinha_rascunho.sql`: 78 publicáveis, os 5 retirados arquivados (não apagados), foto enviada pelo painel preservada e estado `vigente` mantido; a `20261022230000_cardapio_pesos_e_alerta.sql` levou os pesos e o alerta acima, e a `20261022233000_cardapio_aviso_impresso_curto.sql`, a citação do rodapé curto. Nenhuma publicação foi feita; o site segue lendo a cópia embutida. A cada mudança futura: `gerar_migration.py --realinhar <AAAAMMDDHHMMSS>_cardapio_....sql` e `supabase db push` (com `--dry-run` antes).
- Toda mudança de cardápio também vai para o Google: `python scripts/gbp/gbp.py cardapio` (simula) e `--publicar`, depois do push do site. Decisão do proprietário em 22/10/2026.
- Preços, porções e marcações alimentares ainda não receberam uma conferência formal e completa da cozinha/operação; por isso o estado editorial volta a ser `em_conferencia`.
- A interface deve deixar claro quando uma medida diverge ou quando uma informação alimentar foi apenas transcrita do impresso.
- Não se deve transformar ausência de símbolo no impresso em afirmação de ausência de alérgeno.

## Decisões preservadas

- A referência é o cardápio interno versionado; o Hubt não é fonte operacional nem participa dos cálculos de eventos.
- As abas horizontais, busca, modais, legenda de alérgenos, rodapé institucional e botão de voltar ao topo permanecem.
- Os pratos de “Pra Dividir” usam bases de imagem com o sufixo `-para-dividir-sir-fisher`, evitando colisão com as fotos do almoço executivo.
- O aviso geral orienta clientes com alergias ou restrições a consultar a equipe antes do pedido.
- Notas internas, fontes, pendências e divergências técnicas não podem vazar como campos brutos no JSON público.

## Pipeline

```text
scripts/cardapio/catalogo_inicial.py
  -> scripts/cardapio/catalogo_inicial.json
  -> scripts/cardapio/exportar_snapshot.py
  -> site/cardapio/dados/cardapio.json
  -> bloco CARDAPIO-DADOS em site/cardapio/index.html
```

`catalogo_inicial.py` é a origem auditável. Os arquivos JSON e o bloco embutido no HTML são derivados e devem ser regenerados, nunca corrigidos manualmente.

## Regras de publicação

1. Divergência entre fontes fica como `em_conferencia`; não escolher automaticamente um dos valores.
2. Porção divergente não exibe número ao cliente.
3. Porção sem texto fica como não informada, ou em conferência quando existir divergência registrada.
4. Declarações alimentares transcritas do impresso levam aviso de que não substituem ficha técnica.
5. Produto sem marcação no impresso não pode ser anunciado como livre de alérgenos.
6. Mudanças de foto devem manter a separação entre pratos individuais e pratos para compartilhar.

## Conferência necessária com a operação

- validar os 78 preços vigentes;
- confirmar medidas, unidades e rendimento dos pratos para compartilhar;
- revisar ingredientes e alérgenos com a cozinha;
- confirmar receitas divergentes, inclusive a marca do energético do Sherlock Holmes Gin;
- registrar a confirmação por versão, sem apagar a proveniência.

Depois dessa conferência, uma nova alteração pode promover o catálogo de `em_conferencia` para `vigente` e retirar apenas os avisos que deixarem de ser necessários.

## Qualidade e continuidade

- Rodar `catalogo_inicial.py` e depois `exportar_snapshot.py` sempre que a origem mudar.
- Conferir que os 78 produtos continuam presentes.
- Validar que não há campos internos no snapshot público.
- Rodar a suíte de aceitação do cardápio e conferir visualmente desktop e mobile antes de publicar.
- O book de atendimento relacionado fica em `docs/BOOK_QA_ATENDIMENTO.md`.
