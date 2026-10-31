import { REQUEST_TYPES as COMPOSITION_REQUEST_TYPES } from './composicoes.mjs';

export const SESSION_ADAPTER_VERSION = '2026-10-31.4';

const ORIGIN = 'https://retail.teknisa.com';
const man = '/backend_man/index.php/';
const cad = '/backend_cadEst/index.php/';
// Keep the newly observed rules local: persistent runtimes may have cached an
// older static dependency even when this adapter is imported with a fresh URL.
const PATHS = Object.freeze({
  productSave: cad + 'saveProduct',
  bindingRemove: cad + 'grupromocprod_grupopromoc/remove',
});
export const OBSERVED_COMPOSITION_REQUEST_TYPES = Object.freeze({
  [cad + 'crud/produto_produto']: 'FilterData',
  [cad + 'crud/grupromoc']: 'FilterData',
  [cad + 'crud/grupromoc/save']: 'DataSet',
  [cad + 'grupromocprod_grupopromoc']: 'FilterData',
  [cad + 'grupromocprod_grupopromoc/save']: 'DataSet',
  [cad + 'grupromocprod_grupopromoc/remove']: 'Row',
  [cad + 'prodgrupromoc_produto']: 'FilterData',
  [cad + 'prodgrupromoc_produto/save']: 'DataSet',
  [cad + 'saveProduct']: 'Row',
});
const observationReads = ['vnd57000_cadastrodeobs_obsproduto', 'vnd57000_cadastrodeobs_obsproduto_produtos',
  'vnd57000_cadastrodeobs_ocorrencias', 'vnd57000_cadastrodeobs_grupObrig', 'vnd57000_cadastrodeobs_prodObrig'];
const observationWrites = ['vnd57000_cadastrodeobs_produtos/saveOservacaoProdutos', 'vnd57000_cadastrodeobs_obsproduto_produtos/remove'];

// These defaults reproduce the validated shared-tool paths plus the composition
// UI calls validated with successful readbacks. Other writes require
// the complete observed request and an explicit successful readback assertion.
export const DEFAULT_REQUEST_TYPES = Object.freeze({
  ...COMPOSITION_REQUEST_TYPES,
  ...OBSERVED_COMPOSITION_REQUEST_TYPES,
  ...Object.fromEntries(observationReads.map(path => [man + path, 'FilterData'])),
  ...Object.fromEntries(observationWrites.map(path => [man + path, 'DataSet'])),
  [man + 'ger12300_cadloja_produtos']: 'FilterData',
  [man + 'ger12300_cadloja_produtos/save']: 'DataSet',
  [man + 'impressoraNFLoja']: 'FilterData',
  [man + 'impressoraNFLoja/save']: 'DataSet',
  [man + 'vnd42400_tabelapreco_vigencias']: 'FilterData',
  [man + 'vnd42400_tabelapreco_produto']: 'FilterData',
  [cad + 'ger01900_cadastroproduto_venda_imposto']: 'FilterData',
});
export const DEFAULT_READ_PATHS = Object.freeze(Object.keys(DEFAULT_REQUEST_TYPES).filter(path => DEFAULT_REQUEST_TYPES[path] === 'FilterData'));
export const DEFAULT_WRITE_PATHS = Object.freeze(Object.keys(DEFAULT_REQUEST_TYPES).filter(path => DEFAULT_REQUEST_TYPES[path] !== 'FilterData'));
const EXTENDABLE_WRITES = Object.freeze({
  [PATHS.productSave]: 'Row',
  [PATHS.bindingRemove]: 'Row',
  [cad + 'prodgrupromoc_produto/save']: 'DataSet',
  [man + 'vnd41000_grupoPromo_prod/save']: 'DataSet',
  [cad + 'ger01900_cadastroproduto_venda_imposto/save']: 'DataSet',
  [man + 'vnd42400_tabelapreco_produto/save']: 'DataSet',
  [cad + 'vnd42400_tabelapreco_precoProd/save']: 'DataSet',
  [cad + 'produto_para_arvore/save']: 'Row',
});
const authNames = ['Accept', 'Content-Type', 'OAuth-Hash', 'OAuth-KeepConnected', 'OAuth-Project', 'OAuth-Token', 'User-Id'];
const fail = (code, message) => { throw Object.assign(new Error(message), { code }); };
const safeError = code => Object.assign(new Error({
  SESSION_EXPIRED: 'A sessão expirou ou não tem acesso ao recurso.',
  HTTP_ERROR: 'O servidor recusou a chamada. Confira o estado atual antes de repetir.',
  TIMEOUT: 'A chamada excedeu o tempo. Confira o estado atual antes de repetir.',
  INVALID_JSON: 'O servidor respondeu em formato diferente do esperado.',
  DISPOSED: 'A conexão foi encerrada.',
}[code] || 'A chamada não foi concluída. Confira o estado atual antes de repetir.'), { code });
const pathIsInternal = path => typeof path === 'string' && /^\/backend_(?:man|cadEst)\/index\.php\/[A-Za-z0-9_/-]+$/.test(path);

