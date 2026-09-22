-- Rotina "Cardapio": catalogo unico do cardapio do Sir Fisher, editado no
-- painel e lido pelo portal publico em sirfisher.com.br/cardapio/.
--
-- O problema que a estrutura resolve
-- ----------------------------------
-- Hoje o cardapio existe em tres lugares que discordam entre si (um TXT, um
-- HTML e o Hubt). A partir daqui existe um so: estas tabelas. O portal publico
-- nao le as tabelas de edicao -- le uma PUBLICACAO, que e uma fotografia
-- imutavel do catalogo no momento em que alguem apertou "publicar".
--
-- Rascunho x publicado
--   cardapio_produto ........ o que a operacao esta editando agora (rascunho).
--   cardapio_publicacao ..... fotografias publicadas, uma linha por versao,
--                             nunca alteradas depois de criadas.
--   cardapio_publico ........ a unica view que o visitante anonimo enxerga.
--
-- Disponibilidade fica FORA da fotografia
--   "Acabou a picanha" precisa valer agora, sem refazer o catalogo, e nao pode
--   ser desfeito por alguem restaurando uma versao editorial antiga. Por isso
--   cardapio_publico le `disponivel` ao vivo da tabela de rascunho e sobrepoe
--   o valor que estava congelado na publicacao. Restaurar a versao 3 traz os
--   textos da versao 3 e mantem esgotado o que esta esgotado hoje.
--
-- Seguranca
--   As tabelas ficam com RLS ligado e sem grant nenhum para anon/authenticated.
--   A pagina do painel le pelas views app_cardapio_* (mesmo portao das demais
--   rotinas) e escreve pelas RPCs security definer. O visitante so alcanca
--   cardapio_publico, que por construcao devolve unicamente o conteudo da
--   publicacao ativa: rascunho, nota interna, pendencia, fonte, custo e
--   usuario nao passam por ali. Nenhuma view toca auth.users; o nome de quem
--   editou sai de private.nome_exibicao_usuario(uuid).

begin;

-- ---------------------------------------------------------------------------
-- Categorias
-- ---------------------------------------------------------------------------

create table if not exists public.cardapio_categoria (
  id text primary key check (id ~ '^[a-z0-9-]{2,40}$'),
  nome text not null check (length(btrim(nome)) between 2 and 60),
  resumo text,
  -- Agrupamento de leitura do portal. Decide a apresentacao: "comer" usa
  -- cartao com foto, "beber" usa linha comparavel, "extras" usa lista
  -- explicada.
  grupo text not null default 'comer' check (grupo in ('comer', 'beber', 'extras')),
  subgrupos jsonb not null default '[]'::jsonb,
  ordem integer not null default 0,
  ativo boolean not null default true,
  atualizado_por uuid references auth.users(id) on delete set null,
  atualizado_em timestamptz not null default now()
);

comment on table public.cardapio_categoria is
  'Categorias do cardapio. O nome precisa ser compreensivel antes de abrir os itens.';
comment on column public.cardapio_categoria.subgrupos is
  'Lista [{id, nome}] de subgrupos opcionais dentro da categoria.';

-- ---------------------------------------------------------------------------
-- Produtos
-- ---------------------------------------------------------------------------

create table if not exists public.cardapio_produto (
  id text primary key check (id ~ '^[a-z0-9-]{2,60}$'),
  categoria_id text not null references public.cardapio_categoria(id),
  subgrupo text,
  nome text not null check (length(btrim(nome)) between 2 and 90),
  -- Nome como esta na fonte de origem. Nunca sobrescrito pela edicao: e o que
  -- permite rastrear de onde veio o registro quando as fontes divergem.
  nome_original text,
  -- Frase curta que torna legivel um nome comercial ou em ingles
  -- ("NewCastle - camaroes empanados com batatas").
  descritor text,
  descricao text,
  detalhe text,
  preco_centavos integer check (preco_centavos is null or preco_centavos >= 0),
  ordem integer not null default 0,

  inclui text[] not null default '{}',
  opcoes jsonb not null default '[]'::jsonb,
  porcao jsonb not null default '{}'::jsonb,
  alimentar jsonb not null default '{}'::jsonb,
  foto jsonb,
  termos text[] not null default '{}',
  etiquetas text[] not null default '{}',

  -- Campos de governanca. Nada disso chega ao portal publico.
  publicar boolean not null default true,
  pendencias text[] not null default '{}',
  fontes text[] not null default '{}',
  notas_internas text[] not null default '{}',

  -- Disponibilidade e um estado operacional, nao editorial. Vive aqui e e
  -- lida ao vivo pelo portal, por cima da publicacao.
  disponivel boolean not null default true,
  indisponivel_motivo text,
  disponibilidade_em timestamptz,

  criado_por uuid references auth.users(id) on delete set null,
  criado_em timestamptz not null default now(),
  atualizado_por uuid references auth.users(id) on delete set null,
  atualizado_em timestamptz not null default now(),
  arquivado boolean not null default false
);

comment on table public.cardapio_produto is
  'Rascunho do catalogo. O portal publico nunca le esta tabela: le a publicacao ativa.';
comment on column public.cardapio_produto.porcao is
  'Medidas separadas: {texto, principal{valor,unidade,alcance}, total, unidades, rende_pessoas, estado, divergencia, nota}. rende_pessoas so e preenchido se a cozinha confirmar -- peso nunca vira numero de pessoas.';
