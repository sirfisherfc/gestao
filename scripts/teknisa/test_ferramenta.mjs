import test from 'node:test';
import assert from 'node:assert/strict';
import { runInNewContext } from 'node:vm';
import { mkdtemp, readdir, unlink, rmdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createTeknisa } from './teknisa.mjs';
import { RESOURCES, readResource } from './recursos.mjs';
import { preparePlan, applyPlan, prepareUndo } from './planos.mjs';
import { createFileJournal } from './recibos.mjs';
import { connectObservedSession } from './sessao_browser.mjs';
import { summarizeSellerSales } from './vendas.mjs';
import { classifyProduction, buildRoutingUpdates } from './impressao.mjs';

const target = { organization: 42, branch: '0002', store: '0001' };
const product = (id, flag = 'N') => ({ NRORG: 42, CDFILIAL: '0002', CDLOJA: '0001', CDPRODUTO: String(id),
  CDARVPROD: `80000${String(id).padStart(5, '0')}`, NMPRODUTO: `PRODUTO ${id}`, IDIMPCANITEM: flag,
  DSIMPCANITEM: flag === 'S' ? 'SIM' : 'NÃO', NRSEQIMPRPROD: '00001', NMIMPRPROD: 'BALCAO',
  CDSETOR: null, NIVELINICIAL: 'T', __is_new: false });
const printer = code => ({ NRORG: 42, CDFILIAL: '0002', CDLOJA: '0001', NRSEQIMPRLOJA: code,
  NMIMPRLOJA: code === '00001' ? 'BALCAO' : 'COZINHA', NMIMPRESSORA: 'MODELO TESTE', IDATIVO: 'S',
  CDPORTAIMPR: 'USB', DSIPIMPR: null, DSIPPONTE: 'conexao-privada-de-teste', __is_new: false });
function memoryJournal() {
  const records = new Map(); let locked = false;
  return { records, async save(row) { records.set(row.id, structuredClone(row)); },
    async load(id) { return structuredClone(records.get(id)); },
    async lock(_target, callback) { if (locked) throw new Error('bloqueado'); locked = true; try { return await callback(); } finally { locked = false; } } };
}
function server(rows = [product(1), product(2)]) {
  const state = structuredClone(rows), printers = [printer('00001'), printer('00003'), printer('00004')];
  const journal = memoryJournal(), writes = [];
  const request = async (path, body) => {
    const [name, spec] = Object.entries(RESOURCES).find(([, item]) => path === item.path || path === `${item.path}/save`) || [];
    assert.ok(spec);
    const data = name === 'loja.impressoras' ? printers : state;
    if (!path.endsWith('/save')) return { dataset: { [spec.dataset]: structuredClone(data) } };
    writes.push(structuredClone(body));
    for (const saved of body.dataset) {
      const row = data.find(item => item[name === 'loja.impressoras' ? 'NRSEQIMPRLOJA' : 'CDPRODUTO'] === saved[name === 'loja.impressoras' ? 'NRSEQIMPRLOJA' : 'CDPRODUTO']);
      assert.equal(saved.__is_new, false);
      for (const field of spec.writable) if (Object.hasOwn(saved, field)) row[field] = saved[field];
      if (name === 'loja.produtos') {
        row.DSIMPCANITEM = row.IDIMPCANITEM === 'S' ? 'SIM' : 'NÃO';
        row.NMIMPRPROD = printers.find(item => item.NRSEQIMPRLOJA === row.NRSEQIMPRPROD)?.NMIMPRLOJA ?? null;
      }
    }
    return spec.saveResponse === 'keys' ? { dataset: { [spec.dataset]: body.dataset.map(row => Object.fromEntries(spec.keys.map(field => [field, row[field]]))) } } : [];
  };
  return { state, printers, writes, request, journal, tool: createTeknisa({ request, target, operator: 7, journal }) };
}

