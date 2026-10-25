# Semrush: acervo e execução de três dias

Referência: 25/10/2026, America/Fortaleza. O objetivo desta rodada é aproveitar
o teste para guardar dados úteis e melhorar a descoberta comercial do Sir Fisher.
A linha de base de Google, reservas e atendimento continua em
`REVISAO_SEO_LOCAL_CONVERSAO_2026-10-25.md`.

## O que extraímos em 25/10

| Entrega | Conteúdo e limite |
| --- | --- |
| Biblioteca de pesquisa | 49 requisições de relatório, 676 linhas originais e 593 observações deduplicadas. |
| Palavras e bases | 300 pares de palavra/base, correspondentes a 298 termos exatos entre BR, US e UK. Variantes próximas e bases não devem ser somadas para estimar mercado. |
| Resultados e referências | 191 URLs de resultados, fontes e destinos; 172 aparecem em SERPs, dez são fontes de backlinks. Os conjuntos se sobrepõem. |
| Oportunidades | Oito ações por URL, com evidência, confiança, dependência e forma de conferir. |
| Configuração preparada | 40 palavras selecionadas para Google/Fortaleza/celular e 16 prompts com intenção e fatos a conferir. A configuração no painel está pendente. |
| Guias e concierge | Dez URLs encontradas; seis páginas conferidas diretamente. Há páginas históricas e referências confirmadas só pela API. |
| Entrega para o proprietário | Planilha privada em `output/semrush-3-dias/sir-fisher-semrush-acervo-2026-10-25.xlsx`, na raiz do workspace. |

Os originais, schemas, parâmetros e derivados ficam no diretório ignorado
`site/_materiais/revisao-seo-2026-10-25/semrush/`. `LEIA-ME.md` explica os
arquivos e `snapshot-final.json` registra os hashes da versão entregue. Os
CSV de `consolidado/` podem ser usados após o teste, sem outra consulta paga.

## Decisões que os dados ajudam a tomar

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

## Localização, período e interpretação

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

## Plano de uso dos três dias

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

## Acesso e consumo

A credencial fornecida pelo proprietário foi guardada somente em arquivo local
ignorado pelo Git. A autenticação no endpoint oficial funcionou: initialize e
tools/list retornaram 14 ferramentas, sem relatório pago. A consulta gratuita
de saldo Standard respondeu HTTP 400; o saldo MCP continua sem verificação.
Não incluir a chave em comandos, documentação, planilha ou exports.

O conector expõe leitura de projetos, auditorias e acompanhamento. A
[documentação do MCP](https://developer.semrush.com/api/v3/introduction/semrush-mcp/)
confirma esse limite. As tentativas de abrir navegador integrado, Chrome e
Edge retornaram indisponibilidade nesta sessão. A autorização do proprietário
para configurar existe; falta a conexão do navegador. As instruções de conexão
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

## Fechamento técnico

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
