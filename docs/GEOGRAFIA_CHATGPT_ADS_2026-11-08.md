# ChatGPT Ads: Fortaleza, CEPs e revisão do lance

Consulta em 08/11/2026, America/Fortaleza. O proprietário recusou a ativação
com alcance estadual. Campanha, grupo e anúncio foram relidos: os três
continuam pausados e a peça permanece aprovada. Esta investigação não
alterou a configuração no Ads Manager.

## Opções confirmadas e limites

A documentação da OpenAI permite países, estados/regiões, cidades, mercados
e códigos postais disponíveis no país em campanhas padrão, como esta. A
restrição de novas campanhas com catálogo a países não se aplica aqui.
O conector também oferece inclusões e exclusões de locais reconhecidos.
[Configuração de campanhas](https://help.openai.com/en/articles/20001210-creating-campaigns-for-chatgpt-ads).

| Opção | Evidência e utilidade | Limite ou risco |
| --- | --- | --- |
| Cidade de Fortaleza | É um nível oficialmente suportado onde houver cadastro disponível. Evitaria o alcance estadual. | A busca por Fortaleza devolve CEPs e não confirmou um registro do tipo cidade. Isso deixa a resolução da cidade pendente; não comprova ausência de suporte no Brasil. A cidade inteira ainda abrange deslocamentos distintos. |
| Setor postal 60165 | O catálogo devolveu um registro brasileiro de Fortaleza. A consulta pelo CEP completo do restaurante, 60165-121, devolveu o mesmo setor 60165. É a primeira alternativa recomendada para concentrar perto do endereço. | O resultado tem cinco dígitos. Não equivale a um endereço, bairro completo ou raio de distância. O conector não mostrou limites no mapa ou estimativa de público. |
| Setores 60160, 60170 e 60175 | Todos devolveram registros brasileiros de Fortaleza. São candidatos a complementar o setor do restaurante. | Os setores abrangem endereços em diferentes bairros; ampliar exige aceitar essa cobertura mais extensa. Não existe previsão demonstrada de visitas ou volume. |
| Setor 60060 | Registro brasileiro de Fortaleza confirmado; há endereços oficiais na Praia de Iracema. | Também há endereços no Centro com esse prefixo. Deixar como possibilidade de expansão, em vez de incluir automaticamente. |
| Bairro, raio em quilômetros, polígono ou tempo de deslocamento | Não encontrei controle oficialmente confirmado nas ferramentas e na documentação consultadas. | Não prometer segmentação exclusiva da Beira-Mar nem anunciar um raio que a plataforma não salvou. |
| Ceará com exclusões | As ferramentas permitem exclusões de locais reconhecidos. | Excluir uma lista incompleta de áreas não demonstra cobertura restrita à capital. Essa montagem não atende ao pedido atual. |

Foram conferidos país BR, tipo postal e nome canônico Fortaleza em cada
resultado. Códigos iguais também aparecem em outros países. Identificadores
externos, como os do Google Ads, não foram usados para configurar a campanha.
A consulta foi limitada aos setores de interesse; não foi enumerada a cidade.

O endereço do restaurante publicado no site é Avenida Beira-Mar, 3421,
Meireles, CEP 60165-121. [Sir Fisher](https://www.sirfisher.com.br/).
Endereços oficiais ajudam a interpretar os setores, sem definir seus limites:
o Batalhão de Policiamento Turístico informa Meireles com 60160-070;
a Assembleia informa endereços na Aldeota e em Dionísio Torres com 60170;
o cadastro municipal de órgãos contém Praia de Iracema com 60060-510 e
Centro com 60160-150. Uma relação municipal de escolas de 2018 registra
Mucuripe com 60175-270; esse último exemplo é histórico.
[PMCE](https://www.pm.ce.gov.br/contatos/contatos-batalhoes-e-unidades-operacionais/),
[Alece](https://transparencia.al.ce.gov.br/consultas-gerais/perguntas-frequentes),
[Prefeitura](https://transparencia.fortaleza.ce.gov.br/index.php/orgao),
[relação de escolas de 2018](https://compras-arquivos.sepog.fortaleza.ce.gov.br/documentos/editais/4125/0/P.E.%20152_2018%20-%20ED.%204025%20-%20DEFINITIVO%202%282%29.pdf).

## Recomendação geográfica

Priorizar o setor 60165 como primeira configuração local a validar. Ele é
o resultado mais diretamente associado ao endereço do restaurante. Se o
alcance ficar insuficiente, os setores 60160, 60170 e 60175 são candidatos
a ampliação, com o risco de incluir áreas além da orla. O setor 60060 fica
para uma expansão posterior. Essa ordem usa proximidade e endereços como
hipótese operacional; não há dados de desempenho por setor que permitam
classificar o potencial de clientes.

Na aplicação futura, substituir a inclusão Ceará pela seleção postal e
reler a campanha ainda pausada. Manter Ceará junto dos CEPs preservaria
a abrangência estadual. Um resultado no catálogo não comprova elegibilidade
de entrega, tamanho de público ou precisão no mapa. Se a plataforma recusar
os setores ou não permitir confirmar a restrição pretendida, manter a pausa
e encaminhar ao suporte a dificuldade de localizar a cidade. Não houve
abertura de chamado nem aplicação de CEPs nesta investigação.

Escrever Fortaleza/Meireles no texto e nos contextos ajuda na relevância;
não substitui o controle de localização. [Contextos](https://help.openai.com/en/articles/20001521-writing-context-hints-for-chatgpt-ads).

## Lance e orçamento

O grupo continua com máximo manual de R$3,50 por clique e orçamento total
de R$300 na campanha. A leitura do teste anterior, de 06 a 19/10/2026
(intervalo encerrado em 20/10), fornece uma referência própria de CPC.
Esse histórico usava outra abrangência e não comprova o custo de uma
visita com consumo após restringir os locais.

Recomendo manter R$3,50 como teto experimental, sem aumento nesta revisão.
Não há evidência comercial suficiente para chamar esse valor de rentável
ou ideal. Reduzir arbitrariamente a partir da média histórica também não
comprova ganho de eficiência. Primeiro é preciso resolver a geografia e,
em um teste autorizado, acompanhar ações de rota, reservas e comparecimento
com a cobertura de cada fonte. O critério de contenção do plano continua
válido; não existe pausa automática configurada.

Target CPC, previsto para 09/11, define uma meta média e permite cliques
acima dela. Converter R$3,50 de máximo para meta média muda o controle de
lance. A OpenAI informa que os controles antigos permanecem nas campanhas
existentes até a transição, com retirada em 01/01/2027. Não houve migração.
[Lances e preços](https://help.openai.com/en/articles/20001634-bidding-strategies-and-how-pricing-works-in-chatgpt-ads).

O orçamento permanece R$300 totais por sete dias, subordinado ao teto
agregado de R$1.000 mensais. A configuração atual continua com Ceará,
09/11 às 00h até 16/11 às 00h e todos os níveis pausados. Se a ativação
for autorizada depois do início, ajustar as datas para preservar os sete
dias e conciliar o saldo mensal antes de liberar entrega. A recusa de
ativação estadual prevalece sobre a alternativa registrada anteriormente
na descrição da campanha. A peça aprovada e a estratégia foram preservadas.
