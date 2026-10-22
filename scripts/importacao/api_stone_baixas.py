#!/usr/bin/env python3
"""Baixas de parcelas antigas por eventos XML, com auditoria e sem rede Stone."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

import api_stone_conciliacao as xml
from api_cliente import carregar_env
from importacao_core import ErroOperacional, ValidacaoErro, atualizar_painel, executar_com_saida
from stone_fechamento import conectar


def hash_json(value):
    def canonico(v):
        return format(v.normalize(),'f') if isinstance(v,Decimal) else str(v)
    return hashlib.sha256(json.dumps(value, default=canonico, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def dinheiro(valor):
    try:
        n = Decimal(valor or '')
        # NetAmount no XML tem até seis casas; não o tratar como CSV de centavos.
        if not n.is_finite() or n != n.quantize(Decimal('.000001')):
            raise ValueError
        return n
    except (InvalidOperation, ValueError) as exc:
        raise ValidacaoErro('valor de liquidação inválido') from exc


@dataclass(frozen=True)
class Baixa:
    stonecode: str
    stone_id: str
    parcela: int
    pagamento_id: str
    carteira: str
    natureza: str
    referencia: date
    pagamento: date
    original: date
    bruto: Decimal
    liquido: Decimal
    arquivo_sha256: str

    @property
    def chave(self):
        return hash_json((self.stonecode,self.stone_id,self.parcela,self.pagamento_id,self.carteira,self.natureza))

    @property
    def hash_payload(self):
        return hash_json((self.chave,self.pagamento,self.original,self.bruto,self.liquido))


def ler_baixas(dados, codigo, dia):
    resumo=xml.resumir_xml(dados)
    if not resumo.stonecode or not resumo.data_referencia:
        raise ValidacaoErro('liquidação sem cabeçalho completo de unidade e referência')
    xml.conferir_cabecalho(resumo, codigo, dia)
    raiz = ElementTree.fromstring(dados)
    pagamentos = {}
    for secao in xml.filhos(raiz,'Payments'):
        for p in xml.filhos(secao,'Payment'):
            pagamentos[xml.texto(p,'Id')] = (xml.texto(p,'WalletTypeId'),xml.texto(p,'WalletNatureId'))
    eventos = {}
    for secao in xml.filhos(raiz,'FinancialTransactionsAccounts'):
        for t in xml.filhos(secao,'Transaction'):
            stone_id = xml.texto(t,'AcquirerTransactionKey')
            for grupo in xml.filhos(t,'Installments'):
                for p in xml.filhos(grupo,'Installment'):
                    try:
                        numero = int(xml.texto(p,'InstallmentNumber') or '0')
                        pago = date.fromisoformat(datetime.strptime(xml.texto(p,'PaymentDate') or '', '%Y%m%d').date().isoformat())
                        original = datetime.strptime(xml.texto(p,'OriginalPaymentDate') or '', '%Y%m%d').date()
                    except ValueError as exc:
                        raise ValidacaoErro('data ou parcela da liquidação inválida') from exc
                    payment = xml.texto(p,'PaymentId')
                    carteira,natureza = xml.texto(p,'WalletTypeId'),xml.texto(p,'WalletNatureId')
                    bruto,liquido = dinheiro(xml.texto(p,'GrossAmount')),dinheiro(xml.texto(p,'NetAmount'))
                    if not stone_id or numero < 1 or not payment or not carteira or natureza != '1':
                        raise ValidacaoErro('liquidação sem identidade ou natureza de venda validada')
                    if pagamentos.get(payment) != (carteira,natureza):
                        raise ValidacaoErro('liquidação sem pagamento correspondente no XML')
                    if pago > dia or bruto <= 0 or liquido < 0 or liquido > bruto:
                        raise ValidacaoErro('liquidação fora da referência ou com valores não validados')
                    evento = Baixa(codigo,stone_id,numero,payment,carteira,natureza,dia,pago,original,
                                   bruto,liquido,hashlib.sha256(dados).hexdigest())
                    anterior = eventos.get(evento.chave)
                    if anterior and anterior.hash_payload != evento.hash_payload:
                        raise ValidacaoErro('eventos da mesma liquidação divergem dentro do arquivo')
                    eventos[evento.chave] = evento
    return list(eventos.values())


def decidir(evento, parcela, ultima_referencia=None):
    """Não altera taxa/valor nem deduz pagamento apenas pelo vencimento."""
    if ultima_referencia and evento.referencia < ultima_referencia:
        return 'obsoleto', 'Arquivo anterior à última baixa aplicada.', None
    if not parcela:
        return 'pendente', 'Parcela original não encontrada; aguardando captura.', None
    if str(parcela['stonecode']) != evento.stonecode:
        return 'pendente', 'Unidade da parcela não corresponde ao arquivo.', None
    moeda = lambda v: Decimal(v).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    if moeda(parcela['valor_bruto']) != moeda(evento.bruto) or moeda(parcela['valor_liquido']) != moeda(evento.liquido):
        return 'pendente', 'Valores da liquidação divergem da parcela; conferir taxas/ajustes.', None
    status = parcela['ultimo_status'] or ''
    if status == 'Pago':
        if parcela['data_vencimento'] != evento.pagamento:
            return 'pendente', 'Parcela já paga tem outra data; ordem dos eventos precisa ser conferida.', None
        return 'aplicado', 'Pagamento já refletido; valores e data conferidos.', None
    if status not in ('Aberto','Agendado'):
        return 'pendente', 'Status da parcela exige regra específica antes da baixa.', None
    depois = {k:parcela[k] for k in ('ultimo_status','data_ultimo_status','data_vencimento','data_vencimento_original')}
    depois.update(ultimo_status='Pago', data_ultimo_status=datetime.combine(evento.pagamento,datetime.min.time()),
                  data_vencimento=evento.pagamento,data_vencimento_original=evento.original)
    return 'aplicado', 'Liquidação e parcela conferidas; baixa comprovada pelo XML.', depois


def processar(cur, eventos, *, dry_run=False):
    from psycopg2.extras import Json
    resumo = dict(eventos=len(eventos),atualizadas=0,conferidas=0,pendentes=0,obsoletas=0)
    cur.execute("select stonecode from stone_conta where ativa and entra_faturamento and stonecode <> '173835323'")
    permitidos = {str(r[0]) for r in cur.fetchall()}
    if any(e.stonecode not in permitidos for e in eventos):
        raise ErroOperacional('arquivo de unidade fora do escopo automático')
    for e in eventos:
        # O lock é na parcela, não só no PaymentId: versões de identidades
        # diferentes da mesma parcela também não podem regredir seu estado.
        cur.execute('select pg_advisory_xact_lock(hashtextextended(%s,0))',
                    ('stone-baixa:'+e.stonecode+':'+e.stone_id+':'+str(e.parcela),))
        cur.execute('select conta_id,stonecode,valor_bruto,valor_liquido,ultimo_status,data_ultimo_status,'
                    'data_vencimento,data_vencimento_original from raw_stone_recebiveis '
                    "where stone_id=%s and n_parcela=%s and categoria='Venda'" + ('' if dry_run else ' for update'),
                    (e.stone_id,e.parcela))
        row = cur.fetchone()
        campos = ('conta_id','stonecode','valor_bruto','valor_liquido','ultimo_status','data_ultimo_status',
                  'data_vencimento','data_vencimento_original')
        parcela = dict(zip(campos,row)) if row else None
        cur.execute('select max(referencia) from private.stone_baixa_evento '
                    "where stonecode=%s and stone_id=%s and n_parcela=%s and estado='aplicado'",
                    (e.stonecode,e.stone_id,e.parcela))
        ultima = cur.fetchone()[0]
        cur.execute('select hash_payload,estado,conflito from private.stone_baixa_evento where chave=%s and referencia=%s',
                    (e.chave,e.referencia))
        anterior = cur.fetchone()
        if anterior and (anterior[0] != e.hash_payload or anterior[2]):
            estado,mensagem,depois = 'pendente','Mesmo evento/referência mudou de conteúdo; conferência necessária.',None
        else:
            estado,mensagem,depois = decidir(e,parcela,ultima)
        # A fonte precisa continuar vinculada à mesma conta da captura.
        if parcela:
            cur.execute("select conta_id from fonte_financeira where chave='stone_recebiveis' and ativa")
            fonte = cur.fetchone()
            if not fonte or fonte[0] != parcela['conta_id']:
                estado,mensagem,depois = 'pendente','Vínculo da conta de recebíveis exige conferência.',None
        resumo['pendentes' if estado=='pendente' else 'obsoletas' if estado=='obsoleto' else 'conferidas'] += 1
        if depois:
            resumo['atualizadas'] += 1
        if dry_run:
            continue
        if depois:
            cur.execute('update raw_stone_recebiveis set ultimo_status=%s,data_ultimo_status=%s,'
                        'data_vencimento=%s,data_vencimento_original=%s '
                        "where stone_id=%s and n_parcela=%s and categoria='Venda' and conta_id=%s",
                        (*[depois[k] for k in ('ultimo_status','data_ultimo_status','data_vencimento','data_vencimento_original')],
                         e.stone_id,e.parcela,parcela['conta_id']))
            if cur.rowcount != 1:
                raise ErroOperacional('baixa recusada: parcela alterada durante a conferência')
        antes = {k:parcela[k] for k in ('ultimo_status','data_ultimo_status','data_vencimento','data_vencimento_original')} if parcela else None
        cur.execute('insert into private.stone_baixa_evento(chave,referencia,hash_payload,arquivo_sha256,'
                    'stonecode,stone_id,n_parcela,pagamento,estado,mensagem,antes,depois) '
                    'values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
                    'on conflict(chave,referencia) do update set '
                    'estado=case when stone_baixa_evento.conflito or stone_baixa_evento.hash_payload<>excluded.hash_payload then stone_baixa_evento.estado else excluded.estado end,'
                    'conflito=stone_baixa_evento.conflito or stone_baixa_evento.hash_payload<>excluded.hash_payload,mensagem=excluded.mensagem,'
                    'antes=coalesce(stone_baixa_evento.antes,excluded.antes),'
                    'depois=case when not stone_baixa_evento.conflito and stone_baixa_evento.hash_payload=excluded.hash_payload then excluded.depois else stone_baixa_evento.depois end,'
                    'atualizado_em=now()',
                    (e.chave,e.referencia,e.hash_payload,e.arquivo_sha256,e.stonecode,e.stone_id,e.parcela,e.pagamento,
                     estado,mensagem,Json(antes,dumps=lambda v:json.dumps(v,default=str)) if antes is not None else None,
                     Json(depois or antes,dumps=lambda v:json.dumps(v,default=str)) if (depois or antes) is not None else None))
    return resumo


def executar(dia, codigos, pasta, *, dry_run=False, refresh=True):
    eventos = []
    for codigo in codigos:
        caminho = pasta/codigo/f'{dia}.xml'
        if not caminho.is_file():
            raise ErroOperacional('arquivo de liquidação não disponível no cache privado')
        eventos.extend(ler_baixas(caminho.read_bytes(),codigo,dia))
    conn = conectar(readonly=dry_run)
    try:
        with conn, conn.cursor() as cur:
            resultado = processar(cur,eventos,dry_run=dry_run)
            if not dry_run and resultado['atualizadas']:
                cur.execute("insert into log_carga(fontes) values ('Baixas Stone (API)')")
        if not dry_run and refresh:
            atualizar_painel()
        return resultado
    except (ErroOperacional,ValidacaoErro):
        raise
    except Exception as exc:
        raise ErroOperacional(f'falha ao conferir/gravar baixas ({exc.__class__.__name__}); detalhes financeiros preservados') from None
    finally:
        conn.close()


def fluxo():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dia',type=date.fromisoformat,required=True)
    p.add_argument('--stonecode',action='append')
    p.add_argument('--pasta',type=Path,default=xml.PASTA_PADRAO)
    p.add_argument('--dry-run',action='store_true')
    op = p.parse_args()
    carregar_env()
    codigos = xml.resolver_stonecodes(op.stonecode)
    resultado = executar(op.dia,codigos,op.pasta,dry_run=op.dry_run)
    print('STONE_BAIXAS '+json.dumps(resultado))
    if resultado['pendentes']:
        raise ErroOperacional('baixas com divergências; conferir etapa no Status')


if __name__ == '__main__':
    sys.exit(executar_com_saida(fluxo))
