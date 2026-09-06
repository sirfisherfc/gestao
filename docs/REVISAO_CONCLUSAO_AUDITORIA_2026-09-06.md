# Revisão da conclusão da auditoria — 06/09/2026

Parecer: as entregas existem e houve avanço relevante, mas a afirmação de que
nada está pendente não é sustentada. Há falhas reproduzidas no front-end,
limitações nos testes, divergência no histórico de migrations e partes do
escopo original que continuam sendo evolução pendente.

## Escopo e preservação

Revisão do projeto `SirFisher/gestao`, branch `main`, commit `5eda7be`.
A pasta inicialmente aberta era o portal de reservas. O HEAD remoto coincide
com o local. O índice `.git/index` local tem zero bytes; `git status` falha com
`index file smaller than expected`. Não foi possível certificar o estado do
staging. Não houve pull, reconstrução do índice, commit, push ou alteração de
aplicação/migrations. Apenas este parecer e o recado no canal foram escritos.

Consultas ao banco portal usaram conexão com `default_transaction_read_only=on`,
transações somente leitura e timeout de 8 segundos. Nenhuma importação,
recálculo, alteração de flags ou execução de migration foi realizada.
Não foram incluídos segredos, dados financeiros reais ou arquivos brutos.

## Evidências positivas

- CI do HEAD: [Quality gates aprovado](https://github.com/sirfisherfc/sirfisher/actions/runs/34014384107).
- Publicação do HEAD: [GitHub Pages aprovado](https://github.com/sirfisherfc/sirfisher/actions/runs/34014384158).
- 32 testes JavaScript locais aprovados: 21 de apresentação da DRE e 11 de importação web.
- Seis suítes Python locais aprovadas: importação (9 dry-runs e casos adicionais),
  instalação, catálogo de 155 migrations, acesso, contratos financeiros e front-end.
- No banco: corpo da importação contém inserção na fila; watchdog ativo a cada
  dois minutos, com 30 execuções registradas como `succeeded` na última hora.
  Na consulta, nenhuma tarefa pendente.
- No banco: tabela e RPC auxiliares de estoque existem; cascata contém a
  classificação nova e sua constraint existe; calendário contém
  `movimento_real as materialized`; as quatro categorias da migration de bônus
  foram encontradas e estão neutras.
- Os quatro grupos de testes sintéticos de parsers passaram contra as funções
  existentes no banco, chamando apenas as funções de teste SELECT. O inicializador
  que cria objetos não foi executado. Banco atual: PostgreSQL 17.6; CI: PostgreSQL 15.

Essas verificações confirmam presença de objetos e comportamentos pontuais;
não equivalem a comparação integral de definições, teste de claims/RLS,
concorrência real ou medição de desempenho. Os percentuais de ganho e a paridade
dos meses históricos relatados pela IA anterior não foram reproduzidos aqui.

## Pendências encontradas

### 1. Alta: projeção incompleta continua aparecendo como valor calculado

Em `dre.html:188–191`, falhas nas consultas auxiliares viram arrays vazios.
Em `dre.html:240–259`, a soma do array vazio é zero; se o Resumo continua
disponível e a tendência está ativa, o resultado projetado continua numérico.
O aviso de indisponibilidade não impede a apresentação desse resultado.

Reprodução em VM com o JavaScript real e a fixture sintética existente:
o total esperado com os componentes completos é 64; fazendo `DESP_FIXA=[]`,
estado produzido pela falha da consulta, a tela mostra 94. São valores
inteiramente sintéticos. Correção necessária: guardar disponibilidade por
fonte e indisponibilizar os indicadores dependentes, preservando o realizado.

### 2. Média: cancelamento e política de retentativa incompletos

`dre.html:168–180` cria um AbortController e verifica seu estado depois das
promessas, mas não passa o signal para nenhuma das quatro consultas. Isso evita
parte das sobrescritas obsoletas, mas não cancela as requisições em andamento.
É necessário encadear `.abortSignal(signal)` nas consultas, conforme a
[API oficial](https://supabase.com/docs/reference/javascript/using-modifiers-abortsignal).

`assets/supabase-client.js:22` lê status dentro de `error`, ignorando o status
no objeto de resposta. Reproduzido com respostas sintéticas no formato
`{data:null,error:{code,message},status}`: HTTP 400, 401 e 403 fizeram três
tentativas cada. Falta ainda orçamento total/timeout; `Promise.allSettled`
continua esperando todas as consultas para mostrar o realizado. O tratamento
de falha da consulta principal também substitui o conteúdo anterior por erro.

### 3. Alta para rastreabilidade: histórico de migrations divergente

O banco contém os objetos principais recentes, porém
`supabase_migrations.schema_migrations` tem 20 entradas e a maior versão é
`20260905000000`. Não há registro das quatro migrations `20260906000000`,
`20260906010000`, `20260906020000` e `20260906030000`.

Isso não demonstra que o SQL esteja ausente: vários efeitos foram confirmados.
Demonstra que o histórico do executor não acompanha essas entregas. Conferir
definições, grants e a baseline da migração para o banco unificado antes de
reconciliar o histórico. Não reaplicar toda a cadeia ou marcar versões como
aplicadas sem essa conferência.

### 4. Média: paridade de parsers e testes de cascata não cobrem a promessa

Em `scripts/ci/test_paridade_parsers.py`, Stone Extrato e BS Cash comparam
hashes construídos dentro do teste, sem executar o importador Python completo,
nem conferir valores/datas ou quantidade de linhas; `zip` pode omitir linhas
faltantes. Stone Vendas/Recebíveis verificam constantes esperadas no SQL,
sem comparação com os respectivos importadores Python. BB reutiliza seu
parser de valor, mas a montagem do hash é repetida no teste. Motivos de
rejeição e linhas ignoradas não são comparados.

O bootstrap modifica o SQL lido das migrations ao trocar `\v` por `\x0b`.
Portanto, o CI não testa literalmente essas definições do repositório.
Seu fallback para `.env` pode criar objetos se `parse_bb` não existir;
precisa ser limitado explicitamente a banco descartável.

O novo teste de exclusividade da cascata em `test_dre_apresentacao.mjs`
verifica a aritmética da fixture pronta, sem executar a view SQL ou tentar
uma classificação sobreposta. Os testes aprovados são úteis, mas não
comprovam toda a integridade anunciada.

### 5. Pendências operacionais e de escopo

- A fila tem duas tarefas em erro, criadas em 02/09/2026, anteriores às entregas.
  Não foram diagnosticadas individualmente. O watchdog não retenta erros;
  verificar se já foram supridas por recálculo posterior antes de agir.
- O calendário unificou vendas, mas ainda lê `raw_stone_recebiveis` diretamente,
  sem filtro equivalente de conta/fonte nessa CTE. O risco condicional de
  universos diferentes do parecer original não foi integralmente eliminado;
  impacto atual não foi demonstrado.
- A cascata agrega `outras_variaveis`, mas não expõe esse componente como coluna
  na saída. A apresentação explícita desse desconto continua incompleta para
  configurações em que ele seja diferente de zero.
- A tabela de estoque tem chave `(unidade, mes)` e exige mês truncado. Não
  guarda várias contagens semanais. Um modal sozinho não implementa o
  inventário semanal Curva A. A RPC sobrescreve o registro mensal; não cria
  histórico de revisões e reaberturas. A view não expõe os quatro valores de
  entrada e a memória para reedição administrativa.
- O fechamento é auxiliar: a DRE continua baseada em pagamentos de insumos.
  O próprio comentário SQL exige conciliar o consumo antes de usá-lo na DRE.
- O parecer original também previa obrigações vinculadas a pagamentos,
  revisão por componente das projeções, separação de principal/juros,
  CAPEX/depreciação e remuneração/distribuições, cobertura de dados, geração
  dos derivados e calibração de escalas contra operação observada.
  A classificação exclusiva e as quatro flags de bônus não concluem isso.

## Ordem recomendada

1. Preservar e recuperar o índice Git; conferir alterações locais e staging.
2. Corrigir projeções incompletas, status HTTP, cancelamento e limite de espera;
   acrescentar testes dos fluxos reais de carregamento/falha.
3. Conferir objetos implantados e reconciliar histórico de migrations; investigar
   as duas tarefas antigas em erro sem reprocessamento indiscriminado.
4. Completar paridade diferencial, testes SQL da cascata e validação dos
   universos do calendário, cron/concorrência, claims e desempenho.
5. Evoluir estoque e integração reconciliada com a DRE; definir separadamente
   contagens semanais e fechamento mensal. Depois, itemização BTG e revisão
   histórica por materialidade, preservando rastreabilidade e evitando duplicação.

As três sugestões da IA anterior são pertinentes, porém não substituem as
correções acima nem abrangem todo o escopo da auditoria original.
