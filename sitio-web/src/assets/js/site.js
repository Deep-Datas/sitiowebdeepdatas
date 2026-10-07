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

  /* ---------- Hero del inicio: zoom al monitor con el scroll ---------- */
  var heroScene = document.querySelector('[data-hero-scene]');
  if (heroScene) {
    (function (hero) {
      // Escena del tema activo (src/hero.json): tamaño de la imagen y esquinas de la pantalla y del monitor
      var cfg = JSON.parse(hero.getAttribute('data-scene'));
      var IMG_W = cfg.w;
      var IMG_H = cfg.h;
      var QUAD = cfg.screen;                 // arriba-izq., arriba-der., abajo-der., abajo-izq.
      var BOX = { w: 600, h: 585 };          // tamaño de la ventana en la pantalla sin animación (como en tools/render_pantalla.cjs)

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

      var SCREEN = bounds(QUAD);
      // El monitor con su marco (si la escena no lo define, la pantalla con un margen)
      var margin = Math.max(SCREEN.w, SCREEN.h) * 0.04;
      var MONITOR = bounds(cfg.monitor || [[SCREEN.x - margin, SCREEN.y - margin], [SCREEN.x + SCREEN.w + margin, SCREEN.y + SCREEN.h + margin]]);

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
      // El comienzo de la respuesta ya se ve en la pantalla del monitor: aparece de entrada
      var early = steps.filter(function (step) { return step.hasAttribute('data-early'); }).length;
      var motion = window.matchMedia('(prefers-reduced-motion: no-preference)');

      var view = {};
      var shown = -1;
      var ticking = false;

      function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
      function lerp(a, b, t) { return a + (b - a) * t; }
      function ramp(a, b, v) { return clamp((v - a) / (b - a), 0, 1); }
      function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
      function edge(a, b) { return Math.sqrt(Math.pow(a[0] - b[0], 2) + Math.pow(a[1] - b[1], 2)); }

      function place(el, s, ax, ay) {
        // Ubica el centro de la pantalla del monitor en el punto (ax, ay) de la vista, con escala s
        el.style.transform = 'translate3d(' + (ax - s * SCREEN.cx).toFixed(2) + 'px,' +
          (ay - s * SCREEN.cy).toFixed(2) + 'px,0) scale(' + s.toFixed(5) + ')';
      }

      function warp(c, box) {
        // Transformación proyectiva que lleva la ventana (box) a las cuatro esquinas c
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
        screen.style.transform = warp(QUAD.map(function (q) { return [q[0] * s, q[1] * s]; }), BOX);
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
        var header = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 64;
        // Plano general: según la escena, la imagen cubre la vista o la pantalla queda abajo del texto en celulares
        var s0 = shot.width ? (w * shot.width) / IMG_W : Math.max(w / IMG_W, h / IMG_H) * shot.zoom;
        var start = { x: w * shot.x, y: h * shot.y };
        if (cfg.cover) {
          start.x = fit(start.x, s0, SCREEN.cx, IMG_W, w);
          if (w >= 1024) start.y = fit(start.y, s0, SCREEN.cy, IMG_H, h);
        }
        // Plano final: el monitor, con su marco, ocupa cerca del 80 % de la vista debajo del encabezado.
        // Así se sigue viendo la oficina y se entiende que es una persona usando el asistente
        var room = h - header;
        var fill = shot.fill || 0.8;
        var aim = shot.end || [0.5, 0.5];
        var s1 = Math.min((w * fill) / MONITOR.w, (room * fill) / MONITOR.h);
        var end = {
          x: w * aim[0] + s1 * (SCREEN.cx - MONITOR.cx),
          y: header + room * aim[1] + s1 * (SCREEN.cy - MONITOR.cy)
        };
        if (cfg.cover) {
          end.x = fit(end.x, s1, SCREEN.cx, IMG_W, w);
          end.y = fit(end.y, s1, SCREEN.cy, IMG_H, h);
        }
        // La ventana del asistente mide lo mismo que la pantalla al final: el texto se ve a tamaño real
        var box = {
          w: Math.round(Math.max(edge(QUAD[0], QUAD[1]), edge(QUAD[3], QUAD[2])) * s1),
          h: Math.round(Math.max(edge(QUAD[0], QUAD[3]), edge(QUAD[1], QUAD[2])) * s1)
        };
        app.style.width = box.w + 'px';
        app.style.height = box.h + 'px';
        view = { w: w, h: h, s0: s0, s1: s1, start: start, end: end, box: box };
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

        // La ventana del asistente va siempre sobre la pantalla del monitor, en perspectiva
        app.style.transform = warp(QUAD.map(function (q) {
          return [ax + s * (q[0] - SCREEN.cx), ay + s * (q[1] - SCREEN.cy)];
        }), view.box);

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

        // Ya frente al monitor, la conversación avanza con el scroll y se puede desplazar
        var near = ramp(0.44, 0.49, p) > 0.5;
        app.classList.toggle('is-active', near);
        hero.classList.toggle('is-app', near);
        hero.classList.toggle('is-done', p > 0.9);

        document.body.classList.toggle('hero-copy-visible', p < 0.06);

        var revealed = early + Math.round(ramp(0.5, 0.86, p) * (steps.length - early));
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
          app.classList.remove('is-active');
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
      document.querySelectorAll('.cta-band, .site-footer').forEach(function (zone) { zones.observe(zone); });
    }
    window.addEventListener('scroll', updateWa, { passive: true });
    window.addEventListener('resize', updateWa);
    updateWa();
  }

  /* ---------- Año actual en el pie ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
