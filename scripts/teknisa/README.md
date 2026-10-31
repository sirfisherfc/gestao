# Ferramenta do Teknisa

Esta é a entrada padrão para as tarefas repetitivas do Teknisa no workspace.
Comece por `node scripts/teknisa/teknisa.mjs comandos`. O terminal mostra
as funções e o que já foi validado; as chamadas autenticadas usam o runtime
documentado do navegador, com a conta já conectada.

O proprietário pede o resultado de negócio em linguagem comum. A IA
consulta os códigos internos e escolhe o comando correspondente.

## O que pode ser pedido

- “Confira quais produtos estão sem impressora na Praia.”
- “Organize a impressão: bebidas prontas no Balcão, preparadas no Bar e
  alimentos na Cozinha. Preserve a impressão dos cancelamentos.”
- “Confira o preço do produto X na tabela usada pela loja.”
- “Prepare o cadastro de X, categoria Y, unidade Z, preço e destino.”
- “Prepare a correção do nome ou da descrição destes produtos.”
- “Mostre vendas por garçom e comissão do mês, informando fonte e regra.”

Os clientes especializados de composição e componentes foram validados
em 31/10/2026. A edição geral de produtos e preços continua com aplicação
bloqueada; os contratos validados têm o escopo descrito abaixo. A consulta
por garçom usa o relatório oficial observado; a comissão exige percentual
e base explícitos. O
catálogo de comandos informa os limites e impede uma gravação que ainda
não foi validada.

## Capacidades conferidas

| Função | Situação |
| --- | --- |
| Catálogo ativo, tabelas e preços | Em 31/10: 200 produtos ativos e 175 preços na tabela da Praia |
| Cancelamento, nomes e rotas de impressora | Gravação e releitura validadas |
| Organizar Balcão/Cozinha/Bar | Em 27/10: 181 vínculos conferidos e 42 corrigidos |
| Planos, recibos, retomada | Validados em testes e execução real; reversão validada em testes |
| Edição de produto e preço | Prévia disponível; aplicação bloqueada até validar a gravação real |
| Novo produto | Preparação geral; cliente especializado cria os componentes com modelos conferidos |
| Vendas por garçom | Consulta real por período de movimento do caixa, com valores oficiais separados |
| Comissão | Calcula sobre a base e o percentual informados; regra ausente permanece pendente |
| Observações por produto | Leitura, inclusão e retirada validadas; escolhas do cardápio migradas para composição |
| Composição: grupos, componentes, limites e tipo | Gravação e releitura validadas em 31/10/2026; 48 produtos e 118 vínculos conferidos |
| Componentes alimentares e sabores de soda | Criação, imposto, preço e loja validados no cliente especializado |

## Conectar uma sessão

Use a habilidade de navegador e leia a documentação que ela devolver. As
chamadas de navegador continuam pela ferramenta autorizada. Evite abrir
portas de depuração, ler arquivos privados de perfil ou extrair senhas.

1. Selecione a aba autenticada do Teknisa e obtenha a capacidade `cdp`.
2. Importe `teknisa.mjs` no runtime JavaScript por seu caminho local,
   derivado do workspace atual. Use `pathToFileURL` para caminhos com espaços.
3. Inicie a captura, faça uma consulta conhecida pela interface e termine
   a captura. Preserve os rascunhos da pessoa. Uma consulta por módulo de
   autenticação permite reutilizar a sessão nas operações desse módulo.
4. Conecte o transporte e informe o destino conferido. O código de operador
   vem de um `CDOPERADOR` observado numa gravação legítima ou de contexto
   previamente conferido. `User-Id` e `NRORG` têm outras funções; seus
   valores não devem ser usados para inferir o operador.

Exemplo no runtime, depois de obter os identificadores pela sessão:

```js
const cursor = await teknisa.beginSessionCapture(cdp);
// Faça uma consulta pela API documentada de controle do navegador.
const observations = await teknisa.finishSessionCapture(cdp, cursor);
const session = teknisa.connectObservedSession({ cdp, observations });
const tool = teknisa.createTeknisa({
  request: session.request,
  target: { organization, branch, store },
  operator: operatorObservedInTheAuthorizedSession,
});
await tool.run('loja.produtos.auditar');
```

