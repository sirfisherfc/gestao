# Marketing, conteúdo e reservas

Entrega de 02/11/2026. Painel privado:
<https://admin.sirfisher.com.br/marketing.html>. Entrada também em Rotinas.
Gerador privado de links:
<https://reservas.sirfisher.com.br/admin/links-marketing.html>.

## Resultado e evidência

| Frente | Estado | Evidência | Pendência |
| --- | --- | --- | --- |
| Instagram | funcionando e testado | Identidade real `@sirfisherfc`; seis publicações, dois Stories e agregados de 02/10 a 31/10, com período anterior de 02/09 a 01/10. Snapshots gravados no portal e relidos. | Incorporar a coleta contínua ao executor existente e validar suas credenciais naquele ambiente. Stories anteriores à primeira coleta já expirados continuam indisponíveis. |
| Conteúdo, reservas e comparecimento | funcionando e testado | Gerador de links publicado; preservação de UTM e campanha nos dois sites; fluxo até o RPC com payload simulado; agregado real do portal consultado sob o papel autorizado. Pixel/CAPI preservados. | Usar links aprovados nas próximas publicações para acumular reservas com identificador de conteúdo. Sem reatribuição de dados antigos. |
| Anúncios | pendente de acesso ou decisão | DeathStar tem `ads_read`; listagens de contas HTTP 200 vazias. GET direto à conta `1004410887092327`, informada pelo proprietário, retornou HTTP 403/código 200. Painel mostra indisponibilidade. | Atribuir essa conta ao usuário do sistema do DeathStar com acesso de leitura e repetir a coleta. |
| Publicação aprovada | preparado aguardando validação | Rascunho, prévia, revisão, data e aprovação pelo UUID privado do proprietário; revisão concorrente rejeitada; hash do arquivo; claim atômico, recibos e confirmação por GET. | Nenhum conteúdo/data foi aprovado nesta conversa. Validar o primeiro envio aprovado e incorporar o executor à rotina existente. Sem essa incorporação, a fila exige execução pelo procedimento abaixo. |
| Comentários | funcionando e testado | Três comentários próprios coletados sem nomes de autores; Instagram e Página consultados; revisão humana persistida com nova leitura em transação revertida; interface testada. | Facebook limitado às primeiras 20 publicações e primeira página de até 100 comentários por publicação; subthreads/respostas ficam fora. Rotina contínua depende da incorporação do coletor. |
| Fotos Google | preparado aguardando validação | OAuth renovou e leu Sir Fisher; três fotos próprias preparadas; uma parecida com foto da ficha; arquivos privados e snapshot com dimensões, SHA256 e qualidade técnica. | Proprietário precisa revisar os dois materiais restantes, confirmar direitos/qualidade e aprovar data. Nenhuma foto foi publicada. |

O aplicativo real é DeathStar, ID `224912007567636`, com token `SYSTEM_USER`
válido. A Página Sir Fisher `107690041045934` está vinculada ao Instagram
`17841439937145607`. As chamadas confirmaram permissões de insights,
publicação Instagram/Facebook e comentários. O limite retornado pelo
Instagram nesta auditoria foi 0/100 publicações por 86.400 segundos.
O executor consulta a cota novamente antes de enviar. O MCP
`instagram_analytics` conserva suas ferramentas de leitura.

O Direct continua no Jotform; comentários Jotform permanecem desligados e
o piloto próprio permanece pausado. Esta entrega preserva suas configurações.
Nenhuma campanha, orçamento, evento de conversão ou mensagem foi alterado.

## Operação

1. Entre no painel com a conta Google autorizada. Em Marketing, consulte
   1 a 30 dias. A primeira janela consolidada termina em 31/10. O painel
   mostra a data do registro e os instantes reais das leituras, inclusive
   quando o cliente reutiliza cache. A comparação exige janelas de mesmo
   tamanho e mesma versão da API. Reels incluem tempo assistido quando
   disponível; a resposta original conserva definição e unidade.
2. No gerador privado, informe conteúdo/campanha e confira a prévia. Use
   `utm_content=ig_<media-id>` ou `fb_<post-id>` para conteúdo identificado.
   Links preparados antes da publicação podem usar um ID editorial estável;
   registre esse mesmo ID junto da publicação. Campanha paga usa
   `campaign_id`, `ad_group_id` e `ad_id` corretos. A equipe copia o link
   para materiais previamente aprovados. A navegação conserva o toque;
   uma chegada externa nova retira os identificadores anteriores ausentes.
3. Prepare a publicação em Marketing, confira a prévia e salve. Marque
   direitos e qualidade somente após conferir o material. Instagram aceita
   IMAGE/REELS/STORIES neste fluxo; Facebook, TEXT/PHOTO. Fotos Google usam
   PHOTO e o ID da foto própria. Carrosséis e outros formatos de publicação
   ficam fora desta primeira entrega; fotos de carrosséis próprios podem
   ser preparadas para o Google pela ferramenta existente.
