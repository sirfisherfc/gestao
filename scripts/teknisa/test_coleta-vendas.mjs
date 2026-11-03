import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareDailySalesCollection, collectDailySales, readDailySalesCollection } from './coleta-vendas.mjs';
import { createTeknisa } from './teknisa.mjs';

const target = { organization: 42, branch: '0002', store: '0001' };
const now = () => new Date('2026-11-02T12:00:00-03:00');
const period = { from: '2026-10-30', to: '2026-11-01' };
const row = (extra = {}) => ({ NRORG: 42, CDFILIAL: '0002', CDLOJA: '0001',
  CDVENDEDOR2: '01', GARCON: 'PESSOA FICTICIA', QTPRODVEND: 2,
  VRFINALITEM: 110, VRLIQUIDO: 100, VRLIQACRES: 90, ACR: 10, DES: 0,
  VRGORJETA: 10, VRTXENTREGA: 0, VRREPITEM: 0, CPFCONSUMIDOR: 'descartar-campo-privado', ...extra });
const response = rows => ({ dataset: { vnd09900_relProdutividadePorVendedor: rows } });
function journal() {
  const records = new Map(); let locked = false;
  return { records, async save(record) { records.set(record.id, structuredClone(record)); },
    async load(id) { if (!records.has(id)) throw new Error('Recibo ausente.'); return structuredClone(records.get(id)); },
    async lock(_scope, callback) { if (locked) throw new Error('unidade ocupada'); locked = true;
      try { return await callback(); } finally { locked = false; } } };
}

test('planeja dias passados em Fortaleza e declara a cobertura parcial', () => {
  const plan = prepareDailySalesCollection({ target, ...period, now: now() });
  assert.deepEqual(plan.days, ['2026-10-30', '2026-10-31', '2026-11-01']);
  assert.equal(plan.unassignedExcluded, true);
  assert.equal(plan.financialImportAllowed, false);
  assert.equal(plan.automaticExecutionReady, false);
  const nearMidnight = prepareDailySalesCollection({ target, now: new Date('2026-11-02T02:59:59Z') });
  assert.deepEqual(nearMidnight.days, ['2026-10-31']);
});

test('recusa datas inválidas, dia atual, limite excedido e destino incompleto antes de consultar', async () => {
  for (const bounds of [
    { from: '2026-02-30', to: '2026-03-01' }, { from: '2026-10-20', to: '2026-11-01' },
    { from: '2026-11-01', to: '2026-11-02' }, { from: '2026-11-01', to: '2026-10-30' },
    { from: '30/10/2026', to: '01/11/2026' },
  ]) {
    let calls = 0;
    await assert.rejects(collectDailySales({ target, ...bounds, now, journal: journal(), request: async () => { calls++; } }));
    assert.equal(calls, 0);
  }
  assert.throws(() => prepareDailySalesCollection({ target: { ...target, store: '' }, ...period, now: now() }));
});

test('consulta um dia por vez no destino conferido e expõe somente contagens', async () => {
  const store = journal(), calls = [];
  const request = async (path, body) => {
    calls.push({ path, body });
    assert.ok(path.endsWith('/vnd09900_relProdutividadePorVendedor'));
    assert.equal(body.requestType, 'FilterData');
    assert.deepEqual(body.filter.find(f => f.name === 'CDLOJA').value, ['00020001']);
    const dates = body.filter.find(f => f.name === 'DTMOVTURCAIX').value;
    assert.equal(dates[0], dates[1]);
    return response([row()]);
  };
  const result = await collectDailySales({ request, target, journal: store, ...period, now });
  assert.equal(calls.length, 3);
  assert.equal(result.status, 'collected_with_limits');
  assert.equal(result.days.length, 3);
  assert.equal(result.days[0].sellers, 1);
  assert.equal(result.financialImportAllowed, false);
  assert.doesNotMatch(JSON.stringify(result), /PESSOA FICTICIA|reportedNetCents|CPFCONSUMIDOR/);
  const record = store.records.get(result.collectionId);
  assert.equal(record.batches[0].report.sellers[0].reportedNetCents, 10000);
  assert.doesNotMatch(JSON.stringify(record), /CPFCONSUMIDOR|descartar-campo-privado/);
  assert.deepEqual(await readDailySalesCollection({ journal: store, target, collectionId: result.collectionId, now: now() }), result);
});

