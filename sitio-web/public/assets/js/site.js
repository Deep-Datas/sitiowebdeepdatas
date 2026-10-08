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
      label.textContent = toggle.getAttribute(open ? 'data-label-close' : 'data-label-open');
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

  /* ---------- Inicio: la oficina, los sistemas y una sola respuesta ----------
     Solo con html.motion (src/assets/js/motion.js). La escena (tamaño de la foto y esquinas de los
     monitores) viene de data-scene (src/hero.html). El scroll acerca la cámara al monitor de la
     foto, los dos monitores quedan de frente y se funden en uno solo con el asistente. */
  var heroScene = document.querySelector('[data-hero-scene]');
  if (heroScene && document.documentElement.classList.contains('motion')) {
    (function (hero) {
      var cfg = JSON.parse(hero.getAttribute('data-scene'));
      var IMG_W = cfg.w;
      var IMG_H = cfg.h;
      var all = function (sel) { return Array.prototype.slice.call(hero.querySelectorAll(sel)); };
      var track = hero.querySelector('.hp-track');
      var stage = hero.querySelector('.hp-stage');
      var photo = hero.querySelector('.hp-photo');
      var copy = hero.querySelector('.hp-copy');
      var bar = hero.querySelector('.hp-bar');
      var actions = hero.querySelector('.hp-actions');
      var mons = { a: hero.querySelector('.hp-mon-a'), b: hero.querySelector('.hp-mon-b'), c: hero.querySelector('.hp-mon-c') };
      var statuses = all('.hp-status span');
      var steps = all('.hp-step');
      var view = {};
      var ticking = false;

      function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
      function lerp(a, b, t) { return a + (b - a) * t; }
      function ramp(a, b, v) { return clamp((v - a) / (b - a), 0, 1); }
      function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

      function bounds(points) {
        var xs = points.map(function (q) { return q[0]; });
        var ys = points.map(function (q) { return q[1]; });
        var b = { x: Math.min.apply(null, xs), y: Math.min.apply(null, ys) };
        b.w = Math.max.apply(null, xs) - b.x;
        b.h = Math.max.apply(null, ys) - b.y;
        b.cx = b.x + b.w / 2;
        b.cy = b.y + b.h / 2;
        return b;
      }

      // Cuadrilátero con un margen alrededor (el marco de un monitor a partir de su pantalla)
      function grow(quad, m) {
        var c = bounds(quad);
        return quad.map(function (q) {
          var dx = q[0] - c.cx, dy = q[1] - c.cy;
          var d = Math.sqrt(dx * dx + dy * dy) || 1;
          return [q[0] + dx / d * m, q[1] + dy / d * m];
        });
      }

      var QUAD_A = cfg.screen;                 // pantalla del monitor de la mujer (arriba-izq., arriba-der., abajo-der., abajo-izq.)
      var SCREEN = bounds(QUAD_A);
      var MON_A = cfg.monitor;                 // su marco
      var MONITOR = bounds(MON_A);
      var MON_B = grow(cfg.screen2, Math.max(bounds(cfg.screen2).w, bounds(cfg.screen2).h) * 0.045);  // el monitor del compañero

      function rect(x, y, w, h) { return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]; }

      // Rectángulo apenas en perspectiva, con el lado interior (hacia el centro) más alto: los dos
      // monitores parecen mirarse. side: -1 para el de la izquierda, 1 para el de la derecha
      function tilted(x, y, w, h, side) {
        var dy = h * 0.085, dx = w * 0.045;
        return side < 0
          ? [[x + dx, y + dy], [x + w, y], [x + w, y + h], [x + dx, y + h - dy]]
          : [[x, y], [x + w - dx, y + dy], [x + w - dx, y + h - dy], [x, y + h]];
      }

      function mix(q1, q2, t) {
        return q1.map(function (q, i) { return [lerp(q[0], q2[i][0], t), lerp(q[1], q2[i][1], t)]; });
      }

      function scaled(quad, k) {
        var c = bounds(quad);
        return quad.map(function (q) { return [c.cx + (q[0] - c.cx) * k, c.cy + (q[1] - c.cy) * k]; });
      }

      function warp(c, box) {
        // Transformación proyectiva que lleva la caja (box) a las cuatro esquinas c
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
        var m = [a / box.w, d / box.w, 0, g / box.w, b / box.h, e / box.h, 0, h / box.h, 0, 0, 1, 0, x0, y0, 0, 1];
        return 'matrix3d(' + m.map(function (v) { return +v.toFixed(8); }).join(',') + ')';
      }

      function fit(pos, s, center, size, length) {
        // Corre el punto donde va el centro de la pantalla para que la foto cubra la vista en ese eje
        var lo = length - s * (size - center);
        var hi = s * center;
        return lo > hi ? (lo + hi) / 2 : clamp(pos, lo, hi);
      }

      function size(el, box) {
        el.style.width = box.w + 'px';
        el.style.height = box.h + 'px';
      }

      function measure() {
        var w = stage.clientWidth;
        var h = stage.clientHeight;
        var desk = w >= 1024;
        var shot = desk ? cfg.desk : cfg.mob;
        var header = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 64;
        // Espacio libre entre la barra de arriba y los botones de abajo
        var top = header + bar.offsetHeight + 24;
        var bottom = h - actions.offsetHeight - (desk ? 64 : 48);
        var room = Math.max(bottom - top, 200);

        // Plano general: la foto cubre la vista (escritorio) o asoma debajo del texto (celulares)
        var s0 = shot.width ? (w * shot.width) / IMG_W : Math.max(w / IMG_W, h / IMG_H) * shot.zoom;
        var start = { x: w * shot.x, y: h * shot.y };
        if (!shot.width) {
          start.x = fit(start.x, s0, SCREEN.cx, IMG_W, w);
          start.y = fit(start.y, s0, SCREEN.cy, IMG_H, h);
        }
        // Fin del acercamiento: el monitor de la mujer, con su marco, ocupa buena parte del espacio libre
        var s1 = Math.min((w * shot.fill) / MONITOR.w, (room * shot.fill) / MONITOR.h);
        var end = {
          x: w * shot.aim[0] + s1 * (SCREEN.cx - MONITOR.cx),
          y: top + room * shot.aim[1] + s1 * (SCREEN.cy - MONITOR.cy)
        };
        end.x = fit(end.x, s1, SCREEN.cx, IMG_W, w);
        end.y = fit(end.y, s1, SCREEN.cy, IMG_H, h);

        // Los dos monitores de frente: lado a lado en escritorio, uno sobre otro en celulares
        var gap = desk ? 28 : 14;
        var sw, sh, rectA, rectB;
        if (desk) {
          sw = Math.min(w * 0.42, 640, (room - 40) * 16 / 10);
          sh = sw * 10 / 16;
          var sy = top + (room - sh) / 2;
          rectB = tilted(w / 2 - gap / 2 - sw, sy, sw, sh, -1);
          rectA = tilted(w / 2 + gap / 2, sy, sw, sh, 1);
        } else {
          sw = Math.min(w * 0.88, 560, ((room - gap) / 2) * 16 / 10);
          sh = sw * 10 / 16;
          var y0 = top + (room - 2 * sh - gap) / 2;
          rectB = rect(w / 2 - sw / 2, y0, sw, sh);
          rectA = rect(w / 2 - sw / 2, y0 + sh + gap, sw, sh);
        }
        // El monitor final, con el asistente
        var devH = room * 0.96;
        var devW = desk ? Math.min(w * 0.86, devH * 16 / 10) : w * 0.92;
        if (desk) devH = Math.min(devH, devW * 10 / 16); else devH = Math.min(devH, devW * 1.5);
        if (desk && devH < 440) { devH = Math.min(room * 0.96, 440); devW = Math.min(w * 0.86, devH * 16 / 9); }
        var fin = rect((w - devW) / 2, top + (room - devH) / 2, devW, devH);

        var sideBox = { w: Math.round(sw), h: Math.round(sh) };
        var finBox = { w: Math.round(devW), h: Math.round(devH) };
        size(mons.a, sideBox);
        size(mons.b, sideBox);
        size(mons.c, finBox);
        size(photo, { w: IMG_W, h: IMG_H });
        view = { w: w, h: h, s0: s0, s1: s1, start: start, end: end, rectA: rectA, rectB: rectB, fin: fin, sideBox: sideBox, finBox: finBox };
      }

      function show(el, opacity) {
        el.style.opacity = opacity.toFixed(3);
        el.style.visibility = opacity > 0.01 ? '' : 'hidden';
      }

      function render() {
        ticking = false;
        var r = track.getBoundingClientRect();
        var total = track.offsetHeight - stage.offsetHeight;
        var p = total > 0 ? clamp(-r.top / total, 0, 1) : 1;

        // El texto se va y aparece la barra compacta con la pregunta y los pasos
        var out = ramp(0.005, 0.06, p);
        stage.style.setProperty('--cop', (1 - out).toFixed(3));
        stage.style.setProperty('--cty', (-40 * out).toFixed(1) + 'px');
        copy.classList.toggle('is-out', out >= 1);
        stage.style.setProperty('--bar', ramp(0.05, 0.1, p).toFixed(3));
        stage.style.setProperty('--shade', (1 - ramp(0.04, 0.22, p)).toFixed(3));
        stage.style.setProperty('--hop', (1 - ramp(0.005, 0.05, p)).toFixed(3));

        // 1. Acercamiento al monitor de la mujer
        var t = ease(ramp(0.04, 0.36, p));
        var s = view.s0 * Math.pow(view.s1 / view.s0, t);
        var ax = lerp(view.start.x, view.end.x, t);
        var ay = lerp(view.start.y, view.end.y, t);
        photo.style.transform = 'translate3d(' + (ax - s * SCREEN.cx).toFixed(2) + 'px,' + (ay - s * SCREEN.cy).toFixed(2) + 'px,0) scale(' + s.toFixed(5) + ')';
        function onPhoto(quad) {
          return quad.map(function (q) { return [ax + s * (q[0] - SCREEN.cx), ay + s * (q[1] - SCREEN.cy)]; });
        }

        // 2. Los dos monitores se despegan de la foto y quedan de frente; la oficina se desvanece
        var u = ease(ramp(0.34, 0.52, p));
        stage.style.setProperty('--veil', (0.94 * u).toFixed(3));
        var quadA = mix(onPhoto(MON_A), view.rectA, u);
        var quadB = mix(onPhoto(MON_B), view.rectB, u);

        // 3. Se funden en uno solo, con el asistente
        var v = ease(ramp(0.58, 0.8, p));
        var meet = scaled(view.fin, 0.72);
        quadA = mix(quadA, meet, v);
        quadB = mix(quadB, meet, v);
        mons.a.style.transform = warp(quadA, view.sideBox);
        mons.b.style.transform = warp(quadB, view.sideBox);
        var gone = 1 - ramp(0.35, 0.8, v);
        show(mons.a, gone);
        // El monitor del compañero aparece sobre la foto cuando empieza el recorrido (antes se ve su planilla)
        show(mons.b, gone * ramp(0.03, 0.14, p));
        mons.c.style.transform = warp(scaled(view.fin, 0.9 + 0.1 * v), view.finBox);
        show(mons.c, ramp(0.4, 0.85, v));
        stage.style.setProperty('--flash', (0.85 * Math.sin(Math.PI * ramp(0.25, 0.9, v))).toFixed(3));

        var froms = statuses.map(function (el) { return parseFloat(el.getAttribute('data-from')); });
        statuses.forEach(function (el, i) {
          var on = p >= froms[i] && (i === statuses.length - 1 || p < froms[i + 1] || froms[i + 1] === froms[i]);
          el.classList.toggle('is-on', on);
        });
        var stepFroms = steps.map(function (el) { return parseFloat(el.getAttribute('data-from')); });
        steps.forEach(function (el, i) {
          var on = p >= stepFroms[i] && (i === steps.length - 1 || p < stepFroms[i + 1] || stepFroms[i + 1] === stepFroms[i]);
          el.classList.toggle('is-on', on);
          el.classList.toggle('is-done', !on && p >= stepFroms[i]);
        });
        hero.classList.toggle('is-done', p > 0.92);
        document.body.classList.toggle('hero-copy-visible', p < 0.06);
      }

      function onScroll() {
        if (!ticking) {
          ticking = true;
          window.requestAnimationFrame(render);
        }
      }

      hero.classList.add('is-animated');
      measure();
      render();
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', function () { measure(); render(); });
      // Si la barra cambia de altura al cargar las tipografías, se vuelve a medir
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measure(); render(); });
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

  /* ---------- Formularios de contacto ---------- */
  var english = document.documentElement.lang === 'en';
  var formText = english ? {
    sending: 'Sending…',
    required: 'Please fill in the required fields.',
    email: 'Please enter a valid email address.',
    sent: 'Thank you! We received your message and will get back to you shortly.',
    failed: 'We couldn’t send your message. Please email us at fbloise@deepdatas.com.',
    offline: 'We couldn’t send your message. Please check your connection and try again.'
  } : {
    sending: 'Enviando…',
    required: 'Completá los campos obligatorios.',
    email: 'Ingresá un email válido.',
    sent: '¡Gracias! Recibimos tu mensaje y te responderemos a la brevedad.',
    failed: 'No pudimos enviar tu mensaje. Escribinos a fbloise@deepdatas.com.',
    offline: 'No pudimos enviar tu mensaje. Revisá tu conexión e intentá nuevamente.'
  };

  var setupForm = function (form) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var buttonHtml = button.innerHTML;
    var fields = form.querySelectorAll('input:not([name="website"]), select, textarea');

    // Validamos con mensajes propios en español.
    form.setAttribute('novalidate', '');

    // Preselecciona el interés cuando se llega desde un botón (por ejemplo, ?interes=ia)
    var wanted = new URLSearchParams(window.location.search).get('interes');
    var select = form.querySelector('select#interest');
    if (wanted && select && !select.value) {
      var option = select.querySelector('option[data-key="' + wanted.replace(/[^a-z]/g, '') + '"]');
      if (option) option.selected = true;
    }

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
        showStatus('error', onlyEmail ? formText.email : formText.required);
        invalid[0].focus();
        return;
      }

      button.disabled = true;
      button.textContent = formText.sending;
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
              detail: { interest: form.elements.interest ? form.elements.interest.value : '' }
            }));
            form.reset();
            showStatus('ok', formText.sent);
          } else {
            showStatus('error', data.error || formText.failed);
          }
        })
        .catch(function () {
          showStatus('error', formText.offline);
        })
        .finally(function () {
          button.disabled = false;
          button.innerHTML = buttonHtml;
        });
    });
  };
  if (window.fetch) document.querySelectorAll('.contact-form').forEach(setupForm);

  /* ---------- Autoevaluación de datos ---------- */
  var quiz = document.querySelector('[data-quiz]');
  var quizResult = document.querySelector('[data-quiz-result]');
  if (quiz && quizResult) {
    var groups = Array.prototype.slice.call(quiz.querySelectorAll('[data-dimension]'));
    var progress = quiz.querySelector('[data-quiz-progress]');
    var progressText = progress.textContent;
    var quizError = quiz.querySelector('[data-quiz-error]');
    var levels = Array.prototype.slice.call(quizResult.querySelectorAll('[data-level-from]'));
    var tips = quizResult.querySelector('.quiz-tips');
    var allGood = quizResult.querySelector('[data-quiz-all-good]');
    var leadMessage = quizResult.querySelector('[data-lead-message]');

    var choice = function (group) { return group.querySelector('input:checked'); };
    var answered = function () { return groups.filter(choice).length; };

    quiz.addEventListener('change', function (event) {
      var group = event.target.closest('[data-dimension]');
      if (group) group.classList.add('is-answered');
      progress.textContent = progressText.replace(/^\d+/, answered());
      if (answered() === groups.length) quizError.hidden = true;
    });

    quiz.addEventListener('submit', function (event) {
      event.preventDefault();
      var missing = groups.filter(function (group) { return !choice(group); });
      if (missing.length) {
        quizError.hidden = false;
        missing[0].querySelector('input').focus();
        return;
      }
      // Cada respuesta vale de 0 a 3; el resultado va de 0 a 100
      var scores = groups.map(function (group) { return Number(choice(group).value); });
      var total = scores.reduce(function (a, b) { return a + b; }, 0);
      var score = Math.round(total / (3 * groups.length) * 100);
      var level = levels.filter(function (el) {
        return score >= Number(el.getAttribute('data-level-from')) && score <= Number(el.getAttribute('data-level-to'));
      })[0];
      levels.forEach(function (el) { el.hidden = el !== level; });
      quizResult.querySelector('[data-quiz-score]').textContent = score;
      quizResult.querySelector('[data-quiz-meter]').style.width = score + '%';

      // Prioridades: las áreas con menos puntaje (0 o 1); si no hay, las que tienen 2
      var limit = scores.some(function (s) { return s <= 1; }) ? 1 : 2;
      var order = groups.map(function (group, i) { return { id: group.getAttribute('data-dimension'), score: scores[i] }; })
        .sort(function (a, b) { return a.score - b.score; });
      tips.querySelectorAll('[data-tip]').forEach(function (tip) { tip.hidden = true; });
      order.forEach(function (item) {
        var tip = tips.querySelector('[data-tip="' + item.id + '"]');
        tip.hidden = item.score > limit;
        tips.appendChild(tip);
      });
      var anyTip = order.some(function (item) { return item.score <= limit; });
      tips.hidden = !anyTip;
      allGood.hidden = anyTip;

      // Resumen que recibe el equipo si la persona deja sus datos
      if (leadMessage) {
        var lines = [quizResult.getAttribute('data-summary').replace('{score}', score).replace('{level}', level.querySelector('h2').textContent), ''];
        groups.forEach(function (group) {
          lines.push(group.querySelector('.quiz-q-title').textContent.trim());
          lines.push('→ ' + choice(group).parentNode.textContent.trim());
        });
        leadMessage.value = lines.join('\n');
      }

      quiz.hidden = true;
      quizResult.hidden = false;
      quizResult.focus();
      quizResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    quizResult.querySelector('[data-quiz-print]').addEventListener('click', function () { window.print(); });
    quizResult.querySelector('[data-quiz-reset]').addEventListener('click', function () {
      quiz.reset();
      groups.forEach(function (group) { group.classList.remove('is-answered'); });
      progress.textContent = progressText;
      quizResult.hidden = true;
      quiz.hidden = false;
      quiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
      groups[0].querySelector('input').focus({ preventScroll: true });
    });
  }

  /* ---------- Botón flotante de WhatsApp (celulares) ---------- */
  var waFloat = document.querySelector('[data-wa-float]');
  if (waFloat) {
    var heroBlock = document.querySelector('[data-hero-scene]');
    var covered = 0;
    var updateWa = function () {
      // Aparece después del inicio (o de la primera pantalla) y no donde ya hay un botón de WhatsApp
      var start = heroBlock ? heroBlock.offsetTop + heroBlock.offsetHeight - window.innerHeight * 0.5 : window.innerHeight * 0.6;
      waFloat.classList.toggle('is-visible', window.scrollY > start && covered === 0);
    };
    if ('IntersectionObserver' in window) {
      var zones = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var was = entry.target.getAttribute('data-wa-zone') === 'in';
          if (entry.isIntersecting !== was) {
            covered += entry.isIntersecting ? 1 : -1;
            entry.target.setAttribute('data-wa-zone', entry.isIntersecting ? 'in' : 'out');
          }
        });
        updateWa();
      });
      document.querySelectorAll('.finale, .cta-band, .site-footer').forEach(function (zone) { zones.observe(zone); });
    }
    window.addEventListener('scroll', updateWa, { passive: true });
    window.addEventListener('resize', updateWa);
    updateWa();
  }

  /* ---------- Movimiento al hacer scroll (estilo apple.com) ----------
     Solo con html.motion (src/assets/js/motion.js): sin JavaScript o con «reducir movimiento»
     todo se ve desde el principio y nada se anima. */
  var root = document.documentElement;
  if (root.classList.contains('motion')) {
    var clampM = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

    // Separa un título en palabras (conservando énfasis y enlaces) para que entren una por una
    var splitWords = function (el, cls) {
      var count = 0;
      (function walk(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (child) {
          if (child.nodeType === 3) {
            var parts = child.textContent.split(/([ \t\n\r]+)/);
            if (parts.length < 2 && !parts[0]) return;
            var frag = document.createDocumentFragment();
            parts.forEach(function (part) {
              if (!part) return;
              if (/^[ \t\n\r]+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
              var span = document.createElement('span');
              span.className = cls;
              span.textContent = part;
              span.style.setProperty('--i', count++);
              frag.appendChild(span);
            });
            node.replaceChild(frag, child);
          } else if (child.nodeType === 1) {
            walk(child);
          }
        });
      })(el);
      return count;
    };

    // Encabezado de las páginas interiores: entra al cargar, en cascada
    document.querySelectorAll('.page-hero .container > *').forEach(function (el) { el.classList.add('reveal'); });

    // Títulos: palabra por palabra, desde un leve desenfoque
    document.querySelectorAll('.reveal h1, .reveal h2, h1.reveal, h2.reveal').forEach(function (heading) {
      if (heading.hasAttribute('data-scroll-lit') || heading.closest('.hp')) return;
      heading.classList.add('words');
      splitWords(heading, 'w');
      var box = heading.closest('.reveal');
      if (box) box.classList.add('has-split');
    });

    // Aparición en cascada: los elementos hermanos entran uno detrás de otro
    var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
    reveals.forEach(function (el) {
      var siblings = Array.prototype.filter.call(el.parentNode.children, function (c) { return c.classList.contains('reveal'); });
      var index = siblings.indexOf(el);
      if (index > 0) el.style.setProperty('--reveal-delay', Math.min(index, 6) * 90 + 'ms');
    });
    var showNow = function (el) { el.classList.add('is-in'); };
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          showNow(entry.target);
          revealer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) {
      // Lo que ya quedó arriba (por ejemplo, al entrar con un enlace a una sección) se muestra sin animar
      if (el.getBoundingClientRect().bottom < 0) { el.classList.add('is-in', 'no-anim'); return; }
      revealer.observe(el);
    });

    // Frases que se iluminan palabra por palabra a medida que se avanza
    var lit = Array.prototype.slice.call(document.querySelectorAll('[data-scroll-lit]')).map(function (el) {
      splitWords(el, 'sw');
      return { el: el, words: Array.prototype.slice.call(el.querySelectorAll('.sw')), shown: -1 };
    });
    var paintLit = function () {
      var vh = window.innerHeight;
      lit.forEach(function (item) {
        var r = item.el.getBoundingClientRect();
        if (r.bottom < -vh || r.top > vh * 2) return;
        // Empieza cuando el texto entra por abajo y termina cuando llega a la mitad de la pantalla
        var p = clampM((vh * 0.88 - r.top) / (vh * 0.88 - vh * 0.42 + r.height * 0.6), 0, 1);
        var count = Math.round(p * item.words.length);
        if (count === item.shown) return;
        item.shown = count;
        item.words.forEach(function (w, i) { w.classList.toggle('is-lit', i < count); });
      });
    };

    // Cifras que cuentan desde cero al aparecer
    var counter = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        counter.unobserve(entry.target);
        var node = entry.target.firstChild;
        var match = node && node.nodeType === 3 && node.textContent.match(/^(\D*)(\d+)(\D*)$/);
        if (!match) return;
        var target = parseInt(match[2], 10);
        var started = null;
        var step = function (now) {
          if (started === null) started = now;
          var t = clampM((now - started) / 1400, 0, 1);
          var eased = 1 - Math.pow(1 - t, 4);
          node.textContent = match[1] + Math.round(target * eased) + match[3];
          if (t < 1) window.requestAnimationFrame(step);
        };
        node.textContent = match[1] + '0' + match[3];
        window.requestAnimationFrame(step);
      });
    }, { threshold: 0.6 });
    document.querySelectorAll('.stats dd, .case-card-number').forEach(function (el) { counter.observe(el); });

    var motionTicking = false;
    var onScrollMotion = function () {
      if (motionTicking) return;
      motionTicking = true;
      window.requestAnimationFrame(function () { motionTicking = false; paintLit(); });
    };
    if (lit.length) {
      window.addEventListener('scroll', onScrollMotion, { passive: true });
      window.addEventListener('resize', onScrollMotion);
      onScrollMotion();
    }
    root.classList.add('motion-ready');
  }

  /* ---------- Año actual en el pie ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
