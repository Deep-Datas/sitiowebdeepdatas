"""Versión de día de la escena del inicio (para el tema claro).

Usa la misma composición que tools/hero_scene.py (persona, monitor y
rectángulo de la pantalla en las mismas coordenadas), con luz de día:
cielo claro, ciudad iluminada por el sol, escritorio de madera clara y la
persona a contraluz de la ventana. Genera tools/hero/fondo-dia.svg y
tools/hero/frente-dia.svg.
"""
import random

import hero_scene as base

W, H = base.W, base.H
SCREEN = base.SCREEN
BG = '#fafaf8'                            # fondo del sitio en el tema claro

rng = random.Random(11)


def r(a, b):
    return rng.uniform(a, b)


# Paleta de la persona: mismos trazos que de noche, con luz de ventana
FRONT_COLORS = {
    base.SCREEN_LIGHT: '#ffffff',   # contraluz principal
    base.LAMP: '#ffffff',           # contraluz lateral
    '#15161c': '#3b312b', '#07080b': '#1d1814',          # pelo
    '#141821': '#3a4a72', '#0c0f15': '#2a3658', '#05060a': '#1d2640',  # buzo
    '#2a1d17': '#9c6c53', '#140e0c': '#7b5341', '#2e1f18': '#a5745b',  # cuello
    '#171b24': '#5a6170', '#07080c': '#343944',          # silla
    '#1a1e28': '#25335a',           # cuello del buzo
    '#2a1a14': '#a97561',           # orejas
    '#ff9a6a': '#ffc4a6',           # luz a través de las orejas
    '#8a8f9c': '#75685d',           # mechones en sombra
    base.BG: BG,
}


def front_svg():
    svg = base.front_svg()
    for night, day in FRONT_COLORS.items():
        svg = svg.replace(night, day)
    return svg


