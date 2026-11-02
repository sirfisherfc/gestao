"""Previa por padrao; --enviar executa somente revisoes e datas aprovadas."""
import argparse
import contextlib
import datetime as dt
import io
import json
import re
import time
from types import SimpleNamespace
from urllib.parse import urlparse

from meta import Meta, IG, PAGE
from portal import query, verify_portal, ROOT


def validate(item, owner_id, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if not owner_id or item.get('approved_by') != owner_id or item.get('approved_revision') != item.get('revision'):
        raise ValueError('Aprovacao da revisao pelo proprietario ausente.')
    if not item.get('rights_confirmed') or not item.get('quality_confirmed'):
        raise ValueError('Direito de uso ou qualidade sem confirmacao.')
    scheduled = dt.datetime.fromisoformat(item['scheduled_at'].replace('Z','+00:00'))
    if not scheduled <= now <= scheduled + dt.timedelta(hours=1):
        raise ValueError('Horario fora da janela aprovada de envio (ate uma hora).')
    target, format_ = item['target'],item['format']
    if format_ not in {'instagram':{'IMAGE','REELS','STORIES'},'facebook':{'TEXT','PHOTO'},'google_photo':{'PHOTO'}}.get(target,set()):
        raise ValueError('Formato indisponivel neste fluxo.')
    if format_ == 'TEXT' and not item.get('caption','').strip():
        raise ValueError('Texto vazio.')
    if target == 'google_photo':
        if not re.fullmatch(r'\d{5,30}',item.get('source_media_id') or ''):
            raise ValueError('Foto propria sem ID confirmado.')
    elif format_ != 'TEXT':
        url = urlparse(item.get('media_url') or '')
        if url.scheme!='https' or url.netloc not in {'www.sirfisher.com.br','sirfisher.com.br'} or url.query or url.fragment or not re.fullmatch(r'/[A-Za-z0-9_./%~-]+',url.path):
            raise ValueError('Use arquivo proprio no site Sir Fisher.')
    if format_!='TEXT' and (not re.fullmatch(r'[0-9a-f]{64}',item.get('media_sha256') or '') or item.get('verified_revision')!=item['revision']):
        raise ValueError('Arquivo da revisao sem validacao.')


def claim(item_id, expected_revision):
    # A transacao reivindica uma unica revisao: execucoes concorrentes nao enviam duas vezes.
    rows = query('''with candidate as (
      select e.id from public.marketing_editorial e join marketing_private.settings s on s.singleton
      join public.perfil_usuario p on p.user_id=s.owner_id and p.ativo
      where e.id=$1::uuid and e.revision=$2 and e.status='approved' and e.approved_by=s.owner_id
        and (p.papel='admin' or exists (select 1 from public.pagina_permissao pp where pp.pagina='marketing.html' and p.papel=any(pp.papeis)))
        and e.revision=e.approved_revision and e.rights_confirmed and e.quality_confirmed
        and (e.format='TEXT' or (e.media_sha256 is not null and e.verified_revision=e.revision))
        and e.scheduled_at<=now() and e.scheduled_at>=now()-interval '1 hour'
      for update of e skip locked
    ), claimed as (update public.marketing_editorial e set status='sending',updated_at=now()
      from candidate c where e.id=c.id returning e.*), logged as (
      insert into public.marketing_audit(editorial_id,action,detail)
      select id,'send_claimed',jsonb_build_object('revision',revision) from claimed)
    select * from claimed''',[item_id,expected_revision],write=True)
    return rows[0] if rows else None


def set_state(item, state, **fields):
    allowed = {'provider_container_id','provider_id','provider_url','last_error'}
    if not set(fields)<=allowed:
        raise ValueError('Campo fora do contrato.')
    assignments = ['status=$2','updated_at=now()']+[f'{name}=${index}' for index,name in enumerate(fields,3)]
    rows = query('update public.marketing_editorial set '+','.join(assignments)+
        " where id=$1::uuid and status in ('sending','uncertain') returning id,status",[item['id'],state,*fields.values()],write=True)
    if not rows or rows[0]['status']!=state:
        raise RuntimeError('Estado de envio sem confirmacao; interrompido.')
    query('insert into public.marketing_audit(editorial_id,action,detail) values($1::uuid,$2,$3::jsonb)',
        [item['id'],state,json.dumps(fields)],write=True)


def send_meta(meta, item):
    if item['target']=='instagram':
        params = {'image_url':item['media_url']} if item['format']=='IMAGE' else {'media_type':item['format'],'video_url':item['media_url']}
        if item['format']=='STORIES' and re.search(r'\.(jpe?g)(?:$)',item['media_url'],re.I):
            params = {'media_type':'STORIES','image_url':item['media_url']}
        if item['format']!='STORIES':
            params['caption']=item['caption']
        container = meta.request(IG+'/media',params,write=True)['id']
        set_state(item,'sending',provider_container_id=container)
        for attempt in range(12):
            state=meta.request(container,{'fields':'id,status_code'})
            if state.get('status_code')=='FINISHED':
                break
            if state.get('status_code') in {'ERROR','EXPIRED'}:
                raise RuntimeError('Container recusado pela Meta; revisar arquivo antes de nova aprovacao.')
            time.sleep(4)
        else:
            raise RuntimeError('Container ainda processando; conferir antes de tentar publicar.')
        published=meta.request(IG+'/media_publish',{'creation_id':container},write=True)
        ident=published['id']
        set_state(item,'sending',provider_id=ident)
        check=meta.request(ident,{'fields':'id,permalink'})
    else:
        if item['format']=='TEXT':
            published=meta.request(PAGE+'/feed',{'message':item['caption']},write=True,page=True)
            ident=published['id']
        else:
            published=meta.request(PAGE+'/photos',{'url':item['media_url'],'caption':item['caption']},write=True,page=True)
            ident=published.get('post_id') or published['id']
        set_state(item,'sending',provider_id=ident)
        check=meta.request(ident,{'fields':'id,permalink_url'},page=True)
    if check.get('id')!=ident:
        raise RuntimeError('Publicacao sem confirmacao de identidade por nova leitura.')
    return ident,check.get('permalink') or check.get('permalink_url')


def send_google(item):
    from scripts.gbp import gbp
    # Reutiliza a ferramenta Google existente. Nenhuma outra rotina e criada.
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            result=gbp.cmd_instagram(SimpleNamespace(dias=30,itens=item['source_media_id']+':FOOD_AND_DRINK',publicar=True,exigir_completo=True,
                expected_sha256=item['media_sha256'],ao_criar=lambda name:set_state(item,'sending',provider_id=name)))
    finally:
        folder=ROOT/'tmp/marketing';folder.mkdir(parents=True,exist_ok=True)
        (folder/(item['id']+'-google.log')).write_text(output.getvalue(),encoding='utf-8')
    matches=[r for r in result if r['instagram']==item['source_media_id']]
    if len(matches)!=1:
        raise RuntimeError('Foto nao enviada: indisponivel, duplicada ou qualidade insuficiente. Conferir a previa.')
    return matches[0]['name'],None


def run(send=False):
    verify_portal()
    owner=query('select owner_id from marketing_private.settings where singleton')[0]['owner_id']
    due=query("select * from public.marketing_editorial where status='approved' and scheduled_at<=now() order by scheduled_at limit 10")
    summary={'due':len(due),'sent':0,'mode':'send' if send else 'preview','needs_review':0}
    meta=None
    for row in due:
        try: validate(row,owner)
        except (ValueError,TypeError,KeyError):
            summary['needs_review']+=1
            continue
        if not send: continue
        if row['format']!='TEXT':
            from validar import verify_bytes
            if verify_bytes(row)!=row['media_sha256']:
                summary['needs_review']+=1
                continue
        # Permissoes e Pagina sao verificadas antes de reivindicar; falha nao consome o item.
        if row['target']!='google_photo':
            meta=meta or Meta()
            permissions=meta.permissions()
            required='instagram_content_publish' if row['target']=='instagram' else 'pages_manage_posts'
            if not permissions.get(required): raise RuntimeError('Permissao de publicacao ausente.')
            meta.pages()
            if row['target']=='instagram':
                quota=meta.request(IG+'/content_publishing_limit',{'fields':'quota_usage,config'}).get('data',[])
                if not quota or quota[0].get('quota_usage',0)>=quota[0].get('config',{}).get('quota_total',0):
                    raise RuntimeError('Limite de publicacao indisponivel ou atingido.')
        item=claim(row['id'],row['revision'])
        if not item: continue
        try:
            ident,url=send_google(item) if item['target']=='google_photo' else send_meta(meta,item)
            set_state(item,'published',provider_id=ident,provider_url=url,last_error=None)
            summary['sent']+=1
        except Exception:
            # POST sem resposta pode ter sido aceito. Esta fila nao repete automaticamente.
            set_state(item,'uncertain',last_error='Envio sem confirmacao. Conferir rede social/Google e ID antes de preparar nova revisao.')
            summary['needs_review']+=1
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enviar',action='store_true')
    args=parser.parse_args()
    try: print(json.dumps(run(args.enviar)))
    except Exception:
        raise SystemExit('Execucao interrompida; conferir estado no painel privado antes de repetir.') from None
