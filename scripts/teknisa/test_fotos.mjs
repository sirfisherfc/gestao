import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, writeFile, unlink, rmdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createProductPhotoClient, createPhotoClient, buildPhotoReadBody, buildPhotoSaveBody,
  createPublicPhotoHasher, PHOTO_PATHS, PHOTO_SCOPE } from './fotos.mjs';

const directory = dirname(fileURLToPath(import.meta.url));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const bytes = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 1, 2, 3, 4, 0xff, 0xd9]);
const sourceSha = sha(bytes), differentSha = sha('different');
const assetUrl = 'https://midia.teknisa.com/files/Manage588fa3b08b544/ImgProd/aa001.jpg';
let nextId = 1200;
async function fixture(t, { existing = [], saveError, checkpointError, hashError, sourceCount = 1 } = {}) {
  const scratch = await mkdtemp(join(directory, 'test-work-'));
  const sources = [];
  for (let index = 0; index < sourceCount; index++) {
    const path = join(scratch, `photo-${index}.jpg`); await writeFile(path, bytes);
    sources.push({ productId: String(nextId++).padStart(10, '0'), name: `Foto ${index}`, path, sha256: sourceSha });
  }
  t.after(async () => { for (const source of sources) await unlink(source.path); await rmdir(scratch); });
  const state = { writes: [], reads: [], journal: [], rows: new Map(), hashes: new Map(),
    clock: new Date('2026-10-31T15:00:00.000Z'), inflight: 0, maxInflight: 0, onRead: null, onSave: null, onCheckpoint: null };
  const urlFor = id => `https://midia.teknisa.com/files/Manage588fa3b08b544/ImgProd/${Number(id).toString(16)}.jpg`;
  const rowFor = (source, url = urlFor(source.productId)) => ({ CDFILIAL: '0002', CDIMAGEM: '1', NMIMAGEM: source.name, LINKIMGPROD: url });
  for (const source of sources) {
    state.rows.set(source.productId, structuredClone(existing.length ? existing : []));
    state.hashes.set(urlFor(source.productId), sourceSha);
  }
  const enter = async operation => {
    state.inflight++; state.maxInflight = Math.max(state.maxInflight, state.inflight);
    try { await Promise.resolve(); return await operation(); } finally { state.inflight--; }
  };
  const request = async (path, body) => enter(async () => {
    if (path === PHOTO_PATHS.read) {
      state.reads.push(structuredClone(body));
      if (state.onRead) await state.onRead(body);
      return { dataset: { select_prodFili: structuredClone(state.rows.get(body.filter[0].value) || []) } };
    }
    assert.equal(path, PHOTO_PATHS.save);
    state.writes.push(structuredClone(body));
    const source = sources.find(source => source.productId === body.row.CDPRODUTO);
    state.rows.set(source.productId, [rowFor(source)]);
    if (state.onSave) await state.onSave(body);
    if (saveError) throw Object.assign(new Error('timeout fixture'), { code: 'TIMEOUT' });
    return {}; // The real save response has not been asserted; readback decides.
  });
  const hashImage = async url => enter(async () => {
    if (hashError) throw new Error('public asset unavailable');
    return state.hashes.get(url);
  });
  const checkpoint = async receipt => {
    if (state.onCheckpoint) await state.onCheckpoint(receipt);
    if (checkpointError) throw new Error('checkpoint fixture unavailable');
    state.journal.push(structuredClone(receipt));
  };
  const options = { request, hashImage, checkpoint, approvedSources: sources, now: () => state.clock };
  return { state, sources, rowFor, urlFor, options, client: createProductPhotoClient(options) };
}

