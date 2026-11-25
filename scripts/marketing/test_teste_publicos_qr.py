import copy
import datetime as dt
import json
import unittest
from unittest.mock import patch

import meta
import teste_publicos_qr as test

NOW = dt.datetime(2026, 11, 25, 18, tzinfo=dt.timezone.utc)


class Clock(dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)


class Fake:
    def __init__(self, fail_activation=False):
        self.rows = {}
        self.writes = []
        self.next_id = 10000000
        self.fail_activation = fail_activation

    def request(self, path, params, write=False):
        if not write:
            return copy.deepcopy(self.rows[path])
        self.writes.append((path, params))
        if set(params) == {'status'}:
            if self.fail_activation and params['status'] == 'ACTIVE' and self.rows[path].get('name') == test.CAMPAIGN_NAMES['B']:
                raise RuntimeError('Falha de ativação simulada')
            self.rows[path]['status'] = params['status']
            return {'success': True}
        self.next_id += 1
        identifier = str(self.next_id)
        row = {**params, 'id': identifier, 'account_id': meta.AD_ACCOUNT}
        if path.endswith('/adsets'):
            row['targeting'] = json.loads(row['targeting'])
            if row.get('promoted_object'):
                row['promoted_object'] = json.loads(row['promoted_object'])
        if path.endswith('/ads'):
            creative = self.rows[json.loads(row['creative'])['creative_id']]
            row['creative'] = {**creative, 'call_to_action_type': 'LEARN_MORE'}
        if path.endswith('/ad_studies'):
            assert meta.qr_study_allowed(path, params, self.verified_split_campaigns)
            row['cells'] = {'data': json.loads(row['cells'])}
        self.rows[identifier] = row
        return {'id': identifier}


def prepare_fake():
    client = Fake()
    receipt = {}
    saved = []
    with patch.object(test, 'preflight', return_value={'verified': True}):
        test.create(client, receipt, lambda r: saved.append(copy.deepcopy(r)))
    receipt['destination_verified'] = {'A': test.LINK, 'B': test.LINK}
    return client, receipt, saved


