"""Regressions for preserving unrelated Cloudflare rules; no network."""

import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location("cf", Path(__file__).with_name("cf.py"))
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)

RULE = cf.REGRA_REDIRECIONAMENTO
PHASE = "http_request_dynamic_redirect"
OK = {"success": True}


class RulePreservationTest(unittest.TestCase):
    def test_existing_rule_is_patched_without_replacing_other_rules(self):
        current = {"success": True, "result": {"id": "set", "rules": [
            {"id": "apex", "description": RULE["description"]},
            {"id": "webmail", "description": "Webmail: atalho HTTPS"},
        ]}}
        with patch.object(cf, "api", side_effect=[current, OK]) as api:
            self.assertTrue(cf.gravar_regra("zone", PHASE, RULE)["success"])
        self.assertEqual(api.call_args_list[-1].args, (
            "PATCH", "/zones/zone/rulesets/set/rules/apex", RULE))

    def test_new_rule_is_appended(self):
        current = {"success": True, "result": {"id": "set", "rules": [
            {"id": "unrelated", "description": "Existing rule"}]}}
        with patch.object(cf, "api", side_effect=[current, OK]) as api:
            cf.gravar_regra("zone", PHASE, RULE)
        self.assertEqual(api.call_args_list[-1].args, (
            "POST", "/zones/zone/rulesets/set/rules", RULE))

    def test_only_missing_entrypoint_allows_creation(self):
        with patch.object(cf, "api", side_effect=[{"success": False, "http": 404}, OK]) as api:
            cf.gravar_regra("zone", PHASE, RULE)
        self.assertEqual(api.call_args_list[-1].args, (
            "PUT", f"/zones/zone/rulesets/phases/{PHASE}/entrypoint", {"rules": [RULE]}))
        with patch.object(cf, "api", return_value={"success": False, "http": 403}) as api:
            self.assertFalse(cf.gravar_regra("zone", PHASE, RULE)["success"])
        self.assertEqual(api.call_count, 1)

    def test_incomplete_or_ambiguous_sets_do_not_write(self):
        invalid = [None, {}, {"id": "set"}, {"id": "set", "rules": [
            {"description": RULE["description"]}]}, {"id": "set", "rules": [
                {"id": "a", "description": RULE["description"]},
                {"id": "b", "description": RULE["description"]}]}]
        for result in invalid:
            with self.subTest(result=result), patch.object(cf, "api", return_value={
                "success": True, "result": result}) as api:
                self.assertFalse(cf.gravar_regra("zone", PHASE, RULE)["success"])
                self.assertEqual(api.call_count, 1)

    def test_rule_creation_is_not_repeated_after_uncertain_network_result(self):
        with patch.object(cf, "credencial", return_value="offline"), \
             patch.object(cf.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")) as request, \
             patch.object(cf.time, "sleep") as sleep:
            result = cf.api("POST", "/zones/zone/rulesets/set/rules", RULE)
        self.assertFalse(result["success"])
        self.assertEqual(request.call_count, 1)
        sleep.assert_not_called()

    def test_diagnostic_distinguishes_denied_access_from_empty_rules(self):
        def response(method, path, body=None):
            self.assertEqual(method, "GET")
            if path.endswith("/dns_records?per_page=200") or "/certificate_packs" in path:
                return {"success": True, "result": []}
            return {"success": False, "http": 403}
        output = io.StringIO()
        with patch.object(cf, "api", side_effect=response), \
             patch.object(cf, "zona_id", return_value="zone"), contextlib.redirect_stdout(output):
            cf.cmd_diagnostico(None)
        self.assertIn("regras http_request_firewall_custom: indisponivel (HTTP 403)", output.getvalue())
        self.assertIn("alertas: indisponivel (HTTP 403)", output.getvalue())


if __name__ == "__main__":
    unittest.main()
