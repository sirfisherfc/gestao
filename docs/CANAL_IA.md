# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Gestao e reservas liberados após correção de mensagens canceladas (`5f6a80a`/`85abd70`). TEST exclusivo da conta controlada e único cron ativos; clientes bloqueados. Site tem responsável próprio.

## Protocolo
- **Ao começar uma tarefa:** ler este arquivo. As mensagens mais recentes ficam **no fim**.
- **Linha 🚦 Status (topo):** ao **começar**, marque 🔴 + sua área/arquivos + commit-base; ao **terminar**, volte para 🟢 livre. É a resposta rápida para "posso mexer agora?". Se estiver 🔴 de outra IA sem sinal de conclusão, parar e confirmar com o Rogério.
- **Ao terminar / entregar:** acrescentar uma mensagem curta no fim, no formato `## AAAA-MM-DD · <autor> — <assunto>`, dizendo **o que mexeu**, **o que ficou pendente** e qualquer coisa que a outra precise saber. Handoff inclui: arquivos alterados · migration criada (nº) e se aplicou · validações rodadas · estado do deploy · pendências/riscos.
- **Mantenha o canal enxuto:** guarde só a linha 🚦 Status + os **últimos ~3 recados**; pode podar os mais antigos ao deixar um recado novo (o `git` preserva tudo — `git log`/`git diff` recuperam o histórico). O que for regra durável vai para o `AGENTS.md`, não fica aqui. Assim a leitura custa ~o mesmo sempre.
- Isto **não substitui** o `AGENTS.md` (regras canônicas) nem os commits — é o "recado rápido" entre nós.
- Combinados fixos já viraram regra no `AGENTS.md` (checar `ls supabase/migrations/` antes de criar migration; migrations idempotentes; uma IA por vez na mesma branch).

---

**PENDÊNCIA aberta:** migration `20260738000000_cartao_credito_entra_dre_temporario.sql` (2026-07-07) é declaradamente temporária — a fatura de cartão BTG entra na DRE só nas fontes vivas até existir uma fonte de ETL com as compras itemizadas do BTG; quando essa fonte existir, reverter `entra_dre` para a expressão de `20260735000000` (senão a despesa duplica). Ver detalhes no `git log`/na própria migration.

**PENDÊNCIA aberta:** os R$462 mil em despesa na categoria `ANALISAR INDIVIDUAL` (134 lançamentos, 2022–2025) precisam de classificação manual. A migration `20260748000000` (2026-07-14) deixou essa categoria dentro da DRE de propósito, com carve-out explícito, por não haver confirmação de que sejam não-operacionais. Boa parte é Pix para "SIR FISHER COMERCIO DE ALIMENTOS LTDA" e para os sócios; vale investigar se são retirada/pró-labore, empréstimo entre empresas do grupo, ou despesa real mal categorizada.

## 2026-11-01 · Codex — Callback e orçamento do atendimento em nuvem

Atualizados `docs/ATENDIMENTO_INSTAGRAM.md` e a base
`docs/instagram-atendimento/CONHECIMENTO.md`. A Edge Function e a fila
privada estão implantadas com o agente em `off`; a gerente foi configurada.
Callback HTTPS e objeto Instagram do app conferidos com `messages` ativo.
A releitura da Página encontrou apenas `name`; POST autorizado corrigiu
para `messages,name`, preservando o campo original, com HTTP 200 e GET de
retorno. O proprietário acessou o painel autenticado, consultou
o estado e alternou a pausa global mantendo `off`; a pausa foi restaurada
para `true`. Isso não comprova recebimento ou envio de DM.

