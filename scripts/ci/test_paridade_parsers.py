#!/usr/bin/env python3
"""Paridade diferencial dos importadores Python e parsers PostgreSQL.

As fixtures CSV sao sinteticas e passam por ``ler_csv()`` dos cinco
importadores reais. O resultado e comparado, campo a campo, com as funcoes
``private.parse_*`` vigentes, incluindo linhas aceitas, ignoradas e rejeitadas.

Seguranca de banco:

* por padrao, a conexao existente e colocada em modo somente leitura antes de
  qualquer consulta; nenhum objeto e criado;
* o bootstrap so e liberado com ``PARSER_PARITY_DISPOSABLE=1``, ``PGHOST``
  local explicito e banco chamado ``sirfisher_*_test``.

O bootstrap usa SQL versionado sem substituir literais em runtime. Assim, uma
incompatibilidade de migration com a versao do PostgreSQL nao fica mascarada
pelo proprio teste.
"""

from __future__ import annotations

import csv
from contextlib import redirect_stdout
from datetime import date, datetime
from decimal import Decimal
import importlib.util
from io import StringIO
import ipaddress
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = ROOT / "scripts" / "importacao"
MIGRATIONS_DIR = ROOT / "supabase" / "migrations"
SETUP_FIXTURE = ROOT / "scripts" / "ci" / "fixtures" / "paridade_parsers_setup.sql"
PARSER_FIX_MIGRATION = "20260906040000_parsers_web_paridade_python_pg15.sql"
DISPOSABLE_ENV = "PARSER_PARITY_DISPOSABLE"
DISPOSABLE_DATABASE = re.compile(r"^sirfisher_[a-z0-9_]*_test$")
FUNCTION_NAME = re.compile(r"^private\.parse_[a-z_]+$")

sys.path.insert(0, str(IMPORT_DIR))

import importacao_core


