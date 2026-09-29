(function () {
  'use strict';
  const sb = SirFisherSupabase;
  const esc = SirFisherDOM.escapeHTML;
  const ENDPOINT = 'https://lucpxoynpvogkvzepagi.supabase.co/functions/v1/event-quote';
  let ctx = null;
  let rows = [];
  const money = value => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value) || 0);
  const dateBR = value => value ? new Intl.DateTimeFormat('pt-BR').format(new Date(`${value}T12:00:00`)) : '—';
  const itemLabel = {
    pasteizinhos: 'Pasteizinhos (porção = 10)', bolinha_peixe: 'Bolinha de peixe (porção = 6)', crocante_carne_sol: 'Crocante de carne de sol (porção = 6)',
    crocantes: 'Crocantes carne de sol/calabresa (porção = 6)', dadinho_tapioca: 'Dadinho de tapioca (porção = 12)', crispy_chicken: 'Crispy Spicy Chicken (porção 200 g)',
    newcastle: 'NewCastle (porção 250 g)', isca_peixe: 'Isca de peixe (porção 250 g)', lanche: 'Lanches (Edimburger / Fisher Burger / Fish & Chips)',
    travessa_essencial: 'Travessas Essencial (frango, picanha suína, peixe)', travessa_equilibrada: 'Travessas Equilibrada (+ carne de sol)',
    travessa_completa: 'Travessas Completa (peixe, carne de sol, filé, picanha)', brownie: 'Brownie', brownie_sorvete: 'Brownie com sorvete',
    agua: 'Água 500 ml', refrigerante: 'Refrigerante lata', suco: 'Suco copo', chope: 'Chope Brahma 300 ml', coquetel: 'Caipirinha ou caipiroska'
  };
  const label = key => itemLabel[key] || key.replaceAll('_', ' ');
  const driverLabel = { desconto: 'Cardápio com desconto', custo: 'Piso de custo', oportunidade: 'Faturamento esperado do horário', cardapio: 'Cardápio (v2 antiga)', tecnico: 'Mínimo técnico (v2 antiga)' };
  const pct = value => value == null ? '—' : `${Math.round(Number(value) * 1000) / 10}%`;
  const discountText = internal => {
    const b = internal.discountBreakdown;
    if (!b) return '—';
    return `antecipado ${pct(b.antecipado)} · volume ${pct(b.volume)} · horário ${pct(b.horario)} · formato ${pct(b.cardapio)}`;
  };
  const statusLabel = {
    pending: 'Pendente', approved: 'Aprovada', adjustment_requested: 'Ajuste solicitado', rejected: 'Recusada',
    information_requested: 'Informação solicitada', alternative_offered: 'Alternativa oferecida',
    final_proposal_ready: 'Proposta definitiva pronta'
  };

  async function session() {
    const { data: { session: current } } = await sb.auth.getSession();
    if (!current) throw new Error('Sessão expirada. Entre novamente.');
    return current;
  }

  async function api(action, payload = {}) {
    const current = await session();
    const response = await fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${current.access_token}` },
      body: JSON.stringify({ action, ...payload })
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || 'Falha ao consultar o módulo de eventos.');
    return body;
  }

  function renderShell() {
    document.getElementById('main').innerHTML = `<div class="page-intro"><div><h2>Eventos</h2><p>Pré-propostas recebidas pelo site. Revise, ajuste e gere o PDF definitivo antes de confirmar com o cliente.</p></div><button class="button" id="event-refresh">Atualizar</button></div><div class="event-kpis" id="event-kpis"></div><div class="event-filters"><input id="event-search" type="search" placeholder="Código ou cliente"><select id="event-risk-filter"><option value="">Todos os riscos</option><option value="verde">Verde</option><option value="amarelo">Amarelo</option><option value="vermelho">Vermelho</option></select><select id="event-status-filter"><option value="">Todos os status</option>${Object.entries(statusLabel).map(([value, label]) => `<option value="${value}">${label}</option>`).join('')}</select></div><div class="event-list" id="event-list"><div class="loading">Carregando…</div></div>`;
    document.getElementById('event-refresh').addEventListener('click', load);
    document.getElementById('event-search').addEventListener('input', renderRows);
    document.getElementById('event-risk-filter').addEventListener('change', renderRows);
    document.getElementById('event-status-filter').addEventListener('change', renderRows);
  }

  function renderKpis() {
    const open = rows.filter(row => row.status === 'pending');
    const count = risk => open.filter(row => row.risk_level === risk).length;
    document.getElementById('event-kpis').innerHTML = [['Verdes', count('verde'), 'verde'], ['Amarelos', count('amarelo'), 'amarelo'], ['Vermelhos', count('vermelho'), 'vermelho']]
      .map(([label, value, risk]) => `<div class="event-kpi"><span>${label}</span><strong class="event-risk--${risk}">${value}</strong></div>`).join('');
  }

  function renderRows() {
    const search = (document.getElementById('event-search')?.value || '').trim().toLowerCase();
    const risk = document.getElementById('event-risk-filter')?.value || '';
    const status = document.getElementById('event-status-filter')?.value || '';
    const filtered = rows.filter(row => (!search || `${row.public_code} ${row.customer_name}`.toLowerCase().includes(search)) && (!risk || row.risk_level === risk) && (!status || row.status === status));
    const list = document.getElementById('event-list');
    if (!filtered.length) { list.innerHTML = '<div class="event-empty">Nenhuma solicitação neste filtro.</div>'; return; }
    list.innerHTML = filtered.map(row => `<button class="event-row" type="button" data-id="${esc(row.id)}"><div><b>${esc(row.public_code)}</b><small>${dateBR(row.created_at?.slice(0, 10))}</small></div><div><b>${esc(row.customer_name)}</b><small>${row.guests} pessoas</small></div><div><b>${dateBR(row.event_date)} · ${esc(String(row.start_time).slice(0, 5))}</b><small>${esc(row.public_snapshot?.name || '')}</small></div><span class="event-risk event-risk--${esc(row.risk_level)}">${esc(row.risk_level)}</span><span class="event-status">${esc(statusLabel[row.status] || row.status)}</span></button>`).join('');
    list.querySelectorAll('[data-id]').forEach(button => button.addEventListener('click', () => openDetail(button.dataset.id)));
  }

  async function load() {
    const list = document.getElementById('event-list');
    if (list) list.innerHTML = '<div class="loading">Carregando…</div>';
    try { const data = await api('admin-list'); rows = data.requests || []; renderKpis(); renderRows(); }
    catch (error) { if (list) list.innerHTML = `<div class="event-error">${esc(error.message)}</div>`; }
  }

  function kv(items) {
    return `<dl class="event-kv">${items.filter(Boolean).map(([key, value]) => `<div><dt>${esc(key)}</dt><dd>${esc(value == null ? '—' : value)}</dd></div>`).join('')}</dl>`;
  }

  function objectItems(obj) {
    return Object.entries(obj || {}).map(([key, value]) => `<li>${esc(label(key))}: <strong>${esc(value)}</strong></li>`).join('') || '<li>Sem itens calculados.</li>';
  }

  function quantityInputs(kind, obj) {
    return Object.entries(obj || {}).map(([key, value]) => `<label><span>${esc(label(key))}</span><input type="number" min="0" max="10000" step="1" value="${esc(value)}" data-quantity="${kind}" data-key="${esc(key)}"></label>`).join('') || '<p>Sem itens calculados.</p>';
  }

  function adjustmentForm(r, pub, internal) {
    const terms = r.proposal_terms || {};
    return `<section class="event-card event-adjustment" id="event-adjustment" hidden><div class="event-adjustment-head"><div><h3>Editar proposta</h3><p>Salve os ajustes antes de gerar o PDF definitivo.</p></div><button type="button" class="event-close-adjustment">Fechar</button></div><div class="event-form-grid"><label>Data<input id="adjust-date" type="date" value="${esc(r.event_date)}"></label><label>Início<input id="adjust-time" type="time" value="${esc(String(r.start_time).slice(0, 5))}"></label><label>Duração (horas)<input id="adjust-duration" type="number" min="2" max="8" step="0.5" value="${esc(r.duration_hours)}"></label><label>Convidados<input id="adjust-guests" type="number" min="1" max="300" value="${esc(r.guests)}"></label><label>Crianças<input id="adjust-children" type="number" min="0" max="300" value="${esc(r.children)}"></label><label>Valor por pessoa<input id="adjust-price" type="number" min="1" max="10000" step="0.01" value="${esc(pub.pricePerPerson)}"></label><label class="wide">Nome do pacote<input id="adjust-name" maxlength="140" value="${esc(pub.name)}"></label><label class="wide">Descrição<textarea id="adjust-description" maxlength="500">${esc(pub.description || '')}</textarea></label><label class="wide">Modelo de bebidas<input id="adjust-beverage" maxlength="180" value="${esc(pub.beverageLabel || '')}"></label></div><h3>Porções de alimentos</h3><div class="event-quantity-grid">${quantityInputs('food', internal.portions)}</div><h3>Bebidas</h3><div class="event-quantity-grid">${quantityInputs('drink', internal.drinks)}</div><div class="event-form-grid"><label>Validade (dias)<input id="adjust-validity" type="number" min="1" max="30" value="${esc(terms.validityDays || 5)}"></label><label>Sinal (%)<input id="adjust-deposit" type="number" min="0" max="100" step="0.1" value="${esc(terms.depositPercent ?? 20)}"></label><label>Saldo até quantos dias antes<input id="adjust-balance" type="number" min="0" max="60" value="${esc(terms.balanceDaysBefore ?? 7)}"></label><label>Acréscimo no cartão (%)<input id="adjust-card" type="number" min="0" max="30" step="0.5" value="${esc(terms.cardSurchargePercent ?? 10)}"></label><label class="wide">Detalhe das bebidas (aparece no PDF)<textarea id="adjust-beverage-detail" maxlength="400">${esc(pub.beverageDetail || '')}</textarea></label><label class="wide">Adicionais, um por linha<textarea id="adjust-additions">${esc((pub.additions || []).join('\n'))}</textarea></label><label class="wide">Não incluídos, um por linha<textarea id="adjust-excluded">${esc((pub.notIncluded || []).join('\n'))}</textarea></label><label class="wide">Observações comerciais<textarea id="adjust-commercial-notes" maxlength="1000">${esc(terms.additionalNotes || '')}</textarea></label></div><button class="primary event-save-adjustment" type="button">Salvar ajustes</button><div id="event-adjustment-error"></div></section>`;
  }

  async function openDetail(id) {
    const mount = document.getElementById('event-modal');
    mount.innerHTML = '<div class="event-modal-backdrop"><div class="event-modal"><div class="loading">Carregando…</div></div></div>';
    mount.querySelector('.event-modal-backdrop').addEventListener('click', event => { if (event.target.classList.contains('event-modal-backdrop')) closeDetail(); });
    try {
      const { request: r } = await api('admin-detail', { id });
      const internal = r.internal_snapshot || {};
      const pub = r.public_snapshot || {};
      const signals = internal.signals || {};
      const alerts = (internal.alerts || []).map(item => `<li>${esc(item)}</li>`).join('') || '<li>Sem alertas.</li>';
      const waText = encodeURIComponent(`Olá, ${r.customer_name}! Estamos analisando a proposta ${r.public_code} do seu evento.`);
      const notification = r.notification_sent_at ? 'E-mail enviado' : (r.notification_error ? `Falha: ${r.notification_error}` : 'Aguardando envio');
      mount.querySelector('.event-modal').innerHTML = `<div class="event-modal-head"><div><span class="event-risk event-risk--${esc(r.risk_level)}">${esc(r.risk_level)}</span><h2>${esc(r.public_code)} · ${esc(r.customer_name)}</h2><small>${esc(statusLabel[r.status] || r.status)}</small></div><button class="event-close" type="button" aria-label="Fechar">×</button></div><div class="event-detail-grid"><section class="event-card"><h3>Cliente e evento</h3>${kv([['WhatsApp', r.customer_phone], ['Data', dateBR(r.event_date)], ['Início', String(r.start_time).slice(0, 5)], ['Duração', `${r.duration_hours} horas`], ['Convidados', r.guests], ['Crianças', r.children], ['Aviso interno', notification]])}<a class="event-wa" target="_blank" rel="noopener" href="https://api.whatsapp.com/send?phone=55${esc(r.customer_phone)}&text=${waText}">Conversar no WhatsApp</a></section><section class="event-card"><h3>Opção escolhida</h3>${kv([['Pacote', pub.name], ['Bebidas', pub.beverageLabel], ['Por pessoa', money(pub.pricePerPerson)], ['Total', money(pub.total)], ['Atendimento', 'Incluído'], ['Proposta', r.proposal_version ? `Versão ${r.proposal_version}` : 'Ainda não gerada'], ['Versão de preço', r.pricing_version], ['Versão do cardápio', r.menu_version]])}</section><section class="event-card"><h3>Dimensionamento</h3><ul class="event-items">${objectItems(internal.portions)}</ul><h3 style="margin-top:12px">Bebidas</h3><ul class="event-items">${objectItems(internal.drinks)}</ul>${kv([['Adultos calculados', internal.adults], ['Freelancers de salão', internal.freelancerCount], ['Cozinheiros extras', internal.kitchenExtraCount ?? '—']])}</section><section class="event-card"><h3>Análise interna</h3>${kv([['Valor cobrado', money(pub.total)], ['Mesmos itens no cardápio', money(internal.menuEquivalentTotal)], ['Diferença p/ cardápio', internal.menuEquivalentTotal ? `${Math.round((Number(pub.total) / Number(internal.menuEquivalentTotal) - 1) * 100)}%` : '—'], ['Horas além de 3h', internal.durationSurchargeTotal ? money(internal.durationSurchargeTotal) : '—'], ['Desconto calculado', pct(internal.discountTarget)], ['Composição do desconto', discountText(internal)], ['Movimento do horário', internal.demandIndex == null ? '—' : `${Math.round(internal.demandIndex * 100)}% do pico (${internal.demandSource === 'historico' ? 'histórico' : 'estimativa'}${signals.demandNote ? `: ${signals.demandNote}` : ''})`], ['Fator do mês', internal.monthFactor == null ? '—' : `${internal.monthFactor}×`], ['Faturamento esperado na janela', internal.expectedWindowRevenue == null ? 'Sem histórico' : money(internal.expectedWindowRevenue)], ['Piso de oportunidade', internal.opportunityFloorTotal == null ? 'Sem dado' : money(internal.opportunityFloorTotal)], ['Piso de custo', money(internal.technicalMinimumTotal)], ['Quem definiu o preço', driverLabel[internal.priceDriver] || '—'], ['CMV usado', internal.cmvRateUsed == null ? '35% (provisório)' : pct(internal.cmvRateUsed)], ['CMV estimado', money(internal.estimatedCmvTotal)], ['Margem estimada', `${Math.round((Number(internal.estimatedContributionMargin) || 0) * 100)}%`]])}<details class="event-help"><summary>Como ler esta análise</summary><ul><li><b>Mesmos itens no cardápio</b>: quanto o grupo pagaria pedindo exatamente estas porções e bebidas à la carte, já com os 10%.</li><li><b>Horas além de 3h</b>: cada hora extra soma 10% do valor de cardápio (mesma regra da hora extra do contrato).</li><li><b>Desconto calculado</b>: soma de antecipado (5%), volume (3% a 10% conforme convidados), horário (até 10%, quanto mais vazio o horário, maior) e formato (petiscos 3%, lanche 2%, refeição 0%). Teto de 25%.</li><li><b>Movimento do horário</b>: faturamento médio das horas do evento, naquele dia da semana, dividido pela hora mais movimentada da semana, ajustado pelo mês. Vem da base de escalas (últimos 12 meses).</li><li><b>Piso de oportunidade</b>: faturamento esperado na janela × parte do salão que o evento ocupa (ou 100% se exclusivo). O evento nunca sai por menos do que o salão faria normalmente.</li><li><b>Piso de custo</b>: (CMV + freelancers + cozinheiros extras + horas extras + sobra de bebida) ÷ (1 − 35%) × 1,10. A equipe fixa da cozinha não entra: é paga com ou sem evento. Cozinheiro extra: 1 a partir de 61 convidados, 2 a partir de 91. Garante margem mínima de 35%.</li><li><b>Quem definiu o preço</b>: o maior entre cardápio com desconto, piso de custo e piso de oportunidade.</li><li><b>CMV usado</b>: CMV real médio dos últimos 6 meses do painel; sem ele, 35%.</li><li><b>Margem estimada</b>: (valor − CMV − extras contratados − duração − sobra) ÷ valor. Abaixo de 45% fica amarelo.</li></ul></details><h3 style="margin-top:12px">Alertas</h3><ul class="event-items">${alerts}</ul></section>${adjustmentForm(r, pub, internal)}<section class="event-card event-actions"><h3>Próximas etapas</h3><textarea id="event-note" maxlength="1000" placeholder="Justificativa, observação ou mensagem interna"></textarea>${ctx.role === 'admin' ? '<label class="event-discount"><input id="event-discount" type="checkbox"> Aprovar desconto excepcional (justificativa obrigatória)</label>' : ''}<div class="event-buttons"><button class="primary" data-status="approved">Aprovar</button><button id="event-edit" type="button">Editar proposta</button><button data-status="information_requested">Solicitar informação</button><button data-status="alternative_offered">Oferecer alternativa</button><button id="event-pdf" type="button">Gerar e baixar PDF definitivo</button><button class="danger" data-status="rejected">Recusar</button></div><div id="event-action-error"></div></section></div>`;
      mount.querySelector('.event-close').addEventListener('click', closeDetail);
      mount.querySelector('.event-close-adjustment').addEventListener('click', () => { document.getElementById('event-adjustment').hidden = true; });
      mount.querySelector('#event-edit').addEventListener('click', () => { const form = document.getElementById('event-adjustment'); form.hidden = false; form.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
      mount.querySelector('.event-save-adjustment').addEventListener('click', event => saveAdjustment(r.id, event.currentTarget));
      mount.querySelector('#event-pdf').addEventListener('click', event => downloadProposal(r.id, r.public_code, event.currentTarget));
      mount.querySelectorAll('[data-status]').forEach(button => button.addEventListener('click', () => updateRequest(r.id, button.dataset.status, button)));
    } catch (error) { mount.querySelector('.event-modal').innerHTML = `<div class="event-error">${esc(error.message)}</div>`; }
  }

  function collectQuantities(kind) {
    return Object.fromEntries([...document.querySelectorAll(`[data-quantity="${kind}"]`)].map(input => [input.dataset.key, Number(input.value)]));
  }

  async function saveAdjustment(id, button) {
    const note = document.getElementById('event-note').value.trim();
    const discountApproved = Boolean(document.getElementById('event-discount')?.checked);
    const adjustment = {
      date: document.getElementById('adjust-date').value, startTime: document.getElementById('adjust-time').value,
      durationHours: Number(document.getElementById('adjust-duration').value), guests: Number(document.getElementById('adjust-guests').value),
      children: Number(document.getElementById('adjust-children').value), pricePerPerson: Number(document.getElementById('adjust-price').value),
      name: document.getElementById('adjust-name').value, description: document.getElementById('adjust-description').value,
      beverageLabel: document.getElementById('adjust-beverage').value, beverageDetail: document.getElementById('adjust-beverage-detail').value, portions: collectQuantities('food'), drinks: collectQuantities('drink'),
      additions: document.getElementById('adjust-additions').value, notIncluded: document.getElementById('adjust-excluded').value,
      terms: { validityDays: Number(document.getElementById('adjust-validity').value), depositPercent: Number(document.getElementById('adjust-deposit').value), balanceDaysBefore: Number(document.getElementById('adjust-balance').value), cardSurchargePercent: Number(document.getElementById('adjust-card').value), additionalNotes: document.getElementById('adjust-commercial-notes').value }
    };
    button.disabled = true;
    try { await api('admin-adjust', { id, adjustment, note, discountApproved }); await openDetail(id); await load(); }
    catch (error) { document.getElementById('event-adjustment-error').innerHTML = `<div class="event-error">${esc(error.message)}</div>`; button.disabled = false; }
  }

  async function downloadProposal(id, code, button) {
    button.disabled = true;
    const errorMount = document.getElementById('event-action-error');
    try {
      const current = await session();
      const response = await fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${current.access_token}` }, body: JSON.stringify({ action: 'admin-proposal-pdf', id }) });
      if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.error || 'Não foi possível gerar o PDF.'); }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url; link.download = `proposta-${code}.pdf`; document.body.appendChild(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      closeDetail(); await load();
    } catch (error) { errorMount.innerHTML = `<div class="event-error">${esc(error.message)}</div>`; button.disabled = false; }
  }

  async function updateRequest(id, status, button) {
    const note = document.getElementById('event-note').value.trim();
    const discountApproved = Boolean(document.getElementById('event-discount')?.checked);
    if (discountApproved && !note) { document.getElementById('event-action-error').innerHTML = '<div class="event-error">Informe a justificativa do desconto.</div>'; return; }
    button.disabled = true;
    try { await api('admin-update', { id, status, note, discountApproved }); closeDetail(); await load(); }
    catch (error) { document.getElementById('event-action-error').innerHTML = `<div class="event-error">${esc(error.message)}</div>`; button.disabled = false; }
  }

  function closeDetail() { document.getElementById('event-modal').innerHTML = ''; }
  (async () => { ctx = await SirFisherAuth.requireRole(sb); if (!ctx) return; renderShell(); load(); })();
})();
