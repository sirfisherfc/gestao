# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre — Codex publicou e conferiu o ajuste visual dos números de mesas reservadas no mapa público de Réveillon.

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

## 2026-11-07 · Claude — Reimpressão do fechamento de caixa no Teknisa

Consulta sem gravação no Teknisa. O registro está em
`docs/TEKNISA_ACESSOS_OPERACAO.md`. Pelo recibo de 27/10, o grupo
`02 — ADM - SUPERVISOR` tem Fechar Caixa, Leitura X e Relatórios Fiscais
liberados. Não existe permissão própria para reimprimir o fechamento. A nota
da Teknisa indica que a reimpressão vale até o caixa ser reaberto. Falta
testar no aparelho com o login de um gerente. Alterados só documentos; não
houve mudança de banco, site ou reservas.

## 2026-11-07 · Codex — Sinal do Réveillon com qualquer pagamento positivo

Migration `20261107175623_reveillon_any_positive_deposit.sql` aplicada e
registrada no `portal`. `rv_admin_register_payment` aceita valores a partir
de R$ 0,01 e `rv_recalc_booking` passa a marcar `sinal_pago` com pagamento
positivo ativo. O percentual de 30% permanece como sugestão. Pagamentos
estornados deixam de contar; quitação e cortesia mantêm as regras existentes.

A migration ajustou as pré-reservas elegíveis, com data do primeiro pagamento
ativo e histórico da mudança. Os pagamentos e a fila de e-mails permaneceram
iguais. Instalações sem o módulo de Réveillon passam pela guarda de ausência.
Helpers seguem internos e a RPC administrativa preserva a autorização atual.
Interface, fontes SQL, testes e documentação do módulo ficam no reservas.

Passaram: cadeia de 240 migrations, diff, paridade das definições, ensaio
transacional da migration inteira e reaplicação sem novo histórico. Após
aplicar, passaram novamente os testes SQL de R$ 0,01 nas três formas de
pagamento, estornos parcial/total, desconto, total zero, quitação e ACL.
Leitura confirmou a atualização do estado. Advisors sem achados novos.
No reservas, o fluxo com RPC simulada passou em navegador a 390 e 1366 px,
com imagens conferidas e console limpo. Backend publicado e conferido.
Reservas publicado em `41fb2c4`: Pages concluído no mesmo commit, HTTP 200
e arquivos da interface publicados conferem com os locais, ajustando CRLF.

## 2026-11-07 · Codex — Números mais apagados nas mesas reservadas

Reservas publicado em `e5715ee`: a cor do número das mesas reservadas no mapa
público passou de `#7c7468` para `#a69e90`, mais próxima do corpo `#c7c0b4`.
O seletor atua em `.rv-table--reservada .rv-table__label`. Alterados
`assets/css/reveillon-map.css`, a versão de importação em
`assets/css/reveillon.css` e a versão do link em `reveillon.html`.
Mesas bloqueadas, outras situações e painel administrativo preservados.
Sem migration ou alteração de banco; gestão contém apenas este registro.

Diff conferido. Navegador Edge a 390 e 1366 px confirmou as cores calculadas,
texto branco nas mesas livres e ausência de erros JS; imagens conferidas.
Pages concluiu no mesmo commit (run `42417713555`). A página publicada,
sem interceptação, passou na mesma conferência. HTTP 200 e conteúdo dos
arquivos conferem com os locais nas URLs CSS com `?v=20261107-reservadas`.
Site e reservas sincronizados, sem pendência funcional ou de publicação.
