# GEO do Sir Fisher: auditoria e estratégia para recomendações em IA

Referência: 09/11/2026, fuso America/Fortaleza. Pedido do proprietário:
investigar como aumentar a descoberta, a seleção, a citação e a exatidão do
Sir Fisher nas respostas do ChatGPT, do Claude, do Gemini e do Copilot, com um
plano aplicável ao site e ao ecossistema digital. Site auditado:
<https://www.sirfisher.com.br/>, com o portal <https://reservas.sirfisher.com.br/>.
Elaborado por Claude (Claude Code). Todas as consultas a sistemas próprios
foram de leitura. Nenhuma configuração, página, ficha, diretório ou campanha
foi alterada.

## Como ler este documento

Cada afirmação relevante leva um código de evidência. Prática comprovada e
hipótese a testar aparecem separadas no plano.

| Código | Significado |
| --- | --- |
| **O** | Documentação ou comunicado oficial da plataforma |
| **C** | Artigo científico revisado por pares ou aceito em conferência |
| **P** | Preprint científico, sem revisão por pares confirmada |
| **I** | Estudo de indústria ou fornecedor, com metodologia própria e possível conflito de interesse |
| **E** | Medição própria desta auditoria, com data e método descritos |
| **H** | Inferência ou hipótese, ainda sem teste |

Termos usados: **SEO** é otimização para buscadores tradicionais. **SEO
local** cuida do Perfil da Empresa, mapas e diretórios. **AEO** (Answer
Engine Optimization) busca respostas diretas, como trechos em destaque.
**GEO** (Generative Engine Optimization) trata da presença em respostas
geradas por IA. **Recomendação** é a etapa em que o sistema escolhe quais
casas indicar. Na prática, as cinco se sobrepõem: o Google afirma que
otimizar para seus recursos de IA "ainda é SEO" [O].

## Avaliação crítica do pedido

**O objetivo é válido, mas a meta precisa de recorte.** Ser referência para
"melhores restaurantes de Fortaleza" depende de reputação acumulada fora do
site: matérias, listas e volume de avaliações. O Sir Fisher tem 819
avaliações no Google, contra cerca de 26,7 mil do Coco Bambu Beira Mar e 4,6
mil do Illa Mare. Ele não aparece em nenhuma das sete listas de Fortaleza
lidas nesta auditoria. A meta alcançável em três a seis meses é entrar com
frequência no conjunto de casas consideradas para intenções em que o Sir
Fisher é uma resposta forte: fish and chips, pôr do sol e vista na Beira-Mar,
almoço executivo com preço, refeição perto do Jardim Japonês, peixe e
petiscos de frente para o mar, pets e grupos. A lista geral de "melhores" é
consequência de longo prazo dessas frentes.

**Premissas questionadas.**

- Não existe primeiro lugar estável: listas geradas por IA mudam quase a
  cada execução, e o conjunto de marcas consideradas é mais estável que a
  ordem [I].
- Treinamento e busca são mecanismos diferentes. Para um negócio local de
  cauda longa, a busca em tempo real pesa mais que a memória do modelo [C].
- Nenhuma plataforma documenta um arquivo ou marcação especial que faça a IA
  citar um site. O Google diz que não é preciso criar arquivos, marcação ou
  Markdown especiais [O].
- As quatro plataformas usam índices e dados locais diferentes. Uma ação
  raramente beneficia as quatro na mesma medida.

**Riscos.** Texto oculto, avaliações induzidas e páginas em massa violam
políticas, e a literatura mostra efeito instável ou nulo dessas táticas [C].
Publicidade paga sem identificação viola o Código de Defesa do Consumidor e o
Código do CONAR. Medir posição em vez de frequência gera falsos positivos.
Dezembro e janeiro concentram alta estação e Réveillon, o que confunde
comparações antes e depois.

**Informações disponíveis.** O site, os acessos de leitura (GA4, Search
Console, Perfil da Empresa e Cloudflare) e o acervo de outubro bastaram.
Não foi preciso perguntar nada antes de avançar. As lacunas estão no
registro do fim do documento: os aplicativos de consumo das quatro
plataformas não foram consultados nesta sessão, porque não havia navegador
disponível.

**Decisões do proprietário.** Nenhuma bloqueia o plano, mas seis mudam o
resultado.

1. Confirmar a decisão de 25/10 e liberar os robôs de treinamento também na
   borda do Cloudflare.
2. Adotar só "Sir Fisher" como nome público, em vez de "Sir Fisher Praia".
3. Informar a origem do nome "Barra Sol", que aparece em quatro fontes.
4. Definir se a casa se apresenta como quiosque, restaurante ou ambos.
5. Aprovar ou não a publicação de uma faixa de gasto por pessoa.
6. Aprovar as abordagens a imprensa, guias e hotéis.

## 1. Resumo executivo

- **O ChatGPT já é um canal relevante e qualificado.** Em 90 dias, trouxe
  191 sessões orgânicas ao site, com crescimento mensal contínuo. Essas
  sessões se comportam como as do Google orgânico e muito melhor que as do
  ChatGPT Ads. Gemini, Perplexity, Copilot e Claude quase não aparecem [E].
- **O maior gap é de autoridade externa, não técnico.** Para "melhores
  restaurantes" e "onde comer na Beira-Mar", as respostas se apoiam em
  listas e matérias de terceiros [P][I]. O Sir Fisher está fora das sete
  listas lidas, inclusive de páginas das fontes que o ChatGPT mais citou em
  outubro [E].
- **Onde a casa é única, ela já é encontrada.** No Brave Search com país
  Brasil, o site ocupa as três primeiras posições para "fish and chips
  fortaleza" e a segunda para "restaurante beira mar fortaleza" [E]. No
  Google, a posição média nas consultas comerciais centrais fica entre 7,7
  e 10, no limite da primeira página [E].
- **A identidade do restaurante está fragmentada fora do site.** Há quatro
  variações de nome, unidades encerradas ainda indexadas, horários antigos
  em quatro fontes e o celular pessoal do proprietário num diretório
  automático [E].
- **O Tripadvisor é o elo mais fraco com maior alcance.** A ficha tem 11
  avaliações, nota 3,9 e categoria "bares e pubs", e o endereço da página
  ainda traz "Barra Sol". A Tripadvisor tem integração no ChatGPT e no
  Claude [O], e o módulo local do Brave usa dados e fotos dela [E].
- **Há um bloqueio técnico contrário à decisão de 25/10.** O Cloudflare
  bloqueia robôs de treinamento fora de 15 caminhos fixos, inclusive o
  `llms.txt`, o Jardim Japonês e as imagens. Robôs de busca e de usuário
  passam, então o efeito imediato é pequeno [E].
- **O ecossistema Microsoft está sem gestão.** Não há evidência de Bing
  Webmaster Tools, IndexNow ou Bing Places reivindicado. Sem o Bing Webmaster
  Tools, o único relatório oficial de citações no Copilot fica inacessível [E].
- **O FAQ estruturado não corresponde ao texto visível.** São 87 perguntas
  em JSON-LD e só 18 aparecem como pergunta na página. O Brave usa esse
  conteúdo nos resultados, e o Google exige que ele esteja visível [O][E].

Linha de base de sessões vindas de assistentes de IA no site
`www.sirfisher.com.br`, de 09/08 a 06/11/2026, pelo GA4 [E]:

| Origem | Sessões |
| --- | ---: |
| chatgpt.com, canal "AI Assistant" do GA4 | 179 |
| chatgpt.com, meio "organic" | 12 |
| gemini.google.com | 1 |
| Perplexity | 1 |
| Claude e Copilot | 0 |
| ChatGPT Ads (pago, para comparação) | 481 |
| Total de sessões do site no período | 6.734 |

| Mês | Sessões orgânicas do ChatGPT |
| --- | ---: |
| Agosto (a partir de 09/08) | 21 |
| Setembro | 36 |
| Outubro | 92 |
| Novembro (1 a 6) | 48 |

| Comportamento por origem, mesmo período | ChatGPT orgânico | ChatGPT Ads | Google orgânico |
| --- | ---: | ---: | ---: |
| Sessões | 179 | 481 | 658 |
| Taxa de engajamento | 77% | 29% | 60% |
| Sessões que abriram o cardápio | 30% | 9% | 30% |
| Sessões com clique em reservar | 2,8% | 1,9% | 3,3% |
| Sessões com clique em rota | 3,9% | 1,2% | 3,2% |

As páginas de entrada mais usadas por quem chega do ChatGPT são a home (93
sessões), o Réveillon (69 no site e 5 no portal), o almoço executivo (13) e o
cardápio (8). O portal de reservas recebeu outras 38 sessões orgânicas do
ChatGPT. Amostras pequenas pedem leitura cautelosa. Sessões do app do
ChatGPT sem referenciador caem em "direto" e não entram nessa conta [I].

## 2. Fundamentação técnica e científica

### 2.1 O caminho de uma recomendação

| Etapa | O que acontece | O que o restaurante controla | Base |
| --- | --- | --- | --- |
| Memória do modelo | O modelo responde com o que aprendeu no treinamento, sem buscar | Pouco e devagar: só influencia versões futuras, e entidades raras são mal memorizadas | Kandpal et al. 2023 e Mallen et al. 2023 [C] |
| Rastreamento e indexação | Robôs de busca e de treinamento leem as páginas permitidas | robots.txt, CDN, HTML legível sem JavaScript, sitemap, IndexNow | OpenAI, Anthropic e Google [O] |
| Recuperação | A pergunta vira uma ou várias buscas; a IA consulta um índice e bases de lugares | Ranking nos buscadores, fichas locais, menções de terceiros | Google, "query fan-out" [O] |
| Seleção e reordenação | O sistema escolhe poucos documentos e lugares para ler | Autoridade externa, avaliações, clareza dos fatos | Chen et al. 2025 [P]; Liu et al. 2024 [C] |
| Geração e citação | O modelo escreve a resposta e indica fontes | Exatidão e consistência dos dados públicos | Liu, Zhang e Liang 2023 [C] |
| Ação | A pessoa clica, pede rota ou reserva | Links, página de destino, medição | OpenAI, `utm_source` [O] |

**Treinamento não é busca.** Kandpal et al. (ICML 2023) mostram que a
exatidão de um modelo sobre um fato acompanha o número de documentos de
pré-treinamento que citam a entidade, e que a recuperação reduz essa
dependência [C]. Mallen et al. (ACL 2023) mostram que aumentar o modelo
melhora fatos populares, não os de cauda longa, e que a recuperação ajuda
justamente as entidades menos conhecidas [C]. Um restaurante local é cauda
longa. Liberar robôs de treinamento é barato e coerente com a decisão de
25/10, mas o resultado atual depende da busca em tempo real.

**A posição no contexto importa.** Liu et al. (TACL 2024) mostram desempenho
maior quando a informação relevante está no início ou no fim do contexto e
pior no meio [C]. Ser um dos primeiros documentos recuperados ajuda, o que
reforça o ranking tradicional.

**Citação não garante exatidão.** Liu, Zhang e Liang (Findings of EMNLP 2023)
auditaram quatro buscadores generativos. Só 51,5% das frases geradas tinham
apoio completo nas citações, e só 74,5% das citações apoiavam a frase
associada [C]. Por isso o plano mede a exatidão das respostas, além da
presença.

### 2.2 As quatro plataformas