def city(base_y, w_range, h_range, fill, face, win, spacing, prob):
    parts = []
    x = -100
    while x < W + 100:
        bw = r(*w_range)
        bh = r(*h_range)
        top = base_y - bh
        parts.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{bw:.0f}" height="{bh + 40:.0f}" fill="{fill}"/>')
        # cara iluminada por el sol
        parts.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{bw * r(0.25, 0.45):.0f}" height="{bh + 40:.0f}" fill="{face}" opacity="0.55"/>')
        if rng.random() < 0.15:
            parts.append(f'<rect x="{x + bw / 2 - 3:.0f}" y="{top - r(30, 90):.0f}" width="6" height="90" fill="{fill}"/>')
        sx, sy = spacing
        cols = int((bw - sx * 0.6) // sx)
        rows = int((bh - sy) // sy)
        for cx in range(cols):
            for cy in range(rows):
                if rng.random() < prob:
                    parts.append(f'<rect x="{x + sx * 0.5 + cx * sx:.0f}" y="{top + sy * 0.6 + cy * sy:.0f}" width="{sx * 0.42:.0f}" height="{sy * 0.45:.0f}" fill="{rng.choice(win)}" opacity="{r(0.35, 0.8):.2f}"/>')
        x += bw + r(4, 30)
    return '\n'.join(parts)


def back_svg():
    sx, sy, sw, sh = SCREEN
    scx = sx + sw / 2
    p = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#9fbfe6"/>
    <stop offset="0.4" stop-color="#c3d8f0"/>
    <stop offset="0.62" stop-color="#e6edf3"/>
    <stop offset="0.68" stop-color="#f4efe6"/>
  </linearGradient>
  <radialGradient id="sun" cx="0.82" cy="0.12" r="0.5">
    <stop offset="0" stop-color="#fffaf0" stop-opacity="0.95"/>
    <stop offset="1" stop-color="#fffaf0" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="1" stop-color="#f6efe4" stop-opacity="0.75"/>
  </linearGradient>
  <linearGradient id="desk" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e2cdae"/>
    <stop offset="0.4" stop-color="#d2b994"/>
    <stop offset="1" stop-color="#bc9d76"/>
  </linearGradient>
  <linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2a2f39"/>
    <stop offset="1" stop-color="#14171d"/>
  </linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#a3a8b1"/>
    <stop offset="0.5" stop-color="#e3e5e9"/>
    <stop offset="1" stop-color="#9097a1"/>
  </linearGradient>
  <linearGradient id="pot" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#d9d5cc"/>
    <stop offset="0.45" stop-color="#f6f3ee"/>
    <stop offset="1" stop-color="#cfcac0"/>
  </linearGradient>
  <radialGradient id="vignette" cx="0.52" cy="0.46" r="0.72">
    <stop offset="0.6" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="0.88" stop-color="{BG}" stop-opacity="0.7"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
  </radialGradient>
  <linearGradient id="bottomFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
  </linearGradient>
  <linearGradient id="glassStreak" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.22"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
  <filter id="dof" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="4"/></filter>
  <filter id="dofFar" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="24"/></filter>
  <filter id="soft6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="1520" fill="url(#sky)"/>
<rect width="{W}" height="1520" fill="url(#sun)"/>
''']
    # Nubes suaves
    p.append('<g filter="url(#soft)">')
    for cx, cy, rx, ry in [(700, 260, 420, 60), (1180, 330, 300, 40), (2500, 200, 520, 70), (3150, 380, 320, 46), (1900, 120, 260, 36)]:
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#ffffff" opacity="0.75"/>')
    p.append('</g>')
    # Ciudad de día (desenfocada)
    p.append('<g filter="url(#dofFar)">')
    p.append(city(1500, (90, 230), (260, 720), '#b7c5d7', '#d9e3ee', ['#e7eef6', '#a9bbd2', '#f4f7fb'], (24, 34), 0.30))
    p.append('</g>')
    p.append('<rect y="860" width="3600" height="660" fill="url(#haze)"/>')
    p.append('<g filter="url(#dof)">')
    p.append(city(1500, (170, 420), (380, 1050), '#8d9fb8', '#b8c6d8', ['#c9d7e8', '#6f839f', '#e5edf6'], (34, 46), 0.34))
    p.append('</g>')
    # Reflejos y marcos del ventanal
    p.append('<polygon points="2050,0 2500,0 1500,1520 1050,1520" fill="url(#glassStreak)"/>')
    p.append('<polygon points="3050,0 3200,0 2500,1520 2350,1520" fill="url(#glassStreak)"/>')
    for mx in (560, 3020):
        p.append(f'<rect x="{mx}" y="0" width="44" height="1520" fill="#3b4352"/>')
        p.append(f'<rect x="{mx + 40}" y="0" width="3" height="1520" fill="#ffffff" opacity="0.35"/>')
    p.append('<rect x="0" y="1460" width="3600" height="60" fill="#4a5262"/>')
    p.append('<rect x="0" y="1458" width="3600" height="3" fill="#ffffff" opacity="0.5"/>')
    # Escritorio de madera clara
    p.append(f'<rect x="0" y="1515" width="{W}" height="{H - 1515}" fill="url(#desk)"/>')
    p.append('<rect x="0" y="1515" width="3600" height="5" fill="#fff8ec" opacity="0.7"/>')
    for i in range(14):
        y = 1560 + i * 48 + r(-10, 10)
        p.append(f'<path d="M0 {y:.0f} C900 {y + r(-14, 14):.0f} 2700 {y + r(-14, 14):.0f} 3600 {y + r(-8, 8):.0f}" fill="none" stroke="#a88660" stroke-opacity="{r(0.08, 0.18):.2f}" stroke-width="{r(2, 4):.1f}"/>')
    # Lámpara (apagada)
    p.append('<ellipse cx="3040" cy="1712" rx="130" ry="22" fill="#000" opacity="0.12" filter="url(#soft6)"/>')
    p.append('<ellipse cx="3040" cy="1708" rx="120" ry="22" fill="#2b2f38"/>')
    p.append('<path d="M3040 1700 L2930 1240 L3180 1000" fill="none" stroke="#2b2f38" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append('<path d="M3040 1700 L2930 1240 L3180 1000" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append('<circle cx="2930" cy="1240" r="20" fill="#3a3f4a"/>')
    p.append('<path d="M3120 950 L3330 1010 L3290 1050 L3150 1040 Z" fill="#2b2f38"/>')
    # Taza blanca
    p.append('<ellipse cx="2672" cy="1716" rx="64" ry="12" fill="#000" opacity="0.12" filter="url(#soft6)"/>')
    p.append('<path d="M2620 1600 L2720 1600 L2712 1712 Q2670 1726 2628 1712 Z" fill="#f3f1ec"/>')
    p.append('<path d="M2720 1625 Q2770 1630 2766 1662 Q2760 1692 2716 1690" fill="none" stroke="#e4e0d8" stroke-width="14"/>')
    p.append('<ellipse cx="2670" cy="1600" rx="50" ry="10" fill="#6b4a32"/>')
    p.append('<path d="M2700 1606 L2694 1708" stroke="#000" stroke-opacity="0.08" stroke-width="22"/>')
    # Planta con maceta blanca
    p.append('<ellipse cx="430" cy="1705" rx="150" ry="20" fill="#000" opacity="0.12" filter="url(#soft6)"/>')
    p.append('<path d="M300 1700 L560 1700 L530 1520 L330 1520 Z" fill="url(#pot)"/>')
    p.append('<ellipse cx="430" cy="1520" rx="102" ry="16" fill="#6b5a46"/>')
    leaves = [(-210, -780, -60), (-120, -900, -20), (-30, -1000, 6), (40, -930, 30), (130, -820, 48), (190, -650, 70), (-260, -560, -80), (-80, -700, -35), (90, -1050, 18)]
    greens = ['#3f6e4e', '#4c7d5a', '#365f44', '#5a8c66']
    for i, (dx, dy, lean) in enumerate(leaves):
        bx, by = 430 + dx * 0.25, 1520
        tx, ty = 430 + dx + lean, 1520 + dy
        w = 46 + abs(dx) * 0.05
        p.append(f'<path d="M{bx - w / 2:.0f} {by} Q{(bx + tx) / 2 - w:.0f} {(by + ty) / 2:.0f} {tx:.0f} {ty:.0f} Q{(bx + tx) / 2 + w:.0f} {(by + ty) / 2:.0f} {bx + w / 2:.0f} {by} Z" fill="{greens[i % 4]}"/>')
        p.append(f'<path d="M{bx:.0f} {by} Q{(bx + tx) / 2 + w * 0.4:.0f} {(by + ty) / 2:.0f} {tx:.0f} {ty:.0f}" fill="none" stroke="#b9dcbc" stroke-opacity="0.55" stroke-width="3"/>')
    # Monitor
    p.append(f'<ellipse cx="{scx}" cy="1614" rx="320" ry="34" fill="#000" opacity="0.18" filter="url(#soft6)"/>')
    p.append(f'<path d="M{scx - 250} 1608 Q{scx} 1570 {scx + 250} 1608 Q{scx} 1630 {scx - 250} 1608 Z" fill="url(#metal)"/>')
    p.append(f'<rect x="{scx - 46}" y="{sy + sh}" width="92" height="{1595 - sy - sh}" fill="url(#metal)"/>')
    p.append(f'<rect x="{sx - 24}" y="{sy - 24}" width="{sw + 48}" height="{sh + 64}" rx="22" fill="url(#bezel)"/>')
    p.append(f'<rect x="{sx - 24}" y="{sy - 24}" width="{sw + 48}" height="{sh + 64}" rx="22" fill="none" stroke="#ffffff" stroke-opacity="0.25" stroke-width="3"/>')
    p.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#f6f2ea"/>')
    # Teclado y mouse claros
    p.append('<path d="M1470 1786 L2280 1786" stroke="#000" stroke-opacity="0.12" stroke-width="16" filter="url(#soft6)"/>')
    p.append('<path d="M1480 1700 L2230 1700 L2270 1782 L1440 1782 Z" fill="#d9dce2"/>')
    p.append('<path d="M1480 1700 L2230 1700" stroke="#ffffff" stroke-width="3"/>')
    for row in range(4):
        y = 1712 + row * 17
        x0, x1 = 1480 - row * 9, 2230 + row * 9
        n = 15
        for k in range(n):
            kx = x0 + 12 + k * (x1 - x0 - 24) / n
            p.append(f'<rect x="{kx:.0f}" y="{y}" width="{(x1 - x0) / n - 10:.0f}" height="11" rx="2" fill="#f5f6f8"/>')
    p.append('<ellipse cx="2392" cy="1760" rx="54" ry="14" fill="#000" opacity="0.12" filter="url(#soft6)"/>')
    p.append('<ellipse cx="2390" cy="1752" rx="48" ry="28" fill="#eef0f3"/>')
    p.append('<path d="M2346 1742 Q2390 1716 2434 1742" fill="none" stroke="#ffffff" stroke-width="3"/>')
    # Fundido con el fondo del sitio
    p.append(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
    p.append(f'<rect y="{H - 380}" width="{W}" height="380" fill="url(#bottomFade)"/>')
    p.append('</svg>\n')
    return '\n'.join(p)


if __name__ == '__main__':
    base.OUT.mkdir(exist_ok=True)
    (base.OUT / 'fondo-dia.svg').write_text(back_svg(), encoding='utf-8')
    (base.OUT / 'frente-dia.svg').write_text(front_svg(), encoding='utf-8')
    print('  tools/hero/fondo-dia.svg\n  tools/hero/frente-dia.svg')
