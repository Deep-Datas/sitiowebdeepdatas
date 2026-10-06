// Convierte las capas SVG de tools/hero/ en PNG (tools/hero/png/).
// Después, python tools/hero_webp.py genera las imágenes WebP del sitio.
// Requiere Playwright: node tools/render_hero.cjs
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const SRC = path.join(__dirname, 'hero');
const OUT = path.join(SRC, 'png');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 3600, height: 2250 } });
  for (const name of ['fondo', 'frente']) {
    const svg = fs.readFileSync(path.join(SRC, `${name}.svg`), 'utf8');
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    const target = path.join(OUT, `${name}.png`);
    await page.locator('svg').screenshot({ path: target, omitBackground: true });
    console.log('  ' + path.relative(process.cwd(), target));
  }
  await browser.close();
})();