| Aspecto | ChatGPT (OpenAI) | Claude (Anthropic) | Gemini e IA na Pesquisa Google | Copilot (Microsoft) |
| --- | --- | --- | --- | --- |
| Robôs e controles | OAI-SearchBot define a inclusão na busca. GPTBot é treinamento. ChatGPT-User atende ações do usuário, pode não seguir o robots.txt e não decide inclusão. Mudanças no robots.txt levam cerca de 24 h na busca [O] | ClaudeBot é treinamento. Claude-SearchBot indexa para a busca. Claude-User busca a pedido do usuário. Bloquear os dois últimos reduz visibilidade. Desde 30/10/2026 lê um sinal legível por máquina sobre treinamento, mas regra nominal ao ClaudeBot no robots.txt prevalece [O] | Googlebot rastreia para a Pesquisa. Google-Extended controla treinamento e grounding do Gemini Apps e Vertex, sem afetar inclusão ou ranking na Pesquisa. A inclusão nos recursos de IA também depende do controle "IA generativa na Pesquisa" do Search Console [O] | Bingbot rastreia. IndexNow avisa o Bing sobre URLs novas ou alteradas; o Google não participa do protocolo [I] |
| Origem da busca | "Provedores de busca de terceiros" e conteúdo de parceiros, sem nomes divulgados [O]. Estudos divergem: 87% das citações coincidiam com o topo do Bing no início de 2025 (Seer), o alinhamento com o Google subiu em 2025 (Profound), e outra medição achou só 11% a 12% de sobreposição com o top 10 (Ahrefs) [I] | Brave Search consta na lista de subprocessadores de busca desde março de 2025, segundo TechCrunch e Simon Willison [O, relatado] | Sistemas centrais de ranking da Pesquisa, com RAG e "query fan-out": várias buscas paralelas por subtema [O] | Índice do Bing, que alimenta o Copilot [O] |
| Dados locais | Parceiros de dados para mapas, sem nomes [O]. Fornecedores citam Yelp, Foursquare, Mapbox, Google Places e Tripadvisor, com resultados conflitantes [I]. App da Tripadvisor no ChatGPT [O, Tripadvisor] | O app móvel usa a localização e mostra lugares num mapa [O]. Conector da Tripadvisor desde 2026 [O, Tripadvisor]. Uso de Google Maps foi relatado por uma única fonte [I] | O Perfil da Empresa ajuda negócios locais a aparecer em respostas de IA [O]. A API oferece grounding com Google Maps, com mais de 250 milhões de lugares, avaliações, fotos e horários [O]. Ranking local por relevância, distância e proeminência, com peso para número e nota das avaliações [O] | Bing Places, relançado em outubro de 2025 em bing.com/forbusiness, com importação do Perfil da Empresa [I] |
| O que a plataforma diz que ajuda | Permitir OAI-SearchBot e usar noindex para excluir páginas [O] | Permitir Claude-SearchBot e Claude-User [O] | "Ainda é SEO": conteúdo único e rastreável, títulos claros, indexação com snippet. Não exige arquivos, marcação ou Markdown especiais. O `llms.txt` é ignorado. Criar páginas para variações de fan-out com intenção de manipular é abuso de conteúdo em escala [O] | Conteúdo atual, com autoridade, estruturado e claro. Título, descrição e H1 alinhados; perguntas e respostas, listas e tabelas; schema em JSON-LD; frases autocontidas. Não esconder respostas em abas ou menus expansíveis; não deixar fatos só em imagem ou PDF. Nada garante seleção [O] |
| Medição disponível | `utm_source=chatgpt.com` nos links [O]. Canal "AI Assistant" do GA4 desde maio de 2026 [I] | Referenciador claude.ai no GA4 | Relatório de desempenho de IA generativa no Search Console desde junho de 2026: impressões por página, país, dispositivo e data, sem consultas nem cliques [O] | Relatório AI Performance do Bing Webmaster Tools: citações no Copilot e nos resumos do Bing, sem cliques. Prévia desde fevereiro de 2026, com intenções e participação de citações desde 16/06/2026 [I] |
| Implicação para o Sir Fisher | Ranking em Google e Bing, listas locais, Tripadvisor | Ranking no Brave, Tripadvisor, listas locais | Perfil da Empresa, avaliações, ranking orgânico | Bing Webmaster Tools, IndexNow e Bing Places, hoje sem uso comprovado |

Sobre anúncios: a OpenAI publicou em janeiro de 2026 princípios segundo os
quais anúncios não influenciam as respostas, conforme relatos de terceiros;
o texto original não foi conferido nesta auditoria [I]. O teste de ChatGPT
Ads em andamento deve ser medido em separado do orgânico.

### 2.3 Evidência científica

| Referência | Tipo | O que mostra | Implicação para o Sir Fisher | Limites |
| --- | --- | --- | --- | --- |
| Aggarwal et al., "GEO: Generative Engine Optimization", KDD 2024 | C | No GEO-bench, citar fontes, incluir citações textuais e estatísticas elevou a visibilidade em até 40%, com efeito diferente por domínio | Fatos verificáveis e citáveis podem ajudar | Motor simulado, um só ator, sem domínio local; contestado pelo C-SEO Bench |
| Puerto et al., "C-SEO Bench: Does Conversational SEO Work?", NeurIPS 2025, trilha Datasets and Benchmarks | C | A maioria das técnicas de reescrita para IA foi ineficaz e muitas pioraram o resultado; SEO tradicional, que leva o documento ao contexto, funcionou melhor; o ganho encolhe quando todos adotam | Priorizar ser recuperado (ranking e menções), não reescrita estilística | Tarefas de perguntas e de produtos, sem negócio local |
| Chen, Wang, Chen e Koudas, "Generative Engine Optimization: How to Dominate AI Search", 2025 | P | Buscadores de IA preferem fortemente mídia conquistada (terceiros) a conteúdo da marca e redes sociais, com viés a favor de grandes marcas | Matérias e listas de terceiros pesam mais que o site em consultas amplas | Preprint; setores de consumo, não restaurantes |
| Kandpal et al., ICML 2023 | C | Exatidão sobre uma entidade acompanha o número de documentos de treinamento que a citam; recuperação reduz a dependência | Para cauda longa, a busca em tempo real decide | Perguntas factuais, não recomendações |
| Mallen et al., ACL 2023 | C | Aumentar o modelo melhora fatos populares; recuperação ajuda as entidades raras | Idem | Idem |
| Liu et al., "Lost in the Middle", TACL 2024 | C | Desempenho em forma de U conforme a posição da informação no contexto | Estar entre os primeiros resultados recuperados ajuda | Modelos de 2023; o efeito varia nos modelos atuais |
| Liu, Zhang e Liang, Findings of EMNLP 2023 | C | 51,5% das frases com apoio completo; 74,5% das citações apoiavam a frase | Monitorar exatidão, não só presença | Sistemas de 2023 |
| Nestaas, Debenedetti e Tramèr, ICLR 2025 | C | Ataques de manipulação de preferência funcionaram no Bing e no Perplexity; com vários atacantes, todos perdem presença | Manipulação é possível, arriscada e descartada | Cenário adversarial |
| Kumar e Lakkaraju, 2024 | P | Sequências de texto estratégicas aumentaram a chance de um produto fictício ser o primeiro recomendado | Idem | Catálogo fictício |
| Lewis et al., NeurIPS 2020 | C | Define a geração aumentada por recuperação (RAG) | Base conceitual das quatro plataformas | Arquitetura original, anterior aos buscadores atuais |

### 2.4 Estudos de indústria

| Estudo | O que relata | Uso nesta estratégia | Limites |
| --- | --- | --- | --- |
| SparkToro e Gumshoe, janeiro de 2026 | 2.961 execuções de 12 perguntas por 600 voluntários em ChatGPT, Claude e Google AI; listas quase nunca se repetem; o conjunto de marcas é mais estável que a ordem | Medir frequência por intenção, com repetições | Sem restaurantes locais; números conferidos por cobertura de terceiros |
| Seer (fev/2025), Profound (2025) e Ahrefs | Sobreposição entre citações do ChatGPT e buscadores varia de 11% a 87% conforme método e data | Trabalhar Google e Bing; não depender de um índice | Métodos incompatíveis entre si |
| BrightLocal | Pesquisa de 2026 com 1.002 adultos nos EUA: 45% usam IA para recomendações locais. Estudo de busca do ChatGPT com amostra de novembro de 2024: sites de empresas foram 58% das dez primeiras fontes; listas e matérias, 27%, contra 16% no Google | Reforça listas e matérias como fonte | Mercado americano; figuras de 2026 conferidas por cobertura de terceiros |
| Whitespark, Local Search Ranking Factors 2026 | 47 especialistas e 187 fatores; primeira categoria de visibilidade em IA; sinais da página e citações ganham peso; listas de "melhores" contam | Ordem de prioridade dos sinais locais | Levantamento de opinião, não experimento |
| Ahrefs, junho de 2026 | Em 137 mil domínios, 97% dos `llms.txt` não receberam nenhuma requisição em maio de 2026 | Não investir em `llms.txt` além do resumo atual | Um fornecedor, um mês |
| Vercel, dezembro de 2024 | Os principais robôs de IA baixam, mas não executam, JavaScript | Manter fatos no HTML inicial, como o site já faz | Medição de 2024 |
| SOCi, 2026 | Locais recomendados pelo ChatGPT tinham nota média 4,3; pelo Gemini, 3,9 | A nota do Sir Fisher no Google não é barreira; a do Tripadvisor pode ser | Fornecedor; amostra não descrita aqui |

### 2.5 Premissas populares e o que a evidência diz

| Crença comum | Evidência | Conclusão |
| --- | --- | --- |
| "GEO é outra disciplina, separada do SEO" | Google: ainda é SEO [O]. Microsoft: SEO tradicional é a base [O]. C-SEO Bench: SEO tradicional supera truques de reescrita [C] | GEO é SEO, reputação, dados locais e medição própria |
| "`llms.txt` faz a IA citar o site" | Google ignora o arquivo [O]; 97% dos arquivos sem requisição [I] | Manter como resumo barato, sem expectativa |
| "Schema garante citação" | Google: não é necessário para IA [O]. Microsoft: ajuda seus modelos a entender o conteúdo [O, relatado]. Brave exibe o FAQ do JSON-LD do site [E] | Higiene útil; não é a alavanca principal |
| "Basta reescrever tudo em perguntas e respostas" | Reescrita para IA foi ineficaz ou prejudicial no C-SEO Bench [C]; Microsoft recomenda o formato por clareza [O] | Escrever para clareza factual, sem esperar ganho de ranking |
| "Dá para medir a posição no ChatGPT" | Listas mudam a cada execução [I] | Medir frequência de menção, com repetições |
| "Liberar treinamento melhora a busca" ou "bloquear tira da busca" | Controles separados em OpenAI, Anthropic e Google [O] | Treinamento afeta só modelos futuros |
| "O ChatGPT usa o Bing" | Provedores não divulgados; medições conflitantes [O][I] | Trabalhar Google e Bing ao mesmo tempo |
| "Anunciar no ChatGPT melhora o orgânico" | OpenAI afirma independência, segundo relatos [I]; dados próprios mostram engajamento de 77% no orgânico contra 29% no pago [E] | Medir separado; não esperar efeito cruzado |
| "Mais páginas para cada variação de busca" | Google classifica como abuso de conteúdo em escala quando feito para manipular [O] | Enriquecer páginas existentes |
| "Para aparecer, é preciso estar no treinamento" | Cauda longa depende de recuperação [C] | Prioridade para busca, mapas e menções |

### 2.6 Livros e cursos

Não foi encontrado livro técnico revisado por pares específico de GEO. Os
livros comerciais de 2025 e 2026 sobre "SEO para IA" resumem práticas de
fornecedores e não foram usados como evidência. As obras abaixo dão a base
técnica para avaliar qualquer recomendação nova.

| Obra ou curso | Autoria, instituição e ano | Contribuição prática | Limitações |
| --- | --- | --- | --- |
| *Introduction to Information Retrieval* | Manning, Raghavan e Schütze; Cambridge University Press, 2008; versão online gratuita da Stanford | Indexação, ranqueamento e avaliação por precisão e revocação; base para desenhar o painel de medição | Anterior aos LLMs |
| *Search Engines: Information Retrieval in Practice* | Croft, Metzler e Strohman; Addison-Wesley, 2009; versão gratuita dos autores | Arquitetura de buscadores, rastreamento e processamento de consultas | Anterior à busca neural |
| *Pretrained Transformers for Text Ranking: BERT and Beyond* | Lin, Nogueira e Yates; Morgan & Claypool, 2021 | Reordenação neural de passagens, base da etapa de seleção | Técnico; anterior à geração com citação |
| *Speech and Language Processing*, 3ª edição em rascunho | Jurafsky e Martin; Stanford e Universidade do Colorado; atualizado continuamente | Capítulos de perguntas e respostas e de RAG | Rascunho em revisão |
| CS276, *Information Retrieval and Web Search* | Universidade Stanford | Curso de recuperação de informação com material público | Acadêmico, sem foco local |
| Documentação oficial | Google Search Central, Bing Webmaster Guidelines, OpenAI e Anthropic | Regras vigentes de rastreamento, elegibilidade e medição | Não revela algoritmos internos |

## 3. Diagnóstico do Sir Fisher

### 3.1 Linha de base

**Search Console, 08/08 a 05/11/2026, dados finais [E].** O grupo de
consultas comerciais sem marca, sem pôr do sol, somou 643 consultas
visíveis, 49 cliques e 12.447 impressões. A posição média nas consultas
centrais está no fim da primeira página, onde o painel local e os recursos
de IA ficam acima.

| Consulta | Cliques | Impressões | Posição média |
| --- | ---: | ---: | ---: |
| restaurante beira mar fortaleza | 9 | 1.607 | 7,7 |
| restaurantes beira mar fortaleza | 4 | 1.039 | 8,7 |
| restaurantes na beira mar fortaleza | 3 | 643 | 8,4 |
| best fish and chips near me | 0 | 579 | 6,3 |
| restaurante frutos do mar fortaleza | 1 | 392 | 10,2 |
| restaurante de frutos do mar em fortaleza | 0 | 211 | 9,5 |
| onde comer na beira mar fortaleza | 0 | 82 | 9,8 |
| melhores restaurantes beira mar fortaleza | 3 | 78 | 9,3 |
| restaurante com vista para o mar em fortaleza | 0 | 72 | 9,5 |
| almoço executivo fortaleza | 0 | 53 | 10,8 |
| melhores restaurantes fortaleza | 0 | 49 | 26,7 |

| Página | Cliques | Impressões | Posição média |
| --- | ---: | ---: | ---: |
| /por-do-sol/ | 266 | 89.657 | 5,1 |
| / (home) | 262 | 24.425 | 8,2 |
| /reveillon/ | 55 | 474 | 5,2 |
| /cardapio/ | 28 | 1.239 | 4,9 |
| /almoco-executivo/ | 8 | 348 | 8,7 |
| /guia/beira-mar/ | 5 | 1.677 | 9,3 |
| /jardim-japones/ | 3 | 881 | 8,6 |

O relatório de IA generativa do Search Console não tem API documentada. A
exportação anterior registrou 2.672 impressões em recursos de IA até 23/10
([acervo Semrush](SEMRUSH_3_DIAS_2026-10-25.md)). Em outubro, o domínio
apareceu como fonte de AI Overviews para buscas de pôr do sol.

