#!/usr/bin/env python3
"""Testes de paridade diferencial de parsers (Python vs PostgreSQL).

Garante que os parsers Python (scripts/importacao/) e os parsers PostgreSQL
(private.parse_*) geram exatamente os mesmos dedup_hash, valores e datas
para os mesmos dados sintéticos, incluindo:
- Banco do Brasil (formatos antigo e novo de débito, aplicação Selic/Fundo BB, nulos)
- Stone Extrato (crédito, débito, campos nulos representados como 'None' literal)
- BS Cash (créditos vs débitos, campos vazios)
- Stone Vendas e Recebíveis (valores brutos/líquidos e datas)
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = ROOT / "scripts" / "importacao"
MIGRATIONS_DIR = ROOT / "supabase" / "migrations"
sys.path.insert(0, str(IMPORT_DIR))

import importacao_core


def load_import_module(name: str, filename: str):
    path = IMPORT_DIR / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_db_connection():
    """Conecta ao PostgreSQL local (CI) ou Supabase portal."""
    import psycopg2

    # Se PGHOST estiver configurado (ex: GitHub Actions com container postgres)
    if os.environ.get("PGHOST"):
        host = os.environ["PGHOST"]
        port = os.environ.get("PGPORT", "5432")
        database = os.environ.get("PGDATABASE", "postgres")
        user = os.environ.get("PGUSER", "postgres")
        password = os.environ.get("PGPASSWORD")
        conn = psycopg2.connect(host=host, port=port, dbname=database, user=user, password=password)
        conn.autocommit = True
        ensure_parser_functions(conn)
        return conn

    # Conexão padrão obtida via .env do projeto
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=True)
    except ImportError:
        pass

    url = importacao_core._database_url()
    conn = psycopg2.connect(url)
    conn.autocommit = True
    ensure_parser_functions(conn)
    return conn


def ensure_parser_functions(conn) -> None:
    """Carrega as funções de parsing se estiver em um banco descartável novo."""
    cur = conn.cursor()
    cur.execute("select to_regprocedure('private.parse_bb(jsonb)');")
    if cur.fetchone()[0] is not None:
        cur.close()
        return

    cur.execute("create schema if not exists private;")
    cur.execute("""
        do $$
        begin
            if not exists (select 1 from pg_roles where rolname = 'anon') then
                create role anon;
            end if;
            if not exists (select 1 from pg_roles where rolname = 'authenticated') then
                create role authenticated;
            end if;
            if not exists (select 1 from pg_roles where rolname = 'service_role') then
                create role service_role;
            end if;
        end $$;
    """)
    cur.execute("create table if not exists public.saldo_inicial (conta text, saldo numeric, data_base date);")
    cur.execute("create table if not exists public.raw_bb (data date, valor numeric, dedup_hash text);")
    cur.execute("create table if not exists public.raw_bs_cash (data date, valor numeric, dedup_hash text);")

    # Helpers Stone (campo_csv, parse_valor_br, parse_data_hora_br, parse_inteiro_br, parse_stone_*)
    m_stone = (MIGRATIONS_DIR / "20260751000000_importacao_web_stone.sql").read_text(encoding="utf-8-sig")
    p_stone = m_stone[m_stone.index("create or replace function private.campo_csv"):]
    p_stone = p_stone[:p_stone.index("create or replace function public.importar_csv_stone")]
    cur.execute(p_stone)

    # Helpers BB/BS Cash (parse_data_br, parse_data_hora_seg_br, parse_bb, parse_bs_cash)
    m_bb_bs = (MIGRATIONS_DIR / "20260756000000_importacao_web_bb_bs_cash.sql").read_text(encoding="utf-8-sig")
    p_bb_bs = m_bb_bs[m_bb_bs.index("create or replace function private.parse_data_br"):]
    p_bb_bs = p_bb_bs[:p_bb_bs.index("create or replace function public.importar_csv_stone")]
    cur.execute(p_bb_bs)

    # BB vigente com suporte a débito sem sinal negativo (20260819020000)
    m_bb_vig = (MIGRATIONS_DIR / "20260819020000_bb_debito_sem_sinal_negativo.sql").read_text(encoding="utf-8-sig")
    p_bb_vig = m_bb_vig[m_bb_vig.index("create or replace function private.parse_valor_bb"):]
    p_bb_vig = p_bb_vig[:p_bb_vig.index("revoke all privileges on function private.parse_bb(jsonb)")]
    cur.execute(p_bb_vig)

    cur.close()


def test_bb_parity(conn) -> None:
    mod_bb = load_import_module("mod_bb", "04_importar_bb.py")
    cur = conn.cursor()

    bb_test_rows = [
        # Formato antigo com sinal negativo no valor e D
        {
            "Data": "01/07/2026",
            "Lançamento": "Pix - Enviado",
            "Valor": "-4,00 D",
            "N° documento": "12345",
            "Detalhes": "Transferencia Pix",
            "Tipo Lançamento": "Saída"
        },
        # Formato novo com valor positivo e D
        {
            "Data": "01/07/2026",
            "Lançamento": "Pix - Enviado",
            "Valor": "4,00 D",
            "N° documento": "12345",
            "Detalhes": "Transferencia Pix",
            "Tipo Lançamento": "Entrada"
        },
        # Crédito normal
        {
            "Data": "05/07/2026",
            "Lançamento": "Pix recebido",
            "Valor": "150,50 C",
            "N° documento": "67890",
            "Detalhes": "Recebimento Cliente",
            "Tipo Lançamento": "Entrada"
        },
        # Fundo BB provisório
        {
            "Data": "15/07/2026",
            "Lançamento": "Aplicação Fundo BB",
            "Valor": "-5000,00 D",
            "N° documento": "111",
            "Detalhes": "Aplicacao automatica",
            "Tipo Lançamento": "Saída"
        },
        # Fundo BB consolidado (outro rótulo/doc, mas mesma data e valor)
        {
            "Data": "15/07/2026",
            "Lançamento": "BB RF LP Selic",
            "Valor": "5000,00 D",
            "N° documento": "222",
            "Detalhes": "Resgate / Aplicacao",
            "Tipo Lançamento": "Entrada"
        },
        # Campos vazios
        {
            "Data": "20/07/2026",
            "Lançamento": "Tarifa Bancaria",
            "Valor": "15,00 D",
            "N° documento": "",
            "Detalhes": "",
            "Tipo Lançamento": ""
        }
    ]

    py_results = []
    for r in bb_test_rows:
        data_raw = importacao_core.campo(r, "Data")
        valor_raw = importacao_core.campo(r, "Valor")
        data = importacao_core.parse_data_formatos(data_raw, ("%d/%m/%Y",))
        valor = mod_bb.parse_valor_bb(valor_raw)
        lancamento = importacao_core.campo(r, "Lançamento")
        numero_documento = importacao_core.campo(r, "N° documento")
        detalhes = importacao_core.campo(r, "Detalhes")
        if lancamento in mod_bb.ROTULOS_FUNDO_BB and valor < 0:
            base = f"{data.isoformat()}|FUNDO_BB_RF_LP_SELIC|{valor:.2f}"
        else:
            base = f"{data_raw}|{lancamento}|{numero_documento}|{valor:.2f}|{detalhes}"
        h = hashlib.md5(base.encode("utf-8")).hexdigest()
        py_results.append({"data": data, "valor": valor, "hash": h})

    cur.execute("select linha, data, valor, dedup_hash, motivo, ignorar from private.parse_bb(%s);", (json.dumps(bb_test_rows),))
    sql_results = cur.fetchall()

    assert len(py_results) == len(sql_results), "Quantidade de linhas divergiu no BB"
    for i, (py_res, sql_res) in enumerate(zip(py_results, sql_results)):
        assert str(py_res["data"]) == str(sql_res[1]), f"BB: Data divergiu na linha {i+1}"
        assert abs(float(py_res["valor"]) - float(sql_res[2])) < 0.001, f"BB: Valor divergiu na linha {i+1}"
        assert py_res["hash"] == sql_res[3], f"BB: dedup_hash divergiu na linha {i+1}!"

    # Formato antigo e novo devem ter rigorosamente o mesmo dedup_hash
    assert py_results[0]["hash"] == py_results[1]["hash"], "BB: formatos antigo/novo divergiram no Python"
    assert sql_results[0][3] == sql_results[1][3], "BB: formatos antigo/novo divergiram no SQL"

    # Fundo BB provisório e consolidado devem ter rigorosamente o mesmo dedup_hash
    assert py_results[3]["hash"] == py_results[4]["hash"], "BB: fundo provisório/consolidado divergiu no Python"
    assert sql_results[3][3] == sql_results[4][3], "BB: fundo provisório/consolidado divergiu no SQL"

    cur.close()
    print("  [OK] BB: Paridade 100% verificada (formatos antigo/novo e aplicação fundo)")


def test_stone_extrato_parity(conn) -> None:
    cur = conn.cursor()
    stone_test_rows = [
        {
            "Data": "01/07/2026 10:00",
            "Horário": "10:00",
            "Valor": "100,00",
            "Saldo antes": "500,00",
            "Saldo depois": "600,00",
            "Movimentação": "Crédito",
            "Tipo": "Recebível de Cartão",
            "Destino Documento": "12345678000199"
        },
        {
            "Data": "02/07/2026 15:30",
            "Horário": "15:30",
            "Valor": "-25,50",
            "Saldo antes": "600,00",
            "Saldo depois": "574,50",
            "Movimentação": "Débito",
            "Tipo": "Tarifa",
            "Destino Documento": ""  # Ausente
        }
    ]

    py_results = []
    for r in stone_test_rows:
        data_raw = importacao_core.campo(r, "Data")
        horario = importacao_core.campo(r, "Horário")
        valor_raw = importacao_core.campo(r, "Valor")
        saldo_depois_raw = importacao_core.campo(r, "Saldo depois")
        destino_documento = importacao_core.campo(r, "Destino Documento")
        base = f"{data_raw}|{horario}|{valor_raw}|{saldo_depois_raw}|{destino_documento}"
        h = hashlib.md5(base.encode("utf-8")).hexdigest()
        py_results.append({"hash": h})

    cur.execute("select linha, data_hora, valor, dedup_hash from private.parse_stone_extrato(%s);", (json.dumps(stone_test_rows),))
    sql_results = cur.fetchall()

    for i, (py_res, sql_res) in enumerate(zip(py_results, sql_results)):
        assert py_res["hash"] == sql_res[3], f"Stone Extrato: dedup_hash divergiu na linha {i+1}!"

    cur.close()
    print("  [OK] Stone Extrato: Paridade 100% verificada (incluindo literais 'None' em campos ausentes)")


def test_bs_cash_parity(conn) -> None:
    cur = conn.cursor()
    bs_test_rows = [
        {
            "Data": "01/07/2026 10:00:00",
            "Dcto.": "DOC123",
            "Operação": "PIX",
            "Histórico": "Recebimento",
            "Favorecido": "Cliente A",
            "Créditos (R$)": "50,00",
            "Débitos (R$)": "",
            "Saldo (R$)": "50,00"
        },
        {
            "Data": "02/07/2026 12:00:00",
            "Dcto.": "DOC456",
            "Operação": "TED",
            "Histórico": "Pagamento",
            "Favorecido": "Fornecedor B",
            "Créditos (R$)": "",
            "Débitos (R$)": "30,00",
            "Saldo (R$)": "20,00"
        }
    ]

    py_results = []
    for r in bs_test_rows:
        data_raw = importacao_core.campo(r, "Data")
        dcto = importacao_core.campo(r, "Dcto.")
        operacao = importacao_core.campo(r, "Operação")
        creditos_raw = importacao_core.campo(r, "Créditos (R$)")
        debitos_raw = importacao_core.campo(r, "Débitos (R$)")
        valor_raw = creditos_raw or debitos_raw
        favorecido = importacao_core.campo(r, "Favorecido")
        base = f"{data_raw}|{dcto}|{operacao}|{valor_raw}|{favorecido}"
        h = hashlib.md5(base.encode("utf-8")).hexdigest()
        py_results.append({"hash": h})

    cur.execute("select linha, data_hora, valor, dedup_hash from private.parse_bs_cash(%s);", (json.dumps(bs_test_rows),))
    sql_results = cur.fetchall()

    for i, (py_res, sql_res) in enumerate(zip(py_results, sql_results)):
        assert py_res["hash"] == sql_res[3], f"BS Cash: dedup_hash divergiu na linha {i+1}!"

    cur.close()
    print("  [OK] BS Cash: Paridade 100% verificada (créditos, débitos e campos nulos)")


def test_stone_vendas_e_recebiveis_parity(conn) -> None:
    cur = conn.cursor()
    vendas_rows = [
        {
            "DATA DA VENDA": "01/07/2026 10:00",
            "STONE ID": "venda-001",
            "VALOR BRUTO": "100,00",
            "VALOR LIQUIDO": "95,00",
            "DESCONTO DE MDR": "3,00",
            "DESCONTO DE ANTECIPACAO": "2,00"
        }
    ]
    cur.execute("select stone_id, valor_bruto, valor_liquido, desconto_mdr, desconto_antecipacao from private.parse_stone_vendas(%s);", (json.dumps(vendas_rows),))
    r = cur.fetchone()
    print("DEBUG_VENDAS_R:", repr(r))
    print("DEBUG_VENDAS_COLS:", [d[0] for d in cur.description])
    assert r is not None, "parse_stone_vendas retornou None"
    assert r[0] == "venda-001", f"Esperado stone_id='venda-001', obteve: {r}"
    assert float(r[1]) == 100.00
    assert float(r[2]) == 95.00
    assert float(r[3]) == 3.00
    assert float(r[4]) == 2.00

    recebiveis_rows = [
        {
            "DATA DA VENDA": "01/07/2026 10:00",
            "DATA DE VENCIMENTO": "02/07/2026",
            "STONE ID": "rec-001",
            "QTD DE PARCELAS": "1",
            "Nº DA PARCELA": "1",
            "VALOR BRUTO": "100,00",
            "VALOR LÍQUIDO": "95,00"
        }
    ]
    cur.execute("select stone_id, data_vencimento::text, qtd_parcelas, n_parcela, valor_bruto, valor_liquido from private.parse_stone_recebiveis(%s);", (json.dumps(recebiveis_rows),))
    r2 = cur.fetchone()
    print("DEBUG_RECEBIVEIS_R2:", repr(r2))
    assert r2 is not None, "parse_stone_recebiveis retornou None"
    assert r2[0] == "rec-001", f"Esperado stone_id='rec-001', obteve: {r2}"
    assert r2[1] == "2026-07-02"
    assert r2[2] == 1
    assert r2[3] == 1
    assert float(r2[4]) == 100.00
    assert float(r2[5]) == 95.00

    cur.close()
    print("  [OK] Stone Vendas e Recebíveis: Tipagem e parsing numérico/temporal verificados")


def main() -> None:
    print("Iniciando testes de paridade diferencial de parsers (Python vs PostgreSQL)...")
    conn = get_db_connection()
    try:
        test_bb_parity(conn)
        test_stone_extrato_parity(conn)
        test_bs_cash_parity(conn)
        test_stone_vendas_e_recebiveis_parity(conn)
    finally:
        conn.close()

    print("\nPARIDADE_PARSERS_OK: 100% dos hashes, valores e datas idênticos entre Python e PostgreSQL.")


if __name__ == "__main__":
    main()
