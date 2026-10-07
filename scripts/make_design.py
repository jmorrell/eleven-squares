"""Generate the s(11) t-shirt design as a self-contained vector SVG.

All text is converted to outlines (no font dependencies at print time) and the
"tape glitch" is built from plain rectangles, clip paths and <use> copies, so
the file opens in Illustrator / Inkscape / Affinity as ordinary vector art.

usage: python3 scripts/make_design.py [seed]
"""
import json
import random
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 11
rng = random.Random(SEED)

FONTS = {
    "title": "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "serif-it": "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
    "sans": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "mono-b": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
}
_fonts = {}

INK = "#ece6d8"        # warm off-white, like aged J-card print
BG = "#0a0a0c"
PINK = "#d78fc2"
GREENS = ["#6f9c88", "#5f8c78", "#7fac98", "#4f7664", "#6a957f", "#5a8571"]
STREAKS = ["#ff2d55", "#00e5ff", "#ffd400", "#2f6bff", "#39ff88", "#ff7a00",
           "#ffffff", "#c86bff", "#ff4fa3"]

W, H = 1200, 1600                    # artboard (1 unit = 1/100 in at 12x16 in)
CX0, CY0, CX1, CY1 = 90, 60, 1110, 1540   # the "J-card"


def font(name):
    if name not in _fonts:
        f = TTFont(FONTS[name])
        _fonts[name] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _fonts[name]


def text_width(s, name, size):
    f, gs, cmap, upm = font(name)
    return sum(gs[cmap[ord(c)]].width for c in s) * size / upm


def text(s, name, size, x, y, anchor="start", tracking=0.0):
    """Return an SVG path 'd' for string s with baseline at (x, y)."""
    f, gs, cmap, upm = font(name)
    k = size / upm
    w = text_width(s, name, size) + tracking * (len(s) - 1)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    pen = SVGPathPen(gs)
    for c in s:
        g = gs[cmap[ord(c)]]
        g.draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        x += g.width * k + tracking
    return pen.getCommands()


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- packing art
pk = json.load(open("design/packing.json"))
S = pk["side"]
ART = 660                                   # rendered container size
AX, AY = (W - ART) / 2, 520                 # top-left of container
U = ART / S


def to_px(p):
    return AX + p[0] * U, AY + (S - p[1]) * U


def poly(pts):
    return "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in map(to_px, pts)) + " Z"


squares = []
gi = 0
for i, q in enumerate(pk["squares"]):
    if i < pk["tilted"]:
        squares.append((poly(q), PINK))
    else:
        squares.append((poly(q), GREENS[gi % len(GREENS)]))
        gi += 1

out = []
add = out.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    f'viewBox="0 0 {W} {H}" width="{W / 100}in" height="{H / 100}in">')
add("<title>s(11) = 3.87708359… — eleven squares, optimal</title>")
add("<defs>")
add(f'<clipPath id="card"><rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}"/></clipPath>')

# the packing itself, defined once and reused for every glitch copy
add('<g id="pack">')
add(f'<rect x="{fmt(AX)}" y="{fmt(AY)}" width="{ART}" height="{ART}" fill="{BG}"/>')
for d, c in squares:
    add(f'<path d="{d}" fill="{c}" stroke="{BG}" stroke-width="2.5" stroke-linejoin="round"/>')
add(f'<rect x="{fmt(AX)}" y="{fmt(AY)}" width="{ART}" height="{ART}" fill="none" '
    f'stroke="{INK}" stroke-width="3"/>')
add("</g>")
# outline-only version for the chromatic-aberration ghosts
add('<g id="ghost" fill="none" stroke-width="3">')
for d, _ in squares:
    add(f'<path d="{d}"/>')
add(f'<rect x="{fmt(AX)}" y="{fmt(AY)}" width="{ART}" height="{ART}"/>')
add("</g>")
add("</defs>")

add(f'<g clip-path="url(#card)">')
add(f'<rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" fill="{BG}"/>')


# ------------------------------------------------------------ tape streaks
def streak_band(y0, y1, n, op=(0.25, 0.95), wmax=520, grey=0.3):
    for _ in range(n):
        y = rng.uniform(y0, y1)
        h = rng.choice([1, 2, 2, 3, 4, 6, 9, 14])
        x = rng.uniform(CX0 - 100, CX1)
        w = rng.uniform(20, wmax)
        c = rng.choice(STREAKS) if rng.random() >= grey else rng.choice(["#8a8a8a", "#cfcfcf", "#3a3a3a"])
        add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{h}" fill="{c}" '
            f'opacity="{rng.uniform(*op):.2f}"/>')


# grey "dropout" texture: wide, faint bars over the whole card
for _ in range(90):
    y = rng.uniform(CY0, CY1)
    add(f'<rect x="{CX0}" y="{fmt(y)}" width="{CX1 - CX0}" height="{rng.choice([1, 2, 3, 5, 8])}" '
        f'fill="{rng.choice(["#ffffff", "#9aa0a6", "#5b6168"])}" opacity="{rng.uniform(0.03, 0.12):.2f}"/>')

# denser coloured clusters, like the cassette's corrupted rows
bands = [(CY0 + 20, CY0 + 120, 25), (300, 340, 35), (430, 470, 30),
         (690, 760, 40), (940, 1000, 45), (1150, 1200, 40), (1330, 1420, 55)]
for y0, y1, n in bands:
    streak_band(y0, y1, n)

