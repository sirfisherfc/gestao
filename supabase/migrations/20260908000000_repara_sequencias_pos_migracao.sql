-- Repara sequencias de chaves tecnicas apos migracao/restauracao de banco.
--
-- Ao inserir IDs explicitamente durante uma migracao, PostgreSQL nao avanca a
-- sequencia associada. A proxima escrita pode tentar reutilizar um ID ja
-- existente e falhar com "duplicate key ... _pkey", mesmo em um UPSERT cuja
-- chave de negocio esteja correta. Isto atingiu venda_especie e
-- conta_recorrente_pagamento, mas a causa pode existir em qualquer tabela.
--
-- A rotina percorre somente sequencias pertencentes a colunas de tabelas dos
-- schemas da aplicacao (public e private; serial e identity), trava cada tabela enquanto confere seu
-- maior ID e posiciona a sequencia para o proximo valor seguro. Nao altera,
-- exclui ou recria linhas, constraints, views ou permissoes.

begin;

do $reparar_sequencias$
declare
  v_item record;
  v_maior_id bigint;
  v_tem_linhas boolean;
begin
  for v_item in
    select
      tabela_ns.nspname as tabela_schema,
      tabela.relname as tabela_nome,
      coluna.attname as coluna_nome,
      sequencia_ns.nspname as sequencia_schema,
      sequencia.relname as sequencia_nome
    from pg_catalog.pg_class sequencia
    join pg_catalog.pg_namespace sequencia_ns
      on sequencia_ns.oid = sequencia.relnamespace
    join pg_catalog.pg_depend dependencia
      on dependencia.classid = 'pg_class'::regclass
     and dependencia.objid = sequencia.oid
     and dependencia.refclassid = 'pg_class'::regclass
     and dependencia.deptype in ('a', 'i')
    join pg_catalog.pg_class tabela
      on tabela.oid = dependencia.refobjid
     and tabela.relkind in ('r', 'p')
    join pg_catalog.pg_namespace tabela_ns
      on tabela_ns.oid = tabela.relnamespace
    join pg_catalog.pg_attribute coluna
      on coluna.attrelid = tabela.oid
     and coluna.attnum = dependencia.refobjsubid
     and not coluna.attisdropped
    where sequencia.relkind = 'S'
      and tabela_ns.nspname in ('public', 'private')
    order by tabela_ns.nspname, tabela.relname, coluna.attnum
  loop
    -- Impede que um INSERT concorra com a leitura do maximo e com setval.
    execute format(
      'lock table %I.%I in share row exclusive mode',
      v_item.tabela_schema,
      v_item.tabela_nome
    );

    execute format(
      'select max(%I)::bigint, count(*) > 0 from %I.%I',
      v_item.coluna_nome,
      v_item.tabela_schema,
      v_item.tabela_nome
    ) into v_maior_id, v_tem_linhas;

    -- Em tabela vazia, is_called=false faz o proximo nextval retornar 1.
    -- Em tabela preenchida, is_called=true faz o proximo nextval seguir o
    -- maior ID efetivamente armazenado.
    perform pg_catalog.setval(
      pg_catalog.to_regclass(format('%I.%I', v_item.sequencia_schema, v_item.sequencia_nome)),
      coalesce(v_maior_id, 1),
      v_tem_linhas
    );
  end loop;
end;
$reparar_sequencias$;

commit;
