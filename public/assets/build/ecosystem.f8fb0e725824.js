(() => {
  'use strict';
  const root = document.querySelector('.ecosystem-experience');
  if (!root) return;
  const data = JSON.parse(document.getElementById('ecosystem-data').textContent);
  const board = root.querySelector('.eco-map');
  const canvas = root.querySelector('.eco-canvas');
  const ctx = canvas.getContext('2d');
  const nodeButtons = [...root.querySelectorAll('[data-eco-node]')];
  const layerButtons = [...root.querySelectorAll('[data-eco-layer]')];
  const previews = [...root.querySelectorAll('[data-eco-preview]')];
  const detail = root.querySelector('.eco-detail-copy');
  const center = root.querySelector('.eco-center');
  const tourButton = root.querySelector('.eco-tour');
  const motionButton = root.querySelector('.eco-motion');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const initial = {
    category: detail.querySelector('.eco-detail-category').textContent,
    title: detail.querySelector('.eco-detail-title').textContent,
    description: detail.querySelector('.eco-detail-description').textContent,
    href: '/products/', link: 'Explore all products'
  };
  let selected = null, hovered = null, layer = 'all';
  let motion = !reduceMotion.matches, touring = false, tourTimer = null, tourIndex = -1;
  let width = 1, height = 1, dpr = 1, inView = false, frame = 0, lastPaint = 0, phase = 0;
  let yaw = 0, pitch = 0, pointerX = 0, pointerY = 0, drag = null, positions = [];
  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
  const mobilePositions = [[.24,.18,-20],[.76,.18,10],[.23,.64,40],[.77,.64,35],[.5,.89,0]];
  const stars = Array.from({length:65}, (_,i) => ({
    x: ((i * 73 + 19) % 997) / 997,
    y: ((i * 127 + 47) % 991) / 991,
    r: i % 8 === 0 ? 1.1 : .55,
    a: .1 + (i % 5) * .045
  }));
  function stopTour() {
    if (tourTimer) clearInterval(tourTimer);
    tourTimer = null;
    touring = false;
    tourButton.textContent = 'Play tour';
    tourButton.setAttribute('aria-pressed','false');
  }
  function select(key, announce = true) {
    selected = key;
    const node = data.find(n => n.key === key);
    nodeButtons.forEach(b => {
      const active = b.dataset.ecoNode === key;
      b.classList.toggle('is-selected', active);
      b.setAttribute('aria-pressed', String(active));
    });
    if (announce) {
      detail.querySelector('.eco-detail-category').textContent = node ? node.category : initial.category;
      detail.querySelector('.eco-detail-title').textContent = node ? node.name : initial.title;
      detail.querySelector('.eco-detail-description').textContent = node ? node.summary : initial.description;
      const status = detail.querySelector('.eco-detail-status');
      status.hidden = !node?.status;
      status.textContent = node?.status || '';
      const link = detail.querySelector('.eco-detail-link');
      link.href = node ? node.href : initial.href;
      link.textContent = node ? node.link : initial.link;
      detail.querySelector('.eco-model-links').hidden = key !== 'realhand';
      previews.forEach(p => { p.hidden = p.dataset.ecoPreview !== (key || 'all'); });
    }
    draw();
  }
  function setLayer(value) {
    layer = value;
    layerButtons.forEach(b => {
      const active = b.dataset.ecoLayer === value;
      b.classList.toggle('is-active',active);
      b.setAttribute('aria-pressed',String(active));
    });
    nodeButtons.forEach(b => b.classList.toggle('is-muted',value !== 'all' && b.dataset.layer !== value));
    center.style.opacity = value === 'all' ? '1' : '.6';
    const first = data.find(n => n.layer === value);
    select(first ? first.key : null);
  }
  layerButtons.forEach(button => button.addEventListener('click', () => {
    stopTour(); setLayer(button.dataset.ecoLayer);
  }));
  nodeButtons.forEach(button => {
    button.addEventListener('click', () => {
      stopTour();
      if (layer !== 'all' && button.dataset.layer !== layer) setLayer('all');
      select(button.dataset.ecoNode);
    });
    button.addEventListener('pointerenter', () => { hovered = button.dataset.ecoNode; draw(); });
    button.addEventListener('pointerleave', () => { hovered = null; draw(); });
    button.addEventListener('focus', () => { hovered = button.dataset.ecoNode; draw(); });
    button.addEventListener('blur', () => { hovered = null; draw(); });
    button.addEventListener('keydown', event => {
      if (!['ArrowRight','ArrowDown','ArrowLeft','ArrowUp'].includes(event.key)) return;
      event.preventDefault(); stopTour();
      const next = (nodeButtons.indexOf(button) + (['ArrowRight','ArrowDown'].includes(event.key) ? 1 : -1) + nodeButtons.length) % nodeButtons.length;
      const target = nodeButtons[next];
      if (layer !== 'all' && target.dataset.layer !== layer) setLayer('all');
      target.focus(); select(target.dataset.ecoNode);
    });
  });
  board.addEventListener('keydown', event => {
    if (event.target !== board) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault(); stopTour(); nodeButtons[0].focus(); select(data[0].key);
    }
    if (event.key === 'Escape') { stopTour(); setLayer('all'); }
  });
  tourButton.addEventListener('click', () => {
    if (touring) { stopTour(); return; }
    setLayer('all');
    touring = true;
    tourButton.textContent = 'Pause tour';
    tourButton.setAttribute('aria-pressed','true');
    tourIndex = data.findIndex(n => n.key === selected);
    const advance = () => { tourIndex = (tourIndex + 1) % data.length; select(data[tourIndex].key); };
    advance();
    tourTimer = setInterval(() => { if (inView && !document.hidden) advance(); }, 4600);
  });
  function updateMotion() {
    motionButton.textContent = motion ? 'Pause motion' : 'Resume motion';
    motionButton.setAttribute('aria-pressed',String(motion));
    startFrame();
    if (!motion && frame) { cancelAnimationFrame(frame); frame = 0; draw(); }
  }
  motionButton.addEventListener('click', () => { motion = !motion; updateMotion(); });
  root.querySelector('.eco-reset').addEventListener('click', () => {
    stopTour(); yaw = pitch = pointerX = pointerY = 0; setLayer('all'); draw();
  });
  reduceMotion.addEventListener('change', event => {
    if (event.matches) { motion = false; stopTour(); updateMotion(); }
  });
  board.addEventListener('pointerdown', event => {
    if (event.target.closest('button,a') || (event.pointerType === 'mouse' && event.button !== 0)) return;
    drag = { id:event.pointerId, x:event.clientX, y:event.clientY, yaw, pitch, moved:false };
    if (event.pointerType === 'mouse') board.setPointerCapture(event.pointerId);
    stopTour();
  });
  board.addEventListener('pointermove', event => {
    if (drag && drag.id === event.pointerId) {
      const dx = event.clientX - drag.x, dy = event.clientY - drag.y;
      if (!drag.moved && Math.abs(dx) + Math.abs(dy) > 5) {
        drag.moved = true; board.classList.add('is-dragging');
        if (!board.hasPointerCapture(event.pointerId)) board.setPointerCapture(event.pointerId);
      }
      if (drag.moved) {
        yaw = clamp(drag.yaw + dx * .0009, -.21, .21);
        pitch = clamp(drag.pitch - dy * .0007, -.14, .14);
        pointerX = pointerY = 0; draw();
      }
    } else if (motion && event.pointerType === 'mouse') {
      const rect = board.getBoundingClientRect();
      pointerX = (event.clientX - rect.left) / width - .5;
      pointerY = (event.clientY - rect.top) / height - .5;
    }
  });
  function endDrag(event) {
    if (!drag || drag.id !== event.pointerId) return;
    if (board.hasPointerCapture(event.pointerId)) board.releasePointerCapture(event.pointerId);
    drag = null; board.classList.remove('is-dragging');
  }
  board.addEventListener('pointerup', endDrag);
  board.addEventListener('pointercancel', endDrag);
  board.addEventListener('lostpointercapture', () => { drag = null; board.classList.remove('is-dragging'); });
  board.addEventListener('pointerleave', () => { pointerX = pointerY = 0; });
  function project(x, y, z) {
    const cx = width * .5, cy = height * (width < 600 ? .43 : .48);
    const ax = yaw + (motion ? pointerX * .045 : 0);
    const ay = pitch + (motion ? pointerY * .035 : 0);
    const px = x - cx, py = y - cy;
    const rx = px * Math.cos(ax) + z * Math.sin(ax);
    const rz = -px * Math.sin(ax) + z * Math.cos(ax);
    const ry = py * Math.cos(ay) - rz * Math.sin(ay);
    const depth = py * Math.sin(ay) + rz * Math.cos(ay);
    const scale = 850 / (850 + depth);
    return { x:cx + rx * scale, y:cy + ry * scale, z:depth, scale };
  }
  function curvePoint(start, end, t, bend) {
    const mx = (start.x + end.x) / 2 + bend;
    const my = (start.y + end.y) / 2 - Math.abs(bend) * .45;
    const a = 1 - t;
    return {x:a*a*start.x + 2*a*t*mx + t*t*end.x, y:a*a*start.y + 2*a*t*my + t*t*end.y};
  }
  function draw() {
    const compact = width < 600;
    const hub = project(width * .5, height * (compact ? .43 : .48), 0);
    positions = data.map((node,i) => {
      const p = compact ? mobilePositions[i] : node.position;
      return project(p[0]*width,p[1]*height,p[2]);
    });
    nodeButtons.forEach((button,i) => {
      button.style.left = positions[i].x.toFixed(2) + 'px';
      button.style.top = positions[i].y.toFixed(2) + 'px';
    });
    center.style.left = hub.x + 'px';
    center.style.top = hub.y + 'px';
    if (!ctx) return;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.clearRect(0,0,width,height);
    const glow = ctx.createRadialGradient(hub.x,hub.y,10,hub.x,hub.y,width*.57);
    glow.addColorStop(0,'rgba(92,142,205,.16)');glow.addColorStop(.5,'rgba(74,116,171,.04)');glow.addColorStop(1,'rgba(74,116,171,0)');
    ctx.fillStyle = glow;ctx.fillRect(0,0,width,height);
    stars.forEach((s,i) => {
      ctx.beginPath();ctx.fillStyle = 'rgba(167,202,242,' + (s.a + Math.sin(phase*.45+i)*.025) + ')';
      ctx.arc(s.x*width,s.y*height,s.r,0,Math.PI*2);ctx.fill();
    });
    ctx.save();ctx.translate(hub.x,hub.y+45);
    for (let i=0;i<6;i++) {
      ctx.beginPath();ctx.ellipse(0,i*8,65+i*52,23+i*20,0,0,Math.PI*2);
      ctx.strokeStyle='rgba(137,174,221,'+(.11-i*.012)+')';ctx.lineWidth=.6;ctx.stroke();
    }
    for (let i=0;i<12;i++) {
      const a=i*Math.PI/6;
      ctx.beginPath();ctx.moveTo(Math.cos(a)*50,Math.sin(a)*18);
      ctx.lineTo(Math.cos(a)*Math.min(width*.55,370),Math.sin(a)*130+25);
      ctx.strokeStyle='rgba(137,174,221,.055)';ctx.stroke();
    }
    ctx.restore();
    const activeKey = hovered || selected;
    data.forEach((node,i) => {
      const point=positions[i], active=node.key===activeKey;
      const muted=layer!=='all'&&node.layer!==layer;
      const bend=(i%2===0?1:-1)*Math.min(28,width*.04);
      const mx=(hub.x+point.x)/2+bend,my=(hub.y+point.y)/2-Math.abs(bend)*.45;
      ctx.beginPath();ctx.moveTo(hub.x,hub.y);ctx.quadraticCurveTo(mx,my,point.x,point.y);
      ctx.strokeStyle=muted?'rgba(119,157,204,.075)':active?'rgba(175,216,255,.8)':'rgba(130,173,225,.27)';
      ctx.lineWidth=active?1.3:.75;ctx.stroke();
      if (!muted) {
        const count=active?3:1;
        for(let j=0;j<count;j++) {
          const t=((phase*.09+i*.187+j/count)%1+1)%1;
          const p=curvePoint(hub,point,t,bend);
          const spark=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,active?9:5);
          spark.addColorStop(0,active?'rgba(200,233,255,.9)':'rgba(151,198,245,.6)');
          spark.addColorStop(1,'rgba(128,188,251,0)');
          ctx.fillStyle=spark;ctx.beginPath();ctx.arc(p.x,p.y,active?9:5,0,Math.PI*2);ctx.fill();
        }
      }
    });
    const coreRadius=compact?67:76;
    const coreGlow=ctx.createRadialGradient(hub.x,hub.y,10,hub.x,hub.y,coreRadius*1.7);
    coreGlow.addColorStop(0,'rgba(144,190,245,.07)');coreGlow.addColorStop(.5,'rgba(126,178,237,.08)');coreGlow.addColorStop(1,'rgba(106,163,232,0)');
    ctx.fillStyle=coreGlow;ctx.beginPath();ctx.arc(hub.x,hub.y,coreRadius*1.7,0,Math.PI*2);ctx.fill();
    ctx.save();ctx.translate(hub.x,hub.y);
    ctx.beginPath();ctx.arc(0,0,coreRadius,0,Math.PI*2);ctx.strokeStyle='rgba(155,197,245,.2)';ctx.lineWidth=.7;ctx.stroke();
    ctx.setLineDash([2,9]);ctx.beginPath();ctx.arc(0,0,coreRadius+8,phase*.025,Math.PI*2+phase*.025);ctx.strokeStyle='rgba(158,201,251,.32)';ctx.stroke();ctx.setLineDash([]);
    [[-.9,.4],[1.5,2.2],[3.4,3.9]].forEach(([a,b]) => {
      ctx.beginPath();ctx.arc(0,0,coreRadius+15,a+phase*.035,b+phase*.035);ctx.strokeStyle='rgba(173,213,255,.23)';ctx.lineWidth=1.3;ctx.stroke();
    });
    ctx.restore();
  }
  function tick(time) {
    frame=0;
    if (!motion || !inView || document.hidden) return;
    if (time-lastPaint>30) {
      phase+=Math.min((time-lastPaint)/1000,.05);lastPaint=time;draw();
    }
    frame=requestAnimationFrame(tick);
  }
  function startFrame() {
    if (motion && inView && !document.hidden && !frame) { lastPaint=performance.now();frame=requestAnimationFrame(tick); }
  }
  function resize() {
    width=board.clientWidth;height=board.clientHeight;dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);draw();
  }
  new ResizeObserver(resize).observe(board);
  new IntersectionObserver(entries => {
    inView=entries[0].isIntersecting;
    if (!inView && frame) {cancelAnimationFrame(frame);frame=0;}
    startFrame();
  },{rootMargin:'80px'}).observe(board);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && frame) {cancelAnimationFrame(frame);frame=0;} else startFrame();
  });
  updateMotion();resize();
})();