def load_import_module(name: str, filename: str):
    path = IMPORT_DIR / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Nao foi possivel carregar o importador {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_migration(name: str) -> str:
    return (MIGRATIONS_DIR / name).read_text(encoding="utf-8-sig")


def _sql_between(sql: str, start: str, end: str, source: str) -> str:
    try:
        start_at = sql.index(start)
        end_at = sql.index(end, start_at)
    except ValueError as exc:
        raise AssertionError(f"Marcadores da fixture mudaram em {source}") from exc
    return sql[start_at:end_at]


def _assert_no_newer_parser_definition() -> None:
    tracked = (
        "create or replace function private.campo_csv",
        "create or replace function private.parse_valor_br",
        "create or replace function private.parse_data_hora_br",
        "create or replace function private.parse_inteiro_br",
        "create or replace function private.parse_data_br",
        "create or replace function private.parse_data_hora_seg_br",
        "create or replace function private.parse_stone_extrato",
        "create or replace function private.parse_stone_vendas",
        "create or replace function private.parse_stone_recebiveis",
        "create or replace function private.parse_valor_bb",
        "create or replace function private.parse_bb",
        "create or replace function private.parse_bs_cash",
    )
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name <= PARSER_FIX_MIGRATION:
            continue
        sql = path.read_text(encoding="utf-8-sig").lower()
        if any(token in sql for token in tracked):
            raise AssertionError(
                "Atualize a fixture de paridade para a migration posterior: " + path.name
            )


def _bootstrap_statements() -> list[str]:
    """Monta a cadeia minima a partir das definicoes versionadas, sem rewrite."""
    _assert_no_newer_parser_definition()

    stone_name = "20260751000000_importacao_web_stone.sql"
    stone = _read_migration(stone_name)
    stone_parsers = _sql_between(
        stone,
        "create or replace function private.campo_csv",
        "create or replace function public.importar_csv_stone",
        stone_name,
    )

    performance_name = "20260752000000_importacao_web_cabe_no_timeout.sql"
    performance = _read_migration(performance_name)
    optimized_helpers = _sql_between(
        performance,
        "create or replace function private.parse_valor_br",
        "create or replace function public.solicitar_recalculo_saldo",
        performance_name,
    )

    bb_bs_name = "20260756000000_importacao_web_bb_bs_cash.sql"
    bb_bs = _read_migration(bb_bs_name)
    bb_bs_parsers = _sql_between(
        bb_bs,
        "create or replace function private.parse_data_br",
        "create or replace function public.importar_csv_stone",
        bb_bs_name,
    )

    bb_current_name = "20260819020000_bb_debito_sem_sinal_negativo.sql"
    bb_current = _read_migration(bb_current_name)
    bb_current_parser = _sql_between(
        bb_current,
        "create or replace function private.parse_valor_bb",
        "do $block$",
        bb_current_name,
    )

    parity_fix = _read_migration(PARSER_FIX_MIGRATION)
    parity_fix_body = _sql_between(
        parity_fix,
        "create or replace function private.campo_csv",
        "commit;",
        PARSER_FIX_MIGRATION,
    )

    return [
        SETUP_FIXTURE.read_text(encoding="utf-8"),
        stone_parsers,
        optimized_helpers,
        bb_bs_parsers,
        bb_current_parser,
        parity_fix_body,
    ]


def _connect():
    import psycopg2

    if os.environ.get("PGHOST"):
        kwargs = {
            "host": os.environ["PGHOST"],
            "port": os.environ.get("PGPORT", "5432"),
            "dbname": os.environ.get("PGDATABASE", "postgres"),
            "user": os.environ.get("PGUSER", "postgres"),
            "application_name": "sirfisher_parser_parity",
        }
        if os.environ.get("PGPASSWORD") is not None:
            kwargs["password"] = os.environ["PGPASSWORD"]
        return psycopg2.connect(**kwargs)

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass
    return psycopg2.connect(
        importacao_core._database_url(),
        application_name="sirfisher_parser_parity_read_only",
    )


def _assert_disposable_target(conn) -> None:
    if os.environ.get(DISPOSABLE_ENV) != "1":
        raise AssertionError(f"Bootstrap exige {DISPOSABLE_ENV}=1")

    host = os.environ.get("PGHOST", "")
    database = os.environ.get("PGDATABASE", "")
    if host not in {"localhost", "127.0.0.1", "::1"}:
        raise AssertionError("Bootstrap permitido somente com PGHOST local explicito")
    if not DISPOSABLE_DATABASE.fullmatch(database):
        raise AssertionError("Bootstrap exige banco descartavel chamado sirfisher_*_test")

    with conn.cursor() as cur:
        cur.execute(
            "select current_database(), host(inet_server_addr()), "
            "current_setting('server_version_num')::integer"
        )
        current_database, server_address, server_version = cur.fetchone()
    conn.rollback()

    if current_database != database:
        raise AssertionError("PGDATABASE nao corresponde ao banco conectado")
    # O alvo precisa ser um servidor efemero: loopback, ou o endereco privado de
    # um container de servico (o Postgres do CI se enxerga em 172.x, ainda que o
    # cliente chegue por 127.0.0.1). Qualquer endereco roteavel na internet, como
    # o banco de producao, continua bloqueado.
    if server_address is None:
        raise AssertionError("Bootstrap bloqueado: servidor conectado nao identificado")
    server_ip = ipaddress.ip_address(server_address)
    if not (server_ip.is_loopback or server_ip.is_private):
        raise AssertionError(
            f"Bootstrap bloqueado: servidor {server_address} nao e local nem privado"
        )
    if server_version < 150000:
        raise AssertionError("A fixture de paridade exige PostgreSQL 15 ou superior")


def _bootstrap_disposable_database(conn) -> None:
    _assert_disposable_target(conn)
    try:
        with conn.cursor() as cur:
            for statement in _bootstrap_statements():
                cur.execute(statement)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


REQUIRED_FUNCTIONS = (
    "private.parse_stone_extrato(jsonb)",
    "private.parse_stone_vendas(jsonb)",
    "private.parse_stone_recebiveis(jsonb)",
    "private.parse_bb(jsonb)",
    "private.parse_bs_cash(jsonb)",
)


def _assert_parser_functions_exist(conn) -> None:
    with conn.cursor() as cur:
        for signature in REQUIRED_FUNCTIONS:
            cur.execute("select to_regprocedure(%s);", (signature,))
            if cur.fetchone()[0] is None:
                raise AssertionError(
                    f"Funcao {signature} ausente. O modo somente leitura nao faz bootstrap; "
                    f"use um banco local descartavel com {DISPOSABLE_ENV}=1."
                )


def get_db_connection():
    marker = os.environ.get(DISPOSABLE_ENV)
    if marker not in {None, "", "0", "1"}:
        raise AssertionError(f"{DISPOSABLE_ENV} aceita apenas 0 ou 1")

    conn = _connect()
    if marker == "1":
        _bootstrap_disposable_database(conn)
        conn.autocommit = True
        mode = "PostgreSQL local descartavel"
    else:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("show transaction_read_only")
            if cur.fetchone()[0] != "on":
                raise AssertionError("A conexao de verificacao nao ficou somente leitura")
        mode = "banco existente em modo somente leitura"

    _assert_parser_functions_exist(conn)
    print(f"Banco: {mode}.")
    return conn


def _write_csv_fixture(
    directory: Path,
    label: str,
    module,
    rows: Sequence[Mapping[str, object]],
    *,
    delimiter: str,
    encoding: str,
) -> tuple[Path, list[dict[str, str]]]:
    row_headers = {key for row in rows for key in row}
    headers = sorted(set(module.CABECALHOS) | row_headers)
    path = directory / f"{label}.csv"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=headers,
            delimiter=delimiter,
            lineterminator="\n",
        )
        writer.writeheader()
        for values in rows:
            complete = {header: "" for header in headers}
            complete.update(values)
            writer.writerow(complete)

    with path.open(encoding=encoding, newline="") as handle:
        payload = [dict(row) for row in csv.DictReader(handle, delimiter=delimiter)]
    if len(payload) != len(rows):
        raise AssertionError(f"{label}: a fixture CSV alterou a quantidade de linhas")
    return path, payload


