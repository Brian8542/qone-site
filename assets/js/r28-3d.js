/* QONE v28 — WebGL scenes (three.js r128), light theme. Each scene renders only while on screen. */
(function () {
  if (!window.THREE) return;
  var T = THREE, d = document, cfg = window.QONE_CFG || { motion: 'full', heroScene: 'globe' };
  var touch = matchMedia('(hover: none)').matches, small = innerWidth < 720 || touch;
  var DPR = Math.min(devicePixelRatio || 1, small ? 1.5 : 2), D2R = Math.PI / 180;
  var SPEED = cfg.motion === 'subtle' ? 0.45 : 1;
  var PAL = [new T.Color('#0071E3'), new T.Color('#7A3FF2'), new T.Color('#E8287A'), new T.Color('#E27600')];
  function pal(t) { t = ((t % 1) + 1) % 1 * 3; var i = Math.floor(t), f = t - i; return PAL[i].clone().lerp(PAL[i + 1], f); }
  var mouse = { x: 0, y: 0 };
  addEventListener('pointermove', function (e) { mouse.x = e.clientX / innerWidth * 2 - 1; mouse.y = e.clientY / innerHeight * 2 - 1; }, { passive: true });

  function mk(el, fov, z) {
    var r = new T.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    r.setPixelRatio(DPR); r.setClearColor(0xffffff, 0); el.appendChild(r.domElement);
    var s = new T.Scene(), c = new T.PerspectiveCamera(fov, 1, 0.1, 100); c.position.set(0, 0, z);
    function size() { var w = el.clientWidth, h = el.clientHeight; if (!w || !h) return; r.setSize(w, h, false); c.aspect = w / h; c.updateProjectionMatrix(); }
    size(); addEventListener('resize', size);
    var o = { r: r, s: s, c: c, vis: false, el: el };
    new IntersectionObserver(function (es) { o.vis = es[0].isIntersecting; }, { rootMargin: '80px' }).observe(el);
    return o;
  }
  function ll(lat, lon, r) { var p = (90 - lat) * D2R, t = (lon + 180) * D2R; return new T.Vector3(-r * Math.sin(p) * Math.cos(t), r * Math.cos(p), r * Math.sin(p) * Math.sin(t)); }
  function circleTex() {
    var c = d.createElement('canvas'); c.width = c.height = 64; var g = c.getContext('2d');
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.55, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new T.CanvasTexture(c);
  }

  /* ================= GLOBE ================= */
  function globe(el) {
    var o = mk(el, 32, 5.4), s = o.s, c = o.c;
    var root = new T.Group(); root.rotation.x = 0.38; root.rotation.z = -0.08; s.add(root);
    var spin = new T.Group(); root.add(spin);
    var home = ll(37.3, 127.6, 1); spin.rotation.y = -Math.atan2(home.x, home.z) - 0.35;

    // pearl body + rim light
    spin.add(new T.Mesh(new T.SphereGeometry(0.985, 64, 64), new T.ShaderMaterial({
      transparent: true,
      vertexShader: 'varying vec3 vN;varying vec3 vV;void main(){vec4 mv=modelViewMatrix*vec4(position,1.);vN=normalize(normalMatrix*normal);vV=normalize(-mv.xyz);gl_Position=projectionMatrix*mv;}',
      fragmentShader: 'varying vec3 vN;varying vec3 vV;void main(){float f=pow(1.-max(dot(vN,vV),0.),2.2);vec3 col=mix(vec3(.985,.985,.992),vec3(.86,.89,.96),f);gl_FragColor=vec4(col,.92);}'
    })));
    var atm = new T.Mesh(new T.SphereGeometry(1.16, 64, 64), new T.ShaderMaterial({
      transparent: true, side: T.BackSide, depthWrite: false,
      vertexShader: 'varying vec3 vN;varying vec3 vV;void main(){vec4 mv=modelViewMatrix*vec4(position,1.);vN=normalize(normalMatrix*normal);vV=normalize(-mv.xyz);gl_Position=projectionMatrix*mv;}',
      fragmentShader: 'varying vec3 vN;varying vec3 vV;void main(){float f=clamp(-dot(vN,vV),0.,1.);gl_FragColor=vec4(.0,.44,.89,pow(f,2.4)*.42);}'
    })); root.add(atm);

    // land dots
    var dots = new T.Points(new T.BufferGeometry(), new T.ShaderMaterial({
      transparent: true, depthWrite: false,
      uniforms: { uT: { value: 0 }, uPix: { value: DPR }, uC: { value: new T.Color('#2C2C30') } },
      vertexShader: 'attribute float aD;attribute float aP;uniform float uT;uniform float uPix;varying float vA;' +
        'void main(){float t=clamp((uT-aD*2.4)/.9,0.,1.);float tw=.72+.28*sin(uT*2.+aP*6.2831);' +
        'vec4 wp=modelMatrix*vec4(position,1.);vec3 n=normalize((modelMatrix*vec4(position,0.)).xyz);float fc=dot(n,normalize(cameraPosition-wp.xyz));' +
        'vA=t*tw*smoothstep(-.05,.38,fc);vec4 mv=viewMatrix*wp;gl_PointSize=(1.9+1.4*(1.-t))*uPix*(5.4/-mv.z);gl_Position=projectionMatrix*mv;}',
      fragmentShader: 'uniform vec3 uC;varying float vA;void main(){float r=length(gl_PointCoord-.5);if(r>.5)discard;gl_FragColor=vec4(uC,vA*.78*smoothstep(.5,.25,r));}'
    }));
    spin.add(dots);
    fetch(el.getAttribute('data-dots')).then(function (r) { return r.json(); }).then(function (a) {
      var n = a.length / 2, P = new Float32Array(n * 3), AD = new Float32Array(n), AP = new Float32Array(n);
      for (var i = 0; i < n; i++) { var v = ll(a[i * 2], a[i * 2 + 1], 1.0); P[i * 3] = v.x; P[i * 3 + 1] = v.y; P[i * 3 + 2] = v.z; AD[i] = Math.random(); AP[i] = Math.random(); }
      dots.geometry.setAttribute('position', new T.BufferAttribute(P, 3));
      dots.geometry.setAttribute('aD', new T.BufferAttribute(AD, 1)); dots.geometry.setAttribute('aP', new T.BufferAttribute(AP, 1));
      dots.material.uniforms.uT.value = 0; t0 = performance.now();
    });

    // routes from Yeoju
    var cities = JSON.parse(el.getAttribute('data-cities') || '[]');
    var tex = circleTex(), routes = [];
    var origin = new T.Mesh(new T.SphereGeometry(0.018, 16, 16), new T.MeshBasicMaterial({ color: 0x1D1D1F })); origin.position.copy(ll(37.3, 127.6, 1.002)); spin.add(origin);
    function ringAt(pos, color) {
      var m = new T.Mesh(new T.RingGeometry(0.014, 0.02, 40), new T.MeshBasicMaterial({ color: color, transparent: true, side: T.DoubleSide, depthWrite: false }));
      m.position.copy(pos.clone().multiplyScalar(1.004)); m.lookAt(pos.clone().multiplyScalar(2)); spin.add(m); return m;
    }
    var homeRing = ringAt(ll(37.3, 127.6, 1), 0x1D1D1F);
    cities.forEach(function (ct, i) {
      var a = ll(37.3, 127.6, 1.0), b = ll(ct[0], ct[1], 1.0), dist = a.distanceTo(b);
      var mid = a.clone().add(b).normalize().multiplyScalar(1 + dist * 0.42);
      var curve = new T.QuadraticBezierCurve3(a, mid, b), N = 80, pts = curve.getPoints(N);
      var pos = new Float32Array((N + 1) * 3), col = new Float32Array((N + 1) * 3);
      pts.forEach(function (p, k) { pos[k * 3] = p.x; pos[k * 3 + 1] = p.y; pos[k * 3 + 2] = p.z; var cc = pal(k / N * 0.9 + i * 0.11); col[k * 3] = cc.r; col[k * 3 + 1] = cc.g; col[k * 3 + 2] = cc.b; });
      var g = new T.BufferGeometry(); g.setAttribute('position', new T.BufferAttribute(pos, 3)); g.setAttribute('color', new T.BufferAttribute(col, 3)); g.setDrawRange(0, 0);
      var line = new T.Line(g, new T.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.9, depthWrite: false })); spin.add(line);
      var head = new T.Sprite(new T.SpriteMaterial({ map: tex, color: pal(i * 0.11 + 0.9), transparent: true, depthWrite: false })); head.scale.set(0.05, 0.05, 1); head.visible = false; spin.add(head);
      var pin = new T.Mesh(new T.CylinderGeometry(0.003, 0.003, 0.07, 6), new T.MeshBasicMaterial({ color: 0x1D1D1F, transparent: true, opacity: 0 }));
      pin.position.copy(b.clone().multiplyScalar(1.035)); pin.lookAt(b.clone().multiplyScalar(2)); pin.rotateX(Math.PI / 2); spin.add(pin);
      var ring = ringAt(b, pal(i * 0.11 + 0.9)); ring.material.opacity = 0;
      routes.push({ curve: curve, line: line, g: g, head: head, pin: pin, ring: ring, N: N, delay: 1.6 + i * 0.55, len: 1.5 + dist * 0.35 });
    });

    // tilted orbits + satellites
    var orbits = [];
    [[1.38, 0.5, 0.2], [1.55, -0.35, 1.1], [1.72, 0.15, -0.6]].forEach(function (cfgO, i) {
      var e = new T.EllipseCurve(0, 0, cfgO[0], cfgO[0], 0, Math.PI * 2), p = e.getPoints(160).map(function (v) { return new T.Vector3(v.x, 0, v.y); });
      var g = new T.BufferGeometry().setFromPoints(p);
      var grp = new T.Group(); grp.rotation.set(cfgO[1], 0, cfgO[2]); root.add(grp);
      grp.add(new T.LineLoop(g, new T.LineBasicMaterial({ color: 0x1D1D1F, transparent: true, opacity: 0.1 })));
      var sat = new T.Sprite(new T.SpriteMaterial({ map: tex, color: PAL[i], transparent: true, depthWrite: false })); sat.scale.set(0.045, 0.045, 1); grp.add(sat);
      orbits.push({ r: cfgO[0], sat: sat, sp: 0.25 + i * 0.09, ph: i * 2 });
    });

    // far stars
    var SN = 500, SP = new Float32Array(SN * 3);
    for (var i = 0; i < SN; i++) { var v = new T.Vector3().randomDirection ? new T.Vector3().randomDirection() : new T.Vector3(Math.random() - .5, Math.random() - .5, Math.random() - .5).normalize(); v.multiplyScalar(6 + Math.random() * 6); SP[i * 3] = v.x; SP[i * 3 + 1] = v.y; SP[i * 3 + 2] = v.z; }
    var sg = new T.BufferGeometry(); sg.setAttribute('position', new T.BufferAttribute(SP, 3));
    s.add(new T.Points(sg, new T.PointsMaterial({ color: 0x86868B, size: 0.035, transparent: true, opacity: 0.45, depthWrite: false })));

    var t0 = performance.now(), cx = 0, cy = 0;
    function frame(now) {
      requestAnimationFrame(frame);
      if (!o.vis) return;
      var t = (now - t0) / 1000;
      dots.material.uniforms.uT.value = t;
      spin.rotation.y += 0.0009 * SPEED;
      var sc = Math.min(1, scrollY / innerHeight);
      cx += (mouse.x * 0.35 - cx) * 0.04; cy += (-mouse.y * 0.25 - cy) * 0.04;
      c.position.set(cx, cy, 5.4 + sc * 2.6); c.lookAt(0, 0, 0);
      el.style.opacity = String(Math.max(0, 1 - sc * 1.15));
      var hp = (t * 0.8) % 1; homeRing.scale.setScalar(1 + hp * 3.5); homeRing.material.opacity = (1 - hp) * 0.7;
      routes.forEach(function (r) {
        var cyc = r.len + 2.6, lt = t - r.delay; if (lt < 0) return;
        var k = lt % cyc, p = Math.min(1, k / r.len), e = 1 - Math.pow(1 - p, 3);
        var fade = k > r.len + 1.8 ? 1 - (k - r.len - 1.8) / 0.8 : 1;
        r.g.setDrawRange(0, Math.floor(e * r.N) + 1); r.line.material.opacity = 0.9 * fade;
        r.head.visible = p < 1; if (p < 1) r.head.position.copy(r.curve.getPoint(e));
        var a = p >= 1 ? Math.min(1, (k - r.len) / 1.2) : 0;
        r.pin.material.opacity = p >= 1 ? 0.8 * fade : 0;
        r.ring.scale.setScalar(1 + a * 4); r.ring.material.opacity = p >= 1 ? (1 - a) * 0.9 : 0;
      });
      orbits.forEach(function (ob) { var a = t * ob.sp * SPEED + ob.ph; ob.sat.position.set(Math.cos(a) * ob.r, 0, Math.sin(a) * ob.r); });
      o.r.render(s, c);
    }
    requestAnimationFrame(frame);
  }

  /* ================= IRIDESCENT BLOB ================= */
  var NOISE = 'vec3 m289(vec3 x){return x-floor(x*(1./289.))*289.;}vec4 m289(vec4 x){return x-floor(x*(1./289.))*289.;}vec4 pm(vec4 x){return m289(((x*34.)+1.)*x);}vec4 ti(vec4 r){return 1.79284291400159-.85373472095314*r;}' +
    'float sn(vec3 v){const vec2 C=vec2(1./6.,1./3.);const vec4 D=vec4(0.,.5,1.,2.);vec3 i=floor(v+dot(v,C.yyy));vec3 x0=v-i+dot(i,C.xxx);vec3 g=step(x0.yzx,x0.xyz);vec3 l=1.-g;vec3 i1=min(g.xyz,l.zxy);vec3 i2=max(g.xyz,l.zxy);' +
    'vec3 x1=x0-i1+C.xxx;vec3 x2=x0-i2+C.yyy;vec3 x3=x0-D.yyy;i=m289(i);vec4 p=pm(pm(pm(i.z+vec4(0.,i1.z,i2.z,1.))+i.y+vec4(0.,i1.y,i2.y,1.))+i.x+vec4(0.,i1.x,i2.x,1.));' +
    'float n_=.142857142857;vec3 ns=n_*D.wyz-D.xzx;vec4 j=p-49.*floor(p*ns.z*ns.z);vec4 x_=floor(j*ns.z);vec4 y_=floor(j-7.*x_);vec4 x=x_*ns.x+ns.yyyy;vec4 y=y_*ns.x+ns.yyyy;vec4 h=1.-abs(x)-abs(y);' +
    'vec4 b0=vec4(x.xy,y.xy);vec4 b1=vec4(x.zw,y.zw);vec4 s0=floor(b0)*2.+1.;vec4 s1=floor(b1)*2.+1.;vec4 sh=-step(h,vec4(0.));vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy;vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;' +
    'vec3 p0=vec3(a0.xy,h.x);vec3 p1=vec3(a0.zw,h.y);vec3 p2=vec3(a1.xy,h.z);vec3 p3=vec3(a1.zw,h.w);vec4 nr=ti(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));p0*=nr.x;p1*=nr.y;p2*=nr.z;p3*=nr.w;' +
    'vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.);m=m*m;return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));}';
  function blob(el) {
    var o = mk(el, 34, 6.2), s = o.s, c = o.c, grp = new T.Group(); s.add(grp);
    var mat = new T.ShaderMaterial({
      uniforms: { uT: { value: 0 } },
      vertexShader: 'uniform float uT;varying vec3 vN;varying vec3 vV;varying vec3 vP;' + NOISE +
        'float dsp(vec3 p){return .15*sn(p*1.1+uT*.2)+.03*sn(p*2.6-uT*.3);}' +
        'void main(){vec3 p=position;vec3 n=normalize(normal);vec3 tg=normalize(cross(n,vec3(0.,1.,.01)));vec3 bt=normalize(cross(n,tg));float e=.01;' +
        'vec3 p0=p+n*dsp(p);vec3 p1=(p+tg*e);p1+=normalize(p1)*dsp(p1);vec3 p2=(p+bt*e);p2+=normalize(p2)*dsp(p2);vec3 nn=normalize(cross(p1-p0,p2-p0));if(dot(nn,n)<0.)nn=-nn;' +
        'vec4 mv=modelViewMatrix*vec4(p0,1.);vN=normalize(normalMatrix*nn);vV=normalize(-mv.xyz);vP=p0;gl_Position=projectionMatrix*mv;}',
      fragmentShader: 'uniform float uT;varying vec3 vN;varying vec3 vV;varying vec3 vP;' +
        'vec3 pal(float t){t=fract(t)*3.;vec3 a=vec3(0.,.443,.89),b=vec3(.478,.247,.949),c=vec3(.91,.157,.478),d=vec3(.886,.463,0.);return t<1.?mix(a,b,t):t<2.?mix(b,c,t-1.):mix(c,d,t-2.);}' +
        'void main(){float f=pow(1.-max(dot(vN,vV),0.),2.);float k=dot(vN,vec3(.35,.7,.2))*.5+.5;vec3 ir=pal(k*.8+f*.6+uT*.04+vP.y*.15);' +
        'vec3 base=vec3(.955,.952,.972);vec3 col=mix(base,ir,.08+.5*f);float sp=pow(max(dot(reflect(-vV,vN),normalize(vec3(.3,.8,.6))),0.),24.);col+=sp*.35;gl_FragColor=vec4(col,1.);}'
    });
    var seg = small ? 96 : 140;
    grp.add(new T.Mesh(new T.SphereGeometry(1, seg, seg), mat));
    var wire = new T.LineSegments(new T.EdgesGeometry(new T.IcosahedronGeometry(1.62, 1)), new T.LineBasicMaterial({ color: 0x1D1D1F, transparent: true, opacity: 0.14 })); grp.add(wire);
    var RN = 1800, RP = new Float32Array(RN * 3), RC = new Float32Array(RN * 3);
    for (var i = 0; i < RN; i++) { var a = Math.random() * Math.PI * 2, r = 1.85 + Math.pow(Math.random(), 1.6) * 0.6; RP[i * 3] = Math.cos(a) * r; RP[i * 3 + 1] = (Math.random() - .5) * 0.04; RP[i * 3 + 2] = Math.sin(a) * r; var cc = pal(a / (Math.PI * 2)); RC[i * 3] = cc.r; RC[i * 3 + 1] = cc.g; RC[i * 3 + 2] = cc.b; }
    var rg = new T.BufferGeometry(); rg.setAttribute('position', new T.BufferAttribute(RP, 3)); rg.setAttribute('color', new T.BufferAttribute(RC, 3));
    var ringP = new T.Points(rg, new T.PointsMaterial({ size: 0.022, vertexColors: true, transparent: true, opacity: 0.8, depthWrite: false })); ringP.rotation.set(0.42, 0, -0.18); grp.add(ringP);
    var t0 = performance.now(), rx = 0, ry = 0;
    function frame(now) {
      requestAnimationFrame(frame); if (!o.vis) return;
      var t = (now - t0) / 1000 * SPEED; mat.uniforms.uT.value = t;
      rx += (mouse.y * 0.35 - rx) * 0.05; ry += (mouse.x * 0.5 - ry) * 0.05;
      grp.rotation.x = rx; grp.rotation.y = ry + t * 0.08; wire.rotation.y = -t * 0.12; wire.rotation.x = t * 0.05; ringP.rotation.y = t * 0.06;
      o.r.render(s, c);
    }
    requestAnimationFrame(frame);
  }

  /* ================= PARTICLE WAVE ================= */
  function wave(el) {
    var o = mk(el, 40, 1), s = o.s, c = o.c; c.position.set(0, 3.2, 7.5); c.lookAt(0, -0.4, 0);
    var NX = 150, NZ = 70, n = NX * NZ, P = new Float32Array(n * 3), U = new Float32Array(n);
    for (var x = 0; x < NX; x++) for (var z = 0; z < NZ; z++) { var i = x * NZ + z; P[i * 3] = (x / (NX - 1) - .5) * 22; P[i * 3 + 2] = (z / (NZ - 1) - .5) * 9; U[i] = x / (NX - 1); }
    var g = new T.BufferGeometry(); g.setAttribute('position', new T.BufferAttribute(P, 3)); g.setAttribute('aU', new T.BufferAttribute(U, 1));
    var m = new T.ShaderMaterial({
      transparent: true, depthWrite: false,
      uniforms: { uT: { value: 0 }, uM: { value: new T.Vector2(99, 99) }, uPix: { value: DPR } },
      vertexShader: 'uniform float uT;uniform vec2 uM;uniform float uPix;attribute float aU;varying float vU;varying float vH;' +
        'void main(){vec3 p=position;float h=sin(p.x*.45+uT*.9)*.32+sin(p.z*.9+uT*1.2)*.2+sin((p.x+p.z)*.3+uT*.6)*.18;' +
        'float dm=distance(p.xz,uM);h+=exp(-dm*dm*.35)*1.1;p.y=h;vU=aU;vH=h;vec4 mv=modelViewMatrix*vec4(p,1.);gl_PointSize=uPix*(16./-mv.z);gl_Position=projectionMatrix*mv;}',
      fragmentShader: 'varying float vU;varying float vH;' +
        'vec3 pal(float t){t=clamp(t,0.,1.)*2.999;vec3 a=vec3(0.,.443,.89),b=vec3(.478,.247,.949),c=vec3(.91,.157,.478),d=vec3(.886,.463,0.);return t<1.?mix(a,b,t):t<2.?mix(b,c,t-1.):mix(c,d,t-2.);}' +
        'void main(){float r=length(gl_PointCoord-.5);if(r>.5)discard;gl_FragColor=vec4(pal(vU),(.35+.35*smoothstep(-.4,.9,vH))*smoothstep(.5,.2,r));}'
    });
    s.add(new T.Points(g, m));
    var tgt = new T.Vector2(99, 99), cur = new T.Vector2(99, 99), ray = new T.Raycaster(), plane = new T.Plane(new T.Vector3(0, 1, 0), 0), hit = new T.Vector3();
    el.parentNode.addEventListener('pointermove', function (e) {
      var r = el.getBoundingClientRect(); var v = new T.Vector2((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height * 2 - 1));
      ray.setFromCamera(v, c); if (ray.ray.intersectPlane(plane, hit)) tgt.set(hit.x, hit.z);
    });
    el.parentNode.addEventListener('pointerleave', function () { tgt.set(99, 99); });
    var t0 = performance.now();
    function frame(now) {
      requestAnimationFrame(frame); if (!o.vis) return;
      m.uniforms.uT.value = (now - t0) / 1000 * SPEED;
      cur.lerp(tgt, 0.06); m.uniforms.uM.value.copy(cur);
      o.r.render(s, c);
    }
    requestAnimationFrame(frame);
  }

  var hero = d.getElementById('globe');
  if (hero) { if (cfg.heroScene === 'blob') blob(hero); else globe(hero); }
  if (!small) {
    var b = d.getElementById('blob'); if (b) { var fb = b.querySelector('.fallback'); if (fb) fb.remove(); blob(b); }
    var w = d.getElementById('wave'); if (w) wave(w);
  }
})();
