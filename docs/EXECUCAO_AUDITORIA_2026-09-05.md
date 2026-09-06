# Execução prioritária da auditoria — 05/09/2026

Atualização: a primeira entrega foi commitada localmente em `1395e9f`, após
autorização do usuário. Não houve push nem aplicação da migration ao banco.
O registro abaixo preserva as condições da primeira entrega; a segunda está
descrita ao fim deste documento.

Primeira entrega: atualização durável após a importação web e recuperação de
tarefas pendentes sem executor. Implementada localmente; migration ainda não
aplicada no Supabase, sem commit ou push. Referências de escopo: a auditoria
financeira/técnica desta data e os blocos B e C de suas propostas SQL.

## Alterações

- `supabase/migrations/20260905000000_importacao_recalculo_duravel.sql`:
  grava raw e tarefa na mesma transação, devolve `recalculo_id`, cria índice
  parcial, função privada e job de recuperação. Os dois blocos propostos foram
  reunidos numa transação; inserção sem período aborta; a reexecução exige que
  todos os trechos da outbox estejam presentes exatamente uma vez.
- `importar.html`: acompanha cada arquivo salvo, inclusive quando o próximo
  falha; distingue erro de processamento, consulta indisponível e pendência;
  permite consultar novamente sem reenviar dados. O banco anterior usa fallback
  por arquivo, imediatamente após a gravação. O contrato novo não solicita uma
  segunda tarefa. Zero inserções não é apresentado como prova de painel atual.
- `scripts/ci/test_importacao_web.mjs`: onze testes executam o JavaScript real
  com RPCs e DOM sintéticos, incluindo falha parcial, exceções, clique duplo,
  fallback, estados mistos, prazo e nova consulta.
- `scripts/ci/test_importacao_outbox.py` e
  `scripts/ci/fixtures/importacao_outbox.sql`: montam uma fixture descartável
  usando parser, importador, patch de fontes, fila e worker reais do repositório;
  aplicam a migration nova duas vezes e conferem o catálogo resultante.
- `.github/workflows/quality.yml`: integra os testes de comportamento e cria
  um job com PostgreSQL 15 descartável para a fixture SQL.
- `docs/supabase_schema.md`: documenta os objetos, contratos e manutenção.
- `docs/CANAL_IA.md`: recado acrescentado, preservando alterações anteriores.

Não houve alteração de parser, hash, valores, classificação, regra financeira,
migration anterior ou aviso de segurança aceito. As propostas originais foram
preservadas e continuam como registro da auditoria, não como migration aplicada.

## Validações realizadas

- Quality gates, sintaxe Python/JavaScript, contratos financeiros, de acesso e
  front-end, safeguards de instalação e catálogo das 151 migrations: passaram.
- Importadores: nove dry-runs e testes sintéticos de cabeçalho inválido, saldo
  divergente, configuração de conta e formatos BB antigo/novo: passaram.
- Onze testes da importação web: passaram com Node, sem rede ou dados reais.
- Fixture SQL em PostgreSQL embarcado 18.3 (PGlite, instalado apenas na pasta
  temporária): passou. Verifica atomicidade/rollback se a fila falhar, ausência
  de efeitos no dry-run, deduplicação, período só das linhas novas, grants,
  preservação do gate e da configuração de fontes, idempotência, recuperação
  de job ausente/desativado, drenagem e retenção de erros do worker.
- Navegador local isolado com respostas sintéticas: upload de dois arquivos,
  falha do segundo, falha de consulta e retomada sem reimportar passaram em
  1366, 390 e 360 pixels. Sem overflow da página ou erros de console; tabela
  mantém a rolagem horizontal existente. Imagens conferidas visualmente.
  O Browser integrado estava indisponível; validação feita com Chromium local.
- Nenhuma importação real, consulta de dados financeiros ou escrita no Supabase.

Limites: a fixture cobre os objetos relevantes, não toda a cadeia do projeto.
Cron e cálculo pesado são simulados; não mede desempenho, agendamento real,
RLS com claims reais ou duas sessões concorrentes. A execução em PostgreSQL 15
foi configurada no CI, mas não executada nesta sessão. O teste local em 18.3
não substitui essa verificação nem a validação em ambiente Supabase de teste.

## Revisão e publicação

1. Revisar a migration nova e confirmar owners/definições efetivas em ambiente
   de teste. A migration aborta se as âncoras ou owners esperados divergirem.
2. Validar com pg_cron real: pendência sem job, worker ocupado, chegada de tarefa
   durante desagendamento, falha do worker e consulta com papel autorizado.
   Conferir também a carga provocada por lotes com vários arquivos.
3. Depois da revisão, autorizar commit/push conforme `AGENTS.md`; só então
   publicar pelo fluxo normal de `main`. Preferir banco antes da página; durante
   o rollout, front antigo pode gerar tarefas redundantes, e banco antigo com
   front novo ainda tem a lacuna entre gravação e solicitação.
4. Confirmar o job de recuperação ativo, grants e `recalculo_id` da RPC. A
   ausência de ID numa resposta perdida não desfaz uma tarefa já commitada;
   reimportação duplicada não enfileira outra nem comprova conclusão anterior.