comment on column public.cardapio_produto.alimentar is
  'Declaracoes em camadas: {declarados[] (simbolos do impresso), estado, divergencias[], alegacoes[], confirmado_cozinha[], contato_cruzado[]}. Lista vazia significa NAO REVISADO, nunca ausencia de alergeno.';
comment on column public.cardapio_produto.disponivel is
  'Estado operacional do dia. Fica fora da publicacao de proposito: restaurar uma versao antiga nao reativa um item esgotado.';

create index if not exists cardapio_produto_categoria_idx
  on public.cardapio_produto (categoria_id, ordem);
create index if not exists cardapio_produto_pendencia_idx
  on public.cardapio_produto (categoria_id)
  where cardinality(pendencias) > 0;

create table if not exists public.cardapio_variante (
  id bigint generated always as identity primary key,
  produto_id text not null references public.cardapio_produto(id) on delete cascade,
  nome text not null check (length(btrim(nome)) between 1 and 60),
  preco_centavos integer not null check (preco_centavos >= 0),
  ordem integer not null default 0,
  unique (produto_id, nome)
);

comment on table public.cardapio_variante is
  'Jeitos diferentes de pedir o MESMO produto, com precos proprios (Caipirinha nacional x Ypioca). Na listagem viram faixa de preco.';

create table if not exists public.cardapio_adicional (
  id bigint generated always as identity primary key,
  produto_id text not null references public.cardapio_produto(id) on delete cascade,
  nome text not null check (length(btrim(nome)) between 1 and 60),
  preco_centavos integer not null check (preco_centavos >= 0),
  ordem integer not null default 0,
  unique (produto_id, nome)
);

comment on table public.cardapio_adicional is
  'Acrescimo cobrado a parte. NUNCA e preco do produto: o HTML antigo listava a batata de R$ 9,90 como primeira oferta dos sanduiches de R$ 37,00, e um importador ingenuo anunciaria o sanduiche por R$ 9,90.';

create table if not exists public.cardapio_sinonimo (
  termo text primary key,
  alternativas text[] not null default '{}',
  atualizado_em timestamptz not null default now()
);

comment on table public.cardapio_sinonimo is
  'Variantes de grafia e de regiao para a busca (macaxeira/mandioca/aipim). Sao fatos de lingua, cadastrados -- nao sinonimos inventados sobre receitas.';

create table if not exists public.cardapio_aviso (
  id text primary key,
  titulo text not null,
  texto text not null,
  fonte text,
  citacao text,
  estado text not null default 'declarado_no_impresso',
  ordem integer not null default 0,
  publicar boolean not null default true
);

comment on table public.cardapio_aviso is
  'Avisos gerais do cardapio (alergenos, por exemplo). Ficam separados da matriz por prato: o aviso geral do impresso nao vira presenca confirmada de cada item.';

-- ---------------------------------------------------------------------------
-- Publicacoes
-- ---------------------------------------------------------------------------

create sequence if not exists public.cardapio_versao_seq as integer start 1;

create table if not exists public.cardapio_publicacao (
  id bigint generated always as identity primary key,
  versao integer not null unique,
  conteudo jsonb not null,
  resumo jsonb not null default '{}'::jsonb,
  observacao text,
  origem_versao integer,
  publicado_por uuid references auth.users(id) on delete set null,
  publicado_em timestamptz not null default now(),
  ativo boolean not null default false
);

comment on table public.cardapio_publicacao is
  'Fotografias publicadas do catalogo. Linha publicada nunca e alterada: restaurar uma versao antiga cria uma versao NOVA com aquele conteudo, preservando o historico.';
comment on column public.cardapio_publicacao.origem_versao is
  'Preenchido quando a publicacao veio de uma restauracao, apontando a versao restaurada.';

-- Uma publicacao ativa por vez. Indice parcial em vez de trigger: o banco
-- recusa a segunda linha ativa, e nao ha janela de corrida.
create unique index if not exists cardapio_publicacao_ativa_idx
  on public.cardapio_publicacao ((ativo)) where ativo;

create table if not exists public.cardapio_disponibilidade_log (
  id bigint generated always as identity primary key,
  produto_id text not null references public.cardapio_produto(id) on delete cascade,
  disponivel boolean not null,
  motivo text,
  usuario_id uuid references auth.users(id) on delete set null,
  criado_em timestamptz not null default now()
);

create index if not exists cardapio_disponibilidade_log_idx
  on public.cardapio_disponibilidade_log (produto_id, criado_em desc);

comment on table public.cardapio_disponibilidade_log is
  'Quem marcou o que como esgotado e quando. Registro obrigatorio: disponibilidade muda rapido e precisa ser auditavel.';

alter table public.cardapio_categoria enable row level security;
alter table public.cardapio_produto enable row level security;
alter table public.cardapio_variante enable row level security;
alter table public.cardapio_adicional enable row level security;
alter table public.cardapio_sinonimo enable row level security;
alter table public.cardapio_aviso enable row level security;
alter table public.cardapio_publicacao enable row level security;
alter table public.cardapio_disponibilidade_log enable row level security;