export function buildSessionRules(observedContracts = []) {
  if (!Array.isArray(observedContracts)) fail('INVALID_CONTRACT_LIST', 'Informe os contratos observados como lista.');
  const rules = { ...DEFAULT_REQUEST_TYPES };
  for (const contract of observedContracts) {
    const { path, body, source } = contract || {};
    if (!pathIsInternal(path) || !body || typeof source !== 'string' || source.trim().length < 8
      || !['FilterData', 'DataSet', 'Row'].includes(body.requestType)) {
      fail('INVALID_OBSERVED_CONTRACT', 'Informe caminho, corpo completo e origem do contrato observado.');
    }
    const read = body.requestType === 'FilterData';
    if (read) {
      if (/\/(?:save|remove)(?:[A-Z][A-Za-z]+)?$/.test(path) || !Array.isArray(body.filter))
        fail('INVALID_OBSERVED_READ', 'A consulta observada precisa conter filtros e usar um caminho de leitura.');
    } else {
      if (contract.readbackVerified !== true || (EXTENDABLE_WRITES[path] || DEFAULT_REQUEST_TYPES[path]) !== body.requestType
        || (body.requestType === 'DataSet' && (!Array.isArray(body.dataset) || !body.dataset.length))
        || (body.requestType === 'Row' && !body.dataset && !body.row)) {
        fail('UNVERIFIED_WRITE_CONTRACT', 'A escrita exige corpo completo observado e releitura conferida.');
      }
    }
    if (rules[path] && rules[path] !== body.requestType) fail('CONFLICTING_REQUEST_TYPE', 'O caminho já tem outro tipo de requisição validado.');
    rules[path] = body.requestType;
  }
  return Object.freeze(rules);
}

export async function beginSessionCapture(cdp) {
  await cdp.send('Network.enable', {});
  return (await cdp.readEvents({ methods: ['Network.requestWillBeSent'], limit: 1 })).cursor;
}
export async function finishSessionCapture(cdp, cursor) {
  const observations = [];
  let more;
  do {
    const page = await cdp.readEvents({ afterSequence: cursor, methods: ['Network.requestWillBeSent'], limit: 1000 });
    if (page.truncated) fail('TRUNCATED_CAPTURE', 'A captura ficou incompleta. Capture outra consulta conhecida.');
    observations.push(...page.events); cursor = page.cursor; more = page.hasMore;
  } while (more);
  return observations;
}

