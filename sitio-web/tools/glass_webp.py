"""Convierte tools/glass/png/*.png en WebP con transparencia (256 y 512 px) para el sitio."""
from pathlib import Path

from PIL import Image

SRC = Path(__file__).parent / 'glass' / 'png'
OUT = Path(__file__).parent.parent / 'src' / 'assets' / 'img' / 'glass'

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for png in sorted(SRC.glob('*.png')):
        image = Image.open(png).convert('RGBA')
        for size in (256, 512):
            target = OUT / f'{png.stem}-{size}.webp'
            image.resize((size, size), Image.LANCZOS).save(target, 'WEBP', quality=86, method=6)
            print(f'  {target.relative_to(OUT.parent.parent.parent.parent)} ({target.stat().st_size // 1024} KB)')
