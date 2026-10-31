import { createHash, randomUUID } from 'node:crypto';

// Contracts are restricted to operations actually observed in the authorized UI.
// Parent creation: authorized UI operation followed by a successful readback.
// Parent update: full observed DataSet envelope, preserving the source row.
export const PATHS = Object.freeze({
  products: '/backend_cadEst/index.php/crud/produto_produto',
  groups: '/backend_cadEst/index.php/crud/grupromoc',
  groupsSave: '/backend_cadEst/index.php/crud/grupromoc/save',
  bindings: '/backend_cadEst/index.php/grupromocprod_grupopromoc',
  bindingSave: '/backend_cadEst/index.php/grupromocprod_grupopromoc/save',
  bindingRemove: '/backend_cadEst/index.php/grupromocprod_grupopromoc/remove',
  groupItems: '/backend_cadEst/index.php/prodgrupromoc_produto',
  legacyGroupItems: '/backend_man/index.php/vnd41000_grupoPromo_prod',
  groupItemsSave: '/backend_cadEst/index.php/prodgrupromoc_produto/save',
  productSave: '/backend_cadEst/index.php/saveProduct',
});
export const READ_PATHS = Object.freeze([PATHS.products, PATHS.groups, PATHS.bindings, PATHS.groupItems]);
export const WRITE_PATHS = Object.freeze([PATHS.bindingSave, PATHS.groupsSave, PATHS.groupItemsSave, PATHS.bindingRemove, PATHS.productSave]);
export const REQUEST_TYPES = Object.freeze(Object.fromEntries([
  ...READ_PATHS.map(path => [path, 'FilterData']), ...WRITE_PATHS.map(path => [path, [PATHS.bindingRemove, PATHS.productSave].includes(path) ? 'Row' : 'DataSet']),
]));
export const BINDING_ORIGIN = Object.freeze({
  containerName: 'ger14600_composicao_do_produto', widgetName: 'GRUPOPROMOCIONAL',
  containerLabel: 'Composição do Produto', widgetLabel: 'Grupo Promocional',
});
export const CONTRACT_STATUS = Object.freeze({
  productsRead: 'observed-complete', bindingsRead: 'observed-complete',
  groupsRead: 'observed-complete', groupItemsRead: 'observed-complete',
  bindingCreate: 'observed-complete', bindingUpdate: 'observed-complete',
  groupCreate: 'observed-complete', groupItemsCreate: 'observed-complete',
  productTypeUpdate: 'observed-full-row-edit-known-field', bindingRemove: 'observed-row-removal-documented',
});
export const COMPOSITION_CLIENT_VERSION = '2026-10-31.4';
export const PRODUCT_EDIT_ORIGIN = Object.freeze({ containerLabel: 'Produto', widgetLabel: 'Dados do Produto' });
export const PRODUCT_AUDIT_FIELDS = Object.freeze(['DTULTATU', 'DTULTATUPROD', 'CDOPERULTATU', 'NRORGULTATU']);
const clone = value => structuredClone(value);
const canonical = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
const same = (a, b) => canonical(a) === canonical(b);
const fail = (code, message) => { throw Object.assign(new Error(message), { code }); };
const id = value => typeof value === 'string' && /^\d{10}$/.test(value);
const digest = plan => createHash('sha256').update(canonical({ ...plan, checksum: undefined })).digest('hex');
const source = value => typeof value === 'string' && value.trim().length >= 8;
const required = (condition, code, message) => { if (!condition) fail(code, message); };

function validateTarget(target) {
  required(target?.organization === 5482 && /^\d{4}$/.test(target.branch) && /^\d{4}$/.test(target.store),
    'INVALID_TARGET', 'Confira organização 5482, unidade e loja antes de consultar.');
}
function validateLimits(min, max) {
  required(Number.isSafeInteger(min) && Number.isSafeInteger(max) && min >= 0 && min <= max && max === 1,
    'INVALID_LIMITS', 'A migração admite mínimo 0 ou 1 e máximo 1 por grupo.');
}
function validateBinding(row, target, productId) {
  required(row?.NRORG === target.organization && row.CDPRODPROMOCAO === productId
    && id(row.CDGRUPROMOC) && id(row.NRSEQGRPROMO) && row.__is_new === false,
  'INVALID_BINDING_ROW', 'A consulta retornou outra organização, produto ou chave de vínculo.');
  required(Number.isSafeInteger(row.QTPRGRUPROMIN) && Number.isSafeInteger(row.QTPRGRUPPROMOC)
    && row.QTPRGRUPROMIN >= 0 && row.QTPRGRUPROMIN <= row.QTPRGRUPPROMOC,
  'INVALID_BINDING_QUANTITIES', 'O vínculo retornou quantidades inválidas.');
}

