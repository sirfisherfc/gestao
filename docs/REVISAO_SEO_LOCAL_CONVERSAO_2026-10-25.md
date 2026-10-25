# Revisão de SEO, descoberta local e conversão

Data de referência: 25/10/2026, fuso America/Fortaleza. Este registro reúne a
revisão atual e o histórico necessário para retomá-la. Datas de execução,
publicação e períodos dos dados são identificados em cada trecho.

A pesquisa Semrush foi ampliada depois desta primeira entrega. O acervo,
os ajustes adicionais e a prestação de contas atual estão em
[Semrush: acervo e execução de três dias](SEMRUSH_3_DIAS_2026-10-25.md).
O consumo de 720 unidades descrito abaixo pertence à triagem inicial.

## Problema comercial e critérios

O proprietário escolheu aumentar a visibilidade e conquistar novos clientes
em 06/10. Os levantamentos de outubro mostram exposição crescente a buscas
sobre pôr do sol e uma passagem parcialmente medida até a visita. A equipe
também recebeu perguntas sobre reservas e grupos sem resposta humana na
exportação histórica do atendimento. Os registros automáticos disponíveis
medem parte dos comparecimentos; a origem dos clientes que chegam por ordem
de chegada continua sem cobertura.

Essa formulação depende de hipóteses: quem busca o pôr do sol pode estar longe
de Fortaleza; um cliente pode visitar sem reservar; uma reserva futura ainda
não pode ser classificada como ausência. Mais acessos medidos também podem
refletir as mudanças de coleta feitas em 06, 13 e 22/10.

Em 25/10, o proprietário informou mesas disponíveis em todos os horários de
hoje. Essa informação orienta a execução atual; a capacidade futura ainda
depende das condições de cada data.
Também decidiu adiar o registro de clientes sem reserva, pois não dispõe de
equipe para essa coleta. O acompanhamento usa os dados automáticos existentes;
A coleta permanece adiada, sem nova carga para a recepção. A cobertura parcial
dos resultados comerciais permanece explícita.

Priorizar: falhas de acesso e conclusão; coerência de informações que afetam a
visita; medição suficiente para decidir; descoberta comercial compatível com
a oferta. Verificar o comportamento publicado e preservar preços, capacidades,
campanhas e regras confirmadas. Resultados comerciais exigem observação após
a publicação.

## Dados atuais e interpretação

As consultas atuais usaram a propriedade GA4 `353205396` e o domínio
`sc-domain:sirfisher.com.br`. O relatório de aquisição termina em 22/10,
deixando três dias de margem em relação à execução. A janela comparável de
28 dias é 25/09–22/10 contra 28/08–24/09. Os agregados da operação foram
consultados pela rota de leitura da Management API, no projeto `portal`.

| Indicador | Janela anterior de 28 dias | Janela atual de 28 dias | Leitura permitida |
| --- | ---: | ---: | --- |
| Cliques GSC, pesquisa web | 123 | 261 | Cresceu a chegada pela pesquisa; composição por intenção mudou. |
| Impressões GSC | 21.517 | 52.400 | Maior exposição inclui consultas informacionais. |
| Cliques de consultas comerciais sem marca visíveis | 14 | 15 | O aumento geral não se repetiu nesse grupo. Consultas ocultadas pelo GSC ficam fora. |
| Cliques de consultas de pôr do sol visíveis | 14 | 109 | Este grupo explica boa parte da diferença observada nos cliques classificados. |
| Cliques de consultas de marca visíveis | 36 | 49 | Marca cresceu dentro do recorte visível. |
| Sessões GA4 do site institucional | 1.625 | 2.287 | Novas campanhas e mudanças de coleta afetam a comparação. |
| Sessões QR do site | 305 | 394 | Parte do público pode já estar no restaurante. |
| Sessões google / organic do site | 151 | 230 | Origem do GA4 e clique do GSC têm coberturas diferentes. |
| Cliques para reservar no site | 107 | 122 | São ocorrências intermediárias, sem equivalência direta a reservas. |
| Cliques de rota no site | 34 | 29 | Complementar com as rotas no Perfil da Empresa e com visitas. |
| Reservas públicas criadas no banco | 25 | 25 | A contagem operacional ficou igual nessas janelas. |
| Reservas criadas com identificadores GA | 15 de 25 | 25 de 25 | Cobertura melhorou; isso afeta eventos e atribuição observados. |
| Comparecimentos no banco, por data da visita | 13 | 13 | É outro recorte temporal; dividir por reservas criadas produziria uma taxa incoerente. |
| reservation_confirmed no GA4, propriedade | 17 | 25 | Aumento medido acompanha a cobertura; não comprova crescimento equivalente de reservas. |
| visit_realized no GA4, propriedade | 5 | 11 | A marcação operacional e a coleta limitam essa cobertura. |

A Performance API do Perfil da Empresa retornou, para as mesmas janelas de
28 dias, 380 rotas contra 421, 58 cliques no site contra 50, 158 cliques no
cardápio contra 222 e 18 ligações contra 16. Impressões por superfície:
Maps/celular, 5.967 contra 6.427; Busca/celular, 3.448 contra 3.607;
Maps/desktop, 214 contra 202; Busca/desktop, 483 contra 453. Essas contagens
não são pessoas únicas somáveis. O crescimento geral no Search Console não
foi acompanhado de aumento de rotas na ficha nem de reservas públicas criadas.
As fontes e as mudanças de coleta limitam qualquer atribuição de causa.

