# Públicos de quem aceitou publicidade

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
