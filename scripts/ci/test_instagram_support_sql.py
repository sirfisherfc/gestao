"""Contratos reais em PostgreSQL descartavel; sem Meta, Gemini ou Resend."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import ipaddress
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
billing_verified=true,public_data_approved=true,public_delivery_verified=true,pricing_valid_until=now()+interval '1 day' where singleton;
"""
HELPERS = """
create function pg_temp.check_it(ok boolean, message text) returns void language plpgsql as $$
begin if not coalesce(ok,false) then raise exception '%',message; end if; end $$;
create function pg_temp.incoming(sender text, mid text) returns jsonb language sql as $$
 select public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id',$1,
 'recipient_id','17841439937145607','mid',$2,'text','Qual o horario?',
 'timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
$$;
create function pg_temp.safety(sender text, mid text, intent text) returns jsonb language sql as $$
 select public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id',$1,
 'recipient_id','17841439937145607','mid',$2,'text','Solicitacao sintetica.',
 'safety_intent',$3,'timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
$$;
create function pg_temp.withdraw(sender text, mid text) returns jsonb language sql as $$
 select public.ig_support_ingest(jsonb_build_object('kind','withdrawal','sender_id',$1,
 'recipient_id','17841439937145607','mid',$2,'timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
$$;
"""


def verified_test_destination(info, environment):
    """Apenas o banco descartavel local ou o service Docker explicito do Actions."""
    if environment.get("IG_SUPPORT_SQL_DISPOSABLE") != "1":
        return False
    if environment.get("PGHOST") not in {"127.0.0.1", "localhost", "::1"}:
        return False
    if environment.get("PGDATABASE") != "sirfisher_ig_support_test":
        return False
    database, separator, address = info.partition("|")
    if not separator or database != "sirfisher_ig_support_test":
        return False
    try:
        server = ipaddress.ip_address(address)
    except ValueError:
        return False
    if server.is_loopback:
        return True
    return (environment.get("GITHUB_ACTIONS") == "true"
            and environment.get("IG_SUPPORT_SQL_CONTAINER") == "1"
            and environment.get("PGPORT") == "5432"
            and server in ipaddress.ip_network("172.16.0.0/12"))


