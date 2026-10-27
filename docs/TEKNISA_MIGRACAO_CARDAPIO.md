# Migração do cardápio Saipos para o Teknisa

Levantamento iniciado em 26/10/2026, pela interface do Chrome, com
execução e conferências em 26 e 27/10/2026. A sessão
abriu o Teknisa na unidade **0002 — SIR FISHER PRAIA**. Esta entrega
registra as telas examinadas, a comparação com o Saipos e a seleção de
103 itens aprovados para migração. O usuário aprovou as regras comerciais
após a auditoria adicional e autorizou sua execução. Os cadastros comerciais
foram salvos e conferidos; três CESTs e os testes nos aparelhos continuam
pendentes. O Saipos permanece preservado como fonte da leitura original.

Os valores e campos identificados como lidos foram observados na
interface durante o levantamento. As gravações confirmadas constam na
seção de execução. As demais ações ainda precisam ser realizadas e
conferidas no Teknisa.

**Estado atual da execução:** 45 SKUs novos salvos e conferidos por código,
nome e unidade; três produtos da árvore Praia inativados; 159 linhas de
preço relidas, após 48 inclusões e oito correções. Os sete executivos
comuns e os sete Prime receberam seus preços e descrições. CAIXA e POS
foram salvos e relidos com 12 grupos, oito subgrupos e 124 botões cada.
Foram conferidos 494 vínculos de observação usados nos 48 SKUs do menu
que têm perguntas. A loja recebeu a tabela 001 e os 125 SKUs necessários
têm rota para a impressora ELGIN existente. A consulta fiscal recarregada
confirmou 48 cadastros de imposto por unidade, 52 NCMs e 23 CESTs. Faltam
os códigos de apoio para o CEST de Stella Puro Gold e das duas Sukitas.
Antes de operar hoje, 27/10/2026, ainda é preciso resolver esses campos
e testar carga, escolhas, preços, impressão e XML fiscal nos aparelhos.
Nenhuma venda real foi criada.

As seções de levantamento e comparação inicial conservam o diagnóstico
anterior às gravações. A seção **Execução da migração** registra os
resultados já salvos e as conferências que faltam para encerrar a tarefa.

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

## Levantamento inicial dos recursos

Este registro descreve as telas antes das gravações da migração. Contagens
e ausências relatadas aqui correspondem àquela leitura inicial.

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

## Cadastros na leitura inicial e encaminhamento

O produto **Filé Mignon**, código `8.00.05.000.00`, foi aberto. Ele está
ativo, tem tipo **Estoque** e preço de **R$ 90,00** na unidade `0002`,
tabela `001`. Nas configurações `00001 — PADRÃO CAIXA` e
`00002 — PADRÃO POS`, pertence ao grupo **PARA DIVIDIR**. Esses campos
coincidem com o prato para compartilhar da referência local. O executivo
de filé mignon tem outro preço, porção e acompanhamentos.

A lista inicial de produtos foi percorrida do começo ao fim. Nessa leitura, os
nomes exibidos não identificaram uma seção de executivos nem produtos com
“executivo” ou “menu”. A execução posterior criou os sete executivos e os
sete Prime com códigos próprios, conforme os recibos adiante.

| Produto ou assunto | O que foi visto | Conferência necessária |
| --- | --- | --- |
| Big Ben Fries | Códigos `8.00.00.030.00` e `9.00.00.000.00`, com nomes semelhantes. | Verificar tipo, uso, preço e vínculo de cada código. A porção atual definida pelo proprietário é 250 g. |
| Códigos iniciados por 8 e 9 | Há outros nomes semelhantes nas duas séries. | Entender a finalidade de cada série antes de desativar ou unificar produtos. |
| Crispy Spicy Chicken | Na leitura inicial, `8.00.00.040.00` e `9.00.00.030.00` estavam listados, com vínculo em ENTRADAS. O Saipos o mantém ativo por R$ 37,00. | Retirada reafirmada pelo usuário. O código Praia `8.00.00.040.00` já foi inativado e saiu da consulta da tabela 001; a conferência final dos layouts continua. O cadastro global da árvore 9 foi preservado. |
| Marine Sandwich | Na leitura inicial, `8.00.10.010.00` e `9.00.00.060.00` estavam listados. O Saipos o mantém ativo por R$ 46,00. | Retirada reafirmada pelo usuário. O código Praia `8.00.10.010.00` já foi inativado e saiu da consulta da tabela 001; a conferência final dos layouts continua. O cadastro global da árvore 9 foi preservado. |
| Smirnoff Ice | A leitura inicial encontrou `8.05.10.190.00` por R$ 15,00. O Saipos mantém ativo “Sminoff Ice” pelo mesmo preço. | Retirada reafirmada pelo usuário. O código Praia já foi inativado e saiu da consulta da tabela 001; a conferência final dos layouts continua. |
| Cachaça Premium | “Dose de Cachaças Premium” está ativa no Saipos por R$ 12,00 e ainda não tem correspondência direta na tabela `001` lida. | O usuário reafirmou a retirada em 26/10/2026. O item foi excluído da seleção de migração. Conferir o cadastro geral para identificar eventuais vínculos de venda. |
| Adicional Salada | Código `8.00.05.090.00` já existe; preço de R$ 19,00 confirmado na tabela `001` da unidade `0002`. | Conferir porção, vínculos e canais usados pela operação. |
| Corona | Código `8.05.00.080.00`, com R$ 23,90 confirmado na tabela `001`, e um cadastro separado de longneck. | Conferir volume, vínculos e canais. A referência local e o Saipos ativo incluem Corona 600 mL por R$ 23,90. |
| London / Original | `LONDON FISH AND CHIPS UN`, código `9.00.00.050.00`, e Original `8.00.00.090.00` listados. | O plano usa o London da árvore 9, com preço local de R$ 45,00 já salvo e relido na tabela 001. A escolha de massa e os vínculos seguem em conferência. |

