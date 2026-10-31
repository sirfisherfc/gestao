import test from 'node:test';
import assert from 'node:assert/strict';
import { createCompositionClient, buildBindingPayload, buildGroupItemPayload, buildProductTypePayload, PATHS } from './composicoes.mjs';
const target = { organization: 5482, branch: '0002', store: '0001' };
const productId = '0000000015', groupId = '0000000007';
const baseRow = { NRORG: 5482, CDPRODPROMOCAO: productId, CDGRUPROMOC: groupId,
  NRSEQGRPROMO: '0000000001', QTPRGRUPROMIN: 0, QTPRGRUPPROMOC: 2, __is_new: false,
  NMGRUPROMOC: 'ACOMPANHAMENTO', IDAPLICADESC: 'N', IDIMPGRPROMO: 'N', PRESERVE: 'original' };
const groupsPath = PATHS.groups;
const readContract = (path, dataset, scoped) => ({ path, dataset, source: 'fixture: captured UI request',
  body: { page: 1, itemsPerPage: 50, requestType: 'FilterData', origin: { widgetName: 'observed' },
    filter: [{ name: 'NRORG', operator: '=', value: 5482 }, ...(scoped ? [{ name: scoped, operator: '=', value: scoped === 'CDGRUPROMOC' ? groupId : productId }] : [])] } });
