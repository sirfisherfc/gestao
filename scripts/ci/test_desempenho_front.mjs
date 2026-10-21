// Desempenho do front: papel e matriz em paralelo com a configuracao,
// cache entre abas vinculado ao usuario, limpeza no logout, corte do
// Calendario junto com o calendario e medicao ?perf=1.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import vm from 'node:vm';

const authSource=readFileSync(new URL('../../assets/auth.js',import.meta.url),'utf8');
const clientSource=readFileSync(new URL('../../assets/supabase-client.js',import.meta.url),'utf8');

function storage(){
  const m=new Map();
  return {getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k),has:k=>m.has(k)};
}

function element(tag){
  const el={tag,children:[],listeners:{},style:{},className:'',textContent:'',
    classList:{add(){},toggle(){},contains:()=>false},
    setAttribute(){},append(...xs){el.children.push(...xs);},appendChild(x){el.children.push(x);return x;},
    addEventListener(type,fn){(el.listeners[type]=el.listeners[type]||[]).push(fn);},
    contains:()=>false,replaceChildren(){el.children=[];}};
  return el;
}

function find(root,pred){
  if(pred(root))return root;
  for(const c of root.children||[]){const r=find(c,pred);if(r)return r;}
  return null;
}

function ambiente({role='socio',cachedRole=null,userId='u1',page='caixa.html'}={}){
  const calls=[];
  let liberaConfig;
  const appReady=new Promise(resolve=>{liberaConfig=resolve;});
  const local=storage(),session=storage(),body=element('body');
  if(cachedRole)local.setItem('finance_panel_role_v1',JSON.stringify({savedAt:Date.now(),userId:cachedRole.userId,role:cachedRole.role}));
  const sb={
    auth:{
      getSession:async()=>({data:{session:{user:{id:userId,email:'pessoa@exemplo.com',user_metadata:{}}}},error:null}),
      signOut:async()=>{calls.push('signOut');}
    },
    rpc:async name=>{calls.push('rpc:'+name);return {data:role,error:null};},
    from:name=>({select:()=>{calls.push('from:'+name);
      return Promise.resolve({data:[{pagina:page,papeis:['socio','gerente']}],error:null});}})
  };
  const c=vm.createContext({
    localStorage:local,sessionStorage:session,performance:{mark(name){calls.push('mark:'+name);}},
    location:{pathname:'/'+page,search:'',hash:'',href:'https://painel.exemplo/'+page,replace(url){calls.push('replace:'+url);}},
    history:{replaceState(){}},URLSearchParams,
    document:{getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[],
      createElement:element,head:element('head'),body,addEventListener(){}}
  });
  c.window=c;
  c.SirFisherApp={ready:appReady,current:()=>({nome:'Empresa'}),monogram:()=>'E'};
  vm.runInContext(authSource,c);
  return {c,sb,calls,local,body,liberaConfig};
}

const tick=()=>new Promise(resolve=>setImmediate(resolve));

test('papel e matriz de navegacao comecam antes de a configuracao terminar',async()=>{
  const t=ambiente();
  const pronto=t.c.SirFisherAuth.requireRole(t.sb);
  await tick();
  assert.ok(t.calls.includes('rpc:papel_usuario_atual'),'papel deveria ser consultado em paralelo');
  assert.ok(t.calls.includes('from:pagina_permissao'),'matriz deveria ser consultada em paralelo');
  t.liberaConfig();
  const ctx=await pronto;
  assert.equal(ctx.role,'socio');
  assert.equal(t.calls.filter(x=>x==='from:pagina_permissao').length,1,'matriz consultada uma vez');
  assert.ok(t.calls.includes('mark:sirfisher:auth'));
});

test('admin com papel em cache entra sem consultar papel nem matriz',async()=>{
  const t=ambiente({role:'admin',cachedRole:{userId:'u1',role:'admin'}});
  const pronto=t.c.SirFisherAuth.requireRole(t.sb);
  t.liberaConfig();
  const ctx=await pronto;
  assert.equal(ctx.role,'admin');
  assert.ok(!t.calls.some(x=>x.startsWith('rpc:')||x.startsWith('from:')),t.calls.join(','));
});

test('cache de papel de outro usuario e ignorado',async()=>{
  const t=ambiente({role:'gerente',cachedRole:{userId:'outra-pessoa',role:'admin'}});
  const pronto=t.c.SirFisherAuth.requireRole(t.sb);
  t.liberaConfig();
  const ctx=await pronto;
  assert.equal(ctx.role,'gerente');
  assert.ok(t.calls.includes('rpc:papel_usuario_atual'));
});

