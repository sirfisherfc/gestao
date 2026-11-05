(function (root) {
  'use strict';
  const REASONS = Object.freeze({ recovery: 'Recuperação de cliente insatisfeito', friend: 'Cortesia para amigo',
    commercial: 'Representação comercial / fornecedor', photo_production: 'Modelo em produção de fotos',
    staff_birthday: 'Aniversário de funcionário', loyalty: 'Cortesia por fidelidade',
    promotion: 'Ação promocional ou sorteio', influencer: 'Parceria com influenciador',
    award: 'Premiação / atingimento de metas', other: 'Outro motivo' });
  const STATUS = Object.freeze({ available: 'Disponível', used: 'Utilizado', expired: 'Vencido', cancelled: 'Cancelado' });
  const WIDTH = 1600, HEIGHT = 1000;
  const FIELD_LABELS = Object.freeze({beneficiary_name:'Beneficiário',phone:'Telefone',benefit_type:'Tipo de benefício',
    benefit_value:'Benefício',expires_on:'Validade',issue_reason:'Motivo',issue_reason_detail:'Complemento',internal_note:'Nota interna'});
  const money = value => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value));
  const benefit = v => v.benefit_type === 'percent'
    ? `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(Number(v.benefit_value))}%` : money(v.benefit_value);
  const dateBR = value => /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? value.split('-').reverse().join('/') : '—';
  const timeBR = value => value ? new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Fortaleza', dateStyle: 'short', timeStyle: 'short' }).format(new Date(value)) : '—';
  function eventReason(value) {
    const [key,...rest] = String(value || '').split(':');
    return REASONS[key] ? REASONS[key] + (rest.length ? `: ${rest.join(':').trim()}` : '') : String(value || '');
  }
  function changedFields(changes) {
    if (!changes?.before || !changes?.after) return [];
    function display(field,snapshot) {
      const value=snapshot[field]; if(value==null || value==='')return '—';
      if(field==='benefit_value')return benefit(snapshot);
      if(field==='benefit_type')return value==='percent' ? 'Percentual' : 'Valor em reais';
      if(field==='expires_on')return dateBR(value);
      if(field==='issue_reason')return REASONS[value] || String(value);
      return String(value);
    }
    return Object.entries(FIELD_LABELS).filter(([key])=>JSON.stringify(changes.before[key])!==JSON.stringify(changes.after[key]))
      .map(([key,label])=>({label,before:display(key,changes.before),after:display(key,changes.after)}));
  }
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
  function draw(ctx, v, logo, deck) {
    if (v.status !== 'available') throw new Error('Somente vouchers disponíveis podem ser compartilhados.');
    const photoWidth = deck?.naturalWidth || deck?.width, photoHeight = deck?.naturalHeight || deck?.height;
    if (!(photoWidth > 0 && photoHeight > 0)) throw new Error('Não foi possível carregar a foto do deck. Atualize a página e tente novamente.');
    const W = WIDTH, H = HEIGHT, ink = '#12293d', paper = '#f6ecd9', sea = '#226861';
    ctx.clearRect(0, 0, W, H); ctx.fillStyle = paper; ctx.fillRect(0, 0, W, H);
    // A centered card keeps all gift information on one axis over the deck photo.
    const photoBox = { x: 0, y: 0, width: W, height: H };
    const scale = Math.max(photoBox.width / photoWidth, photoBox.height / photoHeight);
    const cropWidth = photoBox.width / scale, cropHeight = photoBox.height / scale;
    ctx.drawImage(deck, (photoWidth - cropWidth) / 2, (photoHeight - cropHeight) * .6, cropWidth, cropHeight,
      photoBox.x, photoBox.y, photoBox.width, photoBox.height);
    const cardFill=ctx.createLinearGradient(368,0,1232,0);
    cardFill.addColorStop(0,'#e9e9e6');cardFill.addColorStop(.5,'#fffefb');cardFill.addColorStop(1,'#e9e9e6');
    ctx.save();ctx.shadowColor='rgba(18,41,61,.18)';ctx.shadowBlur=24;ctx.shadowOffsetY=8;
    ctx.fillStyle=cardFill;ctx.beginPath();ctx.roundRect(368,148,864,704,32);ctx.fill();ctx.restore();
    ctx.drawImage(logo, 754, 178, 92, 92);
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = ink;
    ctx.font = '18px Arial'; ctx.fillText('UM PRESENTE PARA VOCÊ', 800, 299);
    ctx.font='19px Arial';ctx.fillText(v.benefit_type==='percent' ? 'DE DESCONTO' : 'VALE-PRESENTE',800,336);
    const value = fitLines(ctx, benefit(v), 740, 1, 109, 40, 'VoucherSerif, Georgia');
    ctx.fillStyle = sea; ctx.fillText(value.lines[0], 800, 438);
    ctx.font = '18px Arial'; ctx.fillStyle = ink;ctx.fillText('PARA',800,477);
    const name = fitLines(ctx, v.beneficiary_name, 740, 4, 46, 14, 'VoucherSerif, Georgia', 97);
    const nameStart = 491 + (97 - name.lines.length * (name.size + 8)) / 2 + name.size;
    name.lines.forEach((line, i) => ctx.fillText(line, 800, nameStart + i * (name.size + 8)));
    ctx.strokeStyle = '#cccfc9';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(483,609);ctx.lineTo(1117,609);ctx.stroke();
    ctx.font='16px Arial';ctx.fillText('CÓDIGO',800,644);
    const code=fitLines(ctx,v.code,740,1,48,20,'monospace');ctx.font=`700 ${code.size}px monospace`;ctx.fillText(code.lines[0],800,695);
    ctx.font='23px Arial';ctx.fillText(`Válido até ${dateBR(v.expires_on)}`,800,736);
    ctx.font='21px Arial';
    ['Uso único','Não cumulativo com promoções ou outros vouchers.'].forEach((line,i)=>ctx.fillText(line,800,776+i*30));
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
  const api = { WIDTH, HEIGHT, REASONS, STATUS, money, benefit, dateBR, timeBR, eventReason, changedFields, todayPlus, wrap, fitLines, draw, whatsapp, sharePrepared };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.BenefitVoucher = api;
})(typeof window !== 'undefined' ? window : globalThis);
