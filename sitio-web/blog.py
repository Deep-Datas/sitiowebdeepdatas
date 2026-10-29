"""Artículos del blog, en español (blog/es/) y en inglés (blog/en/).

Cada artículo es un archivo .md con un encabezado así:

    ---
    title: Título del artículo
    seo_title: Título corto para la pestaña      (opcional)
    description: Resumen para buscadores y redes (unas 25 palabras)
    date: 2026-10-06
    tags: Etiqueta 1, Etiqueta 2
    cta: diagnostico        (diagnostico, casos o ia: el llamado a la acción del final)
    es: mi-articulo         (solo en inglés: de qué artículo en español es traducción)
    ---

El nombre del archivo es la dirección del artículo (blog/es/mi-articulo.md ->
/blog/mi-articulo/, blog/en/my-article.md -> /en/blog/my-article/). Un artículo
con fecha futura no se publica hasta que se vuelva a generar el sitio en esa
fecha o después.

El campo «es» es lo que empareja las dos versiones: de ahí salen el hreflang, el
enlace del encabezado al otro idioma y los artículos que muestra cada página de
industria. Un artículo en inglés sin «es» se publica igual, pero queda suelto.
"""
import math
from datetime import date
from pathlib import Path

import markdown
from markupsafe import Markup

BLOG = Path(__file__).parent / 'blog'
WORDS_PER_MINUTE = 200


def _parse(path):
    text = path.read_text(encoding='utf-8')
    _, header, body = text.split('---', 2)
    meta = {}
    for line in header.strip().splitlines():
        key, value = line.split(':', 1)
        meta[key.strip()] = value.strip().strip('"')
    html = markdown.markdown(body, extensions=['tables', 'sane_lists'])
    # Las tablas anchas se desplazan de costado en celulares; el contenedor se
    # puede enfocar para desplazarlas también con el teclado.
    html = (html.replace('<table>', '<div class="table-scroll" tabindex="0" role="region" aria-label="Tabla">\n<table>')
                .replace('</table>', '</table>\n</div>'))
    return {
        'slug': path.stem,
        'title': meta['title'],
        # El título de la pestaña y del buscador puede ser más corto que el que se lee
        # arriba del artículo: ahí entran unos 60 caracteres y después se corta.
        'seo_title': meta.get('seo_title', meta['title']),
        'description': meta['description'],
        'date': date.fromisoformat(meta['date']),
        'tags': [t.strip() for t in meta.get('tags', '').split(',') if t.strip()],
        'cta': meta.get('cta', 'diagnostico'),
        # Solo en inglés: el artículo en español del que es traducción
        'es': meta.get('es'),
        'minutes': max(1, math.ceil(len(body.split()) / WORDS_PER_MINUTE)),
        'html': Markup(html),
    }


def load_posts(lang='es', include_future=False):
    posts = [_parse(p) for p in sorted((BLOG / lang).glob('*.md'))]
    if not include_future:
        posts = [p for p in posts if p['date'] <= date.today()]
    posts = sorted(posts, key=lambda p: (p['date'], p['title']), reverse=True)
    # Artículos relacionados: primero los que comparten más etiquetas, después los más recientes.
    for post in posts:
        others = [o for o in posts if o is not post]
        others.sort(key=lambda o: len(set(o['tags']) & set(post['tags'])), reverse=True)
        post['related'] = others[:3]
        post['lang'] = lang
    return posts


MONTHS = {
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
           'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
           'September', 'October', 'November', 'December'],
}


def long_date(value, lang='es'):
    """La fecha escrita como la escribiría cada idioma."""
    mes = MONTHS[lang][value.month - 1]
    return f'{value.day} de {mes} de {value.year}' if lang == 'es' else f'{mes} {value.day}, {value.year}'
