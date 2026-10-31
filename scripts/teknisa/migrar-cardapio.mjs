import { createHash, randomUUID } from 'node:crypto';

export const MIGRATION_RUNNER_VERSION = '2026-10-31.2';
const clone = value => structuredClone(value);
const canonical = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
const same = (a, b) => canonical(a) === canonical(b);
const sorted = values => [...values].sort();
const sameIds = (a, b) => same(sorted(a), sorted(b));
const id = value => typeof value === 'string' && /^\d{10}$/.test(value);
const requireThat = (value, code, message) => { if (!value) throw Object.assign(new Error(message), { code }); };
const idsOf = bindings => bindings.map(row => row.groupId);
const limits = row => ({ groupId: row.CDGRUPROMOC ?? row.groupId,
  min: row.QTPRGRUPROMIN ?? row.min, max: row.QTPRGRUPPROMOC ?? row.max });
const sortBindings = rows => rows.map(limits).sort((a, b) => a.groupId.localeCompare(b.groupId));

export function createCardapioMigrationRunner({ execution, exec, compClient, observationTool,
  checkpointSummary, checkpoint, readProduct, readProductInclusive, observationReader, componentsVerified = false,
  verifyComponentCoverage, now = () => new Date(), excludedProductIds = ['0000000128'] }) {
  execution = clone(execution || exec);
  requireThat(execution?.organization === 5482 && /^\d{4}$/.test(execution.branch) && /^\d{4}$/.test(execution.store)
    && ['products', 'desiredBindings', 'removeBindings', 'clearObs', 'groupDefinitions', 'productTypeChanges']
      .every(key => Array.isArray(execution[key])), 'INVALID_EXECUTION_PLAN', 'Informe o plano completo da unidade e loja conferidas.');
  requireThat(compClient && observationTool?.run && typeof (checkpointSummary || checkpoint) === 'function',
    'MISSING_MIGRATION_CALLBACK', 'Forneça os clientes autorizados e o checkpoint persistente.');
  const target = Object.freeze({ organization: execution.organization, branch: execution.branch, store: execution.store });
  requireThat([compClient.target, observationTool.target].every(scope => scope
    && ['organization', 'branch', 'store'].every(key => scope[key] === target[key])),
  'MIGRATION_CLIENT_TARGET_DIFFERENCE', 'Os clientes de composição e observação precisam informar o mesmo destino do plano.');
  const save = checkpointSummary || checkpoint;
  const productRead = readProduct || readProductInclusive || (compClient.readProduct ? value => compClient.readProduct(value) : null);
  requireThat(typeof productRead === 'function', 'MISSING_PRODUCT_READER', 'Forneça a leitura atual do produto, incluindo os inativos.');
  const productMap = new Map(execution.products.map(row => [row.productId, row]));
  requireThat(productMap.size === execution.products.length && [...productMap.keys()].every(id),
    'DUPLICATE_EXECUTION_PRODUCT', 'O plano contém produto repetido ou código inválido.');
  const clearMap = new Map(execution.clearObs.map(row => [row.productId, row]));
  requireThat(clearMap.size === execution.clearObs.length && execution.clearObs.every(row => productMap.has(row.productId)
    && row.group === '01' && Array.isArray(row.removeCodes) && row.removeCodes.every(code => /^\d{2}$/.test(code))
    && new Set(row.removeCodes).size === row.removeCodes.length && !(row.addCodes || []).length && row.clearOnlyAfterCoverage),
  'INVALID_OBSERVATION_CLEANUP', 'A limpeza deve conter apenas os vínculos de produto do grupo 01 previstos no plano.');
  const seenBindings = new Set();
  for (const row of execution.desiredBindings) {
    const key = row.productId + ':' + row.groupId;
    requireThat(productMap.has(row.productId) && id(row.groupId) && !seenBindings.has(key)
      && [0, 1].includes(row.min) && row.max === 1, 'INVALID_DESIRED_BINDING', 'Confira os grupos e limites sem duplicatas.');
    if (row.min === 0) requireThat(row.groupId === execution.groupIdMap?.sandwichAdditional,
      'UNEXPECTED_OPTIONAL_GROUP', 'O grupo opcional deve ser o adicional dedicado dos sanduíches.');
    seenBindings.add(key);
  }
  const definitionMap = new Map(execution.groupDefinitions.map(row => [row.groupId, row]));
  const queue = execution.products.map(row => row.productId).filter(value => !excludedProductIds.includes(value));
  const planHash = createHash('sha256').update(canonical(execution)).digest('hex');
  let running = false;
  const desiredFor = productId => execution.desiredBindings.filter(row => row.productId === productId);
  async function readCurrentObservations(productIds) {
    if (!productIds.length) return new Map();
    const result = observationReader ? await observationReader(productIds)
      : await observationTool.run('observacoes.vinculos.listar', { group: '01' });
    requireThat(Array.isArray(result), 'INVALID_OBSERVATION_READ', 'A consulta não retornou os vínculos esperados.');
    const seen = new Set();
    for (const row of result) requireThat(id(row.productId) && !seen.has(row.productId)
      && Array.isArray(row.codes) && row.codes.every(code => /^\d{2}$/.test(code))
      && new Set(row.codes).size === row.codes.length && (seen.add(row.productId), true),
    'INVALID_OBSERVATION_READ', 'A consulta contém códigos ou produtos repetidos.');
    // The validated complete list omits products once their last link is removed.
    return new Map(productIds.map(productId => [productId, clone(result.find(row => row.productId === productId)?.codes || [])]));
  }
  async function exactProduct(productId, expectedActive) {
    const row = await productRead(productId);
    requireThat(row?.NRORG === execution.organization && row.CDPRODUTO === productId
      && row.IDPRODATIVPR === (expectedActive ? 'S' : 'N'), 'PRODUCT_IDENTITY_OR_STATUS_CHANGED',
    'O produto mudou de identidade, organização ou estado ativo.');
    return row;
  }
  async function verifyParent(productId, contentCache = new Map()) {
    const spec = productMap.get(productId), cleanup = clearMap.get(productId), coverage = cleanup?.clearOnlyAfterCoverage || {};
    requireThat(spec, 'UNKNOWN_PARENT', 'O produto não pertence ao plano.');
    const row = await exactProduct(productId, spec.activeInCatalog === true);
    if (spec.activeInCatalog === false) {
      requireThat(coverage.reason === 'inactive_legacy_observations_cleanup_only'
        && coverage.mustNotCreateComposition === true && coverage.mustNotReactivate === true
        && desiredFor(productId).length === 0, 'INVALID_INACTIVE_CLEANUP', 'O inativo admite somente retirada de observações.');
      return { productId, active: false, inactiveCleanupOnly: true };
    }
    const desired = desiredFor(productId), current = await compClient.readBindings(productId);
    requireThat(Array.isArray(current) && current.every(binding => binding.NRORG === execution.organization
      && binding.CDPRODPROMOCAO === productId) && new Set(current.map(binding => binding.CDGRUPROMOC)).size === current.length
      && same(sortBindings(current), sortBindings(desired)), 'EXACT_PARENT_BINDINGS_DIFFERENCE',
    'O produto tem grupos ou quantidades diferentes do conjunto exato previsto.');
    if (desired.length) requireThat(row.IDTIPOCOMPPROD === '3', 'PRODUCT_TYPE_NOT_READY', 'O produto ainda precisa do tipo Promoção Combinada.');
    if (coverage.requiredGroupIds) requireThat(sameIds(coverage.requiredGroupIds, idsOf(desired)),
      'COVERAGE_PLAN_DIFFERENCE', 'A cobertura de observações diverge dos grupos do produto.');
    if (coverage.requiredOwnGroupIds) requireThat(sameIds(coverage.requiredOwnGroupIds, idsOf(desired)),
      'NESTED_CHOICES_NOT_ALLOWED', 'O componente auxiliar não deve criar escolhas próprias.');
    if (coverage.replacementOldGroup9MustBeAbsent) requireThat(!current.some(binding => binding.CDGRUPROMOC === '0000000009'),
      'OLD_SANDWICH_GROUP_PRESENT', 'O sanduíche ainda contém o grupo adicional antigo.');
    for (const binding of desired) {
      if (!contentCache.has(binding.groupId)) {
        const definition = definitionMap.get(binding.groupId), members = await compClient.readGroupItems(binding.groupId);
        const expected = definition?.components?.map(item => item.productId);
        requireThat(Array.isArray(expected) && expected.length && expected.every(id) && Array.isArray(members)
          && new Set(members.map(item => item.CDPRODUTO)).size === members.length
          && sameIds(members.map(item => item.CDPRODUTO), expected), 'GROUP_CONTENTS_DIFFERENCE',
        'Um grupo contém componentes diferentes dos previstos no plano.');
        contentCache.set(binding.groupId, true);
      }
    }
    if (coverage.parentId) {
      requireThat(coverage.parentId !== productId && productMap.has(coverage.parentId)
        && sameIds(coverage.parentMustContainGroups || [], idsOf(desiredFor(coverage.parentId))),
      'CHILD_COVERAGE_DIFFERENCE', 'O pai que recebe a escolha precisa estar previsto e cobrir os grupos informados.');
      await verifyParent(coverage.parentId, contentCache);
    }
    return { productId, active: true, groups: sortBindings(current), coverageParent: coverage.parentId || null };
  }
  async function runBatch({ productIds, offset = 0, size = 3 } = {}) {
    requireThat(!running, 'BATCH_ALREADY_RUNNING', 'Já existe um lote em execução nesta instância.');
    requireThat(Number.isSafeInteger(size) && size >= 1 && size <= 3 && Number.isSafeInteger(offset) && offset >= 0,
      'INVALID_BATCH_SIZE', 'Use lotes de até três produtos.');
    const selected = productIds ? [...productIds] : queue.slice(offset, offset + size);
    requireThat(selected.length > 0 && selected.length <= 3 && new Set(selected).size === selected.length
      && selected.every(productId => productMap.has(productId) && !excludedProductIds.includes(productId)),
    'INVALID_BATCH_PRODUCTS', 'Selecione até três produtos distintos; o caldo está excluído.');
    running = true;
    const summary = { kind: 'observation-composition-migration-batch', version: 1, id: randomUUID(), planHash,
      target: { organization: execution.organization, branch: execution.branch, store: execution.store },
      productIds: selected, status: 'running', phase: 'starting', startedAt: now().toISOString(),
      typeChanges: 0, bindingChanges: 0, bindingRemovals: 0, observationsRemoved: 0, verifiedParents: [], receiptIds: [] };
    const phase = async value => { summary.phase = value; await save(clone(summary)); };
    try {
      await phase('preflight');
      const selectedClear = selected.map(productId => clearMap.get(productId)).filter(Boolean);
      if (selectedClear.some(item => item.clearOnlyAfterCoverage.newComponentsTaxPriceStoreMustBeComplete)) {
        const verified = verifyComponentCoverage ? await verifyComponentCoverage(selected, execution) : componentsVerified;
        requireThat(verified === true || verified?.verified === true, 'COMPONENT_PREREQUISITES_PENDING', 'Confira os componentes, preços e vínculos de loja antes da limpeza.');
      }
      const typeIds = [];
      for (const productId of selected) {
        const spec = productMap.get(productId), row = await exactProduct(productId, spec.activeInCatalog === true);
        if (spec.activeInCatalog && desiredFor(productId).length && row.IDTIPOCOMPPROD !== '3') {
          requireThat(row.IDTIPOCOMPPROD === '0' && execution.productTypeChanges.some(change => change.productId === productId),
            'UNPLANNED_TYPE_CHANGE', 'A mudança de tipo não corresponde à prévia.'); typeIds.push(productId);
        }
      }
      if (typeIds.length) { await phase('product-types'); const plan = await compClient.previewProductTypes(typeIds);
        const receipt = await compClient.applyProductTypes(plan); summary.typeChanges = typeIds.length; summary.receiptIds.push(receipt.id || plan.id); }
      const selectedBindings = execution.desiredBindings.filter(binding => selected.includes(binding.productId));
      if (selectedBindings.length) { await phase('desired-bindings'); const plan = await compClient.previewBindings(selectedBindings.map(({ productId, groupId, min, max }) => ({ productId, groupId, min, max })));
        const receipt = await compClient.applyBindings(plan); summary.bindingChanges = receipt.entries?.filter(entry => entry.status === 'verified').length || 0;
        summary.receiptIds.push(receipt.id || plan.id); }
      const removals = [];
      for (const old of execution.removeBindings.filter(binding => selected.includes(binding.productId))) {
        const current = await compClient.readBindings(old.productId);
        if (!current.some(binding => binding.CDGRUPROMOC === old.groupId)) continue;
        const replacementGroupId = old.replacementGroupId || old.replacementGroup;
        const desired = desiredFor(old.productId).find(binding => binding.groupId === replacementGroupId);
        requireThat(desired, 'REMOVAL_REPLACEMENT_NOT_PLANNED', 'O grupo substituto não pertence ao resultado previsto.');
        const expectedReplacementMin = old.expectedReplacementMin ?? old.replacementMin ?? 1;
        const expectedReplacementMax = old.expectedReplacementMax ?? old.replacementMax ?? 1;
        requireThat(desired.min === expectedReplacementMin && desired.max === expectedReplacementMax,
          'REMOVAL_REPLACEMENT_LIMITS', 'Os limites do grupo substituto divergem do plano.');
        removals.push({ productId: old.productId, groupId: old.groupId, replacementGroupId, expectedReplacementMin, expectedReplacementMax });
      }
      if (removals.length) { await phase('old-bindings'); const plan = await compClient.previewBindingRemovals(removals);
        const receipt = await compClient.applyBindingRemovals(plan); summary.bindingRemovals = removals.length; summary.receiptIds.push(receipt.id || plan.id); }
      await phase('verify-exact-coverage');
      const contentCache = new Map();
      for (const productId of selected) summary.verifiedParents.push(await verifyParent(productId, contentCache));
      await phase('observation-preflight');
      const observationIds = selectedClear.map(item => item.productId), before = await readCurrentObservations(observationIds), changes = [];
      for (const item of selectedClear) {
        const current = before.get(item.productId);
        requireThat(current.every(code => item.removeCodes.includes(code)), 'UNEXPECTED_OBSERVATION_LINKS', 'Apareceram observações fora dos vínculos previstos.');
        if (current.length) changes.push({ productId: item.productId, add: [], remove: current });
      }
      if (changes.length) {
        await phase('observation-cleanup');
        const preview = await observationTool.run('observacoes.vinculos.planejar', { group: '01', changes });
        requireThat(preview?.planId, 'INVALID_OBSERVATION_PREVIEW', 'A prévia da limpeza não retornou identificador.');
        summary.receiptIds.push(preview.planId); await save(clone(summary));
        if (preview.changes !== 0) await observationTool.run('plano.aplicar', { planId: preview.planId });
      }
      await phase('verify-observations-empty');
      const after = await readCurrentObservations(observationIds);
      requireThat(observationIds.every(productId => after.get(productId).length === 0), 'OBSERVATIONS_REMAIN', 'A releitura ainda encontrou observações no produto.');
      summary.observationsRemoved = changes.reduce((sum, change) => sum + change.remove.length, 0);
      for (const productId of selected) await exactProduct(productId, productMap.get(productId).activeInCatalog === true);
      summary.status = 'completed'; summary.phase = 'completed'; summary.completedAt = now().toISOString();
      await save(clone(summary)); return clone(summary);
    } catch (error) { summary.status = 'interrupted'; summary.errorCode = error.code || 'MIGRATION_STEP_FAILED';
      try { await save(clone(summary)); } catch { summary.checkpointFailed = true; }
      error.summary = clone(summary); throw error;
    } finally { running = false; }
  }
  return Object.freeze({ target, runBatch, verifyParent, productIds: () => [...queue], batchCount: Math.ceil(queue.length / 3), planHash });
}

export const createMigrationRunner = createCardapioMigrationRunner;
