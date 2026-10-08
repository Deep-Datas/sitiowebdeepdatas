// Núcleo de datos del inicio: partículas dispersas que se ordenan en una esfera luminosa
// (tools/nucleo-escena.html, three.js). Renderiza 48 cuadros de 1600 x 1000 con Chromium sin
// pantalla y los exporta a src/assets/img/core/: d-00..d-23.webp (escritorio, 1440 x 900),
// m-00..m-11.webp (celulares, recorte central 648 x 900) y poster.webp (cuadro final).
// Requiere three.js (npm install three@0.170.0) y Playwright; sharp para los WebP.
// Uso: node tools/nucleo.cjs [carpeta de trabajo]
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const THREE_DIR = path.dirname(require.resolve('three/package.json'));
const out = process.argv[2] || path.join(__dirname, 'hero', 'png', 'nucleo');
const frames = 48;
const only = null;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
  p.on('pageerror', e => console.log('pageerror', e.message));
  p.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
  await p.route('http://core.local/**', route => {
    const u = new URL(route.request().url());
    let file = u.pathname === '/' ? path.join(__dirname, 'nucleo-escena.html') : path.join(path.dirname(THREE_DIR), u.pathname.slice(1));
    if (!fs.existsSync(file)) return route.fulfill({ status: 404 });
    const type = file.endsWith('.js') ? 'text/javascript' : 'text/html';
    route.fulfill({ status: 200, contentType: type, body: fs.readFileSync(file) });
  });
  await p.goto('http://core.local/', { waitUntil: 'load' });
  await p.waitForFunction(() => window.sceneReady, null, { timeout: 60000 });
  const list = only !== null ? [only] : [...Array(frames).keys()];
  for (const i of list) {
    const t = frames > 1 ? i / (frames - 1) : 1;
    const t0 = Date.now();
    const data = await p.evaluate(t => window.renderFrame(t), t);
    fs.writeFileSync(path.join(out, `core-${String(i).padStart(2, '0')}.png`), Buffer.from(data.split(',')[1], 'base64'));
    console.log(`frame ${i} t=${t.toFixed(2)} ${Date.now() - t0} ms`);
  }
  await b.close();
  await exportWebp();
})();

async function exportWebp() {
  let sharp;
  try { sharp = require('sharp'); } catch (e) { console.log('  (sin sharp: los PNG quedan en ' + out + '; convertilos a WebP con tools/hero_foto.py --nucleo)'); return; }
  const dest = path.join(__dirname, '..', 'src', 'assets', 'img', 'core');
  fs.mkdirSync(dest, { recursive: true });
  for (let k = 0; k < 24; k++) {
    const src = path.join(out, `core-${String(k * 2).padStart(2, '0')}.png`);
    await sharp(src).resize(1440, 900).webp({ quality: 72 }).toFile(path.join(dest, `d-${String(k).padStart(2, '0')}.webp`));
    if (k % 2 === 0) await sharp(src).extract({ left: 440, top: 0, width: 720, height: 1000 }).resize(648, 900).webp({ quality: 70 }).toFile(path.join(dest, `m-${String(k / 2).padStart(2, '0')}.webp`));
  }
  await sharp(path.join(out, 'core-47.png')).resize(1600, 1000).webp({ quality: 80 }).toFile(path.join(dest, 'poster.webp'));
  console.log('  src/assets/img/core/ actualizado');
}
