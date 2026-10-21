# Desempenho do painel: linha de base, causas e plano

Medição e diagnóstico de 21/10/2026, a partir do pedido de otimização do
proprietário (cópia local ignorada pelo Git em `tmp/PROMPT_DESEMPENHO_PAINEL.md`).
Como repetir as medições: `docs/OBSERVABILIDADE.md`, seção "Rotina de medição
de desempenho".

## Linha de base (antes de qualquer mudança)

Banco medido como o navegador o usa: papel `authenticated` com claims de um
admin, transação somente leitura e `rollback`. "Dados no banco" reproduz as
rodadas e a concorrência de cada página (`medir_desempenho.py paginas`, três
voltas, uma ida e volta por consulta). Rede medida deste PC: HTML do Pages
0,35–0,45 s; ida e volta ao Supabase 0,09 s (conexão aberta) a 0,25 s (nova).

| Página / fluxo | Consultas | Rodadas | Dados no banco (mediana, faixa) | Dados completos no PC (estimado) | Gargalo principal |
|---|---|---|---|---|---|
| Início | 11 | 3 | 4,0 s (3,7–4,5) | 4,5–4,9 s | resumo mensal 0,9 s; projeções 0,7–1,0 s; saldo atual 1,0 s |
| Caixa | 10 | 2 | 4,6 s (4,2–4,6) | 5,0–5,4 s | saldo atual 1,0 s; recebimento projetado e despesas projetadas ~1 s cada, em paralelo |
| Gerente | 7 | 3 | 4,4 s (4,3–5,5; uma volta 16 s) | 4,9–5,3 s | cascata do gerente 2,3–2,6 s sozinha |
| DRE | 6 | 2 | 2,0 s (1,8–2,4) | 2,5–2,9 s | projeções e resumo |
| Despesas | 9 | 2 | 2,3 s (2,1–5,0) | 2,8–3,2 s | projeções, resumo e ranking |
| Calendário | 2 | 2 | 5,3 s (4,8–6,5) | 5,8–6,2 s | `listar_calendario_financeiro` 3,3–8,8 s (acima do teto de 8 s em alguns momentos) |
| Conciliação | 4 | 2 | 1,7 s (1,7–2,0) | 2,2–2,6 s | resumo mensal Stone e detalhe |
| Importar (1 arquivo) | RPC + fila | — | RPC 2,7 s em média (pico 7,5 s) | ~1 min até os números | worker refaz recálculo, 6 MVs e 3 validadores (~50–65 s) |
| Importar (4 arquivos) | 4 RPC + 4 tarefas | — | — | ~4 min (06/10: 6,5 min) | uma tarefa por arquivo, em fila |
| Publicação | — | — | deploy 25 s–1,5 min | + até 10 min | cache `max-age=600` do Pages no navegador |

Aba nova ou mais de 5 min sem navegar somava 3 rodadas de acesso
(configuração, papel, permissões): 0,36–0,44 s. No celular em 4G cada rodada
custa mais 0,1–0,3 s e o JavaScript roda mais devagar: somar 0,8–1,5 s.

## Causas raiz (com evidência)

1. **Recomputação no servidor a cada leitura.** As mesmas bases são
   recalculadas várias vezes por consulta:
   - `corte_caixa` faz `max(data_caixa)` sobre toda a `fato_financeiro`: 0,3 s
     sozinha e 1,4 s dentro do Calendário. Aparece em 12 views e 8 funções.
   - `venda_diaria` custa 0,2–0,28 s por avaliação e é avaliada 3× em
     `projecao_venda_diaria`, 4× em `painel_resumo_mensal` e ~5× no Calendário
     (EXPLAIN: `raw_stone_vendas` varrida 10–33 vezes por consulta).
   - `caixa_real_diario` custa 1,8–2,8 s; `fato_financeiro` inteira, 1,7–2,1 s.
