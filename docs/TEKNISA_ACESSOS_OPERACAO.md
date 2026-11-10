# Cadastro da equipe no Teknisa

Entrega de 27/10/2026, na unidade **0002 — SIR FISHER PRAIA**. O usuário
autorizou cadastrar oito pessoas para a operação: três gerentes e cinco
garçons. Este registro contém contagens, grupos usados e resultados das
conferências. Os recibos pessoais ficam fora dos repositórios.

## Operadores conferidos

Os oito operadores foram salvos e relidos em uma consulta independente:

| Função aprovada | Grupo de operadores | Quantidade |
| --- | --- | ---: |
| Gerente | `02 — ADM-SUPERVISOR` | 3 |
| Garçom | `04 — GARCOM` | 5 |

O lote reúne **dois operadores novos e seis existentes**, com uma
reativação entre os existentes. Os oito estão ativos e associados
somente à unidade Praia. A conferência independente encontrou os oito
esperados, sem faltantes, duplicados ou divergências.

Os recibos privados são `acessos-execucao8.json` e
`acessos-qa-independente8.json`, na pasta
`output/teknisa-acessos-2026-10-27/`, na raiz do workspace.

## Vendedores vinculados à operação

Os cinco cadastros de vendedor foram salvos: quatro existentes tiveram
nome, nome fantasia e unidade corrigidos; um novo foi vinculado ao
operador aprovado. As taxas e os marcadores dos quatro existentes
foram preservados. O novo cadastro tem taxa e comissão zero.

A conferência independente confirmou os cinco vendedores, seus
operadores e a unidade Praia, sem divergências. Nos quatro existentes,
somente os três campos previstos mudaram. O recibo privado é
`vendedores-qa-independente5.json`, na mesma pasta de acessos.
O teste no aparelho ainda precisa comprovar a identificação do garçom
ao registrar um pedido.

### Gerentes também lançam pedidos e vendas

Na conferência seguinte, o usuário confirmou que os gerentes precisam
lançar pedidos e vender com o próprio acesso. Além das permissões do
grupo de gerentes, foram conferidos os vínculos de vendedor: dois
cadastros novos foram incluídos e um existente teve nome, nome fantasia
e unidade corrigidos. O cadastro existente já apontava para o operador
gerente correto; os outros campos foram preservados.

Os três vendedores ficaram ligados aos próprios operadores e à Praia,
sem limitar a um caixa específico. Taxa diária e comissão foram
conferidas em zero. Após recarregar a página, os três registros foram
relidos sem divergências. A equipe solicitada agora tem oito vínculos
de vendedor: cinco de garçons e três de gerentes.

Recibos privados: `vendas-gerentes-execucao3.json` e
`vendas-gerentes-qa3.json`, na pasta de acessos. Nenhuma venda ou
transação de pagamento foi executada durante a conferência.

### Padronização dos dados dos operadores

O proprietário definiu nomes completos e nomes de acesso pelo primeiro
nome, em minúsculas e sem acentos. Os nomes completos dos oito operadores
já conferiam. Dois nomes de acesso foram corrigidos e salvos; os outros
seis já seguiam o padrão.

O proprietário forneceu os e-mails pessoais reais. Os oito endereços
foram preenchidos em fichas separadas e ficaram aguardando salvamento
manual. Ao alterar o e-mail, o Teknisa pede confirmação para gerar e
enviar uma senha provisória de validação. Essa confirmação foi cancelada
durante a preparação; nenhum novo e-mail foi salvo pelo agente.

Oito rascunhos foram conferidos pelo código, nome completo e nome de
acesso, com o campo de e-mail preenchido a partir da lista recebida.
Os recibos, a lista pessoal e as capturas ficam somente na pasta privada
de acessos. E-mails pessoais e dados de nascimento não foram incluídos
na documentação versionada.

### Troca de senha pelo proprietário

