# SEÇÃO 1: SUMÁRIO EXECUTIVO & DIAGNÓSTICO DO ESTADO ATUAL

O Sir Fisher já tem uma base útil de controle financeiro operacional, com separação entre realizado e projetado, regras de acesso no servidor e processamento assíncrono. Entretanto, a DRE atual não sustenta as interpretações de competência, CMV apurado e lucro líquido contábil que seus rótulos sugerem. A prioridade é alinhar o significado das medidas e assegurar que cada importação provoque atualização durável dos derivados.

Auditoria em 05/09/2026 sobre o checkout `main`, commit `a252141`, com 150 migrations locais, até `20260819020000`. O checkout tinha alterações preexistentes em `docs/CANAL_IA.md` e `docs/security-audit/`; foram preservadas. Não foi feito pull, pois a árvore estava suja. Nenhuma ferramenta Supabase/Postgres estava disponível nesta sessão: definições implantadas, planos, latências, flags atuais de classificação e completude dos dados não foram conferidos no banco. As conclusões distinguem evidência no código de impacto que ainda exige medição. Não foram utilizados dados financeiros reais nos exemplos nem consultados arquivos brutos.

Os três maiores acertos:

1. **Arquitetura estática compatível com a operação:** HTML/CSS/JavaScript e cliente Supabase, publicação por lista explícita em `_site/`, sem necessidade de servidor de aplicação ou build adicional. Há componentes comuns, sanitização de DOM e gates de acesso no servidor.
2. **Separação entre escrita e cálculo pesado:** fila, `pg_cron`, snapshots e materialized views são escolhas adequadas ao orçamento curto da Data API. O padrão intencional `security_barrier=true, security_invoker=false` deve ser preservado, com grants restritos e autorização no `WHERE`.
3. **Consolidação de regras e memória de cálculo:** `saldo_fim_mes_efetivo` unifica o fechamento para painéis; o caixa passou a respeitar o corte e a continuidade entre meses; houve correção de cancelamentos e do formato novo do BB nos dois importadores. Existem testes sintéticos e contratos estáticos.

As três maiores fragilidades:

1. **Precisão numérica com significado financeiro impreciso:** pagamentos tratados como consumo, CAPEX/principal/retiradas incorporados ao resultado e projeção comercial combinada com receita financeira. Uma soma que fecha não assegura subtotais economicamente corretos.
2. **Atualização dependente da sobrevivência do navegador:** a importação e o enfileiramento acontecem em RPCs separadas. Há também uma corrida independente entre enfileirar e desagendar o worker.
3. **Regras duplicadas e regressões na cadeia:** a RPC de calendário foi recriada sem o desenho de leitura consolidada/materialização anterior e conserva leituras brutas de vendas. Testes que procuram fragmentos em migrations antigas não garantem a definição efetiva após a última migration.

Correções de contexto do pedido:

