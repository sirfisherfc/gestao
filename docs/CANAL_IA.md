# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre. Cabeçalho de vouchers corrigido pelo carregamento de product-pages.css. Quality/frontend passaram; publicação pelo Pages deste commit. Browser integrado continua indisponível.

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

## 2026-11-04 · Codex — Diagnóstico do saldo BB com Rende Fácil

Conferidos os dois CSVs de conta corrente de outubro indicados pelo usuário:
arquivos idênticos, leitura validada sem rejeições e todos os movimentos já
presentes em raw_bb pelas chaves do importador. O fechamento do arquivo
reconcilia; há transferências para a aplicação automática BB Rende Fácil.

Consultas exclusivamente pela rota Management API query/read-only do portal
confirmaram conta BB ativa, saldo calculado por movimentos zerado e exclusão
de contas zeradas na view painel_saldo_por_conta. O aplicativo bancário da
imagem combina conta corrente e Rende Fácil; o CSV não informa o saldo da
aplicação nem os rendimentos. Não inferir o saldo combinado apenas pelos
débitos de aplicação. Falta o extrato Rende Fácil do período para reconciliar
e implementar sua inclusão no caixa com precisão.

Documentada a limitação em scripts/importacao/README.md. Nenhuma importação,
escrita no banco, migration ou alteração do painel nesta entrega. CSVs e
valores financeiros não foram incluídos na documentação. Validação: parser
real em leitura, comparação de hashes, consultas agregadas e git diff --check.

## 2026-11-04 · Codex — Rende Fácil incluído no caixa

Complementa o diagnóstico anterior: o proprietário confirmou saldo inicial
zero e início do produto em outubro, e pediu aplicar a correção. Essa
confirmação permite reconstruir aplicações menos resgates sem exigir outro
extrato para recuperar o dinheiro transferido. Rendimentos/tributos ausentes
continuam sem estimativa e podem explicar diferença para o saldo do banco.

Migration 20261104180315 aplicada e registrada no portal. Conta/fonte separada
bb_rende_facil deriva as contrapartidas assinadas de raw_bb, com base zero em
30/09 e vigência em 01/10/2026. Respeita conta de origem e vigência; mantém
saldo da conta corrente, hashes e dados brutos intactos. Não inclui outros
fundos. Nova opção no editor de parâmetros e whitelist da RPC administrativa.

A classificação automática do tipo BB Rende Fácil passa a transferência
entre contas, preservando ajustes manuais; conferida ausência do produto na
DRE. A migration protege saldos preexistentes, configuração idempotente e
saldo não negativo. Nenhuma tabela de reservas ou autenticação foi alterada.

Validação: dez verificações SQL com fixtures sintéticas em schemas isolados,
rollback obrigatório e schemas removidos; aplicação/resgate, filtro por conta
e produto, base zero, DRE, grants, reexecução e rejeição de saldo negativo.
Ensaio completo sobre a base real com rollback passou antes da aplicação.
Refresh resiliente atualizou dez objetos sem falhas; leitura posterior pela
Management API confirmou migration, conta no painel e exclusão da DRE.
Contratos financeiros, acessos, catálogo de migrations e quality gate local
passaram; Node indisponível localmente, verificação JS pelo CI. Acrescentada
execução SQL em PostgreSQL descartável ao workflow Quality. Documentação de
schema e importação atualizada; valores e CSVs não versionados.

## 2026-11-04 · Codex — Vouchers de benefício nos dois portais

Gestão: rotina, emissão idempotente, oito motivos internos + Outro livre,
indicadores separados de reais/percentuais, filtros, detalhes e cancelamento.
PNG por template oficial; compartilhamento nativo ou download + WhatsApp
com anexo manual. Regras e arquivos em docs/VOUCHERS.md. Reserva/Réveillon,
POS e financeiro preservados. Reservas d553098 publicado: build e hashes
HTTP conferidos; consulta, confirmação e erro de rede sem reenviar resgate.

Migrations 20261104200024 e 20261104202352 aplicadas/registradas e relidas.
Três tabelas privadas com RLS; implementações privilegiadas privadas e
wrappers públicos INVOKER. Anon negado inclusive por HTTP. Perfis existentes,
código de 60 bits, rate limit e lock entre uso/cancelamento. Estado e evento
na mesma transação. Retry de emissão com dados diferentes avisa o conflito.

Testes: SQL isolado com limpeza, colisões/retries, motivos/perfis/validade,
grants e três disputas concorrentes. Perfis reais com rollback de fixtures.
14 testes gestão e 20 reservas passaram; cinco PNGs renderizados e
inspecionados, nomes de 160 caracteres e valores altos. Quality, acessos,
frontend, financeiro e catálogo passaram. Advisor sem WARN/ERROR de vouchers;
só INFO de RLS privado sem policy. CI e documentação incluídos.

Pendência real: Browser integrado indisponível. Não afirmar login interativo,
layout mobile ou envio real WhatsApp verificados; testes de estado e
compartilhamento simulado não substituem essa conferência.

## 2026-11-04 · Codex — Cabeçalho da rotina de vouchers

Corrigido vouchers.html: faltava carregar assets/product-pages.css, que
define fundo/posição do header e alinhamento de head-row/tabs. Reutilizado
o CSS das outras rotinas sem alterar estilos globais. Arquivos alterados:
vouchers.html e este canal. Sem mudança de banco, regras ou outros portais.
Quality gate com Node, contratos frontend e git diff --check passaram.
Browser integrado retornou indisponível (lista vazia); não afirmar QA visual
interativo. Publicação segue o workflow Pages; conferir HTML/CSS por HTTP.
