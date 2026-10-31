import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createTeknisa, createComponentClient, connectCompositionSession, connectObservedSession } from './teknisa.mjs';
const target = { organization: 5482, branch: '0002', store: '0001' };
function journal() {
  const records = new Map(), locks = [];
  return { records, locks, save: async row => { records.set(row.id, structuredClone(row)); },
    load: async id => structuredClone(records.get(id)), lock: async (scope, callback) => { locks.push(scope); return callback(); } };
}
const request = async () => { throw new Error('Injected-client commands must not issue duplicate requests from the entry point'); };
function bindingPlan() { return { id: randomUUID(), kind: 'composition-parent-bindings', target,
  blockers: [], items: [{ productId: '0000000073', productName: 'FICTIONAL PRODUCT', groupId: '0000000014', groupName: 'SAUCE', min: 1, max: 1,
    before: { QTPRGRUPROMIN: 0, QTPRGRUPPROMOC: 8, fixturePrivateValue: 'must-stay-in-journal' } }] }; }
test('the unique entry advertises missing optional clients and blocks them without requests', async () => {
  const tool = createTeknisa({ request, target, journal: journal() });
  assert.equal(tool.commands().find(item => item.name === 'composicoes.grupos.listar').configured, false);
  await assert.rejects(tool.run('composicoes.grupos.listar'), /Configure compositionClient/);
  assert.equal(typeof createComponentClient, 'function'); assert.equal(typeof connectCompositionSession, 'function');
  assert.equal(typeof connectObservedSession, 'function');
});
test('previews remain private and generic apply routes once through the injected client and unit lock', async () => {
  const store = journal(), plan = bindingPlan(); let previews = 0, writes = 0;
  const compositionClient = { target, previewBindings: async changes => { previews++; assert.equal(changes.length, 1); return plan; },
    applyBindings: async current => { writes++; assert.deepEqual(current, plan); return { id: plan.id, status: 'completed', entries: [{ status: 'verified', productId: '0000000073' }] }; } };
  const tool = createTeknisa({ request, target, journal: store, compositionClient });
  const preview = await tool.run('composicoes.vinculos.planejar', { changes: [{ productId: '0000000073' }] });
  assert.equal(previews, 1); assert.equal(writes, 0); assert.equal(store.records.get(preview.planId).status, 'prepared');
  assert.doesNotMatch(JSON.stringify(preview), /must-stay-in-journal/);
  const result = await tool.run('plano.aplicar', { planId: preview.planId });
  assert.equal(result.verified, 1); assert.equal(writes, 1); assert.deepEqual(store.locks, [target]);
  assert.deepEqual(await tool.run('plano.aplicar', { planId: preview.planId }), result); assert.equal(writes, 1);
  const receipt = await tool.run('recibo.consultar', { planId: preview.planId });
  assert.doesNotMatch(JSON.stringify(receipt), /must-stay-in-journal/);
  await assert.rejects(tool.run('plano.reverter', { planId: preview.planId }), /nova prévia/);
});
test('wrong injected destination and wrong prepared target are rejected before writes', async () => {
  const store = journal(); let writes = 0;
  const client = { target: { ...target, branch: '0003' }, readGroups: async () => { writes++; return []; } };
  await assert.rejects(createTeknisa({ request, target, journal: store, compositionClient: client }).run('composicoes.grupos.listar'), /outro destino/);
  const prepared = bindingPlan(); prepared.target = { ...target, store: '0002' };
  const tool = createTeknisa({ request, target, journal: store, compositionClient: { previewBindings: async () => prepared } });
  await assert.rejects(tool.run('composicoes.vinculos.planejar', { changes: [] }), /outro destino/);
  assert.equal(writes, 0); assert.equal(store.records.size, 0);
});
test('an interrupted injected apply is recorded and cannot be blindly repeated', async () => {
  const store = journal(), plan = bindingPlan(); let writes = 0;
  const tool = createTeknisa({ request, target, journal: store, compositionClient: {
    previewBindings: async () => plan, applyBindings: async () => { writes++; throw Object.assign(new Error('uncertain mock result'), { code: 'MOCK_WRITE_FAILED' }); },
  } });
  const preview = await tool.run('composicoes.vinculos.planejar', { changes: [] });
  await assert.rejects(tool.run('plano.aplicar', { planId: preview.planId }), { code: 'MOCK_WRITE_FAILED' });
  assert.equal(store.records.get(plan.id).status, 'interrupted');
  await assert.rejects(tool.run('plano.aplicar', { planId: preview.planId }), /nova prévia/); assert.equal(writes, 1);
});
test('component plans keep their checksum body intact and are applied by the injected facade', async () => {
  const store = journal(); let applied = 0;
  const plan = { kind: 'new-menu-components', target, checksum: 'fixture-checksum', entries: [
    { definition: { key: 'sample', name: 'FICTIONAL COMPONENT', rawTreeCode: '8000508001' }, before: { fixturePrivateValue: 'private-synthetic-row' } },
  ] };
  const tool = createTeknisa({ request, target, journal: store, componentClient: { target,
    preview: async definitions => { assert.equal(definitions.length, 1); return structuredClone(plan); },
    apply: async received => { assert.deepEqual(received, plan); applied++; return { status: 'completed', entries: [{ status: 'verified', productId: '8000508001' }] }; },
  } });
  const preview = await tool.run('componentes.planejar', { definitions: [{ key: 'sample' }] });
  assert.ok(preview.planId); assert.equal(Object.hasOwn(store.records.get(preview.planId).plan, 'id'), false);
  assert.doesNotMatch(JSON.stringify(preview), /private-synthetic-row/);
  await tool.run('plano.aplicar', { planId: preview.planId }); assert.equal(applied, 1);
});
test('migration batch execution is not published before unit-wide locking is coordinated', async () => {
  let calls = 0;
  const tool = createTeknisa({ request, target, journal: journal(), migrationRunner: {
    target: Object.freeze({ ...target }), runBatch: async () => { calls++; },
  } });
  assert.equal(tool.commands().some(item => item.name === 'cardapio.migrar.lote'), false);
  await assert.rejects(tool.run('cardapio.migrar.lote', { productIds: ['0000000073'] }), /Comando desconhecido/);
  assert.equal(calls, 0); assert.equal(Object.isFrozen(tool.target), true);
});
test('the facade refuses advanced runners without an immutable matching target', () => {
  assert.throws(() => createTeknisa({ request, target, journal: journal(), migrationRunner: { runBatch: async () => {} } }), /destino imutável/);
  assert.throws(() => createTeknisa({ request, target, journal: journal(), migrationRunner: { target: Object.freeze({ ...target, store: '0002' }) } }), /destino imutável/);
  assert.throws(() => createTeknisa({ request, target, journal: journal(), migrationRunner: { target: { ...target } } }), /destino imutável/);
});
