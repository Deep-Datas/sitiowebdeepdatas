// Convierte los SVG de tools/glass/ en PNG con fondo transparente (tools/glass/png/).
// Después, python tools/glass_webp.py genera las versiones WebP que usa el sitio.
// Requiere Playwright: node tools/render_glass.cjs
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const SRC = path.join(__dirname, 'glass');
const OUT = path.join(SRC, 'png');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 512, height: 512 } });
  const files = fs.readdirSync(SRC).filter(f => f.endsWith('.svg')).map(f => [f, f.replace('.svg', '.png')])
    .concat(fs.readdirSync(path.join(SRC, 'claro')).filter(f => f.endsWith('.svg')).map(f => ['claro/' + f, f.replace('.svg', '-claro.png')]));
  for (const [file, png] of files) {
    const svg = fs.readFileSync(path.join(SRC, file), 'utf8');
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    const target = path.join(OUT, png);
    await page.locator('svg').screenshot({ path: target, omitBackground: true });
    console.log('  ' + path.relative(process.cwd(), target));
  }
  await browser.close();
})();
