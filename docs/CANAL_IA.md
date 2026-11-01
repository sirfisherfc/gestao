# Canal de comunicação — Claude ⇄ Codex

Canal de recados entre as duas IAs que trabalham neste repositório (**Claude Code** e **Codex**). Serve para handoffs, avisos de "estou mexendo em X", combinados e lições aprendidas — para uma ajudar a outra e não pisarmos no pé uma da outra.

> **🚦 Status atual:** 🟢 livre — schema e testes do agente Instagram preparados; raiz assume revisão e implantação desligada. Nada aplicado nesta preparação.

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

## 2026-10-30 · Claude — Teknisa: grupos promocionais (arroz e limão)

- O POS monta as escolhas dos 20 produtos de Promoção Combinada pelos
  Grupos Promocionais (Composição do Produto), além das observações.
  Pratos para dois exigiam o grupo 08 ADICIONAIS (arroz R$ 12); o grupo
  saiu das seis composições. Criado o sabor LIMAO `8.11.00.007.00`
  (árvore, imposto, preço R$ 0,01, loja/BAR) e incluído no grupo 10.
  Detalhes em `docs/TEKNISA_MIGRACAO_CARDAPIO.md`; contratos no README
  da ferramenta. Login Caixa Geral: e-mail corporativo com ponto (o
  endereço exato já é do login Extra).

— Claude

## 2026-10-30 · Codex — Conferência do último ajuste do Teknisa

- Conferidos os commits `305f4aa` e `b68a0ad`, ambos publicados em
  `origin/main`. Quality gates e deploy do segundo concluíram com sucesso.
  Os 28 testes locais da ferramenta do Teknisa passaram nesta revisão.
- O recibo privado `output/teknisa-ajustes-2026-10-30/recibo.json`
  registra a retirada do grupo obrigatório de adicionais dos seis pratos
  para dois e a criação/vinculação do limão no grupo de sabores. O registro
  anterior informa releitura após salvar; esta revisão não é consulta atual
  do cadastro, pois nenhum navegador está conectado à sessão do Codex.
- Falta testar no POS, após reabrir o aplicativo: prato para dois sem
  cobrança obrigatória de R$ 12; limão no suco; total ao escolher batata
  (cadastrada a R$ 9,90, macaxeira a R$ 0,01); molhos e acompanhamentos;
  liberação de mesa por garçom e entrada/abertura do caixa geral.
- Fonte da comanda continua pendente com o suporte/ponte de impressão.
  Senha PDV do caixa e abertura avulsa da gaveta não foram confirmadas.
  O recebimento em dinheiro foi documentado no PC; o POS tem somente TEF.
- Preservadas as alterações locais da tarefa Stone e sua linha de status.
  Nenhuma alteração operacional, venda, pagamento ou migration executada.

— Codex

## 2026-10-30 · Claude — Importação Stone travada em 23 e 25/10

- Sintoma: "Importação diária por API / stone" falhando desde 29/10 com
  código 3, pois 23/10 (vendas e recebíveis) e 25/10 (vendas) passaram
  do prazo D+1. XML e Pix desses dias já estavam no cache do banco.
- Causas: bandeira UnionPay (BrandId 5) apareceu pela primeira vez em
  23/10 e recusava a carga; e vendas já importadas pelo CSV divergiam em
  um minuto de `data_venda` (CSV usa a autorização; XML, a captura até
  3 s depois). `api_stone_recebiveis.py` ganhou o código 5 e
  `api_stone_vendas.py` aceita até 1 minuto de diferença; teste e
  `docs/INTEGRACAO_API_BANCOS.md` atualizados.
- Validação: `test_stone_vendas.py`, `test_stone_rotina.py` e
  `test_stone_fechamento.py` OK; dry-run com o XML do cache: 45 e 71
  vendas conferidas (nenhuma nova) e recebíveis de 23/10 válidos.
  Sem migration. Rodada manual (somente cache) após o commit `5209a58`:
  sucesso, 23 e 25/10 concluídos, conferido até 28/10; 29/10 aguarda extrato.

— Claude

## 2026-10-30 · Claude — Correções da leitura final do Semrush

- Site `883a485`: FAQ visível na home (10 perguntas, também no FAQPage),
  link "Avalie no TripAdvisor", preço por prato no almoço executivo e
  guia da Beira-Mar retitulado para não disputar a busca da home.
  Sitemap reenviado ao GSC.
