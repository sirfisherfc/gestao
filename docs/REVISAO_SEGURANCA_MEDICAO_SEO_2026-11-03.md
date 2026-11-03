# Revisão de segurança, medição e SEO (03/11/2026)

O proprietário autorizou concluir a revisão das imagens, corrigir, validar e
publicar sem novas perguntas. Foram conferidos os três repositórios, APIs do
Cloudflare, Analytics e Search Console, código publicado e e-mail de verificação.

Releitura de **03/11 às 18h12 de Fortaleza**: anunciante aprovado, sitemaps
processados sem erros, módulos publicados e worker ativo. Permanecem a
conferência das conversões dentro do Ads, sem acesso de edição nesta sessão,
e a nova varredura Semrush, cuja API continua sem unidades. Os resultados
dessa releitura estão nas seções correspondentes abaixo.

## Entrega publicada

| Área | Resultado |
| --- | --- |
| Janela de cookies | Pequena, com descrição em duas linhas nas larguras testadas de 320 a 430 px. Controla publicidade Google, Meta e OpenAI. |
| Recusa | Preserva funcionamento, idioma, GA4 estatístico e origem UTM; bloqueia pixels publicitários e remove identificadores de publicidade. |
| Envio pelo servidor | Exige autorização válida por reserva e confere revogação antes do envio Meta/OpenAI. |
| Receita | Retirada a estimativa legada de R$ 58 por pessoa do evento Meta Schedule. Reserva comum mede quantidade, sem receita presumida. |
| Contagem GA4 | `reservation_confirmed` passou de uma vez por sessão para uma vez por evento. O navegador deduplica pelo ID da reserva. |
| Portal nas buscas | Título e H1 identificam a reserva no Sir Fisher Praia; canonical por idioma e sitemap PT/EN. Tradução funciona mesmo com o SDK do banco indisponível. |
| Cancelamento privado | Metas `noindex, nofollow, noarchive` e `no-referrer`, fora dos pixels de publicidade e com URL GA4 sem token. |
| Segurança | HTTPS e TLS conferidos nos três hosts. API Cloudflare retorna seis sugestões restantes, detalhadas abaixo. |

Commits de implementação publicados:

- `gestao`: **ca4ec08**, migration, teste PostgreSQL e CI.
- `site`: **5eeb6f2**, consentimento, atribuição, aviso público e testes.
- `reservas`: **4d0d80e**, consentimento, worker, metadados e testes.

Migration **20261103071209** aplicada e registrada no Supabase do portal,
referência `lucpxoynpvogkvzepagi`. Somente a Edge Function
`send-openai-ads-conversions` foi implantada, na versão **48**, com seu
controle de autenticação preservado. As três páginas principais responderam
HTTP 200. O módulo compartilhado publicado tem hash **8993b0e4f2** nos dois hosts.

## Consentimento e dados enviados

A revisão encontrou Meta/OpenAI carregando antes da escolha, enquanto a
primeira janela tratava apenas do Google. A nova escolha cobre esses
fornecedores. A permissão antiga do Google exige uma nova decisão, pois
seu alcance era menor. O texto curto do celular foi preservado.

Antes de permitir e depois de recusar, os três sinais de publicidade Google
ficam `denied`; Google Signals e personalização também ficam desativados
na tag. O padrão e a redação de dados entram antes do SDK. Os pixels Meta e
OpenAI carregam depois da autorização. Meta usa somente os eventos explícitos
da integração, com a configuração automática desativada. OpenAI recebe seu
comando de consentimento antes da inicialização e na revogação.

O cookie técnico `sf_advertising_v2` guarda escolha, comprovante UUID e data
por até 180 dias. A data original limita a validade; uma navegação não renova
essa autorização. O rodapé permite mudar a escolha. Falhas ao comunicar uma
revogação ficam em `sf_ads_revoke_pending_v1` para nova tentativa na conexão
ou no próximo acesso. O bloqueio local vale imediatamente.

O portal envia o comprovante em `p_attribution`; o banco valida versão e
data e guarda três campos na reserva. As filas de publicidade exigem esse
comprovante, e o worker confere novamente antes de enviar. Reservas antigas
sem a nova autorização ficam fora dos reenvios publicitários, com o motivo
registrado. As regras da reserva, confirmação por e-mail e o aceite separado
de novidades continuam no fluxo existente.

