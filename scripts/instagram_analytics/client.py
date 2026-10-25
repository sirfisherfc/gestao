"""Leituras limitadas da conta propria; reutiliza a credencial canonica do GBP."""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request

from scripts.gbp.gbp import credencial

API_VERSION = "v26.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"
USERNAME = "sirfisherfc"
TZ = dt.timezone(dt.timedelta(hours=-3), "America/Fortaleza")
FIELDS = "id,media_type,media_product_type,caption,timestamp,permalink"
ACCOUNT_METRICS = {
    "reach": "Contas alcancadas no periodo; nao somar alcances diarios.",
    "views": "Visualizacoes; pode incluir varias da mesma conta.",
    "accounts_engaged": "Contas que interagiram; nao equivale a reservas.",
    "total_interactions": "Interacoes, conforme definicao retornada pela Meta.",
    "likes": "Curtidas.", "comments": "Contagem de comentarios, sem seu conteudo.",
    "saves": "Salvamentos.", "shares": "Compartilhamentos.",
    "profile_links_taps": "Toques em links do perfil; nao identifica post nem reserva.",
}
MEDIA_METRICS = {
    "reach": "Contas alcancadas por esta midia; nao somar como pessoas unicas.",
    "views": "Visualizacoes acumuladas da midia, com possiveis repeticoes.",
    "total_interactions": "Interacoes acumuladas da midia.",
    "likes": "Curtidas.", "comments": "Contagem de comentarios, sem seu conteudo.",
    "saved": "Salvamentos desta midia (nome da API difere de saves da conta).",
    "shares": "Compartilhamentos.",
    "ig_reels_avg_watch_time": "Tempo medio assistido de Reels; verificar unidade na resposta.",
    "ig_reels_video_view_total_time": "Tempo assistido de Reels; verificar unidade na resposta.",
}
STORY_METRICS = {k: MEDIA_METRICS[k] for k in ("reach", "views", "shares", "total_interactions")}
READ_PERMISSIONS = ("instagram_basic", "instagram_manage_insights", "pages_show_list", "pages_read_engagement")


class AnalyticsError(Exception):
    """Erro seguro para devolver a uma IA sem URL, token ou traceback."""


def sanitize(value, secret=""):
    """Remove URLs de paginacao autenticadas e chaves privadas antes do cache."""
    if isinstance(value, dict):
        return {k: sanitize(v, secret) for k, v in value.items()
                if k.lower() not in {"access_token", "authorization", "next", "previous"}}
    if isinstance(value, list):
        return [sanitize(v, secret) for v in value]
    if isinstance(value, str):
        value = value.replace(secret, "[segredo removido]") if secret else value
        return re.sub(r"(?i)(access_token|client_secret|appsecret_proof)=[^&\s\"<>]+", r"\1=[removido]", value)
    return value