def _python_parse(module, path: Path) -> tuple[list[dict], int, tuple[date, date]]:
    options = importacao_core.OpcoesImportacao(
        arquivo=path,
        dry_run=True,
        periodo_inicio=None,
        periodo_fim=None,
    )
    with redirect_stdout(StringIO()):
        result = module.ler_csv(path, options)
    if len(result) == 3:
        records, ignored, period = result
    else:
        records, period = result
        ignored = 0
    return records, ignored, period


def _python_rejection(module, path: Path) -> str:
    options = importacao_core.OpcoesImportacao(
        arquivo=path,
        dry_run=True,
        periodo_inicio=None,
        periodo_fim=None,
    )
    try:
        with redirect_stdout(StringIO()):
            module.ler_csv(path, options)
    except importacao_core.ValidacaoErro as exc:
        return str(exc)
    raise AssertionError(f"{path.stem}: o importador Python aceitou fixture invalida")


def _sql_parse(conn, function: str, payload: Sequence[Mapping[str, str]]) -> list[dict]:
    from psycopg2.extras import Json, RealDictCursor

    if not FUNCTION_NAME.fullmatch(function):
        raise AssertionError(f"Nome de parser inesperado: {function}")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"select * from {function}(%s::jsonb) order by linha;",
            (Json(payload, dumps=lambda value: json.dumps(value, ensure_ascii=False)),),
        )
        return [dict(row) for row in cur.fetchall()]


def _assert_value(source: str, row_number: int, field: str, python_value, sql_value) -> None:
    if python_value is None or sql_value is None:
        if python_value is not sql_value:
            raise AssertionError(
                f"{source} linha {row_number}, {field}: Python={python_value!r}, SQL={sql_value!r}"
            )
        return

    if isinstance(python_value, float) or isinstance(sql_value, Decimal):
        equal = Decimal(str(python_value)) == Decimal(str(sql_value))
    elif isinstance(python_value, (date, datetime)):
        equal = python_value == sql_value
    else:
        equal = python_value == sql_value
    if not equal:
        raise AssertionError(
            f"{source} linha {row_number}, {field}: Python={python_value!r}, SQL={sql_value!r}"
        )