class TestComparison(unittest.TestCase):
    def setUp(self):
        clock = patch.object(test.dt, 'datetime', Clock)
        clock.start()
        self.addCleanup(clock.stop)

    def test_total_media_and_reserve_fit_approved_total(self):
        plan = test.plan()
        budgets = [x['adset']['lifetime_budget'] for x in plan['arms'].values()]
        self.assertEqual(budgets, [13000, 13000])
        self.assertEqual(sum(budgets) / 100, plan['media_total_brl'])
        self.assertEqual(plan['media_total_brl'] + plan['reserve_brl'], plan['approved_total_brl'])
        self.assertEqual(plan['approved_total_brl'], 300)
        self.assertTrue(all(x['campaign']['status'] == 'PAUSED' for x in plan['arms'].values()))

    def test_schedule_is_seven_days_in_fortaleza(self):
        start, end = dt.datetime.fromisoformat(test.START), dt.datetime.fromisoformat(test.END)
        self.assertEqual((start.hour, end.hour), (9, 9))
        self.assertEqual(start.utcoffset(), dt.timedelta(hours=-3))
        self.assertEqual(end - start, dt.timedelta(days=7))
        self.assertEqual(test.timestamp('2026-11-26T12:00:00+0000'), test.timestamp(test.START))

    def test_only_audience_strategy_changes(self):
        a, b = test.adset_params('A', '123'), test.adset_params('B', '123')
        for key in a:
            if key not in {'name', 'targeting'}:
                self.assertEqual(a[key], b[key])
        ta, tb = json.loads(a['targeting']), json.loads(b['targeting'])
        self.assertNotIn('custom_audiences', ta)
        self.assertEqual(tb.pop('custom_audiences'), [{'id': test.SIMILAR}])
        self.assertEqual(ta, tb)
        self.assertEqual(ta['excluded_custom_audiences'], [{'id': test.SEED}])
        ca, cb = test.creative_params('A'), test.creative_params('B')
        for key in ca:
            if key not in {'name', 'url_tags'}:
                self.assertEqual(ca[key], cb[key])
        self.assertNotEqual(ca['url_tags'], cb['url_tags'])

    def test_all_entities_created_paused_and_random_cells_verified(self):
        client, receipt, saved = prepare_fake()
        self.assertEqual(receipt['state'], 'prepared_paused_verified')
        self.assertTrue(all(p.get('status') == 'PAUSED' for path, p in client.writes
                            if path.endswith(('/ads', '/adsets', '/campaigns'))))
        self.assertEqual(len(saved[0]['arms']), 2)
        self.assertIn('pending', saved[0])
        self.assertNotIn('pending', saved[-1])

    def test_prepare_again_does_not_duplicate_entities(self):
        client, receipt, _ = prepare_fake()
        count = len(client.writes)
        with patch.object(test, 'preflight', return_value={}):
            test.create(client, receipt, lambda r: None)
        self.assertEqual(len(client.writes), count)

    def test_pending_mutation_is_not_repeated(self):
        fake = Fake()
        with self.assertRaises(RuntimeError):
            test.create(fake, {'pending': {'path': 'unknown'}}, lambda r: None)
        self.assertEqual(fake.writes, [])

    def test_activation_rechecks_budget_before_any_spend(self):
        client, receipt, _ = prepare_fake()
        client.rows[receipt['arms']['B']['adset']]['lifetime_budget'] = 14000
        before = len(client.writes)
        with patch.object(test, 'preflight', return_value={}), self.assertRaises(RuntimeError):
            test.activate(client, receipt, lambda r: None)
        self.assertEqual(len(client.writes), before)

    def test_unverified_cta_prevents_activation(self):
        client, receipt, _ = prepare_fake()
        receipt.pop('destination_verified')
        before = len(client.writes)
        with self.assertRaises(RuntimeError):
            test.activate(client, receipt, lambda r: None)
        self.assertEqual(len(client.writes), before)

    def test_bad_source_or_expansion_blocks_activation(self):
        for key, value in [('targeting_optimization_types', [{'key': 'custom_audience', 'value': 1}]),
                           ('promoted_object', {'pixel_id': '999'})]:
            client, receipt, _ = prepare_fake()
            client.rows[receipt['arms']['B']['adset']][key] = value
            before = len(client.writes)
            with patch.object(test, 'preflight', return_value={}), self.assertRaises(RuntimeError):
                test.activate(client, receipt, lambda r: None)
            self.assertEqual(len(client.writes), before)

    def test_bad_study_cell_prevents_activation(self):
        client, receipt, _ = prepare_fake()
        client.rows[receipt['study']]['cells']['data'][0]['treatment_percentage'] = 80
        with patch.object(test, 'preflight', return_value={}), self.assertRaises(RuntimeError):
            test.activate(client, receipt, lambda r: None)

    def test_activate_only_own_entities_and_rollback_both_campaigns(self):
        client, receipt, _ = prepare_fake()
        client.fail_activation = True
        with patch.object(test, 'preflight', return_value={}), self.assertRaises(RuntimeError):
            test.activate(client, receipt, lambda r: None)
        for arm in ('A', 'B'):
            self.assertEqual(client.rows[receipt['arms'][arm]['campaign']]['status'], 'PAUSED')
        self.assertEqual(receipt['state'], 'activation_failed_check_status')

    def test_active_test_cannot_be_recreated(self):
        client, receipt, _ = prepare_fake()
        with patch.object(test, 'preflight', return_value={}):
            test.activate(client, receipt, lambda r: None)
        self.assertEqual(receipt['state'], 'active_scheduled_verified')
        before = len(client.writes)
        with self.assertRaises(RuntimeError):
            test.create(client, receipt, lambda r: None)
        self.assertEqual(len(client.writes), before)

    def test_study_guard_limits_business_campaigns_and_division(self):
        path = meta.QR_BUSINESS + '/ad_studies'
        campaigns = ['11111111', '22222222']
        params = test.study_params(campaigns)
        self.assertTrue(meta.qr_study_allowed(path, params, campaigns))
        self.assertFalse(meta.qr_study_allowed(path, params))
        self.assertFalse(meta.qr_study_allowed('999/ad_studies', params, campaigns))
        self.assertFalse(meta.qr_study_allowed(path, {**params, 'daily_budget': 10000}, campaigns))
        cells = json.loads(params['cells'])
        cells[0]['campaigns'] = ['9999999']
        self.assertFalse(meta.qr_study_allowed(path, {**params, 'cells': json.dumps(cells)}, campaigns))

    def test_targeting_update_requires_exact_preverified_paused_adset(self):
        targeting = test.targeting('B')
        params = {'targeting': json.dumps(targeting)}
        verified = {'12345678': targeting}
        self.assertFalse(meta.qr_targeting_update_allowed('12345678', params))
        self.assertTrue(meta.qr_targeting_update_allowed('12345678', params, verified))
        self.assertFalse(meta.qr_targeting_update_allowed('87654321', params, verified))
        self.assertFalse(meta.qr_targeting_update_allowed('12345678', {**params, 'lifetime_budget': 999999}, verified))

    def test_report_before_start_does_not_request_insights(self):
        self.assertEqual(test.report(None, {}, '2026-11-25')['state'], 'not_started')

    def test_summary_uses_landing_page_views_and_does_not_sum_reach(self):
        rows = [{'spend': '10.50', 'impressions': '200', 'reach': '100', 'inline_link_clicks': '10',
                 'actions': [{'action_type': 'landing_page_view', 'value': '7'}]},
                {'spend': '4.50', 'impressions': '100', 'reach': '70', 'inline_link_clicks': '5',
                 'actions': [{'action_type': 'landing_page_view', 'value': '3'}]}]
        summary = test.summarize(rows)
        self.assertEqual(summary['landing_page_views_reported'], 10)
        self.assertEqual(summary['cost_per_landing_page_view_brl'], 1.5)
        self.assertNotIn('reach', summary)

    def test_missing_actions_and_zero_views_do_not_produce_fake_cpa(self):
        self.assertIsNone(test.summarize([{'spend': '10'}])['landing_page_views_reported'])
        self.assertIsNone(test.summarize([{'spend': '10', 'actions': []}])['cost_per_landing_page_view_brl'])


if __name__ == '__main__':
    unittest.main()
