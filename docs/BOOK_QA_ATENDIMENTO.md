# Book de perguntas e respostas: atendimento no Instagram

Base: exportação do Direct do @sirfisherfc de 28/09/2026. São 2.056 conversas; 1.327
têm texto de cliente (3.397 mensagens), de setembro de 2023 a setembro de 2026. As
conversas originais ficam só no OneDrive. Este arquivo não tem nome nem telefone de
cliente.

Serve para três coisas:

1. Resposta pronta para quem atende o Direct hoje.
2. Texto das automações nativas do Instagram (perguntas frequentes e respostas
   por palavra-chave).
3. Base de conhecimento do robô de atendimento, quando a Meta liberar o acesso.

As respostas foram confirmadas pelo Rogério em 28/09/2026. As regras de reserva
vêm da configuração do sistema de reservas: corte do mesmo dia às 15h30, até 10
pessoas, até 60 dias de antecedência, tolerância de 15 minutos. Se a configuração
mudar no painel, atualizar aqui. Os fatos batem com o Perfil do Google
([ROTINA_PERFIL_GOOGLE.md](ROTINA_PERFIL_GOOGLE.md)).

Revisão de 25/10/2026: as respostas abaixo incorporam o cardápio próprio e
os destinos atuais de eventos e Réveillon. A leitura pública da configuração
de reservas confirmou os limites acima e o WhatsApp corporativo. Grupos de
11 a 29 pessoas seguem para atendimento; eventos de 30 a 100 pessoas sentadas
usam o configurador, com confirmação da equipe. Os números de conversas e os
problemas descritos a seguir pertencem à exportação até setembro de 2026.
A implantação das respostas e o tempo de atendimento atual ainda precisam
ser conferidos nos canais; esta revisão atualiza a documentação.

Revisão para o assistente virtual em 01/11/2026: o proprietário confirmou o
WhatsApp corporativo acima e o acesso nativo da gerente. A orientação atual
retira horário de atendimento humano e promessa de prazo. Configuração e testes do agente
estão registrados em [ATENDIMENTO_INSTAGRAM.md](ATENDIMENTO_INSTAGRAM.md).
Para carregar a base em uma IA, usar os textos e limites de
[instagram-atendimento/CONHECIMENTO.md](instagram-atendimento/CONHECIMENTO.md).
As respostas deste book que dependem de ação da equipe exigem encaminhamento
registrado; informar o resultado somente depois de verificá-lo.

O proprietário reconfirmou em 01/11/2026: a casa não tem happy hour, permite
levar bolo sem taxa e recebe currículos em `sir.fisher@outlook.com`.
Também confirmou aceitação de VR, Alelo, Ticket e Sodexo/Pluxee, sem informar
restrições. Outros benefícios e aplicativos conservam suas fontes anteriores.
Quatro FAQs fixas foram salvas e ativadas no Instagram, com os textos exatos
na seção de automações abaixo. A nova regra restrita de reserva permanece
desligada. O aplicativo conferido pelo proprietário não apresentou a IA nativa.

## O que as conversas mostram

**Assuntos mais frequentes**, em número de conversas nos três anos:

| Assunto | Conversas |
|---|---|
| Reserva | 271 |
| Horário, se abre hoje | 202 |
| Cardápio e preços | 181 |
| Réveillon | 118 |
| Promoções e happy hour | 118 |
| Almoço executivo e terça em dobro | 87 |
| Música, DJ, transmissão de jogo | 83 |
| Mesa com vista do pôr do sol | 74 |
| Grupos, confraternizações, eventos | 70 |
| Prospecção (influenciador, fornecedor) | 67 |
| Pagamento (vale-refeição, Fortal em Dobro, Prime, Duo Gourmet) | 65 |
| Aniversário e bolo | 49 |
| Delivery | 43 |
| Pet | 34 |
| Currículo | 32 |

**Perguntas sem resposta de uma pessoa.** Conta as conversas com pergunta real, sem
prospecção e spam, que receberam só a resposta automática ou nenhuma.

| Ano | Perguntas | Sem resposta de pessoa |
|---|---|---|
| 2023 | 161 | 29% |
| 2024 | 428 | 29% |
| 2025 | 253 | 64% |
| 2026 | 142 | 49% |

