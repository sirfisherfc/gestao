# Tarefas do Analytics conferidas em 03/11/2026

O proprietário mostrou cinco tarefas pendentes do assistente: criar uma ação
de conversão, segmentar anúncios para públicos, User-ID, dados fornecidos
pelo usuário (UPD) e importação de campanhas. O objetivo é medir e otimizar
reservas do Sir Fisher, habilitando os recursos pertinentes ao site.

## Configuração confirmada

Consulta de 03/11 às 19h05 de Fortaleza, propriedade **353205396**, Sir Fisher
— Site Oficial: fuso America/Fortaleza e moeda BRL. Há um vínculo Ads com o
cliente **149-377-8788**, com personalização habilitada no vínculo e
`canManageClients=false` para o acesso consultado.

A Admin API retornou seis eventos principais: purchase (padrão),
click_reservation, click_maps, click_whatsapp, reservation_confirmed e
visit_realized. Os dois últimos usam **ONCE_PER_EVENT**; os três cliques usam
ONCE_PER_SESSION. O evento de compra padrão não comprova venda realizada.

A API retornou quatro públicos: All Users, Purchasers e os dois públicos
personalizados **Interesse em reservar | 30 dias** e **Reserva concluída |
30 dias**. Ambos os personalizados têm duração de 30 dias e personalização
de anúncios habilitada. Isso confirma sua criação; uso em campanha e volume
elegível precisam de conferência no Ads.

`userProvidedDataSettings` retornou somente o nome do recurso. Seus campos
booleanos de ativação e detecção automática não vieram no JSON, correspondendo
ao padrão false do formato Protobuf JSON. A coleta UPD está desativada. A
identidade de relatório está BLENDED; esse valor não comprova envio de User-ID.

## Tratamento das cinco tarefas

| Tarefa | Situação e decisão |
| --- | --- |
| Criar ação de conversão | Reserva concluída já é evento principal. Conferir/criar a ação baseada em reservation_confirmed no Ads é a prioridade para otimizar campanhas por reservas. A ação Ads ainda não pôde ser inventariada por este acesso. |
| Segmentar anúncios para públicos do Analytics | Os dois públicos personalizados já existem. Seu uso exige seleção na campanha; é opcional, conforme a estratégia. A criação do público não comprova que uma campanha esteja usando ele. |
| Configurar User-ID | Opcional nesta etapa. O site público não tem contas de clientes com login e não envia um identificador próprio consistente entre dispositivos. O cadastro de uma reserva não exige implantar essa identificação para ser medido. |
| Configurar UPD | Desativado e preservado assim. Esse recurso envia dados fornecidos pelo cliente, como e-mail/telefone, para correspondência com dados Google. Requer implementação e política próprias; não é necessário para contar reservas. |
| Importar dados de campanhas | Recurso adicional para custos, cliques e impressões de redes externas ao Google. Faz sentido quando houver dados e chaves de campanha conciliáveis. UTMs e vínculo Ads já existentes têm funções próprias; essa importação não é requisito de coleta das reservas. |

O assistente inclui recursos opcionais. A conclusão deve representar a
implementação ou uma decisão explícita sobre cada recurso; não foi marcado
um recurso como instalado para reduzir o contador.

## Conversão de reserva no Ads

O fluxo do Google é **evento → evento principal → conversão**. Marcar um
evento principal e vincular as contas não confirma que a ação Ads foi criada.
A documentação permite criar essa conversão pela interface do Ads ou pela
área Publicidade → Gerenciamento de conversões do Analytics.

Antes de criar, conferir as ações existentes do cliente 149-377-8788. Se já
houver uma correta para a propriedade e o evento, preservá-la. Usar a reserva
concluída para avaliar a meta principal; cliques no botão e contatos têm outro
significado. Conferir contagem, categoria, atribuição e duplicidade. O fluxo
não deve atribuir receita presumida a uma reserva.

O acesso atual não possui conector Google Ads de edição nem credencial local
de desenvolvedor. A tentativa de acesso à interface retornou novamente host
de navegador e computador indisponíveis. O Discovery oficial da Admin API
consultado expõe o recurso legado conversionEvents, que não substitui a gestão
da ação Google Ads. Não foram criadas ações pela API legada como se resolvessem
essa tarefa.

Assim, o cadastro efetivo da ação e seu uso como meta continuam pendentes de
conferência na interface. Nenhuma campanha ou orçamento foi alterado.

## Validação e alcance

Foram relidos propriedade, vínculo, eventos principais, públicos, configurações
UPD e identidade de relatórios usando analytics.readonly. O MCP também permaneceu
somente de leitura. A API consultada não expõe o progresso do assistente; os
contadores visuais têm como fonte as imagens do proprietário.

Não houve alteração de produto, envio de dados pessoais, importação de custos,
migration ou nova coleta de teste nesta conferência. Recibo técnico em
tmp/revisao-2026-11-03/analytics-tasks-read.json, ignorado pelo Git.

## Fontes oficiais

- [Criar e gerenciar conversões](https://support.google.com/analytics/answer/14710559)
- [Criar conversões GA4 no Ads](https://support.google.com/google-ads/answer/2375435)
- [Identificação com User-ID](https://support.google.com/analytics/answer/9213390)
- [Coleta de dados fornecidos pelo usuário](https://support.google.com/analytics/answer/14077171)
- [Importação de dados](https://support.google.com/analytics/answer/10071301)
- [Admin API: novas configurações UPD](https://developers.google.com/analytics/devguides/config/admin/v1/changelog)
