/* Activa las animaciones al hacer scroll antes de que se pinte la página, para que los
   elementos no aparezcan y vuelvan a ocultarse. Si site.js no llega a encargarse de ellas
   (por un error o porque no cargó), en unos segundos se muestran igual. */
(function () {
  var root = document.documentElement;
  if (!('IntersectionObserver' in window) || !window.matchMedia('(prefers-reduced-motion: no-preference)').matches) return;
  root.classList.add('motion');
  setTimeout(function () {
    if (!root.classList.contains('motion-ready')) root.classList.remove('motion');
  }, 4000);
})();
