import { createHash, randomUUID } from 'node:crypto';
import { readFile, stat } from 'node:fs/promises';
import { basename, resolve } from 'node:path';

export const LAYOUT_PHOTO_PATHS = Object.freeze({
  read: '/backend_man/index.php/vnd80600_configterminalcaixa_layoutProduto',
  save: '/backend_man/index.php/vnd80600_configterminalcaixa_layoutProduto/save',
});
const ORIGIN = { containerName: 'vnd80600_configterminalcaixa', widgetName: 'productsInsideGroup',
  containerLabel: 'Configuração Terminal de Caixa', widgetLabel: 'Produtos' };
const OMIT = new Set(['IMAGE', 'DSENDEIMG', 'CDOPERULTATU', 'NRORGULTATU', 'DTULTATU',
  'changed', 'CDNVPRODUTO', 'LOCALPROD', 'ANTG_NRBUTTON']);
const clone = value => structuredClone(value);
const canon = value => JSON.stringify(value, (_, x) => x && typeof x === 'object' && !Array.isArray(x)
  ? Object.fromEntries(Object.entries(x).sort(([a], [b]) => a.localeCompare(b))) : x);
const digest = value => createHash('sha256').update(Buffer.isBuffer(value) ? value : canon(value)).digest('hex');
const need = (condition, code) => { if (!condition) throw Object.assign(new Error(code), { code }); };
const validSha = x => typeof x === 'string' && /^[a-f0-9]{64}$/.test(x);
const date = x => String(x).replace(/ 00:00:00$/, '');
const key = row => [row.NRPGCONFTELA, row.NRBUTTON, row.CDPRODUTO].join(':');
const business = row => Object.fromEntries(Object.entries(row).filter(([k]) => !OMIT.has(k) && !k.startsWith('__'))
  .map(([k, v]) => [k, k === 'DTINIVIGENCIA' ? date(v) : v]));