revoke all privileges on public.cardapio_categoria from public, anon, authenticated;
revoke all privileges on public.cardapio_produto from public, anon, authenticated;
revoke all privileges on public.cardapio_variante from public, anon, authenticated;
revoke all privileges on public.cardapio_adicional from public, anon, authenticated;
revoke all privileges on public.cardapio_sinonimo from public, anon, authenticated;
revoke all privileges on public.cardapio_aviso from public, anon, authenticated;
revoke all privileges on public.cardapio_publicacao from public, anon, authenticated;
revoke all privileges on public.cardapio_disponibilidade_log from public, anon, authenticated;

-- ---------------------------------------------------------------------------
-- Montagem da publicacao
-- ---------------------------------------------------------------------------

-- Estado global do catalogo: enquanto a operacao nao conferir precos, porcoes
-- e informacao alimentar, o portal avisa o cliente. Uma linha so.
create table if not exists public.cardapio_estado (
  id boolean primary key default true check (id),
  valor text not null default 'em_conferencia'
    check (valor in ('em_conferencia', 'vigente')),
  atualizado_por uuid references auth.users(id) on delete set null,
  atualizado_em timestamptz not null default now()
);
alter table public.cardapio_estado enable row level security;
revoke all privileges on public.cardapio_estado from public, anon, authenticated;
insert into public.cardapio_estado (id, valor) values (true, 'em_conferencia')
  on conflict (id) do nothing;

