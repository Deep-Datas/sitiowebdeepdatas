/* Controles de todo el sitio, página por página.

   Sirve public/ con la política de seguridad de producción puesta y recorre cada
   dirección del sitemap, en escritorio y en celular, controlando lo que se rompe cuando
   se cambia texto en muchas páginas a la vez:

   - Que Vera esté nombrada en el contenido de cada página comercial, no solo en el menú
     y el pie (que la nombran siempre). Es el control que sostiene «Vera en todos lados».
   - Que no haya quedado texto hablando de «un agente de IA» donde ahora va su nombre.
   - Contraste de cada texto contra el color que de verdad tiene detrás.
   - Zonas para tocar de 24 x 24 como mínimo.
   - Que no aparezca scroll horizontal.
   - Que la consola no tenga errores, sobre todo bloqueos de la política de seguridad.
   - Que cada enlace interno lleve a una página que existe.

   La portada del inicio tiene su propio control, más detallado: tools/probar_portada.cjs.

   Antes hay que compilar:  python3 build.py && node tools/probar_sitio.cjs
   Falla diciendo qué está mal, en qué página y en qué tamaño. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright');

const RAIZ = path.join(__dirname, '..', 'public');
const CSP = JSON.parse(fs.readFileSync(path.join(RAIZ, 'staticwebapp.config.json'), 'utf8'))
  .globalHeaders['Content-Security-Policy'];
const TIPOS = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.woff2': 'font/woff2', '.ico': 'image/x-icon', '.webmanifest': 'application/manifest+json',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.vtt': 'text/vtt', '.xml': 'application/xml', '.txt': 'text/plain' };

const server = http.createServer((req, res) => {
  let f = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(RAIZ)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404).end('no'); return; }
  res.writeHead(200, { 'content-type': TIPOS[path.extname(f)] || 'application/octet-stream',
                       'content-security-policy': CSP });
  res.end(fs.readFileSync(f));
});

/* Las páginas que no venden nada: no tienen por qué nombrar a Vera. */
const SIN_VERA = [/^\/privacidad\/$/, /^\/en\/privacy\/$/, /^\/gracias\/$/, /^\/en\/thank-you\/$/,
                  /^\/404\.html$/, /^\/blog\//, /^\/en\/blog\//];

/* Lo que ya no se dice: ahora la asistente tiene nombre. En el blog sí se puede hablar de
   agentes de IA en general, así que las notas quedan afuera de este control. */
const VIEJO = [/\bagentes? de IA\b/i, /\bun agente de inteligencia artificial\b/i,
               /\bAI agents?\b/, /\bthe agent\b/i];

const fallas = [];

(async () => {
  await new Promise(r => server.listen(0, r));
  const base = 'http://127.0.0.1:' + server.address().port;

  const sitemap = fs.readFileSync(path.join(RAIZ, 'sitemap.xml'), 'utf8');
  const rutas = Array.from(sitemap.matchAll(/<loc>([^<]*)<\/loc>/g),
                           m => m[1].replace(/^https?:\/\/[^/]+/, '') || '/');
  if (rutas.length < 20) fallas.push(`[sitemap] solo ${rutas.length} direcciones: ¿compilaste?`);

  const nav = await chromium.launch();
  for (const med of [{ n: 'escritorio', w: 1440, h: 900 }, { n: 'celular', w: 390, h: 844 }]) {
    const ctx = await nav.newContext({ viewport: { width: med.w, height: med.h }, deviceScaleFactor: 1 });
    // Nada sale a internet: lo de afuera (el Turnstile, la analítica, el mapa) no está
    // bajo control acá y su error de red taparía los errores propios.
    await ctx.route('**/*', r => (r.request().url().startsWith(base) ? r.continue() : r.abort()));
    const page = await ctx.newPage();
    const errores = [];
    const propio = t => !/https?:\/\/(?!127\.0\.0\.1)/.test(t) && !/ERR_FAILED|ERR_BLOCKED/.test(t);
    page.on('console', m => { if (m.type() === 'error' && propio(m.text())) errores.push(m.text()); });
    page.on('pageerror', e => errores.push(String(e)));

    for (const ruta of rutas) {
      const donde = `${ruta} ${med.n}`;
      errores.length = 0;
      await page.goto(base + ruta, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(500);
      errores.forEach(e => fallas.push(`[consola ${donde}] ${e}`));

      /* ---- Vera, en el contenido y no solo en el menú ---- */
      const texto = await page.evaluate(() => {
        const main = document.querySelector('main');
        if (!main) return '';
        // El llamado final está dentro de main y nombra a Vera en todas las páginas: se
        // mide solo lo propio. Los títulos de las notas del blog son de las notas, y ahí
        // sí se habla de agentes de IA en general.
        const clon = main.cloneNode(true);
        clon.querySelectorAll('.finale, .post-grid, script').forEach(n => n.remove());
        return clon.textContent.replace(/\s+/g, ' ');
      });
      if (!SIN_VERA.some(re => re.test(ruta)) && !/\bVera\b/.test(texto)) {
        fallas.push(`[sin Vera ${donde}] la página no la nombra en su contenido`);
      }
      if (!/^\/(en\/)?blog\//.test(ruta)) {
        VIEJO.forEach(re => {
          const m = texto.match(re);
          if (m) fallas.push(`[texto viejo ${donde}] todavía dice «${m[0]}»`);
        });
      }

      /* ---- Scroll horizontal ---- */
      const ancho = await page.evaluate(() => ({ doc: document.documentElement.scrollWidth, win: innerWidth }));
      if (ancho.doc > ancho.win + 1) fallas.push(`[scroll ${donde}] ${ancho.doc} > ${ancho.win}`);

      /* ---- Contraste: cada texto contra el color que de verdad tiene detrás ----
         Se recorre la página de a una ventana, porque el fondo real se averigua
         preguntándole al navegador qué hay pintado en ese punto (elementsFromPoint), y eso
         solo funciona con el elemento a la vista. Bajar también dispara las animaciones de
         entrada, así que se mide el estado final, el que se lee. */
      const vistos = new Set();
      const malos = [];
      const alto = await page.evaluate(() => document.documentElement.scrollHeight);
      for (let y = 0; y < alto; y += med.h) {
        await page.evaluate(v => scrollTo(0, v), y);
        await page.waitForTimeout(250);
        const tanda = await page.evaluate(() => {
          const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
          const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
          // rgb(), rgba() y también color(srgb 1 0.96 0.95), que es como el navegador
          // devuelve un color-mix: ahí los componentes van de 0 a 1, no de 0 a 255.
          const rgb = s => {
            const m = s && s.match(/[\d.]+/g);
            if (!m) return null;
            const v = m.map(Number);
            if (s.startsWith('color(')) return [v[0] * 255, v[1] * 255, v[2] * 255, v[3] === undefined ? 1 : v[3]];
            return v.slice(0, 3).concat(v[3] === undefined ? 1 : v[3]);
          };
          const sobre = (fr, de) => fr[3] >= 1 ? fr.slice(0, 3) : fr.slice(0, 3).map((c, i) => c * fr[3] + de[i] * (1 - fr[3]));
          // El color pintado detrás del texto. Se pregunta por el punto, no por el árbol:
          // un rótulo puede ser hijo de una barra de color y dibujarse arriba de ella.
          // Si alguna capa es un degradado o una imagen, el color no se puede deducir:
          // devuelve null y ese texto no se mide (queda para el ojo humano).
          function fondo(el, x, y) {
            const capas = document.elementsFromPoint(x, y);
            if (!capas.length) return null;
            const pila = [];
            for (const n of capas) {
              if (n === el || el.contains(n)) continue;
              const cs = getComputedStyle(n);
              if (cs.backgroundImage !== 'none') return null;
              const b = rgb(cs.backgroundColor);
              if (b && b[3] > 0) { pila.push(b); if (b[3] >= 1) break; }
            }
            pila.push(rgb(getComputedStyle(document.documentElement).backgroundColor) || [255, 255, 255, 1]);
            let c = pila.pop().slice(0, 3);
            while (pila.length) c = sobre(pila.pop(), c);
            return c;
          }
          const out = [];
          document.querySelectorAll('main *').forEach(el => {
            const t = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
            if (!t) return;
            const cs = getComputedStyle(el);
            if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
            const r = el.getBoundingClientRect();
            if (!r.width || !r.height) return;
            // Solo lo que está a la vista en esta ventana
            if (r.bottom < 1 || r.top > innerHeight - 1 || r.right < 1 || r.left > innerWidth - 1) return;
            // El texto solo para lectores de pantalla se recorta a 1px: no se pinta nunca
            if (el.closest('.visually-hidden') || (r.width <= 2 && r.height <= 2)) return;
            const x = Math.min(innerWidth - 2, Math.max(1, r.left + Math.min(r.width / 2, 20)));
            const y = Math.min(innerHeight - 2, Math.max(1, r.top + r.height / 2));
            const f = rgb(cs.color), b = fondo(el, x, y);
            if (!f || !b) return;
            const l1 = lum(sobre(f, b)), l2 = lum(b);
            const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
            const px = parseFloat(cs.fontSize), peso = parseInt(cs.fontWeight, 10) || 400;
            const grande = px >= 24 || (px >= 18.66 && peso >= 700);
            const min = grande ? 3 : 4.5;
            if (ratio < min - 0.01) {
              out.push({ sel: String(el.className || el.tagName).slice(0, 40),
                         txt: el.textContent.trim().slice(0, 40), ratio: +ratio.toFixed(2), min, px: +px.toFixed(1) });
            }
          });
          return out;
        });
        tanda.forEach(m => {
          const clave = `${m.sel}|${m.txt}`;
          if (vistos.has(clave)) return;
          vistos.add(clave);
          malos.push(m);
        });
      }
      await page.evaluate(() => scrollTo(0, 0));
      malos.forEach(m => fallas.push(`[contraste ${donde}] ${m.sel} «${m.txt}» ${m.ratio}:1 (mínimo ${m.min}, ${m.px}px)`));

      /* ---- Zonas para tocar ---- */
      const chicos = await page.evaluate(() => {
        const out = [];
        document.querySelectorAll('main a, main button').forEach(el => {
          const cs = getComputedStyle(el);
          if (cs.visibility === 'hidden' || cs.display === 'none') return;
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height) return;
          // Un enlace dentro de un párrafo hereda el alto de la línea: no es un objetivo suelto
          if (el.closest('p, li, figcaption, dd, .prose') && cs.display === 'inline') return;
          if (r.width < 24 || r.height < 24) {
            out.push({ s: String(el.className || el.tagName).slice(0, 40), w: Math.round(r.width), h: Math.round(r.height) });
          }
        });
        return out;
      });
      chicos.forEach(c => fallas.push(`[tocar ${donde}] ${c.s} mide ${c.w}x${c.h}, mínimo 24x24`));
    }
    await ctx.close();
  }

  /* ---- Enlaces internos: que ninguno lleve a una página que no existe ---- */
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const vistos = new Set();
  for (const ruta of rutas) {
    await page.goto(base + ruta, { waitUntil: 'domcontentloaded' });
    const hrefs = await page.evaluate(() => Array.from(document.querySelectorAll('a[href^="/"]'), a => a.getAttribute('href')));
    for (const href of hrefs) {
      const limpio = href.split('#')[0].split('?')[0];
      if (!limpio || vistos.has(limpio)) continue;
      vistos.add(limpio);
      const dir = path.join(RAIZ, limpio);
      const existe = fs.existsSync(dir) && (fs.statSync(dir).isFile() || fs.existsSync(path.join(dir, 'index.html')));
      if (!existe) fallas.push(`[enlace roto] ${limpio} (desde ${ruta})`);
    }
  }
  await nav.close();
  server.close();

  if (fallas.length) {
    console.error(`\n${fallas.length} problema(s):\n`);
    fallas.forEach(f => console.error('  ' + f));
    process.exit(1);
  }
  console.log(`Todo en orden: ${rutas.length} páginas x 2 tamaños.`);
})();
