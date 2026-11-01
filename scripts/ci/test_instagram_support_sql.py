"""Contratos reais em PostgreSQL descartavel; sem Meta, Gemini ou Resend."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[2]
ACTOR = "11111111-1111-4111-8111-111111111111"
ENABLE = """
update instagram_support.settings set mode='live',paused=false,model_usage_allowed=true,
billing_verified=true,pricing_valid_until=now()+interval '1 day' where singleton;
"""
HELPERS = """
create function pg_temp.check_it(ok boolean, message text) returns void language plpgsql as $$
begin if not coalesce(ok,false) then raise exception '%',message; end if; end $$;
create function pg_temp.incoming(sender text, mid text) returns jsonb language sql as $$
 select public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id',$1,
 'recipient_id','17841439937145607','mid',$2,'text','Qual o horario?',
 'timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
$$;
"""


class InstagramSupportSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("IG_SUPPORT_SQL_DISPOSABLE") != "1":
            raise unittest.SkipTest("Exige IG_SUPPORT_SQL_DISPOSABLE=1 e banco local dedicado.")
        if os.environ.get("PGHOST") not in {"127.0.0.1", "localhost", "::1"} or os.environ.get("PGDATABASE") != "sirfisher_ig_support_test":
            raise RuntimeError("Destino de teste recusado: exige loopback e sirfisher_ig_support_test.")
        cls.psql = os.environ.get("IG_SUPPORT_PSQL") or shutil.which("psql")
        if not cls.psql:
            raise RuntimeError("psql ausente; configure IG_SUPPORT_PSQL.")
        info = cls.run_sql("select current_database() || '|' || host(inet_server_addr())").strip()
        if info not in {"sirfisher_ig_support_test|127.0.0.1", "sirfisher_ig_support_test|::1"}:
            raise RuntimeError("Servidor de teste recusado.")
        cls.run_sql("drop schema if exists instagram_support cascade;")
        cls.run_sql((ROOT / "scripts/ci/fixtures/instagram_support.sql").read_text(encoding="utf-8"))
        files = list((ROOT / "supabase/migrations").glob("*_instagram_support_durable_queue.sql"))
        if len(files) != 1:
            raise RuntimeError("Migration Instagram ambigua.")
        migration = files[0].read_text(encoding="utf-8")
        cls.run_sql(migration)
        cls.run_sql(migration)  # Reaplicar preserva seed seguro e um unico job desligado.

    @classmethod
    def run_sql(cls, sql):
        process = subprocess.run([cls.psql, "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1"],
                                 input=sql, text=True, encoding="utf-8", capture_output=True, timeout=30)
        if process.returncode:
            raise AssertionError(process.stderr.strip())
        return process.stdout.strip()

    def check_sql(self, body, enable=True):
        return self.run_sql("begin;\n" + HELPERS + (ENABLE if enable else "") + body + "\nrollback;")

    def test_permissions_and_disabled_defaults(self):
        self.check_sql("""
select pg_temp.check_it((select mode='off' and paused and not model_usage_allowed and not billing_verified and not alerts_enabled and manager_auth_user_id is null from instagram_support.settings),'defaults');
select pg_temp.check_it((select count(*)=1 and not bool_or(active) from cron.job where jobname='sirfisher-instagram-support-drain'),'cron disabled');
select pg_temp.check_it(not has_schema_privilege('anon','instagram_support','USAGE'),'anon schema');
select pg_temp.check_it(not has_schema_privilege('authenticated','instagram_support','USAGE'),'authenticated schema');
select pg_temp.check_it(not exists(select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace where (n.nspname='instagram_support' or (n.nspname='public' and p.proname like 'ig_support_%')) and p.prosecdef),'invoker only');
select pg_temp.check_it(not exists(select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname like 'ig_support_%' and (has_function_privilege('anon',p.oid,'EXECUTE') or has_function_privilege('authenticated',p.oid,'EXECUTE'))),'no client execute');
select pg_temp.check_it(not exists(select 1 from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='instagram_support' and c.relkind='r' and not c.relrowsecurity),'RLS all tables');
set local role service_role;
select pg_temp.check_it(pg_temp.incoming('100001','off-1')->>'queued'='false','off queues');
select pg_temp.check_it(pg_temp.incoming('100001','off-1')->>'status'='duplicate','mid dedupe');
select pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'off claims');
select pg_temp.check_it((select count(*)=1 and bool_and(text='') from instagram_support.events),'off no text');
""", enable=False)

    def test_allowlist_and_per_thread_lease(self):
        self.check_sql("""