class TestDestinationGuard(unittest.TestCase):
    def test_local_destination_requires_exact_database_and_loopback_client(self):
        env = {"PGHOST": "127.0.0.1", "PGDATABASE": "sirfisher_ig_support_test", "IG_SUPPORT_SQL_DISPOSABLE": "1"}
        self.assertTrue(verified_test_destination("sirfisher_ig_support_test|127.0.0.1", env))
        for info, overrides in [("portal|127.0.0.1", {}), ("sirfisher_ig_support_test|127.0.0.1", {"PGHOST": "remote.invalid"}),
                                ("sirfisher_ig_support_test|127.0.0.1", {"PGDATABASE": "portal"}),
                                ("sirfisher_ig_support_test|127.0.0.1", {"IG_SUPPORT_SQL_DISPOSABLE": "0"}), ("invalid", {})]:
            self.assertFalse(verified_test_destination(info, {**env, **overrides}))

    def test_docker_destination_requires_actions_explicit_optin_port_and_private_network(self):
        env = {"PGHOST": "127.0.0.1", "PGPORT": "5432", "PGDATABASE": "sirfisher_ig_support_test",
               "GITHUB_ACTIONS": "true", "IG_SUPPORT_SQL_CONTAINER": "1", "IG_SUPPORT_SQL_DISPOSABLE": "1"}
        self.assertTrue(verified_test_destination("sirfisher_ig_support_test|172.18.0.2", env))
        for overrides in [{"GITHUB_ACTIONS": "false"}, {"IG_SUPPORT_SQL_CONTAINER": "0"}, {"PGPORT": "65437"}, {"PGHOST": "172.18.0.2"}]:
            self.assertFalse(verified_test_destination("sirfisher_ig_support_test|172.18.0.2", {**env, **overrides}))
        for address in ("203.0.113.2", "172.15.0.2", "172.32.0.2"):
            self.assertFalse(verified_test_destination("sirfisher_ig_support_test|" + address, env))


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
        if not verified_test_destination(info, os.environ):
            raise RuntimeError("Servidor de teste recusado.")
        cls.run_sql("drop schema if exists instagram_support cascade;")
        cls.run_sql((ROOT / "scripts/ci/fixtures/instagram_support.sql").read_text(encoding="utf-8"))
        for suffix in ("durable_queue", "whatsapp_notice", "withdrawal", "whatsapp_continue"):
            files = list((ROOT / "supabase/migrations").glob(f"*_instagram_support_{suffix}.sql"))
            if len(files) != 1:
                raise RuntimeError("Migration Instagram ambigua.")
            migration = files[0].read_text(encoding="utf-8")
            cls.run_sql(migration)
            cls.run_sql(migration)  # Reaplicar preserva seed seguro e um unico job desligado.
        helper = ROOT.parent / "reservas/tools/activate_instagram_support_test.mjs"
        if helper.exists():
            loaded = subprocess.run(["node", "--input-type=module", "-e",
                "import {queries} from './tools/activate_instagram_support_test.mjs'; console.log(JSON.stringify(queries('100001')));"],
                cwd=helper.parents[1], text=True, capture_output=True, timeout=15, check=True)
            cls.activation_queries = json.loads(loaded.stdout)
        else:
            cls.activation_queries = None  # CI de gestao pode ter clone independente.

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
select pg_temp.check_it((select rolbypassrls from pg_roles where rolname='service_role'),'server role matches Supabase');
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

    def test_activation_helper_sql_requires_off_and_fresh_test_message(self):
        if self.activation_queries is None:
            self.skipTest("Contrato do helper fica no clone reservas.")
        sql = self.activation_queries
        activate = sql['activate'].replace('begin; set local', 'set local', 1).replace('commit;', '', 1)
        self.check_sql("select pg_temp.incoming('100001','activation-bootstrap');\n" + activate + "\n" +
            "create temp table activation_readback as " + sql['readback'] + "\n" +
            "select pg_temp.check_it((select test_ready and sender_count=1 and bootstrap_pending=0 from activation_readback),'activation contract');\n"
            "select pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no bootstrap reply');\n"
            "select pg_temp.check_it(pg_temp.incoming('100001','activation-fresh')->>'queued'='true','fresh owner test accepted');\n"
            "select pg_temp.check_it(pg_temp.incoming('100002','activation-customer')->>'queued'='false','other customer remains off');", enable=False)
        with self.assertRaisesRegex(AssertionError, 'activation_guard_failed'):
            self.check_sql("select pg_temp.incoming('100001','activation-wrong-mode');\n" + activate)

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
do $$ declare result jsonb; a jsonb; begin
 result:=public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id','100001','recipient_id','17841439937145607','mid','allergy1','text','Alergia grave.',
   'safety_intent','ALLERGY','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform pg_temp.check_it(result->>'case_saved'='true' and result->>'queued'='true','case and notice persisted before ACK');
 perform pg_temp.check_it(pg_temp.incoming('100001','allergy-followup')->>'queued'='true','followup queued behind safety');
 a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(a->>'handoff_ack'='true' and a->>'reply_key'='ALLERGY','only curated notice after allergy');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.budget_reservations),'no model spend');
 update instagram_support.settings set mode='test',test_sender_ids=array['100003'];
 result:=public.ig_support_ingest(jsonb_build_object('kind','incoming','sender_id','100002','recipient_id','17841439937145607','mid','unlisted-safety','text','Preciso gerente.',
   'safety_intent','HUMAN','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));
 perform pg_temp.check_it(result->>'case_saved'='false','test ignores unlisted customer');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.cases),'no extra case from test');
