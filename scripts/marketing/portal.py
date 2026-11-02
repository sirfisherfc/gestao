"""Destino portal e credencial privada compartilhada; consultas sem imprimir dados."""
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent / 'site/tools/analytics'))
from supabase_credentials import PORTAL_REF, access_token, verify_portal


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
