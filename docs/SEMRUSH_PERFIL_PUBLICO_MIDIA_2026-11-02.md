# Semrush, perfil do público e decisão de mídia

Consulta em 02/11/2026, America/Fortaleza. O objetivo é gerar reservas e
visitas com resultado comercial, usando os dados existentes. O proprietário
dispensou pesquisa com clientes e pediu a comparação dos canais antes da
escolha da plataforma. A análise separa navegação, reserva, comparecimento e
consumo, conforme a cobertura de cada fonte.

## Decisão com a evidência disponível

Há base para organizar públicos por intenção e melhorar a experiência de
celular. A escolha de clientes mais rentáveis e da divisão de investimento
depende de margem, capacidade e consumo atribuídos com cobertura conhecida.
Os dados atuais permitem selecionar candidatos a teste. Ainda faltam os
resultados comerciais comparáveis para escolher a plataforma de maior retorno.

Pesquisa Google é a primeira candidata para um teste de intenção local,
porque há consultas comerciais observadas e acesso orgânico crescente.
Instagram trouxe visitas ao site, com 836 sessões atribuídas em outubro;
testar mídia paga ali exige conferir a conta, a medição e a meta de reserva.
ChatGPT Ads tem gasto e cliques observados, mas a amostra retornada e as metas
atribuídas ainda não sustentam ampliar investimento. Nenhuma campanha ou verba
foi alterada nesta rodada.

## Fontes e cobertura

| Fonte | O que foi conferido | Limite |
| --- | --- | --- |
| GA4, MCP oficial, propriedade `353205396` | Setembro e outubro completos, host `www.sirfisher.com.br`; QR com origem/mídia exata `qr_code / offline` | Identificações técnicas, consentimento, bloqueadores e mudanças de coleta afetam a cobertura. |
| Reservas operacionais | Agregados de `source=public_site`, mês de criação em Fortaleza | Status atuais e reservas futuras exigem acompanhar a coorte até o resultado da visita. |
| Semrush, sessão existente do Navegador | Site Audit de 30/10; posições de 26/10 a 02/11; On Page SEO Checker de 31/10 | Estimativas e conjuntos monitorados têm filtros próprios. Recursos pagos indisponíveis ficaram identificados. |
| ChatGPT Ads Manager conectado | Conta Sir Fisher, BRL e Fortaleza; configuração e retorno de desempenho | As linhas cobrem 23–30/09 e 01–19/10, embora o pedido tenha abrangido os meses completos. |

