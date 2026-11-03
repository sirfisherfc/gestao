# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Codex concluiu a releitura do perfil QR: comportamento agregado desde agosto, cobertura demográfica parcial e públicos de reserva conferidos. Relatório PERFIL_QR_CAMPANHAS_2026-11-03.md. Sem mudança de produto, campanha ou orçamento.

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

## 2026-11-03 · Codex — Tarefas do Analytics

Proprietário mostrou cinco tarefas. Consulta analytics.readonly confirmou
propriedade 353205396, vínculo Ads 1493778788, seis eventos principais e dois
públicos personalizados de 30 dias. reservation_confirmed e visit_realized
em ONCE_PER_EVENT. UserProvidedDataSettings sem ativação; identidade BLENDED
não comprova User-ID. Código público sem User-ID; login interno é separado.

Ação Ads de reserva é a prioridade para campanhas. Públicos já criados;
usar em campanhas é opcional. User-ID, UPD e importação de custos externos
ficaram como recursos adicionais, sem ativação para completar contador.
Discovery público não expõe progresso do assistente nem substitui ações Ads
pelo recurso legado conversionEvents. Interface retornou host indisponível.
Conferir ações existentes antes de criar/importar para evitar duplicidade.

Atualizados relatório final, este canal e ANALYTICS_TAREFAS_2026-11-03.md,
com fontes e limites. Sem mudança de produto, migration, dado pessoal,
custo importado, anúncio ou orçamento. Bases f12c854 / 078652a / 4d0d80e.
Recibo em tmp/revisao-2026-11-03/analytics-tasks-read.json, ignorado pelo Git.

## 2026-11-03 · Claude Code — Grupo Garçom Sênior no Teknisa

Criado `05 — GARCOM SENIOR` (cópia do 04, com retirar taxa de serviço,
desconto, cancelar item e suprimento liberados; sangria bloqueada), supervisionado pelo 02. Um garçom foi
movido do 04 para o 05; releitura sem divergências. Detalhes e teste
pendente no POS em `docs/TEKNISA_ACESSOS_OPERACAO.md`. Feito pela interface;
a ferramenta `teknisa.mjs` não tem comando para grupos (Node ausente neste PC).

## 2026-11-03 · Codex — Perfil QR e públicos para campanhas

Releitura GA4 somente de leitura: 01/08 a 03/11 parcial, hosts públicos,
origem/mídia/campanha com marcação QR. Total sem dimensões: 1.494 sessões,
988 usuários técnicos, 1.012 sessões engajadas e 2.814 visualizações. Celular
aproximadamente 99,7%, português 92,3%. Não somar linhas/hosts/meses para
deduplicar. Cobertura não equivale a todas as leituras físicas ou clientes.

Signals habilitado. Idade/gênero começaram a aparecer em parte da propriedade
desde 02/11, com unknown predominante e limites de privacidade. API recusou
essas dimensões combinadas com o filtro QR; não substituir pelo total do site.
Renda, residência e cliente de maior valor seguem sem evidência suficiente.
Inventário: All Users, Purchasers e dois públicos personalizados de reserva;
nenhum específico de QR. Uso/tamanho elegível em campanha não confirmado.

Criado PERFIL_QR_CAMPANHAS_2026-11-03.md e link no relatório de 02/11.
Validação: consultas reais e metadados; recibos agregados em tmp ignorado.
Sem migration, alteração de consentimento, dados pessoais, anúncio ou verba.
Bases 571643b / 078652a / 4d0d80e. Documentação validada; publicação pelo
fluxo Quality/Pages. Nenhuma alteração de produto nesta entrega.