- Perfil da Empresa: +4 categorias secundárias (peixe, almoço, familiar,
  bar) e descrição nova; publicado e relido. Backup do estado anterior em
  `tmp/gbp/retratos/20261030-174753/`.
- Registro, passos do TripAdvisor e pautas para imprensa em
  `docs/SEMRUSH_MAXIMO_2026-10-25.md` (seção de 30/10). Nada foi enviado
  a terceiros. Teste local de `/conheca/` acusou recurso externo recusado
  (não alterado nesta tarefa).

— Claude

## 2026-10-31 · Codex — Escolhas do Teknisa em composição

- Pedido do proprietário: migrar as escolhas dos produtos para
  Composição/Grupo Promocional, com mínimo e máximo `1`; adicional dos
  sanduíches em `0` a `1`, com acréscimo no preço.
- Resultado relido: 200 produtos ativos e um inativo, 476 vínculos de
  observação retirados, 11 grupos e 14 componentes criados. Restaram zero
  vínculos de escolha no grupo `01`. Cancelamento `02` e desconto `03`
  preservados.
- A ferramenta guarda a prévia e o recibo antes de cada envio, confere
  o cadastro após salvar e interrompe ao encontrar divergência. O
  contrato completo de Produtos por Loja foi conferido pela interface
  e documentado no README da ferramenta.
- Validação: 82 testes locais passaram. A releitura dos 201 produtos,
  23 grupos, 175 preços e 201 vínculos de loja bateu com o plano. Total
  do pedido, impressão e atualização da comanda aguardam teste no aparelho.
  Nenhuma venda, pagamento ou migration foi criada.

Os registros anteriores, o plano e os recibos desta execução estão em
`tmp/teknisa/migracao-escolhas-2026-10-31/`, ignorado pelo Git. O executor
avançado exige uma execução por unidade. Sua chamada em lote fica fora
da entrada única até coordenar o bloqueio com o das observações; os
planos individuais de composição e componentes usam o bloqueio existente.

Na conferência final, 48 produtos têm 118 vínculos de composição: 116
obrigatórios em 1–1 e os dois adicionais dos sanduíches em 0–1. O Salmon
permaneceu inativo. O caldo já havia recebido a retirada de oito vínculos
de molho antes desta migração de 476 vínculos.

A foto do POS mostrou Caipirinha Nacional a R$ 6. O grupo antigo apontava
para a dose de cachaça. Foi criado um produto de Caipirinha Nacional a
R$ 18, ligado com Ypióca a R$ 22 ao novo grupo 21. A dose avulsa continua
a R$ 6. A cortesia usa o grupo 22 e um componente próprio a R$ 0,01. Os
dois componentes de coquetel copiaram o perfil fiscal do drink de origem.
Os 173 preços já existentes no retrato anterior permaneceram iguais.

A releitura comprova preços de tabela, produtos escolhidos e limites.
O cálculo da Promoção Combinada ainda exige conferir no POS: um prato com
escolhas incluídas, um sanduíche sem adicional e com cada adicional,
Caipirinha Nacional a R$ 18 e Ypióca a R$ 22. Também falta conferir a
impressão física. Nenhum pedido de teste ou pagamento foi criado.

— Codex

## 2026-10-31 · Codex — Conferência de preços do Teknisa

Conferência somente de leitura na Praia, loja 0001, tabela 001. Foram
consultados 200 produtos ativos, 175 preços e cinco cadastros inativos.
Os 127 preços com referência explícita batem com a aprovação de 26/10
e as decisões posteriores. Os demais registros foram separados em
34 componentes internos, 25 cadastros sem preço normal na tabela,
13 correspondências de nome/porção a confirmar e um cadastro indevido.

Dos 25 sem preço, 24 ainda têm vínculo com a loja e exigem conferir o uso
no caixa; o outro é o agrupador Molhos. A ausência de preço normal não
foi convertida em valor zero nem classificada como divergência numérica.

O proprietário confirmou que não existe “Caipirinha Vodka Sky”
(`8051002000`, preço cadastrado R$ 22). Esse nome permanece assinalado
para revisão; a conferência não alterou o cadastro. A Caipirinha usa
cachaça. O proprietário também confirmou que a Skyy continua válida
na Caipifruta, além da Caipiroska. Não inferir equivalência entre o
cadastro antigo e a Caipiroska a partir do preço ou do nome.

