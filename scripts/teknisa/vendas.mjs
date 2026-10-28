function percentageCents(amount, basisPoints) {
  const value = BigInt(amount) * BigInt(basisPoints), sign = value < 0n ? -1n : 1n;
  return Number(sign * (((value < 0n ? -value : value) + 5000n) / 10000n));
}
/** Dados normalizados de produtos líquidos, separados de taxa de serviço e gorjeta. */
export function summarizeSellerSales({ rows, month, coverage, commissionRules = [] }) {
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(month)) throw new Error('Informe o mês no formato AAAA-MM.');
  if (coverage?.complete !== true || coverage.month !== month || typeof coverage.source !== 'string' || !coverage.source.trim() || !Array.isArray(rows)) {
    return { status: 'unavailable', month, missing: ['Dados completos do período e identificação da fonte'], sellers: null };
  }
  if (!Array.isArray(commissionRules)) throw new Error('Informe as regras de comissão como lista.');
  const rules = new Map();
  for (const rule of commissionRules) {
    if (typeof rule.sellerId !== 'string' || rules.has(rule.sellerId) || rule.base !== 'netProductCents'
        || !Number.isSafeInteger(rule.rateBasisPoints) || rule.rateBasisPoints < 0 || rule.rateBasisPoints > 10000) {
      throw new Error('Informe uma regra de comissão explícita por vendedor, com base e percentual.');
    }
    rules.set(rule.sellerId, rule);
  }
  const seen = new Set(), groups = new Map();
  const formatter = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Fortaleza', year: 'numeric', month: '2-digit' });
  for (const row of rows) {
    if (typeof row.id !== 'string' || !row.id || seen.has(row.id) || typeof row.sellerId !== 'string' || !row.sellerId
        || !Number.isSafeInteger(row.netProductCents) || !/T.+(?:Z|[+-]\d{2}:\d{2})$/.test(row.occurredAt)
        || !Number.isFinite(Date.parse(row.occurredAt))) throw new Error('A fonte contém movimento duplicado ou dados incompletos.');
    seen.add(row.id);
    const parts = Object.fromEntries(formatter.formatToParts(new Date(row.occurredAt)).map(part => [part.type, part.value]));
    if (`${parts.year}-${parts.month}` !== month) throw new Error('A fonte contém movimento fora do mês em Fortaleza.');
    const seller = groups.get(row.sellerId) || { sellerId: row.sellerId, records: 0, netProductCents: 0 };
    seller.records++; seller.netProductCents += row.netProductCents;
    if (!Number.isSafeInteger(seller.netProductCents)) throw new Error('O total excede a precisão suportada.');
    groups.set(row.sellerId, seller);
  }
  const sellers = [...groups.values()].sort((a, b) => a.sellerId.localeCompare(b.sellerId)).map(seller => {
    const rule = rules.get(seller.sellerId);
    let commission = { status: 'missing_rule', amountCents: null };
    if (rule) {
      commission = { status: 'calculated', base: rule.base, rateBasisPoints: rule.rateBasisPoints,
        amountCents: percentageCents(seller.netProductCents, rule.rateBasisPoints) };
    }
    return { ...seller, commission };
  });
  return { status: 'complete', month, source: coverage.source, records: rows.length, sellers };
}

const reportedFields = Object.freeze({
  reportedTotalCents: 'VRFINALITEM', reportedNetCents: 'VRLIQUIDO', reportedNetWithoutSurchargeCents: 'VRLIQACRES',
  surchargeCents: 'ACR', discountCents: 'DES', tipCents: 'VRGORJETA', deliveryFeeCents: 'VRTXENTREGA',
  reportedRepCents: 'VRREPITEM',
});
/** Agrupa os valores oficiais sem transformar gorjeta, acréscimo ou taxa em comissão. */
export function summarizeReportedSellerSales(rows, target) {
  const groups = new Map();
  for (const row of rows) {
    if (typeof row.CDVENDEDOR2 !== 'string' || !row.CDVENDEDOR2 || typeof row.GARCON !== 'string'
        || typeof row.QTPRODVEND !== 'number' || !Number.isFinite(row.QTPRODVEND)) throw new Error('O relatório está sem vendedor ou quantidade válida.');
    const seller = groups.get(row.CDVENDEDOR2) || { sellerId: row.CDVENDEDOR2, name: row.GARCON, lines: 0,
      quantity: 0, ...Object.fromEntries(Object.keys(reportedFields).map(field => [field, 0])) };
    if (seller.name !== row.GARCON) throw new Error('O código de vendedor retornou nomes diferentes. Confira a origem.');
    seller.lines++; seller.quantity += row.QTPRODVEND;
    for (const [field, source] of Object.entries(reportedFields)) {
      const value = row[source], cents = Math.round(value * 100);
      if (typeof value !== 'number' || !Number.isFinite(value) || !Number.isSafeInteger(cents)
          || Math.abs(value * 100 - cents) > 1e-6) throw new Error(`A precisão monetária de ${source} exige conferência.`);
      seller[field] += cents;
      if (!Number.isSafeInteger(seller[field])) throw new Error('O total excede a precisão suportada.');
    }
    groups.set(row.CDVENDEDOR2, seller);
  }
  return {
    status: 'available', source: 'Teknisa: Produtividade por Vendedor', from: target.from, to: target.to,
    periodBasis: 'DTMOVTURCAIX', unassignedExcluded: true, queriedAt: new Date().toISOString(), lines: rows.length,
    moneyFields: reportedFields,
    sellers: [...groups.values()].map(seller => ({ ...seller, quantity: Math.round(seller.quantity * 1e6) / 1e6,
      commission: { status: 'missing_rule', amountCents: null } })),
  };
}

export function calculateReportedCommission(report, rules = []) {
  if (!Array.isArray(rules)) throw new Error('Informe as regras de comissão como lista.');
  const bySeller = new Map();
  for (const rule of rules) {
    if (typeof rule.sellerId !== 'string' || !rule.sellerId || bySeller.has(rule.sellerId)
        || !Object.hasOwn(reportedFields, rule.base) || !Number.isSafeInteger(rule.rateBasisPoints)
        || rule.rateBasisPoints < 0 || rule.rateBasisPoints > 10000) throw new Error('Informe vendedor, campo-base do relatório e percentual em pontos-base, sem duplicatas.');
    bySeller.set(rule.sellerId, rule);
  }
  return { ...report, commissionRounding: 'por vendedor e período, para o centavo mais próximo; meio centavo se afasta de zero',
    sellers: report.sellers.map(seller => {
      const rule = bySeller.get(seller.sellerId) || bySeller.get('*');
      if (!rule) return seller;
      return { ...seller, commission: { status: 'calculated', base: rule.base, sourceField: reportedFields[rule.base],
        baseCents: seller[rule.base], rateBasisPoints: rule.rateBasisPoints,
        amountCents: percentageCents(seller[rule.base], rule.rateBasisPoints) } };
    }) };
}
