#!/usr/bin/env python3
"""Baixa o arquivo diário de conciliação da Stone (vendas, parcelas e pagamentos).

Primeira etapa da integração por API: salva o XML de cada stonecode e dia em
``scripts/importacao/api-stone-conciliacao/`` (ignorado pelo Git) e resume as
contagens. Ainda não grava no banco: o mapeamento para ``raw_stone_vendas`` e
``raw_stone_recebiveis`` depende de comparar arquivos reais com os CSVs já
importados (ver ``docs/INTEGRACAO_API_BANCOS.md``).

Acesso de cliente Stone, sem parceiro conciliador: o titular cria a chave em
Portal Stone > Perfil > Chaves de Autenticação > "API de Conciliação Stone".
A chave vai como usuário do Basic Auth, sem senha, com ``x-user-type: client``,
e vale para todos os stonecodes do CNPJ que a criou.
"""

from __future__ import annotations

import argparse
import base64
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

from api_cliente import ErroHttp, carregar_env, requisitar, salvar_atomico, variavel
from importacao_core import ErroOperacional, ValidacaoErro, executar_com_saida


URL_ARQUIVO = "https://conciliation.stone.com.br/v2/merchant/{stonecode}/conciliation-file/{data}"
LAYOUTS = ("XML2_2", "XML2_4")
LAYOUT_PADRAO = "XML2_4"
PASTA_PADRAO = Path(__file__).resolve().parent / "api-stone-conciliacao"
MAXIMO_DIAS = 366
MENSAGENS = {
    400: "data de referência ausente ou inválida",
    401: "chave recusada; confira STONE_CONCILIACAO_API_KEY no .env",
    403: (
        "acesso negado; confira o CNPJ/stonecode e o acesso da chave com a Stone. "
        "Não repita a consulta em sequência"
    ),
    429: "limite da Stone: 7 consultas por hora para o mesmo stonecode e dia; tente mais tarde",
    503: "a Stone está atualizando os arquivos; tente de novo depois das 4h (Brasília)",
}
# Um 403 pode ocorrer mesmo após um arquivo aceito. Interromper toda a rodada,
# inclusive outros dias/stonecodes, sem testar se a recusa continua.
STATUS_QUE_ENCERRAM = {401, 403, 429, 503}
# Decisão confirmada pelo proprietário em 22/10/2026: ele não usa link e
# tratará eventual uso futuro separadamente. O e-commerce/link não é
# consultado na API, nem pela lista do banco nem por STONE_STONECODES. Continua
# em stone_conta e no faturamento; só --stonecode explícito o consulta.
STONECODES_FORA_DA_API = {"173835323"}


@dataclass(frozen=True)
class ResumoArquivo:
    stonecode: str | None
    data_referencia: str | None
    layout: str | None
    transacoes: int
    parcelas: int
    liquidacoes: int
    eventos: int
    pagamentos: int

    def texto(self) -> str:
        return (
            f"{self.transacoes} transações, {self.parcelas} parcelas, "
            f"{self.liquidacoes} liquidações, {self.eventos} eventos, "
            f"{self.pagamentos} pagamentos"
        )


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def filhos(elemento, nome: str):
    return [filho for filho in elemento if local(filho.tag) == nome]


def texto(elemento, nome: str) -> str | None:
    for filho in elemento:
        if local(filho.tag) == nome:
            return (filho.text or "").strip() or None
    return None


def _so_digitos(valor: str | None) -> str:
    return "".join(caractere for caractere in valor or "" if caractere.isdigit())


def resumir_xml(dados: bytes) -> ResumoArquivo:
    try:
        raiz = ElementTree.fromstring(dados)
    except ElementTree.ParseError as exc:
        raise ValidacaoErro("a Stone devolveu um XML inválido") from exc
    if local(raiz.tag) != "Conciliation":
        raise ValidacaoErro("o XML recebido não é um arquivo de conciliação")

    cabecalho = next(iter(filhos(raiz, "Header")), None)
    transacoes = parcelas = liquidacoes = eventos = pagamentos = 0
    for secao in raiz:
        nome = local(secao.tag)
        if nome == "FinancialTransactions":
            for transacao in filhos(secao, "Transaction"):
                transacoes += 1
                for grupo in filhos(transacao, "Installments"):
                    parcelas += len(filhos(grupo, "Installment"))
        elif nome == "FinancialTransactionsAccounts":
            liquidacoes += len(filhos(secao, "Transaction"))
        elif nome.startswith("FinancialEvent") and not nome.endswith("Expected"):
            eventos += len(filhos(secao, "Event"))
        elif nome == "Payments":
            pagamentos += len(filhos(secao, "Payment"))
    return ResumoArquivo(
        stonecode=texto(cabecalho, "StoneCode") if cabecalho is not None else None,
        data_referencia=texto(cabecalho, "ReferenceDate") if cabecalho is not None else None,
        layout=texto(cabecalho, "LayoutVersion") if cabecalho is not None else None,
        transacoes=transacoes,
        parcelas=parcelas,
        liquidacoes=liquidacoes,
        eventos=eventos,
        pagamentos=pagamentos,
    )


