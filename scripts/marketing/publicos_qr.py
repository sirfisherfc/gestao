"""Prepara somente público QR consentido e semelhante; prévia por padrão.

python scripts/marketing/publicos_qr.py
python scripts/marketing/publicos_qr.py --aplicar --out tmp/publicos-qr-2026-11-25/recibo.json

Não muda campanhas, anúncios, orçamento, sinal VisitaQR ou consentimento.
"""
import argparse
import json
from pathlib import Path

from meta import Meta, AD_ACCOUNT, QR_PIXEL, QR_NAME, QR_LOOKALIKE, QR_RULE, sanitize

FIELDS = 'id,name,account_id,subtype,rule,lookalike_spec,delivery_status,operation_status,approximate_count_lower_bound,approximate_count_upper_bound'


def website_params():
    # v27 infere WEBSITE da regra; subtype=WEBSITE é recusado (2654).
    return {'name': QR_NAME, 'rule': json.dumps(QR_RULE),
            'retention_days': 180, 'prefill': 'true'}


def similar_params(seed):
    return {'name': QR_LOOKALIKE, 'subtype': 'LOOKALIKE', 'origin_audience_id': seed,
            'lookalike_spec': json.dumps({'ratio': 0.01})}


def verify_seed(row):
    rule = row.get('rule', {})
    if isinstance(rule, str):
        rule = json.loads(rule)
    # A API pode serializar o ID do pixel como número no JSON da regra.
    def normalize(value):
        if isinstance(value, dict):
            return {k: str(v) if k == 'id' else normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [normalize(v) for v in value]
        return value
    if (row.get('name') != QR_NAME or row.get('subtype') != 'WEBSITE'
            or str(row.get('account_id')) != AD_ACCOUNT or normalize(rule) != QR_RULE):
        raise RuntimeError('Público QR com definição divergente; preservado sem alteração.')
    return row['id']


def verify_similar(row, seed):
    spec = row.get('lookalike_spec', {})
    origins = spec.get('origin', [])
    if (row.get('name') != QR_LOOKALIKE or row.get('subtype') != 'LOOKALIKE'
            or str(row.get('account_id')) != AD_ACCOUNT or spec.get('ratio') != 0.01
            or len(origins) != 1 or str(origins[0].get('id')) != seed):
        raise RuntimeError('Semelhante QR com definição divergente; preservado sem alteração.')


def inventory(client):
    account = client.request('act_' + AD_ACCOUNT, {'fields':
        'id,adspixels{id,name},customaudiences.limit(100){' + FIELDS + '}'})
    if account.get('id') != 'act_' + AD_ACCOUNT:
        raise RuntimeError('Conta de destino divergente.')
    pixels = account.get('adspixels', {}).get('data', [])
    if not any(p.get('id') == QR_PIXEL and p.get('name') == 'Sir Fisher - Website' for p in pixels):
        raise RuntimeError('Pixel esperado não confirmado na conta de destino.')
    audience_data = account.get('customaudiences', {})
    if audience_data.get('paging', {}).get('next'):
        raise RuntimeError('Inventário incompleto; não criar públicos sem conferir todas as páginas.')
    rows = audience_data.get('data', [])
    result = {}
    for name in (QR_NAME, QR_LOOKALIKE):
        matching = [r for r in rows if r.get('name') == name]
        if len(matching) > 1:
            raise RuntimeError('Público duplicado; nenhuma criação.')
        result[name] = matching[0] if matching else None
    if result[QR_NAME]:
        seed = verify_seed(result[QR_NAME])
        if result[QR_LOOKALIKE]:
            verify_similar(result[QR_LOOKALIKE], seed)
    elif result[QR_LOOKALIKE]:
        raise RuntimeError('Semelhante existente sem a origem esperada; conferir antes de criar.')
    return result


def prepare(client, apply=False, checkpoint=None):
    existing = inventory(client)
    if not apply:
        return {'state': 'preview', 'website': existing[QR_NAME] or website_params(),
                'lookalike': existing[QR_LOOKALIKE] or similar_params('<ID DO PÚBLICO QR VALIDADO>')}
    permissions = client.request('me/permissions', {'limit': 100})
    if not any(p.get('permission') == 'ads_management' and p.get('status') == 'granted'
               for p in permissions.get('data', [])):
        raise RuntimeError('Permissão ads_management não confirmada; nenhuma criação.')
    result = {'state': 'preparing', 'website': existing[QR_NAME], 'lookalike': existing[QR_LOOKALIKE]}
    if not result['website']:
        created = client.request('act_' + AD_ACCOUNT + '/customaudiences', website_params(), write=True)
        # Guarda o ID antes da releitura: falha de rede nunca autoriza repetir POST.
        result['website'] = created
        if checkpoint:
            checkpoint(result)
        if not str(created.get('id', '')).isdigit():
            raise RuntimeError('Criação retornou ID inesperado; conferir inventário antes de repetir.')
        result['website'] = client.request(created['id'], {'fields': FIELDS})
    seed = verify_seed(result['website'])
    client.verified_qr_seed = seed
    if checkpoint:
        checkpoint(result)
    if not result['lookalike']:
        try:
            created = client.request('act_' + AD_ACCOUNT + '/customaudiences', similar_params(seed), write=True)
        except RuntimeError as error:
            result.update(state='website_verified_lookalike_pending', reason=str(error))
            return result
        result['lookalike'] = created
        if checkpoint:
            checkpoint(result)
        if not str(created.get('id', '')).isdigit():
            raise RuntimeError('Semelhante retornou ID inesperado; conferir inventário antes de repetir.')
        result['lookalike'] = client.request(created['id'], {'fields': FIELDS})
    verify_similar(result['lookalike'], seed)
    result['state'] = 'created_or_existing_and_verified'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    client = Meta()
    def save(data):
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(sanitize(data, client.token), ensure_ascii=False, indent=2), encoding='utf-8')
    result = prepare(client, args.aplicar, save)
    save(result)
    print(json.dumps(sanitize(result, client.token), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
