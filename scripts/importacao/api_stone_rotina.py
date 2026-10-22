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
from importacao_core import ErroOperacional, ImportacaoErro, _database_url, _referencia_projeto, executar_com_saida, atualizar_painel
from stone_fechamento import Fechamento, INICIO, dias_esperados, imprimir_saude
import api_stone_baixas as baixas

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

    def diagnostico(self, tipo, identificador, dia):
        with self.conn, self.conn.cursor() as cur:
            cur.execute('select estado,resposta_http from private.stone_api_controle where tipo=%s and identificador=%s and dia=%s',
                        (tipo,identificador,dia))
            row=cur.fetchone()
            if not row:
                cur.execute("select estado,resposta_http from private.stone_api_controle where estado='erro' and resposta_http in (401,403,429) order by atualizado_em desc limit 1")
                row=cur.fetchone()
        http=row[1] if row else None
        if http in (401,403): return f'Acesso Stone recusado (HTTP {http}); novas consultas suspensas até diagnóstico.'
        if http==429: return 'Limite de consultas Stone (HTTP 429); novas consultas suspensas até diagnóstico.'
        if http and http>=500: return f'Stone indisponível (HTTP {http}); pedido preservado, sem repetição automática.'
        if row and row[0] in ('reservado','erro'): return 'Resultado do pedido incerto; reserva preservada para não duplicar a solicitação.'
        if row and row[0]=='aceito': return 'Pix solicitado; aguardando entrega do arquivo pela Stone.'
        return 'Arquivo ainda indisponível; aguardando coleta ou recuperação, sem repetir pedidos existentes.'

    def fechar(self):
        self.conn.close()


def garantir_xml(controle, chave, codigo, dia, *, consultar=True):
    destino = xml.PASTA_PADRAO / codigo / f"{dia}.xml"
    cache = controle.obter("xml", codigo, dia)
    if cache and cache[1] is not None:
        dados = cache[1].encode("utf-8")
    elif destino.is_file():
        dados = destino.read_bytes()
    else:
        if not consultar:
            raise ErroOperacional('XML ainda não disponível; recuperação usa somente o cache')
        if not controle.reservar("xml", codigo, dia):
            raise ErroOperacional(f"XML de {dia} já foi solicitado; pedido não repetido")
        try:
            dados, _ = xml.baixar_dia(chave, codigo, dia, xml.LAYOUT_PADRAO)
        except Exception as exc:
            controle.concluir("xml", codigo, dia, "erro", http=exc.status if isinstance(exc, ErroHttp) else None,
                              erro="falha ao receber XML; nenhuma repetição automática")
            raise
    xml.conferir_cabecalho(xml.resumir_xml(dados), codigo, dia)
    if not cache or cache[0] not in ('erro','reservado','aceito'):
        controle.concluir("xml", codigo, dia, "recebido", conteudo=dados.decode("utf-8-sig"), http=200)
    salvar_atomico(destino, dados)


def pedir_pix(controle, fila, chave, documento, dia):
    arquivos = fila.arquivos(documento,dia)
    if any(a.conteudo is not None and not a.erro for a in arquivos):
        controle.concluir("pix", documento, dia, "recebido", http=200)
        return
    if arquivos:
        print('Aviso Pix já recebido; recuperar somente o arquivo, sem novo pedido.')
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
    args += ['--sem-refresh-painel']
    resultado = subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace")
    if resultado.returncode:
        # O repositório/log do Actions é público: não publicar a saída financeira.
        raise ErroOperacional(f"{nome} não concluiu (código {resultado.returncode}); conferir a integração no painel")


