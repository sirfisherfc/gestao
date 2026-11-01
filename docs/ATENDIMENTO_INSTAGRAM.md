# Atendimento do Instagram @sirfisherfc

Diagnóstico e configuração de 01/11/2026. Responsável humano confirmado pelo
proprietário: gerente Hêmile Alexandre, 7h–21h, WhatsApp (85) 98854-4274.
Dias da semana ainda não informados. Orçamento autorizado: iniciar gratuito,
com limite total de R$50/mês. Nenhuma contratação realizada.

## Estado da entrega

| Etapa | Estado verificado |
| --- | --- |
| Conta e credencial existentes | GET oficial autenticado confirmou @sirfisherfc e Página Sir Fisher. |
| Mensagens e comentários | Permissões concedidas ao token: `instagram_manage_messages`, `instagram_manage_comments`, `pages_manage_metadata`, `pages_read_engagement`, `pages_messaging` e `pages_show_list`. Isso não comprova entrega ou envio de mensagens. |
| MCP existente | Mantido somente para leitura de métricas. Não foi ampliado para Direct ou escrita. |
| Assinaturas de webhook | GET de `subscribed_apps` da Página e da conta retornou listas vazias para o app/credencial consultados. A consulta não inventaria todas as integrações de outros apps. |
| Leitura atual de conversas | HTTP 400, código -2, subcódigo 2534084. Nova consulta mínima em 01/11, com Page token e `platform=INSTAGRAM`, trouxe detalhe oficial: muitas conversas de usuários sem função no app e exigência de Advanced Access para `instagram_manage_messages`. Permissão no token e acesso avançado do app são etapas distintas. A lista vazia da rota da conta não comprova caixa vazia. |
| Amostra histórica | Originais de 28/09/2026 lidos em memória; resumo abaixo, sem dados pessoais. |
| Base para o agente | Preparada em `instagram-atendimento/CONHECIMENTO.md`, com limites e fontes. |
| FAQs nativas do Instagram | Quatro perguntas com respostas fixas salvas e ativas; textos em `BOOK_QA_ATENDIMENTO.md`. Não interpretam livremente outras perguntas. |
| Regra de reserva | Instagram retirado da regra antiga, preservada no Messenger. Nova regra de Instagram com condições restritas e 15 minutos de inatividade salva e desligada, aguardando teste externo e validação da pausa humana. |
| Atendimento humano | Respostas manuais e cinco casos atribuídos à gerente com Acompanhar, conferidos no filtro nativo. Encaminhamento automático a partir de pedido de humano não configurado; FAQ oferece WhatsApp. |
| Comentários | Seis publicações e nove comentários visíveis revisados; elogios ou reações sem perguntas. Nenhuma resposta publicada ou automação de comentário ativada. |
| IA nativa | Não apareceu no aplicativo conferido pelo proprietário. Atendimento livre com IA ainda indisponível nesta conta. |
| Testes | Prévia, salvamento, estado dos canais, envios manuais e atribuições conferidos. Teste por cliente externo, deduplicação automática e pausa durante atendimento humano pendentes. |

### Estado operacional conferido em 01/11/2026

Resultados da conferência final desta sessão:

| Item | Estado observado |
| --- | --- |
| Conversas distintas com resposta manual | 31: 13 da caixa principal e 18 de Pedidos, sendo 17 normais e um oculto. Complementos na mesma conversa não foram contados novamente. |
| Pedidos normais | Zero restantes no filtro conferido após responder a 17 conversas. |
| Pedidos ocultos | Dois preservados: oferta de catálogo de fornecedor e grupo pedindo divulgação. Nenhum foi excluído. |
| Fila humana | Cinco casos com Hêmile e Acompanhar, conferidos no filtro nativo. Dois pedidos de confirmação sobre vales foram respondidos, concluídos e retirados de Acompanhar. As duas propostas comerciais sem persistência não integram os cinco casos. |
| Encaminhamentos sem persistência | Duas propostas comerciais exibiram registro de atribuição à Hêmile, mas perderam responsável e Acompanhar ao reabrir. O salvamento repetido não confirmou persistência. Links do WhatsApp foram enviados; os encaminhamentos internos continuam pendentes. |
| Não lidas | Conversas individuais revisadas até junho. Restaram grupos antigos com mensagem indisponível ou registros de saída, sem envio. O filtro não comprova ausência de pendências em todo o acervo. |
| Comentários | Seis publicações abertas; nove comentários visíveis, distribuídos em 1 + 1 + 1 + 4 + 1 + 1. Apenas elogios ou reações sem perguntas; zero respostas publicadas e zero automações de comentário ativadas. |
| Automação de reserva nova | Salva e desligada. Conserva 15 minutos de inatividade; falta teste externo e validação da pausa durante atendimento humano. |

