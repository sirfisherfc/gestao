import { createHash, randomUUID } from 'node:crypto';

// Contratos observados em 30/10/2026 na tela Cadastro de Observação (vnd57000).
const base = '/backend_man/index.php/';
export const OBSERVATION_PATHS = Object.freeze({
  produtos: `${base}vnd57000_cadastrodeobs_obsproduto`,
  vinculos: `${base}vnd57000_cadastrodeobs_obsproduto_produtos`,
  ocorrencias: `${base}vnd57000_cadastrodeobs_ocorrencias`,
  grupos: `${base}vnd57000_cadastrodeobs_grupObrig`,
  grupoItens: `${base}vnd57000_cadastrodeobs_prodObrig`,
  adicionar: `${base}vnd57000_cadastrodeobs_produtos/saveOservacaoProdutos`,
  remover: `${base}vnd57000_cadastrodeobs_obsproduto_produtos/remove`,
});
export const OBSERVATION_WRITE_PATHS = Object.freeze([OBSERVATION_PATHS.adicionar, OBSERVATION_PATHS.remover]);
const container = 'vnd57000_cadastroDeObservacao', label = 'Cadastro de Observação';
const origin = (widgetName, widgetLabel) => ({ containerName: container, widgetName, containerLabel: label, widgetLabel });
const code = value => /^\d{2}$/.test(value);
const filter = (target, group, extra = []) => [
  { name: 'NRORG', operator: '=', value: target.organization }, { name: 'CDGRPOCOR', operator: '=', value: group }, ...extra,
];
async function list(request, path, dataset, body) {
  const rows = (await request(path, { disableLoader: false, page: 1, itemsPerPage: 500, requestType: 'FilterData', ...body }))?.dataset?.[dataset];
  if (!Array.isArray(rows)) throw new Error('A consulta de observações não retornou o conjunto esperado.');
  if (rows.length >= 500) throw new Error('A consulta de observações atingiu o limite. Confira a paginação.');
  return rows;
}
function validateTarget(target, group) {
  if (!Number.isSafeInteger(target?.organization) || target.organization <= 0 || !code(group)) throw new Error('Informe a organização e o grupo de observação.');
}

export async function readOccurrences(request, target, group = '01') {
  validateTarget(target, group);
  return (await list(request, OBSERVATION_PATHS.ocorrencias, 'vnd57000_cadastrodeobs_ocorrencias',
    { filter: filter(target, group), origin: origin('Ocorrencia', 'Observações') }))
    .map(row => ({ code: row.CDOCORR, name: row.DSOCORR, kind: row.IDCONTROLAOBS, chargeProduct: row.CDPRODUTO || null }));
}
export async function readMandatoryGroups(request, target, group = '01') {
  validateTarget(target, group);
  const groups = await list(request, OBSERVATION_PATHS.grupos, 'vnd57000_cadastrodeobs_grupObrig',
    { filter: filter(target, group), origin: origin('grupoObserObrig', 'Grupo de Observações Obrigatórias') });
  const result = [];
  for (const item of groups) {
    const members = await list(request, OBSERVATION_PATHS.grupoItens, 'vnd57000_cadastrodeobs_prodObrig', {
      filter: filter(target, group, [{ name: 'CDGRUPOOBRIG', operator: '=', value: item.CDGRUPOOBRIG }]),
      origin: origin('prodObrigOcor', 'Ocorrências Obrigatórias do Grupo') });
    result.push({ id: item.CDGRUPOOBRIG, name: item.NMGRUPOBRIG, codes: members.map(row => row.CDOCORR) });
  }
  return result;
}
async function readProducts(request, target, group) {
  return list(request, OBSERVATION_PATHS.produtos, 'vnd57000_cadastrodeobs_obsproduto',
    { filter: filter(target, group), origin: origin('obsPorProduto', 'Observação por produto') });
}
async function readLinkRows(request, target, group, productId) {
  const rows = await list(request, OBSERVATION_PATHS.vinculos, 'vnd57000_cadastrodeobs_obsproduto_produtos', {
    filter: filter(target, group, [{ name: 'CDPRODUTO', operator: '=', value: productId }]),
    origin: origin('observacoes', 'Observações do produto') });
  if (rows.some(row => row.CDPRODUTO !== productId || String(row.NRORG) !== String(target.organization))) throw new Error('A consulta retornou vínculos de outro produto ou organização.');
  return rows;
}
const codesOf = rows => rows.map(row => row.CDOCORR).sort();
export async function readLinks(request, target, group = '01') {
  validateTarget(target, group);
  const products = await readProducts(request, target, group), result = [];
  for (const product of products) {
    result.push({ productId: product.CDPRODUTO, tree: product.CDARVPROD, name: String(product.NMPRODUTO).trim(),
      codes: codesOf(await readLinkRows(request, target, group, product.CDPRODUTO)) });
  }
  return result;
}

const canonical = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
const digest = plan => createHash('sha256').update(canonical(Object.fromEntries(Object.entries(plan).filter(([key]) => key !== 'checksum')))).digest('hex');

