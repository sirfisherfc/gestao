# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Campanha ChatGPT Ads nova aprovada e ativa, programada 12–26/11, R$300 totais, Brasil, CPC desejado R$3; teste por CEP pausado. Primeira conferência manual em 14/11 às 18h. Ver `docs/CAMPANHA_CHATGPT_ADS_2026-11-11.md`.

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

## 2026-11-10 · Claude — ChatGPT Ads: ajuste autorizado aplicado

Proprietário aprovou a recomendação A. Pela interface do Ads Manager: grupo
com lance máximo de R$3,50 para R$5,00 e os cinco contextos de outubro
(reescritos sem vírgulas internas; fatos conferidos), às 15h44; campanha com
Reserva confirmada e Visita realizada e término de 16/11 para 18/11 às 00h,
às 15h49. O histórico mostra só esses campos. R$300, 14 setores, peça e
destino iguais. Aviso de lance baixo sumiu; entrega ainda não comprovada.
Pendente: conferir em 11/11 a partir das 15h45; sem impressões, pausar e
encerrar sem novo aumento. Recibo em `tmp/chatgpt-ads/ajuste-2026-11-10.json`.

## 2026-11-11 · Claude — Contador de aceite e sinal VisitaQR

Site `bd4b39b` e reservas `8b76ae1`: `google-ads.js` (idêntico) envia ao GA4
`publicidade_aviso_exibido`, `publicidade_aceita` e `publicidade_recusada`;
`atribuicao.js` envia `VisitaQR` ao pixel da Meta para origem `qr_code` com
permissão. Privacidade atualizada (11/11). Testes e produção conferidos.
Pendente: criar na Meta o público `VisitaQR` e o semelhante (navegador
desconectado; passos em `docs/PUBLICOS_PUBLICIDADE_2026-11-11.md`). Google:
públicos QR e de reserva já existem no GA4; falta campanha e a verificação
do anunciante. Portal: versão `?v=` do script é atualizada à mão.

Atualização 10h: na conta de anúncios do Portfólio Sir Fisher (não a
pessoal), criados o público de engajamento do Instagram (365 dias) e o
semelhante 1%. O público `VisitaQR` espera o primeiro evento no pixel.
Chrome: quedas ligadas a ociosidade e à economia de memória ligada; ver
`docs/PUBLICOS_PUBLICIDADE_2026-11-11.md` e a seção abaixo do documento.

**ChatGPT Ads, 11/11 10h40:** ainda zero impressões 19 h após lance R$5;
sem aviso de lance. Causa provável: CEPs sem público elegível. ChatGPT
orgânico trouxe 74 sessões desde 01/11, 76% de fora do Ceará. Decisão de
encerrar ou reformular com o proprietário; detalhes na análise de 10/11.

**Aviso financeiro:** em 11/11 o proprietário assinou o Meta Verified para
empresas, plano Básico recomendado (R$43,09/mês). Nova cobrança recorrente
da Meta no cartão a partir de novembro, categoria de marketing; não é
verba de anúncio. Confirmar o plano pela primeira fatura.

## 2026-11-11 · Codex — Campanha ChatGPT Ads: roteiros e refeições

Pedido delegado de 11/11 executado pelo conector. Campanha “Sir Fisher | Roteiros
e refeições | Novembro 2026”: dois grupos, quatro anúncios, todos criados
pausados, aprovados pela OpenAI e só depois ativados. Teste R$300 por CEP
pausado antes; outras campanhas e conta preservadas. Brasil, todas as
plataformas, CPC desejado R$3, R$300 totais de 12/11 00h a 26/11 00h
(America/Fortaleza). Metas Reserva confirmada e Visita realizada associadas;
aprimoramento criativo desligado conferido na interface, cancelada sem salvar.

Relatório `docs/CAMPANHA_CHATGPT_ADS_2026-11-11.md`: Ads, GA4, Search Console e
portal atualizados; nenhum registro de reserva com UTM ChatGPT desde outubro.
GA4 atual: 67 sessões orgânicas por origem e 36 visualizações (30 entradas) em
/reveillon/; não repetir os 74/36 como sessões. Venda de Réveillon aberta,
mas medição do módulo desligada e pacote com álcool: ficou fora desta rodada.
Fotos oficiais de peixe e pôr do sol sem edição; destinos/imagens HTTP 200.
Sem fonte validada de ociosidade por hora. Sem código, banco ou migration.

Teto agregado novo do proprietário: **R$500 em novembro**, prevalece sobre
R$1.000 histórico. Nova verba R$300; R$200 não liberados, inclusive para atraso
de métricas. Relatório Ads cobre até 10/11; parcial de 11/11 sem linhas não foi
tratado como zero medido. Conferências manuais 14/11 e 18/11 às 18h, fim 26/11
às 10h. Pausa autorizada com >=R$100 e >=30 cliques sem rota, contato ou início
de reserva. **Sem automação/alerta recorrente.** Pacing não garante saldo até o
fim dos 14 dias. Recibos privados em `tmp/chatgpt-ads/`, ignorados pelo Git.

Validações: leituras independentes dos sete objetos ativos e quatro aprovações;
único impedimento atual é início futuro. Fotos inspecionadas e upload aceito;
validador empacotado indisponível por dependência, verificação independente
registrada. Entrega real deve ser conferida após 12/11. Três repositórios e
pares de orientações da raiz conferidos; só relatório e CANAL_IA versionados.
