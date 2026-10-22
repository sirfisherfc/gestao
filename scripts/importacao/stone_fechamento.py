"""Checkpoints privados do fechamento Stone; saúde não faz chamadas bancárias."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
import json

from api_stone_pix import FUSO_LOCAL
from importacao_core import ErroOperacional, _database_url, _referencia_projeto

INICIO = date(2026, 10, 21)
ETAPAS_GERAIS = ('vendas', 'painel', 'extrato')


def conectar(*, readonly=False):
    import psycopg2
    url = _database_url()
    if _referencia_projeto(url) != 'lucpxoynpvogkvzepagi':
        raise ErroOperacional('destino recusado: usar somente o portal')
    conn = psycopg2.connect(url, application_name='sirfisher_stone_fechamento')
    if readonly:
        conn.set_session(readonly=True)
    return conn


def dias_esperados(hoje, inicio=INICIO):
    return [inicio + timedelta(days=i) for i in range(max(0, (hoje-inicio).days))]


def prazo(dia):
    # Exclusivo: 00h de D+2. A operação tem até o último segundo de D+1.
    return datetime.combine(dia+timedelta(days=2), time.min, FUSO_LOCAL)


def expectativas(codigos):
    return [(e, '') for e in ETAPAS_GERAIS] + [(e, c) for c in codigos for e in ('recebiveis', 'baixas')]


def resumir(dias, codigos, registros, agora):
    mapa = {(r['dia'], r['etapa'], r['identificador']): r for r in registros}
    resultado = []
    for dia in dias:
        faltam = [f'{e}:{c}' if c else e for e,c in expectativas(codigos)
                  if mapa.get((dia,e,c), {}).get('estado') != 'concluido']
        resultado.append({'dia': dia, 'concluido': not faltam,
                          'atrasado': bool(faltam) and agora >= prazo(dia), 'faltam': faltam})
    contiguo = None
    for r in resultado:
        if not r['concluido']:
            break
        contiguo = r['dia']
    return {'dias': resultado, 'conferido_ate': contiguo}


class Fechamento:
    def __init__(self, *, readonly=False):
        self.conn = conectar(readonly=readonly)

    def obter(self, dia, etapa, identificador=''):
        with self.conn, self.conn.cursor() as cur:
            cur.execute('select estado from private.stone_fechamento_dia where dia=%s and etapa=%s and identificador=%s',
                        (dia, etapa, identificador))
            row = cur.fetchone()
        return row[0] if row else None

    def marcar(self, dia, etapa, identificador='', *, estado='concluido', mensagem=None, quantidade=0, origem_em=None):
        with self.conn, self.conn.cursor() as cur:
            cur.execute('insert into private.stone_fechamento_dia(dia,etapa,identificador,estado,mensagem,quantidade,origem_em) '
                        'values (%s,%s,%s,%s,%s,%s,%s) on conflict(dia,etapa,identificador) do update set '
                        'estado=excluded.estado,mensagem=excluded.mensagem,quantidade=excluded.quantidade,'
                        'origem_em=excluded.origem_em,atualizado_em=now()',
                        (dia,etapa,identificador,estado,mensagem,quantidade,origem_em))

    def registros(self):
        from psycopg2.extras import RealDictCursor
        with self.conn, self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('select dia,etapa,identificador,estado from private.stone_fechamento_dia where dia >= %s', (INICIO,))
            return [dict(r) for r in cur.fetchall()]

    def fechar(self):
        self.conn.close()


def registrar_extrato(origem_em, inicio=INICIO):
    """Só após saldo conferido e refresh; data da consulta não substitui frescor."""
    try:
        instante = datetime.fromisoformat(str(origem_em).replace('Z', '+00:00')) if origem_em else None
    except ValueError:
        instante = None
    if instante and instante.tzinfo is None:
        instante = None
    agora = datetime.now(FUSO_LOCAL)
    f = Fechamento()
    try:
        for dia in dias_esperados(agora.date(),max(INICIO,inicio)):
            # O snapshot precisa ter sido atualizado depois de terminar D.
            limite = datetime.combine(dia+timedelta(days=1), time.min, FUSO_LOCAL)
            if instante and limite <= instante <= agora + timedelta(minutes=5):
                f.marcar(dia, 'extrato', origem_em=instante,
                         mensagem='Saldo conferido e painel atualizado; snapshot da fonte posterior ao dia.')
            elif f.obter(dia,'extrato') != 'concluido':
                f.marcar(dia, 'extrato', estado='aguardando', origem_em=instante,
                         mensagem='Saldo conferido; aguardando snapshot da origem posterior ao dia.')
    finally:
        f.fechar()


def imprimir_saude(codigos):
    f = Fechamento(readonly=True)
    try:
        agora = datetime.now(FUSO_LOCAL)
        resumo = resumir(dias_esperados(agora.date()), codigos, f.registros(), agora)
        print('STONE_SAUDE ' + json.dumps(resumo, default=str, ensure_ascii=True))
        return resumo
    finally:
        f.fechar()
