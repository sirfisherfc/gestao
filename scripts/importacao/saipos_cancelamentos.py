"""Cancelamentos da Saipos com sinais de risco, para a rotina Cancelamentos.

Recebe as vendas (``search_sales``), os itens (``sales_items``) e o histórico
de status (``sales_status_histories``) de um ou mais dias e devolve:

* uma linha por **item cancelado** (apagado sem ir para outra mesa) e uma por
  **mesa inteira cancelada**, com os sinais, a pontuação e se o gerente
  precisa justificar;
* o valor lançado por dia, turno, hora e funcionário, base dos índices de
  cancelamento fora da curva;
* os nomes dos usuários Saipos que aparecem no histórico.

Regras (análise de 01/09 a 20/10/2026, ver ``docs/INTEGRACAO_API_BANCOS.md``):

* troca de mesa (``id_sale_to``) não é cancelamento;
* item relançado na mesma mesa logo depois é correção de lançamento;
* a Saipos não informa quando o item ficou pronto (``done_at`` é o fechamento
  da mesa), então "provavelmente servido" usa o tempo entre lançar e cancelar:
  10 min para bebida, 40 min para comida;
* pagamento e fechamento de mesa trocada ficam na venda de destino.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta

BEBIDA = (
    "spaten", "heineken", "brahma", "skol", "stella", "corona", "budweiser", "original", "amstel", "chopp",
    "chope", "choppe", "caipi", "drink", "refri", "lata", "água", "agua", "suco", "coca", "guaran", "dose",
    "vinho", "gin", "whisk", "vodka", "long neck", "longneck", "600ml", "350ml", "energ", "red bull", "coco",
    "cerveja", "tonica", "tônica", "soda", "h2oh", "limonada", "batida", "espumante", "campari", "aperol",
    "cachaça", "cachaca", "eisenbahn", "devassa", "ultra", "newcastle", "melancita",
)
MINUTOS_SERVIDO_BEBIDA = 10
MINUTOS_SERVIDO_COMIDA = 40
MINUTOS_RELANCE = 15
PONTOS = {
    "provavelmente servido": 2,
    "depois de começar a pagar": 2,
    "até 15 min antes de pagar": 1,
    "60+ min após lançar": 1,
    "mesa pagou em dinheiro": 1,
    "sem motivo": 1,
}
PONTOS_JUSTIFICAR = 3
VALOR_JUSTIFICAR = 100.0
MESA_MINUTOS_JUSTIFICAR = 30


def _dt(valor) -> datetime | None:
    return datetime.fromisoformat(str(valor)[:19]) if valor else None


def _bebida(produto: str) -> bool:
    texto = produto.lower()
    return any(chave in texto for chave in BEBIDA)


def valor_item(item: dict) -> float:
    base = float(item.get("unit_price") or 0)
    for escolha in item.get("choices") or []:
        preco = escolha.get("aditional_price") or escolha.get("additional_price") or escolha.get("price") or 0
        base += float(preco) * float(escolha.get("quantity") or 1)
    return round(base * float(item.get("quantity") or 0), 2)


def nomes_usuarios(status: dict[int, list]) -> dict[int, str]:
    nomes = {}
    for historico in status.values():
        for passo in historico:
            for chave in ("user", "authorized_by"):
                usuario = passo.get(chave) or {}
                if usuario.get("id_user"):
                    nomes[int(usuario["id_user"])] = (usuario.get("full_name") or "").strip() or f"usuário {usuario['id_user']}"
    return nomes


def montar(vendas: dict[int, dict], itens: dict[int, list], status: dict[int, list], nomes: dict[int, str]):
    """Devolve (cancelamentos, lancado_por_dimensao)."""

    def nome(uid) -> str | None:
        return nomes.get(int(uid), f"usuário {uid}") if uid else None

    destino = {}
    for id_sale, lista in itens.items():
        alvos = Counter(i["id_sale_to"] for i in lista if i.get("id_sale_to"))
        if alvos and not (vendas.get(id_sale) or {}).get("payments"):
            destino[id_sale] = alvos.most_common(1)[0][0]

    def final(id_sale):
        vistos = set()
        while id_sale in destino and id_sale not in vistos:
            vistos.add(id_sale)
            id_sale = destino[id_sale]
        return id_sale

    def pagamento(id_sale):
        venda = vendas.get(final(id_sale)) or {}
        pags = venda.get("payments") or []
        primeiro = min((_dt(p.get("created_at")) for p in pags if p.get("created_at")), default=None)
        if primeiro is None:
            fechou = [_dt(p["created_at"]) for p in status.get(venda.get("id_sale"), [])
                      if (p.get("desc_store_sale_status") or "").lower().startswith("entreg")]
            primeiro = max(fechou) if fechou else None
        dinheiro = any("dinheiro" in (p.get("desc_store_payment_type") or "").lower() for p in pags)
        return primeiro, dinheiro

    cancelamentos, lancado = [], defaultdict(lambda: [0, 0.0])
    for id_sale, lista in itens.items():
        venda = vendas.get(id_sale)
        if not venda:
            continue
        turno = (venda.get("store_shift") or {}).get("desc_store_shift")
        dia = str(venda["shift_date"])[:10]
        mesa = venda.get("desc_sale")
        validos = [i for i in lista if not i.get("id_sale_to")]
        for item in validos:
            criado = _dt(item.get("created_at"))
            chave = (dia, turno, criado.hour if criado else None, nome(item.get("created_by")))
            lancado[chave][0] += 1
            lancado[chave][1] += valor_item(item)

        if venda.get("canceled") == "Y":
            if not validos:
                continue  # mesa aberta por engano, sem itens
            passo = next((p for p in status.get(id_sale, []) if "cancel" in (p.get("desc_store_sale_status") or "").lower()), {})
            cancelada = _dt(passo.get("created_at")) or max(_dt(i.get("deleted_at") or i.get("updated_at")) for i in validos)
            aberta = min(_dt(i["created_at"]) for i in validos)
            minutos = round((cancelada - aberta).total_seconds() / 60)
            valor = round(sum(valor_item(i) for i in validos), 2)
            servidos = [i for i in validos if minutos >= (MINUTOS_SERVIDO_BEBIDA if _bebida(i.get("desc_sale_item") or "") else MINUTOS_SERVIDO_COMIDA)]
            sinais, pontos = [], 0
            if minutos >= MESA_MINUTOS_JUSTIFICAR:
                sinais.append(f"cancelada {minutos} min após abrir"); pontos += 2
            if minutos >= 120:
                pontos += 1
            if servidos:
                sinais.append("itens provavelmente servidos"); pontos += 1
            if valor >= VALOR_JUSTIFICAR:
                sinais.append("valor alto"); pontos += 1
            lancou = Counter(nome(i.get("created_by")) for i in validos).most_common(1)[0][0]
            cancelamentos.append({
                "id": f"mesa:{id_sale}", "tipo": "mesa", "id_sale": id_sale, "id_sale_item": None,
                "data_turno": dia, "turno": turno, "mesa": mesa,
                "produto": ", ".join(sorted({(i.get("desc_sale_item") or "?").strip() for i in validos})),
                "quantidade": len(validos), "valor": valor, "lancado_em": aberta, "cancelado_em": cancelada,
                "minutos": minutos, "min_ate_pagamento": None, "bebida": all(_bebida(i.get("desc_sale_item") or "") for i in validos),
                "lancou": lancou, "garcom_id": validos[0].get("id_store_waiter"),
                "cancelou": nome((passo.get("user") or {}).get("id_user")),
                "autorizou": nome((passo.get("authorized_by") or {}).get("id_user")),
                "motivo": passo.get("desc_cancellation_reason"), "sinais": sinais, "pontos": pontos,
                "exige_justificativa": minutos >= MESA_MINUTOS_JUSTIFICAR or valor >= VALOR_JUSTIFICAR,
            })
            continue

        ativos = defaultdict(list)
        for item in validos:
            if item.get("deleted") != "Y":
                ativos[(item.get("desc_sale_item") or "").strip()].append(_dt(item.get("created_at")))
        primeiro_pag, dinheiro = pagamento(id_sale)
        for item in validos:
            if item.get("deleted") != "Y":
                continue
            produto = (item.get("desc_sale_item") or "?").strip()
            criado, apagado = _dt(item.get("created_at")), _dt(item.get("deleted_at") or item.get("updated_at"))
            minutos = round((apagado - criado).total_seconds() / 60) if criado and apagado else None
            relancado = any(
                t and criado and apagado and timedelta(0) <= t - criado <= (apagado - criado) + timedelta(minutes=MINUTOS_RELANCE)
                for t in ativos.get(produto, [])
            )
            bebida = _bebida(produto)
            ate_pag = round((primeiro_pag - apagado).total_seconds() / 60, 1) if primeiro_pag and apagado else None
            sinais = []
            if minutos is not None and minutos >= (MINUTOS_SERVIDO_BEBIDA if bebida else MINUTOS_SERVIDO_COMIDA):
                sinais.append("provavelmente servido")
            if ate_pag is not None and ate_pag < 0:
                sinais.append("depois de começar a pagar")
            elif ate_pag is not None and ate_pag <= 15:
                sinais.append("até 15 min antes de pagar")
            if minutos is not None and minutos >= 60:
                sinais.append("60+ min após lançar")
            if dinheiro:
                sinais.append("mesa pagou em dinheiro")
            if not item.get("id_store_cancellation_reason"):
                sinais.append("sem motivo")
            if relancado:
                sinais = ["corrigido: relançado na mesma mesa"]
            pontos = 0 if relancado else sum(PONTOS.get(s, 0) for s in sinais)
            valor = valor_item(item)
            cancelamentos.append({
                "id": f"item:{item['id_sale_item']}", "tipo": "item", "id_sale": id_sale, "id_sale_item": item["id_sale_item"],
                "data_turno": dia, "turno": turno, "mesa": mesa, "produto": produto,
                "quantidade": item.get("quantity"), "valor": valor, "lancado_em": criado, "cancelado_em": apagado,
                "minutos": minutos, "min_ate_pagamento": ate_pag, "bebida": bebida,
                "lancou": nome(item.get("created_by")), "garcom_id": item.get("id_store_waiter"),
                "cancelou": nome(item.get("deleted_by")), "autorizou": nome(item.get("delete_authorized_by")),
                "motivo": str(item["id_store_cancellation_reason"]) if item.get("id_store_cancellation_reason") else None,
                "sinais": sinais, "pontos": pontos,
                "exige_justificativa": not relancado and (pontos >= PONTOS_JUSTIFICAR or valor >= VALOR_JUSTIFICAR),
            })
    linhas = [
        {"data_turno": dia, "turno": turno, "hora": hora, "lancou": lancou, "itens": itens_qtd, "valor": round(valor, 2)}
        for (dia, turno, hora, lancou), (itens_qtd, valor) in lancado.items()
    ]
    return cancelamentos, linhas
