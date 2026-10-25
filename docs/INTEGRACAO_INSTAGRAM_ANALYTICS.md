# Instagram: leitura de conteudo, insights e reservas

Conferido em 25/10/2026 no Windows/PowerShell do workspace SirFisher.
A conta autenticada e `@sirfisherfc`, ID `17841439937145607`. A integracao
usa a API oficial da Meta v26.0 e o mesmo app/token da rotina do Perfil da
Empresa. As quatro CLIs usadas pelo proprietario fizeram leituras reais.

## O que existia e o que foi comprovado

| Item | Documentado/configurado antes | Prova desta entrega |
| --- | --- | --- |
| Rotina Instagram para o Google | `scripts/gbp/gbp.py`, `META_IG_TOKEN` e leitura de fotos pela Graph v23.0 | A descoberta por `me/accounts` encontrou a conta correta. O registro privado tambem contem execucao historica em 28/09. O comando que pode publicar no Google ficou fora do MCP. |
| Modalidade de autenticacao | Token de usuario do sistema do Business Manager, com Pagina vinculada | `debug_token` retornou `SYSTEM_USER`, `is_valid=true`, `expires_at=0` e `data_access_expires_at=0`. A descoberta da conta pela familia Facebook Login funcionou. |
| Insights | A rotina anterior nao os consultava | Leituras reais v26.0 confirmaram nove metricas da conta, sete metricas de publicacoes e quatro de um Story. |
| Stories | Sem ferramenta anterior | O endpoint retornou oito Stories disponiveis no instante da coleta. |
| MCP local | Servidores existentes dos outros sistemas | Sete ferramentas novas de leitura, sem substituir os servidores existentes. O SDK oficial `mcp 2.3.0` e o Python privado do Analytics ja estavam instalados. |

O token privado permanece no ambiente ou em `gestao/.env`, pelo carregador
canonico `credencial()` do GBP. O ID opcional `META_IG_USER_ID` e validado
contra o username; a integracao interrompe a leitura se a identidade divergir.
Ela tambem interrompe a descoberta incompleta ou ambigua, sem escolher a
primeira conta disponivel.

O token existente tem permissoes de escrita adicionais. Elas foram
preservadas para os usos existentes. O novo servidor aceita somente GET,
rotas fixas e IDs de midia confirmados para a conta; nao oferece ferramenta
generica de execucao, campos/host livres, publicacao, exclusao, anuncios,
Direct ou conteudo individual de comentarios. As contagens de comentarios
sao metricas agregadas. As permissoes de leitura confirmadas foram
`instagram_basic`, `instagram_manage_insights`, `pages_show_list` e
`pages_read_engagement`.

Nenhuma credencial foi copiada para as configuracoes dos clientes ou para
arquivos versionados. Os parametros de autenticacao e as URLs
`paging.next/previous` sao removidos antes do cache e do retorno. A paginacao
usa cursores e host fixo; redirecionamentos HTTP sao bloqueados.

## Ferramentas disponiveis

Servidor: `instagram_analytics`. Contrato compartilhado pelas quatro IAs:

| Ferramenta | Funcao e limites |
| --- | --- |
| `instagram_identity(refresh=false)` | Confirma conta, ID, nome e contagens atuais. `refresh=true` faz nova leitura autenticada; o padrao usa cache de 15 minutos. |
| `instagram_permissions()` | Confere os quatro escopos de leitura e informa a existencia de privilegios adicionais, sem expor o token. |
| `instagram_media(days=30, max_pages=3, page_size=25, end_date=null)` | Lista ID, formato, legenda, data e permalink. Ate 30 dias, quatro paginas e 50 itens/pagina; marca truncamento. `end_date` e o ultimo dia incluido. |
| `instagram_account_insights(days=30, end_date=null, metrics=null)` | Consulta metricas em `period=day`, `metric_type=total_value`, no periodo informado. Sem data explicita, termina anteontem em Fortaleza. |
| `instagram_media_insights(media_id, metrics=null)` | Consulta somente um ID proprio previamente listado. Preserva `period=lifetime` e o instante de coleta; nao inventa uma serie historica. |
| `instagram_stories()` | Lista os Stories que a API disponibiliza agora, em ate duas paginas. Permite depois consultar seus insights pelo ID. |
| `instagram_metric_catalog()` | Mostra nomes aceitos, definicoes e limites, sem chamada de rede. |

As anotacoes MCP sao `readOnlyHint=true`, `destructiveHint=false` e
`idempotentHint=true`. A restricao efetiva tambem esta no transporte e no
contrato de argumentos. As permissoes especificas do Antigravity CLI cobrem
apenas esses sete nomes.

