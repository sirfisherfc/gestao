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
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = ROOT / "scripts" / "importacao"
sys.path.insert(0, str(IMPORT_DIR))

import api_bb_extrato
import api_cliente
import api_saipos_vendas
import api_stone_conciliacao
import api_stone_recebiveis
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
    with mock.patch.object(api_stone_conciliacao, "stonecodes_do_banco", return_value=["173835323", "770398216"]),             mock.patch.object(api_stone_conciliacao, "variavel", return_value=None):
        if api_stone_conciliacao.resolver_stonecodes(None) != ["770398216"]:
            raise AssertionError("173835323 não deveria ser consultado sem --stonecode explícito")


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
        if [(codigo, dia) for codigo, dia, _ in falhas] != [("123456789", date(2026, 10, 19))] or len(fake.pedidos) != 3:
            raise AssertionError(f"esperado 1 falha e 3 pedidos, veio {falhas} e {len(fake.pedidos)}")
        if existente.read_bytes() != b"antigo":
            raise AssertionError("arquivo já baixado não deveria ser substituído sem --sobrescrever")
        if not (pasta / "555" / "2026-10-19.xml").exists():
            raise AssertionError("arquivo do segundo stonecode deveria ser salvo")
        if list(pasta.rglob("*.parcial")):
            raise AssertionError("gravação atômica deixou arquivo temporário")

        # 429 encerra a rodada: o dia consultado e os pendentes entram como falha.
        with rede([429]) as fake:
            falhas = api_stone_conciliacao.baixar_periodo("k", ["777", "888"], dias, "XML2_4", pasta, False)
        if len(fake.pedidos) != 1 or len(falhas) != 4 or "7 consultas por hora" not in falhas[-1][2]:
            raise AssertionError(f"429 deveria encerrar e marcar os 4 dias pendentes: {falhas}")
        # 403 na primeira consulta descarta o stonecode inteiro, sem novos pedidos.
        with rede([403]) as fake:
            falhas = api_stone_conciliacao.baixar_periodo("k", ["999"], dias, "XML2_4", pasta, False)
        if len(fake.pedidos) != 1 or len(falhas) != 2:
            raise AssertionError(f"403 inicial deveria marcar os 2 dias com um só pedido: {falhas}")


def xml_conciliacao(dia: str, transacoes: str = "", liquidacoes: str = "") -> bytes:
    return f"""<Conciliation>
  <Header><StoneCode>123456789</StoneCode><ReferenceDate>{dia}</ReferenceDate><LayoutVersion>2.4</LayoutVersion></Header>
  <FinancialTransactions>{transacoes}</FinancialTransactions>
  <FinancialEvents><Event/></FinancialEvents>
  <FinancialTransactionsAccounts>{liquidacoes}</FinancialTransactionsAccounts>
</Conciliation>""".encode()


def captura_xml(chave: str, *, brand: str = "2", account: str = "3", eventos: str = "<Captures>1</Captures>") -> str:
    return f"""<Transaction><Events>{eventos}</Events>
  <AcquirerTransactionKey>{chave}</AcquirerTransactionKey><CaptureLocalDateTime>20260907194223</CaptureLocalDateTime>
  <AccountType>{account}</AccountType><NumberOfInstallments>1</NumberOfInstallments><BrandId>{brand}</BrandId>
  <Installments><Installment><InstallmentNumber>1</InstallmentNumber><GrossAmount>29.800000</GrossAmount>
    <NetAmount>29.493060</NetAmount><PrevisionPaymentDate>20260908</PrevisionPaymentDate></Installment></Installments>
</Transaction>"""


CANCELAMENTO_XML = """<Transaction><Events><Cancellations>1</Cancellations></Events>
  <AcquirerTransactionKey>{chave}</AcquirerTransactionKey>
  <Cancellations><Cancellation><OperationKey>op-1</OperationKey><CancellationDateTime>20260908022326</CancellationDateTime>
    <ReturnedAmount>{devolvido}</ReturnedAmount><Billing><ChargedAmount>29.493060</ChargedAmount>
    <PrevisionChargeDate>20260909</PrevisionChargeDate></Billing></Cancellation></Cancellations>
</Transaction>"""


