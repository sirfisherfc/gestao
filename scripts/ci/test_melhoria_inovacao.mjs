// Resumo, ordem de trabalho, filtros e escape da rotina Melhoria e Inovacao.
//
// A pagina calcula o resumo no navegador a partir da mesma lista que desenha,
// entao um erro de contagem nao aparece como falha de consulta: aparece como
// numero errado no cartao. Estes casos fixam o calculo e a ordem.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import vm from 'node:vm';

const read = name => readFileSync(new URL('../../' + name, import.meta.url), 'utf8');
const html = read('melhoria_inovacao.html');
const inline = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)];
assert.equal(inline.length, 1, 'esperado um unico script inline na pagina');

function elemento(id) {
  return {
    id, value: '', textContent: '', innerHTML: '', hidden: false, disabled: false,
    dataset: {}, style: {},
    classList: {add() {}, remove() {}, toggle() {}, contains: () => false},
    addEventListener() {}, setAttribute() {}, getAttribute: () => null,
    focus() {}, setSelectionRange() {},
    querySelector: () => null, querySelectorAll: () => [],
    appendChild() {}, replaceChildren() {}
  };
}

function tela() {
  const elementos = new Map();
  const document = {
    getElementById(id) {
      if (!elementos.has(id)) elementos.set(id, elemento(id));
      return elementos.get(id);
    },
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener() {},
    createElement: () => elemento('novo'),
    body: elemento('body'),
    head: elemento('head')
  };
  const contexto = vm.createContext({console, setTimeout, clearTimeout, document});
  contexto.window = contexto;
  contexto.globalThis = contexto;
  vm.runInContext(read('assets/safe-dom.js'), contexto);
  contexto.SirFisherDOM = contexto.window.SirFisherDOM;
  contexto.SirFisherSupabase = {from: () => ({select: () => ({})}), rpc: async () => ({error: null})};
  // requireRole devolvendo null encerra a inicializacao sem tocar a rede.
  contexto.SirFisherAuth = {requireRole: async () => null};
  vm.runInContext(
    inline[0][1] + '\n;globalThis.__t={render,resumo,filtradas,caminhoEvidencia,htmlEvidencias,'
      + 'defIdeias:v=>{IDEIAS=v;},defFiltro:v=>{FILTRO=v;}};',
    contexto,
    {filename: 'melhoria_inovacao.inline.js'}
  );
  return {
    ...contexto.__t,
    markup: () => elementos.get('main')?.innerHTML || ''
  };
}

const base = {
  descricao: null, origem: 'Equipe', responsavel_id: null, responsavel_nome: null,
  prazo: null, proxima_acao: null, concluida_em: null, resultado_aprendizado: null,
  impacto_financeiro: null, motivo_descarte: null, referencia_origem: null,
  criado_por_nome: null, vencida: false, dias_ate_conclusao: null,
  concluida_no_prazo: null, evidencias: 0
};
const amostra = () => [
  {...base, id: 1, titulo: 'Vencida', area: 'Cozinha', status: 'Em andamento', prioridade: 'Alta',
   primeira_manifestacao_em: '2026-04-01', prazo: '2026-08-31', vencida: true,
   criado_em: '2026-04-01T15:00:00Z', atualizado_em: '2026-04-01T15:00:00Z'},
  {...base, id: 2, titulo: 'Concluída', area: 'Salão', status: 'Concluída', prioridade: 'Média',
   primeira_manifestacao_em: '2026-05-01', prazo: '2026-06-01', concluida_em: '2026-05-20',
   dias_ate_conclusao: 19, concluida_no_prazo: true, impacto_financeiro: '1250.50',
   resultado_aprendizado: 'deu certo', responsavel_nome: 'Responsável',
   criado_em: '2026-05-01T15:00:00Z', atualizado_em: '2026-05-20T15:00:00Z'},
  {...base, id: 3, titulo: 'Recebida agora', area: 'Marketing', status: 'Recebida', prioridade: 'Baixa',
   primeira_manifestacao_em: '2026-09-14',
   criado_em: '2026-09-14T12:00:00Z', atualizado_em: '2026-09-14T12:00:00Z'},
  {...base, id: 4, titulo: 'Descartada', area: 'Bar', status: 'Descartada', prioridade: 'Alta',
   primeira_manifestacao_em: '2026-06-10', motivo_descarte: 'não compensa',
   criado_em: '2026-06-10T12:00:00Z', atualizado_em: '2026-06-10T12:00:00Z'}
];

test('resumo conta status, vencidas e as metricas discretas', () => {
  const t = tela();
  t.defIdeias(amostra());
  const r = t.resumo();
  assert.equal(r.total, 4);
  assert.equal(r.abertas, 2);
  assert.equal(r.vencidas, 1);
  assert.equal(r.porStatus['Em andamento'], 1);
  assert.equal(r.porStatus['Concluída'], 1);
  assert.equal(r.porStatus['Descartada'], 1);
  assert.equal(r.taxa, 25);
  assert.equal(r.prazoMedio, 19);
  assert.equal(r.noPrazo, 100);
  assert.equal(r.impacto, 1250.5);
});