test('entrada única prepara sem gravar e aplica só os campos pedidos', async () => {
  const s = server();
  const plan = await s.tool.run('loja.cancelamento.planejar', { all: true, enabled: true });
  assert.equal(plan.changes, 2); assert.equal(s.writes.length, 0);
  const result = await s.tool.run('plano.aplicar', { planId: plan.planId });
  assert.equal(result.verified, 2); assert.equal(s.state[0].NRSEQIMPRPROD, '00001');
  assert.equal(s.journal.records.get(plan.planId).operator, 7);
  assert.equal((await s.tool.run('plano.aplicar', { planId: plan.planId })).changedThisRun, 0);
  assert.equal(s.writes.length, 1);
});
test('planos alterados, de outro destino ou vencidos são recusados antes da escrita', async () => {
  const s = server(), p = await s.tool.run('loja.cancelamento.planejar', { all: true, enabled: true });
  const original = structuredClone(s.journal.records.get(p.planId));
  s.journal.records.get(p.planId).plan.changes[0].set.IDIMPCANITEM = 'N';
  await assert.rejects(s.tool.run('plano.aplicar', { planId: p.planId }), /modificado/);
  s.journal.records.set(p.planId, original);
  const other = createTeknisa({ request: s.request, target: { ...target, branch: '0003' }, operator: 7, journal: s.journal });
  await assert.rejects(other.run('plano.aplicar', { planId: p.planId }), /outro destino/);
  await assert.rejects(applyPlan({ ...s, planId: p.planId, operator: 7, now: () => new Date(Date.now() + 31 * 60000) }), /prazo/);
  assert.equal(s.writes.length, 0);
});
test('alteração concorrente de impressora ou nome impede a gravação do cancelamento', async () => {
  for (const field of ['NRSEQIMPRPROD', 'NMIMPRPROD', 'NMPRODUTO']) {
    const s = server(), p = await s.tool.run('loja.cancelamento.planejar', { all: true, enabled: true });
    s.state[0][field] = field === 'NRSEQIMPRPROD' ? '00004' : 'alteracao-simultanea';
    await assert.rejects(s.tool.run('plano.aplicar', { planId: p.planId }), /Outro campo/);
    assert.equal(s.writes.length, 0);
  }
});
test('recibo registra falha parcial e retomada consulta antes de repetir a gravação', async () => {
  const s = server(), p = await s.tool.run('loja.cancelamento.planejar', { all: true, enabled: true });
  const flaky = async (path, body) => { const result = await s.request(path, body); if (path.endsWith('/save') && s.writes.length === 2) throw new Error('falha depois do envio'); return result; };
  await assert.rejects(applyPlan({ request: flaky, target, operator: 7, planId: p.planId, journal: s.journal, batchSize: 1 }), /falha/);
  assert.equal(s.journal.records.get(p.planId).status, 'interrupted');
  const resumed = await s.tool.run('plano.aplicar', { planId: p.planId, batchSize: 1 });
  assert.equal(resumed.alreadyApplied, 2); assert.equal(s.writes.length, 2);
});
test('nomes de impressora preservam conexão e aceitam a resposta de chaves observada', async () => {
  const s = server(), p = await s.tool.run('loja.impressoras.nomear', { updates: [{ id: '00003', name: 'COZINHA NOVA' }] });
  await s.tool.run('plano.aplicar', { planId: p.planId });
  assert.equal(s.printers[1].NMIMPRLOJA, 'COZINHA NOVA');
  assert.equal(s.printers[1].DSIPPONTE, 'conexao-privada-de-teste');
  assert.equal(JSON.stringify(await s.tool.run('loja.impressoras.listar')).includes('conexao-privada-de-teste'), false);
});
test('rota exige impressora ativa da mesma loja e aceita descrição derivada', async () => {
  const s = server(), p = await s.tool.run('loja.impressoras.planejar', { updates: [{ id: '1', printerCode: '00003' }] });
  s.printers[1].IDATIVO = 'N';
  await assert.rejects(s.tool.run('plano.aplicar', { planId: p.planId }), /inativa/);
  assert.equal(s.writes.length, 0);
  s.printers[1].IDATIVO = 'S'; await s.tool.run('plano.aplicar', { planId: p.planId });
  assert.equal(s.state[0].NMIMPRPROD, 'COZINHA'); assert.equal(s.state[0].IDIMPCANITEM, 'N');
});
test('a reversão gera uma prévia e preserva o restante do registro', async () => {
  const s = server(), p = await s.tool.run('loja.cancelamento.planejar', { all: true, enabled: true });
  await s.tool.run('plano.aplicar', { planId: p.planId });
  const undo = await prepareUndo({ ...s, planId: p.planId });
  assert.equal(s.state[0].IDIMPCANITEM, 'S');
  await s.tool.run('plano.aplicar', { planId: undo.planId }); assert.equal(s.state[0].IDIMPCANITEM, 'N');
});
test('campo fora da função, registro novo e escrita não validada são recusados', async () => {
  const s = server();
  await assert.rejects(preparePlan({ ...s, name: 'loja.produtos', target, updates: [{ id: '1', set: { NRORG: 9 } }] }), /campo/);
  const fakePrices = { ...product(1), CDTABEPREC: '001', DTINIVGPREC: '06/07/2026 00:00:00', CDPRPAITABPR: '0', VRPRECITEM: 50 };
  const pricesRequest = async () => ({ dataset: { vnd42400_tabelapreco_produto_normal_com_preco: [fakePrices] } });
  const pricePlan = await preparePlan({ request: pricesRequest, journal: s.journal, name: 'precos', target: { ...target, table: '001', effectiveFrom: fakePrices.DTINIVGPREC, productLevel: '5' }, updates: [{ id: '1', set: { VRPRECITEM: 51 } }] });
  await assert.rejects(applyPlan({ request: pricesRequest, journal: s.journal, planId: pricePlan.planId, operator: 7 }), /ainda precisa ser validada/);
  const p = await s.tool.run('loja.cancelamento.planejar', { all: true, enabled: true });
  s.state[0].__is_new = true;
  await assert.rejects(s.tool.run('plano.aplicar', { planId: p.planId }), /Outro campo|existentes/);
});
test('consulta distingue formato inválido, outro destino e paginação repetida', async () => {
  await assert.rejects(readResource(async () => ({}), 'loja.produtos', target), /conjunto de dados/);
  await assert.rejects(readResource(async () => ({ dataset: { ger12300_cadloja_produtos: [{ ...product(1), CDFILIAL: '0009' }] } }), 'loja.produtos', target), /outro destino/);
  const repeated = Array.from({ length: 50 }, (_, i) => ({ ...product(i), SGUNIDADE: 'UN', IDESTOCOMP: 'E', IDIMPRODUVEZ: 'N' }));
  await assert.rejects(readResource(async () => ({ dataset: { produto_produto: repeated } }), 'produtos', target), /página repetida/);
});
test('separação usa o preparo da bebida e recusa códigos com destinos conflitantes', () => {
  assert.equal(classifyProduction({ group: 'DESTILADOS', name: 'Dose de Rum' }), 'balcao');
  assert.equal(classifyProduction({ group: 'BEBIDAS', name: 'Suco copo' }), 'bar');
  assert.equal(classifyProduction({ group: 'COQUETÉIS', name: 'Caipirinha' }), 'bar');
  assert.equal(classifyProduction({ group: 'MENU EXECUTIVO', name: 'Filé' }), 'cozinha');
  const roles = { balcao: '00001', cozinha: '00003', bar: '00004' }, row = product(1);
  assert.throws(() => buildRoutingUpdates([row], [{ sku: row.CDARVPROD, role: 'bar' }, { sku: row.CDARVPROD, role: 'cozinha' }], roles), /destinos diferentes/);
  assert.equal(buildRoutingUpdates([row], [{ sku: row.CDARVPROD, name: 'desconhecido' }], roles).unresolved.length, 1);
});