Esses registros combinam a lista inicial com as gravações já confirmadas.
A raiz 8 identifica o CARDAPIO PRAIA; a raiz 9 é o CARDAPIO geral. Os quatro
produtos reaproveitados da raiz 9 receberam somente preço local na tabela
001, preservando seus nomes e estado ativo globais.

## Referências para comparar com o Saipos

O Saipos mostrou um total geral de 198 itens antes dos filtros. A leitura
dos grupos e itens ativos resultou nos 107 IDs abaixo. Um item ativo que
pertença a um grupo inativo fica fora da referência desta tarefa.

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
  migração. Budweiser 600 não apareceu na seleção ativa lida. As três
  inativações na árvore Praia já foram aplicadas; os layouts seguem em
  conferência.
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

Após as quatro retiradas, a base anterior às novas regras comerciais contém **54 produtos com
opções, 118 associações, 19 conjuntos e 78 opções nesses conjuntos**. A
definição exclusiva de Cachaças Premium saiu dessa seleção. A base aprovada
posteriormente passou a 53 produtos com opções e 117 associações.

| Grupo de escolhas observado | Regra lida | Aplicação a conferir no Teknisa |
| --- | --- | --- |
| Arroz, Batata ou Macaxeira, Molhos e Farofa dos executivos | Cada grupo exige uma escolha; opções incluídas por R$ 0,00. | Associar os quatro grupos aos sete executivos e conferir a impressão. |
| Molhos incluídos em outros pratos | Há um conjunto de sete opções com IDs próprios, além do conjunto de oito dos executivos; escolha obrigatória, mínimo e máximo `1`. | Preservar as associações por produto e distinguir os conjuntos. |
| MOLHO EXTRA | Mínimo `0`, máximo `10`; oito opções de R$ 3,00 cada. | Cobrar o extra conforme a quantidade escolhida, separado do molho incluído no prato. |
| Adicione porção de batata ou macaxeira | Mínimo `0`, máximo `1`; BATATA R$ 9,90 e MACAXEIRA R$ 9,99. | Preservar os valores lidos e conferir os vínculos com os adicionais do Teknisa. |
| Sabor Pastel | Uma escolha entre queijo, carne e camarão, sem acréscimo. | Configurar a escolha do sabor conforme o cadastro atual. |
| Escolha a Massa | Uma escolha, com dois itens ativos. | Conferir a associação e o nome da massa ao migrar o produto correspondente. |
| Polpa e destilados dos coquetéis | Os grupos usados exigem uma escolha; os acréscimos variam com o destilado. | Conferir o total do pedido após cada combinação. |
| Doses Rum Praia, definição `1599364` | Mínimo `1`, máximo `111`; Bacardi ou Montila, sem acréscimo. | O usuário definiu `1..1`; conferir essa regra no novo sistema. |
| Dose Martini Praia, definição `1599365` | Mínimo `1`, máximo `111`; Bianco ou Rosato, sem acréscimo. | O usuário definiu `1..1`; conferir essa regra no novo sistema. |

Os máximos `111` de Rum e Martini e `222` de Cachaças Premium foram
conferidos novamente no DOM e na tela, com rótulo e valor do campo
registrados. São limites dessas definições específicas. A definição de
Cachaças Premium, `1599367`, foi excluída da seleção de migração pela
decisão do usuário. Nenhum desses limites foi alterado no Saipos.

Os editores foram fechados com Cancelar. Nenhum pedido foi criado para
testar a aplicação dessas regras. A migração deve validar a seleção no
caixa, o preço final e a impressão da cozinha.

## Comparação inicial dos preços do Saipos com o Teknisa

Esta comparação usa os 114 preços anteriores à migração. Os números
65/9/29 registram o diagnóstico inicial dos 103 itens selecionados. O
plano atual já relaciona os 103 itens aos cadastros e aos preços relidos,
conforme o registro de execução.

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

O London ativo no Saipos custa R$ 45,00. A execução escolheu o cadastro
London `9.00.00.050.00` e confirmou esse preço na tabela local 001. O
Original de R$ 45,00 permaneceu preservado. O Sir Fisher Fish & Chips está no
Teknisa e no site, mas não apareceu nos 107 itens ativos lidos do Saipos.
No Saipos, London tem a escolha obrigatória de uma massa: **Massa da Casa
(Panko)** ou **Massa Cerveja (Original)**, sem acréscimo. Essa estrutura
representa as duas massas em um produto. As quatro retiradas explícitas
do usuário não incluem o Sir Fisher; a migração deve preservar a escolha
de panko.

