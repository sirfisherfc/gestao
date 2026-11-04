-- Inclui no caixa o principal do Rende Fácil a partir dos movimentos BB.
-- O proprietário confirmou início em outubro/2026 com saldo anterior zero.
-- Rendimentos/tributos não informados na conta corrente não são estimados.
begin;

create temporary table bb_rende_saldos_antes on commit drop as
select dia, conta_id, saldo from private.mv_saldo_conta_diario;

alter table public.fonte_financeira
  drop constraint if exists fonte_financeira_saldo_adaptador_check;
alter table public.fonte_financeira
  add constraint fonte_financeira_saldo_adaptador_check check (
    saldo_adaptador = any (array[
      'nenhum', 'stone_extrato', 'bb', 'bb_rende_facil', 'inter',
      'bs_cash', 'venda_especie'
    ]::text[])
  );

-- Não altera uma configuração existente, nem cria conta em instalações
-- que ainda não tenham movimentos deste produto.
do $seed$
declare
  v_bb public.conta;
  v_id smallint;
begin
  if exists (select 1 from public.fonte_financeira where chave = 'bb_rende_facil')
     or not exists (select 1 from public.raw_bb
                    where lower(btrim(lancamento)) = 'bb rende fácil') then
    return;
  end if;
  if exists (select 1 from public.raw_bb
             where lower(btrim(lancamento)) = 'bb rende fácil'
               and data < date '2026-10-01') then
    raise exception 'Rende Fácil anterior ao início confirmado: revisar saldo-base.';
  end if;
  select c.* into v_bb
  from public.conta c join public.fonte_financeira f on f.conta_id = c.id
  where f.chave = 'bb' and f.saldo_adaptador = 'bb';
  if not found then
    raise exception 'Fonte BB canônica ausente; não é seguro vincular a aplicação.';
  end if;

  insert into public.conta (
    nome, banco, unidade_id, ativa, saldo_metodo, saldo_data_base, saldo_base
  ) values (
    'BB Rende Fácil', v_bb.banco, v_bb.unidade_id, true,
    'movimentos', date '2026-09-30', 0
  ) on conflict (nome) do nothing returning id into v_id;
  if v_id is null then
    raise exception 'Conta BB Rende Fácil já existe sem fonte; revisar vínculo.';
  end if;
  insert into public.fonte_financeira (
    chave, nome, conta_id, ativa, entra_faturamento, entra_caixa,
    entra_caixa_historico, entra_dre, saldo_adaptador, considerar_desde
  ) values (
    'bb_rende_facil', 'BB Rende Fácil (aplicações e resgates)', v_id, true,
    false, true, false, false, 'bb_rende_facil', date '2026-10-01'
  ) on conflict (chave) do nothing;
end;
$seed$;

create or replace view private.movimento_saldo_conta as
with cfg as (
  select
    public.unidade_principal_nome() as unidade,
    coalesce(
      (
        select c.fuso_horario
          from public.configuracao_operacional c
         where c.singleton
         limit 1
      ),
      current_setting('TimeZone')
    ) as fuso
)
select
  f.saldo_adaptador as adaptador,
  e.id::bigint as movimento_id,
  f.conta_id,
  e.data_hora::date as dia,
  e.data_hora as momento,
  e.valor,
  e.saldo_depois as saldo_reportado
from public.fonte_financeira f
cross join public.raw_stone_extrato e
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'stone_extrato'
  and f.conta_id is not null

union all

select
  f.saldo_adaptador,
  b.id::bigint,
  f.conta_id,
  b.data,
  b.data::timestamp,
  b.valor,
  null::numeric
from public.fonte_financeira f
cross join public.raw_bb b
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'bb'
  and f.conta_id is not null

union all

select
  f.saldo_adaptador,
  i.id::bigint,
  f.conta_id,
  i.data,
  i.data::timestamp,
  i.valor,
  null::numeric
from public.fonte_financeira f
cross join public.raw_inter i
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'inter'
  and f.conta_id is not null

union all

select
  f.saldo_adaptador,
  b.id::bigint,
  f.conta_id,
  b.data_hora::date,
  b.data_hora,
  b.valor,
  b.saldo
from public.fonte_financeira f
cross join public.raw_bs_cash b
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'bs_cash'
  and f.conta_id is not null

union all

select
  f.saldo_adaptador,
  v.id::bigint,
  f.conta_id,
  v.data,
  v.data::timestamp,
  v.valor,
  null::numeric
