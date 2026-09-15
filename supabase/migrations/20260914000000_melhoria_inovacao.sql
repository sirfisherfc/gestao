-- Rotina "Melhoria e Inovacao": um lugar unico para registrar uma ideia ou um
-- problema, dar responsavel e prazo, acompanhar e fechar com resultado.
--
-- A regra de projeto aqui e a simplicidade: tres tabelas, nenhuma matriz de
-- pontuacao, nenhuma etapa de aprovacao. Cadastrar deve custar um titulo.
-- Todo o resto (responsavel, prazo, prioridade, proxima acao) e preenchido
-- depois, quando alguem de fato assumir a ideia.
--
-- Estrutura:
--   melhorias            - a ideia/problema e todo o seu acompanhamento;
--   melhoria_evidencias  - links (ou caminho de storage) anexados a uma ideia;
--   melhoria_historico   - linha do tempo de status, alimentada por trigger.
--
-- Seguranca: as tabelas ficam com RLS ligado e sem grant para authenticated.
-- A pagina le pelas views app_melhoria* e escreve pelas RPCs security definer,
-- todas com o mesmo gate configuravel de pagina_permissao. Nenhuma view toca
-- auth.users diretamente: o nome de quem aparece vem de
-- private.nome_exibicao_usuario(uuid).

begin;

-- ---------------------------------------------------------------------------
-- Tabelas
-- ---------------------------------------------------------------------------

create table if not exists public.melhorias (
  id bigint generated always as identity primary key,
  titulo text not null check (length(btrim(titulo)) between 3 and 160),
  descricao text,
  area text not null default 'Geral'
    check (length(btrim(area)) between 2 and 60),
  origem text not null default 'Equipe'
    check (origem in ('Equipe', 'Cliente', 'Fornecedor', 'Auditoria', 'Gestão', 'Outra')),
  status text not null default 'Recebida'
    check (status in ('Recebida', 'Em avaliação', 'Em andamento', 'Concluída', 'Descartada')),
  prioridade text not null default 'Média'
    check (prioridade in ('Baixa', 'Média', 'Alta')),
  responsavel_id uuid references auth.users(id) on delete set null,
  primeira_manifestacao_em date not null default current_date,
  prazo date,
  proxima_acao text,
  concluida_em date,
  resultado_aprendizado text,
  impacto_financeiro numeric(12,2),
  motivo_descarte text,
  criado_por uuid references auth.users(id) on delete set null,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  referencia_origem text,
  -- Chave natural usada apenas pela carga historica. Mantem a carga
  -- re-executavel sem duplicar registro; ideia cadastrada pela pagina fica
  -- com null e nao sofre restricao.
  chave_carga text unique
);

comment on table public.melhorias is
  'Ideias e problemas de melhoria/inovacao, do registro ate a conclusao ou o descarte.';
comment on column public.melhorias.primeira_manifestacao_em is
  'Quando a ideia ou o problema apareceu pela primeira vez. Pode ser anterior ao cadastro.';
comment on column public.melhorias.resultado_aprendizado is
  'Campo unico de fechamento: o que mudou e o que se aprendeu. Nao ha indicador antes/depois obrigatorio.';
comment on column public.melhorias.referencia_origem is
  'De onde veio o registro (reuniao, grupo, auditoria). Nao guarda nome, telefone nem conteudo pessoal.';
comment on column public.melhorias.chave_carga is
  'Identificador estavel da carga historica. Nulo para as ideias cadastradas pela pagina.';

create table if not exists public.melhoria_evidencias (
  id bigint generated always as identity primary key,
  melhoria_id bigint not null
    references public.melhorias(id) on delete cascade,
  titulo text not null check (length(btrim(titulo)) between 2 and 120),
  url text,
  storage_path text,
  criado_por uuid references auth.users(id) on delete set null,
  criado_em timestamptz not null default now(),
  constraint melhoria_evidencias_destino check (
    (url is null) <> (storage_path is null)
  )
);

comment on table public.melhoria_evidencias is
  'Evidencias de uma melhoria: um link externo (url) ou um arquivo no bucket melhoria-evidencias (storage_path). Exatamente um dos dois.';