### Problemas encontrados

1. **A automação atual responde sem responder.** Em 2025, 46 conversas receberam
   "Ficou com alguma dúvida? Estamos à disposição, é só chamar!" como resposta a
   perguntas diretas, como "precisa reservar?", "é por casal ou por pessoa?" e
   "quero cancelar minha reserva". O cliente respondeu "sim" ou "?" e ficou sem
   retorno.
2. **O horário da resposta automática está desatualizado.** O Direct responde
   "todos os dias das 9h às 23h, inclusive feriados". O Perfil do Google diz 9h às
   22h15 de domingo a quinta e 9h às 23h sexta e sábado, fechado em 24 e 25/12.
   Em maio/2026 houve reclamação de cliente que chegou 22h50 e não foi atendido.
3. **O réveillon vai para o celular pessoal.** De 2023 a 2025 o réveillon foi
   encaminhado para um número pessoal antigo. A regra é usar sempre o corporativo
   (85) 98854-4274. Em dezembro de 2025 houve cliente dizendo que o número não
   respondia.
4. **Link que não abre.** O PDF do réveillon estava no OneDrive; vários clientes
   disseram que não conseguiam abrir. Usar página no site ou imagem no destaque do
   perfil.
5. **Regra de reserva diferente a cada resposta.** Reserva para o mesmo dia "até
   14h", "até 14h30" e "até 15h"; tolerância de 20 minutos. A regra única agora
   é a do sistema: mesmo dia até 15h30, tolerância de 15 minutos.
6. **Grupo acima de 10 pessoas mandado para o WhatsApp, que não respondia.** Houve
   pelo menos 4 casos de grupos de 14 a 35 pessoas que voltaram ao Direct dizendo
   que o WhatsApp não respondeu.
7. **Spam de "plataforma de jogos PG" e golpe de influenciador.** Esse spam é
   frequente desde 2025 e chega até em grupos criados para o perfil. A triagem
   atual de mensagens novas está definida abaixo; bloqueio ou exclusão não fazem
   parte da automação.

## Triagem de spam para mensagens novas

Regra de 01/11/2026: spam inequívoco fica sem resposta e sem uso de IA. O
conteúdo permanece no Instagram. A integração verifica assinatura/ativos e
aplica o filtro antes de gravar tarefa, criar caso ou reservar aviso de WhatsApp.
O texto e o MID do evento filtrado não entram na fila; somente a contagem
agregada de eventos ignorados é registrada. Essa contagem pode incluir
reentregas e não representa pessoas únicas ou pedidos resolvidos.

Os sinais fortes cobrem falsa verificação da Meta com ameaça à conta e pedido
de ação, venda direta de seguidores/curtidas, convite de apostas com bônus,
promessa de multiplicar dinheiro por Pix e correntes com recompensa. Há padrões
conservadores em português e inglês. Uma palavra como “link”, “desconto”,
“pagamento” ou “urgente” isolada não basta para descartar.

O relato do cliente tem prioridade: “recebi esse golpe, é de vocês?”, cobrança
contestada, reclamação própria, urgência real e pedido de pessoa seguem o fluxo
de atendimento. O trecho de uma ameaça copiada pelo cliente não vira urgência
médica só porque contém “urgente”. No golpe inequívoco, “fale com nosso atendente”
é parte da oferta e não equivale a um pedido do cliente. Cardápio, reserva,
currículo, fornecedor e proposta comercial comum continuam elegíveis, inclusive
quando incluem link. Um caso duvidoso segue para conferência humana.

Para atendimento manual, leia a mensagem recente e seu contexto antes de
classificar. Ignore a oferta claramente indesejada e preserve o histórico;
não envie respostas de cortesia, não abra links de verificação e não peça dados
ao remetente. Uma proposta legítima ou relato de golpe precisa de leitura da
equipe. Use as fontes oficiais da casa e o WhatsApp já confirmado quando houver
pedido de atendimento humano. Não bloquear ou excluir mensagens por esta regra.

