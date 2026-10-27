# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — oito operadores e cinco vendedores Teknisa conferidos na Praia em 27/10/2026. Testes físicos, três CESTs do cardápio e impresso Big Ben Fries seguem pendentes.

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

## 2026-10-25 · Claude — Big Ben Fries com 250 g

- Decisão do proprietário: Big Ben Fries tem 250 g, como a Macaxeira Frita
  ou Batata Frita (TXT, HTML antigo e impresso diziam 200 g).
- `scripts/cardapio/catalogo_inicial.py` (com nota) → JSON → snapshot do
  site (`dcfb37f`; o pre-commit regenerou o catálogo pré-renderizado).
- Migration `20261025170000_cardapio_big_ben_250g.sql` aplicada por
  `aplicar_migrations_pendentes.py` (só ela pendente; 223 versões); banco
  relido com 250 g. Não há publicação ativa em `cardapio_publico`.
- Google: `gbp.py cardapio --publicar` relido; lá o item não leva porção.
- Pendente: impresso no Canva (mesa `DAHYx8a8mAI` e A3 da entrada) ainda
  com 200 g; sem conector do Canva nesta sessão.

— Claude

## 2026-10-27 · Codex — Cardápio Teknisa salvo e conferido

- Entrega em `docs/TEKNISA_MIGRACAO_CARDAPIO.md`, unidade 0002/loja 0001.
  Base aprovada de 103 itens preservada, quatro retiradas respeitadas e
  Saipos sem alterações. Rum/Martini `1..1`, Molhos `1..10`, Gelo sem
  pergunta de molho e Cortesia sem Ypioca estão no plano aprovado.
- 45 SKUs novos, três inativações na árvore Praia e 159 preços relidos,
  com 48 inclusões e oito correções. Executivos comuns e Prime têm sete
  pratos cada, com preços e descrições. A árvore 9 mantém nomes/ativo
  globais; quatro preços locais foram associados à tabela 001.
- CAIXA e POS originais: 12 grupos, oito subgrupos, 124 botões e 123 SKUs
  por configuração. Cópia nativa só dos produtos CAIXA→POS e recarga
  integral conferidas; equipamentos e recebimentos preservados. Cópias
  00004/00005 conservadas. Os 494 vínculos usados em 48 SKUs foram
  auditados; outros quatro vínculos salvos são protótipos fora do menu.
- Loja vinculada à tabela 001. Os 125 SKUs necessários têm rota para a
  ELGIN existente: 49 inclusões, 181 registros relidos e 132 anteriores
  preservados. Nenhum teste físico de impressão ou venda real foi feito.
- Fiscal: leitura final de 185 códigos confirmou 48 impostos por unidade,
  52 NCMs e 23 CESTs executados, sem alterações fora dos campos autorizados.
  Embalagem lisa dobrável recebeu 48192000; Gelo, 22019000; Rolha, Tipo 09,
  Gênero 00 e NCM vazio. Beats usa analogia à referência Senses autorizada;
  Conhaque genérico mantém o cadastro anterior por falta de identificação.
- Pendência concreta: apoio Teknisa sem 03.021.01 para Stella Puro Gold
  `8.05.00.091.00` e 03.010.02 para Sukitas `8.10.05.091.00` e `.092.00`.
  Os três CESTs ficaram vazios. Implantação/suporte precisa incluir os dois
  códigos e associá-los aos três produtos. Antes de operar hoje, conferir
  carga no PC/POS, limites e totais do pedido, impressão e XML fiscal.
- Recibos, capturas, fontes oficiais, log e fechamento de 27/10 em
  `output/teknisa-2026-10-26/`, fora do Git; data da pasta é o início da
  tarefa. Hash da base aprovada intacto. QA dos layouts, preços, opcionais,
  impressão e campos fiscais passou dentro da cobertura registrada.
  Diffcheck e pares de orientação da raiz conferidos. Só os dois documentos
  de gestão foram versionados; sem migration, SQL ou deploy de código.

— Codex

## 2026-10-27 · Codex — Equipe cadastrada para a Praia no Teknisa

- Resultado em `docs/TEKNISA_ACESSOS_OPERACAO.md`. Oito operadores ativos,
  somente na unidade 0002 Praia: três gerentes no grupo 02 ADM-SUPERVISOR
  e cinco garçons no grupo 04 GARCOM. Dois novos e seis existentes, com
  uma reativação. Consulta independente confirmou oito, sem divergências.
- Cinco vendedores salvos e conferidos: quatro corrigidos em nome,
  nome fantasia e unidade, com os demais campos preservados; um novo
  vinculado ao operador aprovado. Taxas e comissão conferidas.
- Legado Imprensa: uma unidade bloqueada e sua loja inativada, com zero
  exclusões. Histórico preservado; Praia continua padrão, desbloqueada,
  com sua única loja ativa, conforme releitura.
- Recibos pessoais ficam em `output/teknisa-acessos-2026-10-27/`, fora dos
  repositórios. A documentação usa contagens e funções; nenhuma credencial
  foi coletada. Conferência de privacidade e diffcheck aprovados. Pares
  de orientações da raiz iguais às cópias versionadas.
- Pendentes os testes físicos de login, pedido com identificação do garçom,
  autorização de gerente e impressão. As três pendências CEST do cardápio
  continuam registradas no relatório de migração. Só os dois documentos
  de gestão foram alterados; sem migration, SQL ou deploy de código.

— Codex
