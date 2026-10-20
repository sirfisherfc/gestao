#!/usr/bin/env python3
"""Testes sem rede dos baixadores das APIs da Stone e do BB."""

from __future__ import annotations

import base64
import contextlib
import gzip
import io
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = ROOT / "scripts" / "importacao"
sys.path.insert(0, str(IMPORT_DIR))

import api_bb_extrato
import api_cliente
import api_stone_conciliacao
from importacao_core import ErroOperacional, ValidacaoErro


XML_STONE = b"""<?xml version="1.0" encoding="utf-8"?>
<Conciliation>
  <Header><StoneCode>123456789</StoneCode><ReferenceDate>20261019</ReferenceDate><LayoutVersion>2.4</LayoutVersion></Header>
  <FinancialTransactions>
    <Transaction><AcquirerTransactionKey>1</AcquirerTransactionKey>
      <Installments><Installment><InstallmentNumber>1</InstallmentNumber></Installment><Installment><InstallmentNumber>2</InstallmentNumber></Installment></Installments>
    </Transaction>
  </FinancialTransactions>
  <FinancialEvents><Event/></FinancialEvents>
  <FinancialTransactionsAccounts><Transaction/></FinancialTransactionsAccounts>
  <FinancialEventsExpected><Event/></FinancialEventsExpected>
  <Payments><Payment/></Payments>
</Conciliation>"""
SEGREDO = "segredo-no-corpo"


class RespostaFake:
    def __init__(self, corpo: bytes, cabecalhos: dict | None = None):
        self._corpo = corpo
        self.status = 200
        self.headers = cabecalhos or {}

    def read(self) -> bytes:
        return self._corpo

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class RedeFake:
    """Responde em ordem; um inteiro na fila vira erro HTTP com esse status."""

    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.pedidos = []

    def __call__(self, requisicao, *, timeout, contexto):
        self.pedidos.append(requisicao)
        if not self.respostas:
            raise AssertionError(f"pedido inesperado: {requisicao.full_url}")
        resposta = self.respostas.pop(0)
        if isinstance(resposta, int):
            raise urllib.error.HTTPError(
                requisicao.full_url, resposta, "erro", {}, io.BytesIO(SEGREDO.encode())
            )
        return resposta


@contextlib.contextmanager
def rede(respostas):
    fake = RedeFake(respostas)
    original = api_cliente.abrir_url
    api_cliente.abrir_url = fake
    try:
        yield fake
    finally:
        api_cliente.abrir_url = original


@contextlib.contextmanager
def ambiente(**valores):
    anteriores = {nome: os.environ.get(nome) for nome in valores}
    os.environ.update({nome: valor for nome, valor in valores.items() if valor is not None})
    for nome, valor in valores.items():
        if valor is None:
            os.environ.pop(nome, None)
    try:
        yield
    finally:
        for nome, valor in anteriores.items():
            if valor is None:
                os.environ.pop(nome, None)
            else:
                os.environ[nome] = valor


def esperar_erro(tipo, trecho: str, funcao, *args, **kwargs):
    try:
        funcao(*args, **kwargs)
    except tipo as exc:
        if trecho not in str(exc):
            raise AssertionError(f"mensagem sem '{trecho}': {exc}") from exc
        if SEGREDO in str(exc):
            raise AssertionError("mensagem de erro expôs o corpo da resposta") from exc
        return exc
    raise AssertionError(f"{funcao.__name__} deveria falhar com {tipo.__name__}")


def query(requisicao) -> dict[str, str]:
    return dict(urllib.parse.parse_qsl(urllib.parse.urlparse(requisicao.full_url).query))


def test_stone_requisicao() -> None:
    with rede([RespostaFake(gzip.compress(XML_STONE), {"Content-Encoding": "gzip"})]) as fake:
        dados, resumo = api_stone_conciliacao.baixar_dia("chave-teste", "123456789", date(2026, 10, 19), "XML2_4")
    pedido = fake.pedidos[0]
    esperado = "https://conciliation.stone.com.br/v2/merchant/123456789/conciliation-file/20261019?layout=XML2_4"
    if pedido.full_url != esperado:
        raise AssertionError(f"URL da Stone inesperada: {pedido.full_url}")
    basic = "Basic " + base64.b64encode(b"chave-teste:").decode()
    if pedido.get_header("Authorization") != basic:
        raise AssertionError("Basic Auth da Stone deve usar a chave como usuário e senha vazia")
    if pedido.get_header("X-user-type") != "client" or pedido.get_header("Accept-encoding") != "gzip":
        raise AssertionError("cabeçalhos x-user-type e Accept-Encoding são obrigatórios")
    if dados != XML_STONE:
        raise AssertionError("o gzip da Stone deveria ser descompactado antes de salvar")
    contagens = (resumo.transacoes, resumo.parcelas, resumo.liquidacoes, resumo.eventos, resumo.pagamentos)
    if contagens != (1, 2, 1, 1, 1):
        raise AssertionError(f"contagens do XML inesperadas: {contagens}")

    # Gzip sem cabeçalho também é reconhecido pelos bytes iniciais.
    with rede([RespostaFake(gzip.compress(XML_STONE))]):
        dados, _ = api_stone_conciliacao.baixar_dia("chave-teste", "123456789", date(2026, 10, 19), "XML2_2")
    if dados != XML_STONE:
        raise AssertionError("gzip sem Content-Encoding deveria ser descompactado")


