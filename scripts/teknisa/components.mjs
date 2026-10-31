import { createHash } from 'node:crypto';

// Payloads come from UI captures. The caller keeps authentication in memory.
// A component price of R$0.01 mirrors existing markers; it does not prove the
// order total. Verify included-choice pricing and the POS total separately.
export const COMPONENT_PATHS = Object.freeze({
  product: '/backend_cadEst/index.php/saveProduct',
  tax: '/backend_cadEst/index.php/ger01900_cadastroproduto_venda_imposto/save',
  price: '/backend_cadEst/index.php/vnd42400_tabelapreco_precoProd/save',
  store: '/backend_man/index.php/ger12300_cadloja_produtos/save',
});
export const COMPONENT_WRITE_CONTRACTS = Object.freeze(Object.entries(COMPONENT_PATHS).map(([stage, path]) => ({ path, requestType: stage === 'product' ? 'Row' : 'DataSet' })));
const ORG = 5482, BRANCH = '0002', STORE = '0001';
const clone = value => structuredClone(value);
const canonical = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
const equal = (a, b) => canonical(a) === canonical(b);
const fail = (code, message) => { throw Object.assign(new Error(message), { code }); };
const digest = plan => createHash('sha256').update(canonical({ ...plan, checksum: undefined })).digest('hex');
const format = code => `${code[0]}.${code.slice(1,3)}.${code.slice(3,5)}.${code.slice(5,8)}.${code.slice(8)}`;
const rowsOf = result => Array.isArray(result) ? result : Array.isArray(result?.rows) ? result.rows : fail('INVALID_ROWS', 'A leitura precisa devolver linhas do cadastro.');
const exactZero = value => value !== null && value !== undefined && value !== '' && Number(value) === 0;
const dateInFortaleza = date => new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Fortaleza', dateStyle: 'short',
  timeStyle: 'medium', hour12: false }).format(date).replace(',', '');

