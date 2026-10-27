import test from 'node:test';
import assert from 'node:assert/strict';
import { enableCancellationPrinting, planCancellationPrinting, READ_PATH, SAVE_PATH } from './produtos_loja.mjs';

const target = { organization: 42, branch: '0002', store: '0001' };
const fixture = (product, flag = 'N') => ({
  NRORG: 42, CDFILIAL: '0002', CDLOJA: '0001', CDPRODUTO: String(product),
  CDARVPROD: `8.00.00.${String(product).padStart(3, '0')}.00`,
  NMPRODUTO: `PRODUTO TESTE ${product}`, IDIMPCANITEM: flag,
  DSIMPCANITEM: flag === 'S' ? 'SIM' : 'NÃO',
  NRSEQIMPRPROD: '00001', NRSEQIMPRPROD2: null, CDSETOR: null,
  NIVELINICIAL: 'T', __is_new: false,
});

function mockServer(rows, { ignoreSave = false, changePrinter = false } = {}) {
  const state = structuredClone(rows);
  const writes = [];
  const request = async (path, body) => {
    if (path === READ_PATH) {
      assert.deepEqual(body.filter.slice(0, 3).map(item => item.value), [42, '0002', '0001']);
      return { dataset: { ger12300_cadloja_produtos: structuredClone(state) } };
    }
    assert.equal(path, SAVE_PATH);
    writes.push(structuredClone(body));
    for (const saved of body.dataset) {
      assert.equal(saved.changed, true);
      assert.equal(saved.__is_new, false);
      assert.equal(saved.CDOPERADOR, 7);
      assert.equal(saved.DTATU, '27/10/2026 12:00:00');
      assert.ok(!saved.CDARVPROD.includes('.'));
      const row = state.find(item => item.CDPRODUTO === saved.CDPRODUTO);
      assert.equal(saved.NRSEQIMPRPROD, row.NRSEQIMPRPROD);
      if (!ignoreSave) {
        row.IDIMPCANITEM = saved.IDIMPCANITEM;
        row.DSIMPCANITEM = 'SIM';
      }
      if (changePrinter) row.NRSEQIMPRPROD = '00099';
    }
    return [];
  };
  return { request, state, writes };
}

const options = server => ({
  request: server.request, target, operator: 7, apply: true,
  now: () => new Date('2026-10-27T15:00:00Z'),
});

test('prévia conta os vínculos e mantém zero gravações por padrão', async () => {
  const server = mockServer([fixture(1), fixture(2, 'S')]);
  const result = await enableCancellationPrinting({ request: server.request, target });
  assert.equal(result.mode, 'preview');
  assert.equal(result.pending, 1);
  assert.equal(server.writes.length, 0);
});

test('lotes de 25 preservam impressoras, conferem a gravação e permitem repetição', async () => {
  const server = mockServer([...Array.from({ length: 52 }, (_, index) => fixture(index + 1)), fixture(53, 'S')]);
  const result = await enableCancellationPrinting(options(server));
  assert.equal(result.changed, 52);
  assert.equal(result.finalEnabled, 53);
  assert.equal(result.pending, 0);
  assert.deepEqual(server.writes.map(body => body.dataset.length), [25, 25, 2]);
  assert.equal((await enableCancellationPrinting(options(server))).changed, 0);
  assert.equal(server.writes.length, 3);
});

test('destino diferente, duplicatas e valores desconhecidos impedem a gravação', () => {
  for (const rows of [
    [{ ...fixture(1), CDLOJA: '0009' }],
    [fixture(1), fixture(1)],
    [fixture(1, null)],
    [{ ...fixture(1), __is_new: true }],
  ]) assert.throws(() => planCancellationPrinting(rows, target));
  assert.throws(() => planCancellationPrinting(Array.from({ length: 9999 }, (_, index) => fixture(index)), target));
});

test('o operador é necessário quando houver gravação', async () => {
  const server = mockServer([fixture(1)]);
  await assert.rejects(enableCancellationPrinting({ ...options(server), operator: undefined }), /operador/);
  await assert.rejects(enableCancellationPrinting({ ...options(server), apply: 'false' }), /true ou false/);
  assert.equal(server.writes.length, 0);
});

test('sucesso HTTP sem persistência interrompe o lote seguinte', async () => {
  const server = mockServer(Array.from({ length: 26 }, (_, index) => fixture(index)), { ignoreSave: true });
  await assert.rejects(enableCancellationPrinting(options(server)), /ainda desmarcado/);
  assert.equal(server.writes.length, 1);
});

test('mudança em impressora durante a gravação interrompe a execução', async () => {
  const server = mockServer(Array.from({ length: 26 }, (_, index) => fixture(index)), { changePrinter: true });
  await assert.rejects(enableCancellationPrinting(options(server)), /NRSEQIMPRPROD/);
  assert.equal(server.writes.length, 1);
});

test('mudança simultânea em outro campo é detectada antes de gravar', async () => {
  const server = mockServer([fixture(1)]);
  const original = server.request;
  let reads = 0;
  server.request = async (path, body) => {
    if (path === READ_PATH && ++reads === 2) server.state[0].CDSETOR = '0003';
    return original(path, body);
  };
  await assert.rejects(enableCancellationPrinting(options(server)), /CDSETOR/);
  assert.equal(server.writes.length, 0);
});

test('retorno de erro e lista incompleta impedem novas gravações', async () => {
  const server = mockServer([fixture(1)]);
  const original = server.request;
  server.request = (path, body) => path === SAVE_PATH
    ? { error: 'Falha simulada' } : original(path, body);
  await assert.rejects(enableCancellationPrinting(options(server)), /formato inesperado/);
  await assert.rejects(enableCancellationPrinting({ ...options(server), request: async () => ({ dataset: {} }) }), /lista completa/);
});
