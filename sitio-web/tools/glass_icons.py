"""Genera los íconos 3D de vidrio del sitio (SVG) en tools/glass/.

Después se convierten en imágenes WebP con fondo transparente en
src/assets/img/glass/. Uso:

    python tools/glass_icons.py
    node tools/render_glass.cjs
    python tools/glass_webp.py

Los colores siguen la marca: vidrio translúcido con reflejos blancos y un
núcleo naranja que brilla a través de las caras.
"""
from pathlib import Path

OUT = Path(__file__).parent / 'glass'
ORANGE = '#ff6b1a'
ORANGE_LIGHT = '#ffb07a'
ORANGE_DEEP = '#c2410c'

DEFS = f'''
<defs>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.55"/>
    <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.10"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.22"/>
  </linearGradient>
  <linearGradient id="glassDark" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.04"/>
  </linearGradient>
  <linearGradient id="glassSide" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.30"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.06"/>
  </linearGradient>
  <linearGradient id="core" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{ORANGE_LIGHT}"/>
    <stop offset="0.55" stop-color="{ORANGE}"/>
    <stop offset="1" stop-color="{ORANGE_DEEP}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/>
    <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.25"/>
    <stop offset="1" stop-color="{ORANGE_LIGHT}" stop-opacity="0.8"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{ORANGE}" stop-opacity="0.55"/>
    <stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/>
  </radialGradient>
  <filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur14" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
</defs>
'''


def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{DEFS}{body}</svg>\n'


def pts(*p):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in p)


def iso_box(cx, top, w, d, h, core=False, opacity=1.0):
    """Prisma isométrico de vidrio. cx: centro, top: y del vértice superior."""
    a, b = w * 0.866, w * 0.5          # medio ancho en x / y de la cara superior
    T = (cx, top); R = (cx + a, top + b); F = (cx, top + 2 * b); L = (cx - a, top + b)
    Rb, Fb, Lb = (R[0], R[1] + h), (F[0], F[1] + h), (L[0], L[1] + h)
    out = [f'<g opacity="{opacity}">']
    if core:
        out.append(f'<polygon points="{pts(L, F, Fb, Lb)}" fill="url(#core)" opacity="0.85"/>')
        out.append(f'<polygon points="{pts(F, R, Rb, Fb)}" fill="{ORANGE_DEEP}" opacity="0.8"/>')
        out.append(f'<polygon points="{pts(T, R, F, L)}" fill="{ORANGE_LIGHT}" opacity="0.9"/>')
    out.append(f'<polygon points="{pts(L, F, Fb, Lb)}" fill="url(#glassSide)"/>')
    out.append(f'<polygon points="{pts(F, R, Rb, Fb)}" fill="url(#glassDark)"/>')
    out.append(f'<polygon points="{pts(T, R, F, L)}" fill="url(#glass)"/>')
    out.append(f'<polyline points="{pts(L, T, R)}" fill="none" stroke="#fff" stroke-opacity="0.9" stroke-width="2.5" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pts(L, F, R)}" fill="none" stroke="#fff" stroke-opacity="0.55" stroke-width="2" stroke-linejoin="round"/>')
    out.append(f'<line x1="{F[0]}" y1="{F[1]}" x2="{Fb[0]}" y2="{Fb[1]}" stroke="#fff" stroke-opacity="0.7" stroke-width="2.5"/>')
    out.append(f'<polyline points="{pts(L, Lb, Fb, Rb, R)}" fill="none" stroke="url(#edge)" stroke-width="2" stroke-linejoin="round"/>')
    out.append('</g>')
    return '\n'.join(out)


def cube():
    body = ['<ellipse cx="256" cy="300" rx="190" ry="170" fill="url(#glow)"/>']
    # Núcleo naranja dentro del cubo de vidrio
    body.append(f'<g filter="url(#blur2)">{iso_box(256, 200, 62, 0, 62, core=True)}</g>')
    body.append(iso_box(256, 92, 150, 0, 160))
    # Reflejos
    body.append('<path d="M150 190 L240 140" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity="0.65" filter="url(#blur2)"/>')
    body.append('<path d="M140 220 L140 300" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.45" filter="url(#blur2)"/>')
    return svg('\n'.join(body))


