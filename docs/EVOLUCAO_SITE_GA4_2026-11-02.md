# Evolução do site no Google Analytics

Consulta em 02/11/2026. Comparação: setembro de 2026 (30 dias) e outubro de
2026 (31 dias), os dois últimos meses completos, no fuso America/Fortaleza.

## Resultado observado

O site recebeu mais visitas em outubro e os visitantes usaram mais o cardápio
publicado no próprio domínio. Os cliques para reservar caíram. Na conferência
operacional acrescentada em 02/11, as reservas públicas criadas passaram de
27 para 24, queda de 11,1%. O Analytics registrou 22 e 24 eventos de confirmação, enquanto
a presença dos identificadores GA nas reservas passou de 74,1% para 100%.
O crescimento do tráfego exige acompanhamento separado da criação de reservas.

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

Na retomada de 02/11, o Navegador passou a acessar a sessão existente do
Analytics. O checklist, a integração do Search Console e o insight semanal
foram conferidos pela interface. A coorte operacional veio da função canônica
`operations_report`, pela rota Supabase `/database/query/read-only` no projeto
`portal`, com apenas agregados de reservas `source=public_site`.

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
Cada contagem usa a etapa e a cobertura do evento. Calcular uma taxa entre
cliques, confirmações e comparecimentos exige uma coorte com sequência validada.

### Conferência operacional acrescentada em 02/11

| Período de criação em Fortaleza | Reservas públicas criadas | Com ambos os identificadores GA | Cobertura dos identificadores |
| --- | ---: | ---: | ---: |
| Setembro, 01–30 | 27 | 20 | 74,1% |
| Outubro, 01–31 | 24 | 24 | 100% |
| Outubro, 22–31 | 4 | 4 | 100% |

As reservas públicas criadas caíram 11,1% no total. A média diária passou de
0,900 para 0,774, queda de 14,0% depois do ajuste pela quantidade de dias.
O recorte considera a data de criação, com início inclusivo e fim exclusivo
no fuso de Fortaleza. Reservas inseridas por outros canais ficam fora.

Os identificadores preenchidos ajudam a medir a jornada, mas seu preenchimento
não comprova recebimento pelo GA ou correspondência individual. As consultas
operacionais e GA foram agregadas e mantidas em paralelo.

Na data da consulta, oito reservas da coorte de setembro e 11 da de outubro
estavam marcadas como comparecimento. Ainda havia três e sete reservas com
status confirmada, respectivamente. Esses são os status atuais das reservas
criadas em cada mês; comparar o comparecimento final exige acompanhar os
resultados dessas reservas e a data da visita.

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
causa individual exigiria contexto adicional. Para relacioná-las a pedidos
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

## Assistente de Tarefas: execução pelo Navegador

O primeiro acesso da ferramenta estava indisponível. Depois de conectar o
Navegador e tentar novamente em 02/11, a sessão do Chrome abriu a propriedade
correta. Todas as categorias do Assistente foram lidas. A tela passou de
**sete para três de 12 tarefas restantes** depois das configurações desta rodada.

| Tarefa atendida | Resultado conferido |
| --- | --- |
| Criar públicos-alvo | Os dois públicos de reserva aparecem na interface e a tarefa passou a concluída. |
| Vincular ao Search Console | Domínio verificado `sirfisher.com.br` vinculado ao fluxo Sir Fisher, `https://www.sirfisher.com.br`, ID `15405248385`. A interface confirmou “VINCULAÇÃO CRIADA”. |
| Criar insights personalizados | Criado “GA4: queda semanal acima de 50% nas ações principais”, com avaliação semanal e e-mails desligados. |
| Ativar os indicadores do Google | Ativados após a publicação do aviso de privacidade e a confirmação expressa da declaração pelo proprietário. A chave ficou ligada; a interface informou permissão em 307 de 307 regiões. |

O insight compara a métrica Eventos principais com a semana anterior, de
domingo a sábado, e aparece no painel se a redução for superior a 50%.
Ele acompanha o conjunto dos eventos principais existentes, que inclui
reserva e ações de contato. Um recorte específico da sequência da reserva
continua disponível pelo relatório de funil. A lista de destinatários do
insight ficou vazia e o botão de notificações por e-mail foi relido desligado.

