import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { readResource } from './recursos.mjs';
import { preparePlan, applyPlan, prepareUndo } from './planos.mjs';
import { createFileJournal } from './recibos.mjs';
import { summarizeSellerSales, summarizeReportedSellerSales, calculateReportedCommission } from './vendas.mjs';
import { buildRoutingUpdates } from './impressao.mjs';
import { readOccurrences, readMandatoryGroups, readLinks, planLinks, applyLinks } from './observacoes.mjs';
import { summarizePlan as summarizeCompositionPlan } from './composicoes.mjs';
export { connectObservedSession, beginSessionCapture, finishSessionCapture } from './sessao_browser.mjs';
export { createCompositionClient, summarizePlan as summarizeCompositionPlan } from './composicoes.mjs';
export { createComponentClient, createComponentPlan, applyComponentPlan } from './components.mjs';
export { createCardapioMigrationRunner, createMigrationRunner } from './migrar-cardapio.mjs';
export { connectCompositionSession } from './sessao-composicoes.mjs';

export const COMMANDS = Object.freeze([
  { name: 'produtos.listar', status: 'leitura validada', purpose: 'Localizar produtos ativos por nome ou código.' },
  { name: 'produtos.editar.planejar', status: 'prévia; escrita a validar', purpose: 'Preparar alteração de nome e descrição de produtos.' },
  { name: 'produtos.cadastrar.preparar', status: 'preparação; criação a validar', purpose: 'Organizar os dados necessários ao cadastro, preço e impressão.' },
  { name: 'precos.tabelas.listar', status: 'leitura validada', purpose: 'Conferir tabelas e vigências da unidade.' },
  { name: 'precos.listar', status: 'leitura validada', purpose: 'Consultar preços por tabela e vigência.' },
  { name: 'precos.planejar', status: 'prévia; escrita a validar', purpose: 'Preparar preços com valores anteriores e propostos.' },
  { name: 'loja.produtos.auditar', status: 'validado', purpose: 'Conferir cancelamento, rotas e produtos sem impressora.' },
  { name: 'loja.impressoras.listar', status: 'validado', purpose: 'Identificar impressoras por código, nome e modelo.' },
  { name: 'loja.impressoras.nomear', status: 'validado', purpose: 'Preparar nomes dos destinos sem alterar conexões.' },
  { name: 'loja.impressoras.planejar', status: 'validado', purpose: 'Preparar a rota de produção por produto.' },
  { name: 'impressao.organizar', status: 'validado', purpose: 'Preparar rotas por fonte do catálogo e regra Balcão/Cozinha/Bar.' },
  { name: 'loja.cancelamento.planejar', status: 'validado', purpose: 'Preparar impressão de cancelamento nos produtos escolhidos.' },
  { name: 'observacoes.listar', status: 'leitura validada', purpose: 'Listar o catálogo histórico de observações e seus grupos obrigatórios.' },
  { name: 'observacoes.vinculos.listar', status: 'leitura validada', purpose: 'Mostrar as observações ligadas a cada produto.' },
  { name: 'observacoes.vinculos.planejar', status: 'validado', purpose: 'Preparar inclusão ou retirada de observações por produto.' },
  { name: 'composicoes.grupos.listar', client: 'compositionClient', status: 'leitura validada; cliente injetado', purpose: 'Listar os grupos promocionais cadastrados.' },
  { name: 'composicoes.itens.listar', client: 'compositionClient', status: 'leitura validada; cliente injetado', purpose: 'Conferir os componentes de um grupo.' },
  { name: 'composicoes.vinculos.listar', client: 'compositionClient', status: 'leitura validada; cliente injetado', purpose: 'Conferir os grupos e limites de um produto.' },
  { name: 'composicoes.grupos.criar.planejar', client: 'compositionClient', status: 'validado; cliente injetado', purpose: 'Preparar um grupo novo pelo contrato observado.' },
  { name: 'composicoes.itens.planejar', client: 'compositionClient', status: 'validado; cliente injetado', purpose: 'Preparar a inclusão de componentes em um grupo.' },
  { name: 'composicoes.vinculos.planejar', client: 'compositionClient', status: 'validado; cliente injetado', purpose: 'Preparar a criação ou os limites dos grupos do produto.' },
  { name: 'composicoes.vinculos.remover.planejar', client: 'compositionClient', status: 'validado; cliente injetado', purpose: 'Preparar a retirada de grupos após conferir seus substitutos.' },
  { name: 'composicoes.tipos.planejar', client: 'compositionClient', status: 'validado; cliente injetado', purpose: 'Preparar somente o tipo Promoção Combinada dos produtos ativos.' },
  { name: 'componentes.planejar', client: 'componentClient', status: 'validado; cliente injetado', purpose: 'Preparar componentes com imposto, preço e vínculo de loja observados.' },
  { name: 'plano.aplicar', status: 'validado', purpose: 'Aplicar o plano salvo com recibo e releitura.' },
  { name: 'plano.reverter', status: 'validado em testes', purpose: 'Preparar uma reversão a partir de recibo concluído.' },
  { name: 'recibo.consultar', status: 'validado', purpose: 'Conferir progresso e falhas sem expor os dados completos.' },
  { name: 'vendas.garcons.consultar', status: 'leitura validada', purpose: 'Consultar a produtividade oficial por vendedor e período de movimento de caixa.' },
  { name: 'vendas.garcons.comissao', status: 'fonte validada; regra comercial necessária', purpose: 'Consultar o período e calcular comissão sobre a base e o percentual informados.' },
  { name: 'vendas.garcons.resumir', status: 'cálculo testado', purpose: 'Resumir dados já normalizados de outra fonte, com regra explícita.' },
]);