test('retoma o dia que falhou e preserva o anterior sem repetir consultas concluídas', async () => {
  const store = journal(); let calls = 0;
  const request = async () => {
    calls++;
    if (calls === 2) throw Object.assign(new Error('OAuth-Token=nao-deve-aparecer'), { code: 'SESSION_EXPIRED' });
    return response([row()]);
  };
  const first = await collectDailySales({ request, target, journal: store, ...period, now });
  assert.equal(first.status, 'interrupted');
  assert.deepEqual(first.days.map(day => day.status), ['observed', 'failed', 'pending']);
  assert.equal(first.days[1].errorCode, 'SESSION_EXPIRED');
  assert.doesNotMatch(JSON.stringify(first) + JSON.stringify(store.records.get(first.collectionId)), /nao-deve-aparecer|OAuth-Token/);
  const done = await collectDailySales({ request, target, journal: store, collectionId: first.collectionId, now });
  assert.equal(done.status, 'collected_with_limits');
  assert.equal(calls, 4);
  assert.equal((await collectDailySales({ request, target, journal: store, collectionId: first.collectionId, now })).status, 'collected_with_limits');
  assert.equal(calls, 4);
});

test('lista vazia permanece sem cobertura confirmada; formato inválido interrompe', async () => {
  const empty = await collectDailySales({ request: async () => response([]), target, journal: journal(), ...period, now });
  assert.ok(empty.days.every(day => day.status === 'empty_unverified'));
  assert.equal(empty.financialImportAllowed, false);
  const invalid = await collectDailySales({ request: async () => response(null), target, journal: journal(), ...period, now });
  assert.equal(invalid.status, 'interrupted');
  assert.equal(invalid.days[0].errorCode, 'READ_FAILED');
  assert.ok(invalid.days.slice(1).every(day => day.status === 'pending'));
});

test('recusa resposta de outra loja e paginação repetida sem guardar dados como válidos', async () => {
  for (const rows of [[row({ CDLOJA: '0003' })], Array.from({ length: 500 }, () => row())]) {
    const store = journal();
    const result = await collectDailySales({ request: async () => response(rows), target, journal: store, ...period, now });
    assert.equal(result.status, 'interrupted');
    assert.equal(store.records.get(result.collectionId).batches[0].report, undefined);
  }
});

test('recibo de outro destino ou alterado é recusado antes da retomada', async () => {
  const store = journal(), request = async () => response([row()]);
  const done = await collectDailySales({ request, target, journal: store, ...period, now });
  await assert.rejects(collectDailySales({ request, target: { ...target, branch: '0003' }, journal: store, collectionId: done.collectionId, now }), /outro destino/);
  await assert.rejects(collectDailySales({ request, target, journal: store, collectionId: done.collectionId, from: '2026-10-31', now }), /outro destino ou período/);
  const record = store.records.get(done.collectionId);
  record.batches[0].report.sellers[0].reportedNetCents++;
  await assert.rejects(collectDailySales({ request, target, journal: store, collectionId: done.collectionId, now }), /dados do recibo/);
});

test('entrada única integra o coletor sem permitir troca de destino por argumento', async () => {
  const store = journal(), calls = [];
  const tool = createTeknisa({ request: async (path, body) => { calls.push(body); return response([]); }, target, journal: store });
  const result = await tool.run('vendas.coleta.consultar', { from: '2026-10-30', to: '2026-10-30', scope: { branch: '0003' } });
  assert.equal(result.target.branch, target.branch);
  assert.deepEqual(calls[0].filter.find(f => f.name === 'CDFILIAL').value, ['0002']);
  assert.equal((await tool.run('vendas.coleta.recibo', { collectionId: result.collectionId })).collectionId, result.collectionId);
  assert.equal((await tool.run('vendas.coleta.preparar', period)).automaticExecutionReady, false);
  await assert.rejects(tool.run('plano.aplicar', { planId: result.collectionId }), /incompleto ou foi modificado/);
  assert.equal(calls.length, 1);
});

test('bloqueio da unidade impede coletas simultâneas antes da segunda consulta', async () => {
  const store = journal(); let release;
  const gate = new Promise(resolve => { release = resolve; });
  let calls = 0;
  const request = async () => { calls++; await gate; return response([]); };
  const first = collectDailySales({ request, target, journal: store, from: '2026-11-01', to: '2026-11-01', now });
  await assert.rejects(collectDailySales({ request, target, journal: store, ...period, now }), /unidade ocupada/);
  release(); await first;
  assert.equal(calls, 1);
});
