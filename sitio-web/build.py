"""Genera el sitio estático de DeepDatas en la carpeta public/.

Uso:
    pip install -r requirements.txt
    python build.py

Las páginas se escriben en src/pages/ y comparten la estructura de
src/layout.html (encabezado, pie, metadatos). public/ se regenera completo
en cada ejecución: no editar archivos dentro de public/.
"""
import hashlib
import shutil
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from dashboards import EXAMPLES


ROOT = Path(__file__).parent
SRC = ROOT / 'src'
OUT = ROOT / 'public'
SITE_URL = 'https://deepdatas.com'

# Páginas del sitio: plantilla, ruta pública, título y descripción para buscadores.
PAGES = [
    {
        'template': 'index.html', 'path': '/', 'nav': 'inicio',
        'title': 'DeepDatas | Consultora de datos e inteligencia de negocios',
        'description': 'Integramos, limpiamos y analizamos los datos de tu empresa para convertirlos en tableros de gestión y modelos predictivos que ayudan a vender más y gastar menos.',
    },
    {
        'template': 'servicios.html', 'path': '/servicios/', 'nav': 'servicios',
        'title': 'Servicios | DeepDatas',
        'description': 'Ingeniería de datos, calidad y preparación, analítica avanzada con modelos predictivos y tableros de gestión en Power BI. Un solo equipo para todo el ciclo de vida de tus datos.',
    },
    {
        'template': 'ejemplos.html', 'path': '/ejemplos/', 'nav': 'ejemplos',
        'title': 'Ejemplos de tableros | DeepDatas',
        'description': 'Tableros interactivos de ejemplo, con datos ficticios: performance de distribuidores, cobertura de puntos de venta y pronóstico de demanda.',
    },
    {
        'template': 'nosotros.html', 'path': '/nosotros/', 'nav': 'nosotros',
        'title': 'Nosotros | DeepDatas',
        'description': 'Somos un equipo de especialistas en datos con más de 10 años de experiencia, con base en Buenos Aires, Argentina.',
    },
    {
        'template': 'contacto.html', 'path': '/contacto/', 'nav': 'contacto',
        'title': 'Contacto | DeepDatas',
        'description': 'Contanos tu desafío y coordinamos una reunión de diagnóstico sin costo. Bernardo de Irigoyen 330, CABA, Argentina.',
    },
    {
        'template': 'gracias.html', 'path': '/gracias/', 'nav': None, 'noindex': True,
        'title': 'Mensaje enviado | DeepDatas',
        'description': 'Gracias por escribirnos.',
    },
    {
        'template': '404.html', 'path': '/404.html', 'nav': None, 'noindex': True,
        'title': 'Página no encontrada | DeepDatas',
        'description': 'La página que buscás no existe.',
    },
]


def icon(name, label=None, cls=''):
    """Inserta un ícono SVG de src/icons (Bootstrap Icons, licencia MIT)."""
    svg = (SRC / 'icons' / f'{name}.svg').read_text(encoding='utf-8')
    svg = svg[svg.index('<svg'):]
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true" focusable="false"'
    svg = svg.replace('<svg ', f'<svg {a11y} ', 1)
    classes = f'icon {cls}'.strip()
    svg = svg.replace(f'class="bi bi-{name}"', f'class="{classes}"')
    svg = svg.replace('width="16" height="16" ', '')
    return Markup(' '.join(svg.split()))


def asset(path):
    """URL de un archivo de assets con un hash de su contenido, para que los
    navegadores descarguen la versión nueva cuando cambia."""
    file = OUT / 'assets' / path
    digest = hashlib.sha256(file.read_bytes()).hexdigest()[:10] if file.exists() else 'dev'
    return f'/assets/{path}?v={digest}'


class Positions:
    """Posiciones y tamaños de los gráficos.

    La política de seguridad del sitio no permite estilos en línea
    (style="..."), así que cada valor se convierte en una clase CSS
    (por ejemplo "w-42-5" -> --w: 42.5%) que se escribe en charts.css.
    """
    PROPS = {'x': '--x', 'y': '--y', 'w': '--w', 'h': '--h'}

    def __init__(self):
        self.rules = {}

    def __call__(self, prop, value):
        value = round(float(value), 1)
        text = f'{value:g}'
        name = f'{prop}-{text.replace(".", "-")}'
        self.rules[name] = f'.{name} {{ {self.PROPS[prop]}: {text}%; }}'
        return name

    def css(self):
        header = '/* Generado por build.py a partir de dashboards.py: no editar. */\n'
        return header + '\n'.join(self.rules[k] for k in sorted(self.rules)) + '\n'