O transporte aceita apenas os caminhos cadastrados. Cabeçalhos ficam em
memória e não aparecem nos retornos, nos recibos ou nos arquivos do projeto.
Os projetos MAN e CAD_EST usam capturas próprias; junte as observações na
conexão quando precisar de ambos. `session.describe()` retorna contadores
e tempo de chamadas; `session.close()` limpa os cabeçalhos em memória.
Uma sessão expirada exige reconectar pelo fluxo normal já autorizado.

## Consultar, planejar e aplicar

```js
await tool.run('produtos.listar', { search: 'suco', limit: 10 });
await tool.run('loja.impressoras.listar');
await tool.run('precos.tabelas.listar');
await tool.run('precos.listar', {
  scope: { table, effectiveFrom, productLevel }, search: 'suco', limit: 10,
});
const preview = await tool.run('loja.impressoras.planejar', {
  updates: [{ id: productId, printerCode }],
});
// Confira se a prévia corresponde ao pedido já autorizado.
await tool.run('plano.aplicar', { planId: preview.planId });
await tool.run('recibo.consultar', { planId: preview.planId });
```

Para cancelamento, use `loja.cancelamento.planejar` com `enabled: true` e
`productIds: [...]`, ou com `all: true`. O comando `impressao.organizar`
recebe fontes com `{sku, name, group}` e códigos `{cozinha, balcao, bar}`.
Um destino desconhecido fica pendente para conferência. Nomes repetidos
de impressora não são usados para escolher o código.

A regra aprovada é: Balcão para bebidas prontas, cervejas e destilados;
Bar para coquetéis e sucos preparados; Cozinha para alimentos. Café, soda
italiana e sumo de limão acompanham o preparo no Bar. Produtos novos devem
receber destino conferido. O estado ativo/inativo permanece preservado.

## Escolhas do cardápio

Decisão do proprietário em 31/10/2026: as escolhas do cardápio ficam em
**Composição do Produto → Composição Padrão → Grupo Promocional**.
Cada categoria exige uma escolha, com mínimo `1` e máximo `1`. Preserve
as alternativas de cada prato ao migrar um vínculo.

O adicional dos sanduíches usa mínimo `0` e máximo `1`; o item escolhido
acrescenta seu preço ao pedido. Produtos sem escolha ficam sem grupo
promocional. O caldo segue sem molhos, e o Dadinho segue sem escolha de
acompanhamento.

No **Cadastro de Observação**, preserve os grupos `02 — CANCELAMENTO` e
`03 — DESCONTO`. O catálogo `01 — PRODUTOS` pode manter as definições
históricas, com as escolhas desvinculadas dos produtos. A migração retira
os vínculos; as definições continuam disponíveis para consulta.

Os comandos `observacoes.*` continuam lendo e retirando vínculos, com
prévia, recibo e releitura por produto. Uma nova escolha de cardápio deve
seguir a composição definida acima.

```js
await tool.run('observacoes.vinculos.listar');
const preview = await tool.run('observacoes.vinculos.planejar', {
  group: '01',
  changes: [{ productId, add: [], remove: oldChoiceCodes }],
});
// A composição substituta deve estar salva e conferida antes da retirada.
await tool.run('plano.aplicar', { planId: preview.planId });
await tool.run('recibo.consultar', { planId: preview.planId });
```

Ao migrar, confira primeiro os produtos componentes, seus preços e seus
vínculos com a loja e a impressora. Depois salve os grupos e os limites
do prato, releia as escolhas e retire os vínculos antigos de observação.
Escolhas feitas no produto principal devem evitar uma segunda pergunta
igual nos seus componentes.

O preço de `R$ 0,01` dos componentes internos segue o cadastro dos
marcadores existentes. Esse valor isolado exige conferir o cálculo do
pedido na Promoção Combinada. Teste o total de um prato com escolhas
incluídas e de um sanduíche com adicional, além da impressão na cozinha.

## Operar composição pela entrada única

`teknisa.mjs` exporta `createCompositionClient`, `createComponentClient`,
`createCardapioMigrationRunner` e `connectCompositionSession`. O transporte
especializado recebe as capturas dos módulos MAN e CAD_EST. Cabeçalhos
permanecem em memória. Contratos novos de escrita exigem corpo observado
e releitura; o adaptador restringe os caminhos permitidos.

Passe os clientes validados para `createTeknisa({ request, target,
compositionClient, componentClient })`. O catálogo de
comandos indica `configured` para cada dependência. A instância base usada
como `observationTool` pelo executor pode compartilhar o diário privado.

