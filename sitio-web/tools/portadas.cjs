// Portadas de las industrias (tools/portada.html): fondo profundo con auroras de colores y el
// ícono de la industria en un disco de vidrio. Genera PNG de 1200 x 800 y, con sharp, los WebP
// de src/assets/img/industrias/ (<id>-1200.webp y <id>-600.webp). Los colores van por industria.
// Uso: node tools/portadas.cjs [carpeta de trabajo]
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const ICONS = path.join(__dirname, '..', 'src', 'icons');
const out = process.argv[2] || path.join(__dirname, 'hero', 'png', 'portadas');
const INDUSTRIES = {
  consumo: ['cart3', '#ff7a45', '#ffb020', '#ff4d6d'],
  distribucion: ['truck', '#5b8cff', '#67d8ff', '#8b5cf6'],
  pymes: ['briefcase', '#8b5cf6', '#ff7a45', '#5b8cff'],
  retail: ['shop', '#ff4d8d', '#ff7a45', '#8b5cf6'],
  materiales: ['lightning-charge', '#ffb020', '#5b8cff', '#ff7a45'],
  autopartes: ['car', '#67d8ff', '#5b8cff', '#94a3b8'],
  industria: ['building-gear', '#5b8cff', '#8b5cf6', '#67d8ff'],
  agro: ['sprout', '#34d399', '#ffb020', '#5b8cff'],
  salud: ['heart-pulse', '#2dd4bf', '#5b8cff', '#8b5cf6'],
};
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const tpl = fs.readFileSync(path.join(__dirname, 'portada.html'), 'utf8');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 800 } });
  for (const [id, [icon, c1, c2, c3]] of Object.entries(INDUSTRIES)) {
    let svg = fs.readFileSync(path.join(ICONS, icon + '.svg'), 'utf8');
    svg = svg.slice(svg.indexOf('<svg'));
    const html = tpl.replace('{{ICON}}', svg).replace(/\{\{C1\}\}/g, c1).replace(/\{\{C2\}\}/g, c2).replace(/\{\{C3\}\}/g, c3);
    await p.setContent(html, { waitUntil: 'load' });
    await p.screenshot({ path: path.join(out, id + '.png'), clip: { x: 0, y: 0, width: 1200, height: 800 } });
    console.log('  ' + id);
  }
  await b.close();
  let sharp;
  try { sharp = require('sharp'); } catch (e) { console.log('  (sin sharp: los PNG quedan en ' + out + ')'); return; }
  const dest = path.join(__dirname, '..', 'src', 'assets', 'img', 'industrias');
  fs.mkdirSync(dest, { recursive: true });
  for (const id of Object.keys(INDUSTRIES)) {
    await sharp(path.join(out, id + '.png')).webp({ quality: 78 }).toFile(path.join(dest, id + '-1200.webp'));
    await sharp(path.join(out, id + '.png')).resize(600, 400).webp({ quality: 78 }).toFile(path.join(dest, id + '-600.webp'));
  }
  console.log('  src/assets/img/industrias/ actualizado');
})();
