"""Testimonios de clientes.

Un testimonio son las palabras textuales de un cliente, con su nombre y su
cargo, y opcionalmente su foto y un video corto. Nunca se redacta en nombre del
cliente: el texto lo escribe o lo aprueba él, y se publica solo con su
autorización por escrito. La guía para pedirlos está en contenido/testimonios.md.

Como los casos, cada testimonio se publica solo cuando 'publicado' es True y no
le falta ningún dato ([completar]). Mientras tanto se puede revisar con

    python build.py --borradores

Campos:
- case: caso relacionado de casos.py (se muestra dentro del caso) o None.
- industry: industria de industrias.py (se muestra en su página) o None.
- quote: texto del cliente, en el idioma en que lo dio (normalmente español).
- name, role, company: nombre y apellido, cargo y empresa. Si la empresa no
  autoriza su nombre, usá una descripción ('Distribuidora mayorista').
- photo: foto cuadrada en src/assets/img/testimonios/ (por ejemplo
  'testimonios/nombre-apellido.jpg', 240 x 240 px) o None.
- video: video de unos 30 segundos en src/assets/video/testimonios/ (mp4) o un
  enlace a donde está publicado (https://...), o None. Para un video propio,
  'poster' es la imagen de portada y 'captions' los subtítulos (.vtt).
- consent: cómo y cuándo autorizó la publicación (por ejemplo
  'Email del 12/11/2026'). Es obligatorio para publicar.
- en: traducción para la versión en inglés ('quote', 'role' y opcionalmente
  'company'). Sin traducción, en inglés se muestra el texto original.
"""
from casos import PENDIENTE

TESTIMONIALS = [
    {
        'id': 'distribuidores',
        'publicado': False,
        'case': 'distribuidores',
        'industry': 'consumo',
        'quote': PENDIENTE,
        'name': PENDIENTE,
        'role': PENDIENTE,
        'company': 'Empresa de consumo masivo',
        'photo': None,
        'video': None,
        'poster': None,
        'captions': None,
        'consent': PENDIENTE,
        'en': {'quote': PENDIENTE, 'role': PENDIENTE, 'company': 'Consumer goods company'},
    },
    {
        'id': 'pronostico',
        'publicado': False,
        'case': 'pronostico',
        'industry': 'distribucion',
        'quote': PENDIENTE,
        'name': PENDIENTE,
        'role': PENDIENTE,
        'company': 'Distribuidora mayorista',
        'photo': None,
        'video': None,
        'poster': None,
        'captions': None,
        'consent': PENDIENTE,
        'en': {'quote': PENDIENTE, 'role': PENDIENTE, 'company': 'Wholesale distributor'},
    },
]


def published_testimonials(drafts):
    """Testimonios a mostrar. Uno publicado no puede tener datos pendientes."""
    items = [t for t in TESTIMONIALS if t['publicado'] or drafts]
    for item in items:
        if item['publicado'] and (PENDIENTE in repr(item) or not item['consent']):
            raise SystemExit(f'El testimonio "{item["id"]}" está publicado pero le faltan datos '
                             f'o la autorización del cliente.')
    return items


def localized_testimonials(items, lang):
    """Testimonios con los textos del idioma pedido. 'quote_lang' indica en qué
    idioma está la cita, para marcarla si no coincide con el de la página."""
    result = []
    for item in items:
        texts = item['en'] if lang == 'en' else {}
        translated = bool(texts.get('quote'))
        result.append({**item, **texts, 'quote_lang': lang if translated or lang == 'es' else 'es',
                       'translated': translated and lang != 'es'})
    return result
