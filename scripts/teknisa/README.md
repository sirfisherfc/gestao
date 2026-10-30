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

A criação/edição de produtos e a gravação de preços ainda exigem validar
o contrato no primeiro caso real. A consulta por garçom usa o relatório
oficial observado; a comissão exige percentual e base explícitos. O
catálogo de comandos informa os limites e impede uma gravação que ainda
não foi validada.

## Capacidades da versão inicial

| Função | Situação |
| --- | --- |
| Catálogo ativo, tabelas e preços | Leitura real conferida: 185 produtos e 159 preços na tabela da Praia |
| Cancelamento, nomes e rotas de impressora | Gravação e releitura validadas |
| Organizar Balcão/Cozinha/Bar | Usado nesta entrega para conferir 181 vínculos e corrigir 42 |
| Planos, recibos, retomada | Validados em testes e execução real; reversão validada em testes |
| Edição de produto e preço | Prévia disponível; aplicação bloqueada até validar a gravação real |
| Novo produto | Preparação dos dados; criação e vínculos ainda precisam de contrato validado |
| Vendas por garçom | Consulta real por período de movimento do caixa, com valores oficiais separados |
| Comissão | Calcula sobre a base e o percentual informados; regra ausente permanece pendente |
| Opções por produto (observações) | Leitura, inclusão e retirada validadas em 30/10/2026 com releitura |

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

## Opções do cardápio (observações)

Acompanhamentos, molhos e sabores ficam em **Cadastro de Observação**,
grupo `01 — PRODUTOS`. Observação do tipo `O` é gratuita; do tipo `A`
cobra o produto ligado a ela (por exemplo, `55–62` são os molhos extras
de R$ 3). O módulo `observacoes.mjs` lê e altera os vínculos por produto:

```js
await tool.run('observacoes.listar');              // opções e grupos obrigatórios
await tool.run('observacoes.vinculos.listar', { search: 'patinha' });
const preview = await tool.run('observacoes.vinculos.planejar', { changes: [
  { productId: '8000010100', add: ['05', '06'], remove: ['55', '56'] },
] });
await tool.run('plano.aplicar', { planId: preview.planId });
await tool.run('plano.reverter', { planId: preview.planId }); // nova prévia
```

`productId` é o `CDPRODUTO` da grade Observação por produto. A aplicação
confere o estado de cada produto, grava, relê e para na primeira
divergência. O produto precisa já constar em Observação por produto.

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

O próximo contrato necessário é o de criar/editar produtos e atualizar
preços. Para menus laterais que não respondem ao clique por seletor,
usar `getAXState()` e `click(índice)` da API documentada do navegador.
Esse caminho abriu o filtro de Produtividade por Vendedor nesta entrega.
Antes de calcular comissão, confirmar a base comercial e o tratamento
dos cancelamentos; o relatório usa as definições oficiais do sistema.

Execute os testes com:

```text
node --test scripts/teknisa/test_produtos_loja.mjs scripts/teknisa/test_ferramenta.mjs scripts/teknisa/test_observacoes.mjs
```

Esta ferramenta usa a API interna observada do painel. O acesso oficial
independente do navegador depende da documentação e das condições da
Teknisa. A consulta confirma os cadastros; impressão e carga nos aparelhos
continuam exigindo teste operacional.
