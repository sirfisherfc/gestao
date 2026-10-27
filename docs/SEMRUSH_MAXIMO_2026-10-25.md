# Semrush: extração adicional e plano de aquisição

Referência: 25/10/2026, America/Fortaleza. Esta rodada usa os acessos existentes
para responder perguntas comerciais ainda abertas e guardar o material útil
antes de eventual cancelamento. O
[acervo anterior](SEMRUSH_3_DIAS_2026-10-25.md), as planilhas e os ZIPs congelados
conservam seus períodos, contagens e resultados.

As evidências novas ficam em `output/semrush-maximo-2026-10-25/`, na raiz do
workspace, fora dos três repositórios. O site foi publicado e conferido.
A coleta terminou com dois recortes do Maps, quinze respostas de IA
conferidas, os relatórios adicionais por API e o plano de Google Search
preparado para revisão. Nenhum anúncio foi lançado.

## Melhorias publicadas

O site recebeu duas mudanças no commit
[`de2f863`](https://github.com/sirfisherfc/site/commit/de2f863add40377c4ec8284dc6acc9d252a5779e):

- No cardápio, os alergênicos ocupam ícones compactos nos cards. Os nomes
  permanecem no texto acessível, na ficha do prato e na legenda PT/EN.
  São 78 cards e 61 ícones; os cards continuam links para os detalhes, sem
  controles interativos aninhados. Dados culinários e Big Ben Fries 250 g
  foram preservados.
- O [guia da Beira-Mar](https://www.sirfisher.com.br/guia/beira-mar/#hospedagem)
  ganhou uma seção para quem está hospedado na região. Ela liga o visitante
  a almoço, cardápio, horário, rota conforme o hotel de partida e reserva.
  Usa a página existente, sem criar guia de hospedagem ou nova oferta.

Passaram 113 testes Deno e quatro verificadores. A revisão no navegador
aprovou 47 verificações de aceitação, incluindo cardápio PT/EN em celular e
desktop, nomes acessíveis, ficha/legenda e guia nos temas claro/escuro.
Assets e GitHub Pages concluíram com sucesso. Os 14 GETs de verificação
pública, com URLs comuns e parâmetro de consulta, retornaram HTTP 200 e
conteúdo igual ao commit após normalização de quebras de linha. Recibo:
`output/semrush-maximo-2026-10-25/publicacao-site.json`.

## Perguntas e critérios

| Pergunta desta rodada | Evidência necessária para decidir | Limite conhecido |
| --- | --- | --- |
| Quais buscas comerciais ainda merecem atenção? | Lacunas contra concorrentes com negócio e localização aderentes, ligadas às páginas atuais | Volume nacional e posição de concorrente não comprovam clientes locais ou procura pela oferta Sir Fisher. |
| Um anúncio de pesquisa pode trazer clientes com economia aceitável? | Oferta escolhida, termos de intenção comercial, página adequada, acesso e medição da conta, meta e teto aprovados | CPC estimado não define investimento. Reservas confirmadas e comparecimentos dependem da cobertura da coleta. |
| Quem se hospeda na região encontra um caminho claro até a refeição? | Guia com orientação de chegada, horário da oferta, cardápio e reserva; leitura por página | País, idioma e consulta near me não identificam turista ou hóspede. |
| Os alergênicos podem ocupar menos espaço sem perder informação? | Ícones acompanhados de nomes acessíveis e nomes completos na ficha, com validação em celular e teclado | A legenda no fim é apoio. Informação acessível e detalhes do prato precisam continuar disponíveis. |
| O que os painéis locais e de IA acrescentam? | Conjunto, local, idioma, plataforma e data preservados em cada exportação | Uma data fornece uma linha de base. Menção, posição e presença em fonte não equivalem a visita ou venda. |

Boa entrega nesta rodada: responder essas perguntas com fontes identificadas,
publicar apenas ajustes autorizados e testados e entregar arquivos portáteis
com seus limites. Não há lançamento de mídia ou nova coleta manual do salão.

## Base própria reaproveitada

Na comparação de 25/09–22/10 com 28/08–24/09, os cliques GSC passaram de
123 para 261. Consultas comerciais sem marca visíveis passaram de 14 para
15; pôr do sol passou de 14 para 109. As reservas públicas criadas ficaram
em 25 nas duas janelas. IDs do Analytics passaram de 15 de 25 para 25 de 25,
mudança que afeta a cobertura observada. Fonte e definições na
[revisão de SEO, descoberta local e conversão](REVISAO_SEO_LOCAL_CONVERSAO_2026-10-25.md).

O histórico por página do pôr do sol, 21/09–18/10, tem 86 sessões de entrada,
seis cliques no cardápio, um em rota e nenhum em reserva. A página passou por
mudanças em 20/10; esses dados não avaliam o efeito posterior. O conjunto
ainda deixa aberta a passagem de informação turística para uma refeição.

O acervo anterior contém dois termos de hotel da URL Coco Bambu Beira-Mar:
hotel em Fortaleza Beira Mar, volume BR estimado de 2.900 e posição 24, e
hotel Torres Beira Mar, 720 e posição 22, em snapshots de 16–17/10 na base
Brasil/desktop. Não há URL própria Sir Fisher nesses registros. O recorte
que melhor acompanha a oferta é ajudar quem já se hospeda na região a
encontrar almoço, jantar e rota. A pesquisa disponível ainda não sustenta
um guia de escolha ou reserva de hospedagem.

## Plano de Google Search preparado

O [plano para revisão](PLANO_GOOGLE_SEARCH_2026-10-25.md) apresenta grupos,
palavras candidatas, negativas, títulos e descrições, páginas de destino e
critérios de medição. Todos os componentes estão em documento. Ainda será
necessário escolher objetivo, definir economia e teto e conferir a conta.
Nenhum orçamento, lance, anúncio ou campanha foi aplicado por essa preparação.

## Pesquisa adicional por API

O coletor único executou cinco chamadas de relatório: duas com dados e três
`no_data`, preservadas como resultados finais para os parâmetros usados.
As respostas com dados somam 54 linhas: 30 domínios na matriz de backlinks
e 24 links para NOM. São tipos de registro diferentes, sem equivalência a
54 oportunidades comerciais independentes.

| Recorte | O que foi observado | Decisão sustentada |
| --- | --- | --- |
| Anúncios, Brasil | Illa Mare, NOM e a URL exata da unidade Coco Bambu Beira-Mar retornaram `no_data` | Manter o plano pago como proposta baseada na oferta. Não houve anúncio ou CPC recuperado desses alvos, e a ausência de dados não comprova ausência de campanhas. |
| Matriz de backlinks | Dos 30 domínios, 16 apontam a dois alvos: 14 a Illa e NOM, do mesmo Grupo Illa; dois a Illa e à unidade Coco Bambu | A relação entre os negócios explica parte da sobreposição. Fontes compartilhadas não são endossos independentes. |
| Variantes Tripadvisor | As outras 14 linhas da matriz são domínios de país do Tripadvisor | Guardar a cobertura por domínio sem apresentar 14 publicações editoriais distintas. |
| Links para NOM | 24 registros, 21 URLs de origem únicas em 15 domínios; sete linhas com `lostlink=true` e uma com `nofollow` | Conferir disponibilidade e conteúdo antes de considerar qualquer fonte. Um registro perdido não comprova link atual. |

Os originais, schemas, parâmetros e a qualificação das fontes estão no
diretório privado `output/semrush-maximo-2026-10-25/api-gap-ads/`.
Esta documentação guarda a síntese; não publica as respostas brutas.

### Consumo desta extração

| Medida | Unidades API Standard | Condição |
| --- | ---: | --- |
| Consumo confirmado nas respostas | 2.160 | Metadata das duas chamadas com dados. |
| Reserva usada antes de conferir o saldo | 1.800 | Proteção para as três respostas sem metadata individual; foi tratada como reserva, sem atribuição de débito. |
| Exposição conservadora durante a coleta | 3.960 | Confirmado mais reserva; dentro do teto autorizado de 6.000. |
| Saldo observado na interface após a extração | 26.400 | A diferença desde 28.560 é 2.160, igual ao consumo confirmado nas respostas. |
| Estimativa conservadora antes da releitura | 24.600 | Registro do cenário que descontava também a reserva; a interface posterior confirmou 26.400. |

A reserva protegida de 4.900 unidades permanece separada. A cota do Maps usa
créditos próprios; seus pontos não devem ser somados às unidades API Standard.
A conferência do saldo fecha o consumo agregado desta rodada; a metadata
individual ausente dos três `no_data` continua registrada como limite da fonte.
Nenhuma nova chamada API paga é planejada para fechar esta documentação.

## Maps: posição por ponto da região

O Map Rank Tracker permitiu gerar uma campanha Free com uma palavra e
50 créditos iniciais. A consulta `restaurante frutos do mar` foi coletada
em uma grade 5×5 de 25 pontos para o negócio Sir Fisher, com a origem
conferida. Depois, onze pontos sobre a água foram desativados no editor,
preservando a localização do negócio, Av. Beira Mar, 3421, e o campo de raio
de 1,5 km. Uma segunda leitura usou os quatorze pontos terrestres restantes.
As coordenadas e a imagem originais foram guardadas; a ficha pública ficou
igual. Foram usados 25 + 14 créditos, com onze restantes. Não foi contratado
Basic ou Local Pro para essas coletas.

| Medida da grade de 25/10 | Resultado exibido |
| --- | --- |
| Ponto da origem conferido | Posição 1. Os outros pontos variam de 5 a 20+. |
| Avg. Rank | 14,2 no conjunto da grade. |
| Share of Voice | 2,6% na medida Semrush para essa palavra e conjunto. |
| Categorias do painel | Good 4%; Average 16%; Poor 68%; Out of Top 20 12%. |

| Recorte terrestre, 25/10 às 15h20 de Fortaleza | Resultado exibido |
| --- | --- |
| Pontos e origem | Quatorze pontos; posição 1 no ponto central conferido. |
| Avg. Rank | 16,5 nesse conjunto. |
| Share of Voice | 2,79% nesse conjunto. |
| Categorias do painel | Good 7%; Average 0%; Poor 72%; Out of Top 20 21%. |

Os dois recortes usam a mesma consulta em uma data. A posição do ponto central
não representa Fortaleza inteira. O painel define Avg. Rank a partir dos
pontos, e Share of Voice como visibilidade relativa para a palavra; essas
medidas não são participação em vendas. Os valores 20+ permanecem truncados
na fonte e não foram convertidos em posição exata para refazer a média.
As geometrias são diferentes. As setas e diferenças exibidas pelo painel
entre elas não medem evolução de SEO. O segundo recorte ajuda a avaliar
deslocamento terrestre, preservando a limitação da amostra e do ponto de origem.

As capturas e DOMs ficam em `output/semrush-maximo-2026-10-25/ui/`, incluindo
`maps-sir-fisher-grade-dom.txt`, `maps-metricas-tour-dom.txt`, os arquivos
`maps-terrestre-*` e a imagem da grade. O contador de 812 avaliações desse snapshot não substitui a leitura
direta do Perfil da Empresa, que confirmou 813 na revisão anterior.

## Respostas de IA e fontes para distribuição

O Competitor Research foi guardado com o recorte Brasil, todas as plataformas
de IA, referência de 24/10 e três domínios: Sir Fisher, Illa Mare e NOM.
Foram capturados 25 temas em três páginas, 66 registros de prompts em sete
páginas e 109 domínios de fontes em onze páginas. Illa e NOM pertencem ao
mesmo grupo. Os temas amplos incluem assuntos e regiões sem aderência à casa;
os totais pedem seleção por local e intenção antes de orientar uma ação.

O Prompt Research reúne respostas históricas de plataformas e datas próprias.
O recorte brasileiro permite avaliar como elas apresentam aniversários,
refeições, bairros e passeios; os números do tema amplo incluem ruído e não
estimam turistas interessados no Sir Fisher. O resumo usa as 15 respostas
conferidas pelo link de origem e pelo cabeçalho de país, plataforma e pergunta:
cinco ChatGPT, cinco AI Overview, três Gemini e duas AI Mode, com datas de
15/09 a 19/10. O arquivo é `ui/prompt-restaurantes-respostas-conferidas.json`.
As capturas iniciais sem essa associação validada ficaram fora da análise.

Na resposta ChatGPT de 14/10 sobre restaurantes perto de atrações para quem
visita Fortaleza pela primeira vez, Sir Fisher aparece como opção em Meireles
para jantar após passeio na orla e para quem está hospedado na região. A
observação antecede a seção publicada hoje; ela apoia a pertinência da jornada,
sem demonstrar ganho causado pelo ajuste. A lista de fontes pertence à resposta
inteira e não foi convertida em atribuição de cada afirmação a um veículo.

As exportações CSV do Competitor Research e do Prompt Research falharam no
aplicativo. Os DOMs e tabelas derivadas foram preservados; esses arquivos não
são exportações nativas. O CSV nativo da aba Keywords do Maps foi recuperado
do download para cada recorte e conferido intacto, com recibo de tamanho e
hash: 194 bytes para os 25 pontos e 224 bytes para os quatorze terrestres.
São dois CSVs com métricas por palavra; eles não substituem as coordenadas
e imagens das grades.
A opção PDF do Maps pediu aceite de privacidade. O aceite não foi dado e
o PDF não foi gerado.

As respostas de aniversário consultadas citam matérias de 2021 e 2024 sobre
benefícios de outros estabelecimentos. Essas matérias não confirmam ofertas
vigentes nem autorizam cortesias no Sir Fisher. Sugestões de Varjota, música
ao vivo e madrugada também não mudam bairro, horário ou proposta da casa.

A cobertura atual do site já apresenta o almoço individual com seu horário,
cardápio para outras refeições, localização no Meireles, rota, aniversários
e caminhos por tamanho do grupo. A revisão dessas respostas não demonstrou
outra lacuna factual que justificasse ampliar as mudanças autorizadas.

As fontes exibidas pelas plataformas servem para avaliar distribuição futura
de informações públicas. Um link citado comprova presença naquele registro;
possível inclusão do Sir Fisher depende do recorte e do processo da fonte.
Nenhuma mensagem foi enviada a terceiros nem houve compra de inclusão.

### Páginas qualificadas para uma avaliação editorial futura

O coletor guardou dez páginas qualificadas, com origem, data disponível,
pertinência e limite. Elas não representam dez recomendações independentes.
A lista completa está em `api-gap-ads/fontes-qualificadas.csv` e `.json`.

| Fonte e recorte | Material factual que a casa já pode fornecer | Limite da oportunidade |
| --- | --- | --- |
| [Accor: refeições em Fortaleza](https://all.accor.com/a/pt-br/limitless/thematics/food-drink/os-melhores-restaurantes-de-fortaleza--onde-comer-bem.html) | Endereço, refeições, horários e URLs oficiais para a jornada de hotelaria | Sir Fisher ausente no texto conferido; sem data de atualização visível ou garantia de inclusão. |
| [IndicoMais: restaurantes com vista para o mar](https://indicomaisfortaleza.com.br/2026/04/04/restaurantes-com-vista-para-o-mar-em-fortaleza-7-opcoes-do-casual-ao-sofisticado/) | Localização na orla, cardápio e regra de reserva | Aderência ao tema, com Sir Fisher ausente no artigo lido. Generalizações sobre o sol se pôr no mar não devem ser copiadas. |
| [IndicoMais: pauta de executivo](https://indicomaisfortaleza.com.br/2026/08/20/nom-frutos-do-mar-lanca-novo-menu-executivo-com-opcoes-de-crustaceos-carnes-e-sobremesas/) | Sete opções individuais do executivo, dias úteis e exceção de feriados | Produto, formato e preços do concorrente permanecem próprios dele. A matéria não demonstra necessidade de mudar a oferta Sir Fisher. |
| [TV Nordeste Vip: eventos corporativos](https://tvnordestevip.com/nom-frutos-do-mar-aposta-em-eventos-corporativos-e-amplia-experiencias-gastronomicas-em-fortaleza/) | Faixa de 30–100 sentados, formatos atuais e confirmação da equipe | Existe pauta semelhante em outro veículo. O índice marcou link perdido, mas a leitura pública atual ainda contém o link ao NOM. |
| [Fortaleza Real Estate: guia em inglês](https://www.fortalezarealestate.com.br/invest-in-fortaleza/food-and-nightlife/) | Ficha pública PT/EN, cardápio e reserva com continuidade de idioma | Público imobiliário e links de restaurantes não comprovam turistas, tráfego ou retorno para a casa. |
| [Hotel Brasil Tropical: guia da Varjota](https://brasiltropical.com.br/674-2/) | Referência de como hotelaria orienta hóspedes sobre refeições | Artigo centrado na Varjota e sem data visível, com sinais de conteúdo antigo. Uma pauta Beira-Mar exige outro recorte; a localização da casa deve permanecer correta. |

Pautas encerradas de junho/setembro e diretórios com denominações antigas
foram guardados como referência. Qualquer abordagem, parceria ou pagamento
depende de instrução própria; não foi executado nesta rodada.

## Alertas do scanner de diretórios

A leitura gratuita do scanner local exibiu 36/38 entradas para corrigir.
Foram vistos doze diretórios; a expansão da lista completa falhou, portanto
as 38 entradas não foram auditadas individualmente. Três alertas de telefone
mostravam os mesmos dígitos do número oficial, com outra formatação. O alerta
de Instagram ausente também não comprova ausência da conta, já validada na
integração de leitura. Esses resultados não confirmaram erro cadastral que
justificasse alterar a ficha. Nessa leitura, não houve edição do Perfil da Empresa, adesão
ao trial de sincronização ou sincronização de diretórios. Fonte preservada:
`ui/listing-scan-dom.txt`.

## Como acompanhar as páginas com a coleta existente

| Página ou jornada | Leitura útil | Condição para interpretar |
| --- | --- | --- |
| Guia da Beira-Mar e orientação para hóspedes | Sessões de entrada, origem/mídia e dispositivo; ações `click_menu`, `click_maps` e `click_reservation` na página `/guia/beira-mar/`, com `cta_position=conteudo` | Nesta versão, a combinação separa os quatro links da seção de hóspedes dos botões finais `visita`. A coleta usa eventos existentes; é preciso conferir cobertura posterior. Clique ou resultado agregado da página não comprova efeito causal da seção. |
| Pôr do sol | Mesmas ações, com a base histórica identificada e janelas posteriores fechadas | Exposição informacional já foi observada. País ou cidade não comprovam visita ao restaurante; manter a informação útil e avaliar a passagem à oferta. |
| Almoço e restaurante | Consultas comerciais visíveis no GSC, sessões de entrada e ações até o formulário | Não somar variantes ou páginas para apresentar o total da propriedade. Mudanças nas tags e feriados afetam comparações. |
| Fish and chips PT/EN | Continuidade de idioma, acesso ao cardápio, rota e reserva, com origem externa preservada | O cardápio `?lang=en` oferece a interface em inglês e mantém canonical em `/cardapio/`. A rodada não cria uma rota EN separada para esse catálogo. |
| Reserva comum | Funil `form_kind=standard`, `reservation_confirmed` e comparecimentos já registrados com vínculo | Apresentar cobertura, datas futuras e estados sem desfecho. Clique em reserva, reserva criada e comparecimento são unidades distintas. |
| Eventos | Ações do configurador com os nomes e a cobertura que a coleta disponível comprovar | Solicitar proposta não equivale a contratar o evento. O plano não transforma esse fluxo em reserva comum. |

Usar janelas fechadas equivalentes e manter data, fuso, fonte e unidade de cada
indicador. Um diagnóstico pode comparar contagens e cobertura; atribuir ganho
à mudança exige observação posterior e condições que separem outras causas.
O proprietário mantém adiado o registro de clientes sem reserva. Nenhuma
tarefa nova de recepção ou salão foi criada.

## Arquivos para reutilizar depois do teste

O pacote desta rodada usa o nome
`output/semrush-maximo-2026-10-25/sir-fisher-semrush-extracao-adicional-2026-10-25.zip`,
com hash, tamanho, integridade e conferências no sidecar `.verificacao.json`.
O relatório e o plano acompanham as cópias saneadas dos dados.

As respostas API, as tabelas por domínio/URL, os parâmetros e o ledger
permitem retomar a pesquisa sem consultar a API paga outra vez. Os DOMs,
derivados, CSVs nativos do Maps e imagens das grades preservam origem e recorte.
Arquivos originais permanecem na pasta privada; dados brutos e credenciais
ficam fora do Git. O acervo anterior e seus ZIPs conservam os mesmos arquivos.

## Fechamento da rodada

A coleta Gap/Ads terminou após a quinta chamada. Os painéis de IA e os dois
recortes do Maps foram preservados com suas definições, e a publicação do site
foi conferida. O plano pago continua preparado para revisão: objetivo, economia,
teto e medição na conta ainda precisam ser definidos ou confirmados antes de
lançar. Abordagens editoriais e novas ofertas não foram executadas.

Os ganhos demonstrados são a melhoria de apresentação e de orientação nas
páginas publicadas, os recortes locais antes indisponíveis e a retenção dos
dados para uso posterior. Vendas, comparecimentos adicionais e evolução de
ranking causada pelas mudanças exigem observação própria após esta data.

## Uso final em 27/10/2026

Antes do cancelamento, as cotas restantes foram usadas. Evidências privadas em
`output/semrush-final-2026-10-27/`, na raiz do workspace, com `LEIA-ME.md`.

- **API Standard:** saldo de 26.400 a 0 unidades, conferido na tela de
  assinatura. Há 21.080 unidades com resposta salva em 42 consultas: 35 com
  dados e 7 `no_data` sem débito. Outras 120 foram de um teste. 5.200 unidades
  foram consumidas sem dados salvos, porque a biblioteca MCP interrompeu o
  primeiro lote antes da gravação. Quatro dessas cinco consultas foram refeitas.
- **Banco de palavras-chave:** 415 palavras com volume, CPC, dificuldade,
  intenção e tendência. Destas, 320 são de restaurante ou turismo e 227 citam
  Fortaleza ou bairros. As de mais volume são turísticas: o que fazer em
  Fortaleza (8.100), Jardim Japonês e Beira Mar.
- **Google:** os 20 primeiros resultados para cinco buscas turísticas e de
  restaurantes não incluem o sirfisher.com.br. Os primeiros lugares são de
  TripAdvisor, guias de viagem, imprensa local e Instagram.
- **Prompt Tracking:** cota de 50/50, com 26 perguntas genéricas em português e
  8 em inglês. Em 27/10, duas perguntas em português deixaram de citar a casa:
  almoço com preço e jantar com cardápio. As respostas usaram imprensa local e
  TripAdvisor. As 4 em inglês continuaram citando a casa.

A próxima cobrança exibida era 31/10/2026. A leitura das novas perguntas
depende das coletas diárias até o cancelamento.

## Ajustes no site a partir das leituras de 27/10

Commit do site
[`35578bb`](https://github.com/sirfisherfc/site/commit/35578bb), publicado e
conferido: as 10 URLs públicas responderam HTTP 200 com o mesmo conteúdo do
commit. O sitemap foi reenviado ao Search Console sem erros.

- **Eventos:** a página ganhou texto indexável sobre confraternização de fim
  de ano, evento de empresa e aniversário. Inclui os passos até a proposta, o
  caminho por tamanho de grupo, perguntas frequentes e schema FAQPage.
  Usa só regras já publicadas no configurador.
- **Jantar:** a home não usava a palavra. Descrição, abertura, horário e uma
  pergunta frequente foram ajustados, em português e inglês.
- **Jardim Japonês:** página nova em `/jardim-japones/`. Usa dados da Prefeitura
  (Jusaku Fujita, 1.900 m², reforma de 9/7/2026) e a data de inauguração do
  Conexão 085. O horário é o mesmo do guia. Há links do guia, da home e da
  página de rota.
- **Pôr do sol:** "hoje" entrou no título, no H1, no rótulo e em uma pergunta
  frequente. A página já calculava o horário do dia.
- **Jardim Japonês, segunda versão:** no site
  [`49c9932`](https://github.com/sirfisherfc/site/commit/49c9932), a página
  ganhou cinco fotos do Wikimedia Commons sob CC BY-SA 4.0, com autor e
  licença em cada legenda. Também ganhou layout de desktop em `jardim.css` e
  a faixa "Atravesse a avenida" com fotos da casa e botões de reserva,
  cardápio e rota. No celular, uma barra fixa leva ao cardápio.
- **TripAdvisor:** a ficha `d23922740` ainda aparece como "Barra Sol Sir
  Fisher". A URL entrou no `sameAs` do Restaurant. A correção do nome e dos
  dados depende do navegador conectado ao TripAdvisor.
- **Cloudflare:** `/jardim-japones/` ainda não está nas exceções "Robos IA:
  leitura das paginas publicas" e da Semrush. O token da API não lê as regras,
  e a inclusão desse caminho depende da UI.

Validações: 116 testes de atribuição e CTAs, com o adaptador Node para os
testes Deno, e 4 do pôr do sol. CSP e console sem erro em 7 páginas.
Acessibilidade sem problema em celular e desktop, nos temas claro e escuro.
Os três verificadores do CI passaram, e o Pages concluiu a publicação.

