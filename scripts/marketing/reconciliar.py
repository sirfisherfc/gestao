"""Rele envios iniciados/incertos; nao publica nem repete POSTs."""
import datetime as dt
import json

from executar import set_state
from meta import Meta
from portal import query,verify_portal


def run():
    verify_portal()
    rows=query("select * from public.marketing_editorial where status in ('sending','uncertain') order by updated_at limit 50")
    confirmed=0
    for item in rows:
        if item.get('provider_id'):
            try:
                if item['target']=='google_photo':
                    from scripts.gbp import gbp
                    name=item['provider_id']
                    if not name.startswith(f'{gbp.CONTA}/{gbp.LOCAL}/media/'):
                        continue
                    check=gbp.api('GET',f'{gbp.V4}/{name}')
                    ok=check.get('name')==name
                    url=None
                else:
                    meta=Meta()
                    if item['target']=='facebook': meta.pages()
                    fields='id,permalink' if item['target']=='instagram' else 'id,permalink_url'
                    check=meta.request(item['provider_id'],{'fields':fields},page=item['target']=='facebook')
                    ok=check.get('id')==item['provider_id']
                    url=check.get('permalink') or check.get('permalink_url')
                if ok:
                    set_state(item,'published',provider_url=url,last_error=None)
                    confirmed+=1
            except Exception:
                pass
        elif item['status']=='sending' and dt.datetime.fromisoformat(item['updated_at'])<dt.datetime.now(dt.timezone.utc)-dt.timedelta(minutes=15):
            set_state(item,'uncertain',last_error='Execucao interrompida sem ID de publicacao. Conferir recibos privados e rede social; sem reenvio automatico.')
    return {'checked':len(rows),'confirmed':confirmed,'published_by_this_command':0}


if __name__=='__main__':
    try: print(json.dumps(run()))
    except Exception: raise SystemExit('Reconciliacao interrompida; nenhum envio repetido.') from None
