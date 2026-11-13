"""Impulsiona publicacoes proprias do Instagram como anuncios de trafego na Meta.

Contrato: conta do Portfolio (meta.AD_ACCOUNT), somente posicionamentos do
Instagram, orcamento total por item (teto fixo da Meta) com data de fim, soma
dentro do --teto informado e destino em pagina do site oficial. Cria campanha,
conjunto, criativo e anuncio, rele o resultado e grava recibo em tmp/meta-ads/.
Sem --ativar, tudo nasce pausado. Ativar gasta dinheiro: so com orcamento
aprovado pelo proprietario.

Uso: python scripts/marketing/impulsionar.py PLANO.json --teto 300 [--ativar]
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.marketing.meta import AD_ACCOUNT, IG, PAGE, Meta

RAIZ = Path(__file__).resolve().parents[2]
RECIBOS = RAIZ / 'tmp' / 'meta-ads'
HOSTS = {'www.sirfisher.com.br'}
# "explore" foi recusado pela API v26 em 13/11/2026 como posicionamento obsoleto.
POSICOES = ['stream', 'story', 'reels']
CTAS = {'LEARN_MORE', 'SEE_MENU', 'BOOK_NOW'}


def validar(plano, teto, agora=None):
    agora = agora or dt.datetime.now(dt.timezone.utc)
    itens = plano.get('itens') or []
    if not itens:
        raise ValueError('Plano vazio.')
    total = round(sum(float(i['orcamento_total']) for i in itens), 2)
    if total > float(teto):
        raise ValueError(f'Soma dos orcamentos R$ {total:.2f} passa do teto R$ {float(teto):.2f}.')
    for i in itens:
        if not str(i['media_id']).isdigit():
            raise ValueError('media_id invalido.')
        url = urlparse(i['link'])
        if url.scheme != 'https' or url.hostname not in HOSTS or url.query or url.fragment:
            raise ValueError('Link deve ser pagina do site, sem parametros; UTMs vao em url_tags.')
        if i['cta'] not in CTAS:
            raise ValueError('CTA fora da lista permitida.')
        if float(i['orcamento_total']) < 10:
            raise ValueError('Orcamento minimo por item: R$ 10.')
        fim = dt.datetime.fromisoformat(i['fim'])
        if fim.tzinfo is None:
            raise ValueError('fim precisa de fuso explicito, ex.: -03:00.')
        if not agora < fim <= agora + dt.timedelta(days=31):
            raise ValueError('fim deve ficar entre agora e 31 dias.')
    return total


def publico(i):
    lat, lng = i['centro']
    idade = i.get('idade', [21, 65])
    return {
        'geo_locations': {'custom_locations': [{'latitude': lat, 'longitude': lng,
                                                'radius': i.get('raio_km', 20), 'distance_unit': 'kilometer'}],
                          'location_types': ['home', 'recent']},
        'age_min': idade[0], 'age_max': idade[1],
        'publisher_platforms': ['instagram'], 'instagram_positions': POSICOES,
        'targeting_automation': {'advantage_audience': 0},
    }


def agenda(i):
    a = i.get('agenda')
    if not a:
        return {}
    minuto = lambda s: int(s[:2]) * 60 + int(s[3:5])
    # timezone_type USER: horario local de quem ve o anuncio (Fortaleza), nao o fuso da conta.
    return {'adset_schedule': json.dumps([{'start_minute': minuto(a['inicio']), 'end_minute': minuto(a['fim']),
                                           'days': a['dias'], 'timezone_type': 'USER'}]),
            'pacing_type': json.dumps(['day_parting'])}


def criar(m, i, status, feito):
    elegivel = m.analytics._get(str(i['media_id']), {'fields': 'boost_eligibility_info'}, 0, fresh=True)
    if not (elegivel.get('boost_eligibility_info') or {}).get('eligible_to_boost'):
        raise RuntimeError(f"Publicacao nao pode ser impulsionada: {elegivel.get('boost_eligibility_info')}")
    conta = f'act_{AD_ACCOUNT}'
    try:
        if i.get('campanha_id'):
            # Reaproveita campanha vazia criada por uma tentativa anterior deste comando.
            feito['campanha'] = str(i['campanha_id'])
            m.request(feito['campanha'], {'status': status}, write=True)
        else:
            feito['campanha'] = m.request(conta + '/campaigns', {
                'name': i['nome'], 'objective': 'OUTCOME_TRAFFIC', 'status': status, 'buying_type': 'AUCTION',
                'special_ad_categories': '[]', 'is_adset_budget_sharing_enabled': 'false'}, write=True)['id']
        feito['conjunto'] = m.request(conta + '/adsets', {
            'name': i['nome'] + ' | conjunto', 'campaign_id': feito['campanha'], 'status': status,
            'lifetime_budget': int(round(float(i['orcamento_total']) * 100)),
            'start_time': i.get('inicio') or dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
            'end_time': i['fim'], 'billing_event': 'IMPRESSIONS', 'optimization_goal': 'LINK_CLICKS',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP', 'destination_type': 'WEBSITE',
            'targeting': json.dumps(publico(i)), **agenda(i)}, write=True)['id']
        tags = (f"utm_source=instagram&utm_medium=paid_social&utm_campaign={i['utm_campaign']}"
                f"&utm_content=ig_{i['media_id']}&utm_id={{{{campaign.id}}}}")
        feito['criativo'] = m.request(conta + '/adcreatives', {
            'name': i['nome'] + ' | criativo', 'object_id': PAGE, 'instagram_user_id': IG,
            'source_instagram_media_id': str(i['media_id']), 'url_tags': tags,
            'call_to_action': json.dumps({'type': i['cta'], 'value': {'link': i['link']}})}, write=True)['id']
        feito['anuncio'] = m.request(conta + '/ads', {
            'name': i['nome'] + ' | anuncio', 'adset_id': feito['conjunto'], 'status': status,
            'creative': json.dumps({'creative_id': feito['criativo']})}, write=True)['id']
    except Exception:
        if feito.get('campanha'):
            m.request(feito['campanha'], {'status': 'PAUSED'}, write=True)
            feito['pausada_por_erro'] = True
        raise
    feito['leitura'] = m.request(feito['anuncio'], {'fields': (
        'effective_status,configured_status,preview_shareable_link,'
        'adset{lifetime_budget,start_time,end_time,effective_status},campaign{effective_status}')})
    return feito


def main(argv=None):
    p = argparse.ArgumentParser(description='Impulsiona posts do Instagram (trafego para o site).')
    p.add_argument('plano', type=Path)
    p.add_argument('--teto', type=float, required=True, help='Soma maxima dos orcamentos, em reais.')
    p.add_argument('--ativar', action='store_true', help='Cria ativo; sem isso, pausado.')
    a = p.parse_args(argv)
    plano = json.loads(a.plano.read_text(encoding='utf-8'))
    total = validar(plano, a.teto)
    m = Meta()
    conta = m.request(f'act_{AD_ACCOUNT}', {'fields': 'currency,account_status,user_tasks'})
    if conta.get('currency') != 'BRL' or conta.get('account_status') != 1 or 'ADVERTISE' not in (conta.get('user_tasks') or []):
        sys.exit('Conta de anuncios sem condicao de anunciar por este acesso.')
    status = 'ACTIVE' if a.ativar else 'PAUSED'
    RECIBOS.mkdir(parents=True, exist_ok=True)
    arquivo = RECIBOS / f'impulsionar-{dt.datetime.now():%Y%m%dT%H%M%S}.json'
    recibo = {'quando': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'teto': a.teto,
              'total_orcado': total, 'status_pedido': status, 'itens': []}
    try:
        for item in plano['itens']:
            feito = {'nome': item['nome'], 'media_id': str(item['media_id']), 'orcamento_total': item['orcamento_total']}
            recibo['itens'].append(feito)
            criar(m, item, status, feito)
    finally:
        arquivo.write_text(json.dumps(recibo, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(recibo, ensure_ascii=False, indent=2))
        print('Recibo:', arquivo)


if __name__ == '__main__':
    main()