```js
await tool.run('composicoes.vinculos.listar', { productId });
await tool.run('composicoes.itens.listar', { groupId });
const preview = await tool.run('composicoes.vinculos.planejar', {
  changes: [{ productId, groupId, min: 1, max: 1 }],
});
await tool.run('plano.aplicar', { planId: preview.planId });
```

Também há prévias para criar grupos, incluir seus componentes, mudar o
tipo para Promoção Combinada e retirar um grupo após conferir o substituto.
`componentes.planejar` usa modelos completos e callbacks de leitura para
produto, imposto, preço e loja. O cliente de componentes atende os perfis
alimentares e sabores de soda conferidos na Praia; variantes de coquetel
exigem o perfil fiscal do drink de origem.

O executor avançado `createCardapioMigrationRunner` recebe uma ferramenta
base atualizada, cujo destino precisa coincidir com o plano e o cliente
de composição. `runBatch({ offset, size })` atende até três produtos.
Ele salva tipos e vínculos, confere conjuntos e limites, retira as
observações previstas e relê o resultado. Esse executor tem controle de
concorrência por instância; a operação exige uma execução por unidade,
incluindo o outro PC e o painel. O catálogo da entrada única mantém a
migração em lote indisponível até coordenar o bloqueio da unidade com o
bloqueio interno das observações. Os planos individuais de composição e
componentes usam o bloqueio da unidade em `plano.aplicar`.

Um plano interrompido exige consultar o recibo e preparar nova prévia.

## Contratos observados e ainda sem comando

Capturados em 30/10/2026 numa operação real. Use-os como referência para
o próximo comando; cada um exige releitura depois da gravação.

| Operação | Caminho | Observação |
| --- | --- | --- |
| Operador: ler/gravar | `backend_acl/index.php/operator` e `/operator/save` | `requestType: DataSet`; a linha completa vai com `changed: true`. |
| Enviar senha provisória por e-mail | `backend_acl/index.php/validateOperatorEmail` | Só ocorre quando o e-mail muda; filtros `EMAIL`, `CDOPERADOR`, `LANGUAGE`, `STYLE`. |
| Vendedor: desvincular operador | `backend_man/index.php/vnd06400_cadvendedor/save` | Enviar origem com rótulos, `canSaveAddress`/`hasAddress` falsos e `IDTPENDEVEN`. Sem isso o servidor responde 500 **depois** de gravar. |
| Permissões do caixa por grupo | `getPermissoes` (`requestType: Row`) e `vnd61000_controleAcesso/save` | A gravação inclui um campo posicional derivado das permissões; manter pela interface. |
| Botão do layout CAIXA/POS | `vnd80600_configterminalcaixa_layoutProduto` e `/remove` | Ler com o filtro do grupo (`NRBUTTONAUX`, `IDTPBUTONAUX = 2`) e remover a linha lida. |
| Produto: ativo/inativo | `backend_cadEst/index.php/saveProduct` (`requestType: Row`) | Linha com cerca de 250 campos; `IDPRODATIVPR = N` inativa. |
| Composição (grupos promocionais do produto) | `backend_cadEst/index.php/grupromocprod_grupopromoc`, filtro `CDPRODPROMOCAO`; retirada em `/remove` com `requestType: Row` e a linha lida | Os vínculos montam as escolhas do POS. Foram conferidos 48 produtos em 31/10; retirada usa `Row` com a linha completa lida. Um `/remove` com `DataSet` respondeu 500 sem gravar. |
| Produtos de um grupo promocional | `backend_man/index.php/vnd41000_grupoPromo_prod`, `/save` (`DataSet`, linha nova) e `/remove` (`DataSet`) | Grupos 06 a 11: sabores, acompanhamentos, adicionais e molhos. |
| Nó da árvore de produto | `backend_cadEst/index.php/produto_para_arvore/save` (`Row`, `__is_new`) | Criar o nó nível 4 antes do produto, a partir do nó pai. |
| Imposto por unidade | `backend_cadEst/index.php/ger01900_cadastroproduto_venda_imposto` e `/save` | Perfil Comida: ICMS 00, CFOP 5102, CSOSN 102, PIS/COFINS 99 sem incidência. |
| Preço na tabela | `backend_man/index.php/vnd42400_tabelapreco_produto/save` | Resposta `isPlural.result = 1`; reler a tabela 001. |
| Novo vínculo em Produtos por Loja | `backend_man/index.php/ger12300_cadloja_produtos/save` (`DataSet`, uma linha `__is_new` com `PRODUTOS`, `CDPRODUTO_SM`, `CDARVPROD_SM` e `NMPRODUTO_SM` em listas, `NRSEQIMPRPROD`, `IDIMPCANITEM`, `CDFILIAL`, `CDLOJA`, `NRORG`) | Corpo completo conferido em 31/10: intervalos vazios, `NIVELINICIAL: T`, listas de produtos, unidade/loja, impressora, cancelamento, operador observado e horário atual. Exemplo abaixo. Corpo incompleto pode retornar HTTP 200 sem gravar. |

