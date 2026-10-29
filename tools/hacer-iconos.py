#!/usr/bin/env python3
"""Genera icono-192.png e icono-512.png para una app de estudio.

Uso:  python hacer-iconos.py <carpeta-de-la-app> [letra]

Sin letra, usa la inicial de app.nombre en config.json.
Los colores salen de config.json (primario de fondo, secundario de letra).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def fuente(px):
    for ruta in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, px)
    return ImageFont.load_default()


def main(carpeta, letra=None):
    raiz = Path(carpeta)
    cfg = json.loads((raiz / "config.json").read_text(encoding="utf-8"))
    fondo = cfg.get("colores", {}).get("primario", "#1B2D5B")
    tinta = cfg.get("colores", {}).get("secundario", "#BFDBFF")
    texto = (letra or cfg["app"]["nombre"].strip()[:1]).upper()

    for lado in (192, 512):
        img = Image.new("RGB", (lado, lado), fondo)
        d = ImageDraw.Draw(img)
        f = fuente(int(lado * 0.52))
        caja = d.textbbox((0, 0), texto, font=f)
        d.text(
            ((lado - caja[2] - caja[0]) / 2, (lado - caja[3] - caja[1]) / 2),
            texto, font=f, fill=tinta,
        )
        salida = raiz / f"icono-{lado}.png"
        img.save(salida)
        print("escrito", salida)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