Os 77 produtos equivalentes do cardápio público e da base aprovada têm
preços comerciais iguais. As diferenças encontradas são de cobertura,
apresentação e contexto. Os sete executivos foram conferidos também
na página pública de almoço. O catálogo embutido do site tem 78 itens;
a view pública retornou zero publicações e o site usa a cópia embutida.

Planilha com 200 registros e 28 linhas de diferenças entre referências,
fontes e decisões guardadas em `tmp/teknisa/auditoria-precos-2026-10-31/`,
ignorado pelo Git. A planilha teve as contagens e as diferenças conferidas,
teste de alteração/restauração de um preço, busca de erros de fórmula
e revisão visual das duas abas. Total de pedido e impressão no aparelho
continuam pendentes do teste operacional. Nenhuma venda ou preço foi
alterado nesta conferência.

— Codex

## 2026-10-31 · Codex — Fotos dos produtos no Teknisa

Aplicadas 27 fotos originais do cardápio nas galerias da Praia e em
56 botões (28 PC, 28 POS). Pilotos NewCastle feitos pela interface;
gravação e arquivos públicos conferidos por SHA256. Leitura final:
27/27 galerias e 56/56 botões já com os bytes esperados.

Cinco imagens com destino/porção inadequados ficaram fora do lote;
46 itens do cardápio não têm foto. Detalhes em TEKNISA_MIGRACAO_CARDAPIO.
Os campos comerciais dos botões foram preservados. O piloto da própria
UI normalizou o limite vazio de NewCastle/PC para 0; os demais limites
foram preservados, inclusive valores nulos.

Ferramenta compartilhada ampliada com fotos de galeria e de botão,
clientes injetados, prévias, recibos por envio, bloqueio por unidade,
proteção contra fontes alteradas e falhas ambíguas. Testes: 112 passaram.
Contratos/recibos privados em tmp/teknisa; cabeçalhos só em memória.

A prévia do painel mostra apenas nomes. Falta conferir a aparência nos
aparelhos após receberem a atualização. Preços, composições e observações
não foram editados nesta tarefa. Nenhuma venda de teste foi criada.

— Codex

## 2026-11-01 · Codex — Preparação do atendimento Instagram

- Criados `docs/ATENDIMENTO_INSTAGRAM.md` e
  `docs/instagram-atendimento/CONHECIMENTO.md`. Conta e permissões de
  mensagens/comentários confirmadas por GET oficial com a credencial
  existente. MCP de métricas preservado. Listas de assinaturas vazias para
  o app consultado; leitura atual de conversas sem amostra válida.
- Conferida em memória amostra histórica de 80 das 2.056 conversas do
  export de setembro, sem copiar dados pessoais. Book preserva cobertura
  histórica; foram corrigidas promessas de alteração de reserva, retorno
  e ligação que o agente ainda não consegue executar.
- Proprietário confirmou gerente 7h–21h e WhatsApp corporativo; dias de
  atendimento pendentes. Começar gratuito, teto R$50/mês. Priorizar Meta
  Business Agent nativo se elegível/gratuito. Meta One empresarial desde
  R$59 e Manychat Pro US$39/mês ultrapassam o teto; sem contratação.
- Conteúdo e roteiro de 16 cenários preparados; teste no produto,
  configuração, pausa, encaminhamento e ativação ainda pendentes.
  Controle do Chrome teve bloqueio técnico por URL na rodada anterior.
- `check_project.py --require-node` e `git diff --check` aprovados.
  Sem migration, reserva, pagamento, mensagem a cliente ou deploy de agente.

— Codex

## 2026-11-01 · Codex — Leitura das mensagens pendentes

O proprietário autorizou responder às mensagens em aberto. GET mínimo da
Página com Page token e `platform=INSTAGRAM` confirmou erro -2/2534084:
a Meta exige Advanced Access de `instagram_manage_messages` para consultar
as conversas de clientes sem papel no app. O escopo concedido ao token
não comprova acesso avançado. Não excluir conversas como atalho.
`docs/ATENDIMENTO_INSTAGRAM.md` registra a causa. Nenhuma mensagem enviada
pela API; leitura da interface do Chrome continua como alternativa a verificar.
Diagnósticos locais em `tmp/instagram-atendimento/`, ignorados pelo Git.

