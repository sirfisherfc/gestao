import test from 'node:test';
import assert from 'node:assert/strict';
import { createComponentPlan, applyComponentPlan, createComponentClient, buildProductPayload, buildStorePayload, chunkComponentDefinitions, COMPONENT_PATHS } from './components.mjs';

const d = { key: 'arroz_brocolis', name: 'ARROZ DE BROCOLIS', parentCode: '80005080', rawTreeCode: '8000508002', printer: '00001' };
const product = { NRORG:5482, CDPRODUTO:'8000508002', CDARVPROD:d.rawTreeCode, NMPRODUTO:d.name,
  SGUNIDADE:'UN', IDESTOCOMP:'E', IDPRODATIVPR:'S', CDPRODNIVANTE:d.parentCode };
const templates = {
  product: { requestType:'Row', row:{__is_new:true,CDARVPRODNIVANTE:'80024006',CDPRODNIVANTE:'80024006',
    CDARVPROD:'8.00.24.006.00',NMPRODUTO:'MASSA',SGUNIDADE:'UN',IDESTOCOMP:'E',IDPRODATIVPR:'S',CDCLASFISC:''},origin:{containerLabel:'Produto',widgetLabel:'Estoque'} },
  tax: { requestType:'DataSet',dataset:[{__is_new:true,IDTPIMPOSFIS:'T'}],origin:{widgetName:'impostos'} },
  price: { requestType:'DataSet',dataset:[{__is_new:true}],origin:{widgetName:'prodPrec'} },
  // Fixture is deliberately synthetic. Production requires a complete UI capture.
  store: { requestType:'DataSet',dataset:[{__is_new:true,CDPRODINICIAL:'',NMPRODINICIAL:'',NIVELINICIAL:'T'}],origin:{widgetName:'productByStoreWidget'} },
};
function mock() {
  const state = { products:[{NRORG:5482,CDPRODUTO:'0000000112',CDARVPROD:'8000508000',CDPRODNIVANTE:d.parentCode}],tax:[],prices:[],store:[],writes:[],checkpoints:[] };
  const readProducts = async()=>structuredClone(state.products), readTax=async()=>structuredClone(state.tax),
    readPrices=async()=>structuredClone(state.prices), readStore=async()=>structuredClone(state.store);
  const checkpoint=async value=>{state.checkpoints.push(structuredClone(value));};
  const request=async(path,body)=>{
    const last=state.checkpoints.at(-1);
    assert.equal(last.entries.at(-1).stages.at(-1).status,'sending','Durable checkpoint must precede the write');
    state.writes.push({path,body:structuredClone(body)});
    if(path===COMPONENT_PATHS.product)state.products.push(structuredClone(product));
    else {
      const row=body.dataset[0];
      if(path===COMPONENT_PATHS.tax)state.tax.push({...row,CDFILIAL:'0002',__is_new:false});
      if(path===COMPONENT_PATHS.price)state.prices.push({...row,CDFILIAL:'0002',CDTABEPREC:'001',DTINIVGPREC:'06/07/2026 00:00:00',__is_new:false});
      if(path===COMPONENT_PATHS.store)state.store.push({...row,CDPRODUTO:product.CDPRODUTO,__is_new:false});
    }
    return {result:1};
  };
  return {state,readProducts,readTax,readPrices,readStore,checkpoint,request};
}
test('the injected component facade reuses the validated plan and apply functions', async () => {
  const m = mock(), client = createComponentClient({ ...m, templates });
  assert.deepEqual(client.target, { organization: 5482, branch: '0002', store: '0001' });
  const plan = await client.preview([d]); assert.equal(m.state.writes.length, 0);
  const receipt = await client.apply(plan); assert.equal(receipt.status, 'completed'); assert.equal(m.state.writes.length, 4);
});
test('product body preserves captured marker fields and changes only the intended identity',()=>{
  const body=buildProductPayload(templates.product,d);
  assert.equal(body.row.CDARVPROD,'8.00.05.080.02');
  assert.equal(body.row.CDPRODNIVANTE,d.parentCode);
  assert.equal(body.row.CDCLASFISC,'');
  assert.equal(body.row.__is_new,true);
  assert.equal(templates.product.row.NMPRODUTO,'MASSA');
});
test('conflicting existing product is rejected before any write',async()=>{
  const m=mock();m.state.products.push({...product,NMPRODUTO:'OUTRO PRODUTO'});
  await assert.rejects(createComponentPlan({...m,definitions:[d]}),{code:'COMPONENT_PRODUCT_DIFFERENCE'});
  assert.equal(m.state.writes.length,0);
});
test('unknown parent and duplicate definitions are rejected',async()=>{
  const m=mock();m.state.products=[];
  await assert.rejects(createComponentPlan({...m,definitions:[d]}),{code:'UNCONFIRMED_PARENT'});
  await assert.rejects(createComponentPlan({...m,definitions:[d,d]}),{code:'INVALID_COMPONENT_PLAN'});
});
test('creates and confirms all four stages with checkpoints',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});
  const receipt=await applyComponentPlan({...m,plan,templates});
  assert.equal(receipt.status,'completed');assert.equal(receipt.verified,1);assert.equal(m.state.writes.length,4);
  assert.equal(m.state.tax[0].CDCSTICMS,'102');assert.equal(m.state.tax[0].CDCFOPPFIS,'5102');assert.equal(m.state.tax[0].CDCSTPISCOF,'99');
  assert.equal(m.state.prices[0].VRPRECITEM,0.01);assert.equal(m.state.store[0].CDLOJA,'0001');
  assert.equal(m.state.store[0].NRSEQIMPRPROD,'00001');
});
test('new preview after completion safely skips confirmed components',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});await applyComponentPlan({...m,plan,templates});
  m.state.writes=[];
  const again=await createComponentPlan({...m,definitions:[d]});const result=await applyComponentPlan({...m,plan:again,templates});
  assert.equal(m.state.writes.length,0);assert.equal(result.status,'completed');
});
test('partial or different existing tax is not overwritten',async()=>{
  const m=mock();m.state.products.push(product);m.state.tax.push({NRORG:5482,CDFILIAL:'0002',CDPRODUTO:product.CDPRODUTO,CDIMPOSTO:'00',IDTPIMPOSFIS:'T',CDCSTICMS:null});
  await assert.rejects(createComponentPlan({...m,definitions:[d]}),{code:'EXISTING_COMPONENT_STAGE_DIFFERENCE'});
  assert.equal(m.state.writes.length,0);
});
test('incomplete store template blocks the entire execution before creating products',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});
  await assert.rejects(applyComponentPlan({...m,plan,templates:{...templates,store:{requestType:'DataSet',dataset:[{}],origin:{}}}}),{code:'INCOMPLETE_STORE_TEMPLATE'});
  assert.equal(m.state.writes.length,0);
  assert.throws(()=>buildStorePayload({requestType:'DataSet',dataset:[{}],origin:{}},product,d),{code:'INCOMPLETE_STORE_TEMPLATE'});
});
test('failed write has no automatic retry and leaves an interrupted receipt',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});let attempts=0;
  await assert.rejects(applyComponentPlan({...m,plan,templates,request:async()=>{attempts++;throw new Error('unknown result');}}));
  assert.equal(attempts,1);assert.equal(m.state.checkpoints.at(-1).status,'interrupted');
  assert.equal(m.state.checkpoints.at(-1).entries[0].stages[0].status,'sending');
});
test('readback difference stops remaining stages',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});
  const request=async(path,body)=>{await m.request(path,body);if(path===COMPONENT_PATHS.tax)m.state.tax[0].CDCSTPISCOF='01';};
  await assert.rejects(applyComponentPlan({...m,request,plan,templates}),{code:'COMPONENT_READBACK_DIFFERENCE'});
  assert.equal(m.state.writes.length,2);assert.equal(m.state.checkpoints.at(-1).status,'interrupted');
});
test('checksum or stale plans cannot trigger writes',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});plan.entries[0].definition.name='ALTERADO';
  await assert.rejects(applyComponentPlan({...m,plan,templates}),{code:'INVALID_COMPONENT_PLAN'});
  const stale=await createComponentPlan({...m,definitions:[d],now:()=>new Date('2020-01-01T00:00:00Z')});
  await assert.rejects(applyComponentPlan({...m,plan:stale,templates}),{code:'EXPIRED_COMPONENT_PLAN'});
  assert.equal(m.state.writes.length,0);
});
test('store uses the chosen printer and current timestamp while preserving captured interval/operator fields',()=>{
  const template=structuredClone(templates.store);
  Object.assign(template.dataset[0],{NMIMPRPROD:'COZINHA',CDOPERADOR:5482,DTATU:'31/10/2026 18:02:35'});
  const bar={...d,printer:'00004'},body=buildStorePayload(template,product,bar,new Date('2026-10-31T22:30:45Z'));
  assert.equal(body.dataset[0].NMIMPRPROD,'BAR');assert.equal(body.dataset[0].NRSEQIMPRPROD,'00004');
  assert.equal(body.dataset[0].CDOPERADOR,5482);assert.equal(body.dataset[0].CDPRODINICIAL,'');
  assert.equal(body.dataset[0].NMPRODINICIAL,'');assert.equal(body.dataset[0].NIVELINICIAL,'T');
  assert.equal(body.dataset[0].DTATU,'31/10/2026 19:30:45');
  assert.equal(template.dataset[0].DTATU,'31/10/2026 18:02:35');
});
test('a tax-edit template is blocked before creating a new SKU',async()=>{
  const m=mock(),plan=await createComponentPlan({...m,definitions:[d]});
  const bad=structuredClone(templates);bad.tax.dataset[0].__is_new=false;
  await assert.rejects(applyComponentPlan({...m,plan,templates:bad}),{code:'INVALID_TAX_TEMPLATE'});
  assert.equal(m.state.writes.length,0);
});
test('chunks cap the work at four components and retain all definitions',()=>{
  const definitions=Array.from({length:11},(_,i)=>({...d,key:`component_${i}`,rawTreeCode:`80005080${String(i+1).padStart(2,'0')}`}));
  const chunks=chunkComponentDefinitions(definitions);
  assert.deepEqual(chunks.map(x=>x.length),[4,4,3]);assert.equal(chunks.flat().length,11);
  assert.throws(()=>chunkComponentDefinitions(definitions,5),{code:'INVALID_CHUNK_SIZE'});
});
