-- Paridade dos parsers web com os importadores Python no PostgreSQL 15.
--
-- E'\\v' nao representa vertical tab no PostgreSQL 15: o escape desconhecido
-- vira a letra "v". Com isso, os helpers antigos deixavam chr(11) nas pontas
-- e ainda removiam letras "v" legitimas. Python str.strip() faz o inverso.
-- Tambem faltava ao parser web de recebiveis a rejeicao de STONE ID em
-- notacao cientifica que protege o importador Python contra perda de digitos
-- causada pelo Excel.
--
-- Objetos: somente funcoes puras de parsing em private; nenhuma tabela ou
-- dado financeiro e alterado.

begin;

create or replace function private.campo_csv(p_linha jsonb, p_chave text)
returns text
language sql
immutable
set search_path = pg_catalog, pg_temp
as $function$
  select nullif(
    btrim(p_linha ->> p_chave, E' \t\n\r\f' || chr(11)),
    ''
  );
$function$;

create or replace function private.parse_data_hora_br(p_texto text)
returns timestamp
language plpgsql
immutable
set search_path = pg_catalog, pg_temp
as $function$
declare
  m text[];
  v_ano integer;
  v_mes integer;
  v_dia integer;
  v_hora integer;
  v_min integer;
  v_seg integer;
begin
  if p_texto is null then
    return null;
  end if;

  m := regexp_match(
    btrim(p_texto, E' \t\n\r\f' || chr(11)),
    '^(\d{1,2})/(\d{1,2})/(\d{4})(?: (\d{1,2}):(\d{2})(?::(\d{2}))?)?$'
  );
  if m is null then
    return null;
  end if;

  v_ano := m[3]::integer;
  v_mes := m[2]::integer;
  v_dia := m[1]::integer;
  v_hora := coalesce(m[4], '0')::integer;
  v_min := coalesce(m[5], '0')::integer;
  v_seg := coalesce(m[6], '0')::integer;

  if v_ano < 1 or v_mes < 1 or v_mes > 12 or v_dia < 1
     or v_hora > 23 or v_min > 59 or v_seg > 59 then
    return null;
  end if;
  if v_dia > extract(
       day from (make_date(v_ano, v_mes, 1) + interval '1 month' - interval '1 day')
     )::integer then
    return null;
  end if;

  return make_timestamp(v_ano, v_mes, v_dia, v_hora, v_min, v_seg);
end;
$function$;

create or replace function private.parse_data_br(p_texto text)
returns date
language plpgsql
immutable
set search_path = pg_catalog, pg_temp
as $function$
declare
  m text[];
  v_ano integer;
  v_mes integer;
  v_dia integer;
begin
  if p_texto is null then
    return null;
  end if;

  m := regexp_match(
    btrim(p_texto, E' \t\n\r\f' || chr(11)),
    '^(\d{1,2})/(\d{1,2})/(\d{4})$'
  );
  if m is null then
    return null;
  end if;

  v_dia := m[1]::integer;
  v_mes := m[2]::integer;
  v_ano := m[3]::integer;

  if v_ano < 1 or v_mes < 1 or v_mes > 12 or v_dia < 1 then
    return null;
  end if;
  if v_dia > extract(
       day from (make_date(v_ano, v_mes, 1) + interval '1 month' - interval '1 day')
     )::integer then
    return null;
  end if;

  return make_date(v_ano, v_mes, v_dia);
end;
$function$;

create or replace function private.parse_data_hora_seg_br(p_texto text)
returns timestamp
language plpgsql
immutable
set search_path = pg_catalog, pg_temp
as $function$
declare
  m text[];
  v_ano integer;
  v_mes integer;
  v_dia integer;
  v_hora integer;
  v_min integer;
  v_seg integer;
begin
  if p_texto is null then
    return null;
  end if;

  m := regexp_match(
    btrim(p_texto, E' \t\n\r\f' || chr(11)),
    '^(\d{1,2})/(\d{1,2})/(\d{4})(?: (\d{1,2}):(\d{2}):(\d{2}))?$'
  );
  if m is null then
    return null;
  end if;

  v_dia := m[1]::integer;
  v_mes := m[2]::integer;
  v_ano := m[3]::integer;
  v_hora := coalesce(m[4], '0')::integer;
  v_min := coalesce(m[5], '0')::integer;
  v_seg := coalesce(m[6], '0')::integer;

  if v_ano < 1 or v_mes < 1 or v_mes > 12 or v_dia < 1
     or v_hora > 23 or v_min > 59 or v_seg > 59 then
    return null;
  end if;
  if v_dia > extract(
       day from (make_date(v_ano, v_mes, 1) + interval '1 month' - interval '1 day')
     )::integer then
    return null;
  end if;

  return make_timestamp(v_ano, v_mes, v_dia, v_hora, v_min, v_seg);