class Cache:
    def __init__(self, directory=None):
        base = Path(directory) if directory else Path(os.environ.get("LOCALAPPDATA", Path.home() / ".cache")) / "SirFisher" / "instagram-analytics"
        base.mkdir(parents=True, exist_ok=True)
        self.path = base / "cache.sqlite3"
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, expires REAL, created TEXT, value TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS owned_media (id TEXT, scope TEXT, kind TEXT, discovered TEXT, PRIMARY KEY(id,scope))")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=20)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def get(self, key):
        with self.connect() as db:
            row = db.execute("SELECT value,created FROM cache WHERE key=? AND expires>?", (key, time.time())).fetchone()
        return (json.loads(row[0]), row[1]) if row else None

    def put(self, key, value, ttl):
        at = dt.datetime.now(dt.timezone.utc).isoformat()
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?,?)", (key, time.time()+ttl, at, json.dumps(value, ensure_ascii=False)))
        return at

    def remember(self, rows, scope, kind):
        at = dt.datetime.now(dt.timezone.utc).isoformat()
        with self.connect() as db:
            db.executemany("INSERT OR REPLACE INTO owned_media VALUES (?,?,?,?)", [(r["id"], scope, kind, at) for r in rows])

    def kind(self, ident, scope):
        with self.connect() as db:
            row = db.execute("SELECT kind FROM owned_media WHERE id=? AND scope=?", (ident, scope)).fetchone()
        return row[0] if row else None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class InstagramAnalytics:
    def __init__(self, *, token=None, fixed_id=None, cache=None, transport=None):
        self.token = credencial("META_IG_TOKEN") if token is None else token
        self.fixed_id = credencial("META_IG_USER_ID") if fixed_id is None else fixed_id
        if not self.token:
            raise AnalyticsError("META_IG_TOKEN ausente no mecanismo privado existente.")
        self.cache = cache or Cache()
        self.scope = API_VERSION + ":" + USERNAME + ":" + hashlib.sha256(self.token.encode()).hexdigest()[:20]
        self.transport = transport or self._http
        self.calls = 0
        self.reads = []
        self.account_id = None
        self.refresh_identity = False

    def _http(self, path, params):
        # Sem method/path/host/campos livres nos argumentos das ferramentas.
        allowed = path in {"me/accounts", "me/permissions"}
        allowed |= bool(re.fullmatch(r"\d{5,30}", path))
        allowed |= bool(re.fullmatch(r"\d{5,30}/(?:media|stories|insights)", path))
        if not allowed:
            raise AnalyticsError("Rota fora do contrato de leitura.")
        if any(k in params for k in ("access_token", "method", "batch", "callback", "redirect_uri")):
            raise AnalyticsError("Parametro fora do contrato de leitura.")
        req = urllib.request.Request(BASE + "/" + path + "?" + urllib.parse.urlencode(params),
                                     headers={"Authorization": "Bearer " + self.token}, method="GET")
        try:
            with urllib.request.build_opener(NoRedirect()).open(req, timeout=25) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            try:
                error = json.load(exc).get("error", {})
            except (ValueError, TypeError):
                error = {}
            message = sanitize(str(error.get("message", "Resposta sem detalhe publico")), self.token)
            raise AnalyticsError(f"Meta HTTP {exc.code}; codigo {error.get('code', 'indisponivel')}: {message[:700]}") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise AnalyticsError("Falha de rede na leitura da Meta; URL e credencial omitidas.") from None

    def _get(self, path, params, ttl=300, fresh=False):
        key = self.scope + ":" + path + ":" + json.dumps(params, sort_keys=True)
        cached = None if fresh else self.cache.get(key)
        if cached:
            data, at = cached
            self.reads.append({"endpoint": path, "collected_at_utc": at, "cache": True})
            return data
        if self.calls >= 60:
            raise AnalyticsError("Limite de 60 leituras nesta operacao atingido; reutilize o cache.")
        self.calls += 1
        raw = self.transport(path, params)
        has_more = bool(raw.get("paging", {}).get("next"))
        data = sanitize(raw, self.token)
        if "paging" in data:
            data["paging"]["has_more"] = has_more
        at = self.cache.put(key, data, ttl)
        self.reads.append({"endpoint": path, "collected_at_utc": at, "cache": False})
        return data

    def _envelope(self, data, **metadata):
        return {"source": "Meta Instagram API with Facebook Login", "api_version": API_VERSION,
                "username": USERNAME, "requested_timezone": "America/Fortaleza",
                "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "http_reads": self.calls, "reads": self.reads, **metadata, "data": data}

    def _identity(self):
        if self.account_id:
            return {"id": self.account_id, "username": USERNAME}
        ident = self.fixed_id
        if ident and not re.fullmatch(r"\d{5,30}", ident):
            raise AnalyticsError("META_IG_USER_ID possui formato invalido.")
        if not ident:
            matches = set()
            params = {"fields": "id,instagram_business_account{id,username}", "limit": 25}
            complete = False
            for _ in range(3):
                result = self._get("me/accounts", params, 900, fresh=self.refresh_identity)
                for page in result.get("data", []):
                    account = page.get("instagram_business_account", {})
                    if account.get("username", "").lower() == USERNAME:
                        matches.add(account["id"])
                paging = result.get("paging", {})
                if not paging.get("has_more"):
                    complete = True
                    break
                after = paging.get("cursors", {}).get("after")
                if not after:
                    break
                params = {**params, "after": after}
            if len(matches) != 1 or not complete:
                raise AnalyticsError("Nao foi possivel confirmar uma unica conta @sirfisherfc; nenhuma primeira conta foi escolhida.")
            ident = next(iter(matches))
        result = self._get(ident, {"fields": "id,username,name,media_count,followers_count"}, 900, fresh=self.refresh_identity)
        if result.get("username", "").lower() != USERNAME or result.get("id") != ident:
            raise AnalyticsError("Identidade diferente de @sirfisherfc; leitura interrompida.")
        self.account_id = ident
        return result

    def identity(self, refresh=False):
        if type(refresh) is not bool:
            raise AnalyticsError("refresh deve ser booleano.")
        self.refresh_identity = refresh
        return self._envelope(self._identity())

    def permissions(self):
        self._identity()
        result = self._get("me/permissions", {"limit": 100}, 3600)
        granted = {x["permission"] for x in result.get("data", []) if x.get("status") == "granted"}
        return self._envelope({"required_read_permissions": {x: x in granted for x in READ_PERMISSIONS},
                               "other_granted_permissions_count": len(granted-set(READ_PERMISSIONS)),
                               "token_has_write_permissions": bool(granted & {"instagram_content_publish", "instagram_manage_comments", "instagram_manage_messages", "ads_management"}),
                               "server_allows_only_read_tools": True})

    @staticmethod
    def _bounds(days, end_date=None, consolidated=False):
        if type(days) is not int or not 1 <= days <= 30:
            raise AnalyticsError("days deve ser inteiro entre 1 e 30.")
        today = dt.datetime.now(TZ).date()
        if end_date:
            try:
                end = dt.date.fromisoformat(end_date) + dt.timedelta(days=1)
            except (ValueError, TypeError):
                raise AnalyticsError("end_date deve usar YYYY-MM-DD (ultimo dia incluido).") from None
        else:
            # Account: ultimo dia incluido e anteontem; midias: inclui hoje.
            end = today-dt.timedelta(days=1) if consolidated else today+dt.timedelta(days=1)
        start = end-dt.timedelta(days=days)
        if end > today+dt.timedelta(days=1) or start < today-dt.timedelta(days=89):
            raise AnalyticsError("Janela fora dos ultimos 90 dias ou no futuro.")
        a = dt.datetime.combine(start, dt.time(), TZ)
        b = dt.datetime.combine(end, dt.time(), TZ)
        return {"since": int(a.timestamp()), "until": int(b.timestamp())}, {"start_inclusive": a.isoformat(), "end_exclusive": b.isoformat(), "days": days}

    def _list(self, kind, days=30, max_pages=3, page_size=25, end_date=None):
        account = self._identity()
        if type(max_pages) is not int or not 1 <= max_pages <= 4 or type(page_size) is not int or not 1 <= page_size <= 50:
            raise AnalyticsError("Paginacao limitada a 1-4 paginas de 1-50 itens.")
        window, bounds = self._bounds(days, end_date)
        params = {"fields": FIELDS, "limit": page_size}
        if kind == "media":
            params.update(window)
        items, seen, has_more = [], set(), False
        for _ in range(max_pages):
            result = self._get(account["id"]+"/"+kind, params, 60 if kind == "stories" else 300)
            for row in result.get("data", []):
                ident = row.get("id", "")
                if not re.fullmatch(r"\d{5,30}", ident):
                    continue
                try:
                    stamp = dt.datetime.fromisoformat(row["timestamp"]).timestamp()
                except (ValueError, KeyError):
                    continue
                if kind == "media" and not window["since"] <= stamp < window["until"]:
                    continue
                if ident not in seen:
                    seen.add(ident)
                    items.append(row)
            paging = result.get("paging", {})
            has_more = bool(paging.get("has_more"))
            after = paging.get("cursors", {}).get("after")
            if not has_more or not after:
                break
            params = {**params, "after": after}
        items.sort(key=lambda row: (dt.datetime.fromisoformat(row["timestamp"]).timestamp(), row["id"]), reverse=True)
        self.cache.remember(items, self.scope + ":" + account["id"], kind)
        return self._envelope(items, requested_window=bounds if kind == "media" else None,
                              count=len(items), pagination_truncated=has_more,
                              coverage="Stories disponiveis no instante da coleta; nao reconstrui stories expirados." if kind == "stories" else "Publicacoes retornadas nesta janela; paginacao limitada e IDs deduplicados.")

    def media(self, days=30, max_pages=3, page_size=25, end_date=None):
        return self._list("media", days, max_pages, page_size, end_date)

    def stories(self):
        return self._list("stories", max_pages=2)

    def _metrics(self, path, requested, allowed, params):
        if requested is None:
            requested = list(allowed)
        if not isinstance(requested, list) or not requested or len(requested) > 10 or any(not isinstance(x, str) for x in requested) or len(set(requested)) != len(requested) or any(x not in allowed for x in requested):
            raise AnalyticsError("Selecione ate dez metricas distintas do catalogo desta ferramenta.")
        outputs = []
        # Por metrica: uma indisponivel nao transforma as outras em erro ou zero.
        for metric in requested:
            try:
                response = self._get(path, {**params, "metric": metric}, 21600)
                values = response.get("data", [])
                matching = [x for x in values if x.get("name") == metric]
                has_data = any(self._has_value(x) for x in matching)
                outputs.append({"metric": metric, "status": "available" if has_data else "unavailable",
                                "definition": allowed[metric], "response": matching or None,
                                "reason": None if has_data else "Meta nao retornou valor desta metrica; nao equivale a zero."})
            except AnalyticsError as error:
                outputs.append({"metric": metric, "status": "unavailable", "definition": allowed[metric],
                                "response": None, "reason": str(error)})
        return outputs

    @staticmethod
    def _has_value(value):
        if isinstance(value, dict):
            return any((k == "value" and isinstance(v, (int, float)) and not isinstance(v, bool))
                       or InstagramAnalytics._has_value(v) for k, v in value.items())
        if isinstance(value, list):
            return any(InstagramAnalytics._has_value(v) for v in value)
        return False

    def account_insights(self, days=30, end_date=None, metrics=None):
        account = self._identity()
        window, bounds = self._bounds(days, end_date, consolidated=True)
        result = self._metrics(account["id"]+"/insights", metrics, ACCOUNT_METRICS,
                               {**window, "period": "day", "metric_type": "total_value"})
        return self._envelope(result, requested_window=bounds,
                              coverage="Agregados do periodo pedido; manter period/end_time retornados pela Meta. Nao relabelar o dia da Meta como dia civil de Fortaleza.")

    def media_insights(self, media_id, metrics=None):
        account = self._identity()
        if not isinstance(media_id, str) or not re.fullmatch(r"\d{5,30}", media_id):
            raise AnalyticsError("media_id deve ser o ID numerico listado pelas ferramentas desta conta.")
        kind = self.cache.kind(media_id, self.scope + ":" + account["id"])
        if not kind:
            raise AnalyticsError("Midia nao confirmada como propria; liste publicacoes ou stories antes de consultar insights.")
        allowed = STORY_METRICS if kind == "stories" else MEDIA_METRICS
        if metrics is None:
            metrics = list(allowed) if kind == "stories" else ["reach", "views", "total_interactions", "likes", "comments", "saved", "shares"]
        result = self._metrics(media_id+"/insights", metrics, allowed, {})
        return self._envelope(result, media_id=media_id, media_kind=kind,
                              coverage="Metricas acumuladas/as-of, conforme period retornado. Publicacao nos ultimos 30 dias nao transforma lifetime em desempenho desses 30 dias.")


def metric_catalog():
    return {"api_version": API_VERSION, "account": ACCOUNT_METRICS, "media": MEDIA_METRICS,
            "stories": STORY_METRICS, "availability": "Validada por chamada; formato, idade da midia e permissao podem tornar uma metrica indisponivel.",
            "limits": {"max_days": 30, "max_pages": 4, "page_size_max": 50, "graph_reads_per_tool_max": 60},
            "forbidden": ["publicacao", "exclusao", "Direct", "conteudo de comentarios", "anuncios", "endpoint ou metodo arbitrario"]}
