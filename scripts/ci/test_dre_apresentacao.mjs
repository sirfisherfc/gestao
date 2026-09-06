// Casos sinteticos: ausencia nao e custo zero; valores validos sao preservados.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import vm from 'node:vm';

const read=name=>readFileSync(new URL('../../'+name,import.meta.url),'utf8');
const html=read('dre.html');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{const ctx=')[0];
const completo=()=>({mes:'2026-09-01',ano_mes:'2026-09',receita:100,cmv:-30,
  cmv_perc:30,pessoal:-25,pessoal_perc:25,impostos:-10,margem_contribuicao:60,
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
    DESP_DIRETA=[{dia:'2026-09-20',valor:20}];DESP_FIXA=[{dia:'2026-09-20',valor:30}];`,c);
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