A janela de 90 dias completos, 25/07–22/10, retornou 457 cliques e 80.359
impressões GSC; 39 cliques comerciais sem marca, 123 de pôr do sol e 106 de
marca nas consultas visíveis. No GA4 do site, foram 4.634 sessões, das quais
700 de QR. O banco retornou 64 reservas públicas criadas, 40 com identificadores
GA, e 43 comparecimentos por data da visita. A janela anterior de 90 dias não
retornou linhas GA4/GSC; a comparação de crescimento desses indicadores fica
sem base nessa janela. A ausência de linhas é registrada como limite de
cobertura.

As dimensões `form_kind`, `reservation_stage`, `reservation_reason` e
`cta_position` foram encontradas no relatório atual. Em 22/10, o funil novo
retornou um usuário na visualização e zero nas etapas seguintes. Esse volume
permite conferir a existência da coleta e pede mais observação para avaliar
abandono. O funil é sequencial por usuário, permite eventos intermediários e
não exige a mesma sessão ou reserva; `form_kind=standard` é obrigatório em
cada etapa. Reservas do banco continuam como contagem operacional separada.

O relatório mantém 21 sessões `site / organic` na janela atual, embora as UTMs
internas tenham sido corrigidas. Esse resíduo pede investigação por data e
origem quando mudar uma decisão; ele pode refletir atribuição persistida e
não demonstra, isoladamente, um link publicado com a regra antiga.

A coorte de reservas públicas criadas em 25/09–22/10 tem 25 registros, todos
com identificadores GA. Quatro tinham visita futura no fim do período. Na
consulta atual dos estados, 11 estavam como compareceu, um como cancelada e
cinco como no-show; quatro visitas até 22/10 ainda estavam confirmadas ou
pendentes. Os recortes descrevem datas e estados diferentes. A cobertura de
desfecho pede mostrar essas contagens, sem apresentar uma taxa fechada.

No portal, a mesma janela de 28 dias retornou 261 sessões, 177 usuários e
458 visualizações. Entre as origens de sessão: QR, 23; Google, 21; Maps, 12;
ChatGPT pago, sete. Sessões e usuários do portal não devem ser somados aos do
site para formar um total de pessoas.

## Fechamento do teste pago

A leitura atual do ChatGPT Ads retornou 109 cliques, 10.487 impressões,
R$299,98, CTR de 1,04% e CPC de R$2,75 no trecho adicional. A consulta de
conversões retornou zero atribuições com janela de clique de 30 dias e sem
visualização, por data da conversão. Os dados recentes podem mudar com a
recepção e o processamento de eventos; gasto finalizado também pode atrasar
em relação às demais métricas.

A consulta solicitou 13–21/10 com fim exclusivo, mas a resposta identificou
13–20/10 com fim exclusivo. Uma consulta separada de 20–21/10 retornou vazia.
Preservar essa diferença de cobertura ao retomar o relatório. O cadastro
continua com término em 20/10 às 16h19min17s de Fortaleza. A verificação atual
de entrega confirmou `inactive`, motivo `campaign_ended`; o rótulo cadastral
`active` permanece na entidade. Nenhuma campanha, orçamento ou lance foi
alterado nesta revisão.

O GA4 informa uma ocorrência de reserva em sessão `chatgpt / paid` na janela
maior de 28 dias. Esse dado não pode ser tratado como conversão atribuída do
teste adicional de 13–20/10: período, modelo de atribuição e cobertura são
diferentes. A medição de clientes sem reserva segue como dependência da
operação. Sem consumo efetivo do cliente vinculado ao PDV e hipótese de incremento explícita,
o retorno financeiro permanece sem medição suficiente.

As duas metas existentes e a fonte de conversão foram relidas, com 30 dias
de clique e zero de visualização. O Event Quality Score retornou sem nota por
baixo volume (`low_volume`), data de referência 22/10, janela UTC de 16 a
23/10 e processamento em 24/10. Esse estado não é uma nota zero nem uma taxa
de recepção de eventos.

## Histórico recuperado

| Problema e data | Mudança e publicação | Validação registrada | Resultado medido e pendência |
| --- | --- | --- | --- |
| 06/10: aquisição e descoberta precisavam de recortes por intenção | Auditoria autenticada, registro `d2cc523` | GA4, Search Console e GBP consultados; quatro URLs com inspeção de indexação PASS | Set/2026 contra 02–31/08: GSC 146 contra 85 cliques; GBP 440 contra 437 rotas. Exposição de pôr do sol cresceu; rotas e clientes são unidades diferentes. |
| 06/10: dados locais, cardápio no Google e atribuição | Horário especial 31/12, 99Food, atributos, FoodMenus, SEO e remoção de UTMs internas; registros `767c68e` e `9c80b6a`; site `1e6472f` e sequência, reservas `d128689` | Leitura posterior da ficha/cartões e preços do FoodMenus; testes de atribuição/filas, JSON-LD e publicação funcional | Corrigida a base técnica; nenhum aumento de clientes foi atribuído a essa mudança. Pendências operacionais de preços e alérgenos foram atualizadas depois. |
| 13/10: teste pago com atribuição incompleta e valores presumidos | Site `9dc0de0`, reservas `aebd092`, função servidor v17; campanha autorizada até 20/10 às 16h19min17s ou teto acumulado R$577,05 | 83 testes locais, contratos `validate_only` HTTP 200, rejeição sem autenticação HTTP 401 e arquivos públicos conferidos | Contratos aceitos validam partes técnicas. Registros presenciais, recepção de conversões reais e consumo vinculável precisavam de conferência. |
| 15/10: pesquisa de demanda precisava distinguir intenção comercial e informacional | Prompt e critérios registrados em `853f02b`; agregados locais em `site/_materiais/seo-demanda-2026-10-15/` | Fontes salvas e captura GSC lidas antes de nova coleta | O commit registra preparação; a pesquisa e as mudanças de página tiveram entregas próprias. |
| 20/10: auditoria dos canais e teste pago | Auditoria somente de leitura; remoção de token literal legado no site `edf035d` | Publicação e scripts conferidos; acesso Meta Ads negado por permissões | Janela 13–19/10 do teste pago: 109 cliques e cerca de R$300 adicionais; nenhuma reserva ou visita atribuída nessa leitura. Walk-ins continuavam desconhecidos. Revogar credencial legada depende do serviço. |
| 20/10: página do pôr do sol precisava apoiar a visita | Horário de hoje/amanhã, fotos e ações; URL e elementos SEO preservados; site `6353d63`, registro `a1a6701` | Responsividade, teclado, atribuição e acessibilidade; HTTP e arquivos correspondentes após deploy | Linha de base 21/09–18/10: GSC 101 cliques/42.831 impressões; GA4 86 sessões de entrada, seis cliques no cardápio, um em rota e zero em reserva. Janela curta posterior ainda exige observação. |
| 22/10: acesso GA4 persistente por PC | MCP de leitura instalado e registrado, `e1d4885` | Inicialização, propriedade correta e consulta real mínima passaram | Cadastro local facilita consultas. Outra sessão pode exigir reinício para carregar o servidor. |
| 22–23/10: catálogo e impressos precisavam refletir decisões atuais | 78 produtos; catálogo, derivados e rascunho reconciliados; FoodMenus publicado em 22/10 | Log local indica 81 entradas após as duas publicações de FoodMenus | 78 produtos e 81 entradas no Google usam granularidades diferentes. Cozinha/operação ainda precisa conferir preços, rendimento e alérgenos por versão. |

