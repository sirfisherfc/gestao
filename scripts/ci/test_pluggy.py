#!/usr/bin/env python3
"""Contratos da conexão Pluggy: rede simulada, .env temporário e HTTP local."""

from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "importacao"))

import api_pluggy as api
import api_pluggy_stone as importar
import conectar_pluggy as conectar
from api_cliente import ErroHttp, Resposta
from importacao_core import ErroOperacional


def resposta(dado):
    return Resposta(200, json.dumps(dado).encode())


class ClienteTeste(unittest.TestCase):
    def test_auth_aceita_alias_e_nao_reutiliza_api_key_do_arquivo(self):
        with patch.dict(os.environ, {"PLUGGY_Client_ID": "cliente-teste", "PLUGGY_Client_Secret": "secret-teste",
                                    "PLUGGY_API_KEY": "chave-antiga"}, clear=True), \
             patch.object(api, "requisitar", return_value=resposta({"apiKey": "nova"})) as rede:
            cliente = api.Cliente()
            cliente.autenticar()
            self.assertEqual(cliente.api_key, "nova")
            corpo = json.loads(rede.call_args.kwargs["corpo"])
            self.assertEqual(corpo, {"clientId": "cliente-teste", "clientSecret": "secret-teste"})

    def test_chave_expirada_renova_so_uma_vez(self):
        cliente = api.Cliente()
        cliente.api_key = "expirada"
        with patch.object(api, "requisitar", side_effect=[ErroHttp(401, "recusada"),
                          resposta({"apiKey": "nova"}), resposta({"id": "item-teste"})]) as rede, \
             patch.dict(os.environ, {"PLUGGY_CLIENT_ID": "cliente", "PLUGGY_CLIENT_SECRET": "secret"}):
            self.assertEqual(cliente.item("item-teste")["id"], "item-teste")
            self.assertEqual(rede.call_count, 3)
            self.assertEqual(rede.call_args.kwargs["cabecalhos"]["X-API-KEY"], "nova")
        with patch.object(api, "requisitar", side_effect=[ErroHttp(401, "recusada"),
                          resposta({"apiKey": "nova"}), ErroHttp(401, "recusada")]) as rede, \
             patch.dict(os.environ, {"PLUGGY_CLIENT_ID": "cliente", "PLUGGY_CLIENT_SECRET": "secret"}):
            with self.assertRaises(ErroHttp):
                cliente.item("item-teste")
            self.assertEqual(rede.call_count, 3)

    def test_cursor_v2_e_datas_corretas(self):
        from datetime import date
        cliente = api.Cliente()
        with patch.object(cliente, "consultar", side_effect=[
            {"results": [{"id": "t1", "date": "2026-09-01T12:00:00Z"}], "next": "?accountId=conta1&after=cursor-seguinte"},
            {"results": [{"id": "t2", "date": "2026-09-30T12:00:00Z"}], "next": None},
        ]) as rede:
            self.assertEqual(len(cliente.transacoes("conta1", date(2026, 9, 1), date(2026, 9, 30))), 2)
            primeira = rede.call_args_list[0].args[0]
            self.assertEqual(urlsplit(primeira).path, "/v2/transactions")
            params = parse_qs(urlsplit(primeira).query)
            self.assertEqual(params["dateFrom"], ["2026-09-01"])
            self.assertEqual(params["dateTo"], ["2026-10-01"])
            self.assertNotIn("from", params)
            self.assertEqual(rede.call_args_list[1].args[0], "/v2/transactions?accountId=conta1&after=cursor-seguinte")

    def test_recusa_cursor_externo_e_ciclo(self):
        for cursor in ("https://outro.example/roubar", "//outro.example/v2/transactions", "/auth", 3):
            with self.subTest(cursor=cursor), self.assertRaises(ErroOperacional):
                api.proxima_rota("/v2/transactions", cursor)
        cliente = api.Cliente()
        with patch.object(cliente, "consultar", return_value={"results": [], "next": "?accountId=conta1"}):
            with self.assertRaisesRegex(ErroOperacional, "repetiu"):
                cliente.paginas("/v2/transactions", {"accountId": "conta1"}, cursor=True)

    def test_falha_na_segunda_pagina_nao_vira_sucesso_parcial(self):
        cliente = api.Cliente()
        with patch.object(cliente, "consultar", side_effect=[
            {"results": [{"id": "t1"}], "next": "?after=segundo"}, ErroHttp(503, "indisponível"),
        ]), self.assertRaises(ErroHttp):
            cliente.paginas("/v2/transactions", {}, cursor=True)

    def test_resposta_sem_confirmacao_de_ultima_pagina_e_recusada(self):
        cliente = api.Cliente()
        for resposta_api in ({"results": []}, {"results": [], "next": ""}):
            with patch.object(cliente, "consultar", return_value=resposta_api), self.assertRaises(ErroOperacional):
                cliente.paginas("/v2/transactions", {}, cursor=True)

    def test_consentimento_expirado_nao_parece_conta_sem_movimento(self):
        with self.assertRaisesRegex(ErroOperacional, "expirou"):
            api.conferir_item({"status": "UPDATED", "consentExpiresAt": "2020-01-01T00:00:00Z"})
        with self.assertRaises(ErroOperacional):
            api.conferir_item({"status": "LOGIN_ERROR"})
        api.conferir_item({"status": "UPDATED", "consentExpiresAt": "2099-01-01T00:00:00Z"})

    def test_fim_do_mes_em_fortaleza_nao_perde_movimento_em_utc(self):
        from datetime import date
        cliente = api.Cliente()
        with patch.object(cliente, "paginas", return_value=[
            {"date": "2026-09-01T01:00:00Z"},  # Ainda agosto em Fortaleza.
            {"date": "2026-10-01T02:59:59Z"},  # Últimos segundos de setembro.
            {"date": "2026-10-01T03:00:00Z"},
        ]):
            linhas = cliente.transacoes("conta1", date(2026, 9, 1), date(2026, 9, 30))
        self.assertEqual(linhas, [{"date": "2026-10-01T02:59:59Z"}])


