import test from 'node:test';
import assert from 'node:assert/strict';
import { createCardapioMigrationRunner } from './migrar-cardapio.mjs';
const A = '0000000073', B = '0000000117', I = '0000000023', CALDO = '0000000128';
const G = '0000000014', OLD = '0000000011', OPTIONAL = '0000000020', OLD_OPTIONAL = '0000000009';
const C1 = '0000001001', C2 = '0000001002';
const row = (productId, groupId, min = 1) => ({ NRORG: 5482, CDPRODPROMOCAO: productId, CDGRUPROMOC: groupId, QTPRGRUPROMIN: min, QTPRGRUPPROMOC: 1 });
function fixture({ failTypes = false, extraGroup = false, extraMember = false, extraObservation = false } = {}) {
  const execution = { organization: 5482, branch: '0002', store: '0001', groupIdMap: { sandwichAdditional: OPTIONAL },
    products: [A, B, I, CALDO].map(productId => ({ productId, activeInCatalog: productId !== I })),
    productTypeChanges: [{ productId: A }],
    desiredBindings: [{ productId: A, groupId: G, min: 1, max: 1 }, { productId: B, groupId: OPTIONAL, min: 0, max: 1 }],
    removeBindings: [{ productId: A, groupId: OLD, replacementGroup: G },
      { productId: B, groupId: OLD_OPTIONAL, replacementGroup: OPTIONAL, replacementMin: 0, replacementMax: 1 }],
    groupDefinitions: [{ groupId: G, components: [{ productId: C1 }] }, { groupId: OPTIONAL, components: [{ productId: C2 }] }],
    clearObs: [{ productId: A, group: '01', removeCodes: ['05'], addCodes: [], clearOnlyAfterCoverage: { requiredGroupIds: [G], newComponentsTaxPriceStoreMustBeComplete: true } },
      { productId: B, group: '01', removeCodes: ['53'], addCodes: [], clearOnlyAfterCoverage: { requiredGroupIds: [OPTIONAL], replacementOldGroup9MustBeAbsent: true } },
      { productId: I, group: '01', removeCodes: ['34'], addCodes: [], clearOnlyAfterCoverage: { reason: 'inactive_legacy_observations_cleanup_only', mustNotCreateComposition: true, mustNotReactivate: true } }],
  };
  const state = { log: [], saved: [], writes: 0, product: new Map([A, B, I, CALDO].map(productId => [productId,
    { NRORG: 5482, CDPRODUTO: productId, IDPRODATIVPR: productId === I ? 'N' : 'S', IDTIPOCOMPPROD: productId === A ? '0' : '3' }])),
    bindings: new Map([[A, [row(A, OLD), ...(extraGroup ? [row(A, '0000000099')] : [])]], [B, [row(B, OLD_OPTIONAL, 0)]], [I, []], [CALDO, []]]),
    members: new Map([[G, [C1, ...(extraMember ? [C2] : [])]], [OPTIONAL, [C2]]]),
    obs: new Map([[A, ['05', ...(extraObservation ? ['99'] : [])]], [B, ['53']], [I, ['34']]]), obsPlans: new Map(),
  };
  const compClient = {
    target: Object.freeze({ organization: 5482, branch: '0002', store: '0001' }),
    readBindings: async id => structuredClone(state.bindings.get(id) || []),
    readGroupItems: async id => (state.members.get(id) || []).map(CDPRODUTO => ({ CDPRODUTO })),
    previewProductTypes: async ids => ({ id: 'type-plan', ids }),
    applyProductTypes: async plan => { state.log.push('type-write'); if (failTypes) throw new Error('type failed');
      for (const id of plan.ids) { state.product.get(id).IDTIPOCOMPPROD = '3'; state.writes++; } return { id: plan.id }; },
    previewBindings: async changes => ({ id: 'binding-plan', changes }),
    applyBindings: async plan => { state.log.push('binding-write'); const entries = [];
      for (const change of plan.changes) { const rows = state.bindings.get(change.productId); const existing = rows.find(item => item.CDGRUPROMOC === change.groupId);
        if (!existing) { rows.push(row(change.productId, change.groupId, change.min)); state.writes++; entries.push({ status: 'verified' }); }
        else if (existing.QTPRGRUPROMIN !== change.min || existing.QTPRGRUPPROMOC !== change.max) { existing.QTPRGRUPROMIN = change.min; existing.QTPRGRUPPROMOC = change.max; state.writes++; }
      } return { id: plan.id, entries }; },
    previewBindingRemovals: async changes => { state.log.push('removal-preview'); state.removalChanges = changes; return { id: 'remove-plan', changes }; },
    applyBindingRemovals: async plan => { state.log.push('removal-write'); for (const change of plan.changes) {
      state.bindings.set(change.productId, state.bindings.get(change.productId).filter(item => item.CDGRUPROMOC !== change.groupId)); state.writes++; } return { id: plan.id }; },
  };
  const observationTool = { target: Object.freeze({ organization: 5482, branch: '0002', store: '0001' }), run: async (command, args) => {
    state.log.push(command);
    if (command === 'observacoes.vinculos.listar') return [...state.obs].filter(([, codes]) => codes.length).map(([productId, codes]) => ({ productId, codes: [...codes] }));
    if (command === 'observacoes.vinculos.planejar') { const planId = 'obs-' + state.obsPlans.size; state.obsPlans.set(planId, args.changes); return { planId, changes: args.changes.length }; }
    if (command === 'plano.aplicar') { for (const change of state.obsPlans.get(args.planId)) { state.obs.set(change.productId, state.obs.get(change.productId).filter(code => !change.remove.includes(code))); state.writes++; } return { verified: state.obsPlans.get(args.planId).length }; }
    throw new Error('unexpected command');
  } };
  const options = { execution, compClient, observationTool, componentsVerified: true,
    readProductInclusive: async id => structuredClone(state.product.get(id)), checkpointSummary: async summary => { state.saved.push(structuredClone(summary)); } };
  return { state, options, runner: createCardapioMigrationRunner(options) };
}
test('advanced runner exposes an immutable destination and rejects unscoped or foreign clients', () => {
  const { runner, options } = fixture();
  assert.deepEqual(runner.target, { organization: 5482, branch: '0002', store: '0001' });
  assert.equal(Object.isFrozen(runner.target), true);
  assert.throws(() => { runner.target.branch = '0003'; }, TypeError);
  assert.throws(() => createCardapioMigrationRunner({ ...options, compClient: { ...options.compClient, target: undefined } }), { code: 'MIGRATION_CLIENT_TARGET_DIFFERENCE' });
  assert.throws(() => createCardapioMigrationRunner({ ...options,
    observationTool: { ...options.observationTool, target: { organization: 5482, branch: '0003', store: '0001' } } }), { code: 'MIGRATION_CLIENT_TARGET_DIFFERENCE' });
});
test('writes types, desired bindings, removals and verifies all parents before clearing observations', async () => {
  const { runner, state } = fixture();
  const summary = await runner.runBatch({ productIds: [A, B, I] });
  assert.equal(summary.status, 'completed'); assert.equal(summary.observationsRemoved, 3);
  const at = value => state.log.indexOf(value);
  assert.ok(at('type-write') < at('binding-write')); assert.ok(at('binding-write') < at('removal-write'));
  assert.ok(at('removal-write') < at('observacoes.vinculos.planejar'));
  assert.equal(state.removalChanges.find(item => item.productId === B).expectedReplacementMin, 0);
  assert.equal(state.removalChanges.find(item => item.productId === B).expectedReplacementMax, 1);
  assert.equal(state.removalChanges.some(item => item.allowNoReplacement), false);
  assert.equal(state.product.get(I).IDPRODATIVPR, 'N');
  assert.equal(state.bindings.get(I).length, 0); assert.equal(state.saved.at(-1).status, 'completed');
});
test('rerunning the completed batch does not duplicate groups or clear a missing observation product', async () => {
  const { runner, state } = fixture(); await runner.runBatch({ productIds: [A, B, I] });
  const writes = state.writes, observationPlans = state.obsPlans.size;
  const summary = await runner.runBatch({ productIds: [A, B, I] });
  assert.equal(summary.observationsRemoved, 0); assert.equal(state.writes, writes); assert.equal(state.obsPlans.size, observationPlans);
  assert.equal(state.bindings.get(A).length, 1); assert.equal(state.bindings.get(B).length, 1);
});
test('unexpected parent groups block cleanup for the entire batch', async () => {
  const { runner, state } = fixture({ extraGroup: true });
  await assert.rejects(runner.runBatch({ productIds: [A, B, I] }), { code: 'EXACT_PARENT_BINDINGS_DIFFERENCE' });
  assert.equal(state.obsPlans.size, 0); assert.deepEqual(state.obs.get(A), ['05']); assert.deepEqual(state.obs.get(B), ['53']);
});
test('unexpected group components block cleanup', async () => {
  const { runner, state } = fixture({ extraMember: true });
  await assert.rejects(runner.runBatch({ productIds: [A] }), { code: 'GROUP_CONTENTS_DIFFERENCE' }); assert.equal(state.obsPlans.size, 0);
});
test('failure before composition is ready never starts observation cleanup', async () => {
  const { runner, state } = fixture({ failTypes: true });
  await assert.rejects(runner.runBatch({ productIds: [A, B] }), /type failed/);
  assert.equal(state.log.includes('observacoes.vinculos.planejar'), false); assert.equal(state.saved.at(-1).status, 'interrupted');
});
test('new observation links outside the execution plan are preserved and block cleanup', async () => {
  const { runner, state } = fixture({ extraObservation: true });
  await assert.rejects(runner.runBatch({ productIds: [A] }), { code: 'UNEXPECTED_OBSERVATION_LINKS' });
  assert.equal(state.obsPlans.size, 0); assert.deepEqual(state.obs.get(A), ['05', '99']);
});
test('caldo, duplicate selections and excessive batches are rejected before writes', async () => {
  const { runner, state } = fixture();
  await assert.rejects(runner.runBatch({ productIds: [CALDO] }), { code: 'INVALID_BATCH_PRODUCTS' });
  await assert.rejects(runner.runBatch({ productIds: [A, A] }), { code: 'INVALID_BATCH_PRODUCTS' });
  await assert.rejects(runner.runBatch({ productIds: [A], size: 4 }), { code: 'INVALID_BATCH_SIZE' });
  assert.equal(state.writes, 0); assert.equal(runner.productIds().includes(CALDO), false);
});
