"""Round-2 concepts: clean packing, glitch lives in the space and type around it.

usage: python3 scripts/concepts.py [seed]   -> design/concepts/*.svg
"""
import math
import os
import random
import sys
from common import (BG, CYAN, GREENS, H, INK, PINK, RED, ROOT, STREAKS, SVG, W,
                    colours, fmt, load_packing, packing_px, poly_d, row_span, text)

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 11
OUT = os.path.join(ROOT, "design", "concepts")
os.makedirs(OUT, exist_ok=True)

S, SQUARES, NT = load_packing()
TAGLINE = "s(11) = 3.87708359…"


def footer(svg, y, left=TAGLINE, right="W. TRUMP 1979 · LEAN 2026", x0=140, x1=1060, size=22):
    svg.path(text(left, "mono", size, x0, y, tracking=1), INK)
    svg.path(text(right, "mono", size * 0.8, x1, y, "end", tracking=1), INK, 0.7)


# ------------------------------------------------------------------ A: signal
def signal(rng):
    """Packing is the clean signal; noise leaks out sideways along its edges."""
    svg = SVG("Optimal — signal")
    X, Y, A = 270, 200, 660
    polys = packing_px(X, Y, A)
    # rows where geometry happens: every vertex height, plus scatter
    rows = sorted({p[1] for q in polys for p in q} | {rng.uniform(Y, Y + A) for _ in range(30)})
    for y in rows:
        for side in (-1, 1):
            if rng.random() < 0.25:
                continue
            for _ in range(rng.choice([1, 1, 2, 3])):
                L = min(rng.expovariate(1 / 140), 280)
                h = rng.choice([1, 2, 2, 3, 5, 8])
                yy = y + rng.uniform(-6, 6)
                c = rng.choice(STREAKS) if rng.random() < 0.8 else rng.choice([PINK, GREENS[0]])
                x = X - L if side < 0 else X + A
                svg.rect(x, yy, L, h, c, rng.uniform(0.35, 1))
    svg.packing(X, Y, A)
    svg.glitch_word("Optimal", "sans", 190, W / 2, 1180, "middle",
                    slices=((-0.27, 0.17, 30),))
    footer(svg, 1330, x0=W / 2 - 330, x1=W / 2 + 330)
    svg.grain(rng, 500, (0, 0, W, 1400), op=(0.1, 0.4))
    return svg


# ------------------------------------------------------------------ B: search
def search(rng):
    """Every rejected arrangement as glitchy ghosts behind the one that won."""
    svg = SVG("Optimal — search space")
    X, Y, A = 300, 260, 600
    cx, cy = S / 2, S / 2

    def perturb():
        f = rng.uniform(1.0, 1.25)
        out = []
        for i, q in enumerate(SQUARES):
            mx = sum(p[0] for p in q) / 4
            my = sum(p[1] for p in q) / 4
            da = math.radians(rng.gauss(0, 12 if i < NT else 4))
            tx, ty = rng.gauss(0, 0.3), rng.gauss(0, 0.3)
            ca, sa = math.cos(da), math.sin(da)
            out.append([((mx + tx - cx) * f + cx + (p[0] - mx) * ca - (p[1] - my) * sa,
                         (my + ty - cy) * f + cy + (p[0] - mx) * sa + (p[1] - my) * ca) for p in q])
        return out, f

    svg.add('<g id="ghosts" fill="none">')
    for k in range(34):
        sq, f = perturb()
        c = rng.choice(STREAKS)
        dx = rng.choice([0, 0, 0, rng.uniform(-60, 60)])
        op = rng.uniform(0.25, 0.75)
        svg.add(f'<g stroke="{c}" stroke-width="{rng.choice([1, 1.5, 2])}" opacity="{op:.2f}" '
                f'transform="translate({fmt(dx)},0)">')
        for pts in packing_px(X, Y, A, sq):
            svg.add(f'<path d="{poly_d(pts)}"/>')
        # the (larger) box this arrangement would have needed
        d = A * (f - 1) / 2
        if rng.random() < 0.25:
            svg.add(f'<rect x="{fmt(X - d)}" y="{fmt(Y - d)}" width="{fmt(A * f)}" height="{fmt(A * f)}"/>')
        svg.add("</g>")
    svg.add("</g>")
    # tracking slips on the ghost layer
    y = Y - 200
    while y < Y + A + 200:
        h = rng.choice([4, 8, 14, 24])
        if rng.random() < 0.3:
            cid = svg.uid()
            svg.add(f'<clipPath id="{cid}"><rect x="0" y="{fmt(y)}" width="{W}" height="{h}"/></clipPath>')
            svg.add(f'<g clip-path="url(#{cid})"><rect x="0" y="{fmt(y)}" width="{W}" height="{h}" fill="{BG}"/>'
                    f'<use href="#ghosts" transform="translate({fmt(rng.uniform(-80, 80))},0)"/></g>')
        y += h + rng.uniform(10, 50)
    svg.packing(X, Y, A, bg=False)   # ghosts stay visible in the gaps
    svg.glitch_word("Optimal", "sans", 170, W / 2, 1270, "middle", slices=((-0.27, 0.17, 26),))
    svg.path(text("∀ P : Packing 11,  side P ≥ 3.87708359…", "mono", 24, W / 2, 1360, "middle", tracking=1), INK)
    svg.path(text("W. TRUMP 1979 · LEAN 2026", "mono", 18, W / 2, 1400, "middle", tracking=2), INK, 0.6)
    return svg


