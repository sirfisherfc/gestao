(function () {
  'use strict';
  const sb = SirFisherSupabase, esc = SirFisherDOM.escapeHTML;
  const main = document.getElementById('main');
  const day = value => new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Fortaleza' }).format(new Date(value.includes('T') ? value : value + 'T12:00:00-03:00'));
  const stamp = value => value ? new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Fortaleza' }).format(new Date(value)) : 'Indisponível';
  const numeric = value => value == null || value === '' || !Number.isFinite(Number(value)) ? null : Number(value);
  const num = value => numeric(value) == null ? 'Indisponível' : new Intl.NumberFormat('pt-BR').format(Number(value));
  const labels = { reach: 'Contas alcançadas', views: 'Visualizações', accounts_engaged: 'Contas que interagiram', total_interactions: 'Interações', likes: 'Curtidas', comments: 'Comentários', saves: 'Salvamentos', saved: 'Salvamentos', shares: 'Compartilhamentos', profile_links_taps: 'Toques no link do perfil', follows_and_unfollows: 'Seguidores', profile_views: 'Visitas ao perfil', replies: 'Respostas', navigation: 'Navegação' };
  const states = { draft: 'Rascunho', review: 'Em revisão', approved: 'Aprovado e programado', sending: 'Enviando', published: 'Publicação confirmada pela API', uncertain: 'Envio incerto: conferir antes de tentar', failed: 'Falhou', cancelled: 'Cancelado' };
  let owner = false, snapshots = [], editorial = [], comments = [], commentLimit = false, filters, operationRows = null, loadVersion = 0;
  function safeLink(url, label) {
    try { const u = new URL(url); if (u.protocol !== 'https:') return esc(label); }
    catch (_) { return esc(label); }
    return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
  }
  function card(title, value, detail = '') { return `<article class="mk-card"><span>${esc(title)}</span><strong>${esc(value)}</strong><small>${esc(detail)}</small></article>`; }
  function table(headers, rows) { return `<div class="mk-table"><table><thead><tr>${headers.map(h => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.length ? rows.map(row => `<tr>${row.map(c => `<td>${c}</td>`).join('')}</tr>`).join('') : `<tr><td colspan="${headers.length}">Nenhum registro nesta cobertura.</td></tr>`}</tbody></table></div>`; }
  function latest(source, key) { return snapshots.find(s => s.source === source && (!key || s.object_key === key) && s.period_start === filters.start && s.period_end === filters.end); }
  function sourceNote(row) { return row ? `<p class="mk-note">${esc(day(row.period_start))} a ${esc(day(row.period_end))} · Gravado ${esc(stamp(row.collected_at))}${row.payload?.api_collected_from ? ` · Dados da API entre ${esc(stamp(row.payload.api_collected_from))} e ${esc(stamp(row.payload.api_collected_to))}` : ''} · ${esc(row.status === 'partial' ? 'Cobertura parcial' : row.status === 'unavailable' ? 'Indisponível' : 'Disponível')}</p>` : '<p>Sem coleta para este período. Selecione um período coletado ou execute a coleta privada.</p>'; }
  function notice(message) { document.getElementById('mk-message').textContent = message; }
  function metrics(row) {
    return (row?.payload?.metrics || []).map(m => card(labels[m.metric] || m.metric, num(m.value), m.reason || m.definition)).join('');
  }
  function renderInstagram() {
    const account = latest('instagram_account');
    const previousEnd = new Date(filters.start + 'T12:00:00Z'); previousEnd.setUTCDate(previousEnd.getUTCDate() - 1);
    const days = Math.round((Date.parse(filters.end) - Date.parse(filters.start)) / 86400000) + 1;
    const previousStart = new Date(previousEnd); previousStart.setUTCDate(previousStart.getUTCDate() - days + 1);
    const prior = snapshots.find(s => s.source === 'instagram_account' && s.period_start === previousStart.toISOString().slice(0, 10) && s.period_end === previousEnd.toISOString().slice(0, 10));
    const comparisons = (account?.payload?.metrics || []).map(m => {
      const old = prior?.payload?.metrics?.find(p => p.metric === m.metric);
      // Mudanca apenas entre janelas do mesmo tamanho e da mesma versao da API.
      const comparable = m.value != null && old?.value != null && account.payload.api_version === prior.payload.api_version;
      return [esc(labels[m.metric] || m.metric), esc(num(old?.value)), esc(num(m.value)), comparable ? esc(num(m.value - old.value)) : 'Indisponível'];
    });
    document.getElementById('mk-instagram').innerHTML = `<h2>Instagram @sirfisherfc</h2>${sourceNote(account)}<p>${esc(account?.payload?.coverage || '')}</p><div class="mk-cards">${metrics(account)}</div>
      <details><summary>Comparar com o período anterior de ${days} dias</summary>${sourceNote(prior)}${table(['Métrica', 'Anterior', 'Atual', 'Variação'], comparisons)}</details>
      <p>Seguidores no instante da coleta: ${esc(num(account?.payload?.identity?.followers_count))}. O histórico conserva cada coleta. Valores de publicações e Stories abaixo são acumulados até a leitura.</p>`;
    for (const [kind, id, title] of [['instagram_media', 'mk-media', 'Publicações e Reels'], ['instagram_story', 'mk-stories', 'Stories disponíveis na coleta']]) {
      const row = latest(kind);
      const items = (row?.payload?.items || []).map(item => [safeLink(item.permalink, item.id), esc(item.media_product_type || item.media_type || 'Indisponível'), esc(stamp(item.timestamp)), esc((item.caption || '').slice(0, 150)),
        item.insights ? item.insights.metrics.map(m => `${esc(labels[m.metric] || m.metric)}: ${esc(num(m.value))}`).join('<br>') + `<br><small>API: ${esc(stamp(item.insights.api_collected_from))} a ${esc(stamp(item.insights.api_collected_to))}</small>` : 'Insights ainda sem coleta']);
      const coverage = kind === 'instagram_story' ? (row ? `<p class="mk-note">Retrato dos Stories disponíveis em ${esc(stamp(row.collected_at))}. A coleta foi guardada com este relatório; os Stories têm datas próprias.</p>` : sourceNote(row)) : sourceNote(row);
      document.getElementById(id).innerHTML = `<h3>${title}</h3>${coverage}<p>${esc(row?.payload?.coverage || '')} ${row?.payload?.pagination_truncated ? 'A API tem mais páginas além do limite desta coleta.' : ''}</p>${table(['Publicação', 'Formato', 'Publicada em', 'Legenda', 'Métricas acumuladas'], items)}<p>O alcance de cada publicação conserva sua cobertura. Pessoas podem aparecer em mais de uma publicação. Stories expirados antes da coleta ficam indisponíveis.</p>`;
    }
  }
  function renderReservations(data) {
    const rows = data?.rows || [];
    operationRows = rows;
    const publicRows = rows.filter(r => r.source === 'public_site');
    const total = key => publicRows.reduce((sum, row) => sum + Number(row[key] || 0), 0);
    document.getElementById('mk-reservations').innerHTML = `<h2>Reservas e comparecimentos</h2><p>Origem registrada no portal · ${esc(stamp(data?.collected_at))}. Reservas criadas de ${esc(day(filters.start))} a ${esc(day(filters.end))}; comparecimentos mostram o status atual dessa mesma coorte.</p>
      <div class="mk-cards">${card('Reservas do portal', num(total('reservations')))}${card('Comparecimentos da coorte', num(total('attended')))}${card('Aguardam desfecho', num(total('awaiting_outcome')))}${card('Origem declarada pelo cliente', 'Indisponível', 'Não há campo próprio confirmado nesta integração.')}</div>
      ${table(['Entrada', 'Origem UTM', 'Meio', 'Campanha', 'Conteúdo rastreado', 'Reservas', 'Comparecimentos', 'No-show', 'Canceladas / recusadas', 'Aguardam'], rows.map(r => [esc(r.source === 'public_site' ? 'Portal' : 'Painel / outra entrada'), esc(r.utm_source), esc(r.utm_medium || 'Sem identificador'), esc(r.utm_campaign || r.campaign_id || 'Sem identificador'), esc(r.utm_content || 'Sem identificador'), num(r.reservations), num(r.attended), num(r.no_show), num(r.cancelled), num(r.awaiting_outcome)]))}
      <p>Uma ligação com conteúdo exige o identificador no link usado pelo cliente. Registros antigos sem esse identificador permitem análise do canal. Receita confirmada por reserva indisponível: retorno financeiro permanece indisponível.</p>`;
  }
  function renderAds() {
    const row = latest('meta_ads'), p = row?.payload;
    const ads = p?.rows || [], currency = p?.account?.currency;
    const money = value => currency && numeric(value) != null ? new Intl.NumberFormat('pt-BR', { style: 'currency', currency }).format(Number(value)) : 'Indisponível';
    function costs(ad) {
      if (!operationRows || numeric(ad.spend) == null || row.status !== 'available' || p.truncated || !['America/Fortaleza','America/Sao_Paulo','America/Recife','America/Bahia'].includes(p.account?.timezone_name)) return 'Indisponível: cobertura, gasto ou fuso sem confirmação';
      const matched = operationRows.filter(r => r.source === 'public_site' && ['ig','instagram','fb','facebook','meta'].includes((r.utm_source || '').toLowerCase()) && ['paid_social','cpc','paid'].includes((r.utm_medium || '').toLowerCase()) && r.ad_id === ad.ad_id && r.campaign_id === ad.campaign_id);
      const total = key => matched.reduce((sum, r) => sum + Number(r[key] || 0), 0);
      if (!total('reservations')) return 'Indisponível: sem reservas com anúncio e campanha rastreados';
      return `${esc(money(Number(ad.spend) / total('reservations')))} / ${total('awaiting_outcome') ? 'Coorte aguarda desfecho' : total('attended') ? esc(money(Number(ad.spend) / total('attended'))) : 'Comparecimento sem denominador'}`;
    }
    const campaigns = new Map();
    for (const ad of ads) {
      const c = campaigns.get(ad.campaign_id) || { name: ad.campaign_name, spend: 0, impressions: 0, clicks: 0 };
      for (const key of ['spend','impressions','clicks']) c[key] = c[key] == null || numeric(ad[key]) == null ? null : c[key] + Number(ad[key]);
      campaigns.set(ad.campaign_id, c);
    }
    document.getElementById('mk-ads').innerHTML = `<h2>Anúncios Meta</h2>${sourceNote(row)}<p>Conta esperada: 1004410887092327. ${esc(p?.reason || p?.coverage || '')}</p>
      ${p?.account ? `<p>Conta confirmada: ${esc(p.account.name)} · ${esc(currency)} · ${esc(p.account.timezone_name)}. ${esc(p.attribution)}</p>` : '<p>Pendente de acesso à conta. O usuário do sistema do DeathStar precisa receber esse ativo no portfólio empresarial da Meta.</p>'}
      <p>Os totais de campanha somam os anúncios retornados nesta cobertura.</p>${table(['Campanha', 'Gasto', 'Impressões', 'Cliques'], Array.from(campaigns.values()).map(c => [esc(c.name), esc(money(c.spend)), num(c.impressions), num(c.clicks)]))}
      ${table(['Campanha / anúncio', 'Gasto', 'Alcance do anúncio', 'Ações creditadas pela Meta', 'Custo por reserva / comparecimento rastreado'], ads.map(ad => [esc(`${ad.campaign_name} / ${ad.ad_name} (${ad.ad_id})`), esc(money(ad.spend)), num(ad.reach), esc((ad.actions || []).map(a => `${a.action_type}: ${a.value}`).join('; ') || 'Sem ações retornadas'), costs(ad)]))}
      <p>Gasto e ações seguem o período e a atribuição da Meta. As ações mantêm seus nomes originais. Os custos usam apenas reservas com fonte paga, anúncio e campanha identificados na coorte de criação; essa relação conserva os limites do rastreamento. Uma ação recebida pela CAPI ainda precisa do relatório de atribuição para obter crédito em anúncios.</p>`;
    const ga = latest('ga4');
    document.getElementById('mk-ga').innerHTML = `<h2>Google Analytics</h2>${sourceNote(ga)}<p>${esc(ga?.payload?.reason || ga?.payload?.coverage || '')}</p>
      ${ga?.payload?.subject_to_thresholding ? '<p>A consulta está sujeita aos limiares de privacidade do Google.</p>' : ''}
      ${ga?.payload?.data_loss_from_other_row ? '<p>O Google agrupou parte dos dados em outra linha.</p>' : ''}
      ${table(['Origem / meio', 'Campanha medida', 'Conteúdo medido', 'Evento', 'Eventos'], (ga?.payload?.rows || []).map(r => [esc(r.sessionSourceMedium), esc(r.sessionCampaignName), esc(r.sessionManualAdContent), esc(r.eventName), num(r.events)]))}
      <p>Eventos por data de ocorrência no portal e fuso ${esc(ga?.payload?.timezone || 'indisponível')}. Consentimento, processamento e bloqueios podem reduzir a cobertura medida. Os totais ficam separados dos registros operacionais.</p>`;
  }
  function renderEditorial() {
    const photos = snapshots.find(s => s.source === 'google_photos');
    document.getElementById('mk-photo-candidates').innerHTML = `<h3>Fotos Instagram preparadas para o Google</h3>${photos ? `<p>Conferidas em ${esc(stamp(photos.collected_at))}. ${esc(photos.payload.coverage)}</p>` : '<p>Execute a preparação privada para conferir fotos e duplicidade na ficha atual.</p>'}${table(['Foto própria', 'Dimensões / tamanho', 'Conferência', 'Ação'], (photos?.payload?.items || []).map(p => [safeLink(p.permalink, p.id), esc(`${p.width} × ${p.height} · ${num(p.bytes)} bytes`), esc(p.duplicate ? 'Foto parecida já encontrada na ficha' : p.technical_quality ? 'Requer revisão visual e direito de uso' : 'Qualidade técnica insuficiente'), !p.duplicate && p.technical_quality ? `<button type="button" data-photo="${esc(p.id)}">Preparar rascunho Google</button>` : 'Revisar']))}`;
    document.getElementById('mk-editorial-list').innerHTML = table(['Próvia', 'Destino / formato', 'Programado (Fortaleza)', 'Estado / confirmação', 'Ações'], editorial.map(item => [
      `<p class="mk-caption">${esc(item.caption)}</p>${item.media_url ? safeLink(item.media_url, 'Abrir mídia própria') : ''}${item.source_media_id ? `<p>Foto de origem: ${esc(item.source_media_id)}</p>` : ''}`,
      esc(`${item.target} / ${item.format}`), esc(stamp(item.scheduled_at)),
      `${esc(states[item.status])}<br>${item.approved_at ? `Revisão ${item.approved_revision} aprovada em ${esc(stamp(item.approved_at))}<br>` : ''}${item.provider_id ? esc('ID: ' + item.provider_id) : ''}${item.provider_url ? '<br>'+safeLink(item.provider_url, 'Conferir publicação') : ''}${item.last_error ? '<br>'+esc(item.last_error) : ''}`,
      `${['draft','review','approved','failed','cancelled'].includes(item.status) ? `<button type="button" data-edit="${esc(item.id)}">Editar</button>` : ''}
       ${item.status === 'draft' ? `<button type="button" data-action="review" data-id="${esc(item.id)}">Enviar para revisão</button>` : ''}
       ${item.status === 'review' && owner ? (item.format === 'TEXT' || item.verified_revision === item.revision) ? `<button type="button" data-action="approve" data-id="${esc(item.id)}">Aprovar conteúdo e data</button>` : 'Aguardando validação do arquivo desta revisão' : ''}
       ${['draft','review','approved','failed'].includes(item.status) ? `<button type="button" data-action="cancel" data-id="${esc(item.id)}">Cancelar</button>` : ''}`]));
    document.getElementById('mk-owner').textContent = owner ? 'Esta sessão pode aprovar conteúdo e data. A aprovação guarda sua identidade e a revisão do item.' : 'A aprovação exige a conta do proprietário. A equipe pode preparar e enviar rascunhos para revisão.';
  }
  function renderComments() {
    const coverage = latest('access', 'comments');
    document.getElementById('mk-comment-coverage').innerHTML = `${sourceNote(coverage)}<p>${esc(coverage?.payload?.coverage || '')} ${esc((coverage?.payload?.limitations || []).join(' '))}${commentLimit ? ' Exibindo os primeiros 500 comentários; a coleta permanece no banco privado.' : ''}</p>`;
    document.getElementById('mk-comment-list').innerHTML = comments.map(c => `<article class="mk-comment"><p>${safeLink(c.media_url, c.network + ' · ' + c.media_id)} · ${esc(stamp(c.posted_at))}</p><p class="mk-caption">${esc(c.body)}</p>
      <form data-comment="${esc(c.id)}"><label>Tipo<select name="category">${[['review','Revisar'],['question','Pergunta'],['complaint','Reclamação'],['other','Outro']].map(([v,t]) => `<option value="${v}" ${c.category === v ? 'selected' : ''}>${t}</option>`).join('')}</select></label>
      <label>Tratamento<select name="state">${[['new','Novo'],['reviewing','Em tratamento'],['handled','Concluído']].map(([v,t]) => `<option value="${v}" ${c.state === v ? 'selected' : ''}>${t}</option>`).join('')}</select></label>
      <label>Registro interno<textarea name="note" maxlength="1000">${esc(c.note)}</textarea></label><button type="submit">Salvar revisão humana</button></form></article>`).join('') || '<p>Nenhum comentário nesta cobertura.</p>';
  }
  async function load() {
    const version = ++loadVersion;
    filters = { start: document.getElementById('mk-start').value, end: document.getElementById('mk-end').value };
    if (!filters.start || !filters.end || Date.parse(filters.end) < Date.parse(filters.start) || Date.parse(filters.end) - Date.parse(filters.start) > 29 * 86400000) { notice('Selecione um período de 1 a 30 dias.'); return; }
    notice('Consultando dados privados…');
    const results = await Promise.allSettled([
      sb.rpc('marketing_dashboard_snapshots', { p_start: filters.start, p_end: filters.end }),
      sb.rpc('marketing_reservations', { p_start: filters.start, p_end: filters.end }),
      sb.from('marketing_editorial').select('*').order('updated_at', { ascending: false }).limit(100),
      sb.from('marketing_comments').select('*').gte('posted_at', filters.start + 'T00:00:00-03:00').lt('posted_at', new Date(Date.parse(filters.end + 'T00:00:00-03:00') + 86400000).toISOString()).order('posted_at', { ascending: false }).limit(501),
      sb.rpc('marketing_is_owner')
    ]);
    if (version !== loadVersion) return;
    const result = index => results[index].status === 'fulfilled' && !results[index].value.error ? results[index].value.data : null;
    snapshots = result(0) || []; editorial = result(2) || []; comments = (result(3) || []).slice(0, 500); commentLimit = (result(3) || []).length > 500; owner = result(4) === true;
    operationRows = null;
    if (result(1)) renderReservations(result(1)); else document.getElementById('mk-reservations').innerHTML = '<h2>Reservas e comparecimentos</h2><p>Consulta indisponível. Confira a sessão e a permissão da página.</p>';
    renderInstagram(); renderAds(); renderEditorial(); renderComments();
    notice(results.some(r => r.status === 'rejected' || r.value?.error) ? 'Parte das consultas ficou indisponível. Confira sua sessão e o acesso ao painel.' : 'Dados carregados. Os horários usam America/Fortaleza. Cada fonte informa sua cobertura.');
  }
  function setPreview() {
    const form = document.getElementById('mk-draft');
    document.getElementById('mk-preview').textContent = `${form.elements.target.value} · ${form.elements.format.value}\n${form.elements.caption.value}\n${form.elements.media_url.value}\nProgramação: ${form.elements.scheduled_at.value || 'A definir'} (Fortaleza)`;
    const area = document.getElementById('mk-media-preview'); area.replaceChildren();
    try {
      const url = new URL(form.elements.media_url.value);
      if (url.protocol === 'https:' && ['www.sirfisher.com.br','sirfisher.com.br'].includes(url.hostname)) {
        const video = form.elements.format.value === 'REELS' || /\.mp4$/i.test(url.pathname);
        const media = document.createElement(video ? 'video' : 'img'); media.src = url.href;
        if (video) { media.controls = true; media.preload = 'metadata'; } else media.alt = 'Prévia da mídia própria para revisão';
        area.appendChild(media);
      }
    } catch (_) { /* Campo ainda incompleto. */ }
  }
  async function start() {
    if (!await SirFisherAuth.requireRole(sb)) return;
    main.innerHTML = `<div class="mk-wrap"><h1>Marketing e reservas</h1><p>Instagram, anúncios e registros do portal. Cada fonte conserva seu período e sua forma de medir.</p>
      <form id="mk-filter" class="mk-filter"><label>Início<input id="mk-start" type="date" required></label><label>Fim<input id="mk-end" type="date" required></label><button type="submit">Consultar período</button></form>
      <p id="mk-message" role="status" aria-live="polite"></p><nav class="mk-nav" aria-label="Áreas de marketing"><a href="#mk-instagram">Instagram</a><a href="#mk-reservations">Reservas</a><a href="#mk-ads">Anúncios</a><a href="#mk-editorial">Publicações e fotos</a><a href="#mk-comments">Comentários</a><a href="https://reservas.sirfisher.com.br/admin/links-marketing.html">Criar link identificado</a></nav>
      <section id="mk-instagram"></section><section id="mk-media"></section><section id="mk-stories"></section><section id="mk-reservations"></section><section id="mk-ads"></section><section id="mk-ga"></section>
      <section id="mk-editorial"><h2>Publicações e fotos para revisão</h2><p id="mk-owner"></p><p>Instagram: imagem, Reel ou Story. Facebook: texto ou foto. Fotos Google usam a ferramenta e a autorização já existentes. Use arquivos próprios hospedados no site; preparar uma foto do Instagram exige conferir seu ID, qualidade e duplicidade.</p>
      <form id="mk-draft"><input name="id" type="hidden"><input name="revision" type="hidden"><div class="mk-grid"><label>Destino<select name="target"><option value="instagram">Instagram</option><option value="facebook">Página do Facebook</option><option value="google_photo">Foto no Perfil Google</option></select></label><label>Formato<select name="format"><option>IMAGE</option><option>REELS</option><option>STORIES</option><option>TEXT</option><option>PHOTO</option></select></label>
      <label>Data e hora em Fortaleza<input name="scheduled_at" type="datetime-local"></label><label>ID de origem da foto Instagram<input name="source_media_id" inputmode="numeric"></label></div>
      <label>Legenda ou texto<textarea name="caption" maxlength="2200" rows="4"></textarea></label><label>URL pública da mídia própria no site<input name="media_url" type="url" placeholder="https://www.sirfisher.com.br/assets/img/…"></label>
      <label class="mk-check"><input type="checkbox" name="rights_confirmed">Conferi o direito de uso e as autorizações das pessoas retratadas.</label><label class="mk-check"><input type="checkbox" name="quality_confirmed">Revisei o arquivo, o formato e a qualidade. Para foto Google, conferi também a duplicidade.</label>
      <div id="mk-preview" class="mk-preview" aria-label="Prévia do rascunho"></div><div id="mk-media-preview"></div><button type="submit">Salvar rascunho</button><button type="reset">Novo rascunho</button></form><p>Salvar alterações retira a aprovação anterior. O envio exige aprovação da revisão, do arquivo validado e da data pelo proprietário. O executor aceita até uma hora após o horário aprovado; fora dessa janela o item exige outra revisão. A API confirma o recebimento; o Google ainda pode revisar a exibição pública.</p><div id="mk-photo-candidates"></div><div id="mk-editorial-list"></div></section>
      <section id="mk-comments"><h2>Comentários das próprias publicações</h2><p>Classifique perguntas e reclamações e registre o tratamento. A equipe responde pela interface da rede social. Este fluxo salva somente a revisão interna.</p><div id="mk-comment-coverage"></div><div id="mk-comment-list"></div></section>
      <section><h2>Coleta e envio</h2><p>A coleta privada guarda o histórico no portal. A fila conserva a programação; o executor confere aprovação e horário antes de enviar. A coleta contínua e o envio programado aguardam incorporação ao executor existente. Até essa etapa, a equipe acompanha os instantes de coleta e executa os itens aprovados pelo procedimento de operação.</p></section></div>`;
    const end = new Date(Date.now() - 2 * 86400000).toLocaleDateString('en-CA', { timeZone: 'America/Fortaleza' });
    const begin = new Date(end + 'T12:00:00Z'); begin.setUTCDate(begin.getUTCDate() - 29);
    document.getElementById('mk-start').value = begin.toISOString().slice(0, 10); document.getElementById('mk-end').value = end;
    document.getElementById('mk-filter').addEventListener('submit', e => { e.preventDefault(); load().catch(() => notice('Consulta indisponível. Tente novamente.')); });
    const form = document.getElementById('mk-draft'); form.addEventListener('input', setPreview); form.addEventListener('reset', () => { setTimeout(() => { form.elements.id.value = ''; setPreview(); }, 0); });
    form.addEventListener('submit', async e => {
      e.preventDefault(); const f = form.elements;
      const p_item = { expected_revision: f.revision.value ? Number(f.revision.value) : null, target: f.target.value, format: f.format.value, caption: f.caption.value, media_url: f.media_url.value, source_media_id: f.source_media_id.value, scheduled_at: f.scheduled_at.value ? f.scheduled_at.value + ':00-03:00' : null, rights_confirmed: f.rights_confirmed.checked, quality_confirmed: f.quality_confirmed.checked };
      const { data, error } = await sb.rpc('marketing_save_draft', { p_item, p_id: f.id.value || null });
      if (error) { notice('Não foi possível salvar. Confira destino, formato e URL de mídia própria no site.'); return; }
      const check = await sb.from('marketing_editorial').select('id,status').eq('id', data).single();
      if (check.error || check.data.status !== 'draft') { notice('Gravação sem confirmação. Recarregue antes de repetir.'); return; }
      form.reset(); await load(); notice('Rascunho salvo e conferido por nova leitura.');
    });
    main.addEventListener('click', async e => {
      const photo = e.target.closest('[data-photo]');
      if (photo) {
        form.reset(); form.elements.target.value = 'google_photo'; form.elements.format.value = 'PHOTO'; form.elements.source_media_id.value = photo.dataset.photo;
        setPreview(); form.scrollIntoView(); return;
      }
      const edit = e.target.closest('[data-edit]');
      if (edit) {
        const item = editorial.find(r => r.id === edit.dataset.edit); if (!item) return;
        for (const key of ['id','revision','target','format','caption','media_url','source_media_id']) form.elements[key].value = item[key] || '';
        form.elements.scheduled_at.value = item.scheduled_at ? new Date(new Date(item.scheduled_at).getTime() - 3 * 3600000).toISOString().slice(0, 16) : '';
        for (const key of ['rights_confirmed','quality_confirmed']) form.elements[key].checked = item[key];
        setPreview(); form.scrollIntoView(); return;
      }
      const button = e.target.closest('[data-action]'); if (!button) return;
      button.disabled = true;
      const item = editorial.find(r => r.id === button.dataset.id);
      const r = await sb.rpc('marketing_review', { p_id: button.dataset.id, p_action: button.dataset.action, p_expected_revision: item?.revision });
      if (r.error) { notice('Ação indisponível. Aprovação exige proprietário, qualidade, direito de uso e data futura.'); button.disabled = false; return; }
      const check = await sb.from('marketing_editorial').select('status').eq('id', button.dataset.id).single();
      const expected = { review: 'review', approve: 'approved', cancel: 'cancelled' }[button.dataset.action];
      await load(); notice(check.data?.status === expected ? 'Estado salvo e conferido por nova leitura.' : 'Estado sem confirmação; recarregue antes de repetir.');
    });
    main.addEventListener('submit', async e => {
      const f = e.target.closest('[data-comment]'); if (!f) return; e.preventDefault();
      const r = await sb.rpc('marketing_handle_comment', { p_id: f.dataset.comment, p_category: f.elements.category.value, p_state: f.elements.state.value, p_note: f.elements.note.value });
      if (r.error) { notice('Não foi possível salvar o tratamento.'); return; }
      const check = await sb.from('marketing_comments').select('state,note,category').eq('id', f.dataset.comment).single();
      const verified = !check.error && check.data.state === f.elements.state.value && check.data.note === f.elements.note.value && check.data.category === f.elements.category.value;
      await load(); notice(verified ? 'Revisão salva e conferida por nova leitura.' : 'Gravação sem confirmação. Confira antes de repetir.');
    });
    setPreview(); await load();
  }
  start().catch(() => { main.textContent = 'Não foi possível carregar marketing. Entre novamente e confira seu acesso.'; });
})();
