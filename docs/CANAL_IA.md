# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre — Claude concluiu consulta sobre a reimpressão do fechamento no Teknisa (só documentação; nada alterado no sistema). Site e reservas sem alterações.

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

## 2026-11-05 · Codex — Aviso de vencimento e consulta compacta

Reservas: consulta vencida abre alertdialog em destaque, orienta consultar o
emissor, mostra código/data e botão Entendi. A orientação também fica no card.
Aviso reaparece em recusa por vencimento entre consulta/confirmação, inclusive
com reconsulta indisponível; fallback por alerta nativo. Fechamento devolve
foco ao código. Retirados campo Unidade e botão Consultar novamente; consultas
seguem no formulário do topo e ações indisponíveis não deixam espaço vazio.
Alterados HTML, CSS, controlador, texto de status, teste do controlador e docs
do reservas. Gestão só este registro; sem mudanças de banco ou outros portais.
37 testes passaram, incluindo controlador real com DOM adaptado e fluxo de
resgate/reconsulta. Sintaxe JS, IDs de HTML/controlador e diff conferidos.
Não afirmar teste visual interativo; navegador integrado indisponível nesta
sessão. Publicação via Pages; conferir artefato e workflow do mesmo commit.

## 2026-11-05 · Codex — Renovação, detalhes recolhidos e alertas por situação

Gestão: vencido oferece Renovar validade com sugestão de 30 dias, código
preservado e histórico auditado. Condições/Histórico recolhidos; removido
aviso de compartilhamento indisponível, botões inativos de imagem e coluna
de prévia vazia. Usados/cancelados continuam sem edição. Alterados controlador,
CSS, testes de UI/SQL, workflow, instalador e documentação.
Migration 20261105145812 aplicada/registrada: gate de edição aceita também
expired, nova data de hoje em diante, evento de renovação com snapshots e
incremento de revisão. Grants, lock, gates e validações restantes preservados.
102 verificações SQL isoladas e ensaio com perfis reais passaram, fixtures
revertidas; leitura confirmou versão e Advisor sem WARN/ERROR de vouchers.
23 testes JS de gestão passaram, incluindo controlador com DOM adaptado.

Reservas: popup e destaque de vencido estendidos a utilizado/cancelado,
com mensagens e cores próprias. Sucesso de uso não abre alerta de já utilizado.
Retirada a frase explicativa do período da lista, preservando a janela no
servidor. 44 testes JS passaram. HTML/JS/CSS, teste de UI e docs atualizados.
Sem renovação automática de dados reais. Publicar/conferir Pages de ambos
os projetos; navegador indisponível, sem alegar QA visual interativo.

## 2026-11-05 · Claude — Teknisa: multiplicador de prato com composição

Só leitura no painel, nada gravado. "Multiplicador Produto" já está liberado
para garçom e gerente; efeito em Promoção Combinada não testado no POS.
Registro em `docs/TEKNISA_ACESSOS_OPERACAO.md`. `node` ausente no PATH deste PC.

Depois: um gerente incluído no perfil Gerente - Reposicao (gravado e relido).
Aviso: as abas Operadores dos perfis 12 e Administrador vieram vazias antes
disso, ao contrário do registro de 30/10. Causa não apurada; login não testado.

## 2026-11-06 · Claude — Charlotes de morango e chocolate no cardápio

Entraram as duas, a R$ 18: catálogo (80 itens), migration 20261106180000
aplicada e relida, site 0237f2c e Google (83 itens/opções, relido). Sem
publicação ativa no banco; o site segue na cópia embutida. Alérgenos sem ficha
técnica, a conferir com receita ou rótulo. Aceitação: 47 passaram, 0 falhas.

Pendente: Teknisa (sessão expirada, login é do proprietário; produto novo pede
cadastro, imposto, preço, loja, botão e foto); impresso da mesa em rascunho no
Canva aguardando aprovação; A3 da entrada não alterado. `git push` no OneDrive
pode acusar falha ao gravar a referência local mesmo com o envio concluído:
conferir com `git ls-remote` e `git fetch`.

## 2026-11-06 · Claude — Charlotes no Teknisa

Produtos `8.00.20.022.00` e `.023.00` criados e relidos: R$ 18, NCM 21069090,
COZINHA, botões 05/06 de Sobremesa em Caixa e POS, fotos com bytes conferidos.
Sequência e contratos no guia da ferramenta. Não testado no aparelho. Canva
continua pendente: rascunho da mesa sem salvar e A3 sem alteração.

## 2026-11-07 · Claude — Reimpressão do fechamento de caixa no Teknisa

Consulta sem gravação no Teknisa. O registro está em
`docs/TEKNISA_ACESSOS_OPERACAO.md`. Pelo recibo de 27/10, o grupo
`02 — ADM - SUPERVISOR` tem Fechar Caixa, Leitura X e Relatórios Fiscais
liberados. Não existe permissão própria para reimprimir o fechamento. A nota
da Teknisa indica que a reimpressão vale até o caixa ser reaberto. Falta
testar no aparelho com o login de um gerente. Alterados só documentos; não
houve mudança de banco, site ou reservas.