**Perfil da Empresa, leitura de 09/11/2026 [E].** A ficha ativa está
completa e bem mantida.

| Item | Estado |
| --- | --- |
| Nome e status | "Sir Fisher", aberto |
| Categoria principal | Restaurante de frutos do mar |
| Categorias adicionais | Bar, Restaurante, Restaurante de peixe, Restaurante de almoço, Restaurante familiar, Restaurante britânico, Restaurante brasileiro, Restaurante especializado em fish and chips |
| Descrição | 732 caracteres, com endereço, pratos, almoço executivo, horários, reservas, grupos, pets e entrega |
| Atributos | 61, com links de cardápio, reserva, WhatsApp e redes |
| Avaliações | 819, média 4,70 |
| Ritmo recente | 32 novas em 30 dias (média 4,69), 41 em 90 dias e 97 em 365 dias; todas respondidas |
| Termos mais citados nas avaliações | atendimento (335), mar (169), vista (87), fish (57), pôr do sol (50), preço (48), pet (42) |
| Outras fichas da conta | "Sir Fisher - PUB" (Rua Frederico Borges, 336) e "Sir Fisher - Impresa" (Imprensa Food Square), ambas encerradas definitivamente |

**Observações anteriores nas plataformas reais (Semrush, outubro de 2026).**
Em 14/10, uma resposta do ChatGPT citou o Sir Fisher para jantar após
passeio na orla. Em 27/10, duas perguntas em português deixaram de citar a
casa, almoço com preço e jantar com cardápio, enquanto quatro em inglês
continuaram citando. Em 30/10, as fontes mais citadas pelo ChatGPT nas
perguntas monitoradas foram iFortaleza (15 perguntas), O POVO (12),
IndicoMais (11), Sabores da Cidade e Restaurant Guru (5). No Maps, a casa
ficava fora do top 20 em cerca de 86% dos pontos da grade para termos
amplos ([relatório](SEMRUSH_MAXIMO_2026-10-25.md)).

### 3.2 Acesso de robôs

A configuração foi lida pela API do Cloudflare, somente com GET, em
09/11/2026 [E]. O plano é Free. O objeto Bot Management tem
`ai_training=disallow`, `ai_search=disabled`, `ai_user=disabled`,
`ai_bots_protection=only_on_ad_pages`, Bot Fight Mode desligado e robots.txt
gerenciado desligado. A regra "Robos IA: leitura das paginas publicas" pula
a fase de bloqueio para 31 agentes, mas só em 15 caminhos fixos.

Teste com agentes declarados, feito de uma conexão residencial em Fortaleza
na mesma data, em 23 caminhos [E]:

| Agente | Finalidade | 15 caminhos da regra | Jardim Japonês, Conheça, `llms.txt`, /en/menu/ | Imagens em /assets/ |
| --- | --- | --- | --- | --- |
| GPTBot e ClaudeBot | Treinamento | 200 | 403 | 403 |
| CCBot e Amazonbot | Treinamento e coleta | 200 em / e /cardapio/ | 403 em Jardim Japonês e `llms.txt` | Não testado |
| OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User | Busca e pedidos de usuários | 200 | 200 em Jardim Japonês e `llms.txt` | Não testado |
| Googlebot, bingbot, Applebot, DuckDuckBot, meta-externalagent | Buscadores e outros | 200 | 200 em Jardim Japonês e `llms.txt` | Não testado |

O robots.txt registra que o proprietário autorizou em 25/10 o rastreamento
público, inclusive para treinamento. A borda contradiz essa decisão nos
caminhos que não entraram na regra: o Jardim Japonês, criado em 27/10, o
`llms.txt` e as imagens. Robôs de busca e de usuário não são afetados,
então as respostas atuais não perdem acesso. O teste usa agentes declarados
a partir de um IP comum; os IPs reais dos robôs podem ser tratados de outra
forma pelo Cloudflare, mas a configuração lida explica o padrão observado.

### 3.3 Estrutura, indexabilidade e dados estruturados

| Item | Estado em 09/11/2026 | Avaliação |
| --- | --- | --- |
| HTML e renderização | Páginas estáticas no GitHub Pages, atrás do Cloudflare; textos, preços e cardápio no HTML inicial | Favorável para robôs que não executam JavaScript [I] |
| robots.txt e sitemap | Tudo liberado; 13 URLs com `lastmod` e hreflang PT/EN | Correto |
| Canonical, hreflang e redirecionamentos | Canonicals próprios; domínio sem www e http redirecionam com 301 para https://www | Correto |
| Desempenho, celular e acessibilidade | PageSpeed 100 nas quatro categorias, inclusive acessibilidade, em celular e desktop em 25/10; dados de campo com LCP 1,6 s, INP 148 ms e CLS 0 | Correto |
| Restaurant em JSON-LD | Home PT, home EN e Conheça, com endereço, coordenadas, horários, cozinhas, faixa de preço, cardápio, reserva, perfis e comodidades | Bom. Menu, FAQ e Event não referenciam o `@id` do restaurante |
| Menu em JSON-LD | 80 itens e 86 ofertas no cardápio; 7 itens no almoço executivo | Muito bom |
| FAQPage | 87 perguntas em 12 páginas; 18 com a pergunta visível; 61 com a resposta coberta pelo texto visível; parte do JSON-LD sem acentos | Fora das diretrizes do Google, que exigem conteúdo visível. O resultado enriquecido de FAQ é restrito desde 2023 a sites de governo e saúde, mas o Brave usa esse conteúdo |
| Event do Réveillon | Local nomeado "Sir Fisher Praia" | Diverge do nome da entidade |
| Capacidade | `maximumAttendeeCapacity` 99, enquanto o texto de eventos diz até 100 sentados | Pequena incoerência |
| WebSite e Organization | Ausentes | Impacto baixo |
| aggregateRating | Ausente | Correto. Avaliações autogeridas de negócio local não são elegíveis, e copiar a nota do Google violaria as diretrizes |
| `llms.txt` | Publicado, com 2.483 bytes; bloqueado a GPTBot e ClaudeBot | Impacto esperado baixo |
| Bing Webmaster Tools e IndexNow | Sem evidência de verificação, chave ou envio no repositório e na documentação | Lacuna |
| Search Console | Domínio verificado; inclusão nos recursos de IA confirmada em outubro | Correto |
| Portal de reservas | Indexável; título "Reservar mesa no Sir Fisher Praia"; robots.txt bloqueia só administração e cancelamento | Nome diverge |
| Página "Sobre" | Não existe página indexável sobre a casa; Conheça é destino de anúncio com `noindex` por decisão anterior | Lacuna de entidade |

### 3.4 Conteúdo e autoridade

O site cobre as perguntas que as pessoas fazem às IAs: localização, horário,
cardápio com preços, almoço executivo, fish and chips, reservas, grupos,
eventos, pets, pôr do sol, rota e Jardim Japonês, em português e inglês. A
cobertura factual é melhor que a dos concorrentes observados.

A fragilidade está fora do site. Em toda a pesquisa, apareceram só duas
matérias sobre a casa: o guia de quiosques da Beira-Mar do Diário do
Nordeste (15/11/2023) e uma lista de happy hour de 01/08/2025 que cita o
"Sir Fisher Pub", unidade hoje encerrada. A primeira matéria é a que leva o
Sir Fisher às respostas de pôr do sol e fish and chips no teste da seção
3.7. Concorrentes conseguiram pautas recentes para as mesmas ofertas: o
Coco Bambu Meireles teve matéria sobre almoço executivo no Diário do
Nordeste em novembro de 2025, e o NOM teve pautas de executivo (IndicoMais,
agosto de 2026) e de eventos corporativos (TV Nordeste Vip).

A página de pôr do sol é o maior ativo de descoberta do domínio, com 89.657
impressões em 90 dias. Ela funciona como material de referência que
jornalistas e guias podem citar.

### 3.5 Consistência da entidade fora do site

Leituras de 09/11/2026 [E]. O celular pessoal do proprietário não é
reproduzido aqui, por regra do projeto.

| Fonte | Nome publicado | Problema encontrado | Prioridade |
| --- | --- | --- | --- |
| Perfil da Empresa | Sir Fisher | Nenhum | Referência |
| Site | Sir Fisher | Réveillon usa "Sir Fisher Praia" | Média |
| Portal de reservas | Sir Fisher Praia | Nome diferente da ficha e do site | Média |
| Tripadvisor | Sir Fisher, com "Barra_Sol_Sir_Fisher" no endereço da página | Categoria "bares e pubs", 11 avaliações, nota 3,9; leitura automatizada bloqueada | Alta |
| OpenStreetMap, nó 10601139599 | Barra Sol Sir Fisher | Tipo `fast_food`; horário de 2023 (terça a domingo 9h–23h; segunda 11h–23h) | Alta |
| Restaurant Guru | Sir Fisher, com "Barra-Sol" no endereço da página | Categorias incluem churrasco e comida de rua; mostra Google 4,7 com 817 avaliações e posição 274 entre 17.208 restaurantes da cidade | Média |
| Bendito Guia | Barra Sol - Sir Fisher Mucuripe | Celular pessoal do proprietário como telefone; site aponta para linktr.ee; sem horário; texto gerado automaticamente | Alta |
| Duo Gourmet | Sir Fisher, com "sir-fischer" no endereço da página | Horário só de segunda a sexta, 10h–14h30, possivelmente o horário do benefício | Média |
| Comida di Buteco | Sir Fisher, Av. Beira Mar, 3421, B14 | Horário antigo (segunda 11h–22h; terça e quarta 9h–22h; quinta a domingo 9h–22h30) | Média |
| iFood | Três fichas indexadas: "Sir Fisher - Fish & Chip Mucuripe", "Sir Fisher Imprensa Dionísio Torres" e "Sir Fisher Pub Meireles" | Duas são de unidades encerradas; páginas bloquearam leitura automatizada, então o status não foi conferido; o Perfil da Empresa informa entregas pelo 99Food | Alta |
| Diário do Nordeste, 15/11/2023 | Sir Fisher, "Sir Fischer" no quadro de serviço | Quiosque "aberto todos os dias, de 9h às 23h" | Baixa |
| Diário do Nordeste, 01/08/2025 | Sir Fisher Pub, Rua Frederico Borges, 336 | Correto na data, mas a unidade foi encerrada | Desambiguar no site |
| iReserve | Sem nome; endereço correto | Página antiga de reserva ainda no ar, com o texto "esse site aqui" | Baixa |
| Hubt | "Sir Fisher Praia" só no endereço da página | Página despublicada, ainda indexada | Baixa |
| Visiter Fortaleza | Indexada | Responde 404 | Nenhuma ação |

### 3.6 Concorrência

Presença nas sete listas lidas em 09/11/2026: iFortaleza Beira-Mar (sem
data), IndicoMais vista para o mar (04/2026), Viajali 25 melhores
(07/2026), Saipos Beira-Mar (07/2023), Accor (02/2025), O POVO vista
(02/2024) e Sabores da Cidade vista (01/2026) [E].

| Casa | Listas, de 7 | Avaliações públicas | Observação |
| --- | ---: | --- | --- |
| Illa Mare | 5 | Cerca de 4,6 mil, nota 4,5 (Wanderlog) | Mais citado para vista e pôr do sol; mesmo grupo do NOM |
| Coco Bambu Beira Mar | 4 | Cerca de 26,7 mil, nota 4,7 (Wanderlog) | Mais citado para frutos do mar; a rede teve pauta de executivo na unidade Meireles em 11/2025 |
| Mercado dos Peixes | 4 | Não levantado | Mercado com boxes, citado como opção "autêntica" |
| Geppos Beira Mar | 4 | Não levantado | Italiano na orla |
| Vistta Rooftop, Zói e Vignoli | 3 cada | Não levantado | Vista ou orla |
| Siá, Esttaleiro, Gran Marquise, Beira Mar Grill e Boteco Praia | 2 cada | Não levantado | Rooftops e orla |
| **Sir Fisher** | **0** | **819, nota 4,70 (Perfil da Empresa)** | Citado só no guia de quiosques de 2023 |

Os números do Wanderlog servem para dar escala, não para comparação exata.
No Tripadvisor, o Ponza Frutos do Mar aparece com 4,9 e 603 avaliações,
contra 3,9 e 11 do Sir Fisher. Illa Mare e Coco Bambu separam cardápio,
reservas e eventos em páginas próprias, como o Sir Fisher já faz.

### 3.7 Testes de recuperação executados

Os testes abaixo foram executados de fato em 09/11/2026, uma vez por
consulta. Eles mostram a camada de busca, não a resposta final de cada
aplicativo.

**Brave Search, país Brasil.** Relatos públicos associam o Brave à busca do
Claude. Não se sabe se o Claude repassa o país ao Brave [E].

