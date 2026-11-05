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
