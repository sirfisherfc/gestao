# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 Livre — Claude concluiu ajuste de impressão do fechamento nos POS do Teknisa (só docs no Git). Site e reservas sem alterações.

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

## 2026-11-07 · Codex — Email sobre lances e avaliação do ChatGPT Ads

Leitura completa do email de 05/11, documentação oficial atual, conta Sir
Fisher, campanhas, fonte/metas de conversão e GA4. O registro está em
`docs/AVALIACAO_CHATGPT_ADS_2026-11-07.md`. Target CPC/CPA começam em 09/11;
são metas de custo médio. O teste de outubro tem sinais de intenção e zero
metas atribuídas na consulta atual. Clientes sem reserva seguem com cobertura
desconhecida. A avaliação é aguardar evidência comercial antes de novo gasto.
O status cadastral ativo da campanha convive com término em 20/10.

Alterados apenas este canal e o documento da avaliação, sem dados financeiros
brutos, credenciais ou identificadores internos. Nenhuma alteração de anúncio,
verba, código ou banco. Links locais, fontes oficiais, datas, cobertura dos
relatórios e diff conferidos. A disponibilidade das novas estratégias na
conta precisa de leitura após 09/11; não houve autorização de nova despesa.

## 2026-11-07 · Codex — Estratégia para visitas com ChatGPT Ads

O proprietário definiu divulgação ampla para visitas e delegou as escolhas
com os dados existentes, com teto agregado de R$1.000/mês. Proposta em
`docs/PLANO_CHATGPT_ADS_2026-11-07.md`: refeição na Beira-Mar, comida e vista,
uma campanha/grupo, até dois anúncios, cliques automáticos e R$300 de teste
por até sete dias. Restante depende de saldo mensal e resultados. A produção
da peça permanece para a etapa seguinte; nenhuma gravação no Ads Manager.

Fontes oficiais e acervo conferidos. Home, Conheça e cardápio responderam
HTTP 200. A consulta geográfica retornou CEPs, sem resolver a cidade. O teto
global da conta está indisponível; orçamento total e conciliação do gasto
mensal precisam anteceder a ativação. Margem gerencial histórica não comprova
contribuição dos clientes adquiridos. Sem consulta nova ao banco ou alteração
de código. Alterados só o plano e este canal; diff e links locais conferidos.

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
