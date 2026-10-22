#!/usr/bin/env python3
"""Contratos financeiros do cartão XML + Pix webhook, sem rede ou dados reais."""
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "importacao"))
import api_stone_vendas as v
from importacao_core import ValidacaoErro

DIA = date(2026, 10, 21)
DOC = "12345678000199"
E2E = "E" + "1" * 31
CSV = ("id;amount;status;payment_method;created_at;merchant__document;pix_transaction__e2e_id;"
       "pix_transaction__paid_amount;pix_transaction__canceled_amount;pix_transaction__fee_amount;"
       "pix_transaction__detail__operation;pix_transaction__terminal__serial_number\n"
       f"event-1;2980;paid;pix;2026-10-22T01:42:23Z;{DOC};{E2E};2980;0;0;pay;SN1\n")
XML = b'''<Conciliation><Header><StoneCode>123</StoneCode><ReferenceDate>20261021</ReferenceDate></Header>
<FinancialTransactions><Transaction><Events><Captures>1</Captures></Events>
<AcquirerTransactionKey>0000123</AcquirerTransactionKey><CaptureLocalDateTime>20261021194223</CaptureLocalDateTime>
<BrandId>2</BrandId><AccountType>2</AccountType><NumberOfInstallments>2</NumberOfInstallments>
<Poi><SerialNumber>SN2</SerialNumber></Poi><Installments>
<Installment><InstallmentNumber>1</InstallmentNumber><GrossAmount>15.00</GrossAmount><NetAmount>14.50</NetAmount><PrevisionPaymentDate>20261121</PrevisionPaymentDate></Installment>
<Installment><InstallmentNumber>2</InstallmentNumber><GrossAmount>14.80</GrossAmount><NetAmount>14.30</NetAmount><PrevisionPaymentDate>20261221</PrevisionPaymentDate></Installment>
</Installments></Transaction></FinancialTransactions></Conciliation>'''


def rejeita(fn, *args):
    try:
        fn(*args)
    except ValidacaoErro:
        return
    raise AssertionError("deveria recusar sem gravar")


def main():
    p = v.ler_pix(CSV, DIA, DOC)[0]
    assert p["stone_id"] == E2E and p["stone_id"] != "event-1"
    assert p["valor_bruto"] == Decimal("29.80") and p["valor_liquido"] == Decimal("29.80")
    assert p["data_venda"] == datetime(2026, 10, 21, 22, 42)
    assert p["stonecode"] is None and p["n_serie"] == "SN1"
    for texto in (CSV.replace(";paid;", ";canceled;"), CSV.replace(";pay;", ";cancel;"),
                  CSV.replace(DOC, "99999999000199"), CSV.replace(";0;0;pay;", ";1;0;pay;"),
                  CSV.replace(";2980;paid;", ";NaN;paid;"), CSV.replace(E2E, "event-only")):
        rejeita(v.ler_pix, texto, DIA, DOC)
    rejeita(v.ler_pix, CSV, date(2026, 10, 20), DOC)
    cartao = v.ler_cartao(XML, "123", DIA, DOC)[0]
    assert cartao["stone_id"] == "0000123"
    assert cartao["valor_bruto"] == Decimal("29.80") and cartao["valor_liquido"] == Decimal("28.80")
    assert cartao["desconto_mdr"] == Decimal("-1.00") and cartao["n_parcelas"] == 2
    assert cartao["data_venda"] == datetime(2026, 10, 21, 19, 42)
    assert len(v.deduplicar([cartao, p, p])) == 2
    rejeita(v.deduplicar, [p, {**p, "valor_bruto": Decimal("30")}])
    v.conferir_existentes([p], {E2E: p})
    rejeita(v.conferir_existentes, [p], {E2E: {**p, "valor_bruto": Decimal("30")}})
    rejeita(v.ler_cartao, XML.replace(b"<BrandId>2</BrandId>", b"<BrandId>99</BrandId>"), "123", DIA, DOC)
    # Tarifa diferente do MDR conferido não pode ser reclassificada como MDR.
    for campo in (b'<FeeType>2</FeeType>',b'<AdvanceRateAmount>1</AdvanceRateAmount>',
                  b'<SaleFee>1</SaleFee>',b'<AdvancedReceivableOriginalPaymentDate>20261121</AdvancedReceivableOriginalPaymentDate>'):
        rejeita(v.ler_cartao,XML.replace(b'<NumberOfInstallments>',campo+b'<NumberOfInstallments>'),"123",DIA,DOC)
    print("STONE_VENDAS_TESTS_OK valores=centavos fuso=UTC-3 dedup=StoneID_E2E parcelas=2 network=0")


if __name__ == "__main__":
    main()