def test_stone_cabecalho_e_erros() -> None:
    with rede([RespostaFake(XML_STONE)]):
        esperar_erro(ValidacaoErro, "outro stonecode", api_stone_conciliacao.baixar_dia, "k", "987654321", date(2026, 10, 19), "XML2_4")
    with rede([RespostaFake(XML_STONE)]):
        esperar_erro(ValidacaoErro, "outra data", api_stone_conciliacao.baixar_dia, "k", "123456789", date(2026, 10, 18), "XML2_4")
    resumo = api_stone_conciliacao.resumir_xml(XML_STONE.replace(b"20261019", b"19/10/2026"))
    api_stone_conciliacao.conferir_cabecalho(resumo, "123456789", date(2026, 10, 19))
    esperar_erro(ValidacaoErro, "não é um arquivo de conciliação", api_stone_conciliacao.resumir_xml, b"<Outro/>")
    with rede([403]):
        esperar_erro(ErroOperacional, "CNPJ", api_stone_conciliacao.baixar_dia, "k", "123456789", date(2026, 10, 19), "XML2_4")
    esperar_erro(ValidacaoErro, "use --ate até ontem", api_stone_conciliacao.dias_do_periodo, date(2026, 10, 19), date(2026, 10, 20), date(2026, 10, 20))
    dias = api_stone_conciliacao.dias_do_periodo(date(2026, 9, 30), date(2026, 10, 2), date(2026, 10, 20))
    if [dia.isoformat() for dia in dias] != ["2026-09-30", "2026-10-01", "2026-10-02"]:
        raise AssertionError("período diário da Stone montado errado")
    esperar_erro(ValidacaoErro, "só dígitos", api_stone_conciliacao.resolver_stonecodes, ["12a"])
    if api_stone_conciliacao.resolver_stonecodes(["2", " 1 ", "2"]) != ["2", "1"]:
        raise AssertionError("stonecodes repetidos deveriam ser removidos mantendo a ordem")


def test_stone_baixar_periodo() -> None:
    xml_segundo = XML_STONE.replace(b"123456789", b"555")
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        existente = pasta / "123456789" / "2026-10-18.xml"
        existente.parent.mkdir(parents=True)
        existente.write_bytes(b"antigo")
        dias = [date(2026, 10, 18), date(2026, 10, 19)]
        # Stonecode 1: dia 18 já existe; dia 19 dá 403 e encerra só ele.
        # Stonecode 2: dia 18 baixa normalmente, dia 19 também.
        respostas = [403, RespostaFake(xml_segundo.replace(b"20261019", b"20261018")), RespostaFake(xml_segundo)]
        with rede(respostas) as fake:
            falhas = api_stone_conciliacao.baixar_periodo("k", ["123456789", "555"], dias, "XML2_4", pasta, False)
        if falhas != 1 or len(fake.pedidos) != 3:
            raise AssertionError(f"esperado 1 falha e 3 pedidos, veio {falhas} e {len(fake.pedidos)}")
        if existente.read_bytes() != b"antigo":
            raise AssertionError("arquivo já baixado não deveria ser substituído sem --sobrescrever")
        if not (pasta / "555" / "2026-10-19.xml").exists():
            raise AssertionError("arquivo do segundo stonecode deveria ser salvo")
        if list(pasta.rglob("*.parcial")):
            raise AssertionError("gravação atômica deixou arquivo temporário")

        with rede([429]):
            esperar_erro(ErroOperacional, "7 consultas por hora", api_stone_conciliacao.baixar_periodo, "k", ["777"], dias[:1], "XML2_4", pasta, False)


