# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre: Codex concluiu a pesquisa de locais e lance do ChatGPT Ads. Todos os níveis seguem pausados.

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

## 2026-11-07 · Codex — Anúncio efetivamente criado no Ads Manager

Criação confirmada por upload, campanha, grupo e anúncio, seguida de leituras
independentes e conferência da prévia na interface. Peça com foto do acervo,
título `Sir Fisher na Beira-Mar` e descrição `Almoço e jantar em Fortaleza.
Veja o cardápio.`. Todos pausados; a OpenAI aprovou a peça na leitura final. Detalhes
em `docs/PLANO_CHATGPT_ADS_2026-11-07.md`; recibo sem credenciais em
`tmp/chatgpt-ads/criacao-2026-11-07.json`, ignorado, e captura da peça no output.

Orçamento total R$300, 09/11 às 00h até 16/11 às 00h em Fortaleza. Corrigida
a incompatibilidade do plano: orçamento total exige lance manual no preflight
do conector; configurado máximo de R$3,50/clique. Geografia Ceará provisória,
com bloqueio de ativação anotado na descrição. Conector, API e interface só
devolveram CEPs para Fortaleza; a cidade segue sem registro confirmado. Não
usar identificadores externos ou afirmar cobertura municipal a partir disso.
Ativar requer resolver/aprovar abrangência e autorização
de despesa. Conferir saldo mensal antes de liberar, respeitando R$1.000/mês.

Nenhuma campanha anterior, código ou banco foi alterado. A edição da campanha
antiga foi cancelada sem salvar após a inspeção do seletor. Diff, links locais,
imagem estática, contagem de caracteres, datas e orçamento conferidos.

## 2026-11-08 · Claude — Fechamento de caixa no Teknisa: relatórios e impressão

Com autorização do proprietário, os POS 001, 002 e 003 deixaram de pedir
confirmação antes de imprimir o Recibo de Sangria e o Relatório de Produtos
no fechamento. A gravação e a releitura foram conferidas. O relatório Resumo
do Caixa → Comparativo Fechamento Caixa (Operador) separa os fechamentos por
turno e serve para reimprimir. Detalhes, comparação com os cupons e com a
Stone e as pendências estão em `docs/TEKNISA_ACESSOS_OPERACAO.md`. Falta
testar no aparelho. Sem mudança de banco, site ou reservas.

Os 58,75 a mais na Stone do POS 002 em 07/11 foram explicados venda a venda:
cartões de duas mesas do CAIXA 001 passaram na maquininha do POS 002, e seis
vendas do POS 002 foram pagas em outra maquininha. Não falta dinheiro. O
pedido extra do XML de 07/11 à API Stone respondeu HTTP 400 (arquivo ainda
não gerado) e não foi registrado no controle da rotina.


## 2026-11-08 · Codex: Fortaleza e CEPs no ChatGPT Ads

O proprietário recusou ativação estadual. Resultado em
`docs/GEOGRAFIA_CHATGPT_ADS_2026-11-08.md`, com aviso no plano existente.
Campanha, grupo e anúncio relidos: pausados; peça aprovada. Nenhuma
alteração no Ads Manager, banco, código, site ou reservas.

A documentação permite cidades e CEPs onde disponíveis. A cidade continua
sem registro confirmado. Cinco setores postais brasileiros de Fortaleza
foram encontrados; o CEP completo 60165-121 devolve o setor 60165. Priorizar
esse setor na validação futura. Catálogo não comprova elegibilidade,
limites no mapa ou volume. Sem cobertura local confirmada, manter pausa.
R$3,50 permanece teto experimental sem aumento; Target CPC é meta média.
R$300 totais e R$1.000/mês permanecem limites, sem autorização de entrega.
Fontes oficiais, leituras, links e diff conferidos. Somente documentos;
sem migração ou implantação funcional. Não foram configurados os CEPs.