export function buildBindingPayload({ target, productId, groupId, groupName, min, max, before = null }) {
  validateTarget(target); validateLimits(min, max);
  required(id(productId) && id(groupId), 'INVALID_BINDING_ID', 'Informe os códigos do produto e do grupo observados.');
  let row;
  if (before) {
    validateBinding(before, target, productId);
    required(before.CDGRUPROMOC === groupId, 'BINDING_KEY_CHANGE', 'A edição precisa preservar o grupo do vínculo.');
    row = { ...clone(before), QTPRGRUPROMIN: min, QTPRGRUPPROMOC: max,
      changed: true, CDPRODUTO: productId };
  } else {
    required(typeof groupName === 'string' && groupName.trim() && groupName.length <= 100,
      'INVALID_GROUP_NAME', 'Informe o nome conferido do grupo.');
    row = { __createdLocal: true, __is_new: true, CDGRUPROMOC: groupId, NMGRUPROMOC: groupName,
      QTPRGRUPROMIN: min, QTPRGRUPPROMOC: max, NRORDPROMOGRUP: null, CDGRUPMUTEX: '',
      IDAPLICADESC: 'N', IDIMPGRPROMO: 'N', DTINIVGGRPROMO: '', DTFINVGGRPROMO: '',
      changed: true, ISVIGREQUIRED: null, NRORG: target.organization,
      CDPRODUTO: productId, CDPRODPROMOCAO: productId };
  }
  return { dataset: [row], requestType: 'DataSet', origin: { ...BINDING_ORIGIN } };
}
export function buildGroupItemPayload({ target, groupId, product }) {
  validateTarget(target);
  required(id(groupId) && product?.NRORG === target.organization && id(product.CDPRODUTO)
    && /^\d{10}$/.test(String(product.CDARVPROD).replaceAll('.', '')) && typeof product.NMPRODUTO === 'string'
    && product.IDPRODATIVPR !== 'N', 'INVALID_GROUP_ITEM', 'Use um grupo e um produto ativo conferidos.');
  return { dataset: [{ __createdLocal: true, __is_new: true,
    CDARVPROD: String(product.CDARVPROD).replaceAll('.', ''), NMPRODUTO: product.NMPRODUTO.trim(),
    CDPRODUTO: product.CDPRODUTO, SGUNIDADE: '', changed: true, CDGRUPROMOC: groupId }],
    requestType: 'DataSet', origin: { containerName: 'ger14600_composicao_do_produto', widgetName: 'PRODUTOGRUPOPROMO',
      containerLabel: 'Composição do Produto', widgetLabel: 'Produto do Grupo Promocional' } };
}
export function buildProductTypePayload({ target, before }) {
  validateTarget(target);
  required(before?.NRORG === target.organization && id(before.CDPRODUTO) && before.__is_new === false
    && before.IDPRODATIVPR === 'S' && ['0', '3'].includes(before.IDTIPOCOMPPROD),
  'INVALID_PRODUCT_TYPE_ROW', 'A mudança de tipo exige a linha completa de um produto ativo.');
  return { requestType: 'Row', row: { ...clone(before), IDTIPOCOMPPROD: '3', changed: true }, origin: { ...PRODUCT_EDIT_ORIGIN } };
}
export function buildBindingRemovePayload({ target, before }) {
  validateTarget(target); validateBinding(before, target, before?.CDPRODPROMOCAO);
  return { requestType: 'Row', row: clone(before), origin: { ...BINDING_ORIGIN } };
}

function defaultProductsRead(target) {
  return { path: PATHS.products, dataset: 'produto_produto', source: 'gestao/scripts/teknisa/recursos.mjs', body: {
    disableLoader: false, page: 1, itemsPerPage: 50, requestType: 'FilterData',
    filter: [{ name: 'NRORG', operator: '=', value: target.organization },
      { name: 'CDFILIAL', operator: '=', value: target.branch },
      { name: 'PERMVISUPROD', operator: '<>', value: 'B' },
      { name: 'CDOPERADOR', operator: '=', value: 'OPERADOR_LOGADO' },
      { name: 'CDPRODINI', operator: '=', value: null }, { name: 'CDPRODFIN', operator: '=', value: null },
      { name: [{ name: 'CDARVPROD', direction: 'ASC' }], value: null, operator: 'ORDER_BY' },
      { name: 'IDPRODATIVPR', value: 'S', operator: '=', isCustomFilter: true }],
    origin: { containerName: 'ger01900_cadastroproduto', widgetName: 'produtos',
      containerLabel: 'Produto', widgetLabel: 'Produto' },
  } };
}
function defaultCompositionReads() {
  const captured = 'authorized UI capture and readback, 31/10/2026';
  const body = (widgetName, widgetLabel, filter) => ({ disableLoader: false, filter,
    page: 1, itemsPerPage: 500, requestType: 'FilterData', origin: {
      containerName: 'ger14600_composicao_do_produto', widgetName,
      containerLabel: 'Composição do Produto', widgetLabel,
    } });
  return {
    groups: { path: PATHS.groups, dataset: 'grupromoc', source: captured,
      body: body('GRUPOPROMOC', 'Grupo Promocional', [{ name: [{ name: 'CDGRUPROMOC', direction: 'ASC' }], value: null, operator: 'ORDER_BY' }]) },
    bindings: { path: PATHS.bindings, dataset: 'grupromocprod_grupopromoc', source: captured,
      body: body('GRUPOPROMOCIONAL', 'Grupo Promocional', [{ name: 'CDPRODPROMOCAO', operator: '=', value: '0000000073' },
        { name: [{ name: 'CDGRUPROMOC', direction: 'ASC' }], value: null, operator: 'ORDER_BY' }]) },
    groupItems: { path: PATHS.groupItems, dataset: 'prodgrupromoc_produto', source: captured,
      body: body('PRODUTOGRUPOPROMO', 'Produto do Grupo Promocional', [{ name: 'CDGRUPROMOC', operator: '=', value: '0000000012' },
        { name: [{ name: 'CDARVPROD', direction: 'ASC' }], value: null, operator: 'ORDER_BY' }]) },
  };
}
const READ_KINDS = Object.freeze({
  products: { path: PATHS.products, key: 'CDPRODUTO' },
  bindings: { path: PATHS.bindings, scoped: 'CDPRODPROMOCAO', key: 'NRSEQGRPROMO' },
  groupItems: { path: PATHS.groupItems, scoped: 'CDGRUPROMOC', key: 'CDPRODUTO' },
  groups: { path: PATHS.groups, scoped: null, key: 'CDGRUPROMOC' },
});

