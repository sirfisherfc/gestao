#!/usr/bin/env python3
"""Fechamento, retomada e baixas com dados fictícios e rede bloqueada."""
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'importacao'))
import api_stone_baixas as b
import api_stone_rotina as r
import api_stone_pix as pix
import stone_fechamento as f
import api_stone_vendas as v
from importacao_core import ErroOperacional,ValidacaoErro

DIA = date(2026,10,21)
XML = b'''<Conciliation><Header><StoneCode>123</StoneCode><ReferenceDate>20261021</ReferenceDate></Header>
<FinancialTransactionsAccounts><Transaction><AcquirerTransactionKey>0001</AcquirerTransactionKey><Installments>
<Installment><InstallmentNumber>1</InstallmentNumber><PaymentDate>20261021</PaymentDate><OriginalPaymentDate>20261021</OriginalPaymentDate>
<GrossAmount>10.000000</GrossAmount><NetAmount>9.812345</NetAmount><PaymentId>P1</PaymentId><WalletTypeId>11</WalletTypeId><WalletNatureId>1</WalletNatureId></Installment>
</Installments></Transaction></FinancialTransactionsAccounts><Payments><Payment><Id>P1</Id><WalletTypeId>11</WalletTypeId><WalletNatureId>1</WalletNatureId></Payment></Payments></Conciliation>'''


class FechamentoFake:
    def __init__(self): self.rows={}
    def obter(self,d,e,c=''): return self.rows.get((d,e,c),{}).get('estado')
    def marcar(self,d,e,c='',**kw): self.rows[(d,e,c)]={'estado':'concluido',**kw}


class ControleFake:
    def __init__(self): self.rows={};self.reservas=0
    def obter(self,t,c,d): return self.rows.get((t,c,d))
    def reservar(self,t,c,d):
        if (t,c,d) in self.rows: return False
        self.rows[(t,c,d)]=('reservado',None);self.reservas+=1;return True
    def concluir(self,t,c,d,estado,**kw): self.rows[(t,c,d)]=(estado,kw.get('conteudo'))
    def diagnostico(self,*_): return 'Arquivo indisponível; pedido preservado.'