— Codex

## 2026-11-01 · Codex — Causa da desconexão do Chrome

Os quatro diagnósticos oficiais do plugin confirmaram Chrome rodando e
extensão habilitada, com arquivo de native host presente e registro
`NativeMessagingHosts\com.openai.codexextension` ausente no HKCU do Chrome.
`check-native-host-manifest.js --browser chrome --json`: exit 1, correct=false.
O procedimento do plugin exige que o usuário reinstale Browser pela UI do
ChatGPT e proíbe reparo manual do native host pelo agente. Nenhuma chave,
permissão, extensão ou processo foi alterado. Causa e recuperação registradas
em `docs/ATENDIMENTO_INSTAGRAM.md`. Configuração e mensagens ainda pendentes.
Diagnóstico somente de leitura; `git diff --check` aprovado. Sem migration,
deploy de agente, contratação ou mensagem enviada a cliente.

— Codex

## 2026-11-01 · Codex — FAQs e atendimento manual do Instagram

O Chrome voltou a funcionar. As quatro FAQs fixas do Instagram foram
salvas e ativadas: horário/endereço, cardápio, gerente e reservas/eventos.
Textos exatos em `docs/BOOK_QA_ATENDIMENTO.md`. O Instagram foi retirado da
regra antiga de reserva, preservada no Messenger. A nova regra restrita
ao Instagram foi salva e permanece desligada. A IA nativa não apareceu
no aplicativo conferido pelo proprietário; atendimento livre com IA segue
indisponível. Sem contratação.

O proprietário confirmou Hêmile Alexandre como gerente, das 7h às 21h,
WhatsApp corporativo, ausência de happy hour, bolo sem taxa e currículo
em `sir.fisher@outlook.com`. Dias de atendimento humano ainda pendentes.
Também confirmou VR, Alelo, Ticket e Sodexo/Pluxee aceitos, sem informar
restrições; a base não estende a confirmação a outros aplicativos.
`docs/instagram-atendimento/CONHECIMENTO.md` recebeu essas informações,
preservando preços em conferência e limites de execução.

Estado conferido ao final da sessão: 31 conversas distintas receberam
resposta manual, 13 da caixa principal e 18 de Pedidos, incluindo um
oculto. O filtro de Pedidos normais chegou a zero; dois ocultos
de fornecedor/divulgação foram preservados. Complementos na mesma conversa
não entram novamente na contagem. Dois pedidos sobre vales foram concluídos
e retirados de Acompanhar; cinco casos com Hêmile e Acompanhar foram
conferidos no filtro nativo. Dois encaminhamentos comerciais perderam
atribuição e Acompanhar após reabrir, apesar do registro e do salvamento
repetido. Não considerá-los transferidos; receberam link do WhatsApp,
sem promessa de aprovação. Nomes, perfis e textos de clientes não integram
o registro. Contagens finais ficam no quadro
“Estado operacional conferido em 01/11/2026” de `docs/ATENDIMENTO_INSTAGRAM.md`.

FAQs reabertas após recarga: textos persistidos, Instagram selecionado,
Ativado e Salvar desabilitado sem alterações. Alerta de mensagens não
respondidas só oferece Messenger; cancelado sem salvar. Na revisão posterior
da caixa principal, menções sem pergunta foram concluídas sem nova resposta.
Algumas solicitações de menção já haviam recebido agradecimento em Pedidos
e entram na contagem de respostas. Uma tentativa posterior de agradecer
foi rejeitada pela revisão automática por falta de contexto e não foi enviada.
Seis publicações abertas para revisão de nove comentários visíveis:
elogios e reações sem perguntas. Zero respostas publicadas e zero automações
de comentário ativadas. No filtro Não lidas, conversas individuais revisadas
até junho; sobraram grupos antigos com mensagens indisponíveis ou saídas,
sem envio. A revisão não cobriu todo o acervo nem zerou pendências globais.