def processar_dia(dia, codigos, documento, controle, fila, fechamento, *, consultar=False,
                  orcamento=None, aguardar=0, recuperar_downloads=False):
    """Etapas independentes, checkpoints só depois do commit correspondente."""
    prontos = []
    mudou = False
    for codigo in codigos:
        try:
            pode = consultar and orcamento['xml'] > 0
            cache = controle.obter('xml',codigo,dia)
            local = xml.PASTA_PADRAO/codigo/f'{dia}.xml'
            novo = not cache and not local.is_file()
            if pode and novo:
                orcamento['xml'] -= 1
            garantir_xml(controle,variavel('STONE_CONCILIACAO_API_KEY') if pode and novo else None,codigo,dia,consultar=pode)
            prontos.append(codigo)
        except ImportacaoErro:
            for etapa in ('recebiveis','baixas'):
                if fechamento.obter(dia,etapa,codigo) != 'concluido':
                    fechamento.marcar(dia,etapa,codigo,estado='aguardando',
                                      mensagem=controle.diagnostico('xml',codigo,dia))
            continue
        if fechamento.obter(dia,'recebiveis',codigo) != 'concluido':
            try:
                fechamento.marcar(dia,'painel',estado='pendente',mensagem='Atualização de dados em andamento.')
                importar('api_stone_recebiveis.py',dia,[codigo])
                fechamento.marcar(dia,'recebiveis',codigo,mensagem='Arquivo conferido; novas parcelas importadas.')
                mudou = True
            except ImportacaoErro:
                fechamento.marcar(dia,'recebiveis',codigo,estado='erro',mensagem='Recebíveis recusados pela validação; conferir arquivo/eventos.')
        if fechamento.obter(dia,'baixas',codigo) != 'concluido':
            try:
                fechamento.marcar(dia,'painel',estado='pendente',mensagem='Atualização das baixas em andamento.')
                resultado = baixas.executar(dia,[codigo],xml.PASTA_PADRAO,refresh=False)
                fechamento.marcar(dia,'baixas',codigo,estado='aguardando' if resultado['pendentes'] else 'concluido',
                                  quantidade=resultado['conferidas'],
                                  mensagem=(f"{resultado['pendentes']} baixa(s) aguardam captura ou conferência de valores/status."
                                            if resultado['pendentes'] else 'Liquidações e parcelas conferidas; baixas aplicadas sem duplicação.'))
                mudou = True
            except ImportacaoErro:
                fechamento.marcar(dia,'baixas',codigo,estado='erro',mensagem='Arquivo de liquidação exige conferência; valores preservados.')
    # Recebíveis/baixas não dependem do Pix; vendas só avançam com o dia inteiro.
    if fechamento.obter(dia,'vendas') != 'concluido':
        try:
            arquivos = fila.arquivos(documento,dia)
            pronto = pix.escolher_arquivo(arquivos)
            if not pronto and recuperar_downloads:
                fila.recuperar_download(documento,dia)
                arquivos = fila.arquivos(documento,dia)
                pronto = pix.escolher_arquivo(arquivos)
            if not pronto and not arquivos and consultar and orcamento['pix'] > 0 and not controle.obter('pix',documento,dia):
                orcamento['pix'] -= 1
                pedir_pix(controle,fila,variavel('STONE_CONCILIACAO_API_KEY'),documento,dia)
                arquivos = fila.aguardar([(documento,dia)],None,aguardar)
                recebido = arquivos.get((documento,dia))
                pronto = recebido if recebido and recebido.conteudo is not None and not recebido.erro else None
            if not pronto or len(prontos) != len(codigos):
                fechamento.marcar(dia,'vendas',estado='aguardando',mensagem='Aguardando XML e Pix íntegros do mesmo dia; pedidos existentes não serão repetidos.')
            else:
                fechamento.marcar(dia,'painel',estado='pendente',mensagem='Vendas recebidas; atualização do painel pendente.')
                importar('api_stone_vendas.py',dia,codigos)
                fechamento.marcar(dia,'vendas',mensagem='Cartão e Pix conferidos e conciliados com a Saipos já no banco.')
                mudou = True
        except ImportacaoErro:
            fechamento.marcar(dia,'vendas',estado='erro',mensagem=controle.diagnostico('pix',documento,dia)
                              if not pix.escolher_arquivo(fila.arquivos(documento,dia)) else 'Cartão ou Pix contém evento/layout ainda não validado; valores preservados.')
    tem_dados = fechamento.obter(dia,'vendas') == 'concluido' or any(
        fechamento.obter(dia,e,c)=='concluido' for c in codigos for e in ('recebiveis','baixas'))
    if mudou or (tem_dados and fechamento.obter(dia,'painel') != 'concluido'):
        try:
            atualizar_painel()
            fechamento.marcar(dia,'painel',mensagem='Dados do painel atualizados após as cargas disponíveis.')
        except ImportacaoErro:
            fechamento.marcar(dia,'painel',estado='erro',mensagem='Dados preservados; atualização do painel será retomada na próxima rodada.')


