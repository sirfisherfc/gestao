# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Teste ChatGPT Ads ajustado em 10/11 (lance R$5, término 18/11); conferir entrega em 11/11 a partir das 15h45 (ver `docs/ANALISE_CHATGPT_ADS_2026-11-10.md`).

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

## 2026-11-10 · Claude — event-quote implantada; notificações pendentes

A função de eventos foi implantada a partir de reservas 16e2de8: versão 69,
ativa, verify_jwt=false preservado, OPTIONS 200 e GET 405 como no código. O
PDF da proposta já sai com "Sir Fisher". A implantação de send-notifications
e a troca do segredo RESEND_FROM foram negadas pelo classificador do modo
automático; produção segue com send-notifications v52 e o remetente
"Sir Fisher Praia". Comandos para o PowerShell no relatório de GEO, em
"Pendências do proprietário".

## 2026-11-10 · Claude — Nome novo nos e-mails em produção

O proprietário implantou send-notifications a partir de reservas 16e2de8 e
trocou o segredo RESEND_FROM para "Sir Fisher <reservas@sirfisher.com.br>".
Conferido: segredo pelo resumo SHA-256, verify_jwt=false nas duas funções
e 401 sem o segredo. A troca do segredo reiniciou as seis Edge Functions,
cada uma com uma versão nova: send-notifications 54 e event-quote 70. Nenhum
e-mail saiu ainda pela versão nova; o último envio foi em 10/11 às 00h26,
sem falhas recentes. Nota sobre o reinício em reservas 87286a6, no
docs/email.md.

## 2026-11-10 · Claude — Teknisa: relatório de caixa para o gerente

No painel, o perfil "Gerente - Reposicao" passou a ver Vendas → Relatórios →
Estatísticas de Caixa → Fechamento de Caixa; a regra foi relida após
recarregar. A inclusão da Nayane no perfil ficou pendente: a lista de
operadores do painel voltou vazia em Perfil de Acesso e em Operador. Detalhes
em docs/TEKNISA_ACESSOS_OPERACAO.md. Nada foi gravado no cadastro dela.

## 2026-11-10 · Claude — ChatGPT Ads: teste ativo sem entrega

Análise em `docs/ANALISE_CHATGPT_ADS_2026-11-10.md`, só leitura (Ads
Manager no Chrome, GA4, portal read-only e recibos). Até 10/11 às 14h, zero
gasto, impressões e cliques, com aviso "Lance baixo". Mesmo lance de R$3,50
entregava no Ceará em outubro; nos 14 setores, não. A campanha está sem metas
de conversão ("Configurar"). Desde o site `5eeb6f2` o Pixel e o `oppref`
dependem do aceite de publicidade. Nada foi alterado na campanha.
Pendente: decisão do proprietário entre ajustar (lance R$5, cinco contextos
de outubro, metas, término 18/11) ou encerrar. Sem código, banco ou migration.
Leitura do GA4 neste PC: o Python do sistema não tem a biblioteca; usar o do
ambiente `analytics-mcp` em `LOCALAPPDATA`.

## 2026-11-10 · Claude — ChatGPT Ads: ajuste autorizado aplicado

Proprietário aprovou a recomendação A. Pela interface do Ads Manager: grupo
com lance máximo de R$3,50 para R$5,00 e os cinco contextos de outubro
(reescritos sem vírgulas internas; fatos conferidos), às 15h44; campanha com
Reserva confirmada e Visita realizada e término de 16/11 para 18/11 às 00h,
às 15h49. O histórico mostra só esses campos. R$300, 14 setores, peça e
destino iguais. Aviso de lance baixo sumiu; entrega ainda não comprovada.
Pendente: conferir em 11/11 a partir das 15h45; sem impressões, pausar e
encerrar sem novo aumento. Recibo em `tmp/chatgpt-ads/ajuste-2026-11-10.json`.