test('papel consultado fica no armazenamento compartilhado entre abas',async()=>{
  const t=ambiente({role:'socio'});
  const pronto=t.c.SirFisherAuth.requireRole(t.sb);
  t.liberaConfig();
  await pronto;
  const salvo=JSON.parse(t.local.getItem('finance_panel_role_v1'));
  assert.equal(salvo.userId,'u1');
  assert.equal(salvo.role,'socio');
  assert.ok(t.local.has('finance_panel_permissions_v1'));
});

test('sair apaga papel e matriz antes de encerrar a sessao',async()=>{
  const t=ambiente({role:'socio'});
  const pronto=t.c.SirFisherAuth.requireRole(t.sb);
  t.liberaConfig();
  await pronto;
  assert.ok(t.local.has('finance_panel_role_v1'),'papel deveria estar em cache antes do logout');
  assert.ok(t.local.has('finance_panel_permissions_v1'),'matriz deveria estar em cache antes do logout');
  const sair=find(t.body,el=>el.className==='sf-acct-out');
  assert.ok(sair,'botao de sair nao encontrado');
  await sair.listeners.click[0]();
  assert.ok(!t.local.has('finance_panel_role_v1'));
  assert.ok(!t.local.has('finance_panel_permissions_v1'));
  assert.ok(t.calls.includes('signOut'));
});

function cliente(search){
  const criados=[],session=storage();
  const c=vm.createContext({
    sessionStorage:session,URLSearchParams,URL,console:{table(){},info(){}},
    location:{search,href:'https://painel.exemplo/index.html',pathname:'/index.html'},
    performance:{now:()=>Date.now(),getEntriesByType:()=>[],getEntriesByName:()=>[]},
    PerformanceObserver:class{observe(){}},
    fetch:async()=>({status:200}),setTimeout,clearTimeout,
    supabase:{createClient:(...args)=>{criados.push(args);return {};}},
    document:{getElementById:()=>null,createElement:element,body:element('body')}
  });
  c.window=c;
  vm.runInContext(clientSource,c);
  return {c,criados,session};
}

test('sem ?perf=1 o cliente e criado como antes',()=>{
  const t=cliente('');
  assert.equal(t.criados.length,1);
  assert.equal(t.criados[0].length,2);
});

test('?perf=1 mede as consultas sem alterar a resposta',async()=>{
  const t=cliente('?perf=1');
  assert.equal(t.session.getItem('sirfisher_perf'),'1');
  const opcoes=t.criados[0][2];
  assert.equal(typeof opcoes.global.fetch,'function');
  const resposta=await opcoes.global.fetch('https://x.supabase.co/rest/v1/app_painel_resumo_mensal?select=*',{});
  assert.equal(resposta.status,200);
});

function calendario(){
  const html=readFileSync(new URL('../../calendario.html',import.meta.url),'utf8');
  const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{AUTH=')[0];
  const ordem=[];
  let liberaCalendario;
  const resposta=new Promise(resolve=>{liberaCalendario=resolve;});
  const sb={rpc:name=>{ordem.push(name);
    return name==='listar_calendario_financeiro'?resposta:Promise.resolve({data:[{corte_caixa:'2026-10-20'}],error:null});}};
  const elements=new Map();
  const c=vm.createContext({SirFisherSupabase:sb,SirFisherDOM:{escapeHTML:s=>String(s)},Intl,Date,setTimeout,
    console:{error(){}},matchMedia:()=>({matches:false}),
    document:{addEventListener(){},querySelectorAll:()=>[],getElementById(id){
      if(!elements.has(id))elements.set(id,{innerHTML:'',value:'2026-10',addEventListener(){}});
      return elements.get(id);
    }}});
  c.window=c;
  vm.runInContext(source,c);
  vm.runInContext('var renders=0;render=()=>{renders++;};',c);
  return {c,ordem,liberaCalendario,run:code=>vm.runInContext(code,c)};
}

test('calendario pede o corte junto com o calendario e so uma vez por pagina',async()=>{
  const t=calendario();
  const primeira=t.run("carregar('2026-10')");
  await tick();
  assert.deepEqual(t.ordem,['resumo_corte_caixa','listar_calendario_financeiro'],'corte deveria sair antes da resposta do calendario');
  t.liberaCalendario({data:[],error:null});
  await primeira;
  assert.equal(t.run('renders'),1);
  assert.equal(t.run('CORTE.corte_caixa'),'2026-10-20');
  await t.run("carregar('2026-09')");
  assert.equal(t.ordem.filter(n=>n==='resumo_corte_caixa').length,1,'corte nao deve repetir ao trocar de mes');
  assert.equal(t.run('renders'),2);
});