class ImportacaoTeste(unittest.TestCase):
    def linha(self, identificador="novo", valor="20.00", instante="2026-10-20T12:00:00Z"):
        item = {"id": identificador, "accountId": "conta-teste", "currencyCode": "BRL", "status": "POSTED",
                "amount": valor, "type": "CREDIT" if float(valor) > 0 else "DEBIT", "date": instante,
                "operationType": "PIX", "description": "TRANSFERENCIA | PIX | PESSOA FICTICIA",
                "paymentData": {"payer": {"documentNumber": {"type": "CPF", "value": "12345678901"}}}}
        return importar.converter(item, {"id": "conta-teste"})

    def test_documentos_e_nome_conservam_formato_do_de_para(self):
        self.assertEqual(importar.documento("12345678901"), "***.456.789-**")
        self.assertEqual(importar.documento("12345678000190"), "12.345.678/0001-90")
        self.assertEqual(self.linha()["origem"], "PESSOA FICTICIA")
        self.assertEqual(self.linha()["tipo"], "Pix")

    def test_legado_totalmente_coberto_nao_duplica(self):
        from copy import deepcopy
        linha = self.linha()
        velho = deepcopy(linha)
        velho.update(dedup_hash="hash-csv", origem_carga="stone_extrato")
        self.assertEqual(importar.selecionar_novos([linha], [velho]), [])
        with self.assertRaises(ErroOperacional):
            importar.selecionar_novos([linha, self.linha("outro")], [velho])

    def test_reexecucao_pluggy_nao_duplica_e_aceita_nova_mesma_quantia(self):
        from copy import deepcopy
        linha = self.linha()
        velho = deepcopy(linha)
        self.assertEqual(importar.selecionar_novos([linha], [velho]), [])
        novo = self.linha("outro")
        self.assertEqual(importar.selecionar_novos([linha, novo], [velho]), [novo])

    def test_retificacao_e_desaparecimento_nao_passam_silenciosamente(self):
        from copy import deepcopy
        linha = self.linha()
        velho = deepcopy(linha)
        linha["descricao"] = "texto retificado"
        with self.assertRaises(ErroOperacional):
            importar.selecionar_novos([linha], [velho])
        with self.assertRaises(ErroOperacional):
            importar.selecionar_novos([], [velho])

    def test_saldo_antes_mais_novos_precisa_fechar(self):
        from datetime import datetime
        from decimal import Decimal
        ancora = {"data_hora": datetime(2026, 10, 19, 12), "saldo_depois": Decimal("100.00")}
        novos = [self.linha()]
        importar.preencher_saldos(novos, ancora, "120.00")
        self.assertEqual(novos[0]["saldo_depois"], Decimal("120.00"))
        with self.assertRaises(ErroOperacional):
            importar.preencher_saldos(novos, ancora, "121.00")
        with self.assertRaises(ErroOperacional):
            importar.preencher_saldos([self.linha(instante="2026-10-18T12:00:00Z")], ancora, "120.00")
        with self.assertRaises(ErroOperacional):
            importar.preencher_saldos([self.linha("um"), self.linha("dois")], ancora, "140.00")

    def test_valores_invalidos_sao_recusados(self):
        for valor in ("NaN", "Infinity", "0.001", "invalido"):
            with self.subTest(valor=valor), self.assertRaises(ErroOperacional):
                importar.moeda(valor)
        with self.assertRaises(ErroOperacional):
            self.linha(valor="0")