class BancoFake:
    def __init__(self, vendas=None):
        self.vendas = vendas or {}

    def documento(self, stonecode):
        return "00.000.000/0001-00"

    def venda(self, stone_id):
        return self.vendas.get(stone_id)


def test_recebiveis_stone() -> None:
    from decimal import Decimal

    pagamento = """<Transaction><AcquirerTransactionKey>11111111111111</AcquirerTransactionKey>
      <Installments><Installment><InstallmentNumber>1</InstallmentNumber><PaymentDate>20260908</PaymentDate>
      <OriginalPaymentDate>20260908</OriginalPaymentDate></Installment></Installments></Transaction>"""
    leitura = api_stone_recebiveis.ler_arquivo(
        xml_conciliacao("20260907", captura_xml("11111111111111")), "123456789", date(2026, 9, 7)
    )
    leitura.juntar(api_stone_recebiveis.ler_arquivo(
        xml_conciliacao("20260908", CANCELAMENTO_XML.format(chave="11111111111111", devolvido="29.800000"), pagamento),
        "123456789", date(2026, 9, 8),
    ))
    if leitura.eventos_ignorados != 2:
        raise AssertionError("eventos financeiros deveriam ser contados e ignorados")
    registros, rejeicoes = api_stone_recebiveis.montar_registros(leitura, BancoFake())
    if rejeicoes or [item["categoria"] for item in registros] != ["Venda", "Cancelamento"]:
        raise AssertionError(f"venda + cancelamento montados errado: {rejeicoes}")
    venda, cancelamento = registros
    esperado_venda = {
        "bandeira": "MasterCard", "produto": "Debito Pre-pago", "n_parcela": 1, "qtd_parcelas": 1,
        "valor_bruto": Decimal("29.800000"), "valor_liquido": Decimal("29.493060"),
        "desconto_mdr": Decimal("-0.306940"), "entradas_brutas": Decimal("29.800000"),
        "saidas_brutas": Decimal("0"), "ultimo_status": "Pago", "data_vencimento": date(2026, 9, 8),
        "documento": "00.000.000/0001-00", "stonecode": "123456789",
    }
    for campo, valor in esperado_venda.items():
        if venda[campo] != valor:
            raise AssertionError(f"Venda: {campo} = {venda[campo]!r}, esperado {valor!r}")
    if str(venda["data_venda"]) != "2026-09-07 19:42:23":
        raise AssertionError("data da venda deve ser a captura local, com segundos")
    esperado_cancelamento = {
        "valor_bruto": Decimal("-29.800000"), "valor_liquido": Decimal("-29.493060"),
        "desconto_mdr": Decimal("0.306940"), "entradas_brutas": Decimal("0"),
        "saidas_brutas": Decimal("-29.800000"), "data_vencimento": date(2026, 9, 9),
        "produto": "Debito Pre-pago", "ultimo_status": "Aberto",
    }
    for campo, valor in esperado_cancelamento.items():
        if cancelamento[campo] != valor:
            raise AssertionError(f"Cancelamento: {campo} = {cancelamento[campo]!r}, esperado {valor!r}")
    if str(cancelamento["data_venda"]) != "2026-09-08 02:23:26":
        raise AssertionError("data do cancelamento deve ser a do evento")

    # Cancelamento de venda importada antes do período: dados vêm do painel.
    parcial = api_stone_recebiveis.ler_arquivo(
        xml_conciliacao("20260908", CANCELAMENTO_XML.format(chave="22222222222222", devolvido="10.000000")),
        "123456789", date(2026, 9, 8),
    )
    conhecida = api_stone_recebiveis.VendaConhecida("Visa", "Credito", 1, Decimal("29.80"))
    registros, rejeicoes = api_stone_recebiveis.montar_registros(parcial, BancoFake({"22222222222222": conhecida}))
    if rejeicoes or registros[0]["categoria"] != "Cancelamento Parcial":
        raise AssertionError("devolução menor que a venda deveria ser Cancelamento Parcial")
    _, rejeicoes = api_stone_recebiveis.montar_registros(parcial, BancoFake())
    if not rejeicoes or "importe o CSV" not in rejeicoes[0]:
        raise AssertionError("cancelamento sem venda conhecida deveria ser recusado")
    parcelada = api_stone_recebiveis.VendaConhecida("Visa", "Credito", 3, Decimal("29.80"))
    _, rejeicoes = api_stone_recebiveis.montar_registros(parcial, BancoFake({"22222222222222": parcelada}))
    if not rejeicoes or "parcelada" not in rejeicoes[0]:
        raise AssertionError("cancelamento de venda parcelada deveria ser recusado")

    desconhecida = api_stone_recebiveis.ler_arquivo(
        xml_conciliacao("20260907", captura_xml("33333333333333", brand="99")), "123456789", date(2026, 9, 7)
    )
    registros, rejeicoes = api_stone_recebiveis.montar_registros(desconhecida, BancoFake())
    if registros or not any("BrandId 99" in item for item in rejeicoes):
        raise AssertionError("bandeira sem mapeamento deveria recusar a parcela")
    chargeback = api_stone_recebiveis.ler_arquivo(
        xml_conciliacao("20260907", captura_xml("44444444444444", eventos="<Chargebacks>1</Chargebacks>")),
        "123456789", date(2026, 9, 7),
    )
    if not any("Chargebacks sem regra" in item for item in chargeback.rejeicoes):
        raise AssertionError("chargeback deveria recusar a carga até ter regra")

    existentes = {("11111111111111", 1, "Venda"): {
        "data_venda": venda["data_venda"], "data_vencimento": date(2026, 9, 8),
        "valor_bruto": Decimal("29.80"), "valor_liquido": Decimal("29.40"),
    }}
    contagem = api_stone_recebiveis.comparar([venda, cancelamento], existentes)
    if contagem != {"novas": 1, "iguais": 0, "diferentes": 1}:
        raise AssertionError(f"comparação com o painel errada: {contagem}")
    if venda["_origem"] != ("123456789", date(2026, 9, 7)) or cancelamento["_origem"] != ("123456789", date(2026, 9, 8)):
        raise AssertionError("cada linha deveria apontar o arquivo de onde veio")

    alvos = [("123456789", date(2026, 9, 7)), ("123456789", date(2026, 9, 8)), ("123456789", date(2026, 9, 9))]
    execucoes = api_stone_recebiveis._execucoes(
        alvos,
        {alvos[0]: ("ok", 1), alvos[1]: ("sem_movimento", 0)},
        {alvos[2]: "HTTP 403"},
    )
    if [(item.dia_referencia.day, item.situacao) for item in execucoes] != [(7, "ok"), (8, "sem_movimento"), (9, "erro")]:
        raise AssertionError(f"registro de execuções por dia errado: {execucoes}")