export function validateDefinition(definition) {
  const d = definition;
  if (!d || !/^[a-z][a-z0-9_]*$/.test(d.key) || !/^\d{10}$/.test(d.rawTreeCode)
      || !/^\d{8}$/.test(d.parentCode) || !d.rawTreeCode.startsWith(d.parentCode)
      || typeof d.name !== 'string' || !d.name.trim() || d.name.length > 50
      || !['00001', '00004'].includes(d.printer)) fail('INVALID_COMPONENT', 'Confira nome, código, pai e impressora do componente.');
  return clone(d);
}
function assertProduct(row, d) {
  if (!row || String(row.NRORG) !== String(ORG) || row.CDARVPROD !== d.rawTreeCode
      || row.NMPRODUTO !== d.name || row.SGUNIDADE !== 'UN' || row.IDESTOCOMP !== 'E'
      || row.IDPRODATIVPR !== 'S' || !/^\d{10}$/.test(row.CDPRODUTO)
      || row.CDPRODNIVANTE !== d.parentCode || (row.IDTIPOCOMPPROD !== undefined && row.IDTIPOCOMPPROD !== '0')) {
    fail('COMPONENT_PRODUCT_DIFFERENCE', 'O código existente precisa corresponder ao componente planejado e estar ativo.');
  }
  return row;
}
function matchProduct(rows, d) {
  const found = rows.filter(r => r.CDARVPROD === d.rawTreeCode);
  if (found.length > 1) fail('DUPLICATE_PRODUCT', 'A consulta retornou mais de um produto para o código.');
  if (found.length) assertProduct(found[0], d);
  return found[0] || null;
}
function scopeRows(rows, id, kind) {
  const found = rows.filter(r => r.CDPRODUTO === id && (kind !== 'price' || r.CDTABEPREC === '001')
    && (kind !== 'tax' || (r.CDIMPOSTO === '00' && r.IDTPIMPOSFIS === 'T')));
  for (const r of found) {
    if (String(r.NRORG) !== String(ORG) || r.CDFILIAL !== BRANCH || (kind === 'store' && r.CDLOJA !== STORE)) {
      fail('COMPONENT_SCOPE_DIFFERENCE', 'A leitura retornou outra organização, unidade ou loja.');
    }
  }
  if (found.length > 1) fail('DUPLICATE_COMPONENT_STAGE', `A consulta retornou mais de um cadastro de ${kind}.`);
  return found[0] || null;
}
function desiredStage(kind, row, d) {
  if (!row) return false;
  if (kind === 'tax') return row.CDIMPOSTO === '00' && row.IDTPIMPOSFIS === 'T'
    && exactZero(row.VRPEALIMPFIS) && row.CDCFOPPFIS === '5102'
    && row.CDCSTICMS === '102' && row.CDCSTPISCOF === '99' && row.IDINCIDEPISCOF === 'N'
    && exactZero(row.VRALIQPIS) && exactZero(row.VRALIQCOFINS);
  if (kind === 'price') return Number(row.VRPRECITEM) === 0.01 && row.CDTABEPREC === '001'
    && String(row.DTINIVGPREC).startsWith('06/07/2026');
  if (kind === 'store') return row.NRSEQIMPRPROD === d.printer && row.IDIMPCANITEM === 'S';
  return false;
}
function singleTemplate(template, type, field) {
  if (!template || template.requestType !== type || (type === 'DataSet' && (!Array.isArray(template.dataset) || template.dataset.length !== 1))
      || (type === 'Row' && !template.row) || !template.origin) fail('MISSING_CAPTURED_TEMPLATE', `Informe o corpo observado de ${field}.`);
  return clone(template);
}
export function buildProductPayload(template, definition) {
  const d = validateDefinition(definition), body = singleTemplate(template, 'Row', 'produto');
  if (body.row.__is_new !== true || body.row.SGUNIDADE !== 'UN' || body.row.IDESTOCOMP !== 'E' || body.row.IDPRODATIVPR !== 'S') {
    fail('INVALID_PRODUCT_TEMPLATE', 'O modelo precisa representar inclusão de componente ativo em UN.');
  }
  Object.assign(body.row, { CDARVPRODNIVANTE: d.parentCode, CDPRODNIVANTE: d.parentCode,
    CDARVPROD: format(d.rawTreeCode), NMPRODUTO: d.name, changed: true });
  // Preserve the captured marker classification. Do not invent a global NCM.
  return body;
}
function productIdentity(row, product, definition) {
  assertProduct(product, definition);
  Object.assign(row, { CDPRODUTO: product.CDPRODUTO, CDARVPROD: definition.rawTreeCode,
    NMPRODUTO: definition.name, CDPRPAITABPR: product.CDPRODUTO, NRORG: ORG, changed: true });
}
export function buildTaxPayload(template, product, definition) {
  const d = validateDefinition(definition), body = singleTemplate(template, 'DataSet', 'imposto');
  const row = body.dataset[0];
  if (row.__is_new !== true) fail('INVALID_TAX_TEMPLATE', 'Use o modelo de inclusão do imposto; a edição do arroz existente é outra operação.');
  productIdentity(row, product, d);
  Object.assign(row, { CDFILIAL: [BRANCH], NMFILIAL: ['SIR FISHER PRAIA'], CDNVPRODUTO: 5,
    CDIMPOSTO: '00', VRPEALIMPFIS: 0, CDCFOPPFIS: '5102', CDCSTICMS: '102', CDCSTPISCOF: '99',
    IDINCIDEPISCOF: 'N', VRALIQPIS: 0, VRALIQCOFINS: 0, IDTPIMPOSFIS: 'T' });
  return body;
}
export function buildPricePayload(template, product, definition) {
  const d = validateDefinition(definition), body = singleTemplate(template, 'DataSet', 'preço');
  const row = body.dataset[0];
  if (row.__is_new !== true) fail('INVALID_PRICE_TEMPLATE', 'Use o modelo de inclusão do preço.');
  productIdentity(row, product, d);
  Object.assign(row, { CDFILIAL: [BRANCH], CDTABEPREC: ['001'], CDFILIALTAB: [BRANCH],
    DTINIVGPREC: ['06/07/2026'], DTFINVGPREC: ['06/07/2100'], VRPRECITEM: 0.01 });
  return body;
}
export function buildStorePayload(template, product, definition, date = new Date()) {
  const d = validateDefinition(definition), body = singleTemplate(template, 'DataSet', 'loja');
  if (['CDPRODINICIAL', 'NMPRODINICIAL', 'NIVELINICIAL'].some(field => !Object.hasOwn(body.dataset[0], field))) {
    fail('INCOMPLETE_STORE_TEMPLATE', 'Capture o corpo integral da inclusão por loja antes de executar. O exemplo antigo omite campos obrigatórios.');
  }
  assertProduct(product, d);
  const row = body.dataset[0];
  if (row.__is_new !== true || row.CDPRODINICIAL !== '' || row.NMPRODINICIAL !== '' || row.NIVELINICIAL !== 'T') {
    fail('INVALID_STORE_TEMPLATE', 'Use o modelo observado de inclusão por lista, com os campos de intervalo vazios.');
  }
  Object.assign(row, { PRODUTOS: [product.CDPRODUTO], CDPRODUTO_SM: [product.CDPRODUTO],
    CDARVPROD_SM: [d.rawTreeCode], NMPRODUTO_SM: [d.name], NRSEQIMPRPROD: d.printer,
    IDIMPCANITEM: 'S', CDFILIAL: BRANCH, CDLOJA: STORE, NRORG: ORG, changed: true });
  // Interval fields stay exactly as captured. CDOPERADOR is preserved from the
  // successful UI capture; it is never inferred from NRORG or authentication.
  if (Object.hasOwn(row, 'NMIMPRPROD')) row.NMIMPRPROD = d.printer === '00001' ? 'COZINHA' : 'BAR';
  if (Object.hasOwn(row, 'DTATU')) row.DTATU = dateInFortaleza(date);
  return body;
}
export function chunkComponentDefinitions(definitions, size = 4) {
  if (!Array.isArray(definitions) || !Number.isSafeInteger(size) || size < 1 || size > 4) fail('INVALID_CHUNK_SIZE', 'Use lotes de um a quatro componentes.');
  const rows = definitions.map(validateDefinition), chunks = [];
  for (let i = 0; i < rows.length; i += size) chunks.push(rows.slice(i, i + size));
  return chunks;
}
function callbacks(options) {
  for (const name of ['readProducts', 'readPrices', 'readStore', 'readTax']) if (typeof options[name] !== 'function') fail('MISSING_READ_CALLBACK', `Informe ${name}.`);
}
export async function createComponentPlan(options) {
  callbacks(options);
  const definitions = options.definitions.map(validateDefinition);
  if (!definitions.length || definitions.length > 50 || new Set(definitions.map(d => d.rawTreeCode)).size !== definitions.length
      || new Set(definitions.map(d => d.key)).size !== definitions.length) fail('INVALID_COMPONENT_PLAN', 'Informe componentes únicos.');
  const products = rowsOf(await options.readProducts()), prices = rowsOf(await options.readPrices()), stores = rowsOf(await options.readStore());
  const entries = [];
  for (const d of definitions) {
    if (!products.some(p => p.CDPRODNIVANTE === d.parentCode || p.CDARVPRODNIVANTE === d.parentCode)) fail('UNCONFIRMED_PARENT', 'O pai do componente não foi confirmado na leitura atual.');
    const product = matchProduct(products, d);
    const before = { product, tax: null, price: null, store: null };
    if (product) {
      before.tax = scopeRows(rowsOf(await options.readTax(product.CDPRODUTO)), product.CDPRODUTO, 'tax');
      before.price = scopeRows(prices, product.CDPRODUTO, 'price');
      before.store = scopeRows(stores, product.CDPRODUTO, 'store');
      for (const stage of ['tax', 'price', 'store']) if (before[stage] && !desiredStage(stage, before[stage], d)) {
        fail('EXISTING_COMPONENT_STAGE_DIFFERENCE', `O componente já tem ${stage} diferente. Revise antes de alterar.`);
      }
    }
    entries.push({ definition: d, before: clone(before) });
  }
  const plan = { version: 1, kind: 'new-menu-components', target: { organization: ORG, branch: BRANCH, store: STORE },
    createdAt: (options.now?.() || new Date()).toISOString(), entries };
  plan.checksum = digest(plan); return plan;
}

