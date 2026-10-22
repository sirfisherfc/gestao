#!/usr/bin/env python3
"""Importa cartão do XML e Pix do webhook, juntos e sem repetir consultas Stone.

Só processa dias com ambos os arquivos recebidos. Usa os mesmos Stone IDs/E2Es
do CSV do Portal; linhas existentes são preservadas pelo ON CONFLICT.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys
from xml.etree import ElementTree

import api_stone_conciliacao as conciliacao
import api_stone_pix as pix
import api_stone_recebiveis as recebiveis
import integracao_log
from api_cliente import carregar_env
from importacao_core import (
    ErroOperacional, ValidacaoErro, _database_url, _referencia_projeto,
    atualizar_painel, executar_com_saida, importar_registros,
)

COLUNAS = ["conta_id", "documento", "stonecode", "data_venda", "bandeira", "produto",
           "stone_id", "n_parcelas", "valor_bruto", "valor_liquido", "desconto_mdr",
           "desconto_antecipacao", "desconto_unificado", "n_cartao", "meio_captura",
           "n_serie", "ultimo_status", "data_ultimo_status"]
ZERO = Decimal("0")


def linha_base(documento, **campos):
    linha = {c: None for c in COLUNAS[1:]}
    linha.update(documento=documento, desconto_antecipacao=ZERO, desconto_unificado=ZERO,
                 ultimo_status="Aprovada", meio_captura="POS")
    linha.update(campos)
    return linha


def ler_cartao(dados: bytes, stonecode: str, dia: date, documento: str) -> list[dict]:
    leitura = recebiveis.ler_arquivo(dados, stonecode, dia)
    if leitura.rejeicoes or leitura.cancelamentos:
        raise ValidacaoErro("arquivo com cancelamento/chargeback ou layout não validado para vendas; conferir CSV antes de importar")
    raiz = ElementTree.fromstring(dados)
    transacoes = {
        conciliacao.texto(t, "AcquirerTransactionKey"): t
        for secao in conciliacao.filhos(raiz, "FinancialTransactions")
        for t in conciliacao.filhos(secao, "Transaction")
    }
    linhas = []
    for captura in leitura.capturas:
        bandeira = recebiveis.BANDEIRAS.get(captura.brand_id)
        produto = recebiveis.PRODUTOS.get(captura.account_type)
        if not bandeira or not produto:
            raise ValidacaoErro("bandeira ou produto Stone sem regra validada")
        bruto = sum((p.bruto for p in captura.parcelas), ZERO)
        liquido = sum((p.liquido for p in captura.parcelas), ZERO)
        if bruto <= 0 or not bruto.is_finite() or not liquido.is_finite():
            raise ValidacaoErro("valores de cartão inválidos")
        transacao = transacoes[captura.stone_id]
        poi = next(iter(conciliacao.filhos(transacao, "Poi")), None)
        instante = captura.data_venda.replace(second=0, microsecond=0)
        if instante.date() != dia:
            raise ValidacaoErro("captura fora da data de referência; conferir o arquivo")
        linhas.append(linha_base(documento, stonecode=stonecode, data_venda=instante,
            bandeira=bandeira, produto=produto, stone_id=captura.stone_id,
            n_parcelas=captura.qtd_parcelas, valor_bruto=bruto, valor_liquido=liquido,
            desconto_mdr=liquido-bruto, n_cartao=conciliacao.texto(transacao, "CardNumber"),
            n_serie=conciliacao.texto(poi, "SerialNumber") if poi is not None else None,
            data_ultimo_status=instante))
    return linhas


def centavos(valor: str | None) -> Decimal:
    n = pix.decimal_ou_none(valor)
    if n is None or not n.is_finite() or n != n.to_integral_value():
        raise ValidacaoErro("valor Pix deve ser inteiro em centavos")
    return n / 100


def ler_pix(conteudo: str, dia: date, documento: str) -> list[dict]:
    linhas = []
    for item in pix.ler_csv(conteudo):
        if pix._so_digitos(item.get("merchant__document")) != pix._so_digitos(documento):
            raise ValidacaoErro("o Pix pertence a outro CNPJ; nenhuma venda gravada")
        if item.get("payment_method") != "pix" or item.get("status") != "paid":
            raise ValidacaoErro("evento Pix sem regra validada (pagamento/cancelamento); nenhuma venda gravada")
        operacao = item.get("pix_transaction__detail__operation")
        if operacao not in (None, "", "pay"):
            raise ValidacaoErro("operação Pix sem regra validada")
        chave = item.get("pix_transaction__e2e_id") or ""
        if not chave.startswith("E") or len(chave) < 20:
            raise ValidacaoErro("Pix sem identificador E2E válido; não usar o id do evento como Stone ID")
        instante = pix.data_hora_local(item.get("created_at"))
        if instante is None or instante.date() != dia:
            raise ValidacaoErro("data local do Pix não corresponde ao arquivo solicitado")
        instante = instante.replace(second=0, microsecond=0)
        bruto = centavos(item.get("amount"))
        tarifa = centavos(item.get("pix_transaction__fee_amount") or "0")
        pago = centavos(item.get("pix_transaction__paid_amount"))
        cancelado = centavos(item.get("pix_transaction__canceled_amount") or "0")
        if pago != bruto or cancelado:
            raise ValidacaoErro("Pix pago/cancelado diverge do valor da venda; conferir o evento")
        if bruto <= 0 or tarifa < 0 or tarifa > bruto:
            raise ValidacaoErro("valor ou tarifa Pix inválidos")
        linhas.append(linha_base(documento, data_venda=instante, produto="Pix QRcode",
            stone_id=chave, valor_bruto=bruto, valor_liquido=bruto-tarifa, desconto_mdr=-tarifa,
            n_serie=item.get("pix_transaction__terminal__serial_number") or None,
            data_ultimo_status=instante))
    return linhas


def deduplicar(linhas: list[dict]) -> list[dict]:
    por_id = {}
    for item in linhas:
        anterior = por_id.get(item["stone_id"])
        if anterior is not None and anterior != item:
            raise ValidacaoErro("mesmo Stone ID/E2E com conteúdos diferentes; nenhuma gravação")
        por_id[item["stone_id"]] = item
    return list(por_id.values())


def conferir_existentes(linhas, existentes):
    for item in linhas:
        atual = existentes.get(item["stone_id"])
        if not atual:
            continue
        for campo in ("stonecode", "data_venda", "valor_bruto", "produto"):
            if item[campo] != atual[campo]:
                raise ValidacaoErro(f"venda já importada diverge em {campo}; nenhuma gravação")


def fluxo():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--de", type=date.fromisoformat, required=True)
    parser.add_argument("--ate", type=date.fromisoformat)
    parser.add_argument("--stonecode", action="append")
    parser.add_argument("--pasta", type=Path, default=conciliacao.PASTA_PADRAO)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument('--sem-refresh-painel',action='store_true')
    op = parser.parse_args()
    carregar_env()
    url = _database_url()
    if _referencia_projeto(url) != "lucpxoynpvogkvzepagi":
        raise ErroOperacional("destino recusado: usar somente o Supabase portal")
    dias = conciliacao.dias_do_periodo(op.de, op.ate or op.de, date.today())
    codigos = conciliacao.resolver_stonecodes(op.stonecode)
    fila = pix.FilaPix()
    banco = recebiveis.ConsultaBanco()
    registros = []
    arquivos = []
    try:
        documentos = fila.documentos()
        if len(documentos) != 1:
            raise ValidacaoErro("não há um único CNPJ validado para o arquivo Pix")
        for dia in dias:
            for codigo in codigos:
                arquivo = op.pasta / codigo / f"{dia}.xml"
                if not arquivo.is_file():
                    raise ErroOperacional(f"XML de {dia} ainda não recebido; nenhuma consulta Stone será feita por este importador")
                registros.extend(ler_cartao(arquivo.read_bytes(), codigo, dia, banco.documento(codigo)))
            recebidos = [a for a in fila.arquivos(documentos[0], dia) if a.conteudo is not None and not a.erro]
            if not recebidos:
                raise ErroOperacional(f"Pix de {dia} ainda não recebido; cartão e Pix aguardam juntos, sem adiantar o corte do painel")
            escolhido = recebidos[0]
            registros.extend(ler_pix(escolhido.conteudo, dia, banco.documento(codigos[0])))
            arquivos.append(escolhido)
        registros = deduplicar(registros)
        with banco.conn.cursor() as cur:
            cur.execute("select stone_id, stonecode, data_venda, valor_bruto, produto from raw_stone_vendas where stone_id = any(%s)",
                        ([i["stone_id"] for i in registros],))
            existentes = {r[0]: dict(zip(("stonecode", "data_venda", "valor_bruto", "produto"), r[1:])) for r in cur.fetchall()}
        conferir_existentes(registros, existentes)
        novas = [r for r in registros if r["stone_id"] not in existentes]
        print(f"Vendas Stone: {len(registros)} confirmadas; {len(novas)} novas; {len(existentes)} já importadas.")
        if op.dry_run:
            print("DRY-RUN: arquivos conferidos; nenhuma gravação e nenhuma consulta Stone.")
            return
    finally:
        banco.fechar()
        fila.fechar()
    if registros:
        importar_registros(registros=registros, tabela="raw_stone_vendas", colunas=COLUNAS,
            conflito="(stone_id)", montar_linha=lambda r, conta: [conta]+[r[c] for c in COLUNAS[1:]],
            fonte_log="Vendas Stone (API cartão + Pix)", periodo=(op.de, dias[-1]), fonte_chave="stone_vendas")
    # Saipos já está no banco: refazer o casamento não consulta sua API.
    import api_saipos_vendas as saipos
    conn = saipos._conectar()
    try:
        with conn, conn.cursor() as cur:
            saipos.reconciliar_periodo(cur, op.de-timedelta(days=1), dias[-1])
    finally:
        conn.close()
    if not op.sem_refresh_painel:
        atualizar_painel()
    fila = pix.FilaPix()
    try:
        for arquivo in arquivos:
            fila.marcar_processado(arquivo)
    finally:
        fila.fechar()
    por_dia = Counter(r["data_venda"].date() for r in novas)
    dias_com_vendas = {r['data_venda'].date() for r in registros}
    integracao_log.registrar([integracao_log.Execucao("stone_vendas", d, None, "ok" if d in dias_com_vendas else "sem_movimento", por_dia[d],
        "Cartão XML e Pix webhook recebidos; vendas atualizadas e conciliadas") for d in dias])
    print("STONE_VENDAS_IMPORT_OK cartão e Pix gravados; conciliação e painel atualizados.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
