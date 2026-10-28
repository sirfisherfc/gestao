/** Formato observado na gravação de um vínculo existente de produto por loja. */
export function buildStoreProductSaveRow(row, operator, date) {
  if (row.__is_new !== false || typeof row.CDARVPROD !== 'string' || typeof row.NMPRODUTO !== 'string') {
    throw new Error('O vínculo existente precisa de código de árvore e nome de produto.');
  }
  return {
    ...row, CDARVPROD: row.CDARVPROD.replaceAll('.', ''), NIVELINICIAL: '',
    NMPRODINICIAL: row.NMPRODUTO, CDPRODINICIAL: row.CDPRODUTO, changed: true, CDOPERADOR: operator,
    DTATU: new Intl.DateTimeFormat('pt-BR', {
      timeZone: 'America/Fortaleza', dateStyle: 'short', timeStyle: 'medium', hour12: false,
    }).format(date).replace(',', ''),
  };
}