2. **CPU pequena e compartilhada.** Instância Nano: `work_mem` 2 MB, 2 workers
   paralelos, variação de 2–4× na mesma consulta. As esperas amostradas foram
   100% CPU. Três consultas de ~1 s em paralelo levam ~1,9 s cada. O tempo de
   uma página é o total de CPU que ela pede (~4 CPU-s nas principais).
3. **Rodadas em fila.** Início e Gerente esperam 3 rodadas; as outras, 2; aba
   nova somava mais 3 de acesso. Cada rodada acrescenta 0,1–0,25 s de rede.
4. **Importação em fila e cara.** Cada arquivo gera uma tarefa; cada tarefa
   refaz tudo. `saldo_mensal_calculado` reavalia `caixa_real_diario` uma vez
   por mês (55 s; 14,7 s com `MATERIALIZED`). `mv_conciliacao_contabil` leva
   15–19 s e grava 473 MB em disco temporário a cada refresh (por causa do
   `work_mem` de 2 MB), origem da maior parte dos 322 GB temporários desde 30/06.
5. **Nada é reaproveitado entre navegações.** Toda visita refaz todas as
   consultas, embora os dados mudem poucas vezes por dia.
6. **Publicação.** O Pages fixa `max-age=600`: após o deploy, quem abriu a
   página há pouco pode ver a versão anterior por até 10 min.

Não são gargalo: tamanho do banco (109 MB), disco nas consultas das páginas
(nenhum transbordo), bibliotecas (cache de 1 ano) e o HTML.

## Plano priorizado

Ganhos das etapas B a D medidos em protótipo: transação descartada, só objetos
temporários, resultado de cada view e do Calendário com md5 idêntico ao atual.

| Etapa | Mudança | Ganho medido | Esforço | Risco | Atraso de dado | Como reverter |
|---|---|---|---|---|---|---|
| A (feita) | Acesso em paralelo e cache entre abas; `preconnect`; corte do Calendário em paralelo; `?perf=1` | aba nova −0,25 a −0,5 s; Calendário −0,4 a −0,9 s | baixo | baixo | nenhum | `git revert` |
| B1 | Índices em `raw_stone_vendas(data_venda)`, `raw_stone_recebiveis(data_vencimento)` e `(data_venda)`, `raw_stone_extrato(data_hora)` | `max()` e recortes por data passam a ~0 ms | baixo | baixo | nenhum | `drop index` |
| B2 | `MATERIALIZED` nas CTEs de `saldo_mensal_calculado` | worker: 55 s → 14,7 s | baixo | baixo | nenhum | definição anterior |
| B3 | Worker processa todas as tarefas pendentes numa execução (recálculo a partir da menor data, que dá o mesmo resultado final) e usa `work_mem` de 32 MB só no refresh | 4 arquivos: ~4 min → ~1 min; −473 MB de disco por refresh | médio | médio | reduz | função anterior |
| C1 | Snapshot de 1 linha com `max(data_caixa)`, atualizado no refresh; "ontem" continua ao vivo (virada do dia sem job) | corte 0,3–1,4 s → 0 | médio | baixo | corte avança quando o refresh da carga termina | view anterior + `drop` |
| C2 | Snapshot diário da Stone (dia, stonecode, produto) no refresh; espécie, Fundopay e Pix BB continuam ao vivo | `venda_diaria` 0,2 s → 0,013 s | médio | baixo | venda Stone aparece quando o refresh da carga termina | view anterior + `drop` |
| B+C juntos | — | Calendário 6,7 → 0,8 s; resumo 0,93 → 0,14 s; despesa direta 0,99 → 0,06 s; recebimento projetado 1,0 → 0,06 s; saldo atual 0,97 → 0,07 s; cascata do gerente 2,4 → 0,85 s; `saldo_mensal_calculado` 57 → 2,7 s | — | — | — | — |
| D (opcional) | Snapshot de `fato_financeiro` para as views do painel e as MVs | despesa fixa 0,41 → 0,09 s; bonificação 0,33 → 0,07 s; cascata do gerente 0,85 → 0,29 s; Calendário 0,79 → 0,52 s; refresh mais barato | médio | médio | classificação manual chega às projeções quando o worker termina (~1 min), como já ocorre na DRE | views anteriores + `drop` |
| E | Front: rodadas em paralelo depois de B/C; Gerente renderiza por partes; cache local validado por uma "versão dos dados" antes de exibir; apagado no logout | revisita sem dado novo: ~0,3 s e nenhuma consulta pesada | médio | médio | nenhum (valida antes de mostrar) | `git revert` |
| F | Versão nos assets no deploy e aviso de versão nova | consistência após deploy | baixo | baixo | nenhum | `git revert` |