O teste real com a conta controlada do proprietário foi autorizado. A tela
de Webhooks informava entrega apenas de eventos dummy antes de Live,
enquanto Messenger descrevia papéis de desenvolvimento. O proprietário
autorizou publicar o app: Live confirmado após releitura e aviso dummy-only
removido. A URL de instruções de exclusão também persistiu após recarga.
O agente continua em `off`. Nos primeiros testes, mensagens controladas
enviadas após Live e a correção da Página não apareceram como POST da Meta
ou evento na fila no intervalo conferido. O primeiro recebimento real foi
validado depois, conforme registro abaixo. Meta Review/Advanced Access não comprovados;
necessidade para produção a confirmar no contrato e no caminho real.
O Depurador de Webhooks oficial confirmou campos do app e da Página,
conta vinculada e Gerenciar Mensagens ativado. O token original vinha de
System User; um Page token foi gerado no fluxo oficial com usuário humano.
App, Página e Instagram corresponderam; Conversations retornou o mesmo
HTTP 400/-2/2534084, com `error.message=Timeout` e título de tempo limite.
Esse erro não comprova ausência de Advanced Access; interpretação anterior
corrigida. Candidato humano não aplicado no servidor por não conter
`pages_read_engagement` exigida pela consulta de perfil do painel.
Diagnóstico sem causa definida. Rascunho de solicitação de
`instagram_manage_messages` preparado, sem envio ou mudança de acesso.
O vínculo empresarial da Página foi confirmado como verificado. A tela
oficial de Verificação do App também mostrou 100%, com DeathStar no
portfólio Sir Fisher e estado Verificado, sem alteração de vínculo. No Centro
de Contas aberto pelo Instagram pessoal do teste, apareceu somente um
perfil Instagram, sem Facebook listado. Uma tentativa de adicionar
Facebook abriu SSO nativo e aviso de acesso pessoal; parou antes de
autorizar. Depois o proprietário autorizou a associação entre os dois
perfis do teste e as opções finais de dados e anúncios exibidas. O clique
para permitir e concluir retornou erro da Meta, e o Centro de Contas
continuou com apenas um perfil Instagram nessa tentativa. Depois, o fluxo
oficial a partir do Facebook concluiu a associação dos mesmos dois perfis
autorizados; o vínculo persistiu após recarga. Uma nova DM da conta
controlada gerou o primeiro POST real confirmado: HTTP 200, um evento e
uma conversa gravados às 10h08min41s UTC pelo relógio do banco. O envio
ocorreu aproximadamente às 10h07 UTC na interface; diferença de cerca de
85 segundos entre relógios impede inferir latência precisa. GET único da
User Profile API retornou 200 e username exato do proprietário, sem
versionar perfil ou identificador. O recebimento ocorreu após concluir o
vínculo, sem demonstrar uma causa universal para outras contas. Modo
`off`, pausa global e bloqueios de IA, faturamento, alertas e cron
preservados. Lista restrita para o teste real ainda não aplicada; nenhuma
resposta automática enviada.
O guia oficial do Depurador, de 26/06/2026, relaciona esse vínculo aos dados
usados na amostra de depuração, em vez de usuário aleatório. Recomenda
TraceID em suporte se a amostra não chega mesmo com configuração correta.
Não foi encontrado prazo oficial de propagação; não prometer espera fixa.
Categoria de negócios e páginas salva no app. Ícone pendente. A autorização
para acesso temporário a arquivos não foi executada: a política do navegador
bloqueou `chrome://extensions` por aceitar apenas HTTP e HTTPS. Nenhuma
permissão foi ativada e não haverá tentativa de contornar esse bloqueio.
Prevista seleção manual do logo pelo proprietário na própria Meta após
preparar o formulário. As referências
oficiais Application Picture/Application v26.0 não oferecem upload de ícone
por POST documentado; nenhuma chamada de escrita experimental foi feita.
Nenhum novo aceite jurídico foi dado.
Fonte específica de Webhooks do Messenger para Instagram, atualizada em
28/10/2026, confirmou `object=instagram` e separa publicação, outorga de
permissões, função no app e dados próprios/administrados. Não foi alterado
o filtro para objeto Page nem inferida dispensa geral de análise para
clientes. O primeiro POST real foi validado sem ampliar o filtro do receptor.
Conferência somente de leitura dos ativos de Hêmile confirmou acesso total
à Página e acesso parcial ao Instagram com Mensagens. O indicador de
inatividade era de última atividade; não era prova de falta de permissão.
Isso comprova acesso ao atendimento nativo, sem comprovar leitura de casos,
resposta no horário ou dias de acompanhamento ainda não confirmados.
Consulta visual de roteamento mostrou só controles de Messenger e um app
de listagens locais; nada foi alterado e isso não comprova a causa da falha.
Não foram aplicados protocolos de controle antigos ou assinatura de espera.
Comentários e Stories
seguem com cobertura a validar. Quatro FAQs nativas permanecem
ativas e a regra de palavras-chave do Instagram permanece desligada.

O AI Studio exibiu Nível 1/pré-pagamento no projeto padrão vinculado à chave
em uso, com correspondência conferida em memória. A pergunta sintética ao
classificador retornou HTTP 200, `HOURS`, 297 tokens de entrada, dois de
resposta e zero de pensamento, 299 totais. Nenhuma conversa de cliente foi
enviada. O widget do saldo permaneceu carregando; não há valor de créditos
comprovado nem alteração de faturamento. Autorização atual para teste com o
proprietário não libera processamento geral de textos de clientes.

Leituras oficiais confirmaram Supabase Free, sem adicionais selecionados.
As 500 mil invocações Edge mensais são compartilhadas pela organização;
saldo mensal não conferido. Free admite pausa após sete dias sem atividade
e não tem SLA de disponibilidade. O teto do agente é R$45/mês, com limite
adicional de 2.000 gerações reservadas a dois centavos, até R$40. A margem
de R$5 sobre o teto do agente preserva o orçamento total de R$50; outros
usos da mesma chave Google não entram nesse controle.