Macaxeira e Batata Frita são itens separados no Saipos, ambos por
R$ 27,00. A execução criou os códigos `8.00.15.081.00` e
`8.00.15.082.00` para essas porções e confirmou R$ 27,00 em cada uma.
Os componentes antigos foram preservados. O plano usa Patinha de
Caranguejo `8.00.00.101.00`, a R$ 55,00, mantendo o outro cadastro
existente fora desse vínculo.

Dois IDs ativos de Café Expresso no Saipos, um em SOBREMESA e outro em
Outros, custam R$ 5,00. O plano preserva os dois acessos e usa o SKU
`8.00.20.020.00` em ambos. A leitura final dos layouts precisa conferir
essas duas posições.

### Preços dos coquetéis: base do Saipos e leitura inicial do Teknisa

Os cálculos abaixo somam o preço base e o acréscimo do opcional lidos no
Saipos. A conferência foi feita nos cadastros; o preço final aplicado em
um pedido ainda precisa ser validado no Teknisa. A terceira coluna
preserva o levantamento inicial; a última registra os preços já salvos e
relidos após recarga.

| Produto e escolha | Base + acréscimo do Saipos | Leitura inicial do Teknisa | Preço conferido após a execução |
| --- | ---: | ---: | --- |
| Caipirinha com cachaça nacional | R$ 18,00 + R$ 0,00 = R$ 18,00 | Produto-base CAIPIRINHA em R$ 0,01. | Base corrigida para R$ 18,00. |
| Caipirinha com Ypioca 150 | R$ 18,00 + R$ 4,00 = R$ 22,00 | CAIPIRINHA YPIOCA 150 em R$ 18,00. | Variante corrigida para R$ 22,00. |
| Caipiroska com vodka nacional | R$ 20,00 + R$ 0,00 = R$ 20,00 | Nacional em R$ 20,00. | R$ 20,00 preservado; base genérica também corrigida para R$ 20,00. |
| Caipiroska com Sky | R$ 20,00 + R$ 2,00 = R$ 22,00 | Sky em R$ 28,00. | Variante corrigida para R$ 22,00. |
| Caipiroska com Absolut | R$ 20,00 + R$ 8,00 = R$ 28,00 | Absolut em R$ 22,00. | Variante corrigida para R$ 28,00. |
| Caipifruta com nacional, Sky ou Absolut | R$ 22,00 + R$ 0,00/R$ 2,00/R$ 8,00 = R$ 22,00/R$ 24,00/R$ 30,00. | Variantes em R$ 22,00/R$ 24,00/R$ 30,00. | Variantes preservadas; base genérica corrigida para R$ 22,00. |
| Gin Tônica com gin nacional | R$ 21,00 + R$ 0,00 = R$ 21,00 | Nacional em R$ 23,00. | Variante corrigida para R$ 21,00. |
| Gin Tônica com Gordon’s | R$ 21,00 + R$ 2,00 = R$ 23,00 | Gordon’s em R$ 21,00. | Variante corrigida para R$ 23,00. |

A tabela inicial também tem CAIPIRINHA VODKA SKY, código
`8.05.10.020.00`, por R$ 22,00. Esse cadastro foi preservado e ficou fora
dos fluxos do plano atual. O subgrupo Caipirinha usa cachaça nacional por
R$ 18,00 e Ypioca 150 por R$ 22,00. Seus preços foram relidos; a montagem
dos botões e a conferência no aparelho continuam em andamento.

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
máximos `111` no pedido. O usuário definiu `1..1` para cada dose, conforme
o registro das decisões abaixo.

O resumo de canais da lista mostra Salão e Cardápio digital. Na leitura
adicional dos editores, os dois cafés também estavam marcados para Totem
Saipos, com Delivery e Pedido Online desmarcados. Ambos cobram serviço e
imprimem em Cozinha 1, um diretamente e outro pela configuração da
categoria. Esses campos não comprovam a finalidade histórica de cada ID;
a seleção preserva os dois. A definição dos canais do Teknisa deve
considerar o uso real da operação e os vínculos lidos em cada terminal.

O usuário respondeu às três decisões antes da execução no Teknisa:

| Ponto observado no Saipos | Regra aprovada para o Teknisa |
| --- | --- |
| Rum e Martini permitem até 111 escolhas de marca; Molhos avulso tem base zero e usa grupo opcional `0..10`, permitindo nenhuma escolha pelos campos do cadastro. | Usar `1..1` para Rum/Martini e `1..10` somente na venda avulsa de Molhos. Manter os extras dos pratos em `0..10`. |
| Gelo, ID `19440724`, tem o vínculo `19440727` com MOLHO EXTRA `1576146`. | Retirar somente esse vínculo do Gelo; preservar Salada, Adicional Ovo e os outros produtos que usam o grupo. |
| Drink Cortesia, ID `19413680`, tem base R$ 0,01 e usa Caipirinha Praia `1599653`, com nacional a R$ 0,00 e Ypioca a R$ 4,00 de acréscimo. | Retirar Ypioca da cortesia. Manter apenas cachaça nacional, com preço base de R$ 0,01 e acréscimo zero. Preservar a Caipirinha normal com Ypioca por R$ 22,00. |

As associações foram comprovadas na leitura dos cadastros, e as decisões
comerciais foram registradas. O comportamento no pedido ainda precisa
ser validado no Teknisa. Para exigir molho no produto avulso, o sistema deve
usar uma regra por produto ou um grupo separado: o grupo de extras também
atende a pratos nos quais a compra de molho é opcional. Da mesma forma,
uma regra própria da cortesia deve preservar o acréscimo de R$ 4,00 da
Ypioca na Caipirinha normal.