O filtro tem limites: mídia sem texto, outras línguas, grafias disfarçadas e
mensagens ambíguas podem seguir ao atendimento. Ele não lê todo o histórico do
Instagram nem demonstra uma taxa de cobertura. Echo de resposta humana e
cancelamento de envio preservam seus protocolos. A regra fica no código em
nuvem e nestes documentos; não depende da sessão de Chrome ou deste computador.
O agente continua restrito à conta de teste enquanto a produção aguarda liberação.

## Respostas prontas

Tom: próximo e curto, como o perfil já fala ("Olá, tudo bem? ☺️"). Uma pergunta,
uma resposta; sem mandar para o link da bio quando a resposta cabe na mensagem.

### Reservas

**Precisa reservar?**
> Não é obrigatório! Parte das mesas fica para reserva e o restante é por ordem de
> chegada. Nos fins de semana e feriados, entre 16h e 18h (pôr do sol), a casa
> costuma encher, então vale reservar: reservas.sirfisher.com.br

**Como reservo?**
> Até 10 pessoas, direto pelo site: reservas.sirfisher.com.br. A confirmação chega
> na hora. Para 11 a 29 pessoas, fale com a gente no WhatsApp (85) 98854-4274
> com data, horário e número de pessoas. Para eventos de 30 a 100 pessoas
> sentadas, consulte www.sirfisher.com.br/eventos/; a equipe confirma a proposta.

**Consigo mesa de frente para o mar / para o pôr do sol?**
> Escreva o pedido no campo de observação da reserva. A equipe confere as mesas
> disponíveis no dia. A escolha da mesa depende dessa disponibilidade.

**Não tem horário disponível no site para hoje.**
> Reservas para o mesmo dia vão até as 15h30. Depois disso, ou se os horários já
> estiverem lotados, atendemos por ordem de chegada, conforme a disponibilidade.

**Com quanta antecedência posso reservar?**
> Até 60 dias antes, pelo site: reservas.sirfisher.com.br

**Quero mudar ou cancelar minha reserva.**
> Para cancelar, use o link recebido no e-mail da reserva. Para alterar ou se
> precisar de ajuda com o cancelamento, fale com a equipe no WhatsApp
> (85) 98854-4274.
> *(O assistente só confirma alteração ou cancelamento após verificar o
> resultado no sistema. Um nome informado no Direct não autoriza consultar
> ou divulgar dados da reserva.)*

**Qual a tolerância de atraso?**
> Seguramos a mesa por 15 minutos depois do horário da reserva. Se for atrasar
> mais, avise por aqui ou no WhatsApp (85) 98854-4274.

### Horário e funcionamento

**Qual o horário? / Abre hoje? / Abre no feriado?**
> Abrimos todos os dias, inclusive feriados: das 9h às 22h15 de domingo a quinta e
> das 9h às 23h na sexta e no sábado. Só fechamos em 24 e 25 de dezembro.

**Fecha depois do almoço?**
> Não, funcionamos direto, sem pausa.

**Até que horas a cozinha atende?**
> A cozinha fecha às 22h. Depois disso servimos só bebidas até o fechamento.

**Onde fica?**
> Na Av. Beira Mar, 3421, na altura do Náutico, em frente ao Jardim Japonês.

**Tem estacionamento?**
> Não temos estacionamento próprio (nenhum quiosque da orla tem). Há vagas na rua,
> gratuitas e Zona Azul. As ruas do Jardim Japonês e a do hotel ao lado costumam
> ter vaga.

### Cardápio e comida

**Onde vejo o cardápio e os preços?**
> O cardápio está em www.sirfisher.com.br/cardapio/. Você também pode trocar
> para inglês na página.

**Servem almoço? E jantar?**
> Servimos o dia todo. O almoço executivo é de segunda a sexta, das 10h às 14h,
> com sete opções individuais. Nos fins de semana e à noite há os pratos para
> dividir, os petiscos e os sanduíches.

**Qual o valor do executivo? / Tem executivo no sábado?**
> O executivo é só de segunda a sexta, das 10h às 14h. As opções e os valores
> estão em www.sirfisher.com.br/almoco-executivo/.

**Os pratos para dividir servem quantas pessoas?**
> Em média 2 pessoas.

**Tem opção vegetariana?**
> Consulte o cardápio em www.sirfisher.com.br/cardapio/. A equipe pode conferir
> os ingredientes e o preparo com a cozinha antes do pedido.

