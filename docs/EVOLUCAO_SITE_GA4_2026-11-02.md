# Evolução do site no Google Analytics

Consulta em 02/11/2026. Comparação: setembro de 2026 (30 dias) e outubro de
2026 (31 dias), os dois últimos meses completos, no fuso America/Fortaleza.

## Resultado observado

O site recebeu mais visitas em outubro e os visitantes usaram mais o cardápio
publicado no próprio domínio. Os cliques para reservar caíram. As confirmações
registradas pelo Analytics passaram de 22 para 24, com cobertura parcial.
Esses dados ainda precisam da conferência operacional para medir o crescimento
de reservas efetivas e de clientes atendidos.

## Fonte e recortes

As métricas vieram do MCP oficial `google_analytics`, propriedade
`353205396`, **Sir Fisher — Site Oficial**. A conta e o fuso foram conferidos
por consultas reais. Os relatórios principais abaixo filtram
`hostName = www.sirfisher.com.br`. O portal de reservas e os eventos enviados
pelo servidor aparecem em recortes próprios.

As configurações adicionais foram lidas e alteradas pela Admin API, com a
credencial privada existente. O MCP permaneceu somente de leitura.
O proprietário autorizou a análise e a configuração dos recursos úteis para
acompanhar reservas nesta conversa.

As respostas usadas não indicaram amostragem ou perda na linha `(other)`.
A consulta de cidades retornou as 100 primeiras de 510 linhas; seus destaques
são tratados como recortes, sem somar um total de cidades. Os totais mensais
vêm da consulta mensal e os usuários dos canais e hosts não são somados.

## Site institucional

| Indicador do site | Setembro | Outubro | Variação |
| --- | ---: | ---: | ---: |
| Usuários ativos | 1.567 | 2.255 | +43,9% |
| Sessões | 1.913 | 2.780 | +45,3% |
| Sessões por dia | 63,8 | 89,7 | +40,6% |
| Sessões engajadas | 1.433 | 2.040 | +42,4% |
| Taxa de engajamento | 74,9% | 73,4% | −1,5 ponto percentual |
| Visualizações de páginas | 2.695 | 5.226 | +93,9% |
| Visualizações por sessão | 1,41 | 1,88 | +33,4% |
| Tempo de engajamento por usuário ativo | 20,4 s | 88,0 s | Coleta e uso do cardápio mudaram |

O crescimento das sessões permanece depois do ajuste pela quantidade de dias.
O tempo médio foi calculado como `userEngagementDuration / activeUsers`.
As mudanças de navegação e coleta descritas adiante limitam a leitura desse
tempo como melhora da experiência de uma página que permaneceu igual.

Na propriedade inteira, que também mede o portal, os usuários ativos passaram
de 1.605 para 2.299 e as sessões de 1.975 para 2.922 (+47,9%). A consulta por
host retornou 167 e 259 sessões para `reservas.sirfisher.com.br`. Uma pessoa
ou sessão pode passar pelos dois hosts, portanto esses recortes se sobrepõem.
Os ambientes locais tiveram três visualizações em setembro e quatro em outubro;
eles ficam fora da tabela do site institucional.

## Páginas

| Página do site | Visualizações em setembro | Visualizações em outubro |
| --- | ---: | ---: |
| Home | 2.100 | 2.202 |
| Cardápio | 181 | 2.106 |
| Almoço executivo | 275 | 238 |
| Pôr do sol | 50 | 185 |
| Réveillon | 1 | 237 |
| Conheça | Sem linha no período | 172 |

O cardápio acrescentou 1.925 visualizações, correspondentes a 76,1% do aumento
de 2.531 visualizações do site. Os links principais voltaram a abrir o cardápio
próprio em 28/09; outubro reúne um mês completo dessa navegação interna.

A home cresceu 4,9% no total e 1,5% por dia. O executivo caiu 13,5% no total.
Réveillon e Conheça têm bases e períodos de exposição diferentes; seus totais
servem para acompanhar o início dessas jornadas.

## Origem das sessões do site

Os valores abaixo usam origem/mídia da sessão e o mesmo filtro do host `www`.

| Origem registrada | Setembro | Outubro | Variação |
| --- | ---: | ---: | ---: |
| `ig / social` | 925 | 836 | −9,6% |
| `qr_code / offline` | 399 | 717 | +79,7% |
| Direto | 184 | 470 | +155,4% |
| `google / organic` | 179 | 289 | +61,5% |
| `google_maps / organic` | 8 | 94 | +86 sessões |
| `chatgpt.com / ai-assistant` | 35 | 81 | +46 sessões |
| `chatgpt / paid` | 88 | 193 | +105 sessões |

