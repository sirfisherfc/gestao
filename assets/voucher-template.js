(function (root) {
  'use strict';
  const REASONS = Object.freeze({ recovery: 'Recuperação de cliente insatisfeito', friend: 'Cortesia para amigo',
    commercial: 'Representação comercial / fornecedor', photo_production: 'Modelo em produção de fotos',
    staff_birthday: 'Aniversário de funcionário', loyalty: 'Cortesia por fidelidade',
    promotion: 'Ação promocional ou sorteio', influencer: 'Parceria com influenciador',
    award: 'Premiação / atingimento de metas', other: 'Outro motivo' });
  const STATUS = Object.freeze({ available: 'Disponível', used: 'Utilizado', expired: 'Vencido', cancelled: 'Cancelado' });
  const money = value => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value));
  const benefit = v => v.benefit_type === 'percent'
    ? `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(Number(v.benefit_value))}%` : money(v.benefit_value);
  const dateBR = value => /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? value.split('-').reverse().join('/') : '—';
  const timeBR = value => value ? new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Fortaleza', dateStyle: 'short', timeStyle: 'short' }).format(new Date(value)) : '—';
  function todayPlus(days = 0, instant = new Date()) {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Fortaleza', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(instant);
    const part = key => parts.find(x => x.type === key).value;
    const date = new Date(`${part('year')}-${part('month')}-${part('day')}T12:00:00Z`);
    date.setUTCDate(date.getUTCDate() + days);
    return date.toISOString().slice(0, 10);
  }
  // Split overlong words as well as spaces; never omit a beneficiary's name.
  function wrap(ctx, text, width) {
    const lines = []; let line = '';
    for (const word of String(text).trim().split(/\s+/)) {
      if (line && ctx.measureText(`${line} ${word}`).width <= width) { line += ` ${word}`; continue; }
      if (line) { lines.push(line); line = ''; }
      for (const char of word) {
        if (line && ctx.measureText(line + char).width > width) { lines.push(line); line = ''; }
        line += char;
      }
    }
    if (line) lines.push(line);
    return lines;
  }
  function fitLines(ctx, text, width, maxLines, size, minSize, family, maxHeight = Infinity) {
    for (; size >= minSize; size--) {
      ctx.font = `${size}px ${family}`;
      const lines = wrap(ctx, text, width);
      if (lines.length <= maxLines && lines.length * (size + 8) <= maxHeight) return { lines, size };
    }
    throw new Error('O texto não cabe na imagem. Revise o cadastro.');
  }
  function draw(ctx, v, logo) {
    if (v.status !== 'available') throw new Error('Somente vouchers disponíveis podem ser compartilhados.');
    const W = 1080, H = 1440, ink = '#12293d', paper = '#f6ecd9', sea = '#226861';
    ctx.clearRect(0, 0, W, H); ctx.fillStyle = paper; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#c9b995'; ctx.lineWidth = 2; ctx.strokeRect(32, 32, W - 64, H - 64);
    ctx.fillStyle = sea; ctx.fillRect(32, 32, W - 64, 12);
    ctx.drawImage(logo, 452, 72, 176, 176);
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = ink;
    ctx.font = '700 25px Arial'; ctx.fillText('UM PRESENTE PARA VOCÊ', 540, 300);
    ctx.font = '52px VoucherSerif, Georgia'; ctx.fillText('Bons momentos', 540, 375); ctx.fillText('merecem ser compartilhados.', 540, 437);
    const value = fitLines(ctx, benefit(v), 920, 1, 142, 55, 'VoucherSerif, Georgia');
    ctx.fillStyle = sea; ctx.fillText(value.lines[0], 540, 610);
    ctx.font = '24px Arial'; ctx.fillStyle = ink;
    ctx.fillText(v.benefit_type === 'percent' ? 'DE DESCONTO NA CONTA' : 'EM UMA EXPERIÊNCIA SIR FISHER', 540, 665);
    ctx.font = '24px Arial'; ctx.fillText('ESPECIALMENTE PARA', 540, 748);
    const name = fitLines(ctx, v.beneficiary_name, 900, 4, 52, 16, 'VoucherSerif, Georgia', 160);
    const nameStart = 780 + (160 - name.lines.length * (name.size + 8)) / 2 + name.size;
    name.lines.forEach((line, i) => ctx.fillText(line, 540, nameStart + i * (name.size + 8)));
    ctx.strokeStyle = '#c9b995'; ctx.setLineDash([7, 9]); ctx.beginPath(); ctx.moveTo(75, 972); ctx.lineTo(1005, 972); ctx.stroke(); ctx.setLineDash([]);
    ctx.font = '700 42px monospace'; ctx.fillStyle = ink; ctx.fillText(v.code, 540, 1041);
    ctx.font = '30px Arial'; ctx.fillText(`Válido até ${dateBR(v.expires_on)}`, 540, 1101);
    ctx.font = '32px Arial';
    const conditions = (v.conditions || []).flatMap(text => wrap(ctx, text, 916));
    if (conditions.length > 6) throw new Error('Condições excedem o espaço da imagem.');
    conditions.forEach((line, i) => ctx.fillText(line, 540, 1162 + i * 36));
    ctx.font = '24px Arial'; ctx.fillStyle = sea; ctx.fillText('sirfisher.com.br  ·  @sirfisherfc', 540, 1389);
  }
  function whatsapp(v) {
    const phone = String(v.phone || '').replace(/\D/g, '');
    const destination = phone.length === 10 || phone.length === 11 ? `55${phone}` : phone;
    const text = `Olá, ${v.beneficiary_name}! Você recebeu um voucher Sir Fisher de ${benefit(v)}. Código: ${v.code}. Válido até ${dateBR(v.expires_on)}. ${v.conditions.join(' ')} Apresente o voucher à equipe na sua visita.`;
    return `https://wa.me/${destination}?text=${encodeURIComponent(text)}`;
  }
  async function sharePrepared(file, nav, fallback) {
    try {
      if (nav.share && nav.canShare?.({files:[file]})) {
        await nav.share({files:[file],title:'Um presente Sir Fisher'});
        return 'shared';
      }
    } catch (error) { if (error.name === 'AbortError') return 'cancelled'; }
    fallback(); return 'fallback';
  }
  const api = { REASONS, STATUS, money, benefit, dateBR, timeBR, todayPlus, wrap, fitLines, draw, whatsapp, sharePrepared };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.BenefitVoucher = api;
})(typeof window !== 'undefined' ? window : globalThis);