A política do site foi atualizada e publicada em `a62d621`, com Paid
conferido, agente desligado, retenção real, limites da remoção de
identificadores e pedido manual de exclusão em
`https://www.sirfisher.com.br/privacidade/#exclusao-dados`. Duas verificações
de CI aprovadas e HTTP 200. Username e links de perfil do painel foram
implementados e publicados em reservas, commit `b119600`, com build
aprovado; GET do remetente real validado, apresentação do caso no produto
ainda pendente. Sem avatares.
Na última conferência manual, 118 pessoas receberam resposta, com quatro
complementos em conversas já contadas, e 13 grupos foram excluídos. Sete
pendências de identificação: seis registros anônimos e um sem identidade
verificada após recuperar seis conversas nativas. A cobertura permanece
parcial; há mensagens antigas por revisar. Fechamento ainda em conferência.
O balanço da primeira rodada permanece identificado como histórico, sem
somá-lo de novo.
Nenhum perfil pessoal, IGSID, UUID, e-mail privado ou identificador de chave
foi incluído nesta atualização. Commit dos documentos aguarda os resultados
do teste restrito e o fechamento pela raiz.

— Codex

## 01/11/2026 — aviso único para WhatsApp e teste restrito

O proprietário definiu IA para dúvidas no Instagram e atendimento humano
pelo WhatsApp oficial 5585988544274, das 7h às 21h. As FAQs nativas 2 e 3
foram atualizadas, reabertas e conferidas pela coordenação. O BOOK reproduz
os textos salvos. Os acessos existentes da gerente permanecem preservados;
o assistente fica sem responsável padrão e sem avisos por e-mail.

Nova migration `20261101102855_instagram_support_whatsapp_notice.sql` e
backend preparam um único aviso revisado por caso ativo, sem IA: gravam caso
e pausa antes, orientam abrir o WhatsApp e enviar a mensagem por lá. O painel
mostra o estado do envio no Instagram; não comprova atendimento no WhatsApp.
Repetições ficam sem outro aviso. Urgência antes do POST atualiza a orientação
e invalida o lease anterior. Echo, pausa global, assumir, encerrar e retomar
cancelam avisos pendentes; envio incerto não se repete automaticamente.

Validação local: 40 testes Node do atendimento/painel, oito do instalador
OFF, oito do helper restrito e 26 testes reais PostgreSQL18. Incluem o pedido
literal «Como falo com uma pessoa?» sem modelo e a pausa global durante a IA.
Revisão independente aprovada e implantação OFF concluída. Gestao `613d6a0`,
reservas `281e2e7`, migration `20261101102855` registrada atomicamente e Edge 7
ACTIVE, com 28 segredos preservados. Health 200 confirmou OFF real, pausa ativa,
dados e alertas false; anônimo/segredo errado 403; vazio assinado 200/zero eventos;
assinatura inválida 401. Security Advisor sem WARN/ERROR do atendimento;
funções dos outros sistemas preservadas. O helper --check real confirmou
remetente único e perfil exato. Nenhum drain ou Direct foi enviado.
O helper TEST aguarda revisão
separada antes de aplicar; exige remetente único privado, inbound assinado,
Profile API com username exato e os limites de R$45 + R$5 de margem.
Após esse `--check`, a coordenação autorizou e foi aplicado TEST para uma
única conta controlada. Health confirmou TEST efetivo, dados aprovados somente
no teste, listas e interseção de uma conta e pausa global false. Limites R$45/
2.000 gerações/2 centavos e validade de 30 dias conferidos. Leitura inicial:
zero outbox/modelo/casos/bootstrap pendente; o helper não chamou drain.
Depois, a primeira FAQ nova gerou HOURS, sent/MID confirmado pela Meta,
298 tokens de entrada e dois de saída. Uma chamada/um envio, sem caso e sem
pausa humana. Os outros cenários reais continuam em teste.
O teste seguinte de cozinha reprovou HOURS. O agente foi fechado em OFF,
com histórico e custo preservados. Correção `9afafed`, revisada e 57 Node verdes,
força UNKNOWN antes de chamar o modelo para cozinha/último pedido sem fonte.
Implantação OFF e novo check aprovados; TEST reaberto para a mesma conta.
Reteste real: UNKNOWN, sent/MID confirmado, 4,550s e zero nova chamada de IA.
Reserva para quatro passou com portal/corte/tolerância, sem confirmar mesa.
Pedido humano criou caso+pausa e enviou um único WhatsApp sem IA; reclamação
seguinte manteve o caso e não duplicou resposta. Painel mostrou perfil verificado
e estado do link. Encerrar/retomar foram ações separadas sem replay. A resposta
manual da Meta Suite gerou echo e nova pausa. Os dois casos de teste foram
fechados, sem registrar reclamação real como resolvida.