### Inclusão de componente em Produtos por Loja

Contrato conferido em 31/10/2026 na unidade `0002 — SIR FISHER PRAIA`,
loja `0001`. A seleção por lista também envia os campos de intervalo
vazios e `NIVELINICIAL: 'T'`. Preserve o corpo completo capturado.

Gravação: `POST /backend_man/index.php/ger12300_cadloja_produtos/save`.
O exemplo abaixo representa um produto; os identificadores e o destino
devem vir das leituras do cadastro.

```js
const body = {
  dataset: [{
    __createdLocal: true,
    __is_new: true,
    NMPRODINICIAL: '',
    CDPRODINICIAL: '',
    CDARVPROD: '',
    NMPRODUTO: '',
    NMPRODFINAL: '',
    PRODUTOS: [product.CDPRODUTO],
    CDPRODFINAL: '',
    CDSETOR: '',
    NMSETOR: '',
    NRSEQIMPRPUXA: null,
    NMIMPRPUXA: '',
    NRSEQIMPRPROD: printer.code,
    NMIMPRPROD: printer.name,
    NRSEQIMPRPROD2: '',
    NMIMPRPROD2: '',
    NMIMPRPRODBKP: '',
    NMIMPRPROD2BKP: '',
    NMIMPRPUXABKP: '',
    IDIMPCANITEM: 'S',
    NIVELINICIAL: 'T',
    changed: true,
    CDARVPROD_SM: [product.CDARVPROD],
    NMPRODUTO_SM: [product.NMPRODUTO],
    CDPRODUTO_SM: [product.CDPRODUTO],
    CDFILIAL: '0002',
    CDLOJA: '0001',
    NRORG: 5482,
    CDOPERADOR: observedOperator,
    DTATU: timestampInFortaleza,
    NRSEQIMPPRDBKP: null,
    NRSEQIMPPRD2BKP: null,
    NRSEQIMPPUXABKP: null,
  }],
  requestType: 'DataSet',
  origin: {
    containerName: 'ger12300_cadloja',
    widgetName: 'productByStoreWidget',
    containerLabel: 'Cadastro de Loja',
    widgetLabel: 'Produtos por Loja',
  },
};
```

Use `00001 — COZINHA` para os componentes alimentares e `00004 — BAR`
para os sabores de soda, conforme os destinos conferidos nesta migração.
`CDOPERADOR` vem de uma gravação legítima observada; mantenha esse valor
independente de `NRORG`. Atualize `DTATU` para o horário da execução em
America/Fortaleza.

Depois de enviar, consulte Produtos por Loja e confirme o produto, a
unidade, a loja, a impressora e `IDIMPCANITEM: 'S'`. Uma resposta HTTP
200, sozinha, exige essa releitura antes de prosseguir.

## Recibos e falhas

Os planos e recibos ficam em `gestao/tmp/teknisa/`, ignorado pelo Git.
Incluem o estado anterior dos registros, a prévia e o resultado dos lotes.
As novas execuções também registram o operador informado e as tentativas.
Somente o resumo e uma amostra de até oito alterações voltam à conversa.

A aplicação confere o plano, o destino, os valores anteriores e a presença
das impressoras ativas. Salva o recibo antes de enviar cada lote de até 25,
consulta novamente e confere os campos. Um erro interrompe os lotes seguintes.
Não há repetição automática de uma gravação de resultado desconhecido.