| Consulta | Site no top 12 | Melhor posição | Outras páginas sobre o Sir Fisher | Observação |
| --- | --- | ---: | --- | --- |
| fish and chips fortaleza | Sim | 1 (também 2 e 3) | iFood (três fichas, duas de unidades encerradas), Comida di Buteco, Tripadvisor, Hubt | Cartão com telefone e endereço; "As pessoas também perguntam" usa o FAQ do JSON-LD do site |
| restaurante beira mar fortaleza | Sim | 2 | Nenhuma | Atrás da lista da Saipos |
| melhores restaurantes beira mar fortaleza | Não | – | Vídeo do YouTube de 2025 que cita o almoço com vista | Top 12 só com listas, nenhuma com o Sir Fisher; no módulo local, com dados do Tripadvisor, a casa aparece depois de dezenas de concorrentes |
| por do sol fortaleza restaurante | Não | – | Nenhuma | Dominado por casas chamadas "Pôr do Sol" |
| sir fisher fortaleza | Sim | 1 | Tripadvisor (Barra Sol), Instagram, portal, Duo Gourmet, iReserve, Restaurant Guru (Barra Sol), Facebook, iFood, Comida di Buteco | Entidade fragmentada |

**Ferramenta de busca deste ambiente, localizada nos EUA.** É a busca usada
pelo Claude Code, não o claude.ai de consumo [E].

| Consulta | Sir Fisher citado | Fonte que levou à citação |
| --- | --- | --- |
| melhores restaurantes Beira-Mar Fortaleza onde comer | Não | – |
| restaurante frutos do mar Fortaleza onde comer peixe | Não | – |
| restaurante com vista para o mar em Fortaleza | Não | – |
| restaurante para ver o pôr do sol em Fortaleza Beira-Mar | Sim, terceira de seis opções | Diário do Nordeste, 2023 |
| fish and chips Fortaleza | Sim, primeira opção | Diário do Nordeste, 2023 |
| onde comer perto do Jardim Japonês Fortaleza | Indireto, como "quiosque de comida londrina" | Diário do Nordeste, 2023 |
| almoço executivo Beira Mar Fortaleza preço | Não; aparece o Coco Bambu Meireles | – |
| best seafood restaurant Fortaleza Brazil beachfront | Não | – |
| Sir Fisher restaurante Fortaleza Beira Mar | Sim | Site, Restaurant Guru, Duo Gourmet, Wanderboat, Bendito Guia |

A comparação mostra dois efeitos. A localização muda a recuperação: o site
aparece no Brave Brasil e não na busca localizada nos EUA. E, fora das
buscas pela marca, uma única matéria de terceiros sustenta as menções.

Uma leitura direta do Bing devolveu resultados sem relação com as consultas
para um cliente automatizado e foi descartada como evidência. A presença no
Bing precisa ser conferida pelo Bing Webmaster Tools.

### 3.8 Pontos fortes

- Localização de frente para o mar, em frente ao Jardim Japonês, com
  pôr do sol citado por avaliações e imprensa.
- Oferta diferenciada e fácil de citar: fish and chips de pescada amarela.
- Perfil da Empresa completo, com nota 4,70 e todas as avaliações
  respondidas.
- Site rápido, estático, bilíngue, com cardápio e preços no HTML e dados
  estruturados de restaurante e cardápio.
- ChatGPT orgânico já trazendo tráfego engajado e crescente.
- Página de pôr do sol com grande exposição, útil como referência para
  terceiros.
- Medição de origem até reserva e comparecimento já montada no GA4 e no
  banco.

## 4. Plano de ação priorizado

### 4.1 Mapa de ações

Mecanismo indica o que a ação muda. **Elegibilidade** permite ser
encontrado, sem garantir escolha. **Seleção** aumenta a chance de ser
escolhido. **Exatidão** corrige o que a IA diz. **Medição** permite saber
se funcionou.

| ID | Ação | Mecanismo | Plataformas | Impacto | Confiança | Esforço | Custo | Prazo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QW1 | Liberar robôs de treinamento em todo o conteúdo público no Cloudflare | Elegibilidade (treinamento) | ChatGPT e Claude (modelos futuros) | Baixo agora | Alta | Mínimo | Zero | Semana 1 |
| QW2 | Bing Webmaster Tools, sitemap e IndexNow | Elegibilidade e Medição | Copilot; ChatGPT em parte | Médio | Alta | Baixo | Zero | Semana 1 |
| QW3 | Bing Places, Apple Business Connect e Foursquare | Elegibilidade e Exatidão | Copilot; Siri e Apple Mapas; mapas de terceiros | Médio | Média | Baixo | Zero | Semanas 1 e 2 |
| QW4 | Corrigir fichas externas com dados errados | Exatidão | Todas | Médio | Alta | Baixo | Zero | Semanas 1 a 4 |
| QW5 | Encerrar ou corrigir as unidades antigas no iFood | Exatidão | Todas | Médio | Alta | Baixo | Zero | Semana 2 |
| QW6 | Corrigir a ficha do Tripadvisor | Exatidão e Seleção | ChatGPT, Claude, Brave e Apple | Alto | Alta | Baixo | Zero | Semana 1 |
| QW7 | Onda 0 do painel e exportações de linha de base | Medição | Todas | Indireto | Alta | Baixo | Baixo | Semana 1, antes das mudanças |
| ES1 | FAQ visível gerado da mesma fonte do JSON-LD | Seleção e conformidade | Copilot, Google, Brave | Baixo a médio | Alta | Baixo | Zero | Semanas 2 a 4 |
| ES2 | Nome único e entidade conectada nos dados estruturados | Exatidão | Todas | Baixo a médio | Média | Baixo | Zero | Semanas 2 a 4 |
| ES3 | Desambiguação das unidades encerradas e de "Barra Sol" | Exatidão | Todas | Médio | Média | Baixo | Zero | Semanas 2 a 4 |
| ES4 | Páginas "Sobre" e "Na imprensa" indexáveis | Seleção e Exatidão | Todas | Médio | Média | Médio | Zero | Semanas 3 a 6 |
| ES5 | Fatos comparáveis e datas de atualização nas páginas existentes | Seleção | Todas | Médio | Média | Médio | Zero | Semanas 3 a 8 |
| AU1 | Imprensa e listas locais com pautas verdadeiras | Seleção | Todas | Alto | Média a alta | Médio | Baixo | Novembro a janeiro, contínuo |
| AU2 | Programa contínuo de avaliações no Google e no Tripadvisor | Seleção | Gemini, IA do Google, Copilot, ChatGPT e Claude | Alto | Média a alta | Contínuo | Zero | Contínuo |
| AU3 | Parcerias com hotéis e guias turísticos em PT e EN | Seleção | Todas | Médio | Média | Médio | Baixo | Meses 2 a 4 |
| AU4 | Conteúdo orgânico de terceiros e Instagram factual | Seleção | Todas, em parte | Baixo a médio | Baixa a média | Contínuo | Zero a baixo | Contínuo |
| EX1 | Painel GEO mensal em quatro plataformas | Medição | Todas | Indireto | Alta | Médio | Baixo | Mensal |
| EX2 | Teste escalonado do FAQ visível por grupo de páginas | Medição | Copilot, Google | Indireto | Média | Baixo | Zero | Meses 1 a 3 |
| EX3 | Efeito de cada matéria publicada | Medição | Todas | Indireto | Média | Baixo | Zero | A cada matéria |
| EX4 | Teste de título e descrição da home para "frutos do mar" | Seleção | Google e Bing | Baixo a médio | Baixa | Baixo | Zero | Meses 2 e 3 |
| EX5 | Conhecimento sem busca em novas versões de modelos | Medição | ChatGPT, Claude, Gemini | Indireto | Média | Baixo | Zero | A cada lançamento |
| EX6 | Reservas por agentes de IA | Elegibilidade futura | ChatGPT e IA do Google | Incerto | Baixa | Médio | A definir | Monitorar |

### 4.2 Fichas das ações

#### QW1. Liberar robôs de treinamento em todo o conteúdo público

- **O que fazer:** alinhar a borda do Cloudflare à decisão de 25/10, para
  que GPTBot, ClaudeBot e os demais robôs de treinamento leiam todas as
  páginas públicas, o `llms.txt` e as imagens.
- **Por que pode funcionar:** amplia o material disponível para versões
  futuras dos modelos e remove uma contradição entre o robots.txt e a borda.
- **Plataformas:** modelos futuros da OpenAI, da Anthropic e de outros
  coletores. Não muda a busca atual.
- **Evidência:** configuração lida pela API e teste com agentes [E];
  controles separados de busca e treinamento [O]; efeito da presença no
  treinamento sobre entidades raras [C].
- **Como implementar:** a opção A, preferida, é mudar o campo `ai_training`,
  hoje `disallow`, para o valor de liberação aceito pela API de Bot
  Management, seguindo o padrão do comando `robots` do `cf.py`: ler, alterar
  um campo, gravar e reler. A opção B é tirar a lista de caminhos da regra
  "Robos IA", mantendo host `www`, métodos GET e HEAD e a lista de agentes.
  A opção B continua frágil, porque depende de nomes de agentes.
- **Como verificar:** repetir a matriz da seção 3.2 em todas as URLs do
  sitemap, no `llms.txt` e em três imagens, esperando 200. Conferir os
  eventos de segurança e, se disponível no plano Free, o painel de robôs de
  IA. Acrescentar uma checagem semanal ao fluxo de qualidade do site, ciente
  de que IPs de datacenter podem receber outro tratamento.
- **Riscos e dependências:** uso do conteúdo em treinamento, já autorizado;
  tráfego irrelevante para um site estático. Reversível. Requer confirmação
  do proprietário, porque altera configuração externa.

#### QW2. Bing Webmaster Tools, sitemap e IndexNow

- **O que fazer:** verificar o domínio no Bing Webmaster Tools importando a
  propriedade do Search Console, enviar o sitemap e ativar o IndexNow.
- **Por que pode funcionar:** o Copilot usa o índice do Bing, e o IndexNow
  acelera a atualização de preços, horários e páginas sazonais.
- **Plataformas:** Copilot e resumos do Bing; ChatGPT em parte, conforme os
  estudos de sobreposição.
- **Evidência:** índice do Bing alimenta o Copilot [O]; relatório AI
  Performance [I]; sobreposição do ChatGPT com o Bing [I].
- **Como implementar:** no Bing Webmaster Tools, usar a importação do Google
  Search Console e escolher `sc-domain:sirfisher.com.br`. Para o IndexNow,
  publicar na raiz um arquivo `<chave>.txt` com a chave e, a cada
  publicação, enviar a `api.indexnow.org` as URLs cujo `lastmod` mudou, por
  um passo no workflow do site ou um script local.
- **Como verificar:** propriedade verificada, sitemap processado, envios do
  IndexNow aceitos e primeiros dados no relatório AI Performance.
- **Riscos e dependências:** nenhum relevante. O Google não usa IndexNow, e
  o Search Console continua necessário.

#### QW3. Bing Places, Apple Business Connect e Foursquare

- **O que fazer:** reivindicar a ficha no Bing Places, importando do Perfil
  da Empresa; conferir e reivindicar o cartão no Apple Business Connect, se
  disponível no Brasil; procurar e reivindicar a ficha no Foursquare.
- **Por que pode funcionar:** o Copilot responde perguntas locais com dados
  do Bing Places [I]. Mapas de terceiros usados por assistentes combinam
  bases como Foursquare e Tripadvisor [I].
- **Plataformas:** Copilot; Siri e Apple Mapas; mapas embutidos em
  assistentes.
- **Evidência:** relançamento do Bing Places com importação [I]; o Apple
  Business Connect controla o cartão do lugar no Mapas, na Carteira e na
  Siri [O]; disponibilidade no Brasil não confirmada.
- **Como implementar:** em bing.com/forbusiness, importar a ficha e conferir
  categorias, horário regular e de 31/12, links de cardápio e reserva e
  fotos. Repetir no Apple Business Connect com uma conta Apple da empresa.
- **Como verificar:** cartão correto no Bing Maps e no Apple Mapas; resposta
  do Copilot a "Sir Fisher Fortaleza horário" correta no painel.
- **Riscos e dependências:** login do proprietário; manter os dados
  sincronizados quando o Perfil da Empresa mudar.

#### QW4. Corrigir fichas externas com dados errados

- **O que fazer:** corrigir nome, tipo, horário, telefone e site nas fontes
  da seção 3.5.
- **Por que pode funcionar:** assistentes cruzam fontes, e dados
  divergentes produzem respostas erradas ou reduzem a confiança na entidade.
- **Plataformas:** todas.
- **Evidência:** divergências medidas [E]; consistência de dados como base
  do ranking local [I]; baixa exatidão das citações em buscadores
  generativos [C].
- **Como implementar:**
  - OpenStreetMap: com uma conta, editar o nó 10601139599 para
    `name=Sir Fisher`, `amenity=restaurant`,
    `cuisine=seafood;fish_and_chips;british`,
    `opening_hours=Su-Th 09:00-22:15; Fr,Sa 09:00-23:00`, CEP 60165-121 e
    `check_date` atual, sem texto promocional.
  - Restaurant Guru: reivindicar a ficha, retirar churrasco e comida de rua
    e apontar o link direto do site.
  - Bendito Guia: pedir a troca do celular pessoal pelo telefone
    corporativo, do nome e do site. Se não houver resposta, exercer o
    direito de correção de dado pessoal previsto no art. 18 da LGPD.
  - Duo Gourmet: confirmar se o horário exibido é o do benefício e pedir o
    rótulo correto ou o horário completo.
  - Comida di Buteco: pedir a atualização do horário.
  - iReserve e Hubt: pedir remoção ou redirecionamento ao portal.
  - Diário do Nordeste, 2023: pedido opcional de correção do nome no quadro
    de serviço. Não pedir mudança na matéria do Pub, que estava correta.