O cache SQLite fica em `%LOCALAPPDATA%/SirFisher/instagram-analytics/`, fora
do OneDrive e do Git. Os quatro clientes reutilizam o mesmo cache neste PC.
Cada registro inclui o instante da coleta. A propriedade da midia e
separada por versao, token e ID confirmado da conta. Trocar a identidade nao
autoriza consultar IDs guardados pela identidade anterior.

Limites por operacao: 60 leituras HTTP, 30 dias e paginacao limitada. O
cache de sucesso dura 15 minutos para identidade, uma hora para permissoes,
cinco minutos para publicacoes, um minuto para Stories e seis horas para
insights. Uma metrica indisponivel tem status e motivo proprios; um valor
numerico zero permanece disponivel. Datas, definicoes e `period` da Meta
ficam na resposta. Alcances de posts nao devem ser somados como pessoas unicas.

## Estado por cliente

| Cliente instalado | Configuracao local | Leitura autenticada | Interface ja aberta |
| --- | --- | --- | --- |
| Codex CLI `0.164.0-alpha.11.1`, extensao `26.1021.22027` | `~/.codex/config.toml` | `instagram_identity(refresh=true)`: conta correta, duas leituras HTTP, cache=false e saida 0 | A configuracao e compartilhada com a extensao. Carregar em nova sessao; GUI nao foi reiniciada nem validada nesta entrega. |
| Claude Code `2.1.310` da extensao; nativo PATH `2.1.263` | `~/.claude.json`, escopo user-local | Mesmo teste real, em sessao efemera | Configuracao compartilhada; abrir nova conversa para carregar. GUI pendente de chamada propria. |
| Qwen Code CLI `0.23.0`, extensao `0.26.0` | `~/.qwen/settings.json` | Mesmo teste real em sessao isolada | Extensao instalada resolve esse mesmo arquivo; atualizar MCP/abrir nova sessao depois da tarefa ativa. GUI pendente de chamada propria. |
| Antigravity CLI `1.4.7`, extensao `1.9.0` | `~/.gemini/config/mcp_config.json` | Mesmo teste real, apos permitir exatamente os sete nomes no arquivo de permissoes do CLI | O README instalado da extensao aponta o mesmo arquivo MCP. A aprovacao do CLI nao comprova aprovacao na GUI; chamada propria pendente. |

Os servidores anteriores foram comparados antes/depois e permaneceram
iguais. Backups privados com ACL do usuario/SYSTEM ficam fora do Git. O
Claude atualizou seus caches normais durante a execucao isolada; esses
metadados ativos foram preservados. Nao houve mudanca de modelo, plano ou
reinicio de tarefas ativas. Os recibos por cliente e as instrucoes exatas
estao em `output/instagram-analytics-2026-10-25/clientes/`, na raiz do
workspace.
As sete regras especificas do Antigravity CLI ficam em
`~/.gemini/antigravity-cli/settings.json`, separadas da configuracao MCP.

## Como usar e manter

Comecar com `instagram_identity`, depois `instagram_media` ou
`instagram_stories`. Pedir insights apenas dos IDs listados. Para
revalidar a credencial, usar `instagram_identity(refresh=true)`.

O servidor stdio e `scripts/instagram_analytics/server.py`, iniciado pelo
Python privado ja configurado neste PC. Ele resolve o workspace por
`__file__`; nao depende de um `cwd` implicito. A dependencia do servidor
esta fixada em `scripts/instagram_analytics/requirements.txt`. Em outro PC,
usar um ambiente virtual local e essa dependencia, com o mesmo codigo e o
mesmo mecanismo privado de credencial. Reapontar os quatro clientes para o
Python e o script locais, preservando suas outras entradas MCP.

Para uma coleta agregada repetivel, na raiz de `gestao`:

```powershell
python scripts/instagram_analytics/coletar.py --dias 30 --ate 2026-10-22 --max-insights 10 --insights-stories 1
```

O cliente de coleta usa somente a biblioteca padrao do Python. Grava em
`gestao/tmp/instagram-analytics/`, ignorado pelo Git, reutilizando o cache.
Por padrao consulta ate dez publicacoes e um Story; os limites maximos sao
vinte e tres. Nao cria rotina recorrente. A coleta desta entrega foi salva
em `output/instagram-analytics-2026-10-25/coleta/`.

O token nao informa vencimento programado (`expires_at=0`). A autenticacao
atual dispensa renovacao OAuth rotineira. Se uma leitura real deixar de
funcionar, conferir o erro e os ativos/permissoes do mesmo app e usuario do
sistema antes de solicitar qualquer reconexao. Uma substituicao de token
deve usar o arquivo privado existente, sem passar pelo chat. O novo token
gera outro escopo de cache. Nao foi criado app, login ou intermediario novo.

## Dados iniciais e reservas