def conferir_cabecalho(resumo: ResumoArquivo, stonecode: str, dia: date) -> None:
    """O arquivo precisa ser do stonecode e do dia pedidos."""
    if resumo.stonecode and _so_digitos(resumo.stonecode) != _so_digitos(stonecode):
        raise ValidacaoErro(f"arquivo pedido para {stonecode} veio de outro stonecode")
    digitos = _so_digitos(resumo.data_referencia)
    if digitos and not digitos.startswith((f"{dia:%Y%m%d}", f"{dia:%d%m%Y}")):
        raise ValidacaoErro(f"arquivo pedido para {dia} veio com outra data de referência")


def cabecalhos_autenticacao(chave: str) -> dict[str, str]:
    usuario = base64.b64encode(f"{chave}:".encode("utf-8")).decode("ascii")
    return {
        "Authorization": f"Basic {usuario}",
        "x-user-type": "client",
        "Accept-Encoding": "gzip",
        "Accept": "application/xml",
    }


def baixar_dia(chave: str, stonecode: str, dia: date, layout: str) -> tuple[bytes, ResumoArquivo]:
    url = URL_ARQUIVO.format(stonecode=stonecode, data=f"{dia:%Y%m%d}") + f"?layout={layout}"
    resposta = requisitar(url, cabecalhos=cabecalhos_autenticacao(chave), mensagens=MENSAGENS)
    resumo = resumir_xml(resposta.corpo)
    conferir_cabecalho(resumo, stonecode, dia)
    return resposta.corpo, resumo


def stonecodes_do_banco() -> list[str]:
    """Lista os stonecodes que entram no faturamento do painel, somente leitura.

    Imprensa e Pub ficam de fora: são outras casas, e misturá-las ao painel já
    contaminou o faturamento uma vez (ver ``docs/CANAL_IA.md``).
    """
    from importacao_core import _database_url

    try:
        import psycopg2
    except ImportError as exc:
        raise ErroOperacional(
            "dependências ausentes; execute: python -m pip install -r requirements.txt"
        ) from exc
    conn = psycopg2.connect(_database_url())
    try:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            cur.execute(
                "select stonecode from stone_conta where ativa and entra_faturamento order by stonecode;"
            )
            return [linha[0] for linha in cur.fetchall()]
    finally:
        conn.close()


def resolver_stonecodes(informados: list[str] | None) -> list[str]:
    if informados:
        codigos = informados
    elif variavel("STONE_STONECODES", obrigatoria=False):
        codigos = variavel("STONE_STONECODES").split(",")
    else:
        codigos = stonecodes_do_banco()
    codigos = [codigo.strip() for codigo in codigos if codigo.strip()]
    if not informados:
        codigos = [codigo for codigo in codigos if codigo not in STONECODES_FORA_DA_API]
    invalidos = [codigo for codigo in codigos if not codigo.isdigit()]
    if invalidos:
        raise ValidacaoErro("stonecode deve ter só dígitos: " + ", ".join(invalidos))
    if not codigos:
        raise ValidacaoErro("nenhum stonecode informado nem ativo no painel")
    return list(dict.fromkeys(codigos))


def dias_do_periodo(inicio: date, fim: date, hoje: date) -> list[date]:
    if inicio > fim:
        raise ValidacaoErro("--de não pode ser posterior a --ate")
    if fim >= hoje:
        raise ValidacaoErro("o arquivo de um dia só sai no dia seguinte, a partir das 4h; use --ate até ontem")
    quantidade = (fim - inicio).days + 1
    if quantidade > MAXIMO_DIAS:
        raise ValidacaoErro(f"período de {quantidade} dias; baixe no máximo {MAXIMO_DIAS} por vez")
    return [inicio + timedelta(days=indice) for indice in range(quantidade)]


