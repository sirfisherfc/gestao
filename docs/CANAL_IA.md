# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — ferramenta do Teknisa padronizada; impressão conferida nos 181 vínculos e vendas por garçom integradas. Teste físico, escrita de cadastro/preços e regra comercial de comissão pendentes conforme o guia.

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
  Cloudflare (robôs de IA e SemrushBot-SI).
- TripAdvisor `d23922740`: o proprietário conferiu em 27/10 que a ficha já se
  chama "Sir Fisher" e está reivindicada. Só o endereço ainda tem
  `Barra_Sol_Sir_Fisher`. Pendências reais: a categoria aparece como "bares e
  pubs" (nº 20 de 82) e a ficha tem 11 avaliações com nota 3,9.
- Site `49c9932`: a página do Jardim Japonês ganhou cinco fotos do Wikimedia
  Commons (CC BY-SA 4.0, com autor e licença na legenda), um CSS próprio com
  layout de desktop e uma faixa de destaque para o Sir Fisher, com reserva,
  cardápio e rota. No celular há uma barra fixa. As fotos do jardim são de
  2023 e 2025, anteriores à reforma.
- Detalhes em `docs/SEMRUSH_MAXIMO_2026-10-25.md`.

— Claude


## 2026-10-27 · Codex — Padronização dos oito operadores e fichas abertas

- Nomes completos dos oito conferidos. Dois nomes de acesso corrigidos e
  salvos; seis já seguiam o padrão do primeiro nome em minúsculas e sem
  acentos. Permissões, vendedores e demais campos preservados.
- O proprietário forneceu e-mails pessoais reais. Oito fichas foram
  preenchidas com os novos endereços. O salvamento dos e-mails pede
  confirmação para gerar e enviar senha provisória; a confirmação foi
  cancelada na preparação. Zero e-mails novos salvos pelo agente.
- Conforme o pedido final, ficaram oito abas do Teknisa, uma por pessoa,
  identificadas pelo nome. A tela extra foi fechada. O proprietário
  conclui Salvar e a validação do e-mail e depois usa Ações → Alterar
  Senha PDV. Zero senhas lidas, preenchidas ou alteradas pelo agente.
- Rascunhos e organização das abas conferidos. Recibos privados na pasta
  de acessos: `padronizacao-equipe-rascunhos8.json`,
  `padronizacao-equipe-qa-rascunhos8.json` e
  `padronizacao-equipe-abas-handoff8.json`. Nenhum dado de nascimento,
  e-mail pessoal ou credencial foi incluído no Git.
- A confirmação dos e-mails e a troca das senhas aguardam o proprietário.
  Testes físicos, controle administrativo e pendências anteriores
  permanecem nos relatórios. Somente dois documentos de gestão alterados.

— Codex

## 2026-10-27 · Claude — Erro "grupo que não existe" na POS e Rolha

- Causa: os 8 subgrupos da migração (Refrigerante lata, Caipirinha,
  Caipiroska, Caipifruta, Gin Tônica, Rum, Martini, Molhos) não aparecem
  no PC nem na POS. O erro "página 1, número 02" é o subgrupo
  Caipirinha. No PC, os refrigerantes sumiram.
- 29 botões diretos criados na POS 00002 e copiados ao CAIXA 00001 por
  "Exportar Configuração (Sobrepor apenas produtos)". Detalhes e posições em
  `docs/TEKNISA_MIGRACAO_CARDAPIO.md`.
- A exclusão dos subgrupos foi bloqueada para o agente. Ordem da TI:
  excluir todos os produtos do subgrupo e depois o subgrupo. Excluir só
  o subgrupo deixa registros órfãos.
- Rolha agora é faturada como gelo: NCM 22019000, Gênero 22, Tipo 04 e
  Origem 0, relidos após recarga.
- O Chrome desconectou várias vezes. Combinar as etapas em lotes ajudou.
  Em lista de consulta do Teknisa, esperar 2 a 3 s antes de digitar na busca.

— Claude