**Tenho alergia / restrição alimentar.**
> Por segurança, fale diretamente com o gerente quando chegar. Ele confere com a
> cozinha o preparo de cada prato.
> *(Nunca garantir nada por mensagem.)*

**Tem chope? Cerveja sem álcool?**
> Temos chope, sim! E cerveja sem álcool: Corona Zero.

**A casa vende vinho? Posso levar o meu?**
> Pode trazer! Não cobramos taxa de rolha para vinhos e espumantes. Só não temos
> balde de gelo nem taças para vinho, então traga os seus se quiser. Para
> destilados e cervejas trazidos de fora, cobramos taxa de rolha.

**Posso levar bolo?**
> Pode levar bolo, sem taxa. Para outros alimentos e para organizar a
> comemoração, fale com a equipe.
> *(Bolo sem taxa reconfirmado pelo proprietário em 01/11/2026. A regra de
> outros doces e salgados tinha confirmação de 28/09 e exige conferência atual.)*

### Promoções

**Ainda tem a terça em dobro?**
> Tem sim! Toda terça-feira, exceto feriados, das 11h às 14h: na compra de um
> executivo, o segundo igual sai por nossa conta. Vale para consumo no local, com
> duas pessoas e pratos iguais.

**A taxa de serviço na terça em dobro é sobre o valor cheio?**
> Sim. O desconto é da casa, mas o atendimento continua sendo de dois pratos. Por
> isso os 10% são calculados sobre o valor dos dois pratos. A taxa de serviço é
> opcional.
> *(Já gerou reclamação: vale avisar no cardápio e no post da promoção.)*

**Tem a quarta do camarão?**
> Tem sim! Toda quarta-feira.
> *(Os detalhes, como pratos, horário e valor, estão no post fixado. Se o cliente
> pedir mais, encaminhar para uma pessoa até a regra entrar neste book.)*

**Aceitam Fortal em Dobro?**
> Aceitamos todos os dias, exceto feriados e datas comemorativas com menu
> especial (como o Dia dos Namorados). O segundo prato tem que ser igual ao
> primeiro. A cozinha fecha às 22h.
> *(Condições confirmadas pelo proprietário em 28/09/2026; conferir aceitação
> e condições atuais antes de publicar resposta automática.)*

**Aceitam Prime Gourmet? Duo Gourmet?**
> Aceitamos os dois! As condições de cada um estão no aplicativo.

**Tem happy hour? Tem outra promoção?**
> Não temos happy hour. A terça em dobro do executivo segue as condições
> acima. Para outras promoções, a equipe confere a oferta atual.
> *(Ausência de happy hour reconfirmada pelo proprietário em 01/11/2026.)*

**Aniversariante ganha alguma coisa?**
> Ganha! No dia do aniversário, é só avisar a equipe e mostrar um documento com foto
> para receber um drink especial.

### Pagamento

**Aceitam cartão? Pix?**
> Aceitamos cartão de crédito, débito e Pix.

**Aceitam vale-refeição (VR, Alelo, Sodexo/Pluxee, Ticket)?**
> Aceitamos VR, Alelo, Ticket e Sodexo/Pluxee.
> *(Aceitação confirmada pelo proprietário em 01/11/2026, sem informar
> restrições. Não generalizar para outros benefícios ou aplicativos.)*

### Ambiente

**Tem música ao vivo?**
> A programação depende da data. No Réveillon de 31/12/2026, a página oficial
> informa DJ e cantor ao vivo. Para outro dia, a equipe confere a programação.
> *(A resposta sobre dias comuns foi confirmada em 28/09/2026. A antiga
> justificativa de proibição na Beira-Mar não tem fonte oficial nesta base.)*

**Vão transmitir o jogo?**
> A informação confirmada em 28/09/2026 é que a casa não tem TV nem transmite
> jogos. A equipe pode conferir se houve mudança.

**Aceitam pet?**
> Somos pet friendly! 🐶 Pets são bem-vindos na área externa.

**Pode criança? Tem banheiro? Tem wi-fi?**
> Crianças são bem-vindas, temos banheiro e wi-fi. É só pedir a senha à equipe.

