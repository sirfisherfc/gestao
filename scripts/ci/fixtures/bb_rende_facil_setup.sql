-- Dados inteiramente sintéticos. Dependências de outros módulos são stubs;
-- o adaptador e o snapshot de saldo vêm das migrations reais.
create schema if not exists public;
create schema if not exists private;
create schema if not exists auth;
do $roles$ begin
  if not exists(select 1 from pg_roles where rolname='anon') then create role anon; end if;
  if not exists(select 1 from pg_roles where rolname='authenticated') then create role authenticated; end if;
end; $roles$;
create or replace function auth.uid() returns uuid language sql as 'select null::uuid';
create table public.conta (
  id smallserial primary key, nome text unique, banco text, unidade_id smallint,
  ativa boolean, saldo_metodo text, saldo_data_base date, saldo_base numeric
);
create table public.fonte_financeira (
  chave text primary key,nome text,conta_id smallint,ativa boolean,
  entra_faturamento boolean,entra_caixa boolean,entra_caixa_historico boolean,
  entra_dre boolean,saldo_adaptador text,considerar_desde date,encerrada_em date,
  atualizado_por uuid,atualizado_em timestamptz
);
create table public.configuracao_operacional (singleton boolean,fuso_horario text);
insert into public.configuracao_operacional values(true,'America/Fortaleza');
create table public.corte_caixa (dia date);
insert into public.corte_caixa values('2026-10-08');
create table public.raw_bb (id bigint primary key,conta_id smallint,data date,lancamento text,valor numeric);
create table public.raw_inter (id bigint,data date,valor numeric);
create table public.raw_stone_extrato (id bigint,data_hora timestamp,valor numeric,saldo_depois numeric);
create table public.raw_bs_cash (id bigint,data_hora timestamp,valor numeric,saldo numeric);
create table public.venda_especie (id bigint,unidade text,data date,valor numeric,depositada_em timestamptz);
create table private.fonte_financeira_historico (
  chave text,configuracao_anterior jsonb,configuracao_nova jsonb,alterado_por uuid
);
create function public.unidade_principal_nome() returns text language sql as 'select ''TEST''::text';
create function public.usuario_tem_papel(text[]) returns boolean language sql as 'select false';
create function private.agendar_refresh_painel(date,date) returns void language sql as 'select';
create function private.validar_configuracao_saldo() returns void language sql as 'select';
create function private.validar_saldo_diario_materializado() returns void language sql as 'select';
insert into public.conta(nome,banco,unidade_id,ativa,saldo_metodo,saldo_data_base,saldo_base)
values ('BB','BB',1,true,'movimentos','2026-09-30',1000),
       ('Outra conta','Outro',1,true,'ignorar','2026-09-30',0);
insert into public.fonte_financeira(chave,nome,conta_id,ativa,entra_caixa,saldo_adaptador)
values('bb','BB',1,true,true,'bb');
insert into public.raw_bb values
  (1,1,'2026-09-30','Pix-Envio',-5),
  (2,1,'2026-10-05','BB Rende Fácil',-100),
  (3,1,'2026-10-06','BB Rende Fácil',40),
  (4,1,'2026-10-07','Pix-Envio',-10),
  (5,1,'2026-10-07','Aplicação Fundo BB',-20),
  (6,2,'2026-10-07','BB Rende Fácil',-900);
-- As duas prioridades são as mesmas que a migration altera em produção.
create view public.fato_financeiro as
with live_match as (
  select 'bb'::text origem,id raw_id,lancamento tipo,valor,false transf_propria
  from public.raw_bb
), classified as (
  select lm.*,
    case WHEN lm.transf_propria THEN 'Transferencia entre Contas'::text else 'Despesa'::text end categoria,
    case WHEN lm.transf_propria THEN 'classificado'::text else 'excecao'::text end status
  from live_match lm
)
select origem,raw_id,tipo,valor,categoria,status,categoria <> 'Transferencia entre Contas' entra_dre
from classified;