Periodo consolidado pedido: **23/09 a 22/10/2026**, 30 dias. As datas civis
enviadas usam `America/Fortaleza` (UTC-3); a resposta conserva os periodos e
definicoes da Meta. O endpoint Meta pode usar limites diarios proprios;
seus totais nao foram juntados por pessoa ou sessao aos dados do GA4/banco.
Os insights de publicacoes sao acumulados ate a coleta de 25/10, mesmo
quando o filtro de publicacao usa esse periodo fechado.

| Medida | Resultado e cobertura |
| --- | --- |
| Conta no instante da leitura | 41.144 seguidores e 304 publicacoes totais; nao e variacao de 30 dias. |
| Conta no periodo enviado a Meta | 8.221 contas alcancadas; 65.278 visualizacoes; 608 contas que interagiram; 1.322 interacoes; 109 salvamentos; 266 compartilhamentos; 131 toques nos links do perfil. Definicoes originais no JSON. |
| Publicacoes e Stories | Sete publicacoes no recorte consolidado, com insights de cada uma. Oito Stories disponiveis em 25/10 e insights de um deles. O arquivo inicial de janela movel, incluindo 25/10, tem cinco posts e outra cobertura. |
| GA4, site | 941 sessoes agrupadas como Instagram entre 2.419 sessoes do host, 38,9%. Instagram foi a maior origem agrupada. |
| GA4, portal | 115 sessoes Instagram entre 290 sessoes do host, 39,7%. Nao somar os dois hosts como sessoes unicas. |
| Conversao registrada | 17 das 28 reservas publicas criadas tinham UTM Instagram, 60,7%; duas reservas do painel ficaram separadas. |
| Etapas e comparecimento | GA4 contou 92 cliques em reserva, 17 `reservation_confirmed` e cinco `visit_realized` em sessoes Instagram. Na coorte operacional de 17 reservas criadas, havia quatro comparecimentos marcados, seis no-shows, uma cancelada e seis com visita futura ou sem status final no corte. |

Os 17 eventos GA4 e as 17 reservas com UTM concordam em quantidade; nao foi
feito cruzamento de identificadores individuais. Origem declarada pelo
cliente nao tem coluna propria detectada; campos livres nao foram lidos.
O token atual tem `ads_read`, mas a leitura real de `/me/adaccounts` e
`/me/assigned_ad_accounts` retornou HTTP 200 e listas vazias, inclusive
na chamada System User sem filtro adicional. Isso comprova a cobertura
desse acesso; nao estabelece a causa nem a inexistencia de anuncios.
Conversao atribuida pela Meta Ads, sua janela e seu modelo permanecem
indisponiveis. Para consulta-los, a conta de anuncios correta precisa estar
visivel ao acesso de leitura. Nao foi escolhido um ID legado por suposicao.
Os quatro GETs e seus limites estao no diretorio privado `meta-atribuicao`.
`sent` na fila CAPI e a finalizacao pelo worker apos HTTP 2xx;
nao representa sozinho credito publicitario ou deduplicacao confirmada
pela Meta.

As 28 linhas Meta Schedule do periodo tinham IDs esperados e nao havia
grupos duplicados na chave reserva/provedor/evento. Pixel e CAPI usam o
mesmo `sf-sched-<reserva>`. A constraint e o trigger foram conferidos por
consultas somente de leitura. Nao foram criadas reservas, notificacoes,
mensagens, eventos sinteticos de producao ou reenvios para testar.

O Instagram tem apoio dos dados como principal origem medida das reservas
publicas deste recorte. A chegada sem reserva e contatos concluidos fora
do portal ficam fora dessa conclusao. O periodo termina em 22/10; os
ajustes SEO de 25/10 precisam de dados posteriores para medir seu efeito.

## Acoes justificadas e limites de atribuicao

As 17 reservas Instagram tinham `utm_medium=social`, uma etiqueta geral
de bio/perfil e nenhuma campanha. Os dados atuais permitem analisar o
canal; a relacao com um post especifico exige identificador proprio no
link externo. A presenca de `fbclid/_fbc` e a midia `social` nao separam
automaticamente pago de organico.

Exemplo preparado para um Story com link direto ao portal, preservando
`ig/social`:

```text
https://reservas.sirfisher.com.br/?utm_source=ig&utm_medium=social&utm_campaign=reservas_2026_10&utm_content=story_20261025_reservas_01
```

Esse link e uma proposta para uma publicacao identificada. Nenhuma bio,
publicacao, anuncio ou link publico do Instagram foi alterado. Os links
internos continuam preservando a origem externa. Os 131 toques no perfil
nao foram usados como denominador das 17 reservas: as fontes e coberturas
nao estabelecem esse funil por individuo.

