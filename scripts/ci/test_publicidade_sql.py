"""Exercita consentimento e filas em um PostgreSQL descartavel, sem rede externa."""
import os
from pathlib import Path
import psycopg2

if os.environ.get('PUBLICIDADE_SQL_DISPOSABLE') != '1':
    raise SystemExit('Use somente com PUBLICIDADE_SQL_DISPOSABLE=1 e banco descartavel.')
if os.environ.get('PGDATABASE') != 'sirfisher_publicidade_test':
    raise SystemExit('Banco descartavel esperado: sirfisher_publicidade_test.')

root = Path(__file__).resolve().parents[2]
migration = (root / 'supabase/migrations/20261103071209_publicidade_consentimento.sql').read_text(encoding='utf-8')
bootstrap = """
do $$ begin
 if not exists(select 1 from pg_roles where rolname='anon') then create role anon; end if;
 if not exists(select 1 from pg_roles where rolname='authenticated') then create role authenticated; end if;
 if not exists(select 1 from pg_roles where rolname='service_role') then create role service_role; end if;
end $$;
create table public.availability_rules(id int);
create table public.reservations(
 id uuid primary key default gen_random_uuid(), source text default 'public_site', status text default 'confirmada',
 accepted_policy boolean default true, openai_oppref text, customer_email_snapshot text, customer_phone_snapshot text,
 customer_id uuid, party_size int default 2, attribution_landing_url text, meta_fbp text, meta_fbc text
);
create table public.ad_conversion_events(
 id uuid primary key default gen_random_uuid(), reservation_id uuid, provider text, event_name text, event_id text,
 status text default 'pending', attempts int default 0, created_at timestamptz default now(),
 last_attempt_at timestamptz, last_error text,
 unique(reservation_id,provider,event_name)
);
"""
checks = """
create trigger meta after insert on public.reservations for each row execute function public.fn_enqueue_meta_schedule();
create trigger oai_schedule after insert on public.reservations for each row execute function public.fn_enqueue_openai_ads_schedule();
create trigger oai_visit after update of status on public.reservations for each row execute function public.fn_enqueue_openai_ads_visit();
do $$
declare a uuid; b uuid; c uuid; proof uuid:=gen_random_uuid(); q uuid; n int;
begin
 insert into public.reservations default values returning id into a;
 assert not exists(select 1 from public.ad_conversion_events where reservation_id=a), 'No choice queued advertising';
 insert into public.reservations(advertising_consent_receipt,advertising_consent_at,advertising_consent_version,openai_oppref)
 values(proof,now(),'2026-11-03','fixture') returning id into b;
 assert (select count(*)=2 from public.ad_conversion_events where reservation_id=b), 'Granted schedule missing';
 insert into public.reservations(advertising_consent_receipt,advertising_consent_at)
 values(gen_random_uuid(),now()-interval '181 days') returning id into c;
 assert not exists(select 1 from public.ad_conversion_events where reservation_id=c), 'Expired choice queued advertising';
 update public.reservations set status='compareceu' where id=b;
 assert (select count(*)=3 from public.ad_conversion_events where reservation_id=b), 'Granted visit missing';
 select e.id into q from public.ad_conversion_events e where e.reservation_id=b and e.provider='meta';
 assert public.fn_advertising_event_allowed(q), 'Granted event denied';
 select count(*) into n from public.fn_claim_pending_meta_conversions(25);
 assert n=1, 'Claim returned missing or excess events';
 assert public.fn_revoke_advertising_consent(proof), 'Revocation failed';
 assert not public.fn_advertising_event_allowed(q), 'Revoked event allowed';
 assert not exists(select 1 from public.fn_claim_pending_openai_ads_conversions(25)), 'Revoked queue claimed';
 assert (select bool_and(attempts=10 and status='failed') from public.ad_conversion_events where reservation_id=b), 'Revocation did not stop retries';
 assert not private.advertising_allowed(gen_random_uuid(),now()+interval '1 day'), 'Future grant accepted';
 assert not has_table_privilege('anon','private.advertising_revocations','select'), 'Anonymous table read allowed';
 assert not has_function_privilege('anon','public.fn_advertising_event_allowed(uuid)','execute'), 'Anonymous event read allowed';
 assert has_function_privilege('anon','public.fn_revoke_advertising_consent(uuid)','execute'), 'Revocation unavailable';
end $$;
set role anon;
select public.fn_revoke_advertising_consent('11111111-1111-4111-8111-111111111111');
reset role;
"""
connection = psycopg2.connect('')
try:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(bootstrap)
            cursor.execute(migration)
            cursor.execute(migration)  # Reaplicacao preserva o contrato.
            cursor.execute(checks)
    print('PUBLICIDADE_SQL_OK grant deny expiry revoke retry privileges idempotence')
finally:
    connection.close()