- **Como verificar:** checklist mensal das fontes com nome, telefone,
  endereço e horário; perguntas de exatidão F1 a F5 do painel.
- **Riscos e dependências:** terceiros podem não responder. Não usar
  serviços pagos de sincronização sem decisão própria.

#### QW5. Encerrar ou corrigir as unidades antigas no iFood

- **O que fazer:** no portal do parceiro do iFood, encerrar as lojas do Pub
  e do Imprensa e decidir o destino da ficha "Fish & Chip Mucuripe".
- **Por que pode funcionar:** páginas de lojas encerradas, indexadas com o
  nome da marca, alimentam respostas com endereços errados.
- **Plataformas:** todas.
- **Evidência:** três fichas indexadas no Brave [E]; status não conferido
  por bloqueio de leitura.
- **Como implementar:** encerrar no portal; se as entregas ficaram só no
  99Food, encerrar também a terceira ficha ou corrigir nome e bairro. Fazer o
  mesmo com perfis sociais do Pub que ainda existam, apontando o perfil
  ativo e o endereço da Beira-Mar.
- **Como verificar:** fichas fora do ar ou marcadas como encerradas; pergunta
  F5 do painel sem menção ao Pub como ativo.
- **Riscos e dependências:** login do proprietário; decisão comercial sobre o
  canal de entrega.

#### QW6. Corrigir a ficha do Tripadvisor

- **O que fazer:** aplicar os passos já documentados em
  [SEMRUSH_MAXIMO](SEMRUSH_MAXIMO_2026-10-25.md): tipo restaurante;
  culinárias frutos do mar, peixe, brasileira e britânica; almoço e jantar;
  faixa média; site oficial; nome sem "Barra Sol"; conferir o pino no mapa.
- **Por que pode funcionar:** a Tripadvisor está integrada ao ChatGPT e ao
  Claude e fornece os dados locais exibidos pelo Brave.
- **Plataformas:** ChatGPT, Claude, Brave e possivelmente Apple Mapas.
- **Evidência:** integrações [O, Tripadvisor]; módulo local do Brave [E];
  ficha com 11 avaliações e categoria errada [E].
- **Como implementar:** painel de proprietário da ficha `d23922740`.
- **Como verificar:** categoria e dados corretos na ficha e no Restaurant
  Guru, que exibe a nota do Tripadvisor.
- **Riscos e dependências:** login do proprietário. O endereço da página
  pode manter o texto antigo mesmo após a troca do nome.

#### QW7. Onda 0 do painel e exportações de linha de base

- **O que fazer:** rodar a primeira onda do painel da seção 5 antes das
  outras mudanças e exportar o relatório de IA do Search Console.
- **Por que pode funcionar:** sem linha de base, nenhuma mudança poderá ser
  avaliada.
- **Plataformas:** todas.
- **Evidência:** volatilidade das respostas [I].
- **Como implementar:** protocolo da seção 5.1; dados brutos em
  `gestao/tmp/geo/`, ignorado pelo Git.
- **Como verificar:** planilha da onda 0 completa, com as quatro
  plataformas e os controles.
- **Riscos e dependências:** tempo de quem executa; sem navegador, a coleta
  nos aplicativos precisa ser manual ou pela camada de API.

#### ES1. FAQ visível gerado da mesma fonte do JSON-LD

- **O que fazer:** exibir na página cada pergunta e resposta marcada no
  FAQPage, com o mesmo texto e acentos, gerando HTML e JSON-LD de um único
  arquivo de dados. Respostas-chave devem ficar visíveis sem clique.
- **Por que pode funcionar:** o Google exige conteúdo visível; a Microsoft
  recomenda perguntas e respostas e desaconselha esconder respostas em
  menus expansíveis; o Brave já exibe esse conteúdo.
- **Plataformas:** Copilot, Google e Brave.
- **Evidência:** diretrizes [O]; contagem de 87 perguntas e 18 visíveis [E];
  exibição no Brave [E].
- **Como implementar:** no repositório `site`, criar o arquivo de dados por
  página, o gerador e a verificação no pre-commit, no mesmo padrão dos
  geradores de `tools/`. Manter o JSON-LD.
- **Como verificar:** checagem automática que compara JSON-LD e texto
  visível; validador de dados estruturados; teste escalonado EX2.
- **Riscos e dependências:** páginas mais longas no celular; resolver com
  blocos curtos. Ganho de ranking não comprovado: a ação é de conformidade e
  clareza.

#### ES2. Nome único e entidade conectada

- **O que fazer:** usar "Sir Fisher" como nome público no portal e no
  Réveillon; ligar Menu, FAQPage e Event ao `@id` do restaurante; acrescentar
  WebSite com o nome; alinhar a capacidade a 100 pessoas ou explicar a
  diferença.
- **Por que pode funcionar:** nomes diferentes dividem as menções em mais de
  uma entidade; ligações por `@id` deixam explícito que cardápio, perguntas e
  evento pertencem à mesma casa.
- **Plataformas:** todas; a Microsoft afirma usar schema em seus modelos [O,
  relatado].
- **Evidência:** variações encontradas [E]; benefício para a resolução da
  entidade [H].
- **Como implementar:** títulos e textos públicos do `reservas` (página
  inicial e Réveillon) e o JSON-LD do Réveillon no `site`, com
  `"location": {"@id": "https://www.sirfisher.com.br/#restaurante"}`.
- **Como verificar:** busca por "Sir Fisher Praia" sem ocorrências públicas;
  validador sem erros.
- **Riscos e dependências:** decisão do proprietário sobre o nome.

#### ES3. Desambiguação das unidades encerradas e de "Barra Sol"

- **O que fazer:** publicar, no site e na página "Sobre", a pergunta "O Sir
  Fisher tem outras unidades?", respondendo que as unidades da Rua Frederico
  Borges e do Imprensa Food Square foram encerradas e que a casa funciona na
  Av. Beira Mar, 3421.
- **Por que pode funcionar:** a matéria do Pub e as fichas do iFood seguem
  indexadas, e um texto explícito da fonte oficial ajuda a separar as
  entidades.
- **Plataformas:** todas.
- **Evidência:** fontes indexadas com unidades encerradas [E]; efeito sobre
  as respostas [H].
- **Como implementar:** se "Barra Sol" for nome antigo da casa, citar uma vez
  na página "Sobre"; se for erro de terceiros, não citar e pedir correção.
- **Como verificar:** pergunta F5 do painel.
- **Riscos e dependências:** confirmação dos fatos pelo proprietário.

#### ES4. Páginas "Sobre" e "Na imprensa"

- **O que fazer:** criar páginas indexáveis com a história da casa, o
  conceito do fish and chips, a origem da pescada amarela, a descrição
  correta do espaço, capacidade, acessibilidade, pets, participação no
  Comida di Buteco com o ano confirmado e lista de matérias com links.
  Incluir material de imprensa com fotos, créditos e contato.
- **Por que pode funcionar:** dá à IA e aos jornalistas uma fonte oficial
  sobre quem é a casa e liga o site às menções de terceiros.
- **Plataformas:** todas.
- **Evidência:** diretrizes de conteúdo útil do Google [O]; papel das
  menções de terceiros [P][I].
- **Como implementar:** página nova `/sobre/` e seção `/imprensa/`, com
  Restaurant referenciado por `@id`. A página Conheça continua com `noindex`.
- **Como verificar:** indexação no Search Console e no Bing; perguntas de
  exatidão do painel.
- **Riscos e dependências:** fatos e datas confirmados pelo proprietário;
  não publicar prêmios sem fonte verificável.

#### ES5. Fatos comparáveis e datas de atualização

- **O que fazer:** acrescentar às páginas existentes os fatos que as pessoas
  usam para comparar: faixa de gasto por pessoa, pratos mais pedidos,
  melhor horário para a vista, acessibilidade (mesas acessíveis e banheiro
  sem adaptação), crianças, pets, estacionamento e opções vegetarianas.
  Mostrar "Atualizado em" nas páginas com preço e horário, e manter o
  Réveillon atual.
- **Por que pode funcionar:** perguntas como "barato", "com crianças" ou
  "acessível" pedem fatos que a IA só cita se estiverem publicados.
- **Plataformas:** todas.
- **Evidência:** recomendações de clareza da Microsoft [O]; ganho com dados
  e citações no GEO-bench [C], contestado pelo C-SEO Bench [C].
- **Como implementar:** faixa de gasto calculada com dados agregados de
  venda, sem expor dados financeiros brutos e com aprovação do proprietário.
  O Réveillon é a segunda página de entrada vinda do ChatGPT e deve refletir
  o estado real da venda.
- **Como verificar:** perguntas D9, D14 e F4 do painel; impressões das
  páginas no Search Console.
- **Riscos e dependências:** não criar páginas novas para cada variação de
  busca, o que o Google trata como abuso.

#### AU1. Imprensa e listas locais

- **O que fazer:** levar pautas verdadeiras às fontes que as IAs citam e às
  listas em que os concorrentes aparecem.
- **Por que pode funcionar:** é a frente com maior efeito esperado nas
  consultas amplas. A única matéria existente já leva a casa a duas
  respostas no teste.
- **Plataformas:** todas.
- **Evidência:** preferência por mídia conquistada [P]; peso de listas e
  matérias nas fontes do ChatGPT [I]; fontes citadas em outubro [E]; teste
  de recuperação [E].
- **Como implementar:**
  - Fontes prioritárias: Diário do Nordeste (Verso), O POVO, Sabores da
    Cidade, IndicoMais, iFortaleza, Conexão 085, Viajali e Guia da Semana.
  - Pautas: fish and chips de pescada amarela na Beira-Mar; mesas para o
    pôr do sol, com a tabela de horários como referência; almoço executivo
    de R$ 31 a R$ 52; confraternizações de 30 a 100 pessoas com
    configurador; Réveillon de frente para o mar.
  - Os textos de pauta já preparados em
    [SEMRUSH_MAXIMO](SEMRUSH_MAXIMO_2026-10-25.md) servem de base.
  - Novembro e dezembro são a janela das pautas de fim de ano e alta
    estação.
- **Como verificar:** novas matérias com fatos corretos; presença nas listas;
  painel antes e depois de cada publicação (EX3).
- **Riscos e dependências:** aprovação do proprietário para cada envio.
  Conteúdo pago precisa ser identificado como publicidade (CDC, art. 36;
  Código do CONAR, art. 28).

#### AU2. Programa contínuo de avaliações

- **O que fazer:** manter pelo menos 40 avaliações novas por mês no Google e
  levar o Tripadvisor a 50 avaliações, pedindo a todos os clientes, sem
  filtro e sem vantagem.
- **Por que pode funcionar:** número e nota das avaliações entram no ranking
  local do Google; o Tripadvisor alimenta duas das quatro plataformas e o
  Brave.
- **Plataformas:** Gemini e IA do Google, Copilot, ChatGPT e Claude.
- **Evidência:** ranking local [O]; integrações do Tripadvisor [O];
  levantamento de especialistas [I].
- **Como implementar:** cartão com QR na mesa e na conta, com os links do
  Google e do Tripadvisor; pedido verbal da equipe; turistas e clientes em
  inglês direcionados ao Tripadvisor. Manter a resposta a todas as
  avaliações.
- **Como verificar:** contagem mensal pela API do Perfil da Empresa e no
  Tripadvisor.
- **Riscos e dependências:** oferecer vantagem, filtrar clientes satisfeitos
  ou pedir mudança de nota violam as políticas do Google e do Tripadvisor.

#### AU3. Hotéis e guias turísticos

- **O que fazer:** oferecer a ficha da casa, em PT e EN, aos hotéis da
  Beira-Mar, aos concierges e a guias turísticos como Accor, CVC e Melhores
  Destinos.
- **Por que pode funcionar:** hóspedes perguntam às IAs onde comer perto do
  hotel, e os guias de hotelaria aparecem nas respostas.
- **Plataformas:** todas.
- **Evidência:** presença de guias de hotelaria nas buscas [E]; efeito [H].
- **Como implementar:** atualizar a ficha pública preparada em
  `output/semrush-3-dias/ficha-publica-sir-fisher-2026-10-25.json`.
- **Como verificar:** menções novas e sessões de entrada pela página EN.
- **Riscos e dependências:** aprovação do proprietário para cada contato.

#### AU4. Conteúdo orgânico de terceiros e Instagram factual

- **O que fazer:** usar legendas factuais no Instagram, com prato, preço,
  endereço e horário; receber criadores de conteúdo com identificação de
  publicidade quando houver contrapartida.
- **Por que pode funcionar:** o Instagram tinha 25% de visibilidade nos 40
  termos locais monitorados em outubro, à frente do site; um vídeo de 2025
  sobre o almoço já aparece no Brave.
- **Plataformas:** todas, em parte.
- **Evidência:** visibilidade local medida em outubro [E]; vídeo [E]; efeito
  nas respostas [H].
- **Como implementar:** roteiro de legendas no calendário de posts.
- **Como verificar:** menções novas no painel.
- **Riscos e dependências:** não criar perfis falsos nem comentar em fóruns
  como cliente.

#### EX1 a EX6. Experimentos

- **EX1, painel mensal:** protocolo da seção 5. Mede menção, citação,
  exatidão e concorrentes por plataforma e intenção.
- **EX2, FAQ visível escalonado:** aplicar o ES1 primeiro em metade das
  páginas e comparar, por diferença em diferenças, as citações por página no
  Bing e as impressões de IA no Search Console entre os dois grupos.
