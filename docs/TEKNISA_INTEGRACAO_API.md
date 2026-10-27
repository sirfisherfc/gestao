# Integração com os produtos por loja do Teknisa

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
