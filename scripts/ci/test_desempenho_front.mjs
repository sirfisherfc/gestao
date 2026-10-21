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

// Cliente falso: cada consulta e registrada quando de fato e enviada (then),
// e o resumo fica pendente ate o teste liberar.
function clienteFalso(tabelaPendente){
  const pedidos=[];
  let libera;
  const pendente=new Promise(resolve=>{libera=resolve;});
  const from=tabela=>{
    const filtros={};
    let enviado=null;
    const b={
      select:()=>b,order:()=>b,limit:()=>b,maybeSingle:()=>b,
      eq:(coluna,valor)=>{filtros[coluna]=valor;return b;},
      then:(ok,erro)=>{
        if(!enviado){
          pedidos.push({tabela,filtros});
          enviado=tabela===tabelaPendente?pendente:Promise.resolve({data:[],error:null});
        }
        return enviado.then(ok,erro);
      }
    };
    return b;
  };
  return {sb:{from},pedidos,libera:valor=>libera(valor)};
}

function scriptDaPagina(arquivo){
  const html=readFileSync(new URL('../../'+arquivo,import.meta.url),'utf8');
  const source=html.match(/<script>\s*([\s\S]*?)<\/script>\s*<\/body>/)[1];
  return source.slice(0,source.lastIndexOf('(async()=>{'));
}

function contextoPagina(sb){
  const elementos=new Map();
  const el=()=>({innerHTML:'',textContent:'',value:'',style:{},addEventListener(){},parentElement:{innerHTML:''}});
  class Chart{constructor(){}destroy(){}}
  Chart.defaults={font:{}};
  const c=vm.createContext({Date,Intl,Map,Set,Promise,setTimeout,console:{warn(){},error(){}},Chart,
    SirFisherSupabase:sb,SirFisherDOM:{escapeHTML:s=>String(s??'')},
    SirFisherFormat:{brl:String,pct:String,rs:String,monthTrend:()=>({active:false,label:a=>a,value:v=>v})},
    SirFisherApp:{number:(_chave,padrao)=>padrao},addEventListener(){},
    document:{addEventListener(){},querySelectorAll:()=>[],getElementById(id){
      if(!elementos.has(id))elementos.set(id,el());
      return elementos.get(id);
    }}});
  c.window=c;
  return c;
}

const mesCorrente=()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');};

test('inicio pede detalhes e apoio junto com o resumo e desenha o resumo primeiro',async()=>{
  const f=clienteFalso('app_painel_resumo_mensal');
  const c=contextoPagina(f.sb);
  vm.runInContext(scriptDaPagina('index.html'),c);
  vm.runInContext("var etapas=[];renderMes=()=>{etapas.push(LOAD_STAGE);};renderFooter=()=>{};montarSeletorPeriodo=()=>{};document.getElementById('mesSel').value='2026-10';",c);
  const carga=vm.runInContext('main()',c);
  await tick();
  const tabelas=f.pedidos.map(p=>p.tabela);
  for(const t of ['app_painel_dre_cascata','app_projecao_despesa_fixa','app_projecao_despesa_direta',
    'app_painel_composicao_despesa','app_painel_saldo_fim_mes','app_painel_saldo_atual',
    'app_painel_margem_contribuicao','app_painel_ultima_carga','app_painel_cargas','app_painel_resumo_mensal'])
    assert.ok(tabelas.includes(t),t+' deveria sair antes da resposta do resumo');
  assert.equal(vm.runInContext("etapas.join(',')",c),'','nada deveria ser desenhado antes do resumo');
  f.libera({data:[{ano_mes:'2026-10',faturamento:10}],error:null});
  await carga;
  assert.equal(vm.runInContext("etapas.join(',')",c),'detalhes,apoio,concluido');
});

test('gerente pede o mes corrente e o rodape junto com o resumo e reaproveita a consulta',async()=>{
  const f=clienteFalso('app_gerente_resumo_mensal');
  const c=contextoPagina(f.sb);
  vm.runInContext(scriptDaPagina('gerente.html'),c);
  vm.runInContext('var renders=0;render=()=>{renders++;};',c);
  const carga=vm.runInContext('carregar()',c);
  await tick();
  const mes=mesCorrente();
  const doMes=f.pedidos.filter(p=>p.filtros.ano_mes===mes||p.filtros.mes===mes+'-01');
  assert.equal(doMes.length,5,'as cinco consultas do mes deveriam sair com o resumo');
  assert.ok(f.pedidos.some(p=>p.tabela==='app_gerente_ultima_carga'),'rodape deveria sair com o resumo');
  f.libera({data:[{ano_mes:'2026-01'},{ano_mes:mes}],error:null});
  await carga;
  assert.equal(f.pedidos.length,7,'nao deveria repetir as consultas do mes corrente');
  assert.equal(vm.runInContext('renders',c),1);
});

test('gerente busca o mes certo quando o painel abre em outro mes',async()=>{
  const f=clienteFalso('app_gerente_resumo_mensal');
  const c=contextoPagina(f.sb);
  vm.runInContext(scriptDaPagina('gerente.html'),c);
  vm.runInContext('var renders=0;render=()=>{renders++;};',c);
  const carga=vm.runInContext('carregar()',c);
  await tick();
  f.libera({data:[{ano_mes:'2020-01'},{ano_mes:'2020-02'}],error:null});
  await carga;
  const outroMes=f.pedidos.filter(p=>p.filtros.ano_mes==='2020-02'||p.filtros.mes==='2020-02-01');
  assert.equal(outroMes.length,5,'deveria buscar as cinco consultas do mes aberto');
  assert.equal(vm.runInContext('renders',c),1);
});

