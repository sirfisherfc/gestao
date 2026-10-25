"""Regressoes offline para horarios especiais; nao le credenciais nem acessa APIs."""

import copy
import datetime as dt
import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location("gbp", Path(__file__).with_name("gbp.py"))
gbp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gbp)


def periodo(data, abre=9, fecha=22, minuto=15, fim=None):
    return {
        "startDate": gbp.data_api(data),
        "endDate": gbp.data_api(fim or data),
        "openTime": {"hours": abre},
        "closeTime": {"hours": fecha, "minutes": minuto},
    }


def local(periodos=()):
    return {
        "regularHours": {"periods": [
            {"openDay": dia, "openTime": {"hours": 9},
             "closeTime": {"hours": 23} if dia in ("FRIDAY", "SATURDAY")
             else {"hours": 22, "minutes": 15}}
            for dia in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")
        ]},
        "specialHours": {"specialHourPeriods": list(periodos)},
    }


def resultado(ficha, hoje=dt.date(2026, 10, 25), dias=120):
    return gbp.horarios_especiais(ficha, dias, hoje)["specialHourPeriods"]


def na_data(periodos, data):
    return [p for p in periodos if p["startDate"] == gbp.data_api(data)]


class HorariosEspeciaisTest(unittest.TestCase):
    def test_reproduz_falha_anterior_e_recupera_reveillon_aprovado(self):
        data = dt.date(2026, 12, 31)
        atual = periodo(data)
        esperado = gbp.HORARIOS_CONFIRMADOS[data]
        self.assertEqual(na_data(resultado(local([atual])), data), [esperado])

    def test_preserva_feriado_com_excecao_manual(self):
        data = dt.date(2026, 11, 2)
        manual = periodo(data, abre=11, fecha=20, minuto=0)
        self.assertEqual(na_data(resultado(local([manual])), data), [manual])

    def test_preserva_dois_turnos_manuais_no_feriado(self):
        data = dt.date(2026, 11, 15)
        turnos = [periodo(data, abre=10, fecha=14, minuto=0), periodo(data, abre=18, fecha=22, minuto=0)]
        self.assertEqual(na_data(resultado(local(turnos)), data), turnos)

    def test_mantem_natal_fechado_e_feriado_normal(self):
        saida = resultado(local())
        for dia in (24, 25):
            self.assertTrue(na_data(saida, dt.date(2026, 12, dia))[0]["closed"])
        self.assertEqual(na_data(saida, dt.date(2026, 11, 2)), [periodo(dt.date(2026, 11, 2))])

    def test_preserva_data_futura_fora_do_calendario(self):
        data = dt.date(2026, 11, 3)
        manual = periodo(data, fecha=18, minuto=0)
        self.assertEqual(na_data(resultado(local([manual])), data), [manual])

    def test_reveillon_nao_se_repete_em_outro_ano(self):
        saida = resultado(local(), hoje=dt.date(2027, 12, 1))
        esperado = periodo(dt.date(2027, 12, 31), fecha=23, minuto=0)
        atual = na_data(saida, dt.date(2027, 12, 31))[0]
        self.assertEqual(gbp._periodo_comparavel(atual), gbp._periodo_comparavel(esperado))

    def test_fora_da_janela_preserva_decisao_existente(self):
        data = dt.date(2026, 12, 31)
        manual = copy.deepcopy(gbp.HORARIOS_CONFIRMADOS[data])
        self.assertEqual(na_data(resultado(local([manual]), dias=10), data), [manual])

    def test_resultado_estavel_e_ficha_preservada(self):
        ficha = local([periodo(dt.date(2026, 12, 31))])
        antes = copy.deepcopy(ficha)
        primeira = resultado(ficha)
        self.assertEqual(ficha, antes)
        ficha["specialHours"] = {"specialHourPeriods": primeira}
        self.assertEqual(resultado(ficha), primeira)


if __name__ == "__main__":
    unittest.main()