- Atualização: a pedido do proprietário, os 8 subgrupos foram removidos
  dos dois layouts, primeiro os produtos e depois o subgrupo. Molhos e
  Caipiroska do CAIXA foram excluídos durante edição simultânea; se o
  erro voltar, procurar produto órfão. Releitura: nenhum subgrupo.

— Claude

## 2026-10-27 · Codex — Avisos de notas e impressão da parcial no POS

- Registrado em docs/TEKNISA_ACESSOS_OPERACAO.md: fotos mostram notas
  pendentes/rejeitadas desde 06/08/2026 e ausência de impressora parametrizada
  para a parcial. O proprietário confirmou saída na própria maquininha.
- Rota de produtos para ELGIN e permissão para solicitar parcial não
  comprovam a configuração da impressora interna. Conferir caixa/POS e
  parâmetros da função; teste físico continua pendente.
- Guia oficial consultado. A fila fiscal precisa de leitura da filial,
  documentos e motivo da rejeição antes de transmitir. Nenhuma nota foi
  transmitida, cancelada ou alterada.
- Conexão de navegador sem navegadores disponíveis nesta sessão; nenhum
  parâmetro consultado ou salvo ao vivo. Não atribuir os avisos ao Chrome
  sem evidência. Sem migration ou alteração de código da aplicação.
- Revisão do diff e privacidade; orientações da raiz idênticas às cópias
  versionadas. Repositórios inicialmente limpos e pulls sem atualização.
  Git avisou sobre permissão de limpeza de dois metadados de worktrees
  antigos; nenhum deles foi removido manualmente.

— Codex

## 2026-10-27 · Codex — Viabilidade de integração com APIs do Teknisa

- Pesquisa pública em <https://www.teknisa.com/api>: Retail oferece
  consultas de vendas, estoque, fechamentos e cardápio; ERP lista inclusão
  de produtos. A documentação detalhada depende do gerente de contas e
  as integrações estão sujeitas a condições comerciais.
- O catálogo público ainda deixa por confirmar a edição de preços,
  layouts do caixa e permissões de operadores, além da disponibilidade
  desses recursos no contrato e na unidade do Sir Fisher.
- <https://www.teknisa.com/produtos/ia/mcp> anuncia um MCP com lançamento
  em breve, inicialmente para consultar vendas. Essa oferta ainda precisa
  de confirmação de disponibilidade e cobre somente leitura.
- Proposta: conector local com comandos definidos, retorno resumido,
  prévia das alterações e releitura após gravação. Medir tempo e tokens
  em um piloto representativo antes de estimar a economia. Chamadas
  internas do painel exigem levantamento próprio de autenticação,
  regras e estabilidade, caso a API oficial deixe lacunas.
- Esta etapa consultou documentos existentes e páginas públicas. A
  implementação, a autenticação real e os testes de escrita permanecem
  por fazer. Apenas este canal foi alterado; sem migration ou alteração
  das configurações do Teknisa. Validação: revisão das fontes, diff e
  privacidade; conferir sincronização dos repositórios ao concluir.

— Codex

## 2026-10-27 · Codex — Impressão de cancelamento em Produtos por Loja

- Pedido refinado pelo proprietário: campo **Imprime Cancelamento de
  Pedido**, em Cadastro de Loja → Produtos por Loja. Unidade Praia 0002,
  loja 0001. Foram encontrados 181 vínculos; um já estava marcado.
- Foram ativados 180: um pela interface para observar a gravação, dois
  no piloto da API interna e 177 em oito lotes de até 25. Releitura final:
  181 marcados, zero pendentes e zero diferenças nos demais campos dos
  vínculos. Nenhum pedido, venda ou cancelamento real foi executado.
- Conector específico em `scripts/teknisa/produtos_loja.mjs`, testes em
  `scripts/teknisa/test_produtos_loja.mjs` e guia em
  `docs/TEKNISA_INTEGRACAO_API.md`. O workflow de qualidade inclui os oito
  testes sem rede. A autenticação continua na sessão atual do navegador;
  o conector não cria credenciais nem publica um serviço de acesso.
