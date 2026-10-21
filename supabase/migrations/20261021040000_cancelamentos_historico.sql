-- =====================================================================
-- Cancelamentos: casos anteriores à rotina viram histórico
-- =====================================================================
-- A rotina começou em 21/10/2026. A carga inicial trouxe 43 casos de
-- 01/09 a 20/10 que exigiriam justificativa; por decisão do proprietário,
-- eles ficam guardados com a marcação "Histórico anterior à rotina" e saem
-- da lista de pendências. Continuam visíveis (filtro Histórico) e podem ser
-- justificados ou revisados.
--
-- A marcação é gravada nos casos existentes e a view a aplica a qualquer
-- caso com data_turno antes de 21/10/2026, para que o reprocessamento diário
-- dos dias antigos não recrie pendências.
-- Não destrutiva; grants preservados por create or replace.
-- =====================================================================

begin;

alter table public.saipos_cancelamento add column if not exists marcacao text;

update public.saipos_cancelamento
set marcacao = 'Histórico anterior à rotina'
where data_turno < date '2026-10-21'
  and marcacao is null;

create or replace view public.app_saipos_cancelamento
with (security_barrier = true, security_invoker = false) as
select
  c.id, c.tipo, c.id_sale, c.data_turno, c.turno, c.mesa, c.produto, c.quantidade, c.valor,
  c.lancado_em, c.cancelado_em, c.minutos, c.min_ate_pagamento, c.bebida,
  c.lancou, c.garcom_id, c.cancelou, c.autorizou, c.motivo, c.sinais, c.pontos, c.exige_justificativa,
  c.justificativa, private.nome_exibicao_usuario(c.justificado_por) as justificado_por_nome, c.justificado_em,
  c.revisao, c.revisao_obs, private.nome_exibicao_usuario(c.revisado_por) as revisado_por_nome, c.revisado_em,
  coalesce(c.marcacao, case when c.data_turno < date '2026-10-21' then 'Histórico anterior à rotina' end) as marcacao
from public.saipos_cancelamento c
where public.usuario_pode_acessar_pagina('cancelamentos.html');

revoke all on public.app_saipos_cancelamento from anon;
grant select on public.app_saipos_cancelamento to authenticated;

commit;
