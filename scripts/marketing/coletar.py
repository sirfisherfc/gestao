"""Coleta limitada, persistente e privada. Nao publica nem responde comentarios."""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

from meta import Meta, IG, PAGE, AD_ACCOUNT
from portal import query, save_snapshot, verify_portal, ROOT

TZ = dt.timezone(dt.timedelta(hours=-3))


def metric_value(metric):
    if metric.get('status') != 'available':
        return None
    for response in metric.get('response') or []:
        total = response.get('total_value', {}).get('value')
        if isinstance(total, (int, float)) and not isinstance(total, bool):
            return total
        values = response.get('values', [])
        if len(values) == 1 and isinstance(values[0].get('value'), (int, float)):
            return values[0]['value']
    return None


def metrics_payload(envelope):
    stamps = [r['collected_at_utc'] for r in envelope['reads'] if r['endpoint'].endswith('/insights')]
    return {'metrics': [{**m, 'value': metric_value(m)} for m in envelope['data']],
        'reads': envelope['reads'], 'coverage': envelope['coverage'],
        'api_collected_from':min(stamps) if stamps else None,'api_collected_to':max(stamps) if stamps else None,
        'requested_window': envelope.get('requested_window'), 'api_version': envelope['api_version']}


def metrics_status(payload):
    available = sum(m.get('value') is not None for m in payload['metrics'])
    return 'unavailable' if not available else 'available' if available == len(payload['metrics']) else 'partial'


def ga_report(start, end):
    # Mesma conta de servico existente; nenhuma chave copiada ou SDK novo.
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or str(ROOT.parent / 'site/tools/analytics/service_account.json'),
        scopes=['https://www.googleapis.com/auth/analytics.readonly'])
    client = BetaAnalyticsDataClient(credentials=creds)
    result = client.run_report(request={'property': 'properties/353205396',
        'date_ranges': [{'start_date': start, 'end_date': end}],
        'dimensions': [{'name': x} for x in ['hostName','sessionSourceMedium','sessionCampaignName','sessionManualAdContent','eventName']],
        'metrics': [{'name': 'eventCount'}], 'limit': 10000,
        'dimension_filter': {'and_group': {'expressions': [
            {'filter': {'field_name': 'hostName','string_filter': {'match_type': 'EXACT','value': 'reservas.sirfisher.com.br'}}},
            {'filter': {'field_name': 'eventName','in_list_filter': {'values': ['reservation_confirmed','visit_realized']}}}
        ]}}}, retry=None, timeout=30)
    names = [h.name for h in result.dimension_headers]
    rows = [{**dict(zip(names,[v.value for v in row.dimension_values])),
        'events': int(row.metric_values[0].value)} for row in result.rows]
    return {'rows': rows, 'truncated': result.row_count > len(rows),
        'subject_to_thresholding': bool(result.metadata.subject_to_thresholding),
        'data_loss_from_other_row': bool(result.metadata.data_loss_from_other_row),
        'timezone': result.metadata.time_zone,
        'coverage': 'Eventos medidos no portal por data do evento; nao sao a coorte de reservas nem credito Meta.'}