O relatório **Search Console → Consultas** já estava acessível com dados.
No recorte exibido, de 05/10 a 01/11, a consulta “pôr do sol hoje” respondeu
por 160 dos 224 cliques mostrados no relatório (71,4%). Essa janela é distinta
dos meses comparados neste documento. O termo sugere interesse informacional;
para atribuir reservas a ele faltam dados da mesma jornada. O relatório também
mostra consultas de marca e de restaurantes na Beira-Mar.

Os três itens ainda apresentados pelo Assistente foram avaliados:

| Tarefa restante | Condição para adotar |
| --- | --- |
| Vincular ao Google Ads | Definir a conta e o uso de campanhas nessa plataforma, com os dados que serão compartilhados. |
| Configurar o User-ID | Dispor de um identificador interno estável para visitantes autenticados. A jornada pública de reserva funciona sem login. |
| Configurar dados fornecidos pelo usuário (UPD) | Definir quais dados de contato seriam enviados à Google e a finalidade dessa coleta adicional. |

Esses três recursos permaneceram com a configuração existente. A tarefa
Google Ads aparece em duas categorias, sendo contada uma vez no total.
“Corrigir problemas com dados” mostrou nenhuma tarefa detectada.
[Funcionamento do Assistente](https://support.google.com/analytics/answer/16888318?hl=pt-BR).

A primeira leitura da Admin API encontrou os indicadores do Google desligados.
Depois do pedido de perfil demográfico, o proprietário confirmou a declaração
exigida pela Google e autorizou a ativação após a publicação do aviso.
O commit `5f97e9f` do site publicou o aviso em 02/11; o conteúdo público foi
conferido antes da ativação. A interface confirmou os indicadores ligados e
o Assistente passou a mostrar três tarefas restantes.

Os relatórios poderão mostrar idade, gênero e interesses agregados dos
visitantes elegíveis. A exibição depende do consentimento, das condições da
conta Google e dos limites mínimos de dados. O recorte pequeno de QR pode
continuar sem linhas. As consultas de setembro e outubro retornaram linhas
vazias e `subject_to_thresholding=true`; isso representa indisponibilidade.
A ativação não comprova recuperação do histórico nem liberação imediata.
[Indicadores do Google](https://support.google.com/analytics/answer/9445345?hl=pt-BR),
[limites mínimos](https://support.google.com/analytics/answer/9383630?hl=pt-BR).

Desde 15/06/2026, esse ajuste controla a associação dos dados do Analytics a
usuários conectados para relatórios comportamentais.
[Controles atuais dos indicadores](https://support.google.com/analytics/answer/17016975?hl=pt-BR).

Não há vínculo com Google Ads na propriedade. O nome da conta, “Conta do
Google Ads”, não informa o estado desse vínculo. A utilidade de criar um
vínculo depende do uso dessa plataforma e dos dados a compartilhar.

## Acompanhamento da jornada

Priorizar a queda dos cliques para reservar, acompanhando o Instagram e os
botões da home com a posição disponível desde 22/10. Separar QR dos acessos
de descoberta ao avaliar aquisição. O funil sequencial e a coorte operacional
foram conferidos. Relacionar cada saída aos impedimentos ainda exige dados da
mesma jornada; a disponibilidade e as regras também precisam entrar na análise.

Os impedimentos por horário e tamanho de grupo ajudam a revisar se as
orientações e os caminhos alternativos estão claros. Esses dados, por si só,
não justificam mudar as regras de reserva.

### Ajustes no portal de reservas

O commit `444180f` do repositório `reservas` alinha o formulário ao site:

- Grupos acima do limite do portal e até 29 pessoas seguem para consulta no
  WhatsApp; eventos de 30–100 pessoas sentadas abrem o configurador. Acima de
  100, a mensagem orienta consultar a equipe para avaliar o pedido.
- Após o corte, a mensagem informa visita por ordem de chegada conforme a
  disponibilidade e oferece Como chegar e WhatsApp para dúvidas. A orientação
  também aparece quando o corte é retornado apenas na tentativa de envio.

O limite e o horário continuam vindo das configurações existentes. A frase
de corte passou a explicar o momento de confirmar a reserva. As versões em
português e inglês foram alinhadas.

Os 24 testes de funil e atribuição passaram. O teste de navegador bloqueou a
rede externa e simulou os RPCs; cobriu PT/EN em 390 e 1440 px, os limites
11/29/30/100/101, uma configuração de apoio com limite 12 e corte às 16:00,
e o corte retornado no envio com uma ocorrência de impedimento registrada.
Esses testes preservaram os registros e eventos reais de produção.

Arquivos: [formulário](../../reservas/index.html),
[comportamento da reserva](../../reservas/assets/js/reservations.js),
[traduções](../../reservas/assets/js/i18n.js),
[teste do navegador](../../reservas/tools/reservation_funnel_browser_test.py) e
[registro de medição](../../reservas/docs/medicao-google.md).

Consultas agregadas, planos, scripts temporários e recibos permanecem em
`tmp/ga4-2026-11-02/`, ignorado pelo Git. O registro versionado contém a análise
e as configurações verificadas, sem credenciais ou dados individuais.

A avaliação dos avisos Semrush, o perfil agregado do QR e a estratégia de mídia
estão em [Semrush, público e mídia](SEMRUSH_PERFIL_PUBLICO_MIDIA_2026-11-02.md).
As provas da ativação e do checklist ficam em `tmp/semrush-2026-11-02/`.

## Conferência do Google Ads em 03/11/2026

A Admin API confirmou que a propriedade `353205396`, **Sir Fisher — Site
Oficial**, continua sem vinculações com Google Ads. Uma consulta real de
eventos de 27/10 a 02/11 retornou dados. O nome da conta do Analytics,
“Conta do Google Ads”, permanece apenas um nome de cadastro.

O proprietário informou que já anunciou no Google. E-mails do Google de
abril e maio de 2026 identificam uma conta chamada **Barra Sol - Sir Fisher**.
O identificador foi informado ao proprietário na conversa, sem guardar
mensagens ou conteúdo financeiro no repositório. Ainda falta confirmar o
acesso administrativo e o estado atual das campanhas nessa conta.

O MCP disponível oferece consulta das vinculações, sem criar ou editar
esse vínculo. A integração de interface do computador estava indisponível
nesta sessão. Para concluir no painel, usar a mesma conta Google com papel
Editor/Administrador no Analytics e Administrador no Ads: **Administrador →
Vinculações de produtos → Vinculações do Google Ads → Vincular**. Conferir
a propriedade e a conta individual antes de enviar. A opção de publicidade
personalizada vem ligada por padrão; para começar pela mensuração, a
recomendação apresentada foi desligá-la nesse vínculo e habilitar a
codificação automática. A decisão e a gravação continuam pendentes.
[Instruções e permissões](https://support.google.com/analytics/answer/9379420?hl=pt-BR),
[controle de personalização](https://support.google.com/analytics/answer/9626162?hl=pt-BR).

O redirecionamento HTTP do domínio raiz preservou `gclid=TesTER-123` até
`www`. Com User-Agent de navegador, GET e HEAD do site responderam 200 com
e sem esse parâmetro. O cliente Python padrão recebeu 403 no destino.
Esses testes conferem o caminho HTTP; faltam o teste no navegador e a
validação da coleta de um clique real após o vínculo. Nenhum JavaScript
de medição foi executado nos testes.
[Teste recomendado pelo Google](https://support.google.com/analytics/answer/13367418?hl=pt-BR).

Nenhuma campanha, orçamento, conversão ou vinculação foi alterada nesta
conferência. Após criar o vínculo, reler a Admin API e avaliar as conversões
existentes antes de importar novos eventos para os lances. A documentação
informa prazo de até 48 horas para aparecerem dados do Ads no Analytics.
