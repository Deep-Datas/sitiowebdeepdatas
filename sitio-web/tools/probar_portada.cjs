/* Controles de la portada del inicio (src/hero.html).

   Recorre la matriz —español e inglés, escritorio y celular, con animación, sin animación
   y sin JavaScript— sirviendo public/ con la política de seguridad de producción puesta, y
   controla lo que más se rompe en esta escena:

   - Contraste de cada texto contra el color que de verdad tiene detrás.
   - Zonas para tocar de 24 x 24 como mínimo.
   - Que no aparezca scroll horizontal.
   - Que se llegue a las tres preguntas con el teclado.
   - Que cada pregunta quede marcada sola, traiga su respuesta y cite tres fuentes.
   - Que sin JavaScript se lea la primera respuesta y no quede ningún botón muerto.
   - Que sin animación los botones respondan al instante y no haya riel.

   Antes hay que compilar:  python3 build.py && node tools/probar_portada.cjs
   Falla diciendo qué está mal, en qué idioma y en qué tamaño. */
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
  '.mp4': 'video/mp4', '.vtt': 'text/vtt', '.xml': 'application/xml', '.txt': 'text/plain' };

const server = http.createServer((req, res) => {
  let f = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(RAIZ)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404).end('no'); return; }
  res.writeHead(200, { 'content-type': TIPOS[path.extname(f)] || 'application/octet-stream',
                       'content-security-policy': CSP });
  res.end(fs.readFileSync(f));
});

const fallas = [];
const controlar = (q, ok) => { if (!ok) fallas.push(q); };

