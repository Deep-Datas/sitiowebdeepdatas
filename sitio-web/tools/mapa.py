"""Arma la imagen del mapa de la oficina que se ve antes de cargar el de Google.

El mapa de Google venía en un iframe que carga unos 400 KB de JavaScript de terceros
en /contacto/ y /nosotros/, en los dos idiomas, aunque el visitante no lo mire nunca.
Ahora esas páginas muestran primero esta imagen y el mapa de verdad se carga recién al
hacer clic.

La imagen se arma con los mosaicos de OpenStreetMap: se bajan los que cubren el encuadre,
se pegan, se recorta y se marca la dirección.

    python tools/mapa.py            (regenera las dos imágenes)
    python tools/mapa.py --limpiar  (además borra los mosaicos guardados)

Escribe src/assets/img/mapa/oficina-{800,1600}.webp. La de 1600 cubre el mismo terreno
que la de 800 pero con el doble de detalle, para pantallas de alta densidad: por eso va
un nivel de acercamiento más.

Licencia: los datos son de OpenStreetMap, con licencia ODbL, y hay que atribuirlos donde
se vea el mapa. La atribución va en el HTML, debajo de la imagen («© OpenStreetMap»), no
quemada en el archivo. Los mosaicos se bajan una sola vez —quedan guardados en
tools/mapa-cache/, que no se sube— y la imagen ya armada se versiona, así que el sitio no
le pega al servidor de mosaicos en cada compilación. Si se muda la oficina, cambiar
DIRECCION y volver a correr el script.
"""
from __future__ import annotations

import math
import shutil
import sys
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / 'src' / 'assets' / 'img' / 'mapa'
CACHE = Path(__file__).resolve().parent / 'mapa-cache'

# Bernardo de Irigoyen 330, C1072 CABA, según Nominatim (OpenStreetMap)
DIRECCION = (-34.6121617, -58.3803951)

SERVIDOR = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
# La política de uso de los mosaicos de OpenStreetMap pide identificarse
AGENTE = 'DeepDatas-site-build/1.0 (+https://deepdatas.com; fbloise@deepdatas.com)'
LADO = 256  # lo que mide un mosaico

# (ancho, alto, acercamiento, calidad webp). Las dos cubren el mismo terreno: la grande
# va un nivel más cerca, que es justo el doble de detalle.
SALIDAS = (
    (800, 500, 16, 84),
    (1600, 1000, 17, 80),
)

NARANJA = (228, 88, 28)


def xy(lat, lon, z):
    """Dónde cae una coordenada en el plano de mosaicos, en píxeles."""
    n = 2 ** z * LADO
    x = (lon + 180) / 360 * n
    rad = math.radians(lat)
    y = (1 - math.log(math.tan(rad) + 1 / math.cos(rad)) / math.pi) / 2 * n
    return x, y


def mosaico(z, tx, ty):
    """Un mosaico, del disco si ya se bajó."""
    guardado = CACHE / f'{z}-{tx}-{ty}.png'
    if guardado.exists():
        return Image.open(guardado).convert('RGB')
    pedido = urllib.request.Request(SERVIDOR.format(z=z, x=tx, y=ty), headers={'User-Agent': AGENTE})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        datos = r.read()
    guardado.parent.mkdir(parents=True, exist_ok=True)
    guardado.write_bytes(datos)
    return Image.open(BytesIO(datos)).convert('RGB')


def mapa(ancho, alto, z):
    """Pega los mosaicos que cubren el encuadre y lo recorta centrado en la dirección."""
    cx, cy = xy(*DIRECCION, z)
    izq, arriba = cx - ancho / 2, cy - alto / 2
    t0x, t0y = int(izq // LADO), int(arriba // LADO)
    t1x, t1y = int((izq + ancho) // LADO), int((arriba + alto) // LADO)

    lienzo = Image.new('RGB', ((t1x - t0x + 1) * LADO, (t1y - t0y + 1) * LADO))
    for tx in range(t0x, t1x + 1):
        for ty in range(t0y, t1y + 1):
            lienzo.paste(mosaico(z, tx, ty), ((tx - t0x) * LADO, (ty - t0y) * LADO))

    dx, dy = izq - t0x * LADO, arriba - t0y * LADO
    return lienzo.crop((round(dx), round(dy), round(dx) + ancho, round(dy) + alto))


def marcar(im):
    """La chinche sobre la dirección: un punto naranja con halo blanco."""
    d = ImageDraw.Draw(im, 'RGBA')
    cx, cy = im.width / 2, im.height / 2
    r = im.width / 800 * 11
    d.ellipse((cx - r * 1.9, cy - r * 1.9, cx + r * 1.9, cy + r * 1.9), fill=NARANJA + (46,))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=NARANJA,
              width=max(2, round(r / 3)))
    p = r / 2.6
    d.ellipse((cx - p, cy - p, cx + p, cy + p), fill=NARANJA)
    return im


def main() -> int:
    if '--limpiar' in sys.argv and CACHE.exists():
        shutil.rmtree(CACHE)
    DESTINO.mkdir(parents=True, exist_ok=True)
    for ancho, alto, z, calidad in SALIDAS:
        im = marcar(mapa(ancho, alto, z))
        salida = DESTINO / f'oficina-{ancho}.webp'
        im.save(salida, quality=calidad, method=6)
        print(f'{salida.name}: {im.width} x {im.height}, {salida.stat().st_size // 1024} KB')
    print('Datos del mapa © colaboradores de OpenStreetMap (ODbL). La atribución tiene '
          'que verse junto al mapa en el sitio.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