Os achados originais estão no arquivo local
`output/teknisa-2026-10-26/auditoria-saipos-adicional.json`. A base
`saipos-base-migracao.json` foi preservada. A cópia
`teknisa-migracao-aprovada.json` aplica as respostas do usuário com grupos
separados para Molhos avulsos e Cachaça da cortesia, mantendo as regras
compartilhadas dos demais produtos.

A base aprovada contém **103 itens, 53 com opções, 117 associações e 21
conjuntos, com 87 ocorrências de opções e 78 IDs de opção de origem
distintos**. A contagem de ocorrências inclui as opções reaproveitadas
nos dois grupos separados. O Gelo deixou de ter associação de molho;
a Caipirinha normal manteve as duas opções e seus acréscimos.

## Execução da migração

Os cadastros comerciais foram concluídos e conferidos. Os arquivos locais
`teknisa-mapeamento-produtos.json` e `teknisa-log-execucao.json` relacionam
os 103 itens aprovados aos códigos e às gravações do Teknisa. Os recibos
separam nós da árvore, SKUs, preços e vínculos. Um campo preenchido no
planejamento continua pendente até aparecer em uma leitura do cadastro.

| Lote confirmado | Leitura e evidência | Conferência restante |
| --- | --- | --- |
| Crispy `8.00.00.040.00`, Marine `8.00.10.010.00` e Smirnoff Ice `8.05.10.190.00` inativos na árvore 8. | Fichas salvas e relidas sem o marcador ativo. Os três códigos também deixaram a consulta da tabela 001 e os layouts CAIXA/POS. Recibos de produto e dos layouts finais. | A retirada não alterou o estado global dos cadastros da árvore 9. |
| Sete executivos comuns na categoria `8.00.22 — MENU EXECUTIVO`, folhas e SKUs `.000.00` a `.006.00`. | UN/Estoque/fator 1,000; preços R$ 52/46/31/41/38/47/34 relidos por código na tabela 001. Complemento e descrição lidos nos sete cadastros. Recibos `teknisa-executivos-cadastro.json` e `teknisa-prime-descricoes.json`. | Canais e funcionamento do pedido. |
| Sete Prime na categoria `8.00.23 — PRIME`, folhas e SKUs `.000.00` a `.006.00`. | Nomes e IDs próprios do Saipos preservados. Os mesmos sete preços foram confirmados após recarregar a tabela 001. Complemento e descrição copiados dos executivos correspondentes e relidos; nomes e KDS mantêm o sufixo Prime. Recibos `teknisa-prime-cadastro.json`, `teknisa-novos-precos.json` e `teknisa-prime-descricoes.json`. | Funcionamento do pedido. |
| Layouts CAIXA `00001` e POS `00002`, unidade 0002/loja 0001. | Cada configuração tem 12 grupos, 95 botões diretos e oito subgrupos com 29 escolhas: 124 botões e 123 SKUs para os 103 fluxos da fonte. As grades recarregadas conferem com o plano. Recibos `teknisa-layout-caixa-consolidado-final.json` e `teknisa-layout-completo-pos.json`. | Conferir a exibição e a escolha nos aparelhos. O preview anterior não mostrou registros. DLV permaneceu Não nos 124 botões. |
| 52 observações gratuitas, dez adicionais pagos e nove grupos obrigatórios. | Os 446 pares gratuitos em 42 SKUs e os 52 pares pagos em oito SKUs foram salvos e auditados após recarga, sem faltantes ou duplicados. Recibos `teknisa-opcionais-execucao.json`, `teknisa-gratuitos-auditoria-446.json` e `teknisa-pagos-execucao.json`. | Comprovar mínimo/máximo por grupo, cobrança e impressão no pedido. |
| 494 vínculos de observação usados em 48 SKUs dos fluxos finais. | Os 498 pares salvos incluem quatro vínculos de protótipos nos pais genéricos de Rum/Martini, que ficaram fora do layout. A Cortesia recebeu apenas Cachaça Nacional. | Mínimos gerais e `QTMAXOBSERV` foram preservados. Os limites comerciais ainda exigem teste funcional. |
| Duas cópias dos layouts: `00004 — COPIA LAYOUT CAIXA 26-10` e `00005 — COPIA LAYOUT POS 26-10`. | Doze grupos iguais à origem e 16 vínculos conferidos por cópia, cobrindo ADICIONAIS, EXECUTIVOS e PRIME. Ambas sem caixas associados. Recibo `teknisa-backups-layout.json`. | A restauração não foi executada. A conferência dos 16 vínculos tem essa cobertura; os demais botões não foram comparados individualmente nas cópias. |

Os preços abaixo foram corrigidos na tabela `001`, unidade `0002`, e
confirmados após recarregar a consulta:

| Código | Produto ou escolha | Antes | Depois |
| --- | --- | ---: | ---: |
| `8.05.10.010.00` | Caipirinha Ypioca 150 | R$ 18,00 | R$ 22,00 |
| `8.05.10.050.00` | Caipiroska Absolut | R$ 22,00 | R$ 28,00 |
| `8.05.10.060.00` | Caipiroska Sky | R$ 28,00 | R$ 22,00 |
| `8.05.10.110.00` | Gin Tônica Gordon’s | R$ 21,00 | R$ 23,00 |
| `8.05.10.120.00` | Gin Tônica Nacional | R$ 23,00 | R$ 21,00 |
| `8.05.10.000.00` | Caipirinha, preço base | R$ 0,01 | R$ 18,00 |
| `8.05.10.030.00` | Caipiroska, preço base | R$ 0,01 | R$ 20,00 |
| `8.05.10.070.00` | Caipifruta, preço base | R$ 0,01 | R$ 22,00 |

Além dos sete preços dos executivos comuns, **41 inclusões de preço**
foram confirmadas após recarga. Esse lote reúne os sete Prime, produtos
de Outros/Promoções, Brownie de funcionário, bebidas novas, as porções
separadas de Macaxeira/Batata a R$ 27 e os oito molhos pagos
a R$ 3. Inclui preços locais para Salmon `9.00.00.090.00` a R$ 52,
London `9.00.00.050.00` a R$ 45, Pepsi Black `9.05.05.060.00` e Soda
Limonada `9.05.05.070.00` a R$ 8. Nome e estado ativo global desses
cadastros compartilhados ficaram fora da edição de preço.

A consulta desse lote contém **159 códigos**: os 114 iniciais, com três
retirados, mais sete executivos comuns e 41 inclusões. Os oito preços
existentes autorizados foram corrigidos; os outros 103 preços originais
continuam iguais. Essa contagem de preços preservados é distinta da
seleção de 103 produtos de origem. A conferência usa
`teknisa-precos-readback-novos.json` e
`teknisa-precos-persistidos-validacao.json`. Os 41 preços dessa frente
estão confirmados; os vínculos de venda também foram relidos nos dois
layouts. O pedido nos aparelhos ainda precisa ser conferido.

A consulta integral do cadastro ativo encontrou **185 SKUs**, sendo 156
da árvore 8 e 29 da árvore 9. A conferência independente confirmou os
45 SKUs novos por código, nome e unidade de medida, encontrou os 123
códigos usados pelo plano do menu e confirmou a ausência dos três itens
retirados na árvore 8. Os recibos são
`teknisa-catalogo-geral-ativo-final.json` e
`teknisa-catalogo-final-validacao.json`.

Os 14 executivos, comuns e Prime, têm o complemento “Executivo individual:
150 g de proteína”. As descrições Prime reproduzem os campos lidos nos
executivos correspondentes. O empanado conserva a descrição sem salada,
conforme a origem lida. A imagem `teknisa-prime-descricao-suino-relida.jpg`
registra um dos sete resultados conferidos.

### Preço zero e opções cobradas

O SKU `8.00.24.004.00 — Molhos` foi criado, mas a tabela 001 recusou o
preço base R$ 0,00 com a mensagem “O preço deve ser maior que 0”. O
formulário foi cancelado sem incluir um preço substituto. A imagem
`teknisa-molhos-preco-zero-recusado.jpg` registra a validação.

A execução usa um plano de subgrupos de tela que conduzem aos produtos
com preço final: oito molhos de R$ 3, refrigerantes de R$ 8 e variantes
completas dos coquetéis. A leitura do formulário mostrou Nome, Página,
Posição e uma aba Produtos, que só fica disponível depois de salvar o
subgrupo. Os oito subgrupos e suas escolhas foram salvos e relidos no
CAIXA e no POS. O fluxo no aparelho ainda precisa ser testado. A montagem
preserva as contas base + acréscimo do Saipos;
um SKU com preço integral não pode ser usado como acréscimo sobre outro
preço integral. Os SKUs de opção/variante servem ao fluxo e não ampliam
a contagem dos 103 produtos principais da fonte.

Os componentes antigos de R$ 0,01, como Macaxeira e molhos gratuitos,
foram preservados. As opções pagas recebem códigos próprios. A
Macaxeira adicional de R$ 9,99, as duas Sukitas de R$ 8 e as quatro
variantes de Rum/Martini também tiveram seus preços relidos após recarga.
Os oito molhos, a Macaxeira, as Sukitas e as variantes somam 15 SKUs de
suporte. Eles preservam os preços integrais ou acréscimos da fonte; o
funcionamento no pedido continua em conferência.

O plano completo cobre os **103 itens da fonte** em 12 grupos: 95 acessos
diretos e oito subgrupos, com 124 botões de produto e 123 SKUs distintos
por configuração. Os subgrupos são Refrigerante, Rum, Martini,
Caipirinha, Caipiroska, Caipifruta, Gin e Molhos. Os 124 preços esperados
coincidem com os preços relidos na tabela 001. Cada escolha usa o preço
final do seu SKU, sem somar novamente o preço base da fonte.

Patinha usa `8.00.00.101.00`, a R$ 55. Os dois IDs de Café Expresso
preservam seus acessos em SOBREMESA e Outros e usam o mesmo SKU
`8.00.20.020.00`, a R$ 5. A relação está em
`teknisa-plano-layout-completo.json` e
`teknisa-mapeamento-produtos.json`; as conferências de cobertura e preço
ficaram em `teknisa-plano-layout-cobertura-validacao.json` e
`teknisa-plano-layout-precos-validacao.json`. Esses arquivos conferem o
plano e os cadastros. A leitura dos layouts CAIXA e POS também confirmou
esses totais, os nomes, códigos, posições e DLV Não, sem divergências
comerciais.