O MCP Semrush recusou as consultas por `no_api_units`, com repetição indicada
como indisponível. A leitura seguiu pela interface autorizada e pelo acervo
já salvo. Isso não confirma o saldo atual nem autoriza comprar unidades.
[Acesso MCP Semrush](https://www.semrush.com/mcp-access).

O acervo de 25/10 reúne 79 relatórios no ledger e 379 termos após os
complementos. Ele conserva as datas e bases originais; o ZIP de fechamento
permanece como snapshot. A presente rodada acrescenta observações, sem
substituir os históricos por valores de outra data.
[Acervo e métodos](SEMRUSH_3_DIAS_2026-10-25.md).

## Avisos do Site Audit

A campanha `31731302`, desktop e renderização JavaScript desativada, rastreou
19 páginas em 30/10. A tela mostrou saúde 96%, AI Search Health 100%, nenhum
erro, 22 ocorrências de warning em três tipos e cinco notices de um tipo.
Core Web Vitals exigia plano adicional; a tela não forneceu essa medição.

| Aviso | Diagnóstico | Ação indicada |
| --- | --- | --- |
| 16 ocorrências de JavaScript/CSS sem minificação | Todas as linhas conferidas apontam para CSS; são cinco arquivos distintos reutilizados nas páginas. | Otimização de tamanho com prioridade baixa. A necessidade de publicação depende do ganho de desempenho e da validação visual. |
| Cinco páginas com baixa proporção texto/HTML | Home PT, executivo, cardápio PT, cardápio EN por parâmetro e home EN. O indicador compara texto com código e não mede sozinho a utilidade da página. | Preservar conteúdo útil, menu renderizado, dados estruturados e CSS crítico. Acrescentar informação quando houver dúvida real do visitante. |
| Uma página com poucas palavras | `/reservas/`, 180 palavras segundo o rastreador. O conteúdo principal local tem cerca de 283 por outro método de contagem. | A orientação de corte foi esclarecida. O guia informa as condições e conduz ao formulário; a contagem isolada não justifica texto de preenchimento. |
| Cinco recursos em formato de link de página | Links da página Jardim Japonês para páginas `File:` do Wikimedia Commons, usadas como créditos de imagens. | Preservar os créditos. São destinos de atribuição conferidos. |

As proporções exibidas foram 0,04 na home, 0,09 no executivo, 0,05 em cada
cardápio e 0,08 em `/en/`. O cardápio tem conteúdo renderizado no HTML e sua
estrutura inclui código, imagens e estilos. A Google orienta conteúdo útil
e informa que a extensão isolada do texto não determina a classificação.
Não há requisito de acrescentar palavras até atingir a nota do rastreador.
[Guia da Google](https://developers.google.com/search/docs/fundamentals/seo-starter-guide),
[definições do Site Audit](https://www.semrush.com/kb/542-site-audit-issues-list).

Uma simulação local de minificação e Brotli, com o mesmo critério de qualidade
para ambos os arquivos, estimou economia de 2,8 kB em `style.css`, 1,9 kB em
`cardapio.css`, 1,3 kB em `desktop.css`, 0,3 kB em `jardim.css` e 0,2 kB em
`por-do-sol.css`, arredondados. As economias não devem ser somadas como se
cada visita carregasse todos os arquivos. Isso estima bytes comprimidos;
faltam medições de carregamento que demonstrem ganho perceptível.
Minificar e comprimir se complementam.
[Codificação e transferência](https://web.dev/articles/optimizing-content-efficiency-optimize-encoding-and-transfer).

## O que aproveitar da pesquisa Semrush

No Google local, Fortaleza/celular/português e 40 termos acompanhados, a
visibilidade passou a 14,35%, variação de +0,38 ponto percentual na janela.
Cinco termos estavam no Top 3, 11 no Top 10 e 23 no Top 100. Oito melhoraram
e nove caíram. Volume, CPC e tráfego estimado exibidos como zero nesse
relatório local não demonstram ausência de demanda ou clique gratuito.

| Consulta acompanhada | Posição 26/10 → 02/11 | Uso prático |
| --- | --- | --- |
| `fish and chips fortaleza`, marca e variantes próximas | Primeira posição preservada para cinco termos | Preservar páginas e informações da oferta; medir necessidade antes de comprar procura de marca. |
| `almoço beira mar fortaleza` | 10 → 8 | Candidata comercial para comparar com executivo e restaurante na orla. |
| `restaurante beira mar fortaleza` | 10 → 10 | Manter localização, cardápio e reserva claros na home. |
| `best fish and chips near me` | 50 → 8 | Manter jornada EN; a posição não mede tamanho nem rentabilidade de um público estrangeiro. |
| `onde comer frutos do mar em fortaleza` | Sem posição no Top 100 → 10 | Acompanhar cliques próprios e ações comerciais dessa intenção. |
| `almoço executivo fortaleza` | 21 → 24 | Revisar a procura no Search Console e a página antes de ampliar mídia. |
| `almoço executivo em fortaleza` | 15 → 53 | Investigar mudança de consulta/página e persistência; uma janela curta não prova causa. |
| `beira mar fortaleza restaurantes` | 10 → 34, guia como destino atual | Conferir a relação entre home e guia sem apagar páginas de funções distintas. |

Consultas de grupos, confraternização e vários termos de jantar ficaram sem
posição no Top 100. Isso mostra uma lacuna no conjunto monitorado; ainda falta
avaliar procura comercial e conversão para priorizar investimento nesses temas.

A lista de projetos também mostrou visibilidades distintas para dois
acompanhamentos nacionais Google (8,35% e 11,17%, 48 termos cada). Esses
conjuntos não substituem o recorte local. Domínios Instagram e Tripadvisor nas
SERPs são canais presentes nos resultados; sua participação não equivale à
participação de mercado de restaurantes.

No projeto ChatGPT/PT, com 38 prompts, a tela específica mostrou **AI
Visibility 56,98%**, 22 menções e 232 páginas-fonte. A lista de projetos e o
quadro de posições do mesmo relatório mostraram outra medida, 35,27%.
Os nomes e os números foram preservados separadamente. Houve presença em
perguntas sobre fish and chips, reserva para hoje, localização e Réveillon.
O projeto EN tinha 12 prompts e a lista mostrou 68,48% na coluna Visibility.
Essas medidas cobrem perguntas monitoradas, com conjunto ampliado desde
25/10; elas não representam parcela de usuários, cliques ou reservas.

O relatório de canibalização exigia Guru. Sua tabela de demonstração continha
domínios alheios ao Sir Fisher; ela foi descartada. O resumo do projeto local
indicava 11 de 23 termos afetados, mas a leitura detalhada ficou indisponível.
Os dados disponíveis não justificam fundir URLs ou redirecionar o guia.

O On Page SEO Checker existente, atualizado em 31/10, tem 43 ideias para seis
páginas: nove de estratégia, 18 de conteúdo, quatro semânticas, seis de links,
uma técnica e cinco de apresentação na busca. A projeção de mais de 1.000%
de crescimento e os volumes somados pelo produto não são previsão de clientes.
A ferramenta coloca pôr do sol em primeiro por volume; o Search Console
mostrou intenção predominantemente informacional nessa página. Priorizar
refeições exige avaliar o resultado comercial, além do alcance do conteúdo.

As oito ideias do executivo incluem termos de marca e `fishery restaurant`
no mesmo grupo, recomendações de mais texto e inclusão de “Praia do Futuro”
e “Praia de Iracema”. Essas sugestões exigem curadoria: a unidade fica no
Meireles e a página atende almoço executivo. Preservar fatos e linguagem
natural. Sugestões de link são candidatos editoriais; não houve contato,
compra de link ou publicação em terceiros.

A sugestão automática de `aggregateRating`/`ItemList` não foi aplicada.
A Google limita estrelas de avaliações sobre o próprio estabelecimento
em páginas controladas por ele. Os tipos precisam representar o conteúdo.
[Regras de avaliações](https://developers.google.com/search/docs/appearance/structured-data/review-snippet).

## Perfil agregado dos acessos QR

| Medida do QR | Setembro | Outubro |
| --- | ---: | ---: |
| Sessões | 399 | 717 |
| Usuários totais (`totalUsers`) | 263 | 495 |
| Taxa de engajamento | 64,7% | 69,7% |
| Visualizações | 619 | 1.440 |
| Participação nas sessões do site | 20,9% | 25,8% |

Em outubro, 713 sessões foram pelo celular (99,4%); 457 usaram iOS (63,7%)
e 256 Android (35,7%). Português apareceu em 662 sessões (92,3%) e inglês
em 28 (3,9%). Sextas e sábados somaram 49,8% das sessões; outubro teve cinco
ocorrências de cada um desses dias. Esses dados ajudam a priorizar a experiência
em celular, português e os navegadores usados.

Fortaleza recebeu 338 sessões por localização aproximada e São Paulo 151.
A origem técnica pode refletir operadoras, redes e VPNs. Ela não identifica
residência ou proporção de turistas. iOS não demonstra renda. O QR pode ser
encaminhado ou reutilizado, portanto o acesso não comprova presença nem compra.
Em outubro, todas as sessões QR usaram a campanha `cardapio_restaurante`;
o histórico não separa os pontos físicos com cobertura útil.

O cardápio apareceu em 562 sessões QR, detalhes de itens em 198 e cliques de
reserva em três. A hipótese mais coerente é uso frequente para consultar a
oferta durante a visita; o GA sozinho não confirma quem já estava na casa.
Os 11.079 eventos de categoria vista podem se repetir na rolagem. Faltam
pedidos ou consumo associados para concluir preferências ou valor comercial.
Os parâmetros de categoria/prato existem no código, mas não estão cadastrados
como dimensões consultáveis; o relatório atual não recuperou essa abertura.

## Segmentos para trabalhar

Estes são segmentos de jornada e hipóteses de ocasião. A evidência não permite
dar idade, renda, gênero, profissão ou residência às personas.

| Segmento | Base observada | Conteúdo e resultado a acompanhar |
| --- | --- | --- |
| Pessoa consultando o cardápio por QR | 717 sessões QR; uso majoritário em celular e português | Facilitar consulta durante a visita. Avaliar retorno posterior se houver identificação técnica elegível, sem contar acesso atual como aquisição. |
| Pessoa escolhendo restaurante na Beira-Mar/Meireles | Consultas comerciais locais e crescimento de busca/Maps no GA | Localização, oferta e cardápio; reserva e comparecimento como etapas distintas. |
| Pessoa procurando almoço individual durante a semana | Página de executivo e termos locais; queda de visualizações e posições em parte das variantes | Mostrar condições vigentes e caminho adequado para hoje. Avaliar o turno que tenha capacidade disponível. |
| Pessoa buscando fish and chips em PT ou EN | Posições específicas e jornada de conteúdo existente | Criativo e destino no mesmo idioma. Faltam dados para dimensionar a procura por idioma e separar verba. |
| Organizador de grupo ou evento | Oferta existente de 30–100 sentados e consultas monitoradas | Pedido de proposta e contratação têm sequência própria; não misturar com reserva comum. Confiança sobre tamanho e valor desse público ainda baixa. |

O público mais relevante para aquisição, com a evidência atual, é quem procura
uma refeição compatível com a casa e pode comparecer à unidade. A relevância
econômica entre almoço, demais refeições e eventos depende da margem e da
capacidade por ocasião. O QR representa outra etapa da jornada e merece
análise própria, com cuidado ao usá-lo em públicos de aquisição.

## Comparação dos canais e desenho de teste

| Canal | Papel e público propostos | Objetivo, formato e condição |
| --- | --- | --- |
| Google Pesquisa | Busca comercial local por restaurante ou almoço; português e EN em grupos distintos se houver procura suficiente | Candidata prioritária: campanha de Pesquisa voltada a leads/reserva, com palavras de intenção e presença geográfica compatível. Reserva confirmada como ação principal; rota e menu como apoio. Comparecimento decide a qualidade. Marca deve ser relatada separadamente. |
| Instagram/Meta | Descoberta da casa e retorno de visitantes que demonstraram intenção, quando elegíveis | Candidata a teste de criativo visual e jornada até a reserva. Resultado comercial desejado: reserva/comparecimento. A escolha do objetivo disponível depende de conferir a conta e a integração; a documentação Meta consultada redirecionou ao login. O tráfego orgânico não mede retorno de anúncio. |
| ChatGPT Ads | Descoberta contextual; conta atual segmentada para Ceará, com objetivos de alcance e cliques nas campanhas lidas | Manter a avaliação dos eventos recebidos e atribuídos antes de ampliar. Relatar separadamente cliques, inícios, confirmações e visitas. Volume de IA orgânica no Semrush não demonstra eficiência da campanha paga. |
| Perfil da Empresa/Maps, Tripadvisor e referências locais | Pessoas avaliando local, rota e reputação; presença nas SERPs | Prioridade de informação orgânica e reputação. Publicidade ou parceria paga exige preço, cobertura e resultados antes da comparação com outros canais. |
| TikTok, YouTube, display e outras redes de descoberta | Hipóteses de alcance visual | Os dados desta rodada não trouxeram custo nem visitas atribuídas nesses canais. Adiar verba até existir hipótese, criativo e medição que justifiquem o teste. |

O desenho da Pesquisa segue a
[documentação Google](https://support.google.com/google-ads/answer/9510373?hl=pt-BR)
e aproveita o [plano já preparado](PLANO_GOOGLE_SEARCH_2026-10-25.md).
Ele continua sem campanha criada, orçamento ou lances aprovados.

Os públicos GA já criados, de interesse em reservar e reserva concluída por
30 dias, ajudam a separar intenções. Eles podem se sobrepor. Para um futuro
retorno publicitário, a elegibilidade, o tamanho mínimo e a integração da
plataforma precisam ser conferidos; criar público no GA não o disponibiliza
automaticamente em Meta ou ChatGPT. A reserva concluída também não prova
comparecimento. A análise não enviou contatos ou listas de clientes.

### Investimento e critério de continuidade

A recomendação atual é **não aumentar o investimento enquanto o resultado
comercial continuar sem cobertura suficiente**. Os dados não sustentam uma
divisão percentual entre plataformas. Para o primeiro teste adicional,
concentrar a verba de teste aprovada em uma intenção e um canal por vez,
começando pela candidata de Pesquisa local se a conta e os custos forem
compatíveis. Isso permite comparar um resultado mensurável sem pulverizar
uma amostra pequena. Campanhas existentes permanecem como foram encontradas.

O teto depende do valor que o restaurante aceita investir e perder no teste.
O limite de custo por cliente deve ficar abaixo da contribuição incremental
esperada da visita, preservando a margem escolhida pelo restaurante. Para
reservas, considerar também comparecimento e tamanho do grupo na mesma coorte.
Como esses valores faltam, este relatório não fixa CAC, retorno ou lance.

Na conta ChatGPT, a primeira janela retornou uma reserva atribuída, que estava
marcada como no-show; a segunda retornou zero metas atribuídas. A cobertura
parcial e a atribuição por clique de 30 dias, sem visualização, pela data da
interação com o anúncio limitam a conclusão. Outubro pode mudar com o
processamento dos eventos e a finalização dos gastos. Inícios de reserva,
menu e rota apareceram como eventos intermediários. O valor antigo estimado
por reserva foi retirado em outubro e não representa faturamento observado.
Os valores de gasto ficam no recibo agregado privado, fora do Git.
[Medição de conversões ChatGPT](https://help.openai.com/en/articles/20001409-conversion-measurement).

## Dados que faltam para decidir com confiança

| Informação | O que pode ser aproveitado dos registros existentes | Limite atual |
| --- | --- | --- |
| Custo por reserva e visita em cada plataforma | Gasto real, identificadores de clique e eventos já configurados, quando houver acesso | Sem retorno comparável de todas as plataformas e com cobertura parcial no conector ChatGPT. |
| Resultado final de reservas | Status e data da visita nas coortes operacionais | Reservas futuras e status sem fechamento impedem taxa final de comparecimento. |
| Receita e contribuição por origem/ocasião | Consumo e custos da operação, se existir vínculo válido com reserva/canal | O GA atual não apura consumo nem margem do restaurante. Falta correspondência comercial validada. |
| Capacidade que se quer preencher e teto do teste | Ocupação/agenda existentes e decisão do proprietário | Falta escolher turno, período, margem e perda máxima aceitável. |
| Perfil demográfico elegível | Indicadores Google agora ativados e futuros relatórios agregados | Exibição depende de consentimento e limiares; perfil QR pode permanecer oculto. |
| Preferência por categoria ou prato | Parâmetros já enviados e catálogo existente | As dimensões não foram registradas; consultas deste período não recuperaram essa distribuição. |

Pesquisa voluntária e coleta manual no salão ficaram fora por escolha do
proprietário. Os dados atuais também não permitem quantificar toda a origem
das visitas sem reserva. A decisão deve conservar essa parcela como desconhecida.

## Configurações e publicação concluídas

O aviso de privacidade e o guia de reservas foram publicados no site no commit
`5f97e9f`, com validações e conferência HTTP 200 do conteúdo público. O guia
esclarece que o corte é o horário para confirmar a reserva para hoje.

Após a publicação e a confirmação expressa do proprietário, os Indicadores
Google foram ativados na propriedade correta. A interface mostrou chave
ligada e coleta permitida em 307 de 307 regiões. O Assistente passou de sete
para três tarefas restantes ao longo desta rodada. Restam Google Ads,
User-ID e dados fornecidos pelo usuário, cada qual com condições próprias.
Vincular uma plataforma depende da decisão de uso; User-ID precisa de
identificação interna estável; enviar contatos exige definir finalidade e
dados. Esses itens não bloqueiam a leitura da jornada atual.

Idade, gênero e interesses estavam indisponíveis nas consultas históricas,
com indicação de limites mínimos. A ativação permite enriquecer relatórios
de visitantes elegíveis. Ela não comprova preenchimento do passado nem
liberação imediata, e o perfil disponibilizado será agregado.
[Indicadores Google](https://support.google.com/analytics/answer/9445345?hl=pt-BR),
[limites mínimos](https://support.google.com/analytics/answer/9383630?hl=pt-BR).

As configurações anteriores, o funil e a comparação dos dois meses estão no
[relatório GA4](EVOLUCAO_SITE_GA4_2026-11-02.md). Nenhuma pesquisa, alteração
de verba, contato com terceiros ou envio de lista de clientes foi realizado.
Evidências de leitura, simulação, consultas agregadas e imagens ficam nos
diretórios ignorados `tmp/semrush-2026-11-02/`, `tmp/perfil-qr-2026-11-02/`,
`tmp/estrategia-midia-2026-11-02/` e `tmp/ga4-2026-11-02/`.
