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

from jinja2 import Environment, FileSystemLoader, StrictUndefined, pass_context
from markupsafe import Markup, escape

from blog import load_posts, long_date
from casos import CASES, PENDIENTE, localized_cases
from dashboards import EXAMPLES
from pipeline import pipeline
from i18n import LANGS, ROUTES, UI, route
from industrias import LABELS as INDUSTRY_LABELS, industries
from testimonios import localized_testimonials, published_testimonials


ROOT = Path(__file__).parent
SRC = ROOT / 'src'
OUT = ROOT / 'public'
SITE_URL = 'https://deepdatas.com'

# Páginas del sitio: plantilla, ruta pública, título y descripción para buscadores.
PAGES = [
    {
        'template': 'index.html', 'key': 'inicio', 'path': '/', 'nav': 'inicio',
        'title': 'DeepDatas | Datos e IA para distribuidoras, pymes y consumo masivo',
        'description': 'Consultora de datos e IA para distribuidoras, pymes y empresas de consumo masivo: integramos tu ERP, tus planillas y las ventas de tus distribuidores en tableros, pronósticos y agentes de IA, sin que necesites un equipo de datos propio.',
    },
    {
        'template': 'servicios.html', 'key': 'servicios', 'path': '/servicios/', 'nav': 'servicios',
        'title': 'Servicios | DeepDatas',
        'description': 'Ingeniería de datos, calidad y preparación, analítica avanzada con modelos predictivos y tableros de gestión en Power BI. Un solo equipo para todo el ciclo de vida de tus datos.',
    },
    {
        'template': 'inteligencia-artificial.html', 'key': 'ia', 'path': '/inteligencia-artificial/', 'nav': 'ia',
        'title': 'Inteligencia artificial para empresas: agentes de IA con tus datos | DeepDatas',
        'description': 'Agentes de IA conectados a los datos de tu empresa: consultas a tus indicadores, tus números en WhatsApp o Teams, pedidos automáticos, alertas y pronósticos, con datos curados y seguros.',
    },
    {
        'template': 'diagnostico.html', 'key': 'diagnostico', 'path': '/diagnostico/', 'nav': 'diagnostico',
        'title': 'Diagnóstico de datos | DeepDatas',
        'description': 'En dos semanas relevamos tus fuentes de datos, medimos su calidad y te entregamos una hoja de ruta priorizada para decidir mejor y aprovechar la inteligencia artificial.',
    },
    {
        'template': 'autoevaluacion.html', 'key': 'autoevaluacion', 'path': '/autoevaluacion/', 'nav': 'autoevaluacion',
        'title': 'Autoevaluación: ¿qué tan listos están tus datos para la IA? | DeepDatas',
        'description': 'Seis preguntas y dos minutos para saber en qué punto están los datos de tu empresa, qué priorizar y cómo prepararte para aplicar inteligencia artificial.',
    },
    {
        'template': 'casos.html', 'key': 'casos', 'path': '/casos/', 'nav': 'casos', 'requires_cases': True,
        'title': 'Casos de éxito | DeepDatas',
        'description': 'Proyectos reales de integración de datos, tableros de gestión y modelos predictivos, con los resultados que obtuvieron nuestros clientes.',
    },
    {
        'template': 'ejemplos.html', 'key': 'ejemplos', 'path': '/ejemplos/', 'nav': 'ejemplos',
        'title': 'Ejemplos de tableros | DeepDatas',
        'description': 'Tableros interactivos de ejemplo, con datos ficticios: performance de distribuidores, cobertura de puntos de venta y pronóstico de demanda.',
    },
    {
        'template': 'nosotros.html', 'key': 'nosotros', 'path': '/nosotros/', 'nav': 'nosotros',
        'title': 'Nosotros | DeepDatas',
        'description': 'Somos un equipo de especialistas en datos con más de 10 años de experiencia, con base en Buenos Aires, Argentina.',
    },
    {
        'template': 'contacto.html', 'key': 'contacto', 'path': '/contacto/', 'nav': 'contacto',
        'title': 'Contacto | DeepDatas',
        'description': 'Contanos tu desafío y coordinamos una reunión de diagnóstico sin costo. Bernardo de Irigoyen 330, CABA, Argentina.',
    },
    {
        'template': 'privacidad.html', 'key': 'privacidad', 'path': '/privacidad/', 'nav': None,
        'title': 'Política de privacidad | DeepDatas',
        'description': 'Qué datos recibe DeepDatas a través de su sitio, para qué los usa y cómo ejercer tus derechos según la Ley 25.326.',
    },
    {
        'template': 'gracias.html', 'key': 'gracias', 'path': '/gracias/', 'nav': None, 'noindex': True,
        'title': 'Mensaje enviado | DeepDatas',
        'description': 'Gracias por escribirnos.',
    },
    {
        'template': '404.html', 'path': '/404.html', 'nav': None, 'noindex': True,
        'title': 'Página no encontrada | DeepDatas',
        'description': 'La página que buscás no existe.',
    },
]

