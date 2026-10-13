# Retomada controlada do ChatGPT Ads do Sir Fisher

Preparado para Rogerio em 13 de outubro de 2026. A campanha de outubro foi
corrigida e foi ativada com autorizacao do proprietario. A entrega anterior
parou por esgotamento do orcamento; nao
ha evidencia suficiente para concluir que os anuncios nao trouxeram clientes.
O proprietario aprovou ate R$300 adicionais e sete dias, ajustando a proposta
inicial de R$200. O termino aplicado e 20/10/2026 as 16h19min17s em Fortaleza,
com registro dos clientes que chegam sem reserva.

## Diagnostico reavaliado

O problema real e decidir se o gasto traz consumo adicional que paga seus
custos variaveis e a publicidade. Reservas online representam apenas uma parte
da jornada de um restaurante. O registro de origem de clientes sem reserva
ainda nao existe, conforme resposta do proprietario.

Ausencia de reservas identificadas nao equivale a ausencia de clientes. CPC
menor nao prova resultado comercial melhor. As campanhas tiveram objetivos,
destinos e periodos de entrega diferentes; esta comparacao nao isola causas.

| Campanha e periodo completo | Gasto | Impressoes | Cliques | CPC informado pela plataforma |
| --- | ---: | ---: | ---: | ---: |
| Campanha anterior, 01 a 12/10 | R$223,05 | 4.321 | 56 | R$3,98 |
| Novos clientes Outubro 2026, 06 a 12/10 | R$277,05 | 10.147 | 101 | R$2,74 |

O total de outubro ate 12/10 e R$500,10. Gasto finalizado e atribuicao recente
podem mudar com processamento posterior. A nova consumiu seu teto entre 06 e
09/10; um limite total nao distribui obrigatoriamente o gasto pelos sete dias.

Na nova campanha, com atribuicao por clique de 30 dias e sem visualizacao,
foram recebidos 95 eventos de pagina, 16 de cardapio, tres de rota e dois de
inicio de reserva. Sao eventos, nao pessoas unicas nem etapas de uma mesma
coorte. Nenhuma reserva confirmada ou visita foi atribuida nessa consulta.

O GA4 registrou 81 sessoes no site e duas no portal com a UTM da nova campanha,
em 06 a 12/10. O banco tinha nove reservas publicas criadas nesse periodo,
cinco marcadas como compareceu, sem identificacao da nova campanha. Esses
totais nao devem ser creditados aos anuncios nem divididos para calcular
conversao de coorte. A reserva anterior identificada desde 23/09 ficou no_show.

## Problemas e correcoes

| Prioridade e momento | Evidencia e impacto | Acao executada ou pendente | Validacao |
| --- | --- | --- | --- |
| Bloqueador financeiro resolvido | Teto anterior esgotado de R$277,05 | Com aprovacao, teto acumulado elevado para R$577,05 e campanha ativada, com termino definido | Leitura posterior confirmou valores, data e status. Diagnostico nao mostra bloqueador de conta/orcamento |
| Importante, corrigido antes do teste | Campanha de cliques sem metas associadas; relatorio comercial incompleto | Associadas Reserva confirmada e Visita realizada | Leitura posterior confirmou as duas metas; objetivo continua cliques |
| Importante, corrigido antes do teste | Testes reproduziram heranca de oppref/IDs entre campanhas e prioridade do storage antigo sobre cookie novo | Corrigidos site e reservas; nova origem substitui a anterior; navegacao interna preserva o toque | Regressao falhou antes e passou depois; testes de storage bloqueado e GA4 preservados |
| Importante, corrigido antes do teste | Pagina do anuncio aguardava interacao ou sete segundos apos load para baixar tags; acessos curtos podiam escapar | Chegadas pagas em Conheca carregam apos primeira pintura, com teto de um segundo | Testes sem load, com duas pinturas e teto; sem duplicar SDKs. Nas demais chegadas, comportamento preservado |
| Importante, corrigido antes do teste | Pixel/CAPI presumiam Fortaleza/BR para todos os clientes, inclusive turistas; CAPI podia alterar codigo de telefone internacional | Removida localizacao presumida; telefone com + preserva pais informado | Hashes, telefone internacional e payloads testados; contrato real aceito pela API |
| Importante, corrigido antes do teste | Reserva e visita enviavam R$58 por pessoa como valor, sem consumo no PDV | Removidos valores monetarios presumidos da OpenAI e do GA4 | Testes de ausencia de valor no navegador/servidor; versao 17 da funcao implantada |
| Importante, pode iniciar junto do teste | Sem registro de clientes sem reserva vindos do anuncio | Procedimento operacional abaixo; execucao depende da equipe | Conferir registro diario, origem declarada, grupos e pagamento efetivo |
| Importante, pendente | Alvo atual e Ceara. Busca por Fortaleza retornou CEPs, sem resolver com seguranca a entidade cidade | Mantido Ceara; nao usados IDs presumidos ou colecao de CEPs | Sem bloqueio geografico no anuncio atual. Refinamento para cidade exige selecao valida no Ads Manager |
| Melhoria, durante acompanhamento | Grupo informa lance baixo; houve entrega e consumo rapido antes do teto acabar | Lance maximo de R$3,50 preservado | Revisar se, apos autorizacao de verba, houver entrega insuficiente com saldo. Aviso nao explica o teto esgotado |
| Melhoria, posterior | Sistema nao recebe consumo fechado no PDV | Integracao de consumo e margem por venda futura | Nao reportar ROAS financeiro usando valores estimados ou faturamento total da casa |

