// Renderiza la escena del asistente cuadro a cuadro (determinista: window.seek(t)).
// Uso: node tools/video/render.cjs <es|en> <carpeta> [fps] [solo: t1,t2,...]
// Requiere el sitio servido en http://localhost:8077 (python -m http.server 8077 --directory public) por las tipografías.
const fs = require('fs');
const { chromium } = require('playwright');
const lang = process.argv[2] || 'es';
const out = process.argv[3];
const fps = parseInt(process.argv[4] || '30', 10);
const only = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
const html = fs.readFileSync(__dirname + '/escena.html', 'utf8');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
  await p.route('http://localhost:8077/__demo.html*', r => r.fulfill({ contentType: 'text/html', body: html }));
  await p.goto('http://localhost:8077/__demo.html?lang=' + lang, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(200);
  fs.mkdirSync(out, { recursive: true });
  const duration = await p.evaluate(() => window.DURATION);
  const times = only || Array.from({ length: Math.round(duration * fps) }, (_, i) => i / fps);
  let i = 0;
  for (const t of times) {
    await p.evaluate(v => window.seek(v), t);
    const name = only ? `t-${String(t).replace('.', '_')}.png` : `f-${String(i).padStart(4, '0')}.png`;
    await p.screenshot({ path: `${out}/${name}` });
    i++;
  }
  console.log('frames', i, 'duration', duration, 'fps', fps);
  await b.close();
})();