O valor legado de R$58/pessoa na Meta e uma estimativa; nao foi tratado
como receita, faturamento ou ROAS. Esta entrega preserva essa regra e
separa os ajustes tecnicos da medicao de qualquer decisao sobre valores.
Detalhes da auditoria e agregados sem nomes, telefones ou emails ficam em
`output/instagram-analytics-2026-10-25/atribuicao/`.

## Correcoes tecnicas publicadas

- Site `5988034`: o prazo de 90 dias agora e conferido no localStorage e no
  cookie. Uma copia sem timestamp valido, futura ou expirada e descartada;
  o cookie recebe o prazo restante. A navegacao interna conserva o instante
  e a origem externa. Os hashes de assets/CSP foram regenerados.
- Reservas `f92378d`: mesmo contrato de prazo, com testes de compatibilidade.
  A CAPI conserva o pais explicito em telefones internacionais e rejeita
  ocorrencia invalida, futura ou anterior a sete dias. O ID Schedule e a
  regra de valor legado foram preservados. `bf2f08d` registra a implantacao.
- Somente `send-openai-ads-conversions` foi implantada no Supabase portal:
  versao 21 para 22, `ACTIVE`, com `verify_jwt=false` e a autenticacao interna
  existentes preservadas. Os tres modulos baixados depois da implantacao
  coincidiram com o codigo revisado. Nenhuma migration, segredo ou rotina
  agendada foi alterada. A auditoria nao invocou o worker.

As falhas de telefone/data foram reproduzidas com fixtures. As consultas
agregadas nao encontraram casos afetados no historico examinado. As
correcoes valem para o processamento futuro; nao reatribuem reservas antigas.

## Arquivos e configuracoes alterados

- Gestao: `scripts/instagram_analytics/client.py`, `server.py`, `coletar.py`,
  `test_client.py` e `requirements.txt`; este guia; `AGENTS.md`,
  `docs/CANAL_IA.md`, as duas copias em `docs/workspace/` e o job offline de
  `.github/workflows/quality.yml`. Os arquivos `AGENTS.md` e `README.md` da
  raiz foram sincronizados com suas copias versionadas.
- Site: `assets/js/atribuicao.js`, teste e README de analytics. As 13 paginas
  consumidoras receberam somente os hashes novos de asset/CSP.
- Reservas: `assets/js/attribution.js`, referencias de cache em
  `reservations.js`/`reveillon.js` e seus HTMLs; `meta-event.ts` e a chamada
  dos helpers no worker; testes offline e `docs/medicao-google.md`.
- Fora do Git: as quatro entradas MCP user-local e as sete autorizacoes
  especificas do Antigravity CLI. Backups, cache e dados coletados
  permanecem privados. Nenhum `.mcp.json` dos repositorios foi substituido.

## Validacoes e referencias

- Vinte testes offline cobrem identidade estrita, propriedade por conta,
  cache, GET, bloqueio de rotas/auth livres, redacao de erros, limites e
  diferenca entre zero e ausencia de dados.
- Oito testes independentes de seguranca passaram sem rede nem credencial
  real. O initialize/list_tools do SDK confirmou sete ferramentas de leitura.
- Os sete handlers tambem foram executados pelo SDK, reutilizando o cache.
  A ferramenta inexistente `instagram_publish` foi rejeitada, com zero HTTP
  confirmado pelo contador instrumentado no processo de teste.
- As quatro CLIs executaram `instagram_identity(refresh=true)`, com duas
  leituras HTTP reais, `cache=false`, conta correta e saida 0. Interfaces
  graficas continuam com validacao propria pendente em nova sessao.
- Site: 113 testes Deno e quatro verificadores aprovados. Reservas: 32
  testes, verificacao TypeScript e navegador offline aprovados; Pages passou.
- Meta API v26.0: [SDK oficial](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/apiconfig.py),
  [IGUser](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/iguser.py),
  [IGMedia](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/igmedia.py) e
  [colecao oficial Facebook Login](https://www.postman.com/meta/instagram/folder/u4g5a2a/instagram-api-with-facebook-login).
  As paginas canonicas da plataforma retornaram erro/429 durante a pesquisa;
  o SDK e as chamadas reais sustentam o contrato aqui implementado.
- Clientes: [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp),
  [Claude Code MCP](https://code.claude.com/docs/en/mcp),
  [Qwen Code MCP](https://qwenlm.github.io/qwen-code-docs/en/users/features/mcp/) e
  [Antigravity MCP](https://antigravity.google/docs/mcp). Os caminhos das
  extensoes tambem foram conferidos nos arquivos instalados.

Esta integracao nao usa novas consultas Semrush, Composio, cobranca,
upgrade, agendamento ou escrita no Instagram. Os relatorios privados nao
sao publicados pelo GitHub Pages.