A associacao das metas e exigida para o acompanhamento de conversoes da
campanha, conforme [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement).
Nao promete recuperar retroativamente uma origem que nao foi coletada.

## Validacao e limites de prontidao

Foram aprovados 83 testes locais de atribuicao, carregamento das tags, hashes,
identificadores de deduplicacao, timestamps e isolamento do diagnostico. A
funcao do servidor passou na verificacao TypeScript e foi implantada na versao
17, preservando autenticacao e os outros provedores. Uma requisicao sem
autenticacao foi rejeitada com HTTP 401.

A API aceitou os dois contratos de evento em modo validate_only, HTTP 200.
Esse modo nao salva eventos; nao foram criadas reservas, marcados
comparecimentos ou reenviadas conversoes para testar. Os triggers de reserva
e visita estao habilitados; o worker horario existente continua ativo.

Pixel e servidor preservam o mesmo ID da reserva; o nome customizado de visita
permanece visit_realized. Isso valida o contrato de deduplicacao no codigo,
mas a primeira reserva real atribuivel ainda deve ser conferida na plataforma.
O EQS indisponivel por falta de evidencia de atribuicao nao e uma nota zero.

Valores e localizacao do cliente sao opcionais na
[Conversions API](https://developers.openai.com/ads/conversions-api);
o payload deve usar apenas informacoes conhecidas. Sem consumo apurado,
reservas e comparecimentos sao contagens de resultados.

Commits publicados: `9dc0de0` no site e `aebd092` nas reservas. A pagina do
anuncio, o cardapio, o portal e seus scripts de medicao publicados foram
comparados com os arquivos locais, com HTTP 200 e conteudo correspondente.
Configuracoes publicas e consulta de horarios responderam sem criar reserva.

O navegador integrado esta indisponivel. Testes automatizados e verificacao
HTTP cobrem codigo, contratos e arquivos publicados; a interacao visual completa
em um navegador real permanece como verificacao operacional. Nao afirmar que
o contrato aceito comprova uma venda ou toda a jornada de um cliente real.

## Estrutura aprovada e ativada

Usar a campanha existente **Sir Fisher Novos clientes Outubro 2026**, com um
grupo e o anuncio aprovado **Conheca Sir Fisher Comida e vista**. Preservar a
campanha antiga pausada, que ja terminou. O objetivo continua cliques: o volume
de reservas atribuiveis e insuficiente para justificar agora uma nova campanha
otimizada para conversoes. Nao dividir este pequeno teste entre campanhas.

Destino: Conheca, com cardapio, rotas, contato e acesso a reservas. Copy,
imagem, contexto local do grupo e lance permanecem os aprovados. Os sinais de
cardapio/rota justificam observar tambem visitas sem reserva.

| Item | Configuracao aplicada e verificada |
| --- | --- |
| Novo investimento maximo | R$300 adicionais, tratado como custo de um teste, sem retorno garantido |
| Duracao | Ativada em 13/10; termina em 20/10/2026 as 16h19min17s em Fortaleza ou no teto, o que ocorrer primeiro |
| Controle efetivo | Teto total da campanha elevado de R$277,05 para R$577,05, incluindo o gasto anterior. Modelo de orcamento total preservado; nao fixa gasto de R$40 por dia e pode consumir a verba antes |
| Total da conta em outubro | Exposicao prevista ate R$800,10 considerando os R$500,10 ja reportados, sujeito a ajustes de gasto anterior; nao e um teto configurado separado na conta |
| Geografia | Ceara, com contexto explicitamente Fortaleza/Beira-Mar. Preferencia de refinamento: cidade Fortaleza quando houver selecao valida; nao foi aplicada |
| Lance | Manter maximo existente de R$3,50 por clique; sem aumento automatico |
| Revisoes | Primeiros R$100 adicionais e encerramento. Inspecao diaria pela operacao, sem criar agenda automatica nesta entrega |
| Mudancas executadas | Novo teto, data de termino, descricao coerente e ativacao. Nao houve recarga nem alteracao de lance |

R$300 limita a exposicao financeira enquanto se recupera a medicao presencial.
O CPC observado de R$2,74 sugere ordem de grandeza de 110 cliques, sem garantia
de volume. O teste serve para obter evidencias operacionais; nao tem potencia
para comprovar causalidade ou significancia estatistica sozinho.

A leitura posterior confirmou status ativo, metas e segmentacao preservadas.
O diagnostico de entrega nao mostra bloqueadores de conta ou orcamento, mas
aponta entrega limitada por lance possivelmente baixo. O maximo permanece
R$3,50 por clique; a ativacao nao comprova novas impressoes ou cliques. Revisar
esse aviso com dados de entrega do teste, sem aumentar lance automaticamente.

## Medicao presencial e economia

Em cada atendimento, perguntar de forma neutra como a pessoa conheceu a casa
e se e sua primeira visita. Se disser ChatGPT, distinguir **anuncio pago**,
**recomendacao organica** e **nao sabe**. Nao oferecer desconto nem induzir a
resposta. Registrar grupo/comanda, quantidade de pessoas, novo/retorno,
origem declarada, comparecimento e consumo efetivamente pago no controle
interno da casa. Para reservas, usar a observacao interna existente se necessario;
para clientes sem reserva, usar o controle privado de atendimento/caixa.

Nao criar reservas ficticias para contabilizar walk-ins nem inventar oppref.
Deduplicar uma reserva que tambem consta na comanda. Nao somar comandas,
grupos, pagamentos e pessoas como se fossem a mesma unidade. Registrar tambem
origem desconhecida; ausencia de registro nao e resposta negativa.

Manter tres camadas no acompanhamento:

1. Comprovado: gasto da plataforma, reserva/visita identificada e pagamento
   real da comanda. A origem autodeclarada e registrada como tal.
2. Estimado: parcela incremental plausivel e contribuicao com custos variaveis
   estimados. Uma comanda vinculada ao anuncio nao prova sozinha incremento.
3. Desconhecido: clientes sem identificacao e consumo que nao pode ser ligado
   ao canal. Nao atribuir todo o faturamento aos anuncios.

A margem gerencial agregada de setembro, aproximadamente 49,3%, pode servir
apenas como hipotese inicial; ha classificacoes pendentes e ela nao substitui
CMV/custos variaveis dos pedidos adquiridos. Nesse cenario, R$300 exigiriam
cerca de **R$609 de consumo incremental** para cobrir a publicidade antes de
custos fixos. Com margem efetiva de 40%, seriam R$750; com 60%, R$500.
Ticket por pagamento nao e ticket por pessoa, e R$58 nao e receita apurada.

Usar a contribuicao incremental estimada menos gasto publicitario como criterio
economico, deixando explicita a hipotese de incrementalidade. Comparar turnos
equivalentes, levando em conta feriados, clima, capacidade, turistas, promocoes
e outros canais; diferenca de faturamento entre semanas nao e efeito causal
comprovado da publicidade.

## Indicadores e regras de decisao

- **Pausar imediatamente:** pagina/reservas indisponiveis, gasto fora do teto,
  erros persistentes de medicao ou falta de capacidade para atender. Nao tratar
  bloqueio de tag de um visitante isolado como falha de todo o sistema.
- **Revisar nos primeiros R$100 adicionais:** se houver pelo menos 30 cliques
  e nenhum sinal de alta intencao (rota, contato ou inicio de reserva), pausar
  para revisar mensagem/destino. E um limite operacional de perda, nao um
  teste estatistico de fracasso. Com menos cliques, manter o limite total.
- **Encerrar no teto ou no setimo dia:** conferir gasto, intencoes, reservas
  concluidas, comparecimentos e clientes sem reserva, com sua origem declarada.
  Registrar tambem reservas para datas futuras e ausencia; nao exigir que uma
  reserva futura ja tenha comparecido no dia de encerramento.
- **Manter outro teste do mesmo tamanho:** sinais de visitas reais com consumo
  pago e contribuicao incremental plausivel cobrindo o gasto, coleta funcionando
  e capacidade disponivel. Exige nova aprovacao; nao renovar automaticamente.
- **Reduzir/reformular:** ha intencao, mas consumo/contribuicao nao cobrem o
  gasto. Se a medicao presencial nao foi feita, classificar como inconclusivo e
  corrigir a operacao antes de pedir mais verba.
- **Aumentar depois:** somente apos dois ciclos comparaveis com coleta consistente
  e contribuicao incremental estimada pelo menos 30% acima do gasto. Esse 30%
  e uma folga proposta, nao benchmark validado. Nova aprovacao financeira.

## Fases e execucao autorizada

Fase 1 e fase 2: correcoes da conta/codigo, publicacao e validacoes executadas.
Restam verificacao visual
operacional, inicio do registro presencial e refinamento geografico opcional.
Essas limitacoes nao impedem um teste pequeno com medicao parcial explicita.

Fase 3: executada apos o proprietario responder que podia executar e ajustar
o teto da retomada para R$300. Aplicados **R$300 adicionais, ate sete dias,
teto acumulado R$577,05, Ceara e ativacao da campanha corrigida**. Registro
anterior e leitura posterior preservados em artefatos locais fora do Git.
Sem recarga automatica; uma nova recarga, se necessaria, exige aprovacao propria.

Fase 4: revisoes baseadas nos registros do teste e nas regras acima. Sem
integracao do PDV, sem clientes sem reserva identificados e sem comparacao
controlada, nao declarar ROAS ou CAC incremental comprovados.