def test_pix_stone() -> None:
    from datetime import datetime
    from decimal import Decimal

    import api_stone_pix

    e2e = "E1823612020260907224223abcdef12"
    for separador in (",", ";"):
        texto = separador.join(["id", "amount", "status", "created_at", "pix_transaction__e2e_id",
                                "pix_transaction__terminal__serial_number", "pix_transaction__fee_amount"]) + "\n"
        texto += separador.join(["ev_1", "2980", "paid", "2026-09-07T22:42:23.000Z", e2e, "SN1", "0"]) + "\n"
        linhas = api_stone_pix.ler_csv(texto)
        if len(linhas) != 1 or linhas[0]["pix_transaction__e2e_id"] != e2e:
            raise AssertionError(f"CSV Pix com '{separador}' lido errado: {linhas}")
    if api_stone_pix.data_hora_local("2026-09-07T22:42:23.000Z") != datetime(2026, 9, 7, 19, 42, 23):
        raise AssertionError("created_at em UTC deveria virar horário de Fortaleza")
    esperar_erro(ValidacaoErro, "coluna id", api_stone_pix.ler_csv, "outra,coluna\n1,2\n")

    vendas = {e2e: {"data_venda": datetime(2026, 9, 7, 19, 42), "valor_bruto": Decimal("29.80"), "n_serie": "SN1"}}
    resultado = api_stone_pix.analisar(linhas, vendas)
    if resultado["chave escolhida"] != "pix_transaction__e2e_id" or resultado["escala do valor"] != {"centavos": 1}:
        raise AssertionError(f"análise do Pix escolheu chave ou escala errada: {resultado}")
    if resultado["terminal igual"] != {True: 1} or resultado["data do banco - created_at local (min)"] != {0: 1}:
        raise AssertionError(f"análise do Pix comparou terminal ou data errado: {resultado}")

    with ambiente(SUPABASE_URL="https://ref.supabase.co/", STONE_WEBHOOK_TOKEN="tok"):
        if api_stone_pix.url_webhook() != "https://ref.supabase.co/functions/v1/stone-webhook?token=tok":
            raise AssertionError("URL do webhook montada errado")
        with rede([RespostaFake(b"")]) as fake:
            api_stone_pix.cadastrar_webhook("k")
        with rede([RespostaFake(b"")]) as fake_put:
            api_stone_pix.cadastrar_webhook("k", atualizar=True)
    if fake.pedidos[0].get_method() != "POST" or fake_put.pedidos[0].get_method() != "PUT":
        raise AssertionError("cadastro usa POST e atualização usa PUT")
    if json.loads(fake.pedidos[0].data)["url"].count("token=tok") != 1:
        raise AssertionError("corpo do cadastro deveria levar a URL com o token")
    with rede([RespostaFake(b"")]) as fake:
        api_stone_pix.solicitar("k", "37889047000168", date(2026, 9, 7))
    if fake.pedidos[0].full_url != "https://conciliation.stone.com.br/v2/merchant/37889047000168/conciliation-file/pix/2026-09-07":
        raise AssertionError(f"pedido do arquivo Pix com URL errada: {fake.pedidos[0].full_url}")


