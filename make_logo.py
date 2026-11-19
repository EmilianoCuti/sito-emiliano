#!/usr/bin/env python3
"""Genera il marchio «e rovesciata + c» in SVG, dai contorni di Georgia.

Il segno è composto da una «e» a sinistra e da una «c» a destra, della stessa
dimensione e accostate fino a sfiorarsi. La «e» è la curva della «c» ruotata di
180°, con una barra centrale più corta del taglio originale: così il trattino
non attraversa tutta la bocca della lettera.

I contorni sono convertiti in tracciati, quindi il logo non dipende dai font
installati sul computer del visitatore.

Uso:  python make_logo.py
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
# Georgia è il font usato per il marchio. Il logo già pronto è in assets/logo.svg:
# questo script serve solo se lo si vuole rigenerare.
CANDIDATI = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/Library/Fonts/Georgia.ttf",
    os.path.expanduser("~/Library/Fonts/Georgia.ttf"),
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/Georgia.ttf",
]
FONT = next((p for p in CANDIDATI if os.path.exists(p)), CANDIDATI[0])
INK = "#17140f"
CARTA = "#f7f3ea"

GAP = 14        # unità di font fra la e e la c (si sfiorano)
BARRA_L = 300   # lunghezza della barra centrale della e
BARRA_H = 80    # spessore della barra


def contorno(font, gs, cmap, carattere):
    nome = cmap[ord(carattere)]
    pen = SVGPathPen(gs)
    gs[nome].draw(pen)
    bounds = BoundsPen(gs)
    gs[nome].draw(bounds)
    return pen.getCommands(), bounds.bounds


def segno():
    font = TTFont(FONT)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    d_c, (cx0, cy0, cx1, cy1) = contorno(font, gs, cmap, "c")

    # la e è la c ruotata di 180° attorno al centro, spostata a sinistra
    centro = ((cx0 + cx1) / 2, (cy0 + cy1) / 2)
    dx = cx0 - cx1 - GAP
    sinistra = cx0 + dx
    barra_x = sinistra + 95
    barra_y = centro[1] - BARRA_H / 2
    bbox = (sinistra, cy0, cx1, cy1)
    return d_c, centro, dx, (barra_x, barra_y, BARRA_L, BARRA_H), bbox


def gruppo(d_c, centro, dx, barra, colore):
    bx, by, bw, bh = barra
    return (
        '<g fill="%s">'
        '<g transform="translate(%.2f 0) rotate(180 %.2f %.2f)"><path d="%s"/></g>'
        '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="16"/>'
        '<path d="%s"/>'
        '</g>' % (colore, dx, centro[0], centro[1], d_c, bx, by, bw, bh, d_c)
    )


def logo_quadrato(d_c, centro, dx, barra, bbox, lato, padding, fondo, segno_colore):
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    s = min((lato - 2 * padding) / w, (lato - 2 * padding) / h)
    ox = (lato - w * s) / 2 - x0 * s
    oy = (lato - h * s) / 2 + y1 * s
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="Marchio: e rovesciata e c">\n'
        '<rect width="%d" height="%d" fill="%s"/>\n'
        '<g transform="translate(%.2f %.2f) scale(%.4f -%.4f)">%s</g>\n'
        '</svg>\n'
        % (lato, lato, lato, lato, lato, lato, fondo,
           ox, oy, s, s, gruppo(d_c, centro, dx, barra, segno_colore))
    )


def logo_trasparente(d_c, centro, dx, barra, bbox, colore, padding=6):
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.2f %.2f %.2f %.2f" width="%.0f" height="%.0f" role="img" aria-label="Marchio: e rovesciata e c">\n'
        '<g transform="scale(1 -1)">%s</g>\n'
        '</svg>\n'
        % (x0 - padding, -(y1 + padding), w + 2 * padding, h + 2 * padding,
           w + 2 * padding, h + 2 * padding, gruppo(d_c, centro, dx, barra, colore))
    )


def main():
    if not os.path.exists(FONT):
        raise SystemExit(
            "Georgia.ttf non trovato. Il marchio già pronto è in assets/logo.svg; "
            "per rigenerarlo installa il font Georgia o modifica la costante FONT.")
    d_c, centro, dx, barra, bbox = segno()
    out = os.path.join(HERE, "assets")
    os.makedirs(out, exist_ok=True)

    with open(os.path.join(out, "logo.svg"), "w", encoding="utf-8") as f:
        f.write(logo_quadrato(d_c, centro, dx, barra, bbox, 100, 10, INK, CARTA))
    with open(os.path.join(out, "logo-segno.svg"), "w", encoding="utf-8") as f:
        f.write(logo_trasparente(d_c, centro, dx, barra, bbox, INK))
    with open(os.path.join(out, "logo-segno-chiaro.svg"), "w", encoding="utf-8") as f:
        f.write(logo_trasparente(d_c, centro, dx, barra, bbox, CARTA))
    with open(os.path.join(out, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(logo_quadrato(d_c, centro, dx, barra, bbox, 64, 8, INK, CARTA))
    print("Logo generato: logo.svg, logo-segno.svg, logo-segno-chiaro.svg, favicon.svg")


if __name__ == "__main__":
    main()
