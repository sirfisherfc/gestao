#!/usr/bin/env python3
"""Mede o desempenho do painel no banco, sempre em transações somente leitura.

Cada consulta roda como o navegador a executaria: papel ``authenticated`` com
as claims de um admin ativo, dentro de ``begin read only`` e ``rollback``.
Nada é gravado; a saída traz só tempos, contagens e hashes, nunca valores.

Uso (na pasta ``gestao``, com ``DATABASE_URL`` no ``.env``)::

    python scripts/diagnostico/medir_desempenho.py consultas [--repeticoes 2] [--filtro regex]
    python scripts/diagnostico/medir_desempenho.py paginas [--repeticoes 3] [--paginas index,caixa]
    python scripts/diagnostico/medir_desempenho.py checksums public.painel_resumo_mensal ...
    python scripts/diagnostico/medir_desempenho.py pgss salvar retrato.json
    python scripts/diagnostico/medir_desempenho.py pgss delta retrato.json
    python scripts/diagnostico/medir_desempenho.py logs [--horas 2] [--aberturas 8]

``consultas``: tempo de execução no servidor (EXPLAIN ANALYZE) de cada consulta
das páginas prioritárias. ``paginas``: reproduz as rodadas sequenciais de cada
página com a mesma concorrência do navegador e mede o relógio de parede (uma
ida e volta por consulta). ``checksums``: md5 do resultado ordenado, para provar
igualdade antes e depois de uma mudança. ``pgss``: retrato e delta do
``pg_stat_statements`` sem resetar as estatísticas. ``logs``: tempo real de cada
requisição dos navegadores, pelos logs da API do Supabase, agrupado por
abertura de página (separa o tempo no PostgREST do tempo de rede e gateway).
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "importacao"))


def _consultas() -> dict[str, str]:
    hoje = datetime.now(ZoneInfo("America/Fortaleza")).date()
    ini = hoje.replace(day=1)
    prox = (ini + timedelta(days=32)).replace(day=1)
    ant = (ini - timedelta(days=1)).replace(day=1)
    mes, mes_ant = ini.strftime("%Y-%m"), ant.strftime("%Y-%m")
    acionaveis = "('venda sem recebível','recebível sem venda','valor diverge','cancelado/estornado')"
    return {
        "resumo_mensal": "select * from app_painel_resumo_mensal order by mes",
        "resumo_mensal_colunas": "select ano_mes,faturamento,faturamento_proj from app_painel_resumo_mensal order by ano_mes",
        "dre_cascata": "select * from app_painel_dre_cascata order by mes",
        "proj_desp_fixa": "select dia,valor from app_projecao_despesa_fixa",
        "proj_desp_direta": "select dia,valor from app_projecao_despesa_direta",
        "composicao": "select * from app_painel_composicao_despesa",
        "saldo_fim_mes": "select * from app_painel_saldo_fim_mes order by mes",
        "saldo_atual": "select * from app_painel_saldo_atual",
        "margem": "select ano_mes,mc_perc from app_painel_margem_contribuicao",
        "ultima_carga": "select ultima from app_painel_ultima_carga",
        "cargas": "select * from app_painel_cargas limit 50",
        "diario": f"select dia,venda_dia,meta_dia from app_painel_diario where mes='{ini}' order by dia",
        "fluxo_curva": f"select * from app_painel_fluxo_caixa where dia>='{ini - timedelta(days=183)}' and dia<='{prox + timedelta(days=89)}' order by dia",
        "saldo_por_conta": "select * from app_painel_saldo_por_conta",
        "proj_desp_fixa_mes": f"select dia,valor from app_projecao_despesa_fixa where dia>='{ini}' and dia<'{prox}'",
        "proj_desp_direta_mes": f"select dia,valor from app_projecao_despesa_direta where dia>='{ini}' and dia<'{prox}'",
        "receb_conhecido_mes": f"select dia,valor from app_recebimento_conhecido where dia>='{ini}' and dia<'{prox}'",
        "receb_projetado_mes": f"select dia,valor from app_recebimento_projetado where dia>='{ini}' and dia<'{prox}'",
        "g_resumo": "select * from app_gerente_resumo_mensal order by ano_mes",
        "g_cascata": f"select * from app_gerente_dre_cascata_perc where ano_mes='{mes}'",
        "g_gasto_grupo": f"select grupo,participacao_perc from app_gerente_gasto_grupo where ano_mes='{mes}'",
        "g_meta_diaria": f"select dia,venda_dia,meta_dia from app_gerente_meta_diaria where mes='{ini}' order by dia",
        "g_mov_hora": f"select hora,qtd from app_gerente_movimento_hora where ano_mes='{mes}' order by hora",
        "g_saldo_var": f"select ano_mes,variacao_perc,previsao_bonificacao from app_gerente_saldo_variacao where ano_mes='{mes}'",
        "g_ultima": "select ultima from app_gerente_ultima_carga",
        "ranking_fornecedor": f"select * from listar_ranking_fornecedor('{mes}', 6)",
        "desp_mes_atual": f"select * from app_mv_despesa_mensal where ano_mes='{mes}' order by mes,grupo,categoria,fornecedor limit 1000",
        "desp_mes_anterior": f"select * from app_mv_despesa_mensal where ano_mes='{mes_ant}' order by mes,grupo,categoria,fornecedor limit 1000",
        "calendario": f"select * from listar_calendario_financeiro('{ini}')",
        "resumo_corte_caixa": "select * from resumo_corte_caixa()",
        "conc_stone_resumo": "select * from app_conciliacao_stone_resumo_mensal",
        "conc_stone": f"select * from app_conciliacao_stone where mes_referencia>='{ini}' and mes_referencia<'{prox}' and situacao in {acionaveis} order by mes_referencia desc limit 300",
        "conc_saipos_dia": f"select * from app_conciliacao_saipos_dia where data_turno>='{ini}' and data_turno<'{prox}' order by data_turno desc",
        "conc_saipos_pend": f"select * from app_conciliacao_saipos_pendencia where data_turno>='{ini}' and data_turno<'{prox}' order by lado, horario desc limit 300",
        "conf_operacional": "select * from app_configuracao_operacional()",
        "papel": "select papel_usuario_atual()",
        "permissoes": "select pagina, papeis from pagina_permissao",
    }


# Rodadas sequenciais de cada página, como o código das páginas as dispara.
PAGINAS = {
    "index": [["resumo_mensal", "dre_cascata", "proj_desp_fixa", "proj_desp_direta", "composicao",
               "saldo_fim_mes", "saldo_atual", "margem", "ultima_carga", "cargas"],
              ["diario"]],
    "caixa": [["saldo_atual", "saldo_fim_mes", "saldo_por_conta"],
              ["fluxo_curva", "receb_conhecido_mes", "receb_projetado_mes", "proj_desp_fixa_mes",
               "proj_desp_direta_mes", "ultima_carga", "cargas"]],
    "gerente": [["g_resumo", "g_meta_diaria", "g_gasto_grupo", "g_mov_hora", "g_saldo_var",
                 "g_cascata", "g_ultima"]],
    "dre": [["dre_cascata", "resumo_mensal_colunas", "proj_desp_fixa", "proj_desp_direta"],
            ["ultima_carga", "cargas"]],
    "despesas": [["composicao", "resumo_mensal_colunas", "proj_desp_fixa", "proj_desp_direta"],
                 ["ranking_fornecedor", "desp_mes_atual", "desp_mes_anterior", "ultima_carga", "cargas"]],
    "calendario": [["calendario", "resumo_corte_caixa"]],
    "conciliacao": [["conc_stone_resumo"], ["conc_stone", "conc_saipos_dia", "conc_saipos_pend"]],
}
AUTH_FRIO = [["conf_operacional", "papel", "permissoes"]]


def conectar(autocommit: bool = False):
    import psycopg2

    import importacao_core

    conn = psycopg2.connect(importacao_core._database_url(), application_name="sirfisher_medir_desempenho")
    conn.autocommit = autocommit
    return conn


def admin_ativo(cur) -> str:
    cur.execute("select user_id::text from perfil_usuario where papel = 'admin' and ativo limit 1")
    linha = cur.fetchone()
    if not linha:
        raise SystemExit("Nenhum admin ativo para simular o acesso.")
    return linha[0]


def prefixo(uid: str) -> str:
    claims = json.dumps({"sub": uid, "role": "authenticated"})
    return ("begin read only; set local role authenticated; "
            f"select set_config('request.jwt.claims', '{claims}', true); ")


def cmd_consultas(args) -> None:
    consultas = _consultas()
    conn = conectar(autocommit=True)
    cur = conn.cursor()
    pre = prefixo(admin_ativo(cur))
    for nome, sql in consultas.items():
        if args.filtro and not re.search(args.filtro, nome):
            continue
        tempos, linhas = [], None
        for _ in range(args.repeticoes):
            cur.execute(pre + "explain (analyze, format json) " + sql)
            plano = cur.fetchone()[0][0]
            cur.execute("rollback")
            tempos.append(plano["Execution Time"] + plano.get("Planning Time", 0))
            linhas = plano["Plan"].get("Actual Rows")
        print(f"{nome:24s} melhor {min(tempos):8.0f} ms  pior {max(tempos):8.0f} ms  linhas {linhas}", flush=True)


def cmd_paginas(args) -> None:
    consultas = _consultas()
    boot = conectar(autocommit=True)
    pre = prefixo(admin_ativo(boot.cursor()))
    conexoes = [conectar(autocommit=True) for _ in range(10)]

    def rodar(i_nome):
        i, nome = i_nome
        cur = conexoes[i].cursor()
        t0 = time.perf_counter()
        cur.execute(pre + consultas[nome])
        cur.fetchall()
        dt = time.perf_counter() - t0
        cur.execute("rollback")
        return dt

    def pagina(rodadas):
        tempos = []
        with ThreadPoolExecutor(max_workers=len(conexoes)) as ex:
            for rodada in rodadas:
                t0 = time.perf_counter()
                list(ex.map(rodar, enumerate(rodada)))
                tempos.append(time.perf_counter() - t0)
        return tempos

    for i in range(len(conexoes)):
        rodar((i, "papel"))  # aquece as conexões, como o pool do PostgREST
    alvo = args.paginas.split(",") if args.paginas else list(PAGINAS)
    saida = {}
    for nome in alvo:
        voltas = []
        for _ in range(args.repeticoes):
            voltas.append(pagina(PAGINAS[nome]))
            time.sleep(1)
        totais = sorted(sum(v) for v in voltas)
        auth = sum(pagina(AUTH_FRIO))
        saida[nome] = {"mediana_s": round(statistics.median(totais), 2), "melhor_s": round(totais[0], 2),
                       "pior_s": round(totais[-1], 2), "rodadas": len(PAGINAS[nome]),
                       "consultas": sum(len(r) for r in PAGINAS[nome]), "auth_frio_s": round(auth, 2)}
        s = saida[nome]
        print(f"{nome:12s} rodadas {s['rodadas']}  consultas {s['consultas']:2d}  dados: mediana {s['mediana_s']:5.2f} s "
              f"(melhor {s['melhor_s']:.2f}, pior {s['pior_s']:.2f})  acesso em aba nova {s['auth_frio_s']:.2f} s", flush=True)
    if args.saida:
        Path(args.saida).write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")


def cmd_checksums(args) -> None:
    conn = conectar()
    cur = conn.cursor()
    for rel in args.relacoes:
        if not re.fullmatch(r"[a-z_]+\.[a-z0-9_]+", rel):
            raise SystemExit(f"Relação inválida: {rel}")
        cur.execute("begin read only")
        cur.execute(f"select md5(string_agg(t::text, '|' order by t::text)), count(*) from {rel} t")
        md5, n = cur.fetchone()
        conn.rollback()
        print(f"{rel:45s} linhas {n:7d}  md5 {md5}")


PGSS_SQL = r"""
select s.queryid::text, r.rolname, s.calls, s.total_exec_time, s.max_exec_time,
       left(regexp_replace(s.query, '\s+', ' ', 'g'), 400)