test('sem ideias o resumo nao inventa taxa nem impacto', () => {
  const t = tela();
  t.defIdeias([]);
  const r = t.resumo();
  assert.equal(r.total, 0);
  assert.equal(r.taxa, null);
  assert.equal(r.prazoMedio, null);
  assert.equal(r.noPrazo, null);
  assert.equal(r.impacto, null);
  t.render();
  assert.match(t.markup(), /Nenhuma ideia/);
});

test('ordem: vencida, depois aberta por prioridade, encerrada por ultimo', () => {
  const t = tela();
  t.defIdeias(amostra());
  assert.deepEqual(t.filtradas().map(i => i.id), [1, 3, 4, 2]);
});

test('filtros de texto, status e area sao independentes', () => {
  const t = tela();
  t.defIdeias(amostra());
  t.defFiltro({busca: 'descartada', status: '', area: ''});
  assert.deepEqual(t.filtradas().map(i => i.id), [4]);
  t.defFiltro({busca: '', status: 'Concluída', area: ''});
  assert.deepEqual(t.filtradas().map(i => i.id), [2]);
  t.defFiltro({busca: '', status: '', area: 'Bar'});
  assert.deepEqual(t.filtradas().map(i => i.id), [4]);
  t.defFiltro({busca: 'não existe', status: '', area: ''});
  assert.equal(t.filtradas().length, 0);
});

test('lista renderiza cada ideia sem buraco de dado', () => {
  const t = tela();
  t.defIdeias(amostra());
  t.render();
  const markup = t.markup();
  assert.equal((markup.match(/class="mi-item/g) || []).length, 4);
  assert.doesNotMatch(markup, /undefined|NaN|\[object Object\]/);
  assert.match(markup, /Sem responsável/);
  assert.match(markup, /Sem prazo/);
  assert.match(markup, /4 de 4/);
});

test('titulo vindo do banco e escapado antes de ir para a lista', () => {
  const t = tela();
  t.defIdeias([{...amostra()[0], titulo: '<img src=x onerror=alert(1)>'}]);
  t.render();
  const markup = t.markup();
  assert.doesNotMatch(markup, /<img src=x/);
  assert.match(markup, /&lt;img src=x/);
});

// A RPC so aceita melhoria/<id>/<arquivo>, sem ".." e sem segmento vazio; o
// Storage recusa chave com acento, espaco ou barra. O nome do arquivo vem do
// disco de quem envia, entao os dois limites sao testados aqui.
test('caminho do arquivo cabe na regra da RPC e do Storage', () => {
  const t = tela();
  const nomes = [
    'Relatório da auditoria (final).PDF',
    '../../etc/passwd',
    'a'.repeat(200) + '.png',
    '   ',
    'nota..fiscal.pdf',
    '.htaccess'
  ];
  for (const nome of nomes) {
    const caminho = t.caminhoEvidencia(42, nome);
    const partes = caminho.split('/');
    assert.equal(partes.length, 3, `segmentos em ${caminho}`);
    assert.equal(partes[0], 'melhoria');
    assert.equal(partes[1], '42');
    assert.ok(partes[2].length > 0, `nome vazio em ${caminho}`);
    assert.ok(!caminho.includes('..'), `caminho com .. em ${caminho}`);
    assert.match(partes[2], /^[a-z0-9][a-z0-9.-]*$/, `caractere invalido em ${partes[2]}`);
  }
});

test('dois envios do mesmo arquivo nao geram o mesmo caminho', () => {
  const t = tela();
  assert.notEqual(t.caminhoEvidencia(1, 'foto.jpg'), t.caminhoEvidencia(1, 'foto.jpg'));
});

test('evidencia sem link assinado nao vira ancora quebrada', () => {
  const t = tela();
  const comLink = t.htmlEvidencias([
    {id: 1, titulo: 'Nota', url: 'https://exemplo.test/x', storage_path: null}
  ]);
  assert.ok(comLink.includes('data-url="https://exemplo.test/x"'));
  assert.match(comLink, />link</);

  const semAssinatura = t.htmlEvidencias([
    {id: 2, titulo: 'Foto', url: null, storage_path: 'melhoria/1/x.png'}
  ]);
  assert.doesNotMatch(semAssinatura, /<a /);
  assert.match(semAssinatura, />arquivo</);

  const assinada = t.htmlEvidencias([
    {id: 3, titulo: 'Foto', url: null, storage_path: 'melhoria/1/x.png', link_assinado: 'https://s.test/assinado'}
  ]);
  assert.ok(assinada.includes('data-url="https://s.test/assinado"'));
});
