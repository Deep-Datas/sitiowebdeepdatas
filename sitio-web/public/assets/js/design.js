/* Rediseño 2026: interacciones nuevas (se carga después de site.js).
   - El encabezado pasa a claro sobre los paneles profundos ([data-deep]).
   - Portada del inicio: la pregunta en voz alta y los cinco sistemas que se funden ([data-vz]).
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
  /* ---------- Portada del inicio: la pregunta en voz alta ([data-vz]) ----------
     Dos cosas en la misma etapa fija.

     La demostración: se elige una de tres preguntas, se escribe sola en la barra, la onda
     late mientras «escucha» y abajo aparece la respuesta con las fuentes. No hay micrófono
     de verdad: no se pide permiso ni sale audio a ningún lado.

     La consolidación: debajo de la portada hay un riel que mantiene fija su etapa mientras
     dura. Los cinco sistemas entran desde los costados y desde abajo, se acomodan alrededor
     del centro y sus nubes de registros viajan hasta una sola esfera. Las posiciones se
     calculan acá porque dependen de lo que mida la etapa.

     Sin animación no hay riel: la demostración responde igual (sin escribirse letra por
     letra) y la consolidación se dibuja una vez, ya terminada. */
  document.querySelectorAll('[data-vz]').forEach(function (seccion) {
    var preguntas, estados, leyendas;
    try {
      preguntas = JSON.parse(seccion.getAttribute('data-preguntas'));
      estados = JSON.parse(seccion.getAttribute('data-states'));
      leyendas = JSON.parse(seccion.getAttribute('data-fuse'));
    } catch (e) { return; }
    if (!preguntas || !preguntas.length) return;

    var track = seccion.querySelector('[data-vz-track]');
    var pin = seccion.querySelector('.vz-pin');
    var demo = seccion.querySelector('.vz-demo');

    /* ----- La demostración ----- */
    var quieto = seccion.querySelector('[data-vz-still]');
    var boton = seccion.querySelector('[data-vz-play]');
    var dicho = seccion.querySelector('[data-vz-said]');
    var estado = seccion.querySelector('[data-vz-state]');
    var caja = seccion.querySelector('[data-vz-chips]');
    var fichas = slice(seccion.querySelectorAll('[data-vz-q]'));
    var tarjeta = seccion.querySelector('[data-vz-answer]');
    var elQ = seccion.querySelector('[data-vz-aq]');
    var elBig = seccion.querySelector('[data-vz-abig]');
    var elTag = seccion.querySelector('[data-vz-atag]');
    var elTxt = seccion.querySelector('[data-vz-atxt]');
    var elSrc = seccion.querySelector('[data-vz-asrc]');
    var barras = slice(seccion.querySelectorAll('[data-vz-wave] i'));

    // Lo que sin JavaScript no haría nada recién aparece ahora
    if (quieto) quieto.hidden = true;
    if (boton) boton.hidden = false;
    if (caja) caja.hidden = false;

    var semillas = barras.map(function (_, i) {
      return 0.35 + 0.65 * Math.abs(Math.sin(i * 12.9898) * 43758.5453 % 1);
    });

    function onda(amp, t) {
      for (var i = 0; i < barras.length; i++) {
        var h = 4 + amp * (0.55 + 0.45 * Math.sin(t * 7 + i * 0.8)) * semillas[i] * 22;
        barras[i].style.setProperty('height', h.toFixed(1) + 'px');
      }
    }

    function pintar(p) {
      elQ.textContent = p.q;
      elBig.textContent = p.big;
      elTag.textContent = p.tag;
      elTxt.textContent = p.txt;
      tarjeta.className = 'vz-answer vz-' + p.tone;
      while (elSrc.firstChild) elSrc.removeChild(elSrc.firstChild);
      p.src.forEach(function (f) {
        var pastilla = document.createElement('span');
        pastilla.className = 'vz-src-pill vz-c-' + f[0];
        pastilla.appendChild(document.createElement('i'));
        pastilla.appendChild(document.createTextNode(f[1]));
        elSrc.appendChild(pastilla);
      });
    }

    // Una sola corrida por vez: cada llamada se queda con el turno y la anterior se calla
    var turno = 0, latido = 0, tecla = 0, apagando = 0, elegida = 0, tocado = false;

    function marcar(i) {
      fichas.forEach(function (ficha, k) {
        ficha.classList.toggle('is-on', k === i);
        ficha.setAttribute('aria-pressed', k === i ? 'true' : 'false');
      });
    }

    function terminar(p, mio) {
      if (mio !== turno) return;
      demo.classList.remove('is-live');
      demo.classList.add('is-done');
      estado.textContent = estados[2];
      dicho.textContent = p.q;
      dicho.classList.remove('is-typing');
      pintar(p);
      if (!motion) return;
      window.cancelAnimationFrame(latido);
      clearInterval(apagando);
      var t = 0;
      apagando = setInterval(function () {
        t += 0.08;
        onda(Math.max(0, 1 - t * 2.5), t);
        if (t > 0.4) { clearInterval(apagando); onda(0, 0); }
      }, 40);
    }

    function escribir(p, n, mio) {
      if (mio !== turno) return;
      n++;
      dicho.textContent = p.q.slice(0, n);
      if (n < p.q.length) {
        tecla = setTimeout(function () { escribir(p, n, mio); }, 1300 / p.q.length);
      } else {
        dicho.classList.remove('is-typing');
        estado.textContent = estados[1];
        tecla = setTimeout(function () { terminar(p, mio); }, 850);
      }
    }

    function correr(i) {
      var mio = ++turno;
      elegida = i;
      marcar(i);
      clearTimeout(tecla);
      clearInterval(apagando);
      window.cancelAnimationFrame(latido);
      var p = preguntas[i];
      if (!motion) { terminar(p, mio); return; }
      demo.classList.add('is-live');
      demo.classList.remove('is-done');
      estado.textContent = estados[0];
      dicho.classList.add('is-typing');
      dicho.textContent = '';
      var t0 = window.performance && performance.now ? performance.now() : Date.now();
      (function latir() {
        if (mio !== turno) return;
        var ahora = window.performance && performance.now ? performance.now() : Date.now();
        onda(1, (ahora - t0) / 1000);
        latido = window.requestAnimationFrame(latir);
      })();
      escribir(p, 0, mio);
    }

    // La respuesta se anuncia recién cuando alguien pide una: así la que se escribe sola
    // al entrar a la página no le interrumpe la lectura a nadie.
    function pedida() {
      tocado = true;
      tarjeta.setAttribute('aria-live', 'polite');
    }

    fichas.forEach(function (ficha) {
      ficha.addEventListener('click', function () {
        pedida();
        correr(+ficha.getAttribute('data-vz-q'));
      });
    });
    if (boton) {
      boton.addEventListener('click', function () { pedida(); correr(elegida); });
    }
    onda(0, 0);

    /* ----- La consolidación: los cinco sistemas y el núcleo ----- */
    var fuse = seccion.querySelector('[data-vz-fuse]');
    var lienzo = seccion.querySelector('[data-vz-core]');
    var corro = seccion.querySelector('.vz-srcs');
    var sistemas = slice(seccion.querySelectorAll('[data-vz-sys]'));
    var linea = seccion.querySelector('[data-vz-line]');
    var ctx = lienzo && lienzo.getContext ? lienzo.getContext('2d') : null;
    if (!fuse || !track || !pin || !linea) return;

    // El mismo color por sistema que usa el núcleo de datos de más abajo ([data-core])
    var COLORES = ['#0b1220', '#2353d6', '#0f8f7a', '#128c7e', '#e4581c'];
    // Dónde queda cada sistema alrededor del núcleo, en grados sobre el lienzo (la y crece
    // hacia abajo): se reparten el arco de arriba, que es el aire que deja la frase.
    var ANGULOS = [168, 216, 270, 324, 12];
    // Y de qué lado entra cada uno: los dos del medio por los costados, los otros tres
    // desde abajo. El rumbo se estira hasta sacarlos del cuadro, mida lo que mida.
    var RUMBOS = [[-0.75, 1], [-1, 0.15], [0, 1], [1, 0.15], [0.75, 1]];
    // Cuánto espera cada uno antes de entrar, en fracción del riel
    var ESPERA = [0.09, 0.035, 0, 0.035, 0.09];
    var dibujos = COLORES.map(sprite);
    var CUANTOS = window.innerWidth < 720 ? 280 : 600;
    var esfera = fibonacciSphere(CUANTOS);
    var puntos = [];
    for (var i = 0; i < CUANTOS; i++) {
      var ang = Math.random() * Math.PI * 2;
      var rad = Math.sqrt(Math.random()) * 0.13 * (0.5 + Math.random());
      // Los desvíos van en fracción del lado menor: la escena se adapta sin regenerarse
      puntos.push({
        c: i % 5, ox: Math.cos(ang) * rad, oy: Math.sin(ang) * rad * 0.8, v: esfera[i],
        ph: Math.random() * Math.PI * 2, sp: 0.5 + Math.random() * 0.9,
        size: 1.2 + Math.random() * 1.4, d: Math.random(),
      });
    }

    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    var W = 0, H = 0, M = 0, R = 0, cx = 0, cy = 0, giro = 0;
    // «anillo» es dónde termina cada sistema, «entradas» de dónde viene y «puestos» dónde
    // está ahora: la nube de registros viaja pegada a su pastilla, no la espera en el lugar.
    var anillo = [], entradas = [], puestos = [];

    function medir() {
      if (!fuse) return;
      W = fuse.clientWidth;
      H = fuse.clientHeight;
      if (ctx) {
        lienzo.width = Math.round(W * dpr);
        lienzo.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
      M = Math.min(W, H);
      R = M * 0.2;
      cx = W / 2;
      cy = H * 0.46;
      if (!motion) {
        // Sin riel los cinco sistemas van en una fila y la esfera ocupa el aire de arriba
        var tope = corro ? corro.offsetTop : H * 0.6;
        cy = Math.max(tope * 0.5, M * 0.18);
        R = Math.min(M * 0.26, Math.max(tope * 0.38, 52));
      }
      var rx = Math.min(W * 0.33, 430), ry = Math.min(H * 0.27, 250);
      anillo = ANGULOS.map(function (a) {
        var r = a * Math.PI / 180;
        return [cx + Math.cos(r) * rx, cy + Math.sin(r) * ry];
      });
      entradas = RUMBOS.map(function (d) {
        var hx = Math.abs(d[0]) > 0.01 ? (W / 2 + 220) / Math.abs(d[0]) : Infinity;
        var hy = Math.abs(d[1]) > 0.01 ? (H / 2 + 160) / Math.abs(d[1]) : Infinity;
        var k = Math.min(hx, hy);
        return [cx + d[0] * k, cy + d[1] * k];
      });
      puestos = motion ? entradas.slice() : anillo.slice();
    }

    function dibujar(p, t) {
      if (!ctx) return;
      ctx.clearRect(0, 0, W, H);
      // Cada nube se enciende cuando entra la suya, no todas juntas
      var velos = ESPERA.map(function (e) {
        return motion ? smooth(0.02 + e, 0.22 + e, p) : 1;
      });

      var fin = smooth(0.8, 0.98, p);
      if (fin > 0) {
        var halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 2.4);
        halo.addColorStop(0, 'rgba(255, 122, 69, ' + 0.2 * fin + ')');
        halo.addColorStop(0.45, 'rgba(91, 140, 255, ' + 0.09 * fin + ')');
        halo.addColorStop(1, 'rgba(91, 140, 255, 0)');
        ctx.fillStyle = halo;
        ctx.fillRect(0, 0, W, H);
      }

      var viaje = smooth(0.48, 0.86, p);
      var tembleque = (1 - smooth(0.42, 0.84, p)) * 7 + 1.1;
      giro = lerp(giro, t * 0.14, 0.08);
      var lista = [];
      for (var k = 0; k < puntos.length; k++) {
        var q = puntos[k];
        var v = rotate(q.v, giro, -0.25);
        var pr = 1 / (1 - v[2] * 0.32);
        var tx = cx + v[0] * R * pr, ty = cy + v[1] * R * pr;
        var casa = puestos[q.c] || anillo[q.c] || [cx, cy];
        var sx = casa[0] + q.ox * M + Math.sin(t * q.sp + q.ph) * tembleque;
        var sy = casa[1] + q.oy * M + Math.cos(t * q.sp * 0.8 + q.ph) * tembleque;
        var e = clamp((viaje - q.d * 0.3) / 0.7, 0, 1), es = e * e * (3 - 2 * e);
        var hondo = (v[2] + 1) / 2;
        lista.push({
          x: lerp(sx, tx, es), y: lerp(sy, ty, es),
          s: q.size * lerp(1, 0.55 + 0.95 * hondo, es),
          a: lerp(0.8, 0.28 + 0.72 * hondo, es) * velos[q.c],
          c: q.c, z: v[2] * es,
        });
      }
      lista.sort(function (a, b) { return a.z - b.z; });
      for (var j = 0; j < lista.length; j++) {
        var it = lista[j], s = it.s * 2.2;
        ctx.globalAlpha = it.a;
        ctx.drawImage(dibujos[it.c], it.x - s, it.y - s, s * 2, s * 2);
      }
      ctx.globalAlpha = 1;

      if (fin > 0) {
        ctx.save();
        ctx.translate(cx, cy);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(35, 83, 214, ' + 0.35 * fin + ')';
        ctx.beginPath(); ctx.ellipse(0, 0, R * 1.6, R * 0.52, -0.5 + t * 0.05, 0, Math.PI * 2); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(0, 0, R * 1.38, R * 0.44, 0.9 - t * 0.04, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
        var centro = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 0.5);
        centro.addColorStop(0, 'rgba(255, 255, 255, ' + 0.95 * fin + ')');
        centro.addColorStop(0.5, 'rgba(255, 184, 148, ' + 0.4 * fin + ')');
        centro.addColorStop(1, 'rgba(255, 184, 148, 0)');
        ctx.fillStyle = centro;
        ctx.fillRect(cx - R, cy - R, R * 2, R * 2);
      }
    }

    var dicha = -1;
    function ubicar(p) {
      var fusion = smooth(0.5, 0.82, p);
      for (var i = 0; i < sistemas.length; i++) {
        // No entran todos de golpe: primero el de abajo, después los costados
        var entrada = smooth(0.02 + ESPERA[i], 0.24 + ESPERA[i], p);
        var casa = anillo[i] || [cx, cy];
        var fuera = entradas[i] || casa;
        var el = sistemas[i];
        puestos[i] = [lerp(fuera[0], casa[0], entrada), lerp(fuera[1], casa[1], entrada)];
        el.style.setProperty('--x', lerp(puestos[i][0], cx, fusion).toFixed(1) + 'px');
        el.style.setProperty('--y', lerp(puestos[i][1], cy, fusion).toFixed(1) + 'px');
        el.style.setProperty('--s', (lerp(0.82, 1, entrada) * lerp(1, 0.3, fusion)).toFixed(3));
        el.style.setProperty('--o', (entrada * (1 - fusion)).toFixed(3));
      }

      // Dos frases: la de los sistemas sueltos y la del modelo único
      var a0 = smooth(0.14, 0.26, p) * (1 - smooth(0.42, 0.5, p));
      var a1 = smooth(0.8, 0.92, p);
      var cual = a1 >= a0 ? 1 : 0;
      if (cual !== dicha) { dicha = cual; linea.textContent = leyendas[cual][1]; }
      var o = Math.max(a0, a1);
      linea.style.setProperty('--o', o.toFixed(3));
      linea.style.setProperty('--y', (14 * (1 - o)).toFixed(1) + 'px');
    }

    function avance() {
      var rect = track.getBoundingClientRect();
      var total = track.offsetHeight - pin.offsetHeight;
      return total > 0 ? clamp(-rect.top / total, 0, 1) : 0;
    }

    if (!motion) {
      medir();
      dibujar(1, 2);
      window.addEventListener('resize', function () { medir(); dibujar(1, 2); });
      return;
    }

    var tiempo = 0, ultimo = 0, visible = false, girando = false;
    function cuadro(ts) {
      if (!visible) { girando = false; return; }
      tiempo += ultimo ? Math.min(0.05, (ts - ultimo) / 1000) : 0;
      ultimo = ts;
      var p = avance();
      ubicar(p);
      dibujar(p, tiempo);
      window.requestAnimationFrame(cuadro);
    }
    function arrancar() {
      if (girando) return;
      girando = true;
      ultimo = 0;
      window.requestAnimationFrame(cuadro);
    }

    window.addEventListener('resize', function () { medir(); ubicar(avance()); });
    medir();
    ubicar(avance());
    dibujar(avance(), 0);

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries.some(function (e) { return e.isIntersecting; });
        if (visible) arrancar();
      }, { threshold: 0 }).observe(track);
    } else {
      visible = true;
      arrancar();
    }

    // La primera respuesta se escribe sola, una sola vez, si nadie tocó nada antes
    setTimeout(function () { if (!tocado) correr(0); }, 700);
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
    // Dónde queda cada nube de verdad: lo calcula size(), que baja las de arriba lo
    // necesario para que su rótulo no se meta debajo del encabezado.
    var puestos = centers;
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

      // La etapa es pegajosa desde arriba y el encabezado flota encima, así que la
      // primera franja de la escena queda tapada. El rótulo de cada nube se dibuja a
      // M * 0.15 por encima de su centro: las nubes de arriba tienen que bajar lo
      // suficiente para que ese rótulo caiga debajo del encabezado, y no al revés.
      // El +26 es el aire que queda bajo el encabezado más la altura de las mayúsculas:
      // lo que se calcula acá es la línea de base del rótulo, no su borde de arriba.
      var tapa = (parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 0) + 26;
      var yMin = H ? (tapa + M * 0.15 + 4) / H : 0;
      puestos = centers.map(function (c) { return [c[0], Math.max(c[1], yMin)]; });
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
          ctx.fillText(labels[k].toUpperCase(), puestos[k][0] * W, puestos[k][1] * H - M * 0.15 - 4);
        }
      }
      var items = [], rr = M * 0.14;
      for (var i = 0; i < pts.length; i++) {
        var q = pts[i];
        var v = rotate(q.v, ry, rx);
        var pr = 1 / (1 - v[2] * 0.32);
        var tx = cx + v[0] * R * pr, ty = cy + v[1] * R * pr;
        var sx = puestos[q.c][0] * W + q.ox * M + Math.sin(t * q.sp + q.ph) * jit;
        var sy = puestos[q.c][1] * H + q.oy * M + Math.cos(t * q.sp * 0.8 + q.ph) * jit;
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