O histórico dos registros está no Git de `gestao/docs/CANAL_IA.md`. Os recados
recentes do canal foram preservados conforme o limite do projeto.

## Regras e melhorias preservadas

- Unidade ativa: Av. Beira Mar, 3421, Meireles, Fortaleza, em frente ao Jardim
  Japonês. As fichas PUB e Impresa estão encerradas.
- Horário regular documentado: domingo a quinta, 9h–22h15; sexta e sábado,
  9h–23h; cozinha até 22h. Fechamento em 24 e 25/12; horário especial de 31/12
  aprovado em 06/10, das 9h até 2h de 01/01.
- Configuração de reservas relida nesta execução: até dez pessoas, corte do
  mesmo dia às 15h30, 60 dias de antecedência e tolerância de 15 minutos.
  Grupos 11–29 seguem ao WhatsApp (85) 98854-4274; eventos 30–100 sentados
  usam `/eventos/`, sujeitos à confirmação da equipe.
- Cardápio próprio em PT/EN, com fonte editorial versionada. O site lê a cópia
  embutida e pode conferir uma publicação ativa pela view pública; o rascunho
  do painel continua separado. Derivados passam pelo pipeline do handoff.
- A home recebe o QR das mesas. O QR da entrada usa campanha própria. Separar
  `qr_code` da aquisição de pessoas que ainda podem visitar a casa.
- `/conheca/` mantém `noindex,follow` e o destino aprovado do anúncio.
  `/reveillon/` no site é indexável; a página de venda no portal tem `noindex`.
- `sf_origin`, `sf_cta`, UTMs externas reais e identificadores precisam manter
  a continuidade. Tags e storage bloqueados têm de permitir reservar.
- Reserva confirmada, visita marcada e intenção por rota/contato têm definições
  próprias. Valores presumidos de R$58 por pessoa foram retirados de GA4 e
  OpenAI em 13/10; o legado Meta exige cuidado ao interpretar valor.

## Atendimento e operação

O book usa uma exportação de setembro de 2026, com 2.056 conversas e 1.327
com texto de cliente. Nas perguntas reais identificadas em 2026, 49% das 142
conversas receberam somente automação ou ficaram sem resposta humana. O
recorte cobre janeiro a setembro e descreve o histórico dessa exportação.
Havia pelo menos quatro relatos de grupos de 14 a 35 pessoas que voltaram ao
Direct após ficarem sem retorno no WhatsApp.

Nesta execução, as respostas documentadas foram alinhadas ao cardápio próprio,
ao configurador de eventos e à página de Réveillon. O texto orienta conferir
a mesa no dia, conforme disponibilidade, e evita sugerir um horário de chegada
como garantia de vaga. A implantação nos canais e o atendimento atual precisam
de verificação própria; editar o book prepara a equipe e a manutenção futura.

O procedimento de origem declarada existente no documento do teste pago fica
como histórico. Em 25/10, o proprietário adiou a coleta por falta de equipe;
esta revisão não atribui nova tarefa ao atendimento. Origem rastreada,
declarada e desconhecida continuam com significados diferentes, e a ausência
do registro não permite concluir que uma campanha deixou de trazer clientes
por ordem de chegada. Não foram criadas reservas para representar esses
clientes. Os comparecimentos e os estados já salvos no banco continuam
utilizáveis dentro da cobertura existente.

## Automações e acesso a serviços