def money(value):
    return f'$ {value:.2f} M'.replace('.', ',')


def hero_chart():
    """Geometría del gráfico ilustrativo del inicio (ventas reales y pronóstico)."""
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    real = [1.12, 1.18, 1.10, 1.26, 1.31, 1.28, 1.42, 1.47, 1.55]           # enero a septiembre
    forecast = [1.55, 1.61, 1.66, 1.74]                                     # septiembre a diciembre
    spread = [0, 0.04, 0.07, 0.10]                                          # banda de confianza
    width, height = 560, 250
    left, right, top, bottom = 52, 20, 14, 30
    low, high = 1.0, 1.8
    step = (width - left - right) / (len(months) - 1)

    def x(i):
        return left + i * step

    def y(v):
        return top + (high - v) / (high - low) * (height - top - bottom)

    def path(points):
        return 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in points)

    real_pts = [(x(i), y(v)) for i, v in enumerate(real)]
    first = len(real) - 1
    fc_pts = [(x(first + i), y(v)) for i, v in enumerate(forecast)]
    band = ([(x(first + i), y(v + s)) for i, (v, s) in enumerate(zip(forecast, spread))]
            + [(x(first + i), y(v - s)) for i, (v, s) in reversed(list(enumerate(zip(forecast, spread))))])

    columns = []
    for i, month in enumerate(months):
        r = real[i] if i < len(real) else None
        f = forecast[i - first] if first < i < first + len(forecast) else None
        columns.append({
            'x': x(i), 'hit_x': x(i) - step / 2, 'hit_w': step, 'month': month,
            'real': money(r) if r is not None else '',
            'forecast': money(f) if f is not None else '',
            'y': y(r if r is not None else f),
        })

    return {
        'width': width, 'height': height, 'left': left, 'right': width - right,
        'top': top, 'bottom': height - bottom,
        'ticks': [(y(v), f'{v:.1f}'.replace('.', ',')) for v in (1.0, 1.2, 1.4, 1.6, 1.8)],
        'real_line': path(real_pts),
        'real_area': path(real_pts) + f' L{real_pts[-1][0]:.1f} {y(low):.1f} L{real_pts[0][0]:.1f} {y(low):.1f} Z',
        'forecast_line': path(fc_pts),
        'band': path(band) + ' Z',
        'real_end': real_pts[-1], 'forecast_end': fc_pts[-1],
        'forecast_end_label': money(forecast[-1]),
        'columns': columns,
    }


def output_file(path):
    if path.endswith('.html'):
        return OUT / path.lstrip('/')
    return OUT / path.lstrip('/') / 'index.html'


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / 'assets', OUT / 'assets')
    shutil.copy(SRC / 'staticwebapp.config.json', OUT / 'staticwebapp.config.json')

    env = Environment(
        loader=FileSystemLoader([SRC, SRC / 'pages']),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    pos = Positions()
    env.globals.update(icon=icon, asset=asset, hero_chart=hero_chart, pos=pos, examples=EXAMPLES,
                       site_url=SITE_URL, year=date.today().year)

    def render_all():
        return [(page, env.get_template(page['template']).render(page=page))
                for page in ({'noindex': False, **p} for p in PAGES)]

    # Primera pasada: junta las posiciones de los gráficos para escribir charts.css.
    # Segunda pasada: las páginas ya pueden enlazar charts.css con su versión.
    render_all()
    (OUT / 'assets' / 'css' / 'charts.css').write_text(pos.css(), encoding='utf-8')
    for page, html in render_all():
        target = output_file(page['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
        print(f'  {page["path"]:<14} -> {target.relative_to(ROOT)}')

    indexable = [p for p in PAGES if not p.get('noindex')]
    urls = '\n'.join(f'  <url><loc>{SITE_URL}{p["path"]}</loc></url>' for p in indexable)
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{urls}\n</urlset>\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')
    print(f'Sitio generado en {OUT.relative_to(ROOT)}/')


if __name__ == '__main__':
    build()
