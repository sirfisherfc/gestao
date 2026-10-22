#!/usr/bin/env python3
"""Pix Stone pela API: webhook, pedido do arquivo diário e leitura do CSV.

O arquivo de conciliação de cartão não traz Pix (23% do faturamento Stone em
jul-set/2026). A Stone entrega o Pix por outro caminho:

1. Cadastrar uma vez a URL do webhook: a Edge Function ``stone-webhook``,
   protegida pelo token privado ``STONE_WEBHOOK_TOKEN`` na URL.
2. A partir das 3h do dia seguinte, pedir o CSV do dia com
   ``POST .../merchant/{cnpj}/conciliation-file/pix/{AAAA-MM-DD}``.
3. Em até 30 minutos a Stone avisa o webhook com um link pré-assinado; a
   função grava o aviso e o CSV em ``public.stone_pix_arquivo``.

Este módulo pede, aguarda e lê os arquivos. A transformação em linhas de
``raw_stone_vendas`` fica em ``api_stone_vendas.py``. Antes de liberar a
gravação, ``--analisar`` compara um arquivo real com as vendas Pix que o CSV do
Portal já gravou: identificador, escala do valor, fuso da data e terminal.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import ipaddress
import urllib.request
import urllib.error
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

import api_stone_conciliacao as conciliacao
from api_cliente import ErroHttp, carregar_env, requisitar, variavel
from importacao_core import ErroOperacional, ValidacaoErro, executar_com_saida


URL_PIX = "https://conciliation.stone.com.br/v2/merchant/{documento}/conciliation-file/pix/{data}"
URL_WEBHOOK = "https://conciliation.stone.com.br/v2/webhook"
MENSAGENS = {
    **conciliacao.MENSAGENS,
    400: "pedido recusado pela Stone (documento ou data inválidos)",
    403: "a chave não tem acesso a este CNPJ",
    409: "já existe um webhook cadastrado para esta chave; use --atualizar-webhook",
    504: "a Stone demorou a responder; tente de novo",
}
# Fortaleza não tem horário de verão desde 2000; o CSV da Stone vem em UTC.
FUSO_LOCAL = timezone(timedelta(hours=-3))
INTERVALO_CONSULTA = 30


@dataclass(frozen=True)
class ArquivoPix:
    id: str
    documento: str | None
    data_referencia: date | None
    recebido_em: datetime
    conteudo: str | None
    url_arquivo: str | None
    erro: str | None


def escolher_arquivo(arquivos):
    """Um callback inválido mais recente não esconde conteúdo íntegro anterior."""
    return next((a for a in arquivos if a.conteudo is not None and not a.erro), None)


def baixar_csv_recebido(url):
    """GET limitado do arquivo já anunciado, sem credenciais e sem redirects."""
    try:
        endereco=urllib.parse.urlsplit(url)
        host=endereco.hostname or ''
        invalido=(endereco.scheme!='https' or endereco.username or endereco.password or endereco.port not in (None,443)
                  or '.' not in host or host.endswith(('.local','.internal')) or host.endswith('.supabase.co'))
        try:
            ipaddress.ip_address(host)
            invalido=True
        except ValueError:
            pass
        if invalido: raise ValueError
    except ValueError as exc:
        raise ErroOperacional('endereço do arquivo Pix não permitido') from exc
    class SemRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs): return None
    opener=urllib.request.build_opener(SemRedirect())
    try:
        with opener.open(urllib.request.Request(url,headers={'Accept':'text/csv'}),timeout=20) as resposta:
            if resposta.status!=200: raise ErroHttp(resposta.status,'download do CSV com resposta incompleta')
            dados=resposta.read(5_000_001)
        if len(dados)>5_000_000:
            raise ErroOperacional('CSV Pix excede o tamanho permitido')
        texto=dados.decode('utf-8-sig')
        ler_csv(texto)  # HTML/erro vazio não pode ser salvo como um CSV pronto.
        return texto
    except urllib.error.HTTPError as exc:
        raise ErroHttp(exc.code,f'download do CSV respondeu HTTP {exc.code}') from None
    except (urllib.error.URLError,TimeoutError,UnicodeDecodeError):
        raise ErroOperacional('falha ao baixar o CSV Pix') from None


def _so_digitos(valor: object) -> str:
    return "".join(caractere for caractere in str(valor or "") if caractere.isdigit())


def _cabecalhos(chave: str) -> dict[str, str]:
    return {**conciliacao.cabecalhos_autenticacao(chave), "Content-Type": "application/json", "Accept": "application/json"}


def url_webhook() -> str:
    base = variavel("SUPABASE_URL").rstrip("/")
    return f"{base}/functions/v1/stone-webhook?token={variavel('STONE_WEBHOOK_TOKEN')}"


def cadastrar_webhook(chave: str, *, atualizar: bool = False) -> None:
    # Cadastro mínimo documentado: headers opcionais têm contrato ambíguo.
    # A URL com token é privada e nunca deve aparecer em logs ou documentação.
    url = url_webhook()
    if len(url) > 100:
        raise ValidacaoErro("a URL privada do webhook deve ter no máximo 100 caracteres; use token seguro de 24 caracteres")
    corpo = json.dumps({"url": url}).encode("utf-8")
    requisitar(URL_WEBHOOK, metodo="PUT" if atualizar else "POST", cabecalhos=_cabecalhos(chave), corpo=corpo, mensagens=MENSAGENS)


def solicitar(chave: str, documento: str, dia: date) -> None:
    url = URL_PIX.format(documento=documento, data=dia.isoformat())
    requisitar(url, metodo="POST", cabecalhos=_cabecalhos(chave), corpo=b"{}", mensagens=MENSAGENS)


class FilaPix:
    """Leitura e marcação de ``stone_pix_arquivo``; a escrita é só de controle."""

    def __init__(self):
        from importacao_core import _database_url

        import psycopg2

        self.conn = psycopg2.connect(_database_url())
        self.conn.autocommit = True

    def documentos(self) -> list[str]:
        with self.conn.cursor() as cur:
            cur.execute(
                "select distinct documento from raw_stone_vendas where documento is not null and stonecode in "
                "(select stonecode from stone_conta where ativa and entra_faturamento);"
            )
            return sorted({_so_digitos(linha[0]) for linha in cur.fetchall() if _so_digitos(linha[0])})

    def arquivos(self, documento: str, dia: date) -> list[ArquivoPix]:
        with self.conn.cursor() as cur:
            cur.execute(
                "select id::text, documento, data_referencia, recebido_em, conteudo, url_arquivo, erro "
                "from stone_pix_arquivo where documento = %s and data_referencia = %s order by recebido_em desc,id desc;",
                (documento, dia),
            )
            return [ArquivoPix(*linha) for linha in cur.fetchall()]

    def dias_prontos_nao_processados(self, documento):
        with self.conn.cursor() as cur:
            cur.execute('select data_referencia from (select distinct on(data_referencia) data_referencia,processado_em '
                        'from stone_pix_arquivo where documento=%s and conteudo is not null and erro is null '
                        'order by data_referencia,recebido_em desc,id desc) a where processado_em is null', (documento,))
            return {r[0] for r in cur.fetchall()}

    def aguardar(self, pedidos: list[tuple[str, date]], desde: datetime | None, minutos: int) -> dict[tuple[str, date], ArquivoPix]:
        """Espera o aviso de cada pedido feito depois de ``desde``."""
        limite = time.monotonic() + minutos * 60
        prontos: dict[tuple[str, date], ArquivoPix] = {}
        while True:
            for pedido in pedidos:
                if pedido in prontos:
                    continue
                recentes = [item for item in self.arquivos(*pedido) if desde is None or item.recebido_em >= desde]
                valido = escolher_arquivo(recentes)
                if valido:
                    prontos[pedido] = valido
                elif recentes and recentes[0].erro:
                    prontos[pedido] = recentes[0]
            if len(prontos) == len(pedidos) or time.monotonic() >= limite:
                return prontos
            time.sleep(INTERVALO_CONSULTA)

    def conteudo(self, arquivo: ArquivoPix) -> str:
        if arquivo.conteudo:
            return arquivo.conteudo
        if not arquivo.url_arquivo:
            raise ErroOperacional(f"aviso Pix {arquivo.data_referencia} sem link nem conteúdo ({arquivo.erro or 'sem detalhe'})")
        texto = baixar_csv_recebido(arquivo.url_arquivo)
        with self.conn.cursor() as cur:
            cur.execute(
                "update stone_pix_arquivo set conteudo = %s, baixado_em = now(), erro = null where id = %s;",
                (texto, arquivo.id),
            )
        return texto

    def recuperar_download(self, documento, dia):
        """No máximo dois GETs de recuperação, separados por 1h; nunca POST Pix."""
        for arquivo in self.arquivos(documento,dia):
            if arquivo.conteudo is not None or not arquivo.url_arquivo:
                continue
            if 'HTTP 403' in (arquivo.erro or ''):
                continue  # Endereço expirado não se recupera com novo pedido.
            with self.conn, self.conn.cursor() as cur:
                cur.execute('select pg_advisory_xact_lock(hashtextextended(%s,0))',
                            (f'stone-pix-download:{documento}:{dia}',))
                cur.execute('select coalesce(sum(tentativas_download),0),max(ultima_tentativa_download) '
                            'from stone_pix_arquivo where documento=%s and data_referencia=%s', (documento,dia))
                tentativas,ultima=cur.fetchone()
                if tentativas>=2 or (ultima and datetime.now(ultima.tzinfo)-ultima<timedelta(hours=1)):
                    return
                cur.execute('update stone_pix_arquivo set tentativas_download=tentativas_download+1,'
                            'ultima_tentativa_download=now() where id=%s and conteudo is null '
                            "and tentativas_download<2 and (ultima_tentativa_download is null or ultima_tentativa_download<now()-interval '1 hour') "
                            "and recebido_em>now()-interval '20 hours' returning id", (arquivo.id,))
                reservado = cur.fetchone()
            if not reservado:
                continue
            try:
                self.conteudo(arquivo)
                return
            except ErroHttp as exc:
                with self.conn.cursor() as cur:
                    cur.execute('update stone_pix_arquivo set erro=%s where id=%s',
                                (f'download do CSV respondeu HTTP {exc.status}',arquivo.id))
            except (ErroOperacional,ValidacaoErro):
                with self.conn.cursor() as cur:
                    cur.execute('update stone_pix_arquivo set erro=%s where id=%s',('falha ao recuperar download do CSV',arquivo.id))
            return  # Um único GET por rodada, mesmo com callbacks duplicados.

    def marcar_processado(self, arquivo: ArquivoPix) -> None:
        with self.conn.cursor() as cur:
            cur.execute("update stone_pix_arquivo set processado_em = now() where id = %s;", (arquivo.id,))

    def fechar(self) -> None:
        self.conn.close()


def ler_csv(texto: str) -> list[dict[str, str]]:
    """Lê o CSV Pix; a Stone não documenta o separador, então ele é detectado."""
    amostra = texto[:4096]
    try:
        dialeto = csv.Sniffer().sniff(amostra.splitlines()[0] if amostra else ",", delimiters=",;")
    except csv.Error:
        dialeto = csv.excel
    leitor = csv.DictReader(io.StringIO(texto), dialect=dialeto)
    if not leitor.fieldnames or "id" not in leitor.fieldnames:
        raise ValidacaoErro("CSV Pix sem a coluna id; o layout da Stone mudou")
    return [{chave: (valor or "").strip() for chave, valor in linha.items() if chave} for linha in leitor]


def data_hora_local(valor: str | None) -> datetime | None:
    texto = (valor or "").strip()
    if not texto:
        return None
    try:
        momento = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(FUSO_LOCAL).replace(tzinfo=None)


def decimal_ou_none(valor: str | None) -> Decimal | None:
    try:
        return Decimal((valor or "").replace(",", "."))
    except InvalidOperation:
        return None


def analisar(linhas: list[dict[str, str]], vendas_pix: dict[str, dict]) -> dict[str, object]:
    """Compara o CSV real com as vendas Pix já gravadas pelo CSV do Portal.

    ``vendas_pix`` vem do banco: stone_id -> data_venda, valor_bruto, n_serie.
    Só contagens vão para o terminal.
    """
    resultado: dict[str, object] = {"linhas": len(linhas)}
    for coluna in ("id", "pix_transaction__e2e_id", "pix_transaction__pix_key"):
        resultado[f"casam por {coluna}"] = sum(1 for linha in linhas if linha.get(coluna) in vendas_pix)
    chave = max(("id", "pix_transaction__e2e_id", "pix_transaction__pix_key"), key=lambda coluna: resultado[f"casam por {coluna}"])
    casadas = [(linha, vendas_pix[linha[chave]]) for linha in linhas if linha.get(chave) in vendas_pix]
    escala = Counter()
    minutos = Counter()
    terminal = Counter()
    for linha, venda in casadas:
        valor = decimal_ou_none(linha.get("amount"))
        if valor is not None:
            if abs(valor - venda["valor_bruto"]) <= Decimal("0.01"):
                escala["reais"] += 1
            elif abs(valor / 100 - venda["valor_bruto"]) <= Decimal("0.01"):
                escala["centavos"] += 1
            else:
                escala["outro"] += 1
        momento = data_hora_local(linha.get("created_at"))
        if momento is not None and venda["data_venda"] is not None:
            minutos[round((venda["data_venda"] - momento).total_seconds() / 60)] += 1
        terminal[linha.get("pix_transaction__terminal__serial_number") == venda["n_serie"]] += 1
    resultado.update({
        "chave escolhida": chave,
        "escala do valor": dict(escala),
        "data do banco - created_at local (min)": dict(minutos.most_common(4)),
        "terminal igual": dict(terminal),
        "status": dict(Counter(linha.get("status") for linha in linhas)),
        "payment_method": dict(Counter(linha.get("payment_method") for linha in linhas)),
        "tipo pix": dict(Counter(linha.get("pix_transaction__type") for linha in linhas)),
        "operação": dict(Counter(linha.get("pix_transaction__detail__operation") for linha in linhas)),
        "tipo de terminal": dict(Counter(linha.get("pix_transaction__terminal__type") for linha in linhas)),
        "tarifa diferente de zero": sum(1 for linha in linhas if (decimal_ou_none(linha.get("pix_transaction__fee_amount")) or 0) != 0),
        "formato created_at": re.sub(r"\d", "9", linhas[0].get("created_at") or "") if linhas else None,
        "formato amount": re.sub(r"\d", "9", linhas[0].get("amount") or "") if linhas else None,
    })
    return resultado


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pix Stone pela API de Conciliação")
    acao = parser.add_mutually_exclusive_group(required=True)
    acao.add_argument("--cadastrar-webhook", action="store_true", help="cadastra a Edge Function stone-webhook na Stone")
    acao.add_argument("--atualizar-webhook", action="store_true", help="troca a URL do webhook já cadastrado")
    acao.add_argument("--solicitar", action="store_true", help="pede os arquivos Pix do período e aguarda os avisos")
    acao.add_argument("--analisar", action="store_true", help="compara os arquivos Pix recebidos com as vendas Pix do painel")
    parser.add_argument("--de", type=conciliacao._data_iso, help="primeiro dia (AAAA-MM-DD); padrão: ontem")
    parser.add_argument("--ate", type=conciliacao._data_iso, help="último dia (AAAA-MM-DD); padrão: igual a --de")
    parser.add_argument("--documento", action="append", help="CNPJ, só dígitos (padrão: o das vendas dos stonecodes do painel)")
    parser.add_argument("--aguardar", type=int, default=35, help="minutos de espera pelos avisos (padrão: 35)")
    return parser


def _vendas_pix(fila: FilaPix, dia: date) -> dict[str, dict]:
    with fila.conn.cursor() as cur:
        cur.execute(
            "select stone_id, data_venda, valor_bruto, n_serie from raw_stone_vendas "
            "where produto ilike 'pix%%' and data_venda >= %s and data_venda < %s;",
            (dia, dia + timedelta(days=1)),
        )
        return {linha[0]: {"data_venda": linha[1], "valor_bruto": linha[2], "n_serie": linha[3]} for linha in cur.fetchall()}


def fluxo() -> None:
    opcoes = criar_parser().parse_args()
    carregar_env()
    chave = variavel("STONE_CONCILIACAO_API_KEY")
    if opcoes.cadastrar_webhook or opcoes.atualizar_webhook:
        cadastrar_webhook(chave, atualizar=opcoes.atualizar_webhook)
        print("Webhook aceito pela Stone (ela validou a URL antes de salvar).")
        return

    hoje = date.today()
    inicio = opcoes.de or hoje - timedelta(days=1)
    dias = conciliacao.dias_do_periodo(inicio, opcoes.ate or inicio, hoje)
    fila = FilaPix()
    try:
        documentos = [_so_digitos(item) for item in opcoes.documento] if opcoes.documento else fila.documentos()
        if not documentos:
            raise ValidacaoErro("nenhum CNPJ encontrado para pedir o Pix")
        if opcoes.solicitar:
            from api_stone_rotina import Controle, pedir_pix
            pedidos = []
            controle = Controle()
            try:
                for documento in documentos:
                    for dia in dias:
                        pedir_pix(controle, fila, chave, documento, dia)
                        pedidos.append((documento, dia))
                prontos = fila.aguardar(pedidos, None, opcoes.aguardar) if pedidos else {}
            finally:
                controle.fechar()
            for documento, dia in pedidos:
                arquivo = prontos.get((documento, dia))
                situacao = "CSV recebido" if arquivo and arquivo.conteudo else (arquivo.erro if arquivo else "sem aviso no prazo")
                print(f"  Pix {dia}: {situacao}")
            if len(prontos) < len(pedidos) or len(pedidos) < len(documentos) * len(dias):
                raise ErroOperacional("houve dia sem arquivo Pix; veja acima")
            return
        for documento in documentos:
            for dia in dias:
                arquivos = fila.arquivos(documento, dia)
                if not arquivos:
                    print(f"\n{dia}: nenhum aviso Pix recebido")
                    continue
                linhas = ler_csv(fila.conteudo(arquivos[0]))
                print(f"\n== Pix {dia} ==")
                for nome, valor in analisar(linhas, _vendas_pix(fila, dia)).items():
                    print(f"  {nome}: {valor}")
    finally:
        fila.fechar()


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