As contagens descrevem a caixa e os filtros conferidos naquele momento.
Uma resposta enviada não comprova resolução do pedido; atribuição não
comprova que a gerente já leu ou encerrou o caso. A revisão não cobriu todo
o acervo e não comprova ausência global de pendências. Não incluímos nomes,
perfis ou mensagens de clientes nos arquivos versionados.
Na revisão posterior da caixa principal, menções sem pergunta foram
concluídas sem nova resposta. Algumas solicitações de menção já haviam
recebido agradecimento durante a revisão de Pedidos e entram na contagem
de conversas com resposta. Uma
tentativa de agradecer a uma menção foi rejeitada pela revisão automática
por falta de contexto e não foi enviada; ela não integra a contagem acima.

### Acesso ao Chrome e diagnóstico anterior

O Chrome voltou a funcionar nesta sessão. O perfil correto, as automações
e a caixa de entrada foram acessados; respostas manuais e atribuições foram
realizadas. O bloqueio anterior permanece registrado a seguir como histórico.

A ferramenta de controle do Chrome interrompeu as rodadas anteriores por
não conseguir identificar a URL atual com segurança. Em 01/11/2026, os
diagnósticos oficiais do plugin confirmaram: Chrome rodando, extensão ChatGPT
habilitada no perfil Default e arquivo do native host presente, com ausência
da chave `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.openai.codexextension`.
O comando `check-native-host-manifest.js --browser chrome --json` retornou
código 1 e `correct=false` naquele diagnóstico.

O procedimento `chrome-troubleshooting.md` do plugin instrui o usuário a
reinstalar o **Browser** pela interface de plugins do ChatGPT e proíbe o
agente de instalar/reparar o native host ou executar `installManifest.mjs`.
Nenhum registro, extensão, permissão ou processo foi alterado no diagnóstico.
Naquela etapa, a orientação foi repetir a descoberta do navegador e conferir
o perfil após a reinstalação. As orientações públicas estão
em https://learn.chatgpt.com/docs/chrome-extension .

O navegador logado serve ao diagnóstico e à configuração; uma automação
contínua precisa rodar na infraestrutura do fornecedor ou em servidor próprio.

### Acesso da integração contínua

O painel autenticado da Meta confirmou o app existente **DeathStar**, ID
`224912007567636`, no portfólio Sir Fisher. A consulta oficial de depuração
confirmou que ele emitiu a credencial canônica: `SYSTEM_USER`, válida,
com `expires_at=0` (sem vencimento programado informado). O acesso ainda
pode ser revogado; esse resultado não comprova funcionamento do atendimento.
Nenhum token ou segredo foi exibido, renovado ou copiado para a documentação.

O app está **em desenvolvimento**. Em Permissões e recursos,
`instagram_manage_messages`, `instagram_manage_comments`, `pages_messaging`
e `pages_manage_metadata` aparecem com acesso **Standard**, sem análise
solicitada. O produto Messenger está adicionado e a Página Sir Fisher está
vinculada. A tela de mensagens do Instagram informa que o app deve passar
por análise antes de interagir com clientes; durante o desenvolvimento,
limita as mensagens às funções de administrador, desenvolvedor e testador.
O callback de webhook ainda não está configurado nessa tela.

Assim, o erro de listagem de conversas tem cobertura específica. Ele,
isoladamente, não comprova bloqueio de todo evento novo. O painel acrescenta
os requisitos que faltam ao caminho atual com Facebook Login: callback
HTTPS, validação da assinatura, inscrição de eventos, testes controlados,
análise e acesso necessários e publicação do app. Não houve alteração de
modo, inscrição, permissão ou credencial. Nenhum recebimento ou envio por
essa API foi validado. Os caminhos Facebook Login e Instagram Login exigem
configurações próprias; uma condição de um caminho não comprova acesso no outro.

### Pedido de responder às mensagens pendentes

O proprietário autorizou responder às mensagens em aberto em 01/11/2026.
A tentativa pela API confirmou o bloqueio por falta de Advanced Access do
app para essa leitura. Não excluir conversas para reduzir o volume sugerido
pela mensagem da Meta. Nenhuma mensagem foi enviada por essa tentativa.
O atendimento pela interface foi retomado com o Chrome funcionando.
Conferir o histórico de cada conversa; mensagem não lida e pergunta sem
resposta são estados diferentes. Solicitações antigas
podem ter cobertura menor pela API. Preservar o contexto e evitar resposta
genérica ou promessa de operação sem resultado verificado.

