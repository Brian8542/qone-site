/* QONE Yiwu Collection — sample list, catalog filters, product modal, form */
(function () {
  'use strict';
  var d = document, W = window.YW || {}, T = W.t || {};
  var KEY = 'yw_list_v1';
  function $(s, r) { return (r || d).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || d).querySelectorAll(s)); }
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var ICON_X = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';

  /* ---------- sample list (localStorage, falls back to memory) ---------- */
  var mem = [];
  function load() { try { var v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return mem; } }
  function save(v) { mem = v; try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }
  var list = load();
  // ?items=Y-0001,Y-0002 (from a shared link) is merged into the list
  try {
    var qp = new URLSearchParams(location.search).get('items');
    if (qp) qp.split(',').forEach(function (id) { id = id.trim(); if (/^Y-\d{4}$/.test(id) && !has(id)) { var li = d.getElementById(id), m = (window.YWI || {})[id]; list.push(li ? meta(li) : m ? { id: id, n: m[0], ph: m[1], s: m[2] } : { id: id, n: id, ph: '' }); } });
    save(list);
  } catch (e) {}
  function has(id) { return list.some(function (x) { return x.id === id; }); }
  function meta(li) { return { id: li.dataset.id, n: li.dataset.n, ph: li.dataset.ph, s: li.dataset.s }; }
  function toggle(it) {
    if (has(it.id)) list = list.filter(function (x) { return x.id !== it.id; }); else list.push(it);
    save(list); render(); var b = $('.lbtn'); if (b) { b.classList.remove('bump'); void b.offsetWidth; b.classList.add('bump'); }
  }
  function sendHref() { return W.req + (list.length ? '?items=' + list.map(function (x) { return x.id; }).join(',') : ''); }
  function render() {
    $$('.lcount').forEach(function (c) { c.textContent = list.length; });
    $$('.lbtn').forEach(function (b) { b.classList.toggle('has', list.length > 0); });
    $$('.pc').forEach(function (li) {
      var on = has(li.dataset.id), a = $('.pc-a', li);
      li.classList.toggle('in', on);
      if (a) { a.setAttribute('aria-pressed', on ? 'true' : 'false'); a.setAttribute('aria-label', (on ? T.added : T.add) + ': ' + li.dataset.n); }
    });
    var dr = $('#list'); if (dr) {
      dr.classList.toggle('empty', !list.length);
      $('.dr-ul', dr).innerHTML = list.map(function (x) {
        return '<li><img src="/assets/yw/img/t/' + esc(x.ph) + '.jpg" alt="" width="56" height="56" loading="lazy"><span><b>' + esc(x.n) + '</b><small>' + esc(x.id) + (x.s ? ' / ' + esc(x.s) : '') + '</small></span><button type="button" data-rm="' + esc(x.id) + '">' + esc(T.remove) + '</button></li>';
      }).join('');
      var sl = $('[data-send-list]', dr); if (sl) sl.href = sendHref();
    }
    var rl = $('.rq-list'), ta = $('#f-items');
    if (rl) {
      rl.innerHTML = list.map(function (x) { return '<span>' + esc(x.id) + ' ' + esc(x.n) + '<button type="button" data-rm="' + esc(x.id) + '" aria-label="' + esc(T.remove) + ' ' + esc(x.n) + '">' + ICON_X + '</button></span>'; }).join('');
      if (ta && !ta.dataset.touched) ta.value = list.map(function (x) { return x.id + ' — ' + x.n + (x.s ? ' (' + x.s + ')' : ''); }).join('\n');
    }
    syncModalBtn();
  }

  /* ---------- drawer ---------- */
  var dr = $('#list'), lastFocus = null;
  function openList() { if (!dr) return; lastFocus = d.activeElement; dr.hidden = false; d.body.style.overflow = 'hidden'; var b = $('.dr-hd .ib', dr); if (b) b.focus(); }
  function closeList() { if (!dr) return; dr.hidden = true; d.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); }
  d.addEventListener('click', function (ev) {
    var t = ev.target.closest('[data-open-list],[data-close-list],[data-clear-list],[data-rm],.pc-a,.pc-o,[data-room],[data-lb]');
    if (!t) return;
    if (t.matches('[data-open-list]')) { openList(); }
    else if (t.matches('[data-close-list]')) { closeList(); }
    else if (t.matches('[data-clear-list]')) { list = []; save(list); render(); }
    else if (t.matches('[data-rm]')) { list = list.filter(function (x) { return x.id !== t.dataset.rm; }); save(list); render(); }
    else if (t.matches('.pc-a')) { toggle(meta(t.closest('.pc'))); }
    else if (t.matches('.pc-o')) { openModal(t.closest('.pc')); }
    else if (t.matches('[data-room]')) { var r = $('.room-r'); if (r) r.scrollBy({ left: (+t.dataset.room) * r.clientWidth * 0.7, behavior: 'smooth' }); }
    else if (t.matches('[data-lb]')) {
      ev.preventDefault(); var box = d.createElement('div'); box.className = 'lbx'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.tabIndex = -1;
      box.innerHTML = '<img src="' + t.getAttribute('href') + '" alt="' + esc(($('img', t) || {}).alt) + '">'; d.body.appendChild(box); box.focus();
      var kill = function () { box.remove(); d.removeEventListener('keydown', esck); t.focus(); }, esck = function (k) { if (k.key === 'Escape') kill(); };
      box.addEventListener('click', kill); d.addEventListener('keydown', esck);
    }
  });
  d.addEventListener('keydown', function (k) { if (k.key === 'Escape' && dr && !dr.hidden) closeList(); });

  /* ---------- product modal ---------- */
  var md = $('#md'), cur = null;
  function visible() { return $$('.pc').filter(function (li) { return !li.hidden; }); }
  function openModal(li) {
    if (!md || !li) return; cur = li; var D = li.dataset;
    var src = $('source', md), img = $('img', md);
    var dir = D.l ? 'l' : 't'; img.src = '/assets/yw/img/' + dir + '/' + D.ph + '.jpg'; src.srcset = '/assets/yw/img/' + dir + '/' + D.ph + '.avif'; img.alt = D.n;
    var w = +D.w, h = +D.h, k = 440 / Math.max(w, h); img.width = Math.round(w * k); img.height = Math.round(h * k);
    $('.md-ref', md).textContent = D.id + (D.r ? '  /  ' + D.r : '');
    $('#md-n').textContent = D.n;
    var f = { c: (W.cat || {})[D.c] || D.c, s: D.s, mt: D.mt, p: D.p, ct: D.ct, m: (W.mk || {})[D.m] || D.m };
    $$('[data-f]', md).forEach(function (dd) { var v = f[dd.dataset.f]; dd.textContent = v || '—'; });
    syncModalBtn();
    if (!md.open) { if (md.showModal) md.showModal(); else md.setAttribute('open', ''); }
    if (history.replaceState) history.replaceState(null, '', '#' + D.id);
  }
  function syncModalBtn() {
    if (!md || !cur) return; var b = $('.md-add', md), on = has(cur.dataset.id);
    b.setAttribute('aria-pressed', on ? 'true' : 'false'); $('span', b).textContent = on ? b.dataset.lAdded : b.dataset.lAdd;
  }
  if (md) {
    md.addEventListener('click', function (ev) {
      if (ev.target === md || ev.target.closest('[data-md-close]')) { md.close(); return; }
      if (ev.target.closest('.md-add')) { toggle(meta(cur)); return; }
      var dir = ev.target.closest('[data-md-prev]') ? -1 : ev.target.closest('[data-md-next]') ? 1 : 0;
      if (dir) step(dir);
    });
    md.addEventListener('keydown', function (k) { if (k.key === 'ArrowRight') step(1); if (k.key === 'ArrowLeft') step(-1); });
    md.addEventListener('close', function () { if (history.replaceState) history.replaceState(null, '', location.pathname + location.search); if (cur) { var o = $('.pc-o', cur); if (o) o.focus({ preventScroll: true }); } });
  }
  function step(dir) { var v = visible(), i = v.indexOf(cur); if (i < 0) return; openModal(v[(i + dir + v.length) % v.length]); }

  /* ---------- catalog filters ---------- */
  var grid = $('#grid'), q = $('#q'), cnt = $('.cnt');
  var st = { c: '', m: '', q: '' };
  function apply() {
    if (!grid) return; var n = 0, terms = st.q.toLowerCase().split(/\s+/).filter(Boolean);
    $$('.pc', grid).forEach(function (li) {
      var ok = (!st.c || li.dataset.c === st.c) && (!st.m || li.dataset.m === st.m) && terms.every(function (t) { return li.dataset.q.indexOf(t) > -1; });
      li.hidden = !ok; if (ok) n++;
    });
    if (cnt) cnt.textContent = (T.showing || '{n}/{t}').replace('{n}', n).replace('{t}', cnt.dataset.total);
    var none = $('.none'); if (none) none.hidden = n > 0;
    $$('.chip[data-cat]').forEach(function (c) { c.setAttribute('aria-pressed', c.dataset.cat === st.c ? 'true' : 'false'); });
    $$('[data-mk]').forEach(function (c) { c.setAttribute('aria-pressed', c.dataset.mk === st.m ? 'true' : 'false'); });
    try { var u = new URLSearchParams(location.search); ['c', 'm', 'q'].forEach(function (k) { if (st[k]) u.set(k, st[k]); else u.delete(k); }); u.delete('items');
      var s = u.toString(); history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash); } catch (e) {}
  }
  if (grid && cnt) {
    try { var u0 = new URLSearchParams(location.search); st.c = u0.get('c') || ''; st.m = u0.get('m') || ''; st.q = u0.get('q') || ''; if (q) q.value = st.q; } catch (e) {}
    $$('.chip[data-cat]').forEach(function (c) { c.addEventListener('click', function () { st.c = c.dataset.cat; apply(); }); });
    $$('[data-mk]').forEach(function (c) { c.addEventListener('click', function () { st.m = c.dataset.mk; apply(); }); });
    var tmr; if (q) q.addEventListener('input', function () { clearTimeout(tmr); tmr = setTimeout(function () { st.q = q.value.trim(); apply(); }, 120); });
    var rs = $('[data-reset]'); if (rs) rs.addEventListener('click', function () { st = { c: '', m: '', q: '' }; if (q) q.value = ''; apply(); });
    apply();
    var fb = $('.fb'); if (fb && 'IntersectionObserver' in window) { var sen = d.createElement('div'); sen.style.height = '1px'; fb.parentNode.insertBefore(sen, fb);
      new IntersectionObserver(function (es) { fb.classList.toggle('stuck', !es[0].isIntersecting); }, { rootMargin: '-' + (parseInt(getComputedStyle(d.documentElement).getPropertyValue('--hd')) || 64) + 'px 0px 0px 0px' }).observe(sen); }
  }
  // open product from #Y-0001
  if (location.hash && /^#Y-\d{4}$/.test(location.hash)) { var tg = d.getElementById(location.hash.slice(1)); if (tg && md) setTimeout(function () { tg.scrollIntoView({ block: 'center' }); openModal(tg); }, 60); }

  /* ---------- autoplay video only when visible and motion allowed ---------- */
  var rm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  $$('video[data-auto]').forEach(function (v) {
    if (rm) { v.controls = true; return; }
    if (!('IntersectionObserver' in window)) { v.preload = 'auto'; v.play().catch(function () {}); return; }
    new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { v.preload = 'auto'; v.play().catch(function () { v.controls = true; }); } else v.pause(); }); }, { threshold: .25 }).observe(v);
  });

  /* ---------- request form ---------- */
  var f = $('#ywf');
  if (f) {
    var ta = $('#f-items'); if (ta) ta.addEventListener('input', function () { ta.dataset.touched = '1'; });
    var files = $$('input[type=file]', f), sum = $('.sum', f), msg = $('.msg', f), btn = $('button[type=submit]', f);
    function total() { var t = 0; files.forEach(function (i) { [].forEach.call(i.files || [], function (x) { t += x.size; }); }); return t; }
    files.forEach(function (i) { i.addEventListener('change', function () { var t = total(); sum.textContent = t ? (t / 1048576).toFixed(1) + ' MB / 10 MB' : ''; sum.style.color = t > 10485760 ? '#C4123F' : ''; }); });
    f.addEventListener('submit', function (ev) {
      var bad = null; msg.textContent = '';
      $$('[required]', f).forEach(function (el) {
        var ok = el.type === 'checkbox' ? el.checked : el.value.trim() !== '';
        if (ok && el.type === 'email') ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
        el.classList.toggle('bad', !ok); if (!ok && !bad) bad = el;
      });
      if (bad) { ev.preventDefault(); msg.textContent = bad.type === 'email' && bad.value ? T.err_em : T.err_req; bad.focus(); return; }
      if (total() > 10485760) { ev.preventDefault(); msg.textContent = T.err_size; return; }
      var co = $('#f-co').value.trim(), ct = $('#f-ct').value.trim();
      f.querySelector('[name=_subject]').value = T.subj + ' ' + co + ' / ' + ct + (list.length ? ' / ' + list.length + ' items' : '');
      f.querySelector('[name=_replyto]').value = $('#f-em').value.trim();
      btn.disabled = true; btn.textContent = T.sending;
    });
    window.addEventListener('pageshow', function () { btn.disabled = false; btn.textContent = T.send; });
  }
  render();
})();
