"""Contratos offline de aprovacao, midia e envio. Sem credencial/rede."""
import datetime as dt
import contextlib
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent))
import executar
from coletar import metric_value,metrics_status


class MarketingTests(unittest.TestCase):
    def setUp(self):
        self.now=dt.datetime(2026,11,2,15,tzinfo=dt.timezone.utc)
        self.item={'id':'11111111-1111-4111-8111-111111111111','target':'instagram','format':'IMAGE',
            'caption':'Texto aprovado','media_url':'https://www.sirfisher.com.br/assets/img/test.jpg',
            'scheduled_at':(self.now-dt.timedelta(minutes=2)).isoformat(),
            'approved_by':'owner','revision':2,'approved_revision':2,
            'rights_confirmed':True,'quality_confirmed':True,'media_sha256':'a'*64,'verified_revision':2}

    def test_owner_revision_and_hash(self):
        executar.validate(self.item,'owner',self.now)
        for key,value in [('approved_by','another'),('approved_revision',1),('verified_revision',1),('media_sha256',None),('rights_confirmed',False),('quality_confirmed',False)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                executar.validate({**self.item,key:value},'owner',self.now)

    def test_schedule(self):
        for delta in [dt.timedelta(minutes=1),-dt.timedelta(hours=2)]:
            with self.assertRaises(ValueError):
                executar.validate({**self.item,'scheduled_at':(self.now+delta).isoformat()},'owner',self.now)

    def test_external_urls_and_formats(self):
        for url in ['https://evil.example/file.jpg','https://sirfisher.com.br@evil.example/file.jpg','http://www.sirfisher.com.br/file.jpg','https://www.sirfisher.com.br/file.jpg?secret=x']:
            with self.assertRaises(ValueError): executar.validate({**self.item,'media_url':url},'owner',self.now)
        with self.assertRaises(ValueError): executar.validate({**self.item,'format':'TEXT'},'owner',self.now)

    def test_zero_and_missing(self):
        self.assertEqual(metric_value({'status':'available','response':[{'total_value':{'value':0}}]}),0)
        self.assertIsNone(metric_value({'status':'unavailable','response':None}))
        self.assertEqual(metrics_status({'metrics':[{'value':0},{'value':None}]}),'partial')

    def test_send_image_confirmed_once(self):
        calls=[]
        class Fake:
            def request(self,path,params,**kwargs):
                calls.append((path,kwargs.get('write',False)))
                return [{'id':'1111111111'},{'status_code':'FINISHED'},{'id':'2222222222'},{'id':'2222222222','permalink':'https://www.instagram.com/p/test/'}][len(calls)-1]
        with patch.object(executar,'set_state'):
            ident,_=executar.send_meta(Fake(),self.item)
        self.assertEqual(ident,'2222222222')
        self.assertEqual(sum(write for _,write in calls),2)
        self.assertEqual(calls[-1],('2222222222',False))

    def test_timeout_never_retries_publish(self):
        writes=[]
        class Fake:
            def request(self,path,params,**kwargs):
                if kwargs.get('write'): writes.append(path)
                if path.endswith('/media'): return {'id':'1111111111'}
                if path=='1111111111': return {'status_code':'FINISHED'}
                raise RuntimeError('Timeout')
        with patch.object(executar,'set_state'),self.assertRaises(RuntimeError): executar.send_meta(Fake(),self.item)
        self.assertEqual(writes.count(executar.IG+'/media_publish'),1)

    def test_empty_queue_never_opens_meta(self):
        with patch.object(executar,'verify_portal'),patch.object(executar,'query',side_effect=[[{'owner_id':'owner'}],[]]),patch.object(executar,'Meta') as api:
            self.assertEqual(executar.run(True)['sent'],0)
            api.assert_not_called()

    def test_google_only_selected_photo_and_readback(self):
        from scripts.gbp import gbp
        photo=lambda id_: {'id':id_,'url':'https://example.test/'+id_,'post':'https://www.instagram.com/p/test/','data':'2026-11-02','legenda':'Foto propria'}
        # MagicMock oferece os metodos de contexto usados no download.
        from unittest.mock import MagicMock
        download=MagicMock(); download.__enter__.return_value.read.return_value=b'image'
        name=f'{gbp.CONTA}/{gbp.LOCAL}/media/selected'
        with tempfile.TemporaryDirectory() as temp,patch.object(gbp,'SAIDA',Path(temp)),patch.dict(sys.modules,{'PIL':SimpleNamespace(Image=SimpleNamespace(open=lambda p:SimpleNamespace(size=(800,800))))}),patch.object(gbp,'hashes_publicados',return_value=[]),patch.object(gbp,'hashes_descartados',return_value=[]),patch.object(gbp,'fotos_instagram',return_value=[photo('111111'),photo('222222')]),patch.object(gbp,'dhash',return_value=100),patch.object(gbp,'parecida',return_value=False),patch.object(gbp.urllib.request,'urlopen',return_value=download) as fetch,patch.object(gbp,'api',side_effect=[{'name':name},{'name':name}]) as api,patch.object(gbp,'registrar'),contextlib.redirect_stdout(io.StringIO()):
            result=gbp.cmd_instagram(SimpleNamespace(dias=30,itens='222222',publicar=True,exigir_completo=True))
        self.assertEqual(fetch.call_count,1)
        self.assertEqual([c.args[0] for c in api.call_args_list],['POST','GET'])
        self.assertEqual(result,[{'instagram':'222222','name':name}])


if __name__=='__main__': unittest.main()
