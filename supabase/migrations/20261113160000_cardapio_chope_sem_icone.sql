-- Pedido expresso do proprietario em 13/11/2026: retirar icone do chope.
-- Nao certifica ausencia de gluten. Somente alimentar; demais dados preservados.
begin;
do $guard$
begin
  if not exists(select 1 from public.cardapio_produto where id='chope-brahma'
    and (alimentar = '{"declarados": ["GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 2; parecer juridico de 12/11/2026, Anexo I: indicar gluten no Chope Brahma.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb or alimentar = '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2; icone de gluten retirado por pedido expresso do proprietario em 13/11/2026; nao certifica ausencia de gluten.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb)) then
    raise exception 'Chope divergente da origem; revisar antes de alterar.';
  end if;
end;
$guard$;
update public.cardapio_produto set alimentar = '{"declarados": [], "fonte": "Sir Fisher Praia.pdf, página 2; icone de gluten retirado por pedido expresso do proprietario em 13/11/2026; nao certifica ausencia de gluten.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb
where id='chope-brahma' and alimentar = '{"declarados": ["GLÚTEN"], "fonte": "Sir Fisher Praia.pdf, página 2; parecer juridico de 12/11/2026, Anexo I: indicar gluten no Chope Brahma.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;
commit;
