# Integração por API: Stone e Banco do Brasil

Objetivo: trocar a exportação manual de CSV por download automático, sem
mudar as tabelas nem as regras do painel.

## Fechamento D+1 implantado (22/10/2026)

- Escopo atual: operação Praia, cartão/Pix, parcelas e baixas, extrato e
  atualização do painel. **Voucher fica separado.** O proprietário confirmou
  que **não usa link de pagamento**; eventual uso futuro será separado. O
  173835323 permanece fora da coleta e do fechamento, sem alterar o histórico.
- Prazo: dia civil D até **23h59 de D+1 em Fortaleza**. Turno Saipos 08h–08h
  pode incluir a madrugada do dia civil seguinte; isso continua explícito.
- `stone_fechamento.py` registra etapas privadas por dia: vendas, recebíveis,
  baixas, painel e extrato. Saúde e Status geram o calendário desde 21/10,
  incluindo dias sem execução, e mostram o último dia **contíguo** concluído.
  Falta de arquivo nunca significa dia sem movimento. Dias vazios comprovados
  pelos dois arquivos encerram normalmente, sem inventar linhas financeiras.
- `api_stone_baixas.py` aplica liquidações de capturas anteriores, conferindo
  unidade/conta, identificadores, bruto e líquido em centavos. XML preserva sua
  precisão de seis casas. Altera só status/datas comprovadas; não muda valores,
  taxas ou dados da captura. Identidade de pagamento/carteira/parcela, versão,
  hash e antes/depois ficam em `private.stone_baixa_evento`, na mesma transação.
  Conflitos ficam pendentes e não se resolvem automaticamente por replay.
- Migration `20261022200001` aplicada e registrada no portal, após ensaio SQL
  com rollback. Controles privados com RLS e sem acesso de anon/authenticated;
  `app_stone_fechamento` expõe só metadados administrativos e grants explícitos.
  Avisos de view definer/RLS sem policy seguem o padrão intencional do projeto.
- Rotina de 21/10 executada **somente pelo cache**: 63 liquidações conferidas,
  38 baixas novas; reexecução de conferência = zero atualizações e zero
  divergências. Cartão/Pix/recebíveis/painel confirmados. Nenhuma nova chamada
  à API Stone. Uma conferência Pluggy encontrou saldo consistente e zero novos;
  o relógio de sincronização da origem ainda era de 21/10, então o extrato
  ficou corretamente aguardando uma origem posterior ao encerramento do dia.

### Agenda publicada e limites

| Horário de Fortaleza | Operação |
|---|---|
| 06h10 e 18h10 | Coleta limitada de arquivos nunca pedidos e recuperação |
| 11h10, 16h10 e 23h10 | Recuperação estrita pelo cache/fila privada, sem rede bancária |
| 00h10 | Verificação somente leitura; atraso gera saída de erro do workflow |
| 00h43, 09h43 e 21h43 | Conferência/importação do extrato pela Pluggy |

Cada rodada de aquisição permite **no máximo um XML e um pedido Pix novos**.
A reserva persistida antecede a rede; timeout, erro ou rodada paralela não
liberam repetição. Dias nunca iniciados entram em ordem, com o mesmo orçamento.
401/403, 429, 5xx e resultado incerto têm mensagens distintas no fechamento.
Não apagar reservas nem usar novo dia/stonecode para testar uma recusa.

Pix tardio retoma em outra rodada. Um aviso já salvo impede outro POST mesmo
sem controle anterior; callback recente com erro não esconde conteúdo válido.
Novo arquivo válido de dia já processado reabre a conferência das vendas.
Quando há aviso sem CSV, o modo de aquisição pode recuperar o endereço já
recebido: máximo dois GETs por CNPJ/dia, intervalo mínimo de 1h, timeout de20s,
limite de5MB, HTTPS e nenhum redirecionamento/credencial bancária. Link expirado
permanece pendente, sem novo POST automático.

Comandos:

```text
python scripts/importacao/api_stone_rotina.py --saude
python scripts/importacao/api_stone_rotina.py --somente-cache --aguardar 0
python scripts/importacao/api_stone_rotina.py --dia 2026-10-21 --somente-cache
```

`--dry-run` e `--saude` só leem. `--somente-cache` não consulta Stone/Pluggy/
Saipos nem baixa link. `--recuperar-downloads` permite apenas o GET limitado do
arquivo anunciado, sem repetir a solicitação. Saúde/cache dispensam chave
Stone. O resultado aparece em **Status > Fechamento automático Stone**, sem
apagar o histórico anterior de erros. O alerta ativo usa os mecanismos já
existentes do GitHub; nenhum e-mail/WhatsApp externo foi configurado ou enviado.

O extrato só conclui dias dentro do período realmente consultado e com
`lastUpdatedAt` posterior ao dia, saldo conferido e refresh concluído. Não usa
o horário da consulta nem edição de metadados como prova de sincronização.
Autorização expirada, indisponibilidade externa e eventos ainda sem regra
(chargeback, antecipação, certos cancelamentos) são pendências explícitas.
Capturas com FeeType diferente do regime MDR conferido, antecipação ou tarifa
adicional não validada são recusadas, preservando a classificação financeira.

Validação: testes sem rede de retomada, orçamento, Pix, dia vazio, SLA e baixas;
SQL real com rollback para idempotência/precedência/conflitos/transação; testes
do Status para cobertura, escape HTML e paginação. Os próximos arquivos novos
e sincronizações da origem serão processados pela agenda, sem sondagens extras.

## Em produção: cartão e Pix direto da Stone (22/10/2026)

- Webhook `stone-webhook` publicado no portal e cadastrado na Stone (HTTP
  201). Solicitação única do Pix de 21/10 aceita com HTTP 202; os 13 Pix foram
  recebidos e baixados no banco privado. Não usar os Pix da Saipos como venda
  Stone nem criar IDs sintéticos do extrato.