- O snapshot vigente é `private.mv_saldo_conta_diario`, agregado por `private.saldo_caixa_diario`. A antiga `public.mv_saldo_caixa_diario_detalhado` foi substituída em `20260818120000` e removida em `20260818200000`.
- A continuidade entre meses já recebeu correção em `20260814000000`; pagamentos posteriores ao corte foram tratados em `20260818180000`.
- `monthTrend` já existe em `assets/dashboard-utils.js`; retries já existem no Caixa e Calendário, embora com políticas diferentes e espera linear.
- Timeout de comando não é sinônimo de HTTP 504. `57014` identifica cancelamento de consulta; PostgREST documenta classe `57*` como 500 e `PGRST003`/504 como espera pelo pool. O teto de 8s informado pelo projeto é o orçamento de projeto desta auditoria, não uma configuração verificada ao vivo. [PostgREST: erros](https://docs.postgrest.org/en/stable/references/errors.html), [Supabase: timeouts](https://supabase.com/docs/guides/database/postgres/timeouts).

# SEÇÃO 2: DOSSIÊ CONCEITUAL COMPARATIVO (FINANÇAS DE FOOD SERVICE)

USAR é uma referência setorial para restaurantes; Abrasel publica orientação gerencial; os CPCs fundamentam os conceitos contábeis brasileiros. Não formam uma única norma obrigatória de apresentação. A estrutura abaixo é uma proposta gerencial reconciliável, inspirada nessas referências. O material público dos coeditores do USAR 8 contempla competência, estoques e apropriações; o livro integral não foi auditado. [USAR: material dos coeditores](https://www.restaurantowner.com/public/Restaurant-Accounting-for-QuickBooks_Slides.pdf).

| Conceito Atual no App | Definição Empírica Vigente | Conceito Técnico Formal (USAR / Abrasel e referências contábeis) | Distorção Gerada no Restaurante | Ação Pragmática Recomendada |
| --- | --- | --- | --- | --- |
| DRE Competência | `data_competencia` recebe a data bancária; o rodapé afirma competência. | Reconhecer venda quando realizada, serviço quando prestado/consumido e estoque como custo quando consumido/vendido; emissão da NF, sozinha, não determina consumo. | Prazos e antecipações deslocam o resultado entre meses. | Identificar o painel atual como gerencial de base predominantemente financeira; manter data do fato, vencimento e pagamento separados. |
| CMV / Despesa Direta | Grupo `DESPESA DIRETA DE VENDA` vira `cmv`. | Estoque inicial + compras recebidas líquidas + transferências líquidas − estoque final; reconciliar perdas e usos fora da venda. | Compra antecipada pode parecer ineficiência; consumo de estoque antigo pode parecer margem extraordinária. | Contagem semanal Curva A e fechamento mensal; identificar cobertura parcial até completar o estoque. |
| Margem de Contribuição | `receita + variaveis`, segundo flag por grupo. | Receita líquida menos custos e despesas variáveis; na apresentação proposta, separar lucro bruto após CMV e então MDR, comissões, delivery e embalagens variáveis. | Taxas embutidas ou classificadas de modo heterogêneo tornam canais e meses incomparáveis. | Mapear componentes por natureza econômica, registrar bruto/taxa/líquido e explicitar a base de receita. |
| CAPEX | `capex` integra a passagem ao chamado resultado líquido. | Investimento no ativo e no fluxo de investimento; depreciação/amortização apropriadas no resultado. Manutenção comum não é automaticamente CAPEX. | Desembolso por equipamento reduz um resultado que o usuário pode interpretar como lucro. | Criar cadastro simples de bens; apresentar CAPEX em ponte separada de caixa, sem tratá-lo como despesa abaixo do EBITDA. |
| Principal da dívida | Pode integrar `NÃO OPERACIONAL` e reduzir o total. | Principal reduz passivo e gera fluxo de financiamento; juros são despesa financeira da DRE. | Serviço da dívida fica confundido com desempenho econômico. | Registrar principal, juros e encargos separados em cada parcela. |
| Resultado operacional / EBITDA | Receita + variáveis + pessoal + infraestrutura + marketing. | LAJIDA conciliado ao resultado líquido, acrescido de tributos sobre o lucro, resultado financeiro líquido e D&A. | Despesas omitidas, regime financeiro e classificações sobrepostas impedem chamar a medida de EBITDA formal. | Manter o nome atual qualificado até reconciliar; apresentar EBITDA, EBIT, resultado financeiro e lucro líquido em sequência. |
| Prime Cost | `cmv_perc + pessoal_perc`, com nulos convertidos a zero. | Custo de insumos + custo completo de pessoal, divididos por uma receita definida e compatível com a referência. | Ausência de dados pode aparecer verde; encargos/provisões e diferença de base de receita distorcem o termômetro. | Exibir cobertura, usar custo completo e separar remuneração operacional dos sócios de distribuição de lucro. |

Abrasel distingue compras de consumo e contextualiza as referências por operação. Sua cartilha usa 65% sobre **receita bruta** para CMV + mão de obra; isso não fundamenta uma faixa normativa obrigatória de 55–65% sobre receita líquida. Se o restaurante escolher receita líquida para análise interna, a comparação precisa usar o mesmo denominador. [Cartilha CMV Abrasel, seções 2, 3 e 6](https://vhub1.abrasel.com.br/site/assets/files/87141/cartilha_cmv_-_custo_de_mercadoria_vendida.pdf). O material de Prime Cost de coeditor do USAR inclui gerência, tributos sobre folha e benefícios. [RestaurantOwner: Prime Cost](https://www.restaurantowner.com/prime_cost_handout.pdf).

Pró-labore não deve desaparecer do EBITDA simplesmente por ser pago a sócio. Se remunera trabalho operacional ou administrativo, é custo da operação; sua inclusão no subconjunto Prime Cost deve seguir a política usada para comparação. Distribuição de lucros é outra natureza. [Sebrae: pró-labore](https://meuatendimento.sebrae.com.br/sites/PortalSebrae/ufs/ap/artigos/como-definir-o-valor-da-retirada-de-pro-labore-dos-socios%2C6570ace85e4ef510VgnVCM1000004c00210aRCRD).

**Transição de competência sem sobrecarregar a operação.** Começar com os fornecedores de insumos e serviços materialmente relevantes, mais folha, encargos e tributos. No recebimento, registrar fornecedor, documento, data do fato/entrega, valor e vencimento; a quitação bancária baixa a obrigação. Uma compra de alimento entra em estoque; sua NF não vira CMV no recebimento. Para serviços de período, apropriar o mês atendido. Manter o extrato como prova do caixa e uma relação entre obrigação e pagamentos, incluindo pagamentos parciais. Cada obrigação deve substituir, no resultado econômico, o reconhecimento baseado em seu pagamento: somar ambos duplica despesa. Fechar por mês, com revisão e estorno de ajustes documentados. [CPC 16: estoques e reconhecimento do custo](https://www.cpc.org.br/Arquivos/Documentos/243_CPC_16_R1_rev%2013_ComAVISO.pdf).

**Inventário pragmático.** Selecionar itens pelo valor consumido/comprado e risco de perda; padronizar kg, litros e unidades; contar sempre no mesmo ponto de corte, inclusive produtos preparados e embalagens abertas relevantes. Fazer conferência semanal dos itens A e mensal do conjunto, usando método de custo consistente. Registrar refeições da equipe, cortesias, transferências, perdas e devoluções para explicar o consumo, sem descontar uma perda duas vezes se ela já está refletida na redução do estoque final. Contagem parcial permite um CMV parcial ou estimado, identificado como tal. A proposta SQL armazena o fechamento auxiliar e seu escopo; não finge implementar estoque por item ou apuração fiscal completa.

**Cascata econômica proposta**, com valores de custo/despesa positivos nesta notação:

```text
Vendas brutas
− cancelamentos/devoluções/descontos e tributos sobre vendas aplicáveis
= Receita líquida
− CMV apurado
= Lucro bruto gerencial
− despesas variáveis de venda
= Margem de contribuição
− pessoal e demais despesas operacionais não descontadas acima
= EBITDA gerencial conciliado
− depreciação e amortização
= EBIT
+ receitas financeiras − despesas financeiras
− tributos sobre o lucro
= Resultado líquido
```

Todos os componentes devem entrar uma vez. Se mão de obra já estiver incorporada ao custo contábil de transformação, reconciliá-la antes de somar pessoal no Prime Cost. Se `bruto_net` já exclui cancelamentos, não descontá-los novamente. MDR deve ser distinguida de custo financeiro de antecipação; não reconstruir receita bruta com taxa presumida quando o extrato só informa um crédito líquido.

**EBITDA não é caixa operacional.** Estoques, recebíveis, fornecedores, adiantamentos e itens sem caixa explicam a diferença. Tributos sobre vendas continuam sendo custo/dedução do EBITDA; a adição de tributos na definição de LAJIDA se refere aos tributos sobre o lucro. A CVM é referência conceitual aqui, sem afirmar que o restaurante esteja sujeito às regras de divulgação de companhias abertas. [Resolução CVM 156, arts. 1–4](https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/100/resol156.pdf).

A ponte separada para disponibilidade dos sócios parte de caixa operacional conciliado, deduz CAPEX e principal, incorpora financiamento novo quando aplicável e considera o caixa mínimo e demais compromissos. Distribuições reduzem o saldo bancário; não reduzem lucro. Na DFC, juros pagos têm alternativas de classificação que exigem consistência; não são obrigatoriamente financiamento em todos os referenciais. [CPC 03: fluxos operacionais, investimento e financiamento](https://www.cpc.org.br/Arquivos/Documentos/183_CPC_03_R2_rev%2024.pdf). Ativação e depreciação dependem de critérios do ativo, disponibilidade para uso e vida útil; reparo corrente permanece despesa. [CPC 27](https://www.cpc.org.br/Arquivos/Documentos/316_CPC_27_rev%2008.pdf).

# SEÇÃO 3: TOP 5 RISCOS OCULTOS (TÉCNICOS E FINANCEIROS)

**1. Uma cascata pode fechar e ainda apresentar margens erradas — prioridade alta.**

Evidência: [cascata vigente](../supabase/migrations/20260818270000_cascata_dre_fecha_com_grupo_residual.sql), linhas 79–148; [DRE](../dre.html), linhas 204–223 e 308–369.

`outros` garante a igualdade final por subtração, mas não valida o conteúdo dos subtotais. Se um grupo também explicitamente abatido, como pessoal, for marcado variável, entra na margem e é abatido novamente no operacional; o residual pode compensar o erro ao final. A lista de barras entre receita e contribuição só mostra CMV e impostos, enquanto a flag admite mais grupos. O literal `unidade = 'PRAIA'` também reapareceu na cascata apesar da unidade configurável.

A receita projetada da DRE vem do faturamento comercial, enquanto a realizada segue o fato financeiro. Seus cortes e tratamento bruto/líquido não são necessariamente iguais. Impostos aparecem na projeção chamada fixa, mas na DRE realizada são dedução variável; compartilhar totais de caixa não assegura uma MC projetada comparável. `monthTrend.active` exige receita positiva e projeção maior que realizado; ausência de vendas no início do mês pode ocultar a projeção. `N()` converte nulos a zero, inclusive nos indicadores de custo.

Ação: classificação mutuamente exclusiva por componente econômico, contrato explícito de regime/corte/bruto-líquido e testes dos subtotais. Conferir a definição efetiva de `dre_mensal` e da projeção direta no banco: suas definições-base integrais não estão nesta cadeia local. O exemplo sobre flag é um risco condicional do código; não se confirmou essa configuração em produção.

**2. Calendário perdeu proteções anteriores e usa universos diferentes — prioridade alta.**

Evidência: [otimização anterior](../supabase/migrations/20260770000000_calendario_uma_avaliacao_por_fonte.sql), linhas 72–179, versus [recriação posterior](../supabase/migrations/20260814000000_calendario_encadeia_saldo_entre_meses.sql), linhas 94–207. Patches posteriores trocam filtros de caixa e snapshot, sem restaurar o CTE `movimento_real`.

A recriação faz scans separados de `fato_financeiro` para entradas e saídas e remove a materialização explícita dos agregados. Isso confirma perda do desenho anterior, não o retorno medido de 355 InitPlans ou de uma latência específica. No PG15, algumas CTEs já materializam por padrão quando reutilizadas; outras podem ser incorporadas ao plano. Materializar indiscriminadamente pode bloquear filtros e aumentar trabalho temporário. [PostgreSQL 15: CTEs](https://www.postgresql.org/docs/15/queries-with.html#QUERIES-WITH-CTE-MATERIALIZATION).

As CTEs de vendas e recebíveis leem `raw_stone_*` diretamente. O faturamento consolidado usa `recebimento_stone_net`, que consulta configuração da fonte e da conta Stone. Logo, a composição do calendário não herda automaticamente a exclusão de outra conta/unidade. Além disso, código desconhecido segue incluído pelo `coalesce(..., true)` na view canônica: é uma escolha de inclusão que precisa de alerta e revisão de cobertura, não prova de vínculo válido.

Ação: reaplicar a consolidação sobre a versão atual, preservando o encadeamento entre meses e os filtros novos. Unificar a origem da composição comercial e documentar os canais sem detalhe equivalente. Medir o corpo SQL sob papel/claims/filtros equivalentes à Data API; `EXPLAIN` de uma RPC PL/pgSQL pode mostrar apenas Function Scan. Usar corpo extraído ou instrumentação de statements internos. Comparar resultados antes/depois, tempo de planejamento, execução, loops e buffers.

**3. Dados gravados podem permanecer sem atualização dos painéis — prioridade alta.**

Evidência: [importação web](../importar.html), linhas 278–314; [RPC importadora](../supabase/migrations/20260784000000_importacao_web_protecoes_do_python.sql), linhas 392–406; [worker atual](../supabase/migrations/20260808000000_conciliacao_estorno_assincrona.sql), linhas 53–130.

Há duas falhas distintas:

- **Lacuna transacional:** o navegador grava cada arquivo e solicita recálculo somente ao final. Queda de rede, fechamento da aba ou erro em arquivo posterior pode deixar arquivos anteriores gravados sem tarefa. Reimportação com zero inserções retorna antes de solicitar recálculo.
- **Perda de agendamento:** worker observa fila vazia; produtor insere, agenda e comita; worker desagenda e comita. O lock do worker não é adquirido pelo produtor. Uma tarefa pendente pode ficar sem executor agendado.

O advisory lock e `FOR UPDATE SKIP LOCKED` atuais são acertos. Como o processamento ocorre na mesma transação da marcação, crash que aborta a transação desfaz `processando`; não há base para alegar que esse crash necessariamente deixa uma linha presa nesse estado. O polling também pode ver `pendente` enquanto o trabalho está em andamento. Erro capturado pode terminar como sucesso do job no cron e `erro` na fila: monitorar os dois. [PostgreSQL 15: transações](https://www.postgresql.org/docs/15/transaction-iso.html), [pg_cron](https://github.com/citusdata/pg_cron).

Ação: tarefa na mesma transação das linhas raw, devolvendo seu ID; processamento continua assíncrono. Watchdog leve recupera job perdido, sem executar recálculo na API e sem bloquear o produtor pelo tempo do worker. O watchdog não resolve importação sem tarefa, por isso as duas mudanças são necessárias. Definir limite de tentativas, espera e tratamento separado de erro permanente. Os locks diferentes da virada e do worker não impedem concorrência entre esses dois jobs; medir contenção nas MVs e coordenar os executores de refresh em background.

**4. Última data e hash igual não comprovam completude — prioridade alta.**

Evidência: [cortes](../supabase/migrations/20260818110000_sincroniza_derivados_e_virada_diaria.sql), linhas 10–40; [parsers comuns Python](../scripts/importacao/importacao_core.py), linhas 117–146; [parser SQL](../supabase/migrations/20260751000000_importacao_web_stone.sql), linhas 105–130; [BB vigente](../supabase/migrations/20260819020000_bb_debito_sem_sinal_negativo.sql), linhas 44–118.

`max(data_caixa)` de uma fonte adiantada pode avançar o corte enquanto outra fonte está incompleta. Uma data máxima preenchida não comprova que todos os dias anteriores foram recebidos ou que dias sem movimento foram confirmados. Projeções e percentuais podem parecer fechados apesar da cobertura parcial.

A correção do BB normaliza sufixo C/D e valor nos dois caminhos. Contudo, paridade estrita ainda exige corpus diferencial: Python usa `float` e `strip()` Unicode; SQL usa `numeric` e trim explícito de caracteres ASCII no campo. Um espaço não separável nas extremidades pode alterar o texto e o hash em somente um canal. Valores com precisão além de centavos também precisam ser rejeitados ou arredondados pela mesma política. Não foi medido desvio financeiro causado por esses casos. O hash especial de aplicação de fundo com data + valor presume ausência de duas operações legítimas iguais no mesmo dia; é risco de identidade semântica, não de colisão criptográfica MD5.

Ação: registrar período completo por fonte, incluindo zero movimento confirmado; bloquear fechamento quando faltar fonte obrigatória. Comparar parsers Python e SQL com os mesmos dados sintéticos: formato BB antigo/novo, Unicode, delimitador, campos ausentes, precisão, datas inválidas, estorno, parcelas, duplicata legítima e origem. Rejeitar ambiguidades sem descarte silencioso. Versionar o contrato de normalização; qualquer mudança de hash precisa de migração conciliada dos hashes existentes. Reforçar que os testes locais atuais comparam variantes no Python, não executam o parser PostgreSQL.

**5. Bônus e escala podem otimizar o indicador sem melhorar a operação — prioridade média/alta.**

Evidência: [base de bônus](../supabase/migrations/20260818300000_bonificacao_neutraliza_por_categoria.sql), linhas 59–121; [demanda da escala](../supabase/migrations/20260819000000_escalas_equipe.sql), linhas 163–204; [interpolação](../escalas.html), linhas 78–130.

A base de bônus equivale a `Δ(saldo_total − especie_pendente) − movimentos_neutros`. Depósito interno mantém saldo total e reduz espécie: pode gerar base positiva sem lucro novo. Excluir espécie dos dois lados é matematicamente coerente com premiar dinheiro disponibilizado no banco, mas desloca a recompensa para o mês do depósito. Piso zero, teto e falta de compensação de meses negativos permitem incentivos de calendário. Amortização da dívida decidida pelos sócios penaliza o gerente; novos financiamentos, se não neutralizados, podem favorecê-lo. Adiar manutenção ou fornecedores pode melhorar caixa e piorar a operação.

Ação: acordar resultado operacional controlável e condições de conversão em caixa, com principal de dívida/CAPEX aprovado/retiradas/aportes identificados; manter manutenção ordinária como custo operacional. Avaliar média móvel ou acerto trimestral, provisões de contas e retenção parcial do bônus. Depósito conciliado pode ser condição de liberação da parcela associada à venda, sem virar nova receita. A custódia Quiosque → Responsável → Banco deve manter identificação, baixa da espécie e crédito bancário vinculados, com conferência física, antiguidade e divergências visíveis.

Na escala, a SQL subtrai 75 minutos de **cada timestamp antes de agregar**. Isso é melhor do que deslocar um balde horário inteiro, mas a defasagem continua uma hipótese operacional a calibrar. A operação conserva eventos dentro do domínio completo; não conserva necessariamente pico por hora nem total após corte de janela. O denominador usa dias com alguma transação, excluindo dias observados sem venda. Transações não equivalem a clientes/pedidos; cancelamento total pode continuar contribuindo para `count(*)`. Canais sem hora e pagamentos divididos limitam a inferência de carga de cozinha/salão.

`demandaMin` interpola nos centros `h:30`; suaviza o gráfico, sem criar evidência de demanda de cinco em cinco minutos. A integral precisa multiplicar taxa horária por `5/60`; revalidar conservação na janela e bordas. `hora % 24` não muda o dia da semana e, em JS, resto negativo permanece negativo; hoje a janela diurna reduz a exposição, mas isso importa se o funcionamento cruzar a meia-noite. Capacidade e pisos devem ser positivos, específicos da equipe e revisados com dados de operação. Não tratar a mesma capacidade de transações/hora como uma constante física da cozinha e do salão.

# SEÇÃO 4: PROPOSTAS DE ENGENHARIA DDL & SQL CONCRETAS

O arquivo [PROPOSTAS_AUDITORIA_2026-09-05.sql](PROPOSTAS_AUDITORIA_2026-09-05.sql) contém os blocos completos, idempotentes por nome/âncora, para revisão. Não foi criado arquivo em `supabase/migrations`, nem executado SQL no banco. Antes de converter em migration, listar novamente as versões e escolher uma maior que a maior existente naquele momento. Aplicação estrutural exige a revisão do usuário prevista no AGENTS.md.

| Bloco | Problema e objetos | Dependências / risco | Validação para aplicar |
| --- | --- | --- | --- |
| A | Tabela privada `fechamento_consumo_estoque` + view `app_fechamento_consumo_estoque`. Distingue cobertura Curva A/integral, rascunho/fechado e ausência de medida. | É fechamento auxiliar, não estoque por item nem DRE pronta. Exige conciliação e futura RPC com histórico de revisões. | Rascunho não publica consumo; falta de entrada não vira zero; escopo parcial não vira integral; gates de usuário/unidade. |
| B | Índice parcial da fila + `garantir_worker_recalculo_saldo` + job de verificação a cada dois minutos. | Mesmo owner do worker/agendador; requer funções pg_cron existentes. Recupera agendamento, não retenta erro de negócio. | Fila vazia; pendente sem job; job inativo; worker ativo; instalação repetida; pausa de manutenção. |
| C | Altera a RPC importadora com substituições ancoradas, adicionando a tarefa na transação e `recalculo_id` no retorno. | Instalar B antes e coordenar `importar.html` para acompanhar todos os IDs, retirando solicitação redundante. Front antigo pode enfileirar recálculo duplicado. | Dry-run não enfileira; erro faz rollback conjunto; arquivo novo devolve ID; reimportação sem inserção não cria trabalho; fechar aba não perde tarefa. |
| D | Consulta de catálogo com indicadores do desenho vigente do calendário. | Diagnóstico textual; não mede plano nem valida todo o SQL. | Executar após a cadeia completa e complementar com testes de resultado e plano. |

O bloco C insere **somente a tarefa**, sem `refresh_painel` ou recálculo na requisição. Ao chegar um erro no segundo arquivo, a tarefa do primeiro já estará durável. A programação periódica do bloco B cobre a queda do navegador. A alteração de comportamento do front-end é parte necessária do rollout do bloco C; não está implementada nesta auditoria.

O cadastro de consumo não atribui diretamente `cmv` à DRE: consumo de estoque, perdas e usos fora da venda exigem classificação antes disso. RLS fica habilitado na tabela sem grants de acesso direto; a view usa a barreira e o gate exigidos, `grant select` apenas a `authenticated`, e não referencia `auth.users`.

**Performance e índices.** Já existe `raw_historico_empresa_data_idx (empresa, data_hora DESC)`, criado em `20260766000000`; não recriar o mesmo índice com outro nome. A MV por conta já tem índices `(dia, conta_id)` único e `(conta_id, dia)`. Candidatos a conferir em `pg_indexes` e no plano: datas de vendas/vencimentos nas tabelas de origem, parcial de cancelamentos em recebíveis com `stone_id`, e consultas de última competência paga por conta. O índice único já existente de conta/competência pode bastar; um índice adicional só se justifica pelo plano/custo medido.

Preferir limites semiabertos na coluna timestamp a aplicar `::date` em toda linha quando o filtro puder usar índice. Materializar o conjunto já filtrado e reutilizado, não todo `fato_financeiro`. Manter MVs para agregados amplos. Não se promete desempenho abaixo de 8s só por inspeção do SQL. DDL ocorre pelo executor de migrations, não pela Data API; criação concorrente de índice, quando necessária, exige etapa fora de transação explícita e tratamento de índice inválido após falha. [PostgreSQL 15: CREATE INDEX](https://www.postgresql.org/docs/15/sql-createindex.html).

**Contratos de aceite necessários no banco.** Executar migrations em ambiente de teste representativo, verificar objetos finais via catálogo, validar com papel e claims equivalentes aos consumidores e medir p95 com carga plausível. Um alvo inicial sugerido é p95 inferior a 2s para leituras críticas, mantendo margem para o teto de 8s; é critério proposto, não resultado medido. Testar duas sessões concorrentes para a fila, queda entre upload/enfileiramento, virada de mês, contas com pagamento além do corte, fonte atrasada, estorno de outra conta e mudança da flag de grupo. Medir também tempo de planejamento e contenção de refresh. Nunca testar SQL destrutivo em produção.

# SEÇÃO 5: MATRIZ DE AÇÃO (IMPACTO vs. ESFORÇO)

| Classe | Ação | Impacto | Esforço | Critério objetivo |
| --- | --- | --- | --- | --- |
| Quick Win | Ajustar rótulos de regime, CMV por pagamentos, resultado gerencial e qualidade da cobertura. | Alto | Baixo | Não afirmar competência/CMV apurado sem origem suficiente; nulo aparece indisponível. |
| Quick Win | Publicar fonte e denominador do Prime Cost; revisar pró-labore e encargos. | Alto | Baixo | Indicador e referência usam base comparável. |
| Quick Win | Alertar fila pendente antiga/erro e implantar recuperação do agendamento. | Alto | Baixo/médio | Pendente sem job é recuperada; erro não vira sucesso financeiro. |
| Quick Win | Testar igualdade dos subtotais e configuração variável, além do total final. | Alto | Baixo | Sobreposição de grupos é detectada; `outros` não mascara duplicidade. |
| Médio prazo — prioridade imediata | Outbox atômica e adaptação coordenada da importação web. | Alto | Médio | Fechamento da aba ou falha no lote não perde atualização. |
| Médio prazo | Restaurar consolidação do calendário sobre a versão atual e unificar fontes comerciais. | Alto | Médio | Mesmos totais por universo, continuidade preservada e plano dentro do orçamento. |
| Médio prazo | Contas faturadas, recebimentos e pagamentos vinculados, inventário e fechamento revisável. | Muito alto | Médio/alto | DRE econômica conciliada ao caixa sem duplicar pagamentos. |
| Médio prazo | Reclassificar taxa variável, principal, juros, CAPEX, D&A e retiradas. | Alto | Médio | EBITDA, lucro líquido e disponibilidade dos sócios reconciliáveis. |
| Médio prazo | Paridade Python/SQL com contrato versionado e testes diferenciais. | Alto | Médio | Mesmas linhas normalizadas, motivos de rejeição e hashes no corpus sintético. |
| Médio prazo | Política de bônus controlável e calibração por equipe/horário. | Alto | Médio | Não premiar apenas calendário de pagamento/depósito; demanda comparada à operação observada. |
| Médio prazo | Módulos ES nativos para projeções, formatação e acesso resiliente. | Médio/alto | Médio | Mesmas premissas nas páginas, publicação estática e console sem erros. |
| Armadilha | Rebatizar a cascata atual como EBITDA/competência ou retirar todo pró-labore. | Alto risco financeiro | — | Corrigir a base antes da nomenclatura formal. |
| Armadilha | Migrar para `security_invoker=true` + funções privadas de leitura, por alertas aceitos. | Alto risco técnico | — | Preservar o padrão intencional e autorização efetiva. |
| Armadilha | Recalcular dentro da requisição, aumentar timeout para esconder plano ruim ou materializar toda view indiscriminadamente. | Alto risco técnico | — | Leituras pequenas, cálculo em background e planos medidos. |
| Armadilha | Introduzir Node/framework/build, retry ilimitado ou ERP de estoque completo de uma vez. | Alto custo operacional | — | Preservar stack e evoluir pelos controles materialmente relevantes. |

**Integridade da projeção fixa.** Se `M` é a média mensal, `R` o realizado e `A` as contas abertas, a fórmula atual é `F = max(M − R − A, 0) + A = max(M − R, A)`. Quando `A > M−R`, as obrigações formam um piso: isso é coerente, não um erro automático. A validade exige mesma população e período. Hoje `M/R` usam pessoal, infraestrutura, marketing e impostos, enquanto `A` aceita qualquer recorrência de despesa marcada para totais. Uma recorrência fora desses grupos não deve consumir esse colchão; separar `A` por componente. Pagamento parcial, obrigação sem histórico, mês sem movimento e pagamento de competência anterior exigem regras explícitas. O agendamento por competência também pode colocar pagamento de outro mês no vencimento do mês original: validar essa hipótese com casos sintéticos.

A continuidade exige `saldo(corte+1) = saldo_snapshot(corte) + entradas_futuras(corte+1) − saidas_futuras(corte+1)`, sem sobreposição nem lacuna. Propagar também identificador/data da geração das MVs, não apenas datas de importação. Consultas paralelas em HTTP são transações distintas e podem observar gerações diferentes durante um refresh. Arredondamento diário do colchão deve distribuir o resíduo de centavos de forma determinística se for exigido fechamento exato ao centavo.

**Modularização sem build.** Evoluir o `monthTrend` existente para um módulo de cálculos puros com entradas explícitas de regime, corte, base de receita e componentes. Criar `assets/financial-model.js` e `assets/data-access.js`, usar caminhos relativos com extensão e `script type="module"`; migrar uma página por vez. Preservar o carregamento de autenticação e um adaptador temporário para consumidores globais. Adicionar novos assets à cópia e à lista `expected_files` do workflow. Formatação visual pode ser compartilhada; políticas distintas de caixa e competência devem permanecer distintas e explícitas. [MDN: módulos JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules).

**Resiliência móvel.** Centralizar leituras com fábrica de requisição, no máximo três tentativas e orçamento total; usar espera exponencial limitada com jitter, respeitando `Retry-After` quando disponível. Classificar erro por status, código e causa: conexão/5xx transitório pode repetir; falha de permissão/validação não; cancelamento do usuário também não. Não interpretar todo `57014` como falha transitória. Tratar o retorno `{data,error}` do Supabase, não apenas exceções. Cancelar consultas obsoletas com AbortController, manter o último dado confirmado com indicação de defasagem e separar falha de projeção de leitura do realizado. No momento, uma falha em qualquer uma das quatro consultas da DRE apaga a página inteira. Retentativas de mutação exigem identidade idempotente da operação; não reutilizar cegamente a política de leitura. [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController).

Validação visual futura: celular de 360/390px e desktop, abertura/navegação/troca rápida de mês, rede lenta/offline/retorno, mensagens de cobertura e estado do lote, navegação por teclado e console. Nenhum HTML/CSS/JS foi alterado nesta auditoria, portanto não foi alegado teste visual ou de console da aplicação.

**Verificações realizadas nesta auditoria:** contratos financeiros, front-end, acesso e estrutura das 150 migrations passaram. Importação: nove dry-runs sintéticos, rejeição de cabeçalho inválido, saldo BB divergente, regras de conta e formatos BB antigo/novo passaram. A primeira execução do teste de importação teve diferença de codificação entre subprocessos no Windows; repetição com `PYTHONUTF8=1` passou, sem alteração do código. As propostas passaram pelo parsing de 29 statements SQL e quatro blocos PL/pgSQL; a transformação do importador teve suas três âncoras únicas verificadas e o resultado também foi analisado sintaticamente. Cinco verificações matemáticas/de normalização sintéticas passaram. O parser local foi pglast 8.4/libpgquery PostgreSQL 18.4, instalado apenas em pasta temporária: isso não substitui execução/idempotência real em PostgreSQL 15, resolução dos objetos, grants e EXPLAIN. Não havia PostgreSQL local nem conector de banco disponível.

Arquivos novos desta auditoria: este parecer e `docs/PROPOSTAS_AUDITORIA_2026-09-05.sql`. Apenas um recado foi acrescentado ao canal, preservando seu conteúdo preexistente. Não houve mudança em aplicação, importadores ou migrations, nem `git add`, commit ou push. Nenhum segredo, CSV, planilha, dado bruto ou conteúdo da auditoria de segurança preexistente foi incluído nos artefatos. Mensagem de commit sugerida para os arquivos desta tarefa: `docs: registra auditoria financeira e propostas de atualização assíncrona`.