4. Envie o rascunho à revisão. Antes de aprovar mídia, execute a validação
   privada abaixo e recarregue o painel. O proprietário configurado pode
   aprovar a revisão exibida, o arquivo validado e a data em Fortaleza.
   Salvar uma edição retira a aprovação e a validação anteriores. Para
   imagem Instagram, o fluxo valida JPEG até 8 MB; Google, JPEG/PNG,
   10 KB a 5 MB, menor lado de pelo menos 400 px. O fluxo local aceita
   arquivos de até 100 MB. Vídeos exigem revisão técnica do formato antes
   da aprovação; a Meta valida o contêiner. O primeiro envio real por
   formato ainda precisa ser conferido. As URLs de mídia Instagram/Facebook
   precisam apontar para arquivos próprios no site Sir Fisher.
5. Execute a prévia da fila e, no horário aprovado, seu envio. A janela
   aceita até uma hora após a data; um item atrasado exige editar a data,
   revisar e aprovar novamente. Conteúdo aprovado continua no banco quando
   o executor está desligado; a programação isolada não dispara o envio.
   O estado incerto bloqueia repetição automática. Reconcile os IDs antes
   de preparar qualquer reenvio. Confirmar pela API Google registra a
   criação; a exibição pública ainda depende da revisão do Google.
6. Em Comentários, classifique pergunta/reclamação e registre o tratamento.
   O filtro usa a data de postagem do comentário. A equipe responde pela
   interface da rede social. Salvar o tratamento nesta página altera
   somente o registro privado. Respostas, ocultações e exclusões pela API
   continuam sem implementação e exigem regras expressamente autorizadas.

Comandos na raiz de `gestao`, usando o Python privado existente que já tem
Google Analytics e Pillow (neste PC, `python` também possui as dependências):

```powershell
python -B scripts/marketing/coletar.py --dias 30
python -B scripts/marketing/fotos.py
python -B scripts/marketing/validar.py
python -B scripts/marketing/executar.py
python -B scripts/marketing/executar.py --enviar
python -B scripts/marketing/reconciliar.py
```

`coletar` aceita `--ate AAAA-MM-DD`, termina anteontem por padrão e guarda
também o período anterior. Cada janela tem até 30 dias e ambas precisam
caber nos últimos 90. Usa o cache do Analytics e limita insights a 20
publicações e 20 Stories por coleta. Listas de posts têm até quatro páginas
de 50 itens; Stories, duas. O painel informa cortes e métricas ausentes.
Stories são um retrato do instante da coleta, com datas próprias, mesmo
quando guardados junto de um relatório consolidado. Uma coleta diária pode
perder Stories que expiraram entre execuções. Nenhuma segunda rotina GBP
foi criada ou ativada; a rotina existente continua conforme
`ROTINA_PERFIL_GOOGLE.md`. Falta incorporar os comandos ao executor existente,
com as credenciais privadas disponíveis naquele ambiente, e conferir uma
execução agendada. A aprovação editorial de conteúdo continua separada.

`fotos` reaproveita o dHash e os descartes do GBP. Uma conferência parcial
de duplicidade interrompe a preparação/envio por este fluxo. Revise os
arquivos em `tmp/gbp/instagram/`; o painel mostra o ID e o link original.
A rotina GBP já documenta os termos das pessoas retratadas e uso das marcas;
cada seleção ainda precisa da revisão editorial. O executor confere o hash
da foto no envio e o GBP relê o recurso criado. O executor usa apenas as
fotos selecionadas. Logs Google ficam em `tmp/marketing/`, ignorado.

`reconciliar` faz GET de IDs já gravados e pode confirmar uma criação
anterior. Um `sending` sem ID há mais de 15 minutos passa a `uncertain`.
Se faltou o ID após um POST, a equipe deve conferir a rede social e os
recibos privados com o operador técnico. Esse caso permanece bloqueado;
o comando não presume falha nem cria outro envio. Não há reenvio automático.

## Cobertura das medidas

- **Portal:** coorte por data de criação em Fortaleza; comparecimentos,
  cancelamentos e no-shows usam o status atual dessa mesma coorte. Entradas
  do painel ficam separadas. Origem declarada pelo cliente está indisponível
  por falta de campo próprio confirmado.
- **GA4:** eventos `reservation_confirmed` e `visit_realized` no host do
  portal, por data do evento e origem/campanha/conteúdo medidos. O relatório
  conserva o fuso da propriedade, limiares e perda por outras linhas.
  Consentimento e processamento alteram a cobertura. Não junta pessoas ou
  sessões entre hosts.
- **Meta Ads:** consulta a conta confirmada pelo proprietário, nível anúncio
  e configuração de atribuição da conta. As ações mantêm seus nomes originais.
  A consulta exige acesso ao ativo. Sem ele, gasto e crédito ficam indisponíveis.
  As métricas por campanha somam somente anúncios retornados; alcance de
  anúncios/publicações permanece individual.
