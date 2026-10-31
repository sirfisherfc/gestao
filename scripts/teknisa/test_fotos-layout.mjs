import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { buildLayoutPhotoReadBody, createLayoutPhotoClient, createPublicLayoutPhotoHasher } from './fotos-layout.mjs';

const target = { organization: 5482, branch: '0002', store: '0001' };
const scope = { configuration: '00001', effectiveFrom: '01/01/2026 00:00:00', group: '01', page: '1' };
const base = { NRORG: 5482, CDFILIAL: '0002', NRCONFTELA: '00001', NRPGCONFTAUX: '1', NRBUTTONAUX: '01',
  DTINIVIGENCIA: '01/01/2026 00:00:00', IDTPBUTTON: '1', IDTPBUTONAUX: '2', IDTPBUTONAUX2: '0',
  NRBUTTONAUX2: '0', NRPGCONFTAUX2: '0', NRPGCONFTELA: '1', __is_new: false,
  NRCOLORBACK: 14876409, NRCOLORTEXT: 12519206, NRFONTETEXT: 8, NRLIMPRODCOM: null,
  CDOPERULTATU: null, DTULTATU: '27/10/2026 15:53:14', CUSTOM_BUSINESS_FIELD: 'preservar' };
const rows = [
  { ...base, CDPRODUTO: '0000000073', CDARVPROD: '8000000000', CDIDENTBUTON: '0000000073', NRBUTTON: '01',
    DSBUTTON: 'NewCastle', NMPRODUTO: 'NEWCASTLE UN', IMAGE: 'https://midia.teknisa.com/files/Manage588fa3b08b544/LayoutProduto/abcdef.jpg',
    DSENDEIMG: 'Manage588fa3b08b544/LayoutProduto/abcdef.jpg' },
  { ...base, CDPRODUTO: '8000010100', CDARVPROD: '8000010100', CDIDENTBUTON: '8000010100', NRBUTTON: '09',
    DSBUTTON: 'Patinha', NMPRODUTO: 'PATINHA UN', IMAGE: null, DSENDEIMG: null },
];
// Minimal transport fixture, confined to an automatically removed test directory.
const directory = await mkdtemp(join(tmpdir(), 'layout-photo-test-')), path = join(directory, 'fixture.jpg');
const bytes = Buffer.from([255, 216, 255, 217]); await writeFile(path, bytes);
after(() => rm(directory, { recursive: true, force: true }));
const sha256 = createHash('sha256').update(bytes).digest('hex');
const newcastle = { productId: '0000000073', sku: '8000000000', path, sha256, name: 'NewCastle' };
const patinha = { ...newcastle, productId: '8000010100', sku: '8000010100', name: 'Fixture de transporte: sem uso comercial' };
const copy = x => structuredClone(x);
const url = 'https://midia.teknisa.com/files/Manage588fa3b08b544/LayoutProduto/abcd123.jpg';
function setup({ hash = sha256, afterSave = () => {}, readHook = () => {}, now, scope: readScope = scope,
  rejectBeforeSave = false, rejectAfterSave = false } = {}) {
  const state = { rows: copy(rows), saves: [], checkpoints: [], reads: 0 };
  state.rows = state.rows.map(r => ({ ...r, NRBUTTONAUX: readScope.group }));
  const request = async (p, body) => {
    if (p.endsWith('/save')) {
      state.saves.push(copy(body));
      if (rejectBeforeSave) throw Object.assign(new Error('timeout'), { code: 'TIMEOUT' });
      const saved = body.dataset[0], index = state.rows.findIndex(x => x.CDPRODUTO === saved.CDPRODUTO);
      state.rows[index] = { ...copy(saved), IMAGE: url, DSENDEIMG: url.replace('https://midia.teknisa.com/files/', '') };
      for (const k of ['changed', 'LOCALPROD', 'ANTG_NRBUTTON', 'CDNVPRODUTO']) delete state.rows[index][k];
      state.rows[index].DTULTATU = '31/10/2026 20:15:00'; state.rows[index].CDOPERULTATU = '000000054821';
      afterSave(state.rows, index);
      if (rejectAfterSave) throw Object.assign(new Error('timeout'), { code: 'TIMEOUT' });
      return { isPlural: { result: 1 } };
    }
    state.reads++; readHook(state);
    assert(body.filter.every(f => f.operator === '='));
    return { dataset: { vnd80600_configterminalcaixa_layoutProduto: copy(state.rows) } };
  };
  state.client = createLayoutPhotoClient({ request, target, hashImage: async () => hash,
    onCheckpoint: async r => state.checkpoints.push(copy(r)), ...(now ? { now } : {}) });
  return state;
}
test('read envelope matches observed filters and excludes copied layouts/TOTEM', async () => {
  const body = buildLayoutPhotoReadBody({ target, scope });
  assert.equal(body.itemsPerPage, 500); assert.equal(body.requestType, 'FilterData');
  assert.deepEqual(body.filter.map(x => [x.name, x.value]), [['NRORG', 5482], ['CDFILIAL', '0002'],
    ['NRCONFTELA', '00001'], ['NRPGCONFTAUX', '1'], ['NRBUTTONAUX', '01'], ['CDLOJA', '0001'],
    ['IDTPBUTONAUX', '2'], ['DTINIVIGENCIA', '01/01/2026 00:00:00']]);
  for (const configuration of ['00003', '00004', '00005'])
    assert.throws(() => buildLayoutPhotoReadBody({ target, scope: { ...scope, configuration } }), { code: 'INVALID_LAYOUT_PHOTO_SCOPE' });
  assert.throws(() => createLayoutPhotoClient({ request() {}, hashImage() {}, target: { ...target, branch: '0001' } }), { code: 'INVALID_LAYOUT_PHOTO_TARGET' });
});
test('existing desired bytes are idempotent; different bytes block preview', async () => {
  const s = setup(), plan = await s.client.preview({ groups: [scope], updates: [newcastle] });
  assert.equal(plan.kind, 'layout-product-photos'); assert.equal(plan.items[0].status, 'already_desired');
  const receipt = await s.client.apply(plan); assert.equal(receipt.status, 'completed'); assert.equal(s.saves.length, 0);
  const d = setup({ hash: 'f'.repeat(64) });
  await assert.rejects(d.client.preview({ groups: [scope], updates: [newcastle] }), { code: 'EXISTING_DIFFERENT_LAYOUT_PHOTO' });
});
test('upload preserves colors, order, all business fields and null limit', async () => {
  const s = setup(), before = copy(s.rows.find(r => r.CDPRODUTO === patinha.productId));
  const plan = await s.client.preview({ groups: [scope], updates: [patinha] });
  const receipt = await s.client.apply(plan); assert.equal(receipt.entries[0].status, 'verified');
  const body = s.saves[0], saved = body.dataset[0];
  assert.equal(body.requestType, 'DataSet'); assert.equal(body.origin.widgetName, 'productsInsideGroup');
  for (const [k, v] of Object.entries(before)) if (!['IMAGE', 'DSENDEIMG', 'DTINIVIGENCIA'].includes(k)) assert.deepEqual(saved[k], v, k);
  assert.equal(saved.DTINIVIGENCIA, '01/01/2026');
  assert.equal(saved.NRLIMPRODCOM, null); assert.equal(saved.ANTG_NRBUTTON, before.NRBUTTON);
  assert.equal(saved.CDNVPRODUTO, '5'); assert.equal(saved.LOCALPROD, 'N'); assert.equal(saved.changed, true);
  assert.deepEqual(saved.IMAGE, saved.DSENDEIMG); assert.equal(saved.IMAGE[0].size, bytes.length);
  assert.equal(s.checkpoints.find(r => r.entries.at(-1)?.status === 'sending').entries[0].writeStarted, undefined);
  await assert.rejects(s.client.apply(plan), { code: 'INVALID_OR_USED_LAYOUT_PHOTO_PLAN' });
});
test('stale baseline prevents all writes', async () => {
  const s = setup(), plan = await s.client.preview({ groups: [scope], updates: [patinha] });
  s.rows[1].NRCOLORBACK++;
  await assert.rejects(s.client.apply(plan), { code: 'LAYOUT_PHOTO_BASELINE_CHANGED' }); assert.equal(s.saves.length, 0);
});
test('post-write business change stops with a reconciliation receipt', async () => {
  const otherScope = { ...scope, group: '02' }, s = setup({ scope: otherScope, afterSave: (all, i) => { all[i].NRCOLORTEXT++; } });
  const plan = await s.client.preview({ groups: [otherScope], updates: [patinha] });
  await assert.rejects(s.client.apply(plan), e => e.code === 'LAYOUT_PHOTO_BUSINESS_FIELDS_CHANGED' && e.receipt.status === 'needs_reconciliation');
  assert.equal(s.saves.length, 1);
  await assert.rejects(s.client.preview({ groups: [otherScope], updates: [patinha] }), { code: 'UNRESOLVED_LAYOUT_PHOTO_SAVE' });
});
test('ambiguous timeout with missing image blocks a new preview and never retries', async () => {
  const otherScope = { ...scope, group: '03' }, s = setup({ scope: otherScope, rejectBeforeSave: true });
  const plan = await s.client.preview({ groups: [otherScope], updates: [patinha] });
  await assert.rejects(s.client.apply(plan), { code: 'TIMEOUT' });
  await assert.rejects(s.client.preview({ groups: [otherScope], updates: [patinha] }), { code: 'UNRESOLVED_LAYOUT_PHOTO_SAVE' });
  assert.equal(s.saves.length, 1);
});
test('read-only reconciliation accepts verified bytes after a timed-out save', async () => {
  const otherScope = { ...scope, group: '04' }, s = setup({ scope: otherScope, rejectAfterSave: true });
  const plan = await s.client.preview({ groups: [otherScope], updates: [patinha] });
  await assert.rejects(s.client.apply(plan), { code: 'TIMEOUT' });
  const reconciled = await s.client.preview({ groups: [otherScope], updates: [patinha] });
  assert.equal(reconciled.items[0].status, 'already_desired'); await s.client.apply(reconciled); assert.equal(s.saves.length, 1);
});
test('missing product is reported without creating a button', async () => {
  const s = setup(), absent = { ...newcastle, productId: '1234567890', sku: '1234567890' };
  const plan = await s.client.preview({ groups: [scope], updates: [absent] });
  assert.deepEqual(plan.skipped, [{ productId: absent.productId, reason: 'no_existing_button' }]);
  await s.client.apply(plan); assert.equal(s.saves.length, 0);
});
test('wrong row scope, mismatched SKU and modified plan are rejected', async () => {
  const s = setup(); s.rows[0].NRCONFTELA = '00004';
  await assert.rejects(s.client.readGroup(scope), { code: 'WRONG_OR_DUPLICATE_LAYOUT_ROW' });
  const m = setup(); await assert.rejects(m.client.preview({ groups: [scope], updates: [{ ...newcastle, sku: '9999999999' }] }), { code: 'LAYOUT_PHOTO_SKU_MISMATCH' });
  const t = setup(), plan = await t.client.preview({ groups: [scope], updates: [patinha] }); plan.items[0].source.productId = '0000000073';
  await assert.rejects(t.client.apply(plan), { code: 'INVALID_OR_USED_LAYOUT_PHOTO_PLAN' }); assert.equal(t.saves.length, 0);
});
test('expired plans and invalid source hashes cannot write', async () => {
  let clock = new Date('2026-10-31T23:00:00Z'); const s = setup({ now: () => clock });
  const plan = await s.client.preview({ groups: [scope], updates: [patinha] }); clock = new Date(+clock + 600001);
  await assert.rejects(s.client.apply(plan), { code: 'STALE_LAYOUT_PHOTO_PLAN' });
  await assert.rejects(s.client.preview({ groups: [scope], updates: [{ ...newcastle, sha256: 'a'.repeat(64) }] }), { code: 'LAYOUT_PHOTO_SOURCE_CHANGED' });
});
test('public hasher accepts only observed layout path and omits credentials', async () => {
  let options; const hash = createPublicLayoutPhotoHasher({ fetchImpl: async (u, o) => {
    options = o; return { ok: true, url: u, redirected: false, arrayBuffer: async () => await readFile(path) };
  } });
  assert.equal(await hash(url), sha256); assert.deepEqual(options, { method: 'GET', credentials: 'omit', redirect: 'error' });
  await assert.rejects(hash('https://example.com/photo.jpg'), { code: 'INVALID_LAYOUT_PHOTO_URL' });
});