const observed = (overrides = {}) => ({ method: 'Network.requestWillBeSent', params: { request: { method: 'POST', url: 'https://retail.teknisa.com/backend_man/index.php/ger12300_cadloja_produtos',
  headers: { 'OAuth-Token': 'fixture-token', 'OAuth-Hash': 'fixture-hash', 'OAuth-Project': 'MAN', 'User-Id': '7' }, ...overrides } } });
test('transporte só usa caminhos cadastrados e mantém cabeçalhos fora do retorno', async () => {
  const calls = [];
  const cdp = { async send(_method, params) {
    const value = await runInNewContext(params.expression, { AbortController, setTimeout, clearTimeout,
      fetch: async (url, options) => { calls.push({ url, options }); return { ok: true, json: async () => ({ dataset: {} }) }; } });
    return { result: { value } };
  } };
  const session = connectObservedSession({ cdp, observations: [observed()] });
  assert.equal(session.operator, undefined);
  await session.request(RESOURCES['loja.produtos'].path, { requestType: 'FilterData' });
  assert.equal(calls.length, 1); assert.equal(calls[0].options.redirect, 'error');
  assert.equal(JSON.stringify(session.describe()).includes('fixture-token'), false);
  const actor = connectObservedSession({ cdp, observations: [observed({ url: 'https://retail.teknisa.com/backend_man/index.php/ger12300_cadloja_produtos/save', postData: JSON.stringify({ dataset: [{ CDOPERADOR: 12 }] }) })] });
  assert.equal(actor.operator, 12);
  await assert.rejects(session.request('https://example.com', {}), /Caminho/);
  await assert.rejects(session.request(RESOURCES.produtos.path, { requestType: 'FilterData' }), /módulo/);
  session.close(); await assert.rejects(session.request(RESOURCES['loja.produtos'].path, {}), /encerrada/);
});
test('erros do navegador e respostas de autenticação não exibem segredos', async () => {
  const hidden = connectObservedSession({ cdp: { send: async () => { throw new Error('fixture-token'); } }, observations: [observed()] });
  await assert.rejects(hidden.request(RESOURCES['loja.produtos'].path, { requestType: 'FilterData' }), error => !error.message.includes('fixture-token'));
  const expired = connectObservedSession({ cdp: { send: async () => ({ result: { value: { ok: false, code: 'SESSION_EXPIRED' } } }) }, observations: [observed()] });
  await assert.rejects(expired.request(RESOURCES['loja.produtos'].path, { requestType: 'FilterData' }), error => error.code === 'SESSION_EXPIRED');
  assert.throws(() => connectObservedSession({ cdp: { send() {} }, observations: [observed({ url: 'https://example.com/backend_man/index.php/ger12300_cadloja_produtos' })] }), /Capture/);
});
test('comissão diferencia dado ausente, zero confirmado e regra desconhecida', () => {
  assert.equal(summarizeSellerSales({ month: '2026-10', rows: [], coverage: {} }).status, 'unavailable');
  const coverage = { complete: true, month: '2026-10', source: 'fonte de teste' };
  assert.equal(summarizeSellerSales({ month: '2026-10', rows: [], coverage: { ...coverage, complete: 'false' } }).status, 'unavailable');
  assert.deepEqual(summarizeSellerSales({ month: '2026-10', rows: [], coverage }).sellers, []);
  const rows = [{ id: 'v1', sellerId: 'g1', occurredAt: '2026-11-01T02:00:00Z', netProductCents: 10000 }];
  const pending = summarizeSellerSales({ month: '2026-10', rows, coverage });
  assert.equal(pending.sellers[0].commission.amountCents, null);
  const result = summarizeSellerSales({ month: '2026-10', rows, coverage, commissionRules: [{ sellerId: 'g1', base: 'netProductCents', rateBasisPoints: 500 }] });
  assert.equal(result.sellers[0].commission.amountCents, 500);
  assert.throws(() => summarizeSellerSales({ month: '2026-10', rows: [...rows, ...rows], coverage }), /duplicado/);
});
test('dados ausentes e seleção contraditória retornam erro antes de ampliar o lote', async () => {
  const s = server();
  await assert.rejects(s.tool.run('loja.cancelamento.planejar', { all: true, productIds: ['1'], enabled: true }), /Escolha/);
  await assert.rejects(s.tool.run('loja.impressoras.nomear'), /lista/);
  await assert.rejects(s.tool.run('produtos.cadastrar.preparar', { price: Infinity }), /positivo/);
  assert.equal(s.writes.length, 0);
});
test('recibos em arquivo são gravados atomicamente e o bloqueio impede concorrência local', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'teknisa-test-')), journal = createFileJournal(dir);
  try {
    const s = server(), p = await preparePlan({ ...s, journal, target, name: 'loja.produtos', updates: [{ id: '1', set: { IDIMPCANITEM: 'S' } }] });
    assert.equal((await journal.load(p.planId)).status, 'prepared');
    await journal.lock(target, async () => { await assert.rejects(journal.lock(target, async () => {}), /execução local/); });
    await assert.rejects(journal.load('../segredo'), /Identificador/);
  } finally { for (const name of await readdir(dir)) await unlink(join(dir, name)); await rmdir(dir); }
});

