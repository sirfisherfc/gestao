// Optional artifact QA; @napi-rs/canvas is a local test tool, not a product dependency.
// node scripts/ci/render_benefit_vouchers.mjs /absolute/path/to/canvas/module output-directory
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const {createCanvas,loadImage,GlobalFonts}=require(resolve(process.argv[2]));
const V=require('../../assets/voucher-template.js');
GlobalFonts.registerFromPath(resolve(root,'assets/vouchers/fraunces.woff2'),'VoucherSerif');
const logo=await loadImage(resolve(root,'assets/vouchers/logo-emblem.png'));
const deck=await loadImage(resolve(root,'assets/vouchers/deck.webp'));
const out=resolve(process.argv[3] || resolve(root,'tmp/voucher-preview'));
await mkdir(out,{recursive:true});
const base={status:'available',beneficiary_name:'Ana Carolina de Oliveira',benefit_type:'fixed',benefit_value:250,
 code:'A1B2C3',expires_on:'2026-12-04',conditions:['Uso único. Saldo não utilizado é perdido.',
 'Não cumulativo com promoções ou outro voucher na mesma conta.','Válido na unidade Sir Fisher até a data indicada.']};
for(const [name,patch] of [['fixo',{}],['nome-longo',{beneficiary_name:('Ana Carolina de Albuquerque e Oliveira '.repeat(5)).slice(0,160)}],
 ['percentual',{benefit_type:'percent',benefit_value:12.5}],['valor-alto',{benefit_value:9999999999.99}],['sem-espacos',{beneficiary_name:'W'.repeat(160)}]]) {
 const canvas=createCanvas(V.WIDTH,V.HEIGHT),ctx=canvas.getContext('2d');
 const original=ctx.fillText.bind(ctx); const calls=[];
 ctx.fillText=(text,x,y)=>{
   const width=ctx.measureText(text).width;
   const left=ctx.textAlign==='left' ? x : x-width/2;
   assert.ok(left>=24 && left+width<=V.WIDTH-24 && y<V.HEIGHT,`Overflow ${name}: ${text}`);
   calls.push(text);original(text,x,y);
 };
 const v={...base,...patch};
 if(v.benefit_type==='percent')v.conditions=['Desconto sobre a conta inteira. Taxa de serviço opcional. Sem teto em reais.',...v.conditions];
 V.draw(ctx,v,logo,deck);
 assert.ok(calls.join(' ').includes(v.code));
 await writeFile(resolve(out,`${name}.png`),await canvas.encode('png'));
}
console.log('VOUCHER_PNG_RENDER_OK variants=5');