- `api_stone_vendas.py` importa juntos o cartão XML e o Pix CSV. STONE ID do
  cartão = `AcquirerTransactionKey`; Pix = `pix_transaction__e2e_id` (32
  caracteres), preservando a deduplicação com o CSV do Portal. Valores Pix em
  centavos e `created_at` UTC convertido para Fortaleza: prova real dos nove
  créditos já no extrato, mesmos valores e minutos. Os quatro Pix da noite
  ainda ausentes da Pluggy vieram pelo webhook.
- Carga de 21/10 concluída: 38 cartões + 13 Pix = 51 vendas; 49 novas e duas
  preservadas. As 51 conciliam com os 51 pagamentos da Saipos; quantidade e
  soma conferidas. Recebíveis atualizados (36 novas parcelas). `refresh_painel`
  executado e reprocessamento conferido com zero vendas novas.
- `api_stone_rotina.py` executa um dia fechado por vez. O controle
  `private.stone_api_controle` reserva cada pedido antes da rede e guarda o
  XML; Pix recebido fica em `stone_pix_arquivo`. Reexecutar usa esses arquivos;
  não baixa uma semana da Stone nem repete pedidos após timeout. 401/403/429
  suspendem novas consultas até revisão do responsável. Não limpar o controle
  para tentar novamente sem diagnosticar a recusa.
- O cadastro da URL tem limite de **100 caracteres**. Token privado com 24
  caracteres aleatórios, guardado no `.env` e nos segredos da função, mantém
  a URL dentro do limite. Nunca publicar a URL completa, logs de requests ou
  segredos. O receptor exige token, valida CNPJ/data/HTTPS e responde ao aviso
  antes de baixar o CSV em segundo plano. Testes fictícios cobrem autenticação
  e download sem enviar a chave de serviço ao endereço do arquivo.
- Cartão/Pix com cancelamento ou código ainda sem regra validada recusam a
  carga de vendas inteira, para conferência com o CSV. Voucher continua no
  CSV. A Saipos continua reconsultando sete dias para recuperar falhas e
  alterações; sua conciliação lê a Stone no banco, sem chamar a API Stone.

## Diagnóstico e solução proposta para fechar a automação (22/10/2026)

**Registro do diagnóstico anterior à implantação descrita acima.** Escopo: vendas
cartão/Pix, recebíveis e suas baixas, extrato e atualização dos derivados do
painel. Voucher fica separado, explicitamente fora deste fechamento. Um
workflow ativo ou verde não é prova de cobertura de todos os dados.

### Problema real e evidências

- O controlador só processa ontem. Pix entregue depois dos 35 minutos de
  espera fica guardado, mas não volta à carga automaticamente. Também faltam
  recuperação do download após um aviso e preferência por um arquivo válido
  quando um callback posterior contém erro.
- O XML contém liquidações de capturas anteriores. O importador usa essas
  liquidações apenas ao montar capturas presentes no lote e insere com
  `ON CONFLICT DO NOTHING`. Portanto não baixa parcelas antigas já gravadas.
  A leitura dos XML privados existentes confirmou pagamentos de capturas
  anteriores, sem nenhuma nova consulta à Stone. Não confundir crédito no
  extrato com baixa conciliada da parcela.
- Um dia comprovadamente sem cartão e sem Pix chega à importação com lista
  vazia, que o núcleo recusa. Deve existir conclusão `sem_movimento` baseada
  nos arquivos válidos, sem inventar venda para avançar datas.
- Cancelamentos de cartão/Pix, chargebacks e códigos não mapeados podem
  recusar a carga inteira. Há exemplos privados de cancelamento total e
  parcial da Praia; não houve chargeback nos XML disponíveis. Não generalizar
  regras de outras casas ou inventar equivalência sem comprovação.
- O link 173835323 está ativo no faturamento, mas excluído da API por decisão
  anterior do proprietário. Há movimentos históricos nos CSV e XML vazios de
  datas posteriores. Isso **não prova perda de movimento na mesma data**, nem
  comprova cobertura atual. O escopo deve registrá-lo como integração a
  confirmar, sem reativação silenciosa nem novas sondagens.
- Consulta somente leitura ao portal confirmou arquivos de 21/10 recebidos e
  processados e logs de sucesso de vendas/recebíveis desse dia. Não houve nova
  chamada Stone, Pluggy ou Saipos, nem alteração financeira nesta auditoria.

### Pedido reformulado

Automatizar a coleta, importação, conferência e publicação das vendas cartão
e Pix, recebíveis com baixas e extrato Stone, mantendo Voucher como exceção
separada. Controlar cada dia e fonte esperados, recuperar pendências com os
arquivos privados sem repetir pedidos, preservar o histórico, registrar
divergências e informar atraso ou bloqueio. Só declarar fechamento quando as
etapas e o refresh estiverem concluídos. Nenhum dado pode ser inventado para
apresentar uma atualização aparente.

### Solução e ordem de execução

1. **Baixas auditáveis.** Processar os eventos de liquidação por Stone ID,
   parcela e conta mesmo sem captura no arquivo do dia. Atualizar apenas os
   campos comprovados pelo evento, com proveniência e transação. Preservar
   campos de captura, taxas e valores que o evento não confirme; comparar
   valor líquido/data e impedir duplicação ou regressão por arquivo antigo.
   Eventos sem parcela conhecida viram pendência para conciliar após recuperar
   a captura. Validar contra XML/CSV privados antes de escrita real.
2. **Recuperação por arquivos.** Separar aquisição de processamento. O
   processamento retoma datas pendentes pelo XML privado e fila Pix, inclusive
   depois do timeout e com as consultas Stone suspensas. Reprocessar não
   significa pedir o arquivo de novo. Um arquivo íntegro prevalece sobre outro
   callback com erro. Download do link já recebido precisa de controle próprio
   e respeito à validade do endereço, sem novo pedido Pix automático.
3. **Calendário e controle de conclusão.** Registrar cada dia esperado desde
   uma data de início, por fonte/CNPJ/stonecode, incluindo dias sem movimento.
   Separar pedido, recebimento, validação, gravação, conciliação e refresh.
   Detectar tanto dias solicitados incompletos quanto dias nunca iniciados por
   falha de agenda. Não usar apenas `max(data_venda)` ou a última execução verde
   como prova de completude. Ausência de arquivo não equivale a zero vendas.