def _assert_valid_case(
    conn,
    directory: Path,
    *,
    source: str,
    module,
    function: str,
    rows: Sequence[Mapping[str, object]],
    delimiter: str,
    encoding: str,
    fields: Mapping[str, str],
) -> tuple[list[dict], list[dict]]:
    path, payload = _write_csv_fixture(
        directory, source + "-valid", module, rows, delimiter=delimiter, encoding=encoding
    )
    python_rows, python_ignored, python_period = _python_parse(module, path)
    sql_rows = _sql_parse(conn, function, payload)

    if len(sql_rows) != len(payload):
        raise AssertionError(
            f"{source}: SQL devolveu {len(sql_rows)} de {len(payload)} linhas"
        )
    sql_line_numbers = [row["linha"] for row in sql_rows]
    if sql_line_numbers != list(range(1, len(payload) + 1)):
        raise AssertionError(f"{source}: ordinais SQL incompletos ou fora de ordem")

    rejected = [row for row in sql_rows if str(row.get("motivo") or "")]
    if rejected:
        raise AssertionError(f"{source}: SQL rejeitou fixture valida: {rejected[0]['motivo']}")

    ignored = [row for row in sql_rows if row.get("ignorar") is True]
    if len(ignored) != python_ignored:
        raise AssertionError(
            f"{source}: ignoradas Python={python_ignored}, SQL={len(ignored)}"
        )
    accepted = [row for row in sql_rows if row.get("ignorar") is not True]
    if len(accepted) != len(python_rows):
        raise AssertionError(
            f"{source}: aceitas Python={len(python_rows)}, SQL={len(accepted)}"
        )

    for index in range(len(python_rows)):
        python_row = python_rows[index]
        sql_row = accepted[index]
        for python_field, sql_field in fields.items():
            if python_field not in python_row:
                raise AssertionError(f"{source}: campo Python ausente: {python_field}")
            if sql_field not in sql_row:
                raise AssertionError(f"{source}: campo SQL ausente: {sql_field}")
            _assert_value(
                source,
                int(sql_row["linha"]),
                f"{python_field}/{sql_field}",
                python_row[python_field],
                sql_row[sql_field],
            )

    sql_dates = sorted(row["data_ref"] for row in accepted if row["data_ref"] is not None)
    if not sql_dates or python_period != (sql_dates[0], sql_dates[-1]):
        raise AssertionError(
            f"{source}: periodo Python={python_period}, SQL={sql_dates[:1] + sql_dates[-1:]}"
        )
    return python_rows, accepted


def _assert_rejection_case(
    conn,
    directory: Path,
    *,
    source: str,
    module,
    function: str,
    rows: Sequence[Mapping[str, object]],
    delimiter: str,
    encoding: str,
) -> None:
    path, payload = _write_csv_fixture(
        directory, source + "-invalid", module, rows, delimiter=delimiter, encoding=encoding
    )
    python_error = _python_rejection(module, path)
    sql_rows = _sql_parse(conn, function, payload)

    if len(sql_rows) != len(payload):
        raise AssertionError(
            f"{source}: SQL devolveu {len(sql_rows)} de {len(payload)} linhas invalidas"
        )
    rejected = [row for row in sql_rows if str(row.get("motivo") or "")]
    if not rejected:
        raise AssertionError(f"{source}: SQL aceitou todas as linhas invalidas")
    if f"{len(rejected)} linha(s) rejeitada(s)" not in python_error:
        raise AssertionError(
            f"{source}: quantidade de rejeicoes divergiu; SQL={len(rejected)}, Python={python_error}"
        )

    for row in rejected:
        csv_line = int(row["linha"]) + 1
        expected = f"linha {csv_line}: {row['motivo']}"
        if expected not in python_error:
            raise AssertionError(
                f"{source}: motivo SQL nao apareceu no Python para a linha {csv_line}: "
                f"{row['motivo']}"
            )


