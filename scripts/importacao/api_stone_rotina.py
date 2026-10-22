#!/usr/bin/env python3
"""Uma carga Stone por dia, com arquivos privados e pedidos sem repetição."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
import subprocess
import sys

import api_stone_conciliacao as xml
import api_stone_pix as pix
import integracao_log
from api_cliente import ErroHttp, carregar_env, salvar_atomico, variavel
from importacao_core import ErroOperacional, _database_url, _referencia_projeto, executar_com_saida

ROOT = Path(__file__).resolve().parents[2]


class Controle:
    def __init__(self):
        import psycopg2
        url = _database_url()
        if _referencia_projeto(url) != "lucpxoynpvogkvzepagi":
            raise ErroOperacional("destino recusado: usar somente o portal")
        self.conn = psycopg2.connect(url)

    def obter(self, tipo, identificador, dia):
        with self.conn, self.conn.cursor() as cur:
            cur.execute("select estado, conteudo from private.stone_api_controle where tipo=%s and identificador=%s and dia=%s",
                        (tipo, identificador, dia))
            return cur.fetchone()

    def reservar(self, tipo, identificador, dia):
        # PK + INSERT atômico: dois runners não conseguem enviar o mesmo pedido.
        # A reserva fica persistida antes da rede, inclusive se houver timeout.
        with self.conn, self.conn.cursor() as cur:
            cur.execute("select exists(select 1 from private.stone_api_controle where estado='erro' and resposta_http in (401,403,429))")
            if cur.fetchone()[0]:
                raise ErroOperacional("consultas Stone suspensas após recusa anterior; não haverá nova tentativa automática")
            cur.execute("insert into private.stone_api_controle(tipo,identificador,dia,estado) values (%s,%s,%s,'reservado') on conflict do nothing returning tipo",
                        (tipo, identificador, dia))
            return cur.fetchone() is not None

    def concluir(self, tipo, identificador, dia, estado, *, conteudo=None, http=None, erro=None):
        with self.conn, self.conn.cursor() as cur:
            cur.execute("insert into private.stone_api_controle(tipo,identificador,dia,estado,conteudo,resposta_http,erro) values (%s,%s,%s,%s,%s,%s,%s) "
                        "on conflict(tipo,identificador,dia) do update set estado=excluded.estado,conteudo=coalesce(excluded.conteudo,stone_api_controle.conteudo),"
                        "resposta_http=excluded.resposta_http,erro=excluded.erro,atualizado_em=now()",
                        (tipo, identificador, dia, estado, conteudo, http, erro))

    def ja_importado(self, dia, codigos):
        with self.conn, self.conn.cursor() as cur:
            cur.execute("select fonte,stonecode,situacao from (select distinct on(fonte,stonecode) fonte,stonecode,situacao "
                        "from integracao_execucao where dia_referencia=%s and fonte in ('stone_recebiveis','stone_vendas') "
                        "order by fonte,stonecode,executado_em desc) e", (dia,))
            linhas = cur.fetchall()
        vendas = any(f == 'stone_vendas' and s in ('ok','sem_movimento') for f,_,s in linhas)
        recebiveis = all(any(f == 'stone_recebiveis' and c == codigo and s in ('ok','sem_movimento') for f,c,s in linhas) for codigo in codigos)
        return vendas and recebiveis

    def fechar(self):
        self.conn.close()


def garantir_xml(controle, chave, codigo, dia):
    destino = xml.PASTA_PADRAO / codigo / f"{dia}.xml"
    cache = controle.obter("xml", codigo, dia)
    if cache and cache[1] is not None:
        dados = cache[1].encode("utf-8")
    elif destino.is_file():
        dados = destino.read_bytes()
    else:
        if not controle.reservar("xml", codigo, dia):
            raise ErroOperacional(f"XML de {dia} já foi solicitado; pedido não repetido")
        try:
            dados, _ = xml.baixar_dia(chave, codigo, dia, xml.LAYOUT_PADRAO)
        except Exception as exc:
            controle.concluir("xml", codigo, dia, "erro", http=exc.status if isinstance(exc, ErroHttp) else None,
                              erro="falha ao receber XML; nenhuma repetição automática")
            raise
    xml.conferir_cabecalho(xml.resumir_xml(dados), codigo, dia)
    controle.concluir("xml", codigo, dia, "recebido", conteudo=dados.decode("utf-8-sig"), http=200)
    salvar_atomico(destino, dados)


def pedir_pix(controle, fila, chave, documento, dia):
    if any(a.conteudo is not None and not a.erro for a in fila.arquivos(documento, dia)):
        controle.concluir("pix", documento, dia, "recebido", http=200)
        return
    if controle.obter("pix", documento, dia):
        print("Pix já solicitado; aguardando somente a fila privada.")
        return
    if not controle.reservar("pix", documento, dia):
        return
    try:
        pix.solicitar(chave, documento, dia)
    except Exception as exc:
        controle.concluir("pix", documento, dia, "erro", http=exc.status if isinstance(exc, ErroHttp) else None,
                          erro="falha ao solicitar Pix; nenhuma repetição automática")
        raise
    controle.concluir("pix", documento, dia, "aceito", http=202)
    print("Pix solicitado uma vez; aguardando entrega pelo webhook.")


def importar(nome, dia, codigos):
    args = [sys.executable, str(ROOT / "scripts/importacao" / nome), "--de", str(dia), "--ate", str(dia)]
    for codigo in codigos:
        args += ["--stonecode", codigo]
    resultado = subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace")
    if resultado.returncode:
        # O repositório/log do Actions é público: não publicar a saída financeira.
        raise ErroOperacional(f"{nome} não concluiu (código {resultado.returncode}); conferir a integração no painel")


def fluxo():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dia", type=date.fromisoformat)
    parser.add_argument("--aguardar", type=int, choices=range(0,36), default=35)
    parser.add_argument("--dry-run", action="store_true", help="confere sem consultar a Stone nem gravar")
    op = parser.parse_args()
    carregar_env()
    hoje = datetime.now(pix.FUSO_LOCAL).date()
    dia = op.dia or hoje-timedelta(days=1)
    xml.dias_do_periodo(dia, dia, hoje)
    codigos = xml.resolver_stonecodes(None)
    controle, fila = Controle(), pix.FilaPix()
    try:
        if controle.ja_importado(dia, codigos):
            print(f"STONE_ROTINA_OK {dia}: vendas e recebíveis já atualizados; zero consultas Stone.")
            return
        documentos = fila.documentos()
        if len(documentos) != 1:
            raise ErroOperacional("é necessário um único CNPJ validado")
        if op.dry_run:
            print(f"STONE_ROTINA_DRY_RUN {dia}: {len(codigos)} stonecode(s); nenhuma consulta Stone ou gravação.")
            return
        chave = variavel("STONE_CONCILIACAO_API_KEY")
        for codigo in codigos:
            garantir_xml(controle, chave, codigo, dia)
        importar("api_stone_recebiveis.py", dia, codigos)
        documento = documentos[0]
        pedir_pix(controle, fila, chave, documento, dia)
        prontos = fila.aguardar([(documento,dia)], None, op.aguardar)
        arquivo = prontos.get((documento,dia))
        if not arquivo or arquivo.conteudo is None or arquivo.erro:
            raise ErroOperacional("Pix ainda não disponível na fila; pedido não será repetido automaticamente")
        controle.concluir("pix", documento, dia, "recebido", http=200)
        importar("api_stone_vendas.py", dia, codigos)
        print(f"STONE_ROTINA_OK {dia}: cartão, Pix e recebíveis atualizados.")
    except ErroOperacional as exc:
        if not op.dry_run:
            integracao_log.registrar([integracao_log.Execucao("stone_vendas", dia, None, "erro", mensagem=str(exc))])
        raise
    finally:
        controle.fechar()
        fila.fechar()


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
