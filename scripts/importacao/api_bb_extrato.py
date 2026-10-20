#!/usr/bin/env python3
"""Baixa o extrato da conta corrente do Banco do Brasil pela API Extratos.

Primeira etapa da integração por API: salva os lançamentos em JSON, um arquivo
por mês, em ``scripts/importacao/api-bb-extrato/`` (ignorado pelo Git), e
confere ``Saldo Anterior + movimentos = S A L D O`` quando o BB devolve essas
linhas. Ainda não grava no banco: o ``dedup_hash`` de ``raw_bb`` nasce dos
textos do CSV e só pode ser reproduzido depois de comparar um período real
baixado pela API com o mesmo período já importado (ver
``docs/INTEGRACAO_API_BANCOS.md``).

Autenticação: OAuth2 ``client_credentials`` com escopo ``extrato-info`` e a
``developer_application_key`` do aplicativo no Portal Developers BB. Em
produção o BB exige mTLS: certificado e-CNPJ A1 convertido para PEM.
Os endereços e o nome do parâmetro da chave podem ser trocados por variável de
ambiente, caso o portal mostre valores diferentes destes padrões.
"""

from __future__ import annotations

import argparse
import base64
import json
import ssl
import sys
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from api_cliente import caminho_privado, carregar_env, requisitar, salvar_atomico, variavel
from importacao_core import ErroOperacional, ValidacaoErro, executar_com_saida


@dataclass(frozen=True)
class Ambiente:
    url_token: str
    url_api: str
    exige_certificado: bool


AMBIENTES = {
    "homologacao": Ambiente(
        url_token="https://oauth.hm.bb.com.br/oauth/token",
        url_api="https://api.hm.bb.com.br/extratos/v1",
        exige_certificado=False,
    ),
    "producao": Ambiente(
        url_token="https://oauth.bb.com.br/oauth/token",
        url_api="https://api-extratos.bb.com.br/extratos/v1",
        exige_certificado=True,
    ),
}
ESCOPO = "extrato-info"
ROTA = "/conta-corrente/agencia/{agencia}/conta/{conta}"
PARAMETRO_CHAVE_PADRAO = "gw-dev-app-key"
REGISTROS_POR_PAGINA = 200
MAXIMO_PAGINAS = 500
MAXIMO_DIAS = 366
PASTA_PADRAO = Path(__file__).resolve().parent / "api-bb-extrato"
ROTULO_SALDO_ANTERIOR = "Saldo Anterior"
ROTULO_SALDO_FINAL = "S A L D O"
ROTULO_SALDO_DIA = "Saldo do dia"
SINAL_POR_INDICADOR = {"C": 1, "D": -1}
MENSAGENS_TOKEN = {
    400: "pedido de token recusado; o aplicativo precisa ter a API Extratos (escopo extrato-info)",
    401: "BB_CLIENT_ID ou BB_CLIENT_SECRET recusados",
}
MENSAGENS_EXTRATO = {
    400: "parâmetros recusados; agência e conta vão sem dígito e as datas em DDMMAAAA",
    401: "token ou developer_application_key recusados",
    403: "aplicativo sem permissão para esta conta; o usuário master precisa autorizar no internet banking PJ",
    404: "conta não encontrada ou período sem lançamentos",
    429: "limite de consultas do BB atingido; tente mais tarde",
    503: "API Extratos indisponível no momento",
}


@dataclass(frozen=True)
class Configuracao:
    ambiente: str
    url_token: str
    url_api: str
    client_id: str
    client_secret: str
    chave_aplicativo: str
    parametro_chave: str
    agencia: str
    conta: str
    contexto: ssl.SSLContext | None


@dataclass(frozen=True)
class Conferencia:
    aplicada: bool
    confere: bool
    lancamentos: int

    def texto(self) -> str:
        if not self.aplicada:
            return "o BB não trouxe Saldo Anterior e S A L D O; conferência não aplicada"
        return "saldo confere" if self.confere else "saldo NÃO confere com saldo anterior + movimentos"


def _so_digitos_obrigatorio(nome: str) -> str:
    valor = variavel(nome).replace("-", "").replace(".", "")
    if not valor.isdigit():
        raise ValidacaoErro(f"{nome} deve ter só dígitos, sem o dígito verificador")
    return valor


def _contexto_mtls(ambiente: Ambiente) -> ssl.SSLContext | None:
    if not variavel("BB_CERTIFICADO", obrigatoria=False):
        if ambiente.exige_certificado:
            raise ErroOperacional(
                "produção do BB exige mTLS; defina BB_CERTIFICADO e BB_CHAVE_PRIVADA (PEM do e-CNPJ A1)"
            )
        return None
    contexto = ssl.create_default_context()
    try:
        contexto.load_cert_chain(
            certfile=caminho_privado("BB_CERTIFICADO"),
            keyfile=caminho_privado("BB_CHAVE_PRIVADA"),
            password=variavel("BB_CHAVE_SENHA", obrigatoria=False),
        )
    except ssl.SSLError as exc:
        raise ErroOperacional(
            "não foi possível carregar o certificado; confira o PEM, a chave e BB_CHAVE_SENHA"
        ) from exc
    return contexto