O QR code pode ser usado por clientes que já estão na casa. Seu crescimento
ajuda a avaliar o uso do site durante a visita; a aquisição de novos clientes
precisa de outro recorte. Na propriedade inteira, em 30 e 31/10, foram
registradas 427 sessões e 221 sessões de QR, cerca de 52% nesse recorte.

Instagram continua sendo uma origem relevante, mas `ig / social` caiu em
sessões e os cliques para reservar atribuídos a essa origem passaram de 95
para 73. Busca Google e Maps cresceram. A geolocalização do GA é aproximada:
na propriedade inteira, Fortaleza passou de 938 para 1.307 usuários ativos;
São Paulo passou de 128 para 289. A cidade aproximada informa onde o acesso
foi localizado. Identificar turistas, moradores ou intenção de visita exige
informações adicionais.

O rótulo `chatgpt / paid` informa a origem recebida pelo GA. Faltam custos e
conversões publicitárias comparáveis para avaliar retorno do investimento.
Esse grupo teve 64 sessões engajadas entre 193 sessões em outubro, cerca de 33%.
As correções de atribuição de outubro também afetam os recortes por origem.

A tabela reúne origens selecionadas e soma 1.818 sessões em setembro e 2.680
em outubro. Os totais do site vêm da consulta sem dimensão de origem.
QR e Google são recortes contidos nos canais, sem adição entre os dois níveis.

## Reservas e contatos

| Ação registrada | Setembro | Outubro | Variação |
| --- | ---: | ---: | ---: |
| Cliques para reservar, site | 133 | 112 | −15,8% |
| Usuários com clique para reservar, site | 107 | 90 | −15,9% |
| Cliques no WhatsApp, site | 19 | 16 | −15,8% |
| Cliques em rota, site | 33 | 33 | Sem mudança no total |
| `reservation_confirmed`, propriedade | 22 | 24 | +2 eventos |
| Usuários com confirmação, propriedade | 20 | 22 | +2 usuários |
| `visit_realized`, propriedade | 6 | 10 | +4 eventos |

`reservation_confirmed` ocorre após a criação da reserva comum. A tag e os
identificadores disponíveis limitam a cobertura. `visit_realized` depende da
marcação de comparecimento pela equipe e usa outro momento da jornada.
As contagens não formam uma coorte: dividir confirmações por cliques ou
comparecimentos por confirmações produziria uma taxa sem sequência validada.
O banco operacional não foi consultado nesta análise.

As etapas novas do formulário começaram em 22/10. Até 31/10, o GA registrou
48 visualizações do formulário por 27 usuários, 17 inícios por 14 usuários e
oito tentativas de envio por seis usuários. São contagens isoladas por evento.

Também foi consultado pelo MCP um funil fechado de **22 a 31/10**, exigindo
as etapas em sequência e `form_kind=standard` em cada uma:

| Etapa em sequência | Usuários ativos |
| --- | ---: |
| Abriu o formulário | 27 |
| Começou a preencher | 14 |
| Tentou enviar | 6 |
| Concluiu a reserva | 3 |

Nesse recorte, três de 27 usuários percorreram a sequência completa (11,1%).
O volume é pequeno e a instrumentação é recente. A sequência pode atravessar
sessões e reservas diferentes de uma pessoa dentro do período. As saídas
indicam etapas a investigar; relacioná-las aos impedimentos abaixo exige
uma análise da mesma jornada.

Houve 14 ocorrências de impedimento: nove pelo encerramento das reservas para
o mesmo dia, quatro pelo limite de pessoas e uma por data indisponível.
As quatro ocorrências classificadas como erro foram três de horário obrigatório
e uma de campos obrigatórios. Esses motivos descrevem regras e validações do
formulário; a consulta não identificou falha técnica nesses quatro registros.

A consulta específica de conversões publicitárias retornou nenhuma linha.
Isso fica registrado como ausência de dados nesse relatório. Os valores de
receita e transações dos prints não apuram o faturamento do restaurante.

## Mudanças que afetam a comparação

| Data | Mudança verificada no histórico do site | Efeito na leitura |
| --- | --- | --- |
| 06/09 | Continuidade entre site e portal, commit `74e721d` | Setembro inclui período anterior à mudança. |
| 22 e 28/09 | Cardápio próprio criado e links principais direcionados a ele, `010ad71` e `317ffc8` | A medição de páginas e eventos de cardápio cobre só parte de setembro. |
| 28/09 | Categoria vista passou a acompanhar a rolagem, `d0725a4` | Voltar a categorias pode gerar novas ocorrências. |
| 06/10 | `click_menu` deixou de evento principal | O critério de sessão engajada mudou durante o período. |
| 13/10 | Tags passaram a aguardar interação ou prazo; exceção para chegada paga em Conheça | Visitas que saem antes do carregamento podem faltar. |
| 22/10 | Novas etapas do formulário e posição dos botões | Esses detalhes têm cobertura apenas depois da publicação. |
| 06, 13 e 25/10 | Correções de atribuição | Parte da diferença entre origens pode vir da coleta. |

