"""Prueba el camino de publicación de casos y testimonios, sin tocar los datos reales.

Ese código solo corre el día que alguien publica un caso o un testimonio, así que
puede estar roto mucho tiempo sin que se note. Este script lo ejercita con datos de
mentira en memoria y controla que haga lo que promete:

- Un testimonio completo en español se publica aunque no tenga traducción al inglés,
  que es opcional: en la página en inglés se muestra la cita original, marcada.
- Una traducción a medio escribir ([completar]) no bloquea la publicación ni se
  muestra: cuenta como «todavía no traducido».
- Falta un dato obligatorio o la autorización del cliente, y la compilación se
  detiene diciendo cuál falta.
- Lo mismo con un caso publicado al que le falta completar algo.

    python tools/probar_publicacion.py

No escribe nada: los datos de prueba viven solo en memoria.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from casos import PENDIENTE  # noqa: E402
import testimonios  # noqa: E402

COMPLETO = {
    'id': 'prueba', 'publicado': True, 'case': None, 'industry': None,
    'quote': 'Una cita de prueba.', 'name': 'Nombre Apellido', 'role': 'Cargo',
    'company': 'Empresa', 'photo': None, 'video': None, 'poster': None, 'captions': None,
    'consent': 'Email del 1/1/2026',
    'en': {'quote': PENDIENTE, 'role': PENDIENTE, 'company': 'Company'},
}

fallas = []


def controlar(que, condicion):
    print(f'  {"ok  " if condicion else "FALLA"}  {que}')
    if not condicion:
        fallas.append(que)


def con(items):
    """Corre la puerta de publicación con estos testimonios, sin tocar los de verdad."""
    guardados = testimonios.TESTIMONIALS
    testimonios.TESTIMONIALS = items
    try:
        return testimonios.published_testimonials(drafts=False), None
    except SystemExit as e:
        return None, str(e)
    finally:
        testimonios.TESTIMONIALS = guardados


print('Testimonios')
publicados, error = con([COMPLETO])
controlar('se publica uno completo aunque no esté traducido', error is None and len(publicados) == 1)

en = testimonios.localized_testimonials([COMPLETO], 'en')[0]
controlar('sin traducción, en inglés se muestra la cita original',
          en['quote'] == COMPLETO['quote'] and en['quote_lang'] == 'es' and not en['translated'])
MOSTRADOS = ('quote', 'name', 'role', 'company')
controlar('una traducción a medio escribir no se muestra',
          not any(en[k] == PENDIENTE for k in MOSTRADOS))
controlar('la parte traducida sí se usa', en['company'] == 'Company')

traducido = {**COMPLETO, 'en': {'quote': 'A test quote.', 'role': 'Role'}}
en2 = testimonios.localized_testimonials([traducido], 'en')[0]
controlar('con traducción, en inglés se usa y se marca como traducida',
          en2['quote'] == 'A test quote.' and en2['translated'] and en2['quote_lang'] == 'en')
es2 = testimonios.localized_testimonials([traducido], 'es')[0]
controlar('en español nunca se marca como traducida', es2['quote'] == COMPLETO['quote'] and not es2['translated'])

for campo in testimonios.OBLIGATORIOS:
    _, error = con([{**COMPLETO, campo: PENDIENTE}])
    controlar(f'se detiene si falta «{campo}» y lo nombra', error is not None and campo in error)

_, error = con([{**COMPLETO, 'publicado': False, 'quote': PENDIENTE}])
controlar('un borrador incompleto no detiene la compilación', error is None)

print('\nCasos')
import build  # noqa: E402

guardados = build.CASES
build.CASES = [{'id': 'prueba', 'publicado': True, 'client': 'Empresa', 'results': [(PENDIENTE, 'cosas')],
                'duration': None, 'title': 'T', 'summary': 's', 'challenge': 'c', 'solution': 's',
                'outcome': 'o', 'sources': [], 'stack': [], 'logo': None, 'industry': 'i', 'example': None}]
try:
    build.published_cases(drafts=False)
    controlar('se detiene si un caso publicado tiene datos sin completar', False)
except SystemExit as e:
    controlar('se detiene si un caso publicado tiene datos sin completar y los nombra',
              'results' in str(e))
finally:
    build.CASES = guardados

print()
if fallas:
    raise SystemExit(f'{len(fallas)} control(es) fallaron.')
print('Todo en orden.')
