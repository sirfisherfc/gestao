# Atendimento do Instagram @sirfisherfc

Diagnóstico e preparação de 01/11/2026. Responsável humano confirmado pelo
proprietário: gerente de atendimento, 7h–21h, WhatsApp (85) 98854-4274.
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
| Configuração na Meta | Pendente de inspeção do produto na conta. Nenhuma automação alterada. |
| Testes do produto e ativação | Pendentes. Os cenários abaixo são o roteiro, sem resultado de execução. |

A ferramenta de controle do Chrome interrompeu as rodadas anteriores por
não conseguir identificar a URL atual com segurança. Em 01/11/2026, os
diagnósticos oficiais do plugin confirmaram: Chrome rodando, extensão ChatGPT
habilitada no perfil Default e arquivo do native host presente, com ausência
da chave `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.openai.codexextension`.
O comando `check-native-host-manifest.js --browser chrome --json` retornou
código 1 e `correct=false`. Essa instalação precisa ser reparada antes de
retomar a configuração ou as respostas pela interface.

O procedimento `chrome-troubleshooting.md` do plugin instrui o usuário a
reinstalar o **Browser** pela interface de plugins do ChatGPT e proíbe o
agente de instalar/reparar o native host ou executar `installManifest.mjs`.
Nenhum registro, extensão, permissão ou processo foi alterado no diagnóstico.
Após a reinstalação, repetir a descoberta do navegador e conferir o acesso
ao perfil correto antes de operar o Instagram. As orientações públicas estão
em https://learn.chatgpt.com/docs/chrome-extension .

O navegador logado serve ao diagnóstico e à configuração; uma automação
contínua precisa rodar na infraestrutura do fornecedor ou em servidor próprio.

### Pedido de responder às mensagens pendentes

O proprietário autorizou responder às mensagens em aberto em 01/11/2026.
A tentativa pela API confirmou o bloqueio por falta de Advanced Access do
app para essa leitura. Não excluir conversas para reduzir o volume sugerido
pela mensagem da Meta. Nenhuma mensagem foi enviada por essa tentativa.
O atendimento pela interface permanece dependente do controle do Chrome.
Quando a leitura funcionar, conferir o histórico de cada conversa; mensagem
não lida e pergunta sem resposta são estados diferentes. Solicitações antigas
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

Priorizar **Meta Business Agent nativo**, se elegível e gratuito para esta
conta. A Meta anunciou sua expansão ao Instagram e início gratuito. A cota,
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

Se o Business Agent gratuito não estiver disponível, preparar as FAQs nativas
e o atendimento da gerente, preservando o teto. Não cadastrar cartão, iniciar
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
na pesquisa. A regra de 24h/sete dias acima também consta da documentação
operacional oficial do Manychat. Validar o contrato da opção escolhida antes
de depender de exceções. Não prometer atender todos os tipos de interação.

## Conteúdo e operações permitidas

Carregar [CONHECIMENTO.md](instagram-atendimento/CONHECIMENTO.md). O agente
pode responder localização, horários com exceções, regras de reserva, pets,
delivery e condições verificadas do executivo. Cardápio/preços continuam
em conferência; alergias seguem para a cozinha por atendimento humano.

O portal existente consulta disponibilidade e cria reservas por RPC; o
cancelamento público depende do token seguro. **Essas funções ainda não
estão integradas ao agente.** Nesta versão, ele orienta o uso do portal e
do link de cancelamento. Confirmação de reserva, cancelamento, disponibilidade
ou pagamento exige resultado verificado no sistema correspondente.

## Encaminhamento para a gerente

Preferir a mesma conversa no Direct: atribuir à gerente, registrar resumo do
pedido e da informação que falta, marcar pendência e pausar a automação até
o encerramento humano. Testar se a pausa é por conversa e se persiste; uma
pausa automática de 30 minutos não atende casos ainda abertos.

Encaminhar reclamação, cobrança contestada, estorno, urgência, alergia,
objeto perdido, pergunta sem fonte válida e decisão sobre reserva/evento.
Não decidir compensação. Evitar pedir dados já presentes no histórico.
Em urgência dentro da casa, orientar a pessoa a procurar a equipe presente.

O WhatsApp confirmado é opção e contingência. Um link não transfere histórico,
não notifica a gerente e não cria uma fila. Explicar essa limitação quando a
ferramenta não puder registrar a transferência. Fora de 7h–21h, informar a
faixa de atendimento sem prometer resposta imediata ou dia ainda não confirmado.

## Conversas novas e antigas

Começar com novas interações depois da ativação. A equipe revisa manualmente
conversas antigas pendentes, priorizando reclamações, pagamentos e visitas
próximas. Não disparar respostas retroativas. Se o cliente retomar conversa
antiga, ler o contexto e respeitar estado humano e janela de resposta.

Escolher uma aplicação responsável pela conversa. Antes de ativar, inventariar
ManyChat, respostas instantâneas, ausência, FAQs e agentes nativos. Ajustar
as regras que concorrem somente após preparar e verificar a substituição.

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

Estado: roteiro e revisão de conteúdo preparados. **Não executados no produto.**
Testes reais devem usar conta controlada, sem enviar mensagens de teste a clientes.
Apresentar os resultados e comportamento configurado antes da ativação.

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
- [Meta One: preços no Brasil](https://about.fb.com/br/news/2026/09/apresentando-o-meta-one-um-servico-de-assinatura-com-mais-recursos-e-ia-para-criar-se-conectar-e-se-destacar/amp/).
- [Meta: API Instagram e permissões](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api).
- [Meta: resposta privada a comentário](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api/private-replies).
- [Meta: webhooks](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/webhooks).
- [Manychat: plano Pro](https://help.manychat.com/hc/en-us/articles/25800228332572-Pro-plan),
  [preços](https://manychat.com/pricing),
  [janelas de mensagem](https://help.manychat.com/hc/en-us/articles/23358636027932-Understanding-messaging-windows),
  [pausa](https://help.manychat.com/hc/en-us/articles/19957883687708-How-to-pause-all-automations)
  e [roteamento](https://help.manychat.com/hc/en-us/articles/14281188830748-Conversation-Routing-for-Instagram).