As senhas das maquininhas são alteradas em **Controle de Acesso →
Operador → Ações → Alterar Senha PDV**. A tela de edição dos dados do
operador não apresenta os campos dessa troca. O proprietário preenche
Nova Senha e Confirmar Senha e clica em Salvar diretamente no sistema.
As oito fichas de dados ficaram abertas, uma aba por pessoa, identificadas
pelo nome. O proprietário deve salvar os dados e concluir a validação do
e-mail; em seguida, usar a ação de senha PDV. Nenhuma senha foi lida,
preenchida ou alterada pelo agente. A confirmação dos e-mails e a troca
das senhas continuam pendentes da conclusão pelo proprietário.

## Unidade antiga e preservação da Praia

Conforme a orientação do usuário, a unidade antiga Imprensa foi
bloqueada e sua loja foi inativada. Foram **duas alterações e zero
exclusões**. Os cadastros e o histórico foram preservados.

A releitura confirmou a Praia desbloqueada e como unidade padrão, com
sua única loja ativa. O recibo privado é
`output/teknisa-2026-10-26/teknisa-imprensa-limpeza-execucao2.json`.

## Permissões operacionais do PDV

Em 27/10/2026, o usuário definiu que garçons podem lançar pedidos,
receber pagamentos e abrir e fechar o próprio caixa. Cancelamentos de
consumo dependem de gerente. O usuário confirmou os três gerentes como
autorizadores do grupo de garçons.

O ajuste foi feito em **Controle de Acesso ao Caixa**, em Parametrização
de Vendas. A atribuição anterior dos operadores aos grupos já estava
salva; esta etapa conferiu e restringiu as ações do PDV.
O controle do painel administrativo requer uma revisão própria. A
conferência desta etapa cobre as ações do PDV e não comprova restrições
por função no painel administrativo. O estado observado ficou no recibo
privado, para continuidade.

| Ação | Garçom | Gerente |
| --- | --- | --- |
| Operar pedidos, observações e parcial da conta | Liberada | Liberada |
| Receber pagamentos | Liberada | Liberada |
| Abrir e fechar o próprio caixa | Liberada, conforme decisão do usuário | Liberada |
| Cancelar cupom, item ou mesa/comanda; devolver item | Exige código e senha de gerente | Liberada |
| Desconto, acréscimo e retirada de cobranças | Exige código e senha de gerente | Liberada |
| Funções administrativas, incluindo sangria e administração TEF | Bloqueadas no grupo de garçons | Permissões anteriores preservadas |

O grupo de gerentes ficou como único grupo autorizador dos garçons.
Foram alteradas 23 permissões e incluído um vínculo de supervisão. A
releitura após recarregar a página confirmou os 47 campos de permissões
do grupo de garçons e o vínculo, sem divergências. Os 47 campos do grupo
de gerentes foram preservados. Recibos e capturas ficam na pasta privada
de acessos, incluindo `permissoes-caixa-execucao.json` e
`permissoes-caixa-qa47.json`.

A função **Desistência do item (Balcão)** foi mantida liberada. A tela de
permissões não descreve em que momento o POS usa essa função nem se ela
também se aplica ao carrinho de mesas. A retirada de rascunhos antes do
envio e o bloqueio após a transmissão ainda precisam ser testados no
aparelho. O cadastro salvo não comprova esse comportamento por etapa.

