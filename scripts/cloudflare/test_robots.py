"""Offline regressions for robots changes; no credentials or network."""

import contextlib
import copy
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("cf", Path(__file__).with_name("cf.py"))
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)


def configuration(managed):
    return {
        "is_robots_txt_managed": managed,
        "bot_preference_sync_enabled": managed,
        "ai_bots_protection": "only_on_ad_pages",
        "ai_training": "disallow",
        "ai_search": "disabled",
        "ai_user": "disabled",
    }


def read(config):
    return {"success": True, "result": copy.deepcopy(config)}


OK = {"success": True}
ERROR = {"success": False, "http": 403, "errors": "offline refusal"}


class RobotsTest(unittest.TestCase):
    def run_command(self, responses, *, apply=True, rollback=False, failure=False):
        output = io.StringIO()
        with patch.object(cf, "zona_id", return_value="test-zone"), \
             patch.object(cf, "api", side_effect=responses) as api, \
             contextlib.redirect_stdout(output):
            args = SimpleNamespace(aplicar=apply, religar=rollback)
            if failure:
                with self.assertRaises(SystemExit) as raised:
                    cf.cmd_robots(args)
                self.assertTrue(raised.exception.code)
                self.assertNotIn("Configuracao e purga conferidas", output.getvalue())
            else:
                cf.cmd_robots(args)
        return api, output.getvalue()

    def test_dry_run_only_reads(self):
        api, output = self.run_command([read(configuration(True))], apply=False)
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET"])
        self.assertIn("Simulacao", output)

    def test_put_refusal_stops_before_readback_and_purge(self):
        api, _ = self.run_command([read(configuration(True)), ERROR], failure=True)
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "PUT"])

    def test_readback_refusal_stops_before_purge(self):
        api, _ = self.run_command([read(configuration(True)), OK, ERROR], failure=True)
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "PUT", "GET"])

    def test_each_divergent_target_stops_before_purge(self):
        for field in ("is_robots_txt_managed", "bot_preference_sync_enabled"):
            with self.subTest(field=field):
                result = configuration(False)
                result[field] = True
                api, _ = self.run_command([read(configuration(True)), OK, read(result)], failure=True)
                self.assertEqual(api.call_count, 3)

    def test_missing_readback_target_is_not_treated_as_false(self):
        result = configuration(False)
        del result["bot_preference_sync_enabled"]
        api, _ = self.run_command([read(configuration(True)), OK, read(result)], failure=True)
        self.assertEqual(api.call_count, 3)

    def test_other_policy_change_stops_without_automatic_rollback(self):
        result = configuration(False)
        result["ai_bots_protection"] = "block"
        api, _ = self.run_command([read(configuration(True)), OK, read(result)], failure=True)
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "PUT", "GET"])

    def test_purge_failure_reports_partial_result(self):
        api, output = self.run_command([read(configuration(True)), OK, read(configuration(False)), ERROR], failure=True)
        self.assertEqual(api.call_count, 4)
        self.assertIn("ERRO", output)

    def test_success_only_writes_both_robots_fields_and_purges_two_urls(self):
        api, output = self.run_command([read(configuration(True)), OK, read(configuration(False)), OK])
        self.assertEqual(api.call_args_list[1].args[2], {
            "is_robots_txt_managed": False, "bot_preference_sync_enabled": False})
        self.assertEqual(api.call_args_list[-1].args[2], {"files": [
            "https://www.sirfisher.com.br/robots.txt", "https://sirfisher.com.br/robots.txt"]})
        self.assertIn("Configuracao e purga conferidas", output)

    def test_already_targeted_still_verifies_without_put(self):
        api, _ = self.run_command([read(configuration(False)), read(configuration(False)), OK])
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "GET", "POST"])

    def test_rollback_verifies_both_targets_and_preserves_other_policies(self):
        api, _ = self.run_command([read(configuration(False)), OK, read(configuration(True)), OK], rollback=True)
        self.assertEqual(api.call_args_list[1].args[2], {
            "is_robots_txt_managed": True, "bot_preference_sync_enabled": True})

    def test_malformed_readback_and_initial_read_fail(self):
        for result in (ERROR, {"success": True, "result": None}):
            with self.subTest(result=result):
                api, _ = self.run_command([read(configuration(True)), OK, result], failure=True)
                self.assertEqual(api.call_count, 3)
                api, _ = self.run_command([result], failure=True)
                self.assertEqual(api.call_count, 1)


if __name__ == "__main__":
    unittest.main()
