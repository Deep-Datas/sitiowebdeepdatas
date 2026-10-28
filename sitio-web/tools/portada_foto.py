"""Prepara la imagen de la portada del inicio: la aclara y la agranda lo mejor que se puede.

Parte de tools/hero/portada-original.webp, de 1536 x 1024 (3:2) —el escritorio de quien
decide, con el monitor de frente y la mano apoyada sobre la pantalla— y escribe
src/assets/img/hero/portada-{1536,2048}.webp.

Está generada con IA (Gemini / Nano Banana): no es la foto de una oficina real y la
persona que aparece no existe. La licencia está anotada en el README, en «Portada del
inicio»; si se reemplaza por una foto de verdad hay que anotar allá la licencia y la
cesión de imagen de quien aparezca.

Dos cosas pasan acá:

1. Revelado. Viene con un velo cálido fuerte: la mediana se desvía del gris unos 30
   niveles. Se neutraliza por canal con una gamma que no mueve ni el negro ni el blanco,
   y el resto queda apenas insinuado. Ojo acá: esta foto ya viene clara (luz media 136 a
   149) y con un 1 a 1,5 % quemado, así que el aclarado fuerte que pedían las anteriores
   le lava los azules del monitor y la aplana. Si se cambia la foto, volver a mirar estos
   números antes de dar por buenos los valores.

2. Agrandado. La portada ocupa toda la pantalla y la cámara se acerca, así que el
   navegador tiene que estirar la foto varias veces. Un Lanczos a secas queda blando:
   acá se hace retroproyección, que es iterar «agrandar, achicar, comparar con el
   original y devolver la diferencia». Eso no inventa detalle (no hay de dónde), pero
   recupera el que el agrandado se come y deja los bordes mucho más definidos.

   python tools/portada_foto.py            (regenera los dos archivos)
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
# El tamaño grande sale de cuánto se le acerca la cámara. La mitad de pantalla mide unos
# 684 px, que a dpr 2 son ~1370 px de dispositivo; en el encuadre más cerrado se ven unos
# 570 de los 1536 px de ancho de la foto, así que hay que agrandarla. Si se cambian los
# encuadres de hero.html, rehacer esta cuenta.
FOTOS = (
    ('portada-original.webp', 'portada', ((1536, 86), (2048, 82))),
)

GAMMA_LUZ = 0.95        # <1 aclara los medios tonos y deja quietos negro y blanco
SATURACION = 0.96       # un poco menos de color, apenas
CONTRASTE = 0.05        # cuánto se recupera arriba, después de aclarar
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
