(function () {
  'use strict';

  const SUPABASE_URL = "https://lucpxoynpvogkvzepagi.supabase.co";
  const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx1Y3B4b3lucHZvZ2t2emVwYWdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDYxNzQsImV4cCI6MjA5OTE4MjE3NH0.r0XGYX1KqAXQA4g9uoUAFLFTEaWUEXobWqyKVe0_SnE";

  const client = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

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