# Versión en inglés (src/pages/en/). Las rutas salen de i18n.ROUTES.
PAGES_EN = [
    {
        'template': 'en/index.html', 'key': 'inicio', 'nav': 'inicio',
        'title': 'DeepDatas | Data and AI for distributors, SMEs and consumer goods',
        'description': 'Data and AI consultancy for distributors, small and midsize businesses and consumer goods companies: we turn your ERP, spreadsheets and distributor sales into dashboards, forecasts and AI agents, no in-house data team required.',
    },
    {
        'template': 'en/servicios.html', 'key': 'servicios', 'nav': 'servicios',
        'title': 'Services | DeepDatas',
        'description': 'Data engineering, data quality and preparation, advanced analytics with predictive models and Power BI dashboards. One team for the whole data lifecycle.',
    },
    {
        'template': 'en/inteligencia-artificial.html', 'key': 'ia', 'nav': 'ia',
        'title': 'AI for business: AI agents connected to your data | DeepDatas',
        'description': 'AI agents connected to your company data: ask about your KPIs, get your numbers on WhatsApp or Teams, automate orders, alerts and forecasts, with curated, secure data.',
    },
    {
        'template': 'en/diagnostico.html', 'key': 'diagnostico', 'nav': 'diagnostico',
        'title': 'Data assessment | DeepDatas',
        'description': 'In two weeks we map your data sources, measure their quality and deliver a prioritized roadmap to make better decisions and put artificial intelligence to work.',
    },
    {
        'template': 'en/autoevaluacion.html', 'key': 'autoevaluacion', 'nav': 'autoevaluacion',
        'title': 'AI readiness check: is your data ready for AI? | DeepDatas',
        'description': 'Six questions and two minutes to find out where your company’s data stands, what to prioritize and how to get ready to apply artificial intelligence.',
    },
    {
        'template': 'en/casos.html', 'key': 'casos', 'nav': 'casos', 'requires_cases': True,
        'title': 'Case studies | DeepDatas',
        'description': 'Real data integration, dashboard and predictive modeling projects, with the results our clients achieved.',
    },
    {
        'template': 'en/ejemplos.html', 'key': 'ejemplos', 'nav': 'ejemplos',
        'title': 'Dashboard examples | DeepDatas',
        'description': 'Interactive sample dashboards with fictional data: distributor performance, point-of-sale coverage and demand forecasting.',
    },
    {
        'template': 'en/nosotros.html', 'key': 'nosotros', 'nav': 'nosotros',
        'title': 'About us | DeepDatas',
        'description': 'A team of data specialists with more than 10 years of experience, based in Buenos Aires, Argentina.',
    },
    {
        'template': 'en/contacto.html', 'key': 'contacto', 'nav': 'contacto',
        'title': 'Contact | DeepDatas',
        'description': 'Tell us about your challenge and we will set up a free first conversation. Bernardo de Irigoyen 330, Buenos Aires, Argentina.',
    },
    {
        'template': 'en/privacidad.html', 'key': 'privacidad', 'nav': None,
        'title': 'Privacy policy | DeepDatas',
        'description': 'What data DeepDatas receives through its website, what it is used for and how to exercise your rights under Argentine Law 25,326.',
    },
    {
        'template': 'en/gracias.html', 'key': 'gracias', 'nav': None, 'noindex': True,
        'title': 'Message sent | DeepDatas',
        'description': 'Thank you for reaching out.',
    },
]
for _page in PAGES_EN:
    _page.update(lang='en', path=ROUTES[_page['key']]['en'])


