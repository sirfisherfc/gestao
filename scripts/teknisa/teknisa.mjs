import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { readResource } from './recursos.mjs';
import { preparePlan, applyPlan, prepareUndo } from './planos.mjs';
import { createFileJournal } from './recibos.mjs';
import { summarizeSellerSales, summarizeReportedSellerSales, calculateReportedCommission } from './vendas.mjs';
import { buildRoutingUpdates } from './impressao.mjs';
export { connectObservedSession, beginSessionCapture, finishSessionCapture } from './sessao_browser.mjs';

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

export function createTeknisa({ request, target, operator, journal = createFileJournal() }) {
  if (typeof request !== 'function') throw new Error('Conecte uma sessão autenticada antes de usar a ferramenta.');
  target = Object.freeze(structuredClone(target));
  const read = (name, args = {}) => readResource(request, name, { ...target, ...args.scope });
  const plan = (name, args, updates) => preparePlan({ request, name, target: { ...target, ...args.scope }, updates, journal });
  return Object.freeze({
    commands: () => structuredClone(COMMANDS),
    async run(command, args = {}) {
      if (command === 'comandos') return structuredClone(COMMANDS);
      if (!COMMANDS.some(entry => entry.name === command)) throw new Error('Comando desconhecido. Use comandos para ver as funções cadastradas.');
      switch (command) {
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
        case 'plano.aplicar': {
          const receipt = await journal.load(args.planId);
          if (['organization', 'branch', 'store'].some(field => target[field] !== undefined && receipt.plan.target[field] !== target[field])) throw new Error('O plano pertence a outro destino.');
          return applyPlan({ request, planId: args.planId, journal, operator, batchSize: args.batchSize ?? 25 });
        }
        case 'plano.reverter': return prepareUndo({ request, planId: args.planId, journal });
        case 'recibo.consultar': {
          const receipt = await journal.load(args.planId);
          return { planId: receipt.id, status: receipt.status, result: receipt.result, errorCode: receipt.errorCode,
            batches: receipt.batches.map(batch => ({ index: batch.index, status: batch.status, requested: batch.keys.length, verified: batch.verified ?? 0 })) };
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
