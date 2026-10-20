#!/usr/bin/env python3
"""Importa somente movimentos novos do extrato Stone via Meu Pluggy.

Confere o legado por dia/valor/quantidade e os registros Pluggy por ID e
conteúdo. Saldo anterior + novos movimentos deve fechar com o snapshot da
conta. Ambiguidade, alteração ou falta de cobertura interrompe a carga inteira.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from contextlib import closing
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import re
import sys
import unicodedata

from api_cliente import carregar_env
from api_pluggy import Cliente, FUSO, conferir_item, data_local, validar_id, valor_env
from importacao_core import ErroOperacional, _database_url, _referencia_projeto, atualizar_painel, executar_com_saida
from integracao_log import Execucao, registrar

COLUNAS = ("conta_id", "movimentacao", "tipo", "valor", "saldo_antes", "saldo_depois",
           "tarifa", "data_hora", "data_hora_raw", "horario", "situacao", "nosso_numero",
           "destino", "destino_documento", "destino_instituicao", "destino_agencia", "destino_conta",
           "origem", "origem_documento", "origem_instituicao", "origem_agencia", "origem_conta",
           "descricao", "origem_carga", "dedup_hash")


def moeda(valor) -> Decimal:
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite() or numero != numero.quantize(Decimal("0.01")):
            raise ValueError
        return numero.quantize(Decimal("0.01"))
    except (ValueError, InvalidOperation) as exc:
        raise ErroOperacional("valor Pluggy inválido ou com fração de centavo") from exc


def normalizar(valor) -> str:
    return unicodedata.normalize("NFKD", str(valor or "")).encode("ascii", "ignore").decode().upper()


def documento(valor) -> str | None:
    if isinstance(valor, dict):
        valor = valor.get("value") or valor.get("number")
    numero = re.sub(r"\D", "", str(valor or ""))
    if not numero:
        return None
    # Mesmo trecho de CPF do CSV: conserva o DE-Para já usado pelo painel.
    if len(numero) == 11:
        return f"***.{numero[3:6]}.{numero[6:9]}-**"
    if len(numero) != 14:
        raise ErroOperacional("documento de contraparte Pluggy em formato não reconhecido")
    # O DE-Para identifica CNPJ pelo separador '/'; só dígitos não o acionam.
    return f"{numero[:2]}.{numero[2:5]}.{numero[5:8]}/{numero[8:12]}-{numero[12:]}"


def tipo_legado(item: dict) -> str:
    op = item.get("operationType")
    credito = item["type"] == "CREDIT"
    descricao = normalizar(item.get("description"))
    if op == "PIX":
        return "Pix" if not credito or descricao.startswith("TRANSFER") else "Transação"
    if op == "CARTAO":
        return "Recebível de Cartão" if credito else "Transação"
    if op == "TED":
        return "TED"
    if op == "BOLETO":
        if credito:
            raise ErroOperacional("crédito de boleto ainda sem regra validada")
        # No legado cinco pagamentos têm tipo genérico Transação. Para débito,
        # ambos passam pela mesma classificação de contraparte no fato_financeiro.
        return "Pagamento"
    if op == "OUTROS":
        return "Pagamento devolvido" if credito and descricao.startswith("ESTORNO") else "Transação"
    raise ErroOperacional("tipo de operação Pluggy ainda sem regra validada")


def nome_descricao(item: dict) -> str | None:
    # A descrição bancária conserva o nome completo; paymentData pode trazer
    # só o nome comercial/abreviado. Remove apenas prefixos bancários validados.
    texto = normalizar(item.get("description"))
    padrao = {"PIX": r"^TRANSFERENCIA[\s:|\-]+PIX[\s:|\-]+(.+)$",
              "TED": r"^TRANSFERENCIA[\s:|\-]+TED[\s:|\-]+(.+)$",
              "BOLETO": r"^PAGAMENTO[\s:|\-]+(.+)$"}.get(item.get("operationType"))
    match = re.match(padrao, texto) if padrao else None
    return match.group(1).strip() if match else None


def converter(item: dict, conta: dict) -> dict:
    if item.get("accountId") != conta.get("id") or item.get("currencyCode") != "BRL":
        raise ErroOperacional("transação não pertence à conta BRL configurada")
    if item.get("status") != "POSTED":
        raise ErroOperacional("existem movimentos ainda não consolidados; aguarde a próxima sincronização")
    valor = moeda(item.get("amount"))
    if item.get("type") not in ("CREDIT", "DEBIT") or not valor or (valor > 0) != (item["type"] == "CREDIT"):
        raise ErroOperacional("direção ou sinal da transação Pluggy não confere")
    identificador = validar_id(item.get("id"))
    instante = data_local(item.get("date"))
    linha = {c: None for c in COLUNAS}
    linha.update(movimentacao="Crédito" if valor > 0 else "Débito", tipo=tipo_legado(item), valor=valor,
                 tarifa="0", data_hora=instante, data_hora_raw=instante.strftime("%d/%m/%Y %H:%M:%S"),
                 horario=instante.strftime("%H:%M:%S"), situacao="POSTED", descricao=item.get("description"),
                 origem_carga="pluggy", dedup_hash=hashlib.md5(f"pluggy|{conta['id']}|{identificador}".encode()).hexdigest())
    pd = item.get("paymentData") or {}
    for lado, chave in (("origem", "payer"), ("destino", "receiver")):
        parte = pd.get(chave) or {}
        linha[lado] = parte.get("name")
        linha[lado + "_documento"] = documento(parte.get("documentNumber"))
        linha[lado + "_instituicao"] = parte.get("routingNumberISPB") or parte.get("routingNumber")
        linha[lado + "_agencia"] = parte.get("branchNumber")
        linha[lado + "_conta"] = parte.get("accountNumber")
    nome = nome_descricao(item)
    if nome:
        linha["origem" if valor > 0 else "destino"] = nome
    if valor > 0 and item.get("operationType") == "PIX" and linha["tipo"] == "Transação" and not linha["origem"]:
        linha["origem"] = item.get("description")
    return linha


def assinatura(linha: dict):
    return linha["data_hora"].date(), moeda(linha["valor"])


def selecionar_novos(api: list[dict], existentes: list[dict]) -> list[dict]:
    por_hash = {x["dedup_hash"]: x for x in existentes}
    if len({x["dedup_hash"] for x in api}) != len(api):
        raise ErroOperacional("Pluggy repetiu identificadores; nada foi importado")
    pendentes = []
    vistos = set()
    for linha in api:
        anterior = por_hash.get(linha["dedup_hash"])
        if anterior:
            # Inclui texto/tipo: uma retificação de soma zero também deve parar.
            for campo in ("data_hora", "valor", "tipo", "movimentacao", "descricao", "origem_documento", "destino_documento"):
                if linha[campo] != anterior[campo]:
                    raise ErroOperacional("movimento Pluggy já importado foi alterado; revisão necessária")
            vistos.add(linha["dedup_hash"])
        else:
            pendentes.append(linha)
    legado = defaultdict(list)
    for linha in existentes:
        if linha["dedup_hash"] in vistos:
            continue
        if linha.get("origem_carga") == "pluggy":
            raise ErroOperacional("movimento Pluggy anterior não apareceu nesta consulta; confira consentimento e histórico")
        legado[assinatura(linha)].append(linha)
    grupos = defaultdict(list)
    for linha in pendentes:
        grupos[assinatura(linha)].append(linha)
    novos = []
    for chave in grupos.keys() | legado.keys():
        grupo, antes = grupos[chave], legado[chave]
        if not antes:
            novos.extend(grupo)
        elif len(grupo) != len(antes):
            raise ErroOperacional("correspondência parcial com o CSV; revisão necessária antes de importar")
    return sorted(novos, key=lambda x: (x["data_hora"], x["dedup_hash"]))


def preencher_saldos(novos: list[dict], ancora: dict, saldo_atual) -> None:
    saldo = moeda(ancora["saldo_depois"])
    if novos and novos[0]["data_hora"] <= ancora["data_hora"]:
        raise ErroOperacional("há movimento novo anterior à última linha do painel; revisão necessária")
    if novos and sum(x["data_hora"] == novos[-1]["data_hora"] for x in novos) != 1:
        raise ErroOperacional("último instante tem mais de um movimento; ordem do saldo precisa ser conferida")
    for linha in novos:
        linha["saldo_antes"] = saldo
        saldo += linha["valor"]
        linha["saldo_depois"] = saldo
    if saldo != moeda(saldo_atual):
        raise ErroOperacional("saldo do painel + novos movimentos não fecha com a Pluggy; nada foi importado")


def executar(*, dry_run: bool, inicio: date | None = None) -> int:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_values

    item_id = validar_id(valor_env("PLUGGY_STONE_ITEM_ID"))
    conta_id = validar_id(valor_env("PLUGGY_STONE_ACCOUNT_ID"))
    esperada = valor_env("PLUGGY_STONE_CONTA_ID")
    if not esperada:
        raise ErroOperacional("configure PLUGGY_STONE_CONTA_ID com o vínculo validado no Gestão")
    try:
        desde = date.fromisoformat(valor_env("PLUGGY_STONE_DESDE"))
    except ValueError as exc:
        raise ErroOperacional("configure PLUGGY_STONE_DESDE com a data de virada validada") from exc
    hoje = datetime.now(FUSO).date()
    inicio = inicio or desde
    if inicio < desde or inicio > hoje:
        raise ErroOperacional("período fora da data de virada configurada")
    cliente = Cliente()
    conferir_item(cliente.item(item_id))
    contas = [x for x in cliente.contas(item_id) if x.get("id") == conta_id]
    if len(contas) != 1 or contas[0].get("currencyCode") != "BRL":
        raise ErroOperacional("conta Stone configurada não está disponível em BRL")
    conta = contas[0]
    dados = cliente.transacoes(conta_id, inicio, hoje)
    linhas = [converter(x, conta) for x in dados]
    if not linhas:
        raise ErroOperacional("consulta Pluggy vazia; não confirma ausência de movimentos")
    conta_final = [x for x in cliente.contas(item_id) if x.get("id") == conta_id]
    if len(conta_final) != 1 or any(conta_final[0].get(k) != conta.get(k) for k in ("balance", "updatedAt")):
        raise ErroOperacional("Pluggy atualizou a conta durante a consulta; tente novamente")
    url = _database_url()
    if _referencia_projeto(url) != "lucpxoynpvogkvzepagi":
        raise ErroOperacional("destino recusado: integração configurada somente para o Supabase portal")
    with closing(psycopg2.connect(url, application_name="sirfisher_pluggy_stone")) as conn, conn:
        if dry_run:
            conn.set_session(readonly=True)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("set local statement_timeout = '60s'")
            if not dry_run:
                cur.execute("lock table public.raw_stone_extrato in share row exclusive mode")
            cur.execute("select f.conta_id from fonte_financeira f join conta c on c.id=f.conta_id where f.chave='stone_extrato' and f.ativa and c.ativa")
            fonte = cur.fetchone()
            if not fonte or str(fonte["conta_id"]) != esperada:
                raise ErroOperacional("vínculo da fonte Stone mudou; revisão necessária antes de importar")
            cur.execute("select * from raw_stone_extrato where conta_id=%s and data_hora >= %s order by data_hora,id", (esperada, inicio))
            existentes = [dict(x) for x in cur.fetchall()]
            if not existentes:
                raise ErroOperacional("é necessária uma base CSV reconciliada no período antes da virada Pluggy")
            novos = selecionar_novos(linhas, existentes)
            ancora = max(existentes, key=lambda x: x["data_hora"])
            if sum(x["data_hora"] == ancora["data_hora"] for x in existentes) != 1:
                raise ErroOperacional("saldo de abertura tem ordem ambígua; revisão necessária")
            preencher_saldos(novos, ancora, conta["balance"])
            print(f"Conferência Pluggy Stone: {len(linhas)} movimentos; {len(novos)} novos; saldo confere.")
            if dry_run:
                print("DRY-RUN: nenhuma gravação no banco.")
                return len(novos)
            if novos:
                valores = [[esperada if c == "conta_id" else x[c] for c in COLUNAS] for x in novos]
                inseridos = execute_values(cur, "insert into raw_stone_extrato (" + ",".join(COLUNAS) + ") values %s on conflict (dedup_hash) do nothing returning id", valores, fetch=True)
                if len(inseridos) != len(novos):
                    raise ErroOperacional("concorrência alterou a carga; transação cancelada")
                cur.execute("select * from recalcular_saldo_fechamento(%s,%s,0)", (novos[0]["data_hora"].date(), novos[-1]["data_hora"].date()))
                cur.fetchall()
            cur.execute("insert into log_carga(fontes) values ('Extrato Stone')")
    atualizar_painel()  # Falha posterior ao commit é recuperada mesmo sem novos na próxima rodada.
    return len(novos)


def fluxo():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--de", type=date.fromisoformat)
    op = parser.parse_args()
    carregar_env()
    try:
        quantidade = executar(dry_run=op.dry_run, inicio=op.de)
    except ErroOperacional as exc:
        if not op.dry_run:
            registrar([Execucao("Extrato Stone (Pluggy)", datetime.now(FUSO).date(), None, "erro", mensagem=str(exc))])
        raise
    except Exception as exc:
        if not op.dry_run:
            registrar([Execucao("Extrato Stone (Pluggy)", datetime.now(FUSO).date(), None, "erro", mensagem="falha operacional; confira a configuração da integração")])
        raise ErroOperacional(f"falha operacional Pluggy ({exc.__class__.__name__}); consulte a integração") from exc
    if not op.dry_run:
        registrar([Execucao("Extrato Stone (Pluggy)", datetime.now(FUSO).date(), None,
                           "ok" if quantidade else "sem_movimento", quantidade,
                           "saldo conferido; extrato atualizado" if quantidade else "saldo conferido; nenhum movimento novo")])


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
