"""Teste fixo Meta: aberto x semelhante QR, 7 dias, mídia R$260, teto R$300.

Prévia sem escrita por padrão. --preparar cria tudo pausado e valida.
--ativar exige recibo validado; não cria entidades nem muda orçamento.
--relatorio consulta resultados, sem alterar campanhas.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import parse_qs

from meta import Meta, AD_ACCOUNT, IG, PAGE, QR_PIXEL, QR_BUSINESS, QR_STUDY_NAME, sanitize

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / 'tmp/teste-publicos-qr-2026-11-25/recibo.json'
SEED = '120255101123660120'
SIMILAR = '120255101123670120'
MEDIA = '18113719193582226'
LINK = 'https://www.sirfisher.com.br/conheca/'
START = '2026-11-26T09:00:00-03:00'
END = '2026-12-03T09:00:00-03:00'
CAMPAIGN_NAMES = {'A': 'SF | Teste QR 26nov2026 | A Aberto',
                  'B': 'SF | Teste QR 26nov2026 | B Semelhante QR'}
UTMS = {'A': 'teste_qr_aberto_20261126', 'B': 'teste_qr_semelhante_20261126'}
ADSET_FIELDS = ('id,name,account_id,campaign_id,status,effective_status,lifetime_budget,start_time,end_time,'
                'optimization_goal,billing_event,destination_type,targeting,targeting_optimization_types,promoted_object')
AD_FIELDS = 'id,name,account_id,status,effective_status,adset_id,preview_shareable_link,creative{id,name,source_instagram_media_id,url_tags,call_to_action_type,effective_object_story_id,object_story_spec,object_url}'


def timestamp(value):
    if isinstance(value, (int, float)) or str(value).isdigit():
        return int(value)
    return int(dt.datetime.fromisoformat(value).timestamp())


def targeting(arm):
    result = {'geo_locations': {'custom_locations': [{
        'latitude': -3.7247085, 'longitude': -38.4906542, 'radius': 20, 'distance_unit': 'kilometer'}],
        'location_types': ['home', 'recent']}, 'age_min': 21, 'age_max': 65,
        'publisher_platforms': ['instagram'], 'instagram_positions': ['stream', 'story', 'reels'],
        'targeting_automation': {'advantage_audience': 0},
        'targeting_relaxation_types': {'lookalike': 0, 'custom_audience': 0},
        'excluded_custom_audiences': [{'id': SEED}]}
    if arm == 'B':
        result['custom_audiences'] = [{'id': SIMILAR}]
    return result


def tags(arm):
    return ('utm_source=instagram&utm_medium=paid_social&utm_campaign=' + UTMS[arm]
            + '&utm_content=ig_' + MEDIA + '&utm_id={{campaign.id}}')


def campaign_params(arm):
    return {'name': CAMPAIGN_NAMES[arm], 'objective': 'OUTCOME_TRAFFIC', 'status': 'PAUSED',
            'buying_type': 'AUCTION', 'special_ad_categories': '[]', 'is_adset_budget_sharing_enabled': 'false'}


def adset_params(arm, campaign):
    return {'name': CAMPAIGN_NAMES[arm] + ' | conjunto', 'campaign_id': campaign, 'status': 'PAUSED',
            'lifetime_budget': 13000, 'start_time': START, 'end_time': END,
            'billing_event': 'IMPRESSIONS', 'optimization_goal': 'LANDING_PAGE_VIEWS',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP', 'destination_type': 'WEBSITE',
            'targeting': json.dumps(targeting(arm))}


def creative_params(arm):
    return {'name': CAMPAIGN_NAMES[arm] + ' | criativo', 'object_id': PAGE, 'instagram_user_id': IG,
            'source_instagram_media_id': MEDIA, 'url_tags': tags(arm),
            'call_to_action': json.dumps({'type': 'LEARN_MORE', 'value': {'link': LINK}})}


def study_params(campaigns):
    return {'name': QR_STUDY_NAME, 'type': 'SPLIT_TEST',
            'description': 'Somente público varia. Mesmo reel, destino, janela e R$130 por grupo; métrica principal custo por landing page view.',
            'start_time': timestamp(START), 'end_time': timestamp(END),
            'cells': json.dumps([{'name': 'A | Aberto', 'treatment_percentage': 50, 'campaigns': [campaigns[0]]},
                                 {'name': 'B | Semelhante QR', 'treatment_percentage': 50, 'campaigns': [campaigns[1]]}])}


def plan():
    return {'approved_total_brl': 300, 'media_total_brl': 260, 'reserve_brl': 40,
            'start_fortaleza': START, 'end_fortaleza': END, 'primary_metric': 'cost_per_landing_page_view',
            'media_id': MEDIA, 'destination': LINK,
            'arms': {a: {'campaign': campaign_params(a), 'adset': adset_params(a, '<nova campanha>'),
                         'creative': creative_params(a)} for a in ('A', 'B')}}


def preflight(client):
    account = client.request('act_' + AD_ACCOUNT, {'fields':
        'id,currency,account_status,user_tasks,business{id,name},adspixels{id,name},'
        'customaudiences.limit(100){id,name,subtype,delivery_status,lookalike_spec}'})
    if (account.get('id') != 'act_' + AD_ACCOUNT or account.get('currency') != 'BRL'
            or account.get('account_status') != 1 or 'ADVERTISE' not in account.get('user_tasks', [])
            or account.get('business', {}).get('id') != QR_BUSINESS):
        raise RuntimeError('Conta, moeda, acesso ou Portfólio divergente.')
    if not any(p.get('id') == QR_PIXEL for p in account.get('adspixels', {}).get('data', [])):
        raise RuntimeError('Pixel não confirmado na conta.')
    audiences = {r['id']: r for r in account.get('customaudiences', {}).get('data', [])}
    if SEED not in audiences or SIMILAR not in audiences:
        raise RuntimeError('Públicos QR não confirmados.')
    spec = audiences[SIMILAR].get('lookalike_spec', {})
    if (spec.get('ratio') != 0.01 or [str(x.get('id')) for x in spec.get('origin', [])] != [SEED]
            or audiences[SIMILAR].get('delivery_status', {}).get('code') != 200):
        raise RuntimeError('Semelhante divergente ou indisponível.')
    media = client.request(MEDIA, {'fields': 'id,boost_eligibility_info,permalink,caption'})
    if not media.get('boost_eligibility_info', {}).get('eligible_to_boost'):
        raise RuntimeError('Reel não elegível para impulsionamento.')
    return {'account_id': AD_ACCOUNT, 'business_id': QR_BUSINESS, 'media': media, 'audiences': audiences}


def verify_arm(client, arm, ids, expected_status):
    campaign = client.request(ids['campaign'], {'fields': 'id,name,account_id,objective,status'})
    adset = client.request(ids['adset'], {'fields': ADSET_FIELDS})
    ad = client.request(ids['ad'], {'fields': AD_FIELDS})
    if any(str(x.get('account_id')) != AD_ACCOUNT for x in (campaign, adset, ad)):
        raise RuntimeError('Entidade em conta divergente.')
    if (campaign.get('name') != CAMPAIGN_NAMES[arm] or campaign.get('objective') != 'OUTCOME_TRAFFIC'
            or any(x.get('status') != expected_status for x in (campaign, adset, ad))
            or adset.get('campaign_id') != ids['campaign'] or ad.get('adset_id') != ids['adset']):
        raise RuntimeError('Hierarquia ou status divergentes.')
    if (int(adset.get('lifetime_budget', 0)) != 13000
            or timestamp(adset['start_time']) != timestamp(START) or timestamp(adset['end_time']) != timestamp(END)
            or adset.get('optimization_goal') != 'LANDING_PAGE_VIEWS'
            or adset.get('destination_type') != 'WEBSITE'):
        raise RuntimeError('Orçamento, janela ou objetivo divergente.')
    if adset.get('promoted_object', {}).get('pixel_id') not in (None, QR_PIXEL):
        raise RuntimeError('Pixel inesperado no objeto promovido.')
    actual = adset.get('targeting', {})
    if ([str(x.get('id')) for x in actual.get('custom_audiences', [])] != ([SIMILAR] if arm == 'B' else [])
            or [str(x.get('id')) for x in actual.get('excluded_custom_audiences', [])] != [SEED]
            or actual.get('age_min') != 21 or actual.get('age_max') != 65
            or actual.get('targeting_automation', {}).get('advantage_audience') != 0
            or actual.get('publisher_platforms') != ['instagram']
            or sorted(actual.get('instagram_positions', [])) != ['reels', 'story', 'stream']):
        raise RuntimeError('Público, expansão ou posicionamentos divergentes.')
    locations = actual.get('geo_locations', {}).get('custom_locations', [])
    if (len(locations) != 1 or float(locations[0].get('radius', 0)) != 20
            or locations[0].get('distance_unit') != 'kilometer'
            or abs(float(locations[0].get('latitude', 0)) + 3.7247085) > 0.00001
            or abs(float(locations[0].get('longitude', 0)) + 38.4906542) > 0.00001):
        raise RuntimeError('Região divergente.')
    if (any(int(x.get('value', 0)) != 0 for x in adset.get('targeting_optimization_types', [])
            if x.get('key') in {'lookalike', 'custom_audience'})
            or any(int(v) != 0 for k, v in actual.get('targeting_relaxation_types', {}).items()
                   if k in {'lookalike', 'custom_audience'})):
        raise RuntimeError('Expansão de público ativa; teste não isolado.')
    creative = ad.get('creative', {})
    if (creative.get('id') != ids['creative'] or creative.get('source_instagram_media_id') != MEDIA
            or creative.get('call_to_action_type') != 'LEARN_MORE'
            or parse_qs(creative.get('url_tags', '')) != parse_qs(tags(arm))):
        raise RuntimeError('Reel, CTA ou atribuição divergente.')
    return {'campaign': campaign, 'adset': adset, 'ad': ad}


def verify_study(client, receipt):
    study = client.request(receipt['study'], {'fields': 'id,name,type,start_time,end_time,cells{id,name,treatment_percentage,campaigns},objectives{id,name,type}'})
    if (study.get('name') != QR_STUDY_NAME or study.get('type') != 'SPLIT_TEST'
            or timestamp(study.get('start_time', 0)) != timestamp(START)
            or timestamp(study.get('end_time', 0)) != timestamp(END)):
        raise RuntimeError('Experimento com nome, tipo ou janela divergente.')
    cells = study.get('cells', {}).get('data', [])
    for arm, cell_name in [('A', 'A | Aberto'), ('B', 'B | Semelhante QR')]:
        matches = [c for c in cells if c.get('name') == cell_name]
        if len(matches) != 1 or float(matches[0].get('treatment_percentage', 0)) != 50:
            raise RuntimeError('Divisão aleatória do experimento não confirmada.')
        campaigns = matches[0].get('campaigns', [])
        if isinstance(campaigns, dict):
            campaigns = campaigns.get('data', [])
        campaign_ids = [str(c.get('id')) if isinstance(c, dict) else str(c) for c in campaigns]
        if campaign_ids != [receipt['arms'][arm]['campaign']]:
            raise RuntimeError('Campanhas das células divergentes.')
    return study


def create(client, receipt, save):
    if receipt.get('state') == 'active_scheduled_verified':
        raise RuntimeError('Teste já ativado; consultar --relatorio, sem recriar ou mudar seu estado.')
    if receipt.get('pending'):
        raise RuntimeError('Mutação anterior sem resposta: conferir inventário e recibo antes de repetir.')
    if timestamp(START) <= dt.datetime.now(dt.timezone.utc).timestamp():
        raise RuntimeError('Início do teste já passou; não reaproveitar plano vencido.')
    receipt['preflight'] = preflight(client)
    receipt['plan'] = plan()
    receipt.setdefault('arms', {'A': {}, 'B': {}})
    def post(path, params, owner, key):
        if owner.get(key):
            return
        receipt['pending'] = {'path': path, 'params': params}
        save(receipt)
        response = client.request(path, params, write=True)
        if not str(response.get('id', '')).isdigit():
            raise RuntimeError('Resposta de criação sem ID válido; conferir antes de repetir.')
        owner[key] = response['id']
        receipt.pop('pending')
        save(receipt)
    account = 'act_' + AD_ACCOUNT
    try:
        for arm in ('A', 'B'):
            ids = receipt['arms'][arm]
            post(account + '/campaigns', campaign_params(arm), ids, 'campaign')
            post(account + '/adsets', adset_params(arm, ids['campaign']), ids, 'adset')
            post(account + '/adcreatives', creative_params(arm), ids, 'creative')
            post(account + '/ads', {'name': CAMPAIGN_NAMES[arm] + ' | anúncio', 'adset_id': ids['adset'],
                 'status': 'PAUSED', 'creative': json.dumps({'creative_id': ids['creative']})}, ids, 'ad')
        receipt['paused_readback'] = {a: verify_arm(client, a, receipt['arms'][a], 'PAUSED') for a in ('A', 'B')}
        campaigns = [receipt['arms'][a]['campaign'] for a in ('A', 'B')]
        client.verified_split_campaigns = campaigns
        post(QR_BUSINESS + '/ad_studies', study_params(campaigns), receipt, 'study')
        receipt['study_readback'] = verify_study(client, receipt)
        receipt['state'] = 'prepared_paused_verified'
        save(receipt)
    except Exception:
        receipt['state'] = 'preparation_failed_paused'
        save(receipt)
        raise
    return receipt


def activate(client, receipt, save):
    if receipt.get('state') != 'prepared_paused_verified' or receipt.get('pending'):
        raise RuntimeError('Somente o teste pausado e completamente validado pode ser ativado.')
    if receipt.get('plan') != plan() or timestamp(START) <= dt.datetime.now(dt.timezone.utc).timestamp():
        raise RuntimeError('Plano alterado ou início vencido; ativação bloqueada.')
    if receipt.get('destination_verified') != {'A': LINK, 'B': LINK}:
        raise RuntimeError('Conferir o destino real dos dois CTAs no Gerenciador antes de ativar.')
    preflight(client)
    for arm in ('A', 'B'):
        verify_arm(client, arm, receipt['arms'][arm], 'PAUSED')
    verify_study(client, receipt)
    try:
        for level in ('ad', 'adset', 'campaign'):
            for arm in ('A', 'B'):
                client.request(receipt['arms'][arm][level], {'status': 'ACTIVE'}, write=True)
        receipt['active_readback'] = {a: verify_arm(client, a, receipt['arms'][a], 'ACTIVE') for a in ('A', 'B')}
        receipt['state'] = 'active_scheduled_verified'
        save(receipt)
    except Exception:
        receipt['rollback'] = []
        for arm in ('A', 'B'):
            try:
                client.request(receipt['arms'][arm]['campaign'], {'status': 'PAUSED'}, write=True)
                receipt['rollback'].append(arm)
            except Exception:
                pass
        receipt['state'] = 'activation_failed_check_status'
        save(receipt)
        raise
    return receipt


def summarize(rows):
    """Soma entrega, mas não alcance/usuários únicos por dia."""
    spend = round(sum(float(r.get('spend', 0)) for r in rows), 2)
    has_actions = any('actions' in r for r in rows)
    views = sum(float(a.get('value', 0)) for r in rows for a in r.get('actions', [])
                if a.get('action_type') == 'landing_page_view') if has_actions else None
    return {'spend_brl': spend, 'impressions': sum(int(r.get('impressions', 0)) for r in rows),
            'link_clicks': sum(int(r.get('inline_link_clicks', 0)) for r in rows),
            'landing_page_views_reported': views,
            'cost_per_landing_page_view_brl': round(spend / views, 4) if views else None,
            'coverage': 'Resultados medidos pela Meta; ausência de ações não comprova ausência de visitas reais.'}


def report(client, receipt, until):
    start = '2026-11-26'
    if until < start:
        return {'state': 'not_started', 'start': START, 'end': END}
    result = {'start': start, 'end': until, 'timezone': 'Meta America/Noronha; confrontar GA4 America/Fortaleza', 'arms': {}}
    for arm, ids in receipt['arms'].items():
        response = client.request(ids['adset'] + '/insights', {'fields':
            'date_start,date_stop,spend,impressions,reach,inline_link_clicks,actions',
            'time_range': json.dumps({'since': start, 'until': until}), 'time_increment': 1, 'limit': 100})
        rows = response.get('data', [])
        result['arms'][arm] = {'rows': rows, 'summary': summarize(rows),
                               'has_more': bool(response.get('paging', {}).get('next'))}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--preparar', action='store_true')
    actions.add_argument('--ativar', action='store_true')
    actions.add_argument('--relatorio', action='store_true')
    parser.add_argument('--ate', default=dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date().isoformat())
    args = parser.parse_args()
    if not any((args.preparar, args.ativar, args.relatorio)):
        print(json.dumps(plan(), ensure_ascii=False, indent=2)); return
    client = Meta()
    receipt = json.loads(RECEIPT.read_text(encoding='utf-8')) if RECEIPT.exists() else {}
    def save(data):
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(sanitize(data, client.token), ensure_ascii=False, indent=2), encoding='utf-8')
    if args.relatorio:
        result = report(client, receipt, args.ate)
    elif args.ativar:
        result = activate(client, receipt, save)
    else:
        result = create(client, receipt, save)
    print(json.dumps(sanitize(result, client.token), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError) as error:
        raise SystemExit(str(error)) from None