def fluxo():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dia", type=date.fromisoformat)
    parser.add_argument("--aguardar", type=int, choices=range(0,36), default=35)
    parser.add_argument("--dry-run", action="store_true", help="confere sem consultar a Stone nem gravar")
    parser.add_argument('--somente-cache',action='store_true',help='retoma pendências sem qualquer consulta bancária ou download')
    parser.add_argument('--recuperar-downloads',action='store_true',help='retoma GET limitado do endereço Pix já recebido, sem novo pedido')
    parser.add_argument('--saude',action='store_true',help='somente leitura do fechamento; dispensa chave Stone')
    op = parser.parse_args()
    carregar_env()
    hoje = datetime.now(pix.FUSO_LOCAL).date()
    codigos = xml.resolver_stonecodes(None)
    if op.saude or op.dry_run:
        resumo = imprimir_saude(codigos)
        if op.saude and any(d['atrasado'] for d in resumo['dias']):
            raise ErroOperacional('há fechamento atrasado; conferir etapas no Status')
        return
    if op.somente_cache and op.recuperar_downloads:
        raise ErroOperacional('--somente-cache não permite download, mesmo de endereço já recebido')
    dias = [op.dia] if op.dia else dias_esperados(hoje)
    if not dias:
        return
    # O limite de download em lote não se aplica ao calendário de saúde:
    # daqui a anos ainda é necessário preservar lacunas antigas.
    if op.dia:
        xml.dias_do_periodo(op.dia,op.dia,hoje)
    if dias[0] < INICIO:
        raise ErroOperacional('fechamento automático começa em 21/10/2026; histórico deve ser tratado separadamente')
    controle, fila = Controle(), pix.FilaPix()
    fechamento = Fechamento()
    try:
        with controle.conn, controle.conn.cursor() as cur:
            cur.execute("select pg_try_advisory_lock(hashtext('sirfisher-stone-fechamento'))")
            if not cur.fetchone()[0]:
                raise ErroOperacional('outra rodada de fechamento já está em andamento')
        documentos = fila.documentos()
        if len(documentos) != 1:
            raise ErroOperacional("é necessário um único CNPJ validado")
        documento = documentos[0]
        orcamento = {'xml':1,'pix':1}
        completos = {(r['dia'],r['etapa'],r['identificador']) for r in fechamento.registros() if r['estado']=='concluido'}
        pix_novos = fila.dias_prontos_nao_processados(documento)
        for dia in dias:
            etapas = [('vendas',''),('painel','')]+[(e,c) for c in codigos for e in ('recebiveis','baixas')]
            if dia in pix_novos and (dia,'vendas','') in completos:
                fechamento.marcar(dia,'vendas',estado='pendente',mensagem='Novo arquivo Pix recebido; conferência será retomada.')
                completos.discard((dia,'vendas',''))
            if all((dia,e,c) in completos for e,c in etapas):
                continue
            processar_dia(dia,codigos,documento,controle,fila,fechamento,consultar=not op.somente_cache,
                          orcamento=orcamento,aguardar=op.aguardar,recuperar_downloads=op.recuperar_downloads)
        print('STONE_ROTINA_OK rodada concluída; confira fechamento e pendências no Status.')
    finally:
        fechamento.fechar()
        controle.fechar()
        fila.fechar()
    resumo = imprimir_saude(codigos)
    if any(d['atrasado'] for d in resumo['dias']):
        raise ErroOperacional('há dias que ultrapassaram o prazo D+1; conferir pendências no Status')


if __name__ == "__main__":
    sys.exit(executar_com_saida(fluxo))