| Fonte | Acesso encontrado e última validação registrada | Teste atual e dados utilizáveis | Limite |
| --- | --- | --- | --- |
| GA4 | Conta de serviço e scripts; MCP de leitura preparado em 22/10 e instalado/validado neste PC em 25/10 | Protocolo stdio expôs nove ferramentas só de leitura; `get_property_details` e `run_report` reais passaram na propriedade correta, fuso Fortaleza; aquisição de 28/90 dias, portal e dimensões/funil | Tags, identificadores e consolidação afetam cobertura; o funil detalhado começa em 22/10. |
| Search Console | Conta de serviço e rotinas locais; domínio validado em 06/10 | Consulta real e cinco inspeções em 25/10 | Relatório de consultas omite parte dos termos; inspeção é um retrato por URL, não garante exposição futura. |
| Perfil da Empresa | OAuth persistente de `gbp.py`, renovação real validada antes | Unidade correta relida em 25/10; cadastro, horários e resumo de avaliações | Acesso local não comprova execução da rotina na nuvem. |
| Supabase portal | Helper reutiliza credencial local da Management API | Projeto correto e consultas agregadas pela rota somente de leitura em 25/10 | Reservas, status e filas têm unidades próprias; sem registro da origem de walk-ins. |
| ChatGPT Ads Manager | Conector com conta Sir Fisher resolvida | Campanha, desempenho, conversões e metas relidos | Cobertura de data retornada difere da solicitada; zero atribuição não mede todos os clientes. |
| Google Ads | Conector próprio ausente e SDK local incompleto | Acesso de mídia não confirmado nesta execução | O conector ChatGPT Ads não é acesso a Google Ads. |
| Meta Ads | Histórico de 20/10 registrou falta de `ads_read`/`ads_management`; credencial específica de mídia ausente no ambiente/helper atual | Acesso de mídia não confirmado nesta execução | Evento enviado na fila não comprova atribuição ou gasto. |
| Semrush | MCP e schemas disponíveis; três consultas reais passaram em 25/10 | Estimativas BR e duas SERPs, com metadata de 720 unidades | Saldo/cobrança e configuração de projetos não estão expostos; sem tracking localizado ativo. |
| HTTP, navegador e PageSpeed | Scripts e navegador local automatizado | Inventário de páginas, interface PT/EN e laboratório atual | Requests de marketing foram simulados nos testes; laboratório e experiência real usam coberturas distintas. |

| Rotina ou fonte | Evidência disponível | Estado e limite |
| --- | --- | --- |
| GBP diário na nuvem Claude, 10h de Fortaleza | `ROTINA_PERFIL_GOOGLE.md` registra rotina existente e sua URL | Histórico da nuvem precisa ser conferido; configuração documentada não prova execução recente. |
| GBP local no Windows | Consulta atual ao nome da tarefa não encontrou registro neste PC; relatório local mais recente de rotina é de 28/09 | Não foi criada tarefa duplicada. O estado Disabled registrado em 13/10 pertence à observação daquele contexto. |
| Publicações GBP pelo PC | Log privado contém FoodMenus em 22/10 às 16h40 e 21h28 | Demonstra execuções pontuais; não comprova rotina diária. |
| Posts, feriados e fotos GBP | Rotina existente prevê revisão semanal; comandos simulam e só escrevem com `--publicar` | Preservar revisão humana de fotos e regras de resposta. Não criar agenda adicional. |
| Fila de conversões | Configuração e histórico real dos últimos sete dias relidos em 25/10: 170 de 170 comandos de drenagem com sucesso | Filas 25/09–24/10: GA4 visita 11 enviados; Meta e OpenAI reserva, 26 enviados cada, sem último erro. Sucesso do comando, envio e atribuição são verificações separadas. |
| Lembretes e Réveillon | Lembretes 7 de 7 comandos com sucesso; worker Réveillon 678 de 678 no histórico de sete dias | Confirmações de e-mail 28 enviadas e nove lembretes no recorte 25/09–24/10. São registros de fila, sem prova de abertura ou leitura pelo cliente. |
| Velocidade semanal | Monitor automático desativado em 13/10, conforme documentação do site | Rodadas pontuais de PageSpeed não constituem monitoramento recorrente. |
| GA4 MCP | Instalação de leitura validada em 22/10 | Cadastro, ferramentas expostas e consulta real são etapas diferentes de acesso. |

A autorização de 22/10 cobre manter FoodMenus alinhado a mudanças confirmadas
do catálogo depois da publicação do site. A rotina GBP existente também possui
regras para respostas, posts e fotos. A autorização permanente de Git e deploy
cobre as correções técnicas deste pedido. Novos gastos e novas mudanças de
campanha exigem decisão própria. Mensagens a terceiros dependem de instrução
explícita; textos antigos de diretórios continuam como propostas preparadas.

## Achados técnicos e prioridades

A leitura atual da ficha Google confirmou nota 4,7 e 813 avaliações, com
telefone e unidade corretos. O atributo de cardápio já leva a `/cardapio/`,
a reserva vai direto ao portal com UTM de Maps, e o WhatsApp usa o contato
corporativo. Encontrou também uma regressão: o período de
31/12 tinha voltado ao encerramento regular de 22h15, contrariando a decisão
de 06/10 e a jornada do Réveillon. O código de feriados substituía exceções
manuais quando a data também era feriado calculado. A correção preserva essas
exceções e registra a decisão datada de 2026, sem estendê-la a outros anos.

Foi enviado um plano que muda somente 31/12: 9h de 31/12/2026 até 2h de
01/01/2027. O Google validou o contrato, o cadastro foi relido e a leitura
posterior de `getGoogleUpdated` confirmou o horário com `pendingMask` e
`diffMask` ausentes. Os outros oito períodos especiais foram preservados.
O histórico prova a autorização específica; a execução da rotina que gerou
a regressão não foi auditada na nuvem.

FoodMenus foi comparado com o gerador atual. Após normalizar os campos de
moeda que a API devolve como texto/inteiro e os nanos omitidos, nomes, preços,
descrições e opções coincidiram. Nenhuma nova publicação de cardápio foi
necessária nesta revisão. A comparação bruta inicial de serialização não foi
tratada como alteração de preço.