/** changes: [{ productId, add: ['01'], remove: ['55'] }]. Prepara a prévia sem gravar. */
export async function planLinks({ request, target, changes, journal, group = '01', now = () => new Date() }) {
  validateTarget(target, group);
  if (!Array.isArray(changes) || !changes.length) throw new Error('Informe os produtos e as observações a incluir ou retirar.');
  const occurrences = new Set((await readOccurrences(request, target, group)).map(item => item.code));
  const products = new Map((await readProducts(request, target, group)).map(row => [row.CDPRODUTO, row])), seen = new Set(), items = [];
  for (const change of changes) {
    const add = [...new Set(change.add || [])], remove = [...new Set(change.remove || [])];
    if (!products.has(change.productId)) throw new Error('O produto ainda não está em Observação por produto. Inclua o produto pela interface antes.');
    if (seen.has(change.productId)) throw new Error('O mesmo produto aparece duas vezes no pedido.');
    if ([...add, ...remove].some(item => !code(item) || !occurrences.has(item))) throw new Error('Uma observação informada não existe nesse grupo.');
    if (add.some(item => remove.includes(item))) throw new Error('A mesma observação foi pedida para incluir e retirar.');
    seen.add(change.productId);
    const before = codesOf(await readLinkRows(request, target, group, change.productId));
    const toAdd = add.filter(item => !before.includes(item)), toRemove = remove.filter(item => before.includes(item));
    if (!toAdd.length && !toRemove.length) continue;
    const after = [...before.filter(item => !toRemove.includes(item)), ...toAdd].sort();
    items.push({ productId: change.productId, name: String(products.get(change.productId).NMPRODUTO).trim(), before, add: toAdd, remove: toRemove, after });
  }
  const plan = { version: 1, kind: 'observacoes.vinculos', id: randomUUID(), group, target: structuredClone(target),
    createdAt: now().toISOString(), requested: changes.length, unchanged: changes.length - items.length, items };
  plan.checksum = digest(plan);
  await journal.save({ id: plan.id, status: 'prepared', plan, batches: [] });
  return summarizeLinks(plan);
}
export function summarizeLinks(plan) {
  return { planId: plan.id, kind: plan.kind, group: plan.group, requested: plan.requested, unchanged: plan.unchanged,
    changes: plan.items.length, sample: plan.items.slice(0, 8).map(({ productId, name, add, remove }) => ({ productId, name, add, remove })) };
}

/** Confere o estado anterior de cada produto, grava e relê antes de seguir. */
export async function applyLinks({ request, planId, journal, now = () => new Date() }) {
  const receipt = await journal.load(planId), plan = receipt.plan;
  if (plan?.kind !== 'observacoes.vinculos' || plan.checksum !== digest(plan) || receipt.id !== plan.id) throw new Error('O plano está incompleto ou foi modificado. Prepare uma nova prévia.');
  if (now().getTime() - Date.parse(plan.createdAt) > 30 * 60000 || Date.parse(plan.createdAt) > now().getTime() + 60000) {
    throw new Error('O plano passou do prazo de 30 minutos ou tem data inválida. Prepare uma nova prévia.');
  }
  return journal.lock(plan.target, async () => {
    receipt.status = 'running'; await journal.save(receipt);
    let changedThisRun = 0, alreadyApplied = 0;
    try {
      for (const item of plan.items) {
        const rows = await readLinkRows(request, plan.target, plan.group, item.productId), current = codesOf(rows);
        if (canonical(current) === canonical(item.after)) { alreadyApplied++; continue; }
        // Aceita retomar um produto interrompido no meio; qualquer outro estado indica alteração externa.
        const partial = current.every(c => item.before.includes(c) || item.add.includes(c)) && item.before.every(c => current.includes(c) || item.remove.includes(c));
        if (canonical(current) !== canonical(item.before) && !partial) throw new Error(`Os vínculos de ${item.name} mudaram desde a prévia. Prepare uma nova prévia.`);
        const checkpoint = { index: receipt.batches.length + 1, productId: item.productId, status: 'sending' };
        receipt.batches.push(checkpoint); await journal.save(receipt);
        const add = item.add.filter(c => !current.includes(c)), remove = rows.filter(row => item.remove.includes(row.CDOCORR));
        if (add.length) {
          const saved = await request(OBSERVATION_PATHS.adicionar, { requestType: 'DataSet',
            dataset: add.map(c => ({ __is_new: true, CDGRPOCOR: plan.group, NRORG: plan.target.organization, CDPRODUTO: item.productId, CDOCORR: c, changed: true })),
            origin: { containerLabel: label, widgetLabel: 'Adicionar Observações' } });
          if (saved?.dataset?.vnd57000_cadastrodeobs_obsproduto_produtos?.length !== add.length) throw new Error('A inclusão retornou um resultado inesperado. Confira o estado atual.');
        }
        if (remove.length) await request(OBSERVATION_PATHS.remover, { dataset: remove, requestType: 'DataSet', origin: origin('observacoes', 'Observações do produto') });
        const after = codesOf(await readLinkRows(request, plan.target, plan.group, item.productId));
        if (canonical(after) !== canonical(item.after)) throw new Error(`A releitura de ${item.name} não corresponde ao plano. Consulte o recibo.`);
        checkpoint.status = 'verified'; changedThisRun++; await journal.save(receipt);
      }
      receipt.status = 'completed'; receipt.completedAt = now().toISOString();
      receipt.result = { planId, verified: plan.items.length, changedThisRun, alreadyApplied, unchanged: plan.unchanged };
      await journal.save(receipt); return receipt.result;
    } catch (error) {
      receipt.status = 'interrupted'; receipt.errorCode = error.code || 'OPERATION_FAILED';
      await journal.save(receipt); error.receiptId = receipt.id; throw error;
    }
  });
}
