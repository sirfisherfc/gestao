import test from 'node:test';
import assert from 'node:assert/strict';
import { createTeknisa } from './teknisa.mjs';
import { OBSERVATION_PATHS, planLinks, applyLinks } from './observacoes.mjs';
import { ALLOWED_PATHS, WRITE_PATHS } from './recursos.mjs';

const target = { organization: 42, branch: '0002', store: '0001' };
function memoryJournal() {
  const records = new Map();
  return { records, async save(row) { records.set(row.id, structuredClone(row)); },
    async load(id) { return structuredClone(records.get(id)); }, async lock(_target, callback) { return callback(); } };
}
function server() {
  const occurrences = ['01', '02', '05', '06', '55', '56'].map(code => ({ CDGRPOCOR: '01', CDOCORR: code, DSOCORR: `OBS ${code}`,
    IDCONTROLAOBS: code > '50' ? 'A' : 'O', CDPRODUTO: code > '50' ? `81101${code}` : null, NRORG: 42 }));
  const products = [{ CDGRPOCOR: '01', CDPRODUTO: '0000000096', CDARVPROD: '8000500000', NMPRODUTO: 'FILE MIGNON UN', NRORG: 42 },
    { CDGRPOCOR: '01', CDPRODUTO: '8000010100', CDARVPROD: '8000010100', NMPRODUTO: 'PATINHA UN', NRORG: 42 }];
  const links = new Map([['0000000096', ['05', '06']], ['8000010100', ['55', '56']]]);
  const writes = [], journal = memoryJournal();
  const value = (body, name) => body.filter.find(item => item.name === name)?.value;
  const request = async (path, body) => {
    assert.ok(ALLOWED_PATHS.includes(path));
    if (path === OBSERVATION_PATHS.ocorrencias) return { dataset: { vnd57000_cadastrodeobs_ocorrencias: structuredClone(occurrences) } };
    if (path === OBSERVATION_PATHS.produtos) return { dataset: { vnd57000_cadastrodeobs_obsproduto: structuredClone(products) } };
    if (path === OBSERVATION_PATHS.grupos) return { dataset: { vnd57000_cadastrodeobs_grupObrig: [{ CDGRUPOOBRIG: '0000000001', NMGRUPOBRIG: 'ARROZ' }] } };
    if (path === OBSERVATION_PATHS.grupoItens) return { dataset: { vnd57000_cadastrodeobs_prodObrig: [{ CDOCORR: '01' }, { CDOCORR: '02' }] } };
    if (path === OBSERVATION_PATHS.vinculos) {
      const id = value(body, 'CDPRODUTO');
      return { dataset: { vnd57000_cadastrodeobs_obsproduto_produtos: links.get(id).map(code => ({ CDGRPOCOR: '01', CDOCORR: code, CDPRODUTO: id, NRORG: 42, __is_new: false })) } };
    }
    assert.ok(WRITE_PATHS.includes(path)); assert.equal(body.requestType, 'DataSet');
    writes.push({ path, body: structuredClone(body) });
    for (const row of body.dataset) {
      const current = links.get(row.CDPRODUTO);
      if (path === OBSERVATION_PATHS.adicionar) { assert.equal(row.__is_new, true); current.push(row.CDOCORR); }
      else links.set(row.CDPRODUTO, current.filter(code => code !== row.CDOCORR));
    }
    return path === OBSERVATION_PATHS.adicionar
      ? { dataset: { vnd57000_cadastrodeobs_obsproduto_produtos: body.dataset.map(row => ({ CDGRPOCOR: '01', CDPRODUTO: row.CDPRODUTO, NRORG: 42 })) } } : [];
  };
  return { links, writes, request, journal, tool: createTeknisa({ request, target, operator: 7, journal }) };
}

test('opções: prévia sem gravar, aplicação com releitura e repetição sem nova escrita', async () => {
  const s = server();
  const plan = await s.tool.run('observacoes.vinculos.planejar', { changes: [
    { productId: '0000000096', add: ['01', '02', '05'] },
    { productId: '8000010100', add: ['05', '06'], remove: ['55', '56'] }] });
  assert.equal(plan.changes, 2); assert.deepEqual(plan.sample[0].add, ['01', '02']); assert.equal(s.writes.length, 0);
  const result = await s.tool.run('plano.aplicar', { planId: plan.planId });
  assert.equal(result.verified, 2);
  assert.deepEqual([...s.links.get('0000000096')].sort(), ['01', '02', '05', '06']);
  assert.deepEqual([...s.links.get('8000010100')].sort(), ['05', '06']);
  assert.equal(s.writes.length, 3);
  assert.equal((await s.tool.run('plano.aplicar', { planId: plan.planId })).alreadyApplied, 2);
  assert.equal(s.writes.length, 3);
  const undo = await s.tool.run('plano.reverter', { planId: plan.planId });
  await s.tool.run('plano.aplicar', { planId: undo.planId });
  assert.deepEqual([...s.links.get('8000010100')].sort(), ['55', '56']);
});
test('opções: código inexistente, produto fora do cadastro e alteração externa são recusados', async () => {
  const s = server();
  await assert.rejects(s.tool.run('observacoes.vinculos.planejar', { changes: [{ productId: '0000000096', add: ['99'] }] }), /não existe/);
  await assert.rejects(s.tool.run('observacoes.vinculos.planejar', { changes: [{ productId: '123', add: ['01'] }] }), /Observação por produto/);
  const plan = await planLinks({ request: s.request, target, journal: s.journal, changes: [{ productId: '0000000096', add: ['01'] }] });
  s.links.get('0000000096').push('55');
  await assert.rejects(applyLinks({ request: s.request, planId: plan.planId, journal: s.journal }), /mudaram/);
  assert.equal(s.writes.length, 0);
  const late = await planLinks({ request: s.request, target, journal: s.journal, changes: [{ productId: '0000000096', add: ['02'] }] });
  await assert.rejects(applyLinks({ request: s.request, planId: late.planId, journal: s.journal, now: () => new Date(Date.now() + 31 * 60000) }), /prazo/);
});
test('opções: listagem traz ocorrências, grupos obrigatórios e vínculos por produto', async () => {
  const s = server();
  const listed = await s.tool.run('observacoes.listar');
  assert.equal(listed.occurrences.find(item => item.code === '55').kind, 'A');
  assert.deepEqual(listed.mandatoryGroups[0].codes, ['01', '02']);
  const links = await s.tool.run('observacoes.vinculos.listar', { search: 'patinha' });
  assert.deepEqual(links, [{ productId: '8000010100', tree: '8000010100', name: 'PATINHA UN', codes: ['55', '56'] }]);
});