Referências consultadas: [guia de implantação Odhen](https://www.teknisa.com/odhen-guia-express-middle),
que inclui o Controle de Acesso do Caixa entre os cadastros de venda, e
[manual Odhen POS](https://universidade.teknisa.com/wp-content/uploads/2025/04/14_ODHEN_POS_V1.pdf),
que apresenta o carrinho, a transmissão de pedidos e as funções de mesa.

## Conferência nos aparelhos

### Avisos relatados no POS em 27/10/2026

As duas fotos enviadas pelo proprietário mostram ocorrências distintas:

- Na seleção de filial: notas pendentes/rejeitadas desde **06/08/2026**,
  com orientação para transmitir pela retaguarda. A foto não identifica
  a filial, os documentos, o tipo fiscal nem o motivo das rejeições.
  Conferir esses dados e o estado atual antes de qualquer retransmissão.
  Não houve consulta da fila nem transmissão nesta investigação.
- Ao solicitar a parcial: aviso de que não há impressora parametrizada
  para essa função. O proprietário confirmou que a parcial deve sair
  **na própria maquininha**. Conferir o caixa associado ao aparelho e
  os parâmetros da impressora interna usados pela parcial. A rota de
  produtos para a ELGIN não comprova essa configuração; as permissões
  salvas anteriormente liberam a função, mas não configuram a impressora.

O [guia oficial de implantação](https://www.teknisa.com/odhen-guia-express-middle)
lista Cadastro de Caixa, Configuração do Terminal do Caixa e parâmetros
de venda. Também descreve a consulta de transmissão de NFC-e em Vendas
→ Operacional → Transmissão de NFC-e (Consumidor Final). Esse caminho é
referência para a investigação; é necessário confirmar o documento e
a rotina efetivamente usados pela filial antes de executar uma ação.

A conexão de navegador disponível nesta sessão não encontrou navegadores
conectados. Portanto, nenhum parâmetro do POS foi consultado ou alterado
ao vivo. Permanecem pendentes a conferência da fila fiscal, a configuração
da parcial na impressora interna e o teste físico de impressão. As fotos
não permitem atribuir esses avisos a uma falha do Chrome.

Os resultados acima comprovam os cadastros salvos. Antes da operação,
conferir no PC/POS:

1. Login de cada função na unidade Praia.
2. Pedido com identificação do garçom e gravação correta dos itens.
3. Retirada de um item ainda no carrinho e tentativa de cancelamento
   após enviar, exigindo a autorização de um dos gerentes.
4. Impressão do pedido e das observações na cozinha.
5. Recebimento e abertura/fechamento do próprio caixa pelo garçom.

Esses testes físicos continuam pendentes. Credenciais não foram
coletadas nesta tarefa. Nomes, logins, e-mails, PINs e senhas ficam
fora desta documentação e do Git.

A revisão documental conferiu as contagens dos recibos, a ausência de
dados pessoais nos textos versionados e a integridade do diff.

As pendências fiscais e os testes do cardápio constam em
[Migração do cardápio](TEKNISA_MIGRACAO_CARDAPIO.md).

## Ajustes de 30/10/2026

O proprietário pediu os ajustes abaixo; todos foram relidos depois da
gravação. Recibo privado: `output/teknisa-ajustes-2026-10-30/recibo.json`.

- **Senha por e-mail de dois operadores (uma gerente e um garçom).** O
  Teknisa só envia a senha provisória quando o e-mail do operador muda;
  regravar o mesmo endereço não dispara o envio. Como os dois usam Gmail,
  que ignora pontos no endereço, foi gravada a variante com ou sem ponto,
  que chega à mesma caixa. As duas chamadas de validação retornaram OK.
  Nenhuma senha foi lida ou digitada pelo agente.
- **Login do caixa geral.** Reaproveitado o operador de um ex-garçom:
  nome "Caixa Geral" e acesso genérico, no grupo `04 — GARCOM`, que abre e
  fecha caixa e recebe, com cancelamentos dependentes de gerente. O grupo
  `03 — OPERADOR DE CAIXA` foi descartado porque libera cancelamentos,
  descontos e sangria sem gerente. A senha do PDV fica com o proprietário
  (Operador → Ações → Alterar Senha PDV).
- **Desvincular o garçom de logins reaproveitados.** Na ficha do operador o
  vendedor fica bloqueado. O vínculo sai pelo Cadastro de Vendedor,
  limpando o campo Operador. Feito nos vendedores de dois ex-funcionários,
  ligados aos logins genéricos Extra e Caixa Geral. Os cadastros e o
  histórico de vendas foram preservados; o nome do vendedor continua o da
  pessoa, para a apuração por período.
- **Liberar mesa sem gerente.** Em Controle de Acesso ao Caixa, grupo
  `04 — GARCOM`, a permissão Liberar Mesa passou de "código e senha do
  supervisor" para "Permite Acesso". As demais 46 permissões ficaram iguais.

Falta testar no POS: reabrir uma mesa com parcial pedida e lançar um
item com login de garçom; entrar com o login do caixa geral e abrir o caixa.

### Complemento de 30/10/2026 (tarde)

- **Fonte da cozinha:** por orientação do suporte Teknisa, o parâmetro
  "Utiliza fonte expandida no cupom de produção" (Cadastro de Caixa →
  Parâmetros → Frente Caixa (4), campo `IDUTILFONTEXP`) foi ativado nos
  POS 001, 002 e 003; o CAIXA 001 já estava ativo e o TAA 001 ficou como
  estava. Vale só para cupom de produção em Bematech/Elgin/Epson e exige
  reabrir o app. Contrato: `vnd42300_cadcaixa_frentedecaixa4` e `/save`.
- **Novo operador com acesso total:** cadastrado pelo proprietário (que
  definiu a senha), vinculado à Praia, ao grupo `01 — SÓCIO` e ao perfil
  "Administrador de sistema", sem validade, igual ao login do proprietário.

### Painel web por perfil (30/10, noite)

- **Estado encontrado:** o Controle de Acesso do painel está **desativado**
  (título "Perfil de Acesso (Controle de Acesso Desativado)"). Só dois
  operadores têm perfil ("Administrador de sistema": proprietário e o
  operador novo). Com o controle desativado, perfil não restringe nada, e
  a tela "Perfil de Acesso - Menu" fica somente leitura (`isEditable=false`).
- **Feito:** criado o perfil "Gerente - Reposicao" (ID 12, não
  administrador) e vinculados os três operadores do grupo
  `02 — ADM - SUPERVISOR`, sem validade.
- **Relatório indicado para reposição:** Vendas » Relatórios » Relatórios de
  Produtos » "Produtos Vendidos (Venda Normal + Promoções)". Mostra código,
  grupo, produto, quantidade, normal/promocional, notas e preço médio
  unitário, sem total de faturamento. Filtro de loja: a cozinha e o bar
  ficam em lojas diferentes.
- **Concluído (30/10, noite), com autorização do proprietário:**
  1. O operador do sócio do grupo 01 entrou no perfil "Administrador de
     sistema" (sem validade). O operador SUPORTE do fornecedor ficou de fora.
  2. O perfil "Administrador de sistema" recebeu a marca **Administrador**
     (antes desmarcada; sem ela o Teknisa recusa ativar o controle).
  3. **Controle de Acesso ativado** e "Habilitar Parametrização do Controle
     de Acesso por Perfil" ligada (sem ela a árvore fica só leitura).
  4. No perfil 12, regras gravadas: "Produtos Vendidos (Venda Normal +
     Promoções)" = visível (`A`) e "Painel de Controle" = oculto (`I`).
- **Como funciona:** só itens finais (telas) recebem regra; pastas aparecem
  quando algum item de dentro está visível. Sem regra, o item fica oculto
  para perfil não administrador (olho cinza = oculto, azul = visível).
  Operador sem perfil, como garçons e caixa, não tem tela no painel. PDV e
  caixa usam outra permissão (Controle de Acesso ao Caixa) e não mudam.
- **Pendente:** teste real com login de um gerente. Para desfazer: Perfil de
  Acesso → Ações → Desativar Controle de Acesso.
- **Contratos:** `backend_acl/opergrupop` (grupo do operador),
  `partnerAccessProfile` (perfis por parceiro), `acl_zhu_acl_element_rules/save`
  com `{UNIQUE_ID, TYPE, RULE: "A"|"I", RULE_ID, GROUP_ID, ...}`. Clicar no
  olho sem item selecionado envia a regra sem elemento e não grava nada útil.

## Grupo Garçom Sênior (03/11/2026)

O proprietário pediu um perfil intermediário para um garçom, em vez de
colocá-lo no grupo de gerentes. Esse grupo também autoriza os garçons e
libera sangria e TEF. Foi criado o grupo `05 — GARCOM SENIOR`, em Grupo de
Operadores. Em **Controle de Acesso do Caixa** (Parametrização → Vendas →
Parâmetros de Gestão de Vendas), o grupo recebeu as 47 permissões do grupo
`04 — GARCOM`, com cinco diferenças:

| Permissão | Garçom (04) | Garçom Sênior (05) |
| --- | --- | --- |
| Retirar Taxa de Serviço | Código e senha do supervisor | Permite Acesso |
| Cupom com Desconto | Código e senha do supervisor | Permite Acesso |
| Cancela Último Item | Código e senha do supervisor | Permite Acesso |
| Cancela Item Genérico | Código e senha do supervisor | Permite Acesso |
| Suprimento | Não permite acesso | Permite Acesso (incluído no mesmo dia) |

Cancelamento de cupom e de mesa/comanda, devolução, troca, acréscimo,
couvert e consumação continuam dependendo de gerente. Sangria, TEF,
leituras e gaveta seguem bloqueados. O suprimento foi liberado para
lançar no caixa entradas avulsas, como a venda de óleo usado. O grupo
`02 — ADM - SUPERVISOR` aparece como grupo de supervisores do 05.

O operador escolhido foi incluído no grupo 05 e retirado do 04, porque
o vínculo aos dois grupos ficava simultâneo. O cadastro de vendedor e o
histórico foram preservados. Depois de recarregar a página, a releitura
confirmou as 47 permissões sem divergência e o operador somente no grupo 05.

Falta testar no POS: com o login dele, retirar os 10%, dar desconto e
cancelar um item já enviado, sem pedir senha de gerente. Cancelar a mesa
inteira deve continuar pedindo a senha. Se o aparelho já estiver logado,
pode ser necessário sair e entrar de novo. Para desfazer, devolva o
operador ao grupo 04 e retire-o do 05.

## Multiplicar prato com composição (05/11/2026)

O proprietário perguntou se o garçom pode lançar um prato com composição,
como o PF, e multiplicá-lo por 2 ou 3, sem repetir as escolhas. Leitura
no painel, sem gravação:

- Em **Controle de Acesso do Caixa**, a permissão **Multiplicador Produto**
  está em "Permite Acesso" nos grupos `04 — GARCOM` e `02 — ADM - SUPERVISOR`.
  **Produto Combinado** também. O grupo 05 foi copiado do 04 sem diferença
  nessas duas.
- Em Cadastro de Caixa (POS 001) e Cadastro de Loja, Frente de Caixa,
  Comanda e Gestão de Vendas não têm opção de repetir um item montado.
  O único campo de quantidade próximo é "Quantidade máxima permitida de
  venda por produto por vez", um limitador.
- O painel não comprova se o multiplicador do POS repete as escolhas de um
  produto de Promoção Combinada. O manual do POS respondeu 502 nessa data.
  Falta testar num aparelho, numa mesa de teste, e conferir o total e a
  impressão na cozinha. Sem esse teste, perguntar ao suporte Teknisa.

## Gerente incluído no perfil de reposição (05/11/2026)

O proprietário pediu para liberar o portal a um gerente, somente com a
reposição. Em **Perfil de Acesso → Gerente - Reposicao → Operadores →
Adicionar**, o operador foi incluído na filial Praia. A tela pede a filial
depois de escolher o operador. Depois de recarregar a página, ele continuou
na lista. No perfil, Painel de Controle, Estoque, Financeiro e Parametrização
seguem ocultos, e Vendas segue visível.

Contrato: `backend_acl/index.php/findPerfAcessParcOperador` lê os vínculos,
com filtro `NRPERFILACESSO` e `IDATIVO`. A inclusão respondeu `[]` no `save`.

Divergência encontrada: antes da inclusão, a consulta devolveu lista vazia
no perfil 12, onde este documento registra três gerentes em 30/10. A aba
Operadores do perfil Administrador também apareceu vazia. A causa não foi
apurada, e os outros dois gerentes não foram alterados.

Falta testar: entrar com o login desse gerente e abrir o relatório Produtos
Vendidos.

## Relatório de fechamento de caixa para o gerente (10/11/2026)

O proprietário pediu para o gerente acessar o relatório de fechamento de
caixa. Em **Perfil de Acesso - Menu**, o item **Aplicação → Vendas →
Relatórios → Estatísticas de Caixa → Fechamento de Caixa** passou a visível
no perfil "Gerente - Reposicao". A gravação respondeu 200 em
`acl_zhu_acl_element_rules/save`. Depois de recarregar a página, o olho
continuou azul. O "Fechamento de Caixa" de **Vendas → Operacional** é a tela
que fecha o caixa e continua oculto. O relatório mostra valores por forma de
pagamento; até então o perfil não exibia faturamento.

A aba Operadores do perfil mostra um único operador, o gerente incluído em
05/11. Ele precisa sair e entrar de novo no portal para ver o item.

Pedido seguinte, não concluído: incluir a Nayane no mesmo perfil. Em
**Operadores → Adicionar**, `backend_acl/index.php/operator` (filtros
`ACCESS_PROFILE <> 12`, `IDATIVO = S`, `SHOW_FULL_OPERATOR`) respondeu
`{"dataset":{"operator":[]}}`. A tela **Operador**, com e sem filtro de nome,
também voltou vazia. Na primeira abertura dela, com "Organização
Relacionada" SIR FISHER, a lista ficou carregando sem terminar, enquanto
`findOrganization` devolveu outra organização. Na nova tentativa do mesmo
dia, depois de recarregar, a consulta só com `SHOW_FULL_OPERATOR` e
`IDATIVO` voltou vazia tanto com `S` quanto com `N`. A causa não foi apurada.
Em **Cadastro de Vendedor (Garçom)** (Parametrização → Vendas →
Mesa/Comanda), ela é o vendedor `0502`. O gerente do perfil é o vendedor
`0501`, com operador `000000000501`; pelo mesmo padrão, o operador dela
seria `000000000502`. As capturas de 27/10 em `output/teknisa-acessos-2026-10-27/`
confirmam esse operador. Os recibos não guardaram o formato da gravação
de 05/11, por isso a inclusão não foi enviada fora da tela. O cabeçalho da
sessão mostra "Sem perfil selecionado", e a lista de perfis em **Trocar
Perfil/Unidade** também voltou vazia. Isso sugere que o login do
proprietário perdeu o vínculo com "Administrador de sistema", cuja aba
Operadores já aparecia vazia em 05/11. Não foi alterado.
Para continuar, confirmar o código de operador da Nayane e o nome dela no
cadastro, ou perguntar ao suporte por que a lista de operadores volta vazia.

## Reimpressão do fechamento de caixa (07/11/2026)

O proprietário perguntou como liberar a reimpressão do fechamento quando a
impressora falha. Consulta aos recibos e à documentação, sem gravação.

- **Caminho informado pelo suporte:** no app, digitar o código do operador,
  deixar a senha em branco e tocar em **Funções Gerais**. A opção de
  reimprimir o fechamento fica nessa tela e, segundo o suporte, exige
  acesso de supervisor.
- **O que a função faz:** pelo resumo da busca, a nota de versão do Teknisa
  Retail de dez/2025 (FOS 6.59.005) descreve o botão **Rel. Último
  Fechamento de Caixa**, em Funções Gerais. O botão reimprime os relatórios
  do último encerramento, depende da permissão de fechamento de caixa e só
  funciona enquanto o caixa não é reaberto para um novo turno. O PDF
  respondeu 502, então o texto completo e a versão do Odhen POS não foram
  conferidos.
- **Permissões:** o Controle de Acesso do Caixa não tem um item próprio de
  reimpressão do fechamento. No recibo de 27/10, o grupo
  `02 — ADM - SUPERVISOR` tem 46 das 47 permissões em "Permite Acesso",
  incluindo Fechar Caixa, Leitura X e Relatórios Fiscais. A exceção é
  Alteração Garçom por Item. As alterações registradas depois disso
  mexeram apenas nos grupos 04 e 05. O grupo 04 tem Fechar Caixa liberado e
  Leitura X e Relatórios Fiscais bloqueados.

Nada foi alterado. Falta testar no próximo fechamento: com o login de um
gerente, reimprimir antes de abrir o caixa do turno seguinte. Se a opção não
aparecer ou recusar o acesso, conferir a versão do app e perguntar ao suporte
qual permissão controla o botão.

**Teste no aparelho (07/11, noite).** Fotos enviadas pelo proprietário:

- Com o login de uma gerente do grupo 02, no POS 002, Funções Gerais mostrou
  oito botões: Reimpressão - Fiscal, Reimpressão - Pedido, Bloquear e
  Desbloquear Produto, Impressão da Leitura X, Sangria de Caixa, Painel
  Vendas Diárias e Relatório de Vendas. O botão Rel. Último Fechamento de
  Caixa não apareceu. A gerente informou que só conseguiu reimprimir o cupom
  da última venda.
- Em outra foto, sem identificação do login, o app respondeu "Operador não
  tem permissão para executar esta função" sem pedir senha. Esse é o
  comportamento esperado de uma função marcada como "Não permite acesso".
  Pedir a senha do supervisor exige a opção "mediante código e senha".

Portanto, a permissão do gerente não resolve a falta do botão. Pendências:
saber se a foto foi tirada com o caixa fechado, como orientou o suporte,
perguntar ao suporte em qual versão ou tela o botão aparece neste POS e
conferir se o relatório do fechamento pode ser impresso pelo painel web.

**Alternativa pelo painel web.** Em **Vendas » Relatórios » Estatísticas de
Caixa » Fechamento de Caixa**, os tipos disponíveis são Controle, Por Loja,
Por Caixa e Total do Dia. Os filtros são unidade, loja, caixa, período e
Listar Produtos. Em 07/11, o tipo Por Caixa gerou o PDF
`fechCaixaPorCaixa.pdf` numa aba nova, só com leitura. O conteúdo não foi
lido pelo agente, porque o visualizador de PDF do Chrome bloqueia a captura.
Falta o proprietário comparar esse PDF com o cupom de fechamento do POS.

Comparação de 07/11, pelo mesmo relatório gerado em HTML (trocar
`__format=pdf` por `__format=html` no endereço do relatório): o relatório
soma **todos os turnos do dia** em cada caixa, enquanto o cupom do POS
cobre um turno, da abertura ao fechamento. Os cartões do turno coincidiram
centavo a centavo. As diferenças vieram de outro movimento do mesmo caixa
no dia: +80,74 no CAIXA 001 e +1.210,98 no POS 002. No POS 003, o débito e o
Pix do resumo da Stone bateram com o relatório. O crédito da Stone ficou
162,80 acima, mesmo valor de um Master Crédito lançado no CAIXA 001. Isso
indica um cartão passado na máquina do POS 003 e registrado em outro caixa.
O relatório por caixa substitui o cupom quando o caixa teve só um turno no
dia. Ele não traz venda bruta, descontos e cancelamentos.

**Filtro por turno (08/11).** Em **Vendas » Relatórios » Relatórios de Caixa
» Resumo do Caixa** há sete tipos. Dois deles são o Comparativo Fechamento
Caixa (RFC) e o Resumo da Movimentação do Caixa (RMC). Há também um campo
**Abertura**, mas o seletor não abriu com loja, caixa e data preenchidos. Sem
abertura escolhida, o RFC envia `TDTABERTUR=T` e soma o dia. Os valores
digitados à mão em `DTABERTUR` foram ignorados. O RFC traz venda bruta,
cancelamento, desconto e acréscimo. No CAIXA 001, a venda bruta ficou 80,74
acima do cupom do turno das 14:11, a mesma diferença do relatório por caixa.
Os HTML do RFC e do RMC dão erro de sessão no visualizador BIRT, enquanto o
PDF responde no mesmo endereço. Falta perguntar ao suporte como habilitar a
escolha da abertura.

**Fechamento por operador e turno (08/11).** O tipo **Comparativo Fechamento
Caixa (Operador)**, no mesmo Resumo do Caixa, separa cada abertura: operador,
horário de abertura e de fechamento, valores do sistema, sangria e diferença
por forma de pagamento. Para listar todos os caixas, deixe o campo Caixa vazio.
Em 07/11, o relatório reproduziu o cupom da gerente do grupo 02 no CAIXA 001
(14:11–23:23, líquido 919,55 e sangria 945,10). Os 80,74 de diferença
pertenciam a outro turno, 08:37–14:06. O relatório também mostrou três
aberturas sem venda depois das 23h, no POS 001, POS 002 e POS 003, ainda sem
fechamento.

**Impressão do fechamento (08/11, só leitura).** Em Cadastro de Caixa →
Parâmetros, os POS 001, 002 e 003 têm a mesma configuração:
- Periféricos → Impressora Não Fiscal (NFCe/SAT): `00002 POS`, modelo 40, USB,
  ou seja, a impressora interna da maquininha.
- Fechamento do Caixa: confirmação antes do Recibo de Sangria e do Relatório
  de Produtos, Relatório de Fechamento Total do Dia ligado, Leitura X
  desligada e fechamento cego desligado.

O CAIXA 001 usa a impressora `00001 COZINHA`, modelo 18, USB. Os pedidos saem
pelas impressoras de produção, então não comprovam o funcionamento da
impressora interna dos POS. Nenhum parâmetro foi alterado.

**Comparação de 07/11 por turno**, feita com o relatório por operador, as
fotos dos cupons e os resumos da Stone:
- CAIXA 001, turno de 14:11 às 23:23: líquido e sangria iguais ao cupom. A
  sobra aparece como 25,55 no relatório e 5,55 no cupom; a diferença é o
  suprimento de 20,00.
- POS 002, turno das 16:34: 1.399,40, igual ao cupom. A Stone desse período
  ficou 58,75 acima. Explicado em 08/11, venda a venda, com a Manutenção de
  Venda do Teknisa e o CSV de vendas do portal Stone. A maquininha do POS 002
  (série 4AK12X31D) recebeu 330,20 de duas mesas fechadas no CAIXA 001: 238,50
  da mesa de 333,30 das 19:28 e 91,70 da mesa das 20:07. Seis vendas do POS 002,
  somando 271,45, foram pagas em outra maquininha (série 4AJ165H2I). A
  diferença 330,20 − 271,45 = 58,75. Não falta dinheiro. O Pix e o débito de
  28,38 das 19:16 e 19:17 são uma conta dividida, não uma cobrança dupla.
- POS 003: débito e Pix iguais aos da Stone. O crédito da Stone ficou 162,80
  acima, mesmo valor do Master Crédito lançado no CAIXA 001.
- O proprietário autorizou desligar as duas confirmações de impressão do
  fechamento nos POS 001, 002 e 003.

**Confirmações de impressão desligadas (08/11).** Em Cadastro de Caixa →
Parâmetros → Fechamento do Caixa, nos POS 001, 002 e 003, os campos "Exibe
mensagem de confirmação da emissão do Recibo de Sangria" e "... de Relatório
de Produtos" passaram de Sim para Não. Cada gravação respondeu 200
(`vnd42300_cadcaixa_fechcaixa/save`). Após recarregar a página, a releitura
confirmou os seis campos em Não. CAIXA 001 e TAA 001 continuam com Sim. Os
demais parâmetros ficaram iguais.
- Falta testar no próximo fechamento de cada POS se o recibo de sangria e o
  relatório de produtos saem sem pergunta. Se a impressão parar de sair, volte
  os dois campos para Sim e consulte o suporte. A mudança pode exigir reabrir
  o app no aparelho.

**Primeiro fechamento depois da mudança (08/11, 17:44).** Um POS mostrou
"Ocorreu um erro ao imprimir. PRINTER INIT ERROR" em Funções Gerais ao fechar
o caixa, com bobina. Na primeira tentativa o app reiniciou sozinho e, segundo
a equipe, as contas sumiram da tela. A mensagem indica que a impressora interna
não iniciou. A relação com a mudança da madrugada não foi comprovada. O
proprietário preferiu testar antes de reverter: reiniciar a maquininha e
imprimir a Leitura X. Se a Leitura X imprimir e o fechamento falhar, voltar as
duas confirmações para Sim. Se nada imprimir, é o aparelho e cabe ao suporte.
Falta conferir pelo relatório por operador se o turno chegou a fechar.
Antes disso, às 15:58 do mesmo dia, o CAIXA 004 (Stone série 4AK12X31D)
fechou o turno aberto às 12:07 e imprimiu o fechamento e o recibo de sangria
sem pergunta. Líquido 1.446,34 = formas de pagamento = sangria, sobra 0. A
Stone (12:00–15:58) mostrou 1.535,98: débito e crédito iguais; o Pix ficou
89,64 acima (158,04 contra 68,40), indício de Pix lançado em outro caixa.
Logo, a mudança da madrugada não impede a impressão no fechamento.