Estimativa com A+B+C no PC (servidor somado por rodada + 0,09–0,25 s de rede
por rodada + HTML 0–0,45 s + JavaScript ~0,1 s): Início 1,1–2,0 s, Caixa
0,9–1,7 s, Calendário 1,0–1,5 s, Gerente 1,3–2,2 s (0,8–1,6 s com D). Nenhuma
consulta do navegador acima de 1 s no servidor. Com E, revisita sem dado novo
em ~0,3–0,5 s. No celular em 4G, somar 0,5–1,0 s.

## Decisões (21/10/2026)

O proprietário delegou a escolha ("faça o que achar melhor"). Critério: maior
ganho sem mudar números, sem atraso além do aceito e sem risco de mostrar
número desatualizado.

1. **B e C aplicadas** (migrations `20261021050000` a `20261021080000`), com a
   memória do refresh em 16 MB (suficiente para zerar o disco temporário,
   medido) em vez dos 32 MB previstos.
2. **B extra aplicada**: `projecao_despesa_fixa` limita o realizado aos meses a
   partir do corte (`20261021090000`), 0,37 s → 0,22 s.
3. **E, parte segura, aplicada**: Início e Gerente pedem as consultas
   secundárias junto com o resumo (3 rodadas → 1 na carga de dados). O cache
   de números no navegador **não** foi feito: com o banco rápido, o ganho não
   compensa o risco de exibir número antigo.
4. **D não aplicada**: atrasaria a classificação manual nas projeções, e o
   pedido exige que ações manuais apareçam na hora.
5. Nenhum job novo de `pg_cron` foi necessário.

## Resultado (21/10/2026, depois de A–C e da parte segura de E)

Mesma rotina da linha de base. Páginas: mediana de 5 voltas; antes, de 3.

| Página | Dados no banco antes | Depois | Rodadas antes → depois | Dados completos no PC (estimado) |
|---|---|---|---|---|
| Início | 4,0 s | 0,68 s | 3 → 2 | 0,8–1,4 s |
| Caixa | 4,6 s | 0,59 s | 2 → 2 | 0,7–1,2 s |
| Gerente | 4,4 s | 0,91 s | 3 → 1 | 1,0–1,5 s |
| DRE | 2,0 s | 0,51 s | 2 → 2 | 0,6–1,1 s |
| Despesas | 2,3 s | 0,52 s | 2 → 2 | 0,6–1,1 s |
| Calendário | 5,3 s | 1,36 s | 2 → 1 | 1,5–2,0 s |
| Conciliação (não alterada) | 1,7 s | 1,29 s | 2 → 2 | 1,4–1,9 s |

Consultas no servidor (melhor tempo, antes → depois): Calendário 4,1 s →
0,70 s; cartão do gerente 2,3 s → 0,51 s; resumo mensal 0,93 s → 0,19 s;
projeção de despesa direta 0,99 s → 0,06 s; recebimento projetado 1,0 s →
0,06 s; saldo atual 0,98 s → 0,07 s; saldo por conta 0,30 s → 0,001 s;
recebimento conhecido 0,31 s → 0,001 s; resumo do gerente 0,91 s → 0,08 s.
Restam acima de 0,3 s: projeção de despesa fixa (~0,22–0,37 s), bonificação
(~0,33 s), conciliação Stone (~0,33–0,36 s).