function fixture({ rows = [baseRow], type = '3', onWrite, onRead } = {}) {
  const state = { rows: structuredClone(rows), writes: [], reads: [], journal: [], products: [{ NRORG: 5482, CDPRODUTO: productId, CDARVPROD: '9000005000', NMPRODUTO: 'FISH',
    IDTIPOCOMPPROD: type, IDPRODATIVPR: 'S', __is_new: false, PRESERVE: 'original' }],
    groupItems: [], groups: [{ NRORG: 5482, CDGRUPROMOC: groupId, NMGRUPROMOC: 'ACOMPANHAMENTO', IDATIVO: 'S' }] };
  const request = async (path, body) => {
    if (path === PATHS.productSave) { state.writes.push(structuredClone(body));
      const index = state.products.findIndex(row => row.CDPRODUTO === body.row.CDPRODUTO);
      state.products[index] = { ...state.products[index], IDTIPOCOMPPROD: body.row.IDTIPOCOMPPROD, DTULTATU: '31/10/2026 23:59:00' }; return {}; }
    if (path === PATHS.bindingRemove) { state.writes.push(structuredClone(body));
      state.rows = state.rows.filter(row => row.NRSEQGRPROMO !== body.row.NRSEQGRPROMO); return {}; }
    if (path === PATHS.groupItemsSave) { state.writes.push(structuredClone(body)); const row = body.dataset[0];
      state.groupItems.push({ NRORG: 5482, CDGRUPROMOC: row.CDGRUPROMOC, CDPRODUTO: row.CDPRODUTO, CDARVPROD: row.CDARVPROD, NMPRODUTO: row.NMPRODUTO, __is_new: false }); return {}; }
    if (path === PATHS.groupsSave) { state.writes.push(structuredClone(body)); const row = body.dataset[0];
      state.groups.push({ NRORG: 5482, CDGRUPROMOC: row.CDGRUPROMOC, NMGRUPROMOC: row.NMGRUPROMOC, IDATIVO: 'S', __is_new: false }); return {}; }
    if (path === PATHS.bindingSave) {
      state.writes.push(structuredClone(body));
      if (onWrite) return onWrite(state, body);
      const row = body.dataset[0], index = state.rows.findIndex(r => r.CDGRUPROMOC === row.CDGRUPROMOC);
      if (index >= 0) state.rows[index] = { ...state.rows[index], QTPRGRUPROMIN: row.QTPRGRUPROMIN, QTPRGRUPPROMOC: row.QTPRGRUPPROMOC };
      else state.rows.push({ ...structuredClone(row), __is_new: false, NRSEQGRPROMO: '0000000099', changed: undefined, __createdLocal: undefined, ISVIGREQUIRED: undefined, CDPRODUTO: undefined });
      return { result: 1 };
    }
    state.reads.push({ path, body: structuredClone(body) });
    if (onRead) onRead(state, path, body);
    if (path === PATHS.products) return { dataset: { produto_produto: structuredClone(state.products) } };
    if (path === groupsPath) return { dataset: { groups: structuredClone(state.groups) } };
    if (path === PATHS.bindings) return { dataset: { bindings: structuredClone(state.rows) } };
    if (path === PATHS.groupItems) return { dataset: { prodgrupromoc_produto: structuredClone(state.groupItems) } };
    throw new Error('unexpected path');
  };
  const checkpoint = async receipt => { state.journal.push(structuredClone(receipt)); };
  const client = createCompositionClient({ request, target, checkpoint, readContracts: {
    groups: readContract(groupsPath, 'groups'), bindings: readContract(PATHS.bindings, 'bindings', 'CDPRODPROMOCAO'),
  } });
  return { state, client };
}
test('invalid or missing plans remain blocked without a request', async () => {
  let calls = 0;
  const client = createCompositionClient({ request: async () => { calls++; }, target });
  await assert.rejects(client.addGroupItems(), { code: 'INVALID_PLAN' });
  await assert.rejects(client.setProductCompositionType(), { code: 'INVALID_PLAN' });
  assert.equal(calls, 0);
});
test('group items use the captured UI shape and preserve existing members', async () => {
  const { client, state } = fixture();
  state.groupItems = [{ NRORG: 5482, CDGRUPROMOC: groupId, CDPRODUTO: '0000000014', CDARVPROD: '9000004000', NMPRODUTO: 'EXISTING', __is_new: false }];
  const plan = await client.previewGroupItems({ groupId, productIds: [productId] });
  const receipt = await client.applyGroupItems(plan);
  assert.equal(receipt.status, 'completed'); assert.equal(state.groupItems.length, 2);
  assert.equal(state.groupItems[0].NMPRODUTO, 'EXISTING');
  assert.deepEqual(state.writes[0].dataset[0], { __createdLocal: true, __is_new: true, CDARVPROD: '9000005000', NMPRODUTO: 'FISH',
    CDPRODUTO: productId, SGUNIDADE: '', changed: true, CDGRUPROMOC: groupId });
});
test('type update preserves every business field, allows audit timestamps, and never reactivates inactive products', async () => {
  const { client, state } = fixture({ type: '0' });
  const plan = await client.previewProductTypes([productId]);
  const receipt = await client.applyProductTypes(plan);
  assert.equal(receipt.status, 'completed'); assert.equal(state.products[0].IDTIPOCOMPPROD, '3');
  assert.equal(state.products[0].PRESERVE, 'original'); assert.equal(state.writes[0].requestType, 'Row');
  assert.equal(state.writes[0].row.IDPRODATIVPR, 'S');
  assert.throws(() => buildProductTypePayload({ target, before: { ...state.products[0], IDPRODATIVPR: 'N' } }), { code: 'INVALID_PRODUCT_TYPE_ROW' });
});
test('parent removal requires a verified replacement and preserves its record', async () => {
  const replacement = { ...baseRow, CDGRUPROMOC: '0000000014', NRSEQGRPROMO: '0000000014', QTPRGRUPROMIN: 1, QTPRGRUPPROMOC: 1 };
  const { client, state } = fixture({ rows: [baseRow, replacement] });
  await assert.rejects(client.previewBindingRemovals([{ productId, groupId, replacementGroupId: '0000000015' }]), { code: 'REPLACEMENT_NOT_VERIFIED' });
  const plan = await client.previewBindingRemovals([{ productId, groupId, replacementGroupId: replacement.CDGRUPROMOC }]);
  await client.applyBindingRemovals(plan);
  assert.deepEqual(state.rows, [replacement]); assert.equal(state.writes[0].requestType, 'Row');
  assert.deepEqual(state.writes[0].row, baseRow);
});
test('optional sandwich replacement is checked against its explicit 0–1 limits', async () => {
  const replacement = { ...baseRow, CDGRUPROMOC: '0000000020', NRSEQGRPROMO: '0000000020', QTPRGRUPROMIN: 0, QTPRGRUPPROMOC: 1 };
  const { client, state } = fixture({ rows: [baseRow, replacement] });
  await assert.rejects(client.previewBindingRemovals([{ productId, groupId, replacementGroupId: replacement.CDGRUPROMOC }]), { code: 'REPLACEMENT_NOT_VERIFIED' });
  const plan = await client.previewBindingRemovals([{ productId, groupId, replacementGroupId: replacement.CDGRUPROMOC, expectedReplacementMin: 0, expectedReplacementMax: 1 }]);
  await client.applyBindingRemovals(plan); assert.deepEqual(state.rows, [replacement]);
});
test('scoped reads preserve the captured request and reject a foreign organization', async () => {
  let captured;
  const client = createCompositionClient({ target, request: async (path, body) => {
    captured = { path, body };
    return { dataset: { prodgrupromoc_produto: [{ NRORG: 999, CDGRUPROMOC: groupId, CDPRODUTO: productId }] } };
  } });
  await assert.rejects(client.readGroupItems(groupId), { code: 'INVALID_READ_ROW' });
  assert.equal(captured.path, PATHS.groupItems);
  assert.equal(captured.body.filter.find(row => row.name === 'CDGRUPROMOC').value, groupId);
  assert.equal(captured.body.filter.some(row => row.name === 'NRORG'), false);
});
test('creates a group through the newly captured UI contract and preserves other groups', async () => {
  const { client, state } = fixture();
  const plan = await client.previewGroupCreation({ groupId: '0000000013', name: 'ESCOLHA O ARROZ' });
  const receipt = await client.applyGroupCreation(plan);
  assert.equal(receipt.status, 'completed'); assert.equal(state.writes[0].requestType, 'DataSet');
  assert.deepEqual(state.writes[0].dataset[0], { __createdLocal: true, __is_new: true, CDGRUPROMOC: '0000000013', NMGRUPROMOC: 'ESCOLHA O ARROZ', changed: true });
  assert.equal(state.groups.length, 2);
  assert.equal(state.groups[0].NMGRUPROMOC, 'ACOMPANHAMENTO');
});
test('rejects other organizations and maxima outside the requested rule', () => {
  assert.throws(() => createCompositionClient({ request: () => {}, target: { ...target, organization: 99 } }), { code: 'INVALID_TARGET' });
  assert.throws(() => buildBindingPayload({ target, productId, groupId, groupName: 'G', min: 1, max: 2 }), { code: 'INVALID_LIMITS' });
});
test('observed parent update preserves all fields and persists checkpoints around write', async () => {
  const { client, state } = fixture();
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  const receipt = await client.applyBindings(plan);
  assert.equal(receipt.status, 'completed'); assert.equal(state.writes.length, 1);
  assert.equal(state.writes[0].dataset[0].PRESERVE, 'original');
  assert.equal(state.writes[0].dataset[0].CDPRODUTO, productId);
  assert.equal(state.rows[0].QTPRGRUPPROMOC, 1);
  assert.deepEqual(state.journal.map(r => r.entries.at(-1)?.status).filter(Boolean), ['sending', 'awaiting_readback', 'verified', 'verified']);
});
test('creation uses the saved UI envelope and verifies the server-assigned key', async () => {
  const { client, state } = fixture({ rows: [] });
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  const receipt = await client.applyBindings(plan);
  assert.equal(state.writes[0].dataset[0].__is_new, true);
  assert.equal(state.writes[0].dataset[0].__createdLocal, true);
  assert.equal(state.writes[0].dataset[0].CDPRODPROMOCAO, productId);
  assert.equal(receipt.entries[0].after.NRSEQGRPROMO, '0000000099');
});
test('parent bindings wait for the product type update before any binding write', async () => {
  const { client, state } = fixture({ type: '0' });
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  assert.equal(plan.blockers[0].desired, '3');
  await assert.rejects(client.applyBindings(plan), { code: 'PLAN_HAS_BLOCKERS' });
  assert.equal(state.writes.length, 0);
});
test('detects stale composition before writing and preserves external changes', async () => {
  const { client, state } = fixture();
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  state.rows[0].PRESERVE = 'external edit';
  await assert.rejects(client.applyBindings(plan), { code: 'CONCURRENT_COMPOSITION_CHANGE' });
  assert.equal(state.writes.length, 0); assert.equal(state.rows[0].PRESERVE, 'external edit');
});
test('stops on readback differences and never retries an uncertain write', async () => {
  const { client, state } = fixture({ onWrite: async (state, body) => {
    state.rows[0].QTPRGRUPROMIN = body.dataset[0].QTPRGRUPROMIN;
    state.rows[0].QTPRGRUPPROMOC = body.dataset[0].QTPRGRUPPROMOC;
    state.rows[0].PRESERVE = 'changed by server'; return {};
  } });
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  await assert.rejects(client.applyBindings(plan), { code: 'BINDING_READBACK_OTHER_FIELDS' });
  assert.equal(state.writes.length, 1); assert.equal(state.journal.at(-1).status, 'interrupted');
});
test('a checkpoint failure before sending prevents writes', async () => {
  const { client, state } = fixture();
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  const other = createCompositionClient({ request: async () => { throw new Error('request must not run'); }, target,
    checkpoint: async () => { throw new Error('journal unavailable'); } });
  await assert.rejects(other.applyBindings(plan), /journal unavailable/); assert.equal(state.writes.length, 0);
});
test('rejects tampered plans before API access', async () => {
  const { client, state } = fixture();
  const plan = await client.previewBindings([{ productId, groupId, min: 1, max: 1 }]);
  plan.items[0].min = 0;
  await assert.rejects(client.applyBindings(plan), { code: 'INVALID_PLAN' }); assert.equal(state.writes.length, 0);
});
