import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const V = require('../../assets/voucher-template.js');
const voucher = { status:'available', beneficiary_name:'Nome de teste', benefit_type:'fixed', benefit_value:1234.56,
  code:'A1B2C3', expires_on:'2026-12-04', phone:'85999990000', internal_note:'NÃO EXIBIR NOTA',
  issue_reason:'recovery', issue_reason_detail:'NÃO EXIBIR MOTIVO', conditions:['Uso único. Saldo não utilizado é perdido.',
  'Não cumulativo com promoções ou outro voucher na mesma conta.','Válido na unidade Sir Fisher até a data indicada.'] };
function context() {
  const calls=[],images=[];
  return { calls, images, font:'25px Arial', measureText(text) { const size=Number.parseInt(this.font.match(/(\d+)px/)[1],10);return {width:[...text].length*size*.58}; },
    fillText(text,x,y){calls.push({text,x,y,font:this.font,align:this.textAlign});},clearRect(){},fillRect(){},strokeRect(){},drawImage(...args){images.push(args);},setLineDash(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},roundRect(){},fill(){},save(){},restore(){} };
}
const deck={width:960,height:858};
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
  const ctx=context(),v={...voucher,...changes}; V.draw(ctx,v,{},deck);
  const full=ctx.calls.map(c=>c.text).join(' ');
  assert.ok(!full.includes(v.phone) && !full.includes(v.internal_note) && !full.includes(v.issue_reason_detail));
  assert.ok(full.includes(v.code) && full.includes('04/12/2026'));
  for (const call of ctx.calls) {ctx.font=call.font;const width=ctx.measureText(call.text).width;const left=call.align==='left' ? call.x : call.x-width/2;assert.ok(left>=24 && left+width<=V.WIDTH-24,call.text);assert.ok(call.y<V.HEIGHT);}
  const nameCalls=ctx.calls.filter(c=>c.y>=530 && c.y<690);
  assert.ok(nameCalls.every(c=>c.y<676),'nome deve terminar antes da linha do código');
  assert.equal(nameCalls.map(c=>c.text).join('').replace(/\s/g,''),v.beneficiary_name.replace(/\s/g,''));
});
test('foto do deck integra o PNG, sem distorção ou recorte fora do arquivo',()=>{
  const ctx=context();V.draw(ctx,voucher,{},deck);
  const photo=ctx.images.find(args=>args[0]===deck);assert.ok(photo,'a foto deve ser desenhada no mesmo canvas exportado');
  const [,sx,sy,sw,sh,dx,dy,dw,dh]=photo;
  assert.ok(sx>=0 && sy>=0 && sx+sw<=deck.width && sy+sh<=deck.height);
  assert.ok(Math.abs(sw/sh-dw/dh)<1e-10);assert.ok(dx>=0 && dy>=0 && dx+dw<=V.WIDTH && dy+dh<=V.HEIGHT);
});
test('foto ausente impede exportação silenciosa de arte sem deck',()=>{
  assert.throws(()=>V.draw(context(),voucher,{}),/foto do deck/);
});
test('arte horizontal tem só condições essenciais, sem alterar regras do cadastro',()=>{
  assert.ok(V.WIDTH>V.HEIGHT);
  const ctx=context(),v={...voucher,benefit_type:'percent',benefit_value:15,conditions:['Desconto sobre a conta inteira. Sem teto em reais. Saldo não utilizado é perdido.']};
  V.draw(ctx,v,{},deck);const text=ctx.calls.map(c=>c.text).join(' ');
  assert.ok(text.includes('Uso único') && text.includes('Não cumulativo'));
  for(const phrase of ['conta inteira','teto em reais','saldo não','Válido na unidade'])assert.ok(!text.toLowerCase().includes(phrase.toLowerCase()));
  assert.equal(v.conditions.length,1);
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
test('nove categorias principais e outro motivo livre',()=>{
  assert.equal(Object.keys(V.REASONS).length,10);
  assert.equal(V.REASONS.award,'Premiação / atingimento de metas');
  assert.ok(V.REASONS.other);
});
test('histórico conserva motivo original e complementos com dois-pontos',()=>{
  assert.equal(V.eventReason('friend: Presente: aniversário'),'Cortesia para amigo: Presente: aniversário');
  assert.equal(V.eventReason('staff_birthday'),'Aniversário de funcionário');
});
test('auditoria mostra alterações reais e formata unidades antes/depois',()=>{
  const before={benefit_type:'fixed',benefit_value:100,beneficiary_name:'Ana',issue_reason:'friend',expires_on:'2026-12-04'};
  const after={...before,benefit_type:'percent',benefit_value:15,issue_reason:'award'};
  const changes=V.changedFields({before,after});
  assert.equal(changes.length,3);assert.ok(changes.some(x=>x.label==='Benefício' && x.before.includes('100,00') && x.after==='15%'));
  assert.ok(!changes.some(x=>x.label==='Beneficiário'));
  assert.deepEqual(V.changedFields(null),[]);
});
