-- Parecer juridico de 12/11/2026: ajustes comprovados e revisao antes de publicar.

-- Nao confirma cozinha, remove alergenos, muda precos ou publica o rascunho.

begin;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "LACTOSE", "CRUSTÁCEOS", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'patinha-de-caranguejo' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "LACTOSE", "CRUSTÁCEOS"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "LACTOSE", "PEIXE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'bolinha-de-peixe-cremosa' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "LACTOSE", "PEIXE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "OVO", "LACTOSE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'crocante-carne-de-sol' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "OVO", "LACTOSE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'crocante-calabresa' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "OVO", "CORANTES", "LEITE", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'big-ben-fries' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "OVO", "CORANTES"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["LACTOSE", "CRUSTÁCEOS", "GLÚTEN", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": ["Os símbolos são do bloco com os três sabores. O impresso não separa as marcações por sabor."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb, descricao = 'Dez pastéis crocantes com molho especial. Escolha o recheio: 2 queijos, carne ou camarão. As marcações reúnem os três sabores e o molho; consulte a equipe sobre os alérgenos de cada recheio antes de pedir.' where id = 'pasteizinhos' and alimentar is not distinct from '{"declarados": ["LACTOSE", "CRUSTÁCEOS", "GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": ["Os símbolos são do bloco com os três sabores. O impresso não separa as marcações por sabor."], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb and descricao is not distinct from 'Dez pastéis crocantes com molho especial. Sabor a escolher.';

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "LACTOSE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'dadinho-de-tapioca' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "PEIXE", "OVO", "LACTOSE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'isca-de-peixe' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "PEIXE", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "PEIXE", "OVO", "LACTOSE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'fisher-burger' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "PEIXE", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN", "OVO", "LACTOSE", "LEITE"], "fonte": "Sir Fisher Praia.pdf, página 1; parecer juridico de 12/11/2026: leite separado de lactose/derivado lacteo declarado; ficha tecnica pendente.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'edimburger' and alimentar is not distinct from '{"declarados": ["GLÚTEN", "OVO", "LACTOSE"], "fonte": "Sir Fisher Praia.pdf, página 1", "estado": "declarado_no_impresso", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto set alimentar = '{"declarados": ["GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 2; parecer juridico de 12/11/2026, Anexo I: indicar gluten no Chope Brahma.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb where id = 'chope-brahma' and alimentar is not distinct from '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2", "estado": "sem_simbolos", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;


-- Preparacao propria: inclui molhos, extras comestiveis e bebidas montadas na casa.
create or replace function private.cardapio_exige_revisao(categoria text, produto text, subgrupo text)
returns boolean language sql immutable set search_path = pg_catalog as $fn$
  select categoria in ('fish-and-chips','petiscos','sanduiches','para-dividir','sobremesas','coqueteis')
    or (categoria = 'extras' and subgrupo = 'comestiveis')
    or produto in ('agua-de-coco-copo','suco-copo','soda-italiana','sumo-de-limao');
$fn$;
revoke all on function private.cardapio_exige_revisao(text,text,text) from public, anon, authenticated;

-- Atestado exige referencia, data e confirmacao explicita, inclusive lista vazia.
create or replace function private.cardapio_revisao_valida(a jsonb)
returns boolean language sql immutable set search_path = pg_catalog as $fn$
  select coalesce(a->'revisao'->>'conferido' = 'true'
    and length(btrim(a->'revisao'->>'fonte')) >= 3
    and length(btrim(a->'revisao'->>'em')) >= 10, false);
$fn$;
revoke all on function private.cardapio_revisao_valida(jsonb) from public, anon, authenticated;

-- Invalidar revisao antiga quando a composicao muda sem novo atestado.
create or replace function private.cardapio_invalidar_revisao()
returns trigger language plpgsql set search_path = pg_catalog, public as $fn$
begin
  if (jsonb_build_array(new.nome,new.descritor,new.descricao,new.detalhe,new.inclui,new.opcoes,new.alimentar->'declarados')
      is distinct from
      jsonb_build_array(old.nome,old.descritor,old.descricao,old.detalhe,old.inclui,old.opcoes,old.alimentar->'declarados'))
    and new.alimentar->'revisao' is not distinct from old.alimentar->'revisao' then
    new.alimentar := new.alimentar - 'revisao';
  end if;
  return new;
end;
$fn$;
revoke all on function private.cardapio_invalidar_revisao() from public, anon, authenticated;
drop trigger if exists cardapio_invalidar_revisao on public.cardapio_produto;
create trigger cardapio_invalidar_revisao before update on public.cardapio_produto
for each row execute function private.cardapio_invalidar_revisao();

create or replace function private.cardapio_validar_revisoes()
returns void language plpgsql security definer set search_path = pg_catalog, public as $fn$
declare pendentes text;
begin
  select string_agg(nome, ', ' order by ordem) into pendentes
  from public.cardapio_produto p
  where publicar and not arquivado
    and private.cardapio_exige_revisao(categoria_id,id,subgrupo)
    and not private.cardapio_revisao_valida(alimentar);
  if pendentes is not null then
    raise exception 'Publicacao bloqueada. Registre a revisao por ficha tecnica e rotulos: %', pendentes;
  end if;
end;
$fn$;
revoke all on function private.cardapio_validar_revisoes() from public, anon, authenticated;


CREATE OR REPLACE FUNCTION public.cardapio_publicar(p_observacao text DEFAULT NULL::text)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'public'
AS $function$
declare
  v_conteudo jsonb;
  v_versao integer;
  v_anterior jsonb;
  v_resumo jsonb;
begin
  if not public.usuario_pode_acessar_pagina('cardapio.html') then
    raise exception 'Sem permissão para publicar o cardápio.';
  end if;

  perform private.cardapio_validar_revisoes();

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

CREATE OR REPLACE FUNCTION public.cardapio_restaurar(p_versao integer)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'public'
AS $function$
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

  perform private.cardapio_validar_revisoes();
  -- Historico nao dispensa conferencia: receitas restauradas devem coincidir
  -- com a previa atual revisada. Reajustes podem ser feitos no rascunho.
  if exists (
    select 1 from jsonb_array_elements(v_conteudo->'produtos') historico
    where private.cardapio_exige_revisao(historico->>'categoria',historico->>'id',historico->>'subgrupo')
      and not exists (
        select 1 from jsonb_array_elements(private.cardapio_montar_publicacao()->'produtos') atual
        where (atual - 'disponivel') = (historico - 'disponivel')
      )
  ) then
    raise exception 'Restauracao bloqueada: confira as receitas antigas no rascunho e publique uma nova versao revisada.';
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

commit;