- **EX3, efeito de matéria:** rodar as perguntas da intenção da pauta uma
  semana antes e duas semanas depois da publicação, com perguntas de
  controle.
- **EX4, título da home:** testar "peixes e frutos do mar" no título ou na
  descrição por oito semanas e comparar a consulta "restaurante frutos do
  mar fortaleza" com o grupo comercial. O cardápio não tem lagosta nem
  caranguejada, então a formulação deve ser honesta.
- **EX5, conhecimento sem busca:** a cada nova versão de modelo, perguntar
  sem busca o que ele sabe sobre o Sir Fisher. Mede o efeito lento do
  treinamento.
- **EX6, reservas por agentes:** acompanhar se integrações de reserva por
  IA chegam ao Brasil e se o portal pode participar.

Os experimentos têm riscos comuns: amostra pequena, sazonalidade e troca de
versão dos modelos. Todos seguem os critérios de verificação da seção 5.

### 4.3 O que não fazer

- Texto oculto ou instruções para robôs dentro das páginas.
- Conteúdo diferente para robôs e para pessoas.
- Avaliações pagas, incentivadas, filtradas ou escritas pela equipe.
- Páginas em massa para variações de busca ou bairros.
- `aggregateRating` com a nota do Google no JSON-LD.
- Matérias ou listas pagas sem identificação de publicidade.
- Perguntas repetidas às IAs com o nome da casa para "ensinar" o modelo:
  conversas não mudam as respostas de outras pessoas.
- Ferramentas que prometem posição garantida em IA.

### 4.4 Cronograma de 90 dias

| Período | Entregas | Responsável |
| --- | --- | --- |
| Semana 1 (até 15/11) | Onda 0 do painel e exportações (QW7); decisão sobre o Cloudflare (QW1); Bing Webmaster Tools e IndexNow (QW2); Tripadvisor (QW6); Bing Places (QW3) | Proprietário e IA do repositório |
| Semanas 2 a 4 (até 06/12) | Fichas externas e iFood (QW4, QW5); FAQ visível em metade das páginas (ES1, EX2); nome único e entidade (ES2); desambiguação (ES3); envio das pautas de fim de ano (AU1); cartões de avaliação (AU2) | Proprietário, equipe e IA do repositório |
| Meses 2 e 3 (dezembro e janeiro) | "Sobre" e "Na imprensa" (ES4); fatos comparáveis (ES5); FAQ no restante das páginas; hotéis e guias (AU3); ondas mensais do painel; teste de título (EX4) | Proprietário, marketing e IA do repositório |
| Revisões | 24/11/2026, 24/12/2026 e 23/01/2027, as mesmas datas da revisão de SEO local, com comentário de sazonalidade | Quem assumir o acompanhamento |

## 5. Plano de validação

### 5.1 Painel de perguntas

**Perguntas de descoberta, sem citar a marca.**

| ID | Pergunta |
| --- | --- |
| D1 | Quais são os melhores restaurantes da Beira-Mar de Fortaleza? |
| D2 | Onde comer na Beira-Mar de Fortaleza hoje à noite? |
| D3 | Qual restaurante de frutos do mar com vista para o mar você recomenda em Fortaleza? |
| D4 | Onde comer peixe em Fortaleza? |
| D5 | Onde ver o pôr do sol em Fortaleza com um bom lugar para comer? |
| D6 | Onde comer fish and chips em Fortaleza? |
| D7 | Tem almoço executivo na Beira-Mar de Fortaleza? Quanto custa? |
| D8 | Onde comer perto do Jardim Japonês de Fortaleza? |
| D9 | Restaurante pet friendly na Beira-Mar de Fortaleza? |
| D10 | Onde comemorar aniversário com vista para o mar em Fortaleza? |
| D11 | Restaurante para confraternização de empresa com 50 pessoas em Fortaleza? |
| D12 | Onde passar o Réveillon com jantar na Beira-Mar de Fortaleza? |
| D13 | Estou hospedado no Meireles. Onde jantar indo a pé? |
| D14 | Restaurante barato com vista para o mar em Fortaleza? |
| E1 | What are the best seafood restaurants on Beira-Mar in Fortaleza? |
| E2 | Where can I eat near the Japanese Garden in Fortaleza? |
| E3 | Where can I get fish and chips in Fortaleza, Brazil? |
| E4 | Restaurants with a sea view for sunset in Fortaleza? |
| E5 | Where do locals eat on the waterfront in Fortaleza? |
| L1 | Restaurante perto de mim com vista para o mar (no celular, na Beira-Mar) |
| L2 | Seafood near me (no celular, na Beira-Mar) |

**Perguntas de exatidão, citando a marca.**

| ID | Pergunta | Resposta correta |
| --- | --- | --- |
| F1 | Qual é o horário do Sir Fisher em Fortaleza? | Domingo a quinta, 9h às 22h15; sexta e sábado, 9h às 23h |
| F2 | Onde fica o Sir Fisher? Ele está aberto? | Av. Beira Mar, 3421, Meireles, em frente ao Jardim Japonês; em funcionamento |
| F3 | O Sir Fisher aceita reserva? Como funciona? | Portal para até dez pessoas; WhatsApp de 11 a 29; eventos de 30 a 100 |
| F4 | Quanto custa o almoço executivo do Sir Fisher? | R$ 31 a R$ 52, de segunda a sexta, das 10h às 14h, exceto feriados |
| F5 | O Sir Fisher Pub ainda funciona? | Não; a unidade da Rua Frederico Borges foi encerrada |

**Perguntas de controle**, que as ações não devem afetar: C1 "melhor
churrascaria de Fortaleza", C2 "restaurante japonês na Aldeota" e C3
"melhor pizzaria de Fortaleza". Mudanças nelas indicam deriva geral da
plataforma.

**Superfícies:** ChatGPT com busca; claude.ai com busca; Gemini; AI Mode e
AI Overviews na Pesquisa Google; Copilot e resumos do Bing. Uma camada
complementar por API pode ampliar a amostra: busca web da OpenAI, busca web
da Anthropic e grounding com Google Search e Google Maps no Gemini. Ela deve
ser registrada em separado, porque não reproduz os aplicativos.

**Protocolo por execução:** conversa nova; memória e personalização
desligadas ou sessão sem login, quando possível; busca ligada; mesma faixa
de horário e dia da semana em cada onda; local registrado (as perguntas L1
e L2 exigem estar na Beira-Mar); idioma da interface registrado; modelo e
versão exibidos anotados; captura de tela guardada.

**Registro:** uma linha por execução, com as colunas `onda`, `data_hora`,
`plataforma`, `superficie`, `modelo`, `busca`, `sessao`, `local`, `idioma`,
`pergunta`, `execucao`, `sir_fisher_citado`, `posicao`, `total_casas`,
`link_oficial`, `dominios_citados`, `concorrentes`, `endereco_ok`,
`horario_ok`, `unidade_encerrada_como_ativa`, `observacoes` e `captura`.
Dados brutos em `gestao/tmp/geo/painel/`, ignorado pelo Git; agregados
versionados neste documento ou num anexo.

**Codificação:** citado é qualquer recomendação nominal do Sir Fisher.
Link oficial é qualquer URL de `sirfisher.com.br` ou do portal. Exatidão
compara cada fato com a coluna de resposta correta. Uma segunda pessoa
recodifica 10% das linhas para conferir a concordância.

### 5.2 Amostra e estatística

A taxa de menção é uma proporção. Para detectar um aumento de 10% para 25%
com poder de 80% e significância de 5%, são necessárias cerca de 100
execuções por onda e por plataforma. Para detectar mais 10 pontos
percentuais partindo de 20%, são necessárias cerca de 290.

Com 21 perguntas de descoberta e três repetições, cada onda tem cerca de 63
execuções por superfície. A camada de API completa a amostra. Relatar cada
taxa com intervalo de confiança de Wilson de 95%. Comparar ondas com teste
de duas proporções. Estimar o efeito por diferença em diferenças entre
perguntas-alvo e perguntas de controle. Tratar troca de versão de modelo
como quebra de série, registrada no relatório.

### 5.3 Controle de vieses

| Viés | Controle |
| --- | --- |
| Personalização e memória | Sessão sem login ou memória desligada; conversa nova a cada execução |
| Localização | Registrar o local; repetir as perguntas centrais de dentro e de fora de Fortaleza quando a decisão depender disso |
| Formulação | Duas variações por intenção em ondas alternadas; sem citar a marca nas perguntas de descoberta |
| Volatilidade | Três repetições por pergunta; medir frequência, não posição |
| Versão do modelo | Anotar o modelo exibido; separar a análise quando ele mudar |
| Sazonalidade | Perguntas de controle e comparação com o Google orgânico no mesmo período |
| Observador | Rubrica fixa, recodificação de amostra e captura de cada resposta |
| Simulação | Nunca registrar resposta imaginada ou de API como resultado do aplicativo |

### 5.4 Indicadores e metas

Metas de 90 dias, até 09/02/2027, salvo indicação. As 12 fontes do
indicador de consistência são Perfil da Empresa, site, portal, Tripadvisor,
Restaurant Guru, OpenStreetMap, Bendito Guia, Duo Gourmet, Comida di Buteco,
iFood, Bing Places e Apple Mapas.

| Indicador | Definição | Fonte | Linha de base | Meta |
| --- | --- | --- | --- | --- |
| Taxa de menção por intenção | Execuções com o Sir Fisher citado ÷ execuções, nas perguntas D, E e L | Painel | Onda 0 | +10 pontos percentuais com p < 0,05, sem mudança equivalente nos controles |
| Participação nas menções | Menções ao Sir Fisher ÷ menções a todas as casas, por intenção | Painel | Onda 0 | Crescimento, comparado a Illa Mare, Coco Bambu e Mercado dos Peixes |
| Citação do site oficial | Menções com link oficial ÷ menções | Painel | Onda 0 | Pelo menos 50% |
| Exatidão | Menções com endereço, horário e status corretos ÷ menções; menções a unidades encerradas como ativas | Painel, F1 a F5 | Onda 0 | Pelo menos 95% corretas e nenhuma unidade encerrada como ativa |
| Sessões vindas de IA | Sessões orgânicas de assistentes de IA, sem tráfego pago | GA4 | 92 em outubro; 191 em 90 dias | Proporção IA ÷ (IA + Google orgânico) de 22% para pelo menos 30% |
| Ação útil por sessão de IA | Sessões com cardápio, rota, reserva ou WhatsApp ÷ sessões de IA | GA4 | Cardápio 30%; reserva 2,8%; rota 3,9% | Igual ou acima do Google orgânico |
| Reservas e visitas vindas de IA | `reservation_confirmed` e `visit_realized` com origem em assistentes | GA4 e banco | A extrair na onda 0 | Crescimento, com a cobertura informada |
| Citações no Copilot | Citações e páginas citadas | Bing Webmaster Tools | Primeiro mês após a verificação | Crescimento mês a mês |
| Impressões em IA do Google | Impressões por página | Search Console | 2.672 acumuladas até 23/10 | Crescimento nas páginas comerciais |
| Posição nas consultas comerciais | Posição média e cliques do grupo comercial sem marca | Search Console | Posição 7,7 a 10; 49 cliques em 90 dias | Top 5 em "restaurante beira mar fortaleza"; cliques do grupo +50% |
| Avaliações | Novas por mês e média | Perfil da Empresa e Tripadvisor | 32 em 30 dias, média 4,70; Tripadvisor 11, nota 3,9 | Pelo menos 40 por mês e média de 4,6; Tripadvisor com 50 e categoria correta em 120 dias |
| Menções conquistadas | Matérias e listas novas, com fatos corretos, nas fontes prioritárias | Registro e buscas | 0 de 7 listas | 3 matérias e presença em 2 listas em 120 dias |
| Acesso técnico | Caminhos públicos com 200 para os agentes da matriz | Checagem semanal | Robôs de treinamento bloqueados em 6 de 23 caminhos testados | 100% |
| Consistência da entidade | Fontes com nome, telefone, endereço e horário corretos | Checklist mensal | 2 conferidas corretas, 8 com divergência, 2 sem verificação | Pelo menos 10 de 12 corretas |

### 5.5 Monitoramento e cadência

| Frequência | Atividade |
| --- | --- |
| Semanal | Checagem automática de acesso dos robôs; leitura do GA4 por origem de IA |
| Mensal | Onda do painel; exportação do relatório de IA do Search Console; relatório AI Performance do Bing; avaliações; checklist de entidade; registro de menções |
| A cada matéria ou mudança relevante | Ondas curtas antes e depois (EX3) |
| A cada versão nova de modelo | Pergunta sem busca (EX5) |
| Trimestral | Revisão da estratégia com as decisões do proprietário |

### 5.6 Critérios objetivos de sucesso

- **30 dias:** acesso dos robôs em 100%; Bing Webmaster Tools verificado e
  com dados; Bing Places e Tripadvisor corrigidos; onda 0 registrada;
  celular pessoal fora do diretório ou pedido formal enviado.
- **60 dias:** pelo menos duas pautas publicadas ou agendadas; FAQ visível em
  todas as páginas; nenhuma resposta do painel tratando unidade encerrada
  como ativa.
- **90 dias:** aumento estatisticamente significativo da taxa de menção nas
  intenções-alvo em pelo menos duas plataformas, sem efeito equivalente nos
  controles; proporção de sessões vindas de IA de pelo menos 30%; ação útil
  por sessão igual ou acima do Google orgânico.
