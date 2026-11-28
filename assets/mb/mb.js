/* QONE x marburg-style skin: dropdown menus, site search, hero slider, catalog carousel. */
(function () {
  var d = document, qa = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };

  /* dropdowns (click/tap + keyboard; hover handled in CSS on desktop) */
  var its = qa('.mbh .mb-it');
  function closeAll(ex) { its.forEach(function (it) { if (it !== ex) { it.classList.remove('open'); var b = it.querySelector('.mb-top'); if (b) b.setAttribute('aria-expanded', 'false'); } }); }
  its.forEach(function (it) {
    var b = it.querySelector('button.mb-top'); if (!b) return;
    b.addEventListener('click', function (e) { e.stopPropagation(); var o = !it.classList.contains('open'); closeAll(it); it.classList.toggle('open', o); b.setAttribute('aria-expanded', String(o)); });
  });
  d.addEventListener('click', function (e) { if (!e.target.closest('.mb-it')) closeAll(); if (!e.target.closest('.mb-search')) qa('.mb-sr').forEach(function (r) { r.classList.remove('on'); }); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeAll(); qa('.mb-sr').forEach(function (r) { r.classList.remove('on'); }); } });

  /* search: per-language JSON index, loaded on first focus */
  var cache = {};
  function load(l) { if (!cache[l]) cache[l] = fetch('/assets/mb/search-' + l + '.json').then(function (r) { return r.json(); }).catch(function () { return []; }); return cache[l]; }
  function norm(s) { return (s || '').toLowerCase(); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  qa('.mb-search').forEach(function (f) {
    var inp = f.querySelector('input'), box = f.querySelector('.mb-sr'), l = f.getAttribute('data-lang') || 'en', act = -1, hits = [];
    inp.addEventListener('focus', function () { load(l); });
    function render() {
      var q = norm(inp.value).trim(); act = -1;
      if (q.length < 2) { box.classList.remove('on'); box.innerHTML = ''; return; }
      load(l).then(function (ix) {
        var t = q.split(/\s+/);
        hits = ix.map(function (x) { var a = norm(x.t), b = norm(x.d), s = 0; for (var i = 0; i < t.length; i++) { if (a.indexOf(t[i]) > -1) s += 3; else if (b.indexOf(t[i]) > -1) s += 1; else return null; } return { x: x, s: s }; })
          .filter(Boolean).sort(function (p, q2) { return q2.s - p.s; }).slice(0, 8);
        box.innerHTML = hits.length ? hits.map(function (h) { return '<a href="' + esc(h.x.u) + '">' + esc(h.x.t) + (h.x.d ? '<small>' + esc(h.x.d) + '</small>' : '') + '</a>'; }).join('') : '<p>' + esc(box.getAttribute('data-none')) + '</p>';
        box.classList.add('on');
      });
    }
    inp.addEventListener('input', render);
    inp.addEventListener('keydown', function (e) {
      var as = qa('a', box); if (!as.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); act = (act + (e.key === 'ArrowDown' ? 1 : -1) + as.length) % as.length; as.forEach(function (a, i) { a.classList.toggle('act', i === act); }); }
    });
    f.addEventListener('submit', function (e) { e.preventDefault(); var as = qa('a', box); if (as.length) location.href = as[Math.max(act, 0)].href; });
  });

  /* hero slider */
  var hero = d.querySelector('.mb-hero');
  if (hero) {
    var sl = qa('.mb-slide', hero), dots = qa('.mb-dots button', hero), i = 0, tm;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    function go(n) { i = (n + sl.length) % sl.length; sl.forEach(function (s, k) { s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', String(k !== i)); }); dots.forEach(function (b, k) { b.classList.toggle('on', k === i); }); }
    function auto() { clearInterval(tm); if (!reduce) tm = setInterval(function () { go(i + 1); }, 6500); }
    hero.querySelector('.mb-prev').addEventListener('click', function () { go(i - 1); auto(); });
    hero.querySelector('.mb-next').addEventListener('click', function () { go(i + 1); auto(); });
    dots.forEach(function (b) { b.addEventListener('click', function () { go(+b.getAttribute('data-go')); auto(); }); });
    var x0 = null; hero.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) { go(i + (dx < 0 ? 1 : -1)); auto(); } x0 = null; });
    go(0); auto();
  }

  /* catalog carousel */
  qa('[data-car]').forEach(function (c) {
    var t = c.querySelector('.mb-car-t'), dd = c.querySelector('.mb-car-d'), items = qa('.mb-cov', t);
    function per() { return Math.max(1, Math.round(t.clientWidth / (items[0].getBoundingClientRect().width || 1))); }
    function pages() { return Math.max(1, Math.ceil(items.length / per())); }
    function build() { var n = pages(); dd.innerHTML = ''; for (var k = 0; k < n; k++) { var b = d.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', String(k + 1)); (function (k) { b.addEventListener('click', function () { t.scrollLeft = k * t.clientWidth; }); })(k); dd.appendChild(b); } mark(); }
    function mark() { var k = Math.round(t.scrollLeft / Math.max(1, t.clientWidth)); qa('button', dd).forEach(function (b, j) { b.classList.toggle('on', j === k); }); }
    c.querySelector('.mb-car-p').addEventListener('click', function () { t.scrollLeft -= t.clientWidth; });
    c.querySelector('.mb-car-n').addEventListener('click', function () { t.scrollLeft += t.clientWidth; });
    t.addEventListener('scroll', function () { window.requestAnimationFrame(mark); }, { passive: true });
    window.addEventListener('resize', build); build();
  });
})();
