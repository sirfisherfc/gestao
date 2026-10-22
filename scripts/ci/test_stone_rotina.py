#!/usr/bin/env python3
"""Uma chamada por arquivo/data e recuperação por cache, sem rede."""
from datetime import date
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "importacao"))
import api_stone_rotina as r
from api_cliente import ErroHttp
from importacao_core import ErroOperacional

DIA = date(2026, 10, 21)
XML = b'<Conciliation><Header><StoneCode>123</StoneCode><ReferenceDate>20261021</ReferenceDate></Header></Conciliation>'


class ControleFake:
    def __init__(self):
        self.rows = {}
        self.blocked = False

    def obter(self, tipo, chave, dia):
        return self.rows.get((tipo,chave,dia))

    def reservar(self, tipo, chave, dia):
        if self.blocked:
            raise ErroOperacional("suspenso após 403")
        key = (tipo,chave,dia)
        if key in self.rows:
            return False
        self.rows[key] = ('reservado',None)
        return True

    def concluir(self, tipo, chave, dia, estado, **kw):
        self.rows[(tipo,chave,dia)] = (estado,kw.get('conteudo'))
        if kw.get('http') in (401,403,429):
            self.blocked = True


def main():
    c = ControleFake()
    f = SimpleNamespace(arquivos=lambda *_: [])
    with patch.object(r.pix, 'solicitar') as enviar:
        r.pedir_pix(c,f,'fake','123',DIA)
        r.pedir_pix(c,f,'fake','123',DIA)
        assert enviar.call_count == 1
    # Arquivo pronto dispensa solicitação, inclusive em outro runner.
    with patch.object(r.pix, 'solicitar') as enviar:
        r.pedir_pix(ControleFake(),SimpleNamespace(arquivos=lambda *_:[SimpleNamespace(conteudo='id;amount\n',erro=None)]),'fake','123',DIA)
        enviar.assert_not_called()
    c = ControleFake()
    with patch.object(r.pix, 'solicitar',side_effect=ErroHttp(403,'recusado')) as enviar:
        try:
            r.pedir_pix(c,f,'fake','123',DIA)
        except ErroHttp:
            pass
        r.pedir_pix(c,f,'fake','123',DIA)
        try:
            r.pedir_pix(c,f,'fake','123',date(2026,10,22))
        except ErroOperacional:
            pass
        assert enviar.call_count == 1 and c.blocked
    with tempfile.TemporaryDirectory() as pasta, patch.object(r.xml,'PASTA_PADRAO',Path(pasta)):
        c = ControleFake()
        with patch.object(r.xml,'baixar_dia',return_value=(XML,None)) as baixar:
            r.garantir_xml(c,'fake','123',DIA)
            # Simula runner novo: remove só o arquivo temporário do teste.
            (Path(pasta)/'123'/f'{DIA}.xml').unlink()
            r.garantir_xml(c,'fake','123',DIA)
            assert baixar.call_count == 1
            assert (Path(pasta)/'123'/f'{DIA}.xml').read_bytes()==XML
    print('STONE_ROTINA_TESTS_OK pedidos_unicos=1 cache_privado=1 bloqueio_403=1 network=0')


if __name__ == '__main__':
    main()