export function createCompositionClient({ request, target, readContracts = {}, checkpoint, now = () => new Date(), productReader }) {
  required(typeof request === 'function', 'MISSING_REQUEST', 'Forneça o transporte autorizado.');
  validateTarget(target); target = Object.freeze(clone(target));
  const contracts = new Map([['products', defaultProductsRead(target)], ...Object.entries(defaultCompositionReads())]);

  function registerObservedRead(kind, observed) {
    const spec = READ_KINDS[kind];
    required(spec && observed && source(observed.source) && observed.body?.requestType === 'FilterData'
      && Array.isArray(observed.body.filter) && observed.body.origin && typeof observed.dataset === 'string'
      && Number.isSafeInteger(observed.body.itemsPerPage) && observed.body.itemsPerPage > 0
      && observed.body.itemsPerPage <= 9999 && observed.body.page === 1,
    'INVALID_READ_CONTRACT', 'Forneça caminho, corpo completo, dataset e origem da consulta observada.');
    required(spec.path ? observed.path === spec.path
      : /^\/backend_man\/index\.php\/(?:crud\/)?vnd41000_[A-Za-z0-9_]+$/.test(observed.path),
    'INVALID_READ_PATH', 'O caminho não corresponde ao recurso observado de composição.');
    const names = observed.body.filter.map(f => f.name).filter(n => typeof n === 'string');
    required(!spec.scoped || names.includes(spec.scoped),
      'MISSING_READ_SCOPE', 'A consulta deve conter o filtro observado do vínculo.');
    contracts.set(kind, clone(observed));
  }
  for (const [kind, observed] of Object.entries(readContracts)) registerObservedRead(kind, observed);

  async function read(kind, scopedValue) {
    const contract = contracts.get(kind), spec = READ_KINDS[kind];
    required(contract, 'UNOBSERVED_READ_CONTRACT', `Capture o corpo real da consulta ${kind} antes de usá-la.`);
    if (spec.scoped) required(id(scopedValue), 'INVALID_READ_ID', 'Informe a chave observada do vínculo.');
    const rows = [], keys = new Set(), fingerprints = new Set();
    for (let page = 1; page <= 100; page++) {
      const body = clone(contract.body); body.page = page;
      for (const f of body.filter) {
        if (f.name === 'NRORG') f.value = target.organization;
        if (f.name === 'CDFILIAL') f.value = target.branch;
        if (f.name === 'CDLOJA') f.value = target.store;
        if (spec.scoped && f.name === spec.scoped) f.value = scopedValue;
      }
      const response = await request(contract.path, body), batch = response?.dataset?.[contract.dataset];
      required(Array.isArray(batch), 'INVALID_READ_DATASET', 'O servidor não retornou o dataset observado.');
      const fingerprint = canonical(batch);
      required(!batch.length || !fingerprints.has(fingerprint), 'REPEATED_READ_PAGE', 'A consulta repetiu uma página.');
      fingerprints.add(fingerprint);
      for (const row of batch) {
        required(row?.NRORG === target.organization && id(row[spec.key]) && !keys.has(row[spec.key])
          && (!spec.scoped || row[spec.scoped] === scopedValue),
        'INVALID_READ_ROW', 'A consulta retornou outra organização, chave repetida ou escopo divergente.');
        if (kind === 'bindings') validateBinding(row, target, scopedValue);
        keys.add(row[spec.key]); rows.push(clone(row));
      }
      if (batch.length < body.itemsPerPage) return rows;
    }
    fail('READ_PAGE_LIMIT', 'A consulta ultrapassou o limite de páginas.');
  }
  const readProducts = () => read('products');
  const readGroups = () => read('groups');
  const readGroupItems = groupId => read('groupItems', groupId);
  const readBindings = productId => read('bindings', productId);
  async function readProduct(productId) {
    required(id(productId), 'INVALID_PRODUCT_ID', 'Informe o código do produto conferido.');
    const product = productReader ? await productReader(productId) : (await readProducts()).find(row => row.CDPRODUTO === productId);
    required(product?.NRORG === target.organization && product.CDPRODUTO === productId,
      'PRODUCT_READBACK_MISSING', 'O produto não foi encontrado na organização esperada.');
    return clone(product);
  }
  function seal(kind, fields) {
    const plan = { version: 1, kind, id: randomUUID(), target: clone(target), createdAt: now().toISOString(), ...clone(fields) };
    plan.checksum = digest(plan); return plan;
  }
  function checkPlan(plan, kind) {
    required(plan?.version === 1 && plan.kind === kind && same(plan.target, target) && plan.checksum === digest(plan),
      'INVALID_PLAN', 'A prévia foi alterada ou pertence a outro destino.');
    const age = now().getTime() - Date.parse(plan.createdAt);
    required(Number.isFinite(age) && age >= -60000 && age <= 30 * 60000, 'EXPIRED_PLAN', 'Prepare uma prévia atual.');
    required(typeof checkpoint === 'function', 'MISSING_CHECKPOINT', 'Forneça um recibo persistente antes da gravação.');
  }
  async function withReceipt(plan, operation) {
    const receipt = { id: plan.id, planChecksum: plan.checksum, target: clone(target), status: 'running', entries: [], startedAt: now().toISOString() };
    await checkpoint(clone(receipt));
    try { await operation(receipt); receipt.status = 'completed'; receipt.completedAt = now().toISOString(); await checkpoint(clone(receipt)); return receipt; }
    catch (error) { receipt.status = 'interrupted'; receipt.errorCode = error.code || 'UNKNOWN_WRITE_RESULT';
      try { await checkpoint(clone(receipt)); } catch { receipt.checkpointFailed = true; }
      error.receipt = clone(receipt); throw error; }
  }
  async function previewGroupItems({ groupId, productIds }) {
    required(id(groupId) && Array.isArray(productIds) && productIds.length > 0 && productIds.every(id)
      && new Set(productIds).size === productIds.length, 'INVALID_GROUP_ITEM_LIST', 'Informe o grupo e produtos sem duplicatas.');
    const group = (await readGroups()).find(row => row.CDGRUPROMOC === groupId);
    required(group && group.IDATIVO !== 'N', 'MISSING_ACTIVE_GROUP', 'O grupo precisa existir e estar ativo.');
    const products = new Map((await readProducts()).map(row => [row.CDPRODUTO, row]));
    const beforeAll = await readGroupItems(groupId), existing = new Set(beforeAll.map(row => row.CDPRODUTO));
    const items = productIds.map(productId => {
      const product = products.get(productId); buildGroupItemPayload({ target, groupId, product });
      return { product: clone(product), unchanged: existing.has(productId) };
    });
    return seal('composition-group-items-add', { groupId, groupName: group.NMGRUPROMOC, beforeAll, items });
  }
  async function applyGroupItems(plan) {
    checkPlan(plan, 'composition-group-items-add');
    for (const item of plan.items) buildGroupItemPayload({ target, groupId: plan.groupId, product: item.product });
    return withReceipt(plan, async receipt => {
      const group = (await readGroups()).find(row => row.CDGRUPROMOC === plan.groupId);
      required(group && group.IDATIVO !== 'N' && group.NMGRUPROMOC === plan.groupName,
        'GROUP_CHANGED', 'O grupo mudou ou foi inativado desde a prévia.');
      let expected = await readGroupItems(plan.groupId);
      required(same(expected, plan.beforeAll), 'CONCURRENT_GROUP_ITEMS_CHANGE', 'Os itens do grupo mudaram desde a prévia.');
      const products = new Map((await readProducts()).map(row => [row.CDPRODUTO, row]));
      for (const item of plan.items) required(same(products.get(item.product.CDPRODUTO), item.product),
        'COMPONENT_PRODUCT_CHANGED', 'Um componente mudou desde a prévia.');
      for (const item of plan.items) {
        const productId = item.product.CDPRODUTO, entry = { groupId: plan.groupId, productId };
        receipt.entries.push(entry);
        if (item.unchanged) { entry.status = 'already_desired'; await checkpoint(clone(receipt)); continue; }
        const current = await readGroupItems(plan.groupId);
        required(same(current, expected), 'CONCURRENT_GROUP_ITEMS_CHANGE', 'Os itens do grupo mudaram durante a execução.');
        entry.status = 'sending'; await checkpoint(clone(receipt));
        await request(PATHS.groupItemsSave, buildGroupItemPayload({ target, groupId: plan.groupId, product: item.product }));
        entry.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        const after = await readGroupItems(plan.groupId), added = after.filter(row => row.CDPRODUTO === productId);
        required(added.length === 1 && String(added[0].CDARVPROD).replaceAll('.', '') === String(item.product.CDARVPROD).replaceAll('.', '')
          && added[0].NMPRODUTO.trim() === item.product.NMPRODUTO.trim()
          && same(current, after.filter(row => row.CDPRODUTO !== productId)),
        'GROUP_ITEM_READBACK_DIFFERENCE', 'A releitura do item divergiu ou alterou outro item do grupo.');
        entry.status = 'verified'; entry.after = clone(added[0]); expected = after; await checkpoint(clone(receipt));
      }
    });
  }
  async function previewProductTypes(productIds) {
    required(Array.isArray(productIds) && productIds.length > 0 && productIds.every(id) && new Set(productIds).size === productIds.length,
      'INVALID_PRODUCT_LIST', 'Informe produtos sem duplicatas.');
    const products = new Map((await readProducts()).map(row => [row.CDPRODUTO, row]));
    const items = productIds.map(productId => { const before = products.get(productId); buildProductTypePayload({ target, before });
      return { productId, before: clone(before), unchanged: before.IDTIPOCOMPPROD === '3' }; });
    return seal('composition-product-type', { items });
  }
  async function applyProductTypes(plan) {
    checkPlan(plan, 'composition-product-type');
    for (const item of plan.items) buildProductTypePayload({ target, before: item.before });
    const withoutAudit = row => Object.fromEntries(Object.entries(row).filter(([key]) => !PRODUCT_AUDIT_FIELDS.includes(key)));
    return withReceipt(plan, async receipt => {
      // No product is saved if any selected source already diverged at preflight.
      const preflight = new Map((await readProducts()).map(row => [row.CDPRODUTO, row]));
      for (const item of plan.items) required(same(preflight.get(item.productId), item.before), 'CONCURRENT_PRODUCT_CHANGE', 'Um produto mudou desde a prévia.');
      for (const item of plan.items) {
        const entry = { productId: item.productId, before: clone(item.before), desired: '3' }; receipt.entries.push(entry);
        if (item.unchanged) { entry.status = 'already_desired'; await checkpoint(clone(receipt)); continue; }
        const current = await readProduct(item.productId);
        required(same(current, item.before), 'CONCURRENT_PRODUCT_CHANGE', 'O produto mudou durante a execução.');
        entry.status = 'sending'; await checkpoint(clone(receipt));
        await request(PATHS.productSave, buildProductTypePayload({ target, before: current }));
        entry.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        const after = await readProduct(item.productId);
        required(same(withoutAudit(after), withoutAudit({ ...current, IDTIPOCOMPPROD: '3' })),
          'PRODUCT_TYPE_READBACK_DIFFERENCE', 'A releitura mudou campos além do tipo de composição e dos registros de auditoria.');
        entry.status = 'verified'; entry.after = clone(after); await checkpoint(clone(receipt));
      }
    });
  }
  async function previewBindingRemovals(changes) {
    required(Array.isArray(changes) && changes.length > 0, 'INVALID_REMOVAL_LIST', 'Informe os vínculos a retirar.');
    const cache = new Map(), seen = new Set(), items = [];
    for (const change of changes) {
      const { productId, groupId, replacementGroupId, allowNoReplacement = false,
        expectedReplacementMin = 1, expectedReplacementMax = 1 } = change;
      validateLimits(expectedReplacementMin, expectedReplacementMax);
      required(id(productId) && id(groupId) && !seen.has(productId + ':' + groupId), 'INVALID_REMOVAL', 'Informe produtos e grupos sem duplicatas.');
      seen.add(productId + ':' + groupId);
      if (!cache.has(productId)) cache.set(productId, await readBindings(productId));
      const beforeAll = cache.get(productId), before = beforeAll.find(row => row.CDGRUPROMOC === groupId);
      required(before, 'REMOVAL_BINDING_MISSING', 'O vínculo pedido não existe no produto.');
      required(allowNoReplacement || (id(replacementGroupId) && replacementGroupId !== groupId
        && beforeAll.some(row => row.CDGRUPROMOC === replacementGroupId && row.QTPRGRUPROMIN === expectedReplacementMin && row.QTPRGRUPPROMOC === expectedReplacementMax)),
      'REPLACEMENT_NOT_VERIFIED', 'Confira os limites pedidos no grupo substituto antes de retirar o vínculo antigo.');
      items.push({ productId, groupId, replacementGroupId: replacementGroupId || null, allowNoReplacement,
        expectedReplacementMin, expectedReplacementMax,
        before: clone(before), beforeAll: clone(beforeAll) });
    }
    return seal('composition-parent-bindings-remove', { items });
  }
  async function applyBindingRemovals(plan) {
    checkPlan(plan, 'composition-parent-bindings-remove');
    return withReceipt(plan, async receipt => {
      const expectedByProduct = new Map();
      for (const item of plan.items) if (!expectedByProduct.has(item.productId)) {
        const current = await readBindings(item.productId);
        required(same(current, item.beforeAll), 'CONCURRENT_COMPOSITION_CHANGE', 'A composição mudou desde a prévia.');
        expectedByProduct.set(item.productId, current);
      }
      for (const item of plan.items) {
        const current = await readBindings(item.productId);
        required(same(current, expectedByProduct.get(item.productId)), 'CONCURRENT_COMPOSITION_CHANGE', 'A composição mudou durante a execução.');
        required(item.allowNoReplacement || current.some(row => row.CDGRUPROMOC === item.replacementGroupId
          && row.QTPRGRUPROMIN === item.expectedReplacementMin && row.QTPRGRUPPROMOC === item.expectedReplacementMax), 'REPLACEMENT_NOT_VERIFIED', 'O grupo substituto mudou.');
        const before = current.find(row => row.CDGRUPROMOC === item.groupId);
        const entry = { productId: item.productId, groupId: item.groupId, before: clone(before), status: 'sending' };
        receipt.entries.push(entry); await checkpoint(clone(receipt));
        await request(PATHS.bindingRemove, buildBindingRemovePayload({ target, before }));
        entry.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        const after = await readBindings(item.productId);
        required(same(after, current.filter(row => row.CDGRUPROMOC !== item.groupId)), 'REMOVAL_READBACK_DIFFERENCE', 'A retirada divergiu ou alterou outro grupo.');
        entry.status = 'verified'; expectedByProduct.set(item.productId, after); await checkpoint(clone(receipt));
      }
    });
  }
  async function readAll({ productIds } = {}) {
    const products = await readProducts(), groups = await readGroups();
    const productMap = new Map(products.map(row => [row.CDPRODUTO, row]));
    const ids = productIds || [...productMap.keys()];
    required(Array.isArray(ids) && new Set(ids).size === ids.length && ids.every(value => id(value) && productMap.has(value)),
      'INVALID_PRODUCT_SELECTION', 'Selecione produtos presentes no catálogo ativo.');
    const compositions = [], groupItems = [];
    // Keep one serialized execution against the unit; no concurrent writes or reads.
    for (const productId of ids) compositions.push({ product: clone(productMap.get(productId)), groups: await readBindings(productId) });
    for (const group of groups) groupItems.push({ groupId: group.CDGRUPROMOC, name: group.NMGRUPROMOC, rows: await readGroupItems(group.CDGRUPROMOC) });
    return { target: clone(target), readAt: now().toISOString(), products, groups, groupItems, compositions };
  }

  async function previewGroupCreation({ groupId, name }) {
    required(id(groupId) && typeof name === 'string' && name.trim() && name.length <= 100,
      'INVALID_NEW_GROUP', 'Informe código e nome do novo grupo.');
    const beforeAll = await readGroups();
    required(!beforeAll.some(row => row.CDGRUPROMOC === groupId), 'GROUP_ALREADY_EXISTS', 'O código do grupo já está ocupado.');
    const plan = { version: 1, kind: 'composition-group-create', id: randomUUID(), target: clone(target),
      createdAt: now().toISOString(), groupId, name: name.trim(), beforeAll };
    plan.checksum = digest(plan); return plan;
  }
  async function applyGroupCreation(plan) {
    required(plan?.version === 1 && plan.kind === 'composition-group-create' && same(plan.target, target)
      && plan.checksum === digest(plan) && id(plan.groupId), 'INVALID_PLAN', 'A prévia do grupo foi alterada.');
    const age = now().getTime() - Date.parse(plan.createdAt);
    required(Number.isFinite(age) && age >= -60000 && age <= 30 * 60000, 'EXPIRED_PLAN', 'Prepare uma prévia atual.');
    required(typeof checkpoint === 'function', 'MISSING_CHECKPOINT', 'Forneça um recibo persistente antes da gravação.');
    const receipt = { id: plan.id, planChecksum: plan.checksum, target: clone(target), status: 'running', entries: [], startedAt: now().toISOString() };
    await checkpoint(clone(receipt));
    try {
      const current = await readGroups();
      required(same(current, plan.beforeAll), 'CONCURRENT_GROUP_CHANGE', 'O cadastro de grupos mudou desde a prévia.');
      const entry = { groupId: plan.groupId, name: plan.name, status: 'sending' };
      receipt.entries.push(entry); await checkpoint(clone(receipt));
      await request(PATHS.groupsSave, { dataset: [{ __createdLocal: true, __is_new: true,
        CDGRUPROMOC: plan.groupId, NMGRUPROMOC: plan.name, changed: true }], requestType: 'DataSet',
        origin: { containerName: 'ger14600_composicao_do_produto', widgetName: 'GRUPOPROMOC',
          containerLabel: 'Composição do Produto', widgetLabel: 'Grupo Promocional' } });
      entry.status = 'awaiting_readback'; await checkpoint(clone(receipt));
      const afterAll = await readGroups(), found = afterAll.filter(row => row.CDGRUPROMOC === plan.groupId);
      required(found.length === 1 && found[0].NMGRUPROMOC === plan.name && found[0].IDATIVO !== 'N'
        && same(current, afterAll.filter(row => row.CDGRUPROMOC !== plan.groupId)),
      'GROUP_READBACK_DIFFERENCE', 'A releitura do grupo divergiu ou outro cadastro mudou.');
      entry.status = 'verified'; entry.after = clone(found[0]); receipt.status = 'completed';
      receipt.completedAt = now().toISOString(); await checkpoint(clone(receipt)); return receipt;
    } catch (error) {
      receipt.status = 'interrupted'; receipt.errorCode = error.code || 'UNKNOWN_WRITE_RESULT';
      await checkpoint(clone(receipt)); error.receipt = clone(receipt); throw error;
    }
  }

  async function previewBindings(changes) {
    required(Array.isArray(changes) && changes.length > 0 && changes.length <= 1000,
      'INVALID_CHANGE_LIST', 'Informe entre um e mil vínculos de composição.');
    const products = new Map((await readProducts()).map(row => [row.CDPRODUTO, row]));
    const groups = new Map((await readGroups()).map(row => [row.CDGRUPROMOC, row]));
    const seen = new Set(), cache = new Map(), blockers = [], items = [];
    for (const change of changes) {
      const { productId, groupId, min, max } = change; validateLimits(min, max);
      required(id(productId) && id(groupId), 'INVALID_BINDING_ID', 'Use as chaves dos produtos e grupos conferidos.');
      const key = productId + ':' + groupId;
      required(!seen.has(key), 'DUPLICATE_CHANGE', 'O mesmo vínculo aparece mais de uma vez na prévia.'); seen.add(key);
      const product = products.get(productId), group = groups.get(groupId);
      required(product && group && group.IDATIVO !== 'N', 'MISSING_PRODUCT_OR_GROUP', 'Um produto ou grupo está ausente do cadastro ativo.');
      if (product.IDTIPOCOMPPROD !== '3') blockers.push({ productId, code: 'PRODUCT_TYPE_UPDATE_REQUIRED', before: product.IDTIPOCOMPPROD, desired: '3' });
      if (!cache.has(productId)) cache.set(productId, await readBindings(productId));
      const matches = cache.get(productId).filter(row => row.CDGRUPROMOC === groupId);
      required(matches.length <= 1, 'DUPLICATE_PARENT_GROUP', 'O produto já possui vínculos repetidos com o grupo.');
      items.push({ productId, productName: product.NMPRODUTO, groupId, groupName: group.NMGRUPROMOC,
        min, max, before: clone(matches[0] || null), beforeAll: clone(cache.get(productId)) });
    }
    const plan = { version: 1, kind: 'composition-parent-bindings', id: randomUUID(), target: clone(target),
      createdAt: now().toISOString(), blockers, items };
    plan.checksum = digest(plan); return plan;
  }
  function validatePlan(plan) {
    required(plan?.version === 1 && plan.kind === 'composition-parent-bindings' && same(plan.target, target)
      && plan.checksum === digest(plan) && Array.isArray(plan.items) && plan.items.length,
    'INVALID_PLAN', 'A prévia foi alterada ou pertence a outro destino.');
    const age = now().getTime() - Date.parse(plan.createdAt);
    required(Number.isFinite(age) && age >= -60000 && age <= 30 * 60000,
      'EXPIRED_PLAN', 'Prepare uma prévia atual antes de gravar.');
    required(!plan.blockers?.length, 'PLAN_HAS_BLOCKERS', 'A prévia contém contratos ou tipos de produto pendentes.');
    for (const item of plan.items) buildBindingPayload({ target, ...item });
  }
  function verifyAfter(item, beforeAll, afterAll) {
    const found = afterAll.filter(row => row.CDGRUPROMOC === item.groupId);
    required(found.length === 1, 'BINDING_READBACK_MISSING', 'A releitura não contém exatamente um vínculo esperado.');
    const after = found[0];
    required(after.QTPRGRUPROMIN === item.min && after.QTPRGRUPPROMOC === item.max,
      'BINDING_READBACK_LIMITS', 'A releitura retornou limites diferentes do pedido.');
    if (item.before) {
      required(same(after, { ...item.before, QTPRGRUPROMIN: item.min, QTPRGRUPPROMOC: item.max }),
        'BINDING_READBACK_OTHER_FIELDS', 'Outro campo do vínculo mudou durante a gravação.');
    } else {
      required(after.IDAPLICADESC === 'N' && after.IDIMPGRPROMO === 'N',
        'BINDING_READBACK_CREATE_FIELDS', 'O novo vínculo não preservou o comportamento observado.');
    }
    required(same(beforeAll.filter(row => row.CDGRUPROMOC !== item.groupId),
      afterAll.filter(row => row.CDGRUPROMOC !== item.groupId)),
    'OTHER_BINDINGS_CHANGED', 'Outro grupo do produto mudou durante a gravação.');
    return after;
  }
  async function applyBindings(plan) {
    validatePlan(plan);
    required(typeof checkpoint === 'function', 'MISSING_CHECKPOINT', 'Forneça um recibo persistente antes da gravação.');
    const receipt = { id: plan.id, planChecksum: plan.checksum, target: clone(target), status: 'running', entries: [], startedAt: now().toISOString() };
    await checkpoint(clone(receipt));
    try {
      // Preflight the entire destination before the first write.
      const products = new Map((await readProducts()).map(row => [row.CDPRODUTO, row]));
      const groups = new Map((await readGroups()).map(row => [row.CDGRUPROMOC, row]));
      for (const item of plan.items) required(products.get(item.productId)?.IDTIPOCOMPPROD === '3'
        && groups.has(item.groupId) && groups.get(item.groupId).IDATIVO !== 'N',
      'DESTINATION_CHANGED', 'O destino mudou desde a prévia. Prepare outra prévia.');
      const currentByProduct = new Map();
      for (const item of plan.items) {
        if (!currentByProduct.has(item.productId)) {
          const current = await readBindings(item.productId);
          required(same(current, item.beforeAll), 'CONCURRENT_COMPOSITION_CHANGE', 'A composição mudou desde a prévia.');
          currentByProduct.set(item.productId, current);
        }
      }
      for (const item of plan.items) {
        const current = await readBindings(item.productId), expected = currentByProduct.get(item.productId);
        required(same(current, expected), 'CONCURRENT_COMPOSITION_CHANGE', 'A composição mudou durante a execução.');
        const entry = { productId: item.productId, groupId: item.groupId, before: clone(item.before), min: item.min, max: item.max };
        receipt.entries.push(entry);
        if (item.before?.QTPRGRUPROMIN === item.min && item.before?.QTPRGRUPPROMOC === item.max) {
          entry.status = 'already_desired'; entry.after = clone(item.before); await checkpoint(clone(receipt)); continue;
        }
        entry.status = 'sending'; await checkpoint(clone(receipt));
        await request(PATHS.bindingSave, buildBindingPayload({ target, ...item }));
        entry.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        const afterAll = await readBindings(item.productId);
        entry.after = clone(verifyAfter(item, current, afterAll)); entry.status = 'verified';
        currentByProduct.set(item.productId, afterAll); await checkpoint(clone(receipt));
      }
      receipt.status = 'completed'; receipt.completedAt = now().toISOString(); await checkpoint(clone(receipt)); return receipt;
    } catch (error) {
      receipt.status = 'interrupted'; receipt.errorCode = error.code || 'UNKNOWN_WRITE_RESULT';
      await checkpoint(clone(receipt)); error.receipt = clone(receipt); throw error;
    }
  }
  return Object.freeze({ target, registerObservedRead, readProducts, readProduct, readGroups, readGroupItems, readBindings, readAll,
    previewBindings, applyBindings, previewGroupCreation, applyGroupCreation, createGroup: applyGroupCreation,
    previewGroupItems, applyGroupItems, addGroupItems: applyGroupItems,
    previewProductTypes, applyProductTypes, setProductCompositionType: applyProductTypes,
    previewBindingRemovals, applyBindingRemovals,
    transportRules: () => ({ readPaths: [...new Set([...READ_PATHS, ...[...contracts.values()].map(c => c.path)])],
      writePaths: [...WRITE_PATHS], requestTypes: { ...REQUEST_TYPES, ...Object.fromEntries([...contracts.values()].map(c => [c.path, 'FilterData'])) } }),
  });
}