export function connectCompositionSession({ cdp, observations, observedContracts = [], timeoutMs = 20000 }) {
  if (!cdp?.send || !Array.isArray(observations) || !Number.isSafeInteger(timeoutMs) || timeoutMs < 100 || timeoutMs > 60000)
    fail('INVALID_SESSION_INPUT', 'Forneça o CDP autorizado e os eventos capturados na sessão.');
  const rules = buildSessionRules(observedContracts);
  const credentials = new Map();
  for (const event of observations) {
    const request = event?.params?.request;
    if (event.method !== 'Network.requestWillBeSent' || !request || request.method !== 'POST') continue;
    let url;
    try { url = new URL(request.url); } catch { continue; }
    if (url.origin !== ORIGIN || !Object.hasOwn(rules, url.pathname) || url.search || url.hash) continue;
    const headers = {};
    for (const name of authNames) {
      const entry = Object.entries(request.headers || {}).find(([key]) => key.toLowerCase() === name.toLowerCase());
      if (entry && typeof entry[1] === 'string') headers[name] = entry[1];
    }
    if (headers['OAuth-Token'] && headers['OAuth-Hash'] && headers['OAuth-Project'])
      credentials.set(url.pathname.split('/')[1], headers);
  }
  if (!credentials.size) fail('MISSING_CAPTURED_SESSION', 'Capture uma consulta autenticada de um caminho cadastrado.');
  const identities = new Set([...credentials.values()].map(headers => headers['User-Id']).filter(Boolean));
  if (identities.size > 1) { credentials.clear(); fail('MIXED_SESSION_IDENTITIES', 'As capturas pertencem a contas diferentes. Capture novamente.'); }
  const metrics = { calls: 0, writes: 0, elapsedMs: 0 };
  return Object.freeze({
    describe: () => ({ connected: !!credentials.size, origin: ORIGIN, projects: [...credentials.keys()],
      allowedReads: Object.values(rules).filter(type => type === 'FilterData').length,
      allowedWrites: Object.values(rules).filter(type => type !== 'FilterData').length, ...metrics }),
    rules: () => ({ ...rules }),
    close: () => { credentials.clear(); },
    async request(path, body) {
      if (!credentials.size) throw safeError('DISPOSED');
      if (!Object.hasOwn(rules, path)) fail('PATH_NOT_ALLOWED', 'O caminho ainda não foi validado para esta execução.');
      if (!body || body.requestType !== rules[path]) fail('REQUEST_TYPE_NOT_ALLOWED', 'O corpo usa um tipo diferente do contrato observado.');
      const headers = credentials.get(path.split('/')[1]);
      if (!headers) fail('MODULE_NOT_CONNECTED', 'Capture uma consulta autorizada do módulo que atende essa operação.');
      const started = performance.now();
      metrics.calls++; if (rules[path] !== 'FilterData') metrics.writes++;
      // Neither this expression nor its headers are returned, logged, or saved.
      const expression = `(async()=>{const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),${timeoutMs});try{const r=await fetch(${JSON.stringify(ORIGIN + path)},{method:'POST',credentials:'same-origin',redirect:'error',signal:controller.signal,headers:${JSON.stringify(headers)},body:${JSON.stringify(JSON.stringify(body))}});if(!r.ok)return {ok:false,code:[401,403].includes(r.status)?'SESSION_EXPIRED':'HTTP_ERROR'};let data;try{data=await r.json()}catch{return {ok:false,code:'INVALID_JSON'}}return {ok:true,data};}catch(e){return {ok:false,code:e.name==='AbortError'?'TIMEOUT':'BROWSER_ERROR'}}finally{clearTimeout(timer)}})()`;
      try {
        const response = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, { timeoutMs: timeoutMs + 5000 });
        if (response.exceptionDetails || !response.result?.value?.ok) throw safeError(response.result?.value?.code || 'BROWSER_ERROR');
        return response.result.value.data;
      } catch (error) {
        if (['SESSION_EXPIRED', 'HTTP_ERROR', 'TIMEOUT', 'INVALID_JSON', 'BROWSER_ERROR'].includes(error.code)) throw error;
        throw safeError('BROWSER_ERROR');
      } finally { metrics.elapsedMs += Math.round(performance.now() - started); }
    },
  });
}
// Keep the shared-tool connectObservedSession export in sessao_browser.mjs.