def collect(start, end, *, insights_limit=20):
    verify_portal()
    meta = Meta()
    identity = meta.identity
    permissions = meta.permissions()
    access = {'identity': identity, 'permissions': permissions,'ad_account_id_requested': AD_ACCOUNT}
    for key, reader in [('page',meta.pages),('publishing_limit',lambda: meta.request(IG+'/content_publishing_limit', {'fields':'quota_usage,config'}))]:
        try: access[key] = reader()
        except RuntimeError as error: access[key] = {'reason':str(error)}
    save_snapshot('access', IG, start, end, access,'partial' if any('reason' in access[k] for k in ['page','publishing_limit']) else 'available')
    days = (dt.date.fromisoformat(end)-dt.date.fromisoformat(start)).days+1
    for finish in [dt.date.fromisoformat(end),dt.date.fromisoformat(start)-dt.timedelta(days=1)]:
        begin = finish-dt.timedelta(days=days-1)
        account = meta.analytics.account_insights(days=days,end_date=finish.isoformat())
        payload = {**metrics_payload(account),'identity': identity}
        save_snapshot('instagram_account',IG,begin.isoformat(),finish.isoformat(),payload,metrics_status(payload))
    media = meta.analytics.media(days=days,end_date=end,max_pages=4,page_size=50)
    stories = meta.analytics.stories()
    # Cada ferramenta preserva seu limite de 60 leituras e o cache compartilhado.
    from scripts.instagram_analytics.client import InstagramAnalytics
    for kind, listing in [('instagram_media',media),('instagram_story',stories)]:
        selected = listing['data'][:insights_limit]
        entries = []
        for item in listing['data']:
            entry = {k: item[k] for k in ['id','media_type','media_product_type','caption','timestamp','permalink'] if k in item}
            if item in selected:
                analytics = InstagramAnalytics()
                reel_metrics = ['reach','views','total_interactions','likes','comments','saved','shares','ig_reels_avg_watch_time','ig_reels_video_view_total_time'] if item.get('media_product_type')=='REELS' else None
                insight = analytics.media_insights(item['id'],metrics=reel_metrics)
                entry['insights'] = metrics_payload(insight)
            entries.append(entry)
        save_snapshot(kind,IG,start,end,{'items':entries,'coverage':listing['coverage'],
            'pagination_truncated':listing['pagination_truncated'],
            'api_list_reads':listing['reads'],'insights_limit':insights_limit,'listed_count':len(entries),
            'insights_collected':len(selected)},
            'partial' if listing['pagination_truncated'] or len(entries)>insights_limit or any(metrics_status(e['insights'])!='available' for e in entries if 'insights' in e) else 'available')
    try:
        account = meta.request('act_'+AD_ACCOUNT, {'fields':'id,name,currency,timezone_name,account_status'})
        if account.get('id') != 'act_'+AD_ACCOUNT:
            raise RuntimeError('Conta de anuncios divergente.')
        ads, truncated = meta.list_pages('act_'+AD_ACCOUNT+'/insights',
            {'fields':'account_id,campaign_id,campaign_name,ad_id,ad_name,spend,impressions,reach,clicks,actions,action_values,date_start,date_stop',
             'level':'ad','time_range':json.dumps({'since':start,'until':end}),
             'use_account_attribution_setting':'true','limit':100},limit=5)
        save_snapshot('meta_ads',AD_ACCOUNT,start,end,{'account':account,'rows':ads,
            'truncated':truncated,'attribution':'Configuracao de atribuicao da conta; acoes creditadas pela Meta.',
            'coverage':'Gasto e acoes por anuncio no periodo Meta; nao somar alcance como pessoas unicas.'},
            'partial' if truncated else 'available')
    except RuntimeError as error:
        save_snapshot('meta_ads',AD_ACCOUNT,start,end,{'reason':str(error),'requested_account':AD_ACCOUNT},'unavailable')
    try:
        ga = ga_report(start,end)
        save_snapshot('ga4','353205396',start,end,ga,'partial' if ga['truncated'] or ga['subject_to_thresholding'] or ga['data_loss_from_other_row'] else 'available')
    except Exception:
        save_snapshot('ga4','353205396',start,end,
            {'reason':'Consulta GA4 indisponivel neste ambiente; usar Python privado do Analytics e credencial existente.'},'unavailable')
    comment_count = 0
    failures = []
    for network, items in [('instagram',media['data'])]:
        if not permissions.get('instagram_manage_comments'):
            failures.append('Permissao de comentarios Instagram ausente.')
            continue
        for item in items[:20]:
            try:
                comments, truncated = meta.list_pages(item['id']+'/comments', {'fields':'id,text,timestamp','limit':50},limit=2)
                for comment in comments:
                    save_comment(network,item['id'],item.get('permalink'),comment)
                comment_count += len(comments)
                if truncated:
                    failures.append('Comentarios Instagram com paginacao parcial.')
            except RuntimeError as error:
                failures.append(str(error))
    try:
        # feed usa token da Pagina; rota fixa abaixo, sem alterar estado.
        posts_result = meta.request(PAGE,{'fields':'posts.limit(20){id,permalink_url,created_time}'},page=True)
        posts_data = posts_result.get('posts',{})
        if posts_data.get('paging',{}).get('next'):
            failures.append('Facebook: primeiras 20 publicacoes; cobertura parcial.')
        for item in posts_data.get('data',[]):
            stamp = dt.datetime.fromisoformat(item['created_time']).astimezone(TZ).date()
            if not dt.date.fromisoformat(start)<=stamp<=dt.date.fromisoformat(end):
                continue
            result = meta.request(item['id']+'/comments',{'fields':'id,message,created_time','limit':100},page=True)
            for comment in result.get('data',[]):
                save_comment('facebook',item['id'],item.get('permalink_url'),
                    {'id':comment['id'],'text':comment.get('message',''),'timestamp':comment.get('created_time')})
                comment_count += 1
            if result.get('paging',{}).get('next'):
                failures.append('Comentarios Facebook com paginacao parcial.')
    except RuntimeError as error:
        failures.append('Facebook: '+str(error))
    save_snapshot('access','comments',start,end,{'collected_count':comment_count,'limitations':failures,
        'coverage':'Comentarios nas primeiras 20 publicacoes proprias do periodo. Respostas em subthreads nao coletadas; sem autores. Revisao humana.'},
        'partial' if failures else 'available')
    return {'start':start,'end':end,'media_count':len(media['data']),'stories_count':len(stories['data']),
        'comments_collected':comment_count,'comments_partial':bool(failures)}


def save_comment(network,media_id,url,comment):
    query('''insert into public.marketing_comments(id,network,media_id,media_url,body,posted_at)
      values($1,$2,$3,$4,$5,$6::timestamptz) on conflict(id) do update
      set body=excluded.body,collected_at=now()''',
      [comment['id'],network,media_id,url,comment.get('text','')[:20000],comment.get('timestamp')],write=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dias',type=int,default=30)
    parser.add_argument('--ate',type=dt.date.fromisoformat)
    args=parser.parse_args()
    if not 1<=args.dias<=30:
        parser.error('Use 1 a 30 dias.')
    end=args.ate or dt.datetime.now(TZ).date()-dt.timedelta(days=2)
    start=end-dt.timedelta(days=args.dias-1)
    if end>dt.datetime.now(TZ).date()-dt.timedelta(days=2) or start-dt.timedelta(days=args.dias)<dt.datetime.now(TZ).date()-dt.timedelta(days=89):
        parser.error('Periodo consolidado e comparacao precisam caber nos ultimos 90 dias.')
    try:
        print(json.dumps(collect(start.isoformat(),end.isoformat()),ensure_ascii=True))
    except Exception:
        raise SystemExit('Coleta interrompida; conferir acesso e estado privado. Nenhum segredo exibido.') from None
