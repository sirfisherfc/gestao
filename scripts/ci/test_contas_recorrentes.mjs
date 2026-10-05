// Casos sinteticos de pendencias por competencia e baixas fora do mes da tela.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import vm from 'node:vm';

const html=readFileSync(new URL('../../contas_recorrentes.html',import.meta.url),'utf8');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{AUTH=')[0];
const conta=(mes,extra={})=>({conta_id:1,nome:'Conta de teste',dia_vencimento:10,
  categoria:'outros',tipo:'despesa',unidade:'TESTE',ativa:true,incluir_totais:true,
  competencia:mes,media_3:100,situacao:null,pagamento_id:null,...extra});

function tela(rows=[],pending=[],rpc=async()=>({data:[],error:null})){
  const elements=new Map(),calls=[];
  class DateFixa extends Date {constructor(...args){super(...(args.length?args:['2026-10-05T12:00:00-03:00']));}}
  class Chart{constructor(){}destroy(){}}
  const c=vm.createContext({Date:DateFixa,Chart,rows,pending,
    SirFisherSupabase:{rpc:(name,args)=>{calls.push({name,args});return rpc(name,args);}},
    SirFisherDOM:{escapeHTML:s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;')},
    SirFisherApp:{number:(_key,value)=>value,settings:()=>({unidadeCodigo:'TESTE'})},
    confirm:()=>true,setTimeout(){},document:{getElementById(id){
      if(!elements.has(id))elements.set(id,{id,innerHTML:'',classList:{remove(){}},addEventListener(){},querySelectorAll:()=>[]});
      return elements.get(id);
    }}});
  c.window=c;
  vm.runInContext(source,c);
  vm.runInContext("competencia='2026-10';ROWS=rows;PENDING=pending;",c);
  return {c,calls,elements,run:code=>vm.runInContext(code,c)};
}

test('setembro continua vencido em outubro com competencia e identidade proprias',()=>{
  const t=tela([conta('2026-10-01')],[conta('2026-09-01')]);
  assert.equal(t.run('estado(PENDING[0]).rotulo'),'Vencida');
  assert.equal(t.run('estado(ROWS[0]).rotulo'),'Vence em 5d');
  const markup=t.run('listaHTML(contasExibidas())');
  assert.match(markup,/Pendências de meses anteriores/);
  assert.match(markup,/Set 2026 · 10\/09\/2026/);
  assert.match(markup,/data-key="1:2026-09-01"/);
  assert.match(markup,/data-key="1:2026-10-01"/);
});

test('totais somam pendencias anteriores uma vez e separam pagamentos da competencia',()=>{
  const t=tela([conta('2026-10-01',{situacao:'pago',valor:200}),
    conta('2026-10-01',{conta_id:2}),conta('2026-10-01',{conta_id:3,situacao:'sem_movimento'}),
    conta('2026-10-01',{conta_id:4,tipo:'rotina'}),conta('2026-10-01',{conta_id:5,incluir_totais:false})],
    [conta('2026-08-01'),conta('2026-09-01'),conta('2026-09-01',{conta_id:4,tipo:'rotina'})]);
  const sum=t.run('resumo()');
  assert.equal(sum.pagos,200);assert.equal(sum.pendenteMes,100);
  assert.equal(sum.pendenteAnterior,200);assert.equal(sum.pendentes,300);
  assert.equal(sum.previsto,500);assert.equal(sum.vencidas,2);
});

test('pendencia sem media segue visivel e aparece na contagem de valores desconhecidos',()=>{
  const t=tela([],[conta('2026-09-01',{media_3:null})]);
  assert.equal(t.run('resumo().semEstimativa'),1);
  assert.match(t.run('linhaConta(PENDING[0])'),/<strong>—<\/strong>/);
  assert.match(t.run('contagemHTML(contasExibidas())'),/1 de meses anteriores/);
});

test('busca encontra todas as competencias da mesma conta e atualiza a contagem',()=>{
  const t=tela([conta('2026-10-01')],[conta('2026-09-01')]);
  t.run("busca='conta de teste';renderLista()");
  assert.match(t.elements.get('contagemContas').innerHTML,/2 ocorrências/);
  assert.match(t.elements.get('listaContas').innerHTML,/1:2026-09-01/);
  t.run("busca='inexistente';renderLista()");
  assert.match(t.elements.get('contagemContas').innerHTML,/0 ocorrências/);
});

test('vencimento respeita fevereiro bissexto e o dia 31 de meses curtos',()=>{
  const t=tela();
  t.c.fev=conta('2024-02-01',{dia_vencimento:31});
  t.c.abril=conta('2026-04-01',{dia_vencimento:31});
  assert.equal(t.run('vencimentoISO(fev)'),'2024-02-29');
  assert.equal(t.run('vencimentoISO(abril)'),'2026-04-30');
});

test('pagamento em outubro baixa setembro sem sobrescrever outubro',async()=>{
  const t=tela([conta('2026-10-01')],[conta('2026-09-01')]);
  t.c.controls={querySelector:s=>({value:{'.pay-value':'100','.pay-bank':'Banco Teste','.pay-date':'2026-10-05'}[s]}),querySelectorAll:()=>[]};
  t.run('load=()=>{}');
  await t.run('salvarPagamento(controls,PENDING[0])');
  assert.equal(t.calls[0].name,'salvar_pagamento_recorrente');
  assert.equal(t.calls[0].args.p_competencia,'2026-09-01');
  assert.equal(t.calls[0].args.p_data_pagamento,'2026-10-05');
});

test('sem cobranca e limpeza usam a competencia da linha',async()=>{
  const t=tela([],[conta('2026-09-01')]);t.run('load=()=>{}');
  await t.run('salvarSemMovimento(PENDING[0])');
  await t.run('limparPagamento(PENDING[0])');
  assert.equal(t.calls[0].args.p_sem_movimento,true);
  assert.equal(t.calls[0].args.p_competencia,'2026-09-01');
  assert.equal(t.calls[1].args.p_competencia,'2026-09-01');
});

test('eventos distinguem duas competencias com o mesmo conta_id',async()=>{
  const t=tela([conta('2026-10-01')],[conta('2026-09-01')]);
  const handlers=[];
  t.c.list={querySelectorAll:()=>['2026-09-01','2026-10-01'].map(mes=>({
    dataset:{key:'1:'+mes},querySelector:s=>s==='.no-charge'?{addEventListener:(_event,fn)=>handlers.push(fn)}:s==='.edit-account'?{addEventListener(){}}:null
  }))};
  t.run('load=()=>{};bindContas(list)');
  for(const handler of handlers)await handler();
  assert.deepEqual(t.calls.map(c=>c.args.p_competencia),['2026-09-01','2026-10-01']);
});

test('consulta pagina todas as pendencias e preserva erros sem declarar lista vazia',async()=>{
  let pagina=0;
  const t=tela([],[],()=>({range:async()=>({data:pagina++===0?Array(500).fill({}):[{}],error:null})}));
  const result=await t.run("carregarPendencias('2026-10-01')");
  assert.equal(result.data.length,501);
  assert.equal(t.calls.length,2);
  const falha=tela([],[],()=>({range:async()=>({error:{message:'Falha de teste'}})}));
  assert.equal((await falha.run("carregarPendencias('2026-10-01')")).error.message,'Falha de teste');
});

test('baixas e rotina concluida nao aparecem como vencidas',()=>{
  const t=tela([conta('2026-09-01',{situacao:'pago',valor:100}),conta('2026-09-01',{conta_id:2,situacao:'sem_movimento',tipo:'rotina'})]);
  assert.equal(t.run('estado(ROWS[0]).classe'),'paid');
  assert.equal(t.run('estado(ROWS[1]).rotulo'),'Concluída');
});

test('data operacional usa Fortaleza mesmo quando UTC ja virou o dia',()=>{
  const t=tela();
  t.c.Date=class extends Date {constructor(...args){super(...(args.length?args:['2026-10-01T02:00:00Z']));}};
  assert.equal(t.run('hojeISO()'),'2026-09-30');
  assert.equal(t.run('mesAtual()'),'2026-09');
});

test('carga nao copia a baixa atual para pendencias anteriores',async()=>{
  const t=tela([],[],name=>name==='listar_pendencias_recorrentes'
    ?{range:async()=>({data:[{conta_id:1,competencia:'2026-09-01',media_3:100}],error:null})}
    :Promise.resolve({data:[conta('2026-10-01',{situacao:'pago',valor:200,pagamento_id:88,atualizado_em:'2026-10-05'})],error:null}));
  t.c.SirFisherSupabase.from=()=>{const q={select:()=>q,gte:()=>q,order:()=>Promise.resolve({data:[],error:null})};return q;};
  t.run('render=()=>{}');await t.run('load()');
  assert.equal(t.run('ROWS[0].situacao'),'pago');
  assert.equal(t.run('PENDING[0].situacao'),null);
  assert.equal(t.run('PENDING[0].pagamento_id'),null);
  assert.equal(t.run('PENDING[0].atualizado_em'),null);
  assert.equal(t.run('resumo().pendenteAnterior'),100);
});

test('falha na consulta de pendencias bloqueia totais incompletos',async()=>{
  const t=tela([],[],name=>name==='listar_pendencias_recorrentes'
    ?{range:async()=>({data:null,error:{message:'Falha de teste'}})}
    :Promise.resolve({data:[],error:null}));
  t.c.SirFisherSupabase.from=()=>{const q={select:()=>q,gte:()=>q,order:()=>Promise.resolve({data:[],error:null})};return q;};
  await t.run('load()');
  assert.match(t.elements.get('main').innerHTML,/Não foi possível carregar/);
});