Os cookies estatísticos GA4 permanecem. A atribuição conserva os rótulos UTM
e retira identificadores de anúncios quando a publicidade está negada.
URLs de origem ficam sem query e fragmento. O envio GA4 pelo servidor usa
`non_personalized_ads=true` e os dois sinais publicitários do Measurement
Protocol como `DENIED`. Conversões otimizadas e envio de contatos ao Google
Ads seguem desativados. O aviso público esclarece que hashes usados por
Meta/OpenAI permitem correspondência e continuam sendo dados protegidos.

O Advisor foi consultado pela Management API com a credencial existente;
o MCP Supabase desta sessão recusou o projeto. A tabela privada de revogações
tem RLS sem policy pública e privilégios diretos revogados de visitantes.
Sua RPC de revogação é pública por necessidade, retorna somente booleano
e usa um comprovante imprevisível. Os avisos sobre essa RPC e sobre a tabela
privada correspondem a esse desenho. O leitor de autorização do evento é
exclusivo de `service_role`. As exceções existentes do painel financeiro
descritas em AGENTS.md foram preservadas.

## Google Ads e Analytics

API confirmou o vínculo da propriedade **353205396**, Sir Fisher — Site
Oficial, com a conta **149-377-8788**, Sir Fisher Praia. A personalização
está habilitada no vínculo e depende da escolha do visitante na tag.
O fluxo é Web; Firebase não é necessário para essa configuração do site.

O padrão “dados não consentidos” mostrado na imagem combina com Consent
Mode: a escolha no site envia a atualização. Marcar os dados todos como
consentidos dispensaria essa distinção e foi mantido fora da entrega.
O tratamento de dados restrito e o relatório de computação confidencial
mostrados no painel não foram tratados como falhas da tag. Os testes com
SDK real confirmaram as atualizações e a limpeza dos identificadores após
revogação. A imagem recente do proprietário já mostrava a tag sem o marcador
vermelho anterior; o painel autenticado não pôde ser relido nesta sessão.

A contagem de `reservation_confirmed` foi atualizada pela Admin API e
relida como **ONCE_PER_EVENT**. A mudança vale para a coleta seguinte;
os outros eventos foram preservados. O MCP Analytics continua somente
para leitura. O script `site/tools/analytics/configurar_contagem_reservas.py`
tem prévia e exige `--aplicar` para essa escrita específica.

Ainda depende de acesso ao Google Ads conferir as ações já existentes e
criar/importar a conversão de reserva concluída. A sessão não tem uma API de
edição do Ads nem credencial local de desenvolvedor. As duas conexões de
computador/navegador retornaram indisponibilidade do host. Nenhuma ação de
conversão foi inventada, e nenhuma campanha ou orçamento foi alterado.
Uma busca no catálogo encontrou Windsor.ai sem conexão ativa; a descrição
confirma relatórios e operações de campanhas, com a criação/importação de
conversões ainda sem capacidade comprovada. Essa integração não foi usada
como se já tivesse acesso à conta.
Uma importação deve usar `reservation_confirmed`, conferir duplicidades e
separar a reserva concluída dos cliques de intenção antes de definir a meta
principal da campanha. A vinculação e a tag base já estão concluídas.

O e-mail autêntico do Google recebido em **03/11 às 08h07 de Fortaleza**,
assunto **“Você concluiu a verificação do anunciante”**, confirma que todas
as tarefas obrigatórias foram concluídas e que a conta **149-377-8788 foi
verificada**. A leitura dos metadados confirmou remetente Google e resultados
DKIM/SPF/DMARC válidos. A aprovação substitui o estado de revisão informado
no e-mail das 04h30. A mensagem integral e seus cabeçalhos ficaram fora do Git.

A releitura confirmou o mesmo vínculo Ads/GA4 e `reservation_confirmed`
em ONCE_PER_EVENT. A Data API retornou eventos recentes dos dois hosts e
confirmações de reserva. A disponibilidade do painel Ads foi tentada de novo:
o host de navegador/computador segue indisponível, e não há conector Ads de
edição autenticado nesta sessão. A aprovação do anunciante está concluída;
a conferência/importação das ações de conversão ainda depende desse acesso.

## SEO e sugestões do Semrush

