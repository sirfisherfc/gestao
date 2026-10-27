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