end;
$function$;

create or replace function private.parse_stone_recebiveis(p_linhas jsonb)
returns table (
  linha integer,
  documento text, stonecode text, categoria text, bandeira text, produto text,
  stone_id text, ultimo_status text,
  data_venda timestamp, data_vencimento date, data_vencimento_original date,
  data_ultimo_status timestamp, qtd_parcelas integer, n_parcela integer,
  valor_bruto numeric, valor_liquido numeric, desconto_mdr numeric,
  desconto_antecipacao numeric, desconto_unificado numeric,
  entradas_brutas numeric, saidas_brutas numeric,
  data_ref date, motivo text
)
language sql
immutable
set search_path = pg_catalog, pg_temp
as $function$
  with base as (
    select
      t.ord::integer as linha,
      private.campo_csv(t.linha_json, 'STONE ID') as stone_id,
      private.campo_csv(t.linha_json, 'DOCUMENTO') as documento,
      private.campo_csv(t.linha_json, 'STONECODE') as stonecode,
      private.campo_csv(t.linha_json, 'CATEGORIA') as categoria,
      private.campo_csv(t.linha_json, 'DATA DA VENDA') as data_venda_raw,
      private.campo_csv(t.linha_json, 'DATA DE VENCIMENTO') as data_vencimento_raw,
      private.campo_csv(t.linha_json, 'DATA DE VENCIMENTO ORIGINAL') as data_vencimento_original_raw,
      private.campo_csv(t.linha_json, 'BANDEIRA') as bandeira,
      private.campo_csv(t.linha_json, 'PRODUTO') as produto,
      private.campo_csv(t.linha_json, 'QTD DE PARCELAS') as qtd_parcelas_raw,
      private.campo_csv(t.linha_json, 'Nº DA PARCELA') as n_parcela_raw,
      private.campo_csv(t.linha_json, 'VALOR BRUTO') as valor_bruto_raw,
      private.campo_csv(t.linha_json, 'VALOR LÍQUIDO') as valor_liquido_raw,
      private.campo_csv(t.linha_json, 'DESCONTO DE MDR') as desconto_mdr_raw,
      private.campo_csv(t.linha_json, 'DESCONTO DE ANTECIPAÇÃO') as desconto_antecipacao_raw,
      private.campo_csv(t.linha_json, 'DESCONTO UNIFICADO') as desconto_unificado_raw,
      private.campo_csv(t.linha_json, 'ÚLTIMO STATUS') as ultimo_status,
      private.campo_csv(t.linha_json, 'DATA DO ÚLTIMO STATUS') as data_ultimo_status_raw,
      private.campo_csv(t.linha_json, 'ENTRADAS BRUTAS') as entradas_brutas_raw,
      private.campo_csv(t.linha_json, 'SAÍDAS BRUTAS') as saidas_brutas_raw
    from jsonb_array_elements(p_linhas) with ordinality as t(linha_json, ord)
  ), conv as (
    select
      b.*,
      private.parse_data_hora_br(b.data_venda_raw) as data_venda,
      private.parse_data_hora_br(b.data_vencimento_raw)::date as data_vencimento,
      private.parse_data_hora_br(b.data_vencimento_original_raw)::date as data_vencimento_original,
      private.parse_data_hora_br(b.data_ultimo_status_raw) as data_ultimo_status,
      private.parse_inteiro_br(b.qtd_parcelas_raw) as qtd_parcelas,
      private.parse_inteiro_br(b.n_parcela_raw) as n_parcela,
      private.parse_valor_br(b.valor_bruto_raw) as valor_bruto,
      private.parse_valor_br(b.valor_liquido_raw) as valor_liquido,
      private.parse_valor_br(b.desconto_mdr_raw) as desconto_mdr,
      private.parse_valor_br(b.desconto_antecipacao_raw) as desconto_antecipacao,
      private.parse_valor_br(b.desconto_unificado_raw) as desconto_unificado,
      private.parse_valor_br(b.entradas_brutas_raw) as entradas_brutas,
      private.parse_valor_br(b.saidas_brutas_raw) as saidas_brutas
    from base b
  )
  select
    c.linha,
    c.documento, c.stonecode, c.categoria, c.bandeira, c.produto,
    c.stone_id, c.ultimo_status,
    c.data_venda, c.data_vencimento, c.data_vencimento_original,
    c.data_ultimo_status, c.qtd_parcelas, c.n_parcela,
    c.valor_bruto, c.valor_liquido, c.desconto_mdr,
    c.desconto_antecipacao, c.desconto_unificado,
    c.entradas_brutas, c.saidas_brutas,
    coalesce(c.data_vencimento, c.data_venda::date, c.data_vencimento_original) as data_ref,
    array_to_string(array_remove(array[
      case
        when c.stone_id is null then 'STONE ID ausente'
        when c.stone_id ~* '^[0-9]+[.,]?[0-9]*E[+-]?[0-9]+$' then
          'STONE ID em notação científica (' || c.stone_id ||
          ') — o arquivo passou pelo Excel e perdeu dígitos; reexporte sem abrir na planilha'
      end,
      case when c.n_parcela is null then 'número da parcela inválido' end,
      case when c.valor_liquido is null then 'valor líquido inválido' end,
      case when c.data_vencimento is null and c.data_venda is null
                and c.data_vencimento_original is null
           then 'nenhuma data de referência válida' end,
      case when c.data_venda_raw is not null and c.data_venda is null
           then 'data da venda inválida' end,
      case when c.data_vencimento_raw is not null and c.data_vencimento is null
           then 'data de vencimento inválida' end,
      case when c.data_vencimento_original_raw is not null and c.data_vencimento_original is null
           then 'data de vencimento original inválida' end,
      case when c.qtd_parcelas_raw is not null and c.qtd_parcelas is null
           then 'quantidade de parcelas inválida' end,
      case when c.valor_bruto_raw is not null and c.valor_bruto is null
           then 'valor bruto inválido' end,
      case when c.desconto_mdr_raw is not null and c.desconto_mdr is null
           then 'desconto MDR inválido' end,
      case when c.desconto_antecipacao_raw is not null and c.desconto_antecipacao is null
           then 'desconto de antecipação inválido' end,
      case when c.desconto_unificado_raw is not null and c.desconto_unificado is null
           then 'desconto unificado inválido' end,
      case when c.data_ultimo_status_raw is not null and c.data_ultimo_status is null
           then 'data do último status inválida' end,
      case when c.entradas_brutas_raw is not null and c.entradas_brutas is null
           then 'entradas brutas inválidas' end,
      case when c.saidas_brutas_raw is not null and c.saidas_brutas is null
           then 'saídas brutas inválidas' end
    ], null), '; ') as motivo
  from conv c;