def carregar_configuracao() -> Configuracao:
    nome = (variavel("BB_AMBIENTE", obrigatoria=False) or "homologacao").lower()
    if nome not in AMBIENTES:
        raise ValidacaoErro("BB_AMBIENTE deve ser homologacao ou producao")
    ambiente = AMBIENTES[nome]
    return Configuracao(
        ambiente=nome,
        url_token=variavel("BB_URL_TOKEN", obrigatoria=False) or ambiente.url_token,
        url_api=(variavel("BB_URL_API", obrigatoria=False) or ambiente.url_api).rstrip("/"),
        client_id=variavel("BB_CLIENT_ID"),
        client_secret=variavel("BB_CLIENT_SECRET"),
        chave_aplicativo=variavel("BB_DEVELOPER_APP_KEY"),
        parametro_chave=variavel("BB_PARAMETRO_APP_KEY", obrigatoria=False) or PARAMETRO_CHAVE_PADRAO,
        agencia=_so_digitos_obrigatorio("BB_AGENCIA"),
        conta=_so_digitos_obrigatorio("BB_CONTA"),
        contexto=_contexto_mtls(ambiente),
    )


def _json(corpo: bytes, contexto: str) -> dict:
    try:
        dados = json.loads(corpo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErroOperacional(f"resposta de {contexto} do BB não é JSON") from exc
    if not isinstance(dados, dict):
        raise ErroOperacional(f"resposta de {contexto} do BB em formato inesperado")
    return dados


def obter_token(config: Configuracao) -> str:
    credencial = base64.b64encode(f"{config.client_id}:{config.client_secret}".encode("utf-8")).decode("ascii")
    corpo = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": ESCOPO}).encode("ascii")
    resposta = requisitar(
        config.url_token,
        metodo="POST",
        cabecalhos={
            "Authorization": f"Basic {credencial}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        corpo=corpo,
        contexto=config.contexto,
        mensagens=MENSAGENS_TOKEN,
    )
    token = _json(resposta.corpo, "token").get("access_token")
    if not token:
        raise ErroOperacional("o BB não devolveu access_token")
    return token


def data_bb(dia: date) -> str:
    """DDMMAAAA sem zero à esquerda no dia, como a API Extratos pede."""
    return f"{dia.day}{dia:%m%Y}"


def baixar_lancamentos(config: Configuracao, token: str, inicio: date, fim: date, por_pagina: int = REGISTROS_POR_PAGINA) -> list[dict]:
    rota = config.url_api + ROTA.format(agencia=config.agencia, conta=config.conta)
    lancamentos: list[dict] = []
    pagina = 1
    for _ in range(MAXIMO_PAGINAS):
        consulta = urllib.parse.urlencode({
            config.parametro_chave: config.chave_aplicativo,
            "numeroPaginaSolicitacao": pagina,
            "quantidadeRegistroPaginaSolicitacao": por_pagina,
            "dataInicioSolicitacao": data_bb(inicio),
            "dataFimSolicitacao": data_bb(fim),
        })
        resposta = requisitar(
            f"{rota}?{consulta}",
            cabecalhos={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            contexto=config.contexto,
            mensagens=MENSAGENS_EXTRATO,
        )
        dados = _json(resposta.corpo, "extrato")
        lista = dados.get("listaLancamento") or []
        if not isinstance(lista, list):
            raise ErroOperacional("listaLancamento do BB em formato inesperado")
        lancamentos.extend(lista)
        proxima = dados.get("numeroPaginaProximo") or 0
        if not lista or not isinstance(proxima, int) or proxima <= pagina:
            return lancamentos
        pagina = proxima
    raise ErroOperacional(f"extrato passou de {MAXIMO_PAGINAS} páginas; reduza o período")


def valor_assinado(lancamento: dict) -> float:
    try:
        valor = abs(float(lancamento.get("valorLancamento") or 0))
    except (TypeError, ValueError) as exc:
        raise ValidacaoErro("valorLancamento inválido no extrato do BB") from exc
    indicador = str(lancamento.get("indicadorSinalLancamento") or "").strip().upper()
    return valor * SINAL_POR_INDICADOR.get(indicador, 1)


def conferir_saldo(lancamentos: list[dict]) -> Conferencia:
    anteriores, finais, movimentos, quantidade = [], [], 0.0, 0
    for item in lancamentos:
        rotulo = str(item.get("textoDescricaoHistorico") or "").strip()
        if rotulo == ROTULO_SALDO_ANTERIOR:
            anteriores.append(valor_assinado(item))
        elif rotulo == ROTULO_SALDO_FINAL:
            finais.append(valor_assinado(item))
        elif rotulo != ROTULO_SALDO_DIA:
            movimentos += valor_assinado(item)
            quantidade += 1
    if len(anteriores) != 1 or len(finais) != 1:
        return Conferencia(aplicada=False, confere=False, lancamentos=quantidade)
    return Conferencia(
        aplicada=True,
        confere=abs(anteriores[0] + movimentos - finais[0]) <= 0.01,
        lancamentos=quantidade,
    )


def blocos_mensais(inicio: date, fim: date, hoje: date) -> list[tuple[date, date]]:
    if inicio > fim:
        raise ValidacaoErro("--de não pode ser posterior a --ate")
    if fim >= hoje:
        raise ValidacaoErro("o dia de hoje ainda está em aberto; use --ate até ontem")
    if (fim - inicio).days + 1 > MAXIMO_DIAS:
        raise ValidacaoErro(f"baixe no máximo {MAXIMO_DIAS} dias por vez")
    blocos = []
    atual = inicio
    while atual <= fim:
        proximo_mes = (atual.replace(day=28) + timedelta(days=4)).replace(day=1)
        final_bloco = min(fim, proximo_mes - timedelta(days=1))
        blocos.append((atual, final_bloco))
        atual = final_bloco + timedelta(days=1)
    return blocos


def _data_iso(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use o formato AAAA-MM-DD") from exc


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Baixa o extrato do Banco do Brasil pela API Extratos")
    parser.add_argument("--verificar", action="store_true", help="testa credenciais e permissão com os últimos 7 dias, sem salvar")
    parser.add_argument("--de", type=_data_iso, help="primeiro dia (AAAA-MM-DD); padrão: ontem")
    parser.add_argument("--ate", type=_data_iso, help="último dia (AAAA-MM-DD); padrão: igual a --de")
    parser.add_argument("--pasta", type=Path, default=PASTA_PADRAO, help="pasta de destino, fora do Git")
    parser.add_argument("--sobrescrever", action="store_true", help="baixa de novo meses que já existem")
    return parser


def verificar(config: Configuracao, hoje: date) -> None:
    print(f"Ambiente: {config.ambiente}; mTLS: {'sim' if config.contexto else 'não'}.")
    token = obter_token(config)
    print("  token obtido.")
    fim = hoje - timedelta(days=1)
    inicio = fim - timedelta(days=6)
    lancamentos = baixar_lancamentos(config, token, inicio, fim, por_pagina=50)
    conferencia = conferir_saldo(lancamentos)
    print(f"  extrato aceito: {conferencia.lancamentos} lançamento(s) de {inicio} a {fim}.")
    print(f"  {conferencia.texto()}.")


def baixar_periodo(config: Configuracao, blocos: list[tuple[date, date]], pasta: Path, sobrescrever: bool) -> int:
    token = obter_token(config)
    divergentes = 0
    for inicio, fim in blocos:
        destino = pasta / config.ambiente / f"{inicio.isoformat()}_{fim.isoformat()}.json"
        if destino.exists() and not sobrescrever:
            print(f"  {inicio} a {fim}: já baixado, pulado")
            continue
        lancamentos = baixar_lancamentos(config, token, inicio, fim)
        conferencia = conferir_saldo(lancamentos)
        conteudo = {
            "fonte": "api-bb-extrato",
            "ambiente": config.ambiente,
            "periodo": {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
            "baixado_em": datetime.now().isoformat(timespec="seconds"),
            "listaLancamento": lancamentos,
        }
        salvar_atomico(destino, json.dumps(conteudo, ensure_ascii=False, indent=1).encode("utf-8"))
        print(f"  {inicio} a {fim}: {conferencia.lancamentos} lançamento(s); {conferencia.texto()}")
        if conferencia.aplicada and not conferencia.confere:
            divergentes += 1
    return divergentes


def fluxo() -> None:
    opcoes = criar_parser().parse_args()
    carregar_env()
    config = carregar_configuracao()
    hoje = date.today()
    if opcoes.verificar:
        verificar(config, hoje)
        return
    inicio = opcoes.de or hoje - timedelta(days=1)
    blocos = blocos_mensais(inicio, opcoes.ate or inicio, hoje)
    print(f"Baixando {len(blocos)} bloco(s) mensal(is) do ambiente {config.ambiente}.")
    print(f"Destino: {opcoes.pasta / config.ambiente}")
    divergentes = baixar_periodo(config, blocos, opcoes.pasta, opcoes.sobrescrever)
    if divergentes:
        raise ValidacaoErro(
            f"{divergentes} bloco(s) com saldo divergente; arquivos salvos para análise, nada foi gravado no banco"
        )
    print("\nOK.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