STONE_EXTRATO_FIELDS = {
    "movimentacao": "movimentacao",
    "tipo": "tipo",
    "valor": "valor",
    "saldo_antes": "saldo_antes",
    "saldo_depois": "saldo_depois",
    "tarifa": "tarifa",
    "data_hora": "data_hora",
    "data_hora_raw": "data_raw",
    "horario": "horario",
    "situacao": "situacao",
    "nosso_numero": "nosso_numero",
    "destino": "destino",
    "destino_documento": "destino_documento",
    "destino_instituicao": "destino_instituicao",
    "destino_agencia": "destino_agencia",
    "destino_conta": "destino_conta",
    "origem": "origem",
    "origem_documento": "origem_documento",
    "origem_instituicao": "origem_instituicao",
    "origem_agencia": "origem_agencia",
    "origem_conta": "origem_conta",
    "descricao": "descricao",
    "dedup_hash": "dedup_hash",
}

STONE_VENDAS_FIELDS = {
    field: field
    for field in (
        "documento", "stonecode", "data_venda", "bandeira", "produto",
        "stone_id", "n_parcelas", "valor_bruto", "valor_liquido",
        "desconto_mdr", "desconto_antecipacao", "desconto_unificado",
        "n_cartao", "meio_captura", "n_serie", "ultimo_status",
        "data_ultimo_status",
    )
}

STONE_RECEBIVEIS_FIELDS = {
    field: field
    for field in (
        "documento", "stonecode", "categoria", "bandeira", "produto",
        "stone_id", "ultimo_status", "data_venda", "data_vencimento",
        "data_vencimento_original", "data_ultimo_status", "qtd_parcelas",
        "n_parcela", "valor_bruto", "valor_liquido", "desconto_mdr",
        "desconto_antecipacao", "desconto_unificado", "entradas_brutas",
        "saidas_brutas",
    )
}

BB_FIELDS = {
    field: field
    for field in (
        "data", "data_raw", "lancamento", "detalhes", "n_documento",
        "valor", "tipo_lancamento", "dedup_hash",
    )
}

BS_CASH_FIELDS = {
    field: field
    for field in (
        "data_hora", "data_raw", "dcto", "operacao", "historico",
        "favorecido", "valor", "saldo", "dedup_hash",
    )
}


def test_stone_extrato(conn, directory: Path, module) -> None:
    valid = [
        {
            "Movimentação": "\vCrédito\v",
            "Tipo": "Recebível de Cartão",
            "Valor": "1.234,56",
            "Saldo antes": "10,00",
            "Saldo depois": "1.244,56",
            "Tarifa": "0,00",
            "Data": "\v01/01/2000 10:20:30\v",
            "Horário": "10:20:30",
            "Situação": "Concluída",
            "Nosso Número": "v-ref-v",
            "Destino": "vivo-v",
            "Destino Documento": "00000000000100",
            "Destino Instituição": "Instituição sintética",
            "Destino Agência": "1",
            "Destino Conta": "2",
            "Origem": "Origem sintética",
            "Origem Documento": "00000000000200",
            "Origem Instituição": "Banco sintético",
            "Origem Agência": "3",
            "Origem Conta": "4",
            "Descrição": "Fixture sem dado real",
        },
        {
            "Movimentação": "Débito",
            "Tipo": "Tarifa",
            "Valor": "-25,50",
            "Saldo antes": "",
            "Saldo depois": "",
            "Data": "02/01/2000 11:45",
            "Horário": "",
            "Destino Documento": "",
        },
        {
            "Movimentação": "Crédito",
            "Tipo": "Ajuste",
            "Valor": "0,00",
            "Saldo antes": "1.219,06",
            "Saldo depois": "1.219,06",
            "Data": "03/01/2000",
        },
    ]
    _assert_valid_case(
        conn,
        directory,
        source="stone_extrato",
        module=module,
        function="private.parse_stone_extrato",
        rows=valid,
        delimiter=",",
        encoding="utf-8-sig",
        fields=STONE_EXTRATO_FIELDS,
    )
    _assert_rejection_case(
        conn,
        directory,
        source="stone_extrato",
        module=module,
        function="private.parse_stone_extrato",
        rows=[{
            "Movimentação": "",
            "Valor": "invalido",
            "Saldo antes": "1,2,3",
            "Saldo depois": "invalido",
            "Data": "31/02/2000",
        }],
        delimiter=",",
        encoding="utf-8-sig",
    )
    print("  [OK] Stone Extrato: linhas, campos, datas, valores, hash e rejeicoes")