const configSource=readFileSync(new URL('../../assets/app-config.js',import.meta.url),'utf8');

// respostas[nome] pode ser um valor ou uma promessa ainda pendente.
function paginaComConfig(local,respostas){
  const chamadas=[];
  const c=vm.createContext({localStorage:local,Date,JSON,Object,Number,String,Array,
    document:{title:'Painel · Caixa',readyState:'complete',querySelectorAll:()=>[],addEventListener(){}},
    SirFisherSupabase:{rpc:nome=>{chamadas.push(nome);return Promise.resolve(respostas[nome]??{data:null,error:{message:'sem resposta'}});}}});
  c.window=c;
  vm.runInContext(configSource,c);
  return {c,chamadas,pronto:vm.runInContext('window.SirFisherApp.ready',c),
    numero:chave=>vm.runInContext(`window.SirFisherApp.number(${JSON.stringify(chave)},0)`,c)};
}

const operacional=valor=>({data:[{unidade_codigo:'PRAIA',unidade_nome:'Praia',parametros:{caixa_saldo_minimo:valor}}],error:null});
const empresa=nome=>({data:[{nome,subtitulo:'Gestao'}],error:null});
const pendente=()=>new Promise(()=>{});

test('falha so do nome ainda guarda os parametros e nao guarda o nome generico',async()=>{
  const local=storage();
  const primeira=paginaComConfig(local,{app_configuracao_empresa:{data:null,error:{message:'permission denied'}},
    app_configuracao_operacional:operacional(5)});
  await primeira.pronto;
  const salvo=JSON.parse(local.getItem('finance_panel_config_v1'));
  assert.ok(salvo,'configuracao deveria ficar em cache');
  assert.equal(salvo.current,null,'nome generico nao pode ser guardado');
  assert.equal(salvo.settings.caixa_saldo_minimo,5);
});

test('com cache valido a pagina nao espera consulta nenhuma',async()=>{
  const local=storage();
  await paginaComConfig(local,{app_configuracao_empresa:empresa('Empresa Teste'),app_configuracao_operacional:operacional(5)}).pronto;
  const segunda=paginaComConfig(local,{app_configuracao_empresa:pendente(),app_configuracao_operacional:pendente()});
  await segunda.pronto;
  assert.equal(vm.runInContext('window.SirFisherApp.current().nome',segunda.c),'Empresa Teste');
  assert.equal(segunda.numero('caixa_saldo_minimo'),5);
  assert.equal(segunda.chamadas.length,2,'revalidacao deveria sair em segundo plano');
});

test('revalidacao guarda os valores novos so para a proxima pagina',async()=>{
  const local=storage();
  await paginaComConfig(local,{app_configuracao_empresa:empresa('Empresa Teste'),app_configuracao_operacional:operacional(5)}).pronto;
  const segunda=paginaComConfig(local,{app_configuracao_empresa:empresa('Empresa Teste'),app_configuracao_operacional:operacional(9)});
  await segunda.pronto;
  await tick();
  assert.equal(segunda.numero('caixa_saldo_minimo'),5,'a pagina atual nao muda no meio do caminho');
  assert.equal(JSON.parse(local.getItem('finance_panel_config_v1')).settings.caixa_saldo_minimo,9);
  const terceira=paginaComConfig(local,{app_configuracao_empresa:pendente(),app_configuracao_operacional:pendente()});
  await terceira.pronto;
  assert.equal(terceira.numero('caixa_saldo_minimo'),9);
});

test('revalidacao atrasada nao sobrescreve uma recarga forcada',async()=>{
  const local=storage();
  await paginaComConfig(local,{app_configuracao_empresa:empresa('Empresa Teste'),app_configuracao_operacional:operacional(5)}).pronto;
  let liberaAntiga;
  const antiga=new Promise(resolve=>{liberaAntiga=resolve;});
  const respostas={app_configuracao_empresa:empresa('Empresa Teste'),app_configuracao_operacional:antiga};
  const pagina=paginaComConfig(local,respostas);
  await pagina.pronto;
  respostas.app_configuracao_operacional=operacional(7);
  await vm.runInContext('window.SirFisherApp.reload()',pagina.c);
  liberaAntiga(operacional(3));
  await tick();
  assert.equal(JSON.parse(local.getItem('finance_panel_config_v1')).settings.caixa_saldo_minimo,7);
});

test('sem os parametros nada e guardado e a pagina seguinte consulta de novo',async()=>{
  const local=storage();
  const primeira=paginaComConfig(local,{app_configuracao_empresa:empresa('Empresa Teste'),
    app_configuracao_operacional:{data:null,error:{message:'falha'}}});
  await primeira.pronto;
  assert.equal(local.getItem('finance_panel_config_v1'),null);
  const segunda=paginaComConfig(local,{app_configuracao_empresa:empresa('Empresa Teste'),app_configuracao_operacional:operacional(5)});
  await segunda.pronto;
  assert.equal(segunda.chamadas.length,2);
  assert.equal(segunda.numero('caixa_saldo_minimo'),5);
});