def bars():
    body = ['<ellipse cx="256" cy="330" rx="210" ry="150" fill="url(#glow)"/>']
    for i, (h, core) in enumerate([(90, False), (150, False), (220, True)]):
        cx = 150 + i * 105
        base = 420 - i * 0
        top = base - h - 60
        body.append(iso_box(cx, top + i * -0, 52, 0, h, core=core))
    body.append('<path d="M110 300 L118 230" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.5" filter="url(#blur2)"/>')
    # Flecha de tendencia
    body.append(f'<path d="M96 250 Q220 210 300 150 T420 70" fill="none" stroke="{ORANGE_LIGHT}" stroke-width="7" stroke-linecap="round" opacity="0.95"/>')
    body.append(f'<path d="M398 66 L424 66 L420 92" fill="none" stroke="{ORANGE_LIGHT}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg('\n'.join(body))


def disc(cy, rx, ry, h, core=False):
    out = []
    side = f'M{256 - rx} {cy} A{rx} {ry} 0 0 0 {256 + rx} {cy} L{256 + rx} {cy + h} A{rx} {ry} 0 0 1 {256 - rx} {cy + h} Z'
    if core:
        out.append(f'<path d="{side}" fill="url(#core)" opacity="0.75"/>')
    out.append(f'<path d="{side}" fill="url(#glassSide)"/>')
    out.append(f'<ellipse cx="256" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#glass)" stroke="#fff" stroke-opacity="0.85" stroke-width="2.5"/>')
    out.append(f'<path d="M{256 - rx} {cy + h} A{rx} {ry} 0 0 0 {256 + rx} {cy + h}" fill="none" stroke="url(#edge)" stroke-width="2.5"/>')
    out.append(f'<line x1="{256 - rx}" y1="{cy}" x2="{256 - rx}" y2="{cy + h}" stroke="#fff" stroke-opacity="0.6" stroke-width="2"/>')
    out.append(f'<line x1="{256 + rx}" y1="{cy}" x2="{256 + rx}" y2="{cy + h}" stroke="#fff" stroke-opacity="0.4" stroke-width="2"/>')
    return '\n'.join(out)


def database():
    body = ['<ellipse cx="256" cy="290" rx="200" ry="190" fill="url(#glow)"/>']
    for i, core in enumerate([False, True, False]):
        body.append(disc(330 - i * 92, 150, 48, 62, core=core))
    body.append('<path d="M128 150 Q150 128 200 120" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.7" filter="url(#blur2)"/>')
    # Puntos de datos
    for x, y in [(206, 160), (256, 148), (306, 160)]:
        body.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{ORANGE_LIGHT}"/>')
    return svg('\n'.join(body))


def funnel():
    body = ['<ellipse cx="256" cy="270" rx="200" ry="200" fill="url(#glow)"/>']
    # Partículas que entran (datos sueltos)
    for x, y, r, c in [(150, 70, 9, '#fff'), (210, 50, 7, ORANGE_LIGHT), (300, 62, 10, '#fff'), (350, 84, 6, ORANGE_LIGHT), (250, 86, 6, '#fff')]:
        body.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="0.85"/>')
    cone = 'M96 150 A160 46 0 0 0 416 150 L296 330 L296 420 A40 12 0 0 1 216 420 L216 330 Z'
    body.append(f'<path d="M216 330 L296 330 L296 420 A40 12 0 0 1 216 420 Z" fill="url(#core)" opacity="0.8"/>')
    body.append(f'<path d="{cone}" fill="url(#glassSide)" stroke="url(#edge)" stroke-width="2.5" stroke-linejoin="round"/>')
    body.append('<ellipse cx="256" cy="150" rx="160" ry="46" fill="url(#glass)" stroke="#fff" stroke-opacity="0.9" stroke-width="2.5"/>')
    body.append('<ellipse cx="256" cy="330" rx="40" ry="12" fill="none" stroke="#fff" stroke-opacity="0.6" stroke-width="2"/>')
    body.append('<path d="M120 180 L222 318" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.55" filter="url(#blur2)"/>')
    # Gota limpia que sale
    body.append(f'<circle cx="256" cy="462" r="13" fill="{ORANGE}"/>')
    body.append('<circle cx="252" cy="458" r="4" fill="#fff" opacity="0.8"/>')
    return svg('\n'.join(body))


def sphere():
    body = ['<circle cx="256" cy="256" r="220" fill="url(#glow)"/>']
    # Órbita detrás
    body.append(f'<ellipse cx="256" cy="256" rx="196" ry="64" transform="rotate(-18 256 256)" fill="none" stroke="{ORANGE_LIGHT}" stroke-opacity="0.35" stroke-width="3"/>')
    body.append('''
<radialGradient id="ball" cx="0.35" cy="0.3" r="0.75">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.65"/>
  <stop offset="0.35" stop-color="#ffffff" stop-opacity="0.12"/>
  <stop offset="0.8" stop-color="#ff6b1a" stop-opacity="0.18"/>
  <stop offset="1" stop-color="#ffb07a" stop-opacity="0.7"/>
</radialGradient>''')
    # Red neuronal interior
    nodes = [(206, 210), (300, 196), (256, 260), (196, 300), (314, 300), (256, 330)]
    links = [(0, 2), (1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (0, 3), (1, 4)]
    for a, b in links:
        body.append(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="{ORANGE_LIGHT}" stroke-width="3" opacity="0.8"/>')
    body.append(f'<circle cx="256" cy="260" r="34" fill="url(#core)" filter="url(#blur2)"/>')
    for x, y in nodes:
        body.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{ORANGE}" stroke="#fff" stroke-width="2"/>')
    body.append('<circle cx="256" cy="256" r="150" fill="url(#ball)" stroke="url(#edge)" stroke-width="3"/>')
    body.append('<ellipse cx="196" cy="176" rx="46" ry="24" transform="rotate(-35 196 176)" fill="#fff" opacity="0.55" filter="url(#blur6)"/>')
    # Órbita delante
    body.append(f'<path d="M60 256 A196 64 0 0 0 452 256" transform="rotate(-18 256 256)" fill="none" stroke="{ORANGE_LIGHT}" stroke-width="4" opacity="0.9"/>')
    body.append(f'<circle cx="420" cy="170" r="12" fill="{ORANGE}" stroke="#fff" stroke-width="2.5"/>')
    return svg('\n'.join(body))


def ring():
    body = ['<ellipse cx="256" cy="256" rx="230" ry="190" fill="url(#glow)"/>']
    body.append('''
<linearGradient id="ringStroke" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.7"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.12"/>
  <stop offset="1" stop-color="#ffb07a" stop-opacity="0.75"/>
</linearGradient>''')
    # Anillo grueso de vidrio inclinado (toroide simplificado)
    body.append(f'<ellipse cx="256" cy="262" rx="170" ry="120" fill="none" stroke="{ORANGE}" stroke-opacity="0.55" stroke-width="58" filter="url(#blur6)"/>')
    body.append('<ellipse cx="256" cy="256" rx="170" ry="120" fill="none" stroke="url(#ringStroke)" stroke-width="64"/>')
    body.append('<ellipse cx="256" cy="256" rx="202" ry="152" fill="none" stroke="#fff" stroke-opacity="0.85" stroke-width="2.5"/>')
    body.append('<ellipse cx="256" cy="256" rx="138" ry="88" fill="none" stroke="#fff" stroke-opacity="0.6" stroke-width="2"/>')
    body.append('<path d="M96 210 A170 120 0 0 1 220 140" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity="0.7" filter="url(#blur2)"/>')
    body.append(f'<path d="M330 380 A170 120 0 0 0 420 300" fill="none" stroke="{ORANGE_LIGHT}" stroke-width="8" stroke-linecap="round" opacity="0.9" filter="url(#blur2)"/>')
    return svg('\n'.join(body))


ICONS = {'cubo': cube, 'barras': bars, 'base-de-datos': database, 'embudo': funnel, 'esfera': sphere, 'anillo': ring}

# Variante para fondo claro: vidrio con tinte azulado, contornos oscuros y halo más suave
LIGHT_DEFS = [
    ('<stop offset="0" stop-color="#ffffff" stop-opacity="0.55"/>\n    <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.10"/>\n    <stop offset="1" stop-color="#ffffff" stop-opacity="0.22"/>',
     '<stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/>\n    <stop offset="0.45" stop-color="#e3eaf4" stop-opacity="0.3"/>\n    <stop offset="1" stop-color="#c3cfe2" stop-opacity="0.5"/>'),
    ('<stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>\n    <stop offset="1" stop-color="#ffffff" stop-opacity="0.04"/>',
     '<stop offset="0" stop-color="#ccd6e6" stop-opacity="0.45"/>\n    <stop offset="1" stop-color="#b3c1d7" stop-opacity="0.35"/>'),
    ('<stop offset="0" stop-color="#ffffff" stop-opacity="0.30"/>\n    <stop offset="1" stop-color="#ffffff" stop-opacity="0.06"/>',
     '<stop offset="0" stop-color="#e8edf5" stop-opacity="0.45"/>\n    <stop offset="1" stop-color="#ccd6e6" stop-opacity="0.35"/>'),
    ('<stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/>\n    <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.25"/>',
     '<stop offset="0" stop-color="#2b3a57" stop-opacity="0.75"/>\n    <stop offset="0.5" stop-color="#5b6b88" stop-opacity="0.45"/>'),
    ('<stop offset="0" stop-color="{0}" stop-opacity="0.55"/>'.format(ORANGE), '<stop offset="0" stop-color="{0}" stop-opacity="0.22"/>'.format(ORANGE)),
]


def light(svg):
    for dark, clear in LIGHT_DEFS:
        assert dark in svg, dark[:40]
        svg = svg.replace(dark, clear)
    # Los filetes blancos sin desenfoque pasan a ser contornos oscuros; los reflejos desenfocados siguen blancos
    lines = []
    for line in svg.split('\n'):
        if 'stroke="#fff"' in line and 'filter=' not in line:
            line = line.replace('stroke="#fff"', 'stroke="#33415f"')
        lines.append(line)
    return '\n'.join(lines)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    (OUT / 'claro').mkdir(exist_ok=True)
    for name, fn in ICONS.items():
        markup = fn()
        (OUT / f'{name}.svg').write_text(markup, encoding='utf-8')
        (OUT / 'claro' / f'{name}.svg').write_text(light(markup), encoding='utf-8')
        print(f'  tools/glass/{name}.svg  tools/glass/claro/{name}.svg')