from pg_stat_statements s join pg_roles r on r.oid = s.userid
where r.rolname in ('authenticated', 'postgres', 'service_role', 'anon')
  and s.query ~* '(app_[a-z_]+|listar_[a-z_]+|importar_csv_stone|consultar_recalculo|papel_usuario_atual|pagina_permissao|refresh_painel|resumo_corte_caixa|processar_fila)'
  and s.query !~* '^\s*(explain|begin)'
"""
ROTULO = re.compile(r'(app_[a-z_]+|listar_[a-z_]+|importar_csv_stone|consultar_recalculo_saldo|papel_usuario_atual|'
                    r'pagina_permissao|refresh_painel[a-z_]*|resumo_corte_caixa|processar_fila_recalculo_saldo)')


def _pgss_ler() -> dict:
    conn = conectar()
    cur = conn.cursor()
    cur.execute(PGSS_SQL)
    linhas = {f"{q}|{papel}": {"papel": papel, "calls": calls, "total": total, "max": mx, "q": texto}
              for q, papel, calls, total, mx, texto in cur.fetchall()}
    conn.rollback()
    return linhas


def cmd_pgss(args) -> None:
    if args.modo == "salvar":
        Path(args.arquivo).write_text(json.dumps(_pgss_ler(), default=float), encoding="utf-8")
        print(f"retrato salvo em {args.arquivo}")
        return
    antes = json.loads(Path(args.arquivo).read_text(encoding="utf-8"))
    delta = {}
    for chave, linha in _pgss_ler().items():
        base = antes.get(chave, {"calls": 0, "total": 0.0})
        chamadas = linha["calls"] - base["calls"]
        if chamadas <= 0:
            continue
        achado = ROTULO.search(linha["q"])
        rotulo = (achado.group(1) if achado else linha["q"][:40], linha["papel"])
        d = delta.setdefault(rotulo, {"calls": 0, "total": 0.0})
        d["calls"] += chamadas
        d["total"] += linha["total"] - base["total"]
    for (rotulo, papel), d in sorted(delta.items(), key=lambda x: -x[1]["total"]):
        print(f"{rotulo:42s} {papel:13s} chamadas {d['calls']:6d}  média {d['total'] / d['calls']:8.0f} ms")


LOGS_SQL = """
select timestamp,
  log_attributes['request.method'] as metodo,
  log_attributes['request.path'] as caminho,
  toInt32OrZero(log_attributes['response.status_code']) as status,
  toInt32OrZero(log_attributes['response.origin_time']) as origem,
  toInt32OrZero(log_attributes['response.headers.x_envoy_upstream_service_time']) as upstream