end $$;
""")

    def test_whatsapp_notice_once_and_priority_before_claim(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; o jsonb; begin
 perform pg_temp.safety('100001','wa-human','HUMAN');
 perform pg_temp.safety('100001','wa-urgent','URGENCY');
 perform pg_temp.safety('100001','wa-human-again','HUMAN');
 perform pg_temp.incoming('100001','wa-normal');
 a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(a->>'handoff_ack'='true' and a->>'reply_key'='URGENCY','highest priority notice');
 perform pg_temp.check_it((select not human_paused from instagram_support.threads),'WhatsApp does not pause FAQ');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Aviso sintetico urgente WhatsApp.',(a->>'thread_version')::bigint);
 perform pg_temp.check_it(o->>'allowed'='true','first notice prepared');
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','wa-confirmed-mid');
 perform pg_temp.safety('100001','wa-repeated','ALLERGY');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no repeated notice');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.cases),'one case');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.outbox),'one external effect');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.budget_reservations),'zero model budget');
 perform pg_temp.check_it(public.ig_support_control('cases')->'cases'->0->>'handoff_notice_status'='sent','UI says Instagram link sent only');
end $$;
""")

    def test_whatsapp_priority_after_claim_invalidates_old_lease(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; b jsonb; begin
 perform pg_temp.safety('100001','wa-claim-human','HUMAN'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.safety('100001','wa-claim-urgency','URGENCY');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Aviso antigo.',(a->>'thread_version')::bigint)->>'allowed'='false','stale generic notice blocked');
 b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(b->>'event_id'=a->>'event_id' and b->>'lease'<>a->>'lease' and b->>'reply_key'='URGENCY','same case regenerated with urgency');
 perform pg_temp.check_it(public.ig_support_prepare_send((b->>'event_id')::uuid,(b->>'lease')::uuid,'Procure a equipe presente.',(b->>'thread_version')::bigint)->>'allowed'='true','urgent notice prepared once');
end $$;
""")

    def test_whatsapp_global_pause_manual_echo_and_close_cancel_terminally(self):
        for action in ('pause_global', 'assume', 'close', 'echo'):
            with self.subTest(action=action):
                mutate = (f"perform public.ig_support_control('{action}',(a->>'thread_id')::uuid,'{{\"actor_id\":\"{ACTOR}\",\"paused\":true}}');"
                          if action != 'echo' else "perform public.ig_support_ingest(jsonb_build_object('kind','echo','sender_id','100001','recipient_id','17841439937145607','mid','wa-manual-echo','timestamp_ms',floor(extract(epoch from now())*1000)::bigint));")
                self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb; begin
 perform pg_temp.safety('100001','wa-cancel','HUMAN'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 {mutate}
 update instagram_support.settings set paused=false;
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Aviso tardio.',(a->>'thread_version')::bigint)->>'allowed'='false','cancelled notice blocked');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'cancelled notice never replayed');
end $$;
""")

    def test_whatsapp_recover_before_send_and_no_retry_after_uncertain(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb; b jsonb; o jsonb; begin
 perform pg_temp.safety('100001','wa-worker','HUMAN'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 update instagram_support.events set lease_until=now()-interval '1 second' where id=(a->>'event_id')::uuid;
 update instagram_support.threads set lease_until=now()-interval '1 second';
 b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(b->>'handoff_ack'='true' and b->>'lease'<>a->>'lease','worker recovered before external send');
 o:=public.ig_support_prepare_send((b->>'event_id')::uuid,(b->>'lease')::uuid,'Aviso sintetico.',(b->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(b->>'lease')::uuid,'uncertain');
 perform pg_temp.safety('100001','wa-after-unknown','URGENCY');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'unknown external effect not repeated');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.outbox),'one outbox after unknown');
end $$;
""")

    def test_whatsapp_resume_starts_new_case_and_retains_notice(self):
        self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb; b jsonb; v_restricted boolean:=false; begin
 perform pg_temp.safety('100001','wa-old','HUMAN'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_control('resume',(a->>'thread_id')::uuid,'{{"actor_id":"{ACTOR}","confirm":true}}');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'resume does not replay old notice');
 perform pg_temp.safety('100001','wa-new','HUMAN'); b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(b->>'case_id'<>a->>'case_id' and b->>'handoff_ack'='true','new case gets new notice');
 begin delete from instagram_support.events where id=(a->>'event_id')::uuid; exception when foreign_key_violation then v_restricted:=true; end;
 perform pg_temp.check_it(v_restricted,'notice retained to prevent rearming');
end $$;
""")

    def test_off_bootstrap_and_old_case_cannot_replay_notice(self):
        self.check_sql("""
set local role service_role;
do $$ begin
 perform pg_temp.safety('100001','wa-bootstrap','HUMAN');
 update instagram_support.settings set mode='test',paused=false,test_sender_ids=array['100001'];
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'off bootstrap never replayed');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.cases),'off has no human notice');
end $$;
""", enable=False)

    def test_global_pause_during_model_cannot_create_late_notice(self):
        self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb; c jsonb; begin
 perform pg_temp.incoming('100001','wa-model-inflight'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);
 perform public.ig_support_control('pause_global',null,'{{"actor_id":"{ACTOR}","paused":true}}');
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{{"intent":"HUMAN","handoff_reason":"unknown_after_clarification"}}');
 perform pg_temp.check_it(c->>'allowed'='false','completion respects pause after model');
 perform public.ig_support_control('pause_global',null,'{{"actor_id":"{ACTOR}","paused":false}}');
 update instagram_support.events set lease_until=now()-interval '1 second';
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no late notice after unpause');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.cases),'no retroactive case notice');
 perform pg_temp.check_it((select spent_cents=2 and reserved_cents=0 from instagram_support.budget_months),'model reservation settled');
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
 perform pg_temp.check_it(c->>'decision'='handoff' and c->>'case_saved'='true','first unknown saves WhatsApp case');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Pode explicar sua duvida?',(c->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','clarify-mid');
 perform pg_temp.incoming('100001','unknown2'); a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"UNKNOWN"}');
 perform pg_temp.check_it(c->>'decision'='handoff' and c->>'case_saved'='true' and c->>'allowed'='false','second unknown keeps case without another notice');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'O atendimento humano precisa conferir. Automacao pausada.',(c->>'thread_version')::bigint);
 perform pg_temp.check_it(o->>'allowed'='false','no second handoff acknowledgement');
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

    def test_withdrawal_before_original_and_sender_scope(self):
        self.check_sql("""
set local role service_role;
do $$ begin
 perform pg_temp.withdraw('100001','withdraw-first');
 perform pg_temp.check_it(pg_temp.incoming('100001','withdraw-first')->>'status'='duplicate','late original blocked');
 perform pg_temp.check_it(pg_temp.withdraw('100001','withdraw-first')->>'status'='withdrawn_duplicate','withdrawal idempotent');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'tombstone never processed');
 perform pg_temp.incoming('100001','scope-original');
 perform pg_temp.check_it(pg_temp.withdraw('100002','scope-original')->>'reason'='mid_sender_mismatch','wrong sender cannot cancel');
 perform pg_temp.check_it((select withdrawn_at is null and text<>'' from instagram_support.events where mid='scope-original'),'other sender preserved');
 perform pg_temp.check_it((select not human_paused from instagram_support.threads where sender_id='100001'),'unsend is not global optout');
end $$;
""")

    def test_withdrawal_pending_claim_and_reserved_call(self):
        for reserved in (False, True):
            with self.subTest(reserved=reserved):
                reserve = "perform public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2);" if reserved else ""
                cost = "perform pg_temp.check_it((select spent_cents=2 and reserved_cents=0 from instagram_support.budget_months),'started call charged conservatively');" if reserved else "perform pg_temp.check_it((select count(*)=0 from instagram_support.budget_reservations),'zero model before reserve');"
                self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb;c jsonb;begin
 perform pg_temp.incoming('100001','withdraw-work');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 {reserve}
 perform pg_temp.withdraw('100001','withdraw-work');
 perform pg_temp.check_it(public.ig_support_reserve_budget((a->>'event_id')::uuid,(a->>'lease')::uuid,2)->>'allowed'='false','cancelled cannot reserve');
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{{"intent":"HOURS"}}');
 perform pg_temp.check_it(c->>'allowed'='false','old result cancelled');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Resposta antiga.',(a->>'thread_version')::bigint)->>'allowed'='false','old send cancelled');
 perform pg_temp.check_it((select text='' and intent is null and reply_key is null and routing_reason is null and withdrawn_at is not null from instagram_support.events where mid='withdraw-work'),'content and derivations erased');
 {cost}
 perform pg_temp.check_it((select not human_paused from instagram_support.threads),'no new human pause');
 perform pg_temp.check_it(pg_temp.incoming('100001','withdraw-new')->>'queued'='true','fresh message still accepted');
