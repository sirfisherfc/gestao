"""Cliente HTTP mínimo das APIs bancárias, só com a biblioteca padrão.

As funções devolvem os bytes da resposta para quem chamou decidir onde salvar.
Mensagens de erro citam o status HTTP e uma dica, nunca o corpo da resposta nem
os cabeçalhos enviados, que carregam credenciais.
"""

from __future__ import annotations

import gzip
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from importacao_core import ErroOperacional


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
TIMEOUT_PADRAO = 90


@dataclass(frozen=True)
class Resposta:
    status: int
    corpo: bytes


class ErroHttp(ErroOperacional):
    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status = status


def carregar_env() -> None:
    """Lê o ``.env`` do projeto; o ambiente do sistema continua valendo."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(RAIZ_PROJETO / ".env")


def variavel(nome: str, *, obrigatoria: bool = True) -> str | None:
    valor = (os.environ.get(nome) or "").strip()
    if not valor and obrigatoria:
        raise ErroOperacional(f"variável {nome} não encontrada no ambiente nem no .env")
    return valor or None


def caminho_privado(nome: str) -> Path:
    """Resolve um arquivo de credencial; caminho relativo parte da raiz do projeto.

    Caminhos relativos permitem o mesmo ``.env`` nos dois PCs do OneDrive,
    mesmo com perfis de usuário diferentes.
    """
    caminho = Path(variavel(nome)).expanduser()
    if not caminho.is_absolute():
        caminho = (RAIZ_PROJETO / caminho).resolve()
    if not caminho.is_file():
        raise ErroOperacional(f"arquivo indicado em {nome} não foi encontrado")
    return caminho


def abrir_url(requisicao: urllib.request.Request, *, timeout: float, contexto: ssl.SSLContext | None):
    """Ponto único de rede, substituído nos testes."""
    return urllib.request.urlopen(requisicao, timeout=timeout, context=contexto)


def requisitar(
    url: str,
    *,
    metodo: str = "GET",
    cabecalhos: Mapping[str, str] | None = None,
    corpo: bytes | None = None,
    contexto: ssl.SSLContext | None = None,
    mensagens: Mapping[int, str] | None = None,
    timeout: float = TIMEOUT_PADRAO,
) -> Resposta:
    requisicao = urllib.request.Request(url, data=corpo, method=metodo, headers=dict(cabecalhos or {}))
    host = urllib.parse.urlparse(url).netloc
    try:
        with abrir_url(requisicao, timeout=timeout, contexto=contexto) as resposta:
            dados = resposta.read()
            codificacao = (resposta.headers.get("Content-Encoding") or "").lower()
            status = resposta.status
    except urllib.error.HTTPError as exc:
        dica = (mensagens or {}).get(exc.code, "resposta inesperada da API")
        raise ErroHttp(exc.code, f"{host} respondeu HTTP {exc.code}: {dica}") from exc
    except ssl.SSLError as exc:
        raise ErroOperacional(
            f"falha de TLS com {host} ({exc.__class__.__name__}); confira o certificado e a chave"
        ) from exc
    except urllib.error.URLError as exc:
        motivo = exc.reason.__class__.__name__ if not isinstance(exc.reason, str) else exc.reason
        raise ErroOperacional(f"falha de conexão com {host} ({motivo})") from exc
    except TimeoutError as exc:
        raise ErroOperacional(f"{host} não respondeu em {timeout:.0f} s") from exc

    if codificacao == "gzip" or dados[:2] == b"\x1f\x8b":
        try:
            dados = gzip.decompress(dados)
        except OSError as exc:
            raise ErroOperacional(f"{host} devolveu um gzip inválido") from exc
    return Resposta(status=status, corpo=dados)


def salvar_atomico(destino: Path, dados: bytes) -> None:
    """Grava num temporário e troca de uma vez, sem deixar arquivo pela metade."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(destino.name + ".parcial")
    temporario.write_bytes(dados)
    temporario.replace(destino)