## O que os clientes procuram

O [book existente](BOOK_QA_ATENDIMENTO.md) analisa exportação com 2.056
conversas, 1.327 com texto de cliente, 3.397 mensagens, de 2023 a setembro
de 2026. Seus temas mais frequentes são reserva (271 conversas), horário
(202) e cardápio/preços (181). As contagens pertencem àquela exportação.

Nesta entrega foi conferida uma amostra determinística de 80 conversas,
64 de inbox e 16 de solicitações. Dessas, 53 têm 113 mensagens de cliente,
entre 28/09/2023 e 22/09/2026. A triagem por palavras, com sobreposição,
encontrou reservas em 12, promoções em sete, horário em cinco, cardápio/preço
em quatro e grupos/eventos em quatro. Foram confirmados pedidos como
“É preciso reservar?” e “Pode enviar o cardápio?”, aqui parafraseados.

Havia três saídas genéricas “Ficou com alguma dúvida...” após perguntas
de reserva e uma resposta com horário 9h–23h. O book associa a saída genérica
ao ManyChat na exportação. A integração atual e sua configuração precisam
de conferência na conta. Esses dados não medem o atendimento de novembro.
Nenhum nome, telefone ou mensagem integral de cliente foi versionado.

## Escolha e custos

As quatro FAQs fixas e o atendimento da gerente são a configuração atual.
As FAQs executam na infraestrutura da Meta e continuam disponíveis com o
PC desligado. O Chrome foi usado para configurar e atender manualmente;
esta sessão do Codex não foi instalada como atendente contínuo.
O **Meta Business Agent nativo** não apareceu no aplicativo conferido pelo
proprietário. A Meta anunciou sua expansão ao Instagram e início gratuito;
uma oferta anunciada não comprova disponibilidade nesta conta. A cota,
a renovação e os controles de encaminhamento precisam aparecer na conta
antes da ativação. Entrada oficial: https://www.facebook.com/business/ai .

| Opção | Custo publicado e decisão |
| --- | --- |
| Automações nativas disponíveis | Usar recursos sem cobrança adicional confirmados na conta. Respostas fixas cobrem FAQs; interpretação de texto livre e encaminhamento dependem do recurso disponível. |
| Business Agent nativo | Início gratuito anunciado; franquia atual do Instagram não encontrada em fonte pública. Conferir a tela. Preferido se couber no teto e passar nos testes. |
| Meta One para empresas | Essencial desde R$59/mês no Brasil, acima do teto. Não contratar. Core e Instagram Plus não comprovam acesso ao atendimento comercial. |
| Manychat Pro com IA | US$39/mês, ou US$348 cobrados ao ano; 2.500 contatos ativos/mês, dois lugares no Inbox e excedentes. Acima do teto. Não contratar. |
| Manychat Free | Modelo atual com 25 contatos ativos/mês e quatro automações. Conferir eventual plano legado existente; cobertura atual insuficiente para propor atendimento contínuo com IA. |
| Integração própria por API | Exige servidor, webhooks, monitoramento e provedor de IA. Credencial ampla existente não comprova app pronto. Custo e manutenção maiores que a configuração nativa; não implantar infraestrutura sem necessidade. |

Foi localizado acesso existente ao Gemini, já usado em ferramenta de imagens.
Um teste de texto sem dados de clientes validou `gemini-3.5-flash-lite`,
HTTP 200, com 61 tokens de entrada e 19 de saída. A resposta ao exemplo
público usou o horário de domingo fornecido no pedido. Isso valida o acesso
ao modelo; não valida o agente, as operações ou a integração do Instagram.
`gemini-2.5-flash-lite` retornou 404 apesar de constar da listagem; não
depender desse identificador sem investigação.

O preço Standard consultado para o modelo 3.5 é US$0,30 por milhão de tokens
de entrada e US$2,50 por milhão de saída. O exemplo de 80 tokens equivale
a cerca de US$0,000066 pela tarifa publicada, sujeito ao faturamento real.
O `serviceTier=standard` da resposta não identifica Free/Paid. O AI Studio
mostrou um projeto com faturamento pago, mas o vínculo dessa chave e o teto
de gasto da integração ainda precisam de confirmação. Não houve contratação,
mudança de faturamento, envio de conversa de cliente ou implantação de servidor.
Uma integração própria é candidata para baixo uso; custo total e limite de
R$50 ainda dependem de hospedagem, volume e bloqueio de consumo por agente.
O plano gratuito do Gemini permite uso do conteúdo para melhorar produtos;
conferir o plano e o tratamento dos dados antes de enviar mensagens reais.

