# Perfil dos acessos por QR para campanhas

Consulta em 03/11/2026, por volta de 19h21, America/Fortaleza. GA4
`353205396`, acesso somente de leitura.

## Resultado

Conseguimos descrever o comportamento dos acessos identificados como QR.
Ainda falta evidência para definir o perfil demográfico e o valor comercial
dos clientes que usam esses códigos. O Analytics tem públicos de reserva;
a consulta não encontrou um público específico de visitantes por QR.

## Cobertura da consulta

A busca inicial começou na criação da propriedade, em 10/02/2023. Os
primeiros registros QR retornados foram de agosto de 2026. A releitura
usou **01/08/2026 a 03/11/2026**, com o último dia ainda parcial. Essa janela
retornou dados sem amostragem e sem indicação de truncamento.

O filtro reúne os hosts públicos `www.sirfisher.com.br`, `sirfisher.com.br`
e `reservas.sirfisher.com.br`, e procura os termos `qr` ou `qrcode` na
origem, mídia ou campanha da sessão. As linhas encontradas têm origem/mídia
`qr_code / offline`, com campanhas `cardapio_restaurante` e `cardapio_mesa`.

A cobertura depende da identificação no link e do registro pelo Analytics.
Códigos sem essa marcação, bloqueadores e acessos não registrados ficam fora.
Um link QR também pode ser encaminhado. A base não comprova o total de
leituras físicas nem a presença ou compra no restaurante.

## Comportamento observado

| Medida | Resultado |
| --- | ---: |
| Sessões | 1.494 |
| Usuários contabilizados pelo GA4 (`totalUsers`) | 988 |
| Sessões engajadas | 1.012 |
| Taxa de engajamento | 67,7% |
| Visualizações de página | 2.814 |
| Sessões em celular | 1.490, cerca de 99,7% |
| Sessões com idioma português no navegador/aparelho | 1.379, cerca de 92,3% |
| Sessões com clique no cardápio (`click_menu`) | 927 |
| Sessões com abertura do cardápio próprio (`cardapio_aberto`) | 828 |
| Sessões com abertura de detalhe de item | 306 |
| Sessões com clique de reserva | 7 |
| Sessões com `reservation_confirmed` registrado | 1 |

Os 988 usuários são identificações contabilizadas pelo Analytics. Uma
pessoa pode usar mais de um aparelho ou perder seu identificador. Esse
número não equivale a 988 clientes comprovados ou contatos disponíveis.
Sessões e usuários de linhas, meses e hosts podem se sobrepor; o total
acima vem da consulta sem dimensões. Não somar as linhas para deduplicar.

As ações mostram uso frequente para consultar o cardápio. Elas ajudam a
preparar anúncios e páginas para celular e português. Não medem os pratos
mais vendidos, gasto por pessoa ou margem. Os 16.208 eventos de categoria
vista podem se repetir durante a rolagem. O cardápio próprio começou em
22/09, portanto a cobertura desses eventos mudou durante a janela.

A análise anterior de setembro/outubro usava somente `www` e a origem/mídia
exata. Seus números permanecem com aquele recorte no
[relatório de público e mídia](SEMRUSH_PERFIL_PUBLICO_MIDIA_2026-11-02.md).
Os valores desta releitura incluem também a navegação no portal de reservas.

## Dados demográficos

Google Signals está habilitado e com consentimento da propriedade confirmado
pela Admin API. Isso depende também da elegibilidade e das escolhas de cada
visitante. Os relatórios demográficos têm cobertura parcial e limites de
privacidade, conforme a
[documentação Google](https://support.google.com/analytics/answer/9445345)
e as [regras de limite de dados](https://support.google.com/analytics/answer/9383630).

Na consulta de **toda a propriedade**, de 02/11 a 03/11, começaram a aparecer
linhas de idade e gênero. Idade retornou 251 usuários como `unknown`, 12
em 18–24 e 12 em 25–34; gênero retornou 247 `unknown`, 24 `female` e 20
`male`. Interesses retornaram zero linhas. Os três relatórios indicam
`subject_to_thresholding=true`. Linhas ausentes não representam valor zero.

Essas consultas cobrem a propriedade inteira e não identificam o perfil do
QR. A verificação oficial de compatibilidade recusou idade, gênero e
interesses combinados com o filtro QR usado nesta auditoria, mesmo com
`activeUsers`. Não trocar esse recorte por outro e apresentar o resultado
como se fosse o mesmo público. A cobertura atual não sustenta direcionar
as campanhas por uma suposta idade ou gênero predominante do QR.

Renda, profissão e residência não foram demonstradas. Aparelhos iOS e
localização aproximada de rede não comprovam poder de compra ou turismo.

## O que está preparado para anúncios

A Admin API confirmou quatro públicos: os padrões `All Users` e `Purchasers`,
e os personalizados **Interesse em reservar | 30 dias** e
**Reserva concluída | 30 dias**. A existência do público padrão de compras
não comprova compradores ou vendas medidos.

Os dois públicos personalizados estão habilitados para personalização.
Não há público chamado ou filtrado especificamente por QR no inventário
relido. Esta consulta não confirmou tamanho elegível, aplicação em grupos
de anúncios ou campanhas em veiculação. O vínculo GA4/Ads já existe; usar
uma audiência em campanha exige uma configuração própria.

O próximo uso possível é testar o retorno de visitantes QR que tenham
consentimento e sejam elegíveis na plataforma. O teste precisa acompanhar
reserva e comparecimento para avaliar resultado. Compras e margem com
atribuição conhecida continuam necessárias para identificar clientes de
maior valor. Não foi criada campanha nem alterado orçamento nesta tarefa.

## Validação e recibos

Consultas reais pela Data API/MCP e Admin API, com leitura dos metadados,
inventário de públicos e configuração de Signals. Quatro dimensões
personalizadas existentes: `cta_position`, `form_kind`, `reservation_reason`
e `reservation_stage`. Categoria e prato continuam sem dimensão personalizada
cadastrada para essa abertura dos relatórios.

Recibos agregados em `tmp/revisao-2026-11-03/qr-profile-read.json`,
`qr-events-read.json` e `qr-audiences-read.json`, ignorados pelo Git.
Não houve coleta de dados pessoais, alteração de consentimento, migration
ou mudança de código/publicidade. Dados recentes podem receber processamento
posterior do Analytics.
