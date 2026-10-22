import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../../status.html',import.meta.url),'utf8');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1].split('(async()=>{const auth=')[0];
const safe=readFileSync(new URL('../../assets/safe-dom.js',import.meta.url),'utf8');
const dia=(d,extra={})=>['vendas','recebiveis','baixas','painel','extrato'].map(etapa=>({dia:d,etapa,
  identificador:['recebiveis','baixas'].includes(etapa)?'123':'',estado:'concluido',atrasado:false,...extra}));
function tela(paginas){
  const target={innerHTML:''};let calls=0;
  const context=vm.createContext({Date,document:{getElementById:id=>id==='fechamentoStone'?target:null},
    SirFisherSupabase:{from:name=>{assert.equal(name,'app_stone_fechamento');return{select:()=>{
      const q={order:()=>q,range:(a,b)=>{assert.equal(a,calls*500);assert.equal(b,a+499);return Promise.resolve(paginas[calls++]||{data:[]});}};return q;
    }};}}});context.window=context;vm.runInContext(safe,context);vm.runInContext(source,context);
  return{target,context,calls:()=>calls};
}
let cases=0;
{
  const {context:c}=tela([]);
  const rows=[...dia('2026-10-21',{estado:'aguardando'}),...dia('2026-10-22')];
  const r=c.resumirFechamentoStone(rows);assert.equal(r.contiguo,null);assert.equal(r.pendentes,1);
  const html=c.renderFechamentoStone(rows);assert.match(html,/aguardando o primeiro fechamento/);assert.match(html,/23h59/);
  assert.match(html,/Voucher e link de pagamento/);assert.doesNotMatch(html,/<details[^>]*\bopen\b/);cases++;
}
{
  const {context:c}=tela([]);const r=c.resumirFechamentoStone([...dia('2026-10-21'),...dia('2026-10-22')]);
  assert.equal(r.contiguo,'2026-10-22');assert.equal(r.pendentes,0);cases++;
}
{
  const {context:c}=tela([]);const rows=dia('2026-10-21');rows[2]={...rows[2],estado:'erro',atrasado:true,mensagem:'<img src=x onerror=alert(1)>'};
  const html=c.renderFechamentoStone(rows);assert.match(html,/Atrasado/);assert.match(html,/Baixas de parcelas/);
  assert.match(html,/&lt;img/);assert.doesNotMatch(html,/<img/);cases++;
}
{
  const page=Array.from({length:500},(_,i)=>({...dia('2026-10-21')[0],identificador:String(i)}));
  const t=tela([{data:page},{data:dia('2026-10-22')}]);await t.context.loadFechamentoStone();
  assert.equal(t.calls(),2);assert.match(t.target.innerHTML,/Fechamento automático Stone/);cases++;
}
{
  const t=tela([{error:{message:'sem acesso'}}]);await t.context.loadFechamentoStone();
  assert.match(t.target.innerHTML,/conclusão está indisponível/);assert.doesNotMatch(t.target.innerHTML,/Todas as etapas conferidas/);cases++;
}
console.log(`STATUS_FECHAMENTO_TESTS_OK cases=${cases} network=0`);
