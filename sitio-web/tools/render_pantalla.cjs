// Captura la ventana del asistente tal como se ve en la pantalla del monitor
// (estado «Analizando…», 1440 x 900) en tools/hero/png/pantalla.png.
// tools/hero_foto.py la pinta en perspectiva sobre la pantalla de la foto, para
// que la escena se vea bien también sin JavaScript.
// Requiere el sitio generado (python build.py) y Playwright: node tools/render_pantalla.cjs
const fs = require('fs');
const http = require('http');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const PUBLIC = path.join(__dirname, '..', 'public');
const OUT = path.join(__dirname, 'hero', 'png', 'pantalla.png');
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.woff2': 'font/woff2', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml' };

const server = http.createServer((req, res) => {
  let file = path.join(PUBLIC, decodeURIComponent(req.url.split('?')[0]));
  if (file.endsWith('/')) file = path.join(file, 'index.html');
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    res.end(data);
  });
});

server.listen(0, '127.0.0.1', async () => {
  const { port } = server.address();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  // Sin los scripts del sitio: la ventana queda en su estado inicial, sin animación
  await page.route(/\/assets\/js\//, route => route.abort());
  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'load' });
  await page.addStyleTag({ content: '.hs-screen{display:block!important;position:fixed!important;inset:0 auto auto 0!important;width:1440px!important;height:900px!important;overflow:hidden;transform:none!important;z-index:9999;container-type:inline-size}' });
  await page.evaluate(() => document.fonts.ready);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  await page.locator('.hs-screen').screenshot({ path: OUT });
  console.log('  ' + path.relative(process.cwd(), OUT));
  await browser.close();
  server.close();
});
