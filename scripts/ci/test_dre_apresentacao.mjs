// Casos sinteticos: ausencia nao e custo zero; valores validos sao preservados.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import vm from 'node:vm';

const read=name=>readFileSync(new URL('../../'+name,import.meta.url),'utf8');
const html=read('dre.html');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{const ctx=')[0];
const completo=()=>({mes:'2026-09-01',ano_mes:'2026-09',receita:100,cmv:-30,
  cmv_perc:30,pessoal:-25,pessoal_perc:25,impostos:-10,outras_variaveis:0,margem_contribuicao:60,
  mc_perc:60,infraestrutura:-10,marketing:-5,resultado_operacional:20,
  margem_op_perc:20,nao_operacional:-2,contabil:0,capex:-3,outros:-1,
  nao_categorizado:0,resultado_liquido:14,margem_liq_perc:14});

function tela(row=completo(),projetado=false){
  const elements=new Map(),charts=[];
  class Chart{static defaults={font:{}};constructor(el,config){charts.push({id:el.id,...config});}destroy(){}}
  const c=vm.createContext({Chart,fixtures:[row],SirFisherSupabase:{},
    SirFisherDOM:{escapeHTML:s=>String(s??'')},SirFisherApp:{number:(_key,value)=>value},
    addEventListener(){},
    document:{addEventListener(){},getElementById(id){
      if(!elements.has(id))elements.set(id,{id,style:{},parentElement:{},addEventListener(){}});
      return elements.get(id);
    }}});
  c.window=c;
  vm.runInContext(read('assets/dashboard-utils.js'),c);
  vm.runInContext(source,c);
  vm.runInContext(`ROWS=fixtures;RESUMO=[{ano_mes:'2026-09',faturamento:100,faturamento_proj:${projetado?200:100}}];
    DESP_DIRETA=[{dia:'2026-09-20',valor:20}];DESP_FIXA=[{dia:'2026-09-20',valor:30}];
    PROJECAO_ESTADO='disponivel';`,c);
  return {run:code=>vm.runInContext(code,c),render:()=>vm.runInContext("renderMes('2026-09')",c),
    markup:id=>elements.get(id)?.innerHTML||'',parent:id=>elements.get(id)?.parentElement,
    charts};
}

test('valores completos preservam percentuais, tabela e cascata',()=>{
  const t=tela();t.render();
  assert.match(t.markup('bench'),/55,0%/);
  assert.match(t.markup('dreTbl'),/Total gerencial.*?R\$ 14,00/);
  const wf=t.charts.find(c=>c.id==='wf');
  assert.equal(wf.data.datasets[0].data.at(-1)[1],14);
  assert.doesNotMatch(t.markup('bench'),/Indisponível/);
});

for(const ausente of [null,undefined,'','NaN','Infinity'])test(`custo ausente ou invalido indisponibiliza Prime Cost (${String(ausente)})`,()=>{
  const t=tela({...completo(),cmv_perc:ausente});t.render();
  const bench=t.markup('bench');
  assert.equal((bench.match(/Indisponível/g)||[]).length,2);
  assert.equal((bench.match(/class="fill"/g)||[]).length,1);
  assert.doesNotMatch(bench,/55,0%/);
});

test('custo bruto ausente nao e suprido por percentual isolado',()=>{
  const t=tela({...completo(),cmv:null});t.render();
  assert.equal((t.markup('bench').match(/Indisponível/g)||[]).length,2);
  assert.match(t.markup('dreTbl'),/Insumos pagos \(despesa direta\)<\/td><td class="r">—/);
  assert.equal(t.charts.some(c=>c.id==='wf'),false);
  assert.match(t.parent('wf').innerHTML,/Cascata indisponível/);
});

test('zero informado continua zero e participa do indicador',()=>{
  const t=tela({...completo(),cmv:0,cmv_perc:0});t.render();
  assert.match(t.markup('bench'),/>0,0%/);
  assert.match(t.markup('bench'),/Prime Cost \(aprox\.\)[\s\S]*?>25,0%/);
  assert.doesNotMatch(t.markup('bench'),/Indisponível/);
});

for(const receita of [null,0,-10])test(`receita invalida para denominador deixa custos indisponiveis (${receita})`,()=>{
  const t=tela({...completo(),receita});t.render();
  assert.equal((t.markup('bench').match(/Indisponível/g)||[]).length,3);
  assert.doesNotMatch(t.markup('bench'),/class="fill"/);
});

test('projecao preserva calculo com componentes completos',()=>{
  const t=tela(completo(),true);t.render();
  const markup=t.markup('main');
  assert.match(markup,/Margem de contribuição projetada[\s\S]*?title="Valor exato: R\$ 140,00"/);
  assert.match(markup,/Operacional gerencial projetado[\s\S]*?title="Valor exato: R\$ 70,00"/);
  assert.match(markup,/Total gerencial projetado[\s\S]*?title="Valor exato: R\$ 64,00"/);
});

test('componente ausente nao gera total projetado parcial',()=>{
  const t=tela({...completo(),outros:null},true);t.render();
  const projected=t.markup('main').split('Total gerencial projetado')[1].split('</div></div>')[0];
  assert.match(projected,/class="value"[^>]*>—/);
  assert.doesNotMatch(projected,/Valor exato:/);
});

test('receita ausente propaga indisponibilidade para projecoes',()=>{
  const t=tela({...completo(),receita:null},true);t.render();
  assert.match(t.markup('main'),/Projeção operacional indisponível/);
  assert.equal(t.run('corResultado(null)'),t.run('C.muted'));
});

test('historico nao liga artificialmente meses sem margem',()=>{
  const t=tela();t.run("ROWS=[fixtures[0],{mes:'2026-10-01',mc_perc:null,margem_op_perc:'NaN',margem_liq_perc:''}];drawMargens();");
  for(const ds of t.charts[0].data.datasets){assert.equal(ds.data[1],null);assert.equal(ds.spanGaps,false);}
});

test('sem tendencia nao declara mes encerrado ou fontes completas',()=>{
  const t=tela();t.render();
  assert.doesNotMatch(t.markup('main'),/mês encerrado|Valores finais do período/);
  assert.match(t.markup('main'),/completude das fontes não está confirmada/);
  assert.doesNotMatch(html,/Regime de competência/);
});

function resumo(rows){
  const elements=new Map();
  class Chart{static defaults={font:{}};destroy(){}}
  const c=vm.createContext({Chart,fixtures:rows,addEventListener(){},
    SirFisherSupabase:{},SirFisherDOM:{escapeHTML:s=>String(s??'')},
    SirFisherApp:{number:(_key,value)=>value},
    document:{addEventListener(){},getElementById(id){
      if(!elements.has(id))elements.set(id,{id,style:{},addEventListener(){}});
      return elements.get(id);
    }}});
  c.window=c;
  vm.runInContext(read('assets/dashboard-utils.js'),c);
  const indexSource=read('index.html').match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{')[0];
  vm.runInContext(indexSource,c);
  vm.runInContext("ROWS=fixtures;LOAD_STAGE='concluido';drawBullet=()=>{};drawDia=async()=>{};drawBars=()=>{};renderMes('2026-09');",c);
  return elements.get('main').innerHTML;
}

test('Resumo nao calcula variacao contra custo anterior ausente',()=>{
  const markup=resumo([
    {mes:'2026-08-01',ano_mes:'2026-08',receita:100,cmv:null,faturamento:100,faturamento_proj:100},
    {mes:'2026-09-01',ano_mes:'2026-09',receita:100,cmv:30,faturamento:100,faturamento_proj:100},
  ]).split('Receita após desp. direta')[1].split('Saldo em caixa')[0];
  assert.match(markup,/vs mês anterior: —/);
  assert.doesNotMatch(markup,/<div class="sub (up|down)">/);
});

test('Resumo trata espacos como ausencia e mantem percentual zero valido',()=>{
  const markup=resumo([{mes:'2026-09-01',ano_mes:'2026-09',receita:100,cmv:0,
    faturamento:100,faturamento_proj:100,cmv_perc:'  ',pessoal_perc:0}]);
  const insumos=markup.split('class="txt">Insumos pagos')[1].split('class="txt">Pessoal registrado')[0];
  assert.match(insumos,/class="value"[^>]*>—/);
  const pessoal=markup.split('class="txt">Pessoal registrado')[1];
  assert.match(pessoal,/class="value"[^>]*>0,0%/);
});

test('Resumo reconcilia resultado projetado com outros e coincide com DRE',()=>{
  const elements=new Map();
  class Chart{static defaults={font:{}};destroy(){}}
  const c=vm.createContext({Chart,fixtures:[{mes:'2026-09-01',ano_mes:'2026-09',receita:100,faturamento:100,faturamento_proj:200}],
    addEventListener(){},SirFisherSupabase:{},SirFisherDOM:{escapeHTML:s=>String(s??'')},
    SirFisherApp:{number:(_key,value)=>value},
    document:{addEventListener(){},getElementById(id){
      if(!elements.has(id))elements.set(id,{id,style:{},addEventListener(){}});
      return elements.get(id);
    }}});
  c.window=c;
  vm.runInContext(read('assets/dashboard-utils.js'),c);
  const indexSource=read('index.html').match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{')[0];
  vm.runInContext(indexSource,c);
  vm.runInContext(`ROWS=fixtures;DRE_ROWS=[${JSON.stringify(completo())}];
    DETAIL_OK.dre=true;DETAIL_OK.fixa=true;DETAIL_OK.direta=true;
    DESP_DIRETA=[{dia:'2026-09-20',valor:20}];DESP_FIXA=[{dia:'2026-09-20',valor:30}];
    LOAD_STAGE='concluido';drawBullet=()=>{};drawDia=async()=>{};drawBars=()=>{};renderMes('2026-09');`,c);
  const markup=elements.get('main').innerHTML;
  assert.match(markup,/Total gerencial \(tend\.\)[\s\S]*?class="value"[^>]*>R\$ 64<\/div>/);
});

test('Cascata DRE valida integridade dos subtotais mutuamente exclusivos',()=>{
  const row = completo();
  assert.equal(row.margem_contribuicao, row.receita + row.cmv + row.impostos + row.outras_variaveis);
  assert.equal(row.resultado_operacional, row.margem_contribuicao + row.pessoal + row.infraestrutura + row.marketing);
  assert.equal(row.resultado_liquido, row.resultado_operacional + row.nao_operacional + row.contabil + row.capex + row.outros + row.nao_categorizado);
});

test('Cascata DRE acomoda grupo residual em outros sem alterar margem de contribuicao',()=>{
  const t = tela({...completo(), outros: -15, resultado_liquido: 0});
  t.render();
  assert.match(t.markup('dreTbl'), /Outros grupos<\/td><td class="r">R\$ -15,00/);
  assert.match(t.markup('dreTbl'), /Total gerencial<\/td><td class="r">R\$ 0,00/);
  assert.match(t.markup('dreTbl'), /Margem de contribuição<\/td><td class="r">R\$ 60,00/);
});

test('Cascata DRE exibe outras despesas variáveis quando a coluna está presente',()=>{
  const t=tela({...completo(),outras_variaveis:-5,margem_contribuicao:55,
    resultado_operacional:15,resultado_liquido:9});
  t.render();
  assert.match(t.markup('dreTbl'),/Outras despesas variáveis<\/td><td class="r">R\$ -5,00/);
  const waterfall=t.charts.find(chart=>chart.id==='wf');
  assert.ok(waterfall.data.labels.includes('Outras variáveis'));
});

function resilientFetch(){
  const client={};
  const context=vm.createContext({
    supabase:{createClient:()=>client},AbortController,setTimeout,clearTimeout
  });
  context.window=context;
  vm.runInContext(read('assets/supabase-client.js'),context);
  return client.resilientFetch;
}

test('resilientFetch usa o status do envelope e não retenta erros 4xx definitivos',async()=>{
  const resilient=resilientFetch();
  for(const status of [400,401,403,422]){
    let attempts=0;
    const response={status,data:null,error:{message:'erro definitivo'}};
    const result=await resilient(()=>{attempts++;return response;},{
      maxAttempts:3,baseDelayMs:0,jitterMs:0,attemptTimeoutMs:100,budgetMs:500
    });
    assert.equal(result,response);
    assert.equal(attempts,1,`status ${status} foi repetido`);
  }
});

test('resilientFetch retenta apenas status HTTP transitórios previstos',async()=>{
  const resilient=resilientFetch();
  for(const status of [408,429,503]){
    let attempts=0;
    const result=await resilient(()=>{
      attempts++;
      return attempts===1?{status,data:null,error:{message:'temporário'}}:{status:200,data:['ok'],error:null};
    },{maxAttempts:3,baseDelayMs:0,jitterMs:0,attemptTimeoutMs:100,budgetMs:500});
    assert.deepEqual(result.data,['ok']);
    assert.equal(attempts,2,`status ${status} não foi repetido`);
  }
});

test('resilientFetch retenta falha de conectividade sem status HTTP',async()=>{
  const resilient=resilientFetch();
  let attempts=0;
  const result=await resilient(()=>{
    attempts++;
    return attempts===1
      ? {status:0,data:null,error:{code:'ECONNRESET',message:'conexão interrompida'}}
      : {status:200,data:['ok'],error:null};
  },{maxAttempts:3,baseDelayMs:0,jitterMs:0,attemptTimeoutMs:100,budgetMs:500});
  assert.deepEqual(result.data,['ok']);
  assert.equal(attempts,2);
});

test('resilientFetch distingue statement timeout de cancelamento no código 57014',async()=>{
  const resilient=resilientFetch();
  let timeoutAttempts=0;
  const recovered=await resilient(()=>{
    timeoutAttempts++;
    return timeoutAttempts===1
      ? {status:500,data:null,error:{code:'57014',message:'canceling statement due to statement timeout'}}
      : {status:200,data:['ok'],error:null};
  },{maxAttempts:3,baseDelayMs:0,jitterMs:0,attemptTimeoutMs:100,budgetMs:500});
  assert.deepEqual(recovered.data,['ok']);
  assert.equal(timeoutAttempts,2);

  let cancelledAttempts=0;
  const cancelled={status:500,data:null,error:{code:'57014',message:'canceling statement due to user request'}};
  assert.equal(await resilient(()=>{cancelledAttempts++;return cancelled;},{
    maxAttempts:3,baseDelayMs:0,jitterMs:0,attemptTimeoutMs:100,budgetMs:500
  }),cancelled);
  assert.equal(cancelledAttempts,1);
});

test('resilientFetch cancela o backoff imediatamente quando o chamador aborta',async()=>{
  const resilient=resilientFetch();
  const controller=new AbortController();
  let attempts=0;
  const pending=resilient(()=>{
    attempts++;
    return {status:503,data:null,error:{message:'temporário'}};
  },{signal:controller.signal,maxAttempts:3,baseDelayMs:1000,jitterMs:0,attemptTimeoutMs:100,budgetMs:5000});
  setTimeout(()=>controller.abort(),5);
  await assert.rejects(pending,error=>error?.name==='AbortError');
  assert.equal(attempts,1);
});

test('resilientFetch aplica timeout por tentativa e entrega o sinal ao fetcher',async()=>{
  const resilient=resilientFetch();
  const signals=[];
  const pending=resilient(signal=>new Promise((resolve,reject)=>{
    signals.push(signal);
    signal.addEventListener('abort',()=>{
      const error=new Error('abortado pelo timeout');
      error.name='AbortError';
      reject(error);
    },{once:true});
  }),{maxAttempts:2,baseDelayMs:0,jitterMs:0,attemptTimeoutMs:10,budgetMs:100});
  await assert.rejects(pending,error=>error?.code==='RESILIENT_TIMEOUT');
  assert.equal(signals.length,2);
  assert.ok(signals.every(signal=>signal.aborted));
});

function dreAssincrona(plan){
  const elements=new Map(),calls=[];
  class Chart{static defaults={font:{}};constructor(){}destroy(){}}
  const element=id=>{
    if(!elements.has(id))elements.set(id,{id,style:{},parentElement:{},value:'',innerHTML:'',textContent:'',addEventListener(){}});
    return elements.get(id);
  };
  const sb={
    resilientFetch:(fetcher,options)=>fetcher(options.signal),
    from(table){
      const builder={
        select(){return this;},order(){return this;},limit(){return this;},
        abortSignal(signal){calls.push({table,signal});return this;},
        then(resolve,reject){return Promise.resolve(plan(table)).then(resolve,reject);}
      };
      return builder;
    }
  };
  const context=vm.createContext({
    Chart,SirFisherSupabase:sb,AbortController,
    SirFisherDOM:{escapeHTML:value=>String(value??'')},
    SirFisherApp:{number:(_key,value)=>value},
    console:{warn(){}},addEventListener(){},
    document:{documentElement:{clientWidth:1024},addEventListener(){},getElementById:element}
  });
  context.window=context;
  vm.runInContext(read('assets/dashboard-utils.js'),context);
  vm.runInContext(source,context);
  return {
    context,calls,element,
    main:()=>vm.runInContext('main()',context),
    run:code=>vm.runInContext(code,context),
    markup:()=>element('main').innerHTML
  };
}

const resposta=data=>({status:200,data,error:null});
const planoCompleto=table=>({
  app_painel_dre_cascata:resposta([completo()]),
  app_painel_resumo_mensal:resposta([{ano_mes:'2026-09',faturamento:100,faturamento_proj:200}]),
  app_projecao_despesa_fixa:resposta([{dia:'2026-09-20',valor:30}]),
  app_projecao_despesa_direta:resposta([{dia:'2026-09-20',valor:20}]),
  app_painel_ultima_carga:resposta([{ultima:'2026-09-06T12:00:00Z'}]),
  app_painel_cargas:resposta([])
})[table];

test('falha de uma fonte mantém realizado e não exibe projeção parcial',async()=>{
  const t=dreAssincrona(table=>table==='app_projecao_despesa_fixa'
    ? {status:503,data:null,error:{message:'indisponível'}}
    : planoCompleto(table));
  t.run("DESP_FIXA=[{dia:'2026-08-20',valor:999}]");
  await t.main();
  const markup=t.markup();
  assert.match(markup,/Receita financeira registrada[\s\S]*?Valor exato: R\$ 100,00/);
  assert.match(markup,/Projeção de fechamento indisponível/);
  assert.match(markup,/nenhum total projetado parcial é exibido/);
  assert.doesNotMatch(markup,/Margem de contribuição projetada/);
  assert.equal(t.run('DESP_FIXA[0].valor'),999);
});

test('realizado aparece antes de uma fonte auxiliar lenta',async()=>{
  let concluirFixa;
  const fixaPendente=new Promise(resolve=>{concluirFixa=resolve;});
  const t=dreAssincrona(table=>table==='app_projecao_despesa_fixa'?fixaPendente:planoCompleto(table));
  const carregamento=t.main();
  await new Promise(resolve=>setImmediate(resolve));
  assert.match(t.markup(),/Receita financeira registrada[\s\S]*?Valor exato: R\$ 100,00/);
  assert.match(t.markup(),/Projeção de fechamento em carregamento/);
  assert.doesNotMatch(t.markup(),/Margem de contribuição projetada/);
  concluirFixa(resposta([{dia:'2026-09-20',valor:30}]));
  await carregamento;
  assert.match(t.markup(),/Margem de contribuição projetada/);
});

test('todas as queries da DRE recebem AbortSignal e a recarga cancela as anteriores',async()=>{
  const t=dreAssincrona(planoCompleto);
  await t.main();
  const firstSignals=new Map(t.calls.map(call=>[call.table,call.signal]));
  for(const table of ['app_painel_dre_cascata','app_painel_resumo_mensal','app_projecao_despesa_fixa','app_projecao_despesa_direta']){
    assert.ok(firstSignals.get(table),`${table} não recebeu sinal`);
    assert.equal(firstSignals.get(table).aborted,false);
  }
  await t.main();
  for(const signal of firstSignals.values())assert.equal(signal.aborted,true);
});

test('falha da recarga principal preserva a última DRE confirmada com aviso',async()=>{
  let falhar=false;
  const t=dreAssincrona(table=>falhar&&table==='app_painel_dre_cascata'
    ? {status:503,data:null,error:{message:'indisponível'}}
    : planoCompleto(table));
  await t.main();
  assert.match(t.markup(),/Total gerencial registrado[\s\S]*?Valor exato: R\$ 14,00/);
  falhar=true;
  await t.main();
  assert.match(t.markup(),/Não foi possível atualizar agora/);
  assert.match(t.markup(),/Total gerencial registrado[\s\S]*?Valor exato: R\$ 14,00/);
  assert.equal(t.run('ROWS[0].resultado_liquido'),14);
});
