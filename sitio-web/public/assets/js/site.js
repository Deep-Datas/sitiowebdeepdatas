/**
 * DeepDatas - comportamiento del sitio
 * El sitio funciona sin JavaScript; este archivo agrega mejoras progresivas.
 */
(function () {
  'use strict';

  /* ---------- Encabezado con sombra al hacer scroll ---------- */
  var header = document.getElementById('header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Menú móvil ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('menu');
  if (toggle && menu) {
    var label = toggle.querySelector('.visually-hidden');
    var setMenu = function (open) {
      menu.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      label.textContent = open ? 'Cerrar menú' : 'Abrir menú';
      document.body.style.overflow = open ? 'hidden' : '';
    };
    toggle.addEventListener('click', function () {
      setMenu(!menu.classList.contains('is-open'));
    });
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.classList.contains('is-open')) {
        setMenu(false);
        toggle.focus();
      }
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', function (event) {
      if (event.matches) setMenu(false);
    });
  }

  /* ---------- Gráfico del inicio: tooltip al pasar el mouse ---------- */
  document.querySelectorAll('[data-chart]').forEach(function (chart) {
    var svg = chart.querySelector('svg');
    var crosshair = chart.querySelector('.crosshair');
    var tooltip = chart.querySelector('.tooltip');
    var viewBox = svg.viewBox.baseVal;

    function show(rect) {
      var x = parseFloat(rect.dataset.x);
      var scale = svg.getBoundingClientRect().width / viewBox.width;
      crosshair.setAttribute('x1', x);
      crosshair.setAttribute('x2', x);
      chart.classList.add('is-hover');

      tooltip.textContent = '';
      var title = document.createElement('strong');
      title.textContent = rect.dataset.month;
      tooltip.appendChild(title);
      [['real', 'Real'], ['forecast', 'Pronóstico']].forEach(function (pair) {
        var value = rect.dataset[pair[0]];
        if (!value) return;
        var row = document.createElement('span');
        row.className = 't-' + pair[0];
        row.textContent = pair[1] + ': ' + value;
        tooltip.appendChild(row);
      });
      tooltip.hidden = false;
      var left = Math.min(Math.max(x * scale, 80), svg.getBoundingClientRect().width - 80);
      var top = parseFloat(rect.dataset.y) * scale;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
      // Si el punto está muy arriba, el tooltip se muestra debajo para no tapar los indicadores
      tooltip.classList.toggle('is-below', top < 90);
    }

    function hide() {
      chart.classList.remove('is-hover');
      tooltip.hidden = true;
    }

    chart.querySelectorAll('.hits rect').forEach(function (rect) {
      rect.addEventListener('pointerenter', function () { show(rect); });
    });
    svg.addEventListener('pointerleave', hide);
  });

  /* ---------- Tableros de ejemplo: detalle al pasar el mouse ---------- */
  document.querySelectorAll('[data-dashboard]').forEach(function (board) {
    var tip = board.querySelector('.db-tooltip');
    var current = null;

    function clearLines() {
      board.querySelectorAll('[data-line].is-hover').forEach(function (plot) {
        plot.classList.remove('is-hover');
      });
    }

    function hide() {
      current = null;
      tip.hidden = true;
      clearLines();
    }

    function show(target) {
      current = target;
      tip.textContent = '';
      var title = document.createElement('strong');
      title.textContent = target.dataset.tipTitle;
      tip.appendChild(title);
      (target.dataset.tip || '').split('|').forEach(function (text) {
        if (!text) return;
        var line = document.createElement('span');
        line.textContent = text;
        tip.appendChild(line);
      });
      tip.hidden = false;

      clearLines();
      var plot = target.closest('[data-line]');
      if (plot && target.dataset.x) {
        plot.classList.add('is-hover');
        plot.querySelector('.db-crosshair').style.left = target.dataset.x + '%';
      }
    }

    function place(event) {
      var box = board.getBoundingClientRect();
      var half = tip.offsetWidth / 2;
      var x = Math.min(Math.max(event.clientX - box.left, half + 8), box.width - half - 8);
      var y = event.clientY - box.top;
      tip.style.left = x + 'px';
      tip.style.top = y + 'px';
      tip.classList.toggle('is-below', y < tip.offsetHeight + 24);
    }

    function onPointer(event) {
      var target = event.target.closest('[data-tip-title]');
      if (!target) {
        if (current) hide();
        return;
      }
      if (target !== current) show(target);
      place(event);
    }

    board.addEventListener('pointermove', onPointer);
    board.addEventListener('pointerdown', onPointer);
    board.addEventListener('pointerleave', hide);
  });

  /* ---------- Hero del inicio: zoom a la pantalla con el scroll ---------- */
  var heroScene = document.querySelector('[data-hero-scene]');
  if (heroScene) {
    (function (hero) {
      // Escena del tema activo (src/hero.json): tamaño de la imagen y esquinas de la pantalla del monitor
      var cfg = JSON.parse(hero.getAttribute('data-scene'));
      var IMG_W = cfg.w;
      var IMG_H = cfg.h;
      var QUAD = cfg.screen;                 // arriba-izq., arriba-der., abajo-der., abajo-izq.
      var BOX = { w: 1440, h: 900 };         // tamaño de diseño de la ventana que va en la pantalla
      var qx = QUAD.map(function (q) { return q[0]; });
      var qy = QUAD.map(function (q) { return q[1]; });
      var SCREEN = { x: Math.min.apply(null, qx), y: Math.min.apply(null, qy) };
      SCREEN.w = Math.max.apply(null, qx) - SCREEN.x;
      SCREEN.h = Math.max.apply(null, qy) - SCREEN.y;
      var SCREEN_CENTER = { x: SCREEN.x + SCREEN.w / 2, y: SCREEN.y + SCREEN.h / 2 };
      // Filete y sombra de la ventana al final: claros sobre fondo oscuro, oscuros sobre fondo claro
      var LIGHT = document.documentElement.getAttribute('data-theme') === 'claro';
      var EDGE = LIGHT ? { rgb: '11,18,32', a: 0.1 } : { rgb: '255,255,255', a: 0.14 };
      var DROP = LIGHT ? { rgb: '11,18,32', a: 0.3 } : { rgb: '0,0,0', a: 0.8 };

      var stage = hero.querySelector('.hs-stage');
      var frame = hero.querySelector('.hs-frame');
      var scene = hero.querySelector('.hs-scene');
      var screen = hero.querySelector('.hs-screen');
      var front = hero.querySelector('.hs-front');
      var shade = hero.querySelector('.hs-shade');
      var copy = hero.querySelector('.hs-copy');
      var hint = hero.querySelector('.hs-hint');
      var app = hero.querySelector('.hs-app');
      var thread = app.querySelector('.cw-thread');
      var scroller = app.querySelector('.cw-scroll');
      var steps = Array.prototype.slice.call(app.querySelectorAll('[data-step]'));
      var motion = window.matchMedia('(prefers-reduced-motion: no-preference)');

      var view = {};
      var shown = -1;
      var ticking = false;

      function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
      function lerp(a, b, t) { return a + (b - a) * t; }
      function ramp(a, b, v) { return clamp((v - a) / (b - a), 0, 1); }
      function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

      function place(el, s, ax, ay) {
        // Ubica el centro de la pantalla del monitor en el punto (ax, ay) de la vista, con escala s
        el.style.transform = 'translate3d(' + (ax - s * SCREEN_CENTER.x).toFixed(2) + 'px,' +
          (ay - s * SCREEN_CENTER.y).toFixed(2) + 'px,0) scale(' + s.toFixed(5) + ')';
      }

      function warp(c) {
        // Transformación proyectiva que lleva la ventana (BOX) a las cuatro esquinas c
        // (cuadrado unitario a cuadrilátero, P. Heckbert), escrita como matrix3d
        var x0 = c[0][0], y0 = c[0][1], x1 = c[1][0], y1 = c[1][1];
        var x2 = c[2][0], y2 = c[2][1], x3 = c[3][0], y3 = c[3][1];
        var sx = x0 - x1 + x2 - x3;
        var sy = y0 - y1 + y2 - y3;
        var g = 0;
        var h = 0;
        if (Math.abs(sx) > 1e-9 || Math.abs(sy) > 1e-9) {
          var dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2;
          var den = dx1 * dy2 - dx2 * dy1;
          g = (sx * dy2 - dx2 * sy) / den;
          h = (dx1 * sy - sx * dy1) / den;
        }
        var a = x1 - x0 + g * x1, b = x3 - x0 + h * x3;
        var d = y1 - y0 + g * y1, e = y3 - y0 + h * y3;
        var m = [a / BOX.w, d / BOX.w, 0, g / BOX.w, b / BOX.h, e / BOX.h, 0, h / BOX.h, 0, 0, 1, 0, x0, y0, 0, 1];
        return 'matrix3d(' + m.map(function (v) { return +v.toFixed(8); }).join(',') + ')';
      }

      function sizeLayers() {
        [scene, front].forEach(function (el) {
          if (!el) return;
          el.style.width = IMG_W + 'px';
          el.style.height = IMG_H + 'px';
        });
      }

      function fitStatic() {
        frame.style.aspectRatio = IMG_W + ' / ' + IMG_H;
        sizeLayers();
        var s = frame.clientWidth / IMG_W;
        scene.style.transform = 'scale(' + s + ')';
        if (front) front.style.transform = 'scale(' + s + ')';
        screen.style.transform = warp(QUAD.map(function (q) { return [q[0] * s, q[1] * s]; }));
      }

      function fit(pos, s, center, size, length) {
        // Corre el punto donde va el centro de la pantalla para que la imagen cubra la vista en ese eje
        var lo = length - s * (size - center);
        var hi = s * center;
        return lo > hi ? (lo + hi) / 2 : clamp(pos, lo, hi);
      }

      function measure() {
        var w = stage.clientWidth;
        var h = stage.clientHeight;
        var shot = w >= 1024 ? cfg.desk : cfg.mob;
        // Plano general: según la escena, la imagen cubre la vista o la pantalla queda abajo del texto en celulares
        var s0 = shot.width ? (w * shot.width) / IMG_W : Math.max(w / IMG_W, h / IMG_H) * shot.zoom;
        var start = { x: w * shot.x, y: h * shot.y };
        if (cfg.cover) {
          start.x = fit(start.x, s0, SCREEN_CENTER.x, IMG_W, w);
          if (w >= 1024) start.y = fit(start.y, s0, SCREEN_CENTER.y, IMG_H, h);
        }
        var header = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 64;
        // Plano final: la pantalla del monitor cubre toda la vista
        var s1 = Math.max(w / SCREEN.w, h / SCREEN.h) * 1.04;
        // Donde termina la ventana al despegarse del monitor: de frente, cubriendo la vista debajo del encabezado
        var k = Math.max(w / BOX.w, (h - header) / BOX.h);
        var rw = BOX.w * k;
        var rh = BOX.h * k;
        var rx = (w - rw) / 2;
        var ry = header + (h - header - rh) / 2;
        var rect = [[rx, ry], [rx + rw, ry], [rx + rw, ry + rh], [rx, ry + rh]];
        view = { w: w, h: h, s0: s0, s1: s1, start: start, end: { x: w / 2, y: h / 2 }, rect: rect, header: header };
        sizeLayers();
      }

      function setSteps(count) {
        if (count === shown) return;
        shown = count;
        steps.forEach(function (step, i) { step.classList.toggle('is-in', i < count); });
        // La conversación se desplaza para que lo último que apareció quede a la vista
        var last = count > 0 ? steps[count - 1] : null;
        var offset = 0;
        if (last) {
          var bottom = last.offsetTop + last.offsetHeight + 24;
          var top = thread.offsetTop;
          offset = Math.max(0, bottom - top - scroller.clientHeight + 40);
        }
        thread.style.transform = 'translateY(' + (-offset) + 'px)';
      }

      function render() {
        ticking = false;
        var rect = hero.getBoundingClientRect();
        var total = hero.offsetHeight - view.h;
        var p = clamp(-rect.top / total, 0, 1);

        var t = ease(ramp(0.06, 0.46, p));
        var s = view.s0 * Math.pow(view.s1 / view.s0, t);
        var ax = lerp(view.start.x, view.end.x, t);
        var ay = lerp(view.start.y, view.end.y, t);
        place(scene, s, ax, ay);

        // La ventana sigue a la pantalla del monitor y, al acercarse, se despega hasta quedar de frente
        var u = ease(ramp(0.55, 1, t));
        screen.style.transform = warp(QUAD.map(function (q, i) {
          var x = ax + s * (q[0] - SCREEN_CENTER.x);
          var y = ay + s * (q[1] - SCREEN_CENTER.y);
          return [lerp(x, view.rect[i][0], u), lerp(y, view.rect[i][1], u)];
        }));
        screen.style.boxShadow = u > 0 ? '0 40px 90px -30px rgba(' + DROP.rgb + ',' + (DROP.a * u).toFixed(3) + ')' : '';

        if (front) {
          // La persona está más cerca de la cámara: crece más rápido, baja y se desvanece
          var sf = s * (1 + 1.8 * t * t);
          place(front, sf, ax, ay + t * view.h * 0.55);
          front.style.opacity = (1 - ramp(0.2, 0.62, t)).toFixed(3);
        }

        var out = ramp(0.005, 0.06, p);
        copy.style.opacity = (1 - out).toFixed(3);
        copy.style.transform = 'translateY(' + (-48 * out).toFixed(1) + 'px)';
        copy.style.visibility = out >= 1 ? 'hidden' : '';
        hint.style.opacity = (1 - ramp(0, 0.05, p)).toFixed(3);
        shade.style.opacity = (1 - ramp(0.04, 0.22, p)).toFixed(3);

        var appIn = ramp(0.44, 0.49, p);
        frame.style.opacity = (1 - ramp(0.47, 0.5, p)).toFixed(3);
        app.style.opacity = appIn.toFixed(3);
        app.classList.toggle('is-active', appIn > 0.5);
        hero.classList.toggle('is-app', appIn > 0.5);

        // Cierre: la ventana se encoge hasta quedar enmarcada sobre el fondo del sitio
        var settle = ease(ramp(0.88, 0.98, p));
        var side = Math.min(48, Math.max(16, view.w * 0.03)) * settle;
        app.style.top = (view.header + 16 * settle).toFixed(1) + 'px';
        app.style.left = side.toFixed(1) + 'px';
        app.style.right = side.toFixed(1) + 'px';
        app.style.bottom = (40 * settle).toFixed(1) + 'px';
        app.style.borderRadius = (20 * settle).toFixed(1) + 'px';
        app.style.boxShadow = settle > 0 ? '0 0 0 1px rgba(' + EDGE.rgb + ',' + (EDGE.a * settle).toFixed(3) + '), 0 40px 90px -40px rgba(' + DROP.rgb + ',' + (DROP.a * settle).toFixed(3) + ')' : '';
        app.style.transform = appIn < 1 ? 'scale(' + (1.04 - 0.04 * appIn).toFixed(4) + ')' : '';
        hero.classList.toggle('is-done', p > 0.88);

        document.body.classList.toggle('hero-copy-visible', p < 0.06);

        var revealed = Math.round(ramp(0.52, 0.86, p) * steps.length);
        setSteps(revealed);
      }

      function onScroll() {
        if (!ticking) {
          ticking = true;
          window.requestAnimationFrame(render);
        }
      }

      function enable() {
        hero.classList.add('hs-ready');
        if (motion.matches) {
          hero.classList.add('is-animated');
          frame.style.aspectRatio = '';
          measure();
          shown = -1;
          render();
          window.addEventListener('scroll', onScroll, { passive: true });
        } else {
          hero.classList.remove('is-animated', 'is-app', 'is-done');
          document.body.classList.remove('hero-copy-visible');
          window.removeEventListener('scroll', onScroll);
          [scene, screen, front, copy, hint, shade, frame, app, thread].forEach(function (el) { if (el) el.removeAttribute('style'); });
          steps.forEach(function (step) { step.classList.remove('is-in'); });
          fitStatic();
        }
      }

      window.addEventListener('resize', function () {
        if (hero.classList.contains('is-animated')) {
          measure();
          shown = -1;
          render();
        } else {
          fitStatic();
        }
      });
      motion.addEventListener('change', enable);
      enable();
    })(heroScene);
  }

  /* ---------- Gráfico de datos para IA: recorrido de cada elemento ---------- */
  document.querySelectorAll('[data-pipeline]').forEach(function (figure) {
    var svg = figure.querySelector('.pl-svg');
    var detail = figure.querySelector('.pl-detail');
    var parts = {
      stage: detail.querySelector('.pl-detail-stage'),
      title: detail.querySelector('.pl-detail-title'),
      text: detail.querySelector('.pl-detail-text')
    };
    var initial = {
      stage: parts.stage.textContent,
      title: parts.title.textContent,
      text: parts.text.textContent
    };
    var current = null;

    function clear() {
      svg.querySelectorAll('.is-on, .is-current').forEach(function (el) {
        el.classList.remove('is-on', 'is-current');
      });
    }

    function activate(node) {
      if (node === current) return;
      current = node;
      clear();
      svg.classList.add('is-focus');
      node.classList.add('is-current');
      node.dataset.chain.split(' ').forEach(function (id) {
        var el = svg.querySelector('[data-pl="' + id + '"]');
        if (el) el.classList.add('is-on');
      });
      parts.stage.textContent = node.dataset.stage;
      parts.title.textContent = node.dataset.title;
      parts.text.textContent = node.dataset.text;
    }

    function reset() {
      current = null;
      clear();
      svg.classList.remove('is-focus');
      parts.stage.textContent = initial.stage;
      parts.title.textContent = initial.title;
      parts.text.textContent = initial.text;
    }

    svg.querySelectorAll('.pl-node').forEach(function (node) {
      node.addEventListener('pointerenter', function () { activate(node); });
      node.addEventListener('focus', function () { activate(node); });
      node.addEventListener('click', function () { activate(node); });
    });
    svg.addEventListener('pointerleave', function () {
      if (!svg.contains(document.activeElement)) reset();
    });
    svg.addEventListener('focusout', function (event) {
      if (!svg.contains(event.relatedTarget)) reset();
    });
  });

  /* ---------- Formulario de contacto ---------- */
  var form = document.querySelector('.contact-form');
  if (form && window.fetch) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var buttonHtml = button.innerHTML;
    var fields = form.querySelectorAll('input:not([name="website"]), select, textarea');

    // Validamos con mensajes propios en español.
    form.setAttribute('novalidate', '');

    // Preselecciona el interés cuando se llega desde un botón (por ejemplo, ?interes=ia)
    var interestMap = {
      diagnostico: 'Diagnóstico de datos',
      ia: 'Inteligencia artificial',
      tableros: 'Tableros de gestión',
      ingenieria: 'Ingeniería de datos',
      calidad: 'Calidad y preparación de datos',
      analitica: 'Analítica y modelos predictivos'
    };
    var wanted = interestMap[new URLSearchParams(window.location.search).get('interes')];
    var select = form.querySelector('#interest');
    if (wanted && select && !select.value) select.value = wanted;

    var showStatus = function (type, message) {
      status.textContent = '';
      var box = document.createElement('div');
      box.className = type;
      var text = document.createElement('span');
      text.textContent = message;
      box.appendChild(text);
      status.appendChild(box);
    };

    fields.forEach(function (field) {
      field.addEventListener('input', function () {
        field.classList.remove('is-invalid');
        field.removeAttribute('aria-invalid');
      });
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var invalid = Array.prototype.filter.call(fields, function (field) {
        return !field.checkValidity();
      });
      invalid.forEach(function (field) {
        field.classList.add('is-invalid');
        field.setAttribute('aria-invalid', 'true');
      });
      if (invalid.length) {
        var email = form.querySelector('#email');
        var onlyEmail = invalid.length === 1 && invalid[0] === email && email.value.trim();
        showStatus('error', onlyEmail ? 'Ingresá un email válido.' : 'Completá los campos obligatorios.');
        invalid[0].focus();
        return;
      }

      button.disabled = true;
      button.textContent = 'Enviando…';
      status.textContent = '';

      fetch(form.action, {
        method: 'POST',
        body: new URLSearchParams(new FormData(form)),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (response) {
          return response.json().catch(function () { return { ok: false }; });
        })
        .then(function (data) {
          if (data.ok) {
            document.dispatchEvent(new CustomEvent('deepdatas:form-sent', {
              detail: { interest: form.querySelector('#interest').value }
            }));
            form.reset();
            showStatus('ok', '¡Gracias! Recibimos tu mensaje y te responderemos a la brevedad.');
          } else {
            showStatus('error', data.error || 'No pudimos enviar tu mensaje. Escribinos a fbloise@deepdatas.com.');
          }
        })
        .catch(function () {
          showStatus('error', 'No pudimos enviar tu mensaje. Revisá tu conexión e intentá nuevamente.');
        })
        .finally(function () {
          button.disabled = false;
          button.innerHTML = buttonHtml;
        });
    });
  }

  /* ---------- Año actual en el pie ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