`cardapio_categoria_vista` respondeu por 25.576 ocorrências em outubro,
55,5% dos 46.109 eventos do site. O código registra mudanças da categoria
indicada durante a rolagem e permite repetições. Os 973 eventos de categoria
do visitante no print representam ocorrências registradas; identificar sua
causa individual exigiria contexto adicional. São ocorrências de mudança de
categoria, com repetição possível por visitante. Para relacioná-las a pedidos
ou receita, faltam registros dessas ações ligados à mesma jornada.

Referências locais: [medição do site](../../site/tools/analytics/README.md),
[eventos do cardápio](../../site/assets/js/cardapio.js) e
[medição das reservas](../../reservas/docs/medicao-google.md).

## Configurações concluídas em 02/11

Foram criados e relidos pela Admin API dois públicos, com permanência de
30 dias e escopo entre sessões:

| Público | Regra | ID |
| --- | --- | --- |
| Interesse em reservar \| 30 dias | `click_reservation` OU `reservation_form_start` | `16251877074` |
| Reserva concluída \| 30 dias | `reservation_confirmed` | `16251942297` |

Os grupos podem incluir a mesma pessoa. O primeiro acompanha interesse e
pode incluir quem confirmou. Nenhum evento de entrada no público foi criado.
O preenchimento no Analytics começa após a criação e pode levar 24–48 horas.
O comportamento de preenchimento é descrito na
[documentação de públicos](https://support.google.com/analytics/answer/9267572?hl=pt-BR).

A retenção de eventos passou de dois para **14 meses**, com atualização apenas
de `event_data_retention`. A retenção de usuários em 14 meses e sua redefinição
por nova atividade foram preservadas e relidas. A Google informa prazo de
24 horas para a mudança. A retenção ampliada conserva os dados detalhados
ainda existentes para Explorações e funis; os relatórios agregados mantêm seu
histórico. [Efeitos da retenção](https://support.google.com/analytics/answer/7667196?hl=pt-BR).

Uma nova prévia somente de leitura confirmou que os dois públicos já existem
com as regras esperadas. Os eventos principais de reserva, rota, WhatsApp e
comparecimento e as quatro dimensões personalizadas do funil foram conferidos.

## Assistente de Tarefas e pendências

A imagem enviada mostra sete de 12 tarefas restantes. Os nomes visíveis são
**Ativar os indicadores do Google** e **Criar públicos-alvo**. A configuração
de públicos foi concluída; a marcação e o contador do checklist não puderam
ser conferidos, pois o navegador desta sessão estava indisponível. O MCP não
expõe o Assistente. Os nomes das outras cinco pendências continuam necessários
para avaliá-las individualmente. O Assistente permite marcar tarefas depois da
configuração. [Funcionamento do Assistente](https://support.google.com/analytics/answer/16888318?hl=pt-BR).

A Admin API confirmou os indicadores do Google desligados. Eles foram
mantidos assim porque os eventos existentes permitem acompanhar a reserva.
Desde 15/06/2026, esse ajuste controla a associação dos dados do Analytics a
usuários conectados para relatórios comportamentais.
[Controles atuais dos indicadores](https://support.google.com/analytics/answer/17016975?hl=pt-BR).

Não há vínculo com Google Ads na propriedade. O nome da conta, “Conta do
Google Ads”, não informa o estado desse vínculo. A utilidade de criar um
vínculo depende do uso dessa plataforma e dos dados a compartilhar.

## Próximas decisões

Priorizar a queda dos cliques para reservar, acompanhando o Instagram e os
botões da home com a posição disponível desde 22/10. Separar QR dos acessos
de descoberta ao avaliar aquisição. Conferir a sequência do novo funil e a
coorte operacional de reservas para identificar onde as pessoas interrompem
a jornada; validar disponibilidade e regras antes de atribuir uma saída ao site.

Os impedimentos por horário e tamanho de grupo ajudam a revisar se as
orientações e os caminhos alternativos estão claros. Esses dados, por si só,
não justificam mudar as regras de reserva.

Consultas agregadas, planos, scripts temporários e recibos permanecem em
`tmp/ga4-2026-11-02/`, ignorado pelo Git. O registro versionado contém a análise
e as configurações verificadas, sem credenciais ou dados individuais.
