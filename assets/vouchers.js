(async function () {
  'use strict';
  const auth = await window.voucherAuth;
  if (!auth) return;
  const sb = window.SirFisherSupabase, V = window.BenefitVoucher;
  const $ = id => document.getElementById(id);
  const main = $('main');
  // Only constant markup is inserted; all server data uses textContent.
  main.innerHTML = `<div class="voucher-head"><div><h2>Vouchers</h2><p>Um presente com propósito, do convite à visita.</p></div><button id="new-btn" class="voucher-btn">Emitir voucher</button></div><div id="stats" class="voucher-stats"></div><p id="totals-note" class="voucher-note"></p><form id="filters" class="voucher-filters"><label>Buscar por nome, código ou telefone<input id="search" type="search" maxlength="160"></label><label>Situação<select id="status"><option value="">Todas</option><option value="available">Disponíveis</option><option value="used">Utilizados</option><option value="expired">Vencidos</option><option value="cancelled">Cancelados</option></select></label><label>Motivo<select id="reason-filter"><option value="">Todos os motivos</option></select></label><button class="voucher-btn secondary" type="submit">Buscar</button></form><p id="list-message" class="voucher-message" role="status" aria-live="polite"></p><div id="voucher-list" class="voucher-list"></div><div class="voucher-pager"><button id="prev" class="voucher-btn secondary">Anterior</button><span id="page-label"></span><button id="next" class="voucher-btn secondary">Próxima</button></div>`;
  const issueForm = $('issue-form'), cancelForm = $('cancel-form');
  for (const [key, label] of Object.entries(V.REASONS)) {
    for (const select of [issueForm.elements.reason, $('reason-filter')]) {
      const option = document.createElement('option'); option.value = key; option.textContent = label; select.append(option);
    }
  }
  let offset = 0, selected = null, file = null, requestId = null, editing = null, issuing = false, cancelling = false, listSerial = 0, detailSerial = 0;
  function message(id, text, error = false) { $(id).textContent = text; $(id).classList.toggle('error', error); }
  async function rpc(name, args) {
    const { data, error } = await sb.rpc(name, args);
    if (error) throw Object.assign(new Error(error.code === '42501' ? 'Seu perfil não tem permissão para esta operação.' : error.code === '22023' ? error.message : 'Não foi possível confirmar a operação. Verifique sua conexão.'),{code:error.code});
    if (!data) throw new Error('Não foi possível confirmar a operação.');
    if (data.reason === 'rate_limited') throw new Error('Muitas operações em pouco tempo. Aguarde um minuto e tente novamente.');
    return data;
  }
  function text(tag, value, className) { const node = document.createElement(tag); node.textContent = value; if (className) node.className = className; return node; }
  function badge(v) { return text('span', V.STATUS[v.status] || 'Indisponível', `voucher-badge ${v.status}`); }
  async function loadList() {
    const serial = ++listSerial; message('list-message', 'Atualizando…');
    try {
      const data = await rpc('benefit_voucher_list', { p_search: $('search').value.trim(), p_status: $('status').value, p_reason: $('reason-filter').value, p_offset: offset, p_limit: 30 });
      if (serial !== listSerial) return;
      if (!data.ok) throw new Error('Não foi possível consultar os vouchers.');
      $('stats').replaceChildren(...[['issued','Emitidos'],['available','Disponíveis'],['used','Utilizados'],['expired','Vencidos'],['cancelled','Cancelados']].map(([key,label]) => { const n = text('div','', 'voucher-stat'); n.append(text('strong',data.summary[key]),text('span',label)); return n; }));
      $('totals-note').textContent = `Disponíveis em valor fixo: ${V.money(data.summary.fixed_available_total)} · ${data.summary.percent_available_count} voucher(s) percentual(is). Percentuais não entram no total em reais.`;
      $('voucher-list').replaceChildren(...data.rows.map(v => {
        const row = text('button', '', 'voucher-panel voucher-row'); row.type = 'button';
        const left = text('div',''); left.append(text('strong',v.beneficiary_name),text('small',`${v.code} · Até ${V.dateBR(v.expires_on)}`),text('small',V.REASONS[v.issue_reason] || 'Outro motivo'));
        const right = text('div',''); right.append(text('div',V.benefit(v),'value'),badge(v)); row.append(left,right); row.addEventListener('click',()=>openDetail(v.id)); return row;
      }));
      if (!data.rows.length) $('voucher-list').append(text('p','Nenhum voucher encontrado.','voucher-empty'));
      $('prev').disabled = offset === 0; $('next').disabled = offset + 30 >= data.total;
      $('page-label').textContent = data.total ? `${offset + 1}–${offset + data.rows.length} de ${data.total}` : '0 vouchers';
      message('list-message','');
    } catch (error) { if (serial === listSerial) message('list-message',error.message,true); }
  }
  function term(dl,label,value) { dl.append(text('dt',label),text('dd',value || '—')); }
  function resetActions() { file = null; $('download-btn').disabled = true; $('share-btn').disabled = true; $('whatsapp-link').hidden = true; $('whatsapp-link').removeAttribute('href'); $('cancel-btn').hidden = true; $('edit-btn').hidden = true; }
  async function openDetail(id) {
    const serial = ++detailSerial; selected = null; resetActions(); $('detail-body').replaceChildren(); message('detail-message','Consultando…');
    if (!$('detail-dialog').open) $('detail-dialog').showModal();
    try {
      const data = await rpc('benefit_voucher_detail',{p_id:id});
      if (serial !== detailSerial || !$('detail-dialog').open) return;
      if (!data.ok) throw new Error('Voucher não encontrado.');
      selected = data.voucher; const v = selected;
      const layout = text('div','','voucher-detail'), details = text('div',''), dl = text('dl','');
      details.append(badge(v)); term(dl,'Beneficiário',v.beneficiary_name); term(dl,'Benefício',V.benefit(v)); term(dl,'Código',v.code); term(dl,'Validade',V.dateBR(v.expires_on)); term(dl,'Telefone',v.phone); term(dl,'Motivo',V.REASONS[v.issue_reason]); term(dl,'Complemento',v.issue_reason_detail); term(dl,'Nota interna',v.internal_note); term(dl,'Emissão',`${V.timeBR(v.created_at)} · ${v.issued_by_name}`);
      if (v.used_at) term(dl,'Utilização',`${V.timeBR(v.used_at)} · ${v.used_by_name}`);
      if (v.cancelled_at) { term(dl,'Cancelamento',`${V.timeBR(v.cancelled_at)} · ${v.cancelled_by_name}`); term(dl,'Motivo',v.cancellation_reason); }
      details.append(dl);
      const conditions=document.createElement('details');conditions.className='voucher-disclosure';conditions.append(text('summary','Condições'));
      const rules = text('ul',''); v.conditions.forEach(c=>rules.append(text('li',c))); conditions.append(rules);details.append(conditions);
      const historySection=document.createElement('details');historySection.className='voucher-disclosure';historySection.append(text('summary','Histórico'));
      const history = text('ul',''); data.events.forEach(e=>{
        const reason=e.event_type==='issued' ? V.eventReason(e.reason) : e.reason;
        const item=text('li',`${V.timeBR(e.occurred_at)} · ${{issued:'Emissão',edited:'Edição',used:'Utilização',cancelled:'Cancelamento'}[e.event_type]} · ${e.actor_name}${reason ? ` · ${reason}` : ''}`);
        const changes=V.changedFields(e.changes);
        if(changes.length) {
          const disclosure=document.createElement('details'),dl=text('dl','');disclosure.append(text('summary','Ver alterações'));
          changes.forEach(change=>term(dl,change.label,`${change.before} → ${change.after}`));disclosure.append(dl);item.append(disclosure);
        }
        history.append(item);
      }); historySection.append(history);details.append(historySection);
      const preview = text('div','','voucher-preview'); layout.append(details,preview); $('detail-body').replaceChildren(layout);
      $('cancel-btn').hidden = ['used','cancelled'].includes(v.status);
      $('edit-btn').hidden = !['available','expired'].includes(v.status);
      $('edit-btn').textContent = v.status==='expired' ? 'Renovar validade' : 'Editar';
      $('download-btn').hidden = $('share-btn').hidden = v.status!=='available';
      if (v.status !== 'available') { layout.classList.add('voucher-detail--text-only');message('detail-message',''); return; }
      message('detail-message','Preparando imagem…');
      await document.fonts.load('52px VoucherSerif');
      const [logo, deck] = await Promise.all(['assets/vouchers/logo-emblem.png','assets/vouchers/deck.webp'].map(async src => {
        const img = new Image(); img.src = src; await img.decode(); return img;
      }));
      if (serial !== detailSerial || !$('detail-dialog').open) return;
      const canvas = document.createElement('canvas'); canvas.width = V.WIDTH; canvas.height = V.HEIGHT;
      canvas.setAttribute('role','img'); canvas.setAttribute('aria-label',`Voucher de ${V.benefit(v)} para ${v.beneficiary_name}, ${v.code}, válido até ${V.dateBR(v.expires_on)}.`);
      V.draw(canvas.getContext('2d'),v,logo,deck); preview.append(canvas);
      const blob = await new Promise((resolve,reject)=>canvas.toBlob(b=>b ? resolve(b) : reject(new Error('Falha ao preparar a imagem.')),'image/png'));
      if (serial !== detailSerial || !$('detail-dialog').open) return;
      file = new File([blob],`voucher-${v.code}.png`,{type:'image/png'}); $('download-btn').disabled = false; $('share-btn').disabled = false; message('detail-message','');
    } catch (error) { if (serial === detailSerial) message('detail-message',error.message,true); }
  }
  function download() {
    if (!file) return; const url = URL.createObjectURL(file), a = document.createElement('a'); a.href = url; a.download = file.name; document.body.append(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  function fallback() { download(); $('whatsapp-link').href = V.whatsapp(selected); $('whatsapp-link').hidden = false; message('detail-message','Imagem baixada. Abra o WhatsApp e anexe o arquivo em Downloads. O link prepara o texto; ele não anexa a imagem automaticamente.'); }
  $('download-btn').addEventListener('click',download);
  $('share-btn').addEventListener('click',async()=>{
    if (!file || !selected) return;
    const outcome = await V.sharePrepared(file,navigator,fallback);
    if (outcome==='shared') message('detail-message','Compartilhamento encaminhado ao aplicativo escolhido.');
  });
  document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>{
    if (button.dataset.close==='issue-dialog' && issuing || button.dataset.close==='cancel-dialog' && cancelling) return;
    $(button.dataset.close).close();
  }));
  $('detail-dialog').addEventListener('close',()=>{detailSerial++; selected=null; resetActions();});
  $('new-btn').addEventListener('click',()=>{
    if(editing)requestId=null;editing=null;
    $('issue-title').textContent='Um presente Sir Fisher';$('issue-intro').textContent='A imagem é preparada automaticamente após a emissão. Os dados internos ficam apenas na gestão.';$('issue-submit').textContent='Emitir voucher';
    if (!requestId) { issueForm.reset(); issueForm.elements.expiry.min=V.todayPlus(); issueForm.elements.expiry.value=V.todayPlus(30); requestId=crypto.randomUUID(); reasonChanged(); typeChanged(); }
    $('issue-error').textContent=''; $('issue-dialog').showModal();
  });
  $('edit-btn').addEventListener('click',()=>{
    if(!selected || !['available','expired'].includes(selected.status) || issuing)return;
    const v=selected;editing={id:v.id,revision:v.revision};requestId=null;issueForm.reset();
    const f=issueForm.elements;
    f.beneficiary.value=v.beneficiary_name;f.phone.value=v.phone;f.type.value=v.benefit_type;f.value.value=v.benefit_value;
    const renewing=v.status==='expired';
    f.expiry.min=V.todayPlus();f.expiry.value=renewing ? V.todayPlus(30) : v.expires_on;f.reason.value=v.issue_reason;
    f.reason_detail.value=v.issue_reason_detail || '';f.note.value=v.internal_note || '';
    reasonChanged();typeChanged();$('issue-error').textContent='';$('issue-title').textContent=renewing ? 'Renovar voucher' : 'Editar voucher';$('issue-submit').textContent=renewing ? 'Renovar voucher' : 'Salvar alterações';
    $('issue-intro').textContent=renewing ? 'Confira a nova validade. O código será mantido e a renovação ficará no histórico. Compartilhe a imagem atualizada após salvar.' : 'As correções ficam no histórico. A imagem será atualizada; se já foi enviada, compartilhe a nova versão com o beneficiário.';
    $('issue-dialog').showModal();
  });
  function typeChanged() { const percent=issueForm.elements.type.value==='percent'; $('value-label').firstChild.textContent=percent ? 'Desconto (%)' : 'Valor do benefício (R$)'; issueForm.elements.value.max=percent ? '100' : '9999999999.99'; }
  function reasonChanged() { const other=issueForm.elements.reason.value==='other'; issueForm.elements.reason_detail.required=other; issueForm.elements.reason_detail.minLength=other ? 3 : 0; $('reason-detail-label').firstChild.textContent=other ? 'Descreva o motivo · obrigatório' : 'Complemento do motivo · opcional'; }
  issueForm.elements.type.addEventListener('change',typeChanged); issueForm.elements.reason.addEventListener('change',reasonChanged);
  issueForm.addEventListener('submit',async(event)=>{
    event.preventDefault(); if(issuing || !issueForm.reportValidity())return;
    issuing=true; $('issue-submit').disabled=true; $('issue-error').textContent='';
    const edit=editing;
    try {
      const f=issueForm.elements;
      const values={p_beneficiary_name:f.beneficiary.value.trim(),p_phone:f.phone.value,p_benefit_type:f.type.value,p_benefit_value:Number(f.value.value),p_expires_on:f.expiry.value,p_issue_reason:f.reason.value,p_issue_reason_detail:f.reason_detail.value.trim() || null,p_internal_note:f.note.value.trim() || null};
      const result=await rpc(edit ? 'benefit_voucher_edit' : 'benefit_voucher_issue',edit ? {...values,p_id:edit.id,p_expected_revision:edit.revision} : {...values,p_request_id:requestId});
      if(edit) {
        editing=null;$('issue-dialog').close();await openDetail(edit.id);loadList();
        const status=V.STATUS[result.reason];
        message('detail-message',result.ok ? (result.unchanged ? 'Os dados já estavam atualizados.' : 'Alterações salvas. Baixe e compartilhe a imagem atualizada se necessário.')
          : result.reason==='changed' ? 'O voucher foi alterado enquanto você editava. Confira os dados atuais e abra Editar novamente.' : `Edição recusada: ${status || 'consulte a situação atual'}.`,!result.ok);
        return;
      }
      if(result.reason==='request_conflict') {
        requestId=null; $('issue-dialog').close(); await openDetail(result.voucher.id); loadList();
        message('detail-message','A solicitação anterior já havia sido emitida. Este é o voucher original; as alterações posteriores não foram aplicadas. Para outro benefício, inicie uma nova emissão.',true); return;
      }
      if(!result.ok)throw new Error('Não foi possível confirmar a emissão.');
      requestId=null; $('issue-dialog').close(); offset=0; loadList(); await openDetail(result.voucher.id);
    } catch(error) {
      if(edit && error.code==='22023')$('issue-error').textContent=error.message;
      else if(edit) {
        // A resposta pode ter se perdido depois da gravação. Reconsultar; nunca reenviar a edição automaticamente.
        editing=null;$('issue-dialog').close();await openDetail(edit.id);loadList();
        message('detail-message',`${error.message} Consulte os dados e o histórico antes de editar novamente.`,true);
      } else $('issue-error').textContent=`${error.message} Se houve falha de conexão, mantenha este formulário e tente novamente: a mesma emissão não será duplicada.`;
    }
    finally { issuing=false; $('issue-submit').disabled=false; }
  });
  // Prevent dismissal during a write; request_id survives retry after a lost response.
  for (const dialog of [$('issue-dialog'),$('cancel-dialog')]) dialog.addEventListener('cancel',event=>{if(issuing || cancelling)event.preventDefault();});
  $('cancel-btn').addEventListener('click',()=>{if(!selected)return;cancelForm.reset();$('cancel-error').textContent='';$('cancel-dialog').showModal();});
  cancelForm.addEventListener('submit',async(event)=>{
    event.preventDefault(); if(cancelling || !selected || !cancelForm.reportValidity())return;
    const id=selected.id; cancelling=true; const button=cancelForm.querySelector('[type=submit]'); button.disabled=true;
    try { const result=await rpc('benefit_voucher_cancel',{p_id:id,p_reason:cancelForm.elements.reason.value.trim(),p_confirm:true}); if(!result.ok)throw new Error(`Cancelamento recusado: ${V.STATUS[result.reason] || 'consulte a situação atual'}.`); $('cancel-dialog').close(); await openDetail(id); loadList(); }
    catch(error) { $('cancel-error').textContent=error.message; await openDetail(id); loadList(); }
    finally {cancelling=false;button.disabled=false;}
  });
  $('filters').addEventListener('submit',event=>{event.preventDefault();offset=0;loadList();});
  $('status').addEventListener('change',()=>{offset=0;loadList();}); $('reason-filter').addEventListener('change',()=>{offset=0;loadList();});
  $('prev').addEventListener('click',()=>{offset=Math.max(0,offset-30);loadList();}); $('next').addEventListener('click',()=>{offset+=30;loadList();});
  await loadList();
})();
