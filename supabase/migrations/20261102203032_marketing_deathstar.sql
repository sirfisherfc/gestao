-- Historico privado e revisao editorial; reservas e atendimento preservados.
begin;
create schema if not exists marketing_private;
revoke all on schema marketing_private from public, anon, authenticated;
create table if not exists marketing_private.settings (
  singleton boolean primary key default true check (singleton),
  owner_id uuid references auth.users(id)
);
insert into marketing_private.settings(singleton) values (true) on conflict do nothing;

insert into public.pagina_permissao(pagina,papeis)
values ('marketing.html',array['admin','socio']::text[]) on conflict (pagina) do nothing;

create table if not exists public.marketing_snapshots (
  id uuid primary key default gen_random_uuid(),
  source text not null check (source in ('instagram_account','instagram_media','instagram_story','meta_ads','ga4','access','google_photos')),
  object_key text not null,
  period_start date not null,
  period_end date not null check (period_end >= period_start and period_end-period_start < 30),
  collected_at timestamptz not null default now(),
  status text not null check (status in ('available','partial','unavailable')),
  payload jsonb not null
);
create index if not exists marketing_snapshots_lookup on public.marketing_snapshots(source,period_start,period_end,collected_at desc);
alter table public.marketing_snapshots enable row level security;
drop policy if exists marketing_snapshots_read on public.marketing_snapshots;
create policy marketing_snapshots_read on public.marketing_snapshots for select to authenticated
using ((select public.usuario_pode_acessar_pagina('marketing.html')));
revoke all on public.marketing_snapshots from public, anon, authenticated;
grant select on public.marketing_snapshots to authenticated;
grant select,insert,update on public.marketing_snapshots to service_role;

create table if not exists public.marketing_editorial (
  id uuid primary key default gen_random_uuid(),
  target text not null check (target in ('instagram','facebook','google_photo')),
  format text not null check (format in ('IMAGE','REELS','STORIES','TEXT','PHOTO')),
  caption text not null default '' check (length(caption)<=2200),
  media_url text,
  source_media_id text,
  scheduled_at timestamptz,
  rights_confirmed boolean not null default false,
  quality_confirmed boolean not null default false,
  status text not null default 'draft' check (status in ('draft','review','approved','sending','published','uncertain','failed','cancelled')),
  revision integer not null default 1,
  approved_revision integer,
  approved_by uuid,
  approved_at timestamptz,
  created_by uuid default auth.uid(),
  updated_at timestamptz not null default now(),
  provider_container_id text,
  provider_id text,
  provider_url text,
  last_error text
);
create index if not exists marketing_editorial_due on public.marketing_editorial(scheduled_at) where status='approved';
alter table public.marketing_editorial enable row level security;
drop policy if exists marketing_editorial_read on public.marketing_editorial;
create policy marketing_editorial_read on public.marketing_editorial for select to authenticated
using ((select public.usuario_pode_acessar_pagina('marketing.html')));
revoke all on public.marketing_editorial from public, anon, authenticated;
grant select on public.marketing_editorial to authenticated;
grant select,insert,update on public.marketing_editorial to service_role;

create table if not exists public.marketing_comments (
  id text primary key,
  network text not null check (network in ('instagram','facebook')),
  media_id text not null,
  media_url text,
  body text not null,
  posted_at timestamptz,
  collected_at timestamptz not null default now(),
  category text not null default 'review' check (category in ('review','question','complaint','other')),
  state text not null default 'new' check (state in ('new','reviewing','handled')),
  note text not null default '' check (length(note)<=1000),
  handled_by uuid,
  updated_at timestamptz not null default now()
);
alter table public.marketing_comments enable row level security;
drop policy if exists marketing_comments_read on public.marketing_comments;
create policy marketing_comments_read on public.marketing_comments for select to authenticated
using ((select public.usuario_pode_acessar_pagina('marketing.html')));
revoke all on public.marketing_comments from public, anon, authenticated;
grant select on public.marketing_comments to authenticated;
grant select,insert,update on public.marketing_comments to service_role;

