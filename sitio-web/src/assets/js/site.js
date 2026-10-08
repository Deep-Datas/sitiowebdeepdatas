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

  /* ---------- Inicio: la pregunta recorre los sistemas con el scroll ----------
     Solo con html.motion (src/assets/js/motion.js). Las posiciones de las ventanas están en
     design.css (--x, --y, --z); acá se mueve la cámara (--cam) y se calcula qué se ve. */
  var heroScene = document.querySelector('[data-hero-scene]');
  if (heroScene && document.documentElement.classList.contains('motion')) {
    (function (hero) {
      var track = hero.querySelector('.hq-track');
      var stage = hero.querySelector('.hq-stage');
      var world = hero.querySelector('.hq-world');
      var wins = Array.prototype.slice.call(hero.querySelectorAll('.hq-win'));
      var statuses = Array.prototype.slice.call(hero.querySelectorAll('.hq-status span'));
      var steps = Array.prototype.slice.call(hero.querySelectorAll('.hq-step'));
      var CAM = 3200;                        // cuánto avanza la cámara en todo el recorrido (px)
      var depths = [];
      var ticking = false;

      function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
      function ramp(a, b, v) { return clamp((v - a) / (b - a), 0, 1); }

      function measure() {
        depths = wins.map(function (w) { return parseFloat(getComputedStyle(w).getPropertyValue('--z')) || 0; });
      }

      function render() {
        ticking = false;
        var rect = track.getBoundingClientRect();
        var total = track.offsetHeight - stage.offsetHeight;
        var p = total > 0 ? clamp(-rect.top / total, 0, 1) : 1;
        var cam = p * CAM;
        world.style.setProperty('--cam', cam.toFixed(1) + 'px');
        // Cada ventana aparece a lo lejos y se desvanece justo antes de pasar la cámara
        wins.forEach(function (w, i) {
          var dz = depths[i] + cam;
          var op = ramp(-2600, -1900, dz) * (1 - ramp(-320, -120, dz));
          w.style.opacity = op.toFixed(3);
          w.style.visibility = op > 0.01 ? '' : 'hidden';
        });
        var fin = ramp(0.78, 0.96, p);
        stage.style.setProperty('--ao', fin.toFixed(3));
        stage.style.setProperty('--as', (0.6 + 0.4 * fin).toFixed(3));
        stage.style.setProperty('--os', (1 + 22 * ramp(0.55, 0.85, p) * (1 - fin)).toFixed(2));
        stage.style.setProperty('--oo', (1 - fin).toFixed(3));
        stage.style.setProperty('--sp', (ramp(0.08, 0.3, p) * (1 - ramp(0.8, 0.95, p))).toFixed(3));
        stage.style.setProperty('--ss', (0.6 + 1.6 * p).toFixed(3));
        stage.style.setProperty('--hop', (1 - ramp(0.02, 0.1, p)).toFixed(3));
        var current = 0;
        statuses.forEach(function (el, i) { if (p >= parseFloat(el.getAttribute('data-from'))) current = i; });
        statuses.forEach(function (el, i) { el.classList.toggle('is-on', i === current); });
        var step = 0;
        steps.forEach(function (el, i) { if (p >= parseFloat(el.getAttribute('data-from'))) step = i; });
        steps.forEach(function (el, i) {
          el.classList.toggle('is-on', i === step);
          el.classList.toggle('is-done', i < step);
        });
        hero.classList.toggle('is-done', p > 0.95);
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
      if (heading.hasAttribute('data-scroll-lit') || heading.closest('.hq')) return;
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
