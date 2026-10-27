"""Prepara la foto de la portada del inicio: la aclara y la agranda lo mejor que se puede.

Parte de dos fotos del cliente, en tools/hero/:

  portada-original.webp      la oficina entera (1264 x 843): el equipo de datos de un
                             lado y, cruzando la mampara, quien decide del otro.
  portada-tv-original.webp   el primer plano del televisor (1024 x 559), adonde llega
                             la cámara al final del recorrido.

y escribe src/assets/img/hero/portada-oficina-{1264,2528}.webp y portada-tv-{1024,2048}.webp.

Dos cosas pasan acá:

1. Revelado. La foto viene de una tarde: tiene un velo cálido en los medios tonos y
   las sombras cerradas. Se neutraliza el color por canal con una gamma que no mueve ni
   el negro ni el blanco, se levanta el medio tono, se baja un poco la saturación y se
   recupera algo de contraste arriba. Queda una oficina más clara y más blanca, sin
   quemar las ventanas (que ya estaban casi en blanco).

2. Agrandado. La portada ocupa toda la pantalla y la cámara se acerca, así que el
   navegador tiene que estirar la foto varias veces. Un Lanczos a secas queda blando:
   acá se hace retroproyección, que es iterar «agrandar, achicar, comparar con el
   original y devolver la diferencia». Eso no inventa detalle (no hay de dónde), pero
   recupera el que el agrandado se come y deja los bordes mucho más definidos.

   python tools/portada_foto.py            (regenera los tres tamaños)
   python tools/portada_foto.py --revelado (solo muestra los números del revelado)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / 'src' / 'assets' / 'img' / 'hero'
# (archivo de origen, nombre que se publica, (ancho, calidad webp) …)
FOTOS = (
    ('portada-original.webp', 'portada-oficina', ((1264, 86), (2528, 82))),
    ('portada-tv-original.webp', 'portada-tv', ((1024, 86), (2048, 82))),
)

GAMMA_LUZ = 0.79        # <1 aclara los medios tonos y deja quietos negro y blanco
SATURACION = 0.90       # un poco menos de color: la oficina se lee más blanca
CONTRASTE = 0.12        # cuánto se recupera arriba, después de aclarar
PASOS = 12              # iteraciones de retroproyección
EMPUJE = 0.9            # cuánto de la diferencia se devuelve en cada paso


def revelado(a: np.ndarray) -> np.ndarray:
    """Aclara, neutraliza el velo cálido y baja la saturación. Entra y sale en 0..1."""
    # Gamma por canal para que el medio tono quede neutro, sin tocar negro ni blanco
    medios = np.array([np.median(a[..., c]) for c in range(3)])
    objetivo = medios.mean()
    gammas = np.log(objetivo) / np.log(medios)
    a = a ** gammas

    a = a ** GAMMA_LUZ

    gris = (a * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    a = gris + (a - gris) * SATURACION

    # Una ese suave: lo que se aclaró de más arriba vuelve, y el negro no se levanta
    a = a + CONTRASTE * np.sin(2 * np.pi * a) / (2 * np.pi) * -1
    return np.clip(a, 0, 1)


def retroproyeccion(base: Image.Image, ancho: int) -> Image.Image:
    """Agranda iterando: agrandar, achicar, comparar y devolver la diferencia."""
    alto = round(ancho * base.height / base.width)
    chico = np.asarray(base, dtype=np.float32)
    grande = np.asarray(base.resize((ancho, alto), Image.LANCZOS), dtype=np.float32)
    for _ in range(PASOS):
        vuelta = np.asarray(
            Image.fromarray(np.clip(grande, 0, 255).astype('uint8'))
            .resize(base.size, Image.LANCZOS), dtype=np.float32)
        error = chico - vuelta
        grande += EMPUJE * np.asarray(
            Image.fromarray(np.clip(error + 128, 0, 255).astype('uint8'))
            .resize((ancho, alto), Image.LANCZOS), dtype=np.float32) - EMPUJE * 128
    return Image.fromarray(np.clip(grande, 0, 255).astype('uint8'))


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for archivo, nombre, anchos in FOTOS:
        origen = RAIZ / 'tools' / 'hero' / archivo
        if not origen.exists():
            print(f'falta la foto original en {origen}')
            return 1
        original = Image.open(origen).convert('RGB')
        claro = revelado(np.asarray(original, dtype=np.float32) / 255)

        if '--revelado' in sys.argv:
            antes = np.asarray(original, dtype=float)
            despues = claro * 255
            print(archivo)
            for etiqueta, x in (('  antes  ', antes), ('  después', despues)):
                luma = x @ [0.2126, 0.7152, 0.0722]
                print(etiqueta, 'media', round(luma.mean(), 1),
                      '· mediana RGB', np.median(x.reshape(-1, 3), 0).round(1),
                      '· quemado', f'{(luma > 250).mean() * 100:.2f} %')
            continue

        base = Image.fromarray((claro * 255).round().astype('uint8'))
        for ancho, calidad in anchos:
            if ancho == base.width:
                im = base
            else:
                im = retroproyeccion(base, ancho)
                # Un último toque de nitidez, suave: la retroproyección ya hizo lo grueso
                im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=38, threshold=2))
            salida = DESTINO / f'{nombre}-{ancho}.webp'
            im.save(salida, quality=calidad, method=6)
            print(f'{salida.name}: {im.width} x {im.height}, {salida.stat().st_size // 1024} KB')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