end $$;
""")

    def test_withdrawal_old_sent_preserves_newer_work(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb;b jsonb;c jsonb;o jsonb;begin
 perform pg_temp.incoming('100001','withdraw-old');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Horario revisado.',(c->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','old-sent-mid');
 perform pg_temp.incoming('100001','withdraw-newer');b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.withdraw('100001','withdraw-old');
 c:=public.ig_support_complete((b->>'event_id')::uuid,(b->>'lease')::uuid,'{"intent":"HOURS"}');
 perform pg_temp.check_it(c->>'allowed'='true','other event lease/version preserved');
 perform pg_temp.check_it((select status='sent' and provider_mid='old-sent-mid' and text='' from instagram_support.outbox where id=(o->>'outbox_id')::uuid),'sent audit kept without content');
end $$;
""")

    def test_withdrawal_urgency_source_restores_human(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb;begin
 perform pg_temp.safety('100001','source-human','HUMAN');
 perform pg_temp.safety('100001','source-urgent','URGENCY');
 perform pg_temp.withdraw('100001','source-urgent');
 a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(a->>'handoff_ack'='true' and a->>'reply_key'='HUMAN','remaining human source governs notice');
 perform pg_temp.check_it((select reason='human' and status='open' from instagram_support.cases),'shared case preserved');
 perform pg_temp.check_it((select routing_reason='human' from instagram_support.events where mid='source-human'),'original source not overwritten by prior urgency');
end $$;
""")

    def test_withdrawal_notice_can_move_only_before_any_attempt(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb;b jsonb;begin
 perform pg_temp.safety('100001','notice-source-a','HUMAN');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.safety('100001','notice-source-b','URGENCY');
 perform pg_temp.withdraw('100001','notice-source-a');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Antigo.',(a->>'thread_version')::bigint)->>'allowed'='false','old ACK invalidated');
 b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(b->>'event_id'<>a->>'event_id' and b->>'reply_key'='URGENCY','only remaining source may send');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.budget_reservations),'no model for ACK');
end $$;
""")

    def test_withdrawal_never_rearms_attempted_notice(self):
        for outcome in ('sent', 'failed', 'uncertain'):
            with self.subTest(outcome=outcome):
                self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb;o jsonb;begin
 perform pg_temp.safety('100001','attempt-source-a','HUMAN');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Aviso WhatsApp revisado.',(a->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'{outcome}',case when '{outcome}'='sent' then 'attempt-mid' else null end);
 perform pg_temp.safety('100001','attempt-source-b','URGENCY');
 perform pg_temp.withdraw('100001','attempt-source-a');
 perform pg_temp.check_it((select notice_attempted from instagram_support.cases),'attempt marker permanent per case');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no second notice after erase');
 perform pg_temp.check_it((select count(*)=1 and bool_and(text='') from instagram_support.outbox),'one attempt, erased content');
 perform pg_temp.check_it((select reason='urgency' from instagram_support.cases),'other source preserved');
