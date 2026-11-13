import datetime as dt
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.marketing import impulsionar, meta

AGORA = dt.datetime(2026, 11, 13, 20, tzinfo=dt.timezone.utc)
ITEM = {'nome': 'teste', 'media_id': '123456789', 'link': 'https://www.sirfisher.com.br/', 'cta': 'LEARN_MORE',
        'utm_campaign': 'x', 'orcamento_total': 140, 'fim': '2026-11-21T00:00:00-03:00', 'centro': [-3.7, -38.5]}


def cliente():
    m = object.__new__(meta.Meta)
    m.token, m.page_token, m.reads = 'segredo', None, 0
    return m


class Validacao(unittest.TestCase):
    def test_soma_dentro_do_teto(self):
        self.assertEqual(impulsionar.validar({'itens': [ITEM, {**ITEM, 'orcamento_total': 120}]}, 300, AGORA), 260)

    def test_soma_acima_do_teto(self):
        with self.assertRaises(ValueError):
            impulsionar.validar({'itens': [ITEM, {**ITEM, 'orcamento_total': 200}]}, 300, AGORA)

    def test_link_com_parametro_ou_outro_dominio(self):
        for link in ('https://www.sirfisher.com.br/?utm_source=x', 'https://example.com/'):
            with self.assertRaises(ValueError):
                impulsionar.validar({'itens': [{**ITEM, 'link': link}]}, 300, AGORA)

    def test_fim_obrigatorio_com_fuso_e_proximo(self):
        for fim in ('2026-11-21T00:00:00', '2027-02-01T00:00:00-03:00'):
            with self.assertRaises(ValueError):
                impulsionar.validar({'itens': [{**ITEM, 'fim': fim}]}, 300, AGORA)

    def test_agenda_em_horario_local(self):
        a = impulsionar.agenda({'agenda': {'dias': [1, 2, 3, 4, 5], 'inicio': '07:00', 'fim': '14:00'}})
        self.assertIn('"start_minute": 420', a['adset_schedule'])
        self.assertIn('"timezone_type": "USER"', a['adset_schedule'])


class Contrato(unittest.TestCase):
    def test_bloqueia_gravacao_fora_das_rotas(self):
        for path, params in ((f'act_{meta.AD_ACCOUNT}/customaudiences', {}), ('1234567', {'status': 'DELETED'}),
                             ('1234567', {'status': 'ACTIVE', 'daily_budget': 99999}), ('act_999/campaigns', {})):
            with self.assertRaises(RuntimeError):
                cliente().request(path, params, write=True)

    def test_permite_criar_anuncio_e_pausar(self):
        resposta = lambda *a, **k: io.BytesIO(b'{"id": "1"}')
        opener = type('O', (), {'open': staticmethod(resposta)})
        with patch.object(meta.urllib.request, 'build_opener', return_value=opener):
            self.assertEqual(cliente().request(f'act_{meta.AD_ACCOUNT}/ads', {'name': 'a'}, write=True), {'id': '1'})
            self.assertEqual(cliente().request('1234567', {'status': 'PAUSED'}, write=True), {'id': '1'})


if __name__ == '__main__':
    unittest.main()
