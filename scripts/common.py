"""Shared helpers: outlined text, packing geometry, palette, SVG builder."""
import json
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONTS = {
    "title": "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "serif-it": "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
    "sans": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "mono-b": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
}

INK = "#ece6d8"
BG = "#0a0a0c"
PINK = "#d78fc2"
GREENS = ["#6f9c88", "#5f8c78", "#7fac98", "#4f7664", "#6a957f", "#5a8571"]
CYAN, RED = "#00e5ff", "#ff2d55"
STREAKS = ["#ff2d55", "#00e5ff", "#ffd400", "#2f6bff", "#39ff88", "#ff7a00",
           "#ffffff", "#c86bff", "#ff4fa3"]

W, H = 1200, 1600

_fonts = {}


def _font(name):
    if name not in _fonts:
        f = TTFont(FONTS[name])
        _fonts[name] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _fonts[name]


def text_width(s, name, size, tracking=0.0):
    gs, cmap, upm = _font(name)
    return sum(gs[cmap[ord(c)]].width for c in s) * size / upm + tracking * (len(s) - 1)


def text(s, name, size, x, y, anchor="start", tracking=0.0):
    """SVG path data for string s with its baseline at (x, y)."""
    gs, cmap, upm = _font(name)
    k = size / upm
    w = text_width(s, name, size, tracking)
    x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
    pen = SVGPathPen(gs)
    for c in s:
        g = gs[cmap[ord(c)]]
        g.draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        x += g.width * k + tracking
    return pen.getCommands()


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def load_packing():
    pk = json.load(open(os.path.join(ROOT, "design", "packing.json")))
    return pk["side"], pk["squares"], pk["tilted"]


def packing_px(x, y, size, squares=None, side=None):
    """Squares as pixel polygons (y down), container top-left at (x, y)."""
    S, sq, _ = load_packing()
    if squares is not None:
        sq = squares
    if side is not None:
        S = side
    u = size / S
    return [[(x + px * u, y + (S - py) * u) for px, py in q] for q in sq]


def colours(n_tilted=5, n=11):
    return [PINK] * n_tilted + [GREENS[i % len(GREENS)] for i in range(n - n_tilted)]


def poly_d(pts):
    return "M" + " L".join(f"{fmt(a)},{fmt(b)}" for a, b in pts) + " Z"


def row_span(pts, y):
    """Horizontal extent [xl, xr] of convex polygon pts at height y, or None."""
    xs = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return (min(xs), max(xs)) if len(xs) >= 2 else None


class SVG:
    def __init__(self, title):
        self.title = title
        self.out = []
        self.n = 0

    def add(self, s):
        self.out.append(s)

    def uid(self, p="c"):
        self.n += 1
        return f"{p}{self.n}"

    def rect(self, x, y, w, h, fill, op=1.0, extra=""):
        o = "" if op >= 1 else f' opacity="{op:.2f}"'
        self.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" fill="{fill}"{o}{extra}/>')

    def path(self, d, fill, op=1.0, extra=""):
        o = "" if op >= 1 else f' opacity="{op:.2f}"'
        self.add(f'<path d="{d}" fill="{fill}"{o}{extra}/>')

    def packing(self, x, y, size, outline=True, gap=2.5, bg=True):
        """The clean packing: solid squares, thin dark gaps, ink container."""
        if bg:
            self.rect(x, y, size, size, BG)
        for pts, c in zip(packing_px(x, y, size), colours()):
            self.path(poly_d(pts), c, extra=f' stroke="{BG}" stroke-width="{gap}" stroke-linejoin="round"')
        if outline:
            self.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}" '
                     f'fill="none" stroke="{INK}" stroke-width="3"/>')

    def glitch_word(self, word, font, size, x, y, anchor="start", split=5,
                    slices=((-34 / 128, 22 / 128, 22),), fill=INK, op=1.0):
        """RGB-split word with horizontal tracking slips.

        slices: (top offset from baseline, height, dx) with offsets/heights as
        fractions of the font size.
        """
        g = f' opacity="{op:.2f}"' if op < 1 else ""
        self.add(f"<g{g}>")
        self.path(text(word, font, size, x - split, y, anchor), CYAN, 0.8)
        self.path(text(word, font, size, x + split, y, anchor), RED, 0.8)
        self.path(text(word, font, size, x, y, anchor), fill)
        for top, h, dx in slices:
            cid = self.uid("ws")
            sy, sh = y + top * size, h * size
            self.add(f'<clipPath id="{cid}"><rect x="0" y="{fmt(sy)}" width="{W}" height="{fmt(sh)}"/></clipPath>')
            self.add(f'<g clip-path="url(#{cid})">')
            self.rect(0, sy, W, sh, BG)
            self.path(text(word, font, size, x + dx + 8 * (1 if dx >= 0 else -1), y, anchor), CYAN, 0.8)
            self.path(text(word, font, size, x + dx, y, anchor), fill)
            self.add("</g>")
        self.add("</g>")

    def grain(self, rng, n, box=(0, 0, W, H), op=(0.15, 0.55)):
        x0, y0, x1, y1 = box
        for _ in range(n):
            s = rng.choice([1.5, 2, 2, 3])
            c = rng.choice(["#ffffff", "#ffffff", "#9aa0a6", rng.choice(STREAKS)])
            self.rect(rng.uniform(x0, x1), rng.uniform(y0, y1), s, s, c, rng.uniform(*op))

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
                f'width="{W / 100}in" height="{H / 100}in">\n<title>{self.title}</title>\n'
                f'<!-- layer "shirt": delete for printing on a black garment -->\n'
                f'<rect id="shirt" width="{W}" height="{H}" fill="{BG}"/>\n')
        open(path, "w").write(head + "\n".join(self.out) + "\n</svg>\n")