As FAQs nativas foram configuradas com atendimento da gerente, preservando
o teto. Se a IA nativa aparecer, conferir recursos, custos e testes antes de
ativar. Não cadastrar cartão, iniciar
trial com cobrança automática ou contratar assinatura acima do limite.

## Cobertura e regras oficiais

- **Direct:** conta profissional e cliente iniciando a conversa. Aplicar
  janela conservadora de 24h desde a última interação para respostas
  automáticas. Mensagem humana até sete dias exige recurso/tag Human Agent;
  não usar essa exceção para prolongar automação. Não enviar lote para o
  histórico. Grupos não são cobertos pela API de mensagens.
- **Comentários em posts/Reels:** a API permite comentário/resposta com
  permissão própria e uma resposta privada em até sete dias. Continuar no
  Direct somente após resposta do cliente e dentro de 24h. Comentários
  públicos não devem revelar dados de reservas ou cobranças.
- **Stories:** respostas e menções podem chegar pelo webhook de mensagens.
  Comentário público de Story, resposta ao Story e reação têm contratos
  próprios. A cobertura do agente nativo precisa ser testada por evento.
- **Integração própria:** autenticação oficial, HTTPS permanente, app Live,
  permissões e acesso adequados, inscrição na conta, validação de assinatura
  SHA256, deduplicação e tratamento de reentrega. Instagram Login e Facebook
  Login têm conjuntos de permissões diferentes. O diagnóstico reutilizou
  Facebook Login. Standard/Advanced Access depende do caminho e dos ativos.

As páginas canônicas de janela geral/Human Agent tiveram bloqueio de leitura
na pesquisa. A regra de 24h/sete dias acima consta da documentação
operacional oficial do Manychat. Depois, a tela autenticada Permissões e
recursos da Meta também confirmou o prazo de sete dias de Human Agent,
com acesso Standard e nenhuma análise solicitada neste app. O recurso não
foi ativado. Limites numéricos de requisições por segundo/hora não foram
confirmados em fonte primária atual; conferir a conta e tratar os bloqueios
na implementação. Validar o contrato da opção escolhida antes de depender
de exceções. Não prometer atender todos os tipos de interação.

## Conteúdo e operações permitidas

Carregar [CONHECIMENTO.md](instagram-atendimento/CONHECIMENTO.md). O agente
pode responder localização, horários com exceções, regras de reserva, pets,
delivery e condições verificadas do executivo. Cardápio/preços continuam
em conferência; alergias seguem para a cozinha por atendimento humano.
Em 01/11/2026, o proprietário reconfirmou que a casa não tem happy hour,
permite levar bolo sem taxa e recebe currículos em `sir.fisher@outlook.com`.
Também confirmou aceitação de VR, Alelo, Ticket e Sodexo/Pluxee, sem informar
restrições. Essa confirmação não se estende a outros aplicativos ou benefícios.

O portal existente consulta disponibilidade e cria reservas por RPC; o
cancelamento público depende do token seguro. **Essas funções ainda não
estão integradas ao agente.** Nesta versão, ele orienta o uso do portal e
do link de cancelamento. Confirmação de reserva, cancelamento, disponibilidade
ou pagamento exige resultado verificado no sistema correspondente.

## Encaminhamento para a gerente

Preferir a mesma conversa no Direct: atribuir à Hêmile, registrar resumo do
pedido e da informação que falta, marcar pendência e pausar a automação até
o encerramento humano. Testar se a pausa é por conversa e se persiste; uma
pausa automática de 30 minutos não atende casos ainda abertos.
Cinco casos foram conferidos com responsável e Acompanhar no filtro nativo.
Esse acompanhamento foi manual. Não foi configurada transferência automática
por pedido de atendimento humano; a FAQ ativa oferece o WhatsApp oficial.

Encaminhar reclamação, cobrança contestada, estorno, urgência, alergia,
objeto perdido, pergunta sem fonte válida e decisão sobre reserva/evento.
Não decidir compensação. Evitar pedir dados já presentes no histórico.
Em urgência dentro da casa, orientar a pessoa a procurar a equipe presente.

