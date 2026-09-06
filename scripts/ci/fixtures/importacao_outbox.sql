-- SOMENTE banco vazio e descartavel. Dados sinteticos. Nunca usar em producao.
do $$ begin
  if exists (select 1 from pg_namespace where nspname in ('private','cron'))
     or to_regclass('public.raw_stone_extrato') is not null then
    raise exception 'Fixture exige banco vazio; nenhum objeto foi alterado.';
  end if;
end $$;
create role anon;
create role authenticated;
create role service_role;
create schema private;
create schema cron;

-- Contrato de metadados do cron; nenhum daemon ou agendamento real.
create table cron.job (
  jobid bigint generated always as identity primary key,
  jobname text, schedule text, command text,
  username text default current_user, active boolean default true,
  unique(jobname,username)
);
create function cron.schedule(job_name text, schedule text, command text)
returns bigint language sql as $$
  insert into cron.job(jobname,schedule,command) values ($1,$2,$3)
  on conflict(jobname,username) do update
    set schedule=excluded.schedule, command=excluded.command
  returning jobid;
$$;
create function cron.alter_job(job_id bigint, active boolean default null)
returns void language sql as $$update cron.job set active=$2 where jobid=$1;$$;
create function cron.unschedule(job_id bigint) returns boolean language plpgsql as $$
begin delete from cron.job where jobid=$1; return found; end;
$$;
create function public.solicitar_recalculo_saldo(date,date) returns jsonb
language sql as $$select '{}'::jsonb;$$;
create function public.usuario_pode_acessar_pagina(text) returns boolean
language sql as $$select coalesce(current_setting('test.import_allowed',true),'on')='on';$$;
create table public.conta(id smallint primary key,nome text);
insert into public.conta values(1,'Conta sintetica');
create table public.fonte_financeira(chave text, conta_id smallint, ativa boolean);
insert into public.fonte_financeira values('stone_extrato',1,true);
create table public.log_carga(fontes text);
create table private.refresh_test(chamadas integer not null);
insert into private.refresh_test values(0);
create function public.recalcular_saldo_fechamento(date,date,integer)
returns table(mensagem text) language sql as $$select 'Teste sintetico'::text;$$;
create function public.refresh_painel() returns void language plpgsql as $$
begin
  if current_setting('test.fail_refresh',true)='on' then raise exception 'Falha sintetica'; end if;
  update private.refresh_test set chamadas=chamadas+1;
end;
$$;

-- TESTES APOS INSTALAR A CADEIA
create function private.linha_teste(dia text, horario text default '12:00')
returns jsonb language sql as $$
select jsonb_build_array(jsonb_build_object('Data',dia,'Horário',horario,
  'Movimentação','Teste sintetico','Valor','1,00','Saldo antes','0,00','Saldo depois','1,00'));
$$;

do $$ declare r jsonb; body text; begin
  assert (select count(*)=1 from cron.job), 'Idempotencia criou jobs duplicados';
  assert (select active from cron.job), 'Watchdog desativado';
  assert not has_function_privilege('authenticated','private.garantir_worker_recalculo_saldo()','execute'), 'Watchdog exposto';
  assert not has_function_privilege('anon','private.garantir_worker_recalculo_saldo()','execute'), 'Watchdog anon';
  assert not has_function_privilege('service_role','private.garantir_worker_recalculo_saldo()','execute'), 'Watchdog service_role';
  assert has_function_privilege('authenticated','public.importar_csv_stone(text,jsonb,boolean)','execute'), 'Grant da RPC perdido';
  assert not has_table_privilege('authenticated','private.fila_recalculo_saldo','select'), 'Fila exposta';
  body:=pg_get_functiondef('public.importar_csv_stone(text,jsonb,boolean)'::regprocedure);
  assert position('public.usuario_pode_acessar_pagina' in body)>0, 'Gate perdido';
  assert position('from public.fonte_financeira f' in body)>0, 'Configuracao de fontes perdida';
  assert position('public.stone_conta e' in body)>0, 'Configuracao Stone perdida';
  assert position('perform public.refresh_painel' in body)=0, 'Refresh dentro da importacao';
  assert position('cron.schedule' in body)=0, 'Produtor depende do agendamento';

  r:=public.importar_csv_stone('stone_extrato',private.linha_teste('01/09/2026'),true);
  assert (r->>'novas')::integer=1, 'Dry-run incorreto';
  assert (select count(*)=0 from public.raw_stone_extrato), 'Dry-run gravou raw';
  assert (select count(*)=0 from private.fila_recalculo_saldo), 'Dry-run enfileirou';
  assert (select count(*)=0 from public.log_carga), 'Dry-run gravou log';
  r:=public.importar_csv_stone('stone_extrato',private.linha_teste('01/09/2026'),false);
  assert (r->>'inseridos')::integer=1 and r->>'recalculo_id' is not null, 'Importacao sem tarefa';
  assert exists(select 1 from private.fila_recalculo_saldo where id=(r->>'recalculo_id')::bigint and data_min='2026-09-01' and data_max='2026-09-01'), 'Periodo da tarefa incorreto';
  assert (select chamadas=0 from private.refresh_test), 'Importacao executou refresh';
  r:=public.importar_csv_stone('stone_extrato',private.linha_teste('01/09/2026'),false);
  assert (r->>'inseridos')::integer=0 and r ? 'recalculo_id' and r->>'recalculo_id' is null, 'Duplicado enfileirou';
  assert (select count(*)=1 from private.fila_recalculo_saldo), 'Duplicado alterou tarefa antiga';
  r:=public.importar_csv_stone('stone_extrato',private.linha_teste('01/09/2026')||private.linha_teste('03/09/2026'),false);
  assert (r->>'inseridos')::integer=1 and r->>'recalculo_inicio'='2026-09-03', 'Periodo inclui duplicados';
  assert (select count(*)=2 from private.fila_recalculo_saldo), 'Lote nao tem tarefa propria';