function money(value) {
  if (typeof value !== 'number' && (typeof value !== 'string' || !/^\d+(?:[,.]\d{1,2})?$/.test(value))) throw new Error('Informe o preço em reais, sem separador de milhar.');
  const result = typeof value === 'number' ? value : Number(value.replace(',', '.'));
  if (!Number.isFinite(result) || result <= 0 || !Number.isSafeInteger(Math.round(result * 100)) || Math.abs(result * 100 - Math.round(result * 100)) > 1e-6) throw new Error('O preço precisa ser positivo, com até duas casas decimais.');
  return result;
}
const selectPublic = (rows, fields, args) => {
  const limit = args.limit ?? 20;
  if (!Number.isSafeInteger(limit) || limit < 1 || limit > 500) throw new Error('Informe um limite entre 1 e 500.');
  const normalize = text => String(text ?? '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
  const filtered = args.search ? rows.filter(row => fields.some(field => normalize(row[field]).includes(normalize(args.search)))) : rows;
  return { total: rows.length, matches: filtered.length, returned: Math.min(filtered.length, limit),
    rows: filtered.slice(0, limit).map(row => Object.fromEntries(fields.map(field => [field, row[field]]))) };
};
const updatesOf = args => {
  if (!Array.isArray(args.updates) || !args.updates.length || args.updates.some(row => !row || typeof row !== 'object')) throw new Error('Informe uma lista de registros e alterações desejadas.');
  return args.updates;
};

const OPTIONAL_PLAN_METHODS = Object.freeze({
  'composition-group-create': ['compositionClient', 'applyGroupCreation'],
  'composition-group-items-add': ['compositionClient', 'applyGroupItems'],
  'composition-parent-bindings': ['compositionClient', 'applyBindings'],
  'composition-parent-bindings-remove': ['compositionClient', 'applyBindingRemovals'],
  'composition-product-type': ['compositionClient', 'applyProductTypes'],
  'new-menu-components': ['componentClient', 'apply'],
});
export function createTeknisa({ request, target, operator, journal = createFileJournal(),
  compositionClient, componentClient, migrationRunner }) {
  if (typeof request !== 'function') throw new Error('Conecte uma sessão autenticada antes de usar a ferramenta.');
  target = Object.freeze(structuredClone(target));
  if (migrationRunner && (!migrationRunner.target || !Object.isFrozen(migrationRunner.target)
    || ['organization', 'branch', 'store'].some(key => migrationRunner.target[key] !== target[key])))
    throw new Error('O executor avançado precisa expor um destino imutável igual ao da ferramenta.');
  const clients = { compositionClient, componentClient, migrationRunner };
  const client = name => {
    const value = clients[name];
    if (!value) throw new Error(`Configure ${name} com a sessão e os contratos validados antes de usar este comando.`);
    if (value.target && ['organization', 'branch', 'store'].some(key => value.target[key] !== undefined && value.target[key] !== target[key]))
      throw new Error('O cliente injetado pertence a outro destino.');
    return value;
  };
  const commands = () => structuredClone(COMMANDS.map(entry => ({ ...entry,
    ...(entry.client ? { configured: !!clients[entry.client] } : {}) })));
  const assertPlanTarget = prepared => {
    if (!prepared?.target || ['organization', 'branch', 'store'].some(key => prepared.target[key] !== undefined && prepared.target[key] !== target[key]))
      throw new Error('O plano pertence a outro destino.');
  };
  const saveOptionalPlan = async prepared => {
    assertPlanTarget(prepared);
    if (!Object.hasOwn(OPTIONAL_PLAN_METHODS, prepared.kind)) throw new Error('Tipo de plano sem aplicação validada.');
    const planId = prepared.id || randomUUID();
    await journal.save({ id: planId, status: 'prepared', plan: prepared, batches: [] });
    const summary = prepared.kind === 'new-menu-components'
      ? { kind: prepared.kind, components: prepared.entries.length,
        sample: prepared.entries.slice(0, 8).map(entry => ({ key: entry.definition.key, name: entry.definition.name, code: entry.definition.rawTreeCode })) }
      : summarizeCompositionPlan(prepared);
    return { ...summary, planId };
  };
  const applyOptionalPlan = async record => {
    assertPlanTarget(record.plan);
    if (record.status === 'completed') return record.result;
    if (record.status !== 'prepared') throw new Error('Consulte a execução interrompida e prepare uma nova prévia antes de aplicar.');
    const [clientName, method] = OPTIONAL_PLAN_METHODS[record.plan.kind];
    const adapter = client(clientName);
    if (typeof adapter[method] !== 'function') throw new Error('O cliente não oferece a aplicação validada deste plano.');
    if (typeof journal.lock !== 'function') throw new Error('O diário precisa impedir gravações simultâneas na unidade.');
    return journal.lock(target, async () => {
      record.status = 'running'; await journal.save(record);
      try {
        const details = await adapter[method](record.plan);
        if (details?.status !== 'completed') throw new Error('O cliente não confirmou a conclusão do plano.');
        const entries = details.entries || [];
        record.status = 'completed'; record.details = details;
        record.batches = entries.map((entry, index) => ({ index: index + 1, status: entry.status,
          keys: [entry.productId || entry.groupId || entry.definition?.key || String(index)], verified: entry.status === 'verified' ? 1 : 0 }));
        record.result = { planId: record.id, status: 'completed',
          verified: entries.filter(entry => entry.status === 'verified').length,
          alreadyDesired: entries.filter(entry => ['already_desired', 'already_present'].includes(entry.status)).length };
        await journal.save(record); return record.result;
      } catch (error) { record.status = 'interrupted'; record.errorCode = error.code || 'INJECTED_CLIENT_FAILED';
        await journal.save(record); throw error; }
    });
  };
  const read = (name, args = {}) => readResource(request, name, { ...target, ...args.scope });
  const plan = (name, args, updates) => preparePlan({ request, name, target: { ...target, ...args.scope }, updates, journal });
  return Object.freeze({
    target,
    commands,
    async run(command, args = {}) {
      if (command === 'comandos') return commands();
      if (!COMMANDS.some(entry => entry.name === command)) throw new Error('Comando desconhecido. Use comandos para ver as funções cadastradas.');
      switch (command) {
        case 'composicoes.grupos.listar': return selectPublic(await client('compositionClient').readGroups(),
          ['CDGRUPROMOC', 'NMGRUPROMOC', 'IDATIVO'], args);
        case 'composicoes.itens.listar': return selectPublic(await client('compositionClient').readGroupItems(args.groupId),
          ['CDGRUPROMOC', 'CDPRODUTO', 'CDARVPROD', 'NMPRODUTO'], args);
        case 'composicoes.vinculos.listar': return selectPublic(await client('compositionClient').readBindings(args.productId),
          ['CDPRODPROMOCAO', 'CDGRUPROMOC', 'NMGRUPROMOC', 'QTPRGRUPROMIN', 'QTPRGRUPPROMOC'], args);
        case 'composicoes.grupos.criar.planejar': return saveOptionalPlan(await client('compositionClient').previewGroupCreation({ groupId: args.groupId, name: args.name }));
        case 'composicoes.itens.planejar': return saveOptionalPlan(await client('compositionClient').previewGroupItems({ groupId: args.groupId, productIds: args.productIds }));
        case 'composicoes.vinculos.planejar': return saveOptionalPlan(await client('compositionClient').previewBindings(args.changes));
        case 'composicoes.vinculos.remover.planejar': return saveOptionalPlan(await client('compositionClient').previewBindingRemovals(args.changes));
        case 'composicoes.tipos.planejar': return saveOptionalPlan(await client('compositionClient').previewProductTypes(args.productIds));
        case 'componentes.planejar': return saveOptionalPlan(await client('componentClient').preview(args.definitions));
        case 'produtos.listar': return selectPublic(await read('produtos', args), ['CDPRODUTO', 'CDARVPROD', 'NMPRODUTO', 'SGUNIDADE', 'IDESTOCOMP'], args);
        case 'precos.tabelas.listar': return selectPublic(await read('precos.tabelas', args), ['CDTABEPREC', 'NMTABEPREC', 'DTINIVGPREC', 'DTFINVGPREC', 'IDATIVO'], args);
        case 'precos.listar': return selectPublic(await read('precos', args), ['CDPRODUTO', 'CDARVPROD', 'NMPRODUTO', 'VRPRECITEM', 'VRPRECITEMDLV', 'VRPRECITEMCMD'], args);
        case 'loja.impressoras.listar': return selectPublic(await read('loja.impressoras', args), ['NRSEQIMPRLOJA', 'NMIMPRLOJA', 'NMIMPRESSORA', 'IDATIVO'], args);
        case 'loja.produtos.auditar': {
          const rows = await read('loja.produtos', args), routes = {};
          for (const row of rows) routes[row.NRSEQIMPRPROD || 'sem_rota'] = (routes[row.NRSEQIMPRPROD || 'sem_rota'] || 0) + 1;
          return { total: rows.length, cancellationEnabled: rows.filter(row => row.IDIMPCANITEM === 'S').length,
            cancellationDisabled: rows.filter(row => row.IDIMPCANITEM === 'N').length, routes,
            withoutPrinter: rows.filter(row => !row.NRSEQIMPRPROD).map(row => ({ id: row.CDPRODUTO, name: row.NMPRODUTO })) };
        }
        case 'loja.cancelamento.planejar': {
          if (typeof args.enabled !== 'boolean' || (args.all !== true && !Array.isArray(args.productIds))) throw new Error('Informe enabled e os códigos escolhidos, ou all: true.');
          if (args.all === true && args.productIds !== undefined) throw new Error('Escolha a lista de produtos ou all: true para todos.');
          const rows = await read('loja.produtos', args);
          const ids = args.all === true ? rows.map(row => row.CDPRODUTO) : args.productIds;
          return plan('loja.produtos', args, ids.map(id => ({ id, set: { IDIMPCANITEM: args.enabled ? 'S' : 'N' } })));
        }
        case 'loja.impressoras.nomear': return plan('loja.impressoras', args, updatesOf(args).map(row => ({ id: row.id, set: { NMIMPRLOJA: row.name } })));
        case 'loja.impressoras.planejar': return plan('loja.produtos', args, updatesOf(args).map(row => ({ id: row.id, set: row.set || { NRSEQIMPRPROD: row.printerCode } })));
        case 'impressao.organizar': {
          const proposal = buildRoutingUpdates(await read('loja.produtos', args), args.sources, args.roles);
          if (proposal.unresolved.length) return { status: 'needs_decision', counts: proposal.counts, unresolved: proposal.unresolved, outsideSource: proposal.outsideSource };
          const summary = await plan('loja.produtos', args, proposal.updates);
          return { ...summary, counts: proposal.counts, outsideSource: proposal.outsideSource };
        }
        case 'produtos.editar.planejar': return plan('produtos', args, args.updates);
        case 'precos.planejar': return plan('precos', args, updatesOf(args).map(row => ({ id: row.id, key: row.key, set: { VRPRECITEM: money(row.price) } })));
        case 'produtos.cadastrar.preparar': {
          const required = ['name', 'tree', 'unit', 'productType', 'price', 'productionRole'];
          const missing = required.filter(field => args[field] === undefined || args[field] === '');
          if (args.name !== undefined && (typeof args.name !== 'string' || !args.name.trim() || args.name.length > 50)) throw new Error('O nome deve ter entre 1 e 50 caracteres.');
          if (args.price !== undefined && !(money(args.price) > 0)) throw new Error('O preço deve ser positivo.');
          if (args.productionRole !== undefined && !['balcao', 'cozinha', 'bar', 'sem_producao'].includes(args.productionRole)) throw new Error('Informe o destino de produção do novo produto.');
          return { status: missing.length ? 'missing_fields' : 'ready_for_contract_validation', missing,
            next: 'Validar o cadastro pela interface com o primeiro produto real solicitado; incluir preço, impressão e caixa na conferência.' };
        }
        case 'observacoes.listar': return { occurrences: await readOccurrences(request, target, args.group),
          mandatoryGroups: await readMandatoryGroups(request, target, args.group) };
        case 'observacoes.vinculos.listar': {
          const links = await readLinks(request, target, args.group);
          return args.search ? links.filter(item => item.name.toLowerCase().includes(String(args.search).toLowerCase())) : links;
        }
        case 'observacoes.vinculos.planejar': return planLinks({ request, target, changes: args.changes, journal, group: args.group });
        case 'plano.aplicar': {
          const receipt = await journal.load(args.planId);
          if (['organization', 'branch', 'store'].some(field => target[field] !== undefined && receipt.plan.target[field] !== undefined && receipt.plan.target[field] !== target[field])) throw new Error('O plano pertence a outro destino.');
          if (Object.hasOwn(OPTIONAL_PLAN_METHODS, receipt.plan.kind)) return applyOptionalPlan(receipt);
          if (receipt.plan.kind === 'observacoes.vinculos') return applyLinks({ request, planId: args.planId, journal });
          return applyPlan({ request, planId: args.planId, journal, operator, batchSize: args.batchSize ?? 25 });
        }
        case 'plano.reverter': {
          const receipt = await journal.load(args.planId);
          if (Object.hasOwn(OPTIONAL_PLAN_METHODS, receipt.plan.kind)) throw new Error('A reversão deste tipo exige uma nova prévia com o estado atual.');
          if (receipt.plan.kind !== 'observacoes.vinculos') return prepareUndo({ request, planId: args.planId, journal });
          if (receipt.status !== 'completed') throw new Error('A reversão exige um recibo concluído. Para falhas parciais, consulte o estado e retome o plano.');
          return planLinks({ request, target: receipt.plan.target, group: receipt.plan.group, journal,
            changes: receipt.plan.items.map(item => ({ productId: item.productId, add: item.remove, remove: item.add })) });
        }
        case 'recibo.consultar': {
          const receipt = await journal.load(args.planId);
          return { planId: receipt.id, status: receipt.status, result: receipt.result, errorCode: receipt.errorCode,
            batches: receipt.batches.map(batch => ({ index: batch.index, status: batch.status, requested: batch.keys?.length ?? 1,
              verified: batch.verified ?? (batch.status === 'verified' ? 1 : 0) })) };
        }
        case 'vendas.garcons.resumir': return summarizeSellerSales(args);
        case 'vendas.garcons.consultar':
        case 'vendas.garcons.comissao': {
          const reportTarget = { ...target, ...args.scope, from: args.from, to: args.to };
          const report = summarizeReportedSellerSales(await readResource(request, 'vendas.garcons', reportTarget), reportTarget);
          return command.endsWith('.comissao') ? calculateReportedCommission(report, args.rules) : report;
        }
      }
    },
  });
}

if (typeof process !== 'undefined' && process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (!process.argv[2] || ['ajuda', 'comandos'].includes(process.argv[2])) {
    console.log(JSON.stringify({ usage: 'Importe createTeknisa no runtime do navegador e forneça a sessão observada. Guia: scripts/teknisa/README.md', commands: COMMANDS }, null, 2));
  } else { console.error('Use comandos ou ajuda. As operações autenticadas usam o runtime documentado do navegador.'); process.exitCode = 2; }
}