const businessHash = rows => digest(rows.map(r => ({ key: key(r), business: business(r) })).sort((a, b) => a.key.localeCompare(b.key)));
const busy = new Set();
const uncertain = new Map();
const pendingKey = (target, scope, rowKey) => `${canon(target)}:${canon(scope)}:${rowKey}`;
function checkTarget(t) {
  need(t?.organization === 5482 && t.branch === '0002' && t.store === '0001'
    && Object.keys(t).every(k => ['organization', 'branch', 'store'].includes(k)), 'INVALID_LAYOUT_PHOTO_TARGET');
}
function checkScope(s) {
  need(s && ['00001', '00002'].includes(s.configuration) && /^\d{2}$/.test(s.group)
    && /^[1-9]\d*$/.test(s.page) && s.effectiveFrom === '01/01/2026 00:00:00'
    && Object.keys(s).every(k => ['configuration', 'effectiveFrom', 'group', 'page'].includes(k)), 'INVALID_LAYOUT_PHOTO_SCOPE');
}
export function isLayoutPhotoUrl(url) {
  return typeof url === 'string' && /^https:\/\/midia\.teknisa\.com\/files\/Manage588fa3b08b544\/LayoutProduto\/[a-f0-9]+\.jpg$/.test(url);
}
export function buildLayoutPhotoReadBody({ target, scope }) {
  checkTarget(target); checkScope(scope);
  return { disableLoader: false, filter: Object.entries({ NRORG: target.organization, CDFILIAL: target.branch,
    NRCONFTELA: scope.configuration, NRPGCONFTAUX: scope.page, NRBUTTONAUX: scope.group, CDLOJA: target.store,
    IDTPBUTONAUX: '2', DTINIVIGENCIA: scope.effectiveFrom }).map(([name, value]) => ({ name, operator: '=', value })),
  page: 1, itemsPerPage: 500, requestType: 'FilterData', origin: { ...ORIGIN } };
}
export function createPublicLayoutPhotoHasher({ fetchImpl = globalThis.fetch } = {}) {
  return async url => {
    need(isLayoutPhotoUrl(url) && typeof fetchImpl === 'function', 'INVALID_LAYOUT_PHOTO_URL');
    const r = await fetchImpl(url, { method: 'GET', credentials: 'omit', redirect: 'error' });
    need(r.ok && !r.redirected && (!r.url || r.url === url), 'LAYOUT_PHOTO_FETCH_FAILED');
    return digest(Buffer.from(await r.arrayBuffer()));
  };
}
async function sourceFile(u) {
  need(/^\d{10}$/.test(u?.productId) && (!u.sku || /^\d{10}$/.test(u.sku))
    && typeof u.path === 'string' && validSha(u.sha256), 'INVALID_LAYOUT_PHOTO_SOURCE');
  const [bytes, info] = await Promise.all([readFile(u.path), stat(u.path)]);
  need(info.isFile() && /\.jpe?g$/i.test(u.path) && bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255, 'INVALID_LAYOUT_PHOTO_JPEG');
  need(digest(bytes) === u.sha256, 'LAYOUT_PHOTO_SOURCE_CHANGED');
  const lastModified = Math.trunc(info.mtimeMs);
  return { b64File: `data:image/jpeg;base64,${bytes.toString('base64')}`, name: basename(u.path), lastModified,
    lastModifiedDate: new Date(lastModified).toISOString(), webkitRelativePath: '', size: bytes.length, type: 'image/jpeg' };
}
export function buildLayoutPhotoSaveBody({ row, file }) {
  need(row?.IDTPBUTTON === '1' && row.__is_new === false && /^\d{10}$/.test(row.CDPRODUTO), 'INVALID_LAYOUT_PHOTO_ROW');
  checkScope({ configuration: row.NRCONFTELA, effectiveFrom: `${date(row.DTINIVIGENCIA)} 00:00:00`, group: row.NRBUTTONAUX, page: row.NRPGCONFTAUX });
  need(row.CDFILIAL === '0002' && row.NRORG === 5482 && file?.type === 'image/jpeg', 'INVALID_LAYOUT_PHOTO_ROW');
  return { dataset: [{ ...clone(row), IMAGE: [clone(file)], DSENDEIMG: [clone(file)],
    DTINIVIGENCIA: date(row.DTINIVIGENCIA), changed: true, CDNVPRODUTO: '5', LOCALPROD: 'N', ANTG_NRBUTTON: row.NRBUTTON }],
  requestType: 'DataSet', origin: { ...ORIGIN } };
}
export function createLayoutPhotoClient({ request, target, hashImage, onCheckpoint,
  now = () => new Date(), maxPlanAgeMs = 600000 }) {
  checkTarget(target); target = Object.freeze(clone(target));
  need(typeof request === 'function' && typeof hashImage === 'function', 'MISSING_LAYOUT_PHOTO_TRANSPORT');
  const issued = new Map(), used = new Set();
  const clock = () => { const t = now(); need(t instanceof Date && Number.isFinite(+t), 'INVALID_CLOCK'); return t; };
  async function readGroup(scope) {
    const body = buildLayoutPhotoReadBody({ target, scope });
    const result = await request(LAYOUT_PHOTO_PATHS.read, body), rows = result?.dataset?.vnd80600_configterminalcaixa_layoutProduto;
    need(Array.isArray(rows) && rows.length < 500, 'INVALID_OR_INCOMPLETE_LAYOUT_DATASET');
    const keys = new Set();
    for (const r of rows) {
      need(r.NRORG === target.organization && r.CDFILIAL === target.branch && (!r.CDLOJA || r.CDLOJA === target.store)
        && r.NRCONFTELA === scope.configuration && r.NRBUTTONAUX === scope.group && r.NRPGCONFTAUX === scope.page
        && date(r.DTINIVIGENCIA) === date(scope.effectiveFrom) && r.IDTPBUTTON === '1' && r.IDTPBUTONAUX === '2'
        && r.IDTPBUTONAUX2 === '0' && r.NRBUTTONAUX2 === '0' && r.NRPGCONFTAUX2 === '0'
        && r.__is_new === false && /^\d{10}$/.test(r.CDPRODUTO) && !keys.has(key(r)), 'WRONG_OR_DUPLICATE_LAYOUT_ROW');
      keys.add(key(r));
    }
    return { scope: clone(scope), rows: clone(rows), businessHash: businessHash(rows), readAt: clock().toISOString() };
  }
  async function snapshot(scope, updates) {
    const result = await readGroup(scope), images = [];
    for (const r of result.rows) {
      const u = updates.find(x => x.productId === r.CDPRODUTO); if (!u) continue;
      need(!u.sku || u.sku === r.CDARVPROD, 'LAYOUT_PHOTO_SKU_MISMATCH');
      let sha256 = null;
      if (r.IMAGE || r.DSENDEIMG) {
        need(isLayoutPhotoUrl(r.IMAGE) && r.IMAGE === `https://midia.teknisa.com/files/${r.DSENDEIMG}`, 'INVALID_LAYOUT_PHOTO_URL');
        sha256 = await hashImage(r.IMAGE); need(validSha(sha256), 'INVALID_LAYOUT_PHOTO_HASH');
      }
      images.push({ key: key(r), productId: r.CDPRODUTO, sha256 });
    }
    return { ...result, images, fingerprint: digest({ businessHash: result.businessHash, images: images.sort((a, b) => a.key.localeCompare(b.key)) }) };
  }
  async function preview({ groups, updates }) {
    need(Array.isArray(groups) && groups.length > 0 && Array.isArray(updates) && updates.length > 0, 'EMPTY_LAYOUT_PHOTO_PLAN');
    need(new Set(groups.map(canon)).size === groups.length && new Set(updates.map(u => u.productId)).size === updates.length, 'DUPLICATE_LAYOUT_PHOTO_INPUT');
    const sources = updates.map(u => ({ productId: u.productId, sku: u.sku, path: resolve(u.path), sha256: u.sha256, name: u.name }));
    for (const u of sources) await sourceFile(u);
    const snapshots = [], items = [], found = new Set();
    for (const scope of groups) {
      const before = await snapshot(scope, sources); snapshots.push(before);
      for (const image of before.images) {
        const source = sources.find(u => u.productId === image.productId); found.add(image.productId);
        const pending = pendingKey(target, scope, image.key), previous = uncertain.get(pending);
        if (previous) {
          need(previous.sha256 === source.sha256 && before.businessHash === previous.businessHash
            && image.sha256 === source.sha256, 'UNRESOLVED_LAYOUT_PHOTO_SAVE');
          uncertain.delete(pending); // Read-only reconciliation: desired bytes and every business field match.
        }
        need(!image.sha256 || image.sha256 === source.sha256, 'EXISTING_DIFFERENT_LAYOUT_PHOTO');
        items.push({ scope: clone(scope), rowKey: image.key, source: clone(source),
          status: image.sha256 ? 'already_desired' : 'missing' });
      }
    }
    const plan = { kind: 'layout-product-photos', id: randomUUID(), target: clone(target), createdAt: clock().toISOString(),
      updates: sources, groups: snapshots, items, skipped: sources.filter(u => !found.has(u.productId)).map(u => ({ productId: u.productId, reason: 'no_existing_button' })) };
    issued.set(plan.id, digest(plan)); return clone(plan);
  }
  async function apply(plan) {
    need(plan?.kind === 'layout-product-photos' && issued.get(plan.id) === digest(plan) && !used.has(plan.id), 'INVALID_OR_USED_LAYOUT_PHOTO_PLAN');
    need(typeof onCheckpoint === 'function', 'MISSING_LAYOUT_PHOTO_CHECKPOINT');
    const age = +clock() - Date.parse(plan.createdAt), lock = canon(target);
    need(age >= 0 && age <= maxPlanAgeMs, 'STALE_LAYOUT_PHOTO_PLAN'); need(!busy.has(lock), 'LAYOUT_PHOTO_BUSY');
    for (const item of plan.items) need(!uncertain.has(pendingKey(target, item.scope, item.rowKey)), 'UNRESOLVED_LAYOUT_PHOTO_SAVE');
    busy.add(lock); used.add(plan.id);
    const receipt = { kind: plan.kind, planId: plan.id, target: clone(target), status: 'preflight', entries: [], skipped: clone(plan.skipped) };
    const checkpoint = () => onCheckpoint(clone(receipt));
    let active;
    try {
      await checkpoint();
      for (const u of plan.updates) await sourceFile(u);
      for (const before of plan.groups) {
        const fresh = await snapshot(before.scope, plan.updates);
        need(fresh.fingerprint === before.fingerprint, 'LAYOUT_PHOTO_BASELINE_CHANGED');
      }
      for (const group of plan.groups) {
        let current = await snapshot(group.scope, plan.updates);
        need(current.fingerprint === group.fingerprint, 'LAYOUT_PHOTO_BASELINE_CHANGED');
        for (const item of plan.items.filter(x => canon(x.scope) === canon(group.scope))) {
          const immediate = await snapshot(group.scope, plan.updates);
          need(immediate.fingerprint === current.fingerprint, 'LAYOUT_PHOTO_BASELINE_CHANGED'); current = immediate;
          const row = current.rows.find(r => key(r) === item.rowKey);
          active = { scope: clone(item.scope), productId: item.source.productId, rowKey: item.rowKey,
            sourceSha256: item.source.sha256, status: item.status };
          receipt.entries.push(active);
          if (item.status === 'already_desired') { await checkpoint(); active = null; continue; }
          const file = await sourceFile(item.source), body = buildLayoutPhotoSaveBody({ row, file });
          active.status = 'sending'; receipt.status = 'running'; await checkpoint();
          active.writeStarted = true;
          uncertain.set(pendingKey(target, item.scope, item.rowKey), { sha256: item.source.sha256, businessHash: group.businessHash });
          await request(LAYOUT_PHOTO_PATHS.save, body);
          active.status = 'awaiting_readback'; await checkpoint();
          const after = await snapshot(group.scope, plan.updates);
          need(after.businessHash === group.businessHash, 'LAYOUT_PHOTO_BUSINESS_FIELDS_CHANGED');
          const desired = after.images.find(x => x.key === item.rowKey);
          need(desired?.sha256 === item.source.sha256, 'LAYOUT_PHOTO_READBACK_MISMATCH');
          for (const previous of current.images.filter(x => x.key !== item.rowKey))
            need(after.images.find(x => x.key === previous.key)?.sha256 === previous.sha256, 'OTHER_LAYOUT_PHOTO_CHANGED');
          current = after; active.status = 'verified'; active.imageUrl = after.rows.find(r => key(r) === item.rowKey).IMAGE;
          await checkpoint(); uncertain.delete(pendingKey(target, item.scope, item.rowKey)); active = null;
        }
      }
      receipt.status = 'completed'; await checkpoint(); return clone(receipt);
    } catch (error) {
      receipt.status = active?.writeStarted ? 'needs_reconciliation' : 'failed'; receipt.errorCode = error.code || 'LAYOUT_PHOTO_ERROR';
      try { await checkpoint(); } catch { /* The original failure remains authoritative. */ }
      error.receipt = clone(receipt); throw error;
    } finally { busy.delete(lock); }
  }
  return Object.freeze({ target, readGroup, preview, apply });
}
