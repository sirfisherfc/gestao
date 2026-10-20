// Edge Function: stone-webhook
// -----------------------------------------------------------------------------
// Recebe os avisos da API de Conciliação da Stone. Hoje só o Pix usa webhook:
// depois de um POST em .../conciliation-file/pix/{data}, a Stone gera o CSV do
// dia e manda aqui um link pré-assinado. A função grava o aviso em
// public.stone_pix_arquivo e baixa o CSV em segundo plano, porque o link pode
// expirar antes da rotina diária ler a fila. O importador Python
// (scripts/importacao/api_stone_pix.py) processa a fila.
//
// A Stone não assina os avisos. A proteção é o token na própria URL
// cadastrada (?token=...), conferido contra o segredo STONE_WEBHOOK_TOKEN.
// verify_jwt=false no deploy, porque a Stone não manda JWT do Supabase.
//
// Segredos: STONE_WEBHOOK_TOKEN (SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY já
// vêm do ambiente das Edge Functions).
// -----------------------------------------------------------------------------

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const TOKEN = Deno.env.get("STONE_WEBHOOK_TOKEN") ?? "";

function resposta(status: number, texto: string): Response {
  return new Response(texto, { status, headers: { "content-type": "text/plain; charset=utf-8" } });
}

// Compara sem atalho, para o tempo de resposta não revelar o token.
function tokenValido(recebido: string | null): boolean {
  if (!TOKEN || !recebido || recebido.length !== TOKEN.length) return false;
  let diferenca = 0;
  for (let i = 0; i < TOKEN.length; i++) diferenca |= TOKEN.charCodeAt(i) ^ recebido.charCodeAt(i);
  return diferenca === 0;
}

// O formato do aviso não é documentado além de type, document, referenceDate e
// "a URL pré-assinada"; o link é o primeiro valor https do corpo.
function acharLink(valor: unknown): string | null {
  if (typeof valor === "string") return valor.startsWith("https://") ? valor : null;
  if (valor && typeof valor === "object") {
    for (const item of Object.values(valor as Record<string, unknown>)) {
      const achado = acharLink(item);
      if (achado) return achado;
    }
  }
  return null;
}

function dataReferencia(valor: unknown): string | null {
  const texto = String(valor ?? "").replace(/\D/g, "");
  return texto.length === 8 ? `${texto.slice(0, 4)}-${texto.slice(4, 6)}-${texto.slice(6, 8)}` : null;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return resposta(405, "método não permitido");
  if (!tokenValido(new URL(req.url).searchParams.get("token"))) return resposta(401, "não autorizado");

  let corpo: Record<string, unknown>;
  try {
    corpo = await req.json();
  } catch {
    return resposta(400, "corpo inválido");
  }
  // A Stone valida a URL no cadastro e espera 2xx em até 3 segundos.
  if (corpo?.type === "validation_notification") return resposta(200, "ok");

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
    { auth: { persistSession: false } },
  );
  const link = acharLink(corpo);
  const { data, error } = await supabase
    .from("stone_pix_arquivo")
    .insert({
      tipo: typeof corpo?.type === "string" ? corpo.type : null,
      documento: String(corpo?.document ?? "").replace(/\D/g, "") || null,
      data_referencia: dataReferencia(corpo?.referenceDate),
      url_arquivo: link,
      aviso: corpo,
    })
    .select("id")
    .single();
  if (error || !data) return resposta(500, "falha ao registrar o aviso");

  if (link) {
    // A Stone exige 200 em até 5 segundos; o download segue depois da resposta.
    const baixar = async () => {
      try {
        const arquivo = await fetch(link);
        const atualizacao = arquivo.ok
          ? { conteudo: await arquivo.text(), baixado_em: new Date().toISOString() }
          : { erro: `download do CSV respondeu HTTP ${arquivo.status}` };
        await supabase.from("stone_pix_arquivo").update(atualizacao).eq("id", data.id);
      } catch (_erro) {
        await supabase.from("stone_pix_arquivo").update({ erro: "falha ao baixar o CSV" }).eq("id", data.id);
      }
    };
    // @ts-ignore EdgeRuntime existe no runtime do Supabase.
    EdgeRuntime.waitUntil(baixar());
  }
  return resposta(200, "ok");
});
