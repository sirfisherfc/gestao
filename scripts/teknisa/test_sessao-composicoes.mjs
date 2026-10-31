import test from 'node:test';
import assert from 'node:assert/strict';
import { connectCompositionSession, buildSessionRules, DEFAULT_REQUEST_TYPES, OBSERVED_COMPOSITION_REQUEST_TYPES, SESSION_ADAPTER_VERSION } from './sessao-composicoes.mjs';
import { PATHS } from './composicoes.mjs';
const observed = (path, identity = 'same-account', prefix = 'cad') => ({ method: 'Network.requestWillBeSent', params: { request: {
  url: 'https://retail.teknisa.com' + path, method: 'POST', headers: {
    'OAuth-Token': prefix + '-private-fixture', 'OAuth-Hash': prefix + '-fixture-hash', 'OAuth-Project': prefix,
    'User-Id': identity, 'Content-Type': 'application/json',
  },
} } });
test('version4 locally pins the observed write types independently of cached dependencies', () => {
  assert.equal(SESSION_ADAPTER_VERSION, '2026-10-31.4');
  for (const [path, type] of Object.entries({
    '/backend_cadEst/index.php/prodgrupromoc_produto/save': 'DataSet',
    '/backend_cadEst/index.php/grupromocprod_grupopromoc/remove': 'Row',
    '/backend_cadEst/index.php/saveProduct': 'Row',
  })) { assert.equal(OBSERVED_COMPOSITION_REQUEST_TYPES[path], type); assert.equal(DEFAULT_REQUEST_TYPES[path], type); }
});
function fixture(events = [observed(PATHS.groups)]) {
  const calls = [];
  const cdp = { send: async (...args) => { calls.push(args); return { result: { value: { ok: true, data: { result: 'fixture-data' } } } }; } };
  return { calls, session: connectCompositionSession({ cdp, observations: events }) };
}
test('permits captured composition reads and the validated group creation type', async () => {
  const { calls, session } = fixture();
  assert.deepEqual(await session.request(PATHS.groups, { requestType: 'FilterData', filter: [] }), { result: 'fixture-data' });
  await session.request(PATHS.groupsSave, { requestType: 'DataSet', dataset: [{ CDGRUPROMOC: '0000000014' }] });
  assert.equal(calls.length, 2); assert.equal(session.describe().writes, 1);
});
test('unknown paths and wrong request types are rejected before CDP evaluation', async () => {
  const { calls, session } = fixture();
  await assert.rejects(session.request('/backend_cadEst/index.php/arbitrary/save', { requestType: 'DataSet' }), { code: 'PATH_NOT_ALLOWED' });
  await assert.rejects(session.request(PATHS.groups, { requestType: 'Row' }), { code: 'REQUEST_TYPE_NOT_ALLOWED' });
  await assert.rejects(session.request(PATHS.productSave, { requestType: 'DataSet' }), { code: 'REQUEST_TYPE_NOT_ALLOWED' });
  assert.equal(calls.length, 0);
});
test('keeps module credentials separate and excludes private values from summaries', async () => {
  const manPath = '/backend_man/index.php/vnd57000_cadastrodeobs_ocorrencias';
  const { calls, session } = fixture([observed(PATHS.groups), observed(manPath, 'same-account', 'man')]);
  await session.request(manPath, { requestType: 'FilterData', filter: [] });
  assert.match(calls[0][1].expression, /man-private-fixture/);
  assert.doesNotMatch(calls[0][1].expression, /cad-private-fixture/);
  assert.doesNotMatch(JSON.stringify(session.describe()), /private-fixture|fixture-hash|same-account/);
});
test('does not capture another origin or a path with a query string', () => {
  const foreign = observed(PATHS.groups); foreign.params.request.url = 'https://example.com' + PATHS.groups;
  const query = observed(PATHS.groups); query.params.request.url += '?x=1';
  assert.throws(() => fixture([foreign, query]), { code: 'MISSING_CAPTURED_SESSION' });
});
test('rejects mixed accounts and refuses a module without its own capture', async () => {
  assert.throws(() => fixture([observed(PATHS.groups, 'one'), observed('/backend_man/index.php/vnd57000_cadastrodeobs_ocorrencias', 'two')]), { code: 'MIXED_SESSION_IDENTITIES' });
  const { calls, session } = fixture();
  await assert.rejects(session.request('/backend_man/index.php/vnd57000_cadastrodeobs_ocorrencias', { requestType: 'FilterData' }), { code: 'MODULE_NOT_CONNECTED' });
  assert.equal(calls.length, 0);
});
test('an extra Row write requires the complete observed contract and verified readback', () => {
  const path = '/backend_cadEst/index.php/produto_para_arvore/save';
  const contract = { path, source: 'captured legitimate product UI operation', body: { requestType: 'Row', row: { NRORG: 5482, CDPRODUTO: '0000000015' } } };
  assert.throws(() => buildSessionRules([contract]), { code: 'UNVERIFIED_WRITE_CONTRACT' });
  const rules = buildSessionRules([{ ...contract, readbackVerified: true }]);
  assert.equal(rules[path], 'Row');
  assert.equal(DEFAULT_REQUEST_TYPES[path], undefined);
  assert.equal(DEFAULT_REQUEST_TYPES[PATHS.productSave], 'Row');
});
test('an observed read path can be registered without widening any writes', () => {
  const path = '/backend_cadEst/index.php/ger14600_composicao_do_produto';
  const rules = buildSessionRules([{ path, source: 'fixture captured read', body: { requestType: 'FilterData', filter: [] } }]);
  assert.equal(rules[path], 'FilterData');
  assert.equal(rules[path + '/save'], undefined);
});
test('the newly observed component price endpoint needs its full validated DataSet contract', () => {
  const path = '/backend_cadEst/index.php/vnd42400_tabelapreco_precoProd/save';
  const contract = { path, source: 'synthetic fixture of the validated component price contract',
    body: { requestType: 'DataSet', dataset: [{ __is_new: true, NRORG: 5482, CDPRODUTO: '8000508001', VRPRECITEM: 0.01,
      CDFILIAL: ['0002'], CDTABEPREC: ['001'], DTINIVGPREC: ['06/07/2026'] }] } };
  assert.equal(DEFAULT_REQUEST_TYPES[path], undefined);
  assert.throws(() => buildSessionRules([contract]), { code: 'UNVERIFIED_WRITE_CONTRACT' });
  assert.equal(buildSessionRules([{ ...contract, readbackVerified: true }])[path], 'DataSet');
  assert.throws(() => buildSessionRules([{ ...contract, readbackVerified: true, body: { ...contract.body, requestType: 'Row' } }]), { code: 'UNVERIFIED_WRITE_CONTRACT' });
});
test('closing removes the session and network failures do not leak diagnostics', async () => {
  const { session } = fixture(); session.close();
  await assert.rejects(session.request(PATHS.groups, { requestType: 'FilterData' }), { code: 'DISPOSED' });
  const failing = connectCompositionSession({ cdp: { send: async () => { throw new Error('secret diagnostic'); } }, observations: [observed(PATHS.groups)] });
  await assert.rejects(failing.request(PATHS.groups, { requestType: 'FilterData' }), error => error.code === 'BROWSER_ERROR' && !error.message.includes('secret'));
});