class GravacaoTeste(unittest.TestCase):
    def test_callback_valida_item_preserva_segredos_e_nao_duplica(self):
        cliente = api.Cliente()
        with tempfile.TemporaryDirectory() as tmp, patch.object(conectar, "RAIZ_PROJETO", Path(tmp)):
            caminho = Path(tmp) / ".env"
            caminho.write_text("# privado\nOUTRO_SEGREDO=preservado\nPLUGGY_ITEM_IDS='item-antigo'\n", encoding="utf-8")
            with patch.object(cliente, "item", return_value={"id": "item-novo", "connector": {"isSandbox": False}}):
                conectar.salvar_item("item-novo", cliente)
                conectar.salvar_item("item-novo", cliente)
            conteudo = caminho.read_text(encoding="utf-8")
            self.assertIn("OUTRO_SEGREDO=preservado", conteudo)
            self.assertIn("# privado", conteudo)
            self.assertIn("item-antigo,item-novo", conteudo)
            self.assertEqual(conteudo.count("item-novo"), 1)
            anterior = conteudo
            for item in ({"id": "item-diferente"}, {"id": "item-novo", "connector": {"isSandbox": True}}):
                with patch.object(cliente, "item", return_value=item), self.assertRaises(ErroOperacional):
                    conectar.salvar_item("item-novo", cliente)
                self.assertEqual(caminho.read_text(encoding="utf-8"), anterior)


class ServidorTeste(unittest.TestCase):
    def setUp(self):
        self.cliente = api.Cliente()
        self.server = conectar.Servidor(0, self.cliente, 200)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def pedir(self, method="GET", path="/", headers=None, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        r = conn.getresponse()
        result = (r.status, dict(r.getheaders()), r.read())
        conn.close()
        return result

    def test_html_nao_expoe_segredos_e_nao_tem_cache(self):
        with patch.dict(os.environ, {"PLUGGY_CLIENT_SECRET": "segredo-que-nao-pode-vazar"}):
            status, headers, body = self.pedir()
        self.assertEqual(status, 200)
        self.assertNotIn(b"segredo-que-nao-pode-vazar", body)
        self.assertNotIn(b"PLUGGY_CLIENT_SECRET", body)
        self.assertNotIn(b"X-API-KEY", body)
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_host_origem_e_sessao_impedem_requisicoes_externas(self):
        for headers in ({"Host": "ataque.example"}, {"Origin": "https://ataque.example"},
                        {"Origin": self.server.origem, "X-Connect-Session": "incorreta"}):
            status, _, _ = self.pedir("POST", "/api/token", headers, "{}")
            self.assertEqual(status, 403)
        status, _, _ = self.pedir(headers={"Host": "ataque.example"})
        self.assertEqual(status, 403)

    def test_endpoint_entrega_so_token_restrito_e_nao_api_key(self):
        self.cliente.api_key = "chave-aplicacao-privada"
        with patch.object(self.cliente, "token_conexao", return_value="token-restrito"):
            status, _, body = self.pedir("POST", "/api/token", {
                "Origin": self.server.origem, "X-Connect-Session": self.server.sessao,
            }, "{}")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["token"], "token-restrito")
        self.assertNotIn(b"chave-aplicacao-privada", body)


if __name__ == "__main__":
    unittest.main()