O Vault recebeu um único segredo limitado do worker por parâmetros HTTPS
separados do SQL; correspondência confirmada e demais entradas preservadas.
O job existente, owner postgres, foi usado por um ciclo de recuperação de
claim pré-IA expirado com mensagem nova da conta controlada: succeeded,
um POST `/drain` HTTP 200 às 12:04:02,483 UTC e UNKNOWN/sent/MID confirmado.
Contadores finais: seis envios/três chamadas de IA, zero casos abertos,
pendências, e-mails ou bootstrap. Conversa retomada; job e flag desligados.
O tempo de 65,413s inclui retenção e espera intencionais do cron.

O guard existente evita Edge sem fila; lease pré-IA volta à fila, enquanto
envio incerto fica para conferência sem reenvio cego. O header pg_net usa
somente o segredo limitado, não service_role/PAT, e fica temporariamente
descriptografado para papéis LOGIN. Não alterar filas/grants dos outros sistemas.
Free sem SLA e com pausa por inatividade continua uma limitação conhecida.
Metadados às 11:52:56 UTC não mostraram incoming fora do owner; não houve leitura
de perfil de cliente, IA, envio ou mudança de lista nesse diagnóstico.
Cron, e-mails e clientes continuam desligados. As quatro FAQs nativas ficam
ativas durante o teste; desligar respostas duplicadas antes da produção.
Meta Review de produção segue pendente e não foi usado modo live do agente.

— Codex

## 2026-11-01 · Codex — Cancelamento por mensagem e piloto contínuo

- Gestao `5f6a80a` e reservas `85abd70` publicados. Migration `20261101130005`
  aplicada com histórico na mesma transação, após cópia privada. `is_deleted`
  cancela somente o MID/remetente correspondente, inclusive antes do original.
  Retira conteúdo e derivados exclusivos, preserva outras fontes/controle humano
  e não rearma aviso já tentado. Chamada ou envio já iniciados mantêm auditoria
  mínima/custo, sem reenvio cego ou promessa de recolhimento externo.
- Revisão independente sem P0/P1/P2 pendente. 63 testes Node, 37 contratos
  PostgreSQL18 e catálogo226 aprovados. A guarda de destino do runner recebeu
  opt-in estrito para o service Docker do GitHub, mantendo host loopback/banco
  dedicado e identidade lida; dois testes de recusas adicionais aprovados.
  O fixture confere esse banco antes de ajustar somente BYPASSRLS da role
  fictícia compartilhada pelos DBs de CI. Reproduzido sem esse atributo:
  os 37 contratos e duas guardas passaram. Nenhuma alteração cloud.
- Edge 15 ACTIVE foi implantada OFF preservando 29 segredos. Health 200/OFF e
  autenticação/HMAC vazio passaram. Outros sistemas mantiveram definição/grants;
  Advisor: zero WARN/ERROR do atendimento. Depois do check real, o mesmo TEST de uma conta foi
  retomado com o único job `sirfisher-instagram-support-drain` ativo a cada minuto,
  owner postgres e Vault único. Zero pendências/bootstrap, seis envios/três
  chamadas anteriores, responsável NULL/e-mails desligados; clientes bloqueados.
- Sonda externa enviada e recebida na Primary aceita, com zero evento/POST
  no webhook nas leituras consultadas. Sem perfil/IA/envio para esse remetente.
  Causa em aberto. Cancelamento real ainda não testado; sem exclusão na interface.
- Meta: configuração 100%, ícone/categoria/descrição/Website e instruções salvos;
  formulário reaberto com credenciais vazias. Vídeo, dependências,
  tratamento/países e aceites legais pendentes. Review não enviado. Logs e
  contribuição do AI Studio sem confirmação por carregamento incompleto.
  O guia de app próprio trata detalhes do analista como opcionais; acesso
  adicional será considerado se a Meta solicitar, sem convite obrigatório inferido.
- Caixa manual: 118 pessoas, 13 grupos e quatro complementos; três retornos em duas conversas
  já contadas separados. Recorte atual sem não lidas/Pedidos/ocultos/rascunhos;
  histórico parcial e dois casos sem identidade segura preservados. Envio não
  comprova resolução. Nenhum teste contado como cliente. Política do site atualizada
  pela raiz em `6a65d42`/`5f03fce`, com WhatsApp explícito e retenção Google de 55 dias.

Arquivos privados e credenciais permanecem ignorados. As quatro FAQs nativas
continuam ativas durante o piloto; conferir e desligar respostas duplicadas antes
da liberação pública. O agente permanece sem modo live de atendimento.
Auditoria nativa final: resposta automática ativa só no Messenger, Instagram
desmarcado; ausência apenas como sugestão, regra nova IG de reserva OFF.
Nenhuma alteração foi salva nessa conferência.

— Codex
