# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — três gerentes com vendedor vinculado e conferido para pedidos e vendas na Praia. Janela de troca de senha PDV entregue ao proprietário para preenchimento manual. Testes físicos, controle administrativo, três CESTs do cardápio e impresso Big Ben Fries seguem pendentes.

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

## 2026-10-27 · Codex — Permissões operacionais do PDV

- Regras detalhadas em `docs/TEKNISA_ACESSOS_OPERACAO.md`. Em Controle de
  Acesso ao Caixa, 23 permissões do grupo de garçons foram restringidas:
  cancelamentos, devoluções e alterações de cobranças exigem gerente;
  funções administrativas foram bloqueadas. Pedidos e recebimentos
  permanecem liberados. O usuário confirmou que garçons podem abrir e
  fechar o próprio caixa; essas permissões foram preservadas.
- O usuário confirmou os três gerentes como autorizadores. Foi incluído
  um vínculo com o grupo de gerentes, único autorizador dos garçons.
  Os 47 campos do grupo de gerentes permaneceram iguais.
- Releitura após recarregar a página: 47 permissões dos garçons e vínculo
  conferidos, sem divergências. Recibos privados em
  `output/teknisa-acessos-2026-10-27/permissoes-caixa-execucao.json` e
  `permissoes-caixa-qa47.json`. Nenhuma credencial foi coletada.
- Limite: a função Desistência do item (Balcão) continua liberada, mas a
  tela não explica sua aplicação ao carrinho de mesas ou o limite por
  etapa. Testar no aparelho a retirada antes do envio, a exigência de
  gerente após transmitir e o recebimento com abertura/fechamento do
  caixa. Nenhuma venda ou transação de pagamento foi executada.
- Alteração externa feita pela interface do Teknisa; somente dois
  documentos de gestão foram atualizados no workspace. Pendências
  fiscais, impressão e impresso Big Ben Fries preservadas.
- Controle do painel administrativo ainda requer revisão própria. A
  conferência desta etapa cobre ações do PDV; não comprova restrições
  por função no painel administrativo. Estado observado registrado no
  recibo privado de QA para continuidade.

— Codex

## 2026-10-27 · Claude — Semrush: uso final das cotas

- API Standard zerada (26.400 → 0). Banco de 415 palavras-chave e top 20 do
  Google para 5 buscas em `output/semrush-final-2026-10-27/` (fora do Git).
  5.200 unidades foram perdidas no primeiro lote; detalhes no `LEIA-ME.md`.
- Prompt Tracking 50/50: 26 perguntas genéricas PT e 8 EN adicionadas
  aos dois projetos de ChatGPT Fortaleza.
- Resumo em `docs/SEMRUSH_MAXIMO_2026-10-25.md`. Nenhum arquivo do site
  ou do banco foi alterado.
- Pendente: ler as novas perguntas e exportar o painel antes de 31/10
  (cobrança de US$ 199). O cancelamento é feito pelo proprietário.

— Claude

## 2026-10-27 · Codex — Gerentes como vendedores e troca manual de senha

- O usuário confirmou que os gerentes devem lançar pedidos e vender.
  Foram incluídos dois vendedores para gerentes e corrigidos nome,
  nome fantasia e unidade de um vendedor existente que já apontava para
  o operador gerente correto. Três registros relidos após recarga, sem
  divergências; todos ligados aos próprios operadores e à Praia, sem
  caixa fixo, com taxa diária e comissão zero. A equipe solicitada tem
  agora oito vínculos: cinco garçons e três gerentes.
- Recibos privados na pasta de acessos: `vendas-gerentes-execucao3.json`
  e `vendas-gerentes-qa3.json`. Sem venda real ou transação de pagamento.
  Permissões de gerente e demais vendedores preservados.
- Para as maquininhas, a opção correta é Operador → Ações → Alterar
  Senha PDV. Uma janela foi deixada aberta para o proprietário preencher
  e salvar. Nenhuma senha foi coletada ou alterada pelo agente. A troca
  das credenciais continua como intervenção manual do proprietário.
- Somente `docs/TEKNISA_ACESSOS_OPERACAO.md` e este canal foram alterados.
  Os testes no POS, o controle administrativo e as demais pendências
  anteriores continuam registrados.

— Codex

## 2026-10-27 · Claude — Site: eventos, jantar, Jardim Japonês

- Site `35578bb` publicado e conferido. Eventos agora tem texto, FAQ e schema.
  A home PT/EN fala de jantar. Página nova em `/jardim-japones/`. O pôr do sol
  ganhou "hoje". Sitemap reenviado ao Search Console.
- `reservation_cta_test.mjs` passou a cobrir `/jardim-japones/`. Os testes
  Deno rodaram no Node com um adaptador, porque o Deno não está neste PC.
- Pendente com navegador: incluir `/jardim-japones/` nas duas exceções da
  Cloudflare (robôs de IA e SemrushBot-SI) e corrigir a ficha do
  TripAdvisor `d23922740`, que ainda aparece como "Barra Sol Sir Fisher".
- Detalhes em `docs/SEMRUSH_MAXIMO_2026-10-25.md`.

— Claude