A API Search Console retornou **Enviada e indexada**, com rastreamento
permitido e canonical própria nas seis URLs consultadas:

| Página | Conferência do conteúdo e tratamento da sugestão |
| --- | --- |
| Página inicial | Cerca de 1.040 palavras no conteúdo principal, categoria, endereço, cardápio e caminhos para visita. Preservada a função institucional. |
| Almoço executivo | Cerca de 530 palavras, sete opções, preços, horários e perguntas frequentes. Texto já aborda a procura por almoço executivo em Fortaleza. |
| Pôr do sol | Cerca de 760 palavras, horário calculado, tabela mensal, direção da vista e limites do cálculo. Conteúdo informativo preservado. |
| Guia da Beira-Mar | Cerca de 1.500 palavras, trechos da avenida, passeio, acesso e alimentação. O endereço do Sir Fisher é 3421; o alvo “2340” mostrado no Semrush não foi inserido como endereço do restaurante. |
| Fish and chips em inglês | Cerca de 585 palavras, ingredientes, porção, localização e caminhos para cardápio/reserva. O termo “near me” foi avaliado pela utilidade da localização e rota. |
| Portal de reservas | Conteúdo curto voltado ao formulário. Título, H1, canonical e sitemap foram ajustados para deixar clara a intenção de reservar. |

Na inspeção anterior à publicação, Google já selecionava essas URLs como
canônicas próprias. O portal ainda não declarava canonical; agora declara
a raiz em português e `?lang=en` em inglês. Isso reduz variações por
parâmetros e distingue a reserva das informações institucionais. Mudanças
de posição em consultas dependem de novo processamento e observação.

As sugestões de título, H1, palavras no corpo, legibilidade e semântica
foram confrontadas com o conteúdo atual. Quantidade adicional de texto e
repetição de termos não foram usadas para fechar uma contagem do fornecedor.
As páginas consultadas têm H1 único, descrição e canonical; os fluxos
privados ou utilitários mantêm seus controles próprios.

A sugestão de `aggregateRating` no site do próprio restaurante não foi
aplicada: o Google exclui avaliações sobre o próprio negócio dos rich
results de LocalBusiness/Organization, inclusive quando vêm de widgets.
As avaliações visíveis e os links para o Google foram preservados.
Links editoriais de outros sites dependem de publicações de terceiros e
continuam como trabalho de divulgação, fora de uma correção de código.

Os sitemaps de www e reservas foram reenviados pela API em **03/11 às
05h21 de Fortaleza**, ambos com HTTP **204** e releitura de aceitação.
O portal agora inclui as duas versões de idioma e alternates recíprocos.
Na releitura das **18h12**, os dois tinham `isPending=false`, com zero erros
e zero avisos. Os últimos downloads registrados pelo Google ocorreram às
08:21:38Z (www) e 08:21:41Z (reservas) de 03/11.

