"""Destino portal e credencial privada compartilhada; consultas sem imprimir dados."""
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent / 'site/tools/analytics'))
PORTAL_REF = 'lucpxoynpvogkvzepagi'


def access_token():
    if os.environ.get('SUPABASE_ACCESS_TOKEN'):
        return os.environ['SUPABASE_ACCESS_TOKEN']
    # Importacao tardia: testes/checkout isolado nao exigem os outros repos.
    try:
        from supabase_credentials import access_token as shared_token
    except ModuleNotFoundError:
        raise RuntimeError('Use o workspace completo ou SUPABASE_ACCESS_TOKEN no ambiente privado.') from None
    return shared_token()


def verify_portal():
    request = Request('https://api.supabase.com/v1/projects',headers={'Authorization':'Bearer '+access_token()})
    with urlopen(request,timeout=30) as response:
        projects=json.load(response)
    if not any(p.get('id')==PORTAL_REF for p in projects):
        raise RuntimeError('Projeto portal nao confirmado.')


def query(sql, parameters=None, *, write=False):
    route = 'query' if write else 'query/read-only'
    request = Request(f'https://api.supabase.com/v1/projects/{PORTAL_REF}/database/{route}',
        data=json.dumps({'query': sql, 'parameters': parameters or []}).encode(),
        headers={'Authorization': 'Bearer ' + access_token(), 'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=60) as response:
            return json.load(response)
    except Exception:
        raise RuntimeError('Consulta ao portal falhou; detalhes privados omitidos.') from None


def save_snapshot(source, key, start, end, payload, status='available'):
    query('''insert into public.marketing_snapshots
      (source, object_key, period_start, period_end, payload, status)
      values ($1,$2,$3::date,$4::date,$5::jsonb,$6)''',
      [source, key, start, end, json.dumps(payload), status], write=True)
