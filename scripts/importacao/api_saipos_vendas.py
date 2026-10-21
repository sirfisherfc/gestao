#!/usr/bin/env python3
"""Vendas da Saipos pela API de Dados e conciliação com as vendas Stone.

Baixa ``search_sales`` dia a dia pela data do turno, grava em
``saipos_venda``/``saipos_pagamento`` e casa cada pagamento com
``raw_stone_vendas``:

1. cartão na maquininha integrada: ``authorization_code`` = ``stone_id``;
2. Pix na maquininha e pagamentos lançados no caixa: mesmo valor, mesma
   categoria e horário próximo. Lançamento manual aceita outra categoria
   quando não há par na mesma, porque o caixa às vezes marca a forma errada;
3. lançamento no caixa ainda sem par: a única venda Stone de mesmo valor e
   categoria nas 3 h anteriores (conta fechada depois da cobrança) ou a soma
   de 2 a 4 vendas Stone próximas (vale dividido em vários cartões).

Na conta dividida o caixa e a maquininha podem diferir em centavos, então
lançamentos no caixa casam com tolerância de R$ 0,05. Dinheiro, Fiado,
pagamentos zerados e vendas canceladas não entram na conciliação. O resultado
aparece em Conciliação no painel (``app_conciliacao_saipos_dia``).

Prova de 12–18/10/2026: 518 de 529 vendas Stone casadas (ver
``docs/INTEGRACAO_API_BANCOS.md``).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import unicodedata
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from itertools import combinations

import integracao_log
from api_cliente import ErroHttp, carregar_env, requisitar, variavel
from importacao_core import ErroOperacional, ValidacaoErro, executar_com_saida


FONTE = "saipos_vendas"
URL_VENDAS = "https://data.saipos.io/v1/search_sales"
LIMITE_PAGINA = 1000
DIAS_PADRAO = 7
MENSAGENS = {
    400: "consulta recusada pela Saipos (período acima de 15 dias ou data inválida)",
    401: "token recusado; confira SAIPOS_API_TOKEN no .env",
    403: "token sem acesso a esta loja",
    429: "limite da Saipos: 500 consultas a cada 5 minutos; tente depois",
    504: "a Saipos demorou a responder",
}
# O 504 vem do pool de conexões da Saipos; uma nova tentativa costuma passar.
STATUS_REPETIR = {502, 503, 504}
ESPERAS = (5, 20, 60)
FORA_DA_CONCILIACAO = {"dinheiro", "fiado"}
# O primeiro turno começa às 08:00: venda Stone da madrugada é do dia anterior.
INICIO_TURNO = timedelta(hours=8)
JANELA_POS = timedelta(minutes=5)
JANELA_MANUAL = timedelta(minutes=30)
JANELA_AMPLA = timedelta(hours=3)
JANELA_SOMA = timedelta(minutes=10)
TOLERANCIA = Decimal("0.05")
MAXIMO_PARTES = 4


@dataclass
class Pagamento:
    id_sale: int
    origem: str
    ordem: int
    forma: str
    categoria: str
    valor: Decimal
    criado_em: datetime
    codigo_autorizacao: str | None
    id_transacao: str | None
    entra_conciliacao: bool
    stone_id: str | None = None
    casamento: str | None = None
    diferenca_min: int | None = None
    stone_ids_extra: list[str] | None = None


@dataclass(frozen=True)
class VendaStone:
    stone_id: str
    data_venda: datetime
    categoria: str
    valor: Decimal


def _sem_acento(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def categoria(forma: str | None) -> str:
    texto = _sem_acento(forma or "")
    if "pix" in texto:
        return "pix"
    if "debito" in texto:
        return "debito"
    if "credito" in texto:
        return "credito"
    if "dinheiro" in texto:
        return "dinheiro"
    if "fiado" in texto:
        return "fiado"
    return "outro"


def _data_hora(valor: str | None, contexto: str) -> datetime:
    try:
        return datetime.fromisoformat(str(valor)[:19])
    except ValueError as exc:
        raise ValidacaoErro(f"data/hora inválida em {contexto}: {valor!r}") from exc


def _valor(valor, contexto: str) -> Decimal:
    try:
        return Decimal(str(valor)).quantize(Decimal("0.01"))
    except Exception as exc:
        raise ValidacaoErro(f"valor inválido em {contexto}: {valor!r}") from exc


def baixar_dia(token: str, dia: date) -> list[dict]:
    vendas: list[dict] = []
    deslocamento = 0
    while True:
        consulta = urllib.parse.urlencode({
            "p_date_column_filter": "shift_date",
            "p_filter_date_start": f"{dia.isoformat()}T00:00:00",
            "p_filter_date_end": f"{dia.isoformat()}T23:59:59",
            "p_limit": LIMITE_PAGINA,
            "p_offset": deslocamento,
        })
        for tentativa, espera in enumerate((*ESPERAS, None)):
            try:
                resposta = requisitar(
                    f"{URL_VENDAS}?{consulta}",
                    cabecalhos={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                    mensagens=MENSAGENS,
                    timeout=180,
                )
                break
            except ErroHttp as exc:
                if exc.status not in STATUS_REPETIR or espera is None:
                    raise
            except ErroOperacional:
                if espera is None:
                    raise
            print(f"  {dia}: Saipos indisponível, nova tentativa em {espera} s")
            time.sleep(espera)
        try:
            lote = json.loads(resposta.corpo)
        except ValueError as exc:
            raise ErroOperacional("a Saipos devolveu uma resposta que não é JSON") from exc
        if not isinstance(lote, list):
            raise ErroOperacional("a Saipos devolveu um formato inesperado (esperava uma lista)")
        vendas.extend(lote)
        if len(lote) < LIMITE_PAGINA:
            return vendas
        deslocamento += LIMITE_PAGINA


def ler_venda(bruta: dict) -> tuple[dict, list[Pagamento]]:
    id_sale = int(bruta["id_sale"])
    contexto = f"venda {id_sale}"
    cancelada = str(bruta.get("canceled") or "N").upper() == "Y"
    venda = {
        "id_sale": id_sale,
        "id_store": int(bruta["id_store"]),
        "data_turno": date.fromisoformat(str(bruta["shift_date"])[:10]),
        "turno": (bruta.get("store_shift") or {}).get("desc_store_shift"),
        "criada_em": _data_hora(bruta.get("created_at"), contexto),
        "atualizada_em": _data_hora(bruta["updated_at"], contexto) if bruta.get("updated_at") else None,
        "cancelada": cancelada,
        "tipo_venda": bruta.get("id_sale_type"),
        "total": _valor(bruta["total_amount"], contexto) if bruta.get("total_amount") is not None else None,
    }
    pagamentos: list[Pagamento] = []
    # A transação da maquininha repete uma forma de pagamento da venda; só a
    # forma sem transação correspondente vira pagamento manual.
    cobertas: list[tuple[str, Decimal]] = []
    transacoes = list(bruta.get("payment_transaction_smartpos") or [])
    for ordem, transacao in enumerate(transacoes):
        cat = categoria(transacao.get("payment_method"))
        valor = _valor(transacao.get("payment_amount"), contexto)
        valida = bool(transacao.get("approved")) and not transacao.get("cancelled")
        if valida:
            cobertas.append((cat, valor))
        pagamentos.append(Pagamento(
            id_sale, "pos", ordem, str(transacao.get("payment_method") or "").strip() or "?", cat, valor,
            _data_hora(transacao.get("created_at"), contexto),
            (transacao.get("authorization_code") or "").strip() or None,
            str(transacao.get("id_transaction") or "").strip() or None,
            valida and valor > 0 and not cancelada,
        ))
    for ordem, forma in enumerate(bruta.get("payments") or []):
        nome = str(forma.get("desc_store_payment_type") or "").strip() or "?"
        cat = categoria(nome)
        valor = _valor(forma.get("payment_amount"), contexto)
        iguais = [item for item in cobertas if item[0] == cat and abs(item[1] - valor) <= TOLERANCIA]
        if iguais:
            cobertas.remove(min(iguais, key=lambda item: abs(item[1] - valor)))
            continue
        pagamentos.append(Pagamento(
            id_sale, "forma", ordem, nome, cat, valor,
            _data_hora(forma.get("created_at") or bruta.get("created_at"), contexto),
            None, None, cat not in FORA_DA_CONCILIACAO and valor > 0 and not cancelada,
        ))
    return venda, pagamentos


def categoria_stone(produto: str | None) -> str:
    return categoria(produto)


def _casar(pagamento: Pagamento, venda: VendaStone, casamento: str, livres: dict) -> None:
    livres.pop(venda.stone_id)
    pagamento.stone_id, pagamento.casamento = venda.stone_id, casamento
    pagamento.diferenca_min = round((venda.data_venda - pagamento.criado_em).total_seconds() / 60)


def _soma(alvo: Decimal, candidatas: list[VendaStone]) -> list[VendaStone] | None:
    """Menor grupo de 2 a ``MAXIMO_PARTES`` vendas cuja soma bate com o alvo."""
    for tamanho in range(2, min(MAXIMO_PARTES, len(candidatas)) + 1):
        for grupo in combinations(candidatas, tamanho):
            if abs(sum(venda.valor for venda in grupo) - alvo) <= TOLERANCIA:
                return list(grupo)
    return None


def conciliar(pagamentos: list[Pagamento], stone: list[VendaStone]) -> None:
    """Casa os pagamentos com as vendas Stone livres; altera ``pagamentos``."""
    livres = {venda.stone_id: venda for venda in stone}
    for pagamento in pagamentos:
        pagamento.stone_id = pagamento.casamento = pagamento.diferenca_min = pagamento.stone_ids_extra = None
    pendentes = [p for p in pagamentos if p.entra_conciliacao]
    for pagamento in pendentes:
        if pagamento.codigo_autorizacao and pagamento.codigo_autorizacao in livres:
            _casar(pagamento, livres[pagamento.codigo_autorizacao], "codigo", livres)

    def sem_par(origem: str) -> list[Pagamento]:
        return sorted((p for p in pendentes if p.origem == origem and not p.stone_id), key=lambda p: p.criado_em)

    for origem, janela, tolerancia in (("pos", JANELA_POS, Decimal("0")), ("forma", JANELA_MANUAL, TOLERANCIA)):
        for pagamento in sem_par(origem):
            candidatas = [
                venda for venda in livres.values()
                if abs(venda.valor - pagamento.valor) <= tolerancia
                and abs(venda.data_venda - pagamento.criado_em) <= janela
            ]
            mesma = [venda for venda in candidatas if venda.categoria == pagamento.categoria]
            escolhidas = mesma or (candidatas if origem == "forma" else [])
            if escolhidas:
                venda = min(escolhidas, key=lambda v: (abs(v.valor - pagamento.valor), abs(v.data_venda - pagamento.criado_em)))
                _casar(pagamento, venda, "valor_horario", livres)

    # Conta fechada no caixa depois da cobrança: só com par único, para não
    # trocar entre mesas vendas de valor comum (R$ 5, R$ 10).
    for pagamento in sem_par("forma"):
        candidatas = [
            venda for venda in livres.values()
            if venda.categoria == pagamento.categoria and abs(venda.valor - pagamento.valor) <= TOLERANCIA
            and timedelta(0) <= pagamento.criado_em - venda.data_venda <= JANELA_AMPLA
        ]
        if len(candidatas) == 1:
            _casar(pagamento, candidatas[0], "janela_ampla", livres)

    # Vale ou conta dividida em vários cartões: a soma bate com o lançamento.
    for pagamento in sem_par("forma"):
        proximas = sorted(
            (venda for venda in livres.values() if abs(venda.data_venda - pagamento.criado_em) <= JANELA_SOMA),
            key=lambda venda: abs(venda.data_venda - pagamento.criado_em),
        )[:8]
        grupo = _soma(pagamento.valor, proximas)
        if grupo:
            _casar(pagamento, grupo[0], "soma", livres)
            pagamento.stone_ids_extra = [venda.stone_id for venda in grupo[1:]]
            for venda in grupo[1:]:
                livres.pop(venda.stone_id)


def dias_do_periodo(inicio: date, fim: date, hoje: date) -> list[date]:
    if inicio > fim:
        raise ValidacaoErro("--de não pode ser posterior a --ate")
    if fim >= hoje:
        raise ValidacaoErro("o dia ainda não fechou; use --ate até ontem")
    return [inicio + timedelta(days=indice) for indice in range((fim - inicio).days + 1)]


def _conectar():
    try:
        import psycopg2
    except ImportError as exc:
        raise ErroOperacional("dependências ausentes; execute: python -m pip install -r requirements.txt") from exc
    from importacao_core import _database_url

    return psycopg2.connect(_database_url())


def gravar(cur, vendas: list[dict], pagamentos: list[Pagamento]) -> int:
    """Grava as vendas e substitui os pagamentos delas. Devolve vendas novas."""
    if not vendas:
        return 0
    ids = [venda["id_sale"] for venda in vendas]
    cur.execute("select id_sale from saipos_venda where id_sale = any(%s);", (ids,))
    existentes = {linha[0] for linha in cur.fetchall()}
    from psycopg2.extras import execute_values

    # Em lote: cada ida ao banco custa ~50 ms, e uma carga tem milhares de linhas.
    colunas = ("id_sale", "id_store", "data_turno", "turno", "criada_em", "atualizada_em", "cancelada", "tipo_venda", "total")
    execute_values(
        cur,
        f"insert into saipos_venda ({', '.join(colunas)}) values %s "
        "on conflict (id_sale) do update set "
        + ", ".join(f"{coluna} = excluded.{coluna}" for coluna in colunas[1:])
        + ", importado_em = now();",
        [tuple(venda[coluna] for coluna in colunas) for venda in vendas],
    )
    cur.execute("delete from saipos_pagamento where id_sale = any(%s);", (ids,))
    execute_values(
        cur,
        "insert into saipos_pagamento (id_sale, origem, ordem, forma, categoria, valor, criado_em, "
        "codigo_autorizacao, id_transacao, entra_conciliacao) values %s;",
        [
            (p.id_sale, p.origem, p.ordem, p.forma, p.categoria, p.valor, p.criado_em,
             p.codigo_autorizacao, p.id_transacao, p.entra_conciliacao)
            for p in pagamentos
        ],
    )
    return len(set(ids) - existentes)


def reconciliar_periodo(cur, inicio: date, fim: date) -> dict[str, int]:
    """Refaz o casamento dos dias do período com as vendas Stone já no banco."""
    cur.execute(
        "select p.id_sale, p.origem, p.ordem, p.forma, p.categoria, p.valor, p.criado_em, "
        "p.codigo_autorizacao, p.id_transacao, p.entra_conciliacao "
        "from saipos_pagamento p join saipos_venda s on s.id_sale = p.id_sale "
        "where s.data_turno between %s and %s;",
        (inicio, fim),
    )
    pagamentos = [Pagamento(*linha) for linha in cur.fetchall()]
    # Margem de um dia: um casamento por horário pode cruzar a virada do turno.
    cur.execute(
        "select v.stone_id, v.data_venda, v.produto, v.valor_bruto from raw_stone_vendas v "
        "where v.ultimo_status = 'Aprovada' and v.stone_id is not null "
        "and (v.stonecode is null or v.stonecode in "
        "(select c.stonecode from stone_conta c where c.ativa and c.entra_faturamento)) "
        "and v.data_venda >= %s and v.data_venda < %s "
        "and not exists (select 1 from saipos_pagamento p join saipos_venda s on s.id_sale = p.id_sale "
        "where (p.stone_id = v.stone_id or p.stone_ids_extra @> array[v.stone_id]) "
        "and s.data_turno not between %s and %s);",
        (
            datetime.combine(inicio, datetime.min.time()) + INICIO_TURNO - timedelta(days=1),
            datetime.combine(fim + timedelta(days=2), datetime.min.time()) + INICIO_TURNO,
            inicio, fim,
        ),
    )
    stone = [
        VendaStone(stone_id, data_venda, categoria_stone(produto), Decimal(valor).quantize(Decimal("0.01")))
        for stone_id, data_venda, produto, valor in cur.fetchall()
    ]
    conciliar(pagamentos, stone)
    cur.execute(
        "update saipos_pagamento p set stone_id = null, casamento = null, diferenca_min = null, stone_ids_extra = null "
        "from saipos_venda s where s.id_sale = p.id_sale and s.data_turno between %s and %s;",
        (inicio, fim),
    )
    casados = [p for p in pagamentos if p.stone_id]
    from psycopg2.extras import execute_values

    execute_values(
        cur,
        "update saipos_pagamento p set stone_id = v.stone_id, casamento = v.casamento, "
        "diferenca_min = v.diferenca_min, stone_ids_extra = v.extra "
        "from (values %s) as v (stone_id, casamento, diferenca_min, extra, id_sale, origem, ordem) "
        "where p.id_sale = v.id_sale and p.origem = v.origem and p.ordem = v.ordem;",
        [(p.stone_id, p.casamento, p.diferenca_min, p.stone_ids_extra, p.id_sale, p.origem, p.ordem) for p in casados],
        template="(%s, %s, %s::integer, %s::text[], %s::bigint, %s, %s::smallint)",
    )
    conciliaveis = [p for p in pagamentos if p.entra_conciliacao]
    return {
        "conciliaveis": len(conciliaveis),
        **{tipo: sum(1 for p in casados if p.casamento == tipo) for tipo in ("codigo", "valor_horario", "janela_ampla", "soma")},
        "saipos_sem_stone": sum(1 for p in conciliaveis if not p.stone_id),
        "stone_sem_saipos": len(stone) - len(casados) - sum(len(p.stone_ids_extra or []) for p in casados),
    }


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Importa as vendas da Saipos e concilia com a Stone")
    parser.add_argument("--de", type=date.fromisoformat, help=f"primeiro dia do turno (AAAA-MM-DD); padrão: {DIAS_PADRAO} dias atrás")
    parser.add_argument("--ate", type=date.fromisoformat, help="último dia do turno (AAAA-MM-DD); padrão: ontem")
    parser.add_argument("--verificar", action="store_true", help="testa o token com as vendas de ontem, sem gravar")
    parser.add_argument("--dry-run", action="store_true", help="baixa e resume, sem gravar nem registrar execução")
    parser.add_argument("--so-conciliar", action="store_true", help="refaz só o casamento com a Stone, sem consultar a Saipos")
    return parser


def resumir(dia: date, vendas: list[dict], pagamentos: list[Pagamento]) -> str:
    validas = [venda for venda in vendas if not venda["cancelada"]]
    pos = sum(1 for p in pagamentos if p.origem == "pos" and p.entra_conciliacao)
    manuais = sum(1 for p in pagamentos if p.origem == "forma" and p.entra_conciliacao)
    return (f"{dia}: {len(vendas)} venda(s), {len(vendas) - len(validas)} cancelada(s); "
            f"{pos} na maquininha, {manuais} lançada(s) no caixa")


def fluxo() -> None:
    opcoes = criar_parser().parse_args()
    carregar_env()
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    if opcoes.verificar:
        vendas = baixar_dia(variavel("SAIPOS_API_TOKEN"), ontem)
        lojas = sorted({str(venda.get("id_store")) for venda in vendas})
        print(f"Token aceito pela Saipos: {len(vendas)} venda(s) em {ontem}, loja(s) {', '.join(lojas) or '—'}.")
        return
    fim = opcoes.ate or ontem
    inicio = opcoes.de or fim - timedelta(days=DIAS_PADRAO - 1)
    dias = dias_do_periodo(inicio, fim, hoje)

    if opcoes.so_conciliar:
        conn = _conectar()
        try:
            with conn, conn.cursor() as cur:
                print(f"Conciliação {inicio} a {fim}: {reconciliar_periodo(cur, inicio, fim)}")
        finally:
            conn.close()
        return

    token = variavel("SAIPOS_API_TOKEN")
    lidos: dict[date, tuple[list[dict], list[Pagamento]]] = {}
    erros: dict[date, str] = {}
    for dia in dias:
        try:
            vendas, pagamentos = [], []
            for bruta in baixar_dia(token, dia):
                venda, itens = ler_venda(bruta)
                vendas.append(venda)
                pagamentos.extend(itens)
            lidos[dia] = (vendas, pagamentos)
            print(resumir(dia, vendas, pagamentos))
        except (ErroOperacional, ValidacaoErro) as exc:
            erros[dia] = str(exc)
            print(f"{dia}: ERRO {exc}", file=sys.stderr)
    if opcoes.dry_run:
        print("\n--dry-run: nada gravado.")
    else:
        novas: dict[date, int] = {}
        conn = _conectar()
        try:
            with conn, conn.cursor() as cur:
                for dia, (vendas, pagamentos) in lidos.items():
                    novas[dia] = gravar(cur, vendas, pagamentos)
                if lidos:
                    print(f"\nConciliação {inicio} a {fim}: {reconciliar_periodo(cur, inicio, fim)}")
        finally:
            conn.close()
        integracao_log.registrar(
            [integracao_log.Execucao(FONTE, dia, None, "erro", mensagem=mensagem) for dia, mensagem in erros.items()]
            + [
                integracao_log.Execucao(FONTE, dia, None, "ok" if vendas else "sem_movimento", linhas_novas=novas[dia])
                for dia, (vendas, _) in lidos.items()
            ]
        )
    if erros:
        raise ErroOperacional(f"{len(erros)} dia(s) sem vendas da Saipos; os demais foram gravados")
    print("\nOK.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