def test_stone_vendas(conn, directory: Path, module) -> None:
    valid = [
        {
            "DOCUMENTO": "doc-v",
            "STONECODE": "code-v",
            "DATA DA VENDA": "\v04/01/2000 12:30:45\v",
            "BANDEIRA": "Visa",
            "PRODUTO": "Crédito",
            "STONE ID": "venda-v",
            "N DE PARCELAS": "2",
            "VALOR BRUTO": "200,00",
            "VALOR LIQUIDO": "190,00",
            "DESCONTO DE MDR": "6,00",
            "DESCONTO DE ANTECIPACAO": "3,00",
            "DESCONTO UNIFICADO": "1,00",
            "N DO CARTAO": "0000",
            "MEIO DE CAPTURA": "POS",
            "N DE SERIE": "serie-v",
            "ULTIMO STATUS": "Aprovada",
            "DATA DO ULTIMO STATUS": "04/01/2000 12:31:00",
        },
        {
            "DATA DA VENDA": "05/01/2000 09:10",
            "STONE ID": "venda-002",
            "VALOR BRUTO": "10,00",
            "VALOR LIQUIDO": "9,50",
        },
        {
            "DATA DA VENDA": "06/01/2000",
            "STONE ID": "venda-003",
            "VALOR BRUTO": "-10,00",
            "VALOR LIQUIDO": "-9,50",
            "ULTIMO STATUS": "Cancelada",
        },
    ]
    _assert_valid_case(
        conn,
        directory,
        source="stone_vendas",
        module=module,
        function="private.parse_stone_vendas",
        rows=valid,
        delimiter=";",
        encoding="utf-8-sig",
        fields=STONE_VENDAS_FIELDS,
    )
    _assert_rejection_case(
        conn,
        directory,
        source="stone_vendas",
        module=module,
        function="private.parse_stone_vendas",
        rows=[{
            "STONE ID": "",
            "DATA DA VENDA": "31/02/2000",
            "N DE PARCELAS": "1,5",
            "VALOR BRUTO": "invalido",
            "VALOR LIQUIDO": "",
            "DESCONTO DE MDR": "invalido",
            "DESCONTO DE ANTECIPACAO": "invalido",
            "DESCONTO UNIFICADO": "invalido",
            "DATA DO ULTIMO STATUS": "25:00",
        }],
        delimiter=";",
        encoding="utf-8-sig",
    )
    print("  [OK] Stone Vendas: linhas, campos, datas, valores e rejeicoes")