create table if not exists public.marketing_audit (
  id uuid primary key default gen_random_uuid(),
  editorial_id uuid references public.marketing_editorial(id),
  action text not null,
  actor uuid default auth.uid(),
  occurred_at timestamptz not null default now(),
  detail jsonb not null default '{}'
);
alter table public.marketing_audit enable row level security;
drop policy if exists marketing_audit_read on public.marketing_audit;
create policy marketing_audit_read on public.marketing_audit for select to authenticated
using ((select public.usuario_pode_acessar_pagina('marketing.html')));
revoke all on public.marketing_audit from public, anon, authenticated;
grant select on public.marketing_audit to authenticated;
grant select,insert on public.marketing_audit to service_role;

create or replace function public.marketing_is_owner() returns boolean
language sql stable security definer set search_path=pg_catalog,public as $$
  select coalesce(public.usuario_pode_acessar_pagina('marketing.html') and exists
    (select 1 from marketing_private.settings where singleton and owner_id=auth.uid()),false)
$$;
revoke all on function public.marketing_is_owner() from public,anon,authenticated;
grant execute on function public.marketing_is_owner() to authenticated;

create or replace function public.marketing_save_draft(p_item jsonb,p_id uuid default null) returns uuid
language plpgsql security definer set search_path=pg_catalog,public as $$
declare v_id uuid; v_old public.marketing_editorial;
begin
  if not public.usuario_pode_acessar_pagina('marketing.html') then raise exception 'Acesso nao permitido'; end if;
  if p_id is not null then
    select * into v_old from public.marketing_editorial where id=p_id for update;
    if not found or v_old.status not in ('draft','review','approved','failed','cancelled') then
      raise exception 'Item em envio ou publicado; crie outro rascunho'; end if;
  end if;
  if p_item->>'target' not in ('instagram','facebook','google_photo')
     or p_item->>'format' not in ('IMAGE','REELS','STORIES','TEXT','PHOTO') then raise exception 'Formato invalido'; end if;
  if (p_item->>'target'='instagram' and p_item->>'format' not in ('IMAGE','REELS','STORIES'))
     or (p_item->>'target'='facebook' and p_item->>'format' not in ('TEXT','PHOTO'))
     or (p_item->>'target'='google_photo' and p_item->>'format'<>'PHOTO') then raise exception 'Formato indisponivel neste fluxo'; end if;
  if p_item->>'target'<>'google_photo' and p_item->>'format'<>'TEXT' and coalesce(p_item->>'media_url','') !~ '^https://(www\.)?sirfisher\.com\.br/[A-Za-z0-9_./%~-]+$' then
    raise exception 'Use midia propria publicada no site Sir Fisher'; end if;
  if p_item->>'target'='google_photo' and coalesce(p_item->>'source_media_id','') !~ '^[0-9]{5,30}$' then
    raise exception 'Informe o ID da foto propria'; end if;
  v_id:=coalesce(p_id,gen_random_uuid());
  insert into public.marketing_editorial(id,target,format,caption,media_url,source_media_id,scheduled_at,rights_confirmed,quality_confirmed)
  values(v_id,p_item->>'target',p_item->>'format',coalesce(p_item->>'caption',''),nullif(p_item->>'media_url',''),nullif(p_item->>'source_media_id',''),
    nullif(p_item->>'scheduled_at','')::timestamptz,coalesce((p_item->>'rights_confirmed')::boolean,false),coalesce((p_item->>'quality_confirmed')::boolean,false))
  on conflict(id) do update set target=excluded.target,format=excluded.format,caption=excluded.caption,
    media_url=excluded.media_url,source_media_id=excluded.source_media_id,scheduled_at=excluded.scheduled_at,
    rights_confirmed=excluded.rights_confirmed,quality_confirmed=excluded.quality_confirmed,status='draft',
    revision=marketing_editorial.revision+1,approved_revision=null,approved_by=null,approved_at=null,updated_at=now(),last_error=null;
  insert into public.marketing_audit(editorial_id,action,detail) values(v_id,'draft_saved',p_item);
  return v_id;
end $$;
revoke all on function public.marketing_save_draft(jsonb,uuid) from public,anon,authenticated;
grant execute on function public.marketing_save_draft(jsonb,uuid) to authenticated;

