# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Foto oficial do deck incluída no PNG dos vouchers; template 1080×1920, loader e artefato validados. Publicação pelo Pages deste commit. Sem mudança de banco/reservas/site; Browser integrado indisponível.

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

## 2026-11-04 · Codex — Cabeçalho da rotina de vouchers

Corrigido vouchers.html: faltava carregar assets/product-pages.css, que
define fundo/posição do header e alinhamento de head-row/tabs. Reutilizado
o CSS das outras rotinas sem alterar estilos globais. Arquivos alterados:
vouchers.html e este canal. Sem mudança de banco, regras ou outros portais.
Quality gate com Node, contratos frontend e git diff --check passaram.
Browser integrado retornou indisponível (lista vazia); não afirmar QA visual
interativo. Publicação segue o workflow Pages; conferir HTML/CSS por HTTP.

## 2026-11-04 · Codex — Motivo de premiação / metas nos vouchers

Nova opção principal `award`: Premiação / atingimento de metas, disponível
na emissão, filtro e detalhes, com complemento opcional. Motivo permanece
interno. Ajustados template/categorias, testes, instalador e documentação.
Migration 20261104203828 aplicada/registrada e relida no portal; amplia o
CHECK e as validações privadas de emissão/listagem. Preserva dados, demais
motivos, gates e grants. Reexecução e emissão/filtro testados em SQL isolado;
smoke com perfis reais passou e desfez todas as fixtures. 14 testes JS,
quality com Node, catálogo de migrations e diff passaram. Advisor sem
WARN/ERROR de vouchers. Nenhuma edição em reservas/site.

Cabeçalho: deploy c726f25 confirmado e artefato HTML/CSS idêntico ao local.
Leitura HTTP do domínio pelo script recebeu 403 Cloudflare 1010, sem
contorno; Browser indisponível. Não afirmar conferência visual interativa.

## 2026-11-04 · Codex — Foto do deck incorporada ao voucher

Incluída foto oficial no próprio Canvas exportado para PNG e compartilhado.
Arquivo assets/vouchers/deck.webp idêntico ao terraco-por-do-sol-960 do site;
autoria confirmada no guia de analytics do site. Recorte mantém mesas e
horizonte; dados ficam sobre fundo liso. Formato 1080×1920. Nome longo e
valores continuam ajustados sem truncamento. Reabrir voucher disponível já
emitido gera nova arte; não reemitir. Loader aguarda foto/ícone/fontes e
exige foto válida, sem retornar silenciosamente à arte anterior.

Alterados template, loader, asset, allowlist/empacotamento Pages, renderer,
testes e docs/VOUCHERS.md. Referências Belmond/Dorchester agora explicadas
em linguagem comum: exemplos consultados, sem vínculo ou uso de suas artes.
16 testes JS passaram, incluindo foto no mesmo Canvas exportado, proporção,
limites e privacidade; cinco PNGs renderizados (fixo, percentual, nome160,
nome sem espaços e valor alto), inspecionados e sem sobreposição. Quality,
frontend, acessos e diff passaram; foto conferida por SHA256. Não há mudança
de banco ou vouchers cadastrados. Browser indisponível; QA do PNG realizado
diretamente por renderização, sem alegar teste interativo do portal/WhatsApp.
