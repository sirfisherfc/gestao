import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source=readFileSync(new URL('../../supabase/functions/stone-webhook/index.ts',import.meta.url),'utf8');
const token='test-token-with-at-least-24-characters';
const env={STONE_WEBHOOK_TOKEN:token,STONE_PIX_DOCUMENT:'12345678000199',SUPABASE_URL:'https://portal.supabase.co',SUPABASE_SERVICE_ROLE_KEY:'fake-service-only'};
const notice={type:'pix',document:'12345678000199',referenceDate:'2026-10-21',url:'https://files.example.com/arquivo.csv?private=fake'};

function fixture({downloadStatus=200,insertStatus=201}={}){
  let handler;
  const calls=[],background=[];
  const fetch=async(url,options={})=>{
    calls.push({url,options});
    if(url.startsWith(env.SUPABASE_URL)){
      if(options.method==='POST')return new Response(JSON.stringify([{id:'fake-id'}]),{status:insertStatus});
      return new Response(null,{status:204});
    }
    return new Response('id;amount\nevent;1000\n',{status:downloadStatus});
  };
  vm.runInNewContext(source,{Deno:{env:{get:n=>env[n]},serve:fn=>{handler=fn;}},
    URL,Request,Response,AbortSignal,fetch,EdgeRuntime:{waitUntil:p=>background.push(p)}});
  return {calls,background,request:async(body,headers={'x-sirfisher-stone-token':token},query='')=>
    handler(new Request('https://portal.supabase.co/functions/v1/stone-webhook'+query,{method:'POST',headers,body:typeof body==='string'?body:JSON.stringify(body)}))};
}

let passed=0;
{
  const f=fixture(); assert.equal((await f.request({type:'validation_notification'},{},'?token='+token)).status,200);
  assert.equal(f.calls.length,0); passed++;
}
for(const headers of [{},{'x-sirfisher-stone-token':'wrong'}]){
  const f=fixture(); assert.equal((await f.request({type:'validation_notification'},headers)).status,401);
  assert.equal(f.calls.length,0); passed++;
}
{
  const f=fixture(); assert.equal((await f.request({type:'validation_notification'})).status,200);
  assert.equal(f.calls.length,0); passed++;
}
for(const body of ['{invalid',[],null,{...notice,document:'99999999000199'},{...notice,type:'other'},
  {...notice,referenceDate:'2026-02-30'},{...notice,url:'http://files.example.com/x'},
  {...notice,url:'https://127.0.0.1/x'},{...notice,url:'https://portal.supabase.co/rest/v1/private'}]){
  const f=fixture(); assert.ok((await f.request(body)).status>=400); assert.equal(f.calls.length,0); passed++;
}
{
  const f=fixture(); assert.equal((await f.request(notice)).status,200);
  await Promise.all(f.background);
  assert.equal(f.calls.length,3);
  const [insert,download,update]=f.calls;
  assert.equal(JSON.parse(insert.options.body).data_referencia,'2026-10-21');
  assert.equal(insert.options.headers.apikey,env.SUPABASE_SERVICE_ROLE_KEY);
  assert.equal(download.url,notice.url); assert.equal(download.options.headers,undefined);
  assert.equal(download.options.redirect,'error');
  assert.ok(JSON.parse(update.options.body).conteudo.startsWith('id;amount'));
  passed++;
}
{
  const f=fixture({downloadStatus:403}); assert.equal((await f.request(notice)).status,200);
  await Promise.all(f.background);
  assert.match(JSON.parse(f.calls.at(-1).options.body).erro,/HTTP 403/);
  assert.equal(f.calls.filter(c=>c.url===notice.url).length,1); passed++;
}
{
  const f=fixture({insertStatus:500}); assert.equal((await f.request(notice)).status,500);
  assert.equal(f.background.length,0); assert.equal(f.calls.length,1); passed++;
}
console.log(`STONE_WEBHOOK_TESTS_OK cases=${passed} network=0`);