create table if not exists public.melhoria_historico (
  id bigint generated always as identity primary key,
  melhoria_id bigint not null
    references public.melhorias(id) on delete cascade,
  status_anterior text,
  status_novo text not null,
  usuario_id uuid references auth.users(id) on delete set null,
  criado_em timestamptz not null default now(),
  observacao text
);

comment on table public.melhoria_historico is
  'Linha do tempo de status, alimentada por trigger. Nao tem tela propria: aparece dentro do detalhe da ideia.';

create index if not exists melhorias_status_idx
  on public.melhorias (status, prioridade, criado_em desc);
create index if not exists melhorias_prazo_idx
  on public.melhorias (prazo) where prazo is not null;
create index if not exists melhoria_evidencias_melhoria_idx
  on public.melhoria_evidencias (melhoria_id, criado_em);
create index if not exists melhoria_historico_melhoria_idx
  on public.melhoria_historico (melhoria_id, criado_em);

alter table public.melhorias enable row level security;
alter table public.melhoria_evidencias enable row level security;
alter table public.melhoria_historico enable row level security;
revoke all privileges on public.melhorias from public, anon, authenticated;
revoke all privileges on public.melhoria_evidencias from public, anon, authenticated;
revoke all privileges on public.melhoria_historico from public, anon, authenticated;

-- ---------------------------------------------------------------------------
-- Historico automatico
-- ---------------------------------------------------------------------------

create or replace function public.melhoria_registra_historico()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_observacao text;
begin
  if tg_op = 'INSERT' then
    insert into public.melhoria_historico
      (melhoria_id, status_anterior, status_novo, usuario_id, criado_em, observacao)
    values (new.id, null, new.status, new.criado_por, new.criado_em, 'Registro criado');
    return new;
  end if;

  if new.status is distinct from old.status then
    v_observacao := case
      when new.status = 'Descartada' then new.motivo_descarte
      when new.status = 'Concluída' then new.resultado_aprendizado
      else new.proxima_acao
    end;

    insert into public.melhoria_historico
      (melhoria_id, status_anterior, status_novo, usuario_id, observacao)
    values (new.id, old.status, new.status, auth.uid(),
            nullif(left(btrim(coalesce(v_observacao, '')), 280), ''));
  end if;

  return new;
end;
$function$;

drop trigger if exists melhorias_historico_ins on public.melhorias;
create trigger melhorias_historico_ins
  after insert on public.melhorias
  for each row execute function public.melhoria_registra_historico();

drop trigger if exists melhorias_historico_upd on public.melhorias;
create trigger melhorias_historico_upd
  after update on public.melhorias
  for each row execute function public.melhoria_registra_historico();

-- ---------------------------------------------------------------------------
-- Leitura
-- ---------------------------------------------------------------------------

create or replace view public.app_melhorias
with (security_barrier = true, security_invoker = false) as
select
  m.id,
  m.titulo,
  m.descricao,
  m.area,
  m.origem,
  m.status,
  m.prioridade,
  m.responsavel_id,
  private.nome_exibicao_usuario(m.responsavel_id) as responsavel_nome,
  m.primeira_manifestacao_em,
  m.prazo,
  m.proxima_acao,
  m.concluida_em,
  m.resultado_aprendizado,
  m.impacto_financeiro,
  m.motivo_descarte,
  m.referencia_origem,
  private.nome_exibicao_usuario(m.criado_por) as criado_por_nome,
  m.criado_em,
  m.atualizado_em,
  (m.prazo is not null
    and m.prazo < current_date
    and m.status not in ('Concluída', 'Descartada')) as vencida,
  case
    when m.status = 'Concluída' and m.concluida_em is not null
      then (m.concluida_em - m.primeira_manifestacao_em)
  end as dias_ate_conclusao,
  case
    when m.status = 'Concluída' and m.concluida_em is not null and m.prazo is not null
      then m.concluida_em <= m.prazo
  end as concluida_no_prazo,
  (select count(*) from public.melhoria_evidencias e where e.melhoria_id = m.id)
    as evidencias
