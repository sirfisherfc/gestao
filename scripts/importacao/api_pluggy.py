#!/usr/bin/env python3
"""Consulta contas próprias compartilhadas pelo Meu Pluggy, sem gravar no banco.

Credenciais ficam no ambiente/.env. Arquivos financeiros ficam em api-pluggy/
(ignorado pelo Git). Não confundir uma consulta vazia com consentimento válido.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

from api_cliente import ErroHttp, carregar_env, requisitar, salvar_atomico
from importacao_core import ErroOperacional, ValidacaoErro, executar_com_saida

API = "https://api.pluggy.ai"
PASTA_PADRAO = Path(__file__).resolve().parent / "api-pluggy"
MAX_PAGINAS = 1000
FUSO = timezone(timedelta(hours=-3))  # Fortaleza não usa horário de verão.
ERROS = {
    400: "parâmetros recusados pela Pluggy",
    401: "credencial ou autorização recusada; confira a aplicação e o consentimento",
    403: "operação indisponível para esta aplicação ou conexão",
    404: "conexão ou conta não encontrada nesta aplicação",
    429: "limite de consultas atingido; tente mais tarde",
    500: "Pluggy temporariamente indisponível",
    503: "Pluggy temporariamente indisponível",
}


def valor_env(nome: str, alias: str | None = None) -> str:
    return (os.environ.get(nome) or (os.environ.get(alias) if alias else "") or "").strip()


def ids_configurados() -> list[str]:
    raw = valor_env("PLUGGY_ITEM_IDS") or valor_env("PLUGGY_ITEM_ID")
    return list(dict.fromkeys(x.strip() for x in raw.split(",") if x.strip()))


def validar_id(valor: str) -> str:
    # IDs são opacos; evita travessia de caminho e injeção em query/URL.
    if not isinstance(valor, str) or not valor or len(valor) > 128 or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in valor):
        raise ValidacaoErro("identificador Pluggy inválido")
    return valor


def _objeto(corpo: bytes) -> dict:
    try:
        dado = json.loads(corpo)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ErroOperacional("Pluggy retornou JSON inválido") from exc
    if not isinstance(dado, dict):
        raise ErroOperacional("Pluggy retornou uma resposta inesperada")
    return dado


class Cliente:
    def __init__(self):
        self.api_key: str | None = None

    def autenticar(self) -> None:
        cid = valor_env("PLUGGY_CLIENT_ID", "PLUGGY_Client_ID")
        secret = valor_env("PLUGGY_CLIENT_SECRET", "PLUGGY_Client_Secret")
        if not cid or not secret:
            raise ErroOperacional("configure PLUGGY_CLIENT_ID e PLUGGY_CLIENT_SECRET no .env local")
        resposta = requisitar(
            API + "/auth", metodo="POST",
            cabecalhos={"Content-Type": "application/json"},
            corpo=json.dumps({"clientId": cid, "clientSecret": secret}).encode(),
            mensagens=ERROS,
        )
        self.api_key = _objeto(resposta.corpo).get("apiKey")
        if not isinstance(self.api_key, str) or not self.api_key:
            raise ErroOperacional("Pluggy não retornou a chave temporária da aplicação")

    def consultar(self, rota: str, *, metodo: str = "GET", dados: dict | None = None) -> dict:
        if not rota.startswith("/") or rota.startswith("//") or "#" in rota:
            raise ValidacaoErro("rota Pluggy inválida")
        if not self.api_key:
            self.autenticar()
        for tentativa in range(2):
            try:
                return _objeto(requisitar(
                    API + rota, metodo=metodo,
                    cabecalhos={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                    corpo=json.dumps(dados).encode() if dados is not None else None,
                    mensagens=ERROS,
                ).corpo)
            except ErroHttp as exc:
                if exc.status != 401 or tentativa:
                    raise
                self.autenticar()  # Chave temporária vence; uma única renovação.
        raise ErroOperacional("não foi possível renovar a autenticação Pluggy")

    def token_conexao(self) -> str:
        resposta = self.consultar("/connect_token", metodo="POST", dados={
            "options": {"clientUserId": "sirfisher-gestao", "avoidDuplicates": True},
        })
        token = resposta.get("accessToken")
        if not isinstance(token, str) or not token:
            raise ErroOperacional("Pluggy não retornou token para abrir a conexão")
        return token

    def conector_meu_pluggy(self) -> int:
        resposta = self.consultar("/connectors?name=MeuPluggy")
        encontrados = [x for x in resposta.get("results", []) if
                       str(x.get("name", "")).replace(" ", "").lower() == "meupluggy"
                       and not x.get("isSandbox")]
        if len(encontrados) != 1 or not isinstance(encontrados[0].get("id"), int):
            raise ErroOperacional("não foi possível identificar o conector de produção MeuPluggy")
        return encontrados[0]["id"]

    def item(self, identificador: str) -> dict:
        return self.consultar("/items/" + validar_id(identificador))

    def contas(self, identificador: str) -> list[dict]:
        return self.paginas("/accounts", {"itemId": validar_id(identificador), "type": "BANK"})

    def paginas(self, rota: str, parametros: dict, *, cursor: bool = False) -> list[dict]:
        primeira = rota + "?" + urllib.parse.urlencode(parametros)
        atual = primeira
        vistos: set[str] = set()
        linhas: list[dict] = []
        for pagina in range(1, MAX_PAGINAS + 1):
            if atual in vistos:
                raise ErroOperacional("Pluggy repetiu uma página; consulta interrompida sem salvar")
            vistos.add(atual)
            resposta = self.consultar(atual)
            lote = resposta.get("results")
            if not isinstance(lote, list) or any(not isinstance(x, dict) for x in lote):
                raise ErroOperacional("Pluggy retornou uma página sem registros válidos")
            linhas.extend(lote)
            if cursor:
                if "next" not in resposta:
                    raise ErroOperacional("Pluggy não confirmou o fim da paginação; consulta interrompida sem salvar")
                proxima = resposta["next"]
                if proxima is None:
                    return linhas
                if not isinstance(proxima, str) or not proxima:
                    raise ErroOperacional("Pluggy retornou cursor inválido")
                atual = proxima_rota(rota, proxima)
            else:
                total = resposta.get("totalPages", 1)
                if not isinstance(total, int) or total < 0:
                    raise ErroOperacional("Pluggy retornou paginação inválida")
                if pagina >= total:
                    return linhas
                atual = rota + "?" + urllib.parse.urlencode({**parametros, "page": pagina + 1})
        raise ErroOperacional("paginação Pluggy excedeu o limite; consulta interrompida sem salvar")

    def transacoes(self, conta: str, inicio: date, fim: date) -> list[dict]:
        # A API filtra em UTC: o fim do dia em Fortaleza cai no dia UTC seguinte.
        linhas = self.paginas("/v2/transactions", {
            "accountId": validar_id(conta), "dateFrom": inicio.isoformat(),
            "dateTo": (fim + timedelta(days=1)).isoformat(),
        }, cursor=True)
        return [x for x in linhas if inicio <= data_local(x.get("date")).date() <= fim]


def data_local(valor: str) -> datetime:
    try:
        instante = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if instante.tzinfo is None:
            raise ValueError
        return instante.astimezone(FUSO).replace(tzinfo=None)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ErroOperacional("data Pluggy sem fuso ou inválida; consulta interrompida") from exc


def proxima_rota(rota: str, proxima: str) -> str:
    if not isinstance(proxima, str):
        raise ErroOperacional("Pluggy retornou cursor inválido")
    url = urllib.parse.urljoin(API + rota, proxima)
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "api.pluggy.ai" or parsed.path != rota or parsed.fragment:
        raise ErroOperacional("Pluggy retornou paginação fora do endpoint esperado")
    return parsed.path + ("?" + parsed.query if parsed.query else "")


def conferir_item(item: dict) -> None:
    if (item.get("connector") or {}).get("isSandbox"):
        raise ErroOperacional("conexão de teste recusada; use o MeuPluggy de produção")
    status = item.get("status")
    if status != "UPDATED":
        raise ErroOperacional("conexão Pluggy ainda não está pronta; conclua o login ou aguarde a sincronização")
    expira = item.get("consentExpiresAt")
    if expira:
        try:
            instante = datetime.fromisoformat(str(expira).replace("Z", "+00:00"))
            if instante.tzinfo is None:
                instante = instante.replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise ErroOperacional("data de consentimento Pluggy inválida") from exc
        if instante <= datetime.now(timezone.utc):
            raise ErroOperacional("consentimento MeuPluggy expirou; reconecte antes de consultar")


def fluxo():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verificar", action="store_true", help="confere acesso, conexão e quantidade de contas")
    parser.add_argument("--catalogar", action="store_true", help="salva os IDs e dados das contas em arquivo local privado")
    parser.add_argument("--item", action="append", help="ID de conexão; padrão: PLUGGY_ITEM_IDS")
    parser.add_argument("--conta", help="ID explícito da conta a baixar")
    parser.add_argument("--de", type=date.fromisoformat)
    parser.add_argument("--ate", type=date.fromisoformat)
    parser.add_argument("--pasta", type=Path, default=PASTA_PADRAO)
    op = parser.parse_args()
    carregar_env()
    cliente = Cliente()
    cliente.autenticar()
    print("Autenticação Pluggy: OK (credencial temporária mantida em memória).")
    itens = op.item or ids_configurados()
    if not itens:
        raise ErroOperacional("sem conexão configurada; execute conectar_pluggy.py e conclua o login MeuPluggy")
    contas: list[dict] = []
    for item_id in itens:
        item = cliente.item(item_id)
        conferir_item(item)
        contas.extend(cliente.contas(item_id))
    print(f"Conexões prontas: {len(itens)}; contas bancárias disponíveis: {len(contas)}.")
    if not contas:
        raise ErroOperacional("nenhuma conta recebida; confira o compartilhamento e a validade do consentimento MeuPluggy")
    if op.catalogar:
        salvar_atomico(op.pasta / "contas.json", json.dumps(contas, ensure_ascii=False, indent=2).encode("utf-8"))
        print("Catálogo de contas salvo na pasta privada; confira titular, banco, número e moeda antes de escolher.")
    if op.verificar:
        return
    if not op.conta or not op.de or not op.ate:
        raise ValidacaoErro("para baixar, informe --conta, --de e --ate; use --verificar para conferir só o acesso")
    if op.ate < op.de or (op.ate - op.de).days > 366:
        raise ValidacaoErro("período inválido; máximo de 367 dias por execução")
    selecionadas = [x for x in contas if x.get("id") == op.conta]
    if len(selecionadas) != 1:
        raise ValidacaoErro("a conta indicada não pertence às conexões configuradas ou está duplicada")
    conta = selecionadas[0]
    linhas = cliente.transacoes(op.conta, op.de, op.ate)
    destino = op.pasta / f"{validar_id(op.conta)}_{op.de}_{op.ate}.json"
    envelope = {"baixado_em": datetime.now(timezone.utc).isoformat(),
                "inicio": str(op.de), "fim": str(op.ate), "conta": conta, "transacoes": linhas}
    salvar_atomico(destino, json.dumps(envelope, ensure_ascii=False, indent=2).encode("utf-8"))
    print("Consulta concluída; arquivo financeiro salvo na pasta privada de importação.")
    print("Nenhuma gravação no banco. Compare cobertura e lançamentos com o CSV antes de ativar a carga.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
