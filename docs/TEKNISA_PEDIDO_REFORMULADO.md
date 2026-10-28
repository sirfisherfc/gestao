# Pedido reformulado: ferramenta de operação do Teknisa

## Problema real

As IAs repetem a navegação, descobrem os mesmos campos e reconstroem a
conexão a cada tarefa. Isso consome tempo e contexto e dificulta conferir
os lotes. O piloto de 181 vínculos comprovou consulta e gravação por API
interna, com releitura; ainda faltavam uma entrada única e um transporte
reutilizável da sessão.

## O que considerar

Cada operação precisa identificar organização, unidade e os outros códigos
do destino. Produto global, produto por loja e botão do caixa são objetos
distintos. Um novo item também precisa dos vínculos de preço, tributação
por unidade, impressão e caixa que forem usados pela operação. Os
cadastros podem ser salvos antes de os aparelhos receberem
a configuração. Uma resposta HTTP bem-sucedida exige releitura dos campos.
A sessão expira; os caminhos internos podem mudar. O projeto funciona nos
dois PCs, com o mesmo código e credenciais restritas à memória da sessão.

## Perguntas que orientam cada pedido

1. Qual resultado operacional a pessoa quer e em qual unidade/loja/tabela?
2. Quais produtos, códigos ou critérios entram no lote? Há exceções?
3. Quais campos devem mudar e quais valores devem ser preservados?
4. A função já foi validada? A tarefa pede consulta, prévia ou gravação?
5. O cadastro salvo precisa de carga ou teste no aparelho para concluir?

Os dados já presentes no pedido, na sessão ou nas consultas devem ser
aproveitados antes de perguntar ao proprietário. Uma dúvida que afete o
destino ou o significado de uma gravação precisa ser resolvida antes dela.

## Critérios de uma boa solução

- Uma entrada para descobrir comandos, consultar, preparar e executar.
- Comandos limitados a funções conhecidas, com destino explícito e retorno
  resumido. A expansão de funções acompanha evidências reais do sistema.
- Prévia com os valores anteriores e propostos; aplicação limitada ao
  plano preparado e verificação de alterações concorrentes.
- Lotes pequenos, releitura, recibo privado antes da primeira gravação e
  interrupção com informação de progresso quando houver falha.
- Repetição sem gravações desnecessárias e retomada após consulta atual.
- Testes de comportamento e uma consulta real com a ferramenta entregue.
- Instruções persistentes para as IAs consultarem esta ferramenta primeiro.

## O que estava faltando no pedido inicial

O piloto usava uma função de transporte montada na conversa. Precisamos
salvar sua implementação sem salvar a autenticação. Também precisamos
distinguir código pronto, leitura validada e gravação validada; registrar
as falhas parciais; limitar os arquivos gerados a uma pasta privada; e
tratar edições simultâneas. O bloqueio de um processo local não garante
exclusividade em dois computadores ou contra uma pessoa usando o painel.

## Premissas a corrigir

Uma visita à interface valida uma versão e um fluxo. Mudanças de esquema
ou regras podem exigir nova inspeção. O ganho observado no lote justifica
o uso de API; um fator exato de economia exige medição comparável.
Autenticar no navegador não confirma que o contrato inclui uma API oficial
independente. Ler um recurso também não comprova que sua escrita funciona.

## Informações que ainda precisam ser obtidas

O proprietário priorizou cadastrar/editar produtos, vendas por garçom e
comissão do mês, e acrescentou a divisão da impressão por preparo. As
rotas foram definidas: bebidas prontas no Balcão, preparadas no Bar e
alimentos na Cozinha. O cadastro de produtos e preços já pode ser lido;
seus contratos de criação/edição ainda precisam de caso real autorizado.
O relatório de produtividade foi localizado e consultado. Sua base de
período é o movimento de caixa, e a consulta observada exclui vendedores
não associados. A regra comercial de comissão, sua base e o tratamento
dos cancelamentos precisam ser confirmados. O acesso oficial independente do navegador e os testes
físicos dos aparelhos continuam dependendo das condições reais da operação.

## Pedido reformulado

Construir no repositório de gestão uma ferramenta modular para as operações
frequentes do Teknisa, aproveitando a API interna observada na sessão
autorizada. Oferecer uma entrada única, um catálogo de funções com seu
estado de validação, consulta e auditoria dos recursos conhecidos e planos
de alteração com aplicação e releitura. Reutilizar o piloto de impressão
de cancelamento e acrescentar as funções que puderem ser mapeadas e
validadas nesta entrega, incluindo a impressão pedida e preparando os
fluxos de produtos e de vendas/comissão. Manter os
segredos em memória, os recibos fora do Git e as alterações de produção
limitadas ao pedido de cada tarefa. Registrar nas instruções que as IAs
devem usar a ferramenta antes de repetir a navegação. Testar, publicar o
código e relatar exatamente as capacidades entregues e os limites reais.
