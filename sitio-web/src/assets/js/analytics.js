/**
 * DeepDatas - analítica de visitas (Microsoft Clarity)
 * Se incluye solo si CLARITY_ID está configurado en build.py.
 * Además de las visitas, registra las acciones que indican interés comercial y desde qué
 * parte de la página se hicieron, para saber qué botón convierte (ver README, «Analítica»).
 */
(function () {
  'use strict';

  var id = document.currentScript && document.currentScript.dataset.clarity;
  if (!id) return;

  window.clarity = window.clarity || function () {
    (window.clarity.q = window.clarity.q || []).push(arguments);
  };
  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.clarity.ms/tag/' + encodeURIComponent(id);
  document.head.appendChild(tag);

  function track(name) {
    window.clarity('event', name);
  }

  // Dónde está el enlace: el primer bloque de esta lista que lo contiene
  var PLACES = [
    ['[data-wa-float]', 'boton-flotante'],
    ['.site-header', 'encabezado'],
    ['.hp', 'inicio-portada'],
    ['.section-bridge', 'inicio-pasos'],
    ['.pin', 'inicio-asistente'],
    ['#industrias', 'inicio-industrias'],
    ['.plan-card', 'planes'],
    ['.finale', 'cierre'],
    ['.site-footer', 'pie'],
    ['.page-hero', 'encabezado-pagina'],
    ['.contact-card', 'contacto-otros-medios']
  ];

  function place(link) {
    for (var i = 0; i < PLACES.length; i++) {
      if (link.closest(PLACES[i][0])) return PLACES[i][1];
    }
    return 'contenido';
  }

  // Un evento general (para el total) y otro con el lugar (para comparar botones), más una
  // etiqueta de sesión con el último lugar desde el que se hizo cada acción
  function trackFrom(name, link) {
    var from = place(link);
    track(name);
    track(name + ':' + from);
    window.clarity('set', 'origen_' + name, from);
  }

  // Páginas de interés, en los dos idiomas
  var ROUTES = {
    diagnostico: ['/diagnostico/', '/en/data-assessment/'],
    autoevaluacion: ['/autoevaluacion/', '/en/ai-readiness-check/'],
    ia: ['/inteligencia-artificial/', '/en/ai-for-business/'],
    servicios: ['/servicios/', '/en/services/'],
    casos: ['/casos/', '/en/case-studies/'],
    industrias: ['/industrias/', '/en/industries/']
  };

  // El enlace lleva a una de esas páginas y no es la que se está viendo
  function goesTo(href, paths) {
    var target = href.split('#')[0];
    if (!target || target === location.pathname) return false;
    return paths.some(function (path) { return target.indexOf(path) === 0; });
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href');
    if (link.hasAttribute('data-booking') || link.matches('.nav-actions .btn-primary, .cta-actions .btn-primary')) trackFrom('agendar_reunion', link);
    else if (href.indexOf('https://wa.me/') === 0) trackFrom('whatsapp', link);
    else if (href.indexOf('mailto:') === 0) trackFrom('email', link);
    else if (href.indexOf('tel:') === 0) trackFrom('telefono', link);
    else if (goesTo(href, ROUTES.diagnostico)) trackFrom('ver_diagnostico', link);
    else if (goesTo(href, ROUTES.autoevaluacion)) trackFrom('ver_autoevaluacion', link);
    else if (goesTo(href, ROUTES.ia)) track('ver_ia');
    else if (goesTo(href, ROUTES.servicios)) track('ver_servicios');
    else if (goesTo(href, ROUTES.casos)) track('ver_casos');
    else if (goesTo(href, ROUTES.industrias)) track('ver_industria');
  });

  // Formulario enviado con éxito (lo avisa site.js)
  document.addEventListener('deepdatas:form-sent', function (event) {
    track('formulario_enviado');
    if (event.detail && event.detail.interest) {
      window.clarity('set', 'interes', event.detail.interest);
    }
  });

  // Autoevaluación completada, con el nivel que obtuvo (lo avisa site.js)
  document.addEventListener('deepdatas:quiz-done', function (event) {
    track('autoevaluacion_completada');
    if (event.detail && event.detail.level) {
      window.clarity('set', 'autoevaluacion_nivel', event.detail.level);
    }
  });

  // Envío sin JavaScript: la página de gracias confirma el envío
  if ((location.pathname === '/gracias/' || location.pathname === '/en/thank-you/') && location.hash !== '#error') track('formulario_enviado');

  // Idioma de la página, para comparar visitas en español e inglés
  window.clarity('set', 'idioma', document.documentElement.lang);
})();