end $$;
""")

    def test_withdrawal_during_sending_retains_result_without_retry(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb;c jsonb;o jsonb;begin
 perform pg_temp.incoming('100001','withdraw-sending');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Resposta revisada.',(c->>'thread_version')::bigint);
 perform pg_temp.withdraw('100001','withdraw-sending');
 perform pg_temp.check_it((select status='sending' and text='' from instagram_support.outbox),'started POST audit retained');
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','after-withdraw-mid');
 perform pg_temp.check_it((select status='sent' and text='' and provider_mid='after-withdraw-mid' from instagram_support.outbox),'late result recorded');
 perform pg_temp.check_it((select intent is null and reply_key is null and withdrawn_at is not null from instagram_support.events where mid='withdraw-sending'),'late result does not restore content');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no retry');
end $$;
""")

    def test_withdrawal_preserves_human_assignment_and_pause(self):
        self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb;begin
 perform pg_temp.safety('100001','withdraw-assigned','HUMAN');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform public.ig_support_control('assume',(a->>'thread_id')::uuid,'{{"actor_id":"{ACTOR}"}}');
 perform pg_temp.withdraw('100001','withdraw-assigned');
 perform pg_temp.check_it((select assigned_to='{ACTOR}' and reason='human_assumed' from instagram_support.cases),'manual work preserved');
 perform pg_temp.check_it((select human_paused from instagram_support.threads),'existing human pause preserved');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'withdrawn ACK never follows assume');
