# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre — Codex concluiu lista de validações recentes em reservas e ajustes de navegação/texto em gestão. Site sem alterações.

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

## 2026-11-05 · Codex — Cartão e informações centralizados

Template horizontal reorganizado conforme a referência visual enviada:
cartão claro em degradê, arredondado e central sobre a foto oficial do deck;
logo, benefício, nome, código e validade no mesmo eixo. Removida a caixa
separada de site/Instagram. Rodapé continua curto. Sem mudança de banco.
Arquivos: assets/voucher-template.js, teste JS, docs/VOUCHERS.md e este canal.
19 testes passaram; cinco PNGs renderizados, com inspeção dos casos normal
e nome longo. Quality com Node e contratos frontend conferidos antes do push.
Publicação pelo Pages com versionamento automático dos assets; conferir o
workflow do commit e a cópia publicada. Nenhuma edição em reservas ou site.

## 2026-11-05 · Codex — Mais foto ao redor do cartão

Cartão reduzido de 960×800 para 864×704 px: 10% na largura e 12% na altura,
interpretando a segunda menção a largura como altura. Permanece centralizado;
logo, tipografia e espaçamento ajustados proporcionalmente. Template e
docs/VOUCHERS.md atualizados; sem banco ou alterações em reservas/site.
19 testes JS passaram. Cinco variantes PNG renderizadas, incluindo nome
longo e valor alto; casos normal e nome longo inspecionados sem cortes.
Quality e diff conferidos antes do push; publicação pelo Pages, com arquivo
do template versionado automaticamente por conteúdo.

## 2026-11-05 · Codex — Validações recentes e ajustes dos portais

Reservas: removido aviso sobre códigos antigos; lista paginada de vouchers
utilizados hoje e nos dois dias anteriores, em Fortaleza, com nome, código,
benefício, data/responsável. Atualiza ao abrir, manualmente e após tentativa
de utilização. Estados de falha/vazio distintos e respostas antigas descartadas.
Gestão: menu idêntico ao de rotinas, sujeito ao gate existente; removida a
mensagem de imagem pronta/dados internos e seu espaço vazio. Sem mudança na arte.
Arquivos: HTML/JS/CSS dos vouchers, testes, instalador e documentação.

Migration 20261105141504 criada pela CLI e aplicada/registrada no portal:
RPC recent com wrapper INVOKER, gate da equipe ativa e grants explícitos;
índice parcial de used_at. SQL isolado reexecutável passou em 92 verificações,
incluindo período, fuso, paginação, dados privados e permissões. Perfis reais
passaram com rollback das fixtures. 32 testes JS do reservas, quality com Node,
contratos de acesso/frontend e catálogo de migrations passaram. IDs do HTML/JS
e igualdade do menu conferidos. Advisor sem WARN/ERROR para vouchers.

Voucher de teste indicado pelo proprietário apagado por pedido explícito,
junto dos dois eventos vinculados; alvo único conferido antes e ausência
conferida depois, sem dados pessoais versionados. Site permanece sem edições.
Publicação por Pages nos dois projetos; conferir workflows/artefatos do commit.