(async () => {
  await new Promise(r => server.listen(0, r));
  const base = 'http://127.0.0.1:' + server.address().port;
  const nav = await chromium.launch();

  for (const med of [{ n: 'escritorio', w: 1440, h: 900 }, { n: 'celular', w: 390, h: 844 }]) {
    for (const pag of [{ n: 'es', u: '/' }, { n: 'en', u: '/en/' }]) {
      const ctx = await nav.newContext({ viewport: { width: med.w, height: med.h }, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      await page.goto(base + pag.u, { waitUntil: 'networkidle' });
      await page.waitForTimeout(3400);
      const donde = `${pag.n}/${med.n}`;

      /* ---- Contraste: cada texto contra el color que de verdad tiene detrás ---- */
      const malos = await page.evaluate(() => {
        const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
        const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
        const rgb = s => { const m = s.match(/[\d.]+/g); return m ? m.slice(0, 3).map(Number).concat(m[3] === undefined ? 1 : +m[3]) : null; };
        const sobre = (fr, de) => fr[3] >= 1 ? fr.slice(0, 3) : fr.slice(0, 3).map((c, i) => c * fr[3] + de[i] * (1 - fr[3]));
        function fondo(el) {
          let n = el, pila = [];
          while (n && n !== document.documentElement) {
            const b = rgb(getComputedStyle(n).backgroundColor);
            if (b && b[3] > 0) pila.push(b);
            n = n.parentElement;
          }
          pila.push(rgb(getComputedStyle(document.documentElement).backgroundColor) || [255, 255, 255, 1]);
          let c = pila.pop().slice(0, 3);
          while (pila.length) c = sobre(pila.pop(), c);
          return c;
        }
        const out = [];
        document.querySelectorAll('.vz *').forEach(el => {
          const t = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
          if (!t) return;
          const cs = getComputedStyle(el);
          if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height) return;
          // El texto solo para lectores de pantalla se recorta a 1px: no se pinta nunca
          if (el.closest('.visually-hidden') || (r.width <= 2 && r.height <= 2)) return;
          const f = rgb(cs.color), b = fondo(el);
          if (!f) return;
          const l1 = lum(sobre(f, b)), l2 = lum(b);
          const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
          const px = parseFloat(cs.fontSize), peso = parseInt(cs.fontWeight, 10) || 400;
          const grande = px >= 24 || (px >= 18.66 && peso >= 700);
          const min = grande ? 3 : 4.5;
          if (ratio < min - 0.01) {
            out.push({ sel: el.className || el.tagName, txt: el.textContent.trim().slice(0, 40),
                       ratio: +ratio.toFixed(2), min, px: +px.toFixed(1) });
          }
        });
        return out;
      });
      malos.forEach(m => fallas.push(`[contraste ${donde}] ${m.sel} «${m.txt}» ${m.ratio}:1 (mínimo ${m.min}, ${m.px}px)`));

      /* ---- Zonas para tocar ---- */
      const chicos = await page.evaluate(() => {
        const out = [];
        document.querySelectorAll('.vz button, .vz a').forEach(el => {
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height) return;
          if (r.width < 24 || r.height < 24) out.push({ s: el.className || el.tagName, w: Math.round(r.width), h: Math.round(r.height) });
        });
        return out;
      });
      chicos.forEach(c => fallas.push(`[tocar ${donde}] ${c.s} mide ${c.w}x${c.h}, mínimo 24x24`));

      /* ---- Nada tapado por el encabezado ni desbordado ---- */
      const ancho = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      controlar(`[scroll-x ${donde}] ${ancho[0]} > ${ancho[1]}`, ancho[0] <= ancho[1] + 1);

      /* ---- Teclado: se llega a los tres botones y el foco se ve ---- */
      const teclado = await page.evaluate(() => {
        const b = document.querySelector('[data-vz-q="1"]');
        b.focus();
        const o = getComputedStyle(b, ':focus-visible').outlineWidth;
        return { foco: document.activeElement === b, borde: o };
      });
      controlar(`[teclado ${donde}] no se puede enfocar la segunda pregunta`, teclado.foco);

      /* ---- Los tres botones cambian la respuesta y se marcan ---- */
      for (let i = 0; i < 3; i++) {
        await page.click(`[data-vz-q="${i}"]`);
        // A media escritura la barra ya tiene que medir lo que va a medir al final:
        // si creciera renglón a renglón empujaría a los botones y a la respuesta
        await page.waitForTimeout(600);
        const medio = await page.$eval('.vz-bar', el => el.getBoundingClientRect().height);
        await page.waitForTimeout(2400);
        const fin = await page.$eval('.vz-bar', el => el.getBoundingClientRect().height);
        controlar(`[barra ${donde}] cambia de alto mientras escribe la pregunta ${i} (${medio} → ${fin})`,
                  Math.abs(medio - fin) < 1);
        const est = await page.evaluate(() => ({
          marcados: Array.from(document.querySelectorAll('[data-vz-q]')).map(b => b.getAttribute('aria-pressed')),
          pregunta: document.querySelector('[data-vz-aq]').textContent.trim(),
          grande: document.querySelector('[data-vz-abig]').textContent.trim(),
          fuentes: document.querySelectorAll('[data-vz-asrc] .vz-src-pill').length,
          dicho: document.querySelector('[data-vz-said]').textContent.trim(),
        }));
        const esperado = [0, 1, 2].map(k => (k === i ? 'true' : 'false'));
        controlar(`[preguntas ${donde}] el botón ${i} no queda marcado solo (${est.marcados})`,
                  est.marcados.join() === esperado.join());
        controlar(`[preguntas ${donde}] el botón ${i} no trae su respuesta`, est.grande.length > 1);
        controlar(`[preguntas ${donde}] el botón ${i} no cita fuentes`, est.fuentes === 3);
        controlar(`[preguntas ${donde}] la barra no termina de escribir la pregunta ${i}`,
                  est.dicho === est.pregunta);
      }
      await ctx.close();
    }
  }

  /* ---- Sin JavaScript: se lee la primera respuesta y no quedan controles muertos ---- */
  {
    const ctx = await nav.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false });
    const page = await ctx.newPage();
    await page.goto(base + '/', { waitUntil: 'load' });
    const sinJs = await page.evaluate(() => null).catch(() => null);
    const estado = await page.$eval('.vz', el => ({
      respuesta: !!el.querySelector('[data-vz-abig]').textContent.trim(),
      botonesVisibles: Array.from(el.querySelectorAll('button')).filter(b => b.offsetParent !== null).length,
      micDibujo: el.querySelector('[data-vz-still]').offsetParent !== null,
      nucleo: el.querySelector('[data-vz-fuse]').offsetParent !== null,
    }));
    controlar('[sin-js] no se ve la respuesta escrita en el HTML', estado.respuesta);
    controlar(`[sin-js] quedan ${estado.botonesVisibles} botones que no hacen nada`, estado.botonesVisibles === 0);
    controlar('[sin-js] no se ve el micrófono dibujado', estado.micDibujo);
    controlar('[sin-js] se ve el recuadro del núcleo, que sin JavaScript queda vacío', !estado.nucleo);
    await ctx.close();
  }

  /* ---- Sin animación: los botones siguen respondiendo ---- */
  {
    const ctx = await nav.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    await page.goto(base + '/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await page.click('[data-vz-q="2"]');
    await page.waitForTimeout(200);
    const est = await page.evaluate(() => {
      const caja = document.querySelector('[data-vz-fuse]').getBoundingClientRect();
      return {
        grande: document.querySelector('[data-vz-abig]').textContent.trim(),
        marcado: document.querySelector('[data-vz-q="2"]').getAttribute('aria-pressed'),
        // Quieto, los cinco sistemas tienen que verse alrededor del núcleo y dentro del recuadro
        sistemas: Array.from(document.querySelectorAll('[data-vz-sys]')).map(el => {
          const r = el.getBoundingClientRect();
          return { o: +getComputedStyle(el).opacity,
                   dentro: r.left >= caja.left - 1 && r.right <= caja.right + 1
                           && r.top >= caja.top - 1 && r.bottom <= caja.bottom + 1 };
        }),
      };
    });
    controlar('[sin-animación] el tercer botón no responde al instante', est.grande.length > 1 && est.marcado === 'true');
    controlar('[sin-animación] los cinco sistemas no quedan a la vista alrededor del núcleo',
              est.sistemas.length === 5 && est.sistemas.every(s => s.o > 0.95));
    controlar('[sin-animación] algún sistema queda fuera del recuadro del núcleo',
              est.sistemas.every(s => s.dentro));
    await ctx.close();
  }

  await nav.close();
  server.close();
  console.log(fallas.length ? fallas.join('\n') + `\n\n${fallas.length} control(es) fallaron.` : 'Todo en orden.');
  if (fallas.length) process.exitCode = 1;
})();