export function summarizePlan(plan) {
  if (plan?.kind === 'composition-parent-bindings') return { id: plan.id, kind: plan.kind,
    products: new Set(plan.items.map(item => item.productId)).size, bindings: plan.items.length,
    creates: plan.items.filter(item => !item.before).length,
    updates: plan.items.filter(item => item.before && (item.before.QTPRGRUPROMIN !== item.min || item.before.QTPRGRUPPROMOC !== item.max)).length,
    unchanged: plan.items.filter(item => item.before?.QTPRGRUPROMIN === item.min && item.before?.QTPRGRUPPROMOC === item.max).length,
    blockers: clone(plan.blockers), sample: plan.items.slice(0, 8).map(({ productId, productName, groupId, groupName, min, max }) => ({ productId, productName, groupId, groupName, min, max })) };
  if (plan?.kind === 'composition-group-create') return { id: plan.id, kind: plan.kind, groupId: plan.groupId, name: plan.name };
  if (plan?.kind === 'composition-group-items-add') return { id: plan.id, kind: plan.kind, groupId: plan.groupId,
    add: plan.items.filter(item => !item.unchanged).length, unchanged: plan.items.filter(item => item.unchanged).length };
  if (plan?.kind === 'composition-product-type') return { id: plan.id, kind: plan.kind,
    changes: plan.items.filter(item => !item.unchanged).length, unchanged: plan.items.filter(item => item.unchanged).length };
  if (plan?.kind === 'composition-parent-bindings-remove') return { id: plan.id, kind: plan.kind, changes: plan.items.length };
  fail('INVALID_PLAN', 'Prévia desconhecida.');
}
