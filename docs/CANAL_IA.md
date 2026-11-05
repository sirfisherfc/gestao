# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre — Codex reduziu o cartão dos vouchers para mostrar mais a foto. Reservas e site sem edições.

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

## 2026-11-05 · Codex — Edição, códigos curtos e arte horizontal dos vouchers

Botão Editar para vouchers disponíveis, com revisão e histórico antes/depois;
resgate recusa confirmação de revisão antiga. Emissão e consulta passam a usar
seis caracteres Crockford, sem prefixo; códigos antigos mantidos como aliases.
Arte 1600×1000 com foto oficial do deck e cartão claro, rodapé apenas uso único
e não acúmulo. Dados internos permanecem privados. Assets JS/CSS de vouchers
ganham nomes por hash no artefato Pages para atualizar navegador sem versões
manuais no HTML fonte. Reservas recebe consulta curta e resgate com revisão.

Migrations 20261104205451 e 20261105130459 aplicadas/registradas no portal e
relidas; perfis reais validados em transação com rollback das fixtures.
81 verificações SQL com concorrência e limpeza, 19 testes JS de gestão,
27 de reservas e 2 de empacotamento passaram; quality, acessos, frontend e
catálogo de migrations passaram. Cinco PNGs renderizados, com inspeção visual
dos casos normal e nome longo. Advisor sem WARN/ERROR para vouchers.
Publicados gestão 432830f (Pages e Quality verdes) e reservas 6f0d456 (Pages
verde). Artefatos dos mesmos commits conferidos: 11 assets com hash coerente,
botão Editar, arte horizontal, foto e resgate com revisão. Purga Cloudflare
limitada a sete URLs dos vouchers concluída. Site sem alterações.
Browser integrado indisponível e HTTP dos domínios retornou 403 Cloudflare;
não alegar teste interativo do portal/WhatsApp. Sem pendência de implantação.

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
