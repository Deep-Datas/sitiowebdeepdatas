/* Rediseño 2026: interacciones nuevas (se carga después de site.js).
   - El encabezado pasa a claro sobre los paneles profundos ([data-deep]).
   - Núcleo de datos: constelación de registros que se ordena con el scroll ([data-core]).
   - Pregunta y respuesta: el recorrido de una pregunta por los sistemas ([data-flow]).
   - Etapa fija que cambia con cada paso ([data-pin], [data-pin-step], [data-pin-view]).
   - Carrusel horizontal ([data-rail]) y brillo que sigue al cursor (.glow-card).
   Sin animaciones (html sin .motion) quedan el encabezado, el carrusel y el estado final
   del núcleo y del recorrido, dibujados una sola vez. */
(function () {
  var root = document.documentElement;
  var motion = root.classList.contains('motion');
  var slice = function (list) { return Array.prototype.slice.call(list); };

  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smooth(a, b, t) { t = clamp((t - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); }

  /* ---------- Encabezado sobre paneles profundos ---------- */
  var deepZones = slice(document.querySelectorAll('[data-deep]'));
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
  /* ---------- Portada del inicio: una cámara que cruza la oficina ([data-hb]) ----------
     Una sola foto y cuatro actos atados al scroll: el equipo de datos, sus dos monitores,
     el momento en que todo se unifica y, del otro lado de la mampara, los mismos números
     en el televisor de quien decide. La cámara es un rectángulo de la foto que se lleva
     al recorte; cada acto dice qué tiene que entrar sí o sí y acá se le da la forma del
     recorte. Las pantallas se encajan con una matriz de perspectiva y viven dentro de la
     escena, así que la cámara las arrastra sola. Sin animación queda el último acto. */
  document.querySelectorAll('[data-hb]').forEach(function (track) {
    var F, K, statuses, captions;
    try {
      F = JSON.parse(track.getAttribute('data-foto'));
      K = JSON.parse(track.getAttribute('data-cerca'));
      statuses = JSON.parse(track.getAttribute('data-statuses'));
      captions = JSON.parse(track.getAttribute('data-captions'));
    } catch (e) { return; }

    var crop = track.querySelector('.hb-crop');
    var scene = track.querySelector('.hb-scene-a');
    var sceneB = track.querySelector('.hb-scene-b');
    var pin = track.querySelector('.hb-pin');
    if (!crop || !scene || !pin) return;

    // Las pantallas y, sobre el mismo cuadrilátero, el marco que las señala. Las dos
    // últimas viven en la segunda foto, así que se miden contra su tamaño.
    var screens = [
      { el: track.querySelector('.hb-s-tv'), w: 1280, h: 1650, quad: F.tv, foto: F },
      { el: track.querySelector('.hb-r-tv'), w: 1280, h: 1650, quad: F.tv, foto: F },
      { el: track.querySelector('.hb-s-tv2'), w: 1280, h: 720, quad: K.tv, foto: K },
      { el: track.querySelector('.hb-r-tv2'), w: 1280, h: 720, quad: K.tv, foto: K }
    ];

    // Gauss con pivoteo parcial: resuelve los 8 coeficientes de la homografía
    function solve(A, b) {
      var n = b.length, M = A.map(function (row, i) { return row.concat([b[i]]); });
      for (var c = 0; c < n; c++) {
        var piv = c;
        for (var r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
        var t = M[c]; M[c] = M[piv]; M[piv] = t;
        var d = M[c][c];
        for (var j = c; j <= n; j++) M[c][j] /= d;
        for (var k = 0; k < n; k++) {
          if (k === c || !M[k][c]) continue;
          var f = M[k][c];
          for (var j2 = c; j2 <= n; j2++) M[k][j2] -= f * M[c][j2];
        }
      }
      return M.map(function (row) { return row[n]; });
    }

    // Lleva el rectángulo de diseño al cuadrilátero de la pantalla, en píxeles de la
    // escena. sw es el ancho de la escena; el alto sale de la forma de su propia foto.
    function matrixFor(s, sw) {
      var sh = sw * s.foto.h / s.foto.w;
      var src = [[0, 0], [s.w, 0], [s.w, s.h], [0, s.h]];
      var A = [], b = [];
      for (var i = 0; i < 4; i++) {
        var x = src[i][0], y = src[i][1];
        var u = s.quad[i][0] / s.foto.w * sw, v = s.quad[i][1] / s.foto.h * sh;
        A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
        A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
      }
      var h = solve(A, b);
      s.el.style.transform = 'matrix3d(' + [h[0], h[3], 0, h[6], h[1], h[4], 0, h[7], 0, 0, 1, 0, h[2], h[5], 0, 1].join(',') + ')';
    }

    var cropW = 0, cropH = 0, ar = F.w / F.h, fade = 0;
    function measure() {
      cropW = crop.clientWidth;
      cropH = crop.clientHeight;
      if (!cropW || !cropH) return false;
      ar = cropW / cropH;
      fade = copy ? parseFloat(getComputedStyle(copy).getPropertyValue('--fade')) || 0 : 0;
      screens.forEach(function (s) { if (s.el) matrixFor(s, cropW); });
      crop.classList.add('hb-ready');
      return true;
    }

    // El encuadre de un acto: se agranda el rectángulo pedido hasta tener la forma del
    // recorte y se lo mete dentro de la foto. Devuelve [izquierda, arriba, ancho].
    function frame(box, foto) {
      var w = box[2] - box[0], h = box[3] - box[1];
      if (w / h < ar) w = h * ar; else h = w / ar;
      var k = Math.min(1, foto.w / w, foto.h / h);
      w *= k; h *= k;
      var cx = clamp((box[0] + box[2]) / 2, w / 2, foto.w - w / 2);
      var cy = clamp((box[1] + box[3]) / 2, h / 2, foto.h - h / 2);
      return [cx - w / 2, cy - h / 2, w];
    }

    // Una cámara por foto. No salta al valor del scroll: lo persigue con un retardo
    // chico, que es lo que hace que el movimiento se sienta de cámara y no de barra de
    // scroll, y de paso se come los saltos de la rueda del mouse. «quieta» avisa cuándo
    // ya llegó, para no seguir dibujando de gusto.
    function hacerCamara(el, foto) {
      var cam = null, quieta = true;
      return {
        llego: function () { return quieta; },
        arrancar: function () { cam = null; },
        mover: function (p, dt) {
          // En recortes altos (celulares, media pantalla) hay que acercarse más
          var k = ar < 1.1 && foto.cam_alto ? foto.cam_alto : foto.cam, i = 0;
          while (i < k.length - 2 && p > k[i + 1][0]) i++;
          var a = k[i], b = k[i + 1], t = smooth(a[0], b[0], p);
          var meta = frame([lerp(a[1], b[1], t), lerp(a[2], b[2], t),
                            lerp(a[3], b[3], t), lerp(a[4], b[4], t)], foto);
          if (!cam || !dt) {
            cam = meta;
            quieta = true;
          } else {
            var f = 1 - Math.exp(-dt * 7);
            quieta = true;
            for (var j = 0; j < 3; j++) {
              var d = meta[j] - cam[j];
              if (Math.abs(d) > 0.05) quieta = false;
              cam[j] += d * f;
            }
          }
          var s = foto.w / cam[2];
          el.style.transform = 'translate(' + (-s * cam[0] / foto.w * 100).toFixed(3) + '%,' +
            (-s * cam[1] / foto.h * 100).toFixed(3) + '%) scale(' + s.toFixed(4) + ')';
        }
      };
    }

    var camA = hacerCamara(scene, F);
    var camB = sceneB ? hacerCamara(sceneB, K) : null;
    var turnA = track.querySelector('.hb-turn-a');
    var turnB = track.querySelector('.hb-turn-b');
    function quieta() { return camA.llego() && (!camB || camB.llego()); }

    var question = track.getAttribute('data-question') || '';
    var qEl = track.querySelector('[data-hb-q]');
    var caret = track.querySelector('.hb-caret');
    var statusEl = track.querySelector('.hb-status');
    var captionEl = track.querySelector('.hb-caption');
    var micEl = track.querySelector('.hb-mic');
    var scan = track.querySelector('.hb-scan');
    var wave = track.querySelector('.hb-wave path');
    var voice = track.querySelector('.hb-voice');
    var ask = track.querySelector('.hb-ask');
    var join = track.querySelector('.hb-join');
    var joinBar = track.querySelector('.hb-join-bar i');
    var alertEl = track.querySelector('.hb-alert');
    var copy = track.querySelector('.hb-copy');
    var veil = track.querySelector('.hb-veil');
    var rail = track.querySelector('.hb-rail');
    var tvs = slice(track.querySelectorAll('.hb-s-tv, .hb-s-tv2'));
    var wa = track.querySelector('.hb-wa');
    var crm = track.querySelector('.hb-crm');
    var ringTv = slice(track.querySelectorAll('.hb-r-tv, .hb-r-tv2'));
    var oks = slice(track.querySelectorAll('.hb-join-rows .hb-ok'));
    var flies = slice(track.querySelectorAll('.hb-fly'));
    var steps = slice(track.querySelectorAll('.hb-step'));
    var bars = slice(track.querySelectorAll('.hb-tr i'));
    var kpis = slice(track.querySelectorAll('[data-kpi]')).map(function (n) {
      return { n: n, to: n.getAttribute('data-kpi'), pre: n.getAttribute('data-pre') || '', post: n.getAttribute('data-post') || '' };
    });
    var counts = slice(track.querySelectorAll('[data-count]')).map(function (n) {
      return { n: n, to: parseFloat(n.getAttribute('data-count')) };
    });
    // El ancho de cada barra sale de la variable que dejó build.py (pos('w', …)): las
    // pantallas arrancan ocultas, así que el ancho ya calculado todavía no existe.
    var widths = bars.map(function (i) { return parseFloat(getComputedStyle(i).getPropertyValue('--w')) || 0; });
    // Cada paso del riel cubre su acto
    var ACTS = [[0, 0.26], [0.26, 0.54], [0.54, 0.76], [0.76, 1]];

    var locale = root.lang === 'en' ? 'en-US' : 'es-AR';
    function set(el, prop, v) { if (el) el.style.setProperty(prop, v); }
    function text(el, v) {
      if (el && el.getAttribute('data-v') !== v) { el.setAttribute('data-v', v); el.textContent = v; }
    }
    function scramble(value, s) {
      return value.replace(/\d/g, function () { return String((Math.floor(s * 977) + Math.floor(Math.random() * 10)) % 10); });
    }
    var NB = 22;
    function seedAmp(i) { return 0.35 + 0.65 * Math.abs((Math.sin(i * 12.9898) * 43758.5453) % 1); }
    function drawWave(amp, t) {
      var d = '';
      for (var i = 0; i < NB; i++) {
        var x = 2.5 + i * (115 / (NB - 1));
        var hh = 1.6 + amp * (0.55 + 0.45 * Math.sin(t * 7 + i * 0.9)) * seedAmp(i) * 12;
        d += 'M' + x.toFixed(1) + ' ' + (15 - hh).toFixed(1) + ' V' + (15 + hh).toFixed(1) + ' ';
      }
      if (wave) wave.setAttribute('d', d);
    }

    function render(p, t, dt) {
      camA.mover(p, dt);
      // La segunda foto entra girando sobre la pantalla: las dos capas giran a la vez,
      // una saliendo y otra entrando, y el televisor queda donde estaba.
      if (camB) {
        camB.mover(p, dt);
        var cruce = smooth(K.desde, K.hasta, p);
        set(sceneB, '--b', cruce.toFixed(3));
        set(turnA, '--giro', (cruce * -5).toFixed(2) + 'deg');
        set(turnB, '--giro', ((1 - cruce) * 6).toFixed(2) + 'deg');
      }

      // Donde el texto va encima de la escena (celulares) se desvanece con el scroll y
      // el pie entra atrás; donde va al lado (escritorio, media pantalla) se queda.
      // Quién manda es el CSS, con --fade; acá solo se le pasa cuánto se fue.
      if (motion) {
        var fuera = fade ? smooth(0.02, 0.11, p) : 0;
        set(copy, '--out', fuera.toFixed(3));
        set(veil, '--out', fuera.toFixed(3));
        if (copy) copy.hidden = fuera > 0.99;
        set(rail, '--cap', fade ? smooth(0.06, 0.14, p).toFixed(3) : '1');
      }

      // Acto 1: el pedido que acaba de entrar, una vez que el título se fue
      set(ask, '--a', (smooth(0.12, 0.19, p) * (1 - smooth(0.21, 0.27, p))).toFixed(3));

      // El tablero se enciende cuando la cámara ya encara el televisor (antes se ve el
      // que trae la foto, así no quedan números en cero a la vista) y se apaga mientras
      // dura el giro: los dos televisores se ven de ángulos distintos y superpuestos
      // quedarían como una doble imagen. Vuelve del otro lado, ya de frente.
      set(tvs[0], '--a', (smooth(0.68, 0.76, p) * (1 - smooth(0.82, 0.87, p))).toFixed(3));
      if (tvs[1]) set(tvs[1], '--a', smooth(0.90, 0.96, p).toFixed(3));

      // Acto 2: los dos sistemas abiertos mientras se arma la respuesta
      var sale = 1 - smooth(0.50, 0.56, p);
      set(wa, '--a', (smooth(0.26, 0.33, p) * sale).toFixed(3));
      set(crm, '--a', (smooth(0.30, 0.37, p) * sale).toFixed(3));

      // Acto 3: los sistemas cruzan la mampara y se unen en un solo modelo
      set(join, '--a', (smooth(0.55, 0.62, p) * (1 - smooth(0.74, 0.80, p))).toFixed(3));
      set(joinBar, '--p', (smooth(0.57, 0.73, p) * 100).toFixed(1) + '%');
      oks.forEach(function (ok, i) { set(ok, '--ok', smooth(0.58 + i * 0.022, 0.62 + i * 0.022, p).toFixed(3)); });
      flies.forEach(function (fly, i) {
        var f = smooth(0.52 + i * 0.035, 0.70 + i * 0.035, p);
        var vis = f > 0.01 && f < 0.99;
        fly.style.opacity = vis ? 1 : 0;
        if (!vis) return;
        // Van por debajo de los monitores, para no tapar lo que se lee en ellos
        var x = lerp(0.92, 0.06, f) * cropW, y = (0.72 - Math.sin(f * Math.PI) * 0.08 + i * 0.025) * cropH;
        fly.style.transform = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px) translate(-50%,-50%)';
      });

      // Acto 4: la pregunta en voz alta y la respuesta que ya está en el televisor
      set(voice, '--voice', smooth(0.74, 0.80, p).toFixed(3));
      set(alertEl, '--a', smooth(0.93, 0.98, p).toFixed(3));
      var amp = smooth(0.78, 0.83, p) * (1 - smooth(0.90, 0.94, p));
      set(micEl, '--amp', amp.toFixed(3));
      drawWave(amp, t);
      var qn = Math.round(smooth(0.78, 0.90, p) * question.length);
      if (qEl) qEl.textContent = question.slice(0, qn);
      if (caret) caret.hidden = !(qn > 0 && qn < question.length);
      if (statusEl) {
        var st = statuses[0][1];
        statuses.forEach(function (s) { if (p >= s[0]) st = s[1]; });
        text(statusEl, st);
      }
      // El marco del televisor señala y se apaga; la luz de la pantalla se queda
      set(ringTv[0], '--a', (smooth(0.70, 0.76, p) * (1 - smooth(0.80, 0.85, p))).toFixed(3));
      set(ringTv[0], '--g', (smooth(0.70, 0.78, p) * (1 - smooth(0.82, 0.87, p))).toFixed(3));
      if (ringTv[1]) {
        set(ringTv[1], '--a', (smooth(0.91, 0.96, p) * (1 - smooth(0.985, 1, p))).toFixed(3));
        set(ringTv[1], '--g', smooth(0.91, 0.97, p).toFixed(3));
      }
      if (scan) {
        var sc = smooth(0.80, 0.90, p);
        set(scan, '--scan', sc.toFixed(3));
        set(scan, '--scan-a', sc > 0.01 && sc < 0.99 ? '1' : '0');
      }
      kpis.forEach(function (c) {
        var f = smooth(0.82, 0.93, p);
        if (f <= 0) { c.n.textContent = c.pre + c.to.replace(/\d/g, '0') + c.post; return; }
        if (f < 0.45) { c.n.textContent = c.pre + scramble(c.to, f) + c.post; return; }
        var g = clamp((f - 0.45) / 0.55, 0, 1);
        var sep = c.to.indexOf(',') >= 0 ? ',' : '.';
        var dec = (c.to.split(sep)[1] || '').length;
        c.n.textContent = c.pre + (parseFloat(c.to.replace(',', '.')) * g).toFixed(dec).replace('.', sep) + c.post;
      });
      counts.forEach(function (c) {
        c.n.textContent = Math.round(c.to * smooth(0.57, 0.73, p)).toLocaleString(locale);
      });
      bars.forEach(function (bar, i) {
        bar.style.setProperty('--w', (widths[i] * smooth(0.85 + i * 0.02, 0.94 + i * 0.02, p)).toFixed(2) + '%');
      });

      // El riel: en qué acto va el scroll y qué está contando
      steps.forEach(function (step, i) {
        var a = ACTS[i] || ACTS[ACTS.length - 1];
        set(step, '--f', (clamp((p - a[0]) / (a[1] - a[0]), 0, 1) * 100).toFixed(1) + '%');
        if (p >= a[0] && (p < a[1] || i === steps.length - 1)) step.setAttribute('data-on', '');
        else step.removeAttribute('data-on');
      });
      if (captionEl) {
        var cap = captions[0][1];
        captions.forEach(function (c) { if (p >= c[0]) cap = c[1]; });
        text(captionEl, cap);
      }
    }

    var p0 = motion ? 0 : 1;
    function draw(ts, dt) {
      if (!cropW) return;
      render(p0, ts / 1000, dt);
    }

    measure();
    draw(0, 0);

    var resized = function () {
      if (!measure()) return;
      camA.arrancar();
      if (camB) camB.arrancar();
      draw(0, 0);
    };
    if ('ResizeObserver' in window) new ResizeObserver(resized).observe(crop);
    else window.addEventListener('resize', resized);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(resized);
    if (!motion) return;

    // El avance es la parte del riel ya recorrida: la escena queda fija y la cámara viaja
    var header = parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 64;
    // Cuánto avanzó la escena dentro del riel, de 0 a 1. Ojo: el riel empieza pegado al
    // borde de la página, así que con la página arriba de todo la escena pegajosa ya
    // está corrida la altura del encabezado. Eso es el cero, no el borde del riel.
    function progress() {
      var max = track.offsetHeight - pin.offsetHeight;
      if (max <= 0) return 1;
      var top = track.getBoundingClientRect().top;
      var cero = clamp(header - (top + window.pageYOffset), 0, max);
      var ahora = clamp(header - top, 0, max);
      return max - cero <= 0 ? 1 : clamp((ahora - cero) / (max - cero), 0, 1);
    }

    var running = false, lastP = -1, lastTs = 0;
    function frameLoop(ts) {
      if (!running) return;
      var dt = lastTs ? Math.min(0.05, (ts - lastTs) / 1000) : 0;
      lastTs = ts;
      p0 = progress();
      // Quieto el scroll y llegada la cámara, solo hace falta la onda de la voz
      if (p0 !== lastP || !quieta() || (p0 > 0.76 && p0 < 0.95)) { lastP = p0; draw(ts, dt); }
      window.requestAnimationFrame(frameLoop);
    }
    var play = function (on) {
      if (on === running) return;
      running = on;
      // Al volver a entrar en pantalla la cámara arranca donde está el scroll, sin viaje
      if (on) {
        lastTs = 0;
        camA.arrancar();
        if (camB) camB.arrancar();
        window.requestAnimationFrame(frameLoop);
      }
    };
    if ('IntersectionObserver' in window) {
      var seen = new IntersectionObserver(function (entries) {
        play(entries.some(function (e) { return e.isIntersecting; }));
      }, { threshold: 0 });
      seen.observe(track);
    } else {
      play(true);
    }
  });

  /* ---------- Núcleo de datos: constelación de registros ----------
     Cada punto es un registro, con el color del sistema donde vive hoy. Flotan en cinco nubes
     y, a medida que se avanza, viajan hasta una esfera ordenada que se enciende desde el centro.
     Mientras están dispersos, el cursor los aparta; una vez ordenados, la esfera lo sigue.
     Sin animación se dibuja una sola vez el estado final. */
  var TAU = Math.PI * 2;

  function hexA(hex, a) {
    var n = parseInt(hex.slice(1), 16);
    return 'rgba(' + ((n >> 16) & 255) + ', ' + ((n >> 8) & 255) + ', ' + (n & 255) + ', ' + a + ')';
  }

  function sprite(hex) {
    // Un punto suave pre-dibujado: dibujar imágenes es más rápido que dibujar círculos
    var c = document.createElement('canvas');
    c.width = c.height = 32;
    var g = c.getContext('2d');
    var grd = g.createRadialGradient(16, 16, 0, 16, 16, 16);
    grd.addColorStop(0, hexA(hex, 1));
    grd.addColorStop(0.45, hexA(hex, 1));
    grd.addColorStop(0.75, hexA(hex, 0.35));
    grd.addColorStop(1, hexA(hex, 0));
    g.fillStyle = grd;
    g.fillRect(0, 0, 32, 32);
    return c;
  }

  function fibonacciSphere(n) {
    var pts = [], ga = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < n; i++) {
      var y = 1 - (i / (n - 1)) * 2, r = Math.sqrt(1 - y * y), th = ga * i;
      pts.push([Math.cos(th) * r, y, Math.sin(th) * r]);
    }
    return pts;
  }

  function rotate(v, a, b) {
    var ca = Math.cos(a), sa = Math.sin(a), cb = Math.cos(b), sb = Math.sin(b);
    var x1 = v[0] * ca + v[2] * sa, z1 = -v[0] * sa + v[2] * ca;
    return [x1, v[1] * cb - z1 * sb, v[1] * sb + z1 * cb];
  }

  document.querySelectorAll('[data-core]').forEach(function (canvas) {
    var stage = canvas.closest('.core-stage');
    var sticky = canvas.parentElement;
    var captions = slice(stage.querySelectorAll('[data-at]'));
    var ctx = canvas.getContext('2d');
    if (!ctx) return;
    var labels = (canvas.getAttribute('data-labels') || 'ERP|CRM|Planillas|WhatsApp|Correo').split('|');
    var colors = ['#0b1220', '#2353d6', '#0f8f7a', '#128c7e', '#e4581c'];
    var sprites = colors.map(sprite);
    var small = window.innerWidth < 720;
    var centers = small
      ? [[0.22, 0.17], [0.78, 0.15], [0.5, 0.34], [0.2, 0.56], [0.8, 0.54]]
      : [[0.17, 0.26], [0.82, 0.22], [0.5, 0.17], [0.2, 0.66], [0.82, 0.64]];
    var count = small ? 380 : 760;
    var sphere = fibonacciSphere(count);
    var pts = [];
    for (var i = 0; i < count; i++) {
      var ang = Math.random() * TAU, rad = Math.sqrt(Math.random()) * 0.15 * (0.5 + Math.random());
      // Desplazamientos en fracciones del lado menor: la escena se adapta al tamaño sin regenerarse
      pts.push({ c: i % 5, ox: Math.cos(ang) * rad, oy: Math.sin(ang) * rad * 0.8, v: sphere[i], ph: Math.random() * TAU, sp: 0.5 + Math.random() * 0.9, size: 1.3 + Math.random() * 1.5, d: Math.random() });
    }
    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    var W = 0, H = 0, M = 0, R = 0, cx = 0, cy = 0;
    var ptr = { x: 0, y: 0, active: false };
    var ry = 0, rx = -0.25, time = 0, progress = 0;

    function size() {
      W = sticky.clientWidth;
      H = sticky.clientHeight;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      M = Math.min(W, H);
      R = M * 0.3;
      cx = W / 2;
      cy = H * (small ? 0.34 : 0.37);
      if (!motion) {
        // Sin animación todo el texto queda debajo: la esfera ocupa el espacio libre de arriba
        var copy = sticky.querySelector('.core-copy');
        var top = copy ? copy.offsetTop + (parseFloat(getComputedStyle(copy).paddingTop) || 0) : H * 0.6;
        cy = Math.max(top * 0.5, M * 0.2);
        R = Math.min(Math.max(top * 0.4, M * 0.14), M * 0.3);
      }
    }

    function draw(p, t) {
      ctx.clearRect(0, 0, W, H);
      var glow = smooth(0.6, 1, p);
      if (glow > 0) {
        var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 2);
        g.addColorStop(0, 'rgba(255, 122, 69, ' + 0.22 * glow + ')');
        g.addColorStop(0.45, 'rgba(91, 140, 255, ' + 0.1 * glow + ')');
        g.addColorStop(1, 'rgba(91, 140, 255, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, W, H);
      }
      var travel = smooth(0.3, 0.78, p);
      var jit = (1 - smooth(0.15, 0.7, p)) * 9 + 1.2;
      var px = ptr.active ? ptr.x / W - 0.5 : 0, py = ptr.active ? ptr.y / H - 0.5 : 0;
      ry = lerp(ry, t * 0.14 + px * 0.9, 0.08);
      rx = lerp(rx, -0.25 + py * 0.5, 0.08);
      var la = 1 - smooth(0.22, 0.48, p);
      if (la > 0) {
        ctx.font = '600 12px Geist, Inter, sans-serif';
        ctx.textAlign = 'center';
        for (var k = 0; k < 5; k++) {
          ctx.fillStyle = hexA(colors[k], la);
          ctx.fillText(labels[k].toUpperCase(), centers[k][0] * W, centers[k][1] * H - M * 0.15 - 4);
        }
      }
      var items = [], rr = M * 0.14;
      for (var i = 0; i < pts.length; i++) {
        var q = pts[i];
        var v = rotate(q.v, ry, rx);
        var pr = 1 / (1 - v[2] * 0.32);
        var tx = cx + v[0] * R * pr, ty = cy + v[1] * R * pr;
        var sx = centers[q.c][0] * W + q.ox * M + Math.sin(t * q.sp + q.ph) * jit;
        var sy = centers[q.c][1] * H + q.oy * M + Math.cos(t * q.sp * 0.8 + q.ph) * jit;
        if (ptr.active && travel < 1) {
          var dx = sx - ptr.x, dy = sy - ptr.y, dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < rr && dist > 0.01) {
            var f = (1 - dist / rr) * (1 - travel) * 38;
            sx += dx / dist * f;
            sy += dy / dist * f;
          }
        }
        var e = clamp((travel - q.d * 0.3) / 0.7, 0, 1), es = e * e * (3 - 2 * e);
        var depth = (v[2] + 1) / 2;
        items.push({ x: lerp(sx, tx, es), y: lerp(sy, ty, es), s: q.size * lerp(1, 0.55 + 0.95 * depth, es), a: lerp(0.85, 0.28 + 0.72 * depth, es), c: q.c, z: v[2] * es });
      }
      items.sort(function (a, b) { return a.z - b.z; });
      for (var j = 0; j < items.length; j++) {
        var it = items[j], s = it.s * 2.2;
        ctx.globalAlpha = it.a;
        ctx.drawImage(sprites[it.c], it.x - s, it.y - s, s * 2, s * 2);
      }
      ctx.globalAlpha = 1;
      var fin = smooth(0.78, 1, p);
      if (fin > 0) {
        ctx.save();
        ctx.translate(cx, cy);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(35, 83, 214, ' + 0.35 * fin + ')';
        ctx.beginPath(); ctx.ellipse(0, 0, R * 1.6, R * 0.52, -0.5 + t * 0.05, 0, TAU); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(0, 0, R * 1.38, R * 0.44, 0.9 - t * 0.04, 0, TAU); ctx.stroke();
        ctx.restore();
        var core = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 0.5);
        core.addColorStop(0, 'rgba(255, 255, 255, ' + 0.95 * fin + ')');
        core.addColorStop(0.5, 'rgba(255, 184, 148, ' + 0.4 * fin + ')');
        core.addColorStop(1, 'rgba(255, 184, 148, 0)');
        ctx.fillStyle = core;
        ctx.fillRect(cx - R, cy - R, R * 2, R * 2);
      }
    }

    if (!motion) {
      // Estado final, quieto: la esfera ordenada bajo el texto
      size();
      draw(1, 2);
      window.addEventListener('resize', function () { size(); draw(1, 2); });
      return;
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
    }

    var visible = false, running = false, last = 0;
    function frame(ts) {
      if (!visible) { running = false; return; }
      var dt = last ? Math.min(0.05, (ts - last) / 1000) : 0;
      last = ts;
      time += dt;
      paint();
      draw(clamp(progress / 0.85, 0, 1), time);
      window.requestAnimationFrame(frame);
    }
    function start() {
      if (running) return;
      running = true;
      last = 0;
      window.requestAnimationFrame(frame);
    }

    sticky.addEventListener('pointermove', function (e) {
      var r = sticky.getBoundingClientRect();
      ptr.x = e.clientX - r.left;
      ptr.y = e.clientY - r.top;
      ptr.active = true;
    }, { passive: true });
    sticky.addEventListener('pointerleave', function () { ptr.active = false; });
    sticky.addEventListener('pointercancel', function () { ptr.active = false; });
    window.addEventListener('resize', function () { size(); paint(); draw(clamp(progress / 0.85, 0, 1), time); });

    size();
    paint();
    draw(clamp(progress / 0.85, 0, 1), time);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries.some(function (e) { return e.isIntersecting; });
        if (visible) start();
      }, { rootMargin: '20% 0px 20% 0px' }).observe(stage);
    } else {
      visible = true;
      start();
    }
  });

  /* ---------- Pregunta y respuesta: el recorrido por los sistemas ----------
     Las líneas se dibujan en un SVG sobre la grilla; la posición de cada nodo se mide del DOM.
     Con animación, el recorrido se reproduce al entrar en pantalla y con cada pregunta elegida.
     Sin animación se muestra el estado final. */
  document.querySelectorAll('[data-flow]').forEach(function (flow) {
    var qa;
    try { qa = JSON.parse(flow.getAttribute('data-qa')); } catch (e) { return; }
    if (!qa || !qa.length) return;
    var SVG = 'http://www.w3.org/2000/svg';
    var grid = flow.querySelector('.fl-grid');
    var svg = flow.querySelector('.fl-edges');
    var sources = slice(flow.querySelectorAll('[data-flow-src]'));
    var curate = flow.querySelector('[data-flow-curate]');
    var checks = slice(curate.querySelectorAll('li'));
    var agent = flow.querySelector('[data-flow-agent]');
    var qEl = flow.querySelector('[data-flow-q]');
    var aEl = flow.querySelector('[data-flow-a]');
    var caret = flow.querySelector('[data-flow-caret]');
    var srcLine = flow.querySelector('[data-flow-srcline]');
    var chips = slice(flow.querySelectorAll('[data-flow-chip]'));
    var colors = { erp: '#0b1220', crm: '#2353d6', xls: '#0f8f7a', wa: '#128c7e', mail: '#e4581c' };

    function el(name, cls) {
      var n = document.createElementNS(SVG, name);
      n.setAttribute('class', cls);
      return n;
    }
    var edges = sources.map(function (li) {
      var id = li.getAttribute('data-flow-src'), color = colors[id] || '#0b1220';
      var raw = el('path', 'fl-raw'), lit = el('path', 'fl-lit'), pulse = el('circle', 'fl-pulse');
      lit.setAttribute('stroke', color);
      pulse.setAttribute('r', '4');
      pulse.setAttribute('fill', color);
      svg.appendChild(raw); svg.appendChild(lit); svg.appendChild(pulse);
      return { id: id, li: li, raw: raw, lit: lit, pulse: pulse, len: 0 };
    });
    var out = { lit: el('path', 'fl-lit'), pulse: el('circle', 'fl-pulse'), len: 0 };
    out.lit.setAttribute('stroke', '#e4581c');
    out.pulse.setAttribute('r', '5');
    out.pulse.setAttribute('fill', '#e4581c');
    svg.appendChild(out.lit); svg.appendChild(out.pulse);

    var current = 0, p = motion ? 0 : 1, playing = false, last = 0, played = false;

    function layout() {
      var vertical = grid.clientWidth < 640;
      var box = grid.getBoundingClientRect();
      var rel = function (node) { var r = node.getBoundingClientRect(); return { x: r.left - box.left, y: r.top - box.top, w: r.width, h: r.height }; };
      var path = function (a, b) {
        return vertical
          ? 'M ' + a.x + ' ' + a.y + ' C ' + a.x + ' ' + (a.y + (b.y - a.y) * 0.5) + ', ' + b.x + ' ' + (a.y + (b.y - a.y) * 0.5) + ', ' + b.x + ' ' + b.y
          : 'M ' + a.x + ' ' + a.y + ' C ' + (a.x + (b.x - a.x) * 0.5) + ' ' + a.y + ', ' + (b.x - (b.x - a.x) * 0.5) + ' ' + b.y + ', ' + b.x + ' ' + b.y;
      };
      var cu = rel(curate), ag = rel(agent);
      edges.forEach(function (e) {
        var s = rel(e.li);
        var a = vertical ? { x: s.x + s.w / 2, y: s.y + s.h } : { x: s.x + s.w, y: s.y + s.h / 2 };
        var b = vertical ? { x: cu.x + cu.w / 2, y: cu.y } : { x: cu.x, y: cu.y + cu.h / 2 };
        var d = path(a, b);
        e.raw.setAttribute('d', d);
        e.lit.setAttribute('d', d);
        e.len = e.lit.getTotalLength();
        e.lit.setAttribute('stroke-dasharray', String(e.len));
      });
      var a = vertical ? { x: cu.x + cu.w / 2, y: cu.y + cu.h } : { x: cu.x + cu.w, y: cu.y + cu.h / 2 };
      var b = vertical ? { x: ag.x + 24, y: ag.y } : { x: ag.x, y: ag.y + ag.h / 2 };
      out.lit.setAttribute('d', path(a, b));
      out.len = out.lit.getTotalLength();
      out.lit.setAttribute('stroke-dasharray', String(out.len));
    }

    function render() {
      var item = qa[current];
      var qn = Math.round(smooth(0.02, 0.16, p) * item.q.length);
      qEl.textContent = item.q.slice(0, qn);
      edges.forEach(function (e, i) {
        var on = p > 0.08 + i * 0.045;
        e.li.classList.toggle('is-on', on);
        e.raw.classList.toggle('is-on', on);
        var hot = item.hot.indexOf(e.id) >= 0;
        e.li.classList.toggle('is-hot', hot && p > 0.3);
        var tt = smooth(0.3 + i * 0.03, 0.6 + i * 0.03, p);
        var drawn = hot ? tt : tt * 0.6;
        e.lit.setAttribute('stroke-dashoffset', String(e.len * (1 - drawn)));
        e.lit.setAttribute('opacity', hot ? '1' : '0.35');
        var show = tt > 0 && tt < 1;
        e.pulse.classList.toggle('is-on', show);
        if (show && e.len) {
          var pt = e.lit.getPointAtLength(e.len * drawn);
          e.pulse.setAttribute('cx', pt.x);
          e.pulse.setAttribute('cy', pt.y);
        }
      });
      var cur = smooth(0.42, 0.7, p);
      curate.classList.toggle('is-on', cur > 0.15);
      checks.forEach(function (li, i) { li.classList.toggle('is-done', cur > 0.3 + i * 0.18); });
      var to = smooth(0.68, 0.8, p);
      out.lit.setAttribute('stroke-dashoffset', String(out.len * (1 - to)));
      var showOut = to > 0 && to < 1;
      out.pulse.classList.toggle('is-on', showOut);
      if (showOut && out.len) {
        var pt2 = out.lit.getPointAtLength(out.len * to);
        out.pulse.setAttribute('cx', pt2.x);
        out.pulse.setAttribute('cy', pt2.y);
      }
      agent.style.setProperty('--glow', smooth(0.76, 0.9, p).toFixed(3));
      var an = Math.round(smooth(0.82, 0.985, p) * item.a.length);
      aEl.textContent = item.a.slice(0, an);
      caret.hidden = !(an > 0 && an < item.a.length);
      srcLine.textContent = item.src;
      srcLine.classList.toggle('is-on', p > 0.985);
    }

    function step(ts) {
      if (!playing) return;
      var dt = last ? Math.min(0.05, (ts - last) / 1000) : 0;
      last = ts;
      p = Math.min(1, p + dt / 6.5);
      render();
      if (p < 1) window.requestAnimationFrame(step); else playing = false;
    }
    function play() {
      if (!motion) { p = 1; render(); return; }
      p = 0; last = 0; playing = true;
      window.requestAnimationFrame(step);
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        current = parseInt(chip.getAttribute('data-flow-chip'), 10) || 0;
        chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        played = true;
        play();
      });
    });
    sources.forEach(function (li) {
      var id = li.getAttribute('data-flow-src');
      var mark = function (on) {
        if (on) flow.setAttribute('data-hover', id); else flow.removeAttribute('data-hover');
        edges.forEach(function (e) { e.raw.classList.toggle('is-hot', on && e.id === id); e.lit.classList.toggle('is-hot', on && e.id === id); });
      };
      li.addEventListener('pointerenter', function () { mark(true); });
      li.addEventListener('pointerleave', function () { mark(false); });
    });

    var relayout = function () { layout(); render(); };
    layout();
    render();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(relayout);
    if ('ResizeObserver' in window) {
      // La respuesta crece mientras se escribe y mueve al agente: se vuelven a medir las líneas
      var ro = new ResizeObserver(relayout);
      ro.observe(grid);
      ro.observe(flow.querySelector('.fl-answer'));
    } else {
      window.addEventListener('resize', relayout);
    }

    if (motion && 'IntersectionObserver' in window) {
      var seen = new IntersectionObserver(function (entries) {
        if (played || !entries.some(function (e) { return e.isIntersecting; })) return;
        played = true;
        seen.disconnect();
        play();
      }, { threshold: 0.45 });
      seen.observe(flow);
    } else if (motion) {
      play();
    }
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
    var steps = slice(block.querySelectorAll('[data-pin-step]'));
    var views = slice(block.querySelectorAll('[data-pin-view]'));
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

  /* ---------- Videos que se reproducen solos mientras se ven ---------- */
  if ('IntersectionObserver' in window) {
    var videos = slice(document.querySelectorAll('video[data-autoplay]'));
    if (videos.length) {
      var seenVideos = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var v = entry.target;
          if (entry.isIntersecting) {
            var pr = v.play();
            if (pr && pr.catch) pr.catch(function () {});
          } else if (!v.paused) {
            v.pause();
          }
        });
      }, { threshold: 0.35 });
      videos.forEach(function (v) { seenVideos.observe(v); });
    }
  }
})();