def industry_pages():
    """Una página por industria y por idioma (industrias.py), con la plantilla industria.html."""
    pages = []
    for lang in LANGS:
        items = industries(lang)
        for ind in items:
            key = f'ind-{ind["id"]}'
            pages.append({
                'template': 'industria.html', 'key': key, 'lang': lang, 'path': ROUTES[key][lang], 'nav': key,
                'title': ind['title'], 'description': ind['description'],
                'industry': ind, 'labels': INDUSTRY_LABELS[lang],
                'others': [other for other in items if other['id'] != ind['id']],
            })
    return pages


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
BOOKING_URL = 'https://bookings.cloud.microsoft/book/DeepDatas@deepdatas.com/'


@pass_context
def booking_url(ctx, interest='llamada'):
    return BOOKING_URL or f"{route('contacto', ctx.get('lang', 'es'))}?interes={interest}"


@pass_context
def booking_link(ctx, interest='llamada'):
    """Atributos del enlace para agendar: abre la agenda externa en otra pestaña."""
    extra = ' target="_blank" rel="noopener" data-booking' if BOOKING_URL else ''
    return Markup(f'href="{escape(booking_url(ctx, interest))}"{extra}')


@pass_context
def url(ctx, key):
    """Ruta de una página en el idioma de la página actual."""
    return route(key, ctx.get('lang', 'es'))


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
    'ind-consumo': 'Hola, vengo de la web de DeepDatas. Trabajo en una empresa de consumo masivo y quiero hacer una consulta.',
    'ind-distribucion': 'Hola, vengo de la web de DeepDatas. Trabajo en una distribuidora y quiero hacer una consulta.',
    'ind-pymes': 'Hola, vengo de la web de DeepDatas. Tengo una pyme y quiero hacer una consulta.',
    'ind-retail': 'Hola, vengo de la web de DeepDatas. Trabajo en retail y quiero hacer una consulta.',
    'ind-materiales': 'Hola, vengo de la web de DeepDatas. Trabajo en una distribuidora de materiales y quiero hacer una consulta.',
    'ind-autopartes': 'Hola, vengo de la web de DeepDatas. Trabajo en autopartes y repuestos y quiero hacer una consulta.',
    'ind-industria': 'Hola, vengo de la web de DeepDatas. Trabajo en una empresa industrial y quiero hacer una consulta.',
    'ind-agro': 'Hola, vengo de la web de DeepDatas. Trabajo en el agro y quiero hacer una consulta.',
    'ind-salud': 'Hola, vengo de la web de DeepDatas. Trabajo en un laboratorio o empresa de salud y quiero hacer una consulta.',
}
WHATSAPP_MESSAGES_EN = {
    None: "Hi, I'm coming from the DeepDatas website and I have a question.",
    'servicios': "Hi, I'm coming from the DeepDatas website and I'd like to ask about your services.",
    'diagnostico': "Hi, I'm coming from the DeepDatas website and I'm interested in the data assessment.",
    'casos': "Hi, I'm coming from the DeepDatas website. I saw your case studies and I'd like to discuss a project.",
    'ia': "Hi, I'm coming from the DeepDatas website and I'm interested in applying AI in my company.",
    'autoevaluacion': "Hi, I took the AI readiness check on the DeepDatas website and I'd like to discuss next steps.",
    'ejemplos': "Hi, I'm coming from the DeepDatas website. I saw the sample dashboards and I'd like to ask about one for my company.",
    'ind-consumo': "Hi, I'm coming from the DeepDatas website. I work at a consumer goods company and I have a question.",
    'ind-distribucion': "Hi, I'm coming from the DeepDatas website. I work at a distribution company and I have a question.",
    'ind-pymes': "Hi, I'm coming from the DeepDatas website. I run a small or midsize business and I have a question.",
    'ind-retail': "Hi, I'm coming from the DeepDatas website. I work in retail and I have a question.",
    'ind-materiales': "Hi, I'm coming from the DeepDatas website. I work at a supply distribution company and I have a question.",
    'ind-autopartes': "Hi, I'm coming from the DeepDatas website. I work in auto parts and I have a question.",
    'ind-industria': "Hi, I'm coming from the DeepDatas website. I work at a manufacturing company and I have a question.",
    'ind-agro': "Hi, I'm coming from the DeepDatas website. I work in agribusiness and I have a question.",
    'ind-salud': "Hi, I'm coming from the DeepDatas website. I work at a pharmaceutical or healthcare company and I have a question.",
}