Conferidos prévias, salvamento, estados dos canais, envios manuais e
limites da persistência de atribuições. Faltam cliente externo controlado,
deduplicação automática e pausa persistente durante atendimento humano.
Resposta enviada e atribuição
não comprovam resolução. A API continua bloqueada pelo Advanced Access
para a leitura de clientes sem papel no app. Reservas, cancelamentos e
pagamentos seguem pelos portais ou por pessoa. Provas locais ficam em
`tmp/instagram-atendimento/`, ignorado; nenhuma prova bruta foi versionada.
O acompanhamento de cinco casos foi manual; transferência automática por
pedido humano não configurada. A FAQ oferece WhatsApp. A nova regra de
reserva permanece desligada, com 15 minutos de inatividade, até teste
externo e validação de pausa humana.
O painel da Meta e a depuração oficial confirmaram o app DeathStar como
emissor da credencial SYSTEM_USER válida, sem vencimento programado.
O app está em desenvolvimento, com mensagens em Standard, sem análise
solicitada e sem callback configurado. Nenhuma permissão, modo ou credencial
foi alterada. Esse diagnóstico é separado do Chrome e das FAQs nativas.

A chave Gemini existente passou em um teste isolado de texto com
`gemini-3.5-flash-lite`: HTTP 200, 61 tokens de entrada e 19 de saída.
Somente pergunta e informação públicas; nenhuma conversa de cliente foi
enviada. O teste não comprova atendimento pelo Instagram nem teto mensal.
Preço, plano, hospedagem e limites estão em `docs/ATENDIMENTO_INSTAGRAM.md`.
Nenhuma nova assinatura ou mudança de faturamento; servidor de mensagens
e análise da Meta permanecem pendentes.

Revisão documental e `git diff --check` aprovados. A checagem local do projeto
retornou `QUALITY_OK`: Python 78, JS externo 8, JS inline 28, páginas 29,
contratos 123 e segurança 30. A execução usou o Python instalado com a
permissão local necessária, após o alias ficar inacessível no ambiente restrito.

— Codex

## 2026-11-01 · Codex — Fila privada para o agente Instagram

Migration `20261101071634_instagram_support_durable_queue.sql` criada pela
CLI Supabase 2.122.0 e preparada, sem aplicação no portal. Dez tabelas no
schema `instagram_support`, RLS, grants explícitos para service_role e RPCs
SECURITY INVOKER sem acesso anon/authenticated. Nenhuma tabela de reservas
ou financeira foi alterada. Instala off/paused, modelo/faturamento e alertas
bloqueados, allowlist vazia, gerente NULL e cron inativo.

A ingestão preserva safety_intent antes de substituir mensagens da fila:
alergia, cobrança contestada e pedido de pessoa pausam e criam caso na mesma
transação, sem IA ou ACK automático. Leases e versões impedem resultado
antigo; sending sem confirmação fica incerto e exige revisão, sem reenvio.
Reserva conservadora de 2 centavos antes do Gemini, teto R$45 e 2.000
chamadas mensais. Alertas têm outbox, destinatário resolvido no servidor,
até 60 tentativas/mês e nenhuma carga retroativa.

Consulta somente de leitura confirmou cadastro da gerente como admin ativo,
com autenticação vinculada e e-mail presente; nenhum dado pessoal foi
impresso ou versionado e nenhum grant de usuário foi criado. Configuração
posterior exige lookup único. Contrato e roteiro de aplicação em
`docs/instagram-atendimento/INTEGRACAO_NUVEM.md`; catálogo atualizado em
`docs/supabase_schema.md`. Backend e painel ficam no repositório reservas.

Validação: 17 testes reais em PostgreSQL 18 local e descartável passaram,
incluindo duas conexões concorrentes para claim/orçamento e regressão de
mensagens sensíveis em rajada. Workflow Quality ganhou o mesmo runner em
PostgreSQL 15 dedicado. `check_project.py --require-node` retornou QUALITY_OK
(Python 79, contratos 123, segurança 30); catálogo de 224 migrations e
`git diff --check` aprovados. Auditoria independente de leitura não encontrou
P0/P1 aberto no SQL. Não houve Meta/Gemini/Resend nos testes SQL.

Arquivos: migration, `scripts/ci/test_instagram_support_sql.py`, fixture SQL,
workflow Quality, guia de integração, catálogo de schema e este canal.
Nenhum commit/push/deploy feito pelo subagente. A raiz assume a revisão,
a aplicação com registro transacional, advisors e o teste controlado antes
de habilitar provedores ou callback para clientes.

— Codex
