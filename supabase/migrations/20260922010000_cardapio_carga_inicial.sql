-- Carga inicial do cardapio: os 81 registros do cadastro, reconciliados
-- com o cardapio HTML e com o cardapio impresso em 2026-09-22.
--
-- Gerado por scripts/cardapio/gerar_migration.py a partir de
-- catalogo_inicial.json. Nao editar a mao: edite o catalogo e gere de novo.
--
-- Entra como RASCUNHO. Nada aqui foi validado pela cozinha ou pela
-- operacao: precos, porcoes e declaracoes alimentares carregam a fonte e
-- o estado de revisao, e as pendencias ficam visiveis para quem edita.
-- A publicacao e um ato humano, na rotina Gestao -> Rotinas -> Cardapio.
--
-- Re-execucao: cada linha so e sobrescrita enquanto continuar marcada
-- como 'carga-inicial' em fontes. Depois que alguem da casa editar o
-- produto, a carga passa a respeitar a edicao.

begin;

-- Categorias -----------------------------------------------------------
insert into public.cardapio_categoria (id, nome, resumo, grupo, subgrupos, ordem)
values
  ('fish-and-chips', 'Fish & Chips', 'O prato da casa, em duas massas diferentes.', 'comer', '[]'::jsonb, 0),
  ('petiscos', 'Petiscos e porções', 'Para dividir na mesa enquanto a conversa corre.', 'comer', '[{"id": "mar", "nome": "Do mar"}, {"id": "terra", "nome": "Da terra"}, {"id": "fritas", "nome": "Fritas e acompanhamentos"}]'::jsonb, 1),
  ('sanduiches', 'Sanduíches', 'Em pão brioche, servidos individualmente.', 'comer', '[]'::jsonb, 2),
  ('para-dividir', 'Pratos para compartilhar', 'Servidos na travessa, com arroz, batata frita (ou macaxeira), salada, farota e molho artesanal.', 'comer', '[]'::jsonb, 3),
  ('sobremesas', 'Sobremesas e café', 'Para fechar a conta com doce.', 'comer', '[]'::jsonb, 4),
  ('cervejas', 'Cervejas e chope', 'Long neck, garrafa 600 e chope.', 'beber', '[]'::jsonb, 5),
  ('coqueteis', 'Coquetéis', 'Clássicos e criações da casa.', 'beber', '[]'::jsonb, 6),
  ('sem-alcool', 'Bebidas sem álcool', 'Águas, sucos, refrigerantes e energético.', 'beber', '[]'::jsonb, 7),
  ('doses', 'Doses e aperitivos', 'Destilados em dose de 50 mL.', 'beber', '[]'::jsonb, 8),
  ('extras', 'Extras e serviços', 'Adicionais, itens de apoio e cobranças da casa.', 'extras', '[{"id": "comestiveis", "nome": "Adicionais do prato"}, {"id": "apoio", "nome": "Itens de apoio"}, {"id": "cobrancas", "nome": "Cobranças"}]'::jsonb, 9)
on conflict (id) do update set
  nome = excluded.nome, resumo = excluded.resumo, grupo = excluded.grupo,
  subgrupos = excluded.subgrupos, ordem = excluded.ordem
where public.cardapio_categoria.atualizado_por is null;

-- Sinonimos de busca ---------------------------------------------------
-- Variantes de grafia e de regiao, nao sinonimos inventados sobre receitas.
insert into public.cardapio_sinonimo (termo, alternativas) values
  ('agua de coco', array['coco']::text[]),
  ('batata frita', array['fritas', 'batatas']::text[]),
  ('camarao', array['camarões', 'camarao']::text[]),
  ('chope', array['chopp', 'chopinho']::text[]),
  ('fish and chips', array['fish n chips', 'fish chips', 'peixe com batata']::text[]),
  ('macaxeira', array['mandioca', 'aipim']::text[]),
  ('pescada amarela', array['peixe']::text[]),
  ('refrigerante', array['refri']::text[])
on conflict (termo) do update set alternativas = excluded.alternativas;

-- Avisos gerais --------------------------------------------------------
-- O aviso geral do impresso fica aqui, separado da matriz por prato: ele
-- nao vira presenca confirmada nem contato cruzado de item nenhum.
insert into public.cardapio_aviso (id, titulo, texto, fonte, citacao, estado, ordem) values
  ('alergenos', 'Sobre alérgenos', 'As marcações de cada prato foram transcritas do cardápio impresso e ainda não foram conferidas com a cozinha. Elas não substituem uma ficha técnica. Antes de pedir, fale com a equipe sobre alergias e restrições.', 'Sir Fisher Praia.pdf, rodapé da página 1', 'ALÉRGICOS: PODE CONTER CAMARÃO E GLÚTEN.', 'declarado_no_impresso', 0)
on conflict (id) do update set
  titulo = excluded.titulo, texto = excluded.texto, fonte = excluded.fonte,
  citacao = excluded.citacao, estado = excluded.estado;

-- Produtos -------------------------------------------------------------

