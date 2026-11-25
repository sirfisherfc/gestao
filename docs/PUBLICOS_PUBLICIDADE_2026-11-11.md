# Públicos de quem aceitou publicidade

## Público QR e semelhante criados em 25/11/2026

Direção confirmada pelo proprietário: aproveitar os clientes que aceitaram
para encontrar pessoas parecidas no Google e na Meta. Retorno ao site
renovando o sinal QR não é um impedimento para essa finalidade; não alterar
`VisitaQR` ou restringir a coleta para contar novas presenças físicas. O
evento continua sem representar compra ou uma nova presença na casa.

Concluída criação na conta Meta do Portfólio `1004410887092327`, usando
apenas o evento `VisitaQR` do pixel `Sir Fisher - Website` (`948509834960152`):

| Recurso | ID | Releitura após criar |
| --- | --- | --- |
| `Clientes QR com aceite \| 180 dias` | `120255101123660120` | WEBSITE; regra exata VisitaQR; delivery 200, operation 441 (preenchendo) |
| `Semelhante 1% \| Clientes QR` | `120255101123670120` | LOOKALIKE; origem no público acima; proporção 0,01; delivery 200, operation 300 (atualizando) |

Ambos aceitos e relidos na API, com conta, regra e origem verificadas. O
tamanho inicial ainda não é uma contagem consolidada. `prefill=true` aproveita
o histórico do próprio evento consentido, sem regra genérica por URL e sem
upload de nome/telefone. A lista é atualizada pela Meta conforme o evento
e sua retenção. A leitura agregada do pixel confirmou `VisitaQR` recebido;
eventos repetidos não são pessoas adicionais na contagem de público.

No Google Ads, sessão existente reutilizada e conta `149-377-8788`
confirmada: ambos os públicos QR de 90 dias já estão compartilhados com o
Ads. `Visitantes pelo QR | 90 dias` tem lista `9499060310` e
`QR | perfil agregado | 90 dias`, `9499064759`. A interface mostrou 0 em
Pesquisa/YouTube/Display e 8 em Gmail, com tamanho insuficiente e sem uso
em campanhas. A conta informa que não há anúncios sendo veiculados porque
campanhas/grupos estão pausados ou removidos. Isso não equivale a ausência
de acessos no GA4; população elegível para publicidade tem outra cobertura.

Não houve mudança no site, consentimento, reservas, campanhas, segmentação
ativa ou orçamento. Para gerar entrega com a nova base Meta, o semelhante
ainda precisa ser usado como público/sugestão na configuração de campanha.
No Google, aplicar a base como sinal em campanhas compatíveis quando forem
veicular; não reativar campanha expirada nem criar verba por inferência.

Ferramenta reproduzível, com prévia, rotas limitadas e releitura idempotente:

```powershell
python scripts/marketing/publicos_qr.py
python scripts/marketing/publicos_qr.py --aplicar --out tmp/publicos-qr-2026-11-25/recibo.json
python -B -m unittest discover -s scripts/marketing -p test_publicos_qr.py
python -B -m unittest discover -s scripts/marketing -p test_impulsionar.py
```

A escrita aceita apenas esses dois nomes/regras na conta fixa. WEBSITE é
inferido da regra pela API v27: `subtype=WEBSITE` foi recusado com 2654;
LOOKALIKE usa `subtype=LOOKALIKE`, origem validada e somente `ratio=0.01`,
sem país (a localização continua no conjunto). O ID criado é salvo antes
da releitura, para não repetir POST após falha de rede. Os demais comandos
do cliente Meta mantêm v26. Sem ampliação do MCP de Instagram somente leitura.
18 testes sem rede passaram. Recibos em `tmp/publicos-qr-2026-11-25/`.

