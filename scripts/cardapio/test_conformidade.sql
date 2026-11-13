-- Ensaio de conformidade no banco: sempre com ROLLBACK.
-- Requer migration 20261113150000; nao deixa dados ficticios persistidos.
begin;
update public.cardapio_produto set alimentar=alimentar - 'revisao';
do $test$
begin
  -- Marcacoes e precos: assercoes sobre a mudanca solicitada.
  if exists(select 1 from public.cardapio_produto where id='chope-brahma' and alimentar->'declarados' ? 'GLÚTEN') then
    raise exception 'Chope com icone retirado pelo proprietario';
  end if;
  if exists(select 1 from public.cardapio_produto where not arquivado and alimentar->'declarados' ? 'LACTOSE' and not alimentar->'declarados' ? 'LEITE') then
    raise exception 'Lactose sem leite';
  end if;
  begin
    perform private.cardapio_validar_revisoes();
    raise exception 'TEST_FAILURE: publicacao sem revisao aceita';
  exception when others then
    if SQLERRM not like 'Publicacao bloqueada.%' then raise; end if;
  end;
  -- Dados ficticios de revisao SO NO ENSAIO, removidos pelo rollback.
  update public.cardapio_produto set alimentar=jsonb_set(alimentar,'{revisao}',
    '{"fonte":"TESTE TRANSACIONAL FICTICIO", "em":"2026-11-13T12:00:00Z", "conferido":true}'::jsonb)
  where not arquivado;
  perform private.cardapio_validar_revisoes();
  -- Preco/estoque nao invalidam a receita.
  update public.cardapio_produto set preco_centavos=preco_centavos+1, disponivel=not disponivel where id='edimburger';
  perform private.cardapio_validar_revisoes();
  -- Uma composicao alterada exige conferencia nova.
  update public.cardapio_produto set descricao=descricao||' TESTE DE RECEITA' where id='edimburger';
  if exists(select 1 from public.cardapio_produto where id='edimburger' and alimentar ? 'revisao') then
    raise exception 'TEST_FAILURE: revisao antiga preservada';
  end if;
  begin
    perform private.cardapio_validar_revisoes();
    raise exception 'TEST_FAILURE: receita nova aceita sem revisao';
  exception when others then
    if SQLERRM not like 'Publicacao bloqueada.%' then raise; end if;
  end;
  if private.cardapio_revisao_valida('{"revisao":{"conferido":true}}'::jsonb) then
    raise exception 'TEST_FAILURE: referencia ausente aceita';
  end if;
  if private.cardapio_exige_revisao('cervejas','spaten-longneck',null) then
    raise exception 'TEST_FAILURE: cerveja de rotulo foi tratada como receita';
  end if;
  if not private.cardapio_exige_revisao('coqueteis','caipirinha',null) then
    raise exception 'TEST_FAILURE: coquetel sem icones ficou dispensado da revisao';
  end if;
end;
$test$;
rollback;