- Recibo privado na raiz do workspace, em
  `output/teknisa-cancelamento-2026-10-27/cancelamento-execucao-auditoria.json`.
  Sem cabeçalhos de autenticação no arquivo ou no Git. Conferência da
  tela após recarga e testes locais integram a validação da entrega.
- Sem migration. Teste de impressão no aparelho continua pendente.
  Pendências anteriores do POS preservadas.

— Codex

## 2026-10-27 · Codex — Ferramenta do Teknisa e impressão por preparo

- Pedido analisado e reformulado em `docs/TEKNISA_PEDIDO_REFORMULADO.md`.
  Entrada `scripts/teknisa/teknisa.mjs`, módulos de recursos, sessão,
  planos, recibos e cálculos; guia em `scripts/teknisa/README.md`.
- Raiz e gestão orientam as IAs a usar a ferramenta antes de repetir a
  navegação. Cópias de AGENTS/README da raiz reconciliadas em workspace.
- Conexão reconstruída após reinício do runtime; catálogo paginado com
  185 produtos, tabela com 159 preços e impressoras consultados ao vivo.
  Gravação de nomes e rotas executada pela ferramenta, com recibos em
  `tmp/teknisa/`, ignorado. Autenticação permanece somente em memória.
- Códigos preservados: `00001 COZINHA`, `00003 BALCAO`, `00004 BAR` e
  `00002 POS`. A leitura anterior já tinha 82/79/20 vínculos nos três
  códigos; a hipótese de todos em 00001 foi corrigida. Agora são
  82/67/32, após 42 ajustes e 139 preservados, com cancelamento marcado
  nos 181 e zero sem rota. Conexões e modelos das impressoras preservados.
- O proprietário definiu Balcão para bebidas prontas, cervejas e doses;
  Bar para preparados e sucos; Cozinha para alimentos. Fontes privadas
  e resultado em `output/teknisa-impressoras-2026-10-27/`, na raiz.
- 25 testes locais cobrem os lotes, falhas parciais, retomada, escopo,
  recibos e comissão sem assumir regra. Workflow de qualidade atualizado.
  Escrita de produtos/preços ainda exige contrato validado. O relatório
  de produtividade por vendedor foi integrado e consultado de 01/10 a
  27/10 (23 linhas, três vendedores), sem expor valores ou dados pessoais.
  A comissão exige a regra comercial; os comandos explicitam esse limite.
- Sem migration ou pedido de teste. A tela foi conferida após nova
  consulta; teste físico pendente. Validações e publicação são relatadas
  na entrega.

— Codex

## 2026-10-30 · Claude — Ajustes do Teknisa e opções do cardápio por API

- Pedido do proprietário: senha por e-mail de dois operadores, login do
  caixa geral reaproveitando um ex-garçom, liberar mesa sem gerente,
  arroz do prato para dois, molho grátis nos aperitivos, batata ou
  macaxeira, suco de limão, retirar salmão e letra da comanda. Registros
  em `docs/TEKNISA_ACESSOS_OPERACAO.md` e `docs/TEKNISA_MIGRACAO_CARDAPIO.md`;
  recibo privado em `output/teknisa-ajustes-2026-10-30/` na raiz.
- Novo `scripts/teknisa/observacoes.mjs`: lista e altera opções por
  produto com prévia, recibo, releitura e reversão (comandos
  `observacoes.*`). `WRITE_PATHS` passou a definir as gravações aceitas
  pelo transporte. 28 testes passam; workflow inclui `test_observacoes.mjs`.
  Contratos de operador, vendedor, permissões, layout e produto ficaram
  no README da ferramenta, ainda sem comando.
- Lição: o save do vendedor sem os campos completos da interface responde
  500 depois de gravar. Sempre reler antes de repetir.
- Pendentes: fonte da comanda (nenhum campo no painel; suporte Teknisa),
  teste no POS da escolha de acompanhamento/sabor e da liberação de mesa,
  senha PDV do login caixa pelo proprietário. Sem migration nem deploy.
- Não toquei nos arquivos Stone nem na linha de status da sessão 🔴.

— Claude
