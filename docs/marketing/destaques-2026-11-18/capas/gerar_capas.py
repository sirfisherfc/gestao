"""Sir Fisher: capas vetoriais de Destaques, sem fotos nem ativos externos.

Reproduzir: python gerar_capas.py
Dependência: Pillow. Os SVG e os PNG são gerados da mesma lista de formas.
Nenhuma chamada de rede ou publicação é realizada.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageChops, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
NAVY = "#12293d"
CREAM = "#f6ecd9"
GOLD = "#f0a63f"
INK_SOFT = "#4c6274"
STROKE = 8.0
SIZE = 1080
SUPERSAMPLE = 3


def path(d, stroke=CREAM, width=STROKE, fill=None):
    return {"kind": "path", "d": d, "stroke": stroke, "width": width, "fill": fill}


def circle(cx, cy, radius, stroke=CREAM, width=STROKE, fill=None):
    return {"kind": "circle", "cx": cx, "cy": cy, "r": radius,
            "stroke": stroke, "width": width, "fill": fill}


COVERS = [
    {
        "slug": "01-a-casa", "label": "A Casa", "icon": "guarda-sol e ondas",
        "shapes": [
            circle(187, 66, 9, stroke=None, fill=GOLD),
            path([("M", 59, 112), ("C", 68, 52, 188, 52, 197, 112), ("Z",)]),
            path([("M", 128, 70), ("C", 111, 83, 106, 94, 105, 112)], width=6),
            path([("M", 128, 70), ("C", 145, 83, 150, 94, 151, 112)], width=6),
            path([("M", 128, 113), ("L", 128, 163)]),
            path([("M", 61, 178), ("C", 72, 170, 83, 170, 94, 178),
                  ("C", 105, 186, 116, 186, 127, 178),
                  ("C", 138, 170, 149, 170, 160, 178),
                  ("C", 171, 186, 182, 186, 193, 178)]),
            path([("M", 78, 198), ("C", 89, 190, 100, 190, 111, 198),
                  ("C", 122, 206, 133, 206, 144, 198),
                  ("C", 155, 190, 166, 190, 177, 198)]),
        ],
    },
    {
        "slug": "02-sabores", "label": "Sabores", "icon": "prato e talheres",
        "shapes": [
            circle(128, 128, 46),
            path([("M", 60, 78), ("L", 60, 115),
                  ("C", 60, 131, 82, 131, 82, 115), ("L", 82, 78)]),
            path([("M", 71, 79), ("L", 71, 189)]),
            path([("M", 193, 188), ("L", 193, 78),
                  ("C", 177, 94, 177, 112, 177, 131), ("L", 193, 131)]),
            path([("M", 105, 136), ("C", 117, 145, 139, 145, 151, 136)],
                 stroke=GOLD),
        ],
    },
    {
        "slug": "03-drinks", "label": "Drinks", "icon": "taca",
        "shapes": [
            path([("M", 80, 72), ("L", 80, 104),
                  ("C", 80, 135, 101, 153, 128, 153),
                  ("C", 155, 153, 176, 135, 176, 104),
                  ("L", 176, 72), ("Z",)]),
            path([("M", 92, 110), ("C", 111, 118, 145, 118, 164, 110)],
                 stroke=GOLD),
            path([("M", 128, 154), ("L", 128, 199)]),
            path([("M", 98, 199), ("L", 158, 199)]),
        ],
    },
    {
        "slug": "04-quem-veio", "label": "Quem Veio", "icon": "balao com coracao",
        "shapes": [
            path([("M", 87, 70), ("L", 169, 70),
                  ("C", 185, 70, 196, 82, 196, 98),
                  ("L", 196, 145), ("C", 196, 161, 185, 173, 169, 173),
                  ("L", 113, 173), ("L", 79, 196), ("L", 79, 172),
                  ("C", 66, 169, 60, 158, 60, 145),
                  ("L", 60, 98), ("C", 60, 82, 71, 70, 87, 70), ("Z",)]),
            path([("M", 128, 146), ("C", 119, 138, 103, 126, 103, 115),
                  ("C", 103, 100, 121, 96, 128, 108),
                  ("C", 135, 96, 153, 100, 153, 115),
                  ("C", 153, 126, 137, 138, 128, 146), ("Z",)],
                 stroke=None, fill=GOLD),
        ],
    },
    {
        "slug": "05-visite", "label": "Visite", "icon": "pin de localizacao",
        "shapes": [
            path([("M", 128, 199), ("C", 116, 181, 77, 141, 77, 111),
                  ("C", 77, 80, 99, 61, 128, 61),
                  ("C", 157, 61, 179, 80, 179, 111),
                  ("C", 179, 141, 140, 181, 128, 199), ("Z",)]),
            circle(128, 111, 16, stroke=None, fill=GOLD),
        ],
    },
]


def svg_path(commands):
    return " ".join(" ".join(map(str, command)) for command in commands)


def svg(cover):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 256 256">',
        f'  <title>{escape("Sir Fisher — " + cover["label"])}</title>',
        f'  <desc>{escape(cover["icon"] + "; fundo azul, traco creme, acento dourado; sem texto na arte.")}</desc>',
        f'  <rect width="256" height="256" fill="{NAVY}"/>',
    ]
    for shape in cover["shapes"]:
        common = (f'fill="{shape["fill"] or "none"}" stroke="{shape["stroke"] or "none"}" '
                  f'stroke-width="{shape["width"]}" stroke-linecap="round" stroke-linejoin="round"')
        if shape["kind"] == "circle":
            parts.append(f'  <circle cx="{shape["cx"]}" cy="{shape["cy"]}" r="{shape["r"]}" {common}/>')
        else:
            parts.append(f'  <path d="{svg_path(shape["d"])}" {common}/>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def sample_path(commands):
    points = []
    start = None
    current = (0, 0)
    closed = False
    for command in commands:
        op, *v = command
        if op == "M":
            current = (v[0], v[1])
            start = current
            points.append(current)
        elif op == "L":
            current = (v[0], v[1])
            points.append(current)
        elif op == "C":
            p0 = current
            p1, p2, p3 = (v[0], v[1]), (v[2], v[3]), (v[4], v[5])
            for step in range(1, 81):
                t = step / 80
                u = 1 - t
                points.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                               u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
            current = p3
        elif op == "Z":
            points.append(start)
            current = start
            closed = True
        else:
            raise ValueError(op)
    return points, closed


def raster(cover):
    size = SIZE * SUPERSAMPLE
    scale = size / 256
    im = Image.new("RGB", (size, size), NAVY)
    draw = ImageDraw.Draw(im)
    for shape in cover["shapes"]:
        if shape["kind"] == "circle":
            x, y, r = shape["cx"]*scale, shape["cy"]*scale, shape["r"]*scale
            if shape["stroke"]:
                # SVG strokes are centred on their paths.
                width = round(shape["width"] * scale)
                r += width / 2
                draw.ellipse((x-r, y-r, x+r, y+r), fill=shape["fill"],
                             outline=shape["stroke"], width=width)
            else:
                draw.ellipse((x-r, y-r, x+r, y+r), fill=shape["fill"])
            continue
        pts, closed = sample_path(shape["d"])
        pts = [(round(x*scale), round(y*scale)) for x, y in pts]
        if shape["fill"]:
            draw.polygon(pts, fill=shape["fill"])
        if shape["stroke"]:
            width = round(shape["width"]*scale)
            draw.line(pts, fill=shape["stroke"], width=width, joint="curve")
            radius = width / 2
            for x, y in (pts[:1] if closed else [pts[0], pts[-1]]):
                draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=shape["stroke"])
    return im.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def font(size, bold=False):
    candidates = (["C:/Windows/Fonts/seguisb.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else
                  ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"])
    candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def centred(draw, xy, text, text_font, fill=NAVY):
    draw.text(xy, text, font=text_font, fill=fill, anchor="mt")


def circular_preview(source, diameter):
    im = source.resize((diameter, diameter), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", (diameter * 3, diameter * 3))
    ImageDraw.Draw(mask).ellipse((0, 0, diameter*3-1, diameter*3-1), fill=255)
    im.putalpha(mask.resize((diameter, diameter), Image.Resampling.LANCZOS))
    return im


def preview(images):
    board = Image.new("RGB", (1800, 925), CREAM)
    draw = ImageDraw.Draw(board)
    draw.text((65, 49), "SIR FISHER", font=font(24, True), fill=INK_SOFT)
    draw.text((65, 92), "Capas dos Destaques", font=font(47, True), fill=NAVY)
    draw.text((65, 157), "Azul da casa. Traço creme. Um acento de sol.", font=font(24), fill=INK_SOFT)
    for i, (cover, source) in enumerate(zip(COVERS, images)):
        x = 65 + i*345
        board.paste(circular_preview(source, 285), (x, 235), circular_preview(source, 285))
        centred(draw, (x+142, 546), cover["label"], font(29, True))
    draw.line((65, 620, 1735, 620), fill="#d2c9b6", width=2)
    draw.text((65, 657), "Teste de leitura · corte circular a 64 px", font=font(25, True), fill=NAVY)
    for i, (cover, source) in enumerate(zip(COVERS, images)):
        x = 176 + i*345
        crop = circular_preview(source, 64)
        board.paste(crop, (x, 724), crop)
        centred(draw, (x+32, 807), cover["label"], font(22))
    draw.text((65, 878), "Nomes ficam fora das capas. Cada arquivo final: 1080 × 1080 px + SVG editável.",
              font=font(20), fill=INK_SOFT)
    board.save(HERE / "previa-capas.png", optimize=True)

    # This second sheet preserves the 64 px test without requiring a large-page zoom.
    strip = Image.new("RGB", (710, 150), CREAM)
    d = ImageDraw.Draw(strip)
    for i, (cover, source) in enumerate(zip(COVERS, images)):
        x = 39+i*140
        crop = circular_preview(source, 64)
        strip.paste(crop, (x, 21), crop)
        centred(d, (x+32, 103), cover["label"], font(17, True))
    strip.save(HERE / "teste-64px.png", optimize=True)


def validate(cover, im):
    bg = Image.new("RGB", im.size, NAVY)
    diff = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > 12 else 0)
    bounds = diff.getbbox()
    x0, y0, x1, y1 = bounds
    max_corner_radius = max(math.hypot(x-540, y-540) for x in (x0, x1) for y in (y0, y1))
    assert im.size == (1080, 1080) and im.mode == "RGB"
    assert max_corner_radius < 486, (cover["slug"], bounds, max_corner_radius)
    return {"file": cover["slug"] + ".png", "size": [1080, 1080], "mode": im.mode,
            "content_bounds_px": list(bounds), "conservative_content_radius_px": round(max_corner_radius, 1),
            "safe_circle_radius_px": 486, "within_safe_circle": True}


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    images, validations = [], []
    for cover in COVERS:
        (HERE / (cover["slug"] + ".svg")).write_text(svg(cover), encoding="utf-8")
        im = raster(cover)
        im.save(HERE / (cover["slug"] + ".png"), optimize=True)
        images.append(im)
        validations.append(validate(cover, im))
    preview(images)
    manifest = {"brand": "Sir Fisher", "date": "2026-11-18", "canvas_px": [1080, 1080],
                "palette": {"background": NAVY, "stroke": CREAM, "accent": GOLD},
                "stroke_width_viewbox": STROKE, "viewbox": [0, 0, 256, 256],
                "categories": [{k: c[k] for k in ("slug", "label", "icon")} for c in COVERS],
                "validation": validations,
                "notes": ["Icones originais em vetor; sem fotos, textura ou redesenho da marca.",
                          "SVG sem elementos de texto visivel; PNG RGB de fundo solido.",
                          "Prancha inclui simulacao circular e amostras reais a 64 px.",
                          "O script escreve apenas nesta pasta. Nenhum acesso a Instagram ou rede."]}
    (HERE / "manifesto-qa.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("5 SVG + 5 PNG 1080px; previa e teste64px; validacao de area segura OK.")


if __name__ == "__main__":
    main()
