# Integração com os produtos por loja do Teknisa

## Entrada padrão para as próximas tarefas

Usar `node scripts/teknisa/teknisa.mjs comandos` e ler
[`scripts/teknisa/README.md`](../scripts/teknisa/README.md). A ferramenta
centraliza a captura da sessão, as consultas e os planos com recibo,
aplicação e releitura. O piloto descrito abaixo permanece como histórico.
O pedido reformulado e os critérios estão em
[TEKNISA_PEDIDO_REFORMULADO.md](TEKNISA_PEDIDO_REFORMULADO.md).

Em 27/10/2026, o proprietário pediu para marcar **Imprime Cancelamento de
Pedido** em todos os produtos vinculados à loja da Praia. O campo fica em
**Cadastro de Loja → Produtos por Loja**, na ficha de cada vínculo.

## Resultado conferido

- Destino: unidade `0002 — SIR FISHER PRAIA`, loja `0001 — LOJA PADRAO 2`.
- A consulta completa retornou 181 vínculos: um já marcado e 180 desmarcados.
- Um vínculo foi salvo pela interface para observar a chamada real. Dois
  foram gravados juntos pela API interna e relidos. Os 177 restantes foram
  processados em oito lotes de até 25, cada um seguido de nova consulta.
- A conferência final encontrou 181 marcados, zero pendentes e nenhuma
  diferença nos demais campos retornados pela consulta, incluindo setor
  e rotas de impressão. A descrição derivada da opção acompanha o novo valor.
- O recibo privado, com o estado anterior e posterior, está em
  `output/teknisa-cancelamento-2026-10-27/cancelamento-execucao-auditoria.json`,
  na raiz do workspace e fora dos repositórios.

A confirmação no cadastro cobre a gravação do parâmetro. Ainda falta testar
a saída do cancelamento na impressora, com um pedido de teste combinado
com a operação. Esta tarefa não criou pedido, venda nem cancelamento real.

## Conector local

`scripts/teknisa/produtos_loja.mjs` oferece uma operação específica para
ativar a impressão do cancelamento dos vínculos existentes. O transporte
autenticado é fornecido pelo chamador. A implementação usa os caminhos
observados na sessão autorizada do próprio painel:

- Consulta: `POST /backend_man/index.php/ger12300_cadloja_produtos`.
- Gravação: o mesmo caminho com `/save`, `requestType: DataSet`.
- Campo: `IDIMPCANITEM`, com `S` para marcado e `N` para desmarcado.
- Chaves: organização, unidade, loja e produto. A consulta usa todos os
  níveis de produtos e rejeita retorno que possa estar truncado.

A chamada retorna apenas JSON ao adaptador e rejeita falhas HTTP. O
transporte deve reutilizar a sessão vigente no navegador, limitar-se aos
dois caminhos acima e manter os cabeçalhos de autenticação em memória.
Não copiar esses cabeçalhos para arquivos, logs, exemplos ou commits.
O adaptador não cria credenciais e depende da sessão atual do painel.

`enableCancellationPrinting` consulta e prepara uma prévia por padrão.
Para executar, o chamador informa `apply: true`, o destino conferido e o
operador observado na sessão. Antes de cada lote, o adaptador consulta
novamente, confere o destino e compara os demais campos. Cada gravação
recebe uma releitura; uma divergência interrompe os lotes seguintes.
Repetir a operação com todos os vínculos já marcados faz apenas a consulta.