from public.melhorias m
where public.usuario_pode_acessar_pagina('melhoria_inovacao.html');

create or replace view public.app_melhoria_evidencias
with (security_barrier = true, security_invoker = false) as
select
  e.id,
  e.melhoria_id,
  e.titulo,
  e.url,
  e.storage_path,
  private.nome_exibicao_usuario(e.criado_por) as criado_por_nome,
  e.criado_em
from public.melhoria_evidencias e
where public.usuario_pode_acessar_pagina('melhoria_inovacao.html');

create or replace view public.app_melhoria_historico
with (security_barrier = true, security_invoker = false) as
select
  h.id,
  h.melhoria_id,
  h.status_anterior,
  h.status_novo,
  private.nome_exibicao_usuario(h.usuario_id) as usuario_nome,
  h.criado_em,
  h.observacao
from public.melhoria_historico h
where public.usuario_pode_acessar_pagina('melhoria_inovacao.html');

-- Lista de quem pode ser responsavel. Sai de perfil_usuario (papel ativo) e o
-- nome vem da funcao privada, para nao expor auth.users na Data API.
create or replace view public.app_melhoria_responsaveis
with (security_barrier = true, security_invoker = false) as
select
  p.user_id,
  coalesce(private.nome_exibicao_usuario(p.user_id), 'Conta sem nome') as nome,
  p.papel
from public.perfil_usuario p
where p.ativo
  and public.usuario_pode_acessar_pagina('melhoria_inovacao.html');

-- ---------------------------------------------------------------------------
-- Escrita
-- ---------------------------------------------------------------------------

-- Cadastro rapido: so o titulo e obrigatorio. Data e autor entram sozinhos.
create or replace function public.criar_melhoria(
  p_titulo text,
  p_descricao text default null,
  p_area text default 'Geral',
  p_origem text default 'Equipe'
)
returns bigint
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_id bigint;
begin
  if not public.usuario_pode_acessar_pagina('melhoria_inovacao.html') then
    raise exception 'Sem permissao para registrar melhorias.';
  end if;

  insert into public.melhorias
    (titulo, descricao, area, origem, criado_por)
  values (
    btrim(p_titulo),
    nullif(btrim(coalesce(p_descricao, '')), ''),
    coalesce(nullif(btrim(coalesce(p_area, '')), ''), 'Geral'),
    coalesce(nullif(btrim(coalesce(p_origem, '')), ''), 'Equipe'),
    auth.uid()
  )
  returning id into v_id;

  return v_id;
end;
$function$;

