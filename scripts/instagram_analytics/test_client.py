"""Regressoes offline de escopo, cobertura e ausencia de dados; sem credencial real."""
import datetime as dt
import io
import json
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from scripts.instagram_analytics.client import AnalyticsError, Cache, InstagramAnalytics, sanitize

IG = "17841400000000001"
POST = "17900000000000001"
TOKEN = "TOKEN-DE-TESTE-SEM-VALIDADE"


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="sirfisher-ig-test-")
        self.addCleanup(self.directory.cleanup)
        self.cache = Cache(self.directory.name)
        self.requests = []

    def transport(self, path, params):
        self.requests.append((path, dict(params)))
        if path == "me/accounts":
            return {"data": [{"instagram_business_account": {"id": IG, "username": "sirfisherfc"}}]}
        if path == IG:
            return {"id": IG, "username": "sirfisherfc", "followers_count": 5}
        if path.endswith("/media"):
            return {"data": [{"id": POST, "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(), "media_type": "VIDEO"}]}
        if path.endswith("/stories"):
            return {"data": []}
        if path.endswith("/insights"):
            return {"data": [{"name": params["metric"], "period": "lifetime", "total_value": {"value": 0}}]}
        raise AssertionError("Rota inesperada no teste")

    def client(self, **kwargs):
        return InstagramAnalytics(token=TOKEN, fixed_id="", cache=self.cache, transport=kwargs.pop("transport", self.transport), **kwargs)

    def test_identity_requires_exact_username(self):
        def wrong(path, params):
            return {"data": [{"instagram_business_account": {"id": IG, "username": "outra_conta"}}]}
        with self.assertRaises(AnalyticsError):
            self.client(transport=wrong).identity()

    def test_fixed_id_is_also_verified(self):
        c = InstagramAnalytics(token=TOKEN, fixed_id=IG, cache=self.cache, transport=lambda *a: {"id": IG, "username": "outra_conta"})
        with self.assertRaises(AnalyticsError):
            c.identity()

    def test_fixed_id_rejects_path_injection(self):
        c = InstagramAnalytics(token=TOKEN, fixed_id="../me/messages", cache=self.cache, transport=self.transport)
        with self.assertRaises(AnalyticsError):
            c.identity()
        self.assertFalse(self.requests)

    def test_unowned_media_rejected_before_insights(self):
        with self.assertRaises(AnalyticsError):
            self.client().media_insights(POST)
        self.assertFalse(any(p.endswith("/insights") for p, _ in self.requests))

    def test_listed_owned_media_can_be_read(self):
        self.client().media()
        result = self.client().media_insights(POST, ["reach"])
        self.assertEqual(result["data"][0]["status"], "available")
        self.assertIn("acumuladas", result["coverage"])

    def test_ownership_does_not_cross_token_scope(self):
        self.client().media()
        c = InstagramAnalytics(token="OUTRO-TOKEN-FALSO", fixed_id=IG, cache=self.cache, transport=self.transport)
        with self.assertRaises(AnalyticsError):
            c.media_insights(POST)

    def test_ownership_does_not_cross_confirmed_account_id(self):
        self.client().media()
        new_id = "17841400000000002"
        def migrated(path, params):
            if path == new_id:
                return {"id": new_id, "username": "sirfisherfc"}
            raise AssertionError("Nao deve consultar a midia da identidade anterior")
        c = InstagramAnalytics(token=TOKEN, fixed_id=new_id, cache=self.cache, transport=migrated)
        with self.assertRaises(AnalyticsError):
            c.media_insights(POST)

    def test_successful_reads_are_shared_from_cache(self):
        self.client().identity()
        result = self.client().identity()
        self.assertEqual(result["http_reads"], 0)
        self.assertTrue(all(r["cache"] for r in result["reads"]))

    def test_explicit_identity_refresh_revalidates_authentication(self):
        self.client().identity()
        result = self.client().identity(refresh=True)
        self.assertEqual(result["http_reads"], 2)
        self.assertTrue(all(not r["cache"] for r in result["reads"]))

    def test_paging_urls_never_reach_cache_or_output(self):
        secret = {"paging": {"next": "https://graph.facebook.com/media?access_token="+TOKEN, "cursors": {"after": "CURSOR"}}, "data": []}
        cleaned = sanitize(secret, TOKEN)
        self.assertNotIn(TOKEN, json.dumps(cleaned))
        self.assertNotIn("next", cleaned["paging"])
        self.assertEqual(cleaned["paging"]["cursors"]["after"], "CURSOR")

    def test_invalid_window_and_limits_fail(self):
        for days in (0, 31, True, "30"):
            with self.subTest(days=days), self.assertRaises(AnalyticsError):
                self.client().media(days=days)
        with self.assertRaises(AnalyticsError):
            self.client().media(max_pages=5)
        with self.assertRaises(AnalyticsError):
            self.client().account_insights(end_date="2099-01-01")

    def test_media_closed_window_excludes_newer_posts(self):
        end_date = (dt.datetime.now(dt.timezone.utc).date()-dt.timedelta(days=10)).isoformat()
        result = self.client().media(days=3, end_date=end_date)
        self.assertEqual(result["count"], 0)
        params = next(params for path, params in self.requests if path.endswith("/media"))
        self.assertLess(params["until"], dt.datetime.now(dt.timezone.utc).timestamp())

    def test_only_allowlisted_metric_names(self):
        for metrics in (["../comments"], ["reach", "reach"], [["reach"]]):
            with self.subTest(metrics=metrics), self.assertRaises(AnalyticsError):
                self.client().account_insights(metrics=metrics)

    def test_missing_metric_is_not_zero(self):
        def no_data(path, params):
            return {"data": []} if path.endswith("/insights") else self.transport(path, params)
        metric = self.client(transport=no_data).account_insights(metrics=["reach"])["data"][0]
        self.assertEqual(metric["status"], "unavailable")
        self.assertIsNone(metric["response"])

    def test_empty_values_are_not_zero(self):
        def no_data(path, params):
            return {"data": [{"name": "reach", "values": []}]} if path.endswith("/insights") else self.transport(path, params)
        self.assertEqual(self.client(transport=no_data).account_insights(metrics=["reach"])["data"][0]["status"], "unavailable")

    def test_actual_zero_is_available(self):
        metric = self.client().account_insights(metrics=["reach"])["data"][0]
        self.assertEqual(metric["status"], "available")
        self.assertEqual(metric["response"][0]["total_value"]["value"], 0)

    def test_one_metric_error_preserves_the_others(self):
        def partial(path, params):
            if path.endswith("/insights") and params["metric"] == "views":
                raise AnalyticsError("Metrica nao suportada neste formato")
            return self.transport(path, params)
        results = self.client(transport=partial).account_insights(metrics=["views", "reach"])["data"]
        self.assertEqual([r["status"] for r in results], ["unavailable", "available"])

    def test_arbitrary_routes_and_auth_overrides_rejected(self):
        c = self.client()
        for path in ("me/messages", POST+"/comments", POST+"/media_publish", "https://evil.invalid", "../oauth"):
            with self.subTest(path=path), self.assertRaises(AnalyticsError):
                c._http(path, {})
        with self.assertRaises(AnalyticsError):
            c._http(IG, {"method": "POST"})

    def test_transport_uses_get_header_auth_and_redacts_errors(self):
        error = urllib.error.HTTPError("https://graph.facebook.com/", 400, "bad", {}, io.BytesIO(json.dumps({"error": {"code": 100, "message": "falha access_token="+TOKEN}}).encode()))
        with patch("urllib.request.build_opener") as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaises(AnalyticsError) as raised:
                self.client()._http(IG, {"fields": "id"})
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.method, "GET")
            self.assertNotIn(TOKEN, request.full_url)
            self.assertEqual(request.get_header("Authorization"), "Bearer "+TOKEN)
            self.assertNotIn(TOKEN, str(raised.exception))

    def test_paginated_media_is_bounded_and_deduplicated(self):
        def paged(path, params):
            response = self.transport(path, params)
            if path.endswith("/media"):
                response["paging"] = {"next": "https://graph.facebook.com/?access_token="+TOKEN, "cursors": {"after": "CURSOR"}}
            return response
        result = self.client(transport=paged).media(max_pages=2)
        self.assertEqual(result["count"], 1)
        self.assertTrue(result["pagination_truncated"])
        self.assertEqual(sum(p.endswith("/media") for p, _ in self.requests), 2)
        self.assertNotIn(TOKEN, json.dumps(result))


if __name__ == "__main__":
    unittest.main()