Esses caminhos pertencem à API interna usada pelo painel. Mudanças no
Teknisa podem exigir uma nova conferência do formato e da autenticação.
O [catálogo oficial](https://www.teknisa.com/api) continua sendo a referência
para contratar e avaliar uma integração independente do navegador.

## Validação

Execute `node --test scripts/teknisa/test_produtos_loja.mjs`. Os oito testes
usam um servidor simulado em memória e cobrem o destino, os lotes, a
repetição, a preservação de impressoras e a interrupção por divergências.
O workflow `quality.yml` executa esses testes sem acesso ao Teknisa.

Após a gravação, o módulo salvo também foi importado e executado contra a
sessão real: retornou 181 já marcados, zero pendentes e zero novas gravações.
A grade foi recarregada e a ficha do primeiro produto confirmou o campo
marcado. A captura fica na mesma pasta privada, em
`parametro-cancelamento-conferido.png`.

## Impressão por preparo: configuração atual

O proprietário confirmou uma impressora física atendida por três destinos
lógicos e definiu o preparo como regra de separação. Foram reaproveitados
os três cadastros Elgin; o cadastro Stone/POS foi preservado.

| Código | Nome salvo | Destino | Vínculos após a conferência |
| --- | --- | --- | ---: |
| `00001` | COZINHA | Alimentos, pratos e porções | 82 |
| `00003` | BALCAO | Bebidas prontas, cervejas e destilados | 67 |
| `00004` | BAR | Coquetéis, sucos e bebidas preparadas | 32 |
| `00002` | POS | Configuração Stone/POS existente | Preservada |

A leitura do recibo anterior ao ajuste de cancelamentos já mostrava rotas
para os três códigos: 82 para `00001`, 79 para `00003` e 20 para `00004`.
Os nomes Elgin repetidos ocultavam essa diferença. A primeira hipótese
de que todos apontavam para `00001` foi corrigida pela leitura dos códigos.
Para preservar a correspondência predominante, `00001` ficou como Cozinha
e `00003` como Balcão. Os nomes foram relidos; modelo e conexão permaneceram
iguais aos da leitura anterior.

O mapeamento da migração do Saipos identificou 123 SKUs. Os outros 58
vínculos da loja foram conferidos por categoria e nome, incluindo antigos
cadastros e complementos. Foram necessários 42 ajustes de rota, com 139
vínculos já coerentes. Exemplo: Suco Copo e Sumo de Limão foram para Bar;
as Sukitas e os novos destilados acompanharam o Balcão. Café e Soda
Italiana também seguem para Bar. Os produtos mantiveram seus outros campos.

A ferramenta executou os ajustes pelo plano
`97e2a44d-0271-4c54-ace7-b757fd208266`, em dois lotes com releitura.
O recibo fica em `tmp/teknisa/`, ignorado pelo Git. A conferência encontrou
181 vínculos com impressão de cancelamento ativa e zero sem rota.
As fontes e o resumo operacional ficam também na pasta privada da raiz
`output/teknisa-impressoras-2026-10-27/`.

A consulta ao cadastro ativo encontrou 185 produtos com
`IDIMPRODUVEZ = N`, valor apresentado pela interface como Imprime Agrupado.
A separação salva por destino ainda requer teste de pedido e cancelamento
na impressora física. Nenhum pedido ou cancelamento de teste foi criado.

## Capacidades conferidas da ferramenta

Foram consultados os 185 produtos ativos, as vigências, os 159 preços da
tabela 001 e os quatro cadastros de impressora. A consulta de preços usa o
dataset retornado `vnd42400_tabelapreco_produto_normal_com_preco`, diferente
do nome da rota. A paginação do catálogo foi percorrida pela ferramenta.
O transporte foi reconstruído após reiniciar o runtime, com nova captura
autorizada e cabeçalhos restritos à memória.

A criação/edição de produtos e a alteração de preços oferecem preparação
ou prévia. Seus contratos de escrita ainda precisam ser validados em um
caso real solicitado, e a aplicação permanece bloqueada.

A leitura de **Produtividade por Vendedor** foi integrada em
`vendas.garcons.consultar`. O contrato observado é
`POST /backend_man/index.php/vnd09900_relProdutividadePorVendedor`, com
datas em `DTMOVTURCAIX`, unidade e loja no filtro. A consulta de 01/10 a
27/10/2026 retornou 23 linhas e três vendedores. Nenhum valor financeiro,
identificador fiscal ou nome pessoal foi incluído nesta documentação.
As linhas são agregadas por vendedor e os campos fiscais/consumidor
são descartados do retorno da ferramenta.

`vendas.garcons.comissao` usa a mesma fonte e exige uma regra de base e
percentual. Sem regra, a comissão permanece pendente. Os valores de
gorjeta e entrega ficam separados. A configuração consultada exclui
vendedores não associados (N/A), e o período segue o movimento de caixa.
O cálculo com dados já normalizados de outra fonte também está disponível
em `vendas.garcons.resumir`. Os testes usam valores fictícios; a validação
real mostrou apenas cobertura e formato.

## Arquivos da entrega da ferramenta

- `scripts/teknisa/teknisa.mjs`: entrada e catálogo de comandos.
- `scripts/teknisa/recursos.mjs`: contratos, escopo e paginação.
- `scripts/teknisa/sessao_browser.mjs`: transporte da sessão observada.
- `scripts/teknisa/planos.mjs` e `recibos.mjs`: prévia, gravação e histórico.
- `scripts/teknisa/normalizacao.mjs` e `produtos_loja.mjs`: formato de
  gravação compartilhado e compatibilidade com o piloto anterior.
- `scripts/teknisa/impressao.mjs` e `vendas.mjs`: preparo e agregações.
- `scripts/teknisa/test_ferramenta.mjs`: testes adicionais; o teste do
  piloto permanece em `test_produtos_loja.mjs`.
- `scripts/teknisa/README.md`: uso, exemplos e limites.
- `.github/workflows/quality.yml`: execução dos testes sem rede.
- `AGENTS.md`, `docs/CANAL_IA.md`, este guia,
  `docs/TEKNISA_PEDIDO_REFORMULADO.md` e `docs/TEKNISA_MIGRACAO_CARDAPIO.md`:
  instruções e registros.
- `docs/workspace/AGENTS_WORKSPACE.md` e `README_WORKSPACE.md`: espelhos
  dos arquivos `AGENTS.md` e `README.md` da raiz, também atualizados.
