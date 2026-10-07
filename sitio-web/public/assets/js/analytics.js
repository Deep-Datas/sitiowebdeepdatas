/**
 * DeepDatas - analítica de visitas (Microsoft Clarity)
 * Se incluye solo si CLARITY_ID está configurado en build.py.
 * Además de las visitas, registra las acciones que indican interés comercial.
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

  // Clics en los medios de contacto y en la oferta de diagnóstico
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href');
    if (link.hasAttribute('data-booking')) track('agendar_reunion');
    else if (href.indexOf('https://wa.me/') === 0) track('whatsapp');
    else if (href.indexOf('mailto:') === 0) track('email');
    else if (href.indexOf('tel:') === 0) track('telefono');
    else if (href.indexOf('/diagnostico/') === 0 && location.pathname !== '/diagnostico/') track('ver_diagnostico');
    else if (link.matches('.nav-actions .btn-primary, .cta-actions .btn-primary')) track('agendar_reunion');
  });

  // Formulario enviado con éxito (lo avisa site.js)
  document.addEventListener('deepdatas:form-sent', function (event) {
    track('formulario_enviado');
    if (event.detail && event.detail.interest) {
      window.clarity('set', 'interes', event.detail.interest);
    }
  });

  // Envío sin JavaScript: la página de gracias confirma el envío
  if (location.pathname === '/gracias/' && location.hash !== '#error') track('formulario_enviado');
})();
