# Público QR, consulta demográfica e revisão

Aplicado em 03/11/2026, America/Fortaleza, após autorização do proprietário.
Código no repositório `site`, commit `8ae5047`. O MCP de Analytics continua
somente para leitura. As escritas específicas usaram a Admin API oficial,
com a credencial privada existente, prévia e releitura de cada recurso.

## O que foi aplicado

| Recurso | Identificação | Finalidade |
| --- | --- | --- |
| Público `Visitantes pelo QR \| 90 dias` | `16266718717` | Visitantes que atenderam a `sessionSourceMedium=qr_code / offline` e navegaram em host público. Condições estáticas entre sessões; permanência de 90 dias. |
| Público `QR \| perfil agregado \| 90 dias` | `16266526911` | Pessoas com evento `qr_visit`. Permite consultar os dados demográficos elegíveis dos membros ativos, inclusive quando voltam por outros canais. |
| Regra de criação do evento `qr_visit` | `16266719936`, fluxo `15405248385` | Identifica `page_view` com URL pública e os parâmetros `utm_source=qr_code` e `utm_medium=offline` antes do fragmento. |

Propriedade fixa: `353205396`, fluxo `G-F40Z5Y9QT6`. Os três hosts públicos
são `www.sirfisher.com.br`, `sirfisher.com.br` e `reservas.sirfisher.com.br`.
A regra de evento exige o host na própria URL. Os filtros do primeiro público
se aplicam entre sessões e não comprovam compra, presença ou consumo.

A regra cria um evento novo para cada página vista que atender aos critérios.
Recarregar a página ou seguir links identificados pode gerar novas ocorrências.
Esse total não equivale ao número de leituras físicas do QR. Não se alterou
o evento original nem se copiaram parâmetros não internos para o evento novo.
O evento QR não foi marcado como evento principal/conversão.

Os dois públicos retornaram `adsPersonalizationEnabled=true`. A elegibilidade
dos visitantes e as escolhas de consentimento continuam sendo condições de uso.
As permissões de publicidade e os pixels do site permaneceram com a configuração
anterior. Nenhuma campanha, anúncio, verba, contato ou dado de cartão foi criado.

## Causa do erro e solução validada

Os testes separados de compatibilidade retornaram HTTP 400 ao combinar
`userGender` com `sessionSource`, `sessionMedium` ou `sessionCampaignName`.
Controle sem esses campos, filtro de hostname e filtro de nome de público
retornaram HTTP 200. A consulta real revelou uma restrição adicional: públicos
que usam dimensões de aquisição herdam a incompatibilidade demográfica.
`checkCompatibility` isolado com nome do público não comprovou a consulta.

Por isso, o primeiro público fica disponível para acompanhamento/publicidade,
e o perfil demográfico usa o segundo, cuja condição é somente `qr_visit`.
A regra de evento identifica a chegada pelo QR sem usar dimensões de aquisição
na consulta demográfica. Os critérios da regra foram conferidos com casos de
URLs válidas, host alheio, host administrativo, parâmetro parecido e fragmentos.

Depois da criação e releitura, **as três consultas reais de idade, gênero e
interesses responderam HTTP 200**, com `activeUsers` e filtro do público de
perfil. Retornaram zero linhas e `subjectToThresholding=true` na janela
02–03/11, imediatamente após criar o público. Isso indica indisponibilidade
da abertura, sem comprovar ausência de usuários. A coleta nova precisa de
tempo e volume elegível; não há garantia de que todos os detalhes apareçam.

O público mede membros ativos no período. O relatório de tráfego mede sessões
identificadas como QR. Esses recortes têm definições próprias e não devem ser
tratados como equivalentes. Não houve recuperação demográfica do histórico
nem substituição silenciosa por todos os visitantes do site.

Referências: [compatibilidade da Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/checkCompatibility),
[regras de criação de eventos](https://developers.google.com/analytics/devguides/config/admin/v1/rest/v1alpha/properties.dataStreams.eventCreateRules),
[públicos e processamento](https://support.google.com/analytics/answer/9267572?hl=pt-BR),
[limites de privacidade](https://support.google.com/analytics/answer/9383630?hl=pt-BR).

## Reservas, comparecimento e Google Ads

Releitura confirmou `reservation_confirmed` e `visit_realized` com contagem
`ONCE_PER_EVENT`. De 02/11 a 03/11 parcial, a Data API retornou seis eventos
de reserva confirmada, em cinco usuários, e quatro de comparecimento, em
quatro usuários. São eventos recebidos, sujeitos à cobertura da coleta;
não equivalem a uma auditoria individual das reservas operacionais.

O vínculo com a conta Google Ads `1493778788` está presente e habilitado
para personalização. **Conferir/importar a ação de conversão no Ads continua
pendente.** O controlador do navegador retornou host indisponível, o controle
nativo também falhou e não há credencial Google Ads/developer token nas
configurações consultadas. O acesso administrativo ao Analytics não substitui
esse acesso. A busca de integrações não encontrou um conector já conectado
para administrar essas conversões. Não se criou uma ação duplicada por suposição.

Quando o acesso ao Ads estiver disponível, conferir primeiro as ações existentes,
importar `reservation_confirmed` se faltar e revisar qual ação orienta os lances.
Comparecimento serve para avaliar qualidade; evitar somar etapas da mesma
reserva como se fossem clientes distintos. A publicação dos scripts não ativa
campanhas. [Criação de conversões](https://support.google.com/analytics/answer/14710559?hl=pt-BR).

## Revisão em duas semanas

Registrada a tarefa única `SirFisher-RevisaoQR-20261117` neste PC para
**17/11/2026 às 9h de Fortaleza**. Ela consulta o período 03–16/11 e grava
`gestao/tmp/perfil-qr-2026-11-17/perfil-qr.json`, ignorado pelo Git.
Os dias mais recentes ficam sinalizados como sujeitos a processamento.

Exige computador ligado, internet e sessão do proprietário aberta.
`StartWhenAvailable=true` tenta executar depois se perder o horário. A tarefa
não envia mensagens, não muda campanhas e não copia credenciais para o
Agendador. A credencial permanece no arquivo privado existente no OneDrive.
Outro PC não recebe essa configuração local automaticamente.

O mesmo executável e comando foram testados sem janela, com datas já disponíveis
e saída em diretório de teste: código de saída zero, arquivo criado e as três
consultas demográficas concluídas. A tarefa futura não foi executada antecipadamente.

## Verificações e recibos

Oito testes de contratos passaram, incluindo idempotência, preservação de
definições divergentes, destino fixo e ausência de troca silenciosa do público.
Catálogo estático, hashes de assets e CSP passaram. Os testes QR entraram no
workflow de verificação do site. Nenhum HTML, JavaScript público, SQL ou
configuração de segredo foi alterado.

Recibos agregados em `tmp/revisao-2026-11-03/`: prévias e releituras dos públicos,
regra aplicada, investigação de compatibilidade, relatório compatível e ensaio
sem janela. Esses arquivos permanecem ignorados pelo Git.