end $$;
""")

    def test_withdrawal_clears_only_target_sensitive_labels(self):
        self.check_sql("""
set local role service_role;
do $$ begin
 perform pg_temp.safety('100001','withdraw-only-allergy','ALLERGY');
 perform pg_temp.withdraw('100001','withdraw-only-allergy');
 perform pg_temp.check_it((select not human_paused and pause_reason is null from instagram_support.threads),'automatic route had no pause to retain');
 perform pg_temp.check_it((select reason='message_withdrawn' and summary='' from instagram_support.cases),'case source label cleared');
 perform pg_temp.check_it((select reason='message_withdrawn' and status='suppressed' from instagram_support.alerts),'alert audit retained without allergy label');
 perform pg_temp.check_it((select routing_reason is null and intent is null and reply_key is null from instagram_support.events),'target derived labels cleared');
end $$;
""")

    def test_withdrawal_removes_attempted_notice_derived_from_other_source(self):
        for outcome in ('sent', 'failed', 'uncertain'):
            with self.subTest(outcome=outcome):
                self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb;o jsonb;begin
 perform pg_temp.safety('100001','derived-human','HUMAN');
 perform pg_temp.safety('100001','derived-urgent','URGENCY');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Orientacao urgente e WhatsApp.',(a->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'{outcome}',case when '{outcome}'='sent' then 'derived-sent-mid' else null end);
 perform pg_temp.withdraw('100001','derived-urgent');
 perform pg_temp.check_it((select reason='human' and notice_attempted from instagram_support.cases),'remaining source and attempt retained');
 perform pg_temp.check_it((select status='{outcome}' and text='' from instagram_support.outbox),'attempt audit retained without removed derivation');
 perform pg_temp.check_it((select routing_reason='human' and intent is null and reply_key is null from instagram_support.events where mid='derived-human'),'human source retained, derived urgent notice erased');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no rearmed notice');
end $$;
""")

    def test_withdrawal_of_lower_priority_source_preserves_urgency(self):
        self.check_sql("""
set local role service_role;
do $$ begin
 perform pg_temp.safety('100001','lower-allergy','ALLERGY');
 perform pg_temp.safety('100001','higher-urgency','URGENCY');
 perform pg_temp.withdraw('100001','lower-allergy');
 perform pg_temp.check_it((select reason='urgency' from instagram_support.cases),'higher priority source preserved');
 perform pg_temp.check_it((select not human_paused and pause_reason is null from instagram_support.threads),'automatic route leaves no stale pause label');
 perform pg_temp.check_it((select routing_reason='urgency' and withdrawn_at is null from instagram_support.events where mid='higher-urgency'),'other source retained');
 perform pg_temp.check_it((select reason='urgency' from instagram_support.alerts),'alert follows remaining source');
end $$;
""")

    def test_whatsapp_faq_then_repeated_human_keeps_one_notice_and_case(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb;o jsonb;c jsonb;begin
 perform pg_temp.safety('100001','autonomy-human','HUMAN');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Abra o WhatsApp.',(a->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','autonomy-wa-mid');
 perform pg_temp.incoming('100001','autonomy-hours');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(a->>'handoff_ack'='false','FAQ eligible after WhatsApp');
 c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{"intent":"HOURS"}');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Horario confirmado.',(c->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','autonomy-hours-mid');
 perform pg_temp.safety('100001','autonomy-repeat','HUMAN');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'no repeat notice');
 perform pg_temp.check_it((select count(*)=1 and bool_and(status='open' and notice_attempted) from instagram_support.cases),'one open tracked case');
 perform pg_temp.check_it((select count(*)=2 from instagram_support.outbox),'notice plus FAQ only');
 perform pg_temp.check_it((select not human_paused from instagram_support.threads),'no automatic pause');