VARIAVEIS_BB = {
    "BB_AMBIENTE": "homologacao",
    "BB_CLIENT_ID": "id-teste",
    "BB_CLIENT_SECRET": "secret-teste",
    "BB_DEVELOPER_APP_KEY": "app-key-teste",
    "BB_AGENCIA": "1505",
    "BB_CONTA": "1348",
    "BB_CERTIFICADO": None,
    "BB_CHAVE_PRIVADA": None,
    "BB_URL_TOKEN": None,
    "BB_URL_API": None,
    "BB_PARAMETRO_APP_KEY": None,
}


def lancamento(rotulo: str, valor: float, sinal: str) -> dict:
    return {"textoDescricaoHistorico": rotulo, "valorLancamento": valor, "indicadorSinalLancamento": sinal}


def json_bytes(dados: dict) -> RespostaFake:
    return RespostaFake(json.dumps(dados).encode("utf-8"))


def test_bb_configuracao() -> None:
    with ambiente(**VARIAVEIS_BB):
        config = api_bb_extrato.carregar_configuracao()
        if config.contexto is not None or "hm.bb.com.br" not in config.url_api:
            raise AssertionError("homologação deveria usar sandbox sem mTLS")
    with ambiente(**{**VARIAVEIS_BB, "BB_AMBIENTE": "producao"}):
        esperar_erro(ErroOperacional, "mTLS", api_bb_extrato.carregar_configuracao)
    with ambiente(**{**VARIAVEIS_BB, "BB_AMBIENTE": "producao", "BB_CERTIFICADO": "nao-existe.pem", "BB_CHAVE_PRIVADA": "nao-existe.pem"}):
        esperar_erro(ErroOperacional, "não foi encontrado", api_bb_extrato.carregar_configuracao)
    with ambiente(**{**VARIAVEIS_BB, "BB_CONTA": "1348-X"}):
        esperar_erro(ValidacaoErro, "sem o dígito verificador", api_bb_extrato.carregar_configuracao)
    with ambiente(**{**VARIAVEIS_BB, "BB_AMBIENTE": "teste"}):
        esperar_erro(ValidacaoErro, "homologacao ou producao", api_bb_extrato.carregar_configuracao)


def test_bb_token_e_paginas() -> None:
    respostas = [
        json_bytes({"access_token": "token-teste", "token_type": "Bearer"}),
        json_bytes({"numeroPaginaProximo": 2, "listaLancamento": [
            lancamento("Saldo Anterior", 100, "C"), lancamento("Pix - Recebido", 10, "C"),
        ]}),
        json_bytes({"numeroPaginaProximo": 0, "listaLancamento": [
            lancamento("Pix - Enviado", 4, "D"), lancamento("Saldo do dia", 106, "C"), lancamento("S A L D O", 106, "C"),
        ]}),
    ]
    with ambiente(**VARIAVEIS_BB):
        config = api_bb_extrato.carregar_configuracao()
        with rede(respostas) as fake:
            token = api_bb_extrato.obter_token(config)
            lancamentos = api_bb_extrato.baixar_lancamentos(config, token, date(2026, 10, 1), date(2026, 10, 19))
    pedido_token, pagina1, pagina2 = fake.pedidos
    if pedido_token.get_method() != "POST" or pedido_token.full_url != "https://oauth.hm.bb.com.br/oauth/token":
        raise AssertionError("token do BB deveria ser um POST no OAuth do sandbox")
    if dict(urllib.parse.parse_qsl(pedido_token.data.decode())) != {"grant_type": "client_credentials", "scope": "extrato-info"}:
        raise AssertionError("pedido de token sem client_credentials/extrato-info")
    if pedido_token.get_header("Authorization") != "Basic " + base64.b64encode(b"id-teste:secret-teste").decode():
        raise AssertionError("token do BB deveria usar Basic com client_id e client_secret")
    if not pagina1.full_url.startswith("https://api.hm.bb.com.br/extratos/v1/conta-corrente/agencia/1505/conta/1348?"):
        raise AssertionError(f"rota do extrato inesperada: {pagina1.full_url}")
    if pagina1.get_header("Authorization") != "Bearer token-teste":
        raise AssertionError("extrato deveria enviar o Bearer obtido")
    esperado = {
        "gw-dev-app-key": "app-key-teste",
        "numeroPaginaSolicitacao": "1",
        "quantidadeRegistroPaginaSolicitacao": "200",
        "dataInicioSolicitacao": "1102026",
        "dataFimSolicitacao": "19102026",
    }
    if query(pagina1) != esperado or query(pagina2)["numeroPaginaSolicitacao"] != "2":
        raise AssertionError(f"parâmetros do extrato inesperados: {query(pagina1)}")
    conferencia = api_bb_extrato.conferir_saldo(lancamentos)
    if not (conferencia.aplicada and conferencia.confere and conferencia.lancamentos == 2):
        raise AssertionError(f"conferência de saldo do BB errada: {conferencia}")

    divergente = lancamentos[:-1] + [lancamento("S A L D O", 107, "C")]
    if api_bb_extrato.conferir_saldo(divergente).confere:
        raise AssertionError("saldo divergente deveria ser apontado")
    if api_bb_extrato.conferir_saldo(lancamentos[1:3]).aplicada:
        raise AssertionError("sem linhas de saldo a conferência não se aplica")

    with ambiente(**VARIAVEIS_BB):
        config = api_bb_extrato.carregar_configuracao()
        with rede([401]):
            esperar_erro(ErroOperacional, "BB_CLIENT_ID", api_bb_extrato.obter_token, config)