- **Custos:** só calcula quando há gasto finito, relatório completo e fuso
  compatível, fonte paga e IDs de anúncio/campanha iguais aos da reserva.
  Custo por comparecimento exige também desfecho da coorte. A medida é custo
  por reserva rastreada e conserva os limites dessa correspondência.
  A receita confirmada por reserva está indisponível; ROAS não é calculado.
  A estimativa legada de R$58/pessoa da CAPI foi preservada e fica fora desse cálculo.

Pixel e CAPI continuam usando os IDs já existentes, inclusive
`sf-sched-<reserva>`. A nova implementação não cria nem reenvia eventos.
Estado `sent` na fila CAPI representa a conclusão do worker após HTTP 2xx;
ele sozinho não comprova crédito ou deduplicação reconhecidos pela Meta.

## Banco, acesso e validações

Migrations `20261102203032` e `20261102204311` aplicadas ao `portal`,
registradas no histórico e verificadas por nova leitura. Criam
`marketing_snapshots`, `marketing_editorial`, `marketing_comments`,
`marketing_audit` e o vínculo privado de proprietário em
`marketing_private.settings`. RLS e grants explícitos; `anon` sem acesso.
Papéis iniciais de leitura/revisão: admin/socio, conforme a matriz de páginas.
Gerentes podem receber acesso pela matriz existente quando o proprietário
assim decidir. Aprovação exige o UUID privado configurado do proprietário;
um papel admin isolado não concede essa aprovação.

Snapshots são inseridos pelo coletor privado e preservam o histórico.
A RPC de painel retorna as coletas mais recentes do período selecionado e
do anterior; evita baixar o histórico completo. Comentários não guardam
nomes/IDs de autores. Texto de comentário continua sendo dado de cliente:
fica no portal protegido e não integra relatórios ou arquivos públicos.
Esta entrega não cria promessa de exclusão automática desse histórico.

As tabelas de reservas, seus triggers, fila CAPI e atendimento foram
preservados. UUID do proprietário, credenciais e dados reais não foram
incluídos no Git. O coletor reutiliza `META_IG_TOKEN` pelo carregador GBP,
OAuth Google existente, a conta de serviço GA4 privada e a credencial
Management API canônica de `reservas/.env.local`/ambiente. A leitura usa
`database/query/read-only`; migrations e gravação privada usam a rota de
escrita autorizada. Nenhum MCP de leitura foi usado para gravar.

Validações desta entrega:

- Oito testes offline do marketing, incluindo seleção e nova leitura GBP;
  20 do cliente Instagram e oito de feriados GBP.
- Contratos SQL reais em transação revertida: papéis, RLS, restrição anônima,
  aprovação com revisão esperada e edição retirando aprovação. Nenhuma
  reserva ou publicação sintética foi criada.
- QA Edge com autenticação e APIs simuladas em 390/1440 px: 19 critérios,
  formulários/readback, concorrência de filtros/revisões, gate de proprietário,
  XSS, mídia e custos rastreados. Nenhuma chamada real de escrita nesse QA.
  Capturas privadas em `../tmp/qa-marketing-2026-11-02/`.
- Site: 121 testes e verificadores de assets/CSP/CSS; fluxo publicado em
  navegador. Reservas: 42 testes e fluxo até RPC simulado; seis arquivos
  publicados comparados por nova leitura HTTPS.
- Primeira coleta real, preparação de fotos e filas vazias relidas. Nenhum
  envio editorial real foi executado. O primeiro envio aprovado e a execução
  agendada continuam sendo validações próprias pendentes.

## Fontes oficiais consultadas em 02/11/2026

- [Instagram, coleção mantida pela Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-ab559ffb-8e2c-4b0a-b43a-5737b6d2f672): Facebook Login, conta profissional vinculada, publicação e permissões; Stories exigem Business.
- [SDK Meta IGUser](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/iguser.py) e [IGMedia](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/igmedia.py): contêiner, publicação, insights e comentários.
- [Marketing API, coleção oficial](https://www.postman.com/meta/facebook-marketing-api/collection/0zr4mes/facebook-marketing-api-mapi) e [AdAccount](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/adaccount.py): conta e Insights.
- [Google, envio de fotos](https://developers.google.com/my-business/content/upload-photos), [recurso Media](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.media) e [qualidade](https://support.google.com/business/answer/6103862).
- [UTMs no Google Analytics](https://support.google.com/analytics/answer/10917952?hl=en) e [dimensões de origem](https://support.google.com/analytics/answer/11242841?hl=en).
- [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) e [Management API](https://supabase.com/docs/reference/api/v1-run-a-query).

As páginas canônicas da Meta retornaram erro/429. As coleções mantidas pela
Meta, seu SDK e as chamadas reais sustentam os contratos implementados.
O DeathStar atual atende essas funções com os ativos/permissões conferidos;
a consulta de anúncios exige a liberação da conta, sem necessidade comprovada
de outro aplicativo. A autorização do Google permanece própria desse serviço.