export async function applyComponentPlan(options) {
  callbacks(options);
  const { plan, request, templates, checkpoint } = options;
  if (typeof request !== 'function' || typeof checkpoint !== 'function' || !plan || plan.version !== 1
      || plan.kind !== 'new-menu-components' || plan.checksum !== digest(plan)
      || !equal(plan.target, { organization: ORG, branch: BRANCH, store: STORE })) fail('INVALID_COMPONENT_PLAN', 'Confira plano, destino e callbacks de gravação.');
  const now = () => options.now?.() || new Date();
  const age = now().getTime() - Date.parse(plan.createdAt);
  if (!Number.isFinite(age) || age < -60000 || age > 30 * 60000) fail('EXPIRED_COMPONENT_PLAN', 'Prepare uma prévia atual antes de gravar.');
  for (const stage of ['product', 'tax', 'price', 'store']) singleTemplate(templates?.[stage], stage === 'product' ? 'Row' : 'DataSet', stage);
  if (['CDPRODINICIAL', 'NMPRODINICIAL', 'NIVELINICIAL'].some(field => !Object.hasOwn(templates.store.dataset[0], field))) {
    fail('INCOMPLETE_STORE_TEMPLATE', 'O modelo da loja está incompleto; nenhuma gravação foi iniciada.');
  }
  // Validate every captured payload before the first write. This prevents a late
  // template failure after creating a product without its remaining settings.
  for (const item of plan.entries) {
    const d = validateDefinition(item.definition), sample = { NRORG: ORG, CDPRODUTO: d.rawTreeCode, CDARVPROD: d.rawTreeCode,
      NMPRODUTO: d.name, CDPRODNIVANTE: d.parentCode, SGUNIDADE: 'UN', IDESTOCOMP: 'E', IDPRODATIVPR: 'S', IDTIPOCOMPPROD: '0' };
    buildProductPayload(templates.product, d); buildTaxPayload(templates.tax, sample, d);
    buildPricePayload(templates.price, sample, d); buildStorePayload(templates.store, sample, d, now());
  }
  const receipt = { version: 1, kind: plan.kind, checksum: plan.checksum, target: clone(plan.target),
    startedAt: now().toISOString(), status: 'running', entries: [] };
  await checkpoint(clone(receipt));
  try {
    for (const item of plan.entries) {
      const d = validateDefinition(item.definition);
      const entry = { definition: clone(d), before: clone(item.before), stages: [] }; receipt.entries.push(entry);
      let product = matchProduct(rowsOf(await options.readProducts()), d);
      if (item.before.product && !equal(product, item.before.product)) fail('CONCURRENT_COMPONENT_CHANGE', 'O produto mudou desde a prévia.');
      if (!product) {
        const stage = { stage: 'product', status: 'sending', attemptedAt: now().toISOString() }; entry.stages.push(stage);
        await checkpoint(clone(receipt));
        await request(COMPONENT_PATHS.product, buildProductPayload(templates.product, d));
        stage.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        product = matchProduct(rowsOf(await options.readProducts()), d);
        if (!product) fail('PRODUCT_NOT_CREATED', 'O produto não foi confirmado após a gravação.');
        Object.assign(stage, { status: 'verified', after: clone(product), verifiedAt: now().toISOString() });
      } else entry.stages.push({ stage: 'product', status: 'already_present', after: clone(product) });
      await checkpoint(clone(receipt));
      for (const stageName of ['tax', 'price', 'store']) {
        const read = async () => scopeRows(rowsOf(await (stageName === 'tax' ? options.readTax(product.CDPRODUTO)
          : stageName === 'price' ? options.readPrices() : options.readStore())), product.CDPRODUTO, stageName);
        const current = await read();
        const before = item.before[stageName];
        if (current && desiredStage(stageName, current, d)) {
          entry.stages.push({ stage: stageName, status: 'already_present', after: clone(current) });
          await checkpoint(clone(receipt)); continue;
        }
        if (current || before) fail('CONCURRENT_COMPONENT_CHANGE', 'Um cadastro mudou desde a prévia. Releia antes de gravar.');
        const stage = { stage: stageName, status: 'sending', attemptedAt: now().toISOString() }; entry.stages.push(stage);
        await checkpoint(clone(receipt));
        const builder = { tax: buildTaxPayload, price: buildPricePayload, store: buildStorePayload }[stageName];
        await request(COMPONENT_PATHS[stageName], builder(templates[stageName], product, d, now()));
        stage.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        const after = await read();
        if (!desiredStage(stageName, after, d)) fail('COMPONENT_READBACK_DIFFERENCE', `O cadastro de ${stageName} não confirmou os valores previstos.`);
        Object.assign(stage, { status: 'verified', after: clone(after), verifiedAt: now().toISOString() });
        await checkpoint(clone(receipt));
      }
      Object.assign(entry, { status: 'verified', productId: product.CDPRODUTO });
      await checkpoint(clone(receipt));
    }
    Object.assign(receipt, { status: 'completed', completedAt: now().toISOString(), verified: receipt.entries.length });
    await checkpoint(clone(receipt)); return receipt;
  } catch (error) {
    Object.assign(receipt, { status: 'interrupted', errorCode: error.code || 'COMPONENT_OPERATION_FAILED', interruptedAt: now().toISOString() });
    await checkpoint(clone(receipt)); throw error;
  }
}

export function createComponentClient(options) {
  callbacks(options);
  return Object.freeze({ target: Object.freeze({ organization: ORG, branch: BRANCH, store: STORE }),
    preview: definitions => createComponentPlan({ ...options, definitions }),
    apply: plan => applyComponentPlan({ ...options, plan }),
  });
}
