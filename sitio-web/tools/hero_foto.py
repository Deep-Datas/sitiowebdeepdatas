"""Escena del inicio del tema claro a partir de una foto de oficina.

Parte de tools/hero/oficina-original.webp (1024 x 592) y genera
src/assets/img/hero/oficina-{2048,4096}.webp:

1. Superresolución x4 con Real-ESRGAN (modelo ONNX, licencia BSD-3). El
   resultado queda en caché en tools/hero/png/oficina-x4.png.
2. Mapa de profundidad con Depth Anything V2 small (ONNX, Apache-2.0) y
   silueta del hombre con GrabCut a partir de esa profundidad.
3. Pelo del hombre castaño oscuro (era platinado), conservando la textura y
   el contraluz de la ventana.
4. Limpia la pizarra (logo y anotaciones de otra empresa) y dibuja un
   gráfico de barras a mano alzada.
5. Desenfoque de fondo según la profundidad, como el de un lente: el
   hombre y el monitor quedan nítidos. Después, una corrección de color
   con más contraste y luz cálida.
6. Pinta en perspectiva, sobre la pantalla del monitor (esquinas en
   src/hero.json), la ventana del asistente capturada por
   tools/render_pantalla.cjs (tools/hero/png/pantalla.png), con un leve
   resplandor. Así la escena se ve bien sin JavaScript; con JavaScript,
   site.js pone encima la ventana real.

Los modelos se descargan de Hugging Face la primera vez en tools/hero/modelos/.
Requiere: pip install numpy pillow opencv-contrib-python-headless onnxruntime
Uso: python build.py && node tools/render_pantalla.cjs && python tools/hero_foto.py && python build.py
"""
import json
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TOOLS = Path(__file__).parent
SITE = TOOLS.parent
SOURCE = TOOLS / 'hero' / 'oficina-original.webp'
CACHE = TOOLS / 'hero' / 'png'
MODELS = TOOLS / 'hero' / 'modelos'
UPSCALER = ('real-esrgan-x4plus-128.onnx', 'https://huggingface.co/bukuroo/RealESRGAN-ONNX/resolve/main/real-esrgan-x4plus-128.onnx')
DEPTH = ('depth-anything-v2-small.onnx', 'https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx')
OUT = SITE / 'src' / 'assets' / 'img' / 'hero'

# Contorno del pelo del hombre (nacimiento en la frente, patilla, sobre la oreja y nuca),
# en píxeles de la imagen x4; los bordes externos quedan fuera de la cabeza.
HAIR = [(2580, 965), (2615, 988), (2628, 1008), (2642, 1026), (2658, 1048), (2668, 1064), (2672, 1088),
        (2678, 1112), (2692, 1116), (2702, 1106), (2708, 1090), (2720, 1086), (2734, 1086), (2752, 1092),
        (2764, 1110), (2772, 1135), (2782, 1160), (2802, 1182), (2825, 1196), (2850, 1202), (2875, 1203),
        (2990, 1210), (2990, 870), (2560, 870)]
# Zona donde está el hombre (para la silueta con GrabCut)
MAN = (2280, 860, 3500, 2368)

# Superficie blanca de la pizarra, en píxeles de la imagen x4 (arriba-izq., arriba-der., abajo-der., abajo-izq.)
BOARD = [(1212, 574), (1546, 603), (1548, 933), (1214, 948)]


def model(spec):
    import onnxruntime as ort
    name, url = spec
    path = MODELS / name
    if not path.exists():
        MODELS.mkdir(parents=True, exist_ok=True)
        print(f'  descargando {url}')
        urllib.request.urlretrieve(url, path)
    return ort.InferenceSession(str(path), providers=['CPUExecutionProvider'])


def upscale(image):
    """Real-ESRGAN x4 por mosaicos de 128 px con bordes mezclados."""
    tile, overlap, k = 128, 24, 4
    img = np.asarray(image.convert('RGB')).astype(np.float32) / 255.0
    h, w, _ = img.shape
    padded = np.pad(img, ((overlap, overlap + tile), (overlap, overlap + tile), (0, 0)), mode='reflect')
    session = model(UPSCALER)
    name = session.get_inputs()[0].name
    out = np.zeros(((h + 2 * overlap + tile) * k, (w + 2 * overlap + tile) * k, 3), np.float32)
    total = np.zeros(out.shape[:2], np.float32)
    ramp = np.ones(tile * k, np.float32)
    fade = overlap * k
    ramp[:fade] = np.linspace(0.05, 1, fade)
    ramp[-fade:] = np.linspace(1, 0.05, fade)
    weight = np.outer(ramp, ramp)
    step = tile - overlap
    for y in range(0, h + 2 * overlap - overlap, step):
        for x in range(0, w + 2 * overlap - overlap, step):
            part = padded[y:y + tile, x:x + tile].transpose(2, 0, 1)[None]
            res = session.run(None, {name: part})[0][0].transpose(1, 2, 0)
            out[y * k:(y + tile) * k, x * k:(x + tile) * k] += res * weight[..., None]
            total[y * k:(y + tile) * k, x * k:(x + tile) * k] += weight
    out = (out / np.maximum(total, 1e-6)[..., None])[overlap * k:(overlap + h) * k, overlap * k:(overlap + w) * k]
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


