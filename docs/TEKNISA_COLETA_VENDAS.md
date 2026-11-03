# Coleta de vendas do Teknisa

Estado em 02/11/2026: preparação em código e testes sem rede. O proprietário
confirmou que o caixa usa apenas o Teknisa. A agenda Saipos foi retirada;
o histórico continua disponível manualmente.

## O que foi preparado

`scripts/teknisa/coleta-vendas.mjs` consulta um dia por vez pelo contrato
já observado de **Produtividade por Vendedor**. A entrada única oferece:

| Comando | Resultado |
| --- | --- |
| `vendas.coleta.preparar` | Plano de um a sete dias, com destino, fonte e pendências |
| `vendas.coleta.consultar` | Consulta sequencial e recibo privado por dia |
| `vendas.coleta.recibo` | Cobertura e contagens, sem valores ou nomes |

O período usa `DTMOVTURCAIX` e datas anteriores ao dia atual em Fortaleza.
O filtro observado exclui vendedores não associados (N/A). Cada recibo
declara `unassignedExcluded: true`, `financialImportAllowed: false` e
`automaticExecutionReady: false`. Essa fonte serve para comparar a futura
integração com o painel do Teknisa.

Os relatórios diários conservam os campos monetários oficiais em centavos,
com gorjeta e entrega separados. A rotina descarta campos fiscais e de
consumidor. Valores e nomes ficam em `gestao/tmp/teknisa/`, ignorado pelo
Git. O resumo público contém somente dias, situação e contagens.

O diário existente bloqueia uma segunda execução local na mesma unidade.
Uma falha salva o ponto de interrupção. A retomada usa `collectionId`,
confere destino, período e hashes, preserva os dias já consultados e
recomeça pelo dia que falhou. Repetir um recibo concluído devolve o resumo
guardado. Uma nova coleta cria outro recibo para conferir alterações tardias.
Lista vazia recebe `empty_unverified`: ainda falta comprovar a cobertura do dia.

Não foi criado cron, usuário, credencial persistente ou objeto de banco.
A autenticação atual continua em memória. Uma coleta real pelo novo comando
ainda precisa ser validada: o runtime interrompeu o controle do navegador
porque não conseguiu confirmar o endereço da aba no Windows. Nenhum caminho
alternativo de controle foi usado.

## Preparar o período sem conexão

Na raiz do workspace:

```text
node gestao/scripts/teknisa/teknisa.mjs vendas.coleta.preparar --organizacao 5482 --unidade 0002 --loja 0001 --de 2026-10-30 --ate 2026-11-01
```

O comando acima monta o plano e mostra os limites. Os códigos vêm do destino
já conferido: organização 5482, unidade Praia 0002, loja 0001.
Sem datas, o plano usa ontem em Fortaleza.

Depois de conectar a sessão pela rotina do
[`README da ferramenta`](../scripts/teknisa/README.md#conectar-uma-sessão):

```js
const prepared = await tool.run('vendas.coleta.preparar', {
  from: '2026-10-30', to: '2026-11-01',
});
const summary = await tool.run('vendas.coleta.consultar', {
  from: prepared.from, to: prepared.to,
});
// O resumo pode ser exibido; os relatórios ficam no diário privado.
// Se a sessão falhar, reconecte e retome o mesmo recibo:
const resumed = await tool.run('vendas.coleta.consultar', {
  collectionId: summary.collectionId,
});
```

Conferir uma amostra no relatório do painel antes de declarar o novo coletor
validado. A consulta anterior de produtividade por período foi validada
em 27/10; isso ainda exige conferir a nova execução por dia.

## Acesso oficial para executar sem navegador

A [Teknisa publica o catálogo Sale API](https://www.teknisa.com/api), com
`POST /getSales` para vendas detalhadas e recebimentos, `POST /getDayCloses`
para fechamentos e `POST /getClosingSummary` para o resumo de fechamento.
`POST /getSaleProducts` consulta os produtos vendidos.

O fornecedor informa que as APIs dependem de condições comerciais e orienta
obter a documentação técnica com o gerente de contas. A habilitação no
ambiente Sir Fisher ainda precisa ser confirmada. O catálogo público
consultado não fornece URL base, autenticação, renovação, esquema ou paginação.
Essas definições precisam chegar antes de implementar o transporte de serviço.

A busca nos e-mails conectados não encontrou o manual ou a confirmação de
habilitação da Sale API. O contrato Praia de 19/05/2025 localizado e lido
trata de TEF Nuvem/SiTef; a documentação de acesso à API segue pendente.

Texto preparado para solicitar ao fornecedor, ainda sem envio:

> Queremos consultar diariamente as vendas do Sir Fisher Praia para integrar
> com nosso painel de gestão. Poderiam confirmar se a Sale API está incluída
> no contrato e habilitada no nosso ambiente? Precisamos da documentação
> técnica de /getSales, /getDayCloses e /getClosingSummary, com URL do ambiente,
> autenticação de serviço, renovação, limites e paginação. Precisamos também
> das definições de data do movimento, identificadores estáveis de venda e
> pagamento, atualizações, cancelamentos e devoluções, cobertura de vendas
> sem vendedor e exemplos sem dados pessoais. O acesso será para consulta.
> Se houver custo adicional, pedimos informar as condições antes de habilitar.
> A credencial deve ser entregue pelo canal privado apropriado.

## Conferências antes de agendar e importar

1. Validar acesso de serviço ao ambiente e à unidade corretos, incluindo a
   renovação em outra execução, com segredos no armazenamento privado do executor.
2. Mapear o contrato recebido para vendas, pagamentos e alterações tardias;
   comparar totais por dia com o fechamento do Teknisa. Confirmar o corte do
   movimento e a cobertura de vendas sem vendedor. Ausência de resposta ou
   erro de paginação deve permanecer como dado indisponível.
3. Conferir identificadores e cancelamentos em reprocessamento. Gravar em
   fonte própria, com uma migration revisada, para preservar o histórico
   Saipos e conciliar a Stone sem duplicar receita já registrada.
4. Ensaiar sem gravação e depois conferir uma importação autorizada. Definir
   com base no fechamento real o horário e a janela de recuperação da agenda.

A preparação atual mantém `automaticExecutionReady: false`. As definições
da Sale API e a conferência real da cobertura são as dependências para a
próxima etapa.

## Validação

```text
node --test scripts/teknisa/test_coleta-vendas.mjs
node --test scripts/teknisa/test_*.mjs
python scripts/ci/check_project.py --require-node
```

Os testes usam dados fictícios e cobrem corte em Fortaleza, datas inválidas,
limite de período, retomada, isolamento por loja, página repetida, recibo
alterado e bloqueio de concorrência. A entrada `plano.aplicar` recusa o
recibo de coleta. Falhas de autenticação mantêm o erro sem guardar o texto
da exceção, que poderia conter dados de conexão.