O WhatsApp confirmado é opção e contingência. Um link não transfere histórico,
não notifica a gerente e não cria uma fila. Explicar essa limitação quando a
ferramenta não puder registrar a transferência. Fora de 7h–21h, informar a
faixa de atendimento sem prometer resposta imediata ou dia ainda não confirmado.

A sessão encontrou falha de persistência em dois encaminhamentos comerciais:
o registro e o aviso de atribuição apareceram, mas responsável e Acompanhar
sumiram após reabrir, inclusive depois de revisar a seleção e salvar novamente.
Não contar esses casos como transferidos. A fila exige conferência após
reabertura; até resolver a falha, o link de WhatsApp é a contingência já enviada.

## Conversas novas e antigas

Começar com novas interações depois da ativação. A equipe revisa manualmente
conversas antigas pendentes, priorizando reclamações, pagamentos e visitas
próximas. Não disparar respostas retroativas. Se o cliente retomar conversa
antiga, ler o contexto e respeitar estado humano e janela de resposta.

As quatro FAQs do Instagram estão ativas. A regra antiga de reserva passou
a atender somente o Messenger; esse canal foi preservado. A nova regra de
reserva do Instagram está salva e desligada. Conferir respostas instantâneas,
ausência e eventuais integrações antes de ativar outra automação. A relação
histórica com ManyChat não comprova integração atual ativa.

A regra nova, ID `1437395341168944`, foi reaberta e conferida sem alterações:
Instagram selecionado, Messenger desmarcado, estado Desativado e Salvar
desabilitado. Ela procura as frases exatas `como reservar`, `fazer reserva`,
`quero reservar`, `reservar mesa` e `reservar uma mesa`, com inatividade
mínima de 15 minutos. Resposta salva:

> Sou o assistente virtual do Sir Fisher 😊 Para consultar horários e reservar para até 10 pessoas: https://reservas.sirfisher.com.br/ A confirmação depende de concluir o pedido no portal. Para hoje, o corte é 15h30. Para grupos, alterações ou ajuda com cancelamento, fale com a gerente (7h–21h): https://wa.me/5585988544274 Para cancelar, você também pode usar o link recebido no e-mail da reserva.

Para pausar as FAQs apenas no Instagram: Caixa de Entrada → Automações →
Perguntas frequentes → Editar → desmarcar Instagram → Salvar alterações.
O interruptor geral afeta os canais selecionados; preservar o Messenger.
Reativar exige selecionar Instagram, salvar e conferir as quatro respostas.
Esse procedimento usa controles disponíveis na tela; a entrega durante a
pausa e a suspensão por conversa ainda não foram testadas com conta externa.

## Roteiro antes da ativação

| Caso | Resultado exigido |
| --- | --- |
| Primeiro contato | Identifica assistente virtual e oferece pessoa. |
| Hoje/amanhã/Natal | Usa Fortaleza, data e exceção correta; pede data se ausente. |
| Horário regular | Dom–qui 9h–22h15; sex–sáb 9h–23h. |
| Preço/porção em conferência | Envia fonte e pede confirmação, sem inventar valor vigente. |
| Alergia | Encaminha à equipe/cozinha, sem assegurar segurança do alimento. |
| Reserva para 10/11/30 | Portal / gerente / configurador com confirmação humana. |
| “Minha reserva está confirmada?” | Exige resultado do portal; link enviado não é confirmação. |
| Disponibilidade ou API fora do ar | Oferece consulta no portal, sem afirmar vaga. |
| Alteração/cancelamento | Link seguro ou gerente; sem executar por nome. |
| Comprovante/pagamento | Pede conferência humana; sem afirmar quitação. |
| Reclamação e pedido de pessoa | Atribui, sinaliza e pausa; confirma somente ações verificadas. |
| Fora do horário humano | Informa 7h–21h e não promete resposta imediata. |
| Evento repetido/automação antiga | Uma resposta útil por evento; sem resposta concorrente. |
| Resposta a Story e comentário | Verifica cada cobertura e janela separadamente. |
| Retomada de conversa antiga | Preserva atendimento humano e regra de janela. |
| Pausa global e por conversa | Nenhuma resposta nova enquanto pausado; retomada controlada. |

### Validação por camada