class Teste(unittest.TestCase):
    def setUp(self):
        self.sem_rede=patch.object(socket.socket,'connect',side_effect=AssertionError('rede real proibida'))
        self.sem_rede.start();self.addCleanup(self.sem_rede.stop)

    def evento(self): return b.ler_baixas(XML,'123',DIA)[0]
    def parcela(self,**kw):
        return dict(stonecode='123',valor_bruto=Decimal('10'),valor_liquido=Decimal('9.812345'),
                    ultimo_status='Aberto',data_vencimento=DIA+timedelta(days=1),
                    data_vencimento_original=DIA+timedelta(days=1),data_ultimo_status=None,**kw)

    def test_liquidacao_sem_captura_preserva_identidade_e_seis_casas(self):
        e=self.evento();self.assertEqual(e.stone_id,'0001');self.assertEqual(e.liquido,Decimal('9.812345'))
        estado,_,depois=b.decidir(e,self.parcela())
        self.assertEqual(estado,'aplicado');self.assertEqual(depois['ultimo_status'],'Pago')
        self.assertEqual(depois['data_vencimento'],DIA)
        self.assertNotIn('valor_liquido',depois);self.assertNotIn('desconto_antecipacao',depois)

    def test_identidade_nao_depende_da_referencia_e_versao_depende_do_conteudo(self):
        e=self.evento();nova=replace(e,referencia=DIA+timedelta(days=1))
        self.assertEqual(e.chave,nova.chave);self.assertEqual(e.hash_payload,nova.hash_payload)
        self.assertNotEqual(e.chave,replace(e,pagamento_id='P2').chave)
        self.assertNotEqual(e.hash_payload,replace(e,liquido=Decimal('8')).hash_payload)
        self.assertEqual(e.hash_payload,replace(e,bruto=Decimal('10.0')).hash_payload)

    def test_regressao_outra_identidade_mesma_parcela(self):
        e=replace(self.evento(),pagamento_id='outro')
        self.assertEqual(b.decidir(e,self.parcela(),DIA+timedelta(days=1))[0],'obsoleto')

    def test_divergencias_nao_alteram_dados(self):
        e=self.evento();p=self.parcela()
        for nova in (None,{**p,'stonecode':'999'},{**p,'valor_liquido':Decimal('7')},
                     {**p,'ultimo_status':'Cancelado'},{**p,'ultimo_status':'Pago'}):
            estado,_,depois=b.decidir(e,nova)
            self.assertEqual(estado,'pendente');self.assertIsNone(depois)
        estado,_,depois=b.decidir(e,{**p,'ultimo_status':'Pago','data_vencimento':DIA})
        self.assertEqual(estado,'aplicado');self.assertIsNone(depois)

    def test_xml_recusa_cabecalho_pagamento_e_valores_invalidos(self):
        for dados in (XML.replace(b'<StoneCode>123',b'<StoneCode>999'),XML.replace(b'<Id>P1',b'<Id>outro'),
                      XML.replace(b'9.812345',b'NaN'),XML.replace(b'<PaymentId>P1',b'<PaymentId>'),
                      XML.replace(b'20261021</PaymentDate>',b'20261022</PaymentDate>')):
            with self.assertRaises(ValidacaoErro): b.ler_baixas(dados,'123',DIA)

    def test_calendario_buraco_e_fronteira_do_prazo(self):
        codigos=['123'];dias=f.dias_esperados(date(2026,10,24))
        rows=[dict(dia=d,etapa=e,identificador=c,estado='concluido')
              for d in dias[1:] for e,c in f.expectativas(codigos)]
        antes=datetime(2026,10,22,23,59,59,tzinfo=f.FUSO_LOCAL)
        a=f.resumir(dias,codigos,rows,antes)
        self.assertIsNone(a['conferido_ate']);self.assertFalse(a['dias'][0]['atrasado'])
        depois=antes+timedelta(seconds=1)
        self.assertTrue(f.resumir(dias,codigos,rows,depois)['dias'][0]['atrasado'])
        self.assertFalse(any('173835323' in str(k) or 'voucher' in str(k) for k in f.expectativas(codigos)))

    def test_callback_valido_prevalece_sobre_erro_recente(self):
        erro=SimpleNamespace(conteudo=None,erro='download falhou')
        valido=SimpleNamespace(conteudo='id;amount\n',erro=None)
        self.assertIs(pix.escolher_arquivo([erro,valido]),valido)
        fila=object.__new__(pix.FilaPix)
        with patch.object(fila,'arquivos',return_value=[erro,valido]):
            self.assertIs(fila.aguardar([('doc',DIA)],None,0)[('doc',DIA)],valido)

    def test_recupera_pix_tardio_sem_nova_rede_e_repeticao(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(r.xml,'PASTA_PADRAO',Path(tmp)):
            controle=ControleFake();controle.rows[('xml','123',DIA)]=('recebido',XML.decode())
            fechamento=FechamentoFake()
            fila=SimpleNamespace(arquivos=lambda *_:[],recuperar_download=lambda *_:None)
            with patch.object(r,'importar') as importar,patch.object(r.baixas,'executar',return_value={'pendentes':0,'conferidas':1}),\
                 patch.object(r,'atualizar_painel'),patch.object(r.xml,'baixar_dia') as baixar,patch.object(r.pix,'solicitar') as pedir:
                r.processar_dia(DIA,['123'],'doc',controle,fila,fechamento)
                self.assertEqual(fechamento.obter(DIA,'vendas'),'aguardando')
                fila.arquivos=lambda *_:[SimpleNamespace(conteudo='id;amount\n',erro=None)]
                r.processar_dia(DIA,['123'],'doc',controle,fila,fechamento)
                self.assertEqual(fechamento.obter(DIA,'vendas'),'concluido')
                self.assertEqual(fechamento.obter(DIA,'painel'),'concluido')
                self.assertEqual(sum(c.args[0]=='api_stone_vendas.py' for c in importar.call_args_list),1)
                baixar.assert_not_called();pedir.assert_not_called();self.assertEqual(controle.reservas,0)

    def test_retomada_de_refresh_nao_reimporta(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(r.xml,'PASTA_PADRAO',Path(tmp)):
            c=ControleFake();c.rows[('xml','123',DIA)]=('recebido',XML.decode())
            fch=FechamentoFake()
            for e,code in [('vendas',''),('recebiveis','123'),('baixas','123')]: fch.marcar(DIA,e,code)
            fila=SimpleNamespace(arquivos=lambda *_:[])
            with patch.object(r,'importar') as importar,patch.object(r.baixas,'executar') as baixas,\
                 patch.object(r,'atualizar_painel',side_effect=[ErroOperacional('temporário'),None]):
                r.processar_dia(DIA,['123'],'doc',c,fila,fch)
                self.assertEqual(fch.obter(DIA,'painel'),'erro')
                r.processar_dia(DIA,['123'],'doc',c,fila,fch)
                self.assertEqual(fch.obter(DIA,'painel'),'concluido')
                importar.assert_not_called();baixas.assert_not_called()

    def test_orcamento_nao_libera_pedido_reservado(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(r.xml,'PASTA_PADRAO',Path(tmp)):
            c=ControleFake();c.rows[('xml','123',DIA)]=('erro',None)
            c.rows[('pix','doc',DIA)]=('aceito',None)
            fila=SimpleNamespace(arquivos=lambda *_:[])
            budget={'xml':0,'pix':0}
            with patch.object(r.xml,'baixar_dia') as baixar,patch.object(r.pix,'solicitar') as pedir,patch.object(r,'atualizar_painel'):
                r.processar_dia(DIA,['123'],'doc',c,fila,FechamentoFake(),consultar=True,orcamento=budget)
                baixar.assert_not_called();pedir.assert_not_called()
                self.assertEqual(c.rows[('xml','123',DIA)][0],'erro')

    def test_aviso_sem_controle_impede_novo_post_pix(self):
        c=ControleFake();fila=SimpleNamespace(arquivos=lambda *_:[SimpleNamespace(conteudo=None,erro='falha de download')])
        with patch.object(r.pix,'solicitar') as pedir:
            r.pedir_pix(c,fila,'fake','doc',DIA)
            pedir.assert_not_called();self.assertEqual(c.reservas,0)

    def test_download_pix_tem_limite_timeout_e_nao_segue_redirects(self):
        resposta=MagicMock();resposta.__enter__.return_value=resposta;resposta.status=200
        resposta.read.return_value=b'id;amount\n'
        opener=MagicMock();opener.open.return_value=resposta
        with patch.object(pix.urllib.request,'build_opener',return_value=opener) as construir:
            self.assertEqual(pix.baixar_csv_recebido('https://arquivo.example/privado'),'id;amount\n')
            resposta.read.assert_called_once_with(5_000_001)
            self.assertEqual(opener.open.call_args.kwargs['timeout'],20)
            handler=construir.call_args.args[0]
            self.assertIsNone(handler.redirect_request(None,None,None,None,None,None))
            resposta.read.return_value=b'x'*5_000_001
            with self.assertRaises(ErroOperacional): pix.baixar_csv_recebido('https://arquivo.example/privado')
        for url in ['http://arquivo.example/x','https://127.0.0.1/x','https://alguem:senha@arquivo.example/x','https://portal.supabase.co/x']:
            with self.assertRaises(ErroOperacional): pix.baixar_csv_recebido(url)

    def test_frescor_nao_certifica_dia_fora_do_periodo_consultado(self):
        fch=FechamentoFake()
        fch.fechar=lambda:None
        with patch.object(f,'Fechamento',return_value=fch):
            f.registrar_extrato(datetime.now(f.FUSO_LOCAL).isoformat(),inicio=datetime.now(f.FUSO_LOCAL).date())
        self.assertEqual(fch.rows,{})

    def test_zero_vendas_com_arquivos_validos_conclui_sem_insercao(self):
        fila=MagicMock();fila.documentos.return_value=['12345678000199']
        fila.arquivos.return_value=[SimpleNamespace(conteudo='id;amount\n',erro=None)]
        banco=MagicMock();banco.documento.return_value='12345678000199'
        banco.conn.cursor.return_value.__enter__.return_value.fetchall.return_value=[]
        conn=MagicMock()
        import api_saipos_vendas as saipos
        with tempfile.TemporaryDirectory() as tmp:
            pasta=Path(tmp);(pasta/'123').mkdir();(pasta/'123'/f'{DIA}.xml').write_bytes(
                b'<Conciliation><Header><StoneCode>123</StoneCode><ReferenceDate>20261021</ReferenceDate></Header></Conciliation>')
            args=['teste','--de',str(DIA),'--stonecode','123','--pasta',str(pasta)]
            with patch.object(sys,'argv',args),patch.object(v,'carregar_env'),patch.object(v,'_database_url',return_value='fake'),\
                 patch.object(v,'_referencia_projeto',return_value='lucpxoynpvogkvzepagi'),\
                 patch.object(v.pix,'FilaPix',return_value=fila),patch.object(v.recebiveis,'ConsultaBanco',return_value=banco),\
                 patch.object(v,'importar_registros') as inserir,patch.object(v,'atualizar_painel'),\
                 patch.object(saipos,'_conectar',return_value=conn),patch.object(saipos,'reconciliar_periodo'),\
                 patch.object(v.integracao_log,'registrar') as log:
                v.fluxo();inserir.assert_not_called()
                self.assertEqual(log.call_args.args[0][0].situacao,'sem_movimento')


if __name__=='__main__': unittest.main()
