// Recebe o CSV diário de Pix solicitado à Stone. Sem JWT Supabase: o
// remetente usa um token privado cadastrado na Stone. Nunca registrar a URL.
// O download segue em segundo plano; nenhum dado financeiro vai para logs.
const TOKEN = Deno.env.get("STONE_WEBHOOK_TOKEN") ?? "";
const DOCUMENTO = Deno.env.get("STONE_PIX_DOCUMENT") ?? "";
const BASE = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

function resposta(status, texto) {
  return new Response(texto, { status, headers: { "content-type": "text/plain; charset=utf-8" } });
}

function tokenValido(recebido) {
  if (TOKEN.length < 24 || !recebido || recebido.length !== TOKEN.length) return false;
  let diferenca = 0;
  for (let i = 0; i < TOKEN.length; i++) diferenca |= TOKEN.charCodeAt(i) ^ recebido.charCodeAt(i);
  return diferenca === 0;
}

function dataReferencia(valor) {
  const digitos = String(valor ?? "").replace(/\D/g, "");
  if (!/^\d{8}$/.test(digitos)) return null;
  const dia = `${digitos.slice(0, 4)}-${digitos.slice(4, 6)}-${digitos.slice(6, 8)}`;
  const data = new Date(`${dia}T00:00:00Z`);
  return Number.isFinite(data.getTime()) && data.toISOString().slice(0, 10) === dia ? dia : null;
}

function linkValido(valor) {
  try {
    const url = new URL(valor);
    const host = url.hostname.toLowerCase();
    return url.protocol === "https:" && !url.username && !url.password && (!url.port || url.port === "443")
      && host.includes(".") && !/^[\d.]+$/.test(host) && !host.includes(":")
      && !host.endsWith(".local") && !host.endsWith(".internal")
      && host !== new URL(BASE).hostname;
  } catch {
    return false;
  }
}

async function gravar(metodo, sufixo, corpo, retornar = false) {
  return await fetch(`${BASE}/rest/v1/stone_pix_arquivo${sufixo}`, {
    method: metodo,
    headers: {
      apikey: SERVICE, Authorization: `Bearer ${SERVICE}`, "content-type": "application/json",
      Prefer: retornar ? "return=representation" : "return=minimal",
    },
    body: JSON.stringify(corpo), signal: AbortSignal.timeout(2500), redirect: "error",
  });
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return resposta(405, "método não permitido");
  const recebido = req.headers.get("x-sirfisher-stone-token") ?? new URL(req.url).searchParams.get("token");
  if (!tokenValido(recebido)) return resposta(401, "não autorizado");
  let corpo;
  try {
    const texto = await req.text();
    if (texto.length > 65536) return resposta(413, "aviso muito grande");
    corpo = JSON.parse(texto);
    if (!corpo || typeof corpo !== "object" || Array.isArray(corpo)) return resposta(400, "corpo inválido");
  } catch {
    return resposta(400, "corpo inválido");
  }
  if (corpo.type === "validation_notification") return resposta(200, "ok");
  const documento = String(corpo.document ?? "").replace(/\D/g, "");
  const dia = dataReferencia(corpo.referenceDate);
  if (!DOCUMENTO || documento !== DOCUMENTO) return resposta(403, "documento não autorizado");
  if (corpo.type !== "pix" || !dia || !linkValido(corpo.url)) return resposta(400, "aviso Pix inválido");
  let registro;
  try {
    const resultado = await gravar("POST", "?select=id", {
      tipo: "pix", documento, data_referencia: dia, url_arquivo: corpo.url, aviso: corpo,
    }, true);
    if (!resultado.ok) return resposta(500, "falha ao registrar o aviso");
    const linhas = await resultado.json();
    registro = linhas[0]?.id;
    if (!registro) return resposta(500, "falha ao registrar o aviso");
  } catch {
    return resposta(500, "falha ao registrar o aviso");
  }
  const baixar = async () => {
    let atualizacao;
    try {
      const arquivo = await fetch(corpo.url, { signal: AbortSignal.timeout(20000), redirect: "error" });
      if (!arquivo.ok) {
        atualizacao = { erro: `download do CSV respondeu HTTP ${arquivo.status}` };
      } else {
        const conteudo = await arquivo.text();
        atualizacao = conteudo.length > 5_000_000
          ? { erro: "CSV excede o tamanho permitido" }
          : { conteudo, baixado_em: new Date().toISOString(), erro: null };
      }
    } catch {
      atualizacao = { erro: "falha ao baixar o CSV" };
    }
    try {
      await gravar("PATCH", `?id=eq.${encodeURIComponent(registro)}`, atualizacao);
    } catch {
      // O aviso já está salvo; o importador pode recuperar o download.
    }
  };
  EdgeRuntime.waitUntil(baixar());
  return resposta(200, "ok");
});