4. **Aquisição com limites.** Preservar reserva antes da rede, PK única e
   nenhum pedido repetido em paralelo. Para dias nunca solicitados, usar fila
   persistente e orçamento explícito, sem varredura indiscriminada do histórico.
   Recusa de acesso (401/403), limite (429), indisponibilidade (5xx), timeout
   com resultado incerto e erro de layout devem ter diagnósticos diferentes.
   Não apagar reservas ou liberar repetição só pela idade da pendência.
5. **Cobertura financeira.** Validar cancelamentos totais/parciais com os
   exemplos existentes; confirmar regras de parcelamento, estorno Pix,
   chargeback, antecipação e novos códigos usando contrato e exemplos
   comprováveis. Partes independentes podem avançar, mas uma etapa afetada não
   pode ser marcada como concluída. Resolver a cobertura do link antes de
   prometer que somente Voucher continuará manual.
6. **Verificação de saúde e publicação.** Rodadas de recuperação consultam o
   banco, não sondam a Stone. A verificação mostra até qual dia cada fonte foi
   conferida, idade da atualização da origem, o que falta e o motivo. Só
   marcar conclusão após conciliação e refresh; falha após commit deve retomar
   essas etapas sem reinserir valores. Aumentar consultas ao proxy não adianta
   uma sincronização da origem que ainda não ocorreu.

Meta operacional confirmada pelo proprietário: dia civil D fechado até
**23h59 de D+1 em America/Fortaleza**. Manter aquisição inicial às 06h10;
propor retomadas dos arquivos privados durante o dia e conferência final antes
do prazo. Para o extrato, avaliar uma rodada à noite, além das duas atuais,
sempre verificando o frescor da origem. Os horários de retomada são desenho,
não mudanças já publicadas. Prazo vencido com fonte indisponível deve indicar
atraso e causa; não converter a meta em garantia de disponibilidade externa.

### Decisões e informações que faltam

- Prazo operacional **definido**: até o fim do dia seguinte (23h59 em
  Fortaleza), conforme resposta do proprietário em 22/10. Falta medir o frescor
  efetivo das fontes para verificar se atendem consistentemente à meta.
- Separar dia civil financeiro de turno Saipos (08h a 08h). Se houve venda na
  madrugada de hoje atribuída ao turno de ontem, seu arquivo Stone de hoje só
  estará disponível amanhã; não prometer turno inteiramente conciliado antes.
- Confirmar fonte e tratamento do link de pagamento sem contrariar a decisão
  anterior de não consultá-lo; não há prova recente com movimento nesse código.
- Exemplos/contrato dos eventos não presentes no acervo da Praia, especialmente
  chargeback e antecipação. Os exemplos de cancelamento em XML e CSV não foram
  comprovados como o mesmo caso; falta esse cruzamento para validar a regra
  monetária. A falta de exemplos não autoriza ignorar eventos.
- Definir destinatário e canal de alerta ativo, além do Status existente. Não
  enviar mensagens externas nem contratar serviços sem autorização específica.
- Confirmar prazo/validade e forma de renovação do consentimento Pluggy e
  comportamento de entrega/reentrega de arquivos durante incidentes. Incidentes
  de autenticação podem exigir intervenção do titular mesmo com automação.

### Critérios verificáveis de conclusão

- Cada dia esperado desde a virada tem resultado por fonte e unidade; nenhum
  buraco fica oculto pela existência de dados em uma data posterior.
- Reexecutar, receber callback duplicado ou reiniciar após commit não duplica
  vendas, parcelas, baixas ou dinheiro no extrato.
- Liquidação de venda antiga atualiza a parcela correta, com trilha da origem,
  sem trocar valores/status sem prova e sem regredir por evento fora de ordem.
- Pix tardio conclui um dia antigo com zero novos pedidos de arquivo Stone;
  recusa anterior não impede processar dados que já estejam disponíveis.
- Dia vazio comprovado termina `sem_movimento`; aviso com erro não esconde
  arquivo válido. Falha de download, callback ou refresh tem teste de recuperação.
- Totais e quantidades conferem com os arquivos; saldo importado fecha com o
  extrato. Conciliação Saipos aponta diferenças reais sem ajustar à força.
- Meta de atualização e atraso da origem são visíveis; fonte atrasada ou
  inacessível gera pendência explícita, jamais indicação de fechamento falso.
- Dia civil D concluído até 23h59 de D+1 em Fortaleza quando os arquivos
  estiverem disponíveis; ultrapassar o prazo gera atraso identificável. Turno
  que cruza a meia-noite tem janela distinta, sem antecipar dados da Stone.
- Ciclos agendados reais comprovam funcionamento sem PC e sem operação manual,
  além dos testes sem rede de falhas, concorrência, dia vazio e retomada.

A confiabilidade depende também dos provedores: o GitHub documenta atrasos e
possível descarte de jobs agendados; o Meu Pluggy informa atualização da origem
a cada 24h. Uma garantia rígida de horário exigiria resolver essas dependências,
não apenas mudar o cron. A solução deve garantir rastreabilidade, controle de
completude e recuperação segura; indisponibilidade externa precisa aparecer.