update instagram_support.settings set mode='test',test_sender_ids=array['100001'];
set local role service_role;
do $$ declare claim jsonb; begin
 perform pg_temp.check_it(pg_temp.incoming('100002','deny')->>'queued'='false','allowlist deny');
 perform pg_temp.check_it(pg_temp.incoming('100001','allow')->>'queued'='true','allowlist accept');
 claim:=public.ig_support_claim(gen_random_uuid(),1);
 perform pg_temp.check_it(jsonb_array_length(claim)=1 and claim->0->>'first_reply'='true','claim one');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'lease excludes second');
 perform pg_temp.check_it(public.ig_support_reserve_budget((claim->0->>'event_id')::uuid,gen_random_uuid(),2)->>'allowed'='false','wrong lease');
end $$;
""")

    def test_budget_reserved_before_ai_once_and_limit(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; b jsonb; r jsonb; begin
 perform pg_temp.incoming('100001','budget1'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 r:=public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 perform pg_temp.check_it(r->>'allowed'='true','first reservation');
 perform pg_temp.check_it(public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2)->>'reason'='already_started','no second generation');
 perform public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}'::jsonb);
 perform pg_temp.check_it((select spent_cents=2 and reserved_cents=0 and generations=1 from instagram_support.budget_months),'unknown usage full charge');
 update instagram_support.budget_months set spent_cents=4500;
 perform pg_temp.incoming('100002','budget2'); b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(public.ig_support_reserve_budget((b->>'event_id')::uuid,(b->>'lease')::uuid,2)->>'reason'='monthly_limit','budget cap');
end $$;
""")

    def test_model_billing_and_price_expiry_fail_closed(self):
        self.check_sql("""
update instagram_support.settings set billing_verified=false;
set local role service_role;
do $$ declare a jsonb; begin
 perform pg_temp.incoming('100001','billing'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2)->>'reason'='model_not_approved','billing gate');
 update instagram_support.settings set billing_verified=true,pricing_valid_until=now()-interval '1 second';
 perform pg_temp.check_it(public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2)->>'reason'='model_not_approved','pricing expiry');
end $$;
""")

    def test_human_echo_invalidates_inflight_and_persists(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; begin
 perform pg_temp.incoming('100001','human-in'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 perform public.ig_support_ingest(jsonb_build_object('kind','echo','sender_id','100001','recipient_id','17841439937145607','mid','human-out','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform pg_temp.check_it(public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}')->>'decision'='cancelled','inflight cancelled');
 update instagram_support.threads set updated_at=now()-interval '10 days';
 perform pg_temp.check_it(pg_temp.incoming('100001','after-human')->>'queued'='false','no pause TTL');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.cases where status='open'),'durable case');
 perform pg_temp.check_it((select spent_cents=2 and reserved_cents=0 from instagram_support.budget_months),'cancel charges conservatively');
end $$;
""")

    def test_sensitive_burst_routes_before_worker_and_respects_test_gate(self):
        self.check_sql("""
set local role service_role;
do $$ declare result jsonb; begin
 result:=public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id','100001','recipient_id','17841439937145607','mid','allergy1','text','Alergia grave.',
   'safety_intent','ALLERGY','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform pg_temp.check_it(result->>'case_saved'='true' and result->>'queued'='false','safety persisted before ACK');
 perform pg_temp.check_it(pg_temp.incoming('100001','allergy-followup')->>'queued'='false','followup cannot erase safety');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no AI after allergy');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.budget_reservations),'no model spend');
 update instagram_support.settings set mode='test',test_sender_ids=array['100003'];
 result:=public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id','100002','recipient_id','17841439937145607','mid','unlisted-safety','text','Preciso gerente.',
   'safety_intent','HUMAN','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform pg_temp.check_it(result->>'case_saved'='false','test ignores unlisted customer');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.cases),'no extra case from test');
end $$;
""")

    def test_known_echo_and_one_outbox_effect(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; c jsonb; o jsonb; begin
 perform pg_temp.incoming('100001','out-in'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Horario confirmado na fonte.',(c->>'thread_version')::bigint);
 perform pg_temp.check_it(o->>'allowed'='true','one prepare');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Outro envio.',(c->>'thread_version')::bigint)->>'allowed'='false','no second prepare');
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','bot-mid');
 perform public.ig_support_ingest(jsonb_build_object('kind','echo','sender_id','100001','recipient_id','17841439937145607','mid','bot-mid','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform pg_temp.check_it((select not human_paused from instagram_support.threads where sender_id='100001'),'known echo ignored');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.cases),'no case on known bot');
 perform pg_temp.check_it((select bool_and(text='') from instagram_support.events),'customer text erased');
end $$;
""")

    def test_unknown_second_question_handoff_and_single_ack(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; c jsonb; o jsonb; begin
 perform pg_temp.incoming('100001','unknown1'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"UNKNOWN"}');
 perform pg_temp.check_it(c->>'decision'='clarify','clarify once');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Pode explicar sua duvida?',(c->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','clarify-mid');
 perform pg_temp.incoming('100001','unknown2'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"UNKNOWN"}');
 perform pg_temp.check_it(c->>'decision'='handoff' and c->>'case_saved'='true','second question saves case');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'O atendimento humano precisa conferir. Automacao pausada.',(c->>'thread_version')::bigint);
 perform pg_temp.check_it(o->>'allowed'='true','one handoff acknowledgement');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Repeticao.',(c->>'thread_version')::bigint)->>'allowed'='false','handoff not repeated');
