
(function(){
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches;

  function setBg(el){
    var u = el.getAttribute('data-bg'); if(!u) return;
    var b = u.replace(/\.(jpe?g|png)$/i,'');
    el.style.backgroundImage = 'image-set(url("'+b+'.avif") type("image/avif"), url("'+u+'") type("image/jpeg"))';
    if(!el.style.backgroundImage) el.style.backgroundImage = 'url("'+u+'")';
    el.removeAttribute('data-bg');
  }
  var bgs = document.querySelectorAll('[data-bg]');
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ setBg(e.target); io.unobserve(e.target); } }); },{rootMargin:'400px 0px'});
    bgs.forEach(function(el){ io.observe(el); });
  } else { bgs.forEach(setBg); }

  var hero = document.querySelector('.hero.ja-oil');
  if(hero && fine && !reduce){
    var raf = 0, tx = 0, ty = 0;
    hero.addEventListener('pointermove', function(e){
      var r = hero.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width - .5; ty = (e.clientY - r.top) / r.height - .5;
      if(!raf) raf = requestAnimationFrame(function(){
        raf = 0;
        hero.style.setProperty('--px', (tx * -22).toFixed(1) + 'px');
        hero.style.setProperty('--py', (ty * -14).toFixed(1) + 'px');
        hero.style.setProperty('--gx', (50 + tx * 60).toFixed(0) + '%');
        hero.style.setProperty('--gy', (40 + ty * 50).toFixed(0) + '%');
      });
    }, {passive:true});
    hero.addEventListener('pointerleave', function(){ hero.style.setProperty('--px','0px'); hero.style.setProperty('--py','0px'); });
  }

  if(fine && !reduce){
    document.querySelectorAll('.oil-frame').forEach(function(a){
      var fr = a.querySelector('.fr'); if(!fr) return;
      a.addEventListener('pointermove', function(e){
        var r = a.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        fr.style.setProperty('--ry', (x * 14).toFixed(1) + 'deg');
        fr.style.setProperty('--rx', (y * -10).toFixed(1) + 'deg');
      }, {passive:true});
      a.addEventListener('pointerleave', function(){ fr.style.setProperty('--ry','0deg'); fr.style.setProperty('--rx','0deg'); });
    });
  }

  document.querySelectorAll('.jl-video[data-yt]').forEach(function(v){
    v.addEventListener('click', function(){
      if(v.querySelector('iframe')) return;
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + v.getAttribute('data-yt') + '?autoplay=1&rel=0';
      f.title = v.getAttribute('aria-label') || 'video';
      f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture'; f.allowFullscreen = true;
      v.appendChild(f);
    });
  });
})();