Na home, a auditoria encontrou contraste insuficiente no aviso de almoço fora
do horário, em desktop/tema escuro. A página de almoço tinha uma promessa de
“garantir mesa” na FAQ estruturada. Corrigir esses pontos preserva a oferta
e melhora a coerência da informação. O instalador do MCP também precisava
resolver o caminho usado pelo Python da Microsoft Store ao iniciar o ambiente.

| Ordem e componente | Evidência e consequência provável | Correção ou experimento | Impacto / confiança / esforço | Dependência, verificação e indicador | Estado |
| --- | --- | --- | --- | --- | --- |
| 1. Horário GBP de 31/12 e gerador de feriados | API mostrava 22h15; cliente poderia receber horário diferente do evento aprovado | Restaurar 9h–2h e preservar exceções manuais/decisões datadas | Alto / alta / baixo | Autorização de 06/10 recuperada; oito regressões offline e readback Google; acompanhar consistência do horário | Implementado, testado e publicado no Google |
| 2. Resiliência do portal de reservas | Falha de configuração/rede podia deixar formulário sem handler e WhatsApp sem destino; erro no pixel e retorno tardio de horários também afetavam a jornada | Permitir tentar de novo, manter contato acessível, isolar medição e descartar resposta de horário antiga | Alto / alta / médio | Vinte testes Deno, RPCs simuladas e navegador; indicador: conclusão técnica e recuperação de erro | Implementado, testado e publicado, reservas `915e893` |
| 3. Home PT/EN, aviso de almoço | Contraste abaixo do mínimo no desktop escuro dificultava leitura | Ajustar cor sem alterar regra e horário | Médio / alta / baixo | Reteste axe em PT/EN, claro/escuro e larguras móveis/desktop; indicador: ausência da falha de contraste | Implementado, testado e publicado |
| 4. Cardápio nas páginas comerciais e FAQ | Almoço e fish and chips PT ainda tinham destinos Hubt; FAQ sugeria garantir mesa | Apontar ao cardápio próprio, retirar menção obsoleta da privacidade e alinhar promessa à regra | Alto / alta / baixo | Navegação publicada e comparação da FAQ visível/JSON-LD; indicador: acesso ao catálogo atual | Implementado, testado e publicado |
| 5. Continuidade de instruções | Docs ainda citavam Hubt, virada futura e UTMs internas artificiais | Reconciliar docs de cardápio, atendimento e GBP | Médio / alta / baixo | Diff e busca de orientações contraditórias; indicador: manutenção segue fonte atual | Implementado e revisado |
| 6. Acesso persistente GA4 por PC | Python Store resolve caminho diferente no subprocesso do ambiente | Resolver o caminho real no instalador | Médio / alta / baixo | Processo real importa analytics-mcp 0.8.0; indicador: consulta real sem reconexão | Implementado, testado e publicado |
| 7. Descoberta comercial sem marca | Cliques visíveis 14→15, enquanto pôr do sol 14→109 | Acompanhar páginas existentes e ações locais antes de criar conteúdo | Alto potencial / média / médio | Dados automáticos de GSC/GA4 por janelas fechadas; indicador: consultas comerciais e ações de visita | Plano preparado, observação posterior |
| 8. Resultado do teste pago | Zero conversão atribuída no trecho adicional; cobertura de walk-ins ausente | Fechar com métricas automáticas e limites explícitos | Alto para decisão / alta / baixo | Gasto/atribuição atuais e filas; indicador: reservas/visitas atribuídas disponíveis | Relatório preparado; novo gasto depende de decisão própria |
| 9. Ferramenta paga | Uso pontual de 720 unidades; tracking e prompts não configurados | Conferir cobrança e utilidade recorrente até 30/10 | Médio / alta / baixo | Painel autenticado para saldo/data; indicador: decisões úteis e cobertura por custo | Preparado; depende de acesso/decisão |
| 10. Informações de mesa e horários em PT/EN | Textos de reservas e FAQ ainda podiam sugerir mesa garantida ou primeira fila | Explicar regras, corte e disponibilidade; manter idioma e destino dos links | Médio / alta / baixo | Comparar texto visível, FAQ e navegação; indicador: conteúdo coerente com a regra operacional | Implementado, testado e publicado |

No portal, a correção também mantém o WhatsApp disponível no HTML antes do
JavaScript e permite tentar novamente um cancelamento após falha. A troca
de data ou tamanho do grupo invalida o horário escolhido imediatamente,
evitando que a seleção anterior atravesse o intervalo de espera da consulta.
A incidência dessas condições entre clientes reais permanece desconhecida.

O inventário técnico conferiu 14 páginas com HTTP 200 e nenhum destino interno
inexistente no recorte. As inspeções Search Console de home, cardápio, almoço
executivo, pôr do sol e Réveillon retornaram PASS, “Enviada e indexada”, com
canonicals corretos. Indexabilidade técnica e indexação confirmada foram
verificadas separadamente. O `noindex` de Conheça e da venda do Réveillon no
portal foi preservado.

## Semrush, concorrência e ferramenta paga

A coleta complementar respondeu à demanda estimada para buscas comerciais e
aos tipos de página que disputam duas dessas consultas. O responsável leu os
agregados salvos antes de consultar a API. Foram usados `phrase_these` para
12 termos e `phrase_organic` para duas SERPs, com 30 linhas explícitas em cada
uma. Os schemas, parâmetros, respostas originais e transformações foram
preservados no diretório privado da revisão.

