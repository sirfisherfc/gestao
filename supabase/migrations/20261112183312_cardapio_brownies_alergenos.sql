-- Icones dos brownies por receita padrao, a pedido do proprietario (12/11/2026).
-- Derivado de scripts/cardapio/catalogo_inicial.json. Somente alimentar;
-- preserva os demais campos, o aviso padrao e a publicacao ativa.
-- CLI indisponivel neste PC; migration gerada diretamente da fonte canonica.

begin;

update public.cardapio_produto
   set alimentar = '{"declarados": ["GLÚTEN", "LEITE", "LACTOSE", "OVO", "SOJA"], "fonte": "Receita padrão, autorizada pelo proprietário em 12/11/2026; não conferida com a cozinha ou o fornecedor.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb
 where id = 'brownie-de-chocolate'
   and 'carga-inicial' = any(fontes)
   and coalesce(alimentar->'confirmado_cozinha', '[]'::jsonb) = '[]'::jsonb
   and coalesce(alimentar->'contato_cruzado', '[]'::jsonb) = '[]'::jsonb
   and alimentar is distinct from '{"declarados": ["GLÚTEN", "LEITE", "LACTOSE", "OVO", "SOJA"], "fonte": "Receita padrão, autorizada pelo proprietário em 12/11/2026; não conferida com a cozinha ou o fornecedor.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

update public.cardapio_produto
   set alimentar = '{"declarados": ["GLÚTEN", "LEITE", "LACTOSE", "OVO", "SOJA"], "fonte": "Receita padrão, autorizada pelo proprietário em 12/11/2026; não conferida com a cozinha ou o fornecedor.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb
 where id = 'brownie-com-sorvete'
   and 'carga-inicial' = any(fontes)
   and coalesce(alimentar->'confirmado_cozinha', '[]'::jsonb) = '[]'::jsonb
   and coalesce(alimentar->'contato_cruzado', '[]'::jsonb) = '[]'::jsonb
   and alimentar is distinct from '{"declarados": ["GLÚTEN", "LEITE", "LACTOSE", "OVO", "SOJA"], "fonte": "Receita padrão, autorizada pelo proprietário em 12/11/2026; não conferida com a cozinha ou o fornecedor.", "estado": "nao_revisado", "divergencias": [], "alegacoes": [], "confirmado_cozinha": [], "contato_cruzado": []}'::jsonb;

commit;