def test_pix_extrato() -> None:
    from datetime import datetime
    from decimal import Decimal

    import api_stone_pix_extrato as pe

    if not pe.eh_venda_pix("Transação", Decimal("10"), "***.123.456-**"):
        raise AssertionError("crédito Transação com pagador é venda Pix")
    if pe.eh_venda_pix("Pix", Decimal("10"), "***.123.456-**") or pe.eh_venda_pix("Transação", Decimal("10"), "Desconhecido"):
        raise AssertionError("transferência Pix e crédito interno não são venda")
    creditos = [
        pe.CreditoPix("h1", datetime(2026, 9, 7, 19, 42, 50), Decimal("29.80"), "pluggy"),
        pe.CreditoPix("h2", datetime(2026, 9, 7, 19, 43, 10), Decimal("29.80"), "pluggy"),
        pe.CreditoPix("h3", datetime(2026, 9, 7, 20, 0, 0), Decimal("5.00"), "pluggy"),
    ]
    vendas = [
        pe.VendaPix("E1", datetime(2026, 9, 7, 19, 43), Decimal("29.80")),
        pe.VendaPix("E2", datetime(2026, 9, 7, 19, 42), Decimal("29.80")),
        pe.VendaPix("E3", datetime(2026, 9, 7, 21, 0), Decimal("7.00")),
    ]
    pares, sobras, sem_credito = pe.casar(creditos, vendas)
    if sorted((c.dedup_hash, v.stone_id) for c, v, _ in pares) != [("h1", "E2"), ("h2", "E1")]:
        raise AssertionError(f"Pix de mesmo valor deveria casar pelo minuto mais próximo: {pares}")
    if [c.dedup_hash for c in sobras] != ["h3"] or [v.stone_id for v in sem_credito] != ["E3"]:
        raise AssertionError("sobras do casamento Pix erradas")
    linha = pe.linha_venda(creditos[0], "37889047000168")
    if linha["stone_id"] != "EXTRATO-h1" or str(linha["data_venda"]) != "2026-09-07 19:42:00" or linha["produto"] != "Pix QRcode":
        raise AssertionError(f"linha de venda Pix do extrato fora do padrão do CSV: {linha}")


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


