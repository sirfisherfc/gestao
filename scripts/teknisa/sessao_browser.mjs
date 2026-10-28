import { ALLOWED_PATHS, ORIGIN } from './recursos.mjs';

const authNames = ['Accept', 'Content-Type', 'OAuth-Hash', 'OAuth-KeepConnected', 'OAuth-Project', 'OAuth-Token', 'User-Id'];
const safeError = code => Object.assign(new Error({
  SESSION_EXPIRED: 'A sessão do Teknisa expirou ou não possui acesso ao recurso.',
  HTTP_ERROR: 'O Teknisa recusou a chamada. Consulte o recibo antes de repetir uma gravação.',
  TIMEOUT: 'A chamada excedeu o tempo. Faça uma consulta antes de repetir a gravação.',
  INVALID_JSON: 'O servidor retornou um formato diferente de JSON.',
  DISPOSED: 'A conexão foi encerrada.',
}[code] || 'A chamada do navegador falhou. Confira a conexão e consulte o estado atual.'), { code });

export async function beginSessionCapture(cdp) {
  await cdp.send('Network.enable', {});
  return (await cdp.readEvents({ methods: ['Network.requestWillBeSent'], limit: 1 })).cursor;
}
export async function finishSessionCapture(cdp, cursor) {
  const observations = [];
  let more;
  do {
    const page = await cdp.readEvents({ afterSequence: cursor, methods: ['Network.requestWillBeSent'], limit: 1000 });
    if (page.truncated) throw new Error('A captura ficou incompleta. Inicie uma captura nova.');
    observations.push(...page.events); cursor = page.cursor; more = page.hasMore;
  } while (more);
  return observations;
}

/** Use uma requisição observada na sessão autorizada. O retorno não expõe cabeçalhos. */
export function connectObservedSession({ cdp, observations, timeoutMs = 20000 }) {
  if (!cdp?.send || !Array.isArray(observations) || !Number.isSafeInteger(timeoutMs) || timeoutMs < 100 || timeoutMs > 60000) {
    throw new Error('Informe o CDP documentado do navegador e a captura da sessão.');
  }
  let credentials = new Map();
  const capturedOperators = new Set();
  for (const event of observations) {
    const request = event?.params?.request;
    if (event.method !== 'Network.requestWillBeSent' || !request) continue;
    let url;
    try { url = new URL(request.url); } catch { continue; }
    if (url.origin !== ORIGIN || !ALLOWED_PATHS.includes(url.pathname) || url.search || url.hash || request.method !== 'POST') continue;
    const headers = {};
    for (const name of authNames) {
      const entry = Object.entries(request.headers || {}).find(([key]) => key.toLowerCase() === name.toLowerCase());
      if (entry) headers[name] = entry[1];
    }
    if (headers['OAuth-Token'] && headers['OAuth-Hash'] && headers['OAuth-Project']) credentials.set(url.pathname.split('/')[1], headers);
    if (url.pathname.endsWith('/save') && request.postData) {
      let payload;
      try { payload = JSON.parse(request.postData); } catch { continue; }
      for (const row of Array.isArray(payload.dataset) ? payload.dataset : []) {
        if (Number.isSafeInteger(row.CDOPERADOR) && row.CDOPERADOR > 0) capturedOperators.add(row.CDOPERADOR);
      }
    }
  }
  if (!credentials.size) throw new Error('Capture uma consulta autenticada de um recurso cadastrado na ferramenta.');
  const identities = new Set([...credentials.values()].map(headers => headers['User-Id']).filter(Boolean));
  if (identities.size > 1 || capturedOperators.size > 1) throw new Error('As capturas pertencem a identidades diferentes. Refaça a conexão.');
  // User-Id é um cabeçalho de autenticação; não é o código de operador do cadastro.
  const operator = capturedOperators.size === 1 ? [...capturedOperators][0] : undefined;
  const metrics = { calls: 0, writes: 0, elapsedMs: 0 };
  return Object.freeze({
    operator: Number.isSafeInteger(operator) && operator > 0 ? operator : undefined,
    describe: () => ({ connected: !!credentials.size, origin: ORIGIN, projects: [...credentials.keys()], ...metrics }),
    close: () => { credentials.clear(); },
    request: async (path, body) => {
      if (!credentials.size) throw safeError('DISPOSED');
      if (!ALLOWED_PATHS.includes(path)) throw new Error('Caminho fora dos recursos cadastrados.');
      const headers = credentials.get(path.split('/')[1]);
      if (!headers) throw new Error('Capture uma consulta do módulo do Teknisa que atende essa operação.');
      const write = path.endsWith('/save');
      if (!body || body.requestType !== (write ? 'DataSet' : 'FilterData')) throw new Error('Tipo de chamada incompatível com o caminho.');
      const started = performance.now();
      metrics.calls++; if (write) metrics.writes++;
      // A expressão e os cabeçalhos ficam em memória, sem log ou arquivo.
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
