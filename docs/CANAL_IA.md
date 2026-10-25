# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — revisão de SEO, descoberta local e conversão entregue; horários GBP, site e reservas publicados.

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

## 2026-10-25 · Codex — SEO, descoberta local e conversão

- Diagnóstico, histórico, fontes, prioridades e plano de 30/60/90 dias em
  `docs/REVISAO_SEO_LOCAL_CONVERSAO_2026-10-25.md`. GSC/GA4 e operação com
  janelas fechadas até 22/10; cobertura e unidades separadas. Cliques de busca
  cresceram, consultas comerciais ficaram quase estáveis e reservas públicas
  criadas foram 25 nas duas janelas de 28 dias; sem taxa de coorte artificial.
- Corrigido `scripts/gbp/gbp.py`: feriados preservam exceções existentes;
  decisão datada de 31/12/2026 mantém 9h até 2h de 01/01/2027. Publicação exata
  conferida no Google, preservando os outros oito períodos; releitura final
  sem pendingMask/diffMask. O código anterior reproduziu a perda do horário.
- Oito regressões offline e quality local aprovados; teste GBP incluído em
  `.github/workflows/quality.yml`. Revisão independente aprovada. Sem migration,
  escrita no Supabase, alteração financeira ou credencial versionada.
- Site `c0eabff`: links Hubt restantes, informações de reserva/mesa, contraste,
  privacidade, avaliações e instalador MCP corrigidos; assets/Pages aprovados,
  arquivos públicos conferidos e PageSpeed home 100 nas quatro categorias em
  celular e desktop. Reservas `915e893`: recuperação de falhas e seleção de
  horário; 20 testes Deno e publicação conferidos, sem criar reservas reais.
- Docs de cardápio, GBP, Ads e atendimento reconciliados com as decisões atuais.
  FoodMenus coincide com o catálogo após normalizar moeda; sem nova publicação
  de cardápio. Pares AGENTS/README raiz e cópias versionadas idênticos.
- Semrush: 720 unidades previstas e confirmadas; saldo informado 49.900,
  estimado 49.180, saldo real indisponível. Assinatura/recorrência preservadas;
  benefício de US$199/mês ainda precisa ser demonstrado. Conferir painel até
  30/10, usando 31/10 como data conservadora da cobrança informada.
- Decisão do proprietário em 25/10: mesas disponíveis em todos os horários de
  hoje; registro de clientes sem reserva adiado por falta de equipe. Plano usa
  dados automáticos existentes, sem ficha, nova rotina ou carga para recepção.
  Execução recente da rotina GBP na nuvem e preços/alérgenos continuam com os
  limites descritos no relatório. Nenhuma campanha ou orçamento alterado.

— Codex
