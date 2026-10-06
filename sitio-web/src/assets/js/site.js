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
