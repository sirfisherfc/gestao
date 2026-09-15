-- Carga inicial da rotina "Melhoria e Inovacao".
--
-- Sao duas listas:
--   1. 20 iniciativas ja documentadas entre 14/03/2026 e 14/09/2026, extraidas
--      do historico de conversas da operacao e conferidas, quando possivel,
--      contra os commits dos repositorios gestao, reservas e site;
--   2. 6 ideias novas para o restaurante, entrando como Recebida ou
--      Em avaliacao, sem resultado inventado.
--
-- O que NAO entra: nome de pessoa, telefone, mensagem pessoal, valor sensivel
-- e credencial. `referencia_origem` guarda apenas arquivo e faixa de linhas,
-- para quem precisar voltar a fonte. Os arquivos de origem nao sao versionados.
--
-- Re-executavel: cada registro tem `chave_carga` unica e o insert usa
-- ON CONFLICT DO NOTHING. Rodar a migration de novo nao duplica nem sobrescreve
-- o acompanhamento feito depois pela equipe.
--
-- Nenhum registro recebe responsavel: responsavel e prazo sao decisao de quem
-- for tocar a ideia, e a pagina existe justamente para isso.

begin;

insert into public.melhorias (
  chave_carga, titulo, descricao, area, origem, status, prioridade,
  primeira_manifestacao_em, prazo, proxima_acao, concluida_em,
  resultado_aprendizado, motivo_descarte, referencia_origem, criado_em
)
values
  (
    'hist-2026-03-14-delivery-cardapio-mensagens',
    'Manter o cardápio e as mensagens do delivery sob controle',
    'O aplicativo seguia oferecendo itens que a casa não produz mais, e um dos apps não notifica mensagem de cliente como o outro — é preciso abrir e conferir. Os dois pontos custam venda e reputação.',
    'Delivery', 'Equipe', 'Em andamento', 'Média',
    date '2026-03-14', date '2026-09-30',
    'Revisar item a item o cardápio de cada aplicativo e definir quem confere as mensagens em cada turno.',
    null, null, null,
    'Conversa da gerência, linhas 48722 e 49502-49516',
    timestamptz '2026-03-14 12:00-03'
  ),
  (
    'hist-2026-03-21-validade-no-recebimento',
    'Conferir a validade antes de aceitar a entrega',
    'Chegou mercadoria fora da validade e a conferência só aconteceu depois de receber. A checagem precisa ser parte do recebimento, não uma descoberta posterior.',
    'Compras e Estoque', 'Equipe', 'Concluída', 'Média',
    date '2026-03-21', null, null, date '2026-03-21',
    'Conferência de validade passou a ser feita na entrega, com a decisão de aceitar ou recusar subindo para a gerência em vez de ficar com quem recebe.',
    null,
    'Conversa da diretoria, linha 6939; conversa da praia, linha 8924',
    timestamptz '2026-03-21 12:00-03'
  ),
  (
    'hist-2026-04-01-alerta-antecipado-validade',
    'Alerta antecipado de validade e estoque',
    'A contagem encontrou 151 unidades de um mesmo rótulo a 17 dias do vencimento, sem que ninguém tivesse sido avisado antes. O estoque precisa apontar o vencimento com antecedência suficiente para escoar sem queima.',
    'Compras e Estoque', 'Equipe', 'Concluída', 'Alta',
    date '2026-04-01', null, null, date '2026-09-06',
    'O lote foi escoado com promoção, troca de preço e negociação com o fornecedor. No painel, a contagem semanal de estoque foi separada do fechamento mensal e passou a registrar revisões, dando a foto antes de o prazo apertar.',
    null,
    'Conversa da gerência, linhas 49220-49469; commits do repositório gestao em 06/09/2026',
    timestamptz '2026-04-01 12:00-03'
  ),
  (
    'hist-2026-04-07-evento-300-anos',
    'Participar como expositor no evento dos 300 anos da cidade',
    'Convite para um estande em evento oficial de grande público, por dois dias.',
    'Marketing', 'Outra', 'Descartada', 'Baixa',
    date '2026-04-07', null, null, null, null,
    'Custo de entrada, inscrição na campanha, frete dos equipamentos e equipe extra não se pagavam no período; a logística tirava gente da casa em fim de semana.',
    'Conversa da diretoria, linhas 7699-7713',
    timestamptz '2026-04-07 12:00-03'
  ),
  (
    'hist-2026-04-13-iluminacao',
    'Recuperar a iluminação da casa',
    'A iluminação caiu para cerca de 30% a 40%: cliente com dificuldade de ler o cardápio e de entrar à noite, com queda percebida nas vendas do período noturno.',
    'Estrutura', 'Equipe', 'Concluída', 'Alta',
    date '2026-04-13', null, null, date '2026-05-04',
    'Troca das lâmpadas da cozinha e instalação de quatro refletores na área da frente. Ficou o aprendizado de que manutenção de iluminação não pode esperar três semanas nem ser marcada em horário de movimento.',
    null,
    'Conversa da gerência, linhas 49726-49875 e 50246-50254',
    timestamptz '2026-04-13 12:00-03'
  ),
  (
    'hist-2026-04-15-promocao-automatica',
    'Lançar a promoção no sistema em vez de desconto manual',
    'A promoção era fechada com ajuste manual do garçom e uma parte recebida fora do lançamento, o que abre margem para erro de controle e de recebimento. A ideia é cadastrar o item promocional com o valor final já no sistema de vendas.',
    'Tecnologia', 'Equipe', 'Em avaliação', 'Média',
    date '2026-04-15', date '2026-08-15',
    'Cadastrar o item com valor final no sistema e comparar o resultado com a regra de desconto atual antes de trocar.',
    null, null, null,
    'Conversa da gerência, linhas 49780-49808',
    timestamptz '2026-04-15 12:00-03'
  ),
  (
    'hist-2026-04-22-equipe-por-movimento',
    'Ajustar a equipe à curva de movimento da casa',
    'A escala estava dimensionada por hábito, com mão de obra ociosa em dia fraco e pouca gente no pico de fim de semana. A proposta era montar a jornada a partir da curva real de movimento.',
    'Pessoas', 'Gestão', 'Concluída', 'Alta',
    date '2026-04-22', null, null, date '2026-08-18',
    'Rotina de escalas publicada no painel, com a curva de demanda por dia e hora servindo de régua para dimensionar cada turno. A cozinha passou para 5x2 e o salão iniciou a migração.',
    null,
    'Conversa da diretoria, linhas 8171-8181 e 10885-10891; commits do repositório gestao em 17-18/08/2026',
    timestamptz '2026-04-22 12:00-03'
  ),
  (
    'hist-2026-04-23-mudanca-imediata-quadro',
    'Mudar o quadro de pessoal imediatamente',
    'Pedido de reforço imediato de equipe em resposta à percepção de sobrecarga.',
    'Pessoas', 'Equipe', 'Descartada', 'Média',
    date '2026-04-23', null, null, null, null,
    'Optou-se por testar primeiro a escala 5x2 e avaliar o resultado antes de qualquer mudança de quadro.',
    'Conversa da gerência, linhas 50053-50095',
    timestamptz '2026-04-23 12:00-03'
  ),
  (
    'hist-2026-05-19-politica-grupos-grandes',
    'Definir política para grupos grandes',
    'Uma reserva de 25 pessoas chegou com 35 e ocupou o meio da casa e mesas do calçadão. Com a disposição atual só há folga para mover seis mesas, e sem regra a casa ora recusa cliente em dia fraco, ora aceita grupo que não cabe.',
    'Salão', 'Cliente', 'Em andamento', 'Média',
    date '2026-05-19', date '2026-08-31',
    'Fixar o limite de pessoas por reserva e a regra de dividir o grupo em mesas próximas em vez de recusar.',
    null, null, null,
    'Conversa da gerência, linhas 50424-50441',
    timestamptz '2026-05-19 12:00-03'
  ),
  (
    'hist-2026-05-29-substituir-sistema-vendas',
    'Avaliar a substituição do sistema de vendas',
    'O sistema caiu em horário de movimento mais de uma vez e o aplicativo deixou de carregar nas máquinas de cartão, obrigando a operar pelo celular e fechar no computador. A queda acontece justamente quando a casa enche.',
    'Tecnologia', 'Equipe', 'Em avaliação', 'Média',
    date '2026-05-29', null,
    'Registrar cada indisponibilidade com data e duração por três meses e comparar com alternativas antes de decidir.',
    null, null, null,
    'Conversa da gerência, linhas 50573, 50921 e 51387-51394',
    timestamptz '2026-05-29 12:00-03'
  ),
  (
    'hist-2026-06-07-teste-novo-produto',
    'Testar dois pratos novos de entrada',
    'Inclusão de duas entradas no cardápio, com preço e custo definidos antes do lançamento.',
    'Cozinha', 'Gestão', 'Concluída', 'Baixa',
    date '2026-06-07', null, null, date '2026-06-07',
    'Os dois itens entraram no cardápio com preço e CMV calculados. A divergência de gramatura apontada na conferência foi acertada contra a ficha técnica antes da venda — vale repetir essa conferência em todo item novo.',
    null,
    'Conversa da diretoria, linhas 8670-8693',
    timestamptz '2026-06-07 12:00-03'
  ),
  (
    'hist-2026-06-10-rotulos-fixos-cerveja',
    'Manter seis rótulos fixos de cerveja 600ml',
    'Proposta de manter simultaneamente seis rótulos de 600ml em estoque gelado.',
    'Bar', 'Gestão', 'Descartada', 'Média',
    date '2026-06-10', null, null, null, null,
    'Substituído por um mix menor com teste controlado de 30 dias: seis rótulos não cabem gelados e os candidatos disputavam a venda entre si em vez de aumentar o total.',
    'Conversa da diretoria, linhas 8875-8896',
    timestamptz '2026-06-10 12:00-03'
  ),
  (
    'hist-2026-07-08-equipamento-molho-bebida',
    'Separar os equipamentos de molho e de bebida',
    'Molho pesado estava sendo batido no liquidificador de suco, de alta rotação, queimando o aparelho.',
    'Cozinha', 'Equipe', 'Concluída', 'Baixa',
    date '2026-07-08', null, null, date '2026-07-08',
    'Multiprocessador de baixa rotação para os molhos na produção e liquidificador simples só para suco no ponto de venda. Bater molho no liquidificador passou a ser desvio de procedimento.',
    null,
    'Conversa da diretoria, linhas 9729-9769',
    timestamptz '2026-07-08 12:00-03'
  ),
  (
    'hist-2026-07-09-portal-reservas',
    'Portal de reservas próprio',
    'As reservas dependiam de um widget contratado, com e-mail saindo em domínio de terceiro e sem painel de acompanhamento.',
    'Tecnologia', 'Gestão', 'Concluída', 'Alta',
    date '2026-07-09', null, null, date '2026-07-14',
    'Portal próprio no ar em domínio da casa, com painel administrativo, bloqueio de horário, confirmação e lembrete por e-mail no domínio próprio. Os testes de ponta a ponta foram feitos pela própria equipe antes da virada.',
    null,
    'Conversa da diretoria, linhas 9806-10018; commits do repositório reservas em 09-14/07/2026',
    timestamptz '2026-07-09 12:00-03'
  ),
  (
    'hist-2026-07-12-consumo-de-gas',
    'Controlar o consumo de gás',
    'Pedido de gás feito sem conferir o que ainda havia: um pedido a mais teria custado taxa de deslocamento, e comprar fora do fornecedor habitual saiu quase vinte reais acima. A média observada é de seis a sete dias por botijão.',
    'Compras e Estoque', 'Equipe', 'Em andamento', 'Média',
    date '2026-07-12', date '2026-09-20',
    'Registrar a data de troca de cada botijão e disparar o pedido pela média, não pelo susto.',
    null, null, null,
    'Conversa da gerência, linhas 51605-51609',
    timestamptz '2026-07-12 12:00-03'
  ),
  (
    'hist-2026-08-10-anuncios-com-ia',
    'Testar anúncios assistidos por IA',
    'Teste da ferramenta de anúncio assistida por IA, ainda sem separar com clareza o que é resultado do anúncio e o que é busca natural.',
    'Marketing', 'Gestão', 'Em andamento', 'Média',
    date '2026-08-10', date '2026-10-15',
    'Separar o resultado do anúncio do tráfego natural antes de aumentar o investimento.',
    null, null, null,
    'Conversa da diretoria, linhas 10638-10639 e 11090',
    timestamptz '2026-08-10 12:00-03'
  ),
  (
    'hist-2026-08-18-anuncio-ate-comparecimento',
    'Medir o anúncio até o comparecimento do cliente',
    'Saber quem viu o anúncio é pouco: a pergunta é quem reservou e quem de fato apareceu.',
    'Marketing', 'Gestão', 'Concluída', 'Alta',
    date '2026-08-18', null, null, date '2026-09-07',
    'A atribuição do anúncio passou a ser preservada da visita ao site até a reserva, e a marcação de comparecimento no painel de reservas retorna para a origem do anúncio. A atribuição foi estendida a todas as páginas do site, não só à home.',
    null,
    'Conversa da diretoria, linhas 10870-10873; commits do repositório site em 18/08 e 06-07/09/2026',
    timestamptz '2026-08-18 12:00-03'
  ),
  (
    'hist-2026-08-18-manual-fotografico-pratos',
    'Manual fotográfico de apresentação dos pratos',
    'Ideia de um livrete com a foto de cada prato mostrando o padrão de montagem, para acabar com a variação de guarnição e acabamento entre quem produz.',
    'Cozinha', 'Gestão', 'Em avaliação', 'Média',
    date '2026-08-18', null,
    'Fotografar cada prato no padrão aprovado e montar o livrete junto com a ficha técnica.',
    null, null, null,
    'Conversa da diretoria, linhas 10846-10848',
    timestamptz '2026-08-18 12:30-03'
  ),
  (
    'hist-2026-08-18-padrao-entre-turnos',
    'Padronizar a produção entre os turnos',
    'A montagem do prato saía de um jeito pela manhã e de outro à noite, com diferença também no volume de perda. Para o cliente recorrente, é o detalhe que muda a experiência.',
    'Cozinha', 'Equipe', 'Em andamento', 'Alta',
    date '2026-08-18', date '2026-09-30',
    'Alinhar manhã e noite no mesmo padrão de montagem e passar a registrar a perda nos dois turnos.',
    null, null, null,
    'Conversa da diretoria, linhas 10840-10860',
    timestamptz '2026-08-18 13:00-03'
  ),
  (
    'hist-2026-09-12-validade-na-reetiquetagem',
    'Impedir troca de data de validade na reetiquetagem',
    'Item que chega da produção com três meses de validade estava sendo reetiquetado com prazo próprio depois do preparo final, criando duas datas para o mesmo produto. É risco sanitário antes de ser risco de estoque.',
    'Cozinha', 'Auditoria', 'Em andamento', 'Alta',
    date '2026-09-12', date '2026-09-19',
    'Fixar a regra por escrito: a validade acompanha o produto de origem, e o preparo final não gera data nova.',
    null, null, null,
    'Conversa da gerência, linhas 52912-52960; conversa da praia, linha 11242',
    timestamptz '2026-09-12 12:00-03'
  ),
  (
    'ideia-2026-09-engenharia-de-cardapio',
    'Engenharia de cardápio por margem e popularidade',
    'Cruzar quanto cada prato vende com a margem que deixa, para saber o que destacar, o que repricificar, o que redesenhar e o que sair do cardápio. O painel já tem venda por item e custo; falta a leitura conjunta.',
    'Cozinha', 'Gestão', 'Em avaliação', 'Alta',
    date '2026-09-14', null,
    'Levantar venda e margem dos últimos seis meses por item e classificar o cardápio em quatro grupos.',
    null, null, null, null,
    timestamptz '2026-09-14 09:00-03'
  ),
  (
    'ideia-2026-09-controle-desperdicio',
    'Controle de desperdício',
    'Registrar perda por motivo (quebra, queima, validade, devolução do cliente) e por turno, para atacar causa em vez de discutir número no fim do mês.',
    'Cozinha', 'Gestão', 'Recebida', 'Média',
    date '2026-09-14', null, null, null, null, null, null,
    timestamptz '2026-09-14 09:05-03'
  ),
  (
    'ideia-2026-09-pesquisa-pos-visita',
    'Pesquisa rápida pós-visita',
    'Uma pergunta só, enviada depois da visita, para separar problema de atendimento de problema de produto enquanto ainda dá para recuperar o cliente.',
    'Salão', 'Cliente', 'Recebida', 'Média',
    date '2026-09-14', null, null, null, null, null, null,
    timestamptz '2026-09-14 09:10-03'
  ),
  (
    'ideia-2026-09-experiencia-por-do-sol',
    'Experiência especial no horário do pôr do sol',
    'O movimento do fim de tarde já aparece sozinho e depois cai. Montar algo próprio para essa faixa pode segurar a mesa até o jantar.',
    'Salão', 'Gestão', 'Recebida', 'Média',
    date '2026-09-14', null, null, null, null, null, null,
    timestamptz '2026-09-14 09:15-03'
  ),
  (
    'ideia-2026-09-parceria-hoteis-pousadas',
    'Parceria de indicação com hotéis e pousadas',
    'Acordo simples de indicação com a hotelaria da região, com forma de identificar o cliente indicado para saber se a parceria dá retorno.',
    'Marketing', 'Gestão', 'Recebida', 'Baixa',
    date '2026-09-14', null, null, null, null, null, null,
    timestamptz '2026-09-14 09:20-03'
  ),
  (
    'ideia-2026-09-rastreabilidade-pescados',
    'Rastreabilidade simples da origem dos pescados',
    'Registrar fornecedor, data e lote do pescado que entra, com a etiqueta acompanhando o produto até o preparo. Resolve auditoria, ajuda na conversa com o cliente e se encaixa no controle de validade que já está em andamento.',
    'Compras e Estoque', 'Gestão', 'Em avaliação', 'Média',
    date '2026-09-14', null,
    'Definir o mínimo a registrar na entrada sem criar formulário longo para quem recebe.',
    null, null, null, null,
    timestamptz '2026-09-14 09:25-03'
  )
on conflict (chave_carga) do nothing;

commit;
