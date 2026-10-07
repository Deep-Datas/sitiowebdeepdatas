"""Genera el sitio estático de DeepDatas en la carpeta public/.

Uso:
    pip install -r requirements.txt
    python build.py

Las páginas se escriben en src/pages/ y comparten la estructura de
src/layout.html (encabezado, pie, metadatos). public/ se regenera completo
en cada ejecución: no editar archivos dentro de public/.
"""
import hashlib
import json
import shutil
import sys
from urllib.parse import quote
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup, escape

from blog import load_posts, long_date
from casos import CASES, PENDIENTE
from dashboards import EXAMPLES
from pipeline import pipeline


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
        'template': 'inteligencia-artificial.html', 'path': '/inteligencia-artificial/', 'nav': 'ia',
        'title': 'Inteligencia artificial para empresas: agentes de IA con tus datos | DeepDatas',
        'description': 'Agentes de IA conectados a los datos de tu empresa: consultas a tus indicadores, tus números en WhatsApp o Teams, pedidos automáticos, alertas y pronósticos, con datos curados y seguros.',
    },
    {
        'template': 'diagnostico.html', 'path': '/diagnostico/', 'nav': 'diagnostico',
        'title': 'Diagnóstico de datos | DeepDatas',
        'description': 'En dos semanas relevamos tus fuentes de datos, medimos su calidad y te entregamos una hoja de ruta priorizada para decidir mejor y aprovechar la inteligencia artificial.',
    },
    {
        'template': 'autoevaluacion.html', 'path': '/autoevaluacion/', 'nav': 'autoevaluacion',
        'title': 'Autoevaluación: ¿qué tan listos están tus datos para la IA? | DeepDatas',
        'description': 'Seis preguntas y dos minutos para saber en qué punto están los datos de tu empresa, qué priorizar y cómo prepararte para aplicar inteligencia artificial.',
    },
    {
        'template': 'casos.html', 'path': '/casos/', 'nav': 'casos', 'requires_cases': True,
        'title': 'Casos de éxito | DeepDatas',
        'description': 'Proyectos reales de integración de datos, tableros de gestión y modelos predictivos, con los resultados que obtuvieron nuestros clientes.',
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
        'template': 'privacidad.html', 'path': '/privacidad/', 'nav': None,
        'title': 'Política de privacidad | DeepDatas',
        'description': 'Qué datos recibe DeepDatas a través de su sitio, para qué los usa y cómo ejercer tus derechos según la Ley 25.326.',
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


ICON_STROKE = '1.75'


def _icon_source(name):
    """Contenido de un ícono de src/icons: Lucide (trazo, 24 px) o Bootstrap (relleno, 16 px)."""
    svg = (SRC / 'icons' / f'{name}.svg').read_text(encoding='utf-8')
    svg = svg[svg.index('<svg'):]
    head_end = svg.index('>') + 1
    head, inner = svg[:head_end], svg[head_end:svg.rindex('</svg>')]
    stroke = 'stroke="currentColor"' in head
    viewbox = head.split('viewBox="', 1)[1].split('"', 1)[0]
    return ' '.join(inner.split()), stroke, viewbox


def icon(name, label=None, cls=''):
    """Inserta un ícono SVG de src/icons (Lucide, licencia ISC; WhatsApp de Bootstrap Icons, MIT)."""
    inner, stroke, viewbox = _icon_source(name)
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true" focusable="false"'
    paint = (f'fill="none" stroke="currentColor" stroke-width="{ICON_STROKE}" stroke-linecap="round" stroke-linejoin="round"'
             if stroke else 'fill="currentColor"')
    classes = f'icon {cls}'.strip()
    return Markup(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" class="{classes}" {paint} {a11y}>{inner}</svg>')


def icon_svg(name, x, y, size, cls=''):
    """Dibuja un ícono dentro de un SVG (en la posición y el tamaño indicados)."""
    inner, stroke, viewbox = _icon_source(name)
    box = float(viewbox.split()[2])
    paint = (f'fill="none" stroke="currentColor" stroke-width="{ICON_STROKE}" stroke-linecap="round" stroke-linejoin="round"'
             if stroke else 'fill="currentColor"')
    return Markup(f'<g class="{cls}" transform="translate({x:.1f} {y:.1f}) scale({size / box:.4f})" {paint} '
                  f'aria-hidden="true">{inner}</g>')


# Analítica de visitas con Microsoft Clarity. Vacío = desactivada (no se carga
# ningún script externo y la política de seguridad no se modifica).
CLARITY_ID = 'ytmns2p931'
CLARITY_CSP = {
    'script-src': 'https://www.clarity.ms https://scripts.clarity.ms',
    'connect-src': 'https://*.clarity.ms https://c.bing.com',
    'img-src': 'https://*.clarity.ms https://c.bing.com',
}


def swa_config():
    """Configuración de Azure Static Web Apps. Si la analítica está activa,
    habilita en la política de seguridad solo los dominios de Clarity."""
    config = json.loads((SRC / 'staticwebapp.config.json').read_text(encoding='utf-8'))
    if CLARITY_ID:
        headers = config['globalHeaders']
        rules = [r.strip() for r in headers['Content-Security-Policy'].split(';')]
        for i, rule in enumerate(rules):
            name = rule.split(' ', 1)[0]
            if name in CLARITY_CSP:
                rules[i] = f'{rule} {CLARITY_CSP[name]}'
        headers['Content-Security-Policy'] = '; '.join(rules)
    return json.dumps(config, ensure_ascii=False, indent=2) + '\n'


# Tema visual: 'claro' u 'oscuro'. Define los colores (site.css, [data-theme]),
# la escena del inicio (src/hero.json: foto de oficina o ilustración de noche)
# y la versión de los objetos de vidrio.
THEME = 'claro'
THEME_COLOR = {'claro': '#fafaf8', 'oscuro': '#07090e'}
# Imagen para compartir en redes (captura del inicio con el tema correspondiente)
OG_IMAGE = {'claro': 'og-image-claro.jpg', 'oscuro': 'og-image.jpg'}


def glass(name, size=256):
    """Imagen de un objeto de vidrio (tools/glass_icons.py) para el tema activo."""
    suffix = '-claro' if THEME == 'claro' else ''
    return f'/assets/img/glass/{name}{suffix}-{size}.webp'


def hero_scene():
    """Escena del inicio del tema activo (src/hero.json), con las rutas de sus imágenes."""
    scene = json.loads((SRC / 'hero.json').read_text(encoding='utf-8'))[THEME]

    def layer(name):
        if not name:
            return None
        files = [(f'/assets/img/hero/{name}-{w}.webp', w) for w in scene['widths']]
        return {'src': files[0][0], 'srcset': ', '.join(f'{src} {w}w' for src, w in files)}

    config = {k: scene[k] for k in ('w', 'h', 'screen', 'cover', 'desk', 'mob')}
    return {**scene, 'back': layer(scene['img']), 'front_img': layer(scene['front']),
            'config': json.dumps(config, separators=(',', ':'))}


# Enlace para agendar una llamada (página de Microsoft Bookings o Calendly). Con un enlace, los
# botones «Coordinar llamada» abren la agenda en otra pestaña y Contacto la ofrece primero.
# Vacío = los botones llevan al formulario de contacto.
BOOKING_URL = ''


def booking_url(interest='llamada'):
    return BOOKING_URL or f'/contacto/?interes={interest}'


def booking_link(interest='llamada'):
    """Atributos del enlace para agendar: abre la agenda externa en otra pestaña."""
    extra = ' target="_blank" rel="noopener" data-booking' if BOOKING_URL else ''
    return Markup(f'href="{escape(booking_url(interest))}"{extra}')


WHATSAPP_NUMBER = '5491161527387'
# Mensaje con el que se abre el chat de WhatsApp, según la página desde la que se escribe.
WHATSAPP_MESSAGES = {
    None: 'Hola, vengo de la web de DeepDatas y quiero hacer una consulta.',
    'servicios': 'Hola, vengo de la web de DeepDatas y quiero consultar por sus servicios.',
    'diagnostico': 'Hola, vengo de la web de DeepDatas y me interesa el diagnóstico de datos.',
    'casos': 'Hola, vengo de la web de DeepDatas, vi sus casos de éxito y quiero consultar por un proyecto.',
    'ia': 'Hola, vengo de la web de DeepDatas y me interesa aplicar inteligencia artificial en mi empresa.',
    'autoevaluacion': 'Hola, hice la autoevaluación de datos en la web de DeepDatas y quiero consultar por los próximos pasos.',
    'ejemplos': 'Hola, vengo de la web de DeepDatas, vi los tableros de ejemplo y quiero consultar por uno para mi empresa.',
}


def whatsapp(nav=None):
    """Enlace a WhatsApp con un mensaje inicial acorde a la página."""
    text = WHATSAPP_MESSAGES.get(nav, WHATSAPP_MESSAGES[None])
    return f'https://wa.me/{WHATSAPP_NUMBER}?text={quote(text)}'


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


def published_cases(drafts):
    """Casos a mostrar. Un caso publicado no puede tener datos pendientes."""
    cases = [c for c in CASES if c['publicado'] or drafts]
    for case in cases:
        if case['publicado'] and PENDIENTE in repr(case):
            raise SystemExit(f'El caso "{case["id"]}" está publicado pero tiene datos {PENDIENTE}.')
    return cases


def build(drafts=False):
    cases = published_cases(drafts)
    pages = [p for p in PAGES if cases or not p.get('requires_cases')]
    posts = load_posts(include_future=drafts)
    if posts:
        pages.append({
            'template': 'blog.html', 'path': '/blog/', 'nav': 'blog',
            'title': 'Blog: datos, tableros e inteligencia artificial para empresas | DeepDatas',
            'description': 'Guías prácticas sobre integración y calidad de datos, tableros de gestión, Power BI e inteligencia artificial aplicada a empresas.',
        })
        for post in posts:
            pages.append({
                'template': 'articulo.html', 'path': f'/blog/{post["slug"]}/', 'nav': 'blog', 'post': post,
                'title': f'{post["title"]} | DeepDatas', 'description': post['description'],
            })
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / 'assets', OUT / 'assets')
    (OUT / 'staticwebapp.config.json').write_text(swa_config(), encoding='utf-8')

    env = Environment(
        loader=FileSystemLoader([SRC, SRC / 'pages']),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    pos = Positions()
    env.globals.update(icon=icon, booking_url=booking_url, booking_link=booking_link, booking=BOOKING_URL, posts=posts, long_date=long_date, clarity_id=CLARITY_ID, whatsapp=whatsapp, icon_svg=icon_svg, pipeline=pipeline, asset=asset, hero_chart=hero_chart, pos=pos, examples=EXAMPLES,
                       cases=cases, drafts=drafts, pending=PENDIENTE, site_url=SITE_URL, year=date.today().year,
                       theme=THEME, theme_color=THEME_COLOR[THEME], og_image=f'{SITE_URL}/assets/img/brand/{OG_IMAGE[THEME]}', glass=glass, hero=hero_scene())

    def render_all():
        return [(page, env.get_template(page['template']).render(page=page))
                for page in ({'noindex': drafts, **p} for p in pages)]

    # Primera pasada: junta las posiciones de los gráficos para escribir charts.css.
    # Segunda pasada: las páginas ya pueden enlazar charts.css con su versión.
    render_all()
    (OUT / 'assets' / 'css' / 'charts.css').write_text(pos.css(), encoding='utf-8')
    for page, html in render_all():
        target = output_file(page['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
        print(f'  {page["path"]:<14} -> {target.relative_to(ROOT)}')

    indexable = [p for p in pages if not p.get('noindex')]
    urls = '\n'.join(f'  <url><loc>{SITE_URL}{p["path"]}</loc></url>' for p in indexable)
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{urls}\n</urlset>\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')
    print(f'Sitio generado en {OUT.relative_to(ROOT)}/')


if __name__ == '__main__':
    if '--borradores' in sys.argv:
        # Vista previa con los casos en borrador: no se publica.
        OUT = ROOT / 'vista-previa'
        build(drafts=True)
    else:
        build()
