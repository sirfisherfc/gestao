#!/usr/bin/env python3
"""Importa os recebíveis Stone a partir do arquivo de conciliação da API.

Substitui o CSV de recebíveis. Cada parcela capturada vira uma linha ``Venda``
de ``raw_stone_recebiveis`` e cada cancelamento uma linha ``Cancelamento`` ou
``Cancelamento Parcial``, com a mesma chave ``(stone_id, n_parcela,
categoria)`` e as convenções do CSV. A equivalência foi provada em 20/10/2026
com setembro inteiro: as 1.638 parcelas do CSV e da API têm as mesmas chaves,
valores e datas.

As vendas continuam no CSV: o arquivo da API não traz Pix nem Voucher, e
gravar só o cartão adiantaria ``corte_venda`` com dias incompletos.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree

import api_stone_conciliacao as conciliacao
import integracao_log
from api_cliente import carregar_env, variavel
from api_stone_conciliacao import filhos, local, texto
from importacao_core import (
    LIMITE_REJEICOES_EXIBIDAS,
    ErroOperacional,
    ImportacaoErro,
    ValidacaoErro,
    atualizar_painel,
    executar_com_saida,
    importar_registros,
    imprimir_resultado,
)


# Códigos do arquivo de conciliação e os textos que o CSV usa para eles,
# conferidos nas 1.508 vendas de setembro/2026. Código novo recusa a carga
# até ser conferido; adivinhar o texto quebraria os filtros por bandeira.
BANDEIRAS = {"1": "Visa", "2": "MasterCard", "3": "AmericanExpress", "171": "Elo"}
PRODUTOS = {"1": "Debito", "2": "Credito", "3": "Debito Pre-pago", "4": "Credito Pre-pago"}
COLUNAS = [
    "conta_id", "documento", "stonecode", "categoria", "data_venda",
    "data_vencimento", "data_vencimento_original", "bandeira", "produto",
    "stone_id", "qtd_parcelas", "n_parcela", "valor_bruto", "valor_liquido",
    "desconto_mdr", "desconto_antecipacao", "desconto_unificado",
    "ultimo_status", "data_ultimo_status", "entradas_brutas", "saidas_brutas",
]
FONTE = "stone_recebiveis"
CAMPOS_COMPARADOS = ("data_venda", "data_vencimento", "valor_bruto", "valor_liquido")
EVENTOS_SEM_REGRA = ("Chargebacks", "ChargebackRefunds")
ZERO = Decimal("0")
TOLERANCIA = Decimal("0.01")


@dataclass(frozen=True)
class Parcela:
    numero: int
    bruto: Decimal
    liquido: Decimal
    previsao: date


@dataclass(frozen=True)
class Captura:
    stone_id: str
    stonecode: str
    data_venda: datetime
    brand_id: str | None
    account_type: str | None
    qtd_parcelas: int
    parcelas: tuple[Parcela, ...]
    origem: tuple[str, date] | None = None


@dataclass(frozen=True)
class Cancelamento:
    stone_id: str
    stonecode: str
    operacao: str
    data: datetime
    devolvido: Decimal
    cobrado: Decimal
    previsao: date
    origem: tuple[str, date] | None = None


@dataclass
class Leitura:
    capturas: list[Captura] = field(default_factory=list)
    cancelamentos: list[Cancelamento] = field(default_factory=list)
    pagamentos: dict[tuple[str, int], tuple[date, date]] = field(default_factory=dict)
    cobrancas: dict[str, tuple[date, date]] = field(default_factory=dict)
    eventos_ignorados: int = 0
    rejeicoes: list[str] = field(default_factory=list)

    def juntar(self, outra: "Leitura") -> None:
        self.capturas.extend(outra.capturas)
        self.cancelamentos.extend(outra.cancelamentos)
        self.pagamentos.update(outra.pagamentos)
        self.cobrancas.update(outra.cobrancas)
        self.eventos_ignorados += outra.eventos_ignorados
        self.rejeicoes.extend(outra.rejeicoes)


@dataclass(frozen=True)
class VendaConhecida:
    bandeira: str | None
    produto: str | None
    qtd_parcelas: int | None
    bruto_total: Decimal


def _data_hora(valor: str | None, contexto: str) -> datetime:
    try:
        return datetime.strptime((valor or "")[:14], "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise ValueError(f"{contexto} inválida") from exc


def _data(valor: str | None, contexto: str) -> date:
    try:
        return datetime.strptime((valor or "")[:8], "%Y%m%d").date()
    except ValueError as exc:
        raise ValueError(f"{contexto} inválida") from exc


def _decimal(valor: str | None, contexto: str) -> Decimal:
    try:
        return Decimal(valor or "")
    except InvalidOperation as exc:
        raise ValueError(f"{contexto} inválido") from exc


def _contagem(eventos, nome: str) -> int:
    try:
        return int(texto(eventos, nome) or 0) if eventos is not None else 0
    except ValueError:
        return 0


def _ler_captura(transacao, stonecode: str, origem: tuple[str, date]) -> Captura:
    stone_id = texto(transacao, "AcquirerTransactionKey")
    parcelas = []
    for grupo in filhos(transacao, "Installments"):
        for parcela in filhos(grupo, "Installment"):
            parcelas.append(Parcela(
                numero=int(texto(parcela, "InstallmentNumber") or 0),
                bruto=_decimal(texto(parcela, "GrossAmount"), "valor bruto da parcela"),
                liquido=_decimal(texto(parcela, "NetAmount"), "valor líquido da parcela"),
                previsao=_data(texto(parcela, "PrevisionPaymentDate"), "previsão de pagamento"),
            ))
    if not stone_id or not parcelas:
        raise ValueError("captura sem chave ou sem parcelas")
    return Captura(
        stone_id=stone_id,
        stonecode=stonecode,
        data_venda=_data_hora(texto(transacao, "CaptureLocalDateTime"), "data da captura"),
        brand_id=texto(transacao, "BrandId"),
        account_type=texto(transacao, "AccountType"),
        qtd_parcelas=int(texto(transacao, "NumberOfInstallments") or len(parcelas)),
        parcelas=tuple(parcelas),
        origem=origem,
    )


def _ler_cancelamentos(transacao, stonecode: str, origem: tuple[str, date]) -> list[Cancelamento]:
    stone_id = texto(transacao, "AcquirerTransactionKey")
    lidos = []
    for grupo in filhos(transacao, "Cancellations"):
        for item in filhos(grupo, "Cancellation"):
            cobranca = next(iter(filhos(item, "Billing")), None)
            lidos.append(Cancelamento(
                stone_id=stone_id,
                stonecode=stonecode,
                operacao=texto(item, "OperationKey") or "",
                data=_data_hora(texto(item, "CancellationDateTime"), "data do cancelamento"),
                devolvido=_decimal(texto(item, "ReturnedAmount"), "valor devolvido"),
                cobrado=_decimal(texto(cobranca, "ChargedAmount") if cobranca is not None else None, "valor cobrado"),
                previsao=_data(texto(cobranca, "PrevisionChargeDate") if cobranca is not None else None, "previsão da cobrança"),
                origem=origem,
            ))
    return lidos


def _ler_liquidacao(transacao, chave: str | None, leitura: Leitura) -> None:
    """Pagamentos de parcelas e cobranças de cancelamento feitos no dia."""
    for grupo in filhos(transacao, "Installments"):
        for parcela in filhos(grupo, "Installment"):
            pagamento = _data(texto(parcela, "PaymentDate"), "data de pagamento")
            original = texto(parcela, "OriginalPaymentDate")
            leitura.pagamentos[(chave, int(texto(parcela, "InstallmentNumber") or 0))] = (
                pagamento, _data(original, "data original de pagamento") if original else pagamento,
            )
    for grupo in filhos(transacao, "Cancellations"):
        for item in filhos(grupo, "Cancellation"):
            cobranca = next(iter(filhos(item, "Billing")), None)
            if cobranca is None or not texto(cobranca, "ChargeDate"):
                continue
            data_cobranca = _data(texto(cobranca, "ChargeDate"), "data da cobrança")
            original = texto(cobranca, "OriginalChargeDate")
            leitura.cobrancas[texto(item, "OperationKey") or ""] = (
                data_cobranca, _data(original, "data original da cobrança") if original else data_cobranca,
            )


def ler_arquivo(dados: bytes, stonecode: str, dia: date) -> Leitura:
    conciliacao.conferir_cabecalho(conciliacao.resumir_xml(dados), stonecode, dia)
    raiz = ElementTree.fromstring(dados)
    leitura = Leitura()
    for secao in raiz:
        nome = local(secao.tag)
        if nome == "FinancialTransactions":
            for transacao in filhos(secao, "Transaction"):
                chave = texto(transacao, "AcquirerTransactionKey") or "(sem chave)"
                eventos = next(iter(filhos(transacao, "Events")), None)
                try:
                    if _contagem(eventos, "Captures"):
                        leitura.capturas.append(_ler_captura(transacao, stonecode, (stonecode, dia)))
                    if _contagem(eventos, "Cancellations"):
                        leitura.cancelamentos.extend(_ler_cancelamentos(transacao, stonecode, (stonecode, dia)))
                except ValueError as exc:
                    leitura.rejeicoes.append(f"{stonecode} {dia} {chave}: {exc}")
                for evento in EVENTOS_SEM_REGRA:
                    if _contagem(eventos, evento):
                        leitura.rejeicoes.append(
                            f"{stonecode} {dia} {chave}: {evento} sem regra de importação; "
                            "importe o CSV de recebíveis deste dia"
                        )
        elif nome == "FinancialTransactionsAccounts":
            for transacao in filhos(secao, "Transaction"):
                chave = texto(transacao, "AcquirerTransactionKey")
                try:
                    _ler_liquidacao(transacao, chave, leitura)
                except ValueError as exc:
                    leitura.rejeicoes.append(f"{stonecode} {dia} {chave}: {exc}")
        elif nome.startswith("FinancialEvent") and not nome.endswith("Expected"):
            leitura.eventos_ignorados += len(filhos(secao, "Event"))
    return leitura


def _linha(origem: tuple[str, date] | None, **valores) -> dict:
    """Linha no formato de COLUNAS; ``_origem`` aponta o arquivo e não é gravada."""
    linha = {coluna: None for coluna in COLUNAS[1:]}
    linha.update(valores)
    linha["_origem"] = origem
    return linha


def linhas_de_captura(captura: Captura, pagamentos: dict, documento: str | None) -> tuple[list[dict], list[str]]:
    bandeira = BANDEIRAS.get(captura.brand_id or "")
    produto = PRODUTOS.get(captura.account_type or "")
    rejeicoes = []
    if bandeira is None:
        rejeicoes.append(f"{captura.stone_id}: BrandId {captura.brand_id} sem bandeira mapeada")
    if produto is None:
        rejeicoes.append(f"{captura.stone_id}: AccountType {captura.account_type} sem produto mapeado")
    if rejeicoes:
        return [], rejeicoes
    linhas = []
    for parcela in captura.parcelas:
        pago = pagamentos.get((captura.stone_id, parcela.numero))
        vencimento, original = pago if pago else (parcela.previsao, parcela.previsao)
        linhas.append(_linha(
            captura.origem,
            documento=documento,
            stonecode=captura.stonecode,
            categoria="Venda",
            data_venda=captura.data_venda,
            data_vencimento=vencimento,
            data_vencimento_original=original,
            bandeira=bandeira,
            produto=produto,
            stone_id=captura.stone_id,
            qtd_parcelas=captura.qtd_parcelas,
            n_parcela=parcela.numero,
            valor_bruto=parcela.bruto,
            valor_liquido=parcela.liquido,
            desconto_mdr=parcela.liquido - parcela.bruto,
            desconto_antecipacao=ZERO,
            desconto_unificado=ZERO,
            ultimo_status="Pago" if pago else "Aberto",
            data_ultimo_status=datetime.combine(vencimento, datetime.min.time()),
            entradas_brutas=parcela.bruto,
            saidas_brutas=ZERO,
        ))
    return linhas, []


def linha_de_cancelamento(cancelamento: Cancelamento, venda: VendaConhecida | None, cobrancas: dict, documento: str | None) -> tuple[dict | None, str | None]:
    if venda is None:
        return None, (
            f"{cancelamento.stone_id}: cancelamento de venda que não está no período nem no painel; "
            "importe o CSV de recebíveis deste dia"
        )
    if venda.qtd_parcelas != 1:
        return None, (
            f"{cancelamento.stone_id}: cancelamento de venda parcelada ainda sem regra; "
            "importe o CSV de recebíveis deste dia"
        )
    cobrado = cobrancas.get(cancelamento.operacao)
    vencimento, original = cobrado if cobrado else (cancelamento.previsao, cancelamento.previsao)
    total = cancelamento.devolvido >= venda.bruto_total - TOLERANCIA
    return _linha(
        cancelamento.origem,
        documento=documento,
        stonecode=cancelamento.stonecode,
        categoria="Cancelamento" if total else "Cancelamento Parcial",
        data_venda=cancelamento.data,
        data_vencimento=vencimento,
        data_vencimento_original=original,
        bandeira=venda.bandeira,
        produto=venda.produto,
        stone_id=cancelamento.stone_id,
        qtd_parcelas=1,
        n_parcela=1,
        valor_bruto=-cancelamento.devolvido,
        valor_liquido=-cancelamento.cobrado,
        desconto_mdr=cancelamento.devolvido - cancelamento.cobrado,
        desconto_antecipacao=ZERO,
        desconto_unificado=ZERO,
        ultimo_status="Pago" if cobrado else "Aberto",
        data_ultimo_status=datetime.combine(vencimento, datetime.min.time()),
        entradas_brutas=ZERO,
        saidas_brutas=-cancelamento.devolvido,
    ), None


def montar_registros(leitura: Leitura, banco) -> tuple[list[dict], list[str]]:
    """``banco`` responde ``documento(stonecode)`` e ``venda(stone_id)``."""
    registros: list[dict] = []
    rejeicoes = list(leitura.rejeicoes)
    documentos: dict[str, str | None] = {}
    vendas_lote: dict[str, VendaConhecida] = {}

    def documento(stonecode: str) -> str | None:
        if stonecode not in documentos:
            documentos[stonecode] = banco.documento(stonecode)
        return documentos[stonecode]

    for captura in leitura.capturas:
        linhas, erros = linhas_de_captura(captura, leitura.pagamentos, documento(captura.stonecode))
        registros.extend(linhas)
        rejeicoes.extend(erros)
        if linhas:
            vendas_lote[captura.stone_id] = VendaConhecida(
                bandeira=linhas[0]["bandeira"],
                produto=linhas[0]["produto"],
                qtd_parcelas=captura.qtd_parcelas,
                bruto_total=sum((parcela.bruto for parcela in captura.parcelas), ZERO),
            )
    for cancelamento in leitura.cancelamentos:
        venda = vendas_lote.get(cancelamento.stone_id) or banco.venda(cancelamento.stone_id)
        linha, erro = linha_de_cancelamento(cancelamento, venda, leitura.cobrancas, documento(cancelamento.stonecode))
        if linha:
            registros.append(linha)
        if erro:
            rejeicoes.append(erro)
    return registros, rejeicoes


class ConsultaBanco:
    """Leituras do painel em transação somente leitura."""

    def __init__(self):
        from importacao_core import _database_url

        try:
            import psycopg2
        except ImportError as exc:
            raise ErroOperacional(
                "dependências ausentes; execute: python -m pip install -r requirements.txt"
            ) from exc
        try:
            self.conn = psycopg2.connect(_database_url())
        except psycopg2.Error as exc:
            raise ErroOperacional("não foi possível ler o painel para conferir os recebíveis") from exc
        self.conn.set_session(readonly=True)

    def documento(self, stonecode: str) -> str | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "select documento from raw_stone_recebiveis where stonecode = %s and documento is not null "
                "order by data_venda desc limit 1;",
                (stonecode,),
            )
            linha = cur.fetchone()
        return linha[0] if linha else None

    def venda(self, stone_id: str) -> VendaConhecida | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "select max(bandeira), max(produto), max(qtd_parcelas), sum(valor_bruto) "
                "from raw_stone_recebiveis where stone_id = %s and categoria = 'Venda';",
                (stone_id,),
            )
            linha = cur.fetchone()
        if not linha or linha[3] is None:
            return None
        return VendaConhecida(bandeira=linha[0], produto=linha[1], qtd_parcelas=linha[2], bruto_total=Decimal(linha[3]))

    def existentes(self, registros: list[dict]) -> dict[tuple, dict]:
        stone_ids = sorted({item["stone_id"] for item in registros})
        if not stone_ids:
            return {}
        with self.conn.cursor() as cur:
            cur.execute(
                "select stone_id, n_parcela, categoria, data_venda, data_vencimento, valor_bruto, valor_liquido "
                "from raw_stone_recebiveis where stone_id = any(%s);",
                (stone_ids,),
            )
            return {
                (linha[0], linha[1], linha[2]): dict(zip(CAMPOS_COMPARADOS, linha[3:]))
                for linha in cur.fetchall()
            }

    def fechar(self) -> None:
        self.conn.close()


def _igual(campo: str, novo, atual) -> bool:
    if campo.startswith("valor"):
        return atual is not None and abs(Decimal(novo) - Decimal(atual)) <= TOLERANCIA
    return novo == atual


def comparar(registros: list[dict], existentes: dict[tuple, dict]) -> dict[str, int]:
    novas, iguais, diferentes, exemplos = 0, 0, 0, []
    for item in registros:
        atual = existentes.get((item["stone_id"], item["n_parcela"], item["categoria"]))
        if atual is None:
            novas += 1
            continue
        divergentes = [campo for campo in CAMPOS_COMPARADOS if not _igual(campo, item[campo], atual[campo])]
        if divergentes:
            diferentes += 1
            if len(exemplos) < 5:
                exemplos.append(f"{item['stone_id']}/{item['n_parcela']}/{item['categoria']}: {', '.join(divergentes)}")
        else:
            iguais += 1
    print("\n== Comparação com o painel ==")
    print(f"  parcelas novas:            {novas}")
    print(f"  já no painel, iguais:      {iguais}")
    print(f"  já no painel, diferentes:  {diferentes} (a carga não altera linhas existentes)")
    for exemplo in exemplos:
        print(f"    {exemplo}")
    return {"novas": novas, "iguais": iguais, "diferentes": diferentes}


def periodo_dos_registros(registros: list[dict]) -> tuple[date, date]:
    datas = sorted(item["data_vencimento"] or item["data_venda"].date() for item in registros)
    return datas[0], datas[-1]


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Importa recebíveis Stone pelos arquivos de conciliação da API")
    parser.add_argument("--de", type=conciliacao._data_iso, help="primeiro dia (AAAA-MM-DD); padrão: ontem")
    parser.add_argument("--ate", type=conciliacao._data_iso, help="último dia (AAAA-MM-DD); padrão: igual a --de")
    parser.add_argument("--stonecode", action="append", help="stonecode a importar; repita para vários (padrão: os que entram no faturamento)")
    parser.add_argument("--pasta", type=Path, default=conciliacao.PASTA_PADRAO, help="pasta dos XML baixados")
    parser.add_argument("--baixar", action="store_true", help="baixa da Stone os dias que ainda não estão na pasta")
    parser.add_argument("--dry-run", action="store_true", help="lê, confere e compara com o painel sem gravar")
    parser.add_argument("--sem-refresh-painel", action="store_true", help="grava sem atualizar as views do painel")
    return parser


def ler_periodo(pasta: Path, alvos: list[tuple[str, date]]) -> tuple[Leitura, list[tuple[str, date]]]:
    """Lê os XML presentes e devolve também os (stonecode, dia) sem arquivo."""
    leitura = Leitura()
    ausentes = []
    for stonecode, dia in alvos:
        arquivo = pasta / stonecode / f"{dia.isoformat()}.xml"
        if not arquivo.is_file():
            ausentes.append((stonecode, dia))
            continue
        leitura.juntar(ler_arquivo(arquivo.read_bytes(), stonecode, dia))
    return leitura, ausentes


def resumo(leitura: Leitura, registros: list[dict]) -> None:
    categorias: dict[str, int] = {}
    for item in registros:
        categorias[item["categoria"]] = categorias.get(item["categoria"], 0) + 1
    chaves = {(item["stone_id"], item["n_parcela"], item["categoria"]) for item in registros}
    print("\n== Resumo dos arquivos ==")
    print(f"  vendas capturadas:   {len(leitura.capturas)}")
    print(f"  cancelamentos:       {len(leitura.cancelamentos)}")
    print(f"  parcelas pagas:      {len(leitura.pagamentos)} (atualizam vencimento e status das parcelas do período)")
    print(f"  eventos ignorados:   {leitura.eventos_ignorados} (o CSV de recebíveis também não os traz)")
    print(f"  linhas montadas:     {len(registros)} {categorias}")
    print(f"  duplicatas internas: {len(registros) - len(chaves)}")


def _execucoes(alvos, situacao_por_alvo, erros) -> list[integracao_log.Execucao]:
    execucoes = []
    for alvo in alvos:
        stonecode, dia = alvo
        if alvo in erros:
            execucoes.append(integracao_log.Execucao(FONTE, dia, stonecode, "erro", mensagem=erros[alvo]))
        elif alvo in situacao_por_alvo:
            situacao, novas = situacao_por_alvo[alvo]
            execucoes.append(integracao_log.Execucao(FONTE, dia, stonecode, situacao, linhas_novas=novas))
    return execucoes


def fluxo() -> None:
    opcoes = criar_parser().parse_args()
    carregar_env()
    stonecodes = conciliacao.resolver_stonecodes(opcoes.stonecode)
    hoje = date.today()
    inicio = opcoes.de or hoje - timedelta(days=1)
    dias = conciliacao.dias_do_periodo(inicio, opcoes.ate or inicio, hoje)
    alvos = [(stonecode, dia) for stonecode in stonecodes for dia in dias]
    registrar = not opcoes.dry_run
    print(f"Recebíveis Stone pela API: {len(dias)} dia(s), stonecode(s) {', '.join(stonecodes)}.")

    erros: dict[tuple[str, date], str] = {}
    if opcoes.baixar:
        for stonecode, dia, mensagem in conciliacao.baixar_periodo(
            variavel("STONE_CONCILIACAO_API_KEY"), stonecodes, dias,
            conciliacao.LAYOUT_PADRAO, opcoes.pasta, sobrescrever=False,
        ):
            erros[(stonecode, dia)] = mensagem

    try:
        leitura, ausentes = ler_periodo(opcoes.pasta, alvos)
        for alvo in ausentes:
            erros.setdefault(alvo, "arquivo não baixado; rode com --baixar")
        banco = ConsultaBanco()
        try:
            registros, rejeicoes = montar_registros(leitura, banco)
            resumo(leitura, registros)
            if rejeicoes:
                amostra = "; ".join(rejeicoes[:LIMITE_REJEICOES_EXIBIDAS])
                raise ValidacaoErro(f"{len(rejeicoes)} rejeição(ões); nenhuma gravação foi feita. {amostra}")
            existentes = banco.existentes(registros)
            comparar(registros, existentes)
        finally:
            banco.fechar()

        presentes = [alvo for alvo in alvos if alvo not in erros]
        linhas = Counter(item["_origem"] for item in registros)
        novas = Counter(
            item["_origem"] for item in registros
            if (item["stone_id"], item["n_parcela"], item["categoria"]) not in existentes
        )
        if opcoes.dry_run:
            print("\n[DRY-RUN] Arquivos válidos; nada foi gravado no banco.")
        elif registros:
            print("\n== Gravando, recalculando e registrando carga ==")
            imprimir_resultado(importar_registros(
                registros=registros,
                tabela="raw_stone_recebiveis",
                colunas=COLUNAS,
                conflito="(stone_id, n_parcela, categoria)",
                montar_linha=lambda item, conta_id: [conta_id] + [item[coluna] for coluna in COLUNAS[1:]],
                fonte_log="Recebíveis Stone",
                periodo=periodo_dos_registros(registros),
                fonte_chave="stone_recebiveis",
            ))
            if not opcoes.sem_refresh_painel:
                print("\n== Atualizando painel ==")
                atualizar_painel()
                print("  painel atualizado.")
        else:
            print("\nNenhuma parcela no período; nada a gravar.")
    except ImportacaoErro as exc:
        if registrar:
            falhou = {alvo: erros.get(alvo, str(exc)) for alvo in alvos}
            integracao_log.registrar(_execucoes(alvos, {}, falhou))
        raise

    if registrar:
        situacao = {
            alvo: ("ok" if linhas[alvo] else "sem_movimento", novas[alvo]) for alvo in presentes
        }
        integracao_log.registrar(_execucoes(alvos, situacao, erros))
    if erros:
        for (stonecode, dia), mensagem in sorted(erros.items()):
            print(f"  sem arquivo {stonecode} {dia}: {mensagem}")
        raise ErroOperacional(f"{len(erros)} dia(s) sem arquivo da Stone; os demais foram processados")
    print("\nOK.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