def test_bb_blocos_e_gravacao() -> None:
    blocos = api_bb_extrato.blocos_mensais(date(2026, 8, 15), date(2026, 10, 19), date(2026, 10, 20))
    if [(a.isoformat(), b.isoformat()) for a, b in blocos] != [
        ("2026-08-15", "2026-08-31"), ("2026-09-01", "2026-09-30"), ("2026-10-01", "2026-10-19"),
    ]:
        raise AssertionError(f"blocos mensais errados: {blocos}")
    esperar_erro(ValidacaoErro, "use --ate até ontem", api_bb_extrato.blocos_mensais, date(2026, 10, 1), date(2026, 10, 20), date(2026, 10, 20))
    if api_bb_extrato.data_bb(date(2026, 1, 5)) != "5012026":
        raise AssertionError("data do BB deveria omitir o zero à esquerda do dia")

    with tempfile.TemporaryDirectory() as tmp, ambiente(**VARIAVEIS_BB):
        config = api_bb_extrato.carregar_configuracao()
        respostas = [
            json_bytes({"access_token": "token-teste"}),
            json_bytes({"numeroPaginaProximo": 0, "listaLancamento": [
                lancamento("Saldo Anterior", 50, "C"), lancamento("Tarifa", 5, "D"), lancamento("S A L D O", 40, "C"),
            ]}),
        ]
        with rede(respostas):
            divergentes = api_bb_extrato.baixar_periodo(config, [(date(2026, 9, 1), date(2026, 9, 30))], Path(tmp), False)
        arquivo = Path(tmp) / "homologacao" / "2026-09-01_2026-09-30.json"
        conteudo = arquivo.read_text(encoding="utf-8")
        if divergentes != 1:
            raise AssertionError("bloco com saldo divergente deveria ser contado")
        if "secret-teste" in conteudo or "token-teste" in conteudo or "app-key-teste" in conteudo:
            raise AssertionError("arquivo baixado não pode conter credenciais")
        if len(json.loads(conteudo)["listaLancamento"]) != 3:
            raise AssertionError("arquivo baixado deveria guardar todos os lançamentos")
        with rede([json_bytes({"access_token": "token-teste"})]) as fake:
            api_bb_extrato.baixar_periodo(config, [(date(2026, 9, 1), date(2026, 9, 30))], Path(tmp), False)
        if len(fake.pedidos) != 1:
            raise AssertionError("mês já baixado deveria ser pulado sem consultar o extrato")


def test_cli_sem_credenciais() -> None:
    """Sem chave, os scripts param antes de qualquer rede, com código 3."""
    vazio = {**os.environ, "PYTHONIOENCODING": "utf-8", "STONE_CONCILIACAO_API_KEY": "", "BB_CLIENT_ID": ""}
    for script, variavel in (("api_stone_conciliacao.py", "STONE_CONCILIACAO_API_KEY"), ("api_bb_extrato.py", "BB_CLIENT_ID")):
        resultado = subprocess.run(
            [sys.executable, str(IMPORT_DIR / script), "--verificar"],
            capture_output=True, text=True, encoding="utf-8", env=vazio,
        )
        if resultado.returncode != 3 or variavel not in resultado.stdout:
            raise AssertionError(f"{script} sem credencial deveria sair com 3 citando {variavel}: {resultado.stdout}{resultado.stderr}")


def main() -> int:
    test_stone_requisicao()
    test_stone_cabecalho_e_erros()
    test_stone_baixar_periodo()
    test_bb_configuracao()
    test_bb_token_e_paginas()
    test_bb_blocos_e_gravacao()
    test_cli_sem_credenciais()
    print("API_BANCOS_TESTS_OK stone=3 bb=3 cli=2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