A ação nativa “Exportar Configuração (Sobrepor apenas produtos)” copiou
o CAIXA `00001` para o único destino selecionado, POS `00002`, na unidade
`0002`, loja `0001`. A interface confirmou a exportação. Após recarga
integral, os 12 cabeçalhos e os 124 botões foram relidos no POS. Código,
nome, vigência, equipamentos e recebimentos das duas configurações
permaneceram iguais. CAIXA conserva o equipamento `001 — CAIXA 001`;
POS conserva `002 — POS 001`, `003 — POS 002` e `004 — POS 003`.
As cópias `00004` e `00005` ficaram fora dos destinos selecionados.

A comparação registrou uma diferença de campo padrão nos 95 botões
diretos: `NRLIMPRODCOM` aparece como `0` no CAIXA e vazio no POS.
Esse campo trata de produtos dentro de promoção combinada. Sua
equivalência funcional ainda não foi testada; ele não representa o
mínimo/máximo dos opcionais. Os demais campos das 124 linhas conferem.
Os resultados estão em `teknisa-copy-only-products-validacao.json` e
na imagem `teknisa-pos-cardapio-final.jpg`.

### Limites das escolhas e conferência do pedido

Observação por produto apresentou erro com Nível Inicial 8, 1 e 4.
Com o filtro vazio, a consulta passou a listar os produtos associados.
O campo `NRQTDMINOBS` permite mínimo geral por produto no contexto de
`01 — PRODUTOS`; os valores lidos permaneceram em 0.
O campo `QTMAXOBSERV` foi visto vazio no PF Picanha, com o rótulo
“Qtde Obs. Pedido igual ao Gestão de Vendas”. Seu efeito e sua relação
com os grupos não foram demonstrados; nenhum valor foi alterado.

O executor cadastrou os nove grupos obrigatórios e suas ocorrências.
A interface lida ainda não comprovou o vínculo explícito desses grupos
a cada SKU nem a reprodução dos mínimos/máximos do Saipos. Os 494 pares
usados no menu confirmam os vínculos individuais. O plano
completo conserva 117 relações entre produtos e conjuntos, que usam
outra contagem. Pedido, impressão, regras de horário e limites de escolha
continuam pendentes de teste funcional.