def _data_iso(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use o formato AAAA-MM-DD") from exc


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Baixa os arquivos de conciliação da Stone")
    parser.add_argument("--verificar", action="store_true", help="testa a chave com o arquivo de ontem do primeiro stonecode, sem salvar")
    parser.add_argument("--de", type=_data_iso, help="primeiro dia (AAAA-MM-DD); padrão: ontem")
    parser.add_argument("--ate", type=_data_iso, help="último dia (AAAA-MM-DD); padrão: igual a --de")
    parser.add_argument("--stonecode", action="append", help="stonecode a baixar; repita para vários (padrão: STONE_STONECODES ou os que entram no faturamento)")
    parser.add_argument("--layout", choices=LAYOUTS, default=LAYOUT_PADRAO, help=f"layout do XML (padrão: {LAYOUT_PADRAO})")
    parser.add_argument("--pasta", type=Path, default=PASTA_PADRAO, help="pasta de destino, fora do Git")
    parser.add_argument("--sobrescrever", action="store_true", help="baixa de novo arquivos que já existem")
    return parser


def verificar(chave: str, stonecodes: list[str], layout: str, hoje: date) -> None:
    ontem = hoje - timedelta(days=1)
    stonecode = stonecodes[0]
    _, resumo = baixar_dia(chave, stonecode, ontem, layout)
    print(f"Chave aceita pela Stone para o stonecode {stonecode}.")
    print(f"  arquivo de {ontem}: {resumo.texto()}")
    print(f"  layout informado no arquivo: {resumo.layout or '(não informado)'}")
    print("  verificação encerrada após uma única consulta; nenhum outro stonecode consultado")


def baixar_periodo(
    chave: str, stonecodes: list[str], dias: list[date], layout: str, pasta: Path, sobrescrever: bool
) -> list[tuple[str, date, str]]:
    """Baixa o que falta e devolve as falhas como (stonecode, dia, mensagem).

    Dias não tentados por causa de uma falha que encerra a rodada também
    entram na lista, para o registro de execuções mostrar o buraco inteiro.
    """
    falhas: list[tuple[str, date, str]] = []
    pendentes = [(stonecode, dia) for stonecode in stonecodes for dia in dias]
    for indice, (stonecode, dia) in enumerate(pendentes):
        if indice == 0 or pendentes[indice - 1][0] != stonecode:
            print(f"\n== Stonecode {stonecode} ==")
        destino = pasta / stonecode / f"{dia.isoformat()}.xml"
        if destino.exists() and not sobrescrever:
            print(f"  {dia}: já baixado, pulado")
            continue
        try:
            dados, resumo = baixar_dia(chave, stonecode, dia, layout)
        except ErroHttp as exc:
            print(f"  {dia}: ERRO {exc}")
            falhas.append((stonecode, dia, str(exc)))
            if exc.status in STATUS_QUE_ENCERRAM:
                mensagem = f"não consultado: rodada interrompida após {exc}"
                falhas.extend((codigo, data, mensagem) for codigo, data in pendentes[indice + 1:])
                return falhas
            continue
        salvar_atomico(destino, dados)
        print(f"  {dia}: {resumo.texto()}")
    return falhas


def fluxo() -> None:
    opcoes = criar_parser().parse_args()
    carregar_env()
    chave = variavel("STONE_CONCILIACAO_API_KEY")
    stonecodes = resolver_stonecodes(opcoes.stonecode)
    hoje = date.today()
    if opcoes.verificar:
        verificar(chave, stonecodes, opcoes.layout, hoje)
        return
    inicio = opcoes.de or hoje - timedelta(days=1)
    dias = dias_do_periodo(inicio, opcoes.ate or inicio, hoje)
    print(f"Baixando {len(dias)} dia(s) de {len(stonecodes)} stonecode(s), layout {opcoes.layout}.")
    print(f"Destino: {opcoes.pasta}")
    falhas = baixar_periodo(chave, stonecodes, dias, opcoes.layout, opcoes.pasta, opcoes.sobrescrever)
    if falhas:
        raise ErroOperacional(f"{len(falhas)} arquivo(s) não baixado(s); os demais foram salvos")
    print("\nOK.")


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
