# Integração por API: Stone e Banco do Brasil

Objetivo: trocar a exportação manual de CSV por download automático, sem
mudar as tabelas nem as regras do painel.

## Situação em 20/10/2026

| Fonte no painel | API | Estado |
|---|---|---|
| Vendas Stone (`raw_stone_vendas`) | Stone, API de Conciliação | baixador pronto; falta a chave |
| Recebíveis Stone (`raw_stone_recebiveis`) | Stone, API de Conciliação (mesmo arquivo) | baixador pronto; falta a chave |
| Extrato BB (`raw_bb`) | BB, API Extratos | baixador pronto; faltam contrato, aplicativo e certificado |
| Extrato Stone (`raw_stone_extrato`) | Stone, API da Conta Stone | sem acesso de cliente; a Stone pede parceria comercial |

Fase 1, entregue: `scripts/importacao/api_stone_conciliacao.py` e
`scripts/importacao/api_bb_extrato.py` **só baixam e conferem** os arquivos.
Eles salvam em `scripts/importacao/api-*/`, pasta ignorada pelo Git, e não
gravam no banco. Os testes sem rede ficam em `scripts/ci/test_api_bancos.py`.

Fase 2, pendente: gravar no painel. Depende de arquivos reais, porque o
formato das APIs é diferente do CSV (ver "Fase 2" abaixo).

## Passo a passo do proprietário

### Stone: API de Conciliação

1. No computador, entrar em `conta.stone.com.br` como **titular** e trocar
   para a conta da empresa dona dos stonecodes. A Stone documenta este passo
   só na web, não no app.
2. Clicar no nome, no canto superior direito, e abrir **Perfil > Acesso e
   Segurança > Chaves de autenticação > Criar Chave**. Escolher **"API de
   Conciliação Stone"**.
   Em 20/10/2026, o perfil pessoal do titular mostrava só "Segurança" e
   "Aplicativos conectados" nesse grupo. Se a opção não aparecer dentro da
   conta da empresa, pedir ao Atendimento da Stone que a habilite.
3. Copiar a chave e colar no `gestao/.env`, sem enviá-la por chat:
   `STONE_CONCILIACAO_API_KEY=<chave>`.
4. Testar: `python scripts/importacao/api_stone_conciliacao.py --verificar`.
5. Baixar um mês que já foi importado por CSV, para a comparação da fase 2:
   `python scripts/importacao/api_stone_conciliacao.py --de 2026-09-01 --ate 2026-09-30`.

A chave vale para os stonecodes do CNPJ que a criou. Um stonecode de outro
CNPJ responde HTTP 403 e precisa de uma chave criada pelo titular daquele
CNPJ. Sem `--stonecode` nem `STONE_STONECODES`, o script lê os stonecodes
ativos de `stone_conta`, somente leitura, com o `DATABASE_URL` do `.env`.

Limites documentados pela Stone: o arquivo de um dia sai no dia seguinte a
partir das 4h (HTTP 503 antes disso), e cada combinação de stonecode e dia
aceita 7 consultas por hora (HTTP 429). O script não baixa de novo o que já
está na pasta, salvo com `--sobrescrever`.

### Stone: extrato da Conta Stone

A API da Conta Stone (saldo e extrato) é liberada pelo time comercial, por
parceria. Pergunta para a Stone: "a API da Conta Stone libera o extrato para
a própria empresa, sem ser parceira?". Enquanto isso, o CSV continua.

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

Na Stone, conferir no primeiro arquivo real se o `ReferenceDate` do cabeçalho
segue `AAAAMMDD` e se o layout 2.4 traz todos os campos usados abaixo.

## Fase 2: gravar no painel

Regra comum: a API entra pelas mesmas tabelas e pelo mesmo
`importar_registros`, com `on conflict do nothing`. Uma linha que já veio por
CSV não pode entrar de novo pela API.

- **Vendas Stone:** a chave é `stone_id`. Hipótese a provar: o STONE ID do
  CSV é o `AcquirerTransactionKey` do XML. O XML traz códigos (`BrandId`,
  `AccountType`, `EntryMode`, `PoiType`) onde o CSV traz textos (bandeira,
  produto, meio de captura, status); o mapeamento precisa reproduzir os
  textos que as views usam.
- **Recebíveis Stone:** a chave é `(stone_id, n_parcela, categoria)`.
  Parcelas vêm de `Installments`; cancelamentos e chargebacks viram
  categorias próprias. Conferir valores bruto e líquido por parcela.
- **Extrato BB:** `dedup_hash` = md5 de
  `data|lançamento|documento|valor|detalhes`. Hipótese: `textoDescricaoHistorico`,
  `numeroDocumento` e `textoInformacaoComplementar` correspondem a
  Lançamento, N° documento e Detalhes. Se forem idênticos, CSV e API geram o
  mesmo hash e convivem. Se não, definir uma data de virada: CSV até ela, API
  depois, e o importador de CSV recusa linhas posteriores.
- **Prova antes de gravar:** baixar um mês já importado, gerar as linhas da
  API em `--dry-run` e comparar chaves, quantidades e totais com o banco.
  Só gravar quando o mês bater sem diferença.
- **Agendamento** (decidir depois da prova): Agendador de Tarefas do Windows
  num dos PCs (depende do PC ligado), GitHub Actions com segredos (roda na
  nuvem, mas guarda `DATABASE_URL`, chaves e certificado no GitHub) ou Edge
  Function do Supabase com `pg_cron`. Cada opção exige decisão explícita
  sobre onde ficam os segredos.

## Segurança

- Chaves e senhas ficam só no `.env` ignorado; o certificado fica fora dos
  repositórios.
- As mensagens de erro citam o status HTTP e uma dica, nunca o corpo da
  resposta nem os cabeçalhos enviados.
- Os arquivos baixados têm dados financeiros brutos e ficam em
  `scripts/importacao/api-*/`, ignorada pelo Git.

## Fontes

- Stone, acesso de cliente à Conciliação:
  <https://conciliacao.stone.com.br/reference/overview-da-api-cliente-stone>
- Stone, layout 2.4 completo:
  <https://conciliacao.stone.com.br/reference/copy-of-arquivo-completo-layout-24>
- Stone, limites: <https://conciliacao.stone.com.br/reference/rate-limit>
- Stone, erros: <https://conciliacao.stone.com.br/reference/mensagens-de-erro>
- BB, apresentação da API Extratos:
  <https://www.bb.com.br/site/developers/bb-como-servico/api-extratos/>
