# Integração por API: Stone e Banco do Brasil

Objetivo: trocar a exportação manual de CSV por download automático, sem
mudar as tabelas nem as regras do painel.

## Diagnóstico e consulta única em 22/10/2026

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

`.github/workflows/importacao-diaria.yml` roda às 04:43 e às 09:43 de
Fortaleza e reprocessa os últimos 3 dias, ou quantos forem pedidos na
execução manual (Actions > Importação diária por API > Run workflow). A
carga não duplica, então um dia que falhou entra na rodada seguinte. Não
roda à meia-noite porque o arquivo de um dia só existe a partir das 4h do
dia seguinte.

O repositório é público, então o log do Actions também é. A rotina escreve
no log só as linhas de erro; o detalhe fica em `integracao_execucao`.

Segredos em Settings > Secrets and variables > Actions, com os valores do
`gestao/.env`: `DATABASE_URL`, `SUPABASE_URL` e `STONE_CONCILIACAO_API_KEY`.
Sem eles, o primeiro passo da rotina falha avisando qual falta.

## Pix pelo extrato (caminho preferido)

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

## Pix pela API de Conciliação (alternativa, webhook)

1. Publicar `supabase/functions/stone-webhook` com `verify_jwt = false` e
   cadastrar o segredo `STONE_WEBHOOK_TOKEN` na função. O mesmo valor vai no
   `gestao/.env`. Sem o segredo, a função recusa tudo com 401.
2. `python scripts/importacao/api_stone_pix.py --cadastrar-webhook`. A Stone
   testa a URL antes de salvar.
3. `python scripts/importacao/api_stone_pix.py --solicitar --de 2026-09-01 --ate 2026-09-07`
   e depois `--analisar` no mesmo período. A análise diz qual coluna casa com
   o STONE ID das vendas Pix do CSV (esperado: `pix_transaction__e2e_id`,
   formato `E` + 31 caracteres), se o valor vem em reais ou centavos, o fuso de
   `created_at` e se o terminal bate.
4. Com o mapeamento confirmado, criar `api_stone_vendas.py`: grava cartão e
   Pix de um dia só quando os dois arquivos daquele dia chegaram, para
   `corte_venda` não avançar com dia incompleto. Entrar na rotina diária.

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
- **Códigos:** BrandId 1 Visa, 2 MasterCard, 3 AmericanExpress, 171 Elo;
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