test('read and save envelopes match the sanitized observed contract with synthetic JPEG bytes', () => {
  // Observed field names, types and UI metadata; file content, filename and
  // timestamps are synthetic. This fixture has no private-workspace dependency.
  const file = { b64File: 'data:image/jpeg;base64,/9j/4AECAwT/2Q==', name: 'fixture.jpg',
    lastModified: 1793448000000, lastModifiedDate: '2026-10-31T12:00:00.000Z',
    webkitRelativePath: '', size: 10, type: 'image/jpeg' };
  const read = { disableLoader: false, filter: [
    { name: 'CDPRODUTO', operator: '>=', value: '0000000073' },
    { name: 'CDFILIAL', operator: '>=', value: '0002' },
    { name: 'NRORG', operator: '=', value: 5482 },
  ], page: 1, itemsPerPage: 50, requestType: 'FilterData', origin: {
    containerName: 'cadImgProd', widgetName: 'imgProdWidget',
    containerLabel: 'Cadastro de Imagem do Produto', widgetLabel: 'Imagens do Produto' } };
  const save = { requestType: 'Row', row: { __createdLocal: true, __is_new: true, __index: 0,
    CDFILIAL: '0002', CDPRODUTO: '0000000073', CDIMAGEM: 1, NMIMAGEM: 'Foto de teste', LINKIMGPROD: [file],
    __rightActions: [], __leftActions: [], __notSelectable: false, __isSelected: false, changed: true,
    $error: { CDIMAGEM: [], NMIMAGEM: [], LINKIMGPROD: [] }, TPMIDIA: 'Imagem', NRORG: 5482 },
  origin: { containerLabel: 'Cadastro de Imagem do Produto', widgetLabel: 'Imagens do Produto' } };
  assert.deepEqual(buildPhotoReadBody(PHOTO_SCOPE, '0000000073'), read);
  assert.deepEqual(buildPhotoSaveBody({ productId: '0000000073', name: 'Foto de teste', file }), save);
  assert.deepEqual(Buffer.from(file.b64File.split(',')[1], 'base64'), bytes);
});
test('new photo saves once, checkpoints around the write and verifies published bytes', async t => {
  const { state, client, sources } = await fixture(t);
  const receipt = await client.apply(await client.preview());
  assert.equal(receipt.status, 'completed'); assert.equal(state.writes.length, 1);
  assert.equal(state.writes[0].row.CDPRODUTO, sources[0].productId);
  assert.equal(receipt.entries[0].status, 'verified');
  assert.equal(receipt.entries[0].after.images[0].sha256, sourceSha);
  assert.ok(state.journal.some(item => item.entries[0]?.status === 'sending'));
  assert.ok(state.journal.some(item => item.entries[0]?.status === 'awaiting_readback'));
  assert.doesNotMatch(JSON.stringify(receipt), /b64File|data:image|OAuth|Token|headers/);
  assert.deepEqual(state.reads[0], buildPhotoReadBody(PHOTO_SCOPE, sources[0].productId));
});
test('same fetched SHA256 is idempotent without relying on URL or name', async t => {
  const { state, client, sources, rowFor, urlFor } = await fixture(t);
  state.rows.set(sources[0].productId, [{ ...rowFor(sources[0]), NMIMAGEM: 'Outro nome' }]);
  state.hashes.set(urlFor(sources[0].productId), sourceSha);
  const receipt = await client.apply(await client.preview());
  assert.equal(receipt.entries[0].status, 'already_desired'); assert.equal(state.writes.length, 0);
});
test('existing different bytes block the preview and leave the product untouched', async t => {
  const { state, client, sources, rowFor, urlFor } = await fixture(t);
  state.rows.set(sources[0].productId, [rowFor(sources[0])]); state.hashes.set(urlFor(sources[0].productId), differentSha);
  await assert.rejects(client.preview(), { code: 'EXISTING_DIFFERENT_IMAGE' }); assert.equal(state.writes.length, 0);
});
test('a changed baseline or changed bytes at the same URL block writes', async t => {
  const { state, client, sources, rowFor } = await fixture(t);
  const plan = await client.preview(); state.rows.set(sources[0].productId, [rowFor(sources[0])]);
  await assert.rejects(client.apply(plan), { code: 'PHOTO_BASELINE_CHANGED' }); assert.equal(state.writes.length, 0);
  const existingPlan = await client.preview(); state.hashes.set(rowFor(sources[0]).LINKIMGPROD, differentSha);
  await assert.rejects(client.apply(existingPlan), { code: 'PHOTO_BASELINE_CHANGED' }); assert.equal(state.writes.length, 0);
});
test('a changed local file is rejected before any save', async t => {
  const { state, client, sources } = await fixture(t);
  const plan = await client.preview(); await writeFile(sources[0].path, Buffer.concat([bytes, Buffer.from('changed')]));
  await assert.rejects(client.apply(plan), { code: 'SOURCE_HASH_CHANGED' }); assert.equal(state.writes.length, 0);
});
test('expired, modified and unapproved plans cannot write', async t => {
  const { state, client, sources } = await fixture(t);
  await assert.rejects(client.preview(['9999999999']), { code: 'UNAPPROVED_PRODUCT' }); assert.equal(state.reads.length, 0);
  const plan = await client.preview(), tampered = structuredClone(plan); tampered.items[0].source.productId = '9999999999';
  await assert.rejects(client.apply(tampered), { code: 'INVALID_OR_USED_PLAN' });
  state.clock = new Date(state.clock.getTime() + 600001);
  await assert.rejects(client.apply(plan), { code: 'STALE_PHOTO_PLAN' }); assert.equal(state.writes.length, 0);
  assert.equal(sources[0].sha256, sourceSha);
});
test('checkpoint failure before sending prevents all saves', async t => {
  const { state, client } = await fixture(t, { checkpointError: true });
  await assert.rejects(client.apply(await client.preview())); assert.equal(state.writes.length, 0);
});
test('timeout after mutation never retries; explicit read-only reconciliation clears the pending product', async t => {
  const { state, client } = await fixture(t, { saveError: true });
  const plan = await client.preview(); let pending;
  await assert.rejects(client.apply(plan), error => { pending = error.receipt;
    return error.code === 'TIMEOUT' && pending.status === 'needs_reconciliation'; });
  assert.equal(state.writes.length, 1);
  await assert.rejects(client.apply(plan), { code: 'INVALID_OR_USED_PLAN' });
  await assert.rejects(client.apply(await client.preview()), { code: 'UNRESOLVED_IMAGE_SAVE' });
  const receipt = await client.reconcile(pending);
  assert.equal(receipt.status, 'reconciled'); assert.equal(state.writes.length, 1);
  assert.equal((await client.apply(await client.preview())).entries[0].status, 'already_desired');
});
test('readback mismatch stops the batch and records an unresolved save', async t => {
  const { state, client, sources, urlFor } = await fixture(t, { sourceCount: 2 });
  state.onSave = async () => state.hashes.set(urlFor(sources[0].productId), differentSha);
  let pending;
  await assert.rejects(client.apply(await client.preview()), error => {
    pending = error.receipt; return error.code === 'PHOTO_READBACK_MISMATCH' && pending.status === 'needs_reconciliation';
  });
  assert.equal(state.writes.length, 1); assert.equal(pending.entries.length, 1);
  state.hashes.set(urlFor(sources[0].productId), sourceSha); await client.reconcile(pending);
});
test('failed verification checkpoint leaves the written product pending', async t => {
  const { state, client } = await fixture(t); let failed = false, pending;
  state.onCheckpoint = async receipt => {
    if (!failed && receipt.entries[0]?.status === 'verified') { failed = true; throw new Error('disk fixture'); }
  };
  await assert.rejects(client.apply(await client.preview()), error => { pending = error.receipt; return pending.status === 'needs_reconciliation'; });
  assert.equal(state.writes.length, 1); await client.reconcile(pending);
});
test('all products preflight before the first save and operations stay sequential', async t => {
  const { state, client, sources, rowFor } = await fixture(t, { sourceCount: 2 });
  const plan = await client.preview(); state.rows.set(sources[1].productId, [rowFor(sources[1])]);
  await assert.rejects(client.apply(plan), { code: 'PHOTO_BASELINE_CHANGED' }); assert.equal(state.writes.length, 0);
  state.rows.set(sources[1].productId, []);
  await client.apply(await client.preview()); assert.equal(state.writes.length, 2); assert.equal(state.maxInflight, 1);
});
test('another client cannot run a simultaneous batch in the same unit', async t => {
  const { state, client, options } = await fixture(t);
  const other = createProductPhotoClient(options), plan = await client.preview(), otherPlan = await other.preview();
  let release, entered;
  const waiting = new Promise(resolve => { release = resolve; }), firstCheckpoint = new Promise(resolve => { entered = resolve; });
  state.onCheckpoint = async receipt => { if (receipt.status === 'preflight') { entered(); await waiting; } };
  const running = client.apply(plan); await firstCheckpoint;
  await assert.rejects(other.apply(otherPlan), { code: 'PHOTO_EXECUTION_BUSY' }); release(); await running;
});
test('rows without product ID preserve the exact selection request; wrong unit and complete pages block', async t => {
  const { state, client, sources, rowFor } = await fixture(t);
  const id = sources[0].productId; state.rows.set(id, [rowFor(sources[0])]);
  const result = await client.readImages(PHOTO_SCOPE, id);
  assert.equal(result.rows[0].CDPRODUTO, undefined); assert.equal(result.productId, id);
  assert.deepEqual(result.request, buildPhotoReadBody(PHOTO_SCOPE, id));
  state.rows.set(id, [{ ...rowFor(sources[0]), CDFILIAL: '0003' }]);
  await assert.rejects(client.readImages(PHOTO_SCOPE, id), { code: 'INVALID_IMAGE_ROW' });
  state.rows.set(id, Array.from({ length: 50 }, (_, index) => ({ ...rowFor(sources[0]), CDIMAGEM: String(index + 1) })));
  await assert.rejects(client.readImages(PHOTO_SCOPE, id), { code: 'INCOMPLETE_IMAGE_PAGE' }); assert.equal(state.writes.length, 0);
});
test('public hashing uses only the exact observed asset path, omits credentials and refuses redirects', async () => {
  const calls = [];
  const hashImage = createPublicPhotoHasher({ fetchImpl: async (...args) => { calls.push(args);
    return { ok: true, url: args[0], redirected: false, arrayBuffer: async () => bytes }; } });
  assert.equal(await hashImage(assetUrl), sourceSha);
  assert.deepEqual(calls[0], [assetUrl, { method: 'GET', credentials: 'omit', redirect: 'error' }]);
  for (const url of [assetUrl + '?token=x', assetUrl.replace('midia.teknisa.com', 'example.com'),
    assetUrl.replace('/ImgProd/', '/Other/')]) await assert.rejects(hashImage(url), { code: 'UNOBSERVED_PHOTO_URL' });
  assert.equal(calls.length, 1);
  const redirects = createPublicPhotoHasher({ fetchImpl: async () => ({ ok: true, redirected: true }) });
  await assert.rejects(redirects(assetUrl), { code: 'PHOTO_FETCH_FAILED' });
});
test('shared command adapter binds kind, exact target and approved product/source hashes', async t => {
  const { state, options, sources } = await fixture(t);
  const target = { organization: 5482, branch: '0002', store: '0001', table: '001' };
  const client = createPhotoClient({ ...options, target, onCheckpoint: options.checkpoint });
  assert.deepEqual(client.target, target); assert.ok(Object.isFrozen(client.target));
  const plan = await client.preview(sources.map(source => ({ productId: source.productId, name: source.name,
    sourcePath: source.path, sourceSha256: source.sha256 })));
  assert.equal(plan.kind, 'product-photos'); assert.deepEqual(plan.target, target);
  const wrong = structuredClone(plan); wrong.target.store = '0002';
  await assert.rejects(client.apply(wrong), { code: 'INVALID_PHOTO_PLAN_TARGET' });
  assert.equal((await client.apply(plan)).status, 'completed'); assert.equal(state.writes.length, 1);
  assert.equal((await client.readImages(sources[0].productId)).rows.length, 1);
});
test('shared client requires a checkpoint instead of accepting a silent no-op', () => {
  assert.throws(() => createPhotoClient({ target: { organization: 5482, branch: '0002' },
    request: async () => {}, hashImage: async () => sourceSha }), { code: 'MISSING_CHECKPOINT' });
});