| Camada | Resultado e limite |
| --- | --- |
| Conteúdo e interface | Quatro FAQs reabertas após recarga, com textos persistidos, Instagram selecionado, estado Ativado e Salvar desabilitado sem alterações. Nova regra de reserva, com 15 minutos de inatividade, salva e desligada. Isso não comprova entrega por todos os gatilhos. |
| Atendimento real manual | Respostas enviadas a conversas pendentes pela interface, com histórico considerado. Contagens no quadro operacional; envio não comprova resolução. |
| Modelo de IA isolado | Gemini 3.5 Flash-Lite respondeu ao exemplo público fornecido, HTTP 200 e 80 tokens. Não recebeu conversas de clientes e não está conectado ao Direct. |
| Fila humana | Cinco casos com Hêmile e Acompanhar confirmados no filtro nativo. Dois encaminhamentos comerciais falharam na persistência após reabrir e permanecem pendentes; o link do WhatsApp foi enviado. Leitura ou conclusão pela gerente não comprovadas. Transferência automática por pedido humano não configurada. |
| Revisão de comentários | Seis publicações e nove comentários visíveis revisados, todos com elogios ou reações sem perguntas. Nenhuma resposta publicada; revisão não cobre todo o acervo de comentários. |
| Alerta de mensagens sem resposta | Recurso inspecionado; somente Messenger selecionável, sem opção de Instagram. Tela cancelada sem salvar. Não cobre pendências do Instagram. |
| Operações | Reservas, cancelamentos e pagamentos continuam pelos portais ou por pessoa. Nenhuma dessas operações foi executada pelo agente. |
| Automação completa | Falta teste com conta externa controlada, resposta duplicada e pausa persistente durante atendimento humano. Comentários e respostas a Stories continuam com cobertura a verificar. |

Os cenários acima são o roteiro para os testes ainda faltantes. Não atribuir
aprovação geral ao roteiro por causa dos envios manuais. Testes reais devem
usar conta controlada, sem mensagens de teste a clientes. Apresentar os
resultados e o comportamento da nova regra antes de ativá-la. Os 15 minutos
de inatividade não substituem a validação de pausa durante atendimento humano.

## Acompanhamento proposto

Nos primeiros sete dias, a gerente revisa diariamente pendências e respostas
automáticas. Registrar sem conteúdo pessoal: total de novas conversas,
mediana/p90 até a primeira resposta útil, casos resolvidos automaticamente,
encaminhamentos abertos/encerrados e erros por assunto.

Contar resolução automática somente quando houver evidência de conclusão
e ausência de pendência humana; separar sugestões do bot de conclusão
confirmada. Medir resposta humana na faixa 7h–21h e também tempo corrido.
Erro de preço, confirmação falsa ou dados de outro cliente exige pausar,
corrigir e repetir o cenário antes de retomar. Conferir cota e cobrança;
ao atingir o limite gratuito, preservar contingência humana sem upgrade automático.

## Referências oficiais

Consulta em **01/11/2026**:

- [Meta Business Agent: anúncio e início gratuito](https://about.fb.com/news/2026/06/meta-business-agent/).
- [Meta Business Agent para Instagram](https://ai.meta.com/meta-business-agent/instagram/)
  e [entrada pelo aplicativo](https://www.instagram.com/linking/business_ai_onboarding).
- [Meta One: preços no Brasil](https://about.fb.com/br/news/2026/09/apresentando-o-meta-one-um-servico-de-assinatura-com-mais-recursos-e-ia-para-criar-se-conectar-e-se-destacar/amp/).
- [Meta: API Instagram e permissões](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api).
- [Meta: Conversations API com Facebook Login](https://www.postman.com/meta/messenger-platform-api/folder/22794852-255610cd-47f5-4f4d-b3fa-71aec360be9a)
  e [introdução ao Messenger para Instagram](https://developers.facebook.com/docs/messenger-platform/instagram/get-started/).
- [Meta: resposta privada a comentário](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api/private-replies).
- [Meta: webhooks](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/webhooks).
- [Google: preços do Gemini](https://ai.google.dev/gemini-api/docs/pricing),
  [limites](https://ai.google.dev/gemini-api/docs/rate-limits)
  e [faturamento](https://ai.google.dev/gemini-api/docs/billing).
- [Manychat: plano Pro](https://help.manychat.com/hc/en-us/articles/25800228332572-Pro-plan),
  [preços](https://manychat.com/pricing),
  [janelas de mensagem](https://help.manychat.com/hc/en-us/articles/23358636027932-Understanding-messaging-windows),
  [pausa](https://help.manychat.com/hc/en-us/articles/19957883687708-How-to-pause-all-automations)
  e [roteamento](https://help.manychat.com/hc/en-us/articles/14281188830748-Conversation-Routing-for-Instagram).
