import { createHash } from 'node:crypto';
import { OBSERVATION_PATHS, OBSERVATION_WRITE_PATHS } from './observacoes.mjs';
export const ORIGIN = 'https://retail.teknisa.com';
const base = '/backend_man/index.php/';
const origin = (containerName, widgetName, containerLabel, widgetLabel) => ({ containerName, widgetName, containerLabel, widgetLabel });
const storeOrigin = origin('ger12300_cadloja', 'productByStoreWidget', 'Cadastro de Loja', 'Produtos por Loja');
export const PRINTER_FIELDS = Object.freeze({
  producao: 'NRSEQIMPRPROD', producao2: 'NRSEQIMPRPROD2', puxa: 'NRSEQIMPRPUXA',
  backupProducao: 'NRSEQIMPPRDBKP', backupProducao2: 'NRSEQIMPPRD2BKP', backupPuxa: 'NRSEQIMPPUXABKP',
});
export const RESOURCES = Object.freeze({
  'loja.produtos': {
    path: `${base}ger12300_cadloja_produtos`, dataset: 'ger12300_cadloja_produtos',
    keys: ['NRORG', 'CDFILIAL', 'CDLOJA', 'CDPRODUTO'], store: true, limit: 9999,
    required: ['NMPRODUTO', 'CDARVPROD', 'IDIMPCANITEM', 'NRSEQIMPRPROD', '__is_new'],
    origin: storeOrigin,
    filters: () => [{ name: 'NIVELINICIAL', operator: '=', value: 'T' }],
    writable: ['IDIMPCANITEM', ...Object.values(PRINTER_FIELDS)],
    derived: [],
    derivedByField: {
      IDIMPCANITEM: ['DSIMPCANITEM'], NRSEQIMPRPROD: ['NMIMPRPROD', 'LABELIMPRPROD'],
      NRSEQIMPRPROD2: ['NMIMPRPROD2'], NRSEQIMPRPUXA: ['NMIMPRPUXA', 'LABELIMPRPUXA'],
      NRSEQIMPPRDBKP: ['NMIMPRPRODBKP'], NRSEQIMPPRD2BKP: ['NMIMPRPROD2BKP'], NRSEQIMPPUXABKP: ['NMIMPRPUXABKP'],
    },
    writeValidated: true,
  },
  'loja.impressoras': {
    path: `${base}impressoraNFLoja`, dataset: 'impressoraNFLoja', store: true, limit: 500,
    keys: ['NRORG', 'CDFILIAL', 'CDLOJA', 'NRSEQIMPRLOJA'],
    required: ['NMIMPRLOJA', 'NMIMPRESSORA', 'IDATIVO', '__is_new'],
    origin: origin('ger12300_cadloja', 'impLojaWidget', 'Cadastro de Loja', 'Impressoras por Loja'),
    filters: () => [], writable: ['NMIMPRLOJA'], derived: ['DTULTATU', 'CDOPERULTATU', 'NRORGULTATU'], writeValidated: true, saveResponse: 'keys',
  },
  'precos.tabelas': {
    path: `${base}vnd42400_tabelapreco_vigencias`, dataset: 'vnd42400_tabelapreco_vigencias', limit: 500,
    keys: ['NRORG', 'CDFILIAL', 'CDTABEPREC', 'DTINIVGPREC'],
    required: ['IDATIVO', 'DTFINVGPREC', 'NMTABEPREC'],
    origin: origin('vnd42400_tabelapreco', 'zhFilterPreferencesSelectConditions', 'Tabela de Preço', 'Filtro'),
    filters: () => [], writable: [], derived: [], writeValidated: false,
  },
  precos: {
    path: `${base}vnd42400_tabelapreco_produto`, dataset: 'vnd42400_tabelapreco_produto_normal_com_preco', limit: 500,
    keys: ['NRORG', 'CDFILIAL', 'CDTABEPREC', 'DTINIVGPREC', 'CDPRODUTO', 'CDPRPAITABPR'],
    required: ['NMPRODUTO', 'CDARVPROD', 'VRPRECITEM', '__is_new'],
    origin: origin('vnd42400_tabelapreco', 'produtos', 'Tabela de Preço', 'Produtos'),
    filters: target => [
      { name: 'CDTABEPREC', operator: '=', value: target.table },
      { name: 'DTINIVGPREC', operator: '=', value: target.effectiveFrom },
      { name: 'CDNVPRODUTO', operator: '=', value: target.productLevel },
      { name: 'VRPRECITEM', operator: 'IS_NOT_NULL' },
    ],
    writable: ['VRPRECITEM'], derived: [], writeValidated: false,
  },
  produtos: {
    path: '/backend_cadEst/index.php/crud/produto_produto', dataset: 'produto_produto', limit: 50,
    keys: ['NRORG', 'CDPRODUTO'], global: true,
    required: ['NMPRODUTO', 'CDARVPROD', 'SGUNIDADE', 'IDESTOCOMP', 'IDIMPRODUVEZ', '__is_new'],
    origin: origin('ger01900_cadastroproduto', 'produtos', 'Produto', 'Produto'),
    filters: () => [
      { name: 'PERMVISUPROD', operator: '<>', value: 'B' },
      { name: 'CDOPERADOR', operator: '=', value: 'OPERADOR_LOGADO' },
      { name: 'CDPRODINI', operator: '=', value: null }, { name: 'CDPRODFIN', operator: '=', value: null },
      { name: [{ name: 'CDARVPROD', direction: 'ASC' }], value: null, operator: 'ORDER_BY' },
      { name: 'IDPRODATIVPR', value: 'S', operator: '=', isCustomFilter: true },
    ],
    writable: ['NMPRODUTO', 'DSCOMPLNOME', 'DSINFADICPROD'], derived: [], writeValidated: false,
  },
  'vendas.garcons': {
    path: `${base}vnd09900_relProdutividadePorVendedor`, dataset: 'vnd09900_relProdutividadePorVendedor',
    keys: ['NRORG', 'CDFILIAL', 'CDLOJA'], store: true, limit: 500, repeatedKeys: true,
    required: ['CDVENDEDOR2', 'GARCON', 'QTPRODVEND', 'VRFINALITEM', 'VRLIQUIDO', 'VRLIQACRES', 'ACR', 'DES', 'VRGORJETA', 'VRTXENTREGA', 'VRREPITEM'],
    origin: origin('vnd09900_relProdutividadePorVendedor', 'zhFilterPreferencesSelectConditions', 'Produtividade por Vendedor', 'Filtro'),
    scopeFilters: target => [
      { name: 'NRORG', operator: '=', value: target.organization },
      { name: [{ name: 'LABELFILIAL', direction: 'ASC' }, { name: 'GARCON', direction: 'ASC' }], value: null, operator: 'ORDER_BY' },
      { name: 'CDFILIAL', value: [target.branch], operator: 'IN', isCustomFilter: true },
      { name: 'CDLOJA', value: [target.branch + target.store], operator: 'IN', isCustomFilter: true },
      { name: 'DTMOVTURCAIX', value: [target.from, target.to], operator: 'BETWEEN', isCustomFilter: true },
      { name: 'TIPORELATORIO', value: 'A', operator: '=', isCustomFilter: true },
      { name: 'IDUTILVENDASSOC', value: 'EXCETO', operator: '=', isCustomFilter: true },
    ],
    filters: () => [], writable: [], derived: [], writeValidated: false,
  },
});
export const resourceKey = (spec, row) => JSON.stringify(spec.keys.map(field => row[field]));
export function resource(name) {
  const spec = RESOURCES[name];
  if (!Object.hasOwn(RESOURCES, name)) throw new Error('Recurso não cadastrado. Consulte os comandos.');
  return spec;
}
export function validateTarget(target, name) {
  const spec = resource(name);
  if (!Number.isSafeInteger(target?.organization) || target.organization <= 0 || !/^\d{4}$/.test(target.branch)
      || (spec.store && !/^\d{4}$/.test(target.store))) throw new Error('Informe organização, unidade e loja do destino.');
  if (name === 'precos' && (!/^\d{3}$/.test(target.table) || !/^\d{2}\/\d{2}\/\d{4} 00:00:00$/.test(target.effectiveFrom)
      || !/^\d{1,2}$/.test(target.productLevel))) throw new Error('Informe tabela, início da vigência e nível de produto observados.');
  if (name === 'vendas.garcons') {
    const parse = text => {
      if (!/^\d{2}\/\d{2}\/\d{4}$/.test(text)) throw new Error('Informe o período no formato DD/MM/AAAA.');
      const [day, month, year] = text.split('/').map(Number), date = new Date(Date.UTC(year, month - 1, day));
      if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) throw new Error('O período contém uma data inválida.');
      return date.getTime();
    };
    const span = (parse(target.to) - parse(target.from)) / 86400000;
    if (span < 0 || span > 30) throw new Error('Consulte um período de até 31 dias por vez.');
  }
}
export async function readResource(request, name, target) {
  validateTarget(target, name);
  const spec = resource(name);
  const result = [], seen = new Set(), pages = new Set();
  for (let page = 1; page <= 100; page++) {
    const filter = spec.scopeFilters ? spec.scopeFilters(target) : [
      { name: 'NRORG', operator: '=', value: target.organization },
      { name: 'CDFILIAL', operator: '=', value: target.branch },
      ...(spec.store ? [{ name: 'CDLOJA', operator: '=', value: target.store }] : []), ...spec.filters(target),
    ];
    const response = await request(spec.path, { disableLoader: false, filter, page, itemsPerPage: spec.limit, requestType: 'FilterData', origin: { ...spec.origin } });
    const rows = response?.dataset?.[spec.dataset];
    if (!Array.isArray(rows)) throw new Error('A consulta não retornou o conjunto de dados esperado.');
    if (spec.repeatedKeys && rows.length) {
      const fingerprint = createHash('sha256').update(JSON.stringify(rows)).digest('hex');
      if (pages.has(fingerprint)) throw new Error('O relatório repetiu uma página. A cobertura precisa ser conferida.');
      pages.add(fingerprint);
    }
    for (const row of rows) {
      if (String(row.NRORG) !== String(target.organization) || (!spec.global && row.CDFILIAL !== target.branch)
          || (spec.store && row.CDLOJA !== target.store)
          || (name === 'precos' && (row.CDTABEPREC !== target.table || row.DTINIVGPREC !== target.effectiveFrom))
          || [...spec.keys, ...spec.required].some(field => row[field] === undefined)
          || (name === 'loja.produtos' && (!['S', 'N'].includes(row.IDIMPCANITEM) || (row.NRSEQIMPRPROD !== null && !/^\d{5}$/.test(row.NRSEQIMPRPROD))))
          || (!spec.repeatedKeys && seen.has(resourceKey(spec, row)))) {
        throw new Error('A consulta retornou outro destino, chave incompleta ou página repetida.');
      }
      seen.add(resourceKey(spec, row)); result.push(row);
    }
    if (rows.length < spec.limit) return result;
    if (spec.limit === 9999) throw new Error('A consulta atingiu o limite. Confira a paginação antes de continuar.');
  }
  throw new Error('A consulta ultrapassou o limite de páginas.');
}
export const WRITE_PATHS = Object.freeze([...Object.values(RESOURCES).filter(spec => spec.writeValidated).map(spec => `${spec.path}/save`), ...OBSERVATION_WRITE_PATHS]);
export const ALLOWED_PATHS = Object.freeze([...Object.values(RESOURCES).map(spec => spec.path), ...Object.values(OBSERVATION_PATHS), ...WRITE_PATHS]
  .filter((path, index, all) => all.indexOf(path) === index));