O Semrush respondeu `no_api_units`, sem possibilidade de nova consulta com
a cota atual. O host do navegador também ficou indisponível. A primeira
conferência se limitou às categorias e páginas visíveis nas imagens.
Depois, o proprietário baixou o XLSX de 03/11: suas 262 linhas detalhadas
foram conferidas e receberam decisão individual. Melhorias pertinentes de
texto, localização e navegação foram aplicadas em cinco páginas. O
[controle das ideias](seo/SEMRUSH_IDEIAS_2026-11-03.md) e seu JSON registram
o alcance, os motivos e as pendências; não se declarou “43/43 aplicadas”.
Sete redistribuições de termos e uma nova coleta na ferramenta continuam
dependendo desse acesso, e links externos dependem de publicação por terceiros.
[Cota do Semrush](https://www.semrush.com/mcp-access).

## Cloudflare

A leitura atual retornou **seis** ocorrências ativas. Os alertas antigos de
DMARC, TLS, security.txt e hosts web sem proxy já não constavam dessa lista.
SSL continua **Full (strict)**, TLS mínimo 1.2 e HTTPS obrigatório.

| Sugestão restante | Decisão |
| --- | --- |
| Dois CNAME sem proxy | autoconfig/autodiscover da Hostinger mantidos DNS-only para o serviço de e-mail. |
| Reduce skip rules | Duas exceções limitadas a `http_request_sbfm`, para rastreadores já autorizados. As outras fases de proteção ficam preservadas. |
| Bot Fight Mode | Mantido desligado: o modo gratuito ignora as exceções Skip e pode afetar os rastreadores autorizados. |
| AI Labyrinth | Opcional; preservada a decisão de permitir leitura pública pelos robôs de IA autorizados. |
| IP lists | Manutenção opcional para uma única faixa; regra existente preservada. |

www, reservas e admin recusaram TLS 1.0/1.1 com alerta de versão do servidor
e aceitaram 1.2/1.3 com certificado válido. `security.txt` respondeu 200 e
expira em 31/10/2027. DMARC em quarentena foi relido pela API, com os serviços
de e-mail preservados. O avanço para rejeição exige amostras dos relatórios
dos remetentes; as fontes conhecidas já foram verificadas na revisão anterior.
Os avisos opcionais não foram arquivados para reduzir o contador.

A API relida após a aprovação do anunciante retornou as mesmas seis
ocorrências e configurações TLS/HTTPS. As três páginas principais e os
módulos de publicidade responderam 200 com identificação de navegador,
mantendo o hash 8993b0e4f2. Requisições com identificação Python receberam
403/1010 da borda; a checagem de navegador do Cloudflare está ligada.

## Validações e limites

Passaram 127 testes Deno no site e 38 no portal; fluxo completo de reserva,
limites, falhas, idioma e cancelamento em oito cenários de navegador;
consentimento, migração da preferência antiga, revogação e duas linhas no
celular; quatro páginas com SDKs reais e coleta interceptada; sintaxe,
hashes, CSP, XML dos sitemaps e cardápio pré-renderizado.

A conferência local de 30 páginas encontrou 622 links e referências internas
com arquivos de destino presentes. As rotas `#p-` do cardápio correspondem
aos produtos existentes e são abertas pelo controlador de detalhes; os
demais fragmentos correspondem a elementos das páginas.

O PostgreSQL descartável do GitHub validou autorização, validade, filas,
revogação, privilégios e reaplicação da migration. Um ensaio em transação
desfeita validou a RPC de reserva e a limpeza da URL no banco real, sem
gravar reservas ou e-mails. O endpoint de revogação com comprovante nulo
respondeu 200/false; o worker sem autenticação respondeu 401. Não houve
envio de conversões comerciais de teste nem drenagem manual de filas reais.

A releitura operacional usou somente a rota de consulta do Management API.
Migration e três colunas de consentimento continuam presentes; worker 48
está ACTIVE. Desde **03/11 às 05h00 de Fortaleza**, até essa consulta, as
filas registraram três `visit_realized` enviados ao GA4, quatro `schedule`
enviados à Meta e quatro `schedule` enviados ao OpenAI. Todos esses eventos
estavam `sent`, sem erro registrado. São contagens por plataforma, com
possível sobreposição de reservas entre elas. A consulta agregada encontrou
zero evento publicitário ativo/enviado sem autorização válida nesse recorte.
O leitor de autorização continua exclusivo de service_role; a recusa de
execução à consulta de leitura preservou esse limite. Os agregados foram
conferidos sem alterar reservas ou filas.

As pendências externas são o acesso de edição às ações de conversão do Ads
e a nova consulta/varredura Semrush. A aprovação do anunciante e o processamento
dos sitemaps foram confirmados nesta releitura.
Os recibos técnicos ficam em `tmp/revisao-2026-11-03/`, ignorados pelo Git.
Credenciais, mensagens integrais, documentos e dados financeiros brutos
ficaram fora dos commits.

## Referências

- [Google: parâmetros de privacidade](https://developers.google.com/tag-platform/security/guides/privacy)
- [Google: padrão de consentimento da tag](https://support.google.com/google-ads/answer/12131703)
- [Google: consentimento no Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4/reference#consent)
- [Google: avaliações do próprio negócio](https://developers.google.com/search/blog/2019/09/making-review-rich-results-more-helpful)
- [Google: inspeção de URL](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)
- [Google: envio de sitemap](https://developers.google.com/webmaster-tools/v1/sitemaps/submit)
- [ANPD: cookies e proteção de dados](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia_orientativo_cookies_e_protecao_de_dados_pessoais)
- [Supabase: Advisor e funções públicas](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable)
- [Cloudflare: limites do Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/)
