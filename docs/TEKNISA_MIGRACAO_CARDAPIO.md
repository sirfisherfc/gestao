# Teknisa: acesso, cadastros e preparação do cardápio

Levantamento concluído em 26/10/2026, pela interface do Chrome. A sessão
abriu o Teknisa na unidade **0002 — SIR FISHER PRAIA**. Esta entrega
registra as telas examinadas, a comparação com o Saipos e a seleção de
103 itens para migrar. A migração ainda não foi executada: nenhum cadastro,
preço ou configuração do Teknisa ou do Saipos foi alterado nesta etapa.
A auditoria adicional identificou três decisões comerciais que aguardam
resposta do usuário antes da execução: limites por produto, molho extra
no Gelo e acréscimo do Drink Cortesia.

Os valores e campos identificados como lidos foram observados na
interface. As ações propostas nas tabelas e nas etapas finais ainda
precisam ser executadas e conferidas no Teknisa.

## Acesso e alcance da leitura

- Entrada solicitada: <https://retail.teknisa.com//#/product#dashboard>.
- Cadastro de produto observado:
  `/cadEst/#/cadEst_produto#ger01900_cadastroproduto`.
- O usuário entrou no Saipos. A leitura do cadastro atual começou pela
  sessão autenticada. O usuário limitou a referência aos **grupos ativos e
  aos itens ativos dentro desses grupos**, incluindo subgrupos e opcionais,
  como molhos e acompanhamentos.
  O botão Entrar no [site oficial da Saipos](https://saipos.com/) aponta
  para <https://conta.saipos.com>.

Os comandos abaixo apareceram na interface. A existência de um comando
não comprova sua configuração, sua permissão de gravação nem seu efeito no
caixa. Para verificar isso será preciso abrir a configuração correspondente
e reler o resultado de cada ajuste autorizado.

## Recursos encontrados

| Área | O que apareceu na interface |
| --- | --- |
| Cadastro de produto | Adicionar, Editar e Excluir. |
| Produto | Dados, estoque, cardápio, catering, produção, compras, fiscal, varejo e integração. |
| Tipo de Árvore | Aba própria no cadastro do produto. A finalidade de cada árvore ainda precisa ser conferida. |
| Vendas do produto | Impostos por Unidade, Configurações do Produto e Configuração de Preço. |
| Parametrização → Vendas → Produto | Tabela Preço, Tabela Preço Geral, Observação, Grupo Promocional, Bloqueio Produto, Produto por Serviço, Campanha Promocional, Família Produtos, Desconto Quantidade/Valor, Impostos, Cupons, CompreGanhe e Imagem Produto. |
| Caixa | Configuração Terminal Caixa, Menu Produtos Combinados, Grupo Operadores, exportação para balança Toledo, TAA Mobile e Controle Comandas. |
| Vendas → Operacional | Abertura, fechamento, manutenção e conferência de caixa; manutenção de vendas; fechamento e monitor de cupom; consolidação e seu cancelamento; fechar dia ForSale; transmitir NFC-e; gerar XML NFC-e/SAT; royalties e marketing; previsão de consumo e aprovação; gerar nota fiscal de venda. |
| Vendas → Importação/Exportação | Importação Parâmetros P&L Gerencial e Integração AudTax. Esta leitura não encontrou um importador de catálogo Saipos nesse menu. |
| Relatórios de vendas | Caixa, vendas, produtos, faturamento, demonstrativos, descontos, cancelamentos, estatísticas gerais e de caixa, preços, ficha técnica, KDS, consumidor, daypart, metas, sangria, notas, no cash, consolidação e ambiente. |
| Relatórios de preços | Relatório Tabela Preço e Produtos Preço Ficha Técnica × Tabela. |
| Relatórios de produtos | Mais vendidos, rentabilidade, composição, impostos, MTC, cupons e ficha técnica. |
| Estoque | Processamento Produto e relatório de entradas. Na parametrização: Parâmetros, Tipo de Retirada e Produtos Processados. |
| Produção, suprimentos e pedidos | Parametrização de Setor, Cadastros por Fornecedor e Ramo de Atividade. |
| Financeiro | Controle Bancário com Cheque, Relatórios e Integração. Na parametrização: Categorias, Títulos a Receber e Classificação. |
| Documentos fiscais | Saída, Imposto, Relacionamento de Impostos, Replicação e Integração por E-mail. |
| Contábil e fiscal | Contas, parâmetros, qualificação do assinante, histórico e representante; NCM, NCM por Produto e integração de fechamento de cupom. |
| Login e acesso | Configuração e política de login. Administração → Controle de Acesso: Operador, Perfil, Perfil Menu, Meu Perfil e ACL. |
| Logs | Operações, Requisição, SQL e Configuração. |

No formulário Adicionar Produto, os campos obrigatórios lidos foram
Código da Árvore, Código do Produto, Nome e Unidade de Medida. O Nome
aceita até 50 caracteres. O Tipo de Produto começa em Compra, enquanto
o Filé Mignon existente foi lido como Estoque; a criação precisa usar o
tipo adequado aos produtos de venda. O formulário foi cancelado vazio,
sem gravação.

O seletor de árvores mostrou a raiz `8 — CARDAPIO PRAIA` e a raiz
`9 — CARDAPIO`. Sob `8`, apareceram os grupos do cardápio principal,
bebidas com e sem álcool e adicionais. O nível exibido não apresentou
executivos. A tabela de preço `001` e os vínculos do caixa lidos usam
produtos da árvore `8`; os cadastros da árvore `9` devem ter sua
finalidade conferida antes de qualquer alteração.

A tela **Tabela Preço Geral**
(`/man/#/man#register%2Fvnd42700_tabelaprecoGeral`) teve carregamento lento
na primeira tentativa. Em nova leitura, abriu e exibiu “Não há registros”,
com as colunas Tabela, Início de Vigência, Fim de Vigência, Status e
Situação, além das ações Adicionar Vigência e Ações. Nenhuma alteração foi
feita. Esse resultado cobre a consulta dessa tela; a tabela `001` já
apareceu com preço de R$ 90,00 na ficha do Filé Mignon e continua como
referência para a conferência dos preços.

### Configuração de produtos combinados

A tela **Configuração Menu Produtos Combinados**
(`/man/#/man#register%2Fvnd80400_layoutprodcombinado`) abriu. O filtro da
unidade `0002` mostrou as configurações `00001 — PADRÃO CAIXA`,
`00002 — PADRÃO POS` e `00003 — PADRÃO TOTEM`.

Nas configurações `00001` e `00002`, a aba **Grupo Produtos Combinados**
exibiu uma grade sem registros, com as colunas Código, Nome, Limite de
seleção e Cor do Botão, além do comando Adicionar. O menu de exportação
ofereceu PDF, XLS e CSV; nenhuma exportação foi baixada.

No POS, o formulário Adicionar foi aberto para leitura e cancelado sem
alteração de campos nem gravação. Ele mostrou código automático `01`,
Nome obrigatório, Limite de Seleção com controle de quantidade inicialmente
em `0` e Cor do Botão obrigatória. A grade voltou a exibir “Não há
registros”. Essas leituras cobrem CAIXA e POS; o conteúdo da configuração
TOTEM ainda precisa ser conferido.

### Grupos e botões do caixa

A tela **Configuração Terminal Caixa**
(`/man/#/man#register%2Fvnd80600_configterminalcaixa`) abriu com filtro de
unidade `0002` e loja `0001 — LOJA PADRAO 2`. Apareceram as configurações
`00001 — PADRÃO CAIXA`, `00002 — PADRÃO POS` e `00003 — PADRÃO TOTEM`, com
vigência em `01/01/2026`.

A configuração do CAIXA tem as abas Config PDV, Caixas Associados, Grupos
Produtos, Grupos Recebimento, Ambiente, Pré-Visualização Layout e Sugestão
Vendas. Na grade **Grupos Produtos**, apareceram ENTRADAS, SANDUICHES,
PARA DIVIDIR, FAMILIA REAL, ADICIONAIS, SOBREMESAS, BEBIDAS, CERVEJAS,
COQUETEIS e DESTILADOS. Essa grade não exibiu um grupo de executivos.
Cada grupo oferece as abas Grupos, Sugestões, SubGrupos e Produtos.

No CAIXA, a aba **SubGrupos** de **PARA DIVIDIR** exibiu uma grade sem
registros. Essa leitura cobre apenas esse grupo e essa configuração.

No POS `00002`, a grade Grupos Produtos carregou os mesmos dez nomes
listados no CAIXA, também sem um grupo de executivos. As cores dos botões
de ENTRADAS diferem entre as duas configurações. A revisão precisa
conferir os vínculos e a apresentação de CAIXA e POS separadamente.

No grupo ENTRADAS, o Crispy continua vinculado, junto do Big Ben e de
outros produtos com código iniciado por 8. Isso exige conferir tanto o
cadastro do produto quanto os botões e vínculos usados no caixa quando
for feita a revisão dos itens retirados do cardápio.

O formulário **Editar** do botão Big Ben, código `8.00.00.030.00`, foi
aberto e cancelado sem alteração de campos nem gravação. Ele oferece nome
do botão em português, inglês e espanhol, Permite Venda DLV, atalhos,
cores, fontes, código de natureza, mensagem, imagem, Cardápio e limite de
produtos selecionados dentro de promoção combinada. Permite Venda DLV
estava em **Sim**. O seletor Cardápio apresentou opções Somente Call
Center e Somente App. As opções lidas citam canais de venda; essa leitura
ainda não comprovou uma configuração de escolhas de molho ou
acompanhamento.

### Tabela de preços da unidade

A tela **Tabela Preço**
(`/man/#/man#register%2Fvnd42400_tabelapreco`) foi lida com filtro da
unidade `0002`. A tabela `001` tem vigência de `06/07/2026` a
`06/07/2100`, **Status Pendente** e **Situação Ativa**, conforme os campos
exibidos.

A grade de produtos foi percorrida com sobreposição até o último código,
`8.11.00.006.00`. Foram registrados **114 códigos únicos**, todos
iniciados por `8`. Os códigos iniciados por `9`, vistos no cadastro geral,
ainda precisam ter seus preços e vínculos localizados.

Nas 114 linhas, Hora Inicial e Hora Final estavam vazias, e os campos
Preço Delivery e Preço Comanda mostravam `0,00`. O preço efetivo nesses
canais depende das regras e dos vínculos do pedido. Vinte linhas da tabela
tinham preço `0,01`, incluindo opções de sabores e molhos; é preciso
conferir como essas linhas compõem os produtos antes de ajustar valores.

A observação completa ficou em
`output/teknisa-2026-10-26/teknisa-precos.json`, na raiz do workspace,
fora dos repositórios. O arquivo contém metadados e as linhas lidas pela
interface, sem credenciais. A conferência do arquivo confirmou 114 linhas,
114 códigos únicos e o último código registrado.

### Observações e escolhas dos produtos

A tela **Cadastro de Observação**
(`/man/#/man#register%2Fvnd57000_cadastroDeObservacao`) listou os cadastros
`01 — PRODUTOS`, `02 — CANCELAMENTO` e `03 — DESCONTO`. Em `01 — PRODUTOS`,
apareceram as abas Grupo Observação, Observações, Observação Por Produto
e Grupo Observações Obrigatórias.

Depois do carregamento, as abas **Observações** e **Grupo Observações
Obrigatórias** exibiram “Não há registros”. A leitura cobre essas duas
abas do cadastro `01`. As outras configurações e os vínculos por produto
ou serviço ainda precisam ser conferidos. Os nomes das abas identificam
os pontos a examinar para associar escolhas a produtos e definir sua
obrigatoriedade; o comportamento dessas escolhas ainda precisa ser
validado no pedido.

A preparação adicional abriu os formulários novos e os cancelou sem
preencher ou salvar. Os campos úteis para a implementação foram:

| Tela do Teknisa | O que foi observado | O que a leitura ainda não comprovou |
| --- | --- | --- |
| Observação | Código, Nome, Tipo Adicionar/Remover/Observação, Produto vinculado, nomes em inglês/espanhol, exibição no aplicativo, destaque no KDS e ordem. | A ficha nova não mostrou preço ou quantidade máxima. A forma de cobrar o produto vinculado ainda precisa ser validada. |
| Observação por produto | Grade com Código, Nome e Quantidade Mínima de Observações. | A grade não mostrou mínimo e máximo separados por subgrupo nem preço de opcional. |
| Grupo de Observações Obrigatórias | Nome obrigatório e aba Ocorrências Obrigatórias do Grupo. | A aba filha não apresentou conteúdo acessível antes de gravar; a regra de obrigatoriedade por grupo ainda precisa ser conferida. |
| Grupo de Produtos Combinados | Código, Nome, Limite de seleção inicialmente `0` e Cor do Botão. | A ficha nova não mostrou mínimo, preço, produto vinculado ou impressão de cozinha. O significado do limite ainda precisa ser validado. |

Essas leituras identificaram cadastros de observação e vínculos, mas
ainda não comprovaram uma sequência completa para reproduzir os 118
vínculos da seleção com mínimos, máximos e acréscimos do Saipos. A
execução precisa conferir esse funcionamento em documentação técnica,
em cadastro existente que permita leitura ou em validação adequada após
a definição das regras comerciais. O arquivo local
`output/teknisa-2026-10-26/teknisa-opcionais-preparacao-ui.json` preserva
os campos lidos e os limites dessa preparação.

## Cadastros conferidos e pontos a revisar

O produto **Filé Mignon**, código `8.00.05.000.00`, foi aberto. Ele está
ativo, tem tipo **Estoque** e preço de **R$ 90,00** na unidade `0002`,
tabela `001`. Nas configurações `00001 — PADRÃO CAIXA` e
`00002 — PADRÃO POS`, pertence ao grupo **PARA DIVIDIR**. Esses campos
coincidem com o prato para compartilhar da referência local. O executivo
de filé mignon tem outro preço, porção e acompanhamentos.

A lista de produtos foi percorrida do começo ao fim. Nessa leitura, os
nomes exibidos não identificaram uma seção de executivos nem produtos com
“executivo” ou “menu”. Ainda é preciso conferir vínculos por serviço e
outros cadastros antes de concluir que os sete pratos estão ausentes.

| Produto ou assunto | O que foi visto | Conferência necessária |
| --- | --- | --- |
| Big Ben Fries | Códigos `8.00.00.030.00` e `9.00.00.000.00`, com nomes semelhantes. | Verificar tipo, uso, preço e vínculo de cada código. A porção atual definida pelo proprietário é 250 g. |
| Códigos iniciados por 8 e 9 | Há outros nomes semelhantes nas duas séries. | Entender a finalidade de cada série antes de desativar ou unificar produtos. |
| Crispy Spicy Chicken | Códigos `8.00.00.040.00` e `9.00.00.030.00` listados; ainda vinculado a ENTRADAS no caixa. O Saipos o mantém ativo em APERITIVOS por R$ 37,00. | O usuário reafirmou a retirada em 26/10/2026. O item foi excluído da seleção de migração. Conferir os códigos e vínculos antes de aplicar a retirada no Teknisa. |
| Marine Sandwich | Códigos `8.00.10.010.00` e `9.00.00.060.00` listados. O Saipos o mantém ativo em APERITIVOS por R$ 46,00. | O usuário reafirmou a retirada em 26/10/2026. O item foi excluído da seleção de migração. Conferir os códigos e vínculos antes de aplicar a retirada no Teknisa. |
| Smirnoff Ice | Código `8.05.10.190.00` listado por R$ 15,00. O Saipos mantém ativo “Sminoff Ice” em COQUETÉIS pelo mesmo preço. | O usuário reafirmou a retirada em 26/10/2026. O item foi excluído da seleção de migração. Conferir os vínculos antes de aplicar a retirada no Teknisa. |
| Cachaça Premium | “Dose de Cachaças Premium” está ativa no Saipos por R$ 12,00 e ainda não tem correspondência direta na tabela `001` lida. | O usuário reafirmou a retirada em 26/10/2026. O item foi excluído da seleção de migração. Conferir o cadastro geral para identificar eventuais vínculos de venda. |
| Adicional Salada | Código `8.00.05.090.00` já existe; preço de R$ 19,00 confirmado na tabela `001` da unidade `0002`. | Conferir porção, vínculos e canais usados pela operação. |
| Corona | Código `8.05.00.080.00`, com R$ 23,90 confirmado na tabela `001`, e um cadastro separado de longneck. | Conferir volume, vínculos e canais. A referência local e o Saipos ativo incluem Corona 600 mL por R$ 23,90. |
| London / Original | `LONDON FISH AND CHIPS UN`, código `9.00.00.050.00`, e Original `8.00.00.090.00` listados. | Conferir receita e finalidade de cada código. A referência atual usa London — Fish & Chips. |

Esses registros combinam achados da lista e leituras específicas indicadas
na tabela. O status dos itens antigos no cadastro de produto do Teknisa e
o uso das duas séries de códigos ainda precisam ser conferidos.

## Referências para comparar com o Saipos

O Saipos mostra um total geral de 198 itens. Esse número inclui registros
que ainda precisam passar pelos filtros definidos pelo usuário e não
representa a quantidade de produtos a migrar. Um item ativo que pertença
a um grupo inativo fica fora da referência desta tarefa.

A leitura filtrada reuniu **12 grupos ativos, 107 vínculos e 107 IDs
únicos**. Em 26/10/2026, o usuário respondeu **“Aplicar as retiradas já
definidas”** para Crispy Spicy Chicken, Marine Sandwich, Smirnoff Ice e
Cachaças Premium. A cópia preparada para migração remove esses quatro
IDs e contém **103 itens únicos nos mesmos 12 grupos**. A leitura original
de 107 itens foi preservada; nenhum cadastro do Saipos foi alterado.

| Grupo ativo do Saipos | Itens lidos | Seleção para migrar |
| --- | ---: | ---: |
| MENU EXECUTIVO | 7 | 7 |
| BEBIDAS | 9 | 9 |
| CERVEJAS | 11 | 11 |
| APERITIVOS | 21 | 19 |
| COQUETÉIS | 13 | 12 |
| Para Dois | 6 | 6 |
| DESTILADOS | 18 | 17 |
| SOBREMESA | 4 | 4 |
| Outros | 9 | 9 |
| Quarta do Camarão | 1 | 1 |
| Prime | 7 | 7 |
| Promoções | 1 | 1 |
| **Total** | **107** | **103** |

O catálogo geral local tem **78 produtos publicáveis**. A origem editorial
é `scripts/cardapio/catalogo_inicial.py`, com dados em
`scripts/cardapio/catalogo_inicial.json`; o site recebe o derivado
`../site/cardapio/dados/cardapio.json`. O almoço executivo possui página e
lista próprias em `../site/almoco-executivo/index.html`.

O cadastro ativo do Saipos, com as quatro retiradas reafirmadas pelo
usuário, orienta a seleção dos grupos e itens. As fontes locais registram
o cardápio publicado e as decisões recentes do proprietário. A conferência
formal completa dos preços, porções e
declarações alimentares ainda está pendente, conforme
[HANDOFF_CARDAPIO.md](HANDOFF_CARDAPIO.md) e
[CARDAPIO_CONFERENCIA.md](CARDAPIO_CONFERENCIA.md). O inventário antigo
`site/cardapio/cardapio.txt`, citado no histórico, já não existe na árvore
atual. Ele não serve como exportação atual do Saipos.

Decisões recentes a preservar na migração:

- A decisão de 22/10/2026 retirou Crispy Spicy Chicken, Marine Sandwich,
  Budweiser 600, Cachaça Premium e Smirnoff Ice do cardápio publicado.
  Crispy, Marine, “Sminoff Ice” e “Dose de Cachaças Premium” continuam
  ativos no Saipos; em 26/10/2026, o usuário reafirmou sua retirada da
  migração. Budweiser 600 não apareceu na seleção ativa lida. Conferir os
  vínculos no Teknisa antes de aplicar as retiradas.
- Manter Corona 600 mL por R$ 23,90 e Adicional Salada por R$ 19,00.
- Spaten longneck: 355 mL. Bolinha de Peixe Cremosa: 300 g.
- Fish & Chips Sir Fisher e London: 200 g de peixe empanado, preparados com
  150 g de peixe. Fisher Burger: 120 g de peixe empanado, com 100 g de peixe.
- Big Ben Fries: 250 g, decisão de 25/10/2026. O impresso do Canva ainda
  precisa receber essa correção; site, banco e Google já foram atualizados
  na tarefa anterior.
- Usar os nomes London e Patinha de Caranguejo. Corrigir “farota” para
  “farofa” onde esse erro aparecer.
- Preservar a escolha entre batata frita e macaxeira nos pratos em que ela
  está registrada. O número de pessoas servido pelos pratos para
  compartilhar ainda precisa de confirmação.
- As marcações alimentares foram transcritas do impresso e precisam de
  conferência com a cozinha. O aviso atual explica que os fritos usam o
  mesmo óleo e que a equipe frita em panela separada a pedido.

### Pratos executivos da referência publicada

Todos têm **150 g de proteína**, são individuais e incluem os
acompanhamentos descritos abaixo. Os preços vieram da página de almoço
executivo. A leitura dos sete itens ativos no Saipos confirmou esses sete
preços.

| Nome | Preço | Descrição e acompanhamentos |
| --- | ---: | --- |
| Menu Peito de Frango | R$ 31,00 | Peito de frango com ervas, arroz de brócolis, macaxeira, farofa panko, salada e molho de manga. |
| Menu Picanha Suína | R$ 34,00 | Picanha suína grelhada, arroz de brócolis, batata frita, farofa panko, salada e molho barbecue. |
| Menu Filé de Peixe Empanado | R$ 38,00 | Filé de peixe empanado, arroz de brócolis, batata frita, farofa de ovos e chutney de manga. |
| Menu Filé de Peixe Grelhado | R$ 41,00 | Filé de peixe grelhado, arroz de brócolis, batata frita, salada, farofa panko e molho tártaro. |
| Menu Carne de Sol | R$ 46,00 | Carne de sol na chapa, arroz de alho, macaxeira, farofa de bacon, salada e molho barbecue. |
| Menu Filé Mignon | R$ 47,00 | Filé mignon ao molho madeira, arroz branco, batata frita, farofa panko, salada e molho rosé. |
| Menu Picanha Importada | R$ 52,00 | Picanha grelhada na char broiler, arroz de alho, batata frita, farofa de ovos, salada e molho de alho. |

Horário publicado: **segunda a sexta-feira, das 10h às 14h, exceto
feriados**. A promoção de terça tem horário próprio: **11h às 14h**, exceto
feriados. São dois pratos iguais para duas pessoas, com consumo no local;
o segundo sai por conta da casa. A configuração dessa promoção no Teknisa
ainda precisa ser examinada, incluindo seu efeito no lançamento da
cozinha, na conta e nos relatórios.

Na leitura atual do Saipos, os sete executivos apresentaram os mesmos
quatro grupos ativos e opções com acréscimo de **R$ 0,00**. O editor do
**PF Filé mignon**, ID `15125389`, foi lido diretamente. Depois, os
conjuntos de IDs, nomes e preços das opções dos sete pratos foram
relacionados às definições globais, com correspondência única. Essas
quatro definições exigem **mínimo 1 e máximo 1 escolha** e impressão em
uma linha. A leitura cobre o cadastro e suas associações; o comportamento
no pedido ainda precisa ser testado no Teknisa. As descrições da tabela
acima registram os acompanhamentos da página publicada.

| Grupo no Saipos | Opções lidas |
| --- | --- |
| Arroz | Branco e brócolis. |
| Batata ou Macaxeira | Batata e macaxeira. |
| Molhos | Alho, barbecue, chutney de MANGO, ketchup de goiabada, ketchup, maionese, rosé e tártaro. |
| Farofa | Panko, bacon e ovo. |

No PF Filé mignon, os IDs das definições lidas são Arroz `1594247`, Batata
ou Macaxeira `1594248`, Molhos `1594251` e Farofa `1594256`. Os IDs de
associação ao prato são outros (`19287100` a `19287103`). Ao comparar
produtos, é preciso conferir esses IDs e as opções: outros grupos também
se chamam Molhos e têm quantidades diferentes de opções.

### Bebidas sem álcool: leitura inicial do Saipos

Foram lidos nove itens ativos no grupo de bebidas, disponíveis no salão e
no digital: água sem gás R$ 5,00, água com gás R$ 6,00, água de coco
R$ 5,00, água tônica R$ 6,00, refrigerante lata, suco copo R$ 11,00,
energético R$ 16,00, soda italiana R$ 15,00 e sumo de limão R$ 3,00.

O **Refrigerante lata** tem preço base de **R$ 0,00** e sete opções de
**R$ 8,00** cada: Guaraná, Guaraná Zero, Pepsi, Pepsi Black, Soda Limonada,
Sukita Uva e Sukita Laranja. O preço de R$ 8,00 publicado no site
corresponde ao produto com uma dessas opções. Ao levar essa estrutura ao
Teknisa, é preciso conferir o preço final do pedido e como o sistema
aplica o valor da opção.

O **Suco copo** oferece abacaxi, acerola, limão, caju, cajá, maracujá,
morango e manga. A **Soda Italiana** oferece maçã verde, tangerina,
gengibre, grenadine e cranberry. Os grupos de refrigerantes, suco e soda
exigem uma escolha, com mínimo e máximo `1`. Os sabores de suco e soda
têm acréscimo de R$ 0,00.

## Subgrupos, opcionais e regras lidos no Saipos

Todos os 107 produtos ativos foram expandidos para ler os subgrupos e as
opções ativos. A leitura original reuniu **57 produtos com opções, 121
associações, 20 conjuntos de opções e 82 opções nesses conjuntos**. Cada
conjunto usa IDs próprios; nomes iguais não foram usados para decidir se
duas configurações eram a mesma.

Foram lidas 23 definições globais candidatas. Os 20 conjuntos usados pelos
produtos corresponderam, cada um, a uma única definição global pelo
conjunto completo de IDs, nomes e preços das opções. Assim foram
registrados os limites, a obrigatoriedade e o modo de impressão dos 121
vínculos. As três definições globais adicionais ficaram fora desse
mapeamento.

Após as quatro retiradas, a seleção de migração contém **54 produtos com
opções, 118 associações, 19 conjuntos e 78 opções nesses conjuntos**. A
definição exclusiva de Cachaças Premium saiu dessa seleção.

| Grupo de escolhas observado | Regra lida | Aplicação a conferir no Teknisa |
| --- | --- | --- |
| Arroz, Batata ou Macaxeira, Molhos e Farofa dos executivos | Cada grupo exige uma escolha; opções incluídas por R$ 0,00. | Associar os quatro grupos aos sete executivos e conferir a impressão. |
| Molhos incluídos em outros pratos | Há um conjunto de sete opções com IDs próprios, além do conjunto de oito dos executivos; escolha obrigatória, mínimo e máximo `1`. | Preservar as associações por produto e distinguir os conjuntos. |
| MOLHO EXTRA | Mínimo `0`, máximo `10`; oito opções de R$ 3,00 cada. | Cobrar o extra conforme a quantidade escolhida, separado do molho incluído no prato. |
| Adicione porção de batata ou macaxeira | Mínimo `0`, máximo `1`; BATATA R$ 9,90 e MACAXEIRA R$ 9,99. | Preservar os valores lidos e conferir os vínculos com os adicionais do Teknisa. |
| Sabor Pastel | Uma escolha entre queijo, carne e camarão, sem acréscimo. | Configurar a escolha do sabor conforme o cadastro atual. |
| Escolha a Massa | Uma escolha, com dois itens ativos. | Conferir a associação e o nome da massa ao migrar o produto correspondente. |
| Polpa e destilados dos coquetéis | Os grupos usados exigem uma escolha; os acréscimos variam com o destilado. | Conferir o total do pedido após cada combinação. |
| Doses Rum Praia, definição `1599364` | Mínimo `1`, máximo `111`; Bacardi ou Montila, sem acréscimo. | Revisar a intenção do limite antes de configurá-lo no novo sistema. |
| Dose Martini Praia, definição `1599365` | Mínimo `1`, máximo `111`; Bianco ou Rosato, sem acréscimo. | Revisar a intenção do limite antes de configurá-lo no novo sistema. |

Os máximos `111` de Rum e Martini e `222` de Cachaças Premium foram
conferidos novamente no DOM e na tela, com rótulo e valor do campo
registrados. São limites dessas definições específicas. A definição de
Cachaças Premium, `1599367`, foi excluída da seleção de migração pela
decisão do usuário. Nenhum desses limites foi alterado no Saipos.

Os editores foram fechados com Cancelar. Nenhum pedido foi criado para
testar a aplicação dessas regras. A migração deve validar a seleção no
caixa, o preço final e a impressão da cozinha.

## Comparação dos preços do Saipos com o Teknisa

O cruzamento dos 107 IDs ativos lidos com os 114 códigos da tabela `001`
do Teknisa encontrou 68 correspondências com preço igual, nove casos de
estrutura ou correspondência a conferir e 30 itens sem correspondência
direta nessa tabela. Os itens do Saipos indicaram os canais Salão e
Cardápio digital. A comparação usou correspondências explícitas por nome;
porções, receitas e vínculos precisam de conferência própria.

Após aplicar as quatro exclusões decididas pelo usuário à cópia para
migração, a comparação dos **103 itens selecionados** ficou assim:

| Resultado na seleção para migrar | Quantidade | O que precisa ser feito |
| --- | ---: | --- |
| Produto com correspondência e preço igual | 65 | Conferir também porção, receita, canais e opções. Esses campos não foram validados pelo preço. |
| Estrutura ou correspondência a conferir | 9 | Conferir quatro coquetéis, Refrigerante, London/Original, Macaxeira, Batata e Patinha/Pata. |
| Sem correspondência direta na tabela `001` lida | 29 | Buscar no cadastro geral e em outras tabelas antes de decidir criar produtos. |

Os 29 itens da última linha se distribuem assim:

| Grupo | Itens a localizar no Teknisa |
| --- | --- |
| MENU EXECUTIVO | Os sete pratos executivos. |
| CERVEJAS | Stella Puro Gold Longneck, R$ 12,90. |
| APERITIVOS | Salmon and Chips, R$ 52,00. |
| COQUETÉIS | Drink Cortesia, Margarita e Lata Beats Sense/Tropicall. |
| DESTILADOS | Dose Jose Cuervo. |
| SOBREMESA | Brownie Desconto Funcionario. |
| Outros | Embalagem, Adicional Ovo, Farofa, Gelo, Molhos e Rolha. |
| Quarta do Camarão | NewCastle + Camarão alho e óleo. |
| Prime | Os sete pratos PF com sufixo Prime. |
| Promoções | COMBO 3+1 choppe Brahma. |

O London ativo no Saipos custa R$ 45,00. Na tabela do Teknisa, Original
também custa R$ 45,00, e o cadastro geral tem um London na série `9`.
Esses nomes e preços ainda exigem conferir receita e vínculos antes de
escolher o cadastro correspondente. O Sir Fisher Fish & Chips está no
Teknisa e no site, mas não apareceu nos 107 itens ativos lidos do Saipos.
No Saipos, London tem a escolha obrigatória de uma massa: **Massa da Casa
(Panko)** ou **Massa Cerveja (Original)**, sem acréscimo. Essa estrutura
representa as duas massas em um produto. As quatro retiradas explícitas
do usuário não incluem o Sir Fisher; a migração deve preservar a escolha
de panko.

Macaxeira e Batata Frita são itens separados no Saipos, ambos por
R$ 27,00. A tabela do Teknisa tem Macaxeira ou Batata Frita por R$ 27,00,
além de linhas com valores diferentes usadas em outros contextos. A
migração precisa preservar a porção pedida e seu preço. Patinha e Pata de
Caranguejo aparecem em dois códigos do Teknisa, ambos por R$ 55,00; sua
finalidade precisa ser conferida antes de unificar vínculos.

Dois IDs ativos de Café Expresso no Saipos, um em SOBREMESA e outro em
Outros, custam R$ 5,00 e têm o mesmo candidato na tabela do Teknisa. A
seleção preserva os dois IDs e seus grupos. Esta migração não vai
deduplicá-los; os vínculos precisam manter as funções desses grupos.

### Preços dos coquetéis: valores lidos e ações propostas

Os cálculos abaixo somam o preço base e o acréscimo do opcional lidos no
Saipos. A conferência foi feita nos cadastros; o preço final aplicado em
um pedido ainda precisa ser validado no Teknisa.

| Produto e escolha | Base + acréscimo do Saipos | Linha lida na tabela do Teknisa | Ação proposta |
| --- | ---: | ---: | --- |
| Caipirinha com cachaça nacional | R$ 18,00 + R$ 0,00 = R$ 18,00 | Produto-base CAIPIRINHA em R$ 0,01. | Conferir a composição do produto e preservar o total de R$ 18,00. |
| Caipirinha com Ypioca 150 | R$ 18,00 + R$ 4,00 = R$ 22,00 | CAIPIRINHA YPIOCA 150 em R$ 18,00. | Corrigir a correspondência ou o preço para que a escolha Ypioca 150 resulte em R$ 22,00. |
| Caipiroska com vodka nacional | R$ 20,00 + R$ 0,00 = R$ 20,00 | Nacional em R$ 20,00. | Preservar esse valor e conferir o vínculo. |
| Caipiroska com Sky | R$ 20,00 + R$ 2,00 = R$ 22,00 | Sky em R$ 28,00. | Corrigir os vínculos ou valores de Sky e Absolut, que estão invertidos na tabela lida. |
| Caipiroska com Absolut | R$ 20,00 + R$ 8,00 = R$ 28,00 | Absolut em R$ 22,00. | Usar R$ 28,00 para a escolha Absolut após conferir os vínculos. |
| Caipifruta com nacional, Sky ou Absolut | R$ 22,00 + R$ 0,00/R$ 2,00/R$ 8,00 = R$ 22,00/R$ 24,00/R$ 30,00. | Variantes em R$ 22,00/R$ 24,00/R$ 30,00. | Preservar os três totais e conferir a estrutura do produto-base e da polpa. |
| Gin Tônica com gin nacional | R$ 21,00 + R$ 0,00 = R$ 21,00 | Nacional em R$ 23,00. | Corrigir os vínculos ou valores de Nacional e Gordon’s, que estão invertidos na tabela lida. |
| Gin Tônica com Gordon’s | R$ 21,00 + R$ 2,00 = R$ 23,00 | Gordon’s em R$ 21,00. | Usar R$ 23,00 para a escolha Gordon’s após conferir os vínculos. |

A tabela do Teknisa também tem uma linha chamada CAIPIRINHA VODKA SKY
por R$ 22,00. O nome exige revisão ao relacionar os produtos, pois a
definição ativa Caipirinha Praia do Saipos oferece cachaça nacional e
Ypioca 150. Essas ações são propostas para a migração; nenhuma linha foi
alterada.

Os arquivos locais ficam em `output/teknisa-2026-10-26/`, na raiz do
workspace, fora dos repositórios: `saipos-precos-ativos.json` preserva a
leitura de 107 itens; `saipos-base-migracao.json` contém os 103
selecionados; `comparacao-precos-ativos.json` e `comparacao-migracao.json`
registram os cruzamentos. O arquivo `saipos-ativos.json` contém a leitura
completa dos produtos, associações e opções; `saipos-regras-opcoes.json`
registra as definições globais lidas. `saipos-captura-validacao.json`
registra a conferência de hashes da captura e dos dados em três conjuntos:
produtos, vínculos e opções. `saipos-evidencias-limites.json` registra a
releitura dos limites atípicos. Foram validadas as contagens, a unicidade
dos IDs e as correspondências das definições.

## Auditoria adicional do Saipos antes da execução

O usuário pediu uma nova conferência do Saipos antes de atualizar o
Teknisa. A auditoria offline dos 107 itens e das 82 opções não encontrou
preços negativos, grupos vazios, conjuntos obrigatórios sem opções,
mínimos maiores que o máximo ou que a quantidade de opções, nem
referências a definições ausentes. Também não encontrou IDs ou nomes de
opção repetidos dentro de um mesmo conjunto.

O preço base zero do Refrigerante está relacionado a uma escolha
obrigatória de R$ 8,00, e os valores zero dos acompanhamentos incluídos
estão previstos nas opções. A diferença entre MACAXEIRA R$ 9,99 e BATATA
R$ 9,90 é um preço válido no cadastro; nesta etapa, R$ 9,99 será
preservado. Os sete executivos Prime, o brownie de funcionário e os combos
possuem nomes de uso próprios e permanecem separados na seleção.

A [orientação oficial do Saipos sobre opcionais](https://intercom.help/meajuda-saipos/pt-BR/articles/17020505-cadastro-e-edicao-de-opcionais-criados-manualmente)
explica o compartilhamento dos preços e limites entre os produtos que
usam uma definição e reconhece opções repetidas na impressão. Por isso,
a quantidade de nomes de opções, sozinha, não esclarece o efeito dos
máximos `111` no pedido. A regra desejada para cada dose continua como
decisão comercial a registrar.

O resumo de canais da lista mostra Salão e Cardápio digital. Na leitura
adicional dos editores, os dois cafés também estavam marcados para Totem
Saipos, com Delivery e Pedido Online desmarcados. Ambos cobram serviço e
imprimem em Cozinha 1, um diretamente e outro pela configuração da
categoria. Esses campos não comprovam a finalidade histórica de cada ID;
a seleção preserva os dois. A definição dos canais do Teknisa deve
considerar o uso real da operação e os vínculos lidos em cada terminal.

Três decisões foram apresentadas ao usuário antes da gravação no Teknisa:

| Ponto observado no Saipos | Proposta aguardando resposta |
| --- | --- |
| Rum e Martini permitem até 111 escolhas de marca; Molhos avulso tem base zero e usa grupo opcional `0..10`, permitindo nenhuma escolha pelos campos do cadastro. | Usar `1..1` para Rum/Martini e exigir ao menos uma opção apenas na venda avulsa de Molhos. Manter os extras dos pratos em `0..10`. |
| Gelo, ID `19440724`, tem o vínculo `19440727` com MOLHO EXTRA `1576146`. | Retirar somente esse vínculo do Gelo; preservar Salada, Adicional Ovo e os outros produtos que usam o grupo. |
| Drink Cortesia, ID `19413680`, tem base R$ 0,01 e usa Caipirinha Praia `1599653`, com nacional a R$ 0,00 e Ypioca a R$ 4,00 de acréscimo. | Definir se as duas marcas da cortesia devem resultar em R$ 0,01 ou se Ypioca deve continuar em R$ 4,01. |

As associações foram comprovadas na leitura dos cadastros. A intenção
comercial e o comportamento no pedido ainda precisam da decisão e da
validação indicadas. Para exigir molho no produto avulso, o Teknisa deve
usar uma regra por produto ou um grupo separado: o grupo de extras também
atende a pratos nos quais a compra de molho é opcional. Da mesma forma,
uma regra própria da cortesia deve preservar o acréscimo de R$ 4,00 da
Ypioca na Caipirinha normal.

Os achados, os IDs e as propostas estão no arquivo local
`output/teknisa-2026-10-26/auditoria-saipos-adicional.json`. A atualização
do Teknisa aguarda essas respostas; nenhum cadastro do SaaS foi alterado
nesta auditoria.

## Etapas para ajustar e conferir o cardápio

1. Usar a seleção de 103 itens e os opcionais preparados, respeitando as
   quatro retiradas decididas pelo usuário. Reconferir as fontes se houver
   mudança na operação antes da implementação.
2. Ler o significado dos códigos iniciados por 8 e 9, o tipo dos produtos
   e seus vínculos com caixa, POS e serviços. Registrar qual cadastro será
   usado em cada canal antes de corrigir possíveis duplicidades.
3. Conferir os executivos já cadastrados. Criar somente os que faltarem,
   com grupo próprio, descrição, preço, porção e vínculos corretos. Manter
   separados o executivo de filé mignon, o prato para compartilhar e o
   filé mignon trinchado.
4. Conferir tabelas de preço, unidade e grupos exibidos no caixa e no POS.
   Ajustar os produtos antigos e as medidas conforme a comparação.
5. Conferir escolhas, adicionais e observações de cozinha. Examinar a regra
   de horário do executivo e a promoção de terça antes de configurá-las.
6. Reler os cadastros salvos e conferir sua exibição nos canais usados pela
   equipe. Validar preços, escolhas e impressão da cozinha por um fluxo de
   teste próprio, quando o ambiente oferecer esse recurso.
7. Registrar os códigos alterados, os resultados e as pendências. Mudanças
   no cardápio público também seguem a rotina existente de site e Google,
   com comparação posterior dos dados publicados.

O levantamento e a comparação dos cadastros foram concluídos. Permanecem
para a execução da migração a conferência dos vínculos no Teknisa, a
gravação dos ajustes e os testes de pedido, preço e impressão. A seleção
de 103 itens e os achados acima permitem preparar essa execução.
