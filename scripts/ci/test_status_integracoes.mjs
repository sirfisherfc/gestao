// Executa o JavaScript real da página Status com dados fictícios e sem rede.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const html=readFileSync(new URL('../../status.html',import.meta.url),'utf8');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{const auth=')[0];
const safeDom=readFileSync(new URL('../../assets/safe-dom.js',import.meta.url),'utf8');
const runUrl='https://github.com/exemplo/painel/actions/runs/123';
const stamp='2026-10-22T13:58:15.123456+00:00';
const fontes=['saipos_vendas','saipos_cancelamentos'];
const row=(fonte,dia,extra={})=>({fonte,dia_referencia:dia,executado_em:stamp,
  origem:'github',execucao_url:runUrl,situacao:'ok',stonecode:null,linhas_novas:0,...extra});
const semana=(extra={})=>Array.from({length:7},(_,i)=>fontes.map(f=>row(f,`2026-10-${15+i}`,{
  linhas_novas:i===6?(f==='saipos_vendas'?12:3):0,...extra}))).flat();

function tela(rows,error=null){
  const target={innerHTML:''},calls=[];
  class Clock extends Date{
    constructor(...args){super(...(args.length?args:['2026-10-22T18:00:00Z']));}
    static now(){return new Date('2026-10-22T18:00:00Z').getTime();}
  }
  const context=vm.createContext({Date:Clock,document:{getElementById:id=>id==='integracoes'?target:null},
    SirFisherSupabase:{from:name=>{
      calls.push(name);
      return {select:()=>({gte:()=>({order:()=>({limit:n=>{assert.equal(n,1000);return Promise.resolve({data:rows,error});}})})})};
    }}});
  context.window=context;
  vm.runInContext(safeDom,context);
  vm.runInContext(source,context);
  return {target,calls,group:input=>context.agruparExecucoesIntegracao(input),
    render:g=>context.renderExecucaoIntegracao(g),load:()=>context.loadIntegracoes(),
    pending:input=>context.pendenciasIntegracao(input)};
}

let cases=0;
{
  const raw=semana(),before=JSON.stringify(raw),t=tela(raw),g=t.group(raw);
  assert.equal(g.length,1); assert.equal(g[0].dias.length,7); assert.equal(g[0].itens.length,14);
  assert.equal(g[0].vendas_novas,12); assert.equal(g[0].para_justificar,3);
  const result=t.render(g[0]);
  assert.match(result,/7 dias/); assert.match(result,/12 vendas novas/); assert.match(result,/3 para justificar/);
  assert.equal((result.match(/ver no GitHub/g)||[]).length,1);
  assert.match(result,/<summary>Ver detalhes por dia \(14 registros\)<\/summary>/);
  assert.doesNotMatch(result,/<details[^>]*\bopen\b/);
  assert.equal(JSON.stringify(raw),before);cases++;
}
{
  const raw=semana();raw[1]={...raw[1],situacao:'erro',linhas_novas:null,mensagem:'Falha <img src=x onerror=alert(1)>'};
  const t=tela(raw),g=t.group(raw)[0]; assert.equal(g.situacao,'erro'); assert.equal(g.dias_erro,1);
  assert.equal(t.pending(raw).filter(r=>r.situacao==='erro').length,1);
  const markup=t.render(g);assert.match(markup,/status bad/);assert.match(markup,/1 dia com erro/);
  assert.match(markup,/&lt;img/);assert.doesNotMatch(markup,/<img/);cases++;
}
{
  const raw=semana({situacao:'sem_movimento',linhas_novas:0}),t=tela(raw),g=t.group(raw)[0];
  assert.equal(g.situacao,'sem_movimento');assert.match(t.render(g),/Sem movimento/);cases++;
}
{
  const t=tela([]);
  // Mesmo link, outra transação: não mesclar reruns nem perder microssegundos.
  assert.equal(t.group([...semana(),...semana({executado_em:'2026-10-22T13:58:15.123457+00:00'})]).length,2);
  assert.equal(t.group([...semana(),...semana({execucao_url:runUrl+'4'})]).length,2);cases++;
}
{
  const t=tela([]);
  assert.equal(t.group([...semana({origem:'manual',execucao_url:null}),...semana({origem:'manual',execucao_url:null,executado_em:'2026-10-22T14:00:00Z'})]).length,2);
  assert.equal(t.group([row('saipos_vendas','2026-10-21',{executado_em:null,id:'a'}),row('saipos_cancelamentos','2026-10-21',{executado_em:null,id:'b'})]).length,2);cases++;
}
{
  const t=tela([]),raw=[...semana(),row('stone_recebiveis','2026-10-21')];
  const g=t.group(raw);assert.equal(g.length,2);assert.equal(g[1].saipos,false);
  assert.equal(t.group([row('saipos_outra_fonte','2026-10-21'),row('saipos_outra_fonte','2026-10-20')]).length,2);cases++;
}
{
  const raw=[...semana(),...semana({executado_em:'2026-10-21T13:00:00Z',execucao_url:runUrl+'4'}),
    row('Extrato de exemplo','2026-10-21',{execucao_url:null})];
  const t=tela(raw);await t.load();assert.match(t.target.innerHTML,/Extrato de exemplo/);
  assert.equal((t.target.innerHTML.match(/<details /g)||[]).length,2);
  assert.deepEqual(t.calls,['app_integracao_execucao']);cases++;
}
{
  const raw=semana({linhas_novas:null}),t=tela(raw),g=t.group(raw)[0];
  assert.equal(g.vendas_novas,null);assert.equal(g.para_justificar,null);
  assert.match(t.render(g),/— vendas novas/);cases++;
}
{
  const t=tela([]),g=t.group([row('saipos_vendas','2026-10-15'),row('saipos_vendas','2026-10-21')])[0];
  assert.equal(g.dias.length,2);assert.match(t.render(g),/2 dias/);cases++;
}
{
  const raw=Array.from({length:25},(_,i)=>row('Extrato '+i,'2026-10-21',{execucao_url:null}));
  const t=tela(raw);await t.load();assert.match(t.target.innerHTML,/>Extrato 19</);
  assert.doesNotMatch(t.target.innerHTML,/>Extrato 20</);cases++;
}
{
  const t=tela([], {message:'sem acesso'});await t.load();
  assert.match(t.target.innerHTML,/Não foi possível carregar o registro/);cases++;
}
console.log(`STATUS_INTEGRACOES_TESTS_OK cases=${cases} grouped_days=7 records=14 network=0`);
