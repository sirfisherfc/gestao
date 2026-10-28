// Adaptador da API interna observada no Cadastro de Loja do Teknisa Retail.
// O chamador fornece o transporte autenticado da sessão atual, sem gravar tokens.
import { buildStoreProductSaveRow } from './normalizacao.mjs';
export { buildStoreProductSaveRow } from './normalizacao.mjs';
export const READ_PATH = '/backend_man/index.php/ger12300_cadloja_produtos';
export const SAVE_PATH = `${READ_PATH}/save`;
const DATASET = 'ger12300_cadloja_produtos';
const KEYS = ['NRORG', 'CDFILIAL', 'CDLOJA', 'CDPRODUTO'];
const ORIGIN = Object.freeze({
  containerName: 'ger12300_cadloja',
  widgetName: 'productByStoreWidget',
  containerLabel: 'Cadastro de Loja',
  widgetLabel: 'Produtos por Loja',
});
const key = row => KEYS.map(field => String(row[field])).join(':');

function validateTarget(target) {
  if (!Number.isSafeInteger(target?.organization) || target.organization <= 0
      || !/^\d{4}$/.test(target.branch) || !/^\d{4}$/.test(target.store)) {
    throw new Error('Informe organização, unidade e loja válidas.');
  }
}

export function planCancellationPrinting(rows, target) {
  validateTarget(target);
  if (!Array.isArray(rows) || rows.length >= 9999) {
    throw new Error('A consulta precisa retornar uma lista completa de vínculos.');
  }
  const seen = new Set();
  for (const row of rows) {
    if (String(row.NRORG) !== String(target.organization)
        || row.CDFILIAL !== target.branch || row.CDLOJA !== target.store
        || !/^\d+$/.test(row.CDPRODUTO) || !['N', 'S'].includes(row.IDIMPCANITEM)
        || row.__is_new !== false || seen.has(key(row))) {
      throw new Error('Vínculo fora do destino, duplicado ou com formato inesperado.');
    }
    seen.add(key(row));
  }
  return {
    total: rows.length,
    alreadyEnabled: rows.filter(row => row.IDIMPCANITEM === 'S').length,
    pending: rows.filter(row => row.IDIMPCANITEM === 'N').map(key),
  };
}

export async function readStoreProducts(request, target) {
  validateTarget(target);
  const result = await request(READ_PATH, {
    disableLoader: false,
    filter: [
      { name: 'NRORG', operator: '=', value: target.organization },
      { name: 'CDFILIAL', operator: '=', value: target.branch },
      { name: 'CDLOJA', operator: '=', value: target.store },
      { name: 'NIVELINICIAL', operator: '=', value: 'T' },
    ],
    page: 1,
    itemsPerPage: 9999,
    requestType: 'FilterData',
    origin: { ...ORIGIN },
  });
  const rows = result?.dataset?.[DATASET];
  planCancellationPrinting(rows, target);
  return rows;
}

function verify(before, after, expectedEnabled = new Set()) {
  const current = new Map(after.map(row => [key(row), row]));
  if (before.length !== after.length) throw new Error('A quantidade de vínculos mudou.');
  for (const previous of before) {
    const row = current.get(key(previous));
    if (!row) throw new Error('Um vínculo desapareceu da consulta.');
    for (const field of new Set([...Object.keys(previous), ...Object.keys(row)])) {
      if (['IDIMPCANITEM', 'DSIMPCANITEM'].includes(field)) continue;
      if (JSON.stringify(previous[field]) !== JSON.stringify(row[field])) {
        throw new Error(`Outro campo do vínculo mudou: ${field}. Interrompa e confira.`);
      }
    }
    if (previous.IDIMPCANITEM === 'S' && row.IDIMPCANITEM !== 'S') {
      throw new Error('Uma opção que já estava marcada foi desmarcada.');
    }
    if (expectedEnabled.has(key(row)) && row.IDIMPCANITEM !== 'S') {
      throw new Error('A releitura encontrou um produto ainda desmarcado.');
    }
  }
}

/** request(path, body) deve retornar JSON e rejeitar HTTP inválido, sem logar credenciais. */
export async function enableCancellationPrinting({
  request, target, operator, apply = false, batchSize = 25, now = () => new Date(), onBatch,
}) {
  if (typeof request !== 'function' || typeof apply !== 'boolean' || !Number.isSafeInteger(batchSize)
      || batchSize < 1 || batchSize > 25) {
    throw new Error('Informe transporte, apply como true ou false e lote entre 1 e 25.');
  }
  const initial = structuredClone(await readStoreProducts(request, target));
  const plan = planCancellationPrinting(initial, target);
  const report = {
    mode: apply ? 'apply' : 'preview', total: plan.total,
    alreadyEnabled: plan.alreadyEnabled, pending: plan.pending.length,
    changed: 0, finalEnabled: plan.alreadyEnabled, batches: [],
  };
  if (!apply || !plan.pending.length) return report;
  if (!Number.isSafeInteger(operator) || operator <= 0) {
    throw new Error('Informe o operador observado na sessão atual.');
  }
  for (let offset = 0; offset < plan.pending.length; offset += batchSize) {
    const fresh = await readStoreProducts(request, target);
    verify(initial, fresh);
    const batch = new Set(plan.pending.slice(offset, offset + batchSize));
    const rows = fresh.filter(row => batch.has(key(row)) && row.IDIMPCANITEM === 'N');
    if (!rows.length) continue;
    const date = now();
    const result = await request(SAVE_PATH, {
      dataset: rows.map(row => buildStoreProductSaveRow({ ...row, IDIMPCANITEM: 'S' }, operator, date)),
      requestType: 'DataSet', origin: { ...ORIGIN },
    });
    if (!Array.isArray(result) || result.length) {
      throw new Error('A gravação retornou um formato inesperado. Confira antes de repetir.');
    }
    const after = await readStoreProducts(request, target);
    verify(fresh, after, new Set(rows.map(key)));
    report.changed += rows.length;
    report.batches.push({ requested: rows.length, verified: rows.length });
    if (onBatch) await onBatch({ ...report.batches.at(-1) });
  }
  const final = await readStoreProducts(request, target);
  verify(initial, final, new Set(plan.pending));
  report.finalEnabled = final.filter(row => row.IDIMPCANITEM === 'S').length;
  report.pending = final.length - report.finalEnabled;
  return report;
}