Na base Brasil, as estimativas mensais foram: “restaurantes beira mar
fortaleza”, 1.300; singular, 720; “restaurante meireles fortaleza”, 320;
“restaurante frutos do mar fortaleza”, 260; “almoço executivo fortaleza”, 140;
“fish and chips fortaleza”, 20. Variantes próximas não devem ser somadas.
Essas estimativas ajudam a escolher perguntas; a procura local pode existir
mesmo quando a base externa retorna zero.

No snapshot da consulta singular sobre restaurante na Beira Mar, a home do
Sir Fisher apareceu na posição 6. Na consulta de almoço executivo, não entrou
nas 30 linhas solicitadas. O schema não permitiu fixar Fortaleza/dispositivo,
e o payload não informou a data do snapshot: 25/10 é a data da coleta. Essa
posição não representa uma classificação universal nem contradiz impressões
que o Search Console registra para a página.

Para descoberta em IA, a documentação atual do
[Google sobre recursos de IA na pesquisa](https://developers.google.com/search/docs/appearance/ai-features)
mantém os fundamentos de SEO, a indexação e a elegibilidade de snippets como
base; não exige arquivo ou marcação especial para IA. A documentação de
[bots da OpenAI](https://developers.openai.com/api/docs/bots) distingue o
OAI-SearchBot, usado para descoberta na busca, do GPTBot, ligado a treinamento.
Essas finalidades precisam ser consideradas separadamente em uma política de
acesso ao site.

O `robots.txt` do site permite as rotas públicas e cinco URLs comerciais foram
confirmadas como indexadas. Isso comprova o acesso técnico observado nessas
verificações. Citações e posições em respostas de IA ainda precisam de
observação por plataforma; as verificações também não testam o tratamento de
todos os IPs de bots no CDN. Nenhum arquivo especial de IA foi criado nesta
execução com promessa de melhorar citações.

Foram observadas fontes oficiais de três negócios: [Illa Mare](https://www.illamare.com.br/),
[Floresta Bar](https://florestabar.com.br/almoco-executivo-em-fortaleza/) e
[Coco Bambu Beira Mar](https://cocobambu.com/unidades/cb-beiramar).
Illa Mare e Coco Bambu separam cardápio, reserva e eventos; a página de
executivo do Floresta informa formato, horário e localização. Preços e
promoções dos concorrentes não foram confirmados como vigentes. Guias e
perfis sociais também disputam as consultas, com outra função na jornada.

A evidência favorece manter as páginas existentes e corrigir inconsistências
confirmadas. O Sir Fisher já possui home local, almoço executivo, fish and
chips PT/EN e guia da Beira Mar. A pesquisa não demonstrou necessidade de
criar páginas repetidas por bairro nem ampliar conteúdo genérico de pôr do sol.

| Item da prestação de contas | Resultado |
| --- | --- |
| Saldo inicial informado pelo proprietário | 49.900 unidades; os 100 da listagem anterior já estavam descontados. |
| Saldo inicial/final verificado no painel | Indisponível nesta execução; o MCP não expõe saldo/cobrança e o inventário do navegador não tinha sessão disponível. |
| Custo máximo previsto antes do lote | 720 unidades: 120 no lote de termos e 300 em cada SERP, a 10 unidades por linha atual. |
| Débito confirmado nos payloads | 720 unidades, em metadata das três respostas. |
| Saldo final estimado | 49.180, sujeito a uso por outras sessões; reserva de 4.900 preservada na estimativa. |
| Consumo dos tetos autorizados | 720 dos 15.000 do diagnóstico e dos 45.000 da execução; nenhuma compra de unidades. |
| Registro único | `site/_materiais/revisao-seo-2026-10-25/semrush/consumo.json`. |
| Cache e originais | `cache-index.json`, `lote-01-planejado.json`, schemas e os três `lote-01-*.json` no mesmo diretório ignorado. |
| Projeto e acompanhamento | O MCP expõe leitura de projetos e auditorias, sem criação/configuração. A listagem paga anterior vazia não foi repetida. |
| Recursos preparados | Dez termos para Fortaleza/celular e quatro prompts locais; sem configuração ou monitoramento ativo. |
| Assinatura | Plano em teste e US$199 foram informados pelo proprietário. Cobrança exibida em 31/10, checkout anterior 01/11; data, hora, fuso e causa da diferença não confirmados. Recorrência preservada. |

A cobrança dos relatórios foi conferida na
[documentação de keywords v3](https://developer.semrush.com/api/v3/seo/keyword-reports/).
O saldo e o Query Log têm consulta própria, descrita em
[API units balance](https://developer.semrush.com/api/v3/get-started/api-units-balance/).
Não foram usados backlinks, snapshots integrais ou histórico pago, pois as
perguntas atuais já tinham evidência suficiente para as correções.

Esta coleta mostrou utilidade pontual da Semrush a um custo de 720 unidades.
O benefício recorrente de US$199 por mês ainda precisa ser demonstrado para
esta unidade. GA4, Search Console, Perfil da Empresa e o controle operacional
cobrem o acompanhamento principal. Manter a ferramenta deve ter um responsável
que use tracking localizado e observações de IA em decisões recorrentes.
O próximo passo é conferir no painel saldo/cobrança e decidir até 30/10,
usando 31/10 como referência conservadora. A assinatura permanece como estava.

## Acompanhamento de 30, 60 e 90 dias

Datas de revisão propostas: 24/11/2026, 24/12/2026 e 23/01/2027. O plano fica
documentado; nenhuma agenda adicional é criada por este documento. Quem assumir
o acompanhamento deve confirmar a execução e guardar agregados privados.

| Indicador e definição | Fonte, cobertura e linha de base | Frequência e responsável proposto | Critério de decisão |
| --- | --- | --- | --- |
| Comparecimento de coorte: reservas públicas criadas na janela com visita já vencida e status compareceu / reservas públicas dessa coorte com visita já vencida | Banco operacional. Separar cancelamentos e no-show; excluir criações da equipe e mostrar futuros à parte. Usar os estados já registrados e indicar registros sem desfecho. | Semanal; responsável técnico extrai o agregado existente, sem nova coleta da equipe. | Se faltarem estados finais, apresentar cobertura e contagens; publicar uma taxa depende de uma coorte consistente. |
| Funil sequencial padrão: usuários que seguem visualização → início → tentativa → confirmação, `form_kind=standard` | GA4 e `reservation_funnel_report.py`, com cobertura a partir de 22/10. Erros/tentativas isolados são ocorrências. Tags bloqueadas reduzem cobertura. | Semanal; responsável técnico. | Corrigir falha reproduzível de conclusão de imediato; avaliar abandono com volume acumulado e motivo/etapa, sem meta percentual arbitrária. |
| Intenção por origem: sessões/usuários que chegam às páginas e ações de rota, contato e reserva, mantendo unidades próprias | GA4, com QR, pago e orgânico separados e hostnames identificados. Usar o mesmo relatório e período; não somar usuários por canal/host. | Quinzenal; responsável por marketing com suporte técnico. | Verificar se uma mudança comercial aumenta ações úteis e comparecimentos; cliques isolados ajudam a explicar a jornada. |
| Descoberta comercial sem marca: cliques e impressões do conjunto fixo de consultas comerciais | Search Console, domínio; mostrar marca e informação em grupos próprios. GSC pode omitir consultas de baixo volume. | Mensal; marketing. | Aos 30 dias, avaliar cobertura e indexação; aos 60/90, priorizar páginas existentes com intenção aderente e exposição suficiente. |
| Pôr do sol: sessões iniciadas na página e ações de visita, com geografia e dispositivo quando houver cobertura | GSC/GA4. Base 21/09–18/10: 101 cliques GSC e 86 sessões GA4; seis menu/um rota/zero reserva. Métricas de fontes diferentes não formam uma taxa entre si. | Janela fechada de 28 dias; marketing. | Acompanhar várias janelas com coleta estável. Se exposição crescer sem sinais de intenção local, revisar apresentação/oferta e manter a informação útil. |
| GBP: pedidos de rota, cliques em site/cardápio e ligação | Performance API. Base 25/09–22/10: 380 rotas, 58 cliques no site, 158 no cardápio, 18 ligações; contagens não deduplicadas entre superfícies. | Mensal após consolidação; marketing. | Comparar períodos completos equivalentes; investigar inconsistências cadastrais quando ações caírem com exposição estável. |
| Resultado da mídia: gasto e reservas/visitas atribuídas disponíveis automaticamente | Plataforma e banco. Preservar o teto histórico e a janela de atribuição; o registro de origem de walk-ins está adiado pelo proprietário. | Fechamento de cada teste; proprietário com relatório técnico. | Decidir novo investimento com a cobertura conhecida e autorização específica. Consumo incremental e ROAS financeiro permanecem sem medição suficiente. |

Aos 30 dias, conferir cobertura e falhas da jornada; aos 60, comparar janelas
completas equivalentes e ajustar a prioridade; aos 90, decidir quais mudanças
merecem manutenção e se existe base para outro teste pago. Guardar datas de
mudança de campanha/oferta, feriados, clima observado e capacidade por turno.
A janela que cruza Natal e Réveillon precisa de comentário próprio sobre
sazonalidade. Diferenças antes/depois descrevem o período e suas condições.

## Validação e limites da entrega

- Gestão/GBP: oito regressões offline aprovadas, incluindo recuperação do
  Réveillon, preservação de feriados manuais e vários períodos, fechamento de
  Natal e aplicação restrita ao ano aprovado. O código anterior foi executado
  com data fixa e reproduziu a perda do horário; o corrigido preservou a
  exceção. A revisão independente não encontrou falha bloqueante.
- Gestão: `check_project.py --require-node` aprovado, com 63 arquivos Python,
  oito JS externos, 28 blocos JS, 29 páginas, 123 contratos e 30 contratos de
  segurança. Sintaxe dos scripts novos e links locais do relatório conferidos;
  `git diff --check` sem erros.
- Site: 108 testes Deno, quatro Node do cálculo solar e 13 Python aprovados.
  Auditoria de 84 combinações locais em 14 superfícies PT/EN, com larguras
  320/390/1440 e temas claro/escuro; 12 percursos iniciais de teclado. Depois
  das correções, passaram 42 retestes dirigidos (8 + 12 + 6 + 16), com os
  percursos de teclado previstos. Contraste final: 5,15:1 no claro e 4,90:1
  no escuro.
- Reservas: commit `915e893`, 20 testes Deno e testes de navegador aprovados;
  cinco páginas públicas comparadas aos arquivos publicados. Sem reservas
  reais, marcação de comparecimento ou reenvio de conversões para demonstrar
  funcionamento.

Os testes de navegador interceptaram o marketing externo e simularam as
respostas necessárias, preservando as métricas e a operação. Eles verificam
comportamento técnico; não medem uma jornada comercial real. Resultados de
laboratório do PageSpeed têm outra cobertura em relação ao CrUX histórico.
Nenhum ganho em comparecimentos foi atribuído às mudanças desta execução.

Após o deploy do site, a home retornou PageSpeed 100 nas quatro categorias
em celular e desktop. No laboratório móvel: LCP 1,8 s, bloqueio total 10 ms e
CLS 0,021; desktop: LCP 0,4 s, bloqueio total e CLS zero. No CrUX histórico,
LCP 1.574 ms, INP 148 ms e CLS zero; a janela de campo ainda não mede um efeito
isolado desta publicação. A nota inicial desktop 96 em acessibilidade passou
a 100 após corrigir o contraste.

O site foi enviado no commit
[`c0eabff`](https://github.com/sirfisherfc/site/commit/c0eabff3cfa47a97ccd4b6a5510f0d391dc04298).
O verificador de assets e o GitHub Pages passaram. Quatorze arquivos públicos
alterados, incluindo HTML, CSS e sitemap, responderam HTTP 200 e coincidiram
com o conteúdo local normalizado, consultados pelas URLs comuns com pedido de
revalidação de cache. Nenhum purge foi necessário. O portal foi publicado em
[`915e893`](https://github.com/sirfisherfc/reservas/commit/915e893).
A documentação e a prevenção da regressão GBP pertencem ao commit desta
revisão em `gestao`; a alteração externa de horário foi conferida pela API.

O navegador contra o domínio publicado aprovou 12 casos em 390/1440 px:
home PT/EN, almoço executivo, fish and chips PT, privacidade e reservas.
Foram conferidos o total de 813 avaliações, idioma nos links do portal,
destino do cardápio próprio, texto atualizado de privacidade e ausência das
promessas de primeira fila. Os casos passaram sem overflow, erro JS ou CSP,
com marketing bloqueado e sem gravação operacional.

As evidências privadas ficam em
`site/_materiais/revisao-seo-2026-10-25/`, incluindo aquisição de 28/90 dias,
funil, coortes, portal, GBP, inspeções de indexação, Semrush e QA.
O plano, antes/depois e processamento do horário especial ficam em
`gestao/tmp/gbp/seo-20261025/`; o registro de publicação também foi gravado
pela rotina existente. Esses diretórios são ignorados pelo Git.

## Pendências e próximo passo

| Dependência real | Próximo passo exato | Decisão ou condição |
| --- | --- | --- |
| Utilidade recorrente e cobrança Semrush | Conferir painel, Query Log, data/hora/fuso da cobrança e os recursos incluídos até 30/10 | Proprietário decide se o benefício justifica US$199; assinatura e recorrência ficam preservadas nesta execução. |
| Histórico da rotina GBP na nuvem | Abrir a rotina existente e conferir data/resultado da última sessão, inclusive o código atualizado | Exige acesso ao histórico da nuvem; a tarefa local ausente não justifica duplicar agendamento. |
| Cobertura comercial de clientes sem reserva | Manter como limite dos resultados automáticos | Registro adiado pelo proprietário em 25/10; sem nova tarefa para recepção. |
| Preços, porções e alérgenos do catálogo | Preservar `em_conferencia` e registrar futuras confirmações por versão no handoff | A conferência formal da operação/cozinha continua pendente; nenhum preço ou alérgeno foi escolhido pela auditoria. |
| Acessos separados a Google Ads e Meta Ads | Obter relatório autorizado se uma decisão futura de mídia precisar desses canais | Acesso atual não confirmado; conector ChatGPT Ads e filas não substituem relatórios de gasto/atribuição desses provedores. |
| Resultados após as correções | Usar as revisões de 30/60/90 dias com os mesmos recortes e cobertura | Não há necessidade de esperar 90 dias para concluir a implantação atual. |

Textos antigos de correção de diretórios permanecem como material preparado;
o envio a terceiros precisa de instrução explícita. A execução atual não
criou monitoramento de posição/IA nem novas agendas. A clareza factual e a
acessibilidade ajudam a leitura das páginas por pessoas e sistemas; citações
e posições em respostas de IA dependem de observação por plataforma.

## Documentação preparada nesta execução

- `CARDAPIO.md`: fonte editorial atual, operação do painel e QR/atribuição
  reconciliados com o handoff. Removidos plano de virada já superado e sugestão
  antiga de UTM artificial em link interno.
- `ROTINA_PERFIL_GOOGLE.md`: destino do cardápio próprio e limites do inventário
  das rotinas neste PC.
- `HANDOFF_CHATGPT_ADS.md` e `RETOMADA_CHATGPT_ADS_2026-10-13.md`: retomada de
  outubro identificada como autorizada e histórica; decisão de 25/10 adia a
  coleta presencial. Novos gastos mantêm decisão própria.
- `BOOK_QA_ATENDIMENTO.md`: destinos e regras atuais documentados, com período
  explícito para as falhas históricas e implantação nos canais a conferir.

As cópias versionadas de AGENTS e README do workspace foram comparadas por
SHA256 às cópias da raiz em 25/10 e são idênticas. Aplicações financeiras,
cadastro de produtos e banco não foram alterados por esta execução.

## Sincronização dos repositórios

Os três projetos começaram limpos em `main`, com remotos oficiais e
divergência 0/0 em relação a `origin/main`. Os três `pull --ff-only` do início
confirmaram atualização. O site e as reservas concluíram seus pushes e
verificações em `main`; gestão publica as mudanças deste registro e do GBP
em seu commit próprio. A conferência final após os pushes usa `git status`
e divergência HEAD/origin para os três projetos, sem criar repositório na
raiz, incluir arquivos privados ou descartar trabalho.

| Projeto | Remoto | Commit da entrega |
| --- | --- | --- |
| site | `sirfisherfc/site` | `c0eabff` |
| reservas | `sirfisherfc/reservas` | `915e893` |
| gestao | `sirfisherfc/gestao` | Commit desta revisão, identificado no fechamento da entrega |
