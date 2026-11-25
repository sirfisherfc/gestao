# Teste Meta: público aberto × semelhante dos clientes QR

Pedido do proprietário em 25/11/2026: criar campanhas para comparar o
aproveitamento dos clientes que aceitaram publicidade pelo QR das mesas.
Teto informado: **R$300 no total**. Programação criada, validada em pausa
e ativada para início futuro; a entrega depende da aprovação da Meta.

## Configuração publicada

| Item | A — Aberto | B — Semelhante QR |
| --- | --- | --- |
| Campanha | `120255101248710120` | `120255101257490120` |
| Conjunto | `120255101255550120` | `120255101258020120` |
| Anúncio | `120255101257230120` | `120255101259830120` |
| Criativo | `1310978121178662` | `1459411336355885` |
| Público incluído | Sem interesses/lista | Semelhante 1% `120255101123670120` |
| Orçamento total de mídia | R$130 | R$130 |
| UTM de campanha | `teste_qr_aberto_20261126` | `teste_qr_semelhante_20261126` |

Experimento nativo `2143173756312504`, tipo `SPLIT_TEST`, nome
`SF | Teste QR 26nov2026 | Aberto x Semelhante`. Divisão aleatória 50/50;
células `2148749559340047` e `1710864967421398`, cada qual ligada à campanha
correta. Sem sobreposição entre as células do experimento.

Condições comuns:

- **26/11/2026 às 9h até 03/12/2026 às 9h, America/Fortaleza.** A conta
  Meta usa America/Noronha e exibe 10h nos mesmos instantes. API relida em UTC.
- R$260 de mídia somados; R$40 reservados para cobranças adicionais, seguindo
  a divisão usada na rodada anterior. O orçamento programado na Meta é só mídia.
- Raio de 20 km do restaurante (-3.7247085, -38.4906542); 21–65 anos;
  Instagram feed, Stories e Reels. Sem segmentação por gênero ou interesses.
- Exclusão da mesma base `Clientes QR com aceite | 180 dias`
  (`120255101123660120`) em ambos: comparação de prospecção.
- Objetivo `OUTCOME_TRAFFIC`, otimização `LANDING_PAGE_VIEWS`, cobrança por
  impressões. Sem compartilhamento de orçamento entre conjuntos.
- Advantage+ Audience desligado; expansão de semelhante e público personalizado
  explicitamente desligada em `targeting_relaxation_types`. API mantém
  `detailed_targeting=1`, mas nenhum interesse/detailed_targeting foi definido;
  não confundir esse valor com expansão do semelhante (confirmada em zero).
- Mesmo reel próprio Ambiente, de 28/09, mídia `18113719193582226`:
  https://www.instagram.com/reel/Dd1jlNbBdIH/
- Mesmo texto, imagem/vídeo e CTA Saiba mais. Destino real dos dois anúncios
  lido no campo URL do site do Gerenciador: https://www.sirfisher.com.br/conheca/
- `utm_source=instagram`, `utm_medium=paid_social`,
  `utm_content=ig_18113719193582226`, `utm_id={{campaign.id}}`. Campanhas UTM
  separadas por grupo; nenhuma nova regra de atribuição no site ou portal.

Após a ativação, os três níveis dos dois grupos foram relidos com status
configurado ACTIVE. Anúncios ainda IN_PROCESS na conferência inicial, sem
entrega esperada antes de 26/11 às 9h. Início futuro não é entrega comprovada.

## Como comparar

Métrica principal definida antes da entrega: **custo por landing page view
registrada pela Meta**. Conferir também visitas medidas/engajadas no GA4,
cliques no cardápio e reserva, reservas concluídas e comparecimentos medidos.
Cliques, eventos de pixel e leituras de QR não são vendas ou clientes adicionais.

Comparar os sete dias completos, com a mesma atribuição e o mesmo período
em cada fonte, e dar margem para processamento. Não eleger vencedor por CPC
isolado ou pelos primeiros resultados. Orçamento e base pequenos podem
produzir resultado inconclusivo; a origem QR não comprova compra.

No GA4, filtrar `sessionCampaignName` pelas duas UTMs da tabela. Para site,
usar `hostName=www.sirfisher.com.br`, métricas `sessions`, `engagedSessions` e
`totalUsers`. Consultar `reservation_confirmed` e `visit_realized` por campanha
separadamente; isso mede eventos disponíveis na coleta, não uma auditoria do
consumo nem uma coorte de reservas. Servidor/consentimento podem afetar cobertura.
Não somar usuários ou alcance diário como pessoas únicas do período.

Relatório Meta em leitura:

```powershell
python scripts/marketing/teste_publicos_qr.py --relatorio --ate 2026-12-03
```

O relatório retorna linhas diárias e custo por landing page view medida;
campo ausente fica sinalizado e custo com denominador zero não é calculado.
Antes do início, `--relatorio` sem data retorna `not_started`, sem atribuir
zeros fictícios ao desempenho. Revisões úteis: durante a rodada para detectar
falha de entrega; ao final para comparação. Nenhum agendamento foi criado.

## Validação e recuperação

Ferramenta `scripts/marketing/teste_publicos_qr.py`: prévia sem escrita por
padrão, `--preparar` cria pausado e `--ativar` só atua no recibo relido.
IDs e operação pendente são persistidos antes/depois de cada POST; uma
operação sem resposta exige reconciliação, sem repetição automática.
Na ativação, conta, verba, janela, público, expansão, fonte criativa, UTMs,
destinos e células são conferidos. Se ocorrer falha, pausa as duas campanhas
novas. Nunca mexe em anúncios ou campanhas existentes.

33 testes iniciais e duas verificações adicionais do relatório totalizaram
35 testes sem rede aprovados (17 do teste A/B, 7 do impulsionamento e 11
dos públicos QR). Sintaxe e diff conferidos. Página de destino publicada
passou no teste de CSP/consentimento com coleta interceptada (GA 6, Ads 3,
Meta 1, OpenAI 1), sem envio de eventos de teste ou reservas reais.

A API recusou `promoted_object` somente com pixel para este objetivo; o
parâmetro foi retirado, mantendo tráfego/LPV. Conjunto rejeitado ausente no
inventário, campanha pausada reaproveitada. Expansão automática observada
em pausa foi desligada só nos dois conjuntos novos. Releitura do experimento
normaliza horário ISO retornado pela API; não houve estudo duplicado.

Evidências privadas em `tmp/teste-publicos-qr-2026-11-25/`, ignorado pelo Git:
inventário, plano, recibo com estudos/células/entidades, leituras antes/depois
e validação do destino. Orçamento e status da rodada Ambiente anterior,
Google e ChatGPT foram preservados. A rodada já existente pode gerar outras
exposições; o teste mede estas duas estratégias, não incremento de lucro.

Referências oficiais:
[divisão aleatória e variável única](https://developers.facebook.com/documentation/ads-commerce/marketing-api/guides/split-testing),
[objetivos e landing page views](https://developers.facebook.com/docs/marketing-api/reference/adcampaigngroup/).
