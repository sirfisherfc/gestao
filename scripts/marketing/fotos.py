"""Prepara fotos proprias para revisao privada, sem publicar material."""
import datetime as dt
import hashlib
import io
import json
import urllib.request

from meta import Meta
from portal import ROOT,save_snapshot,verify_portal
from scripts.gbp import gbp


def prepare():
    from PIL import Image
    verify_portal()
    Meta()  # Confirma @sirfisherfc antes de ler fotos, incluindo carrosseis.
    hashes=gbp.hashes_publicados(exigir_completo=True)+gbp.hashes_descartados()
    folder=ROOT/'tmp/gbp/instagram';folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    for photo in gbp.fotos_instagram(30):
        with urllib.request.urlopen(urllib.request.Request(photo['url'],headers={'User-Agent':'SirFisher/1.0'}),timeout=30) as response:
            data=response.read(5*1024*1024+1)
        if len(data)>5*1024*1024:
            continue
        image=Image.open(io.BytesIO(data)); image.load()
        path=folder/(photo['id']+'.jpg'); path.write_bytes(data)
        duplicate=gbp.parecida(gbp.dhash(image),hashes)
        rows.append({'id':photo['id'],'permalink':photo['post'],'date':photo['data'],
            'width':image.width,'height':image.height,'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest(),'duplicate':bool(duplicate),
            'technical_quality':image.format in {'JPEG','PNG'} and min(image.size)>=400 and len(data)>=10240,
            'review':'Revisar foco, luz, direito de uso e aprovacao do proprietario.'})
    today=dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date()
    save_snapshot('google_photos','candidates',(today-dt.timedelta(days=29)).isoformat(),today.isoformat(),
        {'items':rows,'coverage':'Fotos proprias listadas nos ultimos 30 dias; arquivos privados em tmp/gbp/instagram. Duplicidade conferida com a ficha atual.'})
    return {'prepared':len(rows),'duplicates':sum(r['duplicate'] for r in rows),'published':0}


if __name__=='__main__':
    try: print(json.dumps(prepare()))
    except Exception:
        raise SystemExit('Preparacao interrompida; conferir acesso Google, Meta e duplicidade. Nada publicado.') from None
