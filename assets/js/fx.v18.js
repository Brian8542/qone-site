/* QONE fx.js — site-wide visual effects */
(function(){
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 2. count-up numbers (.stat .num, .fx-card .n) ---------- */
  function countUp(el){
    var m = /^([\d.,]+)(.*)$/.exec(el.textContent.trim());
    if(!m) return;
    var target = parseFloat(m[1].replace(/,/g,'')), suffix = m[2] || '';
    if(isNaN(target)) return;
    var hasComma = m[1].indexOf(',') > -1, t0 = null, DUR = 1400;
    el.classList.add('fx-count');
    function fmt(n){ n = Math.round(n); return hasComma ? n.toLocaleString('en-US') : String(n); }
    function tick(ts){
      if(!t0) t0 = ts;
      var p = Math.min((ts - t0)/DUR, 1), e = 1 - Math.pow(1-p, 3);
      el.textContent = fmt(target*e) + suffix;
      if(p < 1) requestAnimationFrame(tick);
    }
    if(reduce){ el.textContent = fmt(target)+suffix; return; }
    requestAnimationFrame(tick);
  }
  var nums = document.querySelectorAll('.stat .num, .fx-card .n');
  if(nums.length && 'IntersectionObserver' in window){
    var seen = new WeakSet();
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(e.isIntersecting && !seen.has(e.target)){ seen.add(e.target); countUp(e.target); io.unobserve(e.target); }
      });
    }, {threshold:.4});
    nums.forEach(function(n){ io.observe(n); });
  }

  /* ---------- 5. logo marquee ---------- */
  document.querySelectorAll('.logo-strip').forEach(function(strip){
    var imgs = [].slice.call(strip.querySelectorAll('img'));
    if(imgs.length < 4) return;
    var track = document.createElement('div'); track.className = 'fx-track';
    imgs.forEach(function(i){ track.appendChild(i); });
    imgs.forEach(function(i){ var c = i.cloneNode(true); c.setAttribute('aria-hidden','true'); track.appendChild(c); });
    strip.innerHTML = ''; strip.appendChild(track); strip.classList.add('fx-marquee');
  });

  /* ---------- 9. stagger reveals ---------- */
  document.querySelectorAll('.reveal').forEach(function(el){
    var sibs = el.parentElement ? [].slice.call(el.parentElement.children).filter(function(c){return c.classList.contains('reveal');}) : [];
    var idx = sibs.indexOf(el);
    if(idx > 0) el.style.transitionDelay = Math.min(idx*90, 450) + 'ms';
  });

  /* ---------- 9. button ripple ---------- */
  document.addEventListener('click', function(ev){
    var b = ev.target.closest && ev.target.closest('.btn');
    if(!b || reduce) return;
    var r = b.getBoundingClientRect(), d = Math.max(r.width, r.height);
    var s = document.createElement('span'); s.className = 'fx-ripple';
    s.style.width = s.style.height = d+'px';
    s.style.left = (ev.clientX - r.left - d/2)+'px';
    s.style.top  = (ev.clientY - r.top  - d/2)+'px';
    b.appendChild(s); setTimeout(function(){ s.remove(); }, 650);
  });

  /* ---------- 4. factory process steps ---------- */
  var steps = document.querySelectorAll('.step-row .step');
  if(steps.length && 'IntersectionObserver' in window){
    var io2 = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!e.isIntersecting) return;
        var row = e.target, kids = row.querySelectorAll('.step');
        kids.forEach(function(st,i){ setTimeout(function(){ st.classList.add('lit'); }, reduce ? 0 : i*280); });
        io2.unobserve(row);
      });
    }, {threshold:.25});
    document.querySelectorAll('.step-row').forEach(function(r){ io2.observe(r); });
  }

  /* ---------- 1. hero ambience: floating foam-cell particles ---------- */
  var hero = document.querySelector('section.hero');
  if(hero && !reduce && !hero.classList.contains('ja-oil')){
    hero.classList.add('fx-hero');
    var cv = document.createElement('canvas'); cv.id = 'fxHeroFx'; hero.prepend(cv);
    var ctx = cv.getContext('2d'), P = [], mx = .5, my = .5, W, H;
    function size(){ W = cv.width = hero.offsetWidth; H = cv.height = hero.offsetHeight; }
    size(); addEventListener('resize', size);
    for(var i=0;i<26;i++) P.push({
      x:Math.random(), y:Math.random(), r:8+Math.random()*30,
      vx:(Math.random()-.5)*.00035, vy:-.00018-Math.random()*.00035, o:.05+Math.random()*.09, ph:Math.random()*6.28
    });
    hero.addEventListener('pointermove', function(e){
      var r = hero.getBoundingClientRect();
      mx = (e.clientX-r.left)/r.width; my = (e.clientY-r.top)/r.height;
    });
    (function draw(t){
      ctx.clearRect(0,0,W,H);
      P.forEach(function(p){
        p.x += p.vx + (mx-.5)*.0006; p.y += p.vy;
        if(p.y < -0.08){ p.y = 1.08; p.x = Math.random(); }
        if(p.x < -0.08) p.x = 1.08; if(p.x > 1.08) p.x = -0.08;
        var wob = Math.sin(t/1400 + p.ph)*4;
        var g = ctx.createRadialGradient(p.x*W+wob, p.y*H, 0, p.x*W+wob, p.y*H, p.r);
        g.addColorStop(0, 'rgba(120,200,255,'+p.o+')');
        g.addColorStop(.7,'rgba(120,200,255,'+(p.o*.35)+')');
        g.addColorStop(1, 'rgba(120,200,255,0)');
        ctx.fillStyle = g; ctx.beginPath();
        ctx.arc(p.x*W+wob, p.y*H, p.r, 0, 6.283); ctx.fill();
      });
      requestAnimationFrame(draw);
    })(0);
  }
})();
