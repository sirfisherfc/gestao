const normalize = text => String(text ?? '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toUpperCase();
const sku = value => String(value ?? '').replaceAll('.', '');
export function classifyProduction({ group, name }) {
  const category = normalize(group), product = normalize(name);
  if (category === 'COQUETEIS' || /SUCO|SUMO|SODA ITALIANA|CAFE/.test(product)) return 'bar';
  if (['BEBIDAS', 'CERVEJAS', 'DESTILADOS'].includes(category) || /CHOP+E?|GELO|ROLHA|EMBALAGEM/.test(product)) return 'balcao';
  if (['MENU EXECUTIVO', 'APERITIVOS', 'PARA DOIS', 'PRIME', 'SOBREMESA', 'QUARTA DO CAMARAO'].includes(category)
      || /SALADA|FAROFA|ADICIONAL (OVO|ARROZ|HAMBURGUER)|MOLHOS/.test(product)) return 'cozinha';
  return null;
}
export function buildRoutingUpdates(rows, sources, roles) {
  if (!Array.isArray(sources) || !sources.length || !roles || !['balcao', 'cozinha', 'bar'].every(role => /^\d{5}$/.test(roles[role]))
      || new Set(Object.values(roles)).size !== 3) throw new Error('Informe as fontes e três códigos distintos de destino.');
  const current = new Map();
  for (const row of rows) {
    const code = sku(row.CDARVPROD);
    if (current.has(code)) throw new Error('Há códigos de árvore repetidos na loja.');
    current.set(code, row);
  }
  const classified = new Map(), unresolved = [];
  for (const source of sources) {
    const code = sku(source.sku), row = current.get(code), role = source.role || classifyProduction(source);
    if (!/^\d{10}$/.test(code) || !row || !Object.hasOwn(roles, role)) {
      unresolved.push({ sku: source.sku, name: source.name, reason: !row ? 'vínculo ausente' : 'destino a definir' }); continue;
    }
    if (classified.has(code) && classified.get(code).role !== role) throw new Error('O mesmo SKU recebeu destinos diferentes na fonte.');
    classified.set(code, { id: row.CDPRODUTO, printerCode: roles[role], role });
  }
  const counts = { balcao: 0, cozinha: 0, bar: 0 };
  for (const item of classified.values()) counts[item.role]++;
  return { updates: [...classified.values()].map(({ id, printerCode }) => ({ id, set: { NRSEQIMPRPROD: printerCode } })),
    counts, unresolved, outsideSource: rows.length - classified.size };
}