end $$;

-- Erro na fila reverte raw e log; arquivo anterior permanece duravel.
create function private.falhar_fila_teste() returns trigger language plpgsql as $$
begin raise exception 'Falha sintetica ao enfileirar'; end; $$;
create trigger teste_falha before insert on private.fila_recalculo_saldo
for each row execute function private.falhar_fila_teste();
do $$ declare falhou boolean:=false; logs bigint; begin
  select count(*) into logs from public.log_carga;
  begin
    perform public.importar_csv_stone('stone_extrato',private.linha_teste('04/09/2026'),false);
  exception when raise_exception then falhou:=true;
  end;
  assert falhou, 'Falha da fila nao abortou';
  assert (select count(*)=2 from public.raw_stone_extrato), 'Raw nao reverteu';
  assert (select count(*)=logs from public.log_carga), 'Log nao reverteu';
  assert (select count(*)=2 from private.fila_recalculo_saldo), 'Tarefas anteriores perdidas';
end $$;
drop trigger teste_falha on private.fila_recalculo_saldo;

do $$ declare falhou boolean:=false; begin
  perform set_config('test.import_allowed','off',true);
  begin
    perform public.importar_csv_stone('stone_extrato',private.linha_teste('04/09/2026'),false);
  exception when insufficient_privilege then falhou:=true;
  end;
  assert falhou, 'Gate da importacao nao foi preservado';
  assert (select count(*)=2 from private.fila_recalculo_saldo), 'Acesso negado enfileirou';
end $$;

-- Simula tarefa sem job, reativacao e drenagem pelo worker vigente real.
do $$ begin
  perform private.garantir_worker_recalculo_saldo();
  assert (select count(*)=2 from cron.job), 'Watchdog nao armou worker';
  update cron.job set active=false where jobname='sirfisher-processar-recalculo-saldo';
  perform private.garantir_worker_recalculo_saldo();
  assert (select active from cron.job where jobname='sirfisher-processar-recalculo-saldo'), 'Worker nao reativado';
  perform private.processar_fila_recalculo_saldo();
  assert (select count(*)=1 from private.fila_recalculo_saldo where situacao='pendente'), 'Worker perdeu tarefa seguinte';
  perform private.processar_fila_recalculo_saldo();
  assert (select count(*)=2 from private.fila_recalculo_saldo where situacao='concluido'), 'Conclusao nao ficou consultavel';
  assert (select count(*)=1 from cron.job), 'Worker nao desagendou';
  perform private.garantir_worker_recalculo_saldo();
  assert (select count(*)=1 from cron.job), 'Fila vazia armou worker';
  -- Produtor comita, mas agendamento foi perdido/desativado: recuperar.
  insert into private.fila_recalculo_saldo(data_min,data_max) values('2026-09-04','2026-09-04');
  perform private.garantir_worker_recalculo_saldo();
  assert (select count(*)=2 from cron.job), 'Pendencia nova ficou sem job';
  perform set_config('test.fail_refresh','on',true);
  perform private.processar_fila_recalculo_saldo();
  assert (select count(*)=1 from private.fila_recalculo_saldo where situacao='erro'), 'Erro do worker oculto';
  perform private.garantir_worker_recalculo_saldo();
  assert (select count(*)=1 from cron.job), 'Watchdog retentou erro terminal';
end $$;
