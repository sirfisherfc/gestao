"""Offline regressions for the AI crawler preferences command; no credentials or network."""

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


def configuration(training):
    return {
        "is_robots_txt_managed": False,
        "bot_preference_sync_enabled": False,
        "ai_bots_protection": "only_on_ad_pages",
        "ai_training": training,
        "ai_search": "disabled",
        "ai_user": "disabled",
    }


def read(config):
    return {"success": True, "result": copy.deepcopy(config)}


OK = {"success": True}
ERROR = {"success": False, "http": 403, "errors": "offline refusal"}


class AiPreferencesTest(unittest.TestCase):
    def run_command(self, responses, *, apply=True, rollback=False, failure=False):
        output = io.StringIO()
        with patch.object(cf, "zona_id", return_value="test-zone"), \
             patch.object(cf, "api", side_effect=responses) as api, \
             contextlib.redirect_stdout(output):
            args = SimpleNamespace(aplicar=apply, religar=rollback)
            if failure:
                with self.assertRaises(SystemExit) as raised:
                    cf.cmd_ia(args)
                self.assertTrue(raised.exception.code)
                self.assertNotIn("Preferencias conferidas", output.getvalue())
            else:
                cf.cmd_ia(args)
        return api, output.getvalue()

    def test_dry_run_only_reads(self):
        api, output = self.run_command([read(configuration("disallow"))], apply=False)
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET"])
        self.assertIn("Simulacao", output)

    def test_success_writes_only_the_divergent_field(self):
        api, output = self.run_command([read(configuration("disallow")), OK, read(configuration("disabled"))])
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "PUT", "GET"])
        self.assertEqual(api.call_args_list[1].args[2], {"ai_training": "disabled"})
        self.assertIn("Preferencias conferidas", output)

    def test_put_refusal_stops_before_readback(self):
        api, _ = self.run_command([read(configuration("disallow")), ERROR], failure=True)
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "PUT"])

    def test_readback_with_old_value_fails(self):
        api, _ = self.run_command([read(configuration("disallow")), OK, read(configuration("disallow"))], failure=True)
        self.assertEqual(api.call_count, 3)

    def test_missing_readback_field_fails(self):
        result = configuration("disabled")
        del result["ai_user"]
        api, _ = self.run_command([read(configuration("disallow")), OK, read(result)], failure=True)
        self.assertEqual(api.call_count, 3)

    def test_other_policy_change_stops(self):
        result = configuration("disabled")
        result["fight_mode"] = True
        api, _ = self.run_command([read(configuration("disallow")), OK, read(result)], failure=True)
        self.assertEqual(api.call_count, 3)

    def test_coupled_legacy_field_is_reported_not_rejected(self):
        result = configuration("disabled")
        result["ai_bots_protection"] = "disabled"
        api, output = self.run_command([read(configuration("disallow")), OK, read(result)])
        self.assertEqual(api.call_args_list[1].args[2], {"ai_training": "disabled"})
        self.assertIn("ai_bots_protection (legado, acoplado): only_on_ad_pages -> disabled", output)
        self.assertIn("Preferencias conferidas", output)

    def test_already_released_verifies_without_put(self):
        api, _ = self.run_command([read(configuration("disabled")), read(configuration("disabled"))])
        self.assertEqual([c.args[0] for c in api.call_args_list], ["GET", "GET"])

    def test_rollback_restores_training_block_only(self):
        api, _ = self.run_command([read(configuration("disabled")), OK, read(configuration("disallow"))], rollback=True)
        self.assertEqual(api.call_args_list[1].args[2], {"ai_training": "disallow"})

    def test_malformed_reads_fail(self):
        for result in (ERROR, {"success": True, "result": None}):
            with self.subTest(result=result):
                api, _ = self.run_command([result], failure=True)
                self.assertEqual(api.call_count, 1)
                api, _ = self.run_command([read(configuration("disallow")), OK, result], failure=True)
                self.assertEqual(api.call_count, 3)


if __name__ == "__main__":
    unittest.main()
