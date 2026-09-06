// Executa o JavaScript real da pagina com RPCs e DOM sinteticos, sem rede.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import vm from 'node:vm';

const html=readFileSync(new URL('../../importar.html',import.meta.url),'utf8');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1]
  .split('(async()=>{const auth=')[0];
const arquivo=nome=>({nome,cfg:{fonte:'stone_extrato'},registros:[{fixture:nome}],previa:{novas:1}});
const salvo=id=>({inseridos:1,recalculo_inicio:'2026-09-01',recalculo_fim:'2026-09-02',recalculo_id:id});

function tela(rpc,nomes=['primeiro.csv']){
  const elements=new Map();
  let clock=0;
  const calls=[];
  const context=vm.createContext({
    SirFisherSupabase:{rpc:async(name,args)=>{calls.push({name,args});return rpc(name,args,calls);}},
    SirFisherDOM:{escapeHTML:s=>String(s??'').replaceAll('<','&lt;').replaceAll('>','&gt;')},
    document:{getElementById:id=>{
      if(!elements.has(id))elements.set(id,{style:{},addEventListener(){},classList:{add(){},remove(){}}});
      return elements.get(id);
    }},
    Date:class extends Date{static now(){return clock;}},
    setTimeout:fn=>{clock+=2000;fn();},
  });
  vm.runInContext(source,context);
  context.fixtures=nomes.map(arquivo);
  vm.runInContext('ARQUIVOS=fixtures;',context);
  return {calls,files:context.fixtures,run:()=>vm.runInContext('importar()',context),
    consultar:()=>vm.runInContext('consultarAtualizacoes()',context),
    busy:()=>vm.runInContext('OCUPADO',context),
    message:()=>elements.get('msg')?.textContent,
    markup:()=>elements.get('main')?.innerHTML};
}

test('cada arquivo usa seu ID; sucesso exige todos concluidos e nao solicita outra tarefa',async()=>{
  let id=0;
  const t=tela(async name=>name==='importar_csv_stone'
    ? {data:salvo(++id)}:{data:{situacao:'concluido'}},['a.csv','b.csv']);
  await t.run();
  assert.deepEqual(t.calls.filter(c=>c.name==='consultar_recalculo_saldo').map(c=>c.args.p_id),[1,2]);
  assert.equal(t.calls.some(c=>c.name==='solicitar_recalculo_saldo'),false);
  assert.match(t.message(),/todos os arquivos salvos/);
  assert.equal(t.busy(),false);
});

for(const throws of [false,true])test(`falha do segundo arquivo preserva primeiro e libera tela (throw=${throws})`,async()=>{
  let uploads=0;
  const t=tela(async name=>{
    if(name==='importar_csv_stone'){
      if(++uploads===1)return {data:salvo(7)};
      if(throws)throw new Error('rede indisponivel');
      return {error:{message:'arquivo rejeitado'}};
    }
    return {data:{situacao:'concluido'}};
  },['a.csv','b.csv','c.csv']);
  await t.run();
  assert.equal(uploads,2);
  assert.equal(t.files[0].atualizacao.id,7);
  assert.equal(t.files[0].atualizacao.situacao,'concluido');
  assert.match(t.message(),/sem importação confirmada/);
  assert.equal(t.busy(),false);
});

test('banco anterior agenda logo apos cada arquivo, antes do proximo upload',async()=>{
  let id=10;
  const t=tela(async name=>{
    if(name==='importar_csv_stone'){const data=salvo(null);delete data.recalculo_id;return {data};}
    if(name==='solicitar_recalculo_saldo')return {data:{id:++id}};
    return {data:{situacao:'concluido'}};
  },['a.csv','b.csv']);
  await t.run();
  assert.deepEqual(t.calls.slice(0,4).map(c=>c.name),[
    'importar_csv_stone','solicitar_recalculo_saldo','importar_csv_stone','solicitar_recalculo_saldo']);
});

test('campo presente nulo nao dispara fallback; gravacao e agendamento sao distintos',async()=>{
  const t=tela(async()=>({data:salvo(null)}));
  await t.run();
  assert.equal(t.calls.length,1);
  assert.equal(t.files[0].atualizacao.situacao,'nao_agendado');
  assert.match(t.message(),/Não foi possível confirmar o agendamento/);
});

for(const throws of [false,true])test(`falha do fallback conserva dados salvos (throw=${throws})`,async()=>{
  const t=tela(async name=>{
    if(name==='importar_csv_stone'){const data=salvo(null);delete data.recalculo_id;return {data};}
    if(throws)throw new Error('rede');
    return {error:{message:'falha'}};
  });
  await t.run();
  assert.equal(t.files[0].resultado.inseridos,1);
  assert.equal(t.files[0].erro,undefined);
  assert.match(t.message(),/agendamento/);
  assert.equal(t.busy(),false);
});

test('zero insercoes nao enfileira nem afirma que tarefas antigas terminaram',async()=>{
  const t=tela(async()=>({data:{inseridos:0}}));
  await t.run();
  assert.equal(t.calls.length,1);
  assert.match(t.message(),/anteriores podem continuar pendentes/);
  assert.doesNotMatch(t.message(),/Painel inalterado|painel atualizado/);
});

test('erro de consulta nao vira erro de processamento; nova consulta reutiliza ID',async()=>{
  let consultas=0;
  const t=tela(async name=>{
    if(name==='importar_csv_stone')return {data:salvo(9)};
    if(++consultas===1)throw new Error('offline');
    return {data:{situacao:'concluido'}};
  });
  await t.run();
  assert.equal(t.files[0].atualizacao.situacao,'desconhecido');
  assert.match(t.message(),/Não foi possível consultar/);
  assert.match(t.markup(),/Consultar atualização/);
  await t.consultar();
  assert.equal(t.files[0].atualizacao.situacao,'concluido');
  assert.equal(t.calls.filter(c=>c.name==='importar_csv_stone').length,1);
});

test('lote misto mantem concluido, erro, consulta desconhecida e pendente separados',async()=>{
  let id=0;
  const t=tela(async(name,args)=>{
    if(name==='importar_csv_stone')return {data:salvo(++id)};
    if(args.p_id===3)return {error:{message:'consulta indisponivel'}};
    return {data:{situacao:{1:'concluido',2:'erro',4:'pendente'}[args.p_id]}};
  },['a.csv','b.csv','c.csv','d.csv']);
  await t.run();
  assert.deepEqual(t.files.map(a=>a.atualizacao.situacao),['concluido','erro','desconhecido','pendente']);
  assert.match(t.message(),/atualização de parte dos dados falhou/);
  assert.match(t.message(),/continua pendente/);
  assert.doesNotMatch(t.message(),/painel atualizado para todos/);
  assert.equal(t.busy(),false);
});

test('clique duplo nao duplica upload enquanto lote esta ocupado',async()=>{
  let release;
  const t=tela(name=>name==='importar_csv_stone'
    ? new Promise(resolve=>{release=()=>resolve({data:salvo(1)});})
    : {data:{situacao:'concluido'}});
  const first=t.run();
  await t.run();
  assert.equal(t.calls.length,1);
  release();await first;
  assert.equal(t.busy(),false);
});