-- Indice de busca: so entra o que esta cadastrado (nome, descritor, descricao,
-- opcoes, variantes, acompanhamentos e termos). Nada e inferido a partir do
-- nome comercial. unaccent ja existe no projeto e e o que faz "camarao"
-- encontrar "camarao".
create or replace function private.cardapio_indice_busca(p_id text)
returns text
language sql
stable
set search_path = pg_catalog, public
as $function$
  select array_to_string(array(
    select distinct palavra from unnest(string_to_array(
      lower(public.unaccent(
        concat_ws(' ',
          p.nome, p.nome_original, p.descritor, p.descricao, p.detalhe,
          array_to_string(p.inclui, ' '),
          array_to_string(p.termos, ' '),
          (select string_agg(o->>'texto', ' ') from jsonb_array_elements(p.opcoes) o),
          (select string_agg(v.nome, ' ') from public.cardapio_variante v where v.produto_id = p.id),
          (select string_agg(a.nome, ' ') from public.cardapio_adicional a where a.produto_id = p.id),
          (select string_agg(s.termo || ' ' || array_to_string(s.alternativas, ' '), ' ')
             from public.cardapio_sinonimo s
            where lower(public.unaccent(concat_ws(' ', p.nome, p.descritor, p.descricao,
                                                  array_to_string(p.termos, ' '))))
                  like '%' || lower(public.unaccent(s.termo)) || '%'
               or exists (select 1 from unnest(s.alternativas) alt
                          where lower(public.unaccent(concat_ws(' ', p.nome, p.descritor,
                                p.descricao, array_to_string(p.termos, ' '))))
                                like '%' || lower(public.unaccent(alt)) || '%'))
        )
      )), ' ') as palavra
    where palavra <> ''
    order by palavra
  ), ' ')
  from public.cardapio_produto p where p.id = p_id;
$function$;


-- Esta funcao e o UNICO lugar que decide o que o cliente enxerga. Tudo o que
-- nao for montado aqui simplesmente nao existe para o portal.
--
-- Regras que ela aplica, e o motivo de cada uma:
--   * porcao divergente sai sem numero -- escolher uma das fontes que se
--     contradizem seria inventar um fato;
--   * lista alimentar vazia vira "nao revisado", nunca "nao contem";
--   * adicional nao entra no calculo da faixa de preco -- ele nao e um jeito
--     mais barato de pedir o produto;
--   * rende_pessoas so sai se estiver preenchido; peso nunca e convertido em
--     numero de pessoas;
--   * produto com publicar=false ou arquivado=true fica de fora.
create or replace function private.cardapio_porcao_publica(p jsonb)
returns jsonb
language sql
immutable
set search_path = pg_catalog, public
as $function$
  with base as (
    select
      case coalesce(p->>'estado', 'ausente')
        when 'declarado' then 'informada'
        when 'parcial'   then 'informada'
        when 'divergente' then 'em_conferencia'
        else 'nao_informada'
      end as estado0,
      nullif(p->>'texto', '') as texto0
  ), ajuste as (
    select
      case
        when estado0 = 'informada' and texto0 is null
          then case when p ? 'divergencia' and p->>'divergencia' is not null
                    then 'em_conferencia' else 'nao_informada' end
        else estado0
      end as estado,
      case when estado0 = 'informada' then texto0 end as texto
    from base
  )
  select jsonb_build_object(
    'texto', case when estado = 'informada' then texto end,
    'detalhes', '[]'::jsonb,
    'nota', p->>'nota',
    'estado', estado
  ) from ajuste;
$function$;

create or replace function private.cardapio_alimentar_publica(a jsonb)
returns jsonb
language sql
immutable
set search_path = pg_catalog, public
as $function$
  select jsonb_build_object(
    'declarados', coalesce(a->'declarados', '[]'::jsonb),
    'estado', est,
    'texto', case est
      when 'declarado' then 'Marcações transcritas do cardápio impresso, ainda não conferidas com a cozinha. Consulte a equipe sobre alérgenos.'
      when 'sem_marcacoes' then 'Este item não tem marcações no cardápio impresso. Isso não significa ausência de alérgenos. Consulte a equipe.'
      else 'Informação alimentar ainda não revisada para este item. Consulte a equipe.'
    end,
    'confirmado', coalesce(a->'confirmado_cozinha', '[]'::jsonb),
    'contato_cruzado', coalesce(a->'contato_cruzado', '[]'::jsonb)
  )
  from (select case coalesce(a->>'estado', 'nao_revisado')
                 when 'declarado_no_impresso' then 'declarado'
                 when 'sem_simbolos' then 'sem_marcacoes'
                 else 'nao_revisado' end as est) t;
$function$;

create or replace function private.cardapio_montar_publicacao()
returns jsonb
language plpgsql
stable
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_produtos jsonb;
  v_categorias jsonb;
  v_avisos jsonb;
begin
  select coalesce(jsonb_agg(item order by ordem_cat, ordem_prod), '[]'::jsonb)
    into v_produtos
  from (
    select c.ordem as ordem_cat, p.ordem as ordem_prod,
      jsonb_strip_nulls(jsonb_build_object(
        'id', p.id,
        'categoria', p.categoria_id,
        'subgrupo', p.subgrupo,
        'ordem', p.ordem,
        'nome', p.nome,
        'descritor', p.descritor,
        'descricao', p.descricao,
        'detalhe', p.detalhe
      )) || jsonb_build_object(
        'preco', case
          when v.menor is not null and v.menor <> v.maior
            then jsonb_build_object('tipo', 'faixa', 'min', v.menor,
                                    'max', v.maior, 'centavos', v.menor)
          when v.menor is not null
            then jsonb_build_object('tipo', 'exato', 'centavos', v.menor)
          when p.preco_centavos is not null
            then jsonb_build_object('tipo', 'exato', 'centavos', p.preco_centavos)
          else jsonb_build_object('tipo', 'ausente', 'centavos', null)
        end,
        'variantes', coalesce(v.lista, '[]'::jsonb),
        'adicionais', coalesce(a.lista, '[]'::jsonb),
        'inclui', to_jsonb(p.inclui),
        'opcoes', coalesce((
          select jsonb_agg(jsonb_build_object('texto', o->>'texto'))
          from jsonb_array_elements(p.opcoes) o
          where nullif(o->>'texto', '') is not null), '[]'::jsonb),
        'porcao', private.cardapio_porcao_publica(p.porcao),
        'alimentar', private.cardapio_alimentar_publica(p.alimentar),
        'foto', p.foto,
        'etiquetas', to_jsonb(p.etiquetas),
        'busca', private.cardapio_indice_busca(p.id),
        'disponivel', p.disponivel
      ) as item
    from public.cardapio_produto p
    join public.cardapio_categoria c on c.id = p.categoria_id
    left join lateral (
      select jsonb_agg(jsonb_build_object('nome', x.nome,
                                          'preco_centavos', x.preco_centavos)
                       order by x.ordem, x.nome) as lista,
             min(x.preco_centavos) as menor, max(x.preco_centavos) as maior
      from public.cardapio_variante x where x.produto_id = p.id
    ) v on true
    left join lateral (
      select jsonb_agg(jsonb_build_object('nome', x.nome,
                                          'preco_centavos', x.preco_centavos)
                       order by x.ordem, x.nome) as lista
      from public.cardapio_adicional x where x.produto_id = p.id
    ) a on true
    where p.publicar and not p.arquivado and c.ativo
  ) t;

  select coalesce(jsonb_agg(
    jsonb_build_object(
      'id', c.id, 'nome', c.nome, 'resumo', c.resumo,
      'grupo', c.grupo, 'subgrupos', c.subgrupos,
      'faixa', f.faixa
    ) order by c.ordem), '[]'::jsonb)
    into v_categorias
  from public.cardapio_categoria c
  left join lateral (
    -- Faixa de preco da categoria: ajuda quem chega com um orcamento em
    -- mente. Sai inteira dos precos cadastrados e nao classifica nada como
    -- barato, caro ou vantajoso.
    select case when count(*) = 0 then null else jsonb_build_object(
             'itens', count(*)::int,
             'min', min(valor)::int, 'max', max(valor)::int) end as faixa
    from (
      select p.id,
             coalesce((select min(preco_centavos) from public.cardapio_variante x
                       where x.produto_id = p.id), p.preco_centavos) as valor
      from public.cardapio_produto p
      where p.categoria_id = c.id and p.publicar and not p.arquivado
        and coalesce(p.preco_centavos,
              (select min(preco_centavos) from public.cardapio_variante x
               where x.produto_id = p.id)) is not null
      union all
      select p.id, (select max(preco_centavos) from public.cardapio_variante x
                    where x.produto_id = p.id)
      from public.cardapio_produto p
      where p.categoria_id = c.id and p.publicar and not p.arquivado
        and exists (select 1 from public.cardapio_variante x where x.produto_id = p.id)
    ) q where valor is not null
  ) f on true
  where c.ativo;

  select coalesce(jsonb_agg(jsonb_build_object(
           'id', id, 'titulo', titulo, 'texto', texto) order by ordem), '[]'::jsonb)
    into v_avisos
  from public.cardapio_aviso where publicar;

  return jsonb_build_object(
    'estado', coalesce((select valor from public.cardapio_estado limit 1), 'em_conferencia'),
    'aviso_estado', case
      when coalesce((select valor from public.cardapio_estado limit 1), 'em_conferencia') <> 'vigente'
      then 'Cardápio em conferência. Confirme preços e porções com a equipe.'
    end,
    'moeda', 'BRL',
    'avisos', v_avisos,
    'categorias', v_categorias,
    'produtos', v_produtos
  );
end;
$function$;


---------------------------------------------------------------------
-- Contrato de leitura publica
-- ---------------------------------------------------------------------------

-- A UNICA coisa que o visitante anonimo alcanca. Devolve a publicacao ativa
-- com a disponibilidade do dia aplicada por cima. Nao existe caminho daqui
-- para o rascunho, para as notas internas ou para qualquer dado financeiro.
create or replace view public.cardapio_publico
with (security_barrier = true, security_invoker = false) as
select
  p.versao,
  p.publicado_em,
  jsonb_set(p.conteudo, '{produtos}', coalesce((
    select jsonb_agg(
      case
        when d.id is null then item
        else jsonb_set(item, '{disponivel}', to_jsonb(d.disponivel))
      end
      order by ord)
    from jsonb_array_elements(p.conteudo->'produtos') with ordinality as t(item, ord)
    left join public.cardapio_produto d
      on d.id = item->>'id' and not d.arquivado
  ), '[]'::jsonb)) as conteudo
from public.cardapio_publicacao p
where p.ativo;

comment on view public.cardapio_publico is
  'Contrato de leitura publica do cardapio. Unico objeto do cardapio com grant para anon. Devolve a publicacao ativa com a disponibilidade lida ao vivo: restaurar uma versao antiga nao reativa um item esgotado.';

-- ---------------------------------------------------------------------------
-- Leitura do painel
-- ---------------------------------------------------------------------------

create or replace view public.app_cardapio_categorias
with (security_barrier = true, security_invoker = false) as
select c.id, c.nome, c.resumo, c.grupo, c.subgrupos, c.ordem, c.ativo,
       c.atualizado_em,
       private.nome_exibicao_usuario(c.atualizado_por) as atualizado_por_nome,
       (select count(*) from public.cardapio_produto p
         where p.categoria_id = c.id and not p.arquivado) as produtos
from public.cardapio_categoria c
where public.usuario_pode_acessar_pagina('cardapio.html');

create or replace view public.app_cardapio_produtos
with (security_barrier = true, security_invoker = false) as
select
  p.id, p.categoria_id, p.subgrupo, p.nome, p.nome_original, p.descritor,
  p.descricao, p.detalhe, p.preco_centavos, p.ordem, p.inclui, p.opcoes,
  p.porcao, p.alimentar, p.foto, p.termos, p.etiquetas, p.publicar,
  p.pendencias, p.fontes, p.notas_internas, p.disponivel,
  p.indisponivel_motivo, p.disponibilidade_em, p.arquivado,
  p.criado_em, p.atualizado_em,
  private.nome_exibicao_usuario(p.atualizado_por) as atualizado_por_nome,
  c.nome as categoria_nome, c.grupo as categoria_grupo,
  coalesce((select jsonb_agg(jsonb_build_object('id', v.id, 'nome', v.nome,
             'preco_centavos', v.preco_centavos, 'ordem', v.ordem)
             order by v.ordem, v.nome)
            from public.cardapio_variante v where v.produto_id = p.id),
           '[]'::jsonb) as variantes,
  coalesce((select jsonb_agg(jsonb_build_object('id', a.id, 'nome', a.nome,
             'preco_centavos', a.preco_centavos, 'ordem', a.ordem)
             order by a.ordem, a.nome)
            from public.cardapio_adicional a where a.produto_id = p.id),
           '[]'::jsonb) as adicionais,
  -- Diferenca entre o rascunho e o que esta no ar agora. E o que permite a
  -- pagina mostrar "o que muda se eu publicar".
  (p.atualizado_em > coalesce((select publicado_em from public.cardapio_publicacao
                               where ativo), '-infinity'::timestamptz)) as alterado_apos_publicacao
from public.cardapio_produto p
join public.cardapio_categoria c on c.id = p.categoria_id
where public.usuario_pode_acessar_pagina('cardapio.html');

create or replace view public.app_cardapio_publicacoes
with (security_barrier = true, security_invoker = false) as
select id, versao, resumo, observacao, origem_versao, publicado_em, ativo,
       private.nome_exibicao_usuario(publicado_por) as publicado_por_nome,
       jsonb_array_length(conteudo->'produtos') as produtos
from public.cardapio_publicacao
where public.usuario_pode_acessar_pagina('cardapio.html');

create or replace view public.app_cardapio_disponibilidade
with (security_barrier = true, security_invoker = false) as
select l.id, l.produto_id, p.nome as produto_nome, l.disponivel, l.motivo,
       l.criado_em, private.nome_exibicao_usuario(l.usuario_id) as usuario_nome
from public.cardapio_disponibilidade_log l
join public.cardapio_produto p on p.id = l.produto_id
where public.usuario_pode_acessar_pagina('cardapio.html');

create or replace view public.app_cardapio_estado
with (security_barrier = true, security_invoker = false) as
select e.valor, e.atualizado_em,
       private.nome_exibicao_usuario(e.atualizado_por) as atualizado_por_nome,
       (select count(*) from public.cardapio_produto p
         where cardinality(p.pendencias) > 0 and not p.arquivado) as produtos_com_pendencia,
       (select count(*) from public.cardapio_produto p
         where not p.disponivel and not p.arquivado) as produtos_indisponiveis,
       (select versao from public.cardapio_publicacao where ativo) as versao_publicada,
       (select publicado_em from public.cardapio_publicacao where ativo) as publicado_em
from public.cardapio_estado e
where public.usuario_pode_acessar_pagina('cardapio.html');

-- ---------------------------------------------------------------------------
-- Escrita
-- ---------------------------------------------------------------------------

create or replace function public.cardapio_salvar_produto(
  p_id text,
  p_dados jsonb,
  p_atualizado_em timestamptz default null
)
returns timestamptz
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_atual timestamptz;
  v_novo timestamptz := now();
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para editar o cardápio.';
  end if;

  select atualizado_em into v_atual from public.cardapio_produto where id = p_id;

  -- Edicao concorrente: se alguem salvou depois de a tela ter carregado, o
  -- salvamento e recusado em vez de sobrescrever em silencio.
  if v_atual is not null and p_atualizado_em is not null
     and v_atual > p_atualizado_em then
    raise exception 'EDICAO_CONCORRENTE: este produto foi alterado por outra pessoa às %. Recarregue antes de salvar.',
      to_char(v_atual at time zone 'America/Fortaleza', 'HH24:MI');
  end if;

  insert into public.cardapio_produto as t (
    id, categoria_id, subgrupo, nome, nome_original, descritor, descricao,
    detalhe, preco_centavos, ordem, inclui, opcoes, porcao, alimentar, foto,
    termos, etiquetas, publicar, pendencias, fontes, notas_internas,
    criado_por, atualizado_por, atualizado_em
  ) values (
    p_id,
    p_dados->>'categoria_id',
    nullif(p_dados->>'subgrupo', ''),
    btrim(p_dados->>'nome'),
    nullif(p_dados->>'nome_original', ''),
    nullif(p_dados->>'descritor', ''),
    nullif(p_dados->>'descricao', ''),
    nullif(p_dados->>'detalhe', ''),
    nullif(p_dados->>'preco_centavos', '')::integer,
    coalesce(nullif(p_dados->>'ordem', '')::integer, 0),
    coalesce(array(select jsonb_array_elements_text(p_dados->'inclui')), '{}'),
    coalesce(p_dados->'opcoes', '[]'::jsonb),
    coalesce(p_dados->'porcao', '{}'::jsonb),
    coalesce(p_dados->'alimentar', '{}'::jsonb),
    p_dados->'foto',
    coalesce(array(select jsonb_array_elements_text(p_dados->'termos')), '{}'),
    coalesce(array(select jsonb_array_elements_text(p_dados->'etiquetas')), '{}'),
    coalesce((p_dados->>'publicar')::boolean, true),
    coalesce(array(select jsonb_array_elements_text(p_dados->'pendencias')), '{}'),
    coalesce(array(select jsonb_array_elements_text(p_dados->'fontes')), '{}'),
    coalesce(array(select jsonb_array_elements_text(p_dados->'notas_internas')), '{}'),
    auth.uid(), auth.uid(), v_novo
  )
  on conflict (id) do update set
    categoria_id = excluded.categoria_id,
    subgrupo = excluded.subgrupo,
    nome = excluded.nome,
    nome_original = coalesce(t.nome_original, excluded.nome_original),
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
    atualizado_por = auth.uid(),
    atualizado_em = v_novo;

  -- Variantes e adicionais chegam inteiros e substituem os anteriores. Sao
  -- listas pequenas; reconciliar item a item so traria chance de erro.
  if p_dados ? 'variantes' then
    delete from public.cardapio_variante where produto_id = p_id;
    insert into public.cardapio_variante (produto_id, nome, preco_centavos, ordem)
    select p_id, btrim(v->>'nome'), (v->>'preco_centavos')::integer,
           coalesce((v->>'ordem')::integer, ord::integer)
    from jsonb_array_elements(p_dados->'variantes') with ordinality as x(v, ord)
    where nullif(btrim(v->>'nome'), '') is not null;
  end if;

  if p_dados ? 'adicionais' then
    delete from public.cardapio_adicional where produto_id = p_id;
    insert into public.cardapio_adicional (produto_id, nome, preco_centavos, ordem)
    select p_id, btrim(a->>'nome'), (a->>'preco_centavos')::integer,
           coalesce((a->>'ordem')::integer, ord::integer)
    from jsonb_array_elements(p_dados->'adicionais') with ordinality as x(a, ord)
    where nullif(btrim(a->>'nome'), '') is not null;
  end if;

  return v_novo;
end;
$function$;

-- Acao rapida e isolada: nao passa pelo formulario, nao exige publicar e fica
-- registrada. Marcar esgotado precisa valer na mesa em segundos.
create or replace function public.cardapio_alterar_disponibilidade(
  p_id text,
  p_disponivel boolean,
  p_motivo text default null
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para alterar a disponibilidade.';
  end if;

  update public.cardapio_produto set
    disponivel = p_disponivel,
    indisponivel_motivo = case when p_disponivel then null
                               else nullif(btrim(coalesce(p_motivo, '')), '') end,
    disponibilidade_em = now()
  where id = p_id;

  if not found then
    raise exception 'Produto % não encontrado.', p_id;
  end if;

  insert into public.cardapio_disponibilidade_log
    (produto_id, disponivel, motivo, usuario_id)
  values (p_id, p_disponivel, nullif(btrim(coalesce(p_motivo, '')), ''), auth.uid());
end;
$function$;

create or replace function public.cardapio_previa()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para pré-visualizar o cardápio.';
  end if;
  return private.cardapio_montar_publicacao();
end;
$function$;

create or replace function public.cardapio_publicar(p_observacao text default null)
returns integer
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_conteudo jsonb;
  v_versao integer;
  v_anterior jsonb;
  v_resumo jsonb;
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para publicar o cardápio.';
  end if;

  v_conteudo := private.cardapio_montar_publicacao();

  if jsonb_array_length(v_conteudo->'produtos') = 0 then
    raise exception 'Nenhum produto publicável. A publicação foi cancelada e a versão no ar continua intacta.';
  end if;

  select conteudo into v_anterior from public.cardapio_publicacao where ativo;

  -- Resumo do que muda, para a tela de confirmacao. Comparacao por id: entrou,
  -- saiu, ou algum campo publicado mudou.
  select jsonb_build_object(
    'produtos', jsonb_array_length(v_conteudo->'produtos'),
    'incluidos', coalesce(inc, '[]'::jsonb),
    'removidos', coalesce(rem, '[]'::jsonb),
    'alterados', coalesce(alt, '[]'::jsonb)
  ) into v_resumo
  from (
    select
      (select jsonb_agg(n->>'nome') from jsonb_array_elements(v_conteudo->'produtos') n
        where v_anterior is null or not exists (
          select 1 from jsonb_array_elements(v_anterior->'produtos') o
           where o->>'id' = n->>'id')) as inc,
      (select jsonb_agg(o->>'nome') from jsonb_array_elements(coalesce(v_anterior->'produtos', '[]'::jsonb)) o
        where not exists (select 1 from jsonb_array_elements(v_conteudo->'produtos') n
                           where n->>'id' = o->>'id')) as rem,
      (select jsonb_agg(n->>'nome') from jsonb_array_elements(v_conteudo->'produtos') n
        join jsonb_array_elements(coalesce(v_anterior->'produtos', '[]'::jsonb)) o
          on o->>'id' = n->>'id'
        where (o - 'disponivel') is distinct from (n - 'disponivel')) as alt
  ) t;

  v_versao := nextval('public.cardapio_versao_seq')::integer;

  update public.cardapio_publicacao set ativo = false where ativo;
  insert into public.cardapio_publicacao
    (versao, conteudo, resumo, observacao, publicado_por, ativo)
  values (v_versao, v_conteudo, v_resumo,
          nullif(btrim(coalesce(p_observacao, '')), ''), auth.uid(), true);

  return v_versao;
end;
$function$;

-- Restaurar cria uma versao NOVA com o conteudo antigo. O historico nunca e
-- apagado, e a disponibilidade de hoje continua valendo, porque ela nunca
-- esteve dentro da fotografia.
create or replace function public.cardapio_restaurar(p_versao integer)
returns integer
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_conteudo jsonb;
  v_nova integer;
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para restaurar uma versão do cardápio.';
  end if;

  select conteudo into v_conteudo
  from public.cardapio_publicacao where versao = p_versao;

  if v_conteudo is null then
    raise exception 'Versão % não encontrada.', p_versao;
  end if;

  v_nova := nextval('public.cardapio_versao_seq')::integer;
  update public.cardapio_publicacao set ativo = false where ativo;
  insert into public.cardapio_publicacao
    (versao, conteudo, resumo, observacao, origem_versao, publicado_por, ativo)
  values (v_nova, v_conteudo,
          jsonb_build_object('produtos', jsonb_array_length(v_conteudo->'produtos')),
          format('Restauração da versão %s', p_versao), p_versao, auth.uid(), true);

  return v_nova;
end;
$function$;

create or replace function public.cardapio_definir_estado(p_valor text)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para alterar o estado do cardápio.';
  end if;
  update public.cardapio_estado
     set valor = p_valor, atualizado_por = auth.uid(), atualizado_em = now()
   where id;
end;
$function$;

create or replace function public.cardapio_salvar_categoria(
  p_id text, p_dados jsonb
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para editar categorias.';
  end if;

  insert into public.cardapio_categoria
    (id, nome, resumo, grupo, subgrupos, ordem, ativo, atualizado_por, atualizado_em)
  values (p_id, btrim(p_dados->>'nome'), nullif(p_dados->>'resumo', ''),
          coalesce(nullif(p_dados->>'grupo', ''), 'comer'),
          coalesce(p_dados->'subgrupos', '[]'::jsonb),
          coalesce(nullif(p_dados->>'ordem', '')::integer, 0),
          coalesce((p_dados->>'ativo')::boolean, true), auth.uid(), now())
  on conflict (id) do update set
    nome = excluded.nome, resumo = excluded.resumo, grupo = excluded.grupo,
    subgrupos = excluded.subgrupos, ordem = excluded.ordem,
    ativo = excluded.ativo, atualizado_por = auth.uid(), atualizado_em = now();
end;
$function$;

-- ---------------------------------------------------------------------------
-- Fotos
-- ---------------------------------------------------------------------------

-- Bucket publico: a foto do prato e servida ao visitante anonimo do portal,
-- entao nao ha o que proteger na leitura. Escrever e apagar continuam presos
-- ao mesmo portao da pagina. O bloco e condicional porque o schema storage so
-- existe no Supabase; num Postgres puro (a verificacao de migrations em banco
-- descartavel) o cardapio segue funcionando com as fotos do proprio site.
do $migration$
begin
  if to_regclass('storage.buckets') is null then
    raise notice 'Schema storage ausente: bucket de fotos do cardapio nao criado.';
    return;
  end if;

  insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  values ('cardapio-fotos', 'cardapio-fotos', true, 5242880,
          array['image/jpeg', 'image/png', 'image/webp', 'image/avif'])
  on conflict (id) do update
    set public = true, file_size_limit = 5242880,
        allowed_mime_types = array['image/jpeg', 'image/png', 'image/webp', 'image/avif'];

  if to_regclass('storage.objects') is null then return; end if;

  execute $policy$drop policy if exists cardapio_foto_ler on storage.objects$policy$;
  execute $policy$
    create policy cardapio_foto_ler on storage.objects
      for select to anon, authenticated
      using (bucket_id = 'cardapio-fotos')
  $policy$;

  execute $policy$drop policy if exists cardapio_foto_enviar on storage.objects$policy$;
  execute $policy$
    create policy cardapio_foto_enviar on storage.objects
      for insert to authenticated
      with check (bucket_id = 'cardapio-fotos'
                  and public.usuario_pode_acessar_pagina('cardapio.html')
                  and name like 'produto/%')
  $policy$;

  execute $policy$drop policy if exists cardapio_foto_remover on storage.objects$policy$;
  execute $policy$
    create policy cardapio_foto_remover on storage.objects
      for delete to authenticated
      using (bucket_id = 'cardapio-fotos'
             and public.usuario_pode_acessar_pagina('cardapio.html'))
  $policy$;
end;
$migration$;

-- ---------------------------------------------------------------------------
-- Permissoes
-- ---------------------------------------------------------------------------

revoke all privileges on public.cardapio_publico from public, anon, authenticated;
grant select on public.cardapio_publico to anon, authenticated;

revoke all privileges on public.app_cardapio_categorias from public, anon, authenticated;
revoke all privileges on public.app_cardapio_produtos from public, anon, authenticated;
revoke all privileges on public.app_cardapio_publicacoes from public, anon, authenticated;
revoke all privileges on public.app_cardapio_disponibilidade from public, anon, authenticated;
revoke all privileges on public.app_cardapio_estado from public, anon, authenticated;
grant select on public.app_cardapio_categorias to authenticated;
grant select on public.app_cardapio_produtos to authenticated;
grant select on public.app_cardapio_publicacoes to authenticated;
grant select on public.app_cardapio_disponibilidade to authenticated;
grant select on public.app_cardapio_estado to authenticated;

revoke all privileges on function private.cardapio_montar_publicacao() from public, anon, authenticated;
revoke all privileges on function private.cardapio_indice_busca(text) from public, anon, authenticated;
revoke all privileges on function private.cardapio_porcao_publica(jsonb) from public, anon, authenticated;
revoke all privileges on function private.cardapio_alimentar_publica(jsonb) from public, anon, authenticated;

revoke all privileges on function public.cardapio_salvar_produto(text, jsonb, timestamptz) from public, anon, authenticated;
revoke all privileges on function public.cardapio_salvar_categoria(text, jsonb) from public, anon, authenticated;
revoke all privileges on function public.cardapio_alterar_disponibilidade(text, boolean, text) from public, anon, authenticated;
revoke all privileges on function public.cardapio_previa() from public, anon, authenticated;
revoke all privileges on function public.cardapio_publicar(text) from public, anon, authenticated;
revoke all privileges on function public.cardapio_restaurar(integer) from public, anon, authenticated;
revoke all privileges on function public.cardapio_definir_estado(text) from public, anon, authenticated;

grant execute on function public.cardapio_salvar_produto(text, jsonb, timestamptz) to authenticated;
grant execute on function public.cardapio_salvar_categoria(text, jsonb) to authenticated;
grant execute on function public.cardapio_alterar_disponibilidade(text, boolean, text) to authenticated;
grant execute on function public.cardapio_previa() to authenticated;
grant execute on function public.cardapio_publicar(text) to authenticated;
grant execute on function public.cardapio_restaurar(integer) to authenticated;
grant execute on function public.cardapio_definir_estado(text) to authenticated;

-- Quem enxerga a pagina edita o cardapio. Socio e gerente entram liberados; o
-- ajuste fino continua em permissoes.html, sem migration nova.
insert into public.pagina_permissao (pagina, papeis)
values ('cardapio.html', array['socio', 'gerente']::text[])
on conflict (pagina) do nothing;

commit;