Referências oficiais: [públicos de site](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/guides/website-custom-audiences),
[semelhantes e formato v27](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/guides/lookalike-audiences),
[sinais de público no Google Ads](https://support.google.com/google-ads/answer/14753570).

## Conferência em 25/11/2026, antes da criação dos públicos QR

O proprietário esclareceu: somente QRs nas mesas estão em uso. O objetivo
é aproveitar automaticamente os sinais autorizados nas plataformas; pesquisa
de perfil e mudança do destino do QR não são necessárias a esse objetivo.

Consulta GA4 de 26/10 a 24/11: `publicidade_aceita` em sessões atribuídas a
`qr_code / offline` teve 584 eventos e 581 usuários. Não é tamanho de público
elegível, prova de recebimento pela Meta ou ganho incremental de vendas.
Admin API relida: os dois públicos QR de 90 dias continuam presentes e com
personalização habilitada. Essa configuração não prova uso em campanha.

Leitura real da Marketing API, com identidade `sirfisherfc` confirmada e
`ads_read` concedida, no objeto da conta do Portfólio esperada. Inventário
completo, sem próxima página: apenas o público de engajamento Instagram e
seu semelhante, ambos prontos para uso. O público QR não existe nessa conta.
Dos 17 conjuntos retornados, três com `effective_status=ACTIVE`: todos com
destino WEBSITE, otimização LINK_CLICKS e sem público personalizado no
targeting. Não afirmar que os aceites já estão orientando um público QR
nas campanhas, nem que a entrega aberta não usa nenhum sinal do pixel.

O benefício técnico do aceite é permitir os sinais/publicidade personalizada
previstos no site. Ganho comercial incremental não foi demonstrado. Próxima
etapa para aproveitar especificamente o QR: corrigir o evento, conferir seu
recebimento, preparar público/semelhante elegíveis e uso explícito em campanha.
Não ativar campanhas ou mudar orçamento apenas por causa deste diagnóstico.

Correção proposta para `VisitaQR`, ainda não implantada: exigir entrada atual
com os parâmetros QR/offline, preservar essa entrada por uma janela curta
para aceitar publicidade na página seguinte e deduplicar por visita. Não
usar os 90 dias de origem armazenada como prova de nova leitura. Preservar
a atribuição histórica separadamente. Isso mede abertura do endereço QR,
não distingue câmera, link compartilhado e URL reaberta pelo navegador.

Evidências agregadas: `tmp/qr-aceite-2026-11-25/`. Sem alteração de código,
pixel, público, anúncio ou banco nesta conferência. As seções abaixo são o
histórico da implantação de 11/11, preservado com sua data.

Pedido do proprietário em 11/11/2026: usar quem permite publicidade no site,
em especial clientes que leem o QR Code da mesa, para as plataformas
formarem públicos e procurarem pessoas parecidas. A política de privacidade
já previa "formar públicos para campanhas"; agora cita o QR expressamente.

## Publicado

Site `bd4b39b` e portal `8b76ae1`, conferidos em produção pelo hash dos
scripts. O `google-ads.js` continua idêntico nos dois repositórios.

| Mudança | Onde | Quando dispara |
| --- | --- | --- |
| `publicidade_aviso_exibido` | GA4, site e portal | Aviso aparece para quem ainda não escolheu |
| `publicidade_aceita` | GA4, site e portal | Clique em Permitir |
| `publicidade_recusada` | GA4, site e portal | Clique em Recusar |
| `VisitaQR` | Pixel da Meta, só no site | Origem guardada é `qr_code` e a pessoa permitiu publicidade; uma vez por página |

Os eventos do GA4 não levam comprovante nem dado pessoal. O aviso conta
uma vez por página até a escolha; para taxa de aceite, comparar usuários,
não eventos. Sem permissão, `VisitaQR` não sai. A origem QR vale por 90
dias ou até uma nova chegada externa.

Validação: 89 testes de atribuição e carregamento, 26 do portal, teste de
navegador com os três eventos do GA4 e verificações de assets, CSP, FAQ e
cardápio. Um teste extra no Edge confirmou `VisitaQR` ao aceitar na home
vinda do QR e na página seguinte, e ausência para quem veio do Instagram.

## Meta: criado em 11/11 e pendente

Usar a conta de anúncios do **Portfólio Sir Fisher**. A conta pessoal do
proprietário também aparece no seletor, não enxerga o pixel e oferece criar
outro; não criar. A conta do portfólio não tinha público personalizado nem
semelhante, só dois públicos salvos antigos.

Criados às 10h04 e 10h05, ambos "em preenchimento" e disponíveis para uso:

- `Engajamento Instagram @sirfisherfc | 365 dias`, pessoas que interagiram
  com a conta profissional. Quem chega ao site pelo Instagram já está aqui,
  sem depender do aviso de cookies; por isso não entra no `VisitaQR`.
- `Semelhante (1%) - Engajamento Instagram @sirfisherfc | 365 dias`. A Meta
  não define mais região no semelhante; a localização vem do conjunto de
  anúncios, onde também aparece o tamanho estimado.

Pendente: o pixel ainda não tinha recebido `VisitaQR` (lista com PageView,
ViewContent, InitiateCheckout, Schedule, FindLocation e Contact). Depois do
primeiro evento:

1. Públicos → Criar público → Público personalizado → Site.
2. Pixel `Sir Fisher - Website`; pessoas que realizaram o evento
   `VisitaQR`; retenção de 180 dias. Nome: `Clientes QR com aceite | 180 dias`.
3. Criar público → Público semelhante, origem no público acima, Brasil, 1%.
   Nome: `Semelhante 1% | Clientes QR`.

`VisitaQR` só aparece na lista depois do primeiro evento recebido. O
semelhante precisa de pelo menos 100 pessoas da mesma origem no público de
base; o volume depende da taxa de aceite no QR, ainda sem medição.
Uma regra extra por URL com `utm_source=qr_code` traria histórico anterior,
inclusive visitas de antes de 03/11, sob o aviso então vigente; não foi
recomendada.

## Google

O GA4 já tem, com personalização ativa e vínculo ao Google Ads:
`Visitantes pelo QR | 90 dias`, `QR | perfil agregado | 90 dias`,
`Interesse em reservar | 30 dias` e `Reserva concluída | 30 dias`. Só entram
pessoas com permissão de anúncios. Usá-los exige uma campanha: o último
registro é de conta pausada aguardando a verificação do anunciante, prazo
03/12/2026 ([verificação](GOOGLE_ADS_VERIFICACAO_2026-11-03.md)). Nenhuma
campanha ou verba foi criada.

## ChatGPT Ads

Não oferece público de visitantes do site nem semelhante. Aceita apenas
listas de e-mails ou telefones com pelo menos 25 mil pessoas reconhecidas.
[Custom Audiences](https://help.openai.com/en/articles/20001346-set-up-custom-audiences-for-your-campaign).

## Quedas do Claude in Chrome

A conexão passa pela conta, sem conector local no registro do Chrome. Os
registros do Claude Code mostram só conexões, sem motivo da queda. Nas
transcrições de 09 a 11/11, as quedas vieram após ociosidade: 9 minutos sem
uso, 33 segundos depois de fechar a última aba do grupo do Claude e cerca
de 7 minutos depois da última ação. A economia de memória do Chrome está
ligada e descarta abas paradas. Quatro sessões do Claude Code deste projeto
reconectaram juntas em 11/11; não houve uso simultâneo nas transcrições.

Quando cai, as ferramentas somem da sessão; só o `/chrome` do proprietário
reconecta. Para reduzir: incluir os sites de trabalho em "Sempre manter
estes sites ativos" na economia de memória, não fechar a barra "Claude
começou a depurar", manter uma aba do grupo aberta até o fim da tarefa e
fechar sessões antigas do Claude Code.
