/* QONE v28 — interactions. One rAF loop, transform/opacity only, entrance via Web Animations API.
   FAQ adapted from Lucian UX/UI Prompt #044 · MIT License (c) 2026 Seokwoooo · https://lucianlabs.dev/uxui-prompt/#044
   Inquiry wizard adapted from Lucian UX/UI Prompt #042 · MIT License (c) 2026 Seokwoooo · https://lucianlabs.dev/uxui-prompt/#042 */
(function () {
  var d = document, html = d.documentElement, W = window;
  function qa(s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
  function q(s, r) { return (r || d).querySelector(s); }
  var params = new URLSearchParams(location.search);
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cfg = { motion: 'full', heroScene: 'globe', cursorGlow: false };
  if (params.has('tweak')) { try { var sv = JSON.parse(localStorage.getItem('qone-tweak') || 'null'); if (sv) for (var k in sv) cfg[k] = sv[k]; } catch (e) {} }
  if (reduce) cfg.motion = 'off';
  W.QONE_CFG = cfg;
  if (cfg.motion === 'off') html.classList.add('motion-off');
  var EASE = 'cubic-bezier(.16,1,.3,1)';
  var touch = matchMedia('(hover: none)').matches;
  var full = cfg.motion === 'full', anim = cfg.motion !== 'off';
  var STR = W.QONE_STR || {};

  /* ---------- header: progress + menu ---------- */
  var prog = q('.prog'), menu = q('.menu');
  qa('[data-menu]').forEach(function (b) {
    b.addEventListener('click', function () {
      var open = !menu.classList.contains('open');
      menu.classList.toggle('open', open); d.body.style.overflow = open ? 'hidden' : '';
      qa('[data-menu]').forEach(function (x) { x.setAttribute('aria-expanded', String(open)); });
    });
  });
  qa('.menu a').forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('open'); d.body.style.overflow = ''; }); });

  /* ---------- entrances (only for elements below the first screen) ---------- */
  var vh = innerHeight;
  var KF = {
    t: [{ opacity: 0, transform: 'perspective(800px) translateY(48px) rotateX(-14deg)', filter: 'blur(8px)' }, { opacity: 1, transform: 'none', filter: 'blur(0)' }],
    u: [{ opacity: 0, transform: 'translateY(32px)' }, { opacity: 1, transform: 'none' }]
  };
  var dur = full ? 1200 : 700;
  function play(el) {
    var kind = el.getAttribute('data-r');
    if (kind === 's') {
      qa(':scope > *', el).forEach(function (c, i) {
        c.animate(KF.u, { duration: dur, delay: i * 90, easing: EASE, fill: 'backwards' });
      });
    } else el.animate(KF[kind] || KF.u, { duration: kind === 't' ? (full ? 1300 : 700) : dur, easing: EASE, fill: 'backwards' });
    el.classList.remove('pre');
  }
  if (anim && 'IntersectionObserver' in W) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); play(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    qa('[data-r]').forEach(function (el) {
      if (el.getBoundingClientRect().top > vh * 0.92) { el.classList.add('pre'); io.observe(el); }
    });
  }

  /* ---------- count-up ---------- */
  function fmt(n, sep) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, sep); }
  function count(el) {
    var to = +el.getAttribute('data-count'), suf = el.getAttribute('data-suf') || '', sep = el.getAttribute('data-sep') || ',';
    if (!anim) { el.textContent = fmt(to, sep) + suf; return; }
    var t0 = performance.now(), D = 1600;
    (function f(t) { var p = Math.min(1, (t - t0) / D); p = 1 - Math.pow(1 - p, 4); el.textContent = fmt(Math.round(to * p), sep) + suf; if (p < 1) requestAnimationFrame(f); })(t0);
  }
  var cio = 'IntersectionObserver' in W ? new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { cio.unobserve(e.target); count(e.target); } }); }) : null;
  qa('[data-count]').forEach(function (el) { cio ? cio.observe(el) : count(el); });

  /* ---------- scroll-linked: flips, parallax, ring tilt, progress (one loop) ---------- */
  var flips = anim ? qa('[data-flip]').map(function (el, i) { return { el: el, ax: el.getAttribute('data-flip'), s: i % 2 ? 1 : -1 }; }) : [];
  var pars = full ? qa('[data-par]').map(function (el) { return { el: el, f: +el.getAttribute('data-par') }; }) : [];
  flips.forEach(function (f) { if (f.el.getBoundingClientRect().top < vh * 0.9) f.done = true; });
  var dirty = true, lastY = -1;
  addEventListener('scroll', function () { dirty = true; }, { passive: true });
  addEventListener('resize', function () { vh = innerHeight; dirty = true; });
  var ticks = [];
  function loop(t) {
    var y = scrollY;
    if (dirty || y !== lastY) {
      dirty = false; lastY = y;
      var max = d.documentElement.scrollHeight - vh;
      if (prog) prog.style.transform = 'scaleX(' + (max > 0 ? y / max : 0).toFixed(4) + ')';
      for (var i = 0; i < flips.length; i++) {
        var f = flips[i]; if (f.done) continue;
        var r = f.el.getBoundingClientRect();
        if (r.top > vh * 1.1 || r.bottom < -50) continue;
        var p = Math.min(1, Math.max(0, (vh - r.top) / (vh * 0.42)));
        var a = (1 - p);
        if (f.ax === 'x') f.el.style.setProperty('--fx', (a * 70).toFixed(2) + 'deg');
        else f.el.style.setProperty('--fy', (a * 64 * f.s).toFixed(2) + 'deg');
        f.el.style.setProperty('--fo', (0.15 + 0.85 * p).toFixed(3));
        if (p >= 1) { f.done = true; f.el.style.removeProperty('--fx'); f.el.style.removeProperty('--fy'); f.el.style.removeProperty('--fo'); }
      }
      for (var j = 0; j < pars.length; j++) {
        var pe = pars[j], rr = pe.el.getBoundingClientRect();
        if (rr.bottom < -200 || rr.top > vh + 200) continue;
        var off = (rr.top + rr.height / 2 - vh / 2) * pe.f;
        pe.el.style.transform = pe.el.hasAttribute('data-scale') ? 'translate3d(0,' + off.toFixed(1) + 'px,0) scale(1.08)' : 'translate3d(0,' + off.toFixed(1) + 'px,0)';
      }
    }
    for (var k = 0; k < ticks.length; k++) ticks[k](t);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  /* ---------- hover tilt + glare (pointer devices only) ---------- */
  if (!touch && anim) {
    qa('.card,.rec').forEach(function (c) {
      var g = d.createElement('i'); g.className = 'glare'; c.appendChild(g);
      c.addEventListener('pointermove', function (e) {
        var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        c.classList.add('live');
        c.style.setProperty('--ty', ((x - .5) * 14).toFixed(2) + 'deg');
        c.style.setProperty('--tx', ((.5 - y) * 14).toFixed(2) + 'deg');
        c.style.setProperty('--gx', (x * 100).toFixed(1) + '%'); c.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
      });
      c.addEventListener('pointerleave', function () { c.classList.remove('live'); c.style.setProperty('--tx', '0deg'); c.style.setProperty('--ty', '0deg'); });
    });
  }

  /* ---------- catalog ring (CSS 3D, drag with inertia) ---------- */
  var stage = q('.stage'), ring = q('.ring');
  if (stage && ring) {
    var items = qa('a', ring), N = items.length, step = 360 / N;
    var R = 0, ang = 0, vel = 0, drag = false, lx = 0, moved = 0, visible = false, tilt = -8;
    function layout() {
      var w = items[0].offsetWidth; R = Math.round((w / 2) / Math.tan(Math.PI / N)) + (innerWidth < 720 ? 40 : 80);
      items.forEach(function (it, i) { it.style.transform = 'rotateY(' + (i * step) + 'deg) translateZ(' + R + 'px)'; });
    }
    layout(); addEventListener('resize', layout);
    function render() {
      ring.style.transform = 'translateZ(' + (-R) + 'px) rotateX(' + tilt.toFixed(2) + 'deg) rotateY(' + ang.toFixed(2) + 'deg)';
      for (var i = 0; i < N; i++) {
        var a = ((i * step + ang) % 360 + 360) % 360; if (a > 180) a -= 360;
        var c = Math.cos(a * Math.PI / 180);
        items[i].style.opacity = (0.12 + 0.88 * Math.max(0, c)).toFixed(3);
      }
    }
    render();
    stage.addEventListener('pointerdown', function (e) { drag = true; moved = 0; lx = e.clientX; vel = 0; stage.setPointerCapture(e.pointerId); });
    stage.addEventListener('pointermove', function (e) { if (!drag) return; var dx = e.clientX - lx; lx = e.clientX; moved += Math.abs(dx); vel = dx * 0.18; ang += vel; });
    function end() { drag = false; }
    stage.addEventListener('pointerup', end); stage.addEventListener('pointercancel', end);
    stage.addEventListener('click', function (e) { if (moved > 6) { e.preventDefault(); e.stopPropagation(); } }, true);
    stage.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') { ang += step; render(); } if (e.key === 'ArrowRight') { ang -= step; render(); } });
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(stage);
    ticks.push(function () {
      if (!visible) return;
      if (!drag) { vel *= 0.95; if (anim) ang += (Math.abs(vel) > 0.02 ? vel : 0) + (full ? -0.07 : -0.03); }
      var r = stage.getBoundingClientRect(); var p = (r.top + r.height / 2 - vh / 2) / vh;
      tilt = -8 + p * 14;
      render();
    });
  }

  /* ---------- 8 layers ---------- */
  var stack = q('.lay-stack');
  if (stack) {
    var layers = qa('i', stack), rows = qa('.lay-list li'), boom = false, layVis = false;
    function hl(i) {
      layers.forEach(function (l, k) { l.classList.toggle('hl', k === i); });
      rows.forEach(function (r, k) { r.classList.toggle('on', k === i); });
      stack.classList.toggle('dim', i >= 0);
    }
    rows.forEach(function (r, i) { r.addEventListener('pointerenter', function () { boom = true; hl(i); }); r.addEventListener('pointerleave', function () { boom = false; hl(-1); }); });
    var st = q('.lay-st');
    st.addEventListener('pointerenter', function () { boom = true; }); st.addEventListener('pointerleave', function () { boom = false; });
    st.addEventListener('click', function () { boom = !boom; });
    new IntersectionObserver(function (es) { layVis = es[0].isIntersecting; }).observe(st);
    var gapNow = 4;
    ticks.push(function () {
      if (!layVis) return;
      var r = st.getBoundingClientRect(); var p = Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height)));
      var target = boom ? 40 : 4 + Math.sin(p * Math.PI) * 24;
      if (!anim) target = 22;
      gapNow += (target - gapNow) * 0.08;
      stack.style.setProperty('--gap', gapNow.toFixed(2) + 'px');
    });
    var ba = q('.ba');
    if (ba) q('input', ba).addEventListener('input', function () { ba.style.setProperty('--ba', this.value + '%'); });
  }

  /* ---------- YouTube (load on click) ---------- */
  qa('.vid[data-yt]').forEach(function (v) {
    function go(e) { if (e) e.preventDefault(); if (q('iframe', v)) return; var f = d.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + v.getAttribute('data-yt') + '?autoplay=1&rel=0'; f.title = v.getAttribute('aria-label') || 'Video';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'; f.allowFullscreen = true; v.appendChild(f); }
    v.addEventListener('click', go); v.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') go(e); });
  });

  /* ---------- FAQ (Lucian #044) ---------- */
  qa('.u044').forEach(function (root) {
    var its = qa('.u044-it', root), qs = its.map(function (it) { return q('.u044-q', it); });
    var uid = 'u044-' + Math.random().toString(36).slice(2, 7);
    its.forEach(function (it, i) { var b = q('.u044-body', it); qs[i].id = uid + '-q' + i; b.id = uid + '-a' + i; qs[i].setAttribute('aria-controls', b.id); b.setAttribute('aria-labelledby', qs[i].id); });
    function set(it, open) { it.classList.toggle('open', open); q('.u044-q', it).setAttribute('aria-expanded', String(open)); var a = q('.u044-a a', it); if (a) a.tabIndex = open ? 0 : -1; }
    its.forEach(function (it, i) {
      set(it, it.classList.contains('open'));
      qs[i].addEventListener('click', function () { var w = !it.classList.contains('open'); its.forEach(function (o) { if (o !== it) set(o, false); }); set(it, w); });
      qs[i].addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowDown' ? i + 1 : e.key === 'ArrowUp' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? qs.length - 1 : -2;
        if (n === -2) return; e.preventDefault(); qs[(n + qs.length) % qs.length].focus();
      });
    });
  });

  /* ---------- Inquiry wizard (Lucian #042 → real Web3Forms form) ---------- */
  var wz = q('.u042');
  if (wz) {
    var form = wz.closest('form'), sts = qa('.u042-st', wz), panes = qa('.u042-pane', wz), line = q('.u042-line i', wz);
    var prev = q('.u042-prev', wz), next = q('.u042-next', wz), status = q('.fstat', form), cur = -1, last = panes.length - 1, sending = false;
    function valid(i) {
      var ok = true;
      qa('input,select,textarea', panes[i]).forEach(function (f) {
        var wrap = f.closest('.fld'); if (!wrap) return;
        var good = f.checkValidity(); wrap.classList.toggle('bad', !good);
        if (!good && ok) { ok = false; f.focus(); }
      });
      if (!ok && status) { status.className = 'fstat err'; status.textContent = STR.fix || 'Please check the highlighted field.'; }
      else if (status && status.classList.contains('err')) { status.textContent = ''; status.className = 'fstat'; }
      return ok;
    }
    function go(i) {
      if (i < 0 || i > last || i === cur) return;
      var dir = i > cur ? 1 : -1;
      panes.forEach(function (p, k) {
        var on = k === i; p.classList.toggle('on', on); p.setAttribute('aria-hidden', String(!on)); p.inert = !on;
        p.style.opacity = on ? '1' : '0'; p.style.transform = on ? 'none' : 'translateX(' + (k < i ? -40 : 40) + '%)';
        if (on && cur >= 0 && anim) { p.style.transition = 'none'; p.style.transform = 'translateX(' + (dir * 40) + '%)'; p.style.opacity = '0'; void p.offsetWidth; p.style.transition = ''; p.style.transform = 'none'; p.style.opacity = '1'; }
      });
      cur = i;
      sts.forEach(function (s, k) {
        s.classList.toggle('done', k < i); s.classList.toggle('cur', k === i);
        var dt = q('.u042-dot', s); dt.tabIndex = k < i ? 0 : -1;
        if (k === i) dt.setAttribute('aria-current', 'step'); else dt.removeAttribute('aria-current');
      });
      line.parentNode.style.setProperty('--p', (i / last).toFixed(3));
      prev.setAttribute('aria-disabled', String(i === 0));
      next.textContent = i === last ? (STR.send || 'Send message') : (STR.next || 'Next');
    }
    next.addEventListener('click', function () {
      if (!valid(cur)) return;
      if (cur < last) { go(cur + 1); return; }
      if (sending) return;
      sending = true; next.disabled = true; status.className = 'fstat'; status.textContent = STR.sending || 'Sending…';
      var payload = {}; new FormData(form).forEach(function (v, k) {
        if (k === 'access_key' || k === 'botcheck') return;
        payload[k] = v;
      });
      if (payload.subject && !payload._subject) { payload._subject = payload.subject; delete payload.subject; }
      if (!payload._subject) payload._subject = 'Inquiry from qone.kr';
      payload._template = 'table';
      payload._captcha = 'false';
      fetch('https://formsubmit.co/ajax/chl@qone.kr', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res && (res.success === true || res.success === 'true')) {
            var thanks = form.getAttribute('data-thanks');
            if (thanks) { location.href = thanks; return; }
            status.className = 'fstat ok'; status.textContent = STR.ok || 'Thank you. Your message has been sent.'; form.reset(); setTimeout(function () { go(0); }, 400);
          }
          else { status.className = 'fstat err'; status.textContent = STR.err || 'Something went wrong. Please email chl@qone.kr directly.'; }
        })
        .catch(function () { status.className = 'fstat err'; status.textContent = STR.err || 'Something went wrong. Please email chl@qone.kr directly.'; })
        .then(function () { sending = false; next.disabled = false; });
    });
    prev.addEventListener('click', function () { go(cur - 1); });
    sts.forEach(function (s, k) { q('.u042-dot', s).addEventListener('click', function () { if (k < cur) go(k); }); });
    form.addEventListener('submit', function (e) { e.preventDefault(); next.click(); });
    qa('input,select,textarea', form).forEach(function (f) { f.addEventListener('input', function () { var w = f.closest('.fld'); if (w && f.checkValidity()) w.classList.remove('bad'); }); });
    // deep links: ?inquiry=samples|quote|oem|partner  ?product=...
    var map = { samples: 1, quote: 2, oem: 3, partner: 4 }, iq = params.get('inquiry'), pr = params.get('product');
    if (iq && map[iq] !== undefined) { var r = qa('input[name="inquiry_type"]', form)[map[iq]]; if (r) r.checked = true; }
    if (pr) { var pf = q('#f-product', form); if (pf) pf.value = pr; }
    go(0);
  }

  /* Dedicated inquiry forms: same FormSubmit destination, prefill the product from ?product= */
  var bqf = q('#bqf');
  if (bqf) {
    var named = params.get('product');
    if (named) {
      var det = q('input[name="product details"]', bqf);
      if (det && !det.value) det.value = named;
    }
  }

  /* ---------- cursor glow (off by default) ---------- */
  if (cfg.cursorGlow && !touch && anim) {
    var gl = d.createElement('div'); gl.className = 'glow'; d.body.appendChild(gl);
    addEventListener('pointermove', function (e) { gl.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0)'; }, { passive: true });
  }

  /* ---------- tweak panel (?tweak) ---------- */
  if (params.has('tweak')) {
    var tp = d.createElement('div'); tp.className = 'tweak';
    tp.innerHTML = '<label>motion <select data-k="motion"><option>full</option><option>subtle</option><option>off</option></select></label>' +
      '<label>heroScene <select data-k="heroScene"><option>globe</option><option>blob</option></select></label>' +
      '<label>cursorGlow <select data-k="cursorGlow"><option value="false">off</option><option value="true">on</option></select></label>';
    d.body.appendChild(tp);
    qa('select', tp).forEach(function (s) { var k = s.getAttribute('data-k'); s.value = String(cfg[k]);
      s.addEventListener('change', function () { var v = s.value; cfg[k] = v === 'true' ? true : v === 'false' ? false : v; try { localStorage.setItem('qone-tweak', JSON.stringify(cfg)); } catch (e) {} location.reload(); }); });
  }

  /* ---------- 3D: text first, WebGL later ---------- */
  function hasGL() {   // real GPU only: software rasterizers (SwiftShader, llvmpipe) make WebGL too slow to be pleasant
    try {
      var c = d.createElement('canvas'), g = W.WebGLRenderingContext && (c.getContext('webgl') || c.getContext('experimental-webgl'));
      if (!g) return false;
      var x = g.getExtension('WEBGL_debug_renderer_info'), r = x ? String(g.getParameter(x.UNMASKED_RENDERER_WEBGL)) : '';
      var lose = g.getExtension('WEBGL_lose_context'); if (lose) lose.loseContext();
      return params.get('gl') === 'force' || !/swiftshader|llvmpipe|software|basic render/i.test(r);
    } catch (e) { return false; }
  }
  function load(src, cb) { var s = d.createElement('script'); s.src = src; s.async = true; s.onload = cb; s.crossOrigin = 'anonymous'; d.head.appendChild(s); }
  function boot() {
    if (!anim || !d.body.getAttribute('data-3d') || !hasGL()) return;
    load('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js', function () { load(d.body.getAttribute('data-3d'), function () {}); });
  }
  function later() { (W.requestIdleCallback || function (f) { setTimeout(f, 200); })(boot, { timeout: 2500 }); }
  if (d.readyState === 'complete') setTimeout(later, 600); else addEventListener('load', function () { setTimeout(later, 600); });
})();