from public.fonte_financeira f
cross join cfg
join public.venda_especie v on v.unidade = cfg.unidade
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'venda_especie'
  and f.conta_id is not null

union all

select
  f.saldo_adaptador,
  v.id::bigint,
  f.conta_id,
  (v.depositada_em at time zone cfg.fuso)::date,
  v.depositada_em at time zone cfg.fuso,
  -v.valor,
  null::numeric
from public.fonte_financeira f
cross join cfg
join public.venda_especie v
  on v.unidade = cfg.unidade
 and v.depositada_em is not null
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'venda_especie'
  and f.conta_id is not null

union all

-- Cada movimento na conta corrente tem o sinal inverso na aplicação.
-- EXISTS evita multiplicar linhas caso fontes inativas compartilhem a conta.
select
  f.saldo_adaptador,
  b.id::bigint,
  f.conta_id,
  b.data,
  b.data::timestamp,
  -b.valor,
  null::numeric
from public.fonte_financeira f
cross join public.raw_bb b
where f.ativa and f.entra_caixa
  and f.saldo_adaptador = 'bb_rende_facil'
  and f.conta_id is not null
  and lower(btrim(b.lancamento)) = 'bb rende fácil'
  and (f.considerar_desde is null or b.data >= f.considerar_desde)
  and (f.encerrada_em is null or b.data <= f.encerrada_em)
  and exists (
    select 1 from public.fonte_financeira origem
    where origem.saldo_adaptador = 'bb' and origem.conta_id = b.conta_id
  );


-- Transferências automáticas não são despesa/receita operacional.
-- Altera só a prioridade de classificação desse tipo BB. Ajustes manuais
-- continuam com a precedência já existente no restante da view.
do $classification$
declare
  v_def text := pg_get_viewdef('public.fato_financeiro'::regclass, true);
  v_antigo constant text := 'WHEN lm.transf_propria THEN';
  v_novo constant text :=
    'WHEN (lm.transf_propria OR (lm.origem = ''bb'' AND lower(btrim(lm.tipo)) = ''bb rende fácil'')) THEN';
begin
  if position('bb rende fácil' in v_def) > 0 then
    return;
  end if;
  if (length(v_def) - length(replace(v_def, v_antigo, ''))) / length(v_antigo) <> 2 then
    raise exception 'Classificação financeira mudou; revisar regra Rende Fácil.';
  end if;
  execute 'create or replace view public.fato_financeiro as '
    || replace(v_def, v_antigo, v_novo);
end;
$classification$;

comment on view private.movimento_saldo_conta is
  'Movimentos/saldos por conta; bb_rende_facil usa a contrapartida assinada do extrato BB, sem estimar rendimentos.';
revoke all privileges on table private.movimento_saldo_conta
  from public, anon, authenticated;

create or replace function public.admin_salvar_fonte_financeira_com_vigencia(
  p_chave text,
  p_nome text,
  p_conta_id smallint,
  p_ativa boolean,
  p_entra_faturamento boolean,
  p_entra_caixa boolean,
  p_entra_caixa_historico boolean,
  p_entra_dre boolean,
  p_saldo_adaptador text,
  p_considerar_desde date,
  p_encerrada_em date
)
returns public.fonte_financeira
language plpgsql security definer
set search_path = pg_catalog, pg_temp
as $function$
declare
  v_anterior public.fonte_financeira;
  v public.fonte_financeira;
  v_adaptador text := coalesce(nullif(btrim(p_saldo_adaptador), ''), 'nenhum');
  v_dia date;
