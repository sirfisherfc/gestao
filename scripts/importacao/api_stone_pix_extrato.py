#!/usr/bin/env python3
"""Vendas Pix da Stone a partir do extrato da conta (Pluggy ou CSV).

No extrato Stone, Pix de venda na maquininha chega como crédito ``Transação``
e Pix de transferência como ``Pix``. Em setembro/2026, as 528 vendas Pix do CSV
de vendas casaram uma a uma com um crédito ``Transação`` de mesmo valor, no
mesmo minuto ou com 1 minuto de diferença. Sobraram 4 créditos internos, de
madrugada e com pagador ``Desconhecido``, que não são vendas.

Hoje o script só compara; não grava. O extrato não traz o identificador do Pix
(o STONE ID do CSV de vendas), então gravar por aqui e também importar o CSV
de vendas duplicaria o Pix. A gravação depende de decidir a virada: o CSV de
vendas deixa de gravar Pix a partir de uma data, como já acontece com o
extrato da Pluggy. É a alternativa ao arquivo Pix por webhook
(``api_stone_pix.py``), que continua disponível quando a API de Conciliação
voltar a responder.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

import api_stone_conciliacao as conciliacao
from api_cliente import carregar_env
from importacao_core import executar_com_saida


TIPO_VENDA_PIX = "Transação"
PAGADOR_INTERNO = "Desconhecido"
TOLERANCIA_MINUTOS = 2


@dataclass(frozen=True)
class CreditoPix:
    dedup_hash: str
    data_hora: datetime
    valor: Decimal
    origem_carga: str


@dataclass(frozen=True)
class VendaPix:
    stone_id: str
    data_venda: datetime
    valor_bruto: Decimal


def eh_venda_pix(tipo: str | None, valor, origem_documento: str | None) -> bool:
    return tipo == TIPO_VENDA_PIX and valor is not None and valor > 0 and (origem_documento or "") != PAGADOR_INTERNO


def casar(creditos: list[CreditoPix], vendas: list[VendaPix]) -> tuple[list[tuple[CreditoPix, VendaPix, int]], list[CreditoPix], list[VendaPix]]:
    """Casa crédito e venda de mesmo valor, do mais próximo ao mais distante no tempo."""
    livres: dict[Decimal, list[VendaPix]] = {}
    for venda in sorted(vendas, key=lambda item: item.data_venda):
        livres.setdefault(round(venda.valor_bruto, 2), []).append(venda)
    pares, sobras = [], []
    for credito in sorted(creditos, key=lambda item: item.data_hora):
        candidatos = livres.get(round(credito.valor, 2), [])
        melhor = None
        for venda in candidatos:
            minutos = round((venda.data_venda.replace(second=0) - credito.data_hora.replace(second=0)).total_seconds() / 60)
            if abs(minutos) <= TOLERANCIA_MINUTOS and (melhor is None or abs(minutos) < abs(melhor[1])):
                melhor = (venda, minutos)
        if melhor:
            candidatos.remove(melhor[0])
            pares.append((credito, melhor[0], melhor[1]))
        else:
            sobras.append(credito)
    return pares, sobras, [venda for lista in livres.values() for venda in lista]


def linha_venda(credito: CreditoPix, documento: str | None) -> dict:
    """Linha de ``raw_stone_vendas`` no formato das vendas Pix do CSV, para a futura gravação."""
    data_venda = credito.data_hora.replace(second=0, microsecond=0)
    return {
        "documento": documento, "stonecode": None, "data_venda": data_venda, "bandeira": None,
        "produto": "Pix QRcode", "stone_id": f"EXTRATO-{credito.dedup_hash}", "n_parcelas": None,
        "valor_bruto": credito.valor, "valor_liquido": credito.valor, "desconto_mdr": Decimal("0"),
        "desconto_antecipacao": Decimal("0"), "desconto_unificado": Decimal("0"), "n_cartao": None,
        "meio_captura": "POS", "n_serie": None, "ultimo_status": "Aprovada", "data_ultimo_status": data_venda,
    }


def ler_banco(inicio: date, fim: date) -> tuple[list[CreditoPix], list[VendaPix]]:
    from importacao_core import _database_url

    import psycopg2

    conn = psycopg2.connect(_database_url())
    try:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            margem = timedelta(minutes=TOLERANCIA_MINUTOS + 1)
            cur.execute(
                "select dedup_hash, data_hora, valor, origem_carga, tipo, origem_documento from raw_stone_extrato "
                "where data_hora >= %s and data_hora < %s;",
                (inicio, fim + timedelta(days=1)),
            )
            creditos = [
                CreditoPix(linha[0], linha[1], Decimal(linha[2]), linha[3])
                for linha in cur.fetchall() if eh_venda_pix(linha[4], linha[2], linha[5])
            ]
            cur.execute(
                "select stone_id, data_venda, valor_bruto from raw_stone_vendas "
                "where produto ilike 'pix%%' and data_venda >= %s and data_venda < %s;",
                (datetime.combine(inicio, datetime.min.time()) - margem, datetime.combine(fim + timedelta(days=1), datetime.min.time()) + margem),
            )
            vendas = [VendaPix(linha[0], linha[1], Decimal(linha[2])) for linha in cur.fetchall()]
    finally:
        conn.close()
    return creditos, vendas


def fluxo() -> None:
    parser = argparse.ArgumentParser(description="Compara as vendas Pix do extrato Stone com as do CSV de vendas")
    parser.add_argument("--de", type=conciliacao._data_iso, required=True, help="primeiro dia (AAAA-MM-DD)")
    parser.add_argument("--ate", type=conciliacao._data_iso, required=True, help="último dia (AAAA-MM-DD)")
    opcoes = parser.parse_args()
    carregar_env()
    creditos, vendas = ler_banco(opcoes.de, opcoes.ate)
    vendas_periodo = [venda for venda in vendas if opcoes.de <= venda.data_venda.date() <= opcoes.ate]
    pares, sobras, sem_credito = casar(creditos, vendas)
    sem_credito = [venda for venda in sem_credito if opcoes.de <= venda.data_venda.date() <= opcoes.ate]
    por_dia = Counter(credito.data_hora.date() for credito in sobras)
    print(f"Pix de venda no extrato ({opcoes.de} a {opcoes.ate}): {len(creditos)} crédito(s) {dict(Counter(c.origem_carga for c in creditos))}")
    print(f"Vendas Pix do CSV no período: {len(vendas_periodo)}")
    print(f"  casados:                 {len(pares)} (diferença em minutos: {dict(Counter(item[2] for item in pares))})")
    print(f"  só no extrato:           {len(sobras)} {dict(sorted(por_dia.items()))}")
    print(f"  só no CSV de vendas:     {len(sem_credito)}")
    print("\n[COMPARAÇÃO] Nada foi gravado; a gravação depende da virada do CSV de vendas.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