def test_stone_recebiveis(conn, directory: Path, module) -> None:
    valid = [
        {
            "DOCUMENTO": "doc-r-v",
            "STONECODE": "code-r-v",
            "CATEGORIA": "Venda",
            "DATA DA VENDA": "\v07/01/2000 14:00:30\v",
            "DATA DE VENCIMENTO": "08/01/2000",
            "DATA DE VENCIMENTO ORIGINAL": "09/01/2000",
            "BANDEIRA": "Visa",
            "PRODUTO": "Crédito",
            "STONE ID": "vrecebivel-v",
            "QTD DE PARCELAS": "2",
            "Nº DA PARCELA": "1",
            "VALOR BRUTO": "100,00",
            "VALOR LÍQUIDO": "95,00",
            "DESCONTO DE MDR": "3,00",
            "DESCONTO DE ANTECIPAÇÃO": "1,00",
            "DESCONTO UNIFICADO": "1,00",
            "ÚLTIMO STATUS": "Pago",
            "DATA DO ÚLTIMO STATUS": "08/01/2000 10:00",
            "ENTRADAS BRUTAS": "100,00",
            "SAÍDAS BRUTAS": "5,00",
        },
        {
            "CATEGORIA": "Venda",
            "DATA DA VENDA": "",
            "DATA DE VENCIMENTO": "",
            "DATA DE VENCIMENTO ORIGINAL": "10/01/2000",
            "STONE ID": "recebivel-002",
            "QTD DE PARCELAS": "1",
            "Nº DA PARCELA": "1",
            "VALOR BRUTO": "",
            "VALOR LÍQUIDO": "9,50",
        },
        {
            "CATEGORIA": "Cancelamento",
            "DATA DA VENDA": "11/01/2000",
            "DATA DE VENCIMENTO": "",
            "DATA DE VENCIMENTO ORIGINAL": "",
            "STONE ID": "recebivel-003",
            "QTD DE PARCELAS": "1",
            "Nº DA PARCELA": "1",
            "VALOR BRUTO": "-10,00",
            "VALOR LÍQUIDO": "-9,50",
        },
    ]
    _assert_valid_case(
        conn,
        directory,
        source="stone_recebiveis",
        module=module,
        function="private.parse_stone_recebiveis",
        rows=valid,
        delimiter=";",
        encoding="utf-8-sig",
        fields=STONE_RECEBIVEIS_FIELDS,
    )
    _assert_rejection_case(
        conn,
        directory,
        source="stone_recebiveis",
        module=module,
        function="private.parse_stone_recebiveis",
        rows=[
            {
                "STONE ID": "2,95639E+13",
                "DATA DE VENCIMENTO": "12/01/2000",
                "Nº DA PARCELA": "1",
                "VALOR LÍQUIDO": "9,50",
            },
            {
                "STONE ID": "",
                "DATA DA VENDA": "31/02/2000",
                "DATA DE VENCIMENTO": "invalida",
                "DATA DE VENCIMENTO ORIGINAL": "invalida",
                "QTD DE PARCELAS": "x",
                "Nº DA PARCELA": "x",
                "VALOR BRUTO": "x",
                "VALOR LÍQUIDO": "x",
                "DESCONTO DE MDR": "x",
                "DESCONTO DE ANTECIPAÇÃO": "x",
                "DESCONTO UNIFICADO": "x",
                "DATA DO ÚLTIMO STATUS": "x",
                "ENTRADAS BRUTAS": "x",
                "SAÍDAS BRUTAS": "x",
            },
        ],
        delimiter=";",
        encoding="utf-8-sig",
    )
    print("  [OK] Stone Recebiveis: linhas, campos, datas, valores e rejeicoes")


def test_bb(conn, directory: Path, module) -> None:
    valid = [
        {"Data": "01/01/2000", "Lançamento": "Saldo Anterior", "Valor": "100,00 C"},
        {
            "Data": "\v01/01/2000\v",
            "Lançamento": "Pix - Enviado",
            "Valor": "-4,00 D",
            "N° documento": "doc-1",
            "Detalhes": "Fixture",
            "Tipo Lançamento": "Saída",
        },
        {
            "Data": "01/01/2000",
            "Lançamento": "Pix - Enviado",
            "Valor": "4,00 D",
            "N° documento": "doc-1",
            "Detalhes": "Fixture",
            "Tipo Lançamento": "Entrada",
        },
        {
            "Data": "01/01/2000",
            "Lançamento": "Pix recebido",
            "Valor": "10,00 C",
            "N° documento": "doc-2",
            "Detalhes": "vivo-v",
            "Tipo Lançamento": "Entrada",
        },
        {
            "Data": "01/01/2000",
            "Lançamento": "Aplicação Fundo BB",
            "Valor": "-20,00 D",
            "N° documento": "provisorio",
            "Detalhes": "Aplicação",
            "Tipo Lançamento": "Saída",
        },
        {
            "Data": "01/01/2000",
            "Lançamento": "BB RF LP Selic",
            "Valor": "20,00 D",
            "N° documento": "consolidado",
            "Detalhes": "Consolidação",
            "Tipo Lançamento": "Entrada",
        },
        {"Data": "01/01/2000", "Lançamento": "Saldo do dia", "Valor": "62,00 C"},
        {"Data": "01/01/2000", "Lançamento": "S A L D O", "Valor": "62,00 C"},
    ]
    python_rows, _ = _assert_valid_case(
        conn,
        directory,
        source="bb",
        module=module,
        function="private.parse_bb",
        rows=valid,
        delimiter=",",
        encoding="latin-1",
        fields=BB_FIELDS,
    )

    debit_hashes = [
        row["dedup_hash"]
        for row in python_rows
        if row["lancamento"] == "Pix - Enviado"
    ]
    if len(debit_hashes) != 2 or len(set(debit_hashes)) != 1:
        raise AssertionError("BB: formatos antigo e novo nao convergiram no hash real")
    fund_hashes = [
        row["dedup_hash"]
        for row in python_rows
        if row["lancamento"] in module.ROTULOS_FUNDO_BB
    ]
    if len(fund_hashes) != 2 or len(set(fund_hashes)) != 1:
        raise AssertionError("BB: rotulos provisorio e consolidado nao convergiram no hash real")

    _assert_rejection_case(
        conn,
        directory,
        source="bb",
        module=module,
        function="private.parse_bb",
        rows=[
            {"Data": "01/02/2000", "Lançamento": "Saldo Anterior", "Valor": "100,00 C"},
            {"Data": "", "Lançamento": "", "Valor": ""},
            {"Data": "01/02/2000", "Lançamento": "S A L D O", "Valor": "100,00 C"},
        ],
        delimiter=",",
        encoding="latin-1",
    )
    print("  [OK] BB: linhas, saldos ignorados, datas, valores, hashes e rejeicoes")


