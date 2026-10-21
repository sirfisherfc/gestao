# Observabilidade e desempenho

Este documento orienta diagnósticos sem alterar dados financeiros, schema ou
regras de classificação.

## Rotina operacional

1. Consultar o Status do painel para identificar fontes atrasadas, falhas de
   carga e tarefas de atualização pendentes.
2. Consultar os advisors de segurança e desempenho do Supabase por leitura.
3. Para uma consulta lenta, capturar o período, a página/RPC envolvida e um
   `EXPLAIN (ANALYZE, BUFFERS)` em ambiente seguro antes de propor índice ou
   reescrita.
4. Registrar a decisão, a evidência e o impacto esperado antes de criar uma
   migration.

## Rotina de medição de desempenho

Linha de base, causas e plano atuais: `docs/DESEMPENHO_PAINEL.md`.

**No navegador (tempo real de quem usa):** abrir qualquer página com `?perf=1`
(ex.: `https://admin.sirfisher.com.br/caixa.html?perf=1`). A medição vale para a
aba até `?perf=0`. Ao terminar a carga, um quadro no canto inferior esquerdo
mostra HTML, primeira e maior pintura, acesso liberado, dados completos e o
número de consultas e rodadas; o console traz a tabela por consulta e
`window.SirFisherPerf`. Medir com a aba nova (frio) e depois navegando (quente),
no PC e no celular. Desligada, a medição não altera o cliente.

**No banco (somente leitura, como `authenticated` com claims de um admin):**

```text
python scripts/diagnostico/medir_desempenho.py consultas --repeticoes 2
python scripts/diagnostico/medir_desempenho.py paginas --repeticoes 3 --saida antes.json
python scripts/diagnostico/medir_desempenho.py checksums public.painel_resumo_mensal public.projecao_despesa_fixa
python scripts/diagnostico/medir_desempenho.py pgss salvar retrato.json
python scripts/diagnostico/medir_desempenho.py pgss delta retrato.json
```

- `consultas`: tempo no servidor de cada consulta das páginas prioritárias.
- `paginas`: reproduz as rodadas e a concorrência de cada página.
- `checksums`: md5 do resultado ordenado. Rodar antes e depois de mudar uma
  view ou função, na mesma data, para provar resultado idêntico.
- `pgss`: compara o `pg_stat_statements` por delta, sem resetar estatísticas.
- A CPU do plano Free é compartilhada e varia 2–4× entre rodadas (picos de
  até 8× já foram vistos): comparar medianas de pelo menos 3 voltas e evitar
  loops longos no horário de serviço, porque disputam CPU com as reservas. Os
  arquivos de retrato ficam fora do Git.
- Antes de trocar uma view ou função do painel, ensaiar a migration numa
  transação com rollback e comparar o md5 dos objetos afetados e dependentes
  (inclusive o Calendário como admin). As migrations de 21/10/2026 também
  abortam sozinhas se o md5 mudar.

## Regras para índices

- Um alerta de chave estrangeira sem índice é candidato, não autorização para
  criar todos os índices de uma vez.
- Priorizar relações usadas em joins, filtros, exclusões ou rotinas demoradas.
- Um índice marcado sem uso só pode ser removido após período representativo de
  tráfego e revisão das rotinas mensais/administrativas.
- Toda criação ou remoção deve ocorrer em migration nova, idempotente e com
  validação de plano de execução.

## Segurança

As views `public.app_*` com `security_definer` e as tabelas com RLS sem policy
seguem decisões documentadas no `AGENTS.md`; não devem ser alteradas apenas
para silenciar o Security Advisor.

Funções `SECURITY DEFINER` usadas por endpoints autenticados exigem revisão por
amostragem sempre que forem criadas ou alteradas: `search_path` fixo, checagem
de papel/permissão dentro da função, grants mínimos e ausência de SQL dinâmico
inseguro.

## Sinais que exigem investigação

- timeout ou repetição de refresh;
- carga recusada, parcial ou com saldo não conciliado;
- fonte atrasada ou sem carga;
- query/RPC mais lenta que o orçamento de resposta da página;
- crescimento de exceções, classificações pendentes ou decisões de conciliação.

Nenhuma dessas situações autoriza reclassificar, excluir ou modificar dados
financeiros automaticamente.
