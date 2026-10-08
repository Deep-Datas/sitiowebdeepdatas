/* Rediseño 2026: interacciones nuevas (se carga después de site.js).
   - El encabezado pasa a claro sobre los paneles profundos ([data-deep]).
   - Núcleo de datos: secuencia de cuadros que se recorre con el scroll ([data-core]).
   - Etapa fija que cambia con cada paso ([data-pin], [data-pin-step], [data-pin-view]).
   - Carrusel horizontal ([data-rail]) y brillo que sigue al cursor (.glow-card).
   Sin animaciones (html sin .motion) solo quedan el encabezado y el carrusel. */
(function () {
  var root = document.documentElement;
  var motion = root.classList.contains('motion');

  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }

  /* ---------- Encabezado sobre paneles profundos ---------- */
  var deepZones = Array.prototype.slice.call(document.querySelectorAll('[data-deep]'));
  if (deepZones.length && 'IntersectionObserver' in window) {
    var header = parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 64;
    var over = [];
    var watcher = null;
    var watchDeep = function () {
      if (watcher) watcher.disconnect();
      over = [];
      // Solo cuenta lo que pasa por la franja del encabezado
      watcher = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var i = over.indexOf(entry.target);
          if (entry.isIntersecting && i < 0) over.push(entry.target);
          if (!entry.isIntersecting && i >= 0) over.splice(i, 1);
        });
        root.classList.toggle('on-deep', over.length > 0);
      }, { rootMargin: '0px 0px -' + Math.max(0, window.innerHeight - header) + 'px 0px', threshold: 0 });
      deepZones.forEach(function (zone) { watcher.observe(zone); });
    };
    watchDeep();
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(watchDeep, 150);
    });
  }

  /* ---------- Carrusel horizontal ---------- */
  document.querySelectorAll('[data-rail]').forEach(function (rail) {
    var track = rail.querySelector('.rail-track');
    var prev = rail.querySelector('[data-rail-prev]');
    var next = rail.querySelector('[data-rail-next]');
    if (!track || !prev || !next) return;
    var step = function () {
      var card = track.querySelector('.rail-card');
      return card ? card.offsetWidth + 18 : track.clientWidth * 0.8;
    };
    var update = function () {
      prev.disabled = track.scrollLeft <= 4;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
    };
    prev.addEventListener('click', function () { track.scrollBy({ left: -step() * 2, behavior: 'smooth' }); });
    next.addEventListener('click', function () { track.scrollBy({ left: step() * 2, behavior: 'smooth' }); });
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  if (!motion) return;

  /* ---------- Brillo que sigue al cursor ---------- */
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.addEventListener('pointermove', function (e) {
      var card = e.target.closest && e.target.closest('.glow-card');
      if (!card) return;
      var r = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - r.left).toFixed(0) + 'px');
      card.style.setProperty('--my', (e.clientY - r.top).toFixed(0) + 'px');
    }, { passive: true });
  }

  /* ---------- Etapa fija que cambia con cada paso ---------- */
  document.querySelectorAll('[data-pin]').forEach(function (block) {
    var steps = Array.prototype.slice.call(block.querySelectorAll('[data-pin-step]'));
    var views = Array.prototype.slice.call(block.querySelectorAll('[data-pin-view]'));
    if (!steps.length) return;
    var setCurrent = function (index) {
      steps.forEach(function (el, i) { el.classList.toggle('is-current', i === index); });
      views.forEach(function (el, i) { el.classList.toggle('is-current', i === index); });
    };
    setCurrent(0);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) setCurrent(steps.indexOf(entry.target));
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(function (el) { io.observe(el); });
  });

  /* ---------- Núcleo de datos ---------- */
  document.querySelectorAll('[data-core]').forEach(function (canvas) {
    var stage = canvas.closest('.core-stage');
    var sticky = canvas.parentElement;
    var poster = stage.querySelector('.core-poster');
    var captions = Array.prototype.slice.call(stage.querySelectorAll('[data-at]'));
    var base = canvas.getAttribute('data-src');
    var desktop = window.innerWidth >= 1024;
    var count = parseInt(canvas.getAttribute(desktop ? 'data-frames-d' : 'data-frames-m'), 10) || 1;
    var prefix = desktop ? 'd-' : 'm-';
    var ctx = canvas.getContext('2d');
    var frames = [];
    var loaded = 0;
    var started = false;
    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    var W = 0, H = 0;
    var lastDrawn = -1;

    function size() {
      W = sticky.clientWidth;
      H = sticky.clientHeight;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      lastDrawn = -1;
    }

    function cover(img, alpha) {
      // Dibuja la imagen cubriendo el lienzo (como object-fit: cover)
      var iw = img.naturalWidth, ih = img.naturalHeight;
      if (!iw || !ih) return;
      var s = Math.max(W / iw, H / ih);
      var dw = iw * s, dh = ih * s;
      ctx.globalAlpha = alpha;
      ctx.drawImage(img, (W - dw) / 2 * dpr, (H - dh) / 2 * dpr, dw * dpr, dh * dpr);
      ctx.globalAlpha = 1;
    }

    function ready(i) {
      return frames[i] && frames[i].complete && frames[i].naturalWidth > 0;
    }

    function nearest(i) {
      // El cuadro cargado más cercano, para no esperar a que estén todos
      for (var d = 0; d < count; d++) {
        if (ready(i - d)) return i - d;
        if (ready(i + d)) return i + d;
      }
      return -1;
    }

    var progress = 0;

    function draw() {
      if (!W) size();
      var pos = clamp(progress / 0.78, 0, 1) * (count - 1);
      var a = Math.floor(pos), b = Math.min(count - 1, a + 1), mix = pos - a;
      var fa = nearest(a), fb = nearest(b);
      if (fa < 0) {
        if (poster && poster.complete) { ctx.clearRect(0, 0, canvas.width, canvas.height); cover(poster, 1); }
        return;
      }
      var key = fa * 1000 + fb + mix;
      if (key === lastDrawn) return;
      lastDrawn = key;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      cover(frames[fa], 1);
      if (fb !== fa && mix > 0.02) cover(frames[fb], mix);
    }

    function paint() {
      var rect = stage.getBoundingClientRect();
      var total = stage.offsetHeight - sticky.offsetHeight;
      progress = total > 0 ? clamp(-rect.top / total, 0, 1) : 1;
      var best = null, bestDist = 1;
      captions.forEach(function (el) {
        var dist = Math.abs(progress - parseFloat(el.getAttribute('data-at')));
        if (dist < bestDist) { bestDist = dist; best = el; }
      });
      captions.forEach(function (el) { el.classList.toggle('is-on', el === best && bestDist < 0.2 && progress < 0.8); });
      stage.classList.toggle('is-final', progress >= 0.8);
      draw();
    }

    function load() {
      if (started) return;
      started = true;
      size();
      for (var i = 0; i < count; i++) {
        var img = new Image();
        img.decoding = 'async';
        img.onload = function () {
          loaded++;
          if (loaded === 1) stage.classList.add('is-live');
          lastDrawn = -1;
          draw();
        };
        img.src = base + prefix + (i < 10 ? '0' + i : i) + '.webp';
        frames.push(img);
      }
    }

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { ticking = false; paint(); });
    }, { passive: true });
    window.addEventListener('resize', function () { size(); paint(); });

    if ('IntersectionObserver' in window) {
      var near = new IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) { load(); near.disconnect(); }
      }, { rootMargin: '160% 0px 160% 0px' });
      near.observe(stage);
    } else {
      load();
    }
    paint();
  });
})();