O [manual oficial de integração Teknisa–iFood](https://ead.teknisa.com/wp-content/uploads/2025/11/Manual-Integracao-Teknisa-iFood.pdf)
descreve acréscimos cobrados e observações gratuitas vinculadas a produtos.
Essa referência orienta a investigação da cobrança; o comportamento
precisa ser conferido no POS da unidade.

### Carga dos aparelhos e impressão

O usuário informou que o PC, o POS e a impressora já estão instalados e
que pretende operar em 27/10/2026. A conferência final inclui o menu
recebido por esses aparelhos, a tabela de preço ligada ao caixa e o
roteamento dos produtos e observações para a cozinha.

O exemplo do [manual oficial de integração Neemo](https://universidade.teknisa.com/wp-content/uploads/2025/12/RETAIL_INTEGRACAO_NEEMO_TEKNISA_INTNEETEKV03.pdf)
orienta selecionar a tabela ativa e mostra a tabela 001 com Status
Pendente e Situação Ativa. O rótulo Pendente, isoladamente, não permite
concluir que os preços estejam bloqueados. O
[guia oficial de implantação](https://www.teknisa.com/odhen-guia-express-middle)
inclui a função Exportar Tabela de Preço entre os cadastros de venda.
Na interface, Exportar Tabela de Preço mostrou uma cópia entre unidades
e tabelas. O formulário foi cancelado. A leitura ainda não identificou
um comando administrativo de carga para os aparelhos da Praia.

Em **Cadastro Loja → Parametrização → Gestão de Vendas**, o campo Tabela
Preço estava vazio. A tabela `001` foi selecionada, salva e confirmada
após recarga integral e reabertura da loja `0001`. A tabela conserva seus
159 preços. O recibo é `teknisa-loja-tabela-validacao.json`.

O roteamento usado pela loja fica em **Produtos por Loja**. A leitura
inicial encontrou 132 vínculos com ELGIN i9, porta USB, e nenhum vínculo
em Produtos por Nível. Foram acrescentados 49 vínculos à impressora
existente `00001 — ELGIN`. A consulta recarregada percorreu os 181
registros até o fim e confirmou os 125 SKUs necessários, que incluem os
123 códigos do menu e dois adicionais de hambúrguer. Os 132 vínculos
anteriores foram preservados campo a campo. A conferência está em
`teknisa-impressao-execucao.json`, `teknisa-impressao-readback-final.json`
e `teknisa-impressao-validacao-final.json`.

Esses vínculos confirmam o cadastro da rota. O teste de impressão física
e a conferência das observações no papel ainda dependem dos aparelhos.
Nenhuma venda real foi criada para testar a migração.

### Ajustes e conferência fiscal

A tela Impostos do Produto mostrou campos fiscais vazios nos novos
executivos. A árvore do produto não completou esses campos nessa leitura.
O usuário autorizou conferir cada lacuna na ordem: cadastro existente do
Teknisa, Saipos e produto similar. Depois solicitou pesquisa na internet
para corrigir NCM incompatível com a natureza dos produtos. Cada recibo
registra a fonte usada e os campos autorizados.

Os **48 cadastros de imposto por unidade** foram preenchidos e relidos
após recarga: 34 usam o perfil de origem Comida e 14 o de Bebidas. A
conferência percorreu 185 produtos, comparou os oito campos previstos
nos 48 alvos e confirmou os outros 137 sem alterações nessa frente.
Os resultados estão em `teknisa-fiscal-unidade-48-consolidado.json` e
`teknisa-fiscal-unidade-final-185.json`. Essa gravação trata do imposto
por unidade; o NCM e o Tipo do item ficam também no cadastro global.

No cadastro global, **29 produtos de comida** receberam NCM `21069090`,
Tipo `04 — Produto acabado`, Origem `0 — Nacional` e Gênero `21`.
São os 14 executivos/Prime e outros 15 produtos de comida. Os recibos
e suas auditorias são `teknisa-ncm-pf-prime-execucao14.json`,
`teknisa-ncm-pf-prime-auditoria14.json`,
`teknisa-ncm-extras-execucao15.json` e
`teknisa-ncm-extras-auditoria15.json`. Uma leitura independente dos oito
molhos e da macaxeira adicional, após recarga, confirmou os nove NCMs
em `teknisa-ncm-molhos-macaxeira-readback9.json`.

O usuário confirmou que a embalagem é de papelão liso e dobrável.
O cadastro recebeu NCM `48192000`, Tipo `02 — Embalagem`, Origem `0`
e Gênero `48`, com recarga e releitura no recibo
`teknisa-ncm-embalagem-execucao1.json`. Essa estrutura corresponde à
descrição do código na [TIPI oficial disponibilizada pela RFB em 2026](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/legislacao/documentos-e-arquivos/tipi.xlsx/view).
O Gelo recebeu `22019000`, correspondente a gelo comum de água. A edição
individual em Impostos do Produto permitiu salvar e reler o NCM, inclusive
no cadastro global, preservando Tipo, Origem e Gênero vazios. O recibo é
`teknisa-ncm-gelo-taxunit-prototipo.json`.

A Rolha foi identificada pelo usuário como a taxa pela bebida trazida
pelo cliente. O cadastro global recebeu Tipo `09 — Serviços` e Gênero
`00 — SERVICO`, com NCM intencionalmente vazio. A interface aceitou a
gravação e os valores persistiram ao sair e voltar ao cadastro. Os
outros campos foram preservados. O recibo é
`teknisa-rolha-fiscal-tipo-servico-execucao.json`. O [Guia EFD 3.2.2 da RFB, atualizado em 11/02/2026](https://sped.rfb.gov.br/estatico/74/D84DAAF7A4229EE5EFB705CCD7E7BA4D323CBE/Guia%20Pr%C3%A1tico%20EFD%20-%20Vers%C3%A3o%203.2.2.pdf)
trata o Tipo `09` como Serviços e dispensa seu COD_NCM no registro 0200.
Essa regra de escrituração e a gravação no cadastro ainda precisam ser
conferidas no XML emitido pelo sistema, no contexto fiscal da loja.

O [MOC oficial da NF-e/NFC-e, página 90](https://www.confaz.fazenda.gov.br/legislacao/arquivo-manuais/moc7-anexo-i-leiaute-e-rv.pdf)
distingue as condições de `00` e `00000000`. O seletor NCM do Teknisa
não ofereceu os oito zeros na consulta. Esse código não foi atribuído
à Rolha. A pesquisa e os limites da interpretação estão em
`teknisa-fiscal-pesquisa-embalagem-gelo-rolha.json`.

A pesquisa das bebidas usa as posições da TIPI para cerveja/chope,
refrigerante, rum, vermute e outras bebidas espirituosas. Os trechos
literais e suas hierarquias estão em
`rfb-tipi-bebidas-hierarquia-2026.json`. Os **12 NCMs de bebidas novas**
foram salvos e relidos pela edição individual em Impostos do Produto,
conforme `teknisa-ncm-bebidas-execucao12.json` e sua auditoria. Tipo,
Origem e Gênero foram preservados nessa rota. O cadastro de apoio de
Tipo não ofereceu `00 — Mercadoria para Revenda` nas buscas por nome
e código. Uma tentativa no cadastro global exibiu Tipo obrigatório e
foi cancelada. A importação foi apenas examinada, sem envio de arquivo.

Também foram corrigidos os NCMs de **sete destilados existentes**:
três vodkas para `22086000`, dois gins para `22085000` e duas cachaças
para `22084000`. Campari e Aperol receberam `22089000`. São nove
correções pontuais em produtos existentes, com preservação dos demais
campos de imposto. Os recibos são
`teknisa-ncm-destilados-legados-execucao7.json` e
`teknisa-cest-destilados-aperitivos-execucao9.json`.

O [fabricante de Campari](https://www.campari.com/pt-br/nossos-produtos/campari/)
e o [fabricante de Aperol](https://www.aperol.com/pt-br/) identificam os
produtos originais como aperitivos. O
[DOU de 01/11/2010, página 45](https://www.gov.br/mme/pt-br/arquivos/do-01-11-2010-s1.pdf)
também os identifica nominalmente em `2208.90.00`. Essa publicação foi
usada como apoio histórico da identidade; os códigos foram cotejados
com a TIPI e o Convênio atuais, sem transportar alíquotas do ato antigo.

O [Convênio ICMS 142/18, Anexo III](https://www.confaz.fazenda.gov.br/legislacao/convenios/2018/CV142_18)
sustenta os CESTs aplicados aos 13 destilados/aperitivos existentes:
quatro uísques `02.016.00`, três vodkas `02.018.00`, dois gins
`02.008.00`, duas cachaças `02.004.00` e os dois aperitivos
`02.001.00`. O código anterior `02.025.00` não consta na lista atual
consultada desse anexo. O mapa está em
`teknisa-cest-ncm-legados-plano13.json`, com os recibos de execução
dos quatro uísques e dos outros nove produtos.

O Conhaque genérico conservou a classificação existente por falta de
marca e composição. Para Beats Sense/Tropicall, o usuário autorizou
seguir com produto similar: o CEST `02.023.00` foi escolhido por
analogia à referência de Beats Senses na
[Portaria SRE 9/2025 de São Paulo](https://legislacao.fazenda.sp.gov.br/Paginas/Portaria-SRE-9-de-2025.aspx).
Essa referência histórica foi usada para identificar a categoria; seus
preços e sua vigência não foram transferidos para a operação do Ceará.
A nota ou o rótulo de Tropical ainda pode exigir revisão. Essa decisão
não comprova que as duas variantes tenham a mesma composição.

O conjunto fiscal prevê **26 associações de CEST**. Foram salvas 23:
as 13 acima, nove bebidas novas e o Chope Brahma existente, corrigido
de `03.021.00` para `03.023.00`. Os três produtos abaixo continuam
com CEST vazio porque o seletor do Teknisa não oferece os dois códigos
oficiais necessários:

| Produto | SKU | CEST necessário |
| --- | --- | --- |
| Stella Puro Gold Longneck | `8.05.00.091.00` | `03.021.01` |
| Sukita Uva | `8.10.05.091.00` | `03.010.02` |
| Sukita Laranja | `8.10.05.092.00` | `03.010.02` |

A implantação ou o suporte Teknisa precisa incluir **Cerveja em garrafa
de vidro descartável** (`03.021.01`) e **Refrigerante em lata**
(`03.010.02`) no cadastro de apoio. Depois, associar os três SKUs e
reler o resultado. Foram examinados o seletor, os menus de Fiscal e
Produto, as 27 Tabelas Gerais e o Cadastramento Automático de NCM por
Produto. Não foi encontrado um fluxo nativo que permitisse incluir
esses CESTs. Nenhum cadastro de apoio foi gravado. O recibo é
`teknisa-cest-apoio-bloqueio3.json`.

A cláusula 20 do Convênio exige informar CEST para as mercadorias dos
anexos mesmo quando a operação não estiver sujeita à substituição
tributária. A regra N23-10 do MOC consultado identifica o modelo 55;
essa leitura não comprova uma rejeição específica da NFC-e modelo 65.
Os três campos pendentes precisam ser resolvidos antes da operação
fiscal desses produtos.

A recarga final percorreu **185 códigos únicos**. A auditoria confirmou
os 48 cadastros de imposto por unidade, os 52 NCMs e os 23 CESTs
executados, sem diferenças nos outros campos. Entre os 125 SKUs
necessários, as mercadorias têm NCM; Rolha conserva a exceção de serviço
descrita acima. Os três CESTs vazios constam como pendência na auditoria
`teknisa-fiscal-menu-final-validacao.json`. A fonte recarregada é
`teknisa-fiscal-final-grade-185.json`. Essa prova cobre os cadastros;
o XML da emissão real ainda precisa ser conferido.

## Conferências para encerrar a migração

1. Conservar a base aprovada de 103 itens e as quatro retiradas. Reconferir
   a fonte somente se houver mudança na operação durante a implementação.
2. Solicitar à implantação Teknisa os dois códigos de apoio CEST e
   completar os três SKUs da tabela acima. Reler os campos e manter
   a origem de cada preenchimento.
3. Conferir no PC/POS os 12 grupos e as escolhas dos oito subgrupos já
   salvos e auditados no cadastro. Verificar o recebimento da carga.
4. Testar as regras de escolha, os adicionais e os totais do pedido.
   Os vínculos de observação já foram conferidos no cadastro.
   Examinar o horário do executivo e
   a promoção de terça antes de configurar qualquer automatismo.
5. Conferir nos aparelhos os preços da tabela 001 já vinculada à loja e
   a rota ELGIN já cadastrada para os 125 SKUs necessários.
6. Conferir a exibição no PC/POS e a impressão da cozinha por recurso de
   teste próprio, quando o ambiente o oferecer. Preservar o caixa de venda
   real durante essa validação.
7. Conservar os recibos finais em `output/teknisa-2026-10-26/` e acrescentar
   o resultado dos testes locais. A pasta mantém a data de início da tarefa.

Em 27/10/2026, os cadastros comerciais, os layouts e os campos fiscais
executados foram conferidos. A operação ainda depende dos três CESTs
pendentes e dos testes de carga, pedido, preços, impressão e XML nos
aparelhos. O registro de fechamento está em
`teknisa-fechamento-2026-10-27.json`, junto dos recibos locais.