from logs
where source = 'edge_logs'
  and log_attributes['request.path'] like '/rest/v1/%'
  and log_attributes['request.headers.x_client_info'] like '{cliente}%'
order by timestamp
limit 5000
"""


def cmd_logs(args) -> None:
    """Tempo real das requisições dos navegadores, pelos logs da API do Supabase.

    Usa a credencial de gestão já configurada no workspace (SUPABASE_ACCESS_TOKEN
    ou reservas/.env.local) e só lê: método, caminho, status e tempos. IP,
    usuário e cabeçalhos de autenticação não são consultados.
    """
    import urllib.parse
    import urllib.request
    from datetime import timezone

    sys.path.insert(0, str(ROOT.parent / "site" / "tools" / "analytics"))
    from supabase_credentials import PORTAL_REF, access_token

    versao = re.search(r"supabase-js@([0-9.]+)", (ROOT / "index.html").read_text(encoding="utf-8"))
    cliente = "supabase-js/" + (versao.group(1) if versao else "")
    fim = datetime.now(timezone.utc)
    ini = fim - timedelta(hours=min(args.horas, 24))
    fmt = "%Y-%m-%dT%H:%M:%S.000Z"
    query = urllib.parse.urlencode({"sql": LOGS_SQL.format(cliente=cliente),
                                    "iso_timestamp_start": ini.strftime(fmt), "iso_timestamp_end": fim.strftime(fmt)})
    pedido = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PORTAL_REF}/analytics/endpoints/logs?{query}",
        headers={"Authorization": "Bearer " + access_token()})
    with urllib.request.urlopen(pedido, timeout=90) as resposta:
        dados = json.load(resposta)
    if dados.get("error"):
        raise SystemExit("Logs indisponíveis: " + json.dumps(dados["error"])[:300])
    linhas = dados.get("result", [])
    momento = lambda l: datetime.fromisoformat(str(l["timestamp"]).replace("Z", ""))
    grupos: list[list[dict]] = []
    for linha in linhas:
        if not grupos or (momento(linha) - momento(grupos[-1][-1])).total_seconds() > 3:
            grupos.append([])
        grupos[-1].append(linha)
    fora = lambda l: max(0, l["origem"] - l["upstream"]) if l["upstream"] > 0 else None
    for grupo in grupos[-args.aberturas:]:
        t0 = momento(grupo[0])
        fim_grupo = max((momento(l) - t0).total_seconds() * 1000 + l["origem"] for l in grupo)
        print(f"\n=== {str(grupo[0]['timestamp'])[:19]} UTC  {len(grupo)} requisições  até a última resposta: {fim_grupo:.0f} ms")
        for l in grupo:
            dt = (momento(l) - t0).total_seconds() * 1000
            extra = fora(l)
            print(f"  +{dt:6.0f} ms  {l['metodo']:7s} {l['caminho'][:50]:50s} {l['status']}  total {l['origem']:5d} ms"
                  + (f"  PostgREST {l['upstream']:5d} ms  fora {extra:5d} ms" if extra is not None else ""))
    valores = sorted(v for v in (fora(l) for l in linhas) if v is not None)
    if valores:
        p = lambda q: valores[min(len(valores) - 1, int(q * len(valores)))]
        acima = 100 * sum(1 for v in valores if v > 300) / len(valores)
        print(f"\nfora do PostgREST (rede e gateway): mediana {p(.5)} ms, p90 {p(.9)} ms, p99 {p(.99)} ms, acima de 300 ms {acima:.1f}%")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("consultas")
    p.add_argument("--repeticoes", type=int, default=2)
    p.add_argument("--filtro")
    p.set_defaults(func=cmd_consultas)
    p = sub.add_parser("paginas")
    p.add_argument("--repeticoes", type=int, default=3)
    p.add_argument("--paginas")
    p.add_argument("--saida")
    p.set_defaults(func=cmd_paginas)
    p = sub.add_parser("checksums")
    p.add_argument("relacoes", nargs="+")
    p.set_defaults(func=cmd_checksums)
    p = sub.add_parser("pgss")
    p.add_argument("modo", choices=["salvar", "delta"])
    p.add_argument("arquivo")
    p.set_defaults(func=cmd_pgss)
    p = sub.add_parser("logs")
    p.add_argument("--horas", type=int, default=2)
    p.add_argument("--aberturas", type=int, default=8)
    p.set_defaults(func=cmd_logs)
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