# ------------------------------------------------------------------ C: smear
def smear(rng):
    """Pixel-sort smear: each square drags its colour off to the left."""
    svg = SVG("Optimal — smear")
    X, Y, A = 470, 170, 620
    polys = packing_px(X, Y, A)
    cols = colours()
    for pts, c in zip(polys, cols):
        ys = [p[1] for p in pts]
        y = min(ys)
        while y < max(ys):
            h = rng.choice([2, 3, 4, 6, 9, 14])
            span = row_span(pts, y + h / 2)
            if span and rng.random() < 0.55:
                L = min(rng.expovariate(1 / 160), X + 20)
                if rng.random() < 0.08:
                    L = X + 20                          # occasional full-width run
                cc = c if rng.random() < 0.7 else rng.choice(STREAKS)
                svg.rect(span[0] - L, y, L + 4, h, cc, rng.uniform(0.3, 0.95))
                if rng.random() < 0.3:                  # channel fringe
                    svg.rect(span[0] - L * rng.uniform(0.3, 1), y + rng.choice([-2, h]),
                             L * 0.6, 1.5, rng.choice([CYAN, RED]), 0.9)
            y += h + rng.uniform(0, 5)
    svg.packing(X, Y, A, bg=False)
    svg.glitch_word("Optimal", "sans", 190, 120, 1160, slices=((-0.27, 0.17, 30),))
    footer(svg, 1260, x0=126, x1=1090)
    return svg


# ------------------------------------------------------------------ D: stack
def stack(rng):
    """The word degrading line by line, like a tape played out; packing as seal."""
    svg = SVG("Optimal — stack")
    lines, step, size, y0 = 7, 150, 128, 210
    mid = lines // 2
    for i in range(lines):
        d = abs(i - mid)
        y = y0 + i * step
        if d == 0:
            svg.glitch_word("Optimal", "sans", size, W / 2, y, "middle", slices=((-0.27, 0.17, 26),))
            continue
        slices = []
        for _ in range(d * 2):
            top = rng.uniform(-0.75, -0.05)
            slices.append((top, rng.uniform(0.04, 0.12 + 0.04 * d), rng.uniform(-30, 30) * d))
        fill = INK if d == 1 else (rng.choice([CYAN, RED, PINK]) if d == 2 else rng.choice(STREAKS))
        svg.glitch_word("Optimal", "sans", size, W / 2 + rng.uniform(-8, 8) * d, y, "middle",
                        split=4 + 4 * d, slices=slices, fill=fill, op=[1, 0.75, 0.5, 0.3][d])
    for _ in range(60):  # loose streaks around the fading lines
        y = rng.uniform(80, y0 + lines * step)
        if abs(y - (y0 + mid * step)) < 150:
            continue
        svg.rect(rng.uniform(-100, W), y, rng.uniform(20, 400), rng.choice([1, 2, 3, 6]),
                 rng.choice(STREAKS), rng.uniform(0.2, 0.8))
    A = 300
    svg.packing(W / 2 - A / 2, 1190, A, gap=1.5)
    svg.path(text(TAGLINE, "mono", 22, W / 2, 1545, "middle", tracking=1), INK)
    return svg


for name, fn in (("a-signal", signal), ("b-search", search), ("c-smear", smear), ("d-stack", stack)):
    fn(random.Random(SEED)).save(os.path.join(OUT, f"{name}.svg"))
    print("wrote", name)
