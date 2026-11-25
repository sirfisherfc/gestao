import copy
import io
import json
import unittest
from unittest.mock import patch

import meta
import publicos_qr as qr


def seed():
    return {'id': '123456789', 'account_id': meta.AD_ACCOUNT, 'name': meta.QR_NAME,
            'subtype': 'WEBSITE', 'rule': json.dumps(meta.QR_RULE)}


def similar():
    return {'id': '987654321', 'account_id': meta.AD_ACCOUNT, 'name': meta.QR_LOOKALIKE,
            'subtype': 'LOOKALIKE', 'lookalike_spec': {'ratio': 0.01,
                'origin': [{'id': seed()['id']}]}}


class Fake:
    def __init__(self, rows=None, fail_similar=False, fail_read=False):
        self.rows = rows or []
        self.fail_similar = fail_similar
        self.fail_read = fail_read
        self.writes = []

    def request(self, path, params, write=False):
        if path == 'act_' + meta.AD_ACCOUNT and not write:
            return {'id': path, 'adspixels': {'data': [{'id': meta.QR_PIXEL, 'name': 'Sir Fisher - Website'}]},
                    'customaudiences': {'data': self.rows}}
        if path == 'me/permissions':
            return {'data': [{'permission': 'ads_management', 'status': 'granted'}]}
        if write:
            assert meta.qr_creation_allowed(path, params, getattr(self, 'verified_qr_seed', None))
            self.writes.append(params)
            if params.get('subtype') == 'LOOKALIKE' and self.fail_similar:
                raise RuntimeError('Origem ainda insuficiente para semelhante.')
            row = seed() if params.get('name') == meta.QR_NAME else similar()
            self.rows.append(row)
            return {'id': row['id']}
        if self.fail_read:
            raise RuntimeError('Falha de releitura.')
        return next(r for r in self.rows if r['id'] == path)


class QRContract(unittest.TestCase):
    def test_preview_writes_nothing(self):
        fake = Fake()
        self.assertEqual(qr.prepare(fake)['state'], 'preview')
        self.assertEqual(fake.writes, [])

    def test_create_verify_and_idempotence(self):
        fake = Fake()
        self.assertEqual(qr.prepare(fake, True)['state'], 'created_or_existing_and_verified')
        self.assertEqual(len(fake.writes), 2)
        qr.prepare(fake, True)
        self.assertEqual(len(fake.writes), 2)

    def test_seed_survives_when_lookalike_is_pending(self):
        fake = Fake(fail_similar=True)
        result = qr.prepare(fake, True)
        self.assertEqual(result['state'], 'website_verified_lookalike_pending')
        self.assertEqual(result['website']['id'], seed()['id'])

    def test_created_id_checkpoint_before_read_failure(self):
        saved = []
        with self.assertRaises(RuntimeError):
            qr.prepare(Fake(fail_read=True), True, lambda r: saved.append(copy.deepcopy(r)))
        self.assertEqual(saved[0]['website']['id'], seed()['id'])

    def test_different_rule_does_not_get_overwritten(self):
        row = {**seed(), 'rule': '{}'}
        fake = Fake([row])
        with self.assertRaises(RuntimeError):
            qr.prepare(fake, True)
        self.assertEqual(fake.writes, [])

    def test_api_rule_with_numeric_pixel_id(self):
        rule = copy.deepcopy(meta.QR_RULE)
        rule['inclusions']['rules'][0]['event_sources'][0]['id'] = int(meta.QR_PIXEL)
        self.assertEqual(qr.verify_seed({**seed(), 'rule': json.dumps(rule)}), seed()['id'])

    def test_duplicates_block_creation(self):
        fake = Fake([seed(), seed()])
        with self.assertRaises(RuntimeError):
            qr.prepare(fake, True)
        self.assertEqual(fake.writes, [])

    def test_different_account_and_similar_source_are_rejected(self):
        with self.assertRaises(RuntimeError):
            qr.verify_seed({**seed(), 'account_id': '999'})
        with self.assertRaises(RuntimeError):
            qr.verify_similar(similar(), '44444444')

    def test_create_only_exact_qr_rules(self):
        params = qr.website_params()
        path = 'act_' + meta.AD_ACCOUNT + '/customaudiences'
        self.assertTrue(meta.qr_creation_allowed(path, params))
        for key, value in [('name', 'outro'), ('retention_days', 30), ('prefill', 'false'),
                           ('rule', '{}'), ('rule', 'invalid-json')]:
            self.assertFalse(meta.qr_creation_allowed(path, {**params, key: value}))
        self.assertFalse(meta.qr_creation_allowed('act_999/customaudiences', params))
        self.assertFalse(meta.qr_creation_allowed(path, {**params, 'daily_budget': 10000}))
        self.assertFalse(meta.qr_creation_allowed(path, {**params, 'subtype': 'WEBSITE'}))

    def test_lookalike_requires_verified_source_and_no_location(self):
        params = qr.similar_params(seed()['id'])
        path = 'act_' + meta.AD_ACCOUNT + '/customaudiences'
        self.assertFalse(meta.qr_creation_allowed(path, params))
        self.assertTrue(meta.qr_creation_allowed(path, params, seed()['id']))
        for spec in [{'ratio': 0.1}, {'ratio': 0.01, 'country': 'BR'}]:
            self.assertFalse(meta.qr_creation_allowed(path, {**params, 'lookalike_spec': json.dumps(spec)}, seed()['id']))

    def test_guard_routes_only_this_creation_to_v27(self):
        client = object.__new__(meta.Meta)
        client.token, client.page_token, client.reads = 'secret', None, 0
        urls = []
        def response(req, **kwargs):
            urls.append(req.full_url)
            return io.BytesIO(b'{"id":"123456789"}')
        opener = type('O', (), {'open': staticmethod(response)})
        with patch.object(meta.urllib.request, 'build_opener', return_value=opener):
            client.request('act_' + meta.AD_ACCOUNT + '/customaudiences', qr.website_params(), write=True)
            client.request('act_' + meta.AD_ACCOUNT, {'fields': 'id'})
        self.assertIn('/v27.0/', urls[0])
        self.assertIn('/v26.0/', urls[1])
        self.assertNotIn('secret', ''.join(urls))


if __name__ == '__main__':
    unittest.main()
