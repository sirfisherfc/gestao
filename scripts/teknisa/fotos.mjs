import { createHash, randomUUID } from 'node:crypto';
import { readFile, stat } from 'node:fs/promises';
import { basename, resolve } from 'node:path';

// Exact envelopes captured from Cadastro de Imagem do Produto on 31/10/2026.
// The read endpoint omits CDPRODUTO in its rows. The request scope is retained
// in every snapshot; no equality operator or global-product field is inferred.
export const PHOTO_PATHS = Object.freeze({
  read: '/backend_man/index.php/select_imgProd',
  save: '/backend_man/index.php/saveProdFili',
});
export const PHOTO_SCOPE = Object.freeze({ organization: 5482, branch: '0002' });
export const PHOTO_CONTRACT_VALIDATED_AT = '2026-10-31';
const READ_ORIGIN = Object.freeze({ containerName: 'cadImgProd', widgetName: 'imgProdWidget',
  containerLabel: 'Cadastro de Imagem do Produto', widgetLabel: 'Imagens do Produto' });
const SAVE_ORIGIN = Object.freeze({ containerLabel: 'Cadastro de Imagem do Produto', widgetLabel: 'Imagens do Produto' });
const clone = value => structuredClone(value);
const fail = (code, message) => { throw Object.assign(new Error(message), { code }); };
const requireThat = (condition, code, message) => { if (!condition) fail(code, message); };
const productIdValid = value => typeof value === 'string' && /^\d{10}$/.test(value);
const shaValid = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const canonical = value => JSON.stringify(value, (_, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);
const digest = value => createHash('sha256').update(typeof value === 'string' || Buffer.isBuffer(value) ? value : canonical(value)).digest('hex');
const scopeKey = scope => `${scope.organization}:${scope.branch}`;
const busyScopes = new Set();
const uncertainProducts = new Set();
function checkScope(scope) {
  requireThat(scope?.organization === 5482 && scope.branch === '0002'
    && Object.keys(scope).every(key => ['organization', 'branch'].includes(key)),
  'INVALID_PHOTO_SCOPE', 'As fotos foram conferidas na organização 5482 e unidade 0002.');
}
function checkProduct(productId) {
  requireThat(productIdValid(productId), 'INVALID_PRODUCT_ID', 'Informe o código de dez dígitos conferido do produto.');
}
export function isObservedPhotoUrl(url) {
  return typeof url === 'string'
    && /^https:\/\/midia\.teknisa\.com\/files\/Manage588fa3b08b544\/ImgProd\/[a-f0-9]+\.jpg$/.test(url);
}
export function buildPhotoReadBody(scope, productId) {
  checkScope(scope); checkProduct(productId);
  return { disableLoader: false, filter: [
    { name: 'CDPRODUTO', operator: '>=', value: productId },
    { name: 'CDFILIAL', operator: '>=', value: scope.branch },
    { name: 'NRORG', operator: '=', value: scope.organization },
  ], page: 1, itemsPerPage: 50, requestType: 'FilterData', origin: { ...READ_ORIGIN } };
}
function validateSource(source) {
  requireThat(source && typeof source.path === 'string' && source.path.trim() && shaValid(source.sha256),
    'INVALID_SOURCE', 'Informe o arquivo aprovado e seu SHA256.');
  requireThat(typeof source.name === 'string' && source.name.trim(), 'INVALID_IMAGE_NAME', 'Informe o nome conferido da imagem.');
  checkProduct(source.productId);
  return { productId: source.productId, name: source.name.trim(), path: resolve(source.path), sha256: source.sha256 };
}
async function loadSource(source) {
  const [bytes, info] = await Promise.all([readFile(source.path), stat(source.path)]);
  requireThat(info.isFile() && bytes.length > 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff
    && /\.jpe?g$/i.test(basename(source.path)), 'UNOBSERVED_IMAGE_FORMAT', 'O contrato observado envia um arquivo JPEG.');
  requireThat(digest(bytes) === source.sha256, 'SOURCE_HASH_CHANGED', 'O arquivo mudou desde a aprovação. Confira a foto antes de enviar.');
  return { bytes, file: { b64File: `data:image/jpeg;base64,${bytes.toString('base64')}`, name: basename(source.path),
    lastModified: Math.trunc(info.mtimeMs), lastModifiedDate: new Date(Math.trunc(info.mtimeMs)).toISOString(),
    webkitRelativePath: '', size: bytes.length, type: 'image/jpeg' } };
}
export function buildPhotoSaveBody({ scope = PHOTO_SCOPE, productId, name, file }) {
  checkScope(scope); checkProduct(productId);
  requireThat(typeof name === 'string' && name.trim() && file?.type === 'image/jpeg'
    && typeof file.b64File === 'string' && /^data:image\/jpeg;base64,[A-Za-z0-9+/]+={0,2}$/.test(file.b64File)
    && Number.isSafeInteger(file.size) && file.size > 0 && typeof file.name === 'string'
    && Number.isSafeInteger(file.lastModified) && Number.isFinite(Date.parse(file.lastModifiedDate))
    && file.webkitRelativePath === '', 'INVALID_PHOTO_FILE', 'Use o arquivo JPEG preparado a partir da fonte aprovada.');
  const bytes = Buffer.from(file.b64File.slice('data:image/jpeg;base64,'.length), 'base64');
  requireThat(bytes.length === file.size && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff,
    'INVALID_PHOTO_FILE', 'Os bytes do arquivo não conferem com o corpo do envio.');
  return { requestType: 'Row', row: {
    __createdLocal: true, __is_new: true, __index: 0, CDFILIAL: scope.branch, CDPRODUTO: productId,
    CDIMAGEM: 1, NMIMAGEM: name.trim(), LINKIMGPROD: [clone(file)],
    __rightActions: [], __leftActions: [], __notSelectable: false, __isSelected: false, changed: true,
    $error: { CDIMAGEM: [], NMIMAGEM: [], LINKIMGPROD: [] }, TPMIDIA: 'Imagem', NRORG: scope.organization,
  }, origin: { ...SAVE_ORIGIN } };
}

// Public fetch only: exact returned URL, no credentials, cookies, or redirects.
// Callers may inject an equivalent public-asset bridge when browser CORS blocks.
export function createPublicPhotoHasher({ fetchImpl = globalThis.fetch } = {}) {
  requireThat(typeof fetchImpl === 'function', 'MISSING_FETCH', 'Forneça a leitura pública do arquivo de imagem.');
  return async url => {
    requireThat(isObservedPhotoUrl(url), 'UNOBSERVED_PHOTO_URL', 'A URL da imagem está fora do caminho observado.');
    const response = await fetchImpl(url, { method: 'GET', credentials: 'omit', redirect: 'error' });
    requireThat(response.ok && !response.redirected && (!response.url || response.url === url),
      'PHOTO_FETCH_FAILED', 'A imagem publicada não pôde ser lida no endereço retornado.');
    return digest(Buffer.from(await response.arrayBuffer()));
  };
}

export function createProductPhotoClient({ request, hashImage, checkpoint, approvedSources = [], scope = PHOTO_SCOPE,
  now = () => new Date(), maxBaselineAgeMs = 10 * 60 * 1000 }) {
  checkScope(scope); scope = Object.freeze(clone(scope));
  requireThat(typeof request === 'function' && typeof hashImage === 'function', 'MISSING_PHOTO_TRANSPORT',
    'Forneça o transporte autorizado e a leitura pública dos bytes da imagem.');
  requireThat(Array.isArray(approvedSources), 'MISSING_APPROVED_SOURCES',
    'Forneça os produtos e hashes de fotos já aprovados.');
  requireThat(Number.isSafeInteger(maxBaselineAgeMs) && maxBaselineAgeMs > 0, 'INVALID_BASELINE_AGE', 'Informe a validade da prévia.');
  const approved = new Map();
  for (const raw of approvedSources) {
    const source = validateSource(raw);
    requireThat(!approved.has(source.productId), 'DUPLICATE_APPROVAL', 'Cada produto deve ter uma única foto aprovada.');
    approved.set(source.productId, Object.freeze(source));
  }
  const issuedPlans = new Map(), usedPlans = new Set();
  const time = () => {
    const value = now(); requireThat(value instanceof Date && Number.isFinite(value.getTime()), 'INVALID_CLOCK', 'Confira o relógio da execução.');
    return value;
  };
  async function readImages(requestScope, productId) {
    checkScope(requestScope); checkProduct(productId);
    requireThat(canonical(requestScope) === canonical(scope), 'INVALID_PHOTO_SCOPE', 'A consulta deve conservar a unidade do cliente.');
    const body = buildPhotoReadBody(scope, productId), response = await request(PHOTO_PATHS.read, body);
    const rows = response?.dataset?.select_prodFili;
    requireThat(Array.isArray(rows), 'INVALID_IMAGE_DATASET', 'A consulta não retornou o conjunto de imagens observado.');
    requireThat(rows.length < body.itemsPerPage, 'INCOMPLETE_IMAGE_PAGE', 'A consulta atingiu o limite observado. Confira a cobertura antes de gravar.');
    const ids = new Set();
    for (const row of rows) {
      requireThat(row && row.CDFILIAL === scope.branch && /^\d+$/.test(String(row.CDIMAGEM))
        && Number(row.CDIMAGEM) > 0 && typeof row.NMIMAGEM === 'string' && isObservedPhotoUrl(row.LINKIMGPROD)
        && (row.NRORG === undefined || Number(row.NRORG) === scope.organization)
        && (row.CDPRODUTO === undefined || row.CDPRODUTO === productId) && !ids.has(String(row.CDIMAGEM)),
      'INVALID_IMAGE_ROW', 'A consulta retornou outra unidade, chave repetida ou endereço de imagem não observado.');
      ids.add(String(row.CDIMAGEM));
    }
    return { scope: clone(scope), productId, request: body, rows: clone(rows), readAt: time().toISOString() };
  }
  async function snapshot(productId) {
    const result = await readImages(scope, productId), images = [];
    for (const row of result.rows) {
      const sha256 = await hashImage(row.LINKIMGPROD);
      requireThat(shaValid(sha256), 'INVALID_REMOTE_HASH', 'A leitura pública não retornou um SHA256 válido.');
      images.push({ imageId: String(row.CDIMAGEM), name: row.NMIMAGEM, url: row.LINKIMGPROD, sha256 });
    }
    return { ...result, images, fingerprint: digest({ scope, productId, request: result.request, rows: result.rows, images }) };
  }
  function desiredState(current, source) {
    if (!current.images.length) return 'missing';
    requireThat(current.images.every(image => image.sha256 === source.sha256), 'EXISTING_DIFFERENT_IMAGE',
      'O produto já tem uma imagem com outros bytes. Confira o cadastro antes de substituir.');
    return 'already_desired';
  }
  async function preview(productIds = [...approved.keys()]) {
    requireThat(Array.isArray(productIds) && productIds.length > 0 && new Set(productIds).size === productIds.length,
      'INVALID_PRODUCT_LIST', 'Informe uma lista de produtos sem códigos repetidos.');
    const items = [];
    for (const productId of productIds) {
      const source = approved.get(productId);
      requireThat(source, 'UNAPPROVED_PRODUCT', 'A lista contém produto sem foto aprovada.');
      await loadSource(source);
      const before = await snapshot(productId);
      items.push({ source: clone(source), before, status: desiredState(before, source) });
    }
    const plan = { version: 'photo-plan-v1', id: randomUUID(), scope: clone(scope), createdAt: time().toISOString(), items };
    issuedPlans.set(plan.id, digest(plan));
    return clone(plan);
  }
  async function saveImage(body) {
    // Private plan execution calls this method after the checkpoint. The public
    // method is intentionally absent: callers cannot bypass baseline checks.
    return request(PHOTO_PATHS.save, body);
  }
  async function apply(plan) {
    requireThat(plan && issuedPlans.get(plan.id) === digest(plan) && !usedPlans.has(plan.id),
      'INVALID_OR_USED_PLAN', 'Prepare uma nova prévia neste cliente antes de gravar.');
    requireThat(typeof checkpoint === 'function', 'MISSING_CHECKPOINT', 'Forneça um recibo persistente antes de gravar.');
    const age = time().getTime() - Date.parse(plan.createdAt);
    requireThat(age >= 0 && age <= maxBaselineAgeMs, 'STALE_PHOTO_PLAN', 'A prévia venceu. Consulte as imagens novamente.');
    const key = scopeKey(scope);
    requireThat(!busyScopes.has(key), 'PHOTO_EXECUTION_BUSY', 'Já existe uma execução de fotos nesta unidade.');
    for (const item of plan.items) requireThat(!uncertainProducts.has(`${key}:${item.source.productId}`),
      'UNRESOLVED_IMAGE_SAVE', 'Confira a gravação pendente antes de executar outra prévia para esse produto.');
    busyScopes.add(key); usedPlans.add(plan.id);
    const receipt = { version: 'photo-receipt-v1', id: randomUUID(), planId: plan.id, scope: clone(scope),
      startedAt: time().toISOString(), status: 'preflight', entries: [] };
    let activeEntry;
    try {
      await checkpoint(clone(receipt));
      // Check every baseline before starting a batch that could partially save.
      for (const item of plan.items) {
        await loadSource(item.source);
        const current = await snapshot(item.source.productId);
        requireThat(current.fingerprint === item.before.fingerprint, 'PHOTO_BASELINE_CHANGED', 'As imagens mudaram desde a prévia. Consulte novamente.');
      }
      receipt.status = 'running'; await checkpoint(clone(receipt));
      for (const item of plan.items) {
        const current = await snapshot(item.source.productId);
        requireThat(current.fingerprint === item.before.fingerprint, 'PHOTO_BASELINE_CHANGED', 'As imagens mudaram durante a execução. Consulte novamente.');
        const { file } = await loadSource(item.source);
        activeEntry = { productId: item.source.productId, name: item.source.name, sourceSha256: item.source.sha256,
          sourcePath: item.source.path, request: clone(current.request), before: clone(current), status: desiredState(current, item.source) };
        receipt.entries.push(activeEntry);
        if (activeEntry.status === 'already_desired') { await checkpoint(clone(receipt)); activeEntry = null; continue; }
        const body = buildPhotoSaveBody({ scope, productId: item.source.productId, name: item.source.name, file });
        activeEntry.status = 'sending'; await checkpoint(clone(receipt));
        // From here any error can follow a server-side mutation. There is no
        // retry. The pending product is blocked until an explicit reconciliation.
        activeEntry.writeStarted = true; uncertainProducts.add(`${key}:${item.source.productId}`);
        await saveImage(body);
        activeEntry.status = 'awaiting_readback'; await checkpoint(clone(receipt));
        const after = await snapshot(item.source.productId);
        requireThat(after.images.length === 1 && after.images[0].imageId === '1'
          && after.images[0].name === item.source.name && after.images[0].sha256 === item.source.sha256,
        'PHOTO_READBACK_MISMATCH', 'A imagem relida não confere com a foto aprovada. Confira o cadastro antes de continuar.');
        activeEntry.after = after; activeEntry.status = 'verified';
        await checkpoint(clone(receipt));
        uncertainProducts.delete(`${key}:${item.source.productId}`); activeEntry = null;
      }
      receipt.status = 'completed'; receipt.completedAt = time().toISOString(); await checkpoint(clone(receipt));
      return clone(receipt);
    } catch (error) {
      if (activeEntry?.writeStarted) activeEntry.status = 'needs_reconciliation';
      receipt.status = activeEntry?.writeStarted ? 'needs_reconciliation' : 'stopped';
      receipt.errorCode = typeof error.code === 'string' ? error.code : 'PHOTO_OPERATION_FAILED';
      try { await checkpoint(clone(receipt)); } catch { receipt.checkpointFailed = true; }
      throw Object.assign(new Error(activeEntry?.writeStarted
        ? 'A gravação precisa ser conferida antes de repetir o envio.' : error.message),
      { code: receipt.errorCode, receipt: clone(receipt) });
    } finally { busyScopes.delete(key); }
  }
  async function reconcile(receipt) {
    requireThat(receipt?.version === 'photo-receipt-v1' && canonical(receipt.scope) === canonical(scope)
      && receipt.status === 'needs_reconciliation' && typeof checkpoint === 'function',
    'INVALID_PENDING_RECEIPT', 'Forneça o recibo da gravação que precisa ser conferida.');
    const key = scopeKey(scope);
    requireThat(!busyScopes.has(key), 'PHOTO_EXECUTION_BUSY', 'Já existe uma execução de fotos nesta unidade.');
    busyScopes.add(key);
    const result = clone(receipt);
    try {
      for (const entry of result.entries.filter(entry => entry.status === 'needs_reconciliation')) {
        const approvedSource = approved.get(entry.productId);
        requireThat(approvedSource && approvedSource.sha256 === entry.sourceSha256,
          'UNAPPROVED_PENDING_IMAGE', 'A gravação pendente não corresponde à foto aprovada neste cliente.');
        const after = await snapshot(entry.productId);
        requireThat(after.images.length === 1 && after.images[0].sha256 === entry.sourceSha256
          && after.images[0].imageId === '1' && after.images[0].name === approvedSource.name,
        'PENDING_IMAGE_NOT_VERIFIED', 'A imagem pendente ainda precisa ser conferida na interface.');
        entry.after = after; entry.status = 'verified_after_reconciliation';
      }
      result.status = 'reconciled'; result.reconciledAt = time().toISOString(); await checkpoint(clone(result));
      for (const entry of result.entries) if (entry.status === 'verified_after_reconciliation') uncertainProducts.delete(`${key}:${entry.productId}`);
      return result;
    } finally { busyScopes.delete(key); }
  }
  return Object.freeze({ readImages, hashImage: async url => {
    requireThat(isObservedPhotoUrl(url), 'UNOBSERVED_PHOTO_URL', 'A URL da imagem está fora do caminho observado.');
    return hashImage(url);
  }, preview, apply, reconcile });
}

// Shared catalog adapter. Updates carry the exact authorized product/file/hash
// mapping. The catalog owns its outer journal and unit lock; onCheckpoint must
// persist each product's sending/readback state before execution can proceed.
export function createPhotoClient({ request, target, hashImage, onCheckpoint,
  now, maxBaselineAgeMs } = {}) {
  const scope = { organization: target?.organization, branch: target?.branch };
  checkScope(scope);
  requireThat(typeof onCheckpoint === 'function', 'MISSING_CHECKPOINT', 'Forneça um recibo persistente antes de usar o cliente de fotos.');
  const preservedTarget = clone(target), clients = new Map();
  const options = { request, scope, hashImage, checkpoint: onCheckpoint, now, maxBaselineAgeMs };
  const reader = createProductPhotoClient(options);
  return Object.freeze({
    target: Object.freeze(clone(preservedTarget)),
    readImages: productId => reader.readImages(scope, productId),
    hashImage: reader.hashImage,
    async preview(updates) {
      requireThat(Array.isArray(updates) && updates.length > 0, 'MISSING_APPROVED_SOURCES', 'Informe as fotos e produtos aprovados.');
      const approvedSources = updates.map(update => ({ productId: update.productId, name: update.name,
        path: update.path ?? update.sourcePath, sha256: update.sha256 ?? update.sourceSha256 }));
      const client = createProductPhotoClient({ ...options, approvedSources });
      const plan = await client.preview(); clients.set(plan.id, client);
      return { ...plan, kind: 'product-photos', target: clone(preservedTarget) };
    },
    async apply(plan) {
      requireThat(plan?.kind === 'product-photos' && canonical(plan.target) === canonical(preservedTarget)
        && clients.has(plan.id), 'INVALID_PHOTO_PLAN_TARGET', 'Use a prévia de fotos preparada para este destino.');
      const { kind, target: planTarget, ...inner } = plan;
      return clients.get(plan.id).apply(inner);
    },
    async reconcile(receipt) {
      const sources = receipt?.entries?.map(entry => ({ productId: entry.productId, name: entry.name,
        path: entry.sourcePath, sha256: entry.sourceSha256 }));
      requireThat(Array.isArray(sources) && sources.length > 0, 'INVALID_PENDING_RECEIPT', 'Forneça o recibo pendente da execução.');
      // Receipt mapping must be separately checked by the catalog's journal;
      // this operation reads and checkpoints only, and cannot resend a file.
      return createProductPhotoClient({ ...options, approvedSources: sources }).reconcile(receipt);
    },
  });
}
