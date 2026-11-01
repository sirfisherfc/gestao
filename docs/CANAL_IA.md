# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Gestao e reservas liberados após filtro de spam (`4e27f7a`/`71c5a2d`, Edge 19) e cancelamento real sob pausa. TEST de uma conta e cron ativos; o agente responde só à conta de teste. Site tem responsável próprio.

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

## 2026-11-01 · Codex — Declarações confirmadas e vídeo pendente

O proprietário confirmou URLs de arquivos desligadas, resposta “Não” no campo
de segurança nacional e os procedimentos informados de legitimidade e minimização.
Anthropic foi preservada no formulário como pendência; a integração efetiva
continua sem confirmação. Não houve alteração de fornecedores por inferência.

A captura oficial da aba Instagram retornou indisponibilidade de CDP durante
resposta de documento pausada, nas duas tentativas documentadas. Nenhuma
gravação iniciou e nenhuma pergunta extra, caso ou chamada de modelo foi gerada.
Não houve gravação de clientes. Vídeo e autorização do cancelamento real
continuam pendentes. O helper privado teve apenas preparação/leitura; nenhuma
pausa ou outra mudança operacional foi executada.

Atendimento permanece TEST exclusivo da mesma conta e único cron ativo,
com seis envios/três chamadas anteriores; FAQs nativas continuam ativas para os clientes. Esta entrega
altera somente documentos, sem migration, novo deploy ou envio de mensagens.

— Codex

## 2026-11-01 · Codex — Spam antes da fila e cancelamento real sob pausa

Filtro conservador PT/EN publicado em reservas `71c5a2d`, regras duráveis em
gestao `4e27f7a`. O servidor confirma spam claro com HTTP 200, sem texto/MID na fila, caso, ACK ou IA;
fica no Instagram sem bloqueio/exclusão automática. Relatos reais de golpe,
cobrança, reclamação, urgência e pedido de pessoa têm prioridade. Links/CV/menu
e propostas comuns continuam elegíveis. Echo/retirada mantêm seus protocolos.
Contador agregado pode incluir reentregas; não representa pessoas únicas.

76 testes Node verdes, repetidos pelo revisor; falsos positivos de relato,
cartão duplicado e prioridade de glúten/lactose corrigidos. Sem migration ou
acesso novo. Regra e orientação manual em AGENTS, BOOK e CONHECIMENTO; código
em nuvem independe de Chrome aberto. Mídia/grafias disfarçadas/ambiguidade continuam
limites; sem porcentagem de cobertura ou promessa de triagem perfeita.

Edge 19 ACTIVE implantada OFF preservou 29 nomes de segredos. Saúde/HMAC vazio e check real
passaram; o mesmo TEST/interseção 1 e único cron/postgres/1min foram retomados,
com zero pendências e responsável NULL/e-mails desligados. Histórico de seis envios/três chamadas e
teto de R$45/2.000 gerações/2 centavos preservados. Nenhuma nova chamada de modelo, Meta send
ou drain nessa configuração. Testes de spam são sintéticos locais.

Após autorização específica, a coordenação enviou e cancelou somente a mensagem
de teste permitida. O ensaio usou pausa global/cron OFF; capturou o alvo/MID em
RAM antes da retirada, confirmou `is_deleted` e derivados vazios, sem novo caso,
reserva ou resposta. O texto já estava vazio pela pausa. Restore autorizado
passou com health 200 e leitura fresca, sessão encerrada sem salvar MID. Prova
sequencial de callback real sob pausa; concorrência permanece nos contratos locais.
Nenhuma outra mensagem foi apagada. Vídeo da Meta continua pendente.

— Codex