def test_bs_cash(conn, directory: Path, module) -> None:
    valid = [
        {
            "Data": "",
            "Histórico": "SALDO ANTERIOR",
            "Saldo (R$)": "100,00",
        },
        {
            "Data": "\v13/01/2000 10:20:30\v",
            "Dcto.": "v-doc-v",
            "Operação": "PIX",
            "Histórico": "Recebimento sintético",
            "Favorecido": "vivo-v",
            "Créditos (R$)": "50,00",
            "Débitos (R$)": "",
            "Saldo (R$)": "150,00",
        },
        {
            "Data": "14/01/2000",
            "Dcto.": "doc-2",
            "Operação": "TED",
            "Histórico": "Pagamento sintético",
            "Favorecido": "Fornecedor sintético",
            "Créditos (R$)": "",
            "Débitos (R$)": "30,00",
            "Saldo (R$)": "120,00",
        },
    ]
    _assert_valid_case(
        conn,
        directory,
        source="bs_cash",
        module=module,
        function="private.parse_bs_cash",
        rows=valid,
        delimiter=",",
        encoding="utf-8",
        fields=BS_CASH_FIELDS,
    )
    _assert_rejection_case(
        conn,
        directory,
        source="bs_cash",
        module=module,
        function="private.parse_bs_cash",
        rows=[{
            "Data": "15/01/2000 10:20",
            "Créditos (R$)": "",
            "Débitos (R$)": "",
            "Saldo (R$)": "invalido",
        }],
        delimiter=",",
        encoding="utf-8",
    )
    print("  [OK] BS Cash: linhas, ignoradas, campos, datas, valores, hash e rejeicoes")


def main() -> None:
    print("Iniciando paridade diferencial dos parsers reais...")
    modules = {
        "stone_extrato": load_import_module(
            "paridade_stone_extrato", "01_importar_extrato_stone.py"
        ),
        "stone_vendas": load_import_module(
            "paridade_stone_vendas", "02_importar_vendas_stone.py"
        ),
        "stone_recebiveis": load_import_module(
            "paridade_stone_recebiveis", "03_importar_recebiveis_stone.py"
        ),
        "bb": load_import_module("paridade_bb", "04_importar_bb.py"),
        "bs_cash": load_import_module("paridade_bs_cash", "05_importar_bs_cash.py"),
    }

    conn = get_db_connection()
    try:
        with tempfile.TemporaryDirectory(prefix="sirfisher-parser-parity-") as tmp:
            directory = Path(tmp)
            test_stone_extrato(conn, directory, modules["stone_extrato"])
            test_stone_vendas(conn, directory, modules["stone_vendas"])
            test_stone_recebiveis(conn, directory, modules["stone_recebiveis"])
            test_bb(conn, directory, modules["bb"])
            test_bs_cash(conn, directory, modules["bs_cash"])
    finally:
        conn.close()

    print(
        "PARIDADE_PARSERS_OK: 5 fontes, parsers Python reais, linhas aceitas/"
        "ignoradas/rejeitadas, campos, datas, valores e hashes aplicaveis."
    )


if __name__ == "__main__":
    main()