**Tem cadeira na areia?**
> Não, o atendimento é só no quiosque.

**Posso fazer fotos ou ensaio aí?**
> Pode sim, não cobramos. Só avise a equipe ao chegar.

**Delivery? iFood?**
> Nosso delivery é pelo 99Food. Não estamos no iFood.

### Grupos, aniversários e eventos

**Quero comemorar aniversário / fazer confraternização.**
> Que ótimo! Até 10 pessoas, reserve pelo site: reservas.sirfisher.com.br. Para
> 11 a 29 pessoas, chame no WhatsApp (85) 98854-4274 com a data, o horário e o
> número de pessoas. Para 30 a 100 pessoas sentadas, consulte as opções em
> www.sirfisher.com.br/eventos/; a equipe confirma a proposta.
> *(Grupo grande deve ter retorno no mesmo dia. Ver problema 6.)*

**Vocês fecham o espaço para evento ou casamento?**
> Consulte www.sirfisher.com.br/eventos/ para montar uma proposta de 30 a 100
> pessoas sentadas. A equipe confirma data e condições. Para outras necessidades,
> fale no WhatsApp (85) 98854-4274 com data, horário, número de pessoas e tipo
> de evento.

**Pedido de casamento, surpresa, flores.**
> Que lindo! Faça a reserva e nos avise o horário: a equipe prepara a melhor mesa
> possível. O espaço para guardar flores é pequeno, então o ideal é trazer o buquê
> pouco antes do pedido. Se quiser, entregamos as alianças na mesa.

**Réveillon.**
> As informações do Réveillon estão em www.sirfisher.com.br/reveillon/.
> A página leva à consulta e à pré-reserva de mesas. Para dúvidas sobre a
> proposta e o pagamento, fale no WhatsApp (85) 98854-4274.

### Outros

**Esqueci um objeto aí.**
> A equipe precisa conferir o objeto no restaurante. Você pode falar com a
> gerente pelo WhatsApp (85) 98854-4274 e informar o objeto, o dia e o horário
> da visita.
> *(Quando houver fila integrada e o caso estiver registrado, informar que
> foi encaminhado. A equipe acompanha e encerra a pendência.)*

**Vagas / currículo.**
> Obrigado pelo interesse! Envie seu currículo para sir.fisher@outlook.com.
> *(Endereço reconfirmado pelo proprietário em 01/11/2026; não comprova vaga aberta.)*

**Parceria / influenciador / permuta.**
> Obrigado por pensar no Sir Fisher! No momento não estamos fazendo parcerias nem
> permutas, mas guardamos o seu contato para uma próxima oportunidade.

**Fornecedor / prestador de serviço.**
> Obrigado pelo contato! Pode enviar a apresentação para sir.fisher@outlook.com.

## Casos que sempre vão para uma pessoa

A automação nunca responde sozinha a:

- **Reclamação de atendimento ou de cobrança.** Acolher e encaminhar para a
  gerente. Um sócio pode ser envolvido pela equipe. Voucher só por decisão do
  Rogério. O assistente informa apenas o encaminhamento que conseguiu registrar;
  a equipe decide sobre ligação, compensação e estorno.
- **Alergia ou restrição alimentar.**
- **Grupo acima de 10 pessoas, evento, casamento, réveillon.**
- **Objeto esquecido.**
- **Mudança ou cancelamento de reserva.**
- **Imprensa e produtoras.**

## Automações nativas do Instagram

**Perguntas frequentes do Direct:** quatro perguntas salvas e ativas no
Instagram em 01/11/2026. A configuração anterior foi reaberta após recarga,
com Instagram selecionado e estado Ativado. Os textos atuais abaixo seguem
a orientação de retirar horário humano; a coordenação confere a atualização
na interface separadamente. Prévia e persistência da configuração
não substituem teste por conta externa.

1. **Qual o horário e o endereço?**

   > Sou o assistente virtual do Sir Fisher 😊 Abrimos dom–qui, 9h–22h15; sex–sáb, 9h–23h. Estamos na Av. Beira Mar, 3421, Meireles, em frente ao Jardim Japonês. Em 2026, fechamos 24 e 25/12. Para datas especiais, consulte a equipe. Rota: https://www.sirfisher.com.br/como-chegar/

