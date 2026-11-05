// Run the actual management controller with an offline DOM adapter.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import vm from 'node:vm';
const V = createRequire(import.meta.url)('../../assets/voucher-template.js');
const html = await readFile(new URL('../../vouchers.html', import.meta.url), 'utf8');
const source = await readFile(new URL('../../assets/vouchers.js', import.meta.url), 'utf8');
const base = { id: '11111111-1111-4111-8111-111111111111', revision: 3, code: 'A1B2C3', status: 'expired',
  beneficiary_name: 'Cliente de teste', phone: '85999990000', benefit_type: 'fixed', benefit_value: 100,
  expires_on: '2000-01-01', issue_reason: 'friend', issue_reason_detail: '', internal_note: '',
  created_at: '2026-11-05T14:00:00Z', issued_by_name: 'Sócio de teste', conditions: ['Uso único.'] };

async function mount(status = 'expired') {
  const nodes = new Map(), calls = [], voucher = { ...base, status };
  class Element {
    constructor(tag = 'div') { this.tagName = tag.toUpperCase(); this.children = []; this.events = new Map(); this.open = false; this.value = ''; this.firstChild = { textContent: '' }; this.dataset = {}; this.classList = { add() {}, toggle() {} }; }
    set innerHTML(value) { for (const [, id] of value.matchAll(/\bid="([^"]+)"/g)) nodes.set(id, new Element()); }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children = items; }
    addEventListener(name, fn) { this.events.set(name, fn); }
    setAttribute() {} removeAttribute() {}
    showModal() { this.open = true; }
    close() { this.open = false; this.events.get('close')?.(); }
    reset() {} reportValidity() { return true; }
    click() { return this.events.get('click')?.(); }
  }
  for (const [, id] of html.matchAll(/\bid="([^"]+)"/g)) nodes.set(id, new Element());
  const elements = Object.fromEntries(['beneficiary', 'phone', 'type', 'value', 'expiry', 'reason', 'reason_detail', 'note'].map(name => [name, new Element('input')]));
  nodes.get('issue-form').elements = elements;
  nodes.get('cancel-form').elements = { reason: new Element(), confirmed: new Element() };
  const context = {
    window: { voucherAuth: Promise.resolve({ role: 'socio' }), BenefitVoucher: V, SirFisherSupabase: { rpc: async (name, args) => {
      calls.push({ name, args });
      if (name === 'benefit_voucher_list') return { data: { ok: true, rows: [voucher], total: 1, summary: { issued: 1, available: 0, used: 0, expired: 1, cancelled: 0, fixed_available_total: 0, percent_available_count: 0 } } };
      assert.equal(name, 'benefit_voucher_detail'); return { data: { ok: true, voucher, events: [] } };
    } } },
    document: { getElementById: id => { assert.ok(nodes.has(id), `Missing DOM target ${id}`); return nodes.get(id); }, createElement: tag => new Element(tag), querySelectorAll: () => [] },
  };
  await vm.runInNewContext(source, context);
  await nodes.get('voucher-list').children[0].click();
  return { nodes, calls, elements };
}

test('vencido oferece renovação com nova validade sugerida sem alterar o voucher ao abrir', async () => {
  const app = await mount(); const button = app.nodes.get('edit-btn');
  assert.equal(button.hidden, false); assert.equal(button.textContent, 'Renovar validade');
  button.click(); assert.equal(app.nodes.get('issue-dialog').open, true);
  assert.equal(app.nodes.get('issue-title').textContent, 'Renovar voucher');
  assert.equal(app.elements.expiry.value, V.todayPlus(30)); assert.equal(app.elements.expiry.min, V.todayPlus());
  assert.equal(app.elements.beneficiary.value, base.beneficiary_name);
  assert.equal(app.calls.filter(call => call.name === 'benefit_voucher_edit').length, 0);
});

test('condições e histórico começam recolhidos e sem mensagem de compartilhamento indisponível', async () => {
  const app = await mount();
  const disclosures = app.nodes.get('detail-body').children[0].children[0].children.filter(node => node.tagName === 'DETAILS');
  assert.deepEqual(disclosures.map(node => node.children[0].textContent), ['Condições', 'Histórico']);
  assert.ok(disclosures.every(node => !node.open));
  assert.equal(app.nodes.get('detail-message').textContent, '');
  assert.equal(app.nodes.get('download-btn').hidden, true);
});

for (const status of ['used', 'cancelled']) test(`${status} continua sem edição ou renovação`, async () => {
  const app = await mount(status); assert.equal(app.nodes.get('edit-btn').hidden, true);
  app.nodes.get('edit-btn').click(); assert.equal(app.nodes.get('issue-dialog').open, false);
});