create or replace function public.marketing_review(p_id uuid,p_action text) returns void
language plpgsql security definer set search_path=pg_catalog,public as $$
declare r public.marketing_editorial;
begin
  if not public.usuario_pode_acessar_pagina('marketing.html') then raise exception 'Acesso nao permitido'; end if;
  select * into r from public.marketing_editorial where id=p_id for update;
  if not found then raise exception 'Item ausente'; end if;
  if p_action='review' and r.status='draft' then
    update public.marketing_editorial set status='review',updated_at=now() where id=p_id;
  elsif p_action='approve' and r.status='review' then
    if not public.marketing_is_owner() then raise exception 'Aprovacao exige a conta do proprietario configurada'; end if;
    if not r.rights_confirmed or not r.quality_confirmed or r.scheduled_at is null or r.scheduled_at<=now() then
      raise exception 'Confira direito de uso, qualidade e data futura'; end if;
    update public.marketing_editorial set status='approved',approved_revision=revision,approved_by=auth.uid(),approved_at=now(),updated_at=now() where id=p_id;
  elsif p_action='cancel' and r.status in ('draft','review','approved','failed') then
    update public.marketing_editorial set status='cancelled',updated_at=now() where id=p_id;
  else raise exception 'Transicao indisponivel'; end if;
  insert into public.marketing_audit(editorial_id,action,detail) values(p_id,p_action,to_jsonb(r));
end $$;
revoke all on function public.marketing_review(uuid,text) from public,anon,authenticated;
grant execute on function public.marketing_review(uuid,text) to authenticated;

create or replace function public.marketing_handle_comment(p_id text,p_category text,p_state text,p_note text) returns void
language plpgsql security definer set search_path=pg_catalog,public as $$
begin
  if not public.usuario_pode_acessar_pagina('marketing.html') then raise exception 'Acesso nao permitido'; end if;
  update public.marketing_comments set category=p_category,state=p_state,note=p_note,handled_by=auth.uid(),updated_at=now() where id=p_id;
  if not found then raise exception 'Comentario ausente'; end if;
  insert into public.marketing_audit(action,detail) values('comment_review',jsonb_build_object('id',p_id,'state',p_state,'category',p_category));
end $$;
revoke all on function public.marketing_handle_comment(text,text,text,text) from public,anon,authenticated;
grant execute on function public.marketing_handle_comment(text,text,text,text) to authenticated;

create or replace function public.marketing_reservations(p_start date,p_end date) returns jsonb
language plpgsql stable security definer set search_path=pg_catalog,public as $$
declare result jsonb;
begin
  if not public.usuario_pode_acessar_pagina('marketing.html') then raise exception 'Acesso nao permitido'; end if;
  if p_start is null or p_end is null or p_end<p_start or p_end-p_start>29 then raise exception 'Selecione ate 30 dias'; end if;
  select jsonb_build_object('collected_at',now(),'start',p_start,'end',p_end,
    'coverage','Reservas criadas no periodo; status atual da mesma coorte. Origem registrada em UTM. Declaracao do cliente indisponivel.',
    'declared_source',null,'confirmed_revenue',null,'rows',coalesce(jsonb_agg(to_jsonb(g)),'[]'::jsonb)) into result
  from (select source,coalesce(nullif(utm_source,''),'sem identificador') utm_source,
    nullif(utm_medium,'') utm_medium,nullif(utm_campaign,'') utm_campaign,nullif(utm_content,'') utm_content,
    case when lower(utm_source) in ('ig','instagram','fb','facebook','meta') then chatgpt_campaign_id end campaign_id,
    case when lower(utm_source) in ('ig','instagram','fb','facebook','meta') then chatgpt_ad_id end ad_id,
    count(*) reservations,count(*) filter(where status='compareceu') attended,
    count(*) filter(where status='no_show') no_show,
    count(*) filter(where status in ('cancelada_cliente','cancelada_restaurante','desistiu','recusada')) cancelled,
    count(*) filter(where status not in ('compareceu','no_show','cancelada_cliente','cancelada_restaurante','desistiu','recusada')) awaiting_outcome
    from public.reservations
    where created_at >= (p_start::timestamp at time zone 'America/Fortaleza')
      and created_at < ((p_end+1)::timestamp at time zone 'America/Fortaleza')
    group by 1,2,3,4,5,6,7) g;
  return result;
end $$;
revoke all on function public.marketing_reservations(date,date) from public,anon,authenticated;
grant execute on function public.marketing_reservations(date,date) to authenticated;
commit;
