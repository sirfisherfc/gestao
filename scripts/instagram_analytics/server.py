"""MCP stdio de leitura; compativel com o SDK mcp 2.3 ja instalado no PC."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from scripts.instagram_analytics.client import AnalyticsError, InstagramAnalytics, metric_catalog

app = MCPServer("Sir Fisher Instagram Analytics", instructions=(
    "Leia apenas conteudo proprio e metricas do @sirfisherfc. Confirme identidade; liste publicacoes/stories antes de seus insights. "
    "Use o cache e no maximo 30 dias. Indisponivel difere de zero; alcance de posts nao soma pessoas unicas. "
    "Insights lifetime nao sao uma serie diaria. Nao atribua reservas a um post sem identificador rastreavel. "
    "Nao existem operacoes de escrita, Direct, conteudo de comentarios, anuncios ou chamada generica de API neste servidor."
))
READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)


def call(method, **params):
    try:
        return getattr(InstagramAnalytics(), method)(**params)
    except AnalyticsError as error:
        return {"status": "unavailable", "reason": str(error)}


@app.tool(annotations=READ)
def instagram_identity(refresh: bool = False) -> dict:
    """Confirma @sirfisherfc. refresh=True faz nova leitura autenticada; padrao reutiliza cache de 15 min."""
    return call("identity", refresh=refresh)


@app.tool(annotations=READ)
def instagram_permissions() -> dict:
    """Confere permissoes de leitura e informa se o token compartilhado possui outros privilegios."""
    return call("permissions")


@app.tool(annotations=READ)
def instagram_media(days: int = 30, max_pages: int = 3, page_size: int = 25, end_date: str | None = None) -> dict:
    """Lista IDs, formato, legenda, data e permalink de publicacoes proprias; usa cache e paginacao limitada."""
    return call("media", days=days, max_pages=max_pages, page_size=page_size, end_date=end_date)


@app.tool(annotations=READ)
def instagram_account_insights(days: int = 30, end_date: str | None = None, metrics: list[str] | None = None) -> dict:
    """Le agregados da conta em ate 30 dias. end_date e o ultimo dia incluido; padrao termina anteontem."""
    return call("account_insights", days=days, end_date=end_date, metrics=metrics)


@app.tool(annotations=READ)
def instagram_media_insights(media_id: str, metrics: list[str] | None = None) -> dict:
    """Le insights acumulados de um ID confirmado como proprio por media/stories; disponibilidade varia por formato."""
    return call("media_insights", media_id=media_id, metrics=metrics)


@app.tool(annotations=READ)
def instagram_stories() -> dict:
    """Lista somente stories disponiveis agora; nao recupera os que expiraram."""
    return call("stories")


@app.tool(annotations=READ)
def instagram_metric_catalog() -> dict:
    """Mostra metricas aceitas, limites e definicoes; nenhuma chamada a Meta."""
    return metric_catalog()


if __name__ == "__main__":
    app.run(transport="stdio")
