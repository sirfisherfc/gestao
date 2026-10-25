# Semrush: melhorias publicadas e acompanhamento local

Atualizações posteriores ao acervo estão no
[adendo da rodada adicional](#rodada-adicional-em-2510-após-o-fechamento-do-acervo).
O ZIP entregue conserva o fechamento anterior como snapshot.

Referência: 25/10/2026, America/Fortaleza. O site recebeu links mais claros
para almoço e cardápio, orientação de rota conforme a origem, regra visível
de pets e canais de grupos e eventos. As mudanças foram publicadas e
conferidas no domínio público, incluindo os commits
[`5918c99`](https://github.com/sirfisherfc/site/commit/5918c99) e
[`2b04523`](https://github.com/sirfisherfc/site/commit/2b04523).

| Resultado atual | Estado confirmado |
| --- | --- |
| Auditoria depois das correções | Site Health 96, AI Search Health 99, zero erros e 20 avisos, em 18 páginas. |
| Google local | Fortaleza, celular, português do Brasil e 40 termos configurados, com coleta concluída. Visibilidade Semrush 13,97%, oito termos no Top 10 e cinco no Top 3; há uma única data, 25/10. |
| ChatGPT local | Coleta concluída dos doze prompts em português para Fortaleza; o widget mostrou nove menções. As métricas e divergências da tela estão qualificadas ao fim do documento. |
| Google com recursos de IA | Inclusão padrão confirmada na propriedade de domínio. O relatório histórico tem 2.672 impressões até 23/10, anteriores às mudanças de 25/10. |
| Dados portáteis | Ledger atual com 79 relatórios; o ZIP da versão API preserva 78 relatórios. Backups e derivados posteriores da UI ficam separados, com filtros e datas próprios. |

Os valores de visibilidade e posição são medidas do conjunto acompanhado.
Uma data fornece uma linha de base; resultados comerciais exigem os registros
automáticos já existentes. A linha de base de Google, reservas e atendimento
continua em `REVISAO_SEO_LOCAL_CONVERSAO_2026-10-25.md`.

O [fechamento da extração](#extração-final-antes-do-cancelamento) contém os sete
pontos pedidos, a reformulação e o consumo. A
[conferência do painel](#conferência-posterior-no-painel) registra métodos e
limites. As seções seguintes preservam a primeira extração como histórico.
Nenhuma tarefa de acompanhamento manual foi atribuída ao proprietário.

## Histórico da primeira extração por API: 49 relatórios

| Entrega | Conteúdo e limite |
| --- | --- |
| Biblioteca de pesquisa | 49 requisições de relatório, 676 linhas originais e 593 observações deduplicadas. |
| Palavras e bases | 300 pares de palavra/base, correspondentes a 298 termos exatos entre BR, US e UK. Variantes próximas e bases não devem ser somadas para estimar mercado. |
| Resultados e referências | 191 URLs de resultados, fontes e destinos; 172 aparecem em SERPs, dez são fontes de backlinks. Os conjuntos se sobrepõem. |
| Oportunidades | Oito ações por URL, com evidência, confiança, dependência e forma de conferir. |
| Configuração preparada | 40 palavras selecionadas para Google/Fortaleza/celular e 16 prompts com intenção e fatos a conferir. O estado encontrado depois consta no fechamento final. |
| Guias e concierge | Dez URLs encontradas; seis páginas conferidas diretamente. Há páginas históricas e referências confirmadas só pela API. |
| Entrega para o proprietário | Planilha privada em `output/semrush-3-dias/sir-fisher-semrush-acervo-2026-10-25.xlsx`, na raiz do workspace. |

Os originais, schemas, parâmetros e derivados ficam no diretório ignorado
`site/_materiais/revisao-seo-2026-10-25/semrush/`. `LEIA-ME.md` explica os
arquivos e `snapshot-final.json` registra os hashes da versão entregue. Os
CSV de `consolidado/` podem ser usados após o teste, sem outra consulta paga.

## Decisões da primeira extração: histórico

| Prioridade / página | Evidência observada | Ação nesta rodada |
| --- | --- | --- |
| Almoço executivo | Nos inventários consultados, Sir Fisher aparece em 14 para almoço executivo Fortaleza; Floresta em 4. O volume desse termo varia de 110 a 140 entre os relatórios. | Preservar URL, title e preços. Explicitar a refeição individual na abertura e no link do guia, com os dias e horários confirmados. |
| Home e guia da Beira Mar | Home entre 4 e 6 em variações comerciais; guia entre 26 e 33 em alguns recortes. A SERP também tem guias e perfis sociais. | Manter os papéis das duas páginas e os links úteis. Os dados atuais não estabelecem canibalização. |
| Home / cardápio | A home aparece em 12 para restaurante frutos do mar Fortaleza e em 15 para restaurante Meireles Fortaleza nas SERPs consultadas. | Revisar a apresentação das ofertas existentes e acompanhar a procura local antes de criar outra página. Alterações no catálogo seguem o pipeline editorial. |
| Jornada EN | Há posições para variantes near me na base BR; as consultas com Fortaleza em inglês têm cobertura pequena nas três bases. | Manter cardápio e reserva em inglês; corrigir caminhada genérica, referência a primeira fila, conversão em dólares sem data e retorno involuntário à home PT. |
| Eventos | O HTML tinha title e H1 sem localização; a base Semrush não retornou dados da URL. | Identificar Beira Mar/Fortaleza e a faixa de 30–100 sentados, preservando o configurador e a confirmação da equipe. A confiança é alta para clareza; o ganho de busca exige observação. |
| Réveillon | A base externa privilegia temporadas antigas; o GSC próprio registra impressões da página atual. | Preservar a página de 2027 e a distinção de pré-reserva. Conferir os próximos dados com os fatos atuais da oferta. |
| Guias / concierge | ViajaLi e Maxmilhas citam Illa Mare; Sir Fisher não foi encontrado no HTML consultado. Partiu Fortaleza reúne informações de restaurantes na jornada de concierge. | Preparar os dados públicos da unidade e avaliar os canais. Contato com terceiros e pagamento continuam dependentes de instrução específica. |
| Pôr do sol | O termo amplo concentra volume informacional; a página foi reformulada em 20/10. | Manter a entrega e medir as ações de visita nas janelas definidas. |

Fontes de concorrência foram recortadas por negócio e ocasião: Illa Mare,
URL da unidade Coco Bambu Beira Mar e página executiva do Floresta. As
métricas da rede nacional ou de uma plataforma de cardápios não representam
uma unidade local. Dos 30 primeiros domínios de referência de Illa, 23 eram
variantes do Tripadvisor; 358 domínios conhecidos não significam 358 matérias
editoriais independentes.

Páginas públicas conferidas:
[ViajaLi](https://www.viajali.com.br/restaurantes-fortaleza/),
[Maxmilhas](https://blog.maxmilhas.com.br/destinos/fortaleza) e
[Partiu Fortaleza](https://www.partiufortaleza.com.br/concierge).
O acervo registra a data e o limite de cada consulta, inclusive páginas que
responderam com erro ou tratam de uma programação antiga.

## Recortes da primeira extração e sua interpretação

BR, US e UK são bases nacionais. A pesquisa não controla Fortaleza ou aparelho.
Os timestamps de linhas orgânicas variam entre agosto e outubro; as SERPs
não informaram a data do snapshot. Posições, volumes e tráfego são estimativas.

No complemento GSC de 25/07–22/10, best fish and chips near me teve 569
impressões e zero cliques na propriedade: 565 em desktop Brasil e quatro em
celular Brasil. O recorte por página tem outra agregação: a página EN de fish
teve 154 impressões desktop nessa consulta, e a home também apareceu. Não
somar esse recorte ao total da propriedade nem atribuir as 569 à página EN.
Brasil e near me ainda deixam a cidade e a condição de turista desconhecidas.

Os recortes próprios ficam em `gestao/tmp/semrush-3-dias/gsc-recortes.json`.
O script só consulta GSC e reaproveita o cache. A coleta manual de origem
de clientes no salão permanece adiada por decisão do proprietário.

## Plano inicial de uso dos três dias

Este plano foi preparado antes da conexão do navegador. Os estados da tabela
descrevem aquele momento; a execução posterior e o checklist de 26/27 estão
registrados ao fim do documento.

| Etapa | Trabalho | Estado |
| --- | --- | --- |
| Dia 1: 25/10 | Ampliar a pesquisa, guardar originais e derivados, criar planilha, selecionar termos/prompts e implementar os ajustes de maior confiança. | Pesquisa concluída; validação e publicação registradas no fechamento desta rodada. |
| Dia 2: 26/10 | Configurar um projeto do Sir Fisher, Site Audit e acompanhamento local, conforme as cotas efetivamente disponíveis. Ler a primeira execução e preparar correções concretas. | Configuração autorizada e preparada; depende do navegador conectado ao painel. |
| Dia 3: 27/10 | Rever dados novos de auditoria e acompanhamento; concluir correções viáveis e exportar configurações, resultados e decisões para uso após o teste. | Preparado; depende das execuções anteriores. |

O painel deve mostrar as cotas e eventuais projetos existentes antes de salvar.
Configuração proposta: projeto Sir Fisher Fortaleza, domínio
`sirfisher.com.br`, Google/Fortaleza/celular. Registrar o idioma do motor;
um alvo EN separado depende do que o plano incluir. Site Audit começa com
até 100 URLs públicas no host `www.sirfisher.com.br`; excluir administração,
links de cancelamento, tokens e parâmetros de atribuição.

Os 16 prompts distinguem descoberta e conferência factual. Registrar plataforma,
local, idioma, data e fontes citadas; usar apenas recursos incluídos. Se a
plataforma oferecer somente Brasil, guardar esse recorte como nacional, mesmo
quando a pergunta menciona Fortaleza. Brand Performance usa o domínio próprio
quando o recurso informado estiver confirmado no painel.

A documentação da Semrush descreve
[acompanhamento diário de prompts](https://www.semrush.com/kb/1503-prompt-tracking)
e as [fontes e frequências dos dados de IA](https://www.semrush.com/kb/1607-semrush-ai-visibility-data).
Três dias fornecem uma linha de base curta para acompanhar e conferir a
ferramenta. Efeito sobre visitas exige o acompanhamento comercial já definido.
Esta rodada não criou um agendamento automático de trabalho no Codex.

## Acesso e consumo no primeiro fechamento

A credencial fornecida pelo proprietário foi guardada somente em arquivo local
ignorado pelo Git. A autenticação no endpoint oficial funcionou: initialize e
tools/list retornaram 14 ferramentas, sem relatório pago. A consulta gratuita
de saldo Standard respondeu HTTP 400; o saldo MCP continua sem verificação.
Não incluir a chave em comandos, documentação, planilha ou exports.

O conector expõe leitura de projetos, auditorias e acompanhamento. A
[documentação do MCP](https://developer.semrush.com/api/v3/introduction/semrush-mcp/)
confirma esse limite. As tentativas iniciais de abrir navegador integrado,
Chrome e Edge retornaram indisponibilidade. A autorização do proprietário
para configurar já existia. O Chrome ficou disponível em uma etapa posterior;
Codex da sessão principal passou a conferir o painel. As instruções de conexão
estão na [documentação da extensão](https://learn.chatgpt.com/docs/chrome-extension).

| Prestação de contas | Unidades |
| --- | ---: |
| Saldo inicial informado, já descontada a listagem antiga | 49.900 |
| Débito confirmado, incluindo as 720 da triagem | 11.650 |
| Reserva máxima para sete respostas sem metadata de débito | 2.600 |
| Exposição conservadora desta rodada | 14.250 |
| Saldo final estimado conservador | 35.650 |
| Saldo estimado se respostas sem dados não debitaram | 38.250 |
| Reserva do proprietário preservada | 4.900 |
| Margem conservadora restante do teto total de 45.000 | 30.750 |

O custo esperado das sete respostas sem dados é zero segundo a
[documentação oficial de saldo e consumo](https://developer.semrush.com/api/v3/get-started/api-units-balance/).
A reserva evita tratar esse valor como débito confirmado antes de conferir
saldo ou Query Log. A maior exposição prevista antes de um lote foi 14.340,
dentro do teto de 15.000 para diagnóstico. Limites liberados após respostas
menores não são débitos. `consumo.json` permanece como registro único por chamada.

Assinatura, recorrência e gastos de campanha permanecem preservados. A decisão
sobre US$199 mensais deve considerar os recursos efetivamente usados nesta
janela. Conferir cobrança até 30/10, usando 31/10 como referência conservadora;
a divergência anterior com 01/11 ainda não tem hora, fuso ou causa confirmados.

## Fechamento técnico da primeira etapa

Os ajustes de almoço/guia, EN e eventos usam as páginas existentes. Preços em
reais, catálogo, capacidades e regras de reserva foram preservados. A situação
de testes, commits e publicação consta no registro de entrega desta rodada.
O plano e os textos de contato preparados não constituem envio a terceiros.

O site foi enviado no commit
[`f2614fb`](https://github.com/sirfisherfc/site/commit/f2614fb).
Passaram os 108 testes Deno de CTAs, atribuição e carregamento de marketing,
os verificadores de CSP/assets/CSS embutido e 30 casos de navegador das cinco
páginas em 320/390/1440 px, nos temas claro e escuro. Dez percursos de teclado
também passaram. O navegador bloqueou coletas externas; nenhuma reserva ou
proposta real foi criada. Os workflows de assets e publicação passaram. Seis
arquivos públicos conferem com o commit; dez casos no domínio publicado,
em celular e desktop, também passaram.

A planilha tem oito abas, 11 tabelas com filtros e 783 links. A conferência
reabriu o XLSX e comparou os dados com as fontes salvas; não encontrou erros
de fórmula. As prévias foram revisadas. A interface do Excel não foi testada.

## Conferência posterior do site publicado

O objetivo confirmado pelo proprietário é melhorar o site, o SEO e a presença
em respostas de IA. A pesquisa serve para escolher alterações no site e
conferir o efeito depois da publicação.

O commit `0af3d6d`, incorporado depois da primeira entrega, acrescentou o
cardápio ao HTML inicial, com pratos, preços e H1. Também completou o endereço
do organizador no Event do Réveillon, ajustou o arquivo robots, publicou
`llms.txt` e acrescentou links para as regras de reserva. Esses ajustes foram
conferidos no domínio público; os dois workflows desse commit passaram.

Em nova leitura das 13 URLs do sitemap, todas responderam HTTP 200, declararam
a própria canonical e tinham um H1 e um title. Não apareceu `noindex` nas metas
ou cabeçalhos, e os blocos JSON-LD passaram no parse. Essa verificação cobre
acesso HTTP, marcação básica e sintaxe; indexação e elegibilidade dos dados
estruturados exigem as ferramentas dos buscadores. A evidência privada está em
`site/_materiais/revisao-seo-2026-10-25/seo-ia-publicado-0af3d6d.json`.

A configuração de acesso ao painel descrita acima refere-se à sessão Codex.
O novo commit registra correções do Site Audit feitas em outra execução.
O ganho de posição e as citações em respostas de IA depois das mudanças
continuam sem medição nesta rodada.

A conferência do cardápio comparou os textos públicos dos 78 itens e a
orientação de alergia antes e depois do JavaScript: os textos são iguais.
O aviso editorial permanece restrito à prévia, conforme decisão de 07/10.
A suspeita inicial de que faltava uma ressalva pública foi descartada após
ler essa regra e comparar os dois caminhos. Esta revisão preservou o código
do site; prerender, assets e CSP passaram nas verificações existentes.

### Controles de IA conferidos na documentação oficial

O Google exige indexação, permissão de snippets e inclusão efetiva no controle
**Configurações > IA generativa na Pesquisa**, no Search Console. Esse último
valor da propriedade Sir Fisher foi conferido na etapa posterior de painel,
registrada ao fim deste documento. A documentação informa inclusão como
padrão, com possibilidade de herança da propriedade superior.
[Controle oficial](https://support.google.com/webmasters/answer/16908024?hl=en).

O robots público permite `OAI-SearchBot` pelo grupo geral e bloqueia `GPTBot`.
A OpenAI documenta permissões independentes para busca e treinamento; falta
conferir o acesso dos IPs oficiais pelos controles da CDN.
[Rastreadores OpenAI](https://developers.openai.com/api/docs/bots).

O bloqueio gerenciado de `Google-Extended` limita treinamento e grounding no
Gemini Apps/Vertex. Segundo o Google, esse controle não altera inclusão ou
ranking na Pesquisa. A política foi preservada.
[Rastreadores Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended).

O Google informa que `llms.txt` não participa da visibilidade ou classificação
na Pesquisa. O arquivo continua como resumo auxiliar. As ações prioritárias
são melhorar o acesso e as informações reais das páginas, conferir os controles
dos buscadores e medir as aparições.
[Guia oficial para IA na Pesquisa](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).

## Extração final antes do cancelamento

O proprietário pediu concluir as melhorias do `www` e aproveitar o acesso pago
para guardar informações úteis. A execução preservou a assinatura e a política
de treinamento. Nenhuma mensagem foi enviada a terceiros, nenhuma campanha
de mídia foi alterada e a coleta de clientes sem reserva no salão continua adiada.

### Problema, perguntas e critérios

| Ponto pedido | Conclusão que orienta a execução |
| --- | --- |
| Problema real | Aumentar a descoberta comercial e facilitar escolha, rota e reserva. Nas janelas comparáveis de 28 dias, cliques GSC passaram de 123 para 261, reservas públicas criadas ficaram em 25 e rotas GBP passaram de 421 para 380. Esses agregados não estabelecem causalidade entre canais. |
| Considerações | O site já cobre as principais ofertas. Usar páginas existentes, preservar preços e regras e distinguir as bases nacionais da pesquisa localizada. A auditoria inicial precedia as correções; a nova execução posterior mostrou Site Health 96, AI Search Health 99 e zero erros. |
| Perguntas | Quais intenções ainda chegam a uma página inadequada? Jantar, domingo e grupos correspondem à oferta real? Quais fontes editoriais ajudam quem já planeja visitar a região? Quais condições de acesso e indexação continuam sem prova? |
| Critérios | Corrigir fatos, acesso e ligações entre páginas. Uma boa entrega exige mudanças publicadas e testadas, export portátil com origem, período e limites e pendências reais registradas. Consultas pagas precisam mudar uma decisão, usar cache e respeitar o teto; parar quando a pergunta estiver respondida. |
| Esquecimentos | A orientação fixa de caminhada ainda existia em português; havia dois controles do robots gerenciado; eventos e reservas têm situação de indexação diferente das páginas já indexadas. A URL Guanabara encontrada na SERP mudou de destino. |
| Premissas | A capacidade informada vale para hoje. Preservar as regras de cada jornada. São premissas frágeis deduzir visitas ou receita do tráfego, identificar Fortaleza ou turistas por BR/near me, garantir citações por llms.txt ou configuração e atribuir efeito às mudanças com três dias de dados. Essas conclusões exigem observações próprias e condições que a amostra atual não fornece. Uma interface EN funcional também deixa a indexação separada por confirmar. |
| Informação faltante | Acesso de IPs reais pela CDN e efeito comercial após a publicação. O controle de inclusão da propriedade de domínio foi conferido depois. Os dados automáticos existentes serão usados com seus limites; não foi criada tarefa para recepção. |

O objetivo reformulado foi concluir uma extração finita das informações que
ainda podem mudar o site, aplicar correções verificáveis nas páginas existentes
e guardar fontes, datas e limites para uso posterior. O resultado esperado é
o site corrigido e um acervo portátil. A pesquisa não promete citações em IA
ou aumento de clientes dentro da janela do teste.

### Melhorias publicadas e caminhos mantidos

| Entrega | Estado e conferência |
| --- | --- |
| Ofertas locais e EN | `f2614fb`: almoço individual, links do guia e regras de grupos; localização dos eventos; jornada EN sem câmbio sem data ou promessa de primeira fila. |
| Cardápio no HTML inicial | `0af3d6d`, de Claude: 78 itens, H1, endereço do organizador do Réveillon, links para regras de reserva e resumo auxiliar `llms.txt`. |
| Robots próprio | `5e94b8e`, de Claude: lista de rastreadores no arquivo do site. A confirmação da resposta pública está abaixo. |
| Ligações e rota | `5918c99`: link permanente da foto do executivo, acesso contextual ao cardápio no guia e orientação de caminhada conforme o ponto de partida, no texto PT e no FAQ. |
| Pets e grupos | `2b04523`: regra existente de pets nas mesas externas passou ao texto visível; home e eventos indicam os canais de cada faixa de grupo. Não houve mudança de capacidade ou política. |

Os commits `5918c99` e `2b04523` tiveram workflows aprovados; as URLs alteradas
responderam HTTP 200 e o HTML público coincidiu com o local. A publicação
é verificável. Ganho de busca e efeito comercial posterior continuam sem
medição. A ficha pública para eventual uso editorial foi preparada em
`output/semrush-3-dias/ficha-publica-sir-fisher-2026-10-25.json`, sem duplicar
preços e sem envio a terceiros.

### Estado técnico conferido

- A leitura de índice cobre as 13 URLs do sitemap: dez tiveram `PASS`, com
  canonical própria; `/eventos/` e `/reservas/` estavam detectadas e ainda não
  indexadas; `/privacidade/` ainda não era reconhecida. O último rastreamento
  varia por URL e precede parte das alterações. Esse estado não comprova a
  indexação das novas versões nem transforma baixa cobertura Semrush em
  ausência de procura.
- A auditoria Semrush terminou em 25/10 às 02:07:46 de Fortaleza, antes de
  `f2614fb`, `0af3d6d` e `5e94b8e`. Seus dois erros, 24 avisos e duas notas
  descrevem a versão anterior. Os detalhes devolvidos apontaram robots,
  endereço do organizador e H1 do cardápio; as duas últimas correções já
  apareceram no HTML publicado. O resultado posterior foi obtido na etapa
  de painel registrada abaixo.
- Às 03:02:59 de Fortaleza, GET autorizado de Bot Management retornou
  `is_robots_txt_managed=false` e `bot_preference_sync_enabled=false`.
  O robots público respondeu 200 e coincidiu com o arquivo do site, sem
  diretiva `Content-Signal`; esse nome permanece apenas no comentário.
  A propagação foi confirmada. A leitura atual mostrou treinamento
  `disallow` e `ai_bots_protection=only_on_ad_pages`. O recado de Claude
  registra que as demais opções foram preservadas; este GET posterior
  comprova o estado atual, sem substituir uma comparação antes/depois.
- O comando `robots` preparado por Claude preserva os dois campos. A revisão
  Codex passou a exigir sucesso no PUT, no GET posterior, nos dois alvos e
  na purga. Uma alteração inesperada em outro campo interrompe a conclusão.
  Onze testes offline cobrem recusas, resposta incompleta, alvos divergentes,
  política inesperada, purga, simulação, repetição e rollback. O workflow
  `quality` executa esses testes. Esta revisão não escreveu no Cloudflare.
- O cardápio tem 78 itens no HTML inicial. Com `?lang=en`, o HTML inicial
  continua PT; após JavaScript, a interface e os itens mudam para EN e a
  reserva mantém o idioma. A canonical continua `/cardapio/`, sem alternate
  EN no head. Essa arquitetura foi descrita como interface traduzida;
  nenhuma rota nova foi proposta nesta etapa.
- Restaurant em home PT, EN e Conheça mantém telefone, endereço, geo,
  horários, cozinha e faixa de preços coerentes. Menu e reserva EN usam
  queries de idioma intencionais. O organizador do Réveillon tem o mesmo
  endereço. O parse dos dados estruturados não garante rich results.

### Busca e respostas de IA

O proprietário orientou aproveitar o máximo útil pelas APIs disponíveis.
Depois instalou a extensão e disponibilizou o Chrome; Codex da sessão
principal passou a operar o painel. Não foi atribuída ao proprietário uma tarefa de configurar tracking
ou executar prompts manualmente. Na fase de API, AI Visibility, Brand
Performance e relatórios próprios de ChatGPT/Gemini não ficaram comprovados
pelos recursos acessíveis. Esse limite de acesso não demonstra ausência do
restaurante nesses serviços.

A extração por API encontrou uma campanha existente com 48 palavras, Google,
Brasil, idioma português e desktop, com resultado de 25/10. Esse recorte
difere do acompanhamento Fortaleza/celular preparado inicialmente. Nele, o
domínio apareceu marcado como fonte em AI Overview para `por do sol fortaleza`
e `por do sol hoje fortaleza beira mar`, ambos com destino `/por-do-sol/`.
Essas duas observações não são resultados de ChatGPT ou Gemini nem ganho
atribuível às mudanças desta rodada. Consultas que apenas dispararam AIO,
sem o domínio marcado como fonte, não foram somadas. O Organic Research
devolveu uma linha AIO em snapshot anterior para a primeira consulta;
os dois relatórios mantêm fontes e tempos separados.

A API pública do Search Console documenta Search Analytics, Sitemaps, Sites e
URL Inspection. `Sites` retorna URL e nível de acesso; não foi encontrada
uma rota documentada para ler o controle de IA generativa. A conferência foi
feita pelo painel oficial na etapa posterior, com o escopo registrado abaixo.
[Referência API](https://developers.google.com/webmaster-tools/v1/api_reference_index),
[controle de inclusão](https://support.google.com/webmasters/answer/16908024?hl=en).

O relatório dedicado de IA mostra impressões de AI Overviews e AI Mode por
página, país, aparelho e data, com datas em Pacific Time. Os totais por
propriedade e os agrupamentos por página têm agregações diferentes. Há
exportação própria no painel. A consulta comum `searchAppearance` de
25/09–22/10 retornou `rows[]`; isso não demonstra ausência de IA e não
substitui o relatório dedicado. A API comum não documenta um tipo GenAI.
[Relatório oficial](https://support.google.com/webmasters/answer/16984139?hl=en),
[Search Analytics](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).

OAI-SearchBot e Googlebot continuam permitidos pelas diretivas recebidas;
GPTBot e Google-Extended continuam bloqueados. As permissões de busca e
treinamento têm controles próprios. O arquivo `llms.txt` permanece auxiliar,
com os limites documentados acima. Nenhum teste com User-Agent simulado foi
tratado como acesso proveniente de IP real de buscador.

### Fontes e próximas ações condicionadas

O [guia geral Accor](https://all.accor.com/a/pt-br/limitless/thematics/food-drink/os-melhores-restaurantes-de-fortaleza--onde-comer-bem.html)
foi conferido e acrescenta uma fonte ligada à hotelaria. O texto retornado
separa Beira-Mar, almoço, jantar e frutos do mar e não mencionou Sir Fisher.
A matéria de lagosta da mesma rede exige produto aderente confirmado para
justificar uma proposta. A antiga URL Guanabara sobre restaurantes românticos
agora redireciona a um
[guia geral de Fortaleza](https://viajeguanabara.com.br/blog/o-que-fazer-em-fortaleza-ce/).
Não será tratada como guia especializado atual. Nenhuma inclusão ou contato
foi realizado por esta revisão.

O brief dos sete pontos, a matriz por página, fontes atuais e evidências
técnicas ficam em `output/semrush-3-dias/`, fora dos três repositórios.
O catálogo inicial da planilha permanece como versão congelada; os dados
novos pertencem à extração final, com fontes e datas próprias.

### Acervo portátil da coleta por API

O consolidado final está em
`site/_materiais/revisao-seo-2026-10-25/semrush/extracao-final-20261025/acervo-final/`.
Ele reúne 1.014 observações brutas de pesquisa e tracking, 867 observações
deduplicadas, 388 pares termo/base e 379 termos exatos, além de 45 linhas
de inventário de páginas e 269 URLs no corpus. As contagens têm definições
próprias; bases e variantes não foram somadas como mercado local.

Os CSVs `indice-relatorios`, `keywords`, `observacoes-deduplicadas`,
`tracking-48`, `urls-inventario` e `fontes-qualificadas` permitem reutilizar
os dados sem outra consulta paga. As 21 fontes qualificadas incluem 17 páginas
conferidas diretamente. Originais, esquemas, parâmetros, custos e decisões
acompanham os derivados. A versão API foi congelada antes dos resultados
novos do painel; esses resultados mantêm fontes e filtros separados.

A conferência independente validou tamanho e SHA256 dos 153 arquivos listados
no manifesto. As contagens dos CSVs e a soma dos valores de consumo das
70 respostas com metadata também bateram. O SHA256 de `manifesto.json` é
`56baf5a8edb30f28f4a682657a35a557d210750be834e4a8b5fa004b38dee6fb`.
O acervo é privado, ignorado pelo Git; a documentação versionada registra os
resultados saneados. Nenhuma credencial foi incluída nos exports.

Uma cópia portátil fica em
`output/semrush-3-dias/sir-fisher-acervo-semrush-api-2026-10-25.zip`:
386.990 bytes, 154 membros, correspondentes aos 153 arquivos e ao manifesto.
O SHA256 é
`dbe294a11089bf1120579efc60152412302ee264f4604783d15f5ce73a20f140`.

O pacote principal é
`output/semrush-3-dias/sir-fisher-acervo-completo-2026-10-25.zip`, reunindo este
relatório, o snapshot API histórico preservado e os dados da UI com seus
originais e derivados. O sidecar
`sir-fisher-acervo-completo-2026-10-25.verificacao.json` registra tamanho,
SHA256 e verificações finais. O hash do próprio pacote fica no sidecar.

### Consumo e saldo confirmados no fechamento

O snapshot e o ZIP preservam as 78 requisições da coleta por API: 49 da primeira
coleta, sete da retomada de Site Audit e 22 da extração final, com consumo
confirmado de 20.970. Depois, uma leitura de metadata de campanhas para apoiar
o painel acrescentou 100 unidades. O ledger canônico registra agora 79
requisições, mantendo essa fase separada. As validações gratuitas de
autenticação ficam registradas à parte. Esta conferência dos valores não
fez nova chamada paga.

| Fechamento cumulativo | Unidades |
| --- | ---: |
| Saldo inicial informado, com a listagem antiga já descontada | 49.900 |
| Consumo confirmado por metadata | 21.070 |
| Saldo atual observado na UI | 28.830 |
| Reserva do proprietário preservada | 4.900 |
| Espaço restante pelo teto total de 45.000 | 23.930 |

A tela Subscription info confirmou o saldo 28.830, que confere com
49.900 menos 21.070. A incerteza sobre o saldo total atual foi resolvida.
O ledger preserva o máximo histórico de 2.900 reservado para oito respostas
sem metadata, sem atribuir um débito individual a cada uma. A projeção anterior
de saldo 25.930 permanece como histórico; essa reserva não foi novamente
descontada do saldo observado. A margem não foi consumida para preencher cota.

O painel confirmou próxima cobrança em 31/10/2026, US$199, e recorrência ativa.
Assinatura e recorrência foram somente lidas. A divergência anterior com
01/11 fica resolvida pela informação atual da UI. O pedido de aproveitar os
dados antes do cancelamento não foi tratado como execução de cancelamento.
As evidências saneadas são `assinatura-estado-resumo-dom.txt` e
`assinatura-limites-resumo.txt`, na pasta de painel.

Os limites exibidos foram 136/500 palavras, 4/5 sites, 54/100.000 páginas,
12/50 prompts e Brand Performance 1/1. Essas cotas descrevem a conta;
não foram preenchidas apenas por estarem disponíveis.

## Conferência posterior no painel

### Inclusão na IA generativa do Google

No Chrome com o perfil proprietário, a propriedade de domínio
`sc-domain:sirfisher.com.br` mostrou a opção de incluir links e conteúdo
marcada como padrão, com o botão Salvar desabilitado. A inclusão já estava
ativa; nenhuma configuração foi alterada. A pendência foi resolvida por
leitura da UI, com esse escopo de propriedade. As evidências são
`output/semrush-3-dias/painel-semrush/gsc-ia-inclusao-dom.txt` e a captura
correspondente. Isso confirma o controle do domínio e mantém os limites de
indexação e escolha de fontes descritos anteriormente.

### Impressões reais de IA na Pesquisa Google

O relatório dedicado do Search Console foi aberto pela UI da propriedade de
domínio. Os filtros nativos foram `Web (com base em texto)` e `Últimos 3 meses`.
O ZIP exportado tem 77 linhas diárias de 08/08/2026 a 23/10/2026 e 2.672 impressões
na propriedade; a soma diária confere. São impressões em recursos de IA da
Pesquisa, com datas em Pacific Time. Esses dados antecedem as alterações
de 25/10 e não medem cliques, clientes ou reservas.

A tabela de páginas tem 13 linhas e soma 2.734 impressões na agregação por
URL. Inclui variantes HTTP, UTM e portal e não corresponde às 13 URLs do
sitemap. A soma por página foi preservada, sem ajuste para coincidir com o
total da propriedade. Os 27 países somam 2.672 em sua própria agregação;
os aparelhos também somam 2.672: celular 2.071, computador 587 e tablet 14.
Essas partições não foram somadas entre si.

A exportação nativa foi concluída em
`output/semrush-3-dias/painel-semrush/gsc-genai-exportacao.csv.zip`, com os
CSV de gráfico, páginas, países, dispositivos e filtros. O ZIP teve CRC
conferido. Os valores das 13 linhas de páginas coincidem com o DOM capturado.
Os derivados `gsc-genai-*` preservam procedência e filtros. Essa observação
direta complementa a consulta antiga `searchAppearance`, que retornou
`rows[]` na API comum e não demonstrava ausência de aparições em IA.

### Pedidos de rastreamento de duas URLs públicas

O Search Console confirmou `Indexação solicitada` para
`https://www.sirfisher.com.br/eventos/`, com entrada na fila prioritária de
rastreamento. Isso confirma o pedido, sem mudar imediatamente o estado no
índice. Para `https://www.sirfisher.com.br/reservas/`, duas tentativas comuns
falharam com a mensagem de conexão ao serviço reCAPTCHA; o envio ficou
pendente. Nenhum desafio foi resolvido ou contornado. O portal de reservas
e suas escolhas de noindex não foram alterados.

O procedimento usou a inspeção da UI para poucas URLs próprias alteradas,
conforme a [orientação oficial](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl).
A Indexing API não foi usada. O recibo está em
`output/semrush-3-dias/painel-semrush/gsc-solicitacoes-indexacao.json`, com
DOM e captura da confirmação de eventos. A documentação do Google informa
que o pedido não garante inclusão e que repeti-lo não acelera o rastreamento.

### Nova auditoria após as correções

Com o Chrome disponível, Codex da sessão principal iniciou uma nova execução
real de Site Audit e esperou sua conclusão. A coleta posterior manteve
18 páginas, limite de 100, desktop e JavaScript desabilitado. Esses filtros
descrevem o rastreador da auditoria; não representam todos os buscadores.

| Medida Semrush | Auditoria anterior | Nova auditoria |
| --- | ---: | ---: |
| Site Health | 88 | 96 |
| AI Search Health | 88 | 99 |
| Erros | 2 | 0 |
| Avisos | 24 | 20 |
| Páginas quebradas | 1 | 0 |
| Internal Linking | 97 | 100 |
| Markup | 96 | 100 |
| Core Web Vitals da auditoria | 90 | 100 |

O painel de AI Search Health informou ausência de problemas nesse conjunto.
A nota Core Web Vitals pertence ao filtro Semrush e não é uma nova medição
CrUX. A tela também listou 17 páginas bloqueadas para rastreadores ligados
à política de treinamento preservada; essa contagem não demonstra bloqueio
do Googlebot ou do OAI-SearchBot. As notas de saúde não são posição ou prova
de citação. A evidência está em
`output/semrush-3-dias/painel-semrush/auditoria-apos-correcoes-dom.txt` e na
captura da mesma conferência, fora do Git.

No AI Visibility, a tela com atualização em 23/10 e recorte Worldwide mostrou
nove menções, sendo oito em ChatGPT e uma em Gemini, e dez registros com o
rótulo Cited. A distribuição das menções foi Brasil 7, Estados Unidos 1 e
Argentina 1. Os 14 registros de prompts têm 13 textos distintos. Seus links
identificam nove registros de ChatGPT, dois de Gemini, dois de AI Mode e um
de AI Overview. Essa distribuição de registros difere da distribuição das
nove menções. Os dados antecedem as mudanças de 25/10 e têm outra cobertura
em relação ao tracking Google/Brasil/desktop.

A tabela Cited Pages tem dez linhas e oito URLs distintas próprias: sete no
`www` e uma no portal de reservas. A home aparece em três linhas, mantidas
com seus filtros. Os endereços abrangem pôr do sol, portal, home PT/EN,
fish and chips PT/EN, guia e Réveillon. A tabela Cited Sources tem 37 registros
e 22 strings de domínio; cada URL exige conferência antes de uso como fonte
editorial. Esses conjuntos não foram somados como entidades ou páginas únicas.

A exportação CSV nativa do AI Visibility da Semrush retornou `Export failed`.
Os CSVs derivados
foram produzidos a partir das linhas visíveis do DOM, com fonte, filtros,
posição de linha e valores originais. O formato e a cobertura capturada serão
preservados; os derivados não foram chamados de exportação nativa concluída.

### Brand Performance local

O painel já tinha um perfil, ocupando a cota 1/1, com localização Fortaleza,
Ceará, Brasil, idioma português e plataforma ChatGPT. Na tela de 25/10,
Share of Voice apareceu como 11%; a classificação mostrada foi `favorable`
75% e `general` 25%. Coco Bambu, Illa Mare, Ponza e Nom apareceram no conjunto
de concorrentes. Esses números pertencem ao recorte da ferramenta; não foram
tratados como participação de mercado ou opinião de clientes.

O método informa que a Semrush escolhe perguntas, executa consultas nas IAs
e gera estratégias com IA, com atualizações automáticas a cada sete dias.
O texto de Insights apresentou divergências em relação ao grid. A revisão
usou os valores da tabela e as regras comerciais confirmadas. A sugestão de
combos para 10–20 pessoas foi descartada; permanecem reserva comum até dez,
contato com a equipe de 11 a 29 e proposta de evento de 30 a 100 sentados.
Os dez drivers foram guardados como observações da ferramenta, sem aplicar
automaticamente as propostas comerciais.

As exportações nativas de Brand Performance guardaram 200 registros de
respostas completas: 175 sem marca e 25 com marca. Cinco CSVs, com 797 linhas,
foram conciliados com o DOM por chave e métricas. As grades completas
preservaram 187 registros de domínios, sendo 166 sem marca e 21 com marca,
e 431 de páginas, sendo 398 sem marca e 33 com marca. São linhas das grades,
mantidas com o recorte de cada relatório. Essas respostas do perfil são outro
conjunto em relação aos 12 prompts selecionados do acompanhamento local.

As evidências ficam em `output/semrush-3-dias/painel-semrush/`, nos arquivos
`brand-performance-dom.txt`, `brand-performance-drivers.json` e
`brand-performance-metodo-dom.txt`. O perfil encontrado não foi criado
nesta etapa.

### Acompanhamento local do Google

Foi configurado e iniciado um alvo próprio de Google em Fortaleza, Ceará,
Brasil, aparelho phone/mobile e idioma português do Brasil, com os 40 termos
selecionados. Projeto `31731491`, campanha `31731491_5693858`, identificador
da interface `13982518`, domínio raiz `sirfisher.com.br`. O nome do negócio
para resultados locais foi preenchido como Sir Fisher. Nenhum email semanal
novo foi ativado.

A coleta dos 40 termos foi concluída. Na única data disponível, 25/10, o
painel mostrou visibilidade 13,97%, oito termos no Top 10 e cinco no Top 3.
As faixas não foram somadas. É uma linha de base local; não foi comparada
como ganho de posição em relação ao alvo nacional de outro aparelho.

A campanha original Brasil/desktop com 48 palavras permaneceu preservada.
A cópia criada pelo quickstart no projeto `31731302` ficou como Brasil/desktop
e recebeu o nome `Sir Fisher copia Brasil desktop`. O alvo Fortaleza/mobile
é o do projeto identificado acima. As configurações e os resultados de cada
alvo mantêm essa distinção.

### Acompanhamento local do ChatGPT

A campanha `31731503_5693868`, com nome final `Sir Fisher perguntas IA Fortaleza`,
foi configurada para Fortaleza, português do Brasil e ChatGPT, com os 12
prompts em português selecionados. A primeira coleta terminou com nove
registros Mentioned e três Missed. A seleção tem três perguntas diretas
sobre Sir Fisher, todas Mentioned, e nove genéricas, com seis Mentioned e
três Missed. As três genéricas sem menção tratam de eventos, grupos e frutos
do mar no Meireles. Essas contagens não foram tratadas como taxa de descoberta
ou participação de mercado. O widget também mostrou 49 Source pages.
As contagens de páginas foram
preservadas com o rótulo da tela, sem convertê-las em URLs próprias ou únicas.
As perguntas e fontes detalhadas acompanham o backup.

Na mesma tela, o widget AI Visibility mostrou 74,33% e o Summary mostrou
68,84%. Os dois valores foram preservados com seus rótulos; não foi criada
uma fórmula para reconciliá-los. A leitura prioriza a contagem de menções
e cada pergunta, com as fontes e os fatos efetivamente devolvidos. O conjunto
selecionado não representa todas as perguntas de clientes ou os resultados
que cada pessoa receberá no ChatGPT.

### Estado externo no fechamento do snapshot

Outra execução deixou alterações locais em `site/robots.txt` e
`site/tools/analytics/README.md`, incluindo uma mudança de `Google-Extended`.
Esses dois diffs foram preservados e não foram publicados por esta rodada.
A revisão não confirmou a origem da autorização desse toggle e não o
registra como concluído. Na leitura pública de 25/10 às 04:40:29 de Fortaleza,
Googlebot e OAI-SearchBot continuavam permitidos pelas diretivas, com GPTBot
e Google-Extended bloqueados. Não havia diretiva Content-Signal. A evidência
está em `output/semrush-3-dias/robots-publico-fechamento.json`.

### Checklist de conferência para 26 e 27/10

Este roteiro é para uma nova rodada do agente. Não atribui coleta manual
ao proprietário ou à recepção.

- [ ] **26/10:** conferir se há novas datas nos alvos Google/Fortaleza/mobile
  e ChatGPT/Fortaleza/PT; guardar os resultados e a configuração. Comparar
  as mesmas 40 palavras e os mesmos 12 prompts com a linha de base de 25/10,
  preservando aparelho, idioma, plataforma e fontes. Conferir respostas
  factuais sobre pratos, preços e regras contra o site publicado.
  Conferir o resultado do pedido de eventos e, se o serviço estiver disponível,
  retomar o envio pendente de `/reservas/` na UI, sem contornar verificações.
- [ ] **27/10:** consolidar os resultados disponíveis e seus limites em
  arquivos portáteis. Registrar quais páginas aparecem, quais perguntas
  deixam de mencionar a casa e quais informações precisam de uma fonte
  confirmada. Rever os dados automáticos existentes de procura e ações,
  sem atribuir visitas ou vendas a uma variação curta de posição ou menções.

Brand Performance informa atualizações a cada sete dias; seu recorte não
ganha outra data apenas porque houve uma conferência diária. O checklist
não criou um agendamento no Codex. Novas conferências dependem de outra
rodada de trabalho e do acesso aos dados disponíveis; não há promessa de
execução automática. As coletas nativas da Semrush seguem as configurações
salvas no serviço.

## Rodada adicional em 25/10, após o fechamento do acervo

- **Google-Extended:** o usuário confirmou a liberação e o site
  [`bafeeaf`](https://github.com/sirfisherfc/site/commit/bafeeaf81897262b6bf01e457b3237e24b65cad7)
  foi publicado e conferido no domínio às 05:09 de Fortaleza. Os outros
  bloqueios do robots foram preservados. A purga atingiu somente
  `https://www.sirfisher.com.br/robots.txt`; os dois controles gerenciados
  continuaram desligados. A pendência descrita no fechamento anterior foi
  resolvida depois daquele snapshot. A permissão fornece acesso conforme
  as diretivas e os demais controles da rede; aparições e citações exigem
  observação própria.
- **Nova autorização sobre os demais robôs de IA:** em 25/10, o usuário
  decidiu permitir os 31 agentes do grupo restante, incluindo `GPTBot`,
  `ClaudeBot` e `CCBot`, no conteúdo público do `www`. A lista anterior
  tinha sido herdada da Cloudflare e preservada enquanto faltava essa
  decisão específica. A liberação pode permitir também coleta para treino;
  ela não garante menções, citações ou posições. O site
  [`84cbb26`](https://github.com/sirfisherfc/site/commit/84cbb26a91be2ba81f2160e984b25f83712697b0)
  publicou o novo robots, com Assets e Pages aprovados. A URL comum e a
  versão com parâmetro de conferência responderam HTTP 200, com os mesmos
  bytes do repositório e sitemap correto. A análise das diretivas permitiu
  40 nomes de agentes em três caminhos públicos. As leituras HTTP usaram
  `SirFisher-Audit`; a prova não reproduz uma visita autêntica dos provedores.
  Na Cloudflare, a regra `7af7f90de3944407842037ebdd674f5d`,
  `Robos IA: leitura das paginas publicas`, foi publicada, reaberta e
  conferida como `Active`, na ordem 2 após a regra Semrush existente.
  A expressão combina o host `www.sirfisher.com.br`, GET/HEAD, 15 caminhos
  públicos conhecidos e o texto dos 31 user-agents anteriores, sem distinção
  de maiúsculas. Ela pula somente a fase `http_request_sbfm`, com logs ligados.
  As configurações de regras customizadas, rate limiting, Managed WAF e
  autenticação foram preservadas; os demais subdomínios ficaram fora da
  exceção. A regra Semrush foi preservada. O GET posterior de Bot Management
  confirmou os mesmos campos globais, inclusive `ai_training=disallow` e
  `ai_bots_protection=only_on_ad_pages`; a nova exceção tem o escopo descrito.
  Ao publicar rotas fora dos 15 caminhos, revisar essa exceção. O rollback
  consiste em desativar somente a nova regra na UI. Menções e AI Visibility
  dependem das observações posteriores. O estado anterior continua registrado
  no histórico e nos ZIPs congelados. Recibos JSON/TXT e a captura
  `cloudflare-regra-ativa.png` ficam em
  `output/liberacao-robos-ia-2026-10-25/`. Recibo do robots em
  `output/liberacao-robos-ia-2026-10-25/robots-validacao-publica.json`.
- **Reservas e eventos:** o site
  [`7c2b72c`](https://github.com/sirfisherfc/site/commit/7c2b72ca8ab4bbffecb7c51dcbdbe94f206892ca)
  publicou ajustes nos caminhos de grupos/eventos e na FAQ sobre posição
  da mesa, preservando as regras existentes e sem promessa de primeira fila.
  Passaram 108 testes Deno, quatro verificadores e quatro casos de navegador
  em 390/1440 px, além das verificações de JSON e links internos.
  Assets e Pages concluíram com sucesso. As duas páginas públicas
  responderam HTTP 200 e coincidiram com o HTML local, com e sem parâmetro
  de conferência.
- **Cardápio no Perfil da Empresa:** às 05:41 de Fortaleza, um PATCH somente
  em `attributes/url_menu` publicou
  `https://www.sirfisher.com.br/cardapio/?utm_source=google_maps&utm_medium=organic&utm_campaign=gbp_menu`.
  A leitura posterior coincidiu com esse endereço. Os outros 60 atributos, os campos
  da ficha e FoodMenus ficaram iguais. O destino respondeu HTTP 200, com
  canonical `/cardapio/` sem parâmetros. A identificação permite separar
  futuros acessos desse botão no Analytics; ainda faltam dados posteriores
  para medir o resultado. Recibo agregado fora do Git em
  `output/seo-rodada-adicional-2026-10-25/gbp-url-menu-recibo.json`.
- **ChatGPT em inglês:** o alvo `Sir Fisher IA English Fortaleza`
  (`31731868_5693988`, pasta `13982947`) foi configurado para Fortaleza,
  English e quatro prompts já preparados, com email semanal desligado.
  A primeira coleta terminou em 25/10: quatro linhas `Mentioned`, com três
  perguntas genéricas e uma de marca. A tabela incluiu URLs próprias
  `/en/`, `/en/fish-and-chips/` e `/reservas/`. As superfícies do painel
  mostraram percentuais diferentes durante a consolidação; este registro
  preserva as contagens por pergunta. Há uma data de referência e ainda
  faltam observações posteriores para medir evolução ou efeito das mudanças.
  O export nativo ficou desabilitado pelo Trial; snapshots e CSV derivado
  preservam os resultados, sem upgrade de assinatura.
- **On Page SEO Checker e WAF:** o painel existente mostrou inicialmente 28 ideias para
  seis páginas. O detalhe da página EN de fish and chips informou HTTP 403
  do rastreador e ideias gerais. Uma nova coleta de uma página terminou e
  repetiu o bloqueio. Um evento Cloudflare às 05:46:13 de Fortaleza confirmou
  `firewallManaged`, ação `block` e agente `SemrushBot-SI`, em IP da faixa
  oficial da Semrush. Esse evento confirmou o bloqueio antes da exceção.
  A regra foi identificada como
  `Block AI bots on ad pages`, na fase `http_request_sbfm`.
  Uma exceção foi publicada e relida `Active` na UI, limitada à faixa oficial
  da Semrush, agente `SemrushBot-SI`, host `www`, métodos GET/HEAD, consulta
  vazia e 13 páginas públicas mais robots/sitemap. Ela pula todas as regras
  da fase `http_request_sbfm` apenas nesse conjunto, com logs ligados.
  As demais proteções foram preservadas; não houve ampliação
  do token ou de permissões da API. Às 05:53:47 de Fortaleza, um evento real
  registrou `skip` na regra nova para esse rastreador. A recoleta posterior
  da página EN de fish and chips deixou de mostrar HTTP 403 e passou a
  apresentar cinco ideias com leitura do conteúdo. A prova de acesso vale
  para essa página e esse recorte; outros caminhos exigem suas próprias
  verificações. Bot Management e os dois controles de robots ficaram iguais.
  Recibo em
  `output/semrush-seguimento-2026-10-25/cloudflare-excecao-validacao-eventos.json`
  e relatório em `onpage-en-fish-apos-excecao-dom.txt`, na mesma pasta.
  O rollback consiste em desativar essa regra específica na UI, sem alterar
  os controles gerais. Nenhuma proteção geral foi desligada e nenhuma
  exceção baseada só em user-agent foi criada.
  As sugestões gerais exigem evidência da
  página antes de qualquer implementação, inclusive recomendações de schema.

Esta rodada não fez novas consultas pagas à API Standard da Semrush. O ZIP
`output/semrush-3-dias/sir-fisher-acervo-completo-2026-10-25.zip` conserva
os mesmos bytes e o hash do sidecar original. Assinatura e recorrência
permaneceram intactas. O acompanhamento usa dados automáticos existentes;
o registro manual de clientes sem reserva continua adiado pelo usuário.
