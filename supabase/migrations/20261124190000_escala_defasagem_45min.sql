-- Recalibra a regua da escala contra os lancamentos reais de pedido.
-- So muda dois valores de public.escala_config; sem objeto novo nem grant.
--
-- 1) defasagem_venda_pagamento_min: 75 -> 45.
--    Curva dia da semana x hora dos itens lancados no Saipos (01/09 a
--    29/10/2026, 59 dias) contra os pagamentos deslocados: correlacao 0,886 com
--    50 min, 0,880 com 40 e 0,846 com 70. O 75 antecipava a curva e
--    escondia o movimento depois das 21h.
--
-- 2) capacidade_vendas_hora_pessoa: 4.34 -> 3.97.
--    Mesmo metodo de 20260819010000: pico da propria curva dividido por 3
--    pessoas. Com 45 min o pico passa a domingo 18h, 11,885 vendas/h. 3,97 e
--    nao 3,96 para o ceil() do proprio pico nao exigir uma quarta pessoa.

begin;

update public.escala_config
   set valor = 45,
       descricao = 'Minutos entre o pedido e o pagamento. Desloca a curva para o horario em que o trabalho acontece. Ajustado em 24/11/2026 contra os lancamentos do Saipos.'
 where chave = 'defasagem_venda_pagamento_min';

update public.escala_config
   set valor = 3.97,
       descricao = 'Teto de vendas/hora que uma pessoa atende. Calibrado pelo pico da propria curva com defasagem de 45 min: domingo 18h, 11,885 vendas/hora divididas por 3 pessoas.'
 where chave = 'capacidade_vendas_hora_pessoa';

commit;
