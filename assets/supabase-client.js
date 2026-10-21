(function () {
  'use strict';

  const SUPABASE_URL = "https://lucpxoynpvogkvzepagi.supabase.co";
  const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx1Y3B4b3lucHZvZ2t2emVwYWdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDYxNzQsImV4cCI6MjA5OTE4MjE3NH0.r0XGYX1KqAXQA4g9uoUAFLFTEaWUEXobWqyKVe0_SnE";

  // Medicao de desempenho opcional: ?perf=1 liga e ?perf=0 desliga, valendo
  // para a aba. Desligada, o cliente e criado exatamente como antes.
  const PERF_KEY = 'sirfisher_perf';

  function perfLigado() {
    try {
      const flag = new URLSearchParams(window.location.search).get('perf');
      if (flag === '1') sessionStorage.setItem(PERF_KEY, '1');
      if (flag === '0') sessionStorage.removeItem(PERF_KEY);
      return sessionStorage.getItem(PERF_KEY) === '1';
    } catch (_error) {
      return false;
    }
  }

  function criarMedidor() {
    const registros = [];
    let pendentes = 0;
    let timer = null;
    let lcp = null;
    try {
      new PerformanceObserver((lista) => {
        const entradas = lista.getEntries();
        if (entradas.length) lcp = entradas[entradas.length - 1].startTime;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    } catch (_error) {
      // Navegador sem LCP: o resumo mostra so os demais marcos.
    }

    function rotulo(url) {
      try {
        const caminho = new URL(url, window.location.href).pathname;
        return caminho.replace(/^\/rest\/v1\//, '').replace(/^\/auth\/v1\//, 'auth/');
      } catch (_error) {
        return String(url);
      }
    }

    // Rodada: grupo de requisicoes que comecam antes de a anterior terminar.
    function rodadas(lista) {
      let total = 0;
      let fimRodada = -1;
      lista.slice().sort((a, b) => a.inicio - b.inicio).forEach((r) => {
        if (r.inicio >= fimRodada) total += 1;
        fimRodada = Math.max(fimRodada, r.fim);
      });
      return total;
    }

    function ms(valor) {
      return valor == null ? '—' : Math.round(valor) + ' ms';
    }

    function resumir() {
      const nav = performance.getEntriesByType('navigation')[0] || null;
      const fcp = performance.getEntriesByName('first-contentful-paint')[0] || null;
      const auth = performance.getEntriesByName('sirfisher:auth')[0] || null;
      const fimDados = registros.reduce((max, r) => Math.max(max, r.fim), 0);
      const resumo = {
        pagina: window.location.pathname.split('/').pop() || 'index.html',
        html: nav ? Math.round(nav.responseEnd) : null,
        primeira_pintura: fcp ? Math.round(fcp.startTime) : null,
        maior_pintura: lcp == null ? null : Math.round(lcp),
        auth_pronto: auth ? Math.round(auth.startTime) : null,
        dados_completos: Math.round(fimDados),
        requisicoes: registros.length,
        rodadas: rodadas(registros)
      };
      console.table(registros.map((r) => ({
        consulta: r.nome,
        inicio_ms: Math.round(r.inicio),
        duracao_ms: Math.round(r.fim - r.inicio),
        status: r.status
      })));
      console.info('[perf]', resumo);
      let caixa = document.getElementById('sf-perf');
      if (!caixa) {
        caixa = document.createElement('div');
        caixa.id = 'sf-perf';
        Object.assign(caixa.style, {
          position: 'fixed', left: '8px', bottom: '8px', zIndex: '9999', maxWidth: '320px',
          background: '#12313f', color: '#fff', font: '11px/1.5 Roboto,Arial,sans-serif',
          padding: '8px 10px', borderRadius: '8px', boxShadow: '0 6px 18px rgba(0,0,0,.25)',
          whiteSpace: 'pre-line', cursor: 'pointer'
        });
        caixa.title = 'Medição ativa (?perf=0 desliga). Clique para fechar.';
        caixa.addEventListener('click', () => caixa.remove());
        document.body.appendChild(caixa);
      }
      caixa.textContent = [
        'Medição · ' + resumo.pagina,
        'HTML ' + ms(resumo.html) + ' · 1ª pintura ' + ms(resumo.primeira_pintura),
        'Maior pintura ' + ms(resumo.maior_pintura) + ' · acesso ' + ms(resumo.auth_pronto),
        'Dados completos ' + ms(resumo.dados_completos),
        resumo.requisicoes + ' consultas em ' + resumo.rodadas + ' rodadas'
      ].join('\n');
      window.SirFisherPerf = Object.freeze({ resumo, registros: registros.slice() });
    }

    function agendar() {
      clearTimeout(timer);
      if (pendentes === 0) timer = setTimeout(resumir, 1500);
    }

    async function medirFetch(input, init) {
      const nome = rotulo(typeof input === 'string' ? input : input?.url);
      const inicio = performance.now();
      pendentes += 1;
      clearTimeout(timer);
      try {
        const resposta = await fetch(input, init);
        registros.push({ nome, inicio, fim: performance.now(), status: resposta.status });
        return resposta;
      } catch (error) {
        registros.push({ nome, inicio, fim: performance.now(), status: 'falha' });
        throw error;
      } finally {
        pendentes -= 1;
        agendar();
      }
    }

    return { fetch: medirFetch };
  }

  const medidor = perfLigado() ? criarMedidor() : null;
  const client = medidor
    ? supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { global: { fetch: medidor.fetch } })
    : supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  const RETRY_DEFAULTS = Object.freeze({
    maxAttempts: 3,
    baseDelayMs: 300,
    maxDelayMs: 3000,
    jitterMs: 150,
    attemptTimeoutMs: 12000,
    budgetMs: 30000
  });

  function positiveNumber(value, fallback, allowZero = false) {
    const number = Number(value);
    const valid = Number.isFinite(number) && (allowZero ? number >= 0 : number > 0);
    return valid ? number : fallback;
  }

  function retryOptions(options, legacyBaseDelayMs) {
    const supplied = typeof options === 'number'
      ? {maxAttempts: options, baseDelayMs: legacyBaseDelayMs}
      : (options || {});
    return {
      maxAttempts: Math.max(1, Math.floor(positiveNumber(supplied.maxAttempts, RETRY_DEFAULTS.maxAttempts))),
      baseDelayMs: positiveNumber(supplied.baseDelayMs, RETRY_DEFAULTS.baseDelayMs, true),
      maxDelayMs: positiveNumber(supplied.maxDelayMs, RETRY_DEFAULTS.maxDelayMs, true),
      jitterMs: positiveNumber(supplied.jitterMs, RETRY_DEFAULTS.jitterMs, true),
      attemptTimeoutMs: positiveNumber(supplied.attemptTimeoutMs, RETRY_DEFAULTS.attemptTimeoutMs),
      budgetMs: positiveNumber(supplied.budgetMs, RETRY_DEFAULTS.budgetMs),
      signal: supplied.signal || null
    };
  }

  function abortError(reason) {
    if (reason && reason.name === 'AbortError') return reason;
    const error = new Error('Operação cancelada.');
    error.name = 'AbortError';
    if (reason !== undefined) error.cause = reason;
    return error;
  }

  function timeoutError() {
    const error = new Error('Tempo limite da consulta excedido.');
    error.name = 'TimeoutError';
    error.code = 'RESILIENT_TIMEOUT';
    return error;
  }

  function responseStatus(response, error) {
    const candidates = [response?.status, response?.statusCode, error?.status, error?.statusCode];
    for (const candidate of candidates) {
      const status = Number(candidate);
      if (Number.isFinite(status) && status > 0) return status;
    }
    return 0;
  }

  function errorText(error) {
    return [error?.message, error?.details, error?.hint].filter(Boolean).join(' ');
  }

  function isRetryable(response, error, thrown, timedOut) {
    if (timedOut || error?.code === 'RESILIENT_TIMEOUT') return true;
    if (error?.name === 'AbortError') return false;

    const code = String(error?.code || '').toUpperCase();
    if (code === 'PGRST003') return true;
    if (['ECONNRESET', 'ECONNREFUSED', 'ETIMEDOUT', 'ENETUNREACH', 'EAI_AGAIN'].includes(code)) return true;
    if (code === '57014') {
      // 57014 também representa cancelamento voluntário. Só o statement timeout é transitório.
      return /statement timeout|due to timeout|query timeout|tempo limite/i.test(errorText(error));
    }

    const status = responseStatus(response, error);
    if (status === 408 || status === 429 || (status >= 500 && status <= 599)) return true;
    if (status >= 400 && status <= 499) return false;

    const text = errorText(error);
    const networkFailure = /failed to fetch|fetch failed|network\s*(error|request failed)|load failed|connection (reset|refused|closed)|econnreset|econnrefused/i.test(text);
    return networkFailure || (thrown && error?.name === 'TypeError');
  }

  function waitForRetry(delayMs, signal) {
    if (signal?.aborted) return Promise.reject(abortError(signal.reason));
    if (delayMs <= 0) return Promise.resolve();
    return new Promise((resolve, reject) => {
      let timer;
      const cleanup = () => {
        clearTimeout(timer);
        signal?.removeEventListener?.('abort', onAbort);
      };
      const onAbort = () => {
        cleanup();
        reject(abortError(signal.reason));
      };
      timer = setTimeout(() => {
        cleanup();
        resolve();
      }, delayMs);
      signal?.addEventListener?.('abort', onAbort, {once: true});
    });
  }

  async function runAttempt(fetcher, externalSignal, timeoutMs, attempt) {
    if (externalSignal?.aborted) throw abortError(externalSignal.reason);

    const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
    const attemptSignal = controller?.signal || externalSignal;
    let timer;
    let externalAbort;
    let timedOut = false;
    const races = [Promise.resolve().then(() => fetcher(attemptSignal, attempt))];

    if (externalSignal) {
      races.push(new Promise((_resolve, reject) => {
        externalAbort = () => {
          try { controller?.abort(externalSignal.reason); } catch (_error) { controller?.abort(); }
          reject(abortError(externalSignal.reason));
        };
        externalSignal.addEventListener?.('abort', externalAbort, {once: true});
      }));
    }

    if (timeoutMs > 0) {
      races.push(new Promise((_resolve, reject) => {
        timer = setTimeout(() => {
          timedOut = true;
          try { controller?.abort(); } catch (_error) {}
          reject(timeoutError());
        }, timeoutMs);
      }));
    }

    try {
      return await Promise.race(races);
    } catch (error) {
      if (timedOut && error?.code !== 'RESILIENT_TIMEOUT') throw timeoutError();
      throw error;
    } finally {
      clearTimeout(timer);
      externalSignal?.removeEventListener?.('abort', externalAbort);
    }
  }

  /**
   * Executa consultas Supabase com orçamento total, timeout por tentativa e
   * backoff cancelável. O fetcher recebe (signal, numeroDaTentativa).
   * Mantém compatibilidade com resilientFetch(fetcher, maxAttempts, baseDelayMs).
   */
  async function resilientFetch(fetcher, options, legacyBaseDelayMs) {
    const config = retryOptions(options, legacyBaseDelayMs);
    const startedAt = Date.now();
    let lastResponse;
    let lastError;

    for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
      if (config.signal?.aborted) throw abortError(config.signal.reason);
      const remaining = config.budgetMs - (Date.now() - startedAt);
      if (remaining <= 0) break;

      let retry = false;
      try {
        lastResponse = await runAttempt(
          fetcher,
          config.signal,
          Math.max(1, Math.min(config.attemptTimeoutMs, remaining)),
          attempt
        );
        if (!lastResponse?.error) return lastResponse;
        retry = isRetryable(lastResponse, lastResponse.error, false, false);
        if (!retry || attempt >= config.maxAttempts) return lastResponse;
      } catch (error) {
        if (config.signal?.aborted) throw abortError(config.signal.reason);
        lastError = error;
        retry = isRetryable(null, error, true, error?.code === 'RESILIENT_TIMEOUT');
        if (!retry || attempt >= config.maxAttempts) throw error;
      }

      const budgetAfterAttempt = config.budgetMs - (Date.now() - startedAt);
      if (budgetAfterAttempt <= 0) break;
      const jitter = Math.random() * config.jitterMs;
      const delay = Math.min(
        config.baseDelayMs * Math.pow(2, attempt - 1) + jitter,
        config.maxDelayMs,
        budgetAfterAttempt
      );
      if (delay >= budgetAfterAttempt) break;
      await waitForRetry(delay, config.signal);
    }

    if (lastResponse !== undefined) return lastResponse;
    if (lastError) throw lastError;
    throw timeoutError();
  }

  client.resilientFetch = resilientFetch;
  window.SirFisherSupabase = client;
})();
