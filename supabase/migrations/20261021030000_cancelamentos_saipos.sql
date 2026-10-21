-- =====================================================================
-- Rotina Cancelamentos: itens e mesas cancelados na Saipos, com
-- justificativa dos gerentes e revisão de admin/sócio
-- =====================================================================
-- saipos_cancelamento: um item cancelado (apagado sem ir para outra mesa)
-- ou uma mesa inteira cancelada, com sinais de risco e pontuação calculados
-- por scripts/importacao/saipos_cancelamentos.py. O importador atualiza só
-- os dados da Saipos; justificativa e revisão ficam com as pessoas.
-- saipos_lancamento_resumo: valor lançado por dia, turno, hora e
-- funcionário, base do índice de cancelamento fora da curva.
--
-- Fluxo: casos com exige_justificativa = true aparecem como pendentes; quem
-- acessa cancelamentos.html justifica (justificar_cancelamento). Admin e
-- sócio revisam (revisar_cancelamento) como procedente ou suspeito; depois
-- da revisão a justificativa fica travada.
--
-- Grants explícitos (regra de 30/10/2026): authenticated só lê as views
-- app_* e executa as duas RPCs; anon e service_role não recebem nada.
-- =====================================================================

begin;

create table if not exists public.saipos_cancelamento (
  id text primary key,
  tipo text not null check (tipo in ('item', 'mesa')),
  id_sale bigint not null,
  id_sale_item bigint,
  data_turno date not null,
  turno text,
  mesa text,
  produto text,
  quantidade numeric(10,3),
  valor numeric(12,2) not null,
  lancado_em timestamp,
  cancelado_em timestamp,
  minutos integer,
  min_ate_pagamento numeric(10,1),
  bebida boolean,
  lancou text,
  garcom_id bigint,
  cancelou text,
  autorizou text,
  motivo text,
  sinais text[] not null default '{}',
  pontos smallint not null default 0,
  exige_justificativa boolean not null default false,
  importado_em timestamptz not null default now(),
  justificativa text,
  justificado_por uuid,
  justificado_em timestamptz,
  revisao text check (revisao in ('procedente', 'suspeito')),
  revisao_obs text,
  revisado_por uuid,
  revisado_em timestamptz
);

create index if not exists ix_saipos_cancelamento_data on public.saipos_cancelamento (data_turno);
create index if not exists ix_saipos_cancelamento_pendente
  on public.saipos_cancelamento (data_turno) where exige_justificativa and justificativa is null;

create table if not exists public.saipos_lancamento_resumo (
  data_turno date not null,
  turno text not null default '',
  hora smallint not null default -1,
  lancou text not null default '',
  itens integer not null,
  valor numeric(12,2) not null,
  primary key (data_turno, turno, hora, lancou)
);

alter table public.saipos_cancelamento enable row level security;
alter table public.saipos_lancamento_resumo enable row level security;
revoke all on public.saipos_cancelamento from anon, authenticated;
revoke all on public.saipos_lancamento_resumo from anon, authenticated;

create or replace view public.app_saipos_cancelamento
with (security_barrier = true, security_invoker = false) as
select
  c.id, c.tipo, c.id_sale, c.data_turno, c.turno, c.mesa, c.produto, c.quantidade, c.valor,
  c.lancado_em, c.cancelado_em, c.minutos, c.min_ate_pagamento, c.bebida,
  c.lancou, c.garcom_id, c.cancelou, c.autorizou, c.motivo, c.sinais, c.pontos, c.exige_justificativa,
  c.justificativa, private.nome_exibicao_usuario(c.justificado_por) as justificado_por_nome, c.justificado_em,
  c.revisao, c.revisao_obs, private.nome_exibicao_usuario(c.revisado_por) as revisado_por_nome, c.revisado_em
from public.saipos_cancelamento c
where public.usuario_pode_acessar_pagina('cancelamentos.html');

create or replace view public.app_saipos_lancamento_resumo
with (security_barrier = true, security_invoker = false) as
select r.data_turno, nullif(r.turno, '') as turno, nullif(r.hora, -1) as hora, nullif(r.lancou, '') as lancou, r.itens, r.valor
from public.saipos_lancamento_resumo r
where public.usuario_pode_acessar_pagina('cancelamentos.html');

revoke all on public.app_saipos_cancelamento from anon;
revoke all on public.app_saipos_lancamento_resumo from anon;
grant select on public.app_saipos_cancelamento to authenticated;
grant select on public.app_saipos_lancamento_resumo to authenticated;

create or replace function public.justificar_cancelamento(p_id text, p_justificativa text)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_texto text := nullif(btrim(coalesce(p_justificativa, '')), '');
begin
  if not public.usuario_pode_acessar_pagina('cancelamentos.html') then
    raise exception 'Sem permissao para justificar cancelamentos.';
  end if;
  if v_texto is null or length(v_texto) < 10 then
    raise exception 'Descreva o que aconteceu (minimo de 10 caracteres).';
  end if;
  update public.saipos_cancelamento set
    justificativa = v_texto,
    justificado_por = auth.uid(),
    justificado_em = now()
  where id = p_id and revisao is null;
  if not found then
    raise exception 'Cancelamento nao encontrado ou ja revisado.';
  end if;
end;
$function$;

create or replace function public.revisar_cancelamento(p_id text, p_revisao text, p_obs text default null)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if not public.usuario_tem_papel(array['admin', 'socio']::text[]) then
    raise exception 'Somente admin ou socio revisam cancelamentos.';
  end if;
  if p_revisao is not null and p_revisao not in ('procedente', 'suspeito') then
    raise exception 'Revisao invalida.';
  end if;
  update public.saipos_cancelamento set
    revisao = p_revisao,
    revisao_obs = case when p_revisao is null then null else nullif(btrim(coalesce(p_obs, '')), '') end,
    revisado_por = case when p_revisao is null then null else auth.uid() end,
    revisado_em = case when p_revisao is null then null else now() end
  where id = p_id;
  if not found then
    raise exception 'Cancelamento nao encontrado.';
  end if;
end;
$function$;

revoke all privileges on function public.justificar_cancelamento(text, text) from public, anon, authenticated;
revoke all privileges on function public.revisar_cancelamento(text, text, text) from public, anon, authenticated;
grant execute on function public.justificar_cancelamento(text, text) to authenticated;
grant execute on function public.revisar_cancelamento(text, text, text) to authenticated;

-- Gerente justifica; sócio revisa. Ajuste fino em permissoes.html.
insert into public.pagina_permissao (pagina, papeis)
values ('cancelamentos.html', array['socio', 'gerente']::text[])
on conflict (pagina) do nothing;

commit;