O watchdog verifica a cada dois minutos; esse intervalo somado à fila e ao
processamento pode ultrapassar o acompanhamento de dois minutos da tela.
Pendência continua amarela e pode ser consultada novamente. Erros não são
retentados automaticamente. Tarefas de importações históricas que nunca foram
enfileiradas continuam exigindo reconciliação e solicitação específica.

Sem mudança de regras de classificação ou cálculo, a recuperação pode usar o
lock atual do worker. A tentativa do lock retorna imediatamente; o agendamento
usa os nomes estáveis já adotados no projeto. Referências técnicas:
[PostgreSQL 15, advisory locks](https://www.postgresql.org/docs/15/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS)
e [API do pg_cron](https://github.com/citusdata/pg_cron#managing-and-creating-jobs).

## Próximas prioridades

1. Ajustar rótulos e ausência de dados na DRE/Prime Cost, com base de receita
   explícita, sem apresentar pagamentos como CMV apurado ou competência plena.
2. Conferir a classificação e os subtotais da cascata usando a definição final
   e configuração do banco; não mudar a regra financeira apenas por hipótese.
3. Restaurar a consolidação do calendário sobre a versão atual, validando
   universos, continuidade, resultados e planos no banco antes de publicar.

Estoque/competência e migração econômica mais ampla dependem de dados e regras
operacionais que esta entrega não cria. O bloco A da proposta não foi promovido.

## Estado do repositório

Diretório e branch `main` conferidos. A árvore já estava suja; `git fetch origin
main` confirmou zero commits de diferença. Não foi feito pull sobre alterações
pendentes. Preservados os dois arquivos da auditoria, `docs/security-audit/` e
o conteúdo preexistente de `docs/CANAL_IA.md`. Nenhum arquivo foi staged.

Commit sugerido: `fix: garante recalculo duravel apos importacao web`.
Não incluir arquivos preexistentes não relacionados ao selecionar o commit.

## Segunda entrega — apresentação da DRE e dados indisponíveis

Implementada localmente após o commit `1395e9f`, sem nova migration ou mudança
nas regras de classificação. A árvore ainda continha a auditoria anterior e o
recado correspondente no canal: foram preservados. `git fetch origin main`
confirmou um commit local à frente e nenhum remoto pendente; não houve pull
sobre a árvore suja nem push.

Arquivos desta entrega:

- `dre.html`: identifica a base predominantemente financeira; substitui
  resultado líquido por total gerencial e CMV por insumos pagos/despesa direta;
  esclarece a mistura de bases na projeção. Não declara mês encerrado ou fontes
  completas apenas porque a tendência não está ativa.
- `index.html`: alinha os rótulos do Resumo, qualifica a receita após despesa
  direta/contribuição estimada e deixa indicadores de custo ausentes neutros.
  Sem tendência, receita ou despesa direta ausente não produz diferença numérica.
- `scripts/ci/test_dre_apresentacao.mjs`: 16 testes executam o JavaScript real
  com dados sintéticos e conferem nulos, campos ausentes, vazio, valores
  inválidos, zero válido, denominador não positivo, projeções, tabela e gráficos.
- `.github/workflows/quality.yml`: executa esses testes no CI.
- `docs/EXECUCAO_AUDITORIA_2026-09-05.md` e `docs/CANAL_IA.md`: registro e recado.

Prime Cost é apresentado como aproximação de insumos pagos mais pessoal
registrado, sobre a receita financeira. Só aparece se ambos os componentes e
seus percentuais forem válidos e a receita for positiva. Ausência fica como
“Indisponível”, sem barra ou faixa verde; zero explicitamente informado continua
zero. As faixas configuradas foram mantidas, identificadas como acompanhamento
interno, sem alegação de padrão universal de mercado ou cobertura confirmada de
estoque, encargos e provisões. Zero retornado pelo banco não comprova completude.

Na DRE, projeções propagam componentes ausentes; a tabela mantém esses campos
visíveis com travessão. A cascata não é desenhada com componentes incompletos e
as linhas históricas não atravessam margens indisponíveis. Valores e fórmulas
com todos os componentes válidos permanecem iguais aos anteriores.

Validações: 16 testes novos e os 11 testes da importação passaram; quality gates,
sintaxe, contratos de front-end, financeiros e de acesso passaram. Testes visuais
com Chromium e Chart.js real, Supabase/autenticação simulados, passaram nas duas
páginas em 1366, 390 e 360 pixels: troca de período, estado incompleto/completo,
tooltips e console sem erros. Imagens conferidas; nenhum dado real utilizado.

Limites e próxima prioridade: não há acesso ao banco para validar completude,
classificação ou planos. A interpretação econômica da cascata continua exigindo
revisão dos subtotais e das flags. Na projeção do Resumo, o cálculo preexistente
de `abaixoOperacional` ainda não inclui `outros`, enquanto a DRE inclui; o caso
sintético confirmou a diferença. Tratar essa reconciliação na próxima entrega
de subtotais, sem confundir a correção de rótulos com uma revisão já concluída
das regras financeiras. Esta entrega não altera esse cálculo preexistente.

Commit sugerido para a segunda entrega:
`fix: esclarece base financeira da DRE e preserva dados ausentes`.