def test_saipos_vendas() -> None:
    from datetime import datetime
    from decimal import Decimal

    bruta = {
        "id_sale": 1, "id_store": 9, "shift_date": "2026-10-18", "created_at": "2026-10-18T12:00:00",
        "updated_at": None, "canceled": "N", "id_sale_type": 3, "total_amount": 80,
        "store_shift": {"desc_store_shift": "Manha"},
        "payments": [
            {"desc_store_payment_type": "Dinheiro", "payment_amount": 10, "created_at": "2026-10-18T12:00:00"},
            {"desc_store_payment_type": "Crédito", "payment_amount": 40, "created_at": "2026-10-18T12:00:00"},
            {"desc_store_payment_type": "Pix", "payment_amount": 30, "created_at": "2026-10-18T12:01:00"},
        ],
        "payment_transaction_smartpos": [
            {"payment_method": "CRÉDITO", "payment_amount": 40, "approved": True, "cancelled": False,
             "authorization_code": "391", "id_transaction": "7", "created_at": "2026-10-18T12:00:30"},
        ],
    }
    venda, pagamentos = api_saipos_vendas.ler_venda(bruta)
    if venda["cancelada"] or venda["data_turno"].isoformat() != "2026-10-18":
        raise AssertionError("venda Saipos lida errado")
    resumo = [(p.origem, p.categoria, p.entra_conciliacao) for p in pagamentos]
    # A forma Crédito é a mesma transação da maquininha e não se repete.
    if resumo != [("pos", "credito", True), ("forma", "dinheiro", False), ("forma", "pix", True)]:
        raise AssertionError(f"pagamentos Saipos montados errado: {resumo}")
    cancelada, itens = api_saipos_vendas.ler_venda({**bruta, "canceled": "Y"})
    if not cancelada["cancelada"] or any(p.entra_conciliacao for p in itens):
        raise AssertionError("venda cancelada não pode entrar na conciliação")

    stone = [
        api_saipos_vendas.VendaStone("391", datetime(2026, 10, 18, 12, 0), "credito", Decimal("40.00")),
        api_saipos_vendas.VendaStone("E1", datetime(2026, 10, 18, 12, 3), "pix", Decimal("30.00")),
        api_saipos_vendas.VendaStone("E2", datetime(2026, 10, 18, 12, 2), "debito", Decimal("30.00")),
        api_saipos_vendas.VendaStone("X", datetime(2026, 10, 18, 15, 0), "credito", Decimal("12.00")),
    ]
    api_saipos_vendas.conciliar(pagamentos, stone)
    casados = {(p.categoria, p.stone_id, p.casamento) for p in pagamentos if p.stone_id}
    if casados != {("credito", "391", "codigo"), ("pix", "E1", "valor_horario")}:
        raise AssertionError(f"conciliação Saipos x Stone errada: {casados}")
    # Conta dividida: caixa e maquininha diferem em centavos; zerado não entra.
    _, centavos = api_saipos_vendas.ler_venda({**bruta, "payments": [
        {"desc_store_payment_type": "Crédito", "payment_amount": 40.01, "created_at": "2026-10-18T12:00:00"},
        {"desc_store_payment_type": "Pix", "payment_amount": 0, "created_at": "2026-10-18T12:00:00"},
    ]})
    if [(p.origem, p.entra_conciliacao) for p in centavos] != [("pos", True), ("forma", False)]:
        raise AssertionError("forma com centavos de diferença ou zerada deveria sair da conciliação")

    def manual(valor: str, hora: int, minuto: int, cat: str = "outro") -> api_saipos_vendas.Pagamento:
        return api_saipos_vendas.Pagamento(2, "forma", hora * 60 + minuto, "x", cat, Decimal(valor),
                                           datetime(2026, 10, 18, hora, minuto), None, None, True)

    vale, fechada, comum = manual("117.70", 20, 24), manual("59.18", 22, 44, "credito"), manual("5.00", 22, 44, "pix")
    stone = [
        api_saipos_vendas.VendaStone(f"V{i}", datetime(2026, 10, 18, 20, 23), "outro", Decimal("39.23")) for i in range(3)
    ] + [
        api_saipos_vendas.VendaStone("C", datetime(2026, 10, 18, 21, 4), "credito", Decimal("59.18")),
        api_saipos_vendas.VendaStone("P1", datetime(2026, 10, 18, 21, 0), "pix", Decimal("5.00")),
        api_saipos_vendas.VendaStone("P2", datetime(2026, 10, 18, 21, 30), "pix", Decimal("5.00")),
    ]
    api_saipos_vendas.conciliar([vale, fechada, comum], stone)
    if (vale.casamento, len(vale.stone_ids_extra or [])) != ("soma", 2):
        raise AssertionError("vale dividido em 3 cartões deveria casar pela soma")
    if (fechada.stone_id, fechada.casamento) != ("C", "janela_ampla"):
        raise AssertionError("conta fechada depois da cobrança deveria casar pela janela ampla")
    if comum.stone_id is not None:
        raise AssertionError("valor comum com dois candidatos na janela ampla não pode casar")
    if api_saipos_vendas.categoria("Débito Pré-pago") != "debito" or api_saipos_vendas.categoria("Pix QRcode") != "pix":
        raise AssertionError("categoria de pagamento errada")
    esperar_erro(ValidacaoErro, "ainda não fechou", api_saipos_vendas.dias_do_periodo, date(2026, 10, 20), date(2026, 10, 20), date(2026, 10, 20))


