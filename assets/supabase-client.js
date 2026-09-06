(function () {
  'use strict';

  const SUPABASE_URL = "https://lucpxoynpvogkvzepagi.supabase.co";
  const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx1Y3B4b3lucHZvZ2t2emVwYWdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDYxNzQsImV4cCI6MjA5OTE4MjE3NH0.r0XGYX1KqAXQA4g9uoUAFLFTEaWUEXobWqyKVe0_SnE";

  const client = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  /**
   * Executa consultas Supabase com resiliência móvel:
   * - Retenta falhas transitórias (5xx, timeouts, conectividade) até 3 vezes com backoff exponencial e jitter
   * - Não retenta erros 4xx de cliente/permissão nem cancelamentos por AbortController
   */
  async function resilientFetch(fetcher, maxAttempts = 3, baseDelayMs = 300) {
    let attempt = 0;
    while (attempt < maxAttempts) {
      attempt++;
      try {
        const res = await fetcher();
        if (res && res.error) {
          const err = res.error;
          const status = Number(err.status || err.statusCode || (err.code === 'PGRST003' ? 504 : 0));
          const isTransient = status >= 500 || status === 0 || err.code === 'PGRST003';
          const isPermissionOrClient = status >= 400 && status < 500 && status !== 408 && status !== 429;
          if (isPermissionOrClient || !isTransient || attempt >= maxAttempts) {
            return res;
          }
          const jitter = Math.random() * 150;
          const delay = Math.min(baseDelayMs * Math.pow(2, attempt - 1) + jitter, 3000);
          await new Promise(r => setTimeout(r, delay));
          continue;
        }
        return res;
      } catch (err) {
        if (err.name === 'AbortError' || attempt >= maxAttempts) {
          throw err;
        }
        const jitter = Math.random() * 150;
        const delay = Math.min(baseDelayMs * Math.pow(2, attempt - 1) + jitter, 3000);
        await new Promise(r => setTimeout(r, delay));
      }
    }
  }

  client.resilientFetch = resilientFetch;
  window.SirFisherSupabase = client;
})();
