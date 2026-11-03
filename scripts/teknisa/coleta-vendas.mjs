import { createHash, randomUUID } from 'node:crypto';
import { readResource, validateTarget } from './recursos.mjs';
import { summarizeReportedSellerSales } from './vendas.mjs';

const DAY_MS = 86400000;
const KIND = 'daily-seller-comparison';
export const SALES_COLLECTION_LIMIT = 7;
const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
const scopeOf = target => ({ organization: target?.organization, branch: target?.branch, store: target?.store });
const reportDate = iso => `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}`;

function isoDay(text) {
  if (typeof text !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(text)) throw new Error('Informe as datas no formato AAAA-MM-DD.');
  const value = new Date(`${text}T00:00:00Z`);
  if (!Number.isFinite(value.getTime()) || value.toISOString().slice(0, 10) !== text) throw new Error('O período contém uma data inválida.');
  return value;
}

function todayInFortaleza(now) {
  if (!(now instanceof Date) || !Number.isFinite(now.getTime())) throw new Error('Informe um horário de referência válido.');
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Fortaleza', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now).map(part => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day}`;
}

/** Planeja consultas ao relatório já observado. A cobertura exclui N/A. */
export function prepareDailySalesCollection({ target, from, to, now = new Date() }) {
  const today = todayInFortaleza(now);
  const yesterday = new Date(isoDay(today).getTime() - DAY_MS).toISOString().slice(0, 10);
  to ??= yesterday; from ??= to;
  const first = isoDay(from), last = isoDay(to);
  const count = (last - first) / DAY_MS + 1;
  if (count < 1 || count > SALES_COLLECTION_LIMIT) throw new Error('Consulte de um a sete dias por execução.');
  if (to >= today) throw new Error('Consulte até ontem em Fortaleza; o dia atual ainda está em andamento.');
  const scope = scopeOf(target);
  validateTarget({ ...scope, from: reportDate(from), to: reportDate(to) }, 'vendas.garcons');
  return {
    version: 1, kind: KIND, target: scope, from, to,
    days: Array.from({ length: count }, (_, i) => new Date(first.getTime() + i * DAY_MS).toISOString().slice(0, 10)),
    source: 'Teknisa: Produtividade por Vendedor', periodBasis: 'DTMOVTURCAIX', timeZone: 'America/Fortaleza',
    unassignedExcluded: true, financialImportAllowed: false, automaticExecutionReady: false,
    pending: ['Validar a coleta por dia em uma sessão real',
      'Obter documentação e acesso de serviço à Sale API',
      'Conferir vendas sem vendedor, cancelamentos, pagamentos e fechamento'],
  };
}

function assertRecord(record, target, now, from, to, collectionId) {
  if (record?.kind !== KIND || record.id !== collectionId || !Array.isArray(record.batches)
      || !['prepared', 'running', 'interrupted', 'collected_with_limits'].includes(record.status)
      || record.planHash !== hash(record.plan)) {
    throw new Error('O recibo de coleta está incompleto ou foi alterado.');
  }
  const expected = prepareDailySalesCollection({ target, from: record.plan.from, to: record.plan.to, now });
  if (hash(expected) !== record.planHash || (from !== undefined && from !== record.plan.from)
      || (to !== undefined && to !== record.plan.to)) throw new Error('O recibo pertence a outro destino ou período.');
  if (record.batches.length !== expected.days.length || record.batches.some((batch, index) =>
    batch.day !== expected.days[index] || !['pending', 'querying', 'failed', 'observed', 'empty_unverified'].includes(batch.status)
    || (['observed', 'empty_unverified'].includes(batch.status) && (!batch.report
      || !Number.isSafeInteger(batch.report.lines) || batch.report.lines < 0 || !Array.isArray(batch.report.sellers)
      || batch.reportHash !== hash(batch.report)))
    || (record.status === 'collected_with_limits' && !['observed', 'empty_unverified'].includes(batch.status)))) {
    throw new Error('Os dias ou os dados do recibo de coleta foram alterados.');
  }
}

/** Devolve somente cobertura e contagens. Valores e nomes ficam no diário privado. */
export function summarizeDailySalesCollection(record) {
  return {
    collectionId: record.id, status: record.status, target: { ...record.plan.target },
    from: record.plan.from, to: record.plan.to, source: record.plan.source,
    periodBasis: record.plan.periodBasis, timeZone: record.plan.timeZone,
    unassignedExcluded: true, financialImportAllowed: false, automaticExecutionReady: false,
    days: record.batches.map(batch => ({ day: batch.day, status: batch.status,
      ...(batch.report ? { lines: batch.report.lines, sellers: batch.report.sellers.length } : {}),
      ...(batch.errorCode ? { errorCode: batch.errorCode } : {}) })),
  };
}

/** Coleta sequencial, com recibo por dia e retomada. Não escreve no Teknisa ou no banco. */
export async function collectDailySales({ request, target, journal, from, to, collectionId, now = () => new Date() }) {
  if (typeof request !== 'function' || typeof journal?.save !== 'function' || typeof journal?.load !== 'function'
      || typeof journal?.lock !== 'function') throw new Error('Conecte a consulta e o diário privado com bloqueio da unidade.');
  const scope = scopeOf(target);
  return journal.lock(scope, async () => {
    let record;
    if (collectionId !== undefined) {
      record = await journal.load(collectionId);
      assertRecord(record, scope, now(), from, to, collectionId);
      if (record.status === 'collected_with_limits') return summarizeDailySalesCollection(record);
    } else {
      const plan = prepareDailySalesCollection({ target: scope, from, to, now: now() });
      record = { id: randomUUID(), kind: KIND, status: 'prepared', plan, planHash: hash(plan),
        createdAt: now().toISOString(), batches: plan.days.map((day, index) => ({ index: index + 1, day, status: 'pending' })) };
    }
    record.status = 'running'; await journal.save(record);
    for (const batch of record.batches) {
      if (['observed', 'empty_unverified'].includes(batch.status)) continue;
      batch.status = 'querying'; delete batch.errorCode; await journal.save(record);
      let report;
      try {
        const reportTarget = { ...scope, from: reportDate(batch.day), to: reportDate(batch.day) };
        const rows = await readResource(request, 'vendas.garcons', reportTarget);
        report = summarizeReportedSellerSales(rows, reportTarget);
      } catch (error) {
        batch.status = 'failed';
        batch.errorCode = ['SESSION_EXPIRED', 'HTTP_ERROR', 'TIMEOUT', 'INVALID_JSON', 'DISPOSED'].includes(error?.code)
          ? error.code : 'READ_FAILED';
        record.status = 'interrupted'; await journal.save(record);
        return summarizeDailySalesCollection(record);
      }
      batch.report = report; batch.reportHash = hash(report);
      batch.status = report.lines ? 'observed' : 'empty_unverified';
      batch.verified = report.lines; await journal.save(record);
    }
    record.status = 'collected_with_limits'; record.completedAt = now().toISOString();
    await journal.save(record);
    return summarizeDailySalesCollection(record);
  });
}

export async function readDailySalesCollection({ journal, target, collectionId, now = new Date() }) {
  const record = await journal.load(collectionId);
  assertRecord(record, scopeOf(target), now, undefined, undefined, collectionId);
  return summarizeDailySalesCollection(record);
}
