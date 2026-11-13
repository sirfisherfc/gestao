"""Cliente separado do MCP de leitura. Rotas fixas, sem tokens em logs."""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.instagram_analytics.client import InstagramAnalytics, NoRedirect, sanitize

APP = '224912007567636'
PAGE = '107690041045934'
IG = '17841439937145607'
AD_ACCOUNT = '1004410887092327'  # Conta informada pelo proprietario em 02/11/2026.
BASE = 'https://graph.facebook.com/v26.0/'
# Criacao de anuncios so na conta do Portfolio; orcamento e teto ficam em impulsionar.py.
ADS_WRITE = {f'act_{AD_ACCOUNT}/{kind}' for kind in ('campaigns', 'adsets', 'adcreatives', 'ads')}


class Meta:
    def __init__(self):
        self.analytics = InstagramAnalytics()
        identity = self.analytics.identity()['data']
        if identity['id'] != IG:
            raise RuntimeError('Conta Instagram diferente do Sir Fisher.')
        self.identity = identity
        self.token = self.analytics.token
        self.page_token = None
        self.reads = 0

    def request(self, path, params=None, *, write=False, page=False):
        allowed_read = (path in {'me/permissions', 'me/adaccounts', 'me/assigned_ad_accounts', 'me/accounts', 'debug_token'}
            or bool(re.fullmatch(r'(?:act_)?\d+(?:_\d+)?(?:/(?:insights|comments|media|stories|content_publishing_limit))?', path)))
        allowed_write = (path in {IG + '/media', IG + '/media_publish', PAGE + '/feed', PAGE + '/photos'} | ADS_WRITE
            # Status de campanha/conjunto/anuncio: so pausar ou ativar, nada mais.
            or (bool(re.fullmatch(r'\d{6,30}', path)) and set(params or {}) == {'status'}
                and (params or {}).get('status') in {'ACTIVE', 'PAUSED'}))
        if (write and not allowed_write) or (not write and not allowed_read):
            raise RuntimeError('Rota fora do contrato marketing.')
        params = params or {}
        if set(params) & {'access_token', 'method', 'batch', 'redirect_uri'}:
            raise RuntimeError('Parametro de autenticacao livre bloqueado.')
        credential = self.page_token if page else self.token
        if not credential:
            raise RuntimeError('Credencial da Pagina nao confirmada.')
        data = urllib.parse.urlencode(params).encode() if write else None
        url = BASE + path + ('' if write else '?' + urllib.parse.urlencode(params))
        request = urllib.request.Request(url, data=data,
            headers={'Authorization': 'Bearer ' + credential}, method='POST' if write else 'GET')
        if not write:
            self.reads += 1
            if self.reads > 180:
                raise RuntimeError('Limite desta coleta atingido.')
        try:
            with urllib.request.build_opener(NoRedirect()).open(request, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            try:
                body = json.load(error).get('error', {})
            except Exception:
                body = {}
            code = body.get('code', 'indisponivel')
            # Em gravacoes, a mensagem da Meta diz o que corrigir; o token nunca entra.
            hint = sanitize(str(body.get('error_user_msg') or body.get('message') or ''), credential)[:300] if write else ''
            raise RuntimeError(f'Meta HTTP {error.code}, codigo {code}'
                               + (f': {hint}' if hint else '; detalhes privados omitidos.')) from None
        except (OSError, TimeoutError):
            raise RuntimeError('Falha de rede Meta; conferir estado antes de reenviar.') from None

    def pages(self):
        result = self.request('me/accounts', {'fields': 'id,name,access_token,instagram_business_account{id}', 'limit': 100})
        rows = [p for p in result.get('data', []) if p.get('id') == PAGE and p.get('instagram_business_account', {}).get('id') == IG]
        if len(rows) != 1:
            raise RuntimeError('Pagina Sir Fisher vinculada nao confirmada.')
        self.page_token = rows[0].get('access_token')
        return {'id': PAGE, 'name': rows[0].get('name'), 'instagram_id': IG}

    def permissions(self):
        result = self.request('me/permissions', {'limit': 100})
        granted = {p['permission'] for p in result.get('data', []) if p.get('status') == 'granted'}
        return {name: name in granted for name in ['instagram_basic', 'instagram_manage_insights',
            'instagram_content_publish', 'instagram_manage_comments', 'pages_manage_posts',
            'pages_read_engagement', 'pages_read_user_content', 'ads_read']}

    def list_pages(self, path, params, limit=4):
        rows, more = [], False
        for _ in range(limit):
            result = self.request(path, params)
            rows.extend(result.get('data', []))
            paging = result.get('paging', {})
            more = bool(paging.get('next'))
            cursor = paging.get('cursors', {}).get('after')
            if not more or not cursor:
                break
            params = {**params, 'after': cursor}
        return sanitize(rows, self.token), more
