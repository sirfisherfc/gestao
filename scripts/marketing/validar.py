"""Confere o arquivo da revisao antes da aprovacao; sem publicacao."""
import hashlib
import io
import json
import urllib.request

from meta import Meta,NoRedirect
from portal import query,verify_portal


def media_bytes(item):
    if item['target']=='google_photo':
        Meta()
        from scripts.gbp import gbp
        photos=[p for p in gbp.fotos_instagram(30) if p['id']==item.get('source_media_id')]
        if len(photos)!=1: raise ValueError('Foto propria indisponivel na janela de 30 dias.')
        url=photos[0]['url']
    else:
        url=item['media_url']
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 SirFisher/1.0'})
    with urllib.request.build_opener(NoRedirect()).open(request,timeout=60) as response:
        data=response.read(100*1024*1024+1)
    if not data or len(data)>100*1024*1024:
        raise ValueError('Fluxo local aceita arquivo de ate 100 MB.')
    return data


def verify_bytes(item):
    data=media_bytes(item)
    if item['format'] in {'IMAGE','PHOTO'} or item['format']=='STORIES' and not (item.get('media_url') or '').lower().endswith('.mp4'):
        from PIL import Image
        img=Image.open(io.BytesIO(data));img.verify()
        if img.format not in ({'JPEG'} if item['target']=='instagram' else {'JPEG','PNG'}):
            raise ValueError('Formato de imagem indisponivel.')
        if item['target']=='instagram' and len(data)>8*1024*1024:
            raise ValueError('Imagem Instagram acima de 8 MB.')
        if item['target']=='google_photo' and (len(data)<10240 or len(data)>5*1024*1024 or min(img.size)<400):
            raise ValueError('Foto fora do tamanho aceito pelo fluxo Google.')
    return hashlib.sha256(data).hexdigest()


def prepare():
    verify_portal()
    rows=query("select * from public.marketing_editorial where status='review' and format<>'TEXT' order by updated_at limit 30")
    verified=0
    for item in rows:
        try: digest=verify_bytes(item)
        except Exception: continue
        result=query("update public.marketing_editorial set media_sha256=$2,verified_revision=revision where id=$1::uuid and revision=$3 and status='review' returning id",[item['id'],digest,item['revision']],write=True)
        verified+=len(result)
    return {'review_items':len(rows),'verified':verified,'pending':len(rows)-verified,'published':0}


if __name__=='__main__':
    try: print(json.dumps(prepare()))
    except Exception: raise SystemExit('Validacao interrompida; sem publicacao.') from None