-- Sir Fisher — Fish & Chips (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'sir-fisher-fish-n-chips', 'fish-and-chips', null, 'Sir Fisher — Fish & Chips',
  'Sir Fisher - Fish N’ Chips', 'pescada amarela em crosta de panko, com batatas',
  'Pescada amarela envolta em farinha panko, crocante por fora e suculenta por dentro. Acompanha batatas palito.',
  'Nossa interpretação do clássico Fish & Chips: a pescada amarela é envolta em uma crosta de farinha panko, garantindo textura crocante por fora e suculência por dentro. Acompanhado de batatas palito.',
  4500, 0,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "divergente", "divergencia": "Cardápio HTML: 150 g. Cardápio impresso: 200 g.", "nota": "Peso em conferência com a cozinha.", "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": ["PEIXE", "GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "prato", "larguras": [800, 1200], "alt": "Filés de peixe empanados com batatas fritas, servidos em uma tábua com a bandeira britânica", "estado": "a_confirmar", "nota": "A foto mostra peixe empanado ao estilo panko. Confirmar com a operação se corresponde a esta versão ou à London."}'::jsonb,
  array['peixe', 'pescada amarela', 'panko', 'empanado', 'batata frita', 'fish and chips']::text[],
  array['do-mar', 'classico-da-casa']::text[],
  true,
  array['porcao', 'foto']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O TXT e o HTML trazem o selo “Mais Pedido!”. É uma alegação de popularidade sem dado de vendas: não foi publicada.', 'Porção: Cardápio HTML: 150 g. Cardápio impresso: 200 g.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- London — Fish & Chips (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'london-fish-n-chips', 'fish-and-chips', null, 'London — Fish & Chips',
  'London - Fish N’ Chips', 'peixe em massa fermentada na cerveja, com batatas',
  'Peixe envolto em leve massa fermentada na cerveja e frito até dourar. Acompanha batatas crocantes.',
  'Autêntico Fish & Chips: o peixe é envolto em uma leve massa fermentada na cerveja e frito até atingir a perfeição dourada. Acompanhado de batatas crocantes, inspirado nas barracas à beira-mar das praias inglesas.',
  4500, 1,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "divergente", "divergencia": "Cardápio HTML: 150 g. Cardápio impresso: 200 g.", "nota": "Peso em conferência com a cozinha.", "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": ["PEIXE", "GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['peixe', 'cerveja', 'massa', 'batata frita', 'fish and chips', 'original']::text[],
  array['do-mar', 'classico-da-casa']::text[],
  true,
  array['porcao', 'nome']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O cardápio impresso chama esta versão de “Original — Fish N’ Chips”. A descrição coincide, mas o nome não foi trocado sem confirmação da operação.', 'Porção: Cardápio HTML: 150 g. Cardápio impresso: 200 g.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Patinha de Caranguejo (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'patinha-de-caranguejo', 'petiscos', 'mar', 'Patinha de Caranguejo',
  'Patinha de caranguejo', null,
  'Patas empanadas e crocantes. Acompanha batata frita e molho da casa.',
  null,
  5500, 2,
  array['Batata frita', 'Molho da casa']::text[],
  '[]'::jsonb,
  '{"texto": "10 unidades", "principal": null, "total": null, "unidades": {"quantidade": 10, "rotulo": "patas"}, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["TXT", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["O nome e a descrição citam caranguejo, mas o impresso não traz o símbolo de CRUSTÁCEOS neste bloco. Divergência registrada para conferência: a ausência do símbolo não indica ausência do ingrediente."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['caranguejo', 'patinha', 'empanado', 'frutos do mar']::text[],
  array['do-mar']::text[],
  true,
  array['alimentar', 'nome']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso usa “PATA DE CARANGUEJO”; o cadastro usa “Patinha de caranguejo”. Nome de exibição mantido conforme o cadastro.', 'Alimentar: O nome e a descrição citam caranguejo, mas o impresso não traz o símbolo de CRUSTÁCEOS neste bloco. Divergência registrada para conferência: a ausência do símbolo não indica ausência do ingrediente.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Bolinha de Peixe Cremosa (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'bolinha-de-peixe-cremosa', 'petiscos', 'mar', 'Bolinha de Peixe Cremosa',
  'Bolinha de Peixe Cremosa', null,
  'Seis bolinhas de pescada amarela com recheio cremoso de cream cheese.',
  null,
  4400, 3,
  '{}',
  '[]'::jsonb,
  '{"texto": "6 unidades", "principal": null, "total": null, "unidades": {"quantidade": 6, "rotulo": "bolinhas"}, "rende_pessoas": null, "estado": "parcial", "divergencia": "Peso divergente — TXT e HTML: 300 g. Cardápio impresso: 200 g.", "nota": null, "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["A descrição cita pescada amarela, mas o impresso não traz o símbolo de PEIXE neste bloco. Divergência registrada para conferência."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['peixe', 'pescada amarela', 'cream cheese', 'bolinha']::text[],
  array['do-mar']::text[],
  true,
  array['porcao', 'alimentar']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Porção: Peso divergente — TXT e HTML: 300 g. Cardápio impresso: 200 g.', 'Alimentar: A descrição cita pescada amarela, mas o impresso não traz o símbolo de PEIXE neste bloco. Divergência registrada para conferência.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- NewCastle (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'newcastle', 'petiscos', 'mar', 'NewCastle',
  'NewCastle', 'camarões empanados com batatas',
  'Crocantes por fora, em farinha panko. Inspirado nas ruas de Londres.',
  'Camarões empanados com uma mistura crocante de farinha panko. Acompanha porção de batatas. Uma explosão de sabores inspirada nas vibrantes ruas londrinas.',
  6000, 4,
  array['Porção de batatas']::text[],
  '[]'::jsonb,
  '{"texto": "250 g", "principal": {"valor": 250, "unidade": "g", "alcance": "indefinido"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["CRUSTÁCEOS", "GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "newcastle-camarao-empanado-sir-fisher", "larguras": [440, 660], "alt": "Camarões empanados dourados servidos com batatas fritas e molho, em tábua de madeira", "estado": "conferido"}'::jsonb,
  array['camarao', 'camarões', 'empanado', 'panko', 'batata frita', 'frutos do mar']::text[],
  array['do-mar']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso não cita o acompanhamento de batatas. Omissão não retira o acompanhamento declarado no cadastro.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Crocante de Carne de Sol com Abóbora (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'crocante-carne-de-sol', 'petiscos', 'terra', 'Crocante de Carne de Sol com Abóbora',
  'Crocante de Carne de Sol com...', null,
  'Seis bolinhos crocantes em leve massa de abóbora, com recheio cremoso de carne de sol.',
  null,
  3800, 5,
  '{}',
  '[]'::jsonb,
  '{"texto": "6 unidades / 360 g", "principal": null, "total": {"valor": 360, "unidade": "g"}, "unidades": {"quantidade": 6, "rotulo": "bolinhos"}, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['carne de sol', 'abobora', 'bolinho', 'crocante']::text[],
  array['da-terra']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Nome truncado no TXT (“Crocante de Carne de Sol com...”). Completado pelo HTML e pelo impresso, que coincidem.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Crocante de Calabresa e Alho Poró (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'crocante-calabresa', 'petiscos', 'terra', 'Crocante de Calabresa e Alho Poró',
  'Crocante de Calabresa e Alho...', null,
  'Seis bolinhos crocantes recheados com calabresa frita e alho-poró.',
  null,
  3800, 6,
  '{}',
  '[]'::jsonb,
  '{"texto": "6 unidades / 360 g", "principal": null, "total": {"valor": 360, "unidade": "g"}, "unidades": {"quantidade": 6, "rotulo": "bolinhos"}, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['calabresa', 'alho poro', 'bolinho', 'crocante']::text[],
  array['da-terra']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Nome truncado no TXT. Completado pelo HTML e pelo impresso.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Big Ben Fries (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'big-ben-fries', 'petiscos', 'fritas', 'Big Ben Fries',
  'Big Ben Fries', 'batata frita com cheddar cremoso e bacon',
  null,
  null,
  3300, 7,
  '{}',
  '[]'::jsonb,
  '{"texto": "200 g", "principal": null, "total": {"valor": 200, "unidade": "g"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO", "CORANTES"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['batata frita', 'cheddar', 'bacon', 'fritas']::text[],
  array['da-terra', 'para-compartilhar']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Pasteizinhos (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'pasteizinhos', 'petiscos', 'terra', 'Pasteizinhos',
  'Pasteizinhos', null,
  'Dez pastéis crocantes com molho especial. Sabor a escolher.',
  null,
  3700, 8,
  array['Molho especial']::text[],
  '[{"texto": "2 queijos", "estado": "declarado"}, {"texto": "Carne", "estado": "declarado"}, {"texto": "Camarão", "estado": "declarado"}]'::jsonb,
  '{"texto": "10 unidades", "principal": null, "total": null, "unidades": {"quantidade": 10, "rotulo": "pastéis"}, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["LACTOSE", "CRUSTÁCEOS", "GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos são do bloco com os três sabores. O impresso não separa as marcações por sabor."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['pastel', 'pasteizinho', 'queijo', 'carne', 'camarao']::text[],
  array['da-terra', 'para-compartilhar']::text[],
  true,
  array['opcoes']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Nenhuma fonte informa se é possível misturar sabores em uma mesma porção. Pendente de confirmação com a operação.', 'Os três sabores são opções de um mesmo registro, com preço único. Não foram desdobrados em produtos separados.', 'Alimentar: Os símbolos são do bloco com os três sabores. O impresso não separa as marcações por sabor.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Crispy Spicy Chicken (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'crispy-spicy-chicken', 'petiscos', 'terra', 'Crispy Spicy Chicken',
  'Crispy Spicy Chicken', 'rolinhos de frango empanados recheados com queijo',
  'Marinado em especiarias e frito na hora. Acompanha molho cremoso.',
  null,
  3700, 9,
  array['Molho cremoso']::text[],
  '[]'::jsonb,
  '{"texto": "200 g", "principal": null, "total": {"valor": 200, "unidade": "g"}, "unidades": null, "rende_pessoas": null, "estado": "parcial", "divergencia": "O impresso descreve “4 grandes rolinhos” e não informa peso. As duas informações podem se somar; confirmar a apresentação vigente.", "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['frango', 'queijo', 'empanado', 'apimentado', 'rolinho']::text[],
  array['da-terra']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Porção: O impresso descreve “4 grandes rolinhos” e não informa peso. As duas informações podem se somar; confirmar a apresentação vigente.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Filé Mignon Trinchado (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'file-mignon-trinchado', 'petiscos', 'terra', 'Filé Mignon Trinchado',
  'Filé Mignon Trinchado', null,
  'Filé mignon acebolado, servido com batata frita ou macaxeira dourada.',
  null,
  8400, 10,
  '{}',
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g", "principal": {"valor": 300, "unidade": "g", "alcance": "indefinido"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não delimita se os 300 g são da carne ou do prato montado.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['file mignon', 'carne', 'acebolado', 'batata frita', 'macaxeira']::text[],
  array['da-terra', 'para-compartilhar']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Produto distinto do “Filé Mignon” dos pratos para compartilhar (R$ 90,00), que vem com arroz, salada, farota e molho.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Caldo de Peixe (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'caldo-de-peixe', 'petiscos', 'mar', 'Caldo de Peixe',
  'Caldo de Peixe', null,
  'Caldo de pescada amarela, leve e cheio de sabor.',
  null,
  1800, 11,
  '{}',
  '[]'::jsonb,
  '{"texto": "200 mL", "principal": null, "total": {"valor": 200, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "PEIXE", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['caldo', 'peixe', 'pescada amarela', 'sopa']::text[],
  array['do-mar']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Camarão alho e óleo (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'camarao-alho-e-oleo', 'petiscos', 'mar', 'Camarão alho e óleo',
  'Camarão alho e óleo', null,
  'Camarão G salteado no alho e óleo.',
  null,
  4700, 12,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 g", "principal": {"valor": 300, "unidade": "g", "alcance": "indefinido"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "CRUSTÁCEOS"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "camarao-alho-e-oleo-sir-fisher", "larguras": [440, 660], "alt": "Camarões inteiros salteados com alho, servidos em travessa com limão", "estado": "conferido"}'::jsonb,
  array['camarao', 'alho', 'frutos do mar', 'salteado']::text[],
  array['do-mar']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Dadinho de Tapioca (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'dadinho-de-tapioca', 'petiscos', 'terra', 'Dadinho de Tapioca',
  'Dadinho de Tapioca', null,
  'Doze dadinhos de tapioca crocantes por fora e macios por dentro, com molho especial.',
  null,
  2900, 13,
  array['Molho especial']::text[],
  '[]'::jsonb,
  '{"texto": "12 unidades", "principal": null, "total": null, "unidades": {"quantidade": 12, "rotulo": "dadinhos"}, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "dadinho-de-tapioca-sir-fisher", "larguras": [440, 660], "alt": "Cubos de tapioca dourados servidos com molho em tigela", "estado": "conferido"}'::jsonb,
  array['tapioca', 'dadinho', 'queijo coalho', 'petisco']::text[],
  array['da-terra', 'para-compartilhar']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Calabresa Acebolada com Fritas (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'calabresa-acebolada-com-fritas', 'petiscos', 'terra', 'Calabresa Acebolada com Fritas',
  'Calabresa Acebolada com Fritas', null,
  'Calabresa acebolada com porção generosa de batata frita ou macaxeira crocante.',
  null,
  4600, 14,
  '{}',
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "250 g", "principal": {"valor": 250, "unidade": "g", "alcance": "indefinido"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não delimita se os 250 g são da calabresa ou do prato montado.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['calabresa', 'linguica', 'acebolada', 'batata frita', 'macaxeira']::text[],
  array['da-terra', 'para-compartilhar']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Macaxeira Frita ou Batata Frita (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'macaxeira-ou-batata-frita', 'petiscos', 'fritas', 'Macaxeira Frita ou Batata Frita',
  'Macaxeira Frita ou Batata Frita', null,
  'Macaxeira ou batata frita, douradinhas. Escolha uma das duas.',
  null,
  2700, 15,
  '{}',
  '[{"texto": "Macaxeira frita", "estado": "declarado"}, {"texto": "Batata frita", "estado": "declarado"}]'::jsonb,
  '{"texto": "250 g", "principal": null, "total": {"valor": 250, "unidade": "g"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['macaxeira', 'mandioca', 'aipim', 'batata frita', 'fritas']::text[],
  array['da-terra', 'para-compartilhar']::text[],
  true,
  array['opcoes']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Registro único com duas opções de escolha. Não foi desdobrado em dois produtos: nenhuma fonte dá preço separado para cada uma.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Isca de Peixe (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'isca-de-peixe', 'petiscos', 'mar', 'Isca de Peixe',
  'Isca de Peixe', null,
  'Tiras de pescada amarela empanadas ao panko, com molho especial.',
  null,
  4200, 16,
  array['Molho especial']::text[],
  '[]'::jsonb,
  '{"texto": "250 g", "principal": null, "total": {"valor": 250, "unidade": "g"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "PEIXE", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "isca-de-peixe-sir-fisher", "larguras": [440, 660], "alt": "Tiras de peixe empanadas servidas em tábua com limão e molho", "estado": "conferido"}'::jsonb,
  array['peixe', 'pescada amarela', 'isca', 'empanado', 'panko']::text[],
  array['do-mar', 'para-compartilhar']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Fisher Burger (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'fisher-burger', 'sanduiches', null, 'Fisher Burger',
  'Fisher Burger', 'hambúrguer de pescada amarela empanada',
  'Em pão brioche, com picles e molho especial.',
  'O Fisher Burger é uma criação inspirada nas delícias do mar. Duas fatias de filé de pescada amarela, empanadas para uma crocância perfeita, dispostas em pão brioche. Complementado por picles e um molho especial.',
  3700, 17,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "parcial", "divergencia": "As fontes citam 120 g sem dizer se é o total das duas fatias ou o peso de cada uma.", "nota": "Peso em conferência com a cozinha.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "PEIXE", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['hamburguer', 'sanduiche', 'peixe', 'pescada amarela', 'brioche', 'empanado']::text[],
  array['do-mar']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O sanduíche custa R$ 37,00. O adicional de batata (R$ 9,90) é a primeira oferta estruturada no HTML e nunca deve ser lido como preço do produto.', 'Porção: As fontes citam 120 g sem dizer se é o total das duas fatias ou o peso de cada uma.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('fisher-burger', 'Adicionar batata frita', 990, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'fisher-burger' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Edimburger (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'edimburger', 'sanduiches', null, 'Edimburger',
  'Edimburger', 'blend de 120 g de bovino com bacon',
  'Em pão brioche, com alface, tomate, maionese especial e cheddar.',
  'O Edimburger presta homenagem à capital da Escócia com um blend de 120 g de carne, composto por bovino e bacon. Servido em pão brioche macio, com alface crocante, tomate fresco, maionese especial e fatias generosas de cheddar.',
  3700, 18,
  '{}',
  '[]'::jsonb,
  '{"texto": "120 g de carne", "principal": {"valor": 120, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência.", "fontes": ["TXT", "HTML", "PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['hamburguer', 'sanduiche', 'carne', 'bovino', 'bacon', 'cheddar', 'brioche']::text[],
  array['da-terra']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Preço do sanduíche: R$ 37,00. O adicional de batata é informação separada.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('edimburger', 'Adicionar batata frita', 990, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'edimburger' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Marine Sandwich (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'marine-sandwich', 'sanduiches', null, 'Marine Sandwich',
  'Marine Sandwich', 'camarões salteados com cream cheese empanado',
  'Com molho aioli, alface e pepino, em pão brioche.',
  null,
  4600, 19,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": "Nenhuma fonte informa peso ou quantidade.", "fontes": []}'::jsonb,
  '{"declarados": ["GLÚTEN", "CRUSTÁCEOS", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "marine-sandwich-sir-fisher", "larguras": [440, 660], "alt": "Sanduíche em pão brioche coberto de camarões salteados", "estado": "conferido"}'::jsonb,
  array['camarao', 'sanduiche', 'cream cheese', 'aioli', 'brioche', 'frutos do mar']::text[],
  array['do-mar']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso não cita o pepino presente no cadastro. Omissão não retira o ingrediente.', 'Preço do sanduíche: R$ 46,00. Adicional de batata em separado.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('marine-sandwich', 'Adicionar batata frita', 990, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'marine-sandwich' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Filé Mignon (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'file-mignon-dividir', 'para-dividir', null, 'Filé Mignon',
  'Filé Mignon', null,
  'Filé mignon suculento, com molho madeira ou preparado ao alho e óleo.',
  null,
  9000, 20,
  array['Arroz', 'Batata frita ou macaxeira', 'Salada', 'Farota', 'Molho artesanal']::text[],
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g de proteína", "principal": {"valor": 300, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não informa quantas pessoas o prato serve.", "fontes": ["PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "file-mignon-sir-fisher", "larguras": [440, 660], "alt": "Travessa com filé mignon ao molho, arroz, batata frita e farofa", "estado": "conferido"}'::jsonb,
  array['file mignon', 'carne', 'molho madeira', 'alho e oleo', 'para dividir', 'compartilhar', 'arroz', 'farota']::text[],
  array['para-compartilhar']::text[],
  true,
  array['rendimento']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso declara 300 g de proteína e o rodapé informa peso in natura. Nenhuma fonte informa quantas pessoas o prato serve: o rendimento não foi deduzido do peso.', 'Alimentar: Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('file-mignon-dividir', 'Arroz extra', 1200, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'file-mignon-dividir' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Picanha Importada (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'picanha-importada', 'para-dividir', null, 'Picanha Importada',
  'Picanha Importada', null,
  'Picanha importada, grelhada no charbroil para realçar sabor e suculência.',
  null,
  9900, 21,
  array['Arroz', 'Batata frita ou macaxeira', 'Salada', 'Farota', 'Molho artesanal']::text[],
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g de proteína", "principal": {"valor": 300, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não informa quantas pessoas o prato serve.", "fontes": ["PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "picanha-importada-sir-fisher", "larguras": [440, 660], "alt": "Travessa com fatias de picanha grelhada, arroz, batata frita e farofa", "estado": "conferido"}'::jsonb,
  array['picanha', 'carne', 'importada', 'grelhada', 'charbroil', 'para dividir', 'compartilhar', 'arroz', 'farota']::text[],
  array['para-compartilhar']::text[],
  true,
  array['rendimento']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso declara 300 g de proteína e o rodapé informa peso in natura. Nenhuma fonte informa quantas pessoas o prato serve: o rendimento não foi deduzido do peso.', 'Alimentar: Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('picanha-importada', 'Arroz extra', 1200, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'picanha-importada' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Filé de Peixe Grelhado (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'file-de-peixe-grelhado', 'para-dividir', null, 'Filé de Peixe Grelhado',
  'Filé de Peixe Grelhado', null,
  'Filé de pescada amarela grelhado, leve e cheio de sabor.',
  null,
  8000, 22,
  array['Arroz', 'Batata frita ou macaxeira', 'Salada', 'Farota', 'Molho artesanal']::text[],
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g de proteína", "principal": {"valor": 300, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não informa quantas pessoas o prato serve.", "fontes": ["PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO", "PEIXE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "peixe-grelhado-sir-fisher", "larguras": [440, 660], "alt": "Travessa com filé de peixe grelhado, arroz, batata frita e farofa", "estado": "conferido"}'::jsonb,
  array['peixe', 'pescada amarela', 'grelhado', 'leve', 'para dividir', 'compartilhar', 'arroz', 'farota']::text[],
  array['para-compartilhar']::text[],
  true,
  array['rendimento']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso declara 300 g de proteína e o rodapé informa peso in natura. Nenhuma fonte informa quantas pessoas o prato serve: o rendimento não foi deduzido do peso.', 'Alimentar: Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('file-de-peixe-grelhado', 'Arroz extra', 1200, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'file-de-peixe-grelhado' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Carne de Sol Acebolada (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'carne-de-sol-acebolada', 'para-dividir', null, 'Carne de Sol Acebolada',
  'Carne de Sol Acebolada', null,
  'Carne de sol de primeira, acompanhada de cebolas douradas.',
  null,
  8800, 23,
  array['Arroz', 'Batata frita ou macaxeira', 'Salada', 'Farota', 'Molho artesanal']::text[],
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g de proteína", "principal": {"valor": 300, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não informa quantas pessoas o prato serve.", "fontes": ["PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "carne-de-sol-sir-fisher", "larguras": [440, 660], "alt": "Travessa com carne de sol acebolada, arroz, batata frita e farofa", "estado": "conferido"}'::jsonb,
  array['carne de sol', 'acebolada', 'cebola', 'para dividir', 'compartilhar', 'arroz', 'farota']::text[],
  array['para-compartilhar']::text[],
  true,
  array['rendimento']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso declara 300 g de proteína e o rodapé informa peso in natura. Nenhuma fonte informa quantas pessoas o prato serve: o rendimento não foi deduzido do peso.', 'Alimentar: Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('carne-de-sol-acebolada', 'Arroz extra', 1200, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'carne-de-sol-acebolada' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Peito de Frango com Ervas (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'peito-de-frango-com-ervas', 'para-dividir', null, 'Peito de Frango com Ervas',
  'Peito de Frango com Ervas', null,
  'Peito de frango temperado com ervas finas e grelhado no charbroil.',
  null,
  6200, 24,
  array['Arroz', 'Batata frita ou macaxeira', 'Salada', 'Farota', 'Molho artesanal']::text[],
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g de proteína", "principal": {"valor": 300, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não informa quantas pessoas o prato serve.", "fontes": ["PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "peito-de-frango-sir-fisher", "larguras": [440, 660], "alt": "Travessa com peito de frango grelhado, arroz, batata frita e farofa", "estado": "conferido"}'::jsonb,
  array['frango', 'peito', 'ervas', 'grelhado', 'charbroil', 'para dividir', 'compartilhar', 'arroz', 'farota']::text[],
  array['para-compartilhar']::text[],
  true,
  array['rendimento']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso declara 300 g de proteína e o rodapé informa peso in natura. Nenhuma fonte informa quantas pessoas o prato serve: o rendimento não foi deduzido do peso.', 'Alimentar: Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('peito-de-frango-com-ervas', 'Arroz extra', 1200, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'peito-de-frango-com-ervas' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Picanha Suína (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'picanha-suina', 'para-dividir', null, 'Picanha Suína',
  'Picanha Suína', null,
  'Picanha suína grelhada no charbroil.',
  null,
  6700, 25,
  array['Arroz', 'Batata frita ou macaxeira', 'Salada', 'Farota', 'Molho artesanal']::text[],
  '[{"texto": "Batata frita ou macaxeira", "nota": "Troca sem custo declarado nas fontes. Confirmar com a equipe.", "estado": "a_confirmar"}]'::jsonb,
  '{"texto": "300 g de proteína", "principal": {"valor": 300, "unidade": "g", "alcance": "proteina"}, "total": null, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": "O cardápio impresso informa “peso in natura”. Alcance por prato ainda em conferência. O impresso não informa quantas pessoas o prato serve.", "fontes": ["PDF"]}'::jsonb,
  '{"declarados": ["GLÚTEN", "OVO"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  '{"base": "picanha-suina-sir-fisher", "larguras": [440, 660], "alt": "Travessa com picanha suína grelhada, arroz, batata frita e farofa", "estado": "conferido"}'::jsonb,
  array['picanha suina', 'porco', 'suina', 'grelhada', 'charbroil', 'para dividir', 'compartilhar', 'arroz', 'farota']::text[],
  array['para-compartilhar']::text[],
  true,
  array['rendimento']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso declara 300 g de proteína e o rodapé informa peso in natura. Nenhuma fonte informa quantas pessoas o prato serve: o rendimento não foi deduzido do peso.', 'Alimentar: Os símbolos estão no prato completo. O impresso não diz se vêm da proteína, do molho ou de um acompanhamento.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
-- Adicional, nunca preco do produto.
insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('picanha-suina', 'Arroz extra', 1200, 0)
) as a(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'picanha-suina' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Brownie de Chocolate (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'brownie-de-chocolate', 'sobremesas', null, 'Brownie de Chocolate',
  'Brownie de Chocolate', null,
  'Brownie macio, feito com chocolate de alta qualidade.',
  null,
  1000, 26,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['brownie', 'chocolate', 'doce', 'sobremesa']::text[],
  '{}',
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Brownie com Sorvete (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'brownie-com-sorvete', 'sobremesas', null, 'Brownie com Sorvete',
  'Brownie com Sorvete', null,
  'Brownie de chocolate com sorvete de creme e calda de chocolate.',
  null,
  1800, 27,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['brownie', 'sorvete', 'chocolate', 'doce', 'sobremesa']::text[],
  '{}',
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Café Expresso (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'cafe-expresso', 'sobremesas', null, 'Café Expresso',
  'Café Expresso', null,
  null,
  null,
  500, 28,
  '{}',
  '[]'::jsonb,
  '{"texto": "50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["TXT", "HTML"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['cafe', 'expresso', 'cafezinho']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso lista o café entre as sobremesas e não informa volume. Os 50 mL vêm do cadastro.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Chope Brahma (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'chope-brahma', 'cervejas', null, 'Chope Brahma',
  'Chope Brahma', 'chope',
  null,
  null,
  1090, 29,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['chope brahma', 'cerveja', 'chope']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Spaten Longneck (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'spaten-longneck', 'cervejas', null, 'Spaten Longneck',
  'Spaten Longneck', 'long neck',
  null,
  null,
  1190, 30,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "divergente", "divergencia": "Volume divergente — HTML: 355 mL. Cardápio impresso: 300 mL.", "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['spaten longneck', 'cerveja', 'long neck']::text[],
  array['bebida']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Porção: Volume divergente — HTML: 355 mL. Cardápio impresso: 300 mL.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Stella Artois Longneck (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'stella-artois-longneck', 'cervejas', null, 'Stella Artois Longneck',
  'Stella Artois Longneck', 'long neck',
  null,
  null,
  1290, 31,
  '{}',
  '[]'::jsonb,
  '{"texto": "330 mL", "principal": null, "total": {"valor": 330, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['stella artois longneck', 'cerveja', 'long neck']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Corona Longneck (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'corona-longneck', 'cervejas', null, 'Corona Longneck',
  'Corona Longneck', 'long neck',
  null,
  null,
  1490, 32,
  '{}',
  '[]'::jsonb,
  '{"texto": "330 mL", "principal": null, "total": {"valor": 330, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['corona longneck', 'cerveja', 'long neck']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Corona Zero Longneck (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'corona-zero-longneck', 'cervejas', null, 'Corona Zero Longneck',
  'Corona Zero Longneck', 'long neck',
  null,
  null,
  1490, 33,
  '{}',
  '[]'::jsonb,
  '{"texto": "330 mL", "principal": null, "total": {"valor": 330, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['corona zero longneck', 'cerveja', 'long neck']::text[],
  array['bebida']::text[],
  true,
  array['classificacao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso escreve “CORONA ZERO% LONGNECK”. A classificação como bebida sem álcool depende de conferência do produto e não foi aplicada como etiqueta.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Spaten 600 (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'spaten-600', 'cervejas', null, 'Spaten 600',
  'Spaten 600', 'garrafa',
  null,
  null,
  1940, 34,
  '{}',
  '[]'::jsonb,
  '{"texto": "600 mL", "principal": null, "total": {"valor": 600, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['spaten 600', 'cerveja', 'garrafa']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Original 600 (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'original-600', 'cervejas', null, 'Original 600',
  'Original 600', 'garrafa',
  null,
  null,
  1940, 35,
  '{}',
  '[]'::jsonb,
  '{"texto": "600 mL", "principal": null, "total": {"valor": 600, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['original 600', 'cerveja', 'garrafa']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Budweiser 600 (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'budweiser-600', 'cervejas', null, 'Budweiser 600',
  'Budweiser 600', 'garrafa',
  null,
  null,
  1840, 36,
  '{}',
  '[]'::jsonb,
  '{"texto": "600 mL", "principal": null, "total": {"valor": 600, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['budweiser 600', 'cerveja', 'garrafa']::text[],
  array['bebida']::text[],
  true,
  array['vigencia']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Consta no TXT e no HTML, mas não foi encontrado no cardápio impresso. Ausência em uma fonte não retira o produto do cadastro.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Stella Artois 600 (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'stella-artois-600', 'cervejas', null, 'Stella Artois 600',
  'Stella Artois 600', 'garrafa',
  null,
  null,
  2140, 37,
  '{}',
  '[]'::jsonb,
  '{"texto": "600 mL", "principal": null, "total": {"valor": 600, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['stella artois 600', 'cerveja', 'garrafa']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Stella Pure Gold 600 (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'stella-pure-gold-600', 'cervejas', null, 'Stella Pure Gold 600',
  'Stella Pure Gold 600', 'garrafa',
  null,
  null,
  2390, 38,
  '{}',
  '[]'::jsonb,
  '{"texto": "600 mL", "principal": null, "total": {"valor": 600, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [{"texto": "PURO MALTE, SEM GLÚTEN E COM 17% MENOS CALORIAS", "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "a_conferir", "nota": "Alegação do impresso sobre esta cerveja. Não publicada como informação alimentar: exige conferência com embalagem e fabricante. Não vale para as demais cervejas."}], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['stella pure gold 600', 'cerveja', 'garrafa']::text[],
  array['bebida']::text[],
  true,
  array['alegacao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Alegação do impresso, não publicada: “PURO MALTE, SEM GLÚTEN E COM 17% MENOS CALORIAS” — Alegação do impresso sobre esta cerveja. Não publicada como informação alimentar: exige conferência com embalagem e fabricante. Não vale para as demais cervejas.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Caipirinha (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'caipirinha', 'coqueteis', null, 'Caipirinha',
  'Caipirinha', 'limão, açúcar e cachaça',
  null,
  'Clássica combinação de limão, açúcar e cachaça, refrescante e cheia de sabor. Escolha a cachaça.',
  1800, 39,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['caipirinha', 'cachaca', 'limao', 'ypioca', 'drink', 'coquetel']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O preço do TXT (R$ 18,00) corresponde à variante nacional.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
delete from public.cardapio_variante where produto_id = 'caipirinha'
  and exists (select 1 from public.cardapio_produto p
               where p.id = 'caipirinha' and 'carga-inicial' = any(p.fontes));
insert into public.cardapio_variante (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('caipirinha', 'Cachaça nacional', 1800, 0),
  ('caipirinha', 'Ypioca 150', 2200, 1)
) as v(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'caipirinha' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Caipiroska (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'caipiroska', 'coqueteis', null, 'Caipiroska',
  'Caipiroska', 'limão, açúcar e vodka',
  null,
  'Releitura da caipirinha, com limão, açúcar e vodka. Escolha a vodka.',
  2000, 40,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['caipiroska', 'vodka', 'limao', 'absolut', 'sky', 'drink', 'coquetel']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
delete from public.cardapio_variante where produto_id = 'caipiroska'
  and exists (select 1 from public.cardapio_produto p
               where p.id = 'caipiroska' and 'carga-inicial' = any(p.fontes));
insert into public.cardapio_variante (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('caipiroska', 'Vodka nacional', 2000, 0),
  ('caipiroska', 'Sky', 2200, 1),
  ('caipiroska', 'Absolut', 2800, 2)
) as v(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'caipiroska' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Caipifruta (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'caipifruta', 'coqueteis', null, 'Caipifruta',
  'Caipifruta', 'vodka, açúcar e polpa de fruta',
  null,
  'Vodka, açúcar e o sabor de fruta da sua escolha. Escolha a vodka e a fruta.',
  2200, 41,
  '{}',
  '[{"texto": "Abacaxi, acerola, caju, cajá, maracujá, morango ou manga (polpa)", "estado": "declarado"}]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['caipifruta', 'vodka', 'fruta', 'polpa', 'abacaxi', 'acerola', 'caju', 'caja', 'maracuja', 'morango', 'manga', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
delete from public.cardapio_variante where produto_id = 'caipifruta'
  and exists (select 1 from public.cardapio_produto p
               where p.id = 'caipifruta' and 'carga-inicial' = any(p.fontes));
insert into public.cardapio_variante (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('caipifruta', 'Vodka nacional', 2200, 0),
  ('caipifruta', 'Sky', 2400, 1),
  ('caipifruta', 'Absolut', 3000, 2)
) as v(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'caipifruta' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Gin Tônica (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'gin-tonica', 'coqueteis', null, 'Gin Tônica',
  'Gin Tônica', 'gin, água tônica e toque cítrico',
  null,
  'O clássico refrescante: gin, água tônica e um toque cítrico para equilibrar. Escolha o gin.',
  2100, 42,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['gin', 'tonica', 'gordons', 'drink', 'coquetel', 'citrico']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);
delete from public.cardapio_variante where produto_id = 'gin-tonica'
  and exists (select 1 from public.cardapio_produto p
               where p.id = 'gin-tonica' and 'carga-inicial' = any(p.fontes));
insert into public.cardapio_variante (produto_id, nome, preco_centavos, ordem)
select * from (values
  ('gin-tonica', 'Gin nacional', 2100, 0),
  ('gin-tonica', 'Gordon''s', 2300, 1)
) as v(produto_id, nome, preco_centavos, ordem)
where exists (select 1 from public.cardapio_produto p
              where p.id = 'gin-tonica' and 'carga-inicial' = any(p.fontes))
on conflict (produto_id, nome) do update set
  preco_centavos = excluded.preco_centavos, ordem = excluded.ordem;

-- Melancita (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'melancita', 'coqueteis', null, 'Melancita',
  'Melancita', 'gin, energético de melancia e limão siciliano',
  null,
  'Gin harmonizado com Red Bull melancia e finalizado com fatias de limão siciliano.',
  2700, 43,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['melancia', 'gin', 'red bull', 'energetico', 'limao siciliano', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Sherlock Holmes Gin (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'sherlock-holmes-gin', 'coqueteis', null, 'Sherlock Holmes Gin',
  'Sherlock Holmes Gin', 'gin com energético e gengibre',
  null,
  'Gin com energético e um toque sutil de gengibre. A marca do energético está em conferência com o bar.',
  2900, 44,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['sherlock', 'gin', 'gengibre', 'energetico', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  array['descricao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Receita divergente: o HTML cita Monster; o impresso cita Red Bull Zero e xarope de gengibre. A marca do energético não foi publicada até a confirmação da ficha.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Tropicall (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'tropicall', 'coqueteis', null, 'Tropicall',
  'Tropicall', 'vodka, energético tropical e limão siciliano',
  null,
  'Vodka com Red Bull Tropical e um toque cítrico de limão siciliano.',
  2700, 45,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['tropicall', 'vodka', 'red bull', 'tropical', 'limao siciliano', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Margarita (TXT, HTML)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'margarita', 'coqueteis', null, 'Margarita',
  'Margarita', 'tequila, triple sec e limão',
  null,
  'Tequila, triple sec e o toque cítrico marcante do limão.',
  2900, 46,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": "Nenhuma fonte informa o volume deste coquetel.", "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['margarita', 'tequila', 'triple sec', 'limao', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  array['porcao', 'vigencia']::text[],
  array['TXT', 'HTML', 'carga-inicial']::text[],
  array['Consta no TXT e no HTML, mas não foi encontrado no cardápio impresso. Ausência em uma fonte não retira o produto.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Fitzgerald (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'fitzgerald', 'coqueteis', null, 'Fitzgerald',
  'Fitzgerald', 'gin, limão, açúcar e bitter artesanal',
  null,
  'Gin, suco de limão, açúcar e um toque sutil de bitter artesanal.',
  2300, 47,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['fitzgerald', 'gin', 'limao', 'bitter', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Moscow Mule (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'moscow-mule', 'coqueteis', null, 'Moscow Mule',
  'Moscow mule', 'vodka, gengibre e limão',
  null,
  'Vodka, suco de limão e espuma de gengibre.',
  2600, 48,
  '{}',
  '[]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['moscow mule', 'vodka', 'gengibre', 'limao', 'drink']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  array['descricao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso acrescenta refrigerante de limão à composição. Ficha a confirmar antes de alterar a descrição.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Smirnoff Ice (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'smirnoff-ice', 'coqueteis', null, 'Smirnoff Ice',
  'Smirnoff Ice', null,
  null,
  null,
  1500, 49,
  '{}',
  '[]'::jsonb,
  '{"texto": "275 mL", "principal": null, "total": {"valor": 275, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['smirnoff', 'ice', 'vodka', 'long neck']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Bebida pronta listada entre os coquetéis nas fontes. Mantida na mesma categoria do cadastro.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Água sem gás (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'agua-sem-gas', 'sem-alcool', null, 'Água sem gás',
  'Água sem gás', null,
  null,
  null,
  500, 50,
  '{}',
  '[]'::jsonb,
  '{"texto": "500 mL", "principal": null, "total": {"valor": 500, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['agua', 'sem gas']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Água com gás (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'agua-com-gas', 'sem-alcool', null, 'Água com gás',
  'Água com gás', null,
  null,
  null,
  600, 51,
  '{}',
  '[]'::jsonb,
  '{"texto": "500 mL", "principal": null, "total": {"valor": 500, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['agua', 'com gas', 'gaseificada']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Água de Coco (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'agua-de-coco-copo', 'sem-alcool', null, 'Água de Coco',
  'Água de Coco copo', null,
  null,
  null,
  500, 52,
  '{}',
  '[]'::jsonb,
  '{"texto": "Copo 300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['agua de coco', 'coco', 'natural']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Água Tônica (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'agua-tonica', 'sem-alcool', null, 'Água Tônica',
  'Água Tônica', null,
  null,
  null,
  600, 53,
  '{}',
  '[]'::jsonb,
  '{"texto": "350 mL", "principal": null, "total": {"valor": 350, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['agua tonica', 'tonica']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Refrigerante lata (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'refrigerante-lata', 'sem-alcool', null, 'Refrigerante lata',
  'Refrigerante lata', 'sabor a escolher',
  null,
  null,
  800, 54,
  '{}',
  '[{"texto": "Guaraná, Guaraná Zero, Pepsi, Pepsi Black, laranja, uva ou soda", "estado": "declarado"}]'::jsonb,
  '{"texto": "350 mL", "principal": null, "total": {"valor": 350, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['refrigerante', 'refri', 'lata', 'guarana', 'pepsi', 'laranja', 'uva', 'soda', 'zero']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Suco Copo (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'suco-copo', 'sem-alcool', null, 'Suco Copo',
  'Suco Copo', 'feito com polpa, sabor a escolher',
  null,
  null,
  1100, 55,
  '{}',
  '[{"texto": "Acerola, abacaxi, cajá, caju, limão, maracujá, morango ou manga (polpa)", "estado": "declarado"}]'::jsonb,
  '{"texto": "330 mL", "principal": null, "total": {"valor": 330, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['suco', 'polpa', 'acerola', 'abacaxi', 'caja', 'caju', 'limao', 'maracuja', 'morango', 'manga', 'natural']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Energético Red Bull (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'energetico-red-bull', 'sem-alcool', null, 'Energético Red Bull',
  'Energético Red Bull', null,
  null,
  null,
  1600, 56,
  '{}',
  '[]'::jsonb,
  '{"texto": "269 mL", "principal": null, "total": {"valor": 269, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['red bull', 'energetico']::text[],
  array['bebida']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Soda Italiana (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'soda-italiana', 'sem-alcool', null, 'Soda Italiana',
  'Soda Italiana (sem alcool)', 'sem álcool, sabor a escolher',
  null,
  null,
  1500, 57,
  '{}',
  '[{"texto": "Maçã verde, tangerina, gengibre, granadine ou cranberry", "estado": "declarado"}]'::jsonb,
  '{"texto": "300 mL", "principal": null, "total": {"valor": 300, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['soda italiana', 'sem alcool', 'maca verde', 'tangerina', 'gengibre', 'granadine', 'cranberry']::text[],
  array['bebida', 'sem-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso marca explicitamente este item como SEM ÁLCOOL.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Sumo de Limão (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'sumo-de-limao', 'sem-alcool', null, 'Sumo de Limão',
  'Sumo de Limão', '50 mL',
  null,
  null,
  300, 58,
  '{}',
  '[]'::jsonb,
  '{"texto": "50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['sumo de limao', 'limao', 'suco de limao']::text[],
  array['bebida']::text[],
  true,
  array['classificacao']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso lista o item na seção BEBIDAS, com 50 mL. Se na operação ele funciona como complemento de drink, e não como bebida servida, deve ser movido para Extras. Pendente de confirmação.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Teacher's (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'teachers', 'doses', null, 'Teacher''s',
  'Teacher''s', null,
  null,
  null,
  800, 59,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['whisky', 'teachers', 'escoces', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Black & White (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'black-white', 'doses', null, 'Black & White',
  'Black & White', null,
  null,
  null,
  800, 60,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['whisky', 'black white', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Red Label (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'red-label', 'doses', null, 'Red Label',
  'Red Label', null,
  null,
  null,
  1200, 61,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['whisky', 'red label', 'johnnie walker', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Black Label (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'black-label', 'doses', null, 'Black Label',
  'Black Label', null,
  null,
  null,
  1700, 62,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['whisky', 'black label', 'johnnie walker', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Rum (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'rum', 'doses', null, 'Rum',
  'Rum', null,
  null,
  null,
  800, 63,
  '{}',
  '[{"texto": "Bacardi ou Montila", "estado": "declarado"}]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['rum', 'bacardi', 'montila', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Campari (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'campari', 'doses', null, 'Campari',
  'Campari', null,
  null,
  null,
  800, 64,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['campari', 'aperitivo', 'bitter', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Martini (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'martini', 'doses', null, 'Martini',
  'Martini', null,
  null,
  null,
  700, 65,
  '{}',
  '[{"texto": "Bianco ou Rosato", "estado": "declarado"}]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['martini', 'bianco', 'rosato', 'vermute', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Vodka Nacional (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'vodka-nacional', 'doses', null, 'Vodka Nacional',
  'Vodka Nacional', null,
  null,
  null,
  700, 66,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['vodka', 'nacional', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Vodka Sky (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'vodka-sky', 'doses', null, 'Vodka Sky',
  'Vodka Sky', null,
  null,
  null,
  900, 67,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['vodka', 'sky', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Vodka Absolut (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'vodka-absolut', 'doses', null, 'Vodka Absolut',
  'Vodka Absolut', null,
  null,
  null,
  1500, 68,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['vodka', 'absolut', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Gin Nacional (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'gin-nacional', 'doses', null, 'Gin Nacional',
  'Gin Nacional', null,
  null,
  null,
  1000, 69,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['gin', 'nacional', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Gin Gordon's (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'gin-gordons', 'doses', null, 'Gin Gordon''s',
  'Gin Gordon''s', null,
  null,
  null,
  1200, 70,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['gin', 'gordons', 'britanico', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Aperol (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'aperol', 'doses', null, 'Aperol',
  'Aperol', null,
  null,
  null,
  800, 71,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['aperol', 'aperitivo', 'spritz', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Conhaque (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'conhaque', 'doses', null, 'Conhaque',
  'Conhaque', null,
  null,
  null,
  700, 72,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['conhaque', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Cachaça Nacional (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'cachaca-nacional', 'doses', null, 'Cachaça Nacional',
  'Cachaça Nacional', null,
  null,
  null,
  600, 73,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['cachaca', 'nacional', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Cachaça Ypioca 150 (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'cachaca-ypioca-150', 'doses', null, 'Cachaça Ypioca 150',
  'Cachaça Ypioca 150', null,
  null,
  null,
  1000, 74,
  '{}',
  '[]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['cachaca', 'ypioca', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O “150” faz parte do nome comercial da cachaça. Não é a medida da dose, que é de 50 mL como nas demais.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Cachaça Premium (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'cachaca-premium', 'doses', null, 'Cachaça Premium',
  'Cachaça Premium', null,
  null,
  null,
  1200, 75,
  '{}',
  '[{"texto": "Batista (3 anos em barril de carvalho, MG), Gogó da Ema (2 anos em barril de bálsamo, AL), Matriarca (2 anos em barril de umburana, BA) ou Caipira 5 Estrelas (1 ano em barril de cerejeira, ES)", "estado": "declarado"}]'::jsonb,
  '{"texto": "Dose de 50 mL", "principal": null, "total": {"valor": 50, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["HTML", "PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['cachaca', 'premium', 'batista', 'gogo da ema', 'matriarca', 'caipira 5 estrelas', 'envelhecida', 'dose', 'destilado']::text[],
  array['bebida', 'com-alcool']::text[],
  true,
  array['opcoes']::text[],
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['Quatro rótulos sob um mesmo preço, conforme o cadastro. Disponibilidade por rótulo a confirmar com o bar.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Molho Extra (TXT, HTML)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'molho-extra', 'extras', 'comestiveis', 'Molho Extra',
  'Molho Extra', 'porção adicional de molho',
  null,
  null,
  300, 76,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": null, "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['molho', 'extra', 'adicional']::text[],
  array['adicional']::text[],
  true,
  array['alimentar']::text[],
  array['TXT', 'HTML', 'carga-inicial']::text[],
  array['Nenhuma fonte informa qual molho, nem a quantidade.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Arroz Extra (TXT, HTML, PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'arroz-extra', 'extras', 'comestiveis', 'Arroz Extra',
  'Arroz Extra', 'porção adicional de arroz',
  null,
  null,
  1200, 77,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": null, "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['arroz', 'extra', 'adicional']::text[],
  array['adicional']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'PDF', 'carga-inicial']::text[],
  array['O impresso traz o mesmo item como “ADICIONAL ARROZ R$ 12,00”, na página dos pratos. Mesmo registro, não duplicado.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Rolha (TXT, HTML)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'rolha', 'extras', 'cobrancas', 'Rolha',
  'Rolha', 'taxa para consumir bebida trazida pelo cliente',
  null,
  null,
  3000, 78,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": null, "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['rolha', 'taxa', 'servico']::text[],
  array['servico']::text[],
  true,
  array['regra']::text[],
  array['TXT', 'HTML', 'carga-inicial']::text[],
  array['Cobrança de serviço, não é produto. Regras de aplicação (por garrafa, por mesa) não constam nas fontes.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Pacote de Gelo (TXT, HTML)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'pacote-gelo', 'extras', 'apoio', 'Pacote de Gelo',
  'Pacote Gelo', 'pacote de gelo',
  null,
  null,
  2000, 79,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": null, "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['gelo', 'pacote']::text[],
  array['servico']::text[],
  true,
  array['porcao']::text[],
  array['TXT', 'HTML', 'carga-inicial']::text[],
  array['Nenhuma fonte informa o peso do pacote.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Embalagem para Viagem (TXT, HTML)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'embalagem-viagem', 'extras', 'apoio', 'Embalagem para Viagem',
  'Embalagem Viagem', 'embalagem para levar',
  null,
  null,
  300, 80,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": null, "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['embalagem', 'viagem', 'levar', 'marmita', 'delivery']::text[],
  array['servico']::text[],
  true,
  '{}',
  array['TXT', 'HTML', 'carga-inicial']::text[],
  '{}'
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Adicional Salada (PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'adicional-salada', 'extras', 'comestiveis', 'Adicional Salada',
  'Adicional Salada', 'porção adicional de salada',
  null,
  null,
  1900, 81,
  '{}',
  '[]'::jsonb,
  '{"texto": null, "principal": null, "total": null, "unidades": null, "rende_pessoas": null, "estado": "ausente", "divergencia": null, "nota": null, "fontes": []}'::jsonb,
  '{"declarados": [], "fonte": null, "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['salada', 'adicional', 'extra']::text[],
  array['adicional']::text[],
  false,
  array['vigencia', 'preco']::text[],
  array['PDF', 'carga-inicial']::text[],
  array['Aparece apenas no cardápio impresso (R$ 19,00, página 1). Não está entre os 81 registros do cadastro. Fica em rascunho até a operação confirmar existência e preço vigente.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- Corona 600 (PDF)
insert into public.cardapio_produto (
  id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
  detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
  termos, etiquetas, publicar, pendencias, fontes, notas_internas
) values (
  'corona-600', 'cervejas', null, 'Corona 600',
  'Corona 600', 'garrafa',
  null,
  null,
  null, 82,
  '{}',
  '[]'::jsonb,
  '{"texto": "600 mL", "principal": null, "total": {"valor": 600, "unidade": "mL"}, "unidades": null, "rende_pessoas": null, "estado": "declarado", "divergencia": null, "nota": null, "fontes": ["PDF"]}'::jsonb,
  '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb,
  null,
  array['corona', 'cerveja', 'garrafa']::text[],
  array['bebida']::text[],
  false,
  array['vigencia', 'preco']::text[],
  array['PDF', 'carga-inicial']::text[],
  array['Aparece no grupo de garrafas 600 mL do impresso, mas não consta no cadastro, que tem Budweiser 600 nessa faixa. Preço não importado do impresso. Fica em rascunho para decisão da operação.']::text[]
)
on conflict (id) do update set
  categoria_id = excluded.categoria_id,
  subgrupo = excluded.subgrupo,
  nome = excluded.nome,
  nome_original = excluded.nome_original,
  descritor = excluded.descritor,
  descricao = excluded.descricao,
  detalhe = excluded.detalhe,
  preco_centavos = excluded.preco_centavos,
  ordem = excluded.ordem,
  inclui = excluded.inclui,
  opcoes = excluded.opcoes,
  porcao = excluded.porcao,
  alimentar = excluded.alimentar,
  foto = excluded.foto,
  termos = excluded.termos,
  etiquetas = excluded.etiquetas,
  publicar = excluded.publicar,
  pendencias = excluded.pendencias,
  fontes = excluded.fontes,
  notas_internas = excluded.notas_internas,
  atualizado_em = now()
where 'carga-inicial' = any(public.cardapio_produto.fontes);

-- O catalogo nasce em conferencia. O portal avisa o cliente enquanto
-- precos, porcoes e informacao alimentar nao forem confirmados pela casa.
update public.cardapio_estado set valor = 'em_conferencia' where id;

commit;
