# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre: Codex ativou o teste ChatGPT Ads autorizado para 09 a 16/11; três níveis ativos, aguardando início.

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

## 2026-11-08 · Claude — Charlotes liberadas para venda no POS

O POS recusava a Charlote de Morango por falta de alíquota do PIS. Em Impostos
por Unidade, as duas charlotes (`8.00.20.022.00` e `.023.00`) tinham Alíquota
PIS/COFINS vazias; o Brownie tem `0.00`. Ajustadas pela tela e relidas. Lição
registrada em `scripts/teknisa/README.md` e `docs/TEKNISA_MIGRACAO_CARDAPIO.md`.
Sem código, banco ou migration. Pendente: venda real no aparelho após a carga;
NCM da charlote (`21069090`) segue diferente do Brownie (`21069029`), por decisão a confirmar.


## 2026-11-08 · Codex: 14 setores de Fortaleza salvos no ChatGPT Ads

O proprietário pediu Fortaleza inteira se houver cidade válida; alternativa
com 14 setores explícitos. Todos validados como postais BR/Fortaleza.
Substituí Ceará pelos 14 e atualizei a observação da campanha. Conector
aceitou a gravação; leitura independente conferiu. A interface mostrou
Ceará inicialmente e depois os 14 ao reabrir. Sem segunda gravação;
a edição de conferência foi cancelada. Campanha/grupo/anúncio pausados,
peça aprovada, R$300 totais e máximo R$3,50/clique preservados. Não
houve ativação, mudança de datas, peça, destino ou estratégia de lance.

Consulta real enviada ao chat oficial do suporte. O atendimento automatizado
não confirmou cidade/limites e anunciou encaminhamento ao Ads. A segunda
mensagem pediu protocolo e confirmação do encaminhamento; sem retorno ou
número até a conferência final. Cidade permanece pendente, sem presumir
indisponibilidade. A gravação postal não comprova cobertura municipal inteira
ou entrega. Ativação depende de aprovação específica e saldo mensal.

Atualizados `docs/GEOGRAFIA_CHATGPT_ADS_2026-11-08.md`, o aviso no plano e
este canal. Recibo privado em `tmp/chatgpt-ads/segmentacao-2026-11-08.json`,
ignorado. Diff, fontes oficiais, 14 locais e valores conferidos. Sem
código, banco ou migration. Site e reservas preservados.


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