Para retomar uma falha, consulte o recibo e o estado atual. Reaplicar o
mesmo plano dentro de 30 minutos pula os registros que já chegaram ao
valor desejado. Depois disso, prepare outra prévia. `plano.reverter` cria
uma nova prévia a partir de recibo concluído e exige que os registros ainda
coincidam com o resultado anterior. A reversão também precisa corresponder
a um pedido autorizado.

O bloqueio em arquivo impede dois processos locais de escreverem na mesma
unidade ao mesmo tempo. Um bloqueio antigo exige conferir o processo e o
recibo antes de removê-lo. A API observada não oferece comparação de versão
na gravação: evite edições simultâneas nos dois PCs ou pelo painel.

## Vendas e comissão

`vendas.garcons.consultar` recebe `from` e `to` em DD/MM/AAAA, com até
31 dias por consulta. Usa **Produtividade por Vendedor**, pelo período de
movimento do turno de caixa (`DTMOVTURCAIX`). O corte é o informado; um mês
em andamento deve ser apresentado até a data consultada. A configuração
observada exclui vendedores não associados (N/A), condição declarada no
retorno. Os campos fiscais e do consumidor são descartados do resumo.

O retorno agrega por vendedor as colunas oficiais em centavos: total,
líquido, líquido sem acréscimo, gorjeta e entrega, com os outros campos
do relatório identificados pela origem. Essa separação mantém a base
de comissão explícita. `vendas.garcons.comissao` consulta a mesma fonte e
recebe regras por vendedor, ou `sellerId: '*'` para uma regra geral:

```js
await tool.run('vendas.garcons.consultar', { from, to });
// Somente depois de obter a regra comercial do proprietário:
await tool.run('vendas.garcons.comissao', {
  from, to,
  rules: [{ sellerId, base: baseFieldChosenByTheOwner, rateBasisPoints }],
});
```

O campo-base é escolhido entre os valores retornados, como
`reportedNetCents` (VRLIQUIDO) ou `reportedNetWithoutSurchargeCents`
(VRLIQACRES). A soma e o percentual usam centavos; a comissão é arredondada
por vendedor e período. Gorjeta não recebe automaticamente o significado
de comissão. A regra precisa definir a base e o tratamento dos estornos.
O relatório foi consultado de 01/10 a 27/10/2026; a validação exibiu apenas
a cobertura, sem publicar valores ou nomes da equipe.
Durante a execução, manter os resultados financeiros em memória ou em
artefatos privados. Exibir no log de validação somente cobertura e
contagens; evitar imprimir o objeto completo do relatório.

`vendas.garcons.resumir` exige fonte e cobertura completa do mês. Cada
movimento normalizado contém `id`, `sellerId`, `occurredAt` com fuso e
`netProductCents` em centavos, após descontos, cancelamentos e devoluções.
Taxa de serviço e gorjeta ficam separadas dessa base. O normalizador da
fonte precisa comprovar essa definição antes de usar o cálculo.

As regras são explícitas, por vendedor, com `base: netProductCents` e
`rateBasisPoints` (500 equivale a 5%). A apuração usa Fortaleza. Dado ausente
retorna `unavailable`; regra ausente retorna comissão `null`. Taxa zero no
cadastro não comprova a regra comercial combinada com a equipe.

## Ampliar a ferramenta

Para uma função nova, observe consulta, chaves, paginação e gravação pela
interface no primeiro caso real autorizado. Use uma ação reversível com
releitura e preserve os demais campos. Cadastre o recurso, acrescente
testes e só então marque `writeValidated: true`. Os caminhos de escrita
ficam restritos ao catálogo. Criação fictícia em produção não integra o
fluxo de validação desta ferramenta.

A criação especializada de componentes usa os contratos observados de
produto, imposto, preço e loja. Alterações gerais de cadastro e preço
continuam exigindo validação própria. Para menus laterais que não respondem ao clique por seletor,
usar `getAXState()` e `click(índice)` da API documentada do navegador.
Esse caminho abriu o filtro de Produtividade por Vendedor nesta entrega.
Antes de calcular comissão, confirmar a base comercial e o tratamento
dos cancelamentos; o relatório usa as definições oficiais do sistema.

Execute os testes com:

```text
node --test scripts/teknisa/test_*.mjs
```

Esta ferramenta usa a API interna observada do painel. O acesso oficial
independente do navegador depende da documentação e das condições da
Teknisa. A consulta confirma os cadastros; impressão e carga nos aparelhos
continuam exigindo teste operacional.