end $$;
""")

    def test_unknown_delivery_not_retried_and_close_preserves_pause(self):
        self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb; c jsonb; o jsonb; t uuid; result jsonb; begin
 perform pg_temp.incoming('100001','delivery-in'); a:=public.ig_support_claim(gen_random_uuid(),1)->0; t:=(a->>'thread_id')::uuid;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{{"intent":"HOURS"}}');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Resposta curta.',(c->>'thread_version')::bigint);
 result:=public.ig_support_control('resume',t,jsonb_build_object('actor_id','{ACTOR}','confirm',true));
 perform pg_temp.check_it(result->>'changed'='false','cannot resume sending');
 update instagram_support.outbox set send_deadline=now()-interval '1 second';
 perform public.ig_support_claim(gen_random_uuid(),1);
 perform pg_temp.check_it((select status='uncertain' from instagram_support.outbox),'expired sending uncertain');
 perform pg_temp.check_it(pg_temp.incoming('100001','delivery-next')->>'queued'='false','new message paused');
 perform public.ig_support_control('close',t,jsonb_build_object('actor_id','{ACTOR}'));
 perform pg_temp.check_it((select human_paused from instagram_support.threads where id=t),'close keeps paused');
 perform pg_temp.check_it(jsonb_array_length(public.ig_support_control('cases')->'cases')=1,'closed paused remains visible');
 perform public.ig_support_control('resume',t,jsonb_build_object('actor_id','{ACTOR}','confirm',true));
 perform pg_temp.check_it(pg_temp.incoming('100001','delivery-resumed')->>'queued'='true','explicit resume allows new message');
end $$;
""")

    def test_new_message_supersedes_inflight(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; begin
 perform pg_temp.incoming('100001','old'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 perform pg_temp.incoming('100001','new');
 perform pg_temp.check_it(public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}')->>'decision'='cancelled','stale result cancelled');
 perform pg_temp.check_it(jsonb_array_length(public.ig_support_claim(gen_random_uuid(),1))=1,'new message claimable');
end $$;
""")

    def test_expired_ai_lease_does_not_call_ai_again(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; begin
 perform pg_temp.incoming('100001','timeout'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 update instagram_support.events set lease_until=now()-interval '1 second';
 update instagram_support.threads set lease_until=now()-interval '1 second';
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no retry after ai started');
 perform pg_temp.check_it((select human_paused from instagram_support.threads),'timeout human');
 perform pg_temp.check_it((select spent_cents=2 and reserved_cents=0 from instagram_support.budget_months),'timeout full charge');
end $$;
""")

    def test_rates_and_skip(self):
        self.check_sql("""
update instagram_support.settings set global_per_minute=1;
set local role service_role;
do $$ declare a jsonb; b jsonb; begin
 perform pg_temp.incoming('100001','rate1'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 perform pg_temp.incoming('100002','rate2'); b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(public.ig_support_reserve_budget((b->>'event_id')::uuid,(b->>'lease')::uuid,2)->>'reason'='global_rate','global cap');
 perform pg_temp.check_it(public.ig_support_complete((b->>'event_id')::uuid,(b->>'lease')::uuid,'{"intent":"IGNORE","skip":true}')->>'decision'='cancelled','skip');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.cases),'skip no case');
end $$;
""")

    def test_usage_anomaly_pauses_globally(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; c jsonb; begin
 perform pg_temp.incoming('100001','usage'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"UNKNOWN","handoff_reason":"usage_bound_exceeded","policy_error":"usage_bound_exceeded"}');
 perform pg_temp.check_it((select mode='off' and paused from instagram_support.settings),'anomaly global stop');
 perform pg_temp.check_it(c->>'case_saved'='true','anomaly case');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Ack.',(c->>'thread_version')::bigint)->>'allowed'='false','no send after global stop');
end $$;
""")

    def test_early_echo_during_send_keeps_human_pause_after_success(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; c jsonb; o jsonb; begin
 perform pg_temp.incoming('100001','early-in'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Resposta curta.',(c->>'thread_version')::bigint);
 perform public.ig_support_ingest(jsonb_build_object('kind','echo','sender_id','100001','recipient_id','17841439937145607','mid','early-bot-mid','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','early-bot-mid');
 perform pg_temp.check_it((select human_paused from instagram_support.threads),'early unknown echo stays paused');
 perform pg_temp.check_it(pg_temp.incoming('100001','early-followup')->>'queued'='false','no resume after own late reconciliation');
end $$;
""")

    def test_per_thread_rate_and_lease_recovery_before_ai(self):
        self.check_sql("""
update instagram_support.settings set thread_per_ten_minutes=1;
set local role service_role;
do $$ declare a jsonb; b jsonb; c jsonb; o jsonb; begin
 perform pg_temp.incoming('100001','lease-before-ai'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 update instagram_support.events set lease_until=now()-interval '1 second';
 update instagram_support.threads set lease_until=now()-interval '1 second';
 b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(b->>'event_id'=a->>'event_id' and b->>'lease'<>a->>'lease','safe recovery before AI');
 perform public.ig_support_reserve_budget((b->>'event_id')::uuid,(b->>'lease')::uuid,2);
 c:=public.ig_support_complete((b->>'event_id')::uuid,(b->>'lease')::uuid,'{"intent":"HOURS"}');
 o:=public.ig_support_prepare_send((b->>'event_id')::uuid,(b->>'lease')::uuid,'Resposta.',(c->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(b->>'lease')::uuid,'sent','rate-thread-mid');
 perform pg_temp.incoming('100001','rate-thread-next'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2)->>'reason'='thread_rate','thread rate cap');
end $$;
""")

    def test_alerts_private_cap_idempotency_and_no_backlog(self):
        self.check_sql(f"""
insert into public.app_users(auth_user_id,email,active,role) values('{ACTOR}','manager@example.invalid',true,'admin');
set local role service_role;
do $$ declare a jsonb; c jsonb; alert jsonb; begin
 perform pg_temp.incoming('100001','no-alert'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{{"handoff_reason":"complaint"}}');
 update instagram_support.settings set alerts_enabled=true,manager_auth_user_id='{ACTOR}',alerts_activation_after=now(),alerts_monthly_limit=1;
 perform pg_temp.check_it(public.ig_support_claim_alerts(gen_random_uuid(),1)='[]'::jsonb,'no historical alerts');
 perform pg_temp.incoming('100002','alert1'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{{"handoff_reason":"payment"}}');
 alert:=public.ig_support_claim_alerts(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(alert->>'manager_email'='manager@example.invalid','manager server resolved');
 perform pg_temp.check_it(public.ig_support_claim_alerts(gen_random_uuid(),1)='[]'::jsonb,'no duplicate alert claim');
 perform public.ig_support_finish_alert((alert->>'alert_id')::uuid,(alert->>'lease')::uuid,'uncertain',null,false);
 perform pg_temp.incoming('100003','alert2'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{{"handoff_reason":"allergy"}}');
 perform pg_temp.check_it(public.ig_support_claim_alerts(gen_random_uuid(),1)='[]'::jsonb,'monthly alert cap');
 perform pg_temp.check_it(position('manager@example.invalid' in public.ig_support_control('cases')::text)=0,'no email in case UI');
 perform pg_temp.check_it(not(public.ig_support_control('status')->'settings' ? 'manager_auth_user_id'),'no manager identity in UI settings');
end $$;
""")

    def test_z_concurrent_claim_and_budget(self):
        # Dados sinteticos commitados apenas no banco com nome/host conferidos.
        self.run_sql(HELPERS + ENABLE + "select pg_temp.incoming('900001','concurrent-one');")
        def claim(_):
            return json.loads(self.run_sql("set role service_role; select public.ig_support_claim('" + str(uuid.uuid4()) + "',1);"))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, range(2)))
        self.assertEqual(sorted(map(len, results)), [0, 1])
        self.run_sql("update instagram_support.settings set monthly_budget_cents=2;" + HELPERS + "select pg_temp.incoming('900002','concurrent-two');")
        second = claim(0)[0]
        first = next(item[0] for item in results if item)
        def reserve(item):
            return json.loads(self.run_sql("set role service_role; select public.ig_support_reserve_budget('" + item["event_id"] + "','" + item["lease"] + "',2);"))
        with ThreadPoolExecutor(max_workers=2) as pool:
            reserved = list(pool.map(reserve, [first, second]))
        self.assertEqual(sorted(result["allowed"] for result in reserved), [False, True])
        self.run_sql("update instagram_support.settings set mode='off',paused=true;")


if __name__ == "__main__":
    unittest.main(verbosity=2)
