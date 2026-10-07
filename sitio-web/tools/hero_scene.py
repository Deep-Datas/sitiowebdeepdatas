"""Genera la escena del inicio: una persona de espaldas frente a un monitor,
de noche, con la ciudad detrás.

Produce dos capas SVG en tools/hero/ que tools/render_hero.cjs convierte en
imágenes (src/assets/img/hero/):

- fondo: ciudad, ventanal, escritorio, objetos y monitor (con la pantalla vacía)
- frente: la persona y la silla, con fondo transparente

Entre ambas capas, el sitio coloca la pantalla real en HTML (la conversación
con el asistente), en el rectángulo SCREEN.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent / 'hero'
W, H = 3600, 2250
SCREEN = (1202, 561, 1296, 810)          # x, y, ancho, alto de la pantalla
BG = '#07090e'                           # color de fondo del sitio (bordes de la escena)
SCREEN_LIGHT = '#fff4e2'                 # luz cálida que emite la pantalla
EMBER = '#ff7a45'
LAMP = '#ffb877'

rng = random.Random(7)


def r(a, b):
    return rng.uniform(a, b)


# ---------------------------------------------------------------- ciudad
def city_layer(base_y, n, w_range, h_range, fill, light_size, spacing, prob, light_alpha, x_from=-100, x_to=W + 100):
    parts = []
    x = x_from
    while x < x_to:
        bw = r(*w_range)
        bh = r(*h_range)
        top = base_y - bh
        parts.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{bw:.0f}" height="{bh + 40:.0f}" fill="{fill}"/>')
        # antena o remate en algunos edificios
        if rng.random() < 0.18:
            parts.append(f'<rect x="{x + bw / 2 - 3:.0f}" y="{top - r(30, 90):.0f}" width="6" height="90" fill="{fill}"/>')
        lw, lh = light_size
        sx, sy = spacing
        cols = int((bw - sx * 0.6) // sx)
        rows = int((bh - sy) // sy)
        warm = rng.random() < 0.7
        for cx in range(cols):
            for cy in range(rows):
                if rng.random() < prob:
                    color = rng.choice(['#ffd9a0', '#ffc77a', '#ffe7c4']) if warm else rng.choice(['#cfe0ff', '#a9c4ff', '#e8f0ff'])
                    a = r(*light_alpha)
                    parts.append(f'<rect x="{x + sx * 0.5 + cx * sx:.0f}" y="{top + sy * 0.6 + cy * sy:.0f}" width="{lw}" height="{lh}" fill="{color}" opacity="{a:.2f}"/>')
        x += bw + r(4, 30)
    return '\n'.join(parts)


def bokeh(n, y_range, r_range, colors, alpha):
    out = []
    for _ in range(n):
        out.append(f'<circle cx="{r(0, W):.0f}" cy="{r(*y_range):.0f}" r="{r(*r_range):.0f}" fill="{rng.choice(colors)}" opacity="{r(*alpha):.2f}"/>')
    return '\n'.join(out)


# ---------------------------------------------------------------- capas
def back_svg():
    sx, sy, sw, sh = SCREEN
    scx, scy = sx + sw / 2, sy + sh / 2
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#05070d"/>
    <stop offset="0.45" stop-color="#0b1222"/>
    <stop offset="0.62" stop-color="#18213a"/>
    <stop offset="0.68" stop-color="#2a2433"/>
  </linearGradient>
  <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{EMBER}" stop-opacity="0"/>
    <stop offset="0.7" stop-color="{EMBER}" stop-opacity="0.16"/>
    <stop offset="1" stop-color="#ffb07a" stop-opacity="0.10"/>
  </linearGradient>
  <linearGradient id="desk" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#17130f"/>
    <stop offset="0.35" stop-color="#0f0d0b"/>
    <stop offset="1" stop-color="#070605"/>
  </linearGradient>
  <radialGradient id="screenGlow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{SCREEN_LIGHT}" stop-opacity="0.28"/>
    <stop offset="0.5" stop-color="{SCREEN_LIGHT}" stop-opacity="0.08"/>
    <stop offset="1" stop-color="{SCREEN_LIGHT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="deskGlow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{SCREEN_LIGHT}" stop-opacity="0.34"/>
    <stop offset="1" stop-color="{SCREEN_LIGHT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="lampPool" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{LAMP}" stop-opacity="0.45"/>
    <stop offset="1" stop-color="{LAMP}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="lampCone" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{LAMP}" stop-opacity="0.22"/>
    <stop offset="1" stop-color="{LAMP}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1a1e27"/>
    <stop offset="1" stop-color="#0b0d12"/>
  </linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#2a2e36"/>
    <stop offset="0.5" stop-color="#6b6f78"/>
    <stop offset="1" stop-color="#22252c"/>
  </linearGradient>
  <radialGradient id="vignette" cx="0.52" cy="0.46" r="0.72">
    <stop offset="0.55" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="0.86" stop-color="{BG}" stop-opacity="0.75"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
  </radialGradient>
  <linearGradient id="bottomFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
  </linearGradient>
  <linearGradient id="glassStreak" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.03"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
  <filter id="dof" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="5"/></filter>
  <filter id="dofFar" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
  <filter id="soft6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="bokehBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="1520" fill="url(#sky)"/>
''']
    # Ciudad (desenfocada por la profundidad de campo)
    parts.append('<g filter="url(#dofFar)">')
    parts.append(city_layer(1500, 0, (90, 230), (260, 720), '#121a2c', (7, 10), (24, 34), 0.22, (0.35, 0.8)))
    parts.append('</g>')
    parts.append('<rect y="900" width="3600" height="620" fill="url(#haze)"/>')
    parts.append('<g filter="url(#dof)">')
    parts.append(city_layer(1500, 0, (170, 420), (380, 1050), '#0a0f1c', (11, 15), (34, 46), 0.26, (0.45, 0.95)))
    parts.append('</g>')
    parts.append('<g filter="url(#bokehBlur)">')
    parts.append(bokeh(70, (700, 1480), (10, 34), ['#ffcf8a', '#ffb877', '#cfe0ff', EMBER], (0.25, 0.6)))
    parts.append('</g>')
    # Reflejos en el vidrio y marcos del ventanal
    parts.append('<polygon points="2050,0 2500,0 1500,1520 1050,1520" fill="url(#glassStreak)"/>')
    parts.append('<polygon points="3050,0 3200,0 2500,1520 2350,1520" fill="url(#glassStreak)"/>')
    for mx in (560, 3020):
        parts.append(f'<rect x="{mx}" y="0" width="44" height="1520" fill="#04060a"/>')
        parts.append(f'<rect x="{mx + 40}" y="0" width="3" height="1520" fill="#ffffff" opacity="0.06"/>')
    parts.append('<rect x="0" y="1460" width="3600" height="60" fill="#05070b"/>')
    parts.append('<rect x="0" y="1458" width="3600" height="3" fill="#ffffff" opacity="0.07"/>')
    # Halo de la pantalla sobre el vidrio y la pared
    parts.append(f'<ellipse cx="{scx}" cy="{scy}" rx="1250" ry="820" fill="url(#screenGlow)"/>')
    # Escritorio
    parts.append(f'<rect x="0" y="1515" width="{W}" height="{H - 1515}" fill="url(#desk)"/>')
    parts.append('<rect x="0" y="1515" width="3600" height="4" fill="#ffe9cc" opacity="0.18"/>')
    parts.append(f'<ellipse cx="{scx}" cy="1600" rx="1150" ry="190" fill="url(#deskGlow)"/>')
    # Lámpara (derecha)
    parts.append('<polygon points="3120,1015 3330,1015 3460,1720 2830,1720" fill="url(#lampCone)"/>')
    parts.append('<ellipse cx="3130" cy="1700" rx="420" ry="90" fill="url(#lampPool)"/>')
    parts.append('<ellipse cx="3040" cy="1712" rx="120" ry="22" fill="#0b0c10"/>')
    parts.append('<path d="M3040 1700 L2930 1240 L3180 1000" fill="none" stroke="#14161c" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append('<path d="M3040 1700 L2930 1240 L3180 1000" fill="none" stroke="#ffd2a1" stroke-opacity="0.25" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append('<circle cx="2930" cy="1240" r="20" fill="#1b1e25"/>')
    parts.append('<path d="M3120 950 L3330 1010 L3290 1050 L3150 1040 Z" fill="#15171d"/>')
    parts.append(f'<ellipse cx="3225" cy="1035" rx="85" ry="16" fill="{LAMP}" opacity="0.95"/>')
    parts.append(f'<ellipse cx="3225" cy="1035" rx="160" ry="50" fill="{LAMP}" opacity="0.35" filter="url(#soft)"/>')
    # Taza
    parts.append('<path d="M2620 1600 L2720 1600 L2712 1712 Q2670 1726 2628 1712 Z" fill="#191b21"/>')
    parts.append('<path d="M2720 1625 Q2770 1630 2766 1662 Q2760 1692 2716 1690" fill="none" stroke="#191b21" stroke-width="14"/>')
    parts.append('<ellipse cx="2670" cy="1600" rx="50" ry="10" fill="#2a2d35"/>')
    parts.append(f'<path d="M2632 1608 L2640 1700" stroke="{LAMP}" stroke-opacity="0.35" stroke-width="4"/>')
    for i, dx in enumerate((-14, 12)):
        parts.append(f'<path d="M{2670 + dx} 1585 q-22 -40 0 -80 q22 -40 0 -90" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="7" stroke-linecap="round" filter="url(#soft6)"/>')
    # Planta (izquierda): hojas largas y puntiagudas a contraluz
    parts.append('<path d="M300 1700 L560 1700 L530 1520 L330 1520 Z" fill="#14130f"/>')
    parts.append('<ellipse cx="430" cy="1520" rx="102" ry="16" fill="#1d1b16"/>')
    leaves = [(-210, -780, -60), (-120, -900, -20), (-30, -1000, 6), (40, -930, 30), (130, -820, 48), (190, -650, 70), (-260, -560, -80), (-80, -700, -35), (90, -1050, 18)]
    for dx, dy, lean in leaves:
        bx, by = 430 + dx * 0.25, 1520
        tx, ty = 430 + dx + lean, 1520 + dy
        w = 46 + abs(dx) * 0.05
        parts.append(f'<path d="M{bx - w / 2:.0f} {by} Q{(bx + tx) / 2 - w:.0f} {(by + ty) / 2:.0f} {tx:.0f} {ty:.0f} Q{(bx + tx) / 2 + w:.0f} {(by + ty) / 2:.0f} {bx + w / 2:.0f} {by} Z" fill="#0d1612"/>')
        parts.append(f'<path d="M{bx:.0f} {by} Q{(bx + tx) / 2 + w * 0.4:.0f} {(by + ty) / 2:.0f} {tx:.0f} {ty:.0f}" fill="none" stroke="#9fd6b4" stroke-opacity="0.16" stroke-width="3"/>')
    # Monitor
    parts.append(f'<ellipse cx="{scx}" cy="1612" rx="300" ry="38" fill="#000" opacity="0.5" filter="url(#soft6)"/>')
    parts.append(f'<path d="M{scx - 250} 1608 Q{scx} 1570 {scx + 250} 1608 Q{scx} 1630 {scx - 250} 1608 Z" fill="url(#metal)"/>')
    parts.append(f'<rect x="{scx - 46}" y="{sy + sh}" width="92" height="{1595 - sy - sh}" fill="url(#metal)"/>')
    parts.append(f'<rect x="{sx - 24}" y="{sy - 24}" width="{sw + 48}" height="{sh + 64}" rx="22" fill="url(#bezel)"/>')
    parts.append(f'<rect x="{sx - 24}" y="{sy - 24}" width="{sw + 48}" height="{sh + 64}" rx="22" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="3"/>')
    parts.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#f6f2ea"/>')
    # Teclado y mouse, iluminados por la pantalla
    parts.append('<path d="M1480 1700 L2230 1700 L2270 1782 L1440 1782 Z" fill="#0f1218"/>')
    parts.append('<path d="M1480 1700 L2230 1700" stroke="#fff4e2" stroke-opacity="0.35" stroke-width="3"/>')
    for row in range(4):
        y = 1712 + row * 17
        x0, x1 = 1480 - row * 9, 2230 + row * 9
        n = 15
        for k in range(n):
            kx = x0 + 12 + k * (x1 - x0 - 24) / n
            parts.append(f'<rect x="{kx:.0f}" y="{y}" width="{(x1 - x0) / n - 10:.0f}" height="11" rx="2" fill="#1a1e27"/>')
    parts.append('<ellipse cx="2390" cy="1752" rx="48" ry="28" fill="#12151c"/>')
    parts.append('<path d="M2346 1742 Q2390 1716 2434 1742" fill="none" stroke="#fff4e2" stroke-opacity="0.3" stroke-width="3"/>')
    # Viñeta para fundir los bordes con el fondo del sitio
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
    parts.append(f'<rect y="{H - 380}" width="{W}" height="380" fill="url(#bottomFade)"/>')
    parts.append('</svg>\n')
    return '\n'.join(parts)


def smooth_path(points, closed=True):
    """Curva suave (Catmull-Rom convertida a Bézier) que pasa por los puntos."""
    n = len(points)
    d = f'M{points[0][0]:.1f} {points[0][1]:.1f} '
    rng_ = range(n) if closed else range(n - 1)
    for i in rng_:
        p0 = points[(i - 1) % n] if closed or i > 0 else points[i]
        p1, p2 = points[i], points[(i + 1) % n]
        p3 = points[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} '
    return d + ('Z' if closed else '')


def hair_outline():
    """Contorno de la cabeza con pelo corto, visto de atrás, levemente irregular."""
    cx, cy = 1250, 1168
    pts = []
    for i in range(72):
        t = -math.pi / 2 + i * 2 * math.pi / 72          # empieza arriba
        st, ct = math.sin(t), math.cos(t)
        rx = 236 if st <= 0 else 236 * (1 - 0.40 * st ** 1.6)
        ry = 236 if st <= 0 else 226
        x, y = cx + rx * ct, cy + ry * st
        if st < 0.2:                                      # textura del pelo en la parte de arriba
            x += r(-4, 4)
            y += r(-5, 3)
        if st > 0.85:                                     # nacimiento del pelo en la nuca
            y += math.sin(i * 1.7) * 8
        pts.append((x, y))
    return pts


def front_svg():
    """Persona de espaldas (a contraluz) y respaldo de la silla."""
    hair_pts = hair_outline()
    hair = smooth_path(hair_pts)
    neck = smooth_path([(1146, 1330), (1354, 1330), (1366, 1420), (1392, 1478), (1250, 1490), (1108, 1478), (1134, 1420)])
    ear_l = 'M1030 1188 C1004 1186 994 1214 998 1246 C1002 1278 1018 1302 1042 1298 Z'
    ear_r = 'M1470 1188 C1496 1186 1506 1214 1502 1246 C1498 1278 1482 1302 1458 1298 Z'
    body = smooth_path([(1250, 1452), (1380, 1462), (1520, 1500), (1660, 1548), (1760, 1600), (1812, 1680),
                        (1836, 1820), (1852, 2000), (1866, 2250), (634, 2250), (648, 2000), (664, 1820),
                        (688, 1680), (740, 1600), (840, 1548), (980, 1500), (1120, 1462)])
    collar = ('M1104 1470 C1150 1446 1350 1446 1396 1470 C1404 1492 1396 1510 1380 1516 '
              'C1330 1500 1170 1500 1120 1516 C1104 1510 1096 1492 1104 1470 Z')
    chair = ('M872 1834 C872 1786 912 1760 974 1756 C1076 1750 1160 1748 1250 1748 '
             'C1340 1748 1424 1750 1526 1756 C1588 1760 1628 1786 1628 1834 '
             'L1644 2250 L856 2250 Z')

    # Mechones: curvas casi paralelas que bajan desde la coronilla siguiendo la forma de la cabeza
    strands = []
    for k in range(260):
        x0 = 1250 + r(-215, 215)
        rel = (x0 - 1250) / 236
        top = 1168 - 236 * math.sqrt(max(0.0, 1 - rel * rel))
        y0 = top + r(4, 60)
        ang = math.radians(rel * 38 + r(-6, 6))            # se abren hacia los costados
        length = r(90, 260)
        ex, ey = x0 + math.sin(ang) * length, y0 + math.cos(ang) * length
        mx, my = (x0 + ex) / 2 + rel * r(10, 30), (y0 + ey) / 2 - r(0, 18)
        lit = y0 < 1080
        op = r(0.03, 0.08) if lit else r(0.015, 0.035)
        color = SCREEN_LIGHT if lit else '#8a8f9c'
        strands.append(f'<path d="M{x0:.0f} {y0:.0f} Q{mx:.0f} {my:.0f} {ex:.0f} {ey:.0f}" '
                       f'fill="none" stroke="{color}" stroke-opacity="{op:.2f}" stroke-width="{r(1.0, 2.2):.1f}" stroke-linecap="round"/>')
    # Pelos sueltos que agarran la luz en el borde superior
    flyaways = []
    for i in range(0, 30, 2):
        x, y = hair_pts[(i - 15) % 72]
        if y > 1120:
            continue
        nx, ny = x - 1250, y - 1168
        norm = math.hypot(nx, ny)
        ox, oy = nx / norm, ny / norm
        lx, ly = x + ox * r(6, 16), y + oy * r(6, 16)
        flyaways.append(f'<path d="M{x - ox * 6:.1f} {y - oy * 6:.1f} Q{(x + lx) / 2 + r(-8, 8):.1f} {(y + ly) / 2 + r(-8, 8):.1f} {lx:.1f} {ly:.1f}" '
                        f'fill="none" stroke="{SCREEN_LIGHT}" stroke-opacity="{r(0.35, 0.7):.2f}" stroke-width="1.4" stroke-linecap="round"/>')

    def rim(path_id, color, width, blur, opacity, mask):
        return (f'<g clip-path="url(#clip-{path_id})" mask="url(#{mask})">'
                f'<use href="#{path_id}" fill="none" stroke="{color}" stroke-width="{width}" '
                f'stroke-opacity="{opacity}" filter="url(#blur{blur})"/></g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <path id="hair" d="{hair}"/>
  <path id="body" d="{body}"/>
  <path id="chair" d="{chair}"/>
  <path id="neck" d="{neck}"/>
  <clipPath id="clip-hair"><use href="#hair"/></clipPath>
  <clipPath id="clip-body"><use href="#body"/></clipPath>
  <clipPath id="clip-chair"><use href="#chair"/></clipPath>
  <clipPath id="clip-neck"><use href="#neck"/></clipPath>
  <filter id="blur3" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="blur8" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="blur14" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="blur30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  <linearGradient id="topLit" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.5"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="rightLit" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0.55" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#fff"/>
  </linearGradient>
  <mask id="maskHair" maskUnits="userSpaceOnUse" x="0" y="900" width="{W}" height="460"><rect x="0" y="900" width="{W}" height="460" fill="url(#topLit)"/></mask>
  <mask id="maskBody" maskUnits="userSpaceOnUse" x="0" y="1440" width="{W}" height="380"><rect x="0" y="1440" width="{W}" height="380" fill="url(#topLit)"/></mask>
  <mask id="maskRight" maskUnits="userSpaceOnUse" x="600" y="1440" width="1300" height="810"><rect x="600" y="1440" width="1300" height="810" fill="url(#rightLit)"/></mask>
  <mask id="maskChair" maskUnits="userSpaceOnUse" x="0" y="1740" width="{W}" height="160"><rect x="0" y="1740" width="{W}" height="160" fill="url(#topLit)"/></mask>
  <radialGradient id="hairShade" cx="0.5" cy="0.25" r="0.8">
    <stop offset="0" stop-color="#15161c"/>
    <stop offset="1" stop-color="#07080b"/>
  </radialGradient>
  <linearGradient id="bodyShade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#141821"/>
    <stop offset="0.4" stop-color="#0c0f15"/>
    <stop offset="1" stop-color="#05060a"/>
  </linearGradient>
  <linearGradient id="neckShade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#2a1d17"/>
    <stop offset="0.5" stop-color="#140e0c"/>
    <stop offset="1" stop-color="#2e1f18"/>
  </linearGradient>
  <linearGradient id="chairShade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#171b24"/>
    <stop offset="1" stop-color="#07080c"/>
  </linearGradient>
  <linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
  </linearGradient>
</defs>
<!-- Luz de la pantalla que se derrama alrededor de la cabeza -->
<ellipse cx="1250" cy="1120" rx="360" ry="320" fill="{SCREEN_LIGHT}" opacity="0.12" filter="url(#blur30)"/>
<use href="#body" fill="url(#bodyShade)"/>
{rim('body', SCREEN_LIGHT, 18, 8, 0.6, 'maskBody')}
{rim('body', LAMP, 22, 14, 0.35, 'maskRight')}
<path d="M818 1720 C846 1860 860 2040 864 2250" fill="none" stroke="#000" stroke-opacity="0.45" stroke-width="18" filter="url(#blur8)"/>
<path d="M1682 1720 C1654 1860 1640 2040 1636 2250" fill="none" stroke="#000" stroke-opacity="0.45" stroke-width="18" filter="url(#blur8)"/>
<path d="M1250 1520 C1246 1640 1252 1720 1250 1760" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="10" filter="url(#blur8)"/>
<use href="#neck" fill="url(#neckShade)"/>
{rim('neck', SCREEN_LIGHT, 10, 3, 0.45, 'maskBody')}
<path d="{collar}" fill="#1a1e28"/>
<path d="M1104 1470 C1150 1446 1350 1446 1396 1470" fill="none" stroke="{SCREEN_LIGHT}" stroke-opacity="0.35" stroke-width="3"/>
<path d="{ear_l}" fill="#2a1a14"/>
<path d="{ear_r}" fill="#2a1a14"/>
<path d="M1000 1236 C1002 1270 1016 1292 1036 1296" fill="none" stroke="#ff9a6a" stroke-opacity="0.6" stroke-width="6" filter="url(#blur3)"/>
<path d="M1500 1236 C1498 1270 1484 1292 1464 1296" fill="none" stroke="#ff9a6a" stroke-opacity="0.6" stroke-width="6" filter="url(#blur3)"/>
<use href="#hair" fill="url(#hairShade)"/>
<g clip-path="url(#clip-hair)">{''.join(strands)}</g>
{rim('hair', SCREEN_LIGHT, 26, 8, 0.85, 'maskHair')}
<use href="#hair" fill="none" stroke="{SCREEN_LIGHT}" stroke-opacity="0.6" stroke-width="2" mask="url(#maskHair)"/>
{''.join(flyaways)}
<use href="#chair" fill="url(#chairShade)"/>
{rim('chair', SCREEN_LIGHT, 12, 3, 0.35, 'maskChair')}
{''.join(f'<path d="M{896 + i * 42} 1800 L{892 + i * 43} 2250" stroke="#ffffff" stroke-opacity="0.025" stroke-width="2"/>' for i in range(18))}
<rect x="0" y="{H - 260}" width="{W}" height="260" fill="url(#fadeBottom)"/>
</svg>
'''


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    (OUT / 'fondo.svg').write_text(back_svg(), encoding='utf-8')
    (OUT / 'frente.svg').write_text(front_svg(), encoding='utf-8')
    print('  tools/hero/fondo.svg\n  tools/hero/frente.svg')