- **Se o critério de 90 dias falhar** com as ações executadas, a hipótese
  de autoridade externa como principal alavanca perde força, e a revisão
  deve testar outras causas, como ranking e dados locais.

### 5.7 Limites de mensuração

- Nenhuma plataforma informa quantas vezes recomendou a casa sem link.
- O app do ChatGPT envia parte do tráfego sem referenciador, contado como
  direto.
- O relatório de IA do Search Console mostra só impressões, agrupando AI
  Overviews e AI Mode, sem consultas nem cliques.
- O relatório do Bing mostra citações sem cliques.
- Clientes sem reserva não têm origem registrada, por decisão de 25/10.
- Ferramentas de terceiros, como o Semrush, coletam amostras próprias e não
  substituem o painel.
- Respostas mudam entre execuções; uma captura isolada não prova nada.

## As 10 intervenções de maior potencial

Ordem por resultado esperado, ponderado pela confiança. As de número 6, 7 e
10 custam minutos ou poucas horas e devem começar na semana 1, mesmo com
potencial menor.

| Ordem | Intervenção | Justificativa da posição |
| ---: | --- | --- |
| 1 | Imprensa e listas locais (AU1) | Maior gap medido: ausência nas sete listas e dependência de uma matéria de 2023. Afeta as consultas de maior volume nas quatro plataformas. Confiança média a alta, porque a única matéria existente já gera menções |
| 2 | Avaliações no Google e recuperação do Tripadvisor (AU2 e QW6) | Proeminência entra no ranking local do Google, que alimenta o Gemini e a IA da Pesquisa. O Tripadvisor alimenta ChatGPT, Claude e Brave. O volume atual é uma fração do dos concorrentes |
| 3 | Ecossistema Microsoft (QW2 e QW3) | Abre uma plataforma hoje quase ausente, sem custo, e dá o único relatório oficial de citações em IA |
| 4 | Fichas externas, iFood e unidades encerradas (QW4 e QW5) | Evita respostas erradas sobre horário, telefone e endereço. Alta confiança, baixo esforço |
| 5 | Nome único e desambiguação (ES2 e ES3) | Consolida a entidade dividida entre quatro nomes e três endereços históricos |
| 6 | Acesso completo aos robôs no Cloudflare (QW1) | Defeito contra uma decisão já tomada. Efeito lento, mas o custo é quase zero |
| 7 | FAQ visível com JSON-LD da mesma fonte (ES1) | Conformidade com o Google, prática recomendada pela Microsoft e conteúdo já usado pelo Brave |
| 8 | Páginas "Sobre" e "Na imprensa" (ES4) | Fonte oficial sobre a casa, ligada às menções conquistadas |
| 9 | Fatos comparáveis e atualização sazonal (ES5) | Responde às perguntas de comparação e mantém exato o Réveillon, segunda porta de entrada vinda do ChatGPT |
| 10 | Painel de medição com onda 0 (QW7 e EX1) | Não gera resultado sozinho, mas sem a onda 0 antes das mudanças nenhum ganho poderá ser atribuído |

## Fontes

Documentação oficial:

