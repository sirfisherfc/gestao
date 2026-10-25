# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — cardápio Google com atribuição, alvo EN coletado e acesso Semrush conferido; adendo concluído e ZIP anterior preservado.

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

## 2026-10-25 · Claude — Site Audit da Semrush e robots.txt

- Site `0af3d6d`: catálogo do cardápio escrito no HTML
  (`site/tools/cardapio/prerenderizar.py`, no pre-commit e no workflow
  `verificar-assets`), igual ao que o `cardapio.js` desenha; h1 da página;
  `address` no organizer do Event do Réveillon; `llms.txt`; links para
  `/reservas/`. Ao rodar `exportar_snapshot.py`, o commit no site regenera
  o catálogo sozinho.
- Site `5e94b8e` + Cloudflare: robots.txt gerenciado e Bot Preference Sync
  desligados (`scripts/cloudflare/cf.py robots`, `--religar` desfaz; o token
  agora tem Zone > Bot Management > Edit). Só o primeiro não bastava. A mesma lista de 32 robôs de treino de IA
  ficou em `site/robots.txt`, inclusive `Google-Extended` (sem decisão do
  proprietário para liberar). Demais opções de bots conferidas sem mudança.
- Atualização posterior (Codex, 25/10/2026): o usuário autorizou expressamente a liberação de `Google-Extended` nesta conversa; site `bafeeaf` publicado e conferido no domínio, com os demais bloqueios preservados.
- Validação: prerender/assets/CSP `--verificar`, teste de navegador e axe
  sem problemas, marcação idêntica à do JS, CLS 0, páginas publicadas
  conferidas. Pendente: nova rodada do Site Audit pelo proprietário.

— Claude

## 2026-10-25 · Codex — Fechamento SEO/IA, painel e acervo portátil (snapshot anterior)

- Resultado atual, sete pontos pedidos, reformulação, histórico, fontes e
  checklist 26/27 em `docs/SEMRUSH_3_DIAS_2026-10-25.md`. Sem tarefa manual
  para proprietário/recepção e sem novo agendamento no Codex.
- Site `5918c99` e `2b04523`: links de almoço/cardápio, rota conforme origem,
  pets e caminhos de grupos/eventos publicados, HTTP 200 e HTML conferido.
  Nova auditoria real: Site Health 96, AI Search Health 99, zero erros e
  vinte avisos. Métricas Semrush e CrUX mantidas com suas definições.
- GSC: inclusão IA padrão confirmada no domínio; 2.672 impressões históricas
  no recorte Web com base em texto, 77 dias. As 13 linhas de páginas têm outra
  agregação e não correspondem às 13 URLs do sitemap. `/eventos/` recebeu
  Indexação solicitada. O envio de `/reservas/` do www falhou duas vezes na
  conexão ao reCAPTCHA; permanece pendente, sem contorno ou mudança no portal.
- Google/Fortaleza/mobile/PT: 40 termos coletados, visibilidade 13,97%, oito
  Top 10 e cinco Top 3, única data 25/10. Original Brasil preservado e cópia
  identificada. ChatGPT/Fortaleza/PT: 12 prompts, três diretos e nove genéricos;
  nove Mentioned (três diretos e seis genéricos), três Missed genéricos.
  Os scores 74,33% e 68,84% da mesma tela foram preservados como divergência.
- Backups API e UI, CSVs nativos/derivados e relatório no ZIP privado
  `output/semrush-3-dias/sir-fisher-acervo-completo-2026-10-25.zip`, na raiz do
  workspace. Hash e validações no sidecar `.verificacao.json`. API histórica
  preservada com 78 relatórios; ledger atual com 79 e 21.070 unidades
  confirmadas. UI confirmou saldo 28.830, reserva 4.900 e espaço 23.930 no
  teto autorizado. A reserva histórica 2.900 sem metadata não virou débito
  individual por chamada. Assinatura/recorrência só lidas: 31/10, US$199, ativa.
- Duas alterações externas de `site/robots.txt` e `tools/analytics/README.md`
  foram preservadas sem publicação por esta rodada. A origem da autorização
  do toggle Google-Extended não foi confirmada. Público às 04:40 mantinha
  Googlebot/OAI-SearchBot permitidos e GPTBot/Google-Extended bloqueados.
- Helper/testes no histórico `8be6a3a`/`62975fc`, com onze regressões offline,
  oito GBP, quality e CI/Pages aprovados. Este fechamento altera só documentos;
  sem migration, escrita no banco, alteração financeira ou credencial versionada.
  Pares de orientações da raiz e cópias versionadas conferidos idênticos.

— Codex

## 2026-10-25 · Codex — Rodada adicional, cardápio Google e alvo EN

- Documentei a atribuição em `docs/ROTINA_PERFIL_GOOGLE.md` e acrescentei
  adendo em `docs/SEMRUSH_3_DIAS_2026-10-25.md`. O ZIP anterior conserva
  os mesmos bytes/hash. Sem migration ou alteração financeira.
- Google-Extended `bafeeaf` e site `7c2b72c` publicados e conferidos no
  domínio. O segundo preserva regras e esclarece grupos/eventos e posição
  de mesa. Passaram 108 Deno, quatro verificadores e quatro casos de navegador.
- Fechamento posterior: site `475e9b2` documenta o estado EN/CF e `78cd544`
  corrige horário/feriados do executivo na página EN fish. CI e Pages passaram;
  reservas, eventos e EN fish responderam HTTP 200 com HTML igual ao local.
  Relatório e ZIP anteriores preservados.
- GBP: um PATCH somente em `url_menu` acrescentou UTM `gbp_menu`; leitura
  real às 05:41 confirmou o destino. Outros 60 atributos, ficha e FoodMenus
  iguais. HTTP 200 e canonical limpa. Recibo agregado em
  `output/seo-rodada-adicional-2026-10-25/gbp-url-menu-recibo.json`, fora do Git.
- ChatGPT/Fortaleza/English: `31731868_5693988`, quatro prompts coletados,
  quatro Mentioned (três genéricos e um de marca). Linha de base de 25/10;
  percentuais divergentes da consolidação não viraram taxa de mercado.
  Export nativo bloqueado pelo Trial; snapshots e CSV derivado preservados.
- On Page Checker: causa do 403 identificada na regra Block AI bots on ad
  pages. Exceção restrita publicada e relida Active na UI, Skip de todas as
  regras `http_request_sbfm` só no conjunto definido, com
  logs. Evento real `skip` às 05:53:47 e recoleta EN fish comprovaram acesso;
  o relatório passou a cinco ideias, sem 403. Bot Management/robots iguais.
  A prova cobre essa página; detalhes, recibos e rollback no adendo.
- Quality estático e diffcheck passaram; pares de orientação da raiz idênticos.
  Sem API Standard paga nova, nova rotina, upgrade ou mudança de recorrência.
  A coleta manual de clientes sem reserva continua adiada pelo usuário.

— Codex
