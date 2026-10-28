import { createHash, randomUUID } from 'node:crypto';
import { resource, resourceKey, readResource, PRINTER_FIELDS } from './recursos.mjs';
import { buildStoreProductSaveRow } from './normalizacao.mjs';

const canonical = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
const equal = (left, right) => canonical(left) === canonical(right);
const digest = plan => createHash('sha256').update(canonical(Object.fromEntries(Object.entries(plan).filter(([key]) => key !== 'checksum')))).digest('hex');
const idField = name => name === 'loja.impressoras' ? 'NRSEQIMPRLOJA' : 'CDPRODUTO';
function validatePatch(name, patch) {
  const spec = resource(name);
  if (!patch || !Object.keys(patch).length || Object.keys(patch).some(field => !spec.writable.includes(field))) {
    throw new Error('O plano contém campo sem operação de escrita cadastrada.');
  }
  for (const [field, value] of Object.entries(patch)) {
    if (field === 'NMIMPRLOJA' && (typeof value !== 'string' || !value.trim() || value.length > 30)) throw new Error('Informe um nome de impressora entre 1 e 30 caracteres.');
    if (field === 'NMPRODUTO' && (typeof value !== 'string' || !value.trim() || value.length > 50)) throw new Error('O nome do produto deve ter entre 1 e 50 caracteres.');
    if (['DSCOMPLNOME', 'DSINFADICPROD'].includes(field) && typeof value !== 'string') throw new Error('A descrição do produto precisa ser texto.');
    if (field === 'IDIMPCANITEM' && !['S', 'N'].includes(value)) throw new Error('Cancelamento deve ser S ou N.');
    if (Object.values(PRINTER_FIELDS).includes(field) && value !== null && !/^\d{5}$/.test(value)) throw new Error('Use o código da impressora da loja.');
    if (field === 'VRPRECITEM' && (typeof value !== 'number' || !Number.isFinite(value) || value <= 0
        || Math.abs(value * 100 - Math.round(value * 100)) > 1e-6)) throw new Error('Informe um preço positivo em reais com até duas casas decimais.');
  }
}
function validatePlan(plan) {
  if (plan?.version !== 1 || plan.checksum !== digest(plan) || !Array.isArray(plan.changes)
      || !Number.isFinite(Date.parse(plan.createdAt))) throw new Error('O plano está incompleto ou foi modificado. Prepare uma nova prévia.');
  const spec = resource(plan.resource), seen = new Set();
  for (const change of plan.changes) {
    validatePatch(plan.resource, change.set);
    if (resourceKey(spec, change.before) !== change.key || seen.has(change.key)) throw new Error('O plano contém chave inválida ou repetida.');
    seen.add(change.key);
  }
  return spec;
}
export function summarizePlan(plan) {
  return { planId: plan.id, resource: plan.resource, target: plan.target, total: plan.total,
    changes: plan.changes.length, unchanged: plan.unchanged,
    writeValidated: resource(plan.resource).writeValidated,
    sample: plan.changes.slice(0, 8).map(change => ({ id: change.before[idField(plan.resource)],
      name: change.before.NMPRODUTO || change.before.NMIMPRLOJA,
      before: Object.fromEntries(Object.keys(change.set).map(field => [field, change.before[field]])), after: change.set })) };
}
export async function preparePlan({ request, name, target, updates, journal, now = () => new Date() }) {
  if (!Array.isArray(updates) || !updates.length) throw new Error('Informe os registros e os valores desejados.');
  const rows = await readResource(request, name, target), spec = resource(name), seen = new Set(), changes = [];
  let unchanged = 0;
  for (const update of updates) {
    validatePatch(name, update.set);
    const found = rows.filter(row => update.key ? resourceKey(spec, row) === update.key : row[idField(name)] === update.id);
    if (found.length !== 1) throw new Error('Um código está ausente ou corresponde a vários registros. Use a chave completa.');
    const row = found[0], key = resourceKey(spec, row);
    if (seen.has(key)) throw new Error('O mesmo registro aparece duas vezes no pedido.');
    seen.add(key);
    const set = Object.fromEntries(Object.entries(update.set).filter(([field, value]) => !equal(row[field], value)));
    if (!Object.keys(set).length) { unchanged++; continue; }
    changes.push({ key, before: structuredClone(row), set: structuredClone(set) });
  }
  const plan = { version: 1, id: randomUUID(), resource: name, target: structuredClone(target),
    createdAt: now().toISOString(), total: rows.length, unchanged, changes };
  plan.checksum = digest(plan);
  await journal.save({ id: plan.id, status: 'prepared', plan, batches: [] });
  return summarizePlan(plan);
}
function checkRow(spec, change, row, requireAfter = false) {
  if (!row) throw new Error('O registro desapareceu. Interrompa e prepare uma nova prévia.');
  const derived = new Set([...spec.derived, ...Object.keys(change.set).flatMap(field => spec.derivedByField?.[field] || [])]);
  for (const field of new Set([...Object.keys(change.before), ...Object.keys(row)])) {
    if (derived.has(field)) continue;
    const desired = Object.hasOwn(change.set, field) ? change.set[field] : change.before[field];
    if (Object.hasOwn(change.set, field)) {
      if (!equal(row[field], desired) && (requireAfter || !equal(row[field], change.before[field]))) {
        throw new Error(`O valor de ${field} divergiu do plano. Consulte o recibo.`);
      }
    } else if (!equal(row[field], desired)) throw new Error(`Outro campo mudou: ${field}. Prepare uma nova prévia.`);
  }
}
async function validatePrinters(request, plan) {
  const values = plan.changes.flatMap(change => Object.entries(change.set)
    .filter(([field, value]) => Object.values(PRINTER_FIELDS).includes(field) && value !== null).map(([, value]) => value));
  if (!values.length) return;
  const printers = await readResource(request, 'loja.impressoras', plan.target);
  if (values.some(code => !printers.some(row => row.NRSEQIMPRLOJA === code && row.IDATIVO === 'S'))) {
    throw new Error('Uma impressora do plano está ausente ou inativa nessa loja.');
  }
}
export async function applyPlan({ request, planId, journal, operator, batchSize = 25, now = () => new Date() }) {
  const receipt = await journal.load(planId), plan = receipt.plan, spec = validatePlan(plan);
  if (receipt.id !== plan.id || !Number.isSafeInteger(operator) || operator <= 0 || !Number.isSafeInteger(batchSize)
      || batchSize < 1 || batchSize > 25) throw new Error('Informe recibo, operador e lote válidos.');
  if (!spec.writeValidated && plan.changes.length) throw new Error('A escrita desse recurso ainda precisa ser validada em uma operação real pela interface. A prévia está disponível.');
  if (now().getTime() - Date.parse(plan.createdAt) > 30 * 60000 || Date.parse(plan.createdAt) > now().getTime() + 60000) {
    throw new Error('O plano passou do prazo de 30 minutos ou tem data inválida. Prepare uma nova prévia.');
  }
  return journal.lock(plan.target, async () => {
    let changedThisRun = 0, alreadyApplied = 0;
    receipt.operator = operator;
    receipt.executions = [...(receipt.executions || []), { id: randomUUID(), operator, startedAt: now().toISOString() }];
    receipt.status = 'running'; await journal.save(receipt);
    try {
      await validatePrinters(request, plan);
      for (let offset = 0; offset < plan.changes.length; offset += batchSize) {
        const fresh = await readResource(request, plan.resource, plan.target), current = new Map(fresh.map(row => [resourceKey(spec, row), row]));
        // Confere todos os itens do plano antes de cada gravação, inclusive lotes anteriores.
        for (const change of plan.changes) checkRow(spec, change, current.get(change.key));
        const chunk = plan.changes.slice(offset, offset + batchSize), pending = [];
        for (const change of chunk) {
          const row = current.get(change.key);
          if (Object.entries(change.set).every(([field, value]) => equal(row[field], value))) { alreadyApplied++; continue; }
          pending.push({ change, row });
        }
        if (!pending.length) continue;
        const checkpoint = { index: receipt.batches.length + 1, status: 'sending', keys: pending.map(item => item.change.key) };
        receipt.batches.push(checkpoint); await journal.save(receipt);
        const dataset = pending.map(({ row, change }) => {
          if (row.__is_new !== false) throw new Error('A operação aceita apenas registros existentes.');
          return plan.resource === 'loja.produtos'
            ? buildStoreProductSaveRow({ ...row, ...change.set }, operator, now())
            : { ...row, ...change.set, changed: true };
        });
        const saved = await request(`${spec.path}/save`, { dataset, requestType: 'DataSet', origin: { ...spec.origin } });
        const returnedKeys = saved?.dataset?.[spec.dataset];
        const expectedKeys = new Set(pending.map(({ change }) => change.key));
        const validResponse = spec.saveResponse === 'keys'
          ? Array.isArray(returnedKeys) && returnedKeys.length === pending.length
            && returnedKeys.every(row => expectedKeys.has(resourceKey(spec, row)))
          : Array.isArray(saved) && saved.length === 0;
        if (!validResponse) throw new Error('A gravação retornou um resultado inesperado. Confira o estado atual.');
        const after = await readResource(request, plan.resource, plan.target), afterMap = new Map(after.map(row => [resourceKey(spec, row), row]));
        for (const { change } of pending) checkRow(spec, change, afterMap.get(change.key), true);
        checkpoint.status = 'verified'; checkpoint.verified = pending.length;
        changedThisRun += pending.length; await journal.save(receipt);
      }
      const final = await readResource(request, plan.resource, plan.target), finalMap = new Map(final.map(row => [resourceKey(spec, row), row]));
      for (const change of plan.changes) checkRow(spec, change, finalMap.get(change.key), true);
      receipt.status = 'completed'; receipt.completedAt = now().toISOString();
      receipt.result = { planId, verified: plan.changes.length, changedThisRun, alreadyApplied, unchanged: plan.unchanged };
      await journal.save(receipt); return receipt.result;
    } catch (error) {
      receipt.status = 'interrupted'; receipt.errorCode = error.code || 'OPERATION_FAILED';
      await journal.save(receipt); error.receiptId = receipt.id; throw error;
    }
  });
}

export async function prepareUndo({ request, planId, journal, now }) {
  const receipt = await journal.load(planId), plan = receipt.plan, spec = validatePlan(plan);
  if (receipt.status !== 'completed') throw new Error('A reversão exige um recibo concluído. Para falhas parciais, consulte o estado e retome o plano.');
  const rows = await readResource(request, plan.resource, plan.target), current = new Map(rows.map(row => [resourceKey(spec, row), row]));
  for (const change of plan.changes) checkRow(spec, change, current.get(change.key), true);
  return preparePlan({ request, name: plan.resource, target: plan.target, journal, now,
    updates: plan.changes.map(change => ({ key: change.key, set: Object.fromEntries(Object.keys(change.set).map(field => [field, change.before[field]])) })) });
}
