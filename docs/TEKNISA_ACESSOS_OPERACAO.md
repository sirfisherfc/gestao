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

## Unidade antiga e preservação da Praia

Conforme a orientação do usuário, a unidade antiga Imprensa foi
bloqueada e sua loja foi inativada. Foram **duas alterações e zero
exclusões**. Os cadastros e o histórico foram preservados.

A releitura confirmou a Praia desbloqueada e como unidade padrão, com
sua única loja ativa. O recibo privado é
`output/teknisa-2026-10-26/teknisa-imprensa-limpeza-execucao2.json`.

## Conferência nos aparelhos

Os resultados acima comprovam os cadastros salvos. Antes da operação,
conferir no PC/POS:

1. Login de cada função na unidade Praia.
2. Pedido com identificação do garçom e gravação correta dos itens.
3. Autorização de gerente nas ações que a operação exigir.
4. Impressão do pedido e das observações na cozinha.

Esses testes físicos continuam pendentes. Credenciais não foram
coletadas nesta tarefa. Nomes, logins, e-mails, PINs e senhas ficam
fora desta documentação e do Git.

A revisão documental conferiu as contagens dos recibos, a ausência de
dados pessoais nos textos versionados e a integridade do diff.

As pendências fiscais e os testes do cardápio constam em
[Migração do cardápio](TEKNISA_MIGRACAO_CARDAPIO.md).