begin
  if not public.usuario_tem_papel(array['admin']::text[]) then
    raise exception using errcode = '42501', message = 'Apenas administradores.';
  end if;
  if btrim(coalesce(p_nome, '')) = '' then
    raise exception using errcode = '22023', message = 'Nome da fonte obrigatório.';
  end if;
  if v_adaptador <> all (
    array['nenhum', 'stone_extrato', 'bb', 'bb_rende_facil', 'inter', 'bs_cash', 'venda_especie']::text[]
  ) then
    raise exception using errcode = '22023', message = 'Adaptador de saldo inválido.';
  end if;
  if p_encerrada_em is not null
     and p_considerar_desde is not null
     and p_encerrada_em < p_considerar_desde then
    raise exception using errcode = '22023',
      message = 'A data de encerramento não pode ser anterior ao início da vigência.';
  end if;

  select * into v_anterior
  from public.fonte_financeira f
  where f.chave = p_chave
  for update;

  if not found then
    raise exception using errcode = '22023', message = 'Fonte desconhecida.';
  end if;

  if p_conta_id is not null and not exists (
    select 1 from public.conta c where c.id = p_conta_id and c.ativa
  ) then
    raise exception using errcode = '22023',
      message = 'Conta padrão inválida ou inativa.';
  end if;

  if coalesce(p_ativa, true) and coalesce(p_entra_caixa, false) then
    if p_conta_id is null or v_adaptador = 'nenhum' then
      raise exception using errcode = '22023',
        message = 'Fonte ativa do caixa exige conta e adaptador de saldo.';
    end if;
    if not exists (
      select 1 from public.conta c
      where c.id = p_conta_id and c.ativa and c.saldo_metodo <> 'ignorar'
    ) then
      raise exception using errcode = '22023',
        message = 'A conta escolhida precisa ter cálculo de saldo ativo.';
    end if;
    if exists (
      select 1 from public.fonte_financeira f
      where f.chave <> p_chave
        and f.ativa and f.entra_caixa and f.saldo_adaptador = v_adaptador
    ) then
      raise exception using errcode = '22023',
        message = 'Este adaptador já alimenta outra fonte ativa do caixa.';
    end if;
  end if;

  update public.fonte_financeira f
     set nome = btrim(p_nome),
         conta_id = p_conta_id,
         ativa = coalesce(p_ativa, true),
         entra_faturamento = coalesce(p_entra_faturamento, false),
         entra_caixa = coalesce(p_entra_caixa, false),
         entra_caixa_historico = coalesce(p_entra_caixa_historico, false),
         entra_dre = coalesce(p_entra_dre, false),
         saldo_adaptador = v_adaptador,
         considerar_desde = p_considerar_desde,
         encerrada_em = p_encerrada_em,
         atualizado_por = auth.uid(),
         atualizado_em = now()
   where f.chave = p_chave
   returning * into v;

  perform private.validar_configuracao_saldo();

  if to_jsonb(v_anterior) is distinct from to_jsonb(v) then
    insert into private.fonte_financeira_historico (
      chave, configuracao_anterior, configuracao_nova, alterado_por
    ) values (
      v.chave, to_jsonb(v_anterior), to_jsonb(v), auth.uid()
    );

    select coalesce(c.dia, current_date) into v_dia
    from public.corte_caixa c limit 1;
    perform private.agendar_refresh_painel(
      coalesce(v_dia, current_date), coalesce(v_dia, current_date)
    );
  end if;

  return v;
end;
$function$;

-- A função já existia: preservar o gate admin e o mesmo grant mínimo.
revoke all privileges on function public.admin_salvar_fonte_financeira_com_vigencia(
  text, text, smallint, boolean, boolean, boolean, boolean, boolean, text, date, date
) from public, anon, authenticated;
grant execute on function public.admin_salvar_fonte_financeira_com_vigencia(
  text, text, smallint, boolean, boolean, boolean, boolean, boolean, text, date, date
) to authenticated;

refresh materialized view private.mv_saldo_conta_diario;
select private.validar_saldo_diario_materializado();

do $validate$
begin
  -- Nenhuma conta que já existia pode mudar, nem no histórico.
  if exists (
    (select s.dia,s.conta_id,s.saldo from private.mv_saldo_conta_diario s
      where exists (select 1 from bb_rende_saldos_antes a where a.conta_id=s.conta_id)
     except all select * from bb_rende_saldos_antes)
    union all
    (select * from bb_rende_saldos_antes
     except all select s.dia,s.conta_id,s.saldo from private.mv_saldo_conta_diario s)
  ) then
    raise exception 'Rende Fácil alterou o saldo de outra conta.';
  end if;
  if exists (select 1 from private.mv_saldo_conta_diario s
             join public.fonte_financeira f on f.conta_id=s.conta_id
             where f.saldo_adaptador='bb_rende_facil' and s.saldo < 0) then
    raise exception 'Resgates Rende Fácil excedem o saldo: conferir cobertura.';
  end if;
  if exists (select 1 from public.fato_financeiro f
             where f.origem='bb' and lower(btrim(f.tipo))='bb rende fácil'
               and f.entra_dre) then
    raise exception 'Movimento Rende Fácil ainda entra na DRE; revisar ajuste manual.';
  end if;
end;
$validate$;

commit;