def depth_map(source, size):
    """Profundidad relativa (mayor = más cerca) con Depth Anything V2, llevada al tamaño final."""
    w, h = 896, 518                     # múltiplos de 14, con la proporción de la foto
    x = np.asarray(source.convert('RGB').resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    depth = model(DEPTH).run(None, {'pixel_values': x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    return cv2.resize(depth, size, interpolation=cv2.INTER_CUBIC)


def man_mask(image, depth):
    """Silueta del hombre: GrabCut inicializado con la profundidad y bordes afinados con la foto."""
    x0, y0, x1, y1 = MAN
    sub = np.asarray(image)[y0:y1, x0:x1]
    small = cv2.resize(sub, (sub.shape[1] // 2, sub.shape[0] // 2), interpolation=cv2.INTER_AREA)
    d = cv2.resize(depth[y0:y1, x0:x1], (small.shape[1], small.shape[0]), interpolation=cv2.INTER_AREA)
    mask = np.full(d.shape, cv2.GC_PR_BGD, np.uint8)
    mask[d > 1.9] = cv2.GC_PR_FGD
    mask[d > 2.8] = cv2.GC_FGD
    mask[d < 1.0] = cv2.GC_BGD
    cv2.setRNGSeed(1)
    cv2.grabCut(small, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
    fg = ((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)).astype(np.float32)
    fg = cv2.resize(fg, (sub.shape[1], sub.shape[0]), interpolation=cv2.INTER_LINEAR)
    fg = np.clip(cv2.ximgproc.guidedFilter(guide=sub.astype(np.float32) / 255, src=fg, radius=6, eps=1e-3), 0, 1)
    full = np.zeros(depth.shape, np.float32)
    full[y0:y1, x0:x1] = fg
    return full


def retouch_hair(image, depth):
    """Pelo castaño oscuro: oscurece en LAB conservando la textura, con brillo de contraluz arriba."""
    img8 = np.asarray(image)
    xs, ys = [p[0] for p in HAIR], [p[1] for p in HAIR]
    x0, y0, x1, y1 = min(xs) - 40, min(ys) - 40, max(xs) + 40, max(ys) + 160
    crop = img8[y0:y1, x0:x1]
    region = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(region).polygon([(x - x0, y - y0) for x, y in HAIR], fill=255)
    region = np.asarray(region.filter(ImageFilter.GaussianBlur(8))).astype(np.float32) / 255
    person = np.clip((depth[y0:y1, x0:x1] - 1.4) / 0.9, 0, 1).astype(np.float32)
    silhouette = np.clip(cv2.ximgproc.guidedFilter(guide=crop.astype(np.float32) / 255, src=person, radius=5, eps=2e-3), 0, 1)
    alpha = (silhouette * region)[..., None]
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0] * 100 / 255
    smooth = cv2.GaussianBlur(L, (0, 0), 1.2)              # suaviza el aspecto de «pelaje»
    mid = np.median(L[alpha[..., 0] > 0.8])
    new = 17 + (smooth - mid) * 0.7 + (L - smooth) * 0.55
    edge = cv2.GaussianBlur((silhouette > 0.5).astype(np.float32), (0, 0), 6)
    rim = np.clip((1 - edge) * 2.2, 0, 1) * (silhouette > 0.2)
    top = np.clip(1.2 - np.arange(y1 - y0)[:, None] / (y1 - y0) * 1.6, 0, 1)
    new = np.clip(new + rim * 16 * top, 4, 68)
    lab = np.stack([new * 255 / 100, np.full_like(L, 128 + 3.5), np.full_like(L, 128 + 9)], -1).astype(np.uint8)
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float32)
    out = img8.copy()
    out[y0:y1, x0:x1] = np.clip(crop * (1 - alpha) + rgb * alpha, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def depth_of_field(image, depth, sharp):
    """Desenfoque de lente según la profundidad: nítido el plano del hombre y del monitor.

    Cada nivel de desenfoque es una convolución normalizada que solo toma los píxeles
    que también se desenfocan, para que el sujeto nítido no deje halos en el fondo."""
    img = np.asarray(image).astype(np.float32)
    radius = np.where(depth < 2.2, (2.2 - depth) * 10, 0) + np.where(depth > 5.2, (depth - 5.2) * 3, 0)
    radius = cv2.GaussianBlur(np.clip(radius, 0, 18).astype(np.float32), (0, 0), 6) * (1 - sharp)
    weight = np.clip(radius / 1.5, 0, 1).astype(np.float32)
    levels = [0, 2, 4, 7, 11, 16]
    layers = [img]
    for r in levels[1:]:
        num = cv2.GaussianBlur(img * weight[..., None], (0, 0), r / 2)
        den = cv2.GaussianBlur(weight, (0, 0), r / 2)[..., None]
        plain = cv2.GaussianBlur(img, (0, 0), r / 2)
        layers.append(np.where(den > 0.05, num / np.maximum(den, 1e-6), plain))
    out = np.zeros_like(img)
    for i in range(len(levels) - 1):
        lo, hi = levels[i], levels[i + 1]
        t = np.clip((radius - lo) / (hi - lo), 0, 1)[..., None]
        inside = ((radius >= lo) & ((radius < hi) | (i == len(levels) - 2)))[..., None]
        out = np.where(inside, layers[i] * (1 - t) + layers[i + 1] * t, out)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def grade(image, sharp):
    """Corrección de color: más contraste, luz cálida, algo más de color y viñeta suave."""
    img = np.asarray(image).astype(np.float32) / 255
    curve = img * img * (3 - 2 * img)                       # curva en S
    img = img * 0.72 + curve * 0.28
    luma = (img @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    img = luma + (img - luma) * 1.12                        # saturación
    img = img * np.float32([1.025, 1.0, 0.965]) * (0.35 + 0.65 * luma) + img * (0.65 - 0.65 * luma)
    h, w = luma.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt(((xx - w * 0.55) / w) ** 2 + ((yy - h * 0.5) / h) ** 2)
    img *= (1 - np.clip(dist - 0.35, 0, 1) * 0.22)[..., None]
    # Un poco más de definición en el hombre
    blur = cv2.GaussianBlur(img, (0, 0), 3)
    img = img + (img - blur) * 0.35 * sharp[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))


def quad_mask(size, quad, feather):
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).polygon(quad, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(feather)) if feather else mask


def clean_board(image):
    """Borra lo escrito en la pizarra conservando la luz que le llega desde la ventana."""
    arr = np.asarray(image).astype(np.float32)
    x0, y0 = min(p[0] for p in BOARD) - 40, min(p[1] for p in BOARD) - 40
    x1, y1 = max(p[0] for p in BOARD) + 40, max(p[1] for p in BOARD) + 40
    region = arr[y0:y1, x0:x1]
    # Fondo de la pizarra: cierre morfológico (borra los trazos oscuros) y suavizado
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    background = cv2.morphologyEx(region, cv2.MORPH_CLOSE, kernel)
    background = cv2.GaussianBlur(background, (0, 0), 14)
    rng = np.random.default_rng(3)
    background += rng.normal(0, 1.1, background.shape[:2])[..., None]
    mask = np.asarray(quad_mask(image.size, BOARD, 3)).astype(np.float32)[y0:y1, x0:x1, None] / 255
    arr[y0:y1, x0:x1] = region * (1 - mask) + background * mask
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def marker_sketch(w, h):
    """Gráfico de barras con tendencia, dibujado a mano alzada (tinta azul y naranja)."""
    ss = 4
    layer = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = np.random.default_rng(5)
    navy, orange = (32, 44, 78, 185), (226, 92, 34, 200)

    def stroke(points, color, width):
        pts = [((x + rng.normal(0, 0.6)) * ss, (y + rng.normal(0, 0.6)) * ss) for x, y in points]
        d.line(pts, fill=color, width=int(width * ss), joint='curve')
        for x, y in (pts[0], pts[-1]):
            r = width * ss / 2
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def scribble(x, y, length, height=5):
        # «Letra» ilegible: una línea ondulada continua
        n = int(length / 4)
        pts = [(x + i * length / n, y + np.sin(i * 1.9 + rng.uniform(0, 1)) * height * rng.uniform(0.5, 1)) for i in range(n + 1)]
        stroke(pts, navy, 2.2)

    # Título y notas
    scribble(30, 34, 120, 6)
    stroke([(30, 50), (150, 49)], navy, 2.2)
    scribble(214, 36, 70, 5)
    # Ejes
    stroke([(42, 92), (42, 300), (300, 300)], navy, 3)
    # Barras crecientes
    for i, top in enumerate((236, 210, 176, 132)):
        x = 66 + i * 56
        stroke([(x, 300), (x, top), (x + 34, top), (x + 34, 300)], navy, 3)
        for k in range(1, 4):   # sombreado
            yy = top + (300 - top) * k / 4
            stroke([(x + 6, yy), (x + 28, yy - 10)], navy, 1.6)
    # Tendencia en naranja con flecha
    trend = [(70, 228), (126, 198), (182, 168), (238, 120), (292, 86)]
    stroke(trend, orange, 3.4)
    stroke([(268, 84), (292, 86), (284, 108)], orange, 3.4)
    # Nota a la derecha, encerrada
    scribble(250, 160, 52, 4)
    stroke([(244, 150), (306, 148), (308, 174), (244, 176), (244, 150)], orange, 2.4)
    scribble(60, 330, 150, 5)
    return layer.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))


def paste_warped(image, overlay, quad, opacity=1.0):
    """Pega overlay (RGBA) deformado en perspectiva sobre las cuatro esquinas quad."""
    ow, oh = overlay.size
    src = np.float32([(0, 0), (ow, 0), (ow, oh), (0, oh)])
    matrix = cv2.getPerspectiveTransform(src, np.float32(quad))
    rgba = np.asarray(overlay.convert('RGBA')).astype(np.float32)
    warped = cv2.warpPerspective(rgba, matrix, image.size, flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    alpha = np.clip(warped[..., 3:4] / 255 * opacity, 0, 1)
    base = np.asarray(image).astype(np.float32)
    out = base * (1 - alpha) + np.clip(warped[..., :3], 0, 255) * alpha
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def ink(image, sketch, quad):
    """Tinta sobre la pizarra: multiplica el color del trazo por la superficie."""
    ow, oh = sketch.size
    matrix = cv2.getPerspectiveTransform(np.float32([(0, 0), (ow, 0), (ow, oh), (0, oh)]), np.float32(quad))
    rgba = np.asarray(sketch).astype(np.float32) / 255
    warped = cv2.warpPerspective(rgba, matrix, image.size, flags=cv2.INTER_LINEAR)
    base = np.asarray(image).astype(np.float32) / 255
    alpha = warped[..., 3:4]
    tinted = base * (1 - alpha) + base * warped[..., :3] * alpha
    return Image.fromarray((np.clip(tinted, 0, 1) * 255 + 0.5).astype(np.uint8))


def glow(image, quad):
    """Leve resplandor de la pantalla sobre el marco del monitor y el escritorio."""
    light = np.asarray(quad_mask(image.size, quad, 0)).astype(np.float32) / 255
    light = cv2.GaussianBlur(light, (0, 0), 45)[..., None]
    img = np.asarray(image).astype(np.float32)
    img = img + (255 - img) * light * 0.16
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def screen(image, quad):
    """La ventana del asistente en la pantalla del monitor, con la luz de la foto."""
    ui = Image.open(CACHE / 'pantalla.png').convert('RGB')
    width = int(max(quad[1][0], quad[2][0]) - min(quad[0][0], quad[3][0]))
    ui = ui.resize((width, round(width * ui.height / ui.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.35))
    # Leve caída de luz hacia el borde más lejano (derecha), como en la foto
    arr = np.asarray(ui).astype(np.float32)
    falloff = np.linspace(1.0, 0.93, arr.shape[1])[None, :, None]
    ui = Image.fromarray(np.clip(arr * falloff, 0, 255).astype(np.uint8)).convert('RGBA')
    return paste_warped(image, ui, quad)


if __name__ == '__main__':
    CACHE.mkdir(parents=True, exist_ok=True)
    big = CACHE / 'oficina-x4.png'
    if big.exists():
        image = Image.open(big).convert('RGB')
    else:
        print('  superresolución x4 (unos minutos)...')
        image = upscale(Image.open(SOURCE))
        image.save(big)
    scene = json.loads((SITE / 'src' / 'hero.json').read_text(encoding='utf-8'))['claro']
    assert image.size == (scene['w'], scene['h']), image.size
    quad = [tuple(p) for p in scene['screen']]
    depth = depth_map(Image.open(SOURCE), image.size)
    sharp = man_mask(image, depth)
    image = retouch_hair(image, depth)
    image = clean_board(image)
    image = ink(image, marker_sketch(330, 370), BOARD)
    image = depth_of_field(image, depth, sharp)
    image = grade(image, sharp)
    image = glow(image, quad)
    image = screen(image, quad)
    image.save(CACHE / 'oficina-final.png')
    OUT.mkdir(parents=True, exist_ok=True)
    for width in scene['widths']:
        target = OUT / f"{scene['img']}-{width}.webp"
        resized = image if width == image.width else image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
        resized.save(target, 'WEBP', quality=82, method=6)
        print(f'  {target.relative_to(SITE)} ({target.stat().st_size // 1024} KB)')
