#!/bin/bash
# Genera src/assets/video/asistente-{es,en}.{mp4,webm,webp} a partir de la escena (tools/video/escena.html).
# Requiere Node con Playwright (npm i playwright) y ffmpeg, y el sitio servido en http://localhost:8077.
set -e
cd "$(dirname "$0")/../.."
mkdir -p src/assets/video
for L in es en; do
  rm -rf /tmp/asistente-$L && node tools/video/render.cjs $L /tmp/asistente-$L 30
  ffmpeg -y -hide_banner -loglevel error -framerate 30 -i /tmp/asistente-$L/f-%04d.png -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart src/assets/video/asistente-$L.mp4
  ffmpeg -y -hide_banner -loglevel error -framerate 30 -i /tmp/asistente-$L/f-%04d.png -c:v libvpx-vp9 -crf 34 -b:v 0 -row-mt 1 -pix_fmt yuv420p src/assets/video/asistente-$L.webm
  ffmpeg -y -hide_banner -loglevel error -i /tmp/asistente-$L/f-0345.png -c:v libwebp -quality 80 src/assets/video/asistente-$L.webp
done
ls -la src/assets/video