-- Acompanhamento. Um unico ponto de escrita para status, responsavel, prazo,
-- prioridade, proxima acao e os campos de fechamento.
create or replace function public.atualizar_melhoria(
  p_id bigint,
  p_status text,
  p_prioridade text,
  p_responsavel_id uuid default null,
  p_prazo date default null,
  p_proxima_acao text default null,
  p_resultado_aprendizado text default null,
  p_impacto_financeiro numeric default null,
  p_motivo_descarte text default null
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_resultado text := nullif(btrim(coalesce(p_resultado_aprendizado, '')), '');
  v_motivo text := nullif(btrim(coalesce(p_motivo_descarte, '')), '');
begin
  if not public.usuario_pode_acessar_pagina('melhoria_inovacao.html') then
    raise exception 'Sem permissao para editar melhorias.';
  end if;

  if p_status = 'Descartada' and v_motivo is null then
    raise exception 'Informe um motivo curto para descartar a ideia.';
  end if;
  if p_status = 'Concluída' and v_resultado is null then
    raise exception 'Informe o resultado e o aprendizado para concluir a ideia.';
  end if;

  update public.melhorias set
    status = p_status,
    prioridade = p_prioridade,
    responsavel_id = p_responsavel_id,
    prazo = p_prazo,
    proxima_acao = nullif(btrim(coalesce(p_proxima_acao, '')), ''),
    resultado_aprendizado = case when p_status = 'Concluída' then v_resultado else resultado_aprendizado end,
    impacto_financeiro = case when p_status = 'Concluída' then p_impacto_financeiro else impacto_financeiro end,
    motivo_descarte = case when p_status = 'Descartada' then v_motivo else motivo_descarte end,
    concluida_em = case
      when p_status = 'Concluída' then coalesce(concluida_em, current_date)
      else null
    end,
    atualizado_em = now()
  where id = p_id;

  if not found then
    raise exception 'Melhoria % nao encontrada.', p_id;
  end if;
end;
$function$;

-- Troca de status direto na lista. Concluir e descartar continuam exigindo o
-- texto curto, entao a pagina abre o detalhe nesses dois casos.
create or replace function public.alterar_status_melhoria(
  p_id bigint,
  p_status text
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if not public.usuario_pode_acessar_pagina('melhoria_inovacao.html') then
    raise exception 'Sem permissao para editar melhorias.';
  end if;

  if p_status in ('Concluída', 'Descartada') then
    raise exception 'Concluir ou descartar exige abrir a ideia e registrar o texto correspondente.';
  end if;

  update public.melhorias set
    status = p_status,
    concluida_em = null,
    atualizado_em = now()
  where id = p_id;

  if not found then
    raise exception 'Melhoria % nao encontrada.', p_id;
  end if;
end;
$function$;

-- Evidencia e um link externo OU um arquivo no bucket. Quem envia arquivo sobe
-- primeiro para o Storage e passa o caminho aqui: a linha so existe se o objeto
-- ja estiver la, e nao ha caminho apontando para fora do bucket da rotina.
drop function if exists public.salvar_melhoria_evidencia(bigint, text, text);

create or replace function public.salvar_melhoria_evidencia(
  p_melhoria_id bigint,
  p_titulo text,
  p_url text default null,
  p_storage_path text default null
)
returns bigint
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_url text := nullif(btrim(coalesce(p_url, '')), '');
  v_path text := nullif(btrim(coalesce(p_storage_path, '')), '');
  v_id bigint;
begin
  if not public.usuario_pode_acessar_pagina('melhoria_inovacao.html') then
    raise exception 'Sem permissao para anexar evidencias.';
  end if;

  if (v_url is null) = (v_path is null) then
    raise exception 'Informe um link ou um arquivo, nao os dois.';
  end if;

  if v_url is not null and v_url !~* '^https?://' then
    raise exception 'O link da evidencia precisa comecar com http ou https.';
  end if;

  -- O caminho e sempre melhoria/<id>/<arquivo>: barra o envio de um arquivo
  -- para dentro da pasta de outra ideia e o uso de .. para subir de nivel.
  if v_path is not null
     and (v_path <> format('melhoria/%s/%s', p_melhoria_id, split_part(v_path, '/', 3))
          or split_part(v_path, '/', 3) = ''
          or v_path like '%..%') then
    raise exception 'Caminho de arquivo invalido para esta melhoria.';
  end if;

  insert into public.melhoria_evidencias
    (melhoria_id, titulo, url, storage_path, criado_por)
  values (p_melhoria_id, btrim(p_titulo), v_url, v_path, auth.uid())
  returning id into v_id;

  return v_id;
end;
$function$;

-- Devolve o caminho no Storage (ou null, se for link) para a pagina apagar o
-- objeto logo depois. Sem isso o arquivo ficaria orfao no bucket.
drop function if exists public.excluir_melhoria_evidencia(bigint);

create or replace function public.excluir_melhoria_evidencia(p_id bigint)
returns text
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
declare
  v_path text;
begin
  if not public.usuario_pode_acessar_pagina('melhoria_inovacao.html') then
    raise exception 'Sem permissao para remover evidencias.';
  end if;

  delete from public.melhoria_evidencias where id = p_id
  returning storage_path into v_path;

  return v_path;
end;
$function$;

-- ---------------------------------------------------------------------------
-- Bucket das evidencias em arquivo
-- ---------------------------------------------------------------------------

-- Bucket privado: nada e servido por URL publica, so por link assinado gerado
-- na hora para quem ja passou pelo gate da pagina. O bloco e condicional
-- porque o schema storage so existe no Supabase; num Postgres puro (a
-- verificacao de migrations em banco descartavel) a rotina segue funcionando
-- com evidencia em link.
do $migration$
begin
  if to_regclass('storage.buckets') is null then
    raise notice 'Schema storage ausente: bucket de evidencias nao criado.';
    return;
  end if;

  insert into storage.buckets (id, name, public, file_size_limit)
  values ('melhoria-evidencias', 'melhoria-evidencias', false, 10485760)
  on conflict (id) do update
    set public = false,
        file_size_limit = 10485760;

  if to_regclass('storage.objects') is null then
    return;
  end if;

  -- Mesmo gate da pagina, agora no objeto. Sem update: evidencia se substitui
  -- removendo e enviando de novo, o que mantem o historico honesto.
  execute $policy$drop policy if exists melhoria_evidencia_ler on storage.objects$policy$;
  execute $policy$
    create policy melhoria_evidencia_ler
      on storage.objects
      for select
      to authenticated
      using (
        bucket_id = 'melhoria-evidencias'
        and public.usuario_pode_acessar_pagina('melhoria_inovacao.html')
      )
  $policy$;

  execute $policy$drop policy if exists melhoria_evidencia_enviar on storage.objects$policy$;
  execute $policy$
    create policy melhoria_evidencia_enviar
      on storage.objects
      for insert
      to authenticated
      with check (
        bucket_id = 'melhoria-evidencias'
        and public.usuario_pode_acessar_pagina('melhoria_inovacao.html')
        and name like 'melhoria/%'
      )
  $policy$;

  execute $policy$drop policy if exists melhoria_evidencia_remover on storage.objects$policy$;
  execute $policy$
    create policy melhoria_evidencia_remover
      on storage.objects
      for delete
      to authenticated
      using (
        bucket_id = 'melhoria-evidencias'
        and public.usuario_pode_acessar_pagina('melhoria_inovacao.html')
      )
  $policy$;
end;
$migration$;

-- ---------------------------------------------------------------------------
-- Permissoes
-- ---------------------------------------------------------------------------

revoke all privileges on public.app_melhorias from public, anon, authenticated;
revoke all privileges on public.app_melhoria_evidencias from public, anon, authenticated;
revoke all privileges on public.app_melhoria_historico from public, anon, authenticated;
revoke all privileges on public.app_melhoria_responsaveis from public, anon, authenticated;
grant select on public.app_melhorias to authenticated;
grant select on public.app_melhoria_evidencias to authenticated;
grant select on public.app_melhoria_historico to authenticated;
grant select on public.app_melhoria_responsaveis to authenticated;

revoke all privileges on function public.melhoria_registra_historico() from public, anon, authenticated;
revoke all privileges on function public.criar_melhoria(text, text, text, text) from public, anon, authenticated;
revoke all privileges on function public.atualizar_melhoria(bigint, text, text, uuid, date, text, text, numeric, text) from public, anon, authenticated;
revoke all privileges on function public.alterar_status_melhoria(bigint, text) from public, anon, authenticated;
revoke all privileges on function public.salvar_melhoria_evidencia(bigint, text, text, text) from public, anon, authenticated;
revoke all privileges on function public.excluir_melhoria_evidencia(bigint) from public, anon, authenticated;
grant execute on function public.criar_melhoria(text, text, text, text) to authenticated;
grant execute on function public.atualizar_melhoria(bigint, text, text, uuid, date, text, text, numeric, text) to authenticated;
grant execute on function public.alterar_status_melhoria(bigint, text) to authenticated;
grant execute on function public.salvar_melhoria_evidencia(bigint, text, text, text) to authenticated;
grant execute on function public.excluir_melhoria_evidencia(bigint) to authenticated;

-- Quem enxerga a pagina pode sugerir e acompanhar. Socio e gerente entram
-- liberados; o ajuste fino continua em permissoes.html, sem migration nova.
insert into public.pagina_permissao (pagina, papeis)
values ('melhoria_inovacao.html', array['socio', 'gerente']::text[])
on conflict (pagina) do nothing;

commit;
