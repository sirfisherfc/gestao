# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — resumo executivo do workspace entregue em PDF local de duas páginas; aplicações e banco sem alterações.

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

## 2026-10-23 · Claude — Rodapé da proposta em dois blocos

- A pedido do proprietário, a faixa preta virou um bloco próprio, colado
  abaixo do marrom e sem sobrepô-lo. Vai da coluna dos coquetéis até as
  bordas direita e inferior da página. O bloco marrom termina onde o preto
  começa.
- Contatos centralizados em três colunas iguais, com os ícones simétricos
  em torno do centro do bloco. Os dez ícones de alérgenos passaram para
  100×50 e foram centralizados, espaçados por igual.
- Bandeiras de cartão retiradas da mesa. Nenhuma lei que as exija foi
  encontrada (a Lei CE 17.899/2022 trata só dos alérgenos), e o A3 da
  entrada já as mostra.
- Salvo e conferido em exportação de 4000 px. Arquivos: este canal e
  `docs/HANDOFF_CARDAPIO.md`.

— Claude

## 2026-10-23 · Claude — Revisão de alinhamento e espaçamento da proposta

- Bloco preto dos alérgenos afinado para 50 px, com 12 px de folga, e
  contatos recentralizados no marrom.
- Página 1:
  - Petiscos, sanduíches, pratos para dividir e Família Real com espaço
    igual entre itens. Antes de "Batata frita ou macaxeira" havia um vão
    de 18 px, contra 4 a 6 nos outros itens.
  - Um x de partida por coluna, preço na altura do nome e ícones de
    alérgenos centrados no título.
  - Cabeçalho da Família Real, que estava 10 px fora do centro, centralizado.
  - Legendas das fotos com a mesma margem.
- Página 2:
  - Coquetéis com espaçamento igual, preço da margarita na linha do nome e
    o degrau de 2 px do rum nos destilados corrigido.
  - Sobremesas centradas no bloco e alinhadas às colunas dos destilados.
- Junções: degraus de 1 a 4 px entre blocos e bordas onduladas das fotos
  com moldura "recortada à mão" foram endireitados com sobreposição de
  blocos retos, porque a API recusou trocar a moldura. O texto inclinado
  "Veja a foto" desceu 12 px na primeira tentativa (o Canva posiciona
  rotacionados pela caixa girada) e voltou ao lugar.
- Conferido em exportações de 3200 px, com zoom nas junções. Arquivos:
  este canal e `docs/HANDOFF_CARDAPIO.md`.

— Claude

## 2026-10-23 · Codex — Resumo executivo do workspace

- Entregue o PDF profissional de duas páginas A4 em
  `../output/pdf/sir-fisher-resumo-executivo.pdf`, com módulos, entregas,
  conexões, serviços e escopo de implantação em outro estabelecimento.
- Levantamento pelo código e pela documentação de site, reservas e gestão;
  APIs e importações por arquivo identificadas. Limites preservados: DRE
  gerencial, pagamentos de eventos confirmados pela equipe e preparação
  ainda necessária para iniciar um banco novo, com contas e dados separados.
- Validação: revisão factual do texto extraído; três portais públicos com
  HTTP 200; PDF com duas páginas, renderizado por Poppler e inspecionado
  visualmente, sem cortes ou sobreposições. Sem auditoria integral dos
  serviços externos.
- Única alteração versionada: este registro, com recados antigos podados
  conforme o protocolo e pendências duráveis preservadas. PDF e temporários
  ficam locais, fora dos repositórios. Nenhum código, schema, credencial ou
  dado financeiro alterado; sem implantação de aplicação nesta entrega.

— Codex