def test_saipos_cancelamentos() -> None:
    import saipos_cancelamentos as sc

    def item(id_item, produto, criado, apagado=None, **extra):
        return {"id_sale_item": id_item, "desc_sale_item": produto, "unit_price": 20, "quantity": 1,
                "created_at": f"2026-10-18T{criado}:00", "deleted": "Y" if apagado else "N",
                "deleted_at": f"2026-10-18T{apagado}:00" if apagado else None, "created_by": 1, "deleted_by": 9,
                "id_store_cancellation_reason": 5, **extra}

    vendas = {
        1: {"id_sale": 1, "shift_date": "2026-10-18", "canceled": "N", "desc_sale": "10",
            "payments": [{"desc_store_payment_type": "Dinheiro", "payment_amount": 40, "created_at": "2026-10-18T21:10:00"}]},
        2: {"id_sale": 2, "shift_date": "2026-10-18", "canceled": "Y", "desc_sale": "11", "payments": []},
        3: {"id_sale": 3, "shift_date": "2026-10-18", "canceled": "N", "payments": []},
    }
    itens = {
        1: [
            item(10, "Chope Brahma", "20:00", "21:00"),  # servido, perto do pagamento, dinheiro
            item(11, "Filé", "20:00", "20:02"),  # correção: relançado logo depois
            item(12, "Filé", "20:03"),
            item(13, "Suco", "20:00", "20:01", id_sale_to=3),  # troca de mesa
        ],
        2: [item(20, "Edimburger", "18:00", "20:30"), item(21, "Edimburger", "18:00", "20:30")],
    }
    status = {2: [{"desc_store_sale_status": "Cancelados", "created_at": "2026-10-18T20:30:00",
                   "desc_cancellation_reason": "Cliente desistiu do pedido",
                   "user": {"id_user": 9, "full_name": "Caixa"}}]}
    nomes = sc.nomes_usuarios(status)
    cancelamentos, resumo = sc.montar(vendas, itens, status, nomes)
    por_id = {c["id"]: c for c in cancelamentos}
    if set(por_id) != {"item:10", "item:11", "mesa:2"}:
        raise AssertionError(f"cancelamentos errados: {sorted(por_id)}")
    chope = por_id["item:10"]
    if not chope["exige_justificativa"] or "provavelmente servido" not in chope["sinais"] or "mesa pagou em dinheiro" not in chope["sinais"]:
        raise AssertionError(f"chope servido e cancelado antes do pagamento deveria pedir justificativa: {chope}")
    if por_id["item:11"]["pontos"] != 0 or por_id["item:11"]["exige_justificativa"]:
        raise AssertionError("item relançado em seguida é correção, não caso de risco")
    mesa = por_id["mesa:2"]
    if not mesa["exige_justificativa"] or mesa["minutos"] != 150 or mesa["cancelou"] != "Caixa":
        raise AssertionError(f"mesa cancelada 150 min depois deveria pedir justificativa: {mesa}")
    if round(sum(r["valor"] for r in resumo), 2) != 100.0:
        raise AssertionError("resumo lançado deveria somar os itens sem a troca de mesa")


def main() -> int:
    test_stone_requisicao()
    test_stone_cabecalho_e_erros()
    test_stone_baixar_periodo()
    test_recebiveis_stone()
    test_pix_stone()
    test_pix_extrato()
    test_bb_configuracao()
    test_bb_token_e_paginas()
    test_bb_blocos_e_gravacao()
    test_saipos_vendas()
    test_saipos_cancelamentos()
    test_cli_sem_credenciais()
    print("API_BANCOS_TESTS_OK stone=3 recebiveis=1 pix=1 pix_extrato=1 saipos=2 bb=3 cli=2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