# ------------------------------------------------------------ the packing
for colour, dx, dy in (("#00e5ff", -7, 0), ("#ff2d55", 7, 2)):
    add(f'<use xlink:href="#ghost" href="#ghost" stroke="{colour}" opacity="0.85" '
        f'transform="translate({dx},{dy})"/>')
add('<use xlink:href="#pack" href="#pack"/>')

# horizontal slice displacement (tracking error)
y = AY - 10
k = 0
while y < AY + ART + 10:
    h = rng.choice([3, 5, 8, 12, 18, 26, 40])
    if rng.random() < 0.35:
        dx = rng.choice([-1, 1]) * rng.uniform(6, 70)
        cid = f"s{k}"
        k += 1
        add(f'<clipPath id="{cid}"><rect x="{CX0}" y="{fmt(y)}" width="{CX1 - CX0}" height="{h}"/></clipPath>')
        add(f'<g clip-path="url(#{cid})">')
        add(f'<rect x="{CX0}" y="{fmt(y)}" width="{CX1 - CX0}" height="{h}" fill="{BG}"/>')
        tint = rng.random()
        if tint < 0.25:   # slice shows only one colour channel
            add(f'<use xlink:href="#ghost" href="#ghost" stroke="{rng.choice(STREAKS)}" '
                f'transform="translate({fmt(dx)},0)"/>')
        else:
            add(f'<use xlink:href="#pack" href="#pack" transform="translate({fmt(dx)},0)"/>')
            if tint > 0.8:  # with a bleed of colour across the row
                add(f'<rect x="{CX0}" y="{fmt(y)}" width="{CX1 - CX0}" height="{h}" '
                    f'fill="{rng.choice(STREAKS)}" opacity="0.35"/>')
        add("</g>")
    y += h + rng.uniform(4, 60)

# streaks that run across the art
streak_band(AY + 60, AY + ART - 40, 30, op=(0.15, 0.6), wmax=320, grey=0.1)

# ------------------------------------------------------------ type
add(f'<g fill="{INK}">')
add(f'<path d="{text("Eleven", "title", 104, 140, 190)}"/>')
add(f'<path d="{text("Squares", "title", 104, 140, 292)}"/>')
# s(11) = 3.87708359…
x = 140
for run, f in (("s", "serif-it"), ("(11) = 3.87708359…", "serif")):
    add(f'<path d="{text(run, f, 58, x, 398)}"/>')
    x += text_width(run, f, 58)
add(f'<path d="{text("n = 11   ⊢ optimal   ∎ Lean", "mono", 22, 142, 450, tracking=1.5)}"/>')
add("</g>")

# little row of "LED" dots, homage to the reference
dots = ["#ff2d55", "#ffd400", "#39ff88", "#00e5ff", "#2f6bff", "#c86bff", "#ffffff"]
for i, c in enumerate(dots):
    add(f'<rect x="{620 + i * 22}" y="438" width="14" height="14" rx="7" fill="{c}" opacity="0.9"/>')

# big sans word, with its own RGB split + slice
WORD, WY = "Optimal", 1340
for colour, dx in (("#00e5ff", -5), ("#ff2d55", 5)):
    add(f'<path d="{text(WORD, "sans", 128, 140 + dx, WY)}" fill="{colour}" opacity="0.8"/>')
add(f'<path d="{text(WORD, "sans", 128, 140, WY)}" fill="{INK}"/>')
# tracking slip through the lower half of the word (a shift, not a strikethrough)
SY, SH = WY - 34, 22
add(f'<clipPath id="wslice"><rect x="{CX0}" y="{SY}" width="{CX1 - CX0}" height="{SH}"/></clipPath>')
add(f'<g clip-path="url(#wslice)"><rect x="{CX0}" y="{SY}" width="{CX1 - CX0}" height="{SH}" fill="{BG}"/>'
    f'<path d="{text(WORD, "sans", 128, 140 + 30, WY)}" fill="#00e5ff" opacity="0.8"/>'
    f'<path d="{text(WORD, "sans", 128, 140 + 22, WY)}" fill="{INK}"/></g>')

# footer, on a paper strip like the cassette label
add(f'<rect x="{CX0 + 30}" y="1440" width="{CX1 - CX0 - 60}" height="70" fill="{INK}" opacity="0.92"/>')
add(f'<g fill="{BG}">')
add(f'<path d="{text("SIDE A — n = 11", "mono-b", 22, 140, 1484, tracking=1)}"/>')
add(f'<path d="{text("W. TRUMP 1979", "mono-b", 18, 1060, 1470, "end", tracking=1)}"/>')
add(f'<path d="{text("LEAN 4 · 2026", "mono-b", 18, 1060, 1497, "end", tracking=1)}"/>')
add("</g>")

# final over-print: a few bright scratches and grain
streak_band(CY0, CY1, 14, op=(0.15, 0.5), wmax=700)
for _ in range(1400):
    x, y = rng.uniform(CX0, CX1), rng.uniform(CY0, CY1)
    s = rng.choice([1.5, 2, 2, 3])
    add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{s}" height="{s}" '
        f'fill="{rng.choice(["#ffffff", "#ffffff", "#9aa0a6", rng.choice(STREAKS)])}" '
        f'opacity="{rng.uniform(0.15, 0.6):.2f}"/>')
add("</g>")

# worn edge of the card
add(f'<rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" fill="none" '
    f'stroke="#2a2a2e" stroke-width="2"/>')
add("</svg>")

open("design/eleven-squares.svg", "w").write("\n".join(out))
print("wrote design/eleven-squares.svg", len(out), "elements")
