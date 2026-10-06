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
      var IMG_W = 3600;
      var IMG_H = 2250;
      var SCREEN = { x: 1202, y: 561, w: 1296, h: 810 };
      var SCREEN_CENTER = { x: SCREEN.x + SCREEN.w / 2, y: SCREEN.y + SCREEN.h / 2 };

      var stage = hero.querySelector('.hs-stage');
      var frame = hero.querySelector('.hs-frame');
      var scene = hero.querySelector('.hs-scene');
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
        // Ubica el punto (ax, ay) de la imagen en el centro elegido de la pantalla, con escala s
        el.style.transform = 'translate3d(' + (ax - s * SCREEN_CENTER.x).toFixed(2) + 'px,' +
          (ay - s * SCREEN_CENTER.y).toFixed(2) + 'px,0) scale(' + s.toFixed(5) + ')';
      }

      function fitStatic() {
        var s = frame.clientWidth / IMG_W;
        scene.style.transform = 'scale(' + s + ')';
        front.style.transform = 'scale(' + s + ')';
      }

      function measure() {
        var w = stage.clientWidth;
        var h = stage.clientHeight;
        var wide = w >= 1024;
        // Plano general: la escena llena la pantalla; en celulares, la pantalla del monitor queda centrada abajo del texto
        var s0 = wide ? Math.max(w / IMG_W, h / IMG_H) * 1.02 : (w * 1.7) / IMG_W;
        var start = wide ? { x: w * 0.72, y: h * 0.5 } : { x: w * 0.5, y: h * 0.79 };
        // Plano final: la pantalla del monitor cubre toda la vista
        var s1 = Math.max(w / SCREEN.w, (h - 0) / SCREEN.h) * 1.04;
        view = { w: w, h: h, s0: s0, s1: s1, start: start, end: { x: w / 2, y: h / 2 } };
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

        var t = ease(ramp(0.06, 0.5, p));
        var s = view.s0 * Math.pow(view.s1 / view.s0, t);
        var ax = lerp(view.start.x, view.end.x, t);
        var ay = lerp(view.start.y, view.end.y, t);
        place(scene, s, ax, ay);

        // La persona está más cerca de la cámara: crece más rápido, baja y se desvanece
        var sf = s * (1 + 1.8 * t * t);
        place(front, sf, ax, ay + t * view.h * 0.55);
        front.style.opacity = (1 - ramp(0.2, 0.62, t)).toFixed(3);

        var out = ramp(0.005, 0.06, p);
        copy.style.opacity = (1 - out).toFixed(3);
        copy.style.transform = 'translateY(' + (-48 * out).toFixed(1) + 'px)';
        copy.style.visibility = out >= 1 ? 'hidden' : '';
        hint.style.opacity = (1 - ramp(0, 0.05, p)).toFixed(3);
        shade.style.opacity = (1 - ramp(0.04, 0.22, p)).toFixed(3);

        var appIn = ramp(0.485, 0.515, p);
        frame.style.opacity = (1 - ramp(0.505, 0.53, p)).toFixed(3);
        app.style.opacity = appIn.toFixed(3);
        app.style.transform = 'scale(' + (1.04 - 0.04 * appIn).toFixed(4) + ')';
        app.classList.toggle('is-active', appIn > 0.5);
        hero.classList.toggle('is-app', appIn > 0.5);

        var revealed = Math.round(ramp(0.55, 0.93, p) * steps.length);
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
          measure();
          shown = -1;
          render();
          window.addEventListener('scroll', onScroll, { passive: true });
        } else {
          hero.classList.remove('is-animated', 'is-app');
          window.removeEventListener('scroll', onScroll);
          [scene, front, copy, hint, shade, frame, app, thread].forEach(function (el) { el.removeAttribute('style'); });
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
