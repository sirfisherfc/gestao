#!/usr/bin/env python3
"""Abre Pluggy Connect localmente e guarda os IDs autorizados no .env ignorado.

O navegador recebe só o connect token restrito. Client secret e API key nunca
saem do Python. O servidor aceita apenas localhost, com proteção de origem e
sessão, e valida cada item na aplicação antes de salvar seu ID.
"""

from __future__ import annotations

import argparse
import json
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from api_cliente import RAIZ_PROJETO, carregar_env
from api_pluggy import Cliente, ids_configurados, validar_id
from importacao_core import ErroOperacional

WIDGET = "https://cdn.pluggy.ai/pluggy-connect/v2.10.0/pluggy-connect.js"
HTML = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Conectar Meu Pluggy · Gestão Sir Fisher</title>
<style>
body{font:17px/1.5 system-ui,sans-serif;background:#f2f6f6;color:#183c3c;margin:0;padding:24px}
main{max-width:650px;margin:7vh auto;background:white;padding:28px;border-radius:16px}
h1{font-size:28px;line-height:1.2}button{font:inherit;background:#006d68;color:white;border:0;border-radius:8px;padding:12px 20px;cursor:pointer}
button:disabled{opacity:.6;cursor:wait}#msg{white-space:pre-line}a{color:#006d68}
</style><main><h1>Conectar suas contas ao Gestão</h1>
<p>Entre na sua conta <strong>Meu Pluggy</strong> para compartilhar uma conta bancária que já esteja conectada no portal.</p>
<p>Se houver mais de um banco, repita a conexão para cada um.</p>
<button id="abrir">Conectar Meu Pluggy</button><p id="msg" role="status" aria-live="polite">Pronto para conectar.</p>
<p>Ao terminar, volte ao chat. Esta etapa salva a autorização; a importação será conferida antes de alterar o painel.</p>
</main><script src="__WIDGET__"></script><script>
const session=__SESSION__;
const button=document.getElementById('abrir'),msg=document.getElementById('msg');
async function enviar(path,data){
 const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Connect-Session':session},body:JSON.stringify(data)});
 const result=await r.json();if(!r.ok)throw new Error(result.error||'Não foi possível concluir.');return result;
}
button.addEventListener('click',async()=>{
 button.disabled=true;msg.textContent='Abrindo conexão segura…';
 try{
  if(typeof PluggyConnect!=='function')throw new Error('O componente da Pluggy não carregou. Confira sua conexão e recarregue a página.');
  const data=await enviar('/api/token',{});
  const widget=new PluggyConnect({connectToken:data.token,selectedConnectorId:data.connectorId,connectorIds:[data.connectorId],includeSandbox:false,
   onSuccess:async({item})=>{
    msg.textContent='Validando e salvando a conexão…';
    try{const saved=await enviar('/api/item',{itemId:item.id});msg.textContent=saved.message;}
    catch(e){msg.textContent=e.message+' Você pode tentar conectar novamente; a autorização existente será preservada.';}
    finally{button.disabled=false;}
   },
   onError:()=>{msg.textContent='A Pluggy não concluiu a conexão. Confira o aviso na janela e tente novamente.';button.disabled=false;},
   onClose:()=>{button.disabled=false;}
  });widget.init();
 }catch(e){msg.textContent=e.message;button.disabled=false;}
});
</script></html>"""


def salvar_item(identificador: str, cliente: Cliente) -> dict:
    from dotenv import dotenv_values, set_key

    identificador = validar_id(identificador)
    item = cliente.item(identificador)
    if item.get("id") != identificador:
        raise ErroOperacional("A conexão não foi confirmada nesta aplicação.")
    if (item.get("connector") or {}).get("isSandbox"):
        raise ErroOperacional("Conexão de teste recusada. Use o Meu Pluggy com suas contas reais.")
    caminho = RAIZ_PROJETO / ".env"
    atual = dotenv_values(caminho)
    lista = str(atual.get("PLUGGY_ITEM_IDS") or atual.get("PLUGGY_ITEM_ID") or "")
    itens = list(dict.fromkeys([x.strip() for x in lista.split(",") if x.strip()] + [identificador]))
    set_key(str(caminho), "PLUGGY_ITEM_IDS", ",".join(itens))
    return {"message": "Conexão autorizada e salva no ambiente local. Volte ao chat para conferir as contas e os lançamentos.",
            "conexoesSalvas": len(itens)}


class Servidor(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, porta: int, cliente: Cliente, conector: int):
        super().__init__(("127.0.0.1", porta), Handler)
        self.cliente = cliente
        self.conector = conector
        self.sessao = secrets.token_urlsafe(32)
        self.trava = threading.Lock()
        self.origem = f"http://127.0.0.1:{self.server_port}"


class Handler(BaseHTTPRequestHandler):
    server: Servidor

    def log_message(self, *args):
        pass  # Nunca registrar corpo, token, item ou parâmetros no terminal.

    def responder(self, status: int, dados: bytes, tipo="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(dados)

    def json(self, status: int, dados: dict):
        self.responder(status, json.dumps(dados, ensure_ascii=False).encode())

    def host_valido(self) -> bool:
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def do_GET(self):
        if not self.host_valido():
            self.json(403, {"error": "Acesso local inválido."})
        elif self.path == "/":
            pagina = HTML.replace("__WIDGET__", WIDGET).replace("__SESSION__", json.dumps(self.server.sessao))
            self.responder(200, pagina.encode(), "text/html; charset=utf-8")
        elif self.path == "/api/status":
            self.json(200, {"conexoesSalvas": len(ids_configurados())})
        else:
            self.json(404, {"error": "Página não encontrada."})

    def do_POST(self):
        autorizado = (self.host_valido()
                      and self.headers.get("Origin") == self.server.origem
                      and secrets.compare_digest(self.headers.get("X-Connect-Session", ""), self.server.sessao))
        if not autorizado:
            self.json(403, {"error": "Recarregue a página local para continuar."})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho < 2 or tamanho > 2048:
                raise ValueError
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            self.json(400, {"error": "Pedido inválido."})
            return
        try:
            with self.server.trava:
                if self.path == "/api/token":
                    self.json(200, {"token": self.server.cliente.token_conexao(), "connectorId": self.server.conector})
                elif self.path == "/api/item":
                    resultado = salvar_item(dados.get("itemId", ""), self.server.cliente)
                    # Atualiza apenas os IDs na memória; não altera outras variáveis.
                    from dotenv import dotenv_values
                    import os
                    os.environ["PLUGGY_ITEM_IDS"] = dotenv_values(RAIZ_PROJETO / ".env")["PLUGGY_ITEM_IDS"]
                    self.json(200, resultado)
                else:
                    self.json(404, {"error": "Operação não encontrada."})
        except ErroOperacional as exc:
            self.json(502, {"error": str(exc)})
        except (OSError, ValueError, TypeError):
            self.json(500, {"error": "Não foi possível salvar a conexão. Confira o arquivo local e tente novamente."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--porta", type=int, default=8766)
    parser.add_argument("--sem-abrir", action="store_true")
    op = parser.parse_args()
    carregar_env()
    cliente = Cliente()
    cliente.autenticar()
    conector = cliente.conector_meu_pluggy()
    with Servidor(op.porta, cliente, conector) as servidor:
        print(f"Conexão local pronta: {servidor.origem}", flush=True)
        if not op.sem_abrir:
            webbrowser.open(servidor.origem)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    try:
        main()
    except ErroOperacional as exc:
        print(f"ERRO: {exc}")
        raise SystemExit(1)
