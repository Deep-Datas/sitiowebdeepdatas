/**
 * DeepDatas - comportamiento del sitio
 */
(function () {
  "use strict";

  const header = document.querySelector('#header');
  const nav = document.querySelector('#navbar');
  const navToggle = document.querySelector('.nav-toggle');
  const backToTop = document.querySelector('.back-to-top');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /**
   * Header con fondo sólido y botón "volver arriba" al hacer scroll
   */
  function onScroll() {
    const scrolled = window.scrollY > 40;
    header.classList.toggle('scrolled', scrolled);
    backToTop.classList.toggle('visible', window.scrollY > 600);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /**
   * Menú móvil
   */
  function setMenu(open) {
    nav.classList.toggle('open', open);
    header.classList.toggle('menu-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    navToggle.querySelector('i').className = open ? 'bi bi-x-lg' : 'bi bi-list';
  }

  window.matchMedia('(min-width: 1200px)').addEventListener('change', function (event) {
    if (event.matches) setMenu(false);
  });

  navToggle.addEventListener('click', function () {
    setMenu(!nav.classList.contains('open'));
  });

  nav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      setMenu(false);
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      setMenu(false);
      navToggle.focus();
    }
  });

  /**
   * Resalta en el menú la sección visible
   */
  const navLinks = Array.from(nav.querySelectorAll('.nav-link[href^="#"]'));
  // El hero también se observa para que ningún link quede activo al volver al inicio
  const sections = ['#inicio'].concat(navLinks.map(function (link) { return link.getAttribute('href'); }))
    .map(function (selector) { return document.querySelector(selector); })
    .filter(Boolean);

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (link) {
          const active = link.getAttribute('href') === '#' + entry.target.id;
          link.classList.toggle('active', active);
          if (active) {
            link.setAttribute('aria-current', 'true');
          } else {
            link.removeAttribute('aria-current');
          }
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (section) { observer.observe(section); });
  }

  /**
   * Animaciones al hacer scroll
   */
  if (window.AOS) {
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      offset: 60,
      disable: reducedMotion
    });
  }

  /**
   * Galería de casos de éxito
   */
  if (window.GLightbox) {
    GLightbox({ selector: '.case-lightbox' });
  }

  /**
   * Año actual en el pie de página
   */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /**
   * Formulario de contacto (envío sin recargar la página)
   */
  const form = document.querySelector('.contact-form');
  if (form && window.fetch) {
    // Con JavaScript validamos nosotros para mostrar mensajes en español
    form.setAttribute('novalidate', '');
    const status = form.querySelector('.form-status');
    const button = form.querySelector('button[type="submit"]');
    const buttonLabel = button.innerHTML;

    function showStatus(type, message) {
      const icon = type === 'ok' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill';
      status.innerHTML = '';
      const span = document.createElement('span');
      span.className = type;
      span.innerHTML = '<i class="bi ' + icon + '" aria-hidden="true"></i> ';
      span.appendChild(document.createTextNode(message));
      status.appendChild(span);
    }

    form.querySelectorAll('input, textarea').forEach(function (field) {
      field.addEventListener('input', function () {
        field.classList.remove('invalid');
        field.removeAttribute('aria-invalid');
      });
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();

      const invalid = Array.from(form.querySelectorAll('input, textarea')).filter(function (field) {
        return !field.checkValidity();
      });
      invalid.forEach(function (field) {
        field.classList.add('invalid');
        field.setAttribute('aria-invalid', 'true');
      });
      if (invalid.length) {
        const emailField = form.querySelector('#email');
        const onlyEmail = invalid.length === 1 && invalid[0] === emailField && emailField.value.trim();
        showStatus('error', onlyEmail ? 'Ingresá un email válido.' : 'Completá todos los campos obligatorios.');
        invalid[0].focus();
        return;
      }

      button.disabled = true;
      button.innerHTML = 'Enviando…';
      status.innerHTML = '';

      fetch(form.action, {
        method: 'POST',
        body: new URLSearchParams(new FormData(form)),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (response) {
          return response.json().catch(function () {
            return { ok: false };
          });
        })
        .then(function (data) {
          if (data.ok) {
            form.reset();
            showStatus('ok', '¡Gracias! Recibimos tu mensaje y te responderemos a la brevedad.');
          } else {
            showStatus('error', data.error || 'No pudimos enviar tu mensaje. Escribinos a contacto@deepdatas.com.');
          }
        })
        .catch(function () {
          showStatus('error', 'No pudimos enviar tu mensaje. Revisá tu conexión e intentá nuevamente.');
        })
        .finally(function () {
          button.disabled = false;
          button.innerHTML = buttonLabel;
        });
    });
  }

})();
