/* QONE Costco hub: TOC highlight + apply form (FormSubmit multipart, 10MB total limit) */
(function () {
  var d = document;
  // TOC
  var links = [].slice.call(d.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { links.forEach(function (a) { a.classList.remove('on'); }); var a = map[e.target.id]; if (a) a.classList.add('on'); }
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    Object.keys(map).forEach(function (id) { var s = d.getElementById(id); if (s) io.observe(s); });
  }
  // form
  var f = d.getElementById('cxform');
  if (!f) return;
  var MAX = 10 * 1024 * 1024, files = [].slice.call(f.querySelectorAll('input[type=file]')), sum = f.querySelector('.drop .sum'),
      drop = f.querySelector('.drop'), msg = f.querySelector('.subm .msg'), btn = f.querySelector('button[type=submit]');
  function mb(n) { return (n / 1048576).toFixed(n < 1048576 ? 2 : 1) + 'MB'; }
  function total() { var t = 0, c = 0; files.forEach(function (i) { [].forEach.call(i.files || [], function (x) { t += x.size; c++; }); }); return { t: t, c: c }; }
  function upd() {
    var r = total();
    if (!r.c) { sum.textContent = '첨부 파일 없음 · 최대 3개, 합계 10MB까지'; sum.classList.remove('bad'); return true; }
    var ok = r.t <= MAX;
    sum.textContent = '첨부 ' + r.c + '개 · 합계 ' + mb(r.t) + (ok ? ' (10MB 이내)' : ' — 10MB를 넘습니다. 일부 파일을 빼거나 아래 대용량 파일 링크 칸을 이용해 주세요.');
    sum.classList.toggle('bad', !ok);
    return ok;
  }
  files.forEach(function (i) { i.addEventListener('change', upd); });
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function () { drop.classList.add('over'); }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function () { drop.classList.remove('over'); }); });
  upd();
  f.addEventListener('submit', function (e) {
    var bad = null;
    [].forEach.call(f.querySelectorAll('[required]'), function (el) {
      var v = el.type === 'checkbox' ? el.checked : (el.value || '').trim();
      var ok = !!v && (el.type !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim()));
      el.classList.toggle('bad', !ok);
      if (!ok && !bad) bad = el;
    });
    if (bad) { e.preventDefault(); msg.textContent = '표시된 필수 항목을 확인해 주세요.'; bad.focus(); return; }
    if (!upd()) { e.preventDefault(); msg.textContent = '첨부 파일 합계가 10MB를 넘습니다.'; return; }
    var co = (f.querySelector('[data-k=company]').value || '').trim(), pr = (f.querySelector('[data-k=product]').value || '').trim();
    f.querySelector('[name=_subject]').value = '[해외유통 입점 제안] ' + co + ' / ' + pr;
    f.querySelector('[name=_replyto]').value = f.querySelector('[data-k=email]').value.trim();
    msg.textContent = '';
    btn.disabled = true; btn.textContent = '전송 중입니다…';
  });
  window.addEventListener('pageshow', function () { btn.disabled = false; btn.textContent = '입점 제안 보내기'; });
})();
/* lightbox for field photos */
(function () {
  var d = document, box;
  d.addEventListener('click', function (ev) {
    var pic = ev.target.closest && ev.target.closest('.pf picture');
    if (!pic) return;
    var img = pic.querySelector('img'); if (!img) return;
    ev.preventDefault();
    if (!box) {
      box = d.createElement('div'); box.className = 'lbx'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', '사진 크게 보기');
      box.innerHTML = '<button type="button">CLOSE</button><img alt=""><p></p>'; d.body.appendChild(box);
      box.addEventListener('click', function (e2) { if (e2.target.tagName !== 'IMG') box.classList.remove('on'); });
      d.addEventListener('keydown', function (k) { if (k.key === 'Escape') box.classList.remove('on'); });
    }
    var big = box.querySelector('img'); big.src = img.currentSrc || img.src; big.alt = img.alt;
    var cap = pic.parentNode.querySelector('figcaption'); box.querySelector('p').textContent = cap ? cap.textContent : img.alt;
    box.classList.add('on'); box.querySelector('button').focus();
  });
})();