Referências: [agendamento GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule),
[atualização Meu Pluggy](https://meu.pluggy.ai/api-guide),
[erros Stone](https://conciliacao.stone.com.br/reference/mensagens-de-erro) e
[limites Stone](https://conciliacao.stone.com.br/reference/rate-limit).

## Diagnóstico inicial de 22/10/2026 (antes da ativação acima)

- Às 14:43 de Fortaleza, uma única requisição do arquivo de 21/10 para
  o stonecode 770398216 retornou **HTTP 200**, com XML validado. Sem repetição,
  redirecionamento ou consulta a outro stonecode. O XML ficou na pasta privada
  já ignorada pelo Git; não houve importação nem alteração de dados no banco.
  Esse sucesso pontual não comprova resolução permanente do 403 intermitente.
- O histórico registra cerca de 120 consultas na carga de 20/10 e cinco testes
  em 21/10. Volume é uma hipótese para a recusa, ainda sem confirmação da Stone.
  Não repetir esses testes nem usar outro dia/stonecode para sondar o bloqueio.
- O baixador agora interrompe toda a rodada no primeiro 403, mesmo que um
  arquivo anterior tenha sido aceito. Os alvos restantes ficam como
  **não consultados**, distinguindo pendências de novas requisições. A mesma
  distinção vale para as interrupções por 401, 429 e 503. Os testes são sem rede.
- As linhas de 22/10 às 10:58 no Status correspondem a uma execução Saipos:
  sete dias de vendas e sete de cancelamentos, todos com o mesmo link do
  Actions. A conciliação usa as vendas Stone já no banco; não consulta a Stone.
- As vendas Stone de 21/10 no banco terminavam às **10:29**, importadas antes
  do encerramento do dia. A Saipos já continha o turno completo de 21/10.
  O Pluggy atualiza `raw_stone_extrato`, não `raw_stone_vendas`. O importador
  automático de vendas Stone (cartão + Pix e deduplicação com o CSV) continua
  pendente; baixar o XML ou atualizar recebíveis não preenche essa tabela.
- O agendamento de `importacao-diaria.yml` permanece pausado desde 20/10, e
  `STONE_CONCILIACAO_API_KEY` segue ausente dos Secrets do GitHub. Um teste
  bem-sucedido não religa a rotina nem significa que as vendas foram atualizadas.

## Situação em 20/10/2026

| Fonte no painel | API | Estado |
|---|---|---|
| Recebíveis Stone (`raw_stone_recebiveis`) | Stone, API de Conciliação | importador provado; gravação autorizada; rotina no GitHub aguarda segredos e a chave voltar a responder |
| Vendas Stone com cartão | Stone, API de Conciliação | mapeamento provado; grava junto com o Pix do mesmo dia |
| Vendas Stone Pix (23% do faturamento Stone) | extrato Stone pela Pluggy (preferido) ou arquivo Pix por webhook | extrato: comparação provada, gravação aguarda a virada do CSV de vendas; webhook: código pronto, não publicado |
| Vendas Stone Voucher (0,8%) | nenhuma | a Stone não entrega Voucher por API; segue pelo CSV |
| Extrato BB (`raw_bb`) | BB, API Extratos | baixador pronto; faltam contrato, aplicativo e certificado |
| Extrato Stone (`raw_stone_extrato`) | Stone, API da Conta Stone | sem acesso de cliente; a Stone pede parceria comercial |

- `scripts/importacao/api_stone_conciliacao.py` baixa o XML diário de
  conciliação por stonecode.
- `scripts/importacao/api_stone_recebiveis.py` monta as linhas de
  `raw_stone_recebiveis` a partir desses XML e grava pelo mesmo
  `importar_registros` do CSV. Com `--baixar`, baixa antes os dias que faltam.
- `scripts/importacao/api_stone_pix.py` cadastra o webhook, pede o arquivo
  Pix e compara os arquivos recebidos com o painel.
- `scripts/importacao/integracao_log.py` grava cada dia processado em
  `integracao_execucao`, mostrado em Status > Integrações automáticas.
- `scripts/importacao/api_bb_extrato.py` só baixa e confere o extrato BB.
- Arquivos baixados ficam em `scripts/importacao/api-*/`, pasta ignorada pelo
  Git. Testes sem rede: `scripts/ci/test_api_bancos.py`.

## Rotina diária no GitHub Actions

`.github/workflows/importacao-diaria.yml` tem aquisição às **06h10 e18h10**,
retomada estrita do cache às **11h10,16h10 e23h10** e saúde às **00h10**, em
Fortaleza. O GitHub pode atrasar a execução. A rotina recupera dias desde21/10,
limitando novos pedidos por rodada e guardando arquivos no banco privado. O
XML exige D+1 após 05h, e o Pix, D+1 após 03h. O webhook aguarda a geração do
arquivo, não recebe cada pagamento em tempo real.

Execução manual: Actions > Importação diária por API > Run workflow. Campo
`dia` opcional (AAAA-MM-DD; vazio = ontem); `dry_run` confere sem consultas
Stone ou gravação. Um dia com vendas e recebíveis já importados termina com
**zero consultas**. Não usar o antigo campo `dias` nem fazer cargas em lote
para sondar acesso. Enquanto a Stone prepara o Pix, a rotina consulta só a
fila do nosso banco, sem novos pedidos à Stone.

O repositório é público, então o log do Actions também é. A rotina escreve
no log só as linhas de erro; o detalhe fica em `integracao_execucao`.

Segredos em Settings > Secrets and variables > Actions, com os valores do
`gestao/.env`: `DATABASE_URL` e `STONE_CONCILIACAO_API_KEY` (já cadastrados).
`SUPABASE_URL` está fixada no workflow para o portal público correto; não é
segredo. O token do webhook só é necessário no receptor e no cadastro, não
na rotina diária. Não guardar XML/CSV em caches ou artifacts do Actions.

## Pix pelo extrato (comparação; fonte de vendas substituída pelo webhook)

No extrato Stone, Pix de venda na maquininha é crédito `Transação` e Pix de
transferência é `Pix`. `scripts/importacao/api_stone_pix_extrato.py` compara
esses créditos com as vendas Pix do CSV, sem gravar:

- setembro/2026: 528 de 528 casados por valor, no mesmo minuto ou com 1 minuto
  de diferença; os 4 créditos internos de madrugada com pagador
  `Desconhecido` ficam de fora;
- 1–20/10/2026: 349 de 349 casados, mais 23 vendas Pix de 19–20/10 que só o
  extrato da Pluggy tinha.

O extrato não traz o identificador do Pix, então a venda gravada por aqui teria
`stone_id` `EXTRATO-<dedup_hash>` e não casaria com a mesma venda vinda do CSV.
Gravar exige uma virada: a partir de uma data, o CSV de vendas deixa de gravar
Pix (proteção como a do extrato Pluggy). Faz sentido quando o cartão também
vier pela conciliação; até lá o CSV de vendas continua por causa do cartão.

## Pix pela API de Conciliação (webhook implantado)

1. Receptor e cadastro **já concluídos**. Não cadastrá-los novamente para
   testar esta entrega. Reimplantação, se necessária:
   `python scripts/implantacao/implantar_stone_webhook.py --aplicar`.
   Destino validado por credencial local; só altera esta função e seus segredos
   `STONE_WEBHOOK_TOKEN`/`STONE_PIX_DOCUMENT`, preservando as demais funções.
2. Rotina normal: `python scripts/importacao/api_stone_rotina.py`. Para um
   dia específico, `--dia AAAA-MM-DD`; `--dry-run` não consulta a Stone.
3. Arquivos já recebidos: `python scripts/importacao/api_stone_vendas.py
   --de AAAA-MM-DD --dry-run`. Sem `--dry-run`, importa, concilia com a Saipos
   já no banco e atualiza o painel. Só prossegue com cartão e Pix do dia.
4. `api_stone_pix.py --solicitar` também respeita o controle persistente de
   pedidos. Não usar a função Python de rede `solicitar()` diretamente fora
   da rotina/controlador. `--analisar` continua disponível para comparações.

## Passo a passo do proprietário

### Stone: API de Conciliação

1. No computador, entrar em `conta.stone.com.br` como **titular** e trocar
   para a conta da empresa dona dos stonecodes. A Stone documenta este passo
   só na web, não no app.
2. Clicar no nome, no canto superior direito, e abrir **Perfil > Acesso e
   Segurança > Chaves de autenticação > Criar Chave**. Escolher **"API de
   Conciliação Stone"**.
3. Copiar a chave e colar no `gestao/.env`, sem enviá-la por chat:
   `STONE_CONCILIACAO_API_KEY=<chave>`.
4. Quando for solicitado um diagnóstico, executar **uma única vez**:
   `python scripts/importacao/api_stone_conciliacao.py --verificar --stonecode 770398216`.
   O comando consulta somente o arquivo de ontem desse stonecode. Não repetir
   em sequência nem consultar outros alvos após um erro. O teste de 22/10 já
   foi feito; não executá-lo novamente para conferir este registro.

Feito em 20/10/2026 com a chave "chaveapi-sirfisher". Ela funciona para
770398216 (Praia) e 173835323 (link de pagamento). O 140366173 (Imprensa)
respondeu 403: é de outro CNPJ e não entra no faturamento.

Sem `--stonecode` nem `STONE_STONECODES`, os scripts usam os stonecodes com
`ativa` e `entra_faturamento` em `stone_conta`, lidos com o `DATABASE_URL`
do `.env` em modo somente leitura. Imprensa e Pub ficam de fora.
Desde 21/10/2026, por decisão do proprietário, o 173835323 (link de
pagamento) também fica fora da API (`STONECODES_FORA_DA_API`), mesmo se vier
do banco ou de `STONE_STONECODES`. Segue em `stone_conta` e no faturamento;
só um `--stonecode 173835323` explícito o consulta.
Incidente de 20/10/2026: depois de cerca de 120 consultas em uma hora, a
chave passou a receber 403 em todos os dias dos dois stonecodes, inclusive
dias baixados com sucesso minutos antes. O 403 informa uma recusa de acesso;
sozinho não confirma chave válida, CNPJ incorreto ou bloqueio por volume.
Conferir no site da Stone se a chave segue ativa e com os stonecodes; se
estiver, perguntar à Stone se há bloqueio por volume. Desde 22/10, um 403
encerra toda a rodada sem consultar outros dias ou stonecodes. O agendamento
continua pausado; o padrão atual exclui o link de pagamento.

Limites documentados pela Stone: o arquivo de um dia sai no dia seguinte a
partir das 4h (HTTP 503 antes disso), e cada combinação de stonecode e dia
aceita 7 consultas por hora (HTTP 429). O script não baixa de novo o que já
está na pasta, salvo com `--sobrescrever`.

### Stone: extrato da Conta Stone

A API da Conta Stone (saldo, extrato, Pix e boletos) é a mesma que sistemas
de gestão como o vhsys usam. A Stone a libera por contrato de parceria com o
time comercial, não por chave no site. Pedido a fazer: "queremos a API da
Conta Stone para o sistema próprio da Sir Fisher ler o extrato da nossa
conta; vocês liberam como parceiro de integração própria?". Enquanto isso, o
CSV continua.

### Alternativas para automatizar todo o painel

| Caminho | Cobre | Custo | Observação |
|---|---|---|---|
| APIs diretas (atual) | Stone cartão, Pix e recebíveis; BB pela API Extratos; Conta Stone se a parceria sair | sem mensalidade conhecida; confirmar tarifa do BB | mais trabalho por banco |
| Open Finance via agregador (ex.: Pluggy Data) | extratos de todas as contas, inclusive Stone, BB, Inter e BNB | a partir de R$ 2.500/mês (Pluggy, out/2026) | consentimento renovado periodicamente; descrições diferentes do CSV pedem data de virada |
| Meu Pluggy (gratuito) | contas próprias autorizadas no Meu Pluggy | grátis para o acesso aos próprios dados pelo conector MeuPluggy | guia oficial permite proxy na aplicação demo sem assinatura/due diligence; não confundir com produto para dados de terceiros |
| Sistema de gestão integrado à Stone (ex.: vhsys) | extrato da Conta Stone | mensalidade do sistema | o painel leria do sistema, mais uma dependência |

Não entram em nenhum caminho: vendas em espécie, que são lançamento manual,
e Voucher, que a Stone não entrega por API.

### Meu Pluggy: extrato Stone e execução online

O [guia oficial](https://meu.pluggy.ai/api-guide) documenta o acesso gratuito
aos próprios dados via conector MeuPluggy na aplicação demo. A afirmação
anterior de que esse caminho exigia o plano comercial foi corrigida.
Conectar um banco diretamente no Dashboard é outro fluxo.

- `conectar_pluggy.py` abre uma página **só em 127.0.0.1**, por padrão na
  porta 8766, para autorizar uma conta já conectada no Meu Pluggy. Salva
  `PLUGGY_ITEM_IDS` no `.env` privado depois de consultar o item na aplicação.
  Somente o connect token restrito vai ao navegador. Client ID/secret e API
  key permanecem no Python. Aceita os nomes antigos `PLUGGY_Client_ID` e
  `PLUGGY_Client_Secret`, além dos nomes totalmente maiúsculos.
- `api_pluggy.py --verificar --catalogar` confere consentimento e salva um
  catálogo privado em `scripts/importacao/api-pluggy/contas.json`. Para baixar,
  indicar `--conta`, `--de` e `--ate`. Paginação usa `/v2/transactions`,
  `dateFrom/dateTo` e a query `next` completa. As datas são convertidas para
  Fortaleza, com a janela UTC ampliada até o dia seguinte e filtro local.
- `api_pluggy_stone.py --dry-run` compara com o histórico e confere saldo.
  Sem a opção, importa somente movimentos novos, recalcula e atualiza o painel.
  Configuração privada: `PLUGGY_STONE_ITEM_ID`, `PLUGGY_STONE_ACCOUNT_ID`,
  `PLUGGY_STONE_CONTA_ID` (vínculo do Gestão) e `PLUGGY_STONE_DESDE`.
- A execução automática fica em `.github/workflows/importacao-pluggy.yml`,
  às **00:43 e 09:43 de Fortaleza**, com credenciais nos Secrets privados do
  GitHub. **Não depende do PC ligado**. O resultado aparece em
  **Status > Integrações automáticas > Extrato Stone (Pluggy)**.

Prova de 20/10/2026: 891 movimentos de setembro correspondem por data local,
valor e multiplicidade ao CSV. Simulação na view financeira vigente reproduziu
as 891 classificações individuais e os 191 grupos diários de categoria/grupo/
status e seus totais. O nome completo foi preservado da descrição bancária;
CNPJ mantém a formatação com `/` e CPF o trecho mascarado usado no legado.
Cinco débitos de boleto tinham tipo genérico `Transação` no CSV e ficam como
`Pagamento`; ambos seguem o mesmo DE-Para e a classificação financeira conferiu.

Regras de segurança da carga:

- Registros Pluggy usam hash de conta + ID da transação; reexecução não duplica.
  Alteração de conteúdo de ID já importado interrompe a carga. O legado é
  preservado e comparado por dia/valor/quantidade; isso não comprova identidade
  nem detecta toda possível retificação de soma zero no histórico sem IDs comuns.
- Correspondência parcial, movimento retroativo, moeda/tipo desconhecido,
  consulta incompleta, saldo divergente ou último instante com ordem ambígua
  impedem a gravação inteira. O saldo final da base + novos movimentos deve
  corresponder ao snapshot da conta, reconsultado antes de gravar.
- Escrita, recálculo e log de carga ficam na mesma transação, com bloqueio
  de concorrência da tabela de extrato. O refresh posterior é recuperável na
  próxima rodada, inclusive quando não houver novos movimentos.
- Migration `20261020231044` impede novos CSVs na conta a partir da primeira
  data efetivamente importada pela Pluggy. Hashes históricos idênticos continuam
  sendo ignorados normalmente. Um fallback de CSV após a virada exige revisão
  da integração; não misturar os dois formatos sem esse controle.
- A origem do Meu Pluggy atualiza a cada 24h. O proxy não aceita PATCH;
  `nextAutoSyncAt` nulo é normal. `/v2/items` não está disponível nesse caminho;
  guardar IDs no callback. Renovar o consentimento quando expirar.

BB fica para uma etapa posterior: o proprietário informou que conectará depois.
Não contratar plano nem criar conexão bancária direta para contornar esse passo.

Implantação conferida: migration aplicada no portal (histórico 204), primeira
carga de 33 movimentos de 19–20/10 com saldo fechado e reexecução sem novos.
Rotina real no GitHub aprovada em
https://github.com/sirfisherfc/gestao/actions/runs/39514186190 e registrada na
página Status como origem `github`. Qualidade e deploy Pages aprovados.

### Banco do Brasil: API Extratos

1. **Gerente BB:** pedir a habilitação da **API Extratos** para a conta PJ e
   perguntar se há tarifa.
2. **Portal Developers BB** (developers.bb.com.br): criar a conta de
   desenvolvedor, criar uma aplicação e incluir a API **Extratos**. O portal
   entrega as credenciais de homologação: `developer_application_key`,
   `client_id` e `client_secret`.
3. **Homologação (teste, sem dinheiro real):** preencher o `.env` com
   `BB_AMBIENTE=homologacao`, as três credenciais e a agência e conta de teste
   da documentação do sandbox. Rodar
   `python scripts/importacao/api_bb_extrato.py --verificar`.
4. **Certificado e-CNPJ A1:** produção exige mTLS. Converter o `.pfx` para
   PEM, guardando os arquivos fora dos repositórios, por exemplo em
   `SirFisher/_credenciais/bb/`:

   ```powershell
   openssl pkcs12 -in empresa.pfx -clcerts -nokeys -out certificado.pem
   openssl pkcs12 -in empresa.pfx -nocerts -out chave.pem
   ```

   O segundo comando pede uma senha nova para proteger a chave; ela vai em
   `BB_CHAVE_SENHA`. O `openssl` vem com o Git for Windows.
5. **Produção:** no portal, pedir a passagem da aplicação para produção e
   enviar a parte pública do certificado quando o portal solicitar. O usuário
   master da conta autoriza o aplicativo no internet banking PJ; o gerente ou
   o próprio portal indicam o menu.
6. Trocar o `.env` para `BB_AMBIENTE=producao`, com as credenciais de
   produção, `BB_AGENCIA`, `BB_CONTA`, `BB_CERTIFICADO` e `BB_CHAVE_PRIVADA`.
   Rodar `--verificar` e depois baixar um mês já importado por CSV:
   `python scripts/importacao/api_bb_extrato.py --de 2026-09-01 --ate 2026-09-30`.

## Variáveis do `.env`

| Variável | Uso |
|---|---|
| `STONE_CONCILIACAO_API_KEY` | chave da API de Conciliação |
| `STONE_STONECODES` | opcional; lista separada por vírgula |
| `STONE_WEBHOOK_TOKEN` | token da URL do webhook Pix; o mesmo valor fica nos segredos da Edge Function |
| `SUPABASE_URL` | já existente; base da URL do webhook |
| `SAIPOS_API_TOKEN` | token da API de Dados Saipos, sem o prefixo `Bearer` |
| `BB_AMBIENTE` | `homologacao` (padrão) ou `producao` |
| `BB_CLIENT_ID`, `BB_CLIENT_SECRET` | credenciais OAuth da aplicação |
| `BB_DEVELOPER_APP_KEY` | `developer_application_key` da aplicação |
| `BB_AGENCIA`, `BB_CONTA` | só dígitos, sem o dígito verificador |
| `BB_CERTIFICADO`, `BB_CHAVE_PRIVADA` | PEM do e-CNPJ; caminho relativo parte de `gestao/` |
| `BB_CHAVE_SENHA` | opcional; senha do PEM da chave |
| `BB_URL_TOKEN`, `BB_URL_API`, `BB_PARAMETRO_APP_KEY` | opcionais; só se o portal mostrar valores diferentes dos padrões |

Caminhos relativos permitem o mesmo `.env` nos dois PCs do OneDrive.

## Pontos a confirmar quando houver acesso

A documentação da API Extratos fica atrás do login do portal. O baixador
usa a especificação conhecida, com os pontos abaixo configuráveis:

- servidores: `oauth.hm.bb.com.br` e `api.hm.bb.com.br/extratos/v1` em
  homologação; `oauth.bb.com.br` e `api-extratos.bb.com.br/extratos/v1` em
  produção;
- escopo `extrato-info`; chave do aplicativo no parâmetro `gw-dev-app-key`;
- datas `DDMMAAAA` sem zero à esquerda no dia; até 200 registros por página;
- a resposta traz as linhas `Saldo Anterior` e `S A L D O`? Se trouxer, o
  script confere o saldo como o importador do CSV; se não, avisa.

## Stone: o que o arquivo de conciliação provou (20/10/2026)

Comparação de setembro inteiro e de 1 a 18/10 com o que o CSV já tinha
gravado, somente leitura:

- **Recebíveis:** as 1.509 linhas de setembro (1.508 parcelas de venda e um
  cancelamento) e as 905 de outubro montadas pela API já estão no painel com
  a mesma chave. As 21 colunas são iguais; só o `ultimo_status` difere em 260
  parcelas, em que a API diz "Pago" e o CSV, exportado antes, "Aberto".
  Nenhuma view lê esse campo.
- **Regras do CSV reproduzidas:** STONE ID = `AcquirerTransactionKey`;
  `data_venda` = `CaptureLocalDateTime`; vencimento = `PaymentDate`, ou a
  previsão enquanto não pago; `desconto_mdr` = líquido − bruto; antecipação
  e unificado zero; `entradas_brutas` = bruto. Cancelamento: valores
  negativos, data do evento, vencimento da cobrança e "Cancelamento Parcial"
  quando a devolução é menor que a venda.
- **Horário:** o CSV grava a hora da autorização; `CaptureLocalDateTime` vem
  de 0 a 3 s depois (setembro a outubro/2026). Na virada do minuto, a venda
  do CSV fica um minuto antes; a conferência de vendas aceita essa diferença.
- **Códigos:** BrandId 1 Visa, 2 MasterCard, 3 AmericanExpress, 5 UnionPay
  (conferido com o CSV em 23/10/2026), 171 Elo;
  AccountType 1 Debito, 2 Credito, 3 Debito Pre-pago, 4 Credito Pre-pago.
  Código novo, chargeback e cancelamento de venda parcelada recusam a carga
  inteira, com orientação de usar o CSV do dia, até ganharem regra conferida.
- **Por que só recebíveis:** o arquivo traz apenas cartão. As 528 vendas Pix
  e as 26 Voucher de setembro não aparecem. Pix e Voucher não geram recebível
  na Stone, então o importador de recebíveis cobre 100% do CSV de
  recebíveis. Gravar só as vendas com cartão faria `corte_venda`, que usa a
  maior `data_venda` de `raw_stone_vendas`, tratar dias sem Pix como
  fechados. `recebimento_projetado` já corta na maior `data_venda` de
  `raw_stone_recebiveis`, então recebíveis em dia só melhoram a projeção.
- **Pix pela API:** existe um arquivo próprio
  (`POST .../conciliation-file/pix/{data}`), mas a Stone entrega o link por
  webhook. Exige um endereço público para receber o aviso, por exemplo uma
  Edge Function. Fica para uma decisão futura.

## Fase 2: gravar no painel

Regra comum: a API entra pelas mesmas tabelas e pelo mesmo
`importar_registros`, com `on conflict do nothing`. Uma linha que já veio por
CSV não pode entrar de novo pela API.

- **Extrato BB:** `dedup_hash` = md5 de
  `data|lançamento|documento|valor|detalhes`. Hipótese: `textoDescricaoHistorico`,
  `numeroDocumento` e `textoInformacaoComplementar` correspondem a
  Lançamento, N° documento e Detalhes. Se forem idênticos, CSV e API geram o
  mesmo hash e convivem. Se não, definir uma data de virada: CSV até ela, API
  depois, e o importador de CSV recusa linhas posteriores.
- **Prova antes de gravar:** baixar um mês já importado, gerar as linhas da
  API em `--dry-run` e comparar chaves, quantidades e totais com o banco.
  Só gravar quando o mês bater sem diferença.
- **Agendamento:** decidido em 20/10/2026, GitHub Actions (ver "Rotina diária").

## Saipos: vendas do PDV e conciliação com a Stone (21/10/2026)

API de Dados Saipos (`https://data.saipos.io/v1`, `Authorization: Bearer`),
token da loja 37889047000168 (`id_store` 49581), contratado a R$ 59,90/mês.
Importador `scripts/importacao/api_saipos_vendas.py`; tabelas
`saipos_venda`/`saipos_pagamento` (migration `20261021000000`).

- Consulta `search_sales` por `shift_date`, **um dia por vez**: 15 dias numa
  consulta deram HTTP 504 (pool da Saipos). 502/503/504 e falhas de rede
  têm até 4 novas tentativas (5, 20, 60 e 120 s); falha em dia anterior ao último vira aviso, pois a rodada seguinte refaz o período. Limite: 500 consultas em 5 min.
- Pagamento conciliável = transação da maquininha integrada (origem `pos`)
  ou forma lançada no caixa sem transação igual (origem `forma`). A forma
  que repete a transação da maquininha não entra duas vezes. Dinheiro,
  Fiado e vendas canceladas ficam fora.
- Casamento com `raw_stone_vendas` (Praia e Pix, status `Aprovada`):
  1. `authorization_code` = `stone_id` (cartão na maquininha);
  2. Pix na maquininha: mesmo valor e categoria, até 5 min (o código "A..."
     da Saipos não é o E2E da Stone);
  3. lançamento no caixa: valor com tolerância de R$ 0,05 (conta dividida
     gera centavos de diferença), até 30 min, mesma categoria de
     preferência; aceita outra categoria se não houver par;
  4. ainda sem par: a única venda Stone de mesmo valor e categoria nas 3 h
     anteriores (`janela_ampla`, conta fechada depois da cobrança) ou a soma
     de 2 a 4 vendas Stone em 10 min (`soma`, vale em vários cartões; as
     demais ficam em `stone_ids_extra`).
- Forma do caixa que repete a transação da maquininha (mesma categoria, até
  R$ 0,05 de diferença) e pagamentos de R$ 0,00 não entram.
- Dia de comparação = data do turno; o turno Manhã começa às 08:00, então a
  venda Stone da madrugada vai para o dia anterior.
- Cada rodada baixa os últimos 7 dias e refaz o casamento do período, pois
  as vendas Stone podem chegar depois (`--so-conciliar` refaz sem consultar).
- Prova 12–18/10/2026: 518 de 529 vendas Stone casadas; cartão na
  maquininha 338/338 pelo código, com valores idênticos.
- Carga 01/09–20/10/2026 com as regras acima: 3.452 pagamentos Saipos de
  cartão/Pix; 23 sem par na Stone (R$ 1.494,82), quase todos "Pagamento não
  cadastrado" e valores redondos. Stone sem Saipos: 32.
- Painel: Conciliação > "Saipos × Stone" (`app_conciliacao_saipos_dia` e
  `app_conciliacao_saipos_pendencia`). Rotina: `importacao-saipos.yml`,
  05:30 de Fortaleza; exige o secret `SAIPOS_API_TOKEN` no GitHub.

## Saipos: rotina Cancelamentos (21/10/2026)

O mesmo importador baixa `sales_items` e `sales_status_histories` de cada dia
e grava em `saipos_cancelamento` e `saipos_lancamento_resumo` (migration
`20261021030000`). Regras em `scripts/importacao/saipos_cancelamentos.py`:

- **Não é cancelamento:** item apagado com `id_sale_to` (troca de mesa).
- **Correção:** item apagado e o mesmo produto relançado na mesma mesa logo
  em seguida; zero ponto, sem justificativa.
- **`done_at` não é preparo:** é o fechamento da mesa. "Provavelmente
  servido" = bebida cancelada 10+ min ou comida 40+ min após lançar.
- **Mesa trocada:** pagamento e fechamento vêm da venda de destino.
- **Pontos do item:** provavelmente servido 2; depois de começar a pagar 2;
  até 15 min antes de pagar 1; 60+ min após lançar 1; mesa paga em dinheiro
  1; sem motivo 1. Justificativa obrigatória com 3+ pontos ou R$ 100+.
- **Mesa inteira cancelada:** justificativa quando aberta há 30+ min ou com
  R$ 100+. Mesa sem itens (aberta por engano) é ignorada.
- Análise de 01/09–20/10/2026: 228 cancelamentos (R$ 6.221,30, 2,1% do
  lançado), 43 exigindo justificativa (R$ 1.484,50). 234 de 239 itens foram
  cancelados no login "Caixa" e nenhum teve autorização registrada.

Página `cancelamentos.html` (Rotinas): gerente justifica
(`justificar_cancelamento`); admin e sócio marcam procedente ou suspeito
(`revisar_cancelamento`), o que trava a justificativa. A seção "Fora da
curva" compara a taxa por dia, hora, turno, dia da semana e funcionário.
O importador só atualiza os dados Saipos; justificativa e revisão nunca são
sobrescritas, e um caso já tratado não é apagado.
A rotina conta a partir de 21/10/2026: casos anteriores levam a marcação
"Histórico anterior à rotina" (coluna `marcacao`, migration
`20261021040000`), ficam fora das pendências e aparecem no filtro Histórico.

## Segurança

- Chaves e senhas ficam só no `.env` ignorado; o certificado fica fora dos
  repositórios.
- As mensagens de erro citam o status HTTP e uma dica, nunca o corpo da
  resposta nem os cabeçalhos enviados.
- Os arquivos baixados têm dados financeiros brutos e ficam em
  `scripts/importacao/api-*/`, ignorada pelo Git.

## Fontes

- Saipos, API de Dados: <https://saipos-data-api.readme.io/reference/introducao>

- Stone, acesso de cliente à Conciliação:
  <https://conciliacao.stone.com.br/reference/overview-da-api-cliente-stone>
- Stone, layout 2.4 completo:
  <https://conciliacao.stone.com.br/reference/copy-of-arquivo-completo-layout-24>
- Stone, limites: <https://conciliacao.stone.com.br/reference/rate-limit>
- Stone, erros: <https://conciliacao.stone.com.br/reference/mensagens-de-erro>
- BB, apresentação da API Extratos:
  <https://www.bb.com.br/site/developers/bb-como-servico/api-extratos/>