@pass_context
def whatsapp(ctx, nav=None):
    """Enlace a WhatsApp con un mensaje inicial acorde a la página y al idioma."""
    messages = WHATSAPP_MESSAGES_EN if ctx.get('lang') == 'en' else WHATSAPP_MESSAGES
    text = messages.get(nav, messages[None])
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


def alternates(page):
    """Versiones de la página en cada idioma, para hreflang y el selector de idioma."""
    key = page.get('key')
    if not key or page.get('post'):
        return {}
    return {lang: path for lang, path in ROUTES[key].items() if path}


def build(drafts=False):
    cases = published_cases(drafts)
    testimonials = published_testimonials(drafts)
    pages = [p for p in PAGES + PAGES_EN if cases or not p.get('requires_cases')] + industry_pages()
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
    env.globals.update(icon=icon, booking_url=booking_url, booking_link=booking_link, booking=BOOKING_URL, posts=posts, url=url, long_date=long_date, clarity_id=CLARITY_ID, whatsapp=whatsapp, icon_svg=icon_svg, pipeline=pipeline, asset=asset, hero_chart=hero_chart, pos=pos,
                       cases=cases, drafts=drafts, pending=PENDIENTE, site_url=SITE_URL, year=date.today().year,
                       theme=THEME, theme_color=THEME_COLOR[THEME], og_image=f'{SITE_URL}/assets/img/brand/{OG_IMAGE[THEME]}', glass=glass, hero=hero_scene())

    def render(page):
        lang = page.get('lang', 'es')
        return env.get_template(page['template']).render(
            page=page, lang=lang, t=UI[lang], alt=alternates(page),
            examples=EXAMPLES[lang], cases=localized_cases(cases, lang),
            testimonials=localized_testimonials(testimonials, lang), industries=industries(lang))

    def render_all():
        return [(page, render(page)) for page in ({'noindex': drafts, **p} for p in pages)]

    # Primera pasada: junta las posiciones de los gráficos para escribir charts.css.
    # Segunda pasada: las páginas ya pueden enlazar charts.css con su versión.
    render_all()
    (OUT / 'assets' / 'css' / 'charts.css').write_text(pos.css(), encoding='utf-8')
    for page, html in render_all():
        target = output_file(page['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
        print(f'  {page["path"]:<14} -> {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}')

    indexable = [p for p in pages if not p.get('noindex')]
    entries = []
    for p in indexable:
        links = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{lang}" href="{SITE_URL}{path}"/>'
                        for lang, path in alternates(p).items()) if len(alternates(p)) > 1 else ''
        entries.append(f'  <url><loc>{SITE_URL}{p["path"]}</loc>{links}</url>')
    urls = '\n'.join(entries)
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f'{urls}\n</urlset>\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')
    print(f'Sitio generado en {OUT.relative_to(ROOT) if OUT.is_relative_to(ROOT) else OUT}/')


if __name__ == '__main__':
    if '--borradores' in sys.argv:
        # Vista previa con los casos en borrador: no se publica.
        OUT = ROOT / 'vista-previa'
        build(drafts=True)
    else:
        build()
