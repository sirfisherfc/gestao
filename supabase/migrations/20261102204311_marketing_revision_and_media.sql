-- Revisao exibida e arquivo precisam coincidir com a aprovacao.
begin;
alter table public.marketing_editorial add column if not exists media_sha256 text check (media_sha256 ~ '^[0-9a-f]{64}$');
alter table public.marketing_editorial add column if not exists verified_revision integer;
drop function if exists public.marketing_review(uuid,text);
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
  if p_id is not null and (p_item->>'expected_revision')::integer is distinct from v_old.revision then raise exception 'Revisao mudou; recarregue o rascunho'; end if;
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
    revision=marketing_editorial.revision+1,approved_revision=null,approved_by=null,approved_at=null,media_sha256=null,verified_revision=null,updated_at=now(),last_error=null;
  insert into public.marketing_audit(editorial_id,action,detail) values(v_id,'draft_saved',p_item);
  return v_id;
end $$;
revoke all on function public.marketing_save_draft(jsonb,uuid) from public,anon,authenticated;
grant execute on function public.marketing_save_draft(jsonb,uuid) to authenticated;

create or replace function public.marketing_review(p_id uuid,p_action text,p_expected_revision integer) returns void
language plpgsql security definer set search_path=pg_catalog,public as $$
declare r public.marketing_editorial;
begin
  if not public.usuario_pode_acessar_pagina('marketing.html') then raise exception 'Acesso nao permitido'; end if;
  select * into r from public.marketing_editorial where id=p_id for update;
  if not found then raise exception 'Item ausente'; end if;
  if p_expected_revision is distinct from r.revision then raise exception 'Revisao mudou; recarregue antes de aprovar'; end if;
  if p_action='review' and r.status='draft' then
    update public.marketing_editorial set status='review',updated_at=now() where id=p_id;
  elsif p_action='approve' and r.status='review' then
    if not public.marketing_is_owner() then raise exception 'Aprovacao exige a conta do proprietario configurada'; end if;
    if not r.rights_confirmed or not r.quality_confirmed or r.scheduled_at is null or r.scheduled_at<=now() then
      raise exception 'Confira direito de uso, qualidade e data futura'; end if;
    if r.format<>'TEXT' and (r.media_sha256 is null or r.verified_revision is distinct from r.revision) then raise exception 'Validacao do arquivo desta revisao pendente'; end if;
    update public.marketing_editorial set status='approved',approved_revision=revision,approved_by=auth.uid(),approved_at=now(),updated_at=now() where id=p_id;
  elsif p_action='cancel' and r.status in ('draft','review','approved','failed') then
    update public.marketing_editorial set status='cancelled',updated_at=now() where id=p_id;
  else raise exception 'Transicao indisponivel'; end if;
  insert into public.marketing_audit(editorial_id,action,detail) values(p_id,p_action,to_jsonb(r));
end $$;
revoke all on function public.marketing_review(uuid,text,integer) from public,anon,authenticated;
grant execute on function public.marketing_review(uuid,text,integer) to authenticated;

create or replace function public.marketing_dashboard_snapshots(p_start date,p_end date)
returns setof public.marketing_snapshots language sql stable security invoker
set search_path=pg_catalog,public as $$
  select distinct on (source,object_key,
    case when source='google_photos' then null else period_start end,
    case when source='google_photos' then null else period_end end) *
  from public.marketing_snapshots
  where public.usuario_pode_acessar_pagina('marketing.html') and p_end-p_start between 0 and 29
    and ((period_start=p_start and period_end=p_end)
      or (source='instagram_account' and period_start=p_start-(p_end-p_start+1) and period_end=p_start-1)
      or source='google_photos')
  order by source,object_key,
    case when source='google_photos' then null else period_start end,
    case when source='google_photos' then null else period_end end,collected_at desc
$$;
revoke all on function public.marketing_dashboard_snapshots(date,date) from public,anon,authenticated;
grant execute on function public.marketing_dashboard_snapshots(date,date) to authenticated;
commit;