const saleLine = (extra = {}) => ({ NRORG: 42, CDFILIAL: '0002', CDLOJA: '0001', CDVENDEDOR2: 'g1', GARCON: 'Vendedor de teste',
  QTPRODVEND: 1, VRFINALITEM: 110, VRLIQUIDO: 100, VRLIQACRES: 95, ACR: 5, DES: 2, VRGORJETA: 3, VRTXENTREGA: 2, VRREPITEM: 10,
  NRINSCRCONS: 'identificador-privado-de-teste', ...extra });
test('consulta real de produtividade preserva colunas oficiais e descarta identificadores fiscais', async () => {
  const journal = memoryJournal();
  const request = async (path, body) => {
    assert.equal(path, RESOURCES['vendas.garcons'].path);
    assert.deepEqual(body.filter.find(f => f.name === 'DTMOVTURCAIX').value, ['01/10/2026', '27/10/2026']);
    assert.deepEqual(body.filter.find(f => f.name === 'CDLOJA').value, ['00020001']);
    return { dataset: { vnd09900_relProdutividadePorVendedor: [saleLine(), saleLine()] } };
  };
  const tool = createTeknisa({ request, journal, target, operator: 7 });
  const report = await tool.run('vendas.garcons.consultar', { from: '01/10/2026', to: '27/10/2026' });
  assert.equal(report.lines, 2); assert.equal(report.sellers[0].reportedNetCents, 20000);
  assert.equal(report.sellers[0].tipCents, 600); assert.equal(report.sellers[0].commission.amountCents, null);
  assert.equal(report.periodBasis, 'DTMOVTURCAIX'); assert.equal(report.unassignedExcluded, true);
  assert.equal(JSON.stringify(report).includes('identificador-privado-de-teste'), false);
  const calculated = await tool.run('vendas.garcons.comissao', { from: '01/10/2026', to: '27/10/2026',
    rules: [{ sellerId: '*', base: 'reportedNetCents', rateBasisPoints: 500 }] });
  assert.equal(calculated.sellers[0].commission.amountCents, 1000);
  assert.equal(calculated.sellers[0].commission.sourceField, 'VRLIQUIDO');
});
test('relatório financeiro recusa página repetida, intervalo inválido e precisão não conferida', async () => {
  const reportTarget = { ...target, from: '01/10/2026', to: '27/10/2026' };
  const repeated = async () => ({ dataset: { vnd09900_relProdutividadePorVendedor: Array.from({ length: 500 }, () => saleLine()) } });
  await assert.rejects(readResource(repeated, 'vendas.garcons', reportTarget), /repetiu uma página/);
  await assert.rejects(readResource(repeated, 'vendas.garcons', { ...reportTarget, from: '31/02/2026' }), /data inválida/);
  await assert.rejects(readResource(repeated, 'vendas.garcons', { ...reportTarget, from: '01/01/2026' }), /31 dias/);
  const tool = createTeknisa({ request: async () => ({ dataset: { vnd09900_relProdutividadePorVendedor: [saleLine({ VRLIQUIDO: 1.2345 })] } }), target });
  await assert.rejects(tool.run('vendas.garcons.consultar', { from: reportTarget.from, to: reportTarget.to }), /precisão monetária/);
});