Importação: um refresh completo leva 28,5 s (antes ~50–65 s por tarefa), sem
disco temporário. Duas tarefas enfileiradas juntas foram processadas numa
execução só (início em 6 s, 28,7 s). Com 4 arquivos: ~35 s até os números,
contra ~4 min antes.

**Riscos que continuam.** A CPU do plano Free é compartilhada: a mesma página
ainda pode ter picos de 2–8× (Calendário: um pico de 8,2 s em 5 voltas). A
primeira chamada numa conexão nova também planeja mais devagar (~0,3 s a mais
no Calendário), e o PostgREST fecha conexões ociosas. O que confirma a
experiência real é medir com `?perf=1` no PC e no celular.

## Medição real nos navegadores (21/10/2026, à noite)

Três aberturas do Caixa com `?perf=1` (uma com Ctrl+Shift+R) deram 2,3–4,6 s,
acima do previsto. Os logs da API do Supabase (`medir_desempenho.py logs`)
mostraram, requisição por requisição:

- **O banco já não era o gargalo:** no PostgREST, as consultas do Caixa
  levaram 10–430 ms.
- **`app_configuracao_empresa` respondia 403 em toda página.** Os grants por
  coluna do desenho original tinham sumido do portal. Sem essa resposta, o
  `app-config.js` nunca guardava a configuração, e toda página pagava uma
  rodada a mais antes de liberar o acesso. Corrigido em `20261021100000`; o
  cabeçalho volta a mostrar o nome configurado ("Sir Fisher").
- **Rede e gateway do Supabase:** fora do PostgREST, mediana de 62 ms, mas
  7% das requisições passam de 300 ms (p99 1,6 s; máximo 4,2 s, sem nova
  tentativa do gateway). A primeira requisição de cada abertura é a mais
  afetada: 24% acima de 300 ms, e metade quando o painel ficou de 30 s a
  5 min parado (conexão fria). A medição 2 (4,6 s) foi isso: requisições de
  8–81 ms no banco levaram 1,6–2,6 s no total.
- A verificação CORS (`OPTIONS`) vale 1 h por endereço; só pesa na primeira
  visita da hora e no Ctrl+Shift+R.

O que mudou em seguida:

1. `app-config.js` guarda os parâmetros mesmo se só o nome falhar, sem
   guardar o nome genérico. Com o cache válido, a página não espera nenhuma
   consulta: usa o que tem e busca em segundo plano os valores para a
   próxima página. Essa consulta também abre cedo a conexão fria. A página
   atual nunca muda de valor no meio do caminho, e uma recarga forçada dos
   parâmetros não é sobrescrita (testes em `test_desempenho_front.mjs`).
2. Conciliação Stone com snapshots (`20261021110000`): resumo mensal 364 ms →
   0,8 ms e detalhe 324 ms → 45 ms, com conteúdo idêntico.

## Achados fora do escopo

- Em 13/10, três tarefas da fila terminaram com erro nos validadores
  (`mv_fluxo_caixa_diario` e `mv_despesa_mensal` divergiram); as seguintes
  concluíram. Vale investigar à parte.
- `mv_conciliacao_contabil` é recalculada em todo refresh (15–19 s de CPU)
  embora só a página de conciliação contábil a use. É hoje metade do refresh.
- O job horário `sirfisher-virada-financeira` (criado em `20260818110000`) não
  existe mais no `cron.job` do portal; o saldo e o fluxo materializados só
  avançam na virada do dia quando há carga. Restaurar exige decisão.
- `private.processar_fila_recalculo_saldo()` tem EXECUTE para PUBLIC e
  `authenticated` (schema `private`, fora da API). Vale revogar à parte.