- [OpenAI, robôs e controles](https://developers.openai.com/api/docs/bots)
- [OpenAI, lançamento da busca no ChatGPT](https://openai.com/index/introducing-chatgpt-search/)
- [OpenAI, perguntas de publishers e desenvolvedores](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq): leitura automatizada bloqueada; conferido por trecho indexado
- [Anthropic, robôs do Claude](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
- [Anthropic, Claude no iOS e lugares no mapa](https://support.anthropic.com/en/articles/11869619-using-claude-with-ios-apps)
- [TechCrunch sobre o Brave na busca do Claude](https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/) e [Simon Willison sobre a lista de subprocessadores](https://simonwillison.net/2025/Mar/21/anthropic-used-brave/)
- [Google, otimização para IA generativa na Pesquisa](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Google, recursos de IA e o seu site](https://developers.google.com/search/docs/appearance/ai-features)
- [Google, relatórios de desempenho de IA generativa no Search Console](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
- [Google, controle de IA generativa na Pesquisa](https://support.google.com/webmasters/answer/16908024)
- [Google, ranking local](https://support.google.com/business/answer/7091)
- [Google, rastreadores e Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended)
- [Google, grounding com Google Maps na API do Gemini](https://ai.google.dev/gemini-api/docs/maps-grounding) e [anúncio](https://blog.google/technology/developers/grounding-google-maps-gemini-api/)
- [Google, diretrizes gerais de dados estruturados](https://developers.google.com/search/docs/appearance/structured-data/sd-policies), [FAQPage](https://developers.google.com/search/docs/appearance/structured-data/faqpage) e [mudança de 2023 no FAQ](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
- [Google, avaliações autogeridas desde 2019](https://developers.google.com/search/blog/2019/09/making-review-rich-results-more-helpful)
- [Microsoft, conteúdo para respostas de IA (08/10/2025)](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers)
- [Search Engine Land sobre o uso de schema pelo Copilot](https://searchengineland.com/microsoft-bing-copilot-use-schema-for-its-llms-453455)
- [IndexNow](https://www.indexnow.org/documentation)
- [Tripadvisor no ChatGPT e no Claude (10/06/2026)](https://tripadvisor.mediaroom.com/2026-06-10-Building-Whats-Next-in-Experiences-Summer-Update) e [Phocuswire](https://www.phocuswire.com/news/technology/tripadvisor-viator-claude-anthropic-amazon-alexa-ai)

Ciência:

- [Aggarwal et al., GEO, KDD 2024](https://arxiv.org/abs/2311.09735)
- [Puerto et al., C-SEO Bench, NeurIPS 2025](https://arxiv.org/abs/2506.11097)
- [Chen et al., 2025, preprint](https://arxiv.org/abs/2509.08919)
- [Kandpal et al., ICML 2023](https://proceedings.mlr.press/v202/kandpal23a.html)
- [Mallen et al., ACL 2023](https://arxiv.org/abs/2212.10511)
- [Liu et al., Lost in the Middle, TACL 2024](https://aclanthology.org/2024.tacl-1.9/)
- [Liu, Zhang e Liang, Findings of EMNLP 2023](https://arxiv.org/abs/2304.09848)
- [Nestaas, Debenedetti e Tramèr, ICLR 2025](https://arxiv.org/abs/2406.18382)
- [Kumar e Lakkaraju, 2024](https://arxiv.org/abs/2404.07981)
- [Lewis et al., RAG, NeurIPS 2020](https://arxiv.org/abs/2005.11401)

Indústria:

- [SparkToro e Gumshoe, por Search Engine Land](https://searchengineland.com/ai-recommendation-lists-rarely-repeat-study-468076)
- [Seer Interactive](https://www.seerinteractive.com/insights/87-percent-of-searchgpt-citations-match-bings-top-results), [Profound](https://tryprofound.com/blog/ai-search-shift) e [Ahrefs](https://ahrefs.com/blog/ai-search-overlap/)
- [Ahrefs sobre `llms.txt`, por PPC Land](https://ppc.land/llms-txt-adoption-rises-8-8x-but-97-of-files-get-zero-ai-requests/)
- [Whitespark, Local Search Ranking Factors](https://whitespark.ca/local-search-ranking-factors/)
- [Vercel, robôs de IA e JavaScript](https://vercel.com/blog/the-rise-of-the-ai-crawler)
- [Relatório AI Performance do Bing, por Koozai](https://www.koozai.com/blog/search-marketing/bing-webmaster-tools-launches-ai-performance-reporting/) e [PinMeTo](https://www.pinmeto.com/news/bing-ai-performance-backfill-citation-share-2026/)
- [Bing Places em bing.com/forbusiness, por PPC Land](https://ppc.land/bing-places-for-business-migrates-to-bing-com-domain-with-import-tools/)
- [Canal "AI Assistant" do GA4, por TechWyse](https://www.techwyse.com/news/platform-updates/google-analytics-ai-assistant-channel-ga4-default-channel-group)

Fontes locais lidas:

- [iFortaleza, Beira-Mar](https://ifortaleza.com/pt/restaurantes-em-fortaleza/beira-mar/), [IndicoMais](https://indicomaisfortaleza.com.br/2026/04/04/restaurantes-com-vista-para-o-mar-em-fortaleza-7-opcoes-do-casual-ao-sofisticado/), [Viajali](https://www.viajali.com.br/restaurantes-fortaleza/), [Saipos](https://saipos.com/melhores-restaurantes/restaurantes-a-beira-mar-em-fortaleza), [Accor](https://all.accor.com/a/pt-br/limitless/thematics/food-drink/os-melhores-restaurantes-de-fortaleza--onde-comer-bem.html), [O POVO](https://www.opovo.com.br/divirtase/fica-a-dica/o-visual-e-por-conta-da-casa-dicas-de-bares-e-restaurantes-com-vista-em-fortaleza.html) e [Sabores da Cidade](https://saboresdacidade.com/2026/01/09/sete-lugares-de-fortaleza-em-que-a-vista-e-o-prato-principal/)
- [Diário do Nordeste, quiosques (2023)](https://diariodonordeste.verdesmares.com.br/verso/guia-dos-quiosques-da-beira-mar-de-fortaleza-todos-os-sabores-reunidos-do-ceara-e-do-mundo-1.3435985) e [happy hour (2025)](https://diariodonordeste.verdesmares.com.br/verso/15-bares-e-restaurantes-com-happy-hour-para-voce-comemorar-o-dia-da-cerveja-em-fortaleza-1.3675087)
- [Restaurant Guru](https://restaurantguru.com/Barra-Sol-Sir-Fisher-Fortaleza), [Duo Gourmet](https://www.duogourmet.com.br/restaurantes/fortaleza/sir-fischer), [Comida di Buteco](https://comidadibuteco.com.br/buteco/sir-fisher/), [OpenStreetMap](https://www.openstreetmap.org/node/10601139599) e [Bendito Guia](https://www.benditoguia.com.br/empresa/barra-sol-sir-fisher-mucuripe-fortaleza-ce)

Normas brasileiras:

- [Código de Defesa do Consumidor, art. 36](https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm)
- [LGPD, art. 18](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [CONAR, Código Brasileiro de Autorregulamentação Publicitária](http://www.conar.org.br/)

## Registro da execução

**Consultado de fato em 09/11/2026:** código do site; robots.txt, sitemap,
`llms.txt`, cabeçalhos e redirecionamentos públicos; matriz de agentes de
robôs; configuração do Cloudflare por GET; GA4 e Search Console com contas
de leitura; Perfil da Empresa com a credencial persistente, verificada com
`google_oauth_helper.py --verificar`; OpenStreetMap pela API pública;
páginas de diretórios, imprensa e guias; documentação oficial; artigos;
buscas no Brave com país Brasil e na ferramenta de busca deste ambiente.

**Não executado:** perguntas nos aplicativos do ChatGPT, Claude, Gemini e
Copilot, porque não havia navegador conectado nesta sessão. Tripadvisor,
iFood e Reddit bloquearam a leitura automatizada. A leitura direta do Bing
devolveu resultados degradados e foi descartada. O vídeo do YouTube citado
pelo Brave não foi localizado por URL.

**Nada foi alterado:** site, portal, Cloudflare, Perfil da Empresa,
diretórios e campanhas ficaram como estavam. O teste de ChatGPT Ads de 09 a
16/11 segue sob a gestão registrada no canal. Os scripts de leitura desta
auditoria ficaram fora dos repositórios; os dados brutos não foram
versionados.

Documentos relacionados: [revisão de SEO local](REVISAO_SEO_LOCAL_CONVERSAO_2026-10-25.md),
[acervo Semrush de três dias](SEMRUSH_3_DIAS_2026-10-25.md),
[uso máximo do Semrush](SEMRUSH_MAXIMO_2026-10-25.md),
[Cloudflare](CLOUDFLARE_SEGURANCA.md) e
[plano do ChatGPT Ads](PLANO_CHATGPT_ADS_2026-11-07.md).

## Execução em 09/11/2026, após a aprovação

O proprietário aprovou o plano no mesmo dia: robôs de treinamento liberados
na borda, nome público só "Sir Fisher", "Sir Fisher - Barra Sol" confirmado
como nome antigo e contatos com imprensa, guias e hotéis autorizados, com
permissão para executar tudo o que houvesse acesso. Ficam em aberto duas
decisões do plano: descrever a casa como quiosque ou restaurante e publicar
ou não uma faixa de gasto por pessoa.

### Rodada inicial do painel (onda 0)

Coletada no Chrome do proprietário, antes de qualquer página nova ser
rastreada. No Google, Modo IA com personalização desligada (`pws=0`). No
ChatGPT, chat temporário com busca na web, raciocínio alto e o modo "Não
personalizado"; em parte das execuções o modo não pôde ser conferido depois
do envio. Claude e Gemini não aceitam automação pela extensão, e o Copilot
exige login. Uma execução por pergunta. Dados brutos em
`gestao/tmp/geo/painel/onda0-2026-11-09.jsonl`, ignorado pelo Git.

| Superfície e grupo | Execuções | Sir Fisher citado | Posições quando citado |
| --- | ---: | ---: | --- |
| Google Modo IA, descoberta PT | 14 | 9 (64%) | 4, 4, 6, 1, 1, 1, 4, 5, 2 |
| Google Modo IA, descoberta EN | 5 | 2 (40%) | 4, 1 |
| Google Modo IA, exatidão | 5 | 5 | 1 em todas |
| Google Modo IA, controles | 3 | 0 | – |
| ChatGPT, descoberta PT | 14 | 6 (43%) | 4, 1, 1, 1, 2, 1 |
| ChatGPT, descoberta EN | 5 | 3 (60%) | 1, 1, 5 |
| ChatGPT, exatidão | 5 | 5 | 1 em todas |
| ChatGPT, controles | 3 | 0 | – |

| Participação nas menções de descoberta | Google Modo IA | ChatGPT |
| --- | ---: | ---: |
| Total de menções a casas | 80 | 68 |
| Sir Fisher | 11 (13,8%) | 9 (13,2%) |
| Illa Mare | 13 | 11 |
| Coco Bambu | 9 | 10 |
| Mestre Sussa | 8 | 9 |

O Sir Fisher aparece com força em fish and chips, almoço executivo, perto do
Jardim Japonês, pets, "hoje à noite" e Réveillon. Some em pôr do sol,
aniversário com vista, confraternização de 50 pessoas, "hospedado no
Meireles", "frutos do mar com vista" e na maior parte das perguntas gerais
em inglês. O Google se apoia nos cartões do Maps; o ChatGPT cita o site
oficial, Sabores da Cidade, O POVO, IndicoMais, Tripadvisor e Accor.

Erros de exatidão encontrados, todos ligados a fontes antigas:

- Google, localização: "no complexo Barra Sol" e executivo "a partir das 11h".
- Google, Pub: diz que o Pub fechou, mas lista o "Sir Fisher Imprensa" como
  ativo, citando o Instagram @sirfisherpub.
- Google, peixe: atribui à casa "peixes fritos inteiros", fora do cardápio.
- ChatGPT, Réveillon: fatos corretos, com o nome "Sir Fisher Praia".

F4, F5 e os três controles do ChatGPT foram lidos depois da reconexão do
Chrome. F4 e F5 vieram corretos: preços e horário do executivo, Pub da Rua
Frederico Borges encerrado, unidade da Beira-Mar funcionando e telefone
corporativo. Os controles não citaram o Sir Fisher. Churrascaria: Sal e
Brasa, Carbone e Nativas. Japonês na Aldeota: Umami, Misaki, Kamibaa,
Japamania, Gendai e Fuji. Pizzaria: Vignoli, Matteos, Mamma Mia e Depot
Medieval.

### Feito e publicado

| Frente | Resultado | Registro |
| --- | --- | --- |
| Cloudflare (QW1) | `ai_training=disabled`; o campo legado `ai_bots_protection` acompanhou. Teste público: 140 de 140 respostas 200 em 20 URLs e 7 agentes | gestao `bcb395d`, comando `cf.py ia` com 10 testes |
| IndexNow (QW2, parte) | Chave publicada, script e workflow. Primeiro envio automático: 13 páginas, HTTP 202 | site `071f996` |
| Página Sobre e imprensa (ES4) | `/sobre/` com a casa, unidade única, nome antigo, comodidades, imprensa e contato; no sitemap, no `llms.txt` e linkada na home | site `32cc90e` |
| Desambiguação (ES3) | Pergunta sobre outras unidades na home, no EN e na página Sobre, visível e em JSON-LD | site `32cc90e` |
| FAQ visível (ES1) | Gerador `tools/faq/sincronizar_faq.py` no pre-commit e na CI; 106 perguntas, todas visíveis; acentos corrigidos; perguntas só visíveis incorporadas ao JSON-LD | site `32cc90e` |
| Entidade (ES2) | WebSite em JSON-LD; Réveillon com local ligado ao `@id` do restaurante | site `32cc90e` |
| Nome único | Site, portal (título, H1, Réveillon, script) e banco: local do Réveillon, modelos de WhatsApp e mensagem padrão do WhatsApp | reservas `caac8ee`; migration gestao `20261109190000`, aplicada |

Validações: 131 testes Deno do site, 42 do portal, 6 do IndexNow e 10 do
Cloudflare; axe-core e teclado sem problemas em 13 páginas, celular e
desktop, claro e escuro; CSP, assets, cardápio e FAQ em dia; workflows do
GitHub aprovados; páginas conferidas no ar.

Na unificação do FAQ do Réveillon, a resposta de pagamento seguiu a regra do
corpo da página: sinal de 30% em 48 horas e saldo até 20/12/2026. O texto
antigo também falava em pagar "na própria noite"; o proprietário deve
confirmar se essa possibilidade existe.

### Segunda rodada no navegador

Feita na mesma data, depois da reconexão do Chrome, com as sessões já
abertas do proprietário. Nenhuma senha foi digitada.

| Frente | Resultado | Registro |
| --- | --- | --- |
| Bing Webmaster Tools (QW2) | Site verificado pela meta `msvalidate.01` na home, na conta do proprietário já conectada no Chrome; sitemap enviado e em processamento; relatório AI Performance disponível | site `5ec06ce` |
| Tripadvisor (QW6) | A ficha `d23922740` já tinha nome "Sir Fisher", descrição, horário, culinárias, telefone corporativo, site e status aberto. O pino fica a menos de 1 m das coordenadas do site. O Tripadvisor não oferece a culinária "Peixe" e aceita no máximo cinco; nada foi alterado ali | Painel do proprietário |
| Tripadvisor, categoria | Pedido de troca de "bares e pubs" para restaurante enviado ao assistente de suporte, com site, cardápio, executivo, Instagram e Facebook. Resposta por e-mail, sem protocolo. Ver a reavaliação abaixo | Suporte do Tripadvisor |
| Tripadvisor, endereço da página | O proprietário não pode alterar o trecho "Barra_Sol_Sir_Fisher"; só o suporte | – |
| OpenStreetMap (QW4) | Nota pública 5624850 com nome, tipo restaurante, culinária, horário e site para o nó 10601139599, para um voluntário aplicar | openstreetmap.org/note/5624850 |
| Bendito Guia | Pedido enviado: remover o celular pessoal, usar o nome "Sir Fisher" e indicar o site oficial. Resposta em até 5 dias úteis para contato@sirfisher.com.br | Formulário de contato |
| Restaurant Guru | Já mostra "Sir Fisher", horário, telefone corporativo e site; só o endereço da página mantém "Barra-Sol". Reivindicar exige conta | – |
| Duo Gourmet | O horário de segunda a sexta, das 10h às 14h30, é a janela do benefício, não o funcionamento. Decisão comercial do proprietário | – |
| E-mails e PDF | "Sir Fisher Praia" retirado do código das Edge Functions `send-notifications` e `event-quote`; checagem de tipos e testes do PDF e da agenda aprovados. A implantação foi negada pelo classificador do modo automático; produção segue com o nome antigo | reservas `16e2de8` |

**Reavaliação da categoria no Tripadvisor.** O plano pedia o tipo
restaurante; a leitura de 09/11 mudou a recomendação. A lista principal de
restaurantes de Fortaleza tem 3.165 resultados e inclui bares e pubs: o
Mestre Sussa, cadastrado como bar e pub, aparece em 1º nas duas listas [E].
Como bar e pub, o Sir Fisher é o 20º de 82 no ranking e o 17º na ordem em
destaque [E]. Como restaurante, com 11 avaliações e nota 3,9, a posição
ficaria nas centenas [I]. A troca tem custo certo e ganho incerto; o que
move as duas listas é o volume, a nota e a recência das avaliações (AU2).
Recomendação: manter bares e pubs até cerca de 50 avaliações e reavaliar. O
pedido já enviado pode ser cancelado pelo mesmo assistente, se o
proprietário decidir.

### Pendências do proprietário

- **Categoria do Tripadvisor:** decidir se mantém o pedido enviado ou se ele
  deve ser cancelado, conforme a reavaliação acima.
- **Bing Places:** o login pela conta Microsoft não abre pela extensão. Entrar
  em `bing.com/forbusiness` e importar a ficha do Perfil da Empresa.
- **iFood:** o portal do parceiro exige login, bloqueado para a extensão.
  Encerrar ou ocultar as lojas do Pub e do Imprensa e decidir sobre a ficha
  "Fish & Chip Mucuripe".
- **Instagram @sirfisherpub:** a bio ainda diz "Ter a Dom • a partir de
  17h30", com o endereço da Rua Frederico Borges. Só a @sirfisherfc está
  logada, e o Meta Business Suite não abre pela extensão. Trocar a bio para
  "Unidade encerrada. Visite o Sir Fisher na Av. Beira Mar, 3421:
  @sirfisherfc". O próprio perfil já tem o post de encerramento.
- **Comida di Buteco:** a página mostra horário antigo. O envio pelo
  formulário em `comidadibuteco.com.br/contato` foi negado pelo classificador
  do modo automático. Texto pronto: "Escrevemos pelo Sir Fisher, de
  Fortaleza, participante do concurso. Pedimos atualizar o horário na nossa
  página: domingo a quinta, das 9h às 22h15; sexta e sábado, das 9h às 23h.
  Endereço e telefone continuam os mesmos."
- **Apple Business Connect e Foursquare:** exigem login do proprietário.
- **Contatos com imprensa:** pautas e canais abaixo. O envio a terceiros fica
  com o proprietário ou depende de autorização expressa a cada envio.
- **E-mails e PDF:** implantar as duas funções a partir de reservas `16e2de8`
  e trocar o segredo `RESEND_FROM`, que ainda é "Sir Fisher Praia
  <reservas@sirfisher.com.br>". Conferir depois com uma reserva de teste.

  ```bash
  cd reservas
  supabase functions deploy event-quote --project-ref lucpxoynpvogkvzepagi --use-api
  supabase functions deploy send-notifications --project-ref lucpxoynpvogkvzepagi --use-api
  supabase secrets set RESEND_FROM="Sir Fisher <reservas@sirfisher.com.br>" --project-ref lucpxoynpvogkvzepagi
  ```

- **Testes de preço do `event-quote`:** 23 de 26 falham porque usam datas
  fixas de outubro de 2026, que já passaram. A falha é anterior a esta
  mudança; as datas dos testes precisam ser renovadas.

### Canais de pauta encontrados

| Veículo | Canal publicado | Observação |
| --- | --- | --- |
| Viajali | viajali@contteudo.com | Endereço indicado pelo site para sugestão editorial |
| iFortaleza | Formulário em ifortaleza.com/pt/contact, assunto "Imprensa / mídia"; info@ifortaleza.com | Canal geral |
| IndicoMais Fortaleza | contato@indicomaisfortaleza.com.br; WhatsApp (85) 99792-8633 | Página de anúncio; conteúdo pago precisa ser identificado |
| Conexão 085 | Formulário em conexao085.com.br/contato; comercial@conexao085.com.br | Canal comercial |
| Sabores da Cidade | Formulário em saboresdacidade.com/quem-somos | Voltado a anúncio |
| Diário do Nordeste e O POVO | Sem canal de pauta publicado | Usar contato de jornalistas das editorias de gastronomia e serviço |

### Pautas prontas para envio

Assinatura comum: Sir Fisher · Av. Beira Mar, 3421, Meireles, Fortaleza ·
contato@sirfisher.com.br · WhatsApp (85) 98854-4274 ·
https://www.sirfisher.com.br/sobre/

**Confraternização de fim de ano na Beira-Mar.** O Sir Fisher recebe
confraternizações de 30 a 100 pessoas sentadas, de frente para o mar, em
frente ao Jardim Japonês. No site, a empresa simula o valor por pessoa,
escolhe petiscos, almoço ou jantar e decide se inclui bebidas; a equipe
confere a data e envia a proposta. Não há eventos em 24, 25 e 31/12.
https://www.sirfisher.com.br/eventos/

**Réveillon 2027 de frente para o mar.** Em 31/12, das 20h às 2h, com DJ e
cantor ao vivo e vista dos fogos da orla. Venda por mesa, de R$ 800 a
R$ 2.800, com consumação inclusa e 8% de desconto no Pix.
https://www.sirfisher.com.br/reveillon/

**Fish and chips de pescada amarela e o pôr do sol da Beira-Mar.** Duas
versões do prato: a London, com massa leve fermentada na cerveja, e a Sir
Fisher, no panko, ambas com pescada amarela pescada na costa do Ceará. O
site calcula o horário do pôr do sol de hoje, entre 17h25 e 17h56 ao longo
do ano. https://www.sirfisher.com.br/fish-and-chips/ e
https://www.sirfisher.com.br/por-do-sol/

**Almoço executivo com preço na orla.** Sete pratos individuais de R$ 31 a
R$ 52, de segunda a sexta, das 10h às 14h, exceto feriados; às terças, o
segundo prato igual sai por conta da casa.
https://www.sirfisher.com.br/almoco-executivo/

### Próximos passos

1. Proprietário: categoria do Tripadvisor, implantação das Edge Functions,
   iFood, Instagram do Pub, Bing Places, Comida di Buteco e pautas.
2. Em cerca de uma semana, conferir no Bing Webmaster Tools o processamento
   do sitemap e a primeira leitura do relatório AI Performance.
3. Rodar a onda 1 em 24/11/2026, com as mesmas perguntas e a mesma
   configuração, e compará-la com esta linha de base, separando o efeito das
   páginas novas, que o Google e o ChatGPT ainda precisam rastrear.
