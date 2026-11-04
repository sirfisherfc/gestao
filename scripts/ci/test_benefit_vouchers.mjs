import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const V = require('../../assets/voucher-template.js');
const voucher = { status:'available', beneficiary_name:'Nome de teste', benefit_type:'fixed', benefit_value:1234.56,
  code:'SF-01AB-CDEF-GHJK', expires_on:'2026-12-04', phone:'85999990000', internal_note:'NÃO EXIBIR NOTA',
  issue_reason:'recovery', issue_reason_detail:'NÃO EXIBIR MOTIVO', conditions:['Uso único. Saldo não utilizado é perdido.',
  'Não cumulativo com promoções ou outro voucher na mesma conta.','Válido na unidade Sir Fisher até a data indicada.'] };
function context() {
  const calls=[];
  return { calls, font:'25px Arial', measureText(text) { const size=Number.parseInt(this.font.match(/(\d+)px/)[1],10);return {width:[...text].length*size*.58}; },
    fillText(text,x,y){calls.push({text,x,y,font:this.font});},clearRect(){},fillRect(){},strokeRect(){},drawImage(){},setLineDash(){},beginPath(){},moveTo(){},lineTo(){},stroke(){} };
}
test('reais e percentuais mantêm unidades, centavos e valores distintos',()=>{
  assert.match(V.benefit(voucher),/1\.234,56/);
  assert.equal(V.benefit({...voucher,benefit_type:'percent',benefit_value:12.5}),'12,5%');
  assert.equal(V.benefit({...voucher,benefit_type:'percent',benefit_value:100}),'100%');
});
test('padrão 30 dias usa Fortaleza, incluindo virada UTC, mês e ano',()=>{
  assert.equal(V.todayPlus(0,new Date('2026-11-05T01:00:00Z')),'2026-11-04');
  assert.equal(V.todayPlus(30,new Date('2026-12-20T12:00:00Z')),'2027-01-19');
  assert.equal(V.dateBR('2026-12-04'),'04/12/2026');
  assert.match(V.timeBR('2026-11-05T01:00:00Z'),/04\/11\/2026.*22:00/);
});
for (const [label,changes] of [
  ['valor normal',{}], ['nome com160caracteres',{beneficiary_name:('Ana Maria de Souza '.repeat(10)).slice(0,160)}],
  ['nome sem espaços',{beneficiary_name:'W'.repeat(160)}], ['maior valor suportado',{benefit_value:9999999999.99}],
  ['percentual fracionário',{benefit_type:'percent',benefit_value:12.5}], ['percentual100',{benefit_type:'percent',benefit_value:100}],
]) test(`template: ${label}, texto cabe e dados internos não são desenhados`,()=>{
  const ctx=context(),v={...voucher,...changes}; V.draw(ctx,v,{});
  const full=ctx.calls.map(c=>c.text).join(' ');
  assert.ok(!full.includes(v.phone) && !full.includes(v.internal_note) && !full.includes(v.issue_reason_detail));
  assert.ok(full.includes(v.code) && full.includes('04/12/2026'));
  for (const call of ctx.calls) {ctx.font=call.font;assert.ok(ctx.measureText(call.text).width<=1020,call.text);assert.ok(call.y<1440);}
  const nameCalls=ctx.calls.filter(c=>c.y>=780 && c.y<972);
  assert.ok(nameCalls.every(c=>c.y<945),'nome deve terminar antes da linha do código');
  assert.equal(nameCalls.map(c=>c.text).join('').replace(/\s/g,''),v.beneficiary_name.replace(/\s/g,''));
});
test('não prepara imagens para voucher usado, vencido ou cancelado',()=>{
  for(const status of ['used','expired','cancelled'])assert.throws(()=>V.draw(context(),{...voucher,status},{}));
});
test('WhatsApp recebe só dados do presente, nome escapado e número com país',()=>{
  const url=new URL(V.whatsapp({...voucher,beneficiary_name:'Ana & João?'}));
  assert.equal(url.pathname,'/5585999990000');
  const text=url.searchParams.get('text'); assert.ok(text.includes('Ana & João?') && text.includes(voucher.code));
  assert.ok(!text.includes(voucher.internal_note) && !text.includes(voucher.issue_reason_detail));
});
test('compartilha arquivo já preparado mantendo chamada na interação do usuário',async()=>{
  const file={name:'voucher.png'},calls=[];
  const promise=V.sharePrepared(file,{canShare:()=>true,share:args=>{calls.push(args);return Promise.resolve();}},()=>assert.fail('fallback inesperado'));
  assert.equal(calls.length,1); assert.equal(calls[0].files[0],file); assert.equal(await promise,'shared');
});
test('sem suporte, canShare falso ou erro, oferece download e link',async()=>{
  for(const nav of [{},{canShare:()=>false,share:()=>assert.fail()}, {canShare:()=>true,share:()=>Promise.reject(new Error('blocked'))}, {canShare:()=>{throw new Error('blocked');},share:()=>{}}]) {
    let fallback=0;assert.equal(await V.sharePrepared({},nav,()=>fallback++),'fallback');assert.equal(fallback,1);
  }
});
test('cancelar compartilhamento não dispara download nem mensagem involuntária',async()=>{
  assert.equal(await V.sharePrepared({},{canShare:()=>true,share:()=>Promise.reject(Object.assign(new Error(),{name:'AbortError'}))},()=>assert.fail()),'cancelled');
});
test('oito categorias principais e outro motivo livre',()=>{assert.equal(Object.keys(V.REASONS).length,9);assert.ok(V.REASONS.other);});
