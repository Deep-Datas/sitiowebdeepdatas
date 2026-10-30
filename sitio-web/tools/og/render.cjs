// Dibuja la imagen que se ve cuando alguien comparte el sitio y la guarda como JPG.
//
//   python3 -m http.server 8077 --directory public &
//   node tools/og/render.cjs
//
// Escribe src/assets/img/brand/og-image-claro.jpg y og-image.jpg (el oscuro), 1200 x 630.
// El sitio tiene que estar servido en http://localhost:8077 por las tipografías y el logo.
// Para cambiar los textos, editá tools/og/portada.html y volvé a correr esto.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.join(__dirname, '..', '..');
const html = fs.readFileSync(path.join(__dirname, 'portada.html'), 'utf8');
const SALIDAS = [
  { tema: 'claro', lang: 'es', archivo: 'og-image-claro.jpg' },
  { tema: 'oscuro', lang: 'es', archivo: 'og-image.jpg' },
];

(async () => {
  const navegador = await chromium.launch();
  const page = await navegador.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.route('http://localhost:8077/__og.html*', r => r.fulfill({ contentType: 'text/html', body: html }));
  for (const s of SALIDAS) {
    await page.goto(`http://localhost:8077/__og.html?tema=${s.tema}&lang=${s.lang}`, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(250);
    const destino = path.join(RAIZ, 'src/assets/img/brand', s.archivo);
    await page.screenshot({ path: destino, type: 'jpeg', quality: 88 });
    console.log(destino, fs.statSync(destino).size + ' bytes');
  }
  await navegador.close();
})();