2. **Onde vejo o cardápio?**

   > Sou o assistente virtual do Sir Fisher 😊 Cardápio: https://www.sirfisher.com.br/cardapio/ Executivo: https://www.sirfisher.com.br/almoco-executivo/ (seg–sex, 10h–14h, exceto feriados). A equipe confirma preços, porções e ingredientes. Para atendimento humano: https://wa.me/5585988544274

3. **Como falo com uma pessoa?**

   > Sou o assistente virtual do Sir Fisher 😊 O atendimento humano é pelo WhatsApp oficial: https://wa.me/5585988544274 Abra o link e envie sua mensagem por lá para a equipe conferir seu pedido.

4. **Como reservo ou faço evento?**

   > Sou o assistente virtual do Sir Fisher 😊 Até 10 pessoas: https://reservas.sirfisher.com.br/ A reserva depende da conclusão e confirmação no portal. Para hoje, o corte é 15h30; tolerância de 15 min. Para 11–29 pessoas, fale com a equipe: https://wa.me/5585988544274 Eventos de 30–100 pessoas: https://www.sirfisher.com.br/eventos/ A equipe confirma a data e a proposta.

As FAQs são respostas fixas. O link de WhatsApp inicia outra conversa;
não transfere o histórico nem avisa a equipe por si só. Não informar horário
humano ou prometer prazo de resposta. A atualização da cópia nativa é conferida
separadamente pela coordenação; os horários da casa permanecem válidos.

No agente em nuvem, indicar WhatsApp mantém a próxima FAQ elegível no
Instagram. Um caso ativo recebe um aviso; pedidos repetidos não repetem o
link. O aviso sensível pendente vem antes da FAQ. Pausas manuais, echo sem
origem reconciliada e envio incerto conservam o bloqueio até conferência e
retomada explícita. Encerrar o caso preserva a pausa que estiver vigente.

**Regra de reserva:** o Instagram foi retirado da regra antiga, preservada
no Messenger. Uma nova regra restrita ao Instagram foi salva, conserva
15 minutos de inatividade e ficou desligada. Falta teste por conta externa
e validação de resposta duplicada e pausa no atendimento humano antes de
ativar. O agente nativo de IA não apareceu no aplicativo conferido pelo
proprietário. Acompanhamento manual com Hêmile foi conferido em cinco casos;
transferência automática por pedido de humano não foi configurada.
O proprietário decidiu que a IA responde às dúvidas no Instagram e os pedidos
humanos seguem por link ao WhatsApp. Os textos 2 e 3 acima foram salvos e
reabertos com Instagram ativo; o Messenger foi preservado. Antes de liberar
a IA para clientes, desligar as respostas nativas que duplicarem esse fluxo.

**Proposta de palavras-chave:** a tabela abaixo é uma referência antiga,
não uma lista de regras implantadas. Palavras amplas podem alcançar
reclamações e pedidos de cancelamento; não ativar o conjunto sem revisão.

| Palavras | Resposta |
|---|---|
| reserva, reservar, mesa | Como reservo? |
| horário, abre, aberto, funciona | Horário |
| cardápio, menu, preço, valor | Cardápio |
| pet, cachorro | Pet |
| estacionamento, estacionar | Estacionamento |
| onde fica, endereço, localização | Onde fica |
| terça, dobro | Terça em dobro + Fortal em Dobro |
| camarão, quarta | Quarta do camarão |
| happy, promoção | Happy hour / promoções |
| rolha, vinho, espumante | Rolha |
| bolo, aniversário | Bolo + aniversariante |
| vr, vale, alelo, sodexo, pluxee, ticket | Vale-refeição |
| delivery, entrega, ifood, 99 | Delivery |
| jogo, tv, transmitir | Jogo |
| música, ao vivo | Música |

**Conferir a mensagem "Ficou com alguma dúvida?".** Na exportação de setembro,
ela era enviada pelo ManyChat como resposta a perguntas diretas. A proposta é
substituí-la por uma resposta útil e encaminhar os casos que exigem uma pessoa.
Verificar a configuração atual antes de alterar; este book não comprova que a
automação tenha sido desligada ou substituída.
