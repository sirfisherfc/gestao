# Atendimento ativo no Jotform

Estado conferido em **02/11/2026**, no fuso de Fortaleza. O Direct do
`@sirfisherfc` está conectado ao agente **Sir Fisher — Assistente virtual**,
com **All DMs** e **Reply to DMs: Active**. A conta que administra o Jotform
é do proprietário. A execução ocorre na nuvem do fornecedor e dispensa
manter o PC ou Chrome aberto.

- [Configuração do agente](https://www.jotform.com/agent/build/01a19a3df878700089e34a4245ed6168877e/publish/instagram)
- [Conversas do agente](https://www.jotform.com/conversations/263048519155056)

Esses endereços exigem o acesso do proprietário para administrar o agente.
Não contêm senha ou credencial. Os dois aplicativos próprios da Meta foram
preservados. O pedido de análise do DeathStar continua sem envio; a
conexão Jotform foi testada por uma conta fora do piloto antigo.

## Respostas e limites

O agente responde em português, com mensagens curtas e base pública
revisada. A saudação simples se identifica como assistente virtual.
Perguntas sobre comida, pratos, almoço, porções, bebidas e preços devem
receber o link completo https://www.sirfisher.com.br/cardapio/ junto da
informação confirmada. Preço ou disponibilidade sem fonte atual segue
também ao WhatsApp, sem inventar valor.

Pedidos de pessoa, reclamação, cobrança contestada e assuntos sem fonte
segura recebem https://wa.me/5585988544274 . Não há horário humano,
prazo ou promessa de estorno. O cliente precisa abrir o WhatsApp e enviar
a mensagem. O link não transfere o histórico nem notifica a equipe.
Uma pergunta seguinte no Direct continua elegível para resposta.

Reservas de 1 a 10 pessoas usam https://reservas.sirfisher.com.br/ .
O agente não consulta disponibilidade nem conclui reserva, cancelamento
ou pagamento. Nenhuma dessas integrações operacionais foi habilitada.
Áudios, imagens e assuntos sem interpretação segura exigem encaminhamento;
o ensaio atual cobriu mensagens de texto.

O treinamento automático por bio, posts e DMs foi pulado. Foi carregada
uma única entrada de conhecimento com fatos públicos. A memória entre
sessões e a busca automática no site foram desligadas. As conversas
continuam registradas no Jotform, conforme a conexão autorizada.

Uma prévia com memória ligada inventou confirmação de reserva ao retornar
à conversa. A correção foi aplicada antes da liberação do Direct: memória
desligada e novo teste sem essa confirmação. Duas regras experimentais
ficaram **desabilitadas**: saudação por `Conversation starts`, que interferiu
em outro pedido, e inclusão ampla de WhatsApp para informação ausente, que
encaminhou uma FAQ conhecida. Não reativá-las sem corrigir e testar.
Permanecem a regra de saudação simples e a resposta mínima para spam.

## Spam e pausas

No Direct, **Excluded Categories** está ligado para oferta de venda de
seguidores ou curtidas artificiais, com **Fallback Message** desligado.
O teste dessa oferta ficou sem resposta; a pergunta legítima seguinte
recebeu resposta. Outras formas inequívocas de spam têm a orientação
mínima “Este canal atende dúvidas sobre o restaurante Sir Fisher.”
Não há exclusão nem bloqueio automático de perfis.

Relatos reais de golpe, reclamações, currículos e fornecedores comuns
devem ser preservados. Esse filtro depende de classificação e não garante
detecção de todo spam. O ensaio confirmou somente a oferta de seguidores.

**Response Hours**, **Delayed Response** e filtro por quantidade de
seguidores estão desligados. **Automatic Pause** permanece no padrão
observado de 12 horas quando alguém envia manualmente um Direct. Isso
exige atenção se o proprietário intervier pelo Instagram. Enviar o link
do WhatsApp pela IA não causou essa pausa nos testes.

Para pausar o Direct: abrir a configuração acima e desligar **Reply to
DMs**. Para pausar o agente inteiro: **Settings → General → Agent Status
→ Disabled**. Essa pausa global foi aplicada e conferida na prévia, que
ficou indisponível; depois o agente foi reativado para os testes. O botão
**Take Over** existe no painel de conversas, mas não foi acionado no ensaio.

## Canais e prevenção de duplicidade

| Canal/integração | Estado final conferido |
| --- | --- |
| Jotform Direct | Ativo para All DMs; oito respostas reais no teste controlado |
| Jotform comentários, stories e menções | Desligados; exigem teste próprio antes da ativação |
| Piloto próprio Supabase/Gemini | Pausa global ligada; modo efetivo OFF; público próprio segue OFF |
| FAQ nativa Meta | Instagram desmarcado e salvo; Messenger preservado |
| Palavra-chave nativa “Instagram - orientar reserva” | Desligada |
| Outra palavra-chave nativa “reserva” | Messenger ligado, Instagram desligado; preservada |
| Saudação nativa Meta | Messenger ligado, Instagram desligado; preservada |

O legado conservou 13 envios/seis chamadas, cinco casos fechados e zero
abertos na leitura de conferência. Não retomar esse piloto junto do
Jotform. O cron antigo foi preservado e a pausa global impede as respostas;
nenhum novo cron, servidor local ou deploy foi criado nesta ativação.

## Testes e acompanhamento

Oito respostas reais foram conferidas no Direct do `@sirfisherpub` e no
histórico do Jotform. A página do agente confirmou **8 DM replies**:

| Entrada controlada | Resultado observado |
| --- | --- |
| Oi inicial | Resposta recebida; a identificação virtual foi reforçada e retestada abaixo |
| Endereço e horário | Endereço e horários regulares corretos |
| Almoço executivo | Regras do executivo e link do cardápio |
| Cobrança em duplicidade/pessoa | WhatsApp oficial, sem prometer estorno ou prazo |
| Bolo e Alelo após WhatsApp | Resposta pertinente e cardápio; sem pausa geral da conversa |
| Confirmar reserva de quatro pessoas | Portal de reservas, sem confirmação inventada |
| Oi após regra de saudação | Identificou-se como assistente virtual |
| Preço de camarão após spam | Sem valor inventado; cardápio e WhatsApp |

A oferta sintética de seguidores ficou sem resposta no intervalo observado
de pelo menos 57 segundos e antes da resposta à pergunta seguinte. Nenhum
envio duplicado foi observado nessa sequência. A prévia também cobriu
perguntas frequentes, informação ausente e spam. Tempos antigos do piloto
Gemini não medem o Jotform; o painel observou entrada/saída no mesmo minuto
nos primeiros testes, sem estabelecer prazo ou média de atendimento.

As provas de tela e os recibos ficam em `tmp/instagram-atendimento/provas/`,
ignorados pelo Git. Foram usadas contas controladas; nenhum conteúdo de
cliente foi incluído na base ou nesta documentação.

O proprietário pode acompanhar em **Conversations** as mensagens e o
resultado, os encaminhamentos ao WhatsApp e possíveis erros. Usar
amostras de conversas para medir resposta correta e resolução; o contador
de respostas não comprova resolução. Não registrar como concluído um
pagamento, reserva ou atendimento humano só porque foi enviado um link.

## Custo e manutenção

Plano **Starter gratuito**, sem cartão ou contratação. A conta mostrou
**1 de 100 conversas mensais usada** após o teste. A cota é da conta do
proprietário e pode ser compartilhada com outros agentes que ele criar.
Ao atingir a cota, o fornecedor para de responder até a renovação ou troca
de plano. Não contratar nem prometer cobertura mensal integral sem medir
o volume e apresentar o custo adicional.

Conferir o consumo pelo avatar do proprietário no Jotform, manter a
conexão do Instagram autorizada e atualizar a entrada de conhecimento
quando a casa mudar informações. Nenhuma rotina recorrente de revisão foi
criada. A análise histórica de seis meses continua com os limites e os
22 registros locais descritos em `../ATENDIMENTO_INSTAGRAM.md`; a ativação
não envia respostas retroativas a todo o acervo.

Fontes oficiais consultadas em 01–02/11/2026:
[Instagram Agent](https://www.jotform.com/ai/instagram-agent/),
[preços e limite de uso](https://www.jotform.com/ai/instagram-agent/pricing/),
[esclarecimento do suporte sobre Starter](https://www.jotform.com/answers/32500571-account-agents-limit-clarification-on-counting-ai-setups-and-topics).
Conta, cota, configurações e entrega foram conferidos na interface em
02/11/2026. As condições comerciais futuras precisam de nova consulta.