$function$;

revoke all privileges on function private.campo_csv(jsonb, text)
  from public, anon, authenticated;
revoke all privileges on function private.parse_data_hora_br(text)
  from public, anon, authenticated;
revoke all privileges on function private.parse_data_br(text)
  from public, anon, authenticated;
revoke all privileges on function private.parse_data_hora_seg_br(text)
  from public, anon, authenticated;
revoke all privileges on function private.parse_stone_recebiveis(jsonb)
  from public, anon, authenticated;

comment on function private.campo_csv(jsonb, text) is
  'Normaliza campo CSV como str.strip() dos importadores, incluindo vertical tab no PostgreSQL 15 e preservando a letra v.';
comment on function private.parse_stone_recebiveis(jsonb) is
  'Parser web de recebíveis em paridade com o Python, inclusive rejeição de STONE ID em notação científica.';

do $validation$
declare
  v_motivo text;
begin
  if private.campo_csv(
       jsonb_build_object('campo', chr(11) || 'vivo-v' || chr(11)),
       'campo'
     ) is distinct from 'vivo-v' then
    raise exception 'campo_csv nao preservou letra v ou nao removeu vertical tab';
  end if;

  if private.parse_data_hora_br(chr(11) || '01/01/2000 10:20' || chr(11))
       is distinct from timestamp '2000-01-01 10:20:00' then
    raise exception 'parse_data_hora_br divergiu do strip do Python';
  end if;
  if private.parse_data_br(chr(11) || '01/01/2000' || chr(11))
       is distinct from date '2000-01-01' then
    raise exception 'parse_data_br divergiu do strip do Python';
  end if;
  if private.parse_data_hora_seg_br(chr(11) || '01/01/2000 10:20:30' || chr(11))
       is distinct from timestamp '2000-01-01 10:20:30' then
    raise exception 'parse_data_hora_seg_br divergiu do strip do Python';
  end if;

  select r.motivo
    into v_motivo
  from private.parse_stone_recebiveis(jsonb_build_array(jsonb_build_object(
    'STONE ID', '2,95639E+13',
    'Nº DA PARCELA', '1',
    'VALOR LÍQUIDO', '9,50',
    'DATA DE VENCIMENTO', '01/01/2000'
  ))) r;

  if v_motivo is distinct from
       'STONE ID em notação científica (2,95639E+13) — o arquivo passou pelo Excel e perdeu dígitos; reexporte sem abrir na planilha' then
    raise exception 'parse_stone_recebiveis nao rejeitou STONE ID em notacao cientifica';
  end if;
end;
$validation$;

commit;
