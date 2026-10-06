"""Convierte tools/hero/png/*.png en WebP para el sitio (3600 y 1800 px de ancho)."""
from pathlib import Path

from PIL import Image

SRC = Path(__file__).parent / 'hero' / 'png'
OUT = Path(__file__).parent.parent / 'src' / 'assets' / 'img' / 'hero'

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name, quality in (('fondo', 80), ('frente', 82)):
        image = Image.open(SRC / f'{name}.png')
        image = image.convert('RGBA' if name == 'frente' else 'RGB')
        for width in (3600, 1800):
            target = OUT / f'{name}-{width}.webp'
            resized = image if width == image.width else image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
            resized.save(target, 'WEBP', quality=quality, method=6)
            print(f'  {target.relative_to(OUT.parents[3])} ({target.stat().st_size // 1024} KB)')
