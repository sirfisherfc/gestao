# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre: Claude concluiu o plano de GEO e a rodada no navegador. Atenção: reservas `16e2de8` (nome nos e-mails e no PDF) ainda não foi implantado. Teste ChatGPT Ads do Codex segue de 09 a 16/11.

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

## 2026-11-08 · Codex: teste ChatGPT Ads ativado por autorização expressa

Gravados apenas os status de anúncio, grupo e campanha, nessa ordem.
Os três ativos; peça aprovada. R$300 totais, sete dias de 09/11 às 00h
até 16/11 às 00h em Fortaleza, máximo R$3,50/clique e os 14 setores
preservados. Comparação antes/depois conferiu os demais campos. Sem mudança
de verba, locais, datas, texto, imagem, destino ou outras campanhas.

Conector e interface confirmaram controles ativos. A edição de conferência
da campanha mostrou os 14 setores, valor e datas, depois foi cancelada.
O único motivo atual de não veiculação é início futuro. Conta aprovada,
faturamento configurado e nenhum bloqueio geográfico indicado. Ainda sem
comprovação de impressões; o início automático foi explicado ao usuário.
O relatório mensal veio sem linhas e não foi descrito como zero medido.
As outras campanhas têm término anterior a novembro e foram preservadas.

Atualizados plano e geografia. Proposta de acompanhamento diário com gastos,
tráfego, intenção e reservas/comparecimento com origem medida. Não foi
criada automação, revisão recorrente ou pausa automática. Recibo privado
`tmp/chatgpt-ads/ativacao-2026-11-08.json`, ignorado. Leituras, diff e links
conferidos. Sem código, banco ou migration; site e reservas preservados.

## 2026-11-09 · Claude — Auditoria e estratégia de GEO

Pedido do proprietário: estratégia para o Sir Fisher aparecer nas respostas
de ChatGPT, Claude, Gemini e Copilot. Entrega em
`docs/GEO_AUDITORIA_ESTRATEGIA_2026-11-09.md`, com plataformas, evidência
científica, diagnóstico, plano priorizado e painel de validação.
Achados que pedem ação: Cloudflare com `ai_training=disallow` e regra Skip
de 15 caminhos fixos bloqueia GPTBot e ClaudeBot em `/jardim-japones/`,
`/conheca/`, `/llms.txt` e imagens, contra a decisão de 25/10; sem Bing
Webmaster Tools, IndexNow ou Bing Places; FAQPage com 87 perguntas e só 18
visíveis; OSM e diretórios com "Barra Sol", horários antigos e unidades
encerradas; Bendito Guia exibe o celular pessoal; Tripadvisor com nota 3,9,
11 avaliações e categoria errada.
Só leitura: GA4, Search Console, Perfil da Empresa e Cloudflare por GET.
Nada alterado no site, portal, Cloudflare, fichas ou campanhas. Sem código,
banco ou migration. `check_project.py` OK sem Node, ausente neste PC.
Pendente: decisões do proprietário listadas no documento e onda 0 do painel
antes de qualquer mudança.

## 2026-11-09 · Claude — Execução do plano de GEO

Proprietário aprovou: robôs de IA liberados, nome público só "Sir Fisher",
"Barra Sol" é nome antigo, imprensa autorizada. Publicado: gestao `bcb395d`
(comando `cf.py ia`, `ai_training=disabled`, 140/140 respostas 200), site
`32cc90e` (página /sobre/, desambiguação, FAQ visível gerado do JSON-LD por
`tools/faq/sincronizar_faq.py` no pre-commit e na CI, nome no Réveillon) e
`071f996` (IndexNow, primeiro envio HTTP 202), reservas `caac8ee` (nome no
portal e no Réveillon). Migration `20261109190000_nome_publico_sir_fisher`
aplicada no portal e conferida. Onda 0 do painel em
`tmp/geo/painel/onda0-2026-11-09.jsonl`, resumo no relatório de GEO.
Pendente: logins do proprietário (Bing, Tripadvisor, iFood, OSM, Instagram
do Pub), envio das pautas, e-mails e PDF das Edge Functions ainda com
"Sir Fisher Praia" (reimplantar com teste), F4/F5/controles do ChatGPT.

## 2026-11-09 · Claude — GEO no navegador; Edge Functions à frente de produção

Onda 0 completa com F4, F5 e controles do ChatGPT. Bing Webmaster Tools
verificado pela meta `msvalidate.01` da home (site `5ec06ce`, não remover) e
sitemap enviado. Tripadvisor: ficha já correta; pedido de troca para
restaurante enviado ao suporte, mas a reavaliação no relatório de GEO
recomenda manter "bares e pubs" (decisão do proprietário). Nota OSM
5624850. Bendito Guia: pedido para retirar o celular pessoal.

**Atenção, reservas:** `16e2de8` tira "Sir Fisher Praia" de
`send-notifications` e `event-quote`, mas a implantação foi negada no modo
automático. Produção segue nas versões 52 e 68, e o segredo `RESEND_FROM`
ainda é "Sir Fisher Praia <reservas@sirfisher.com.br>". Quem implantar essas
funções leva a troca junto; comandos no relatório de GEO. Os testes de preço
do `event-quote` têm 23 falhas antigas por datas fixas de outubro de 2026.