end $$;
""")

    def test_sensitive_notice_precedes_faq_and_old_worker_is_invalid(self):
        self.check_sql("""
set local role service_role;
do $$ declare a jsonb;b jsonb;o jsonb;begin
 perform pg_temp.safety('100001','priority-human','HUMAN');a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.safety('100001','priority-urgent','URGENCY');
 perform pg_temp.incoming('100001','priority-faq');
 perform pg_temp.check_it(public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Antigo.',(a->>'thread_version')::bigint)->>'allowed'='false','old generic lease invalid');
 b:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(b->>'reply_key'='URGENCY' and b->>'handoff_ack'='true','urgent first');
 o:=public.ig_support_prepare_send((b->>'event_id')::uuid,(b->>'lease')::uuid,'Procure equipe presente.',(b->>'thread_version')::bigint);
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(b->>'lease')::uuid,'sent','priority-urgent-mid');
 a:=public.ig_support_claim(gen_random_uuid(),1)->0;
 perform pg_temp.check_it(a->>'handoff_ack'='false','FAQ follows notice');
 perform pg_temp.check_it((select count(*)=0 from instagram_support.budget_reservations),'notice never reserved model budget');
end $$;
""")

    def test_close_preserves_current_pause_and_unknown_preserves_open_case(self):
        self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb;t uuid;begin
 perform pg_temp.safety('100001','close-route','HUMAN');select id into t from instagram_support.threads;
 perform public.ig_support_control('close',t,'{{"actor_id":"{ACTOR}"}}');
 perform pg_temp.check_it((select not human_paused from instagram_support.threads),'close keeps auto route unpaused');
 perform pg_temp.safety('100001','close-route-again','HUMAN');
 perform public.ig_support_control('assume',t,'{{"actor_id":"{ACTOR}"}}');
 perform public.ig_support_control('close',t,'{{"actor_id":"{ACTOR}"}}');
 perform pg_temp.check_it((select human_paused and pause_reason='human_assumed' from instagram_support.threads),'close preserves later real pause');
 perform pg_temp.incoming('100001','close-paused-unknown');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'unknown cannot clear real pause');
end $$;
""")

    def test_public_gates_default_false_and_each_required_even_with_model_approval(self):
        self.check_sql("""
update instagram_support.settings set mode='live',paused=false,model_usage_allowed=true,billing_verified=true;
set local role service_role;
do $$ begin
 perform pg_temp.check_it((select not public_data_approved and not public_delivery_verified from instagram_support.settings),'public defaults closed');
 perform pg_temp.check_it(pg_temp.incoming('100001','public-no-consent')->>'queued'='false','test approval does not enable public');
 update instagram_support.settings set public_data_approved=true;
 perform pg_temp.check_it(pg_temp.incoming('100001','public-no-delivery')->>'queued'='false','delivery proof separate');
 update instagram_support.settings set public_data_approved=false,public_delivery_verified=true;
 perform pg_temp.check_it(pg_temp.incoming('100001','public-no-data')->>'queued'='false','data consent separate');
 update instagram_support.settings set mode='test',test_sender_ids=array['100001'];
 perform pg_temp.check_it(pg_temp.incoming('100001','test-owner-still-eligible')->>'queued'='true','owner test stays eligible');
end $$;
""", enable=False)

    def test_fresh_request_binds_first_notice_after_cancelled_source_without_replaying_old(self):
        for cancelled_by in ('global_pause', 'withdrawal'):
            for fresh_kind in ('HUMAN', 'UNKNOWN'):
                cancel = (f"perform public.ig_support_control('pause_global',null,'{{\"actor_id\":\"{ACTOR}\",\"paused\":true}}');"
                          f"perform public.ig_support_control('pause_global',null,'{{\"actor_id\":\"{ACTOR}\",\"paused\":false}}');"
                          if cancelled_by == 'global_pause' else "perform pg_temp.withdraw('100001','cancel-first-source');")
                fresh = ("perform pg_temp.safety('100001','fresh-first-source','HUMAN');a:=public.ig_support_claim(gen_random_uuid(),1)->0;"
                         if fresh_kind == 'HUMAN' else "perform pg_temp.incoming('100001','fresh-first-source');a:=public.ig_support_claim(gen_random_uuid(),1)->0;"
                         "c:=public.ig_support_complete((a->>'event_id')::uuid,(a->>'lease')::uuid,'{\"intent\":\"UNKNOWN\"}');"
                         "perform pg_temp.check_it(c->>'allowed'='true','fresh unknown may supply first notice');"
                         "a:=a||jsonb_build_object('thread_version',c->'thread_version');")
                with self.subTest(cancelled_by=cancelled_by, fresh_kind=fresh_kind):
                    self.check_sql(f"""
set local role service_role;
do $$ declare a jsonb;c jsonb;o jsonb;old_id uuid;begin
 perform pg_temp.safety('100001','cancel-first-source','HUMAN');select id into old_id from instagram_support.events where mid='cancel-first-source';
 {cancel}
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'old notice stays terminal');
 {fresh}
 perform pg_temp.check_it((a->>'event_id')::uuid<>old_id,'new source only');
 o:=public.ig_support_prepare_send((a->>'event_id')::uuid,(a->>'lease')::uuid,'Primeiro WhatsApp.',(a->>'thread_version')::bigint);
 perform pg_temp.check_it(o->>'allowed'='true','first notice allowed on fresh request');
 perform public.ig_support_finish_send((o->>'outbox_id')::uuid,(a->>'lease')::uuid,'sent','first-fresh-confirmed');
 perform pg_temp.safety('100001','fresh-first-repeat','HUMAN');
 perform pg_temp.check_it(public.ig_support_claim(gen_random_uuid(),1)='[]'::jsonb,'notice attempted stays final');
 perform pg_temp.check_it((select count(*)=1 and bool_and(notice_attempted) from instagram_support.cases),'same case one attempt');
 perform pg_temp.check_it((select count(*)=1 from instagram_support.outbox),'no duplicate external effect');
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

    def test_z_concurrent_notice_claim(self):
        self.run_sql(HELPERS + ENABLE + "select pg_temp.safety('900003','concurrent-wa','HUMAN');")
        def claim(_):
            return json.loads(self.run_sql("set role service_role; select public.ig_support_claim('" + str(uuid.uuid4()) + "',1);"))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, range(2)))
        self.assertEqual(sorted(map(len, results)), [0, 1])
        self.assertTrue(next(result[0]["handoff_ack"] for result in results if result))
        self.run_sql("update instagram_support.settings set mode='off',paused=true;")


if __name__ == "__main__":
    unittest.main(verbosity=2)
