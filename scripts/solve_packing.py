"""Reconstruct Walter Trump's 1979 packing of 11 unit squares in a square of
side s(11) = 3.87708359...

Starts from coordinates measured off the published figure and relaxes them
with a separating-axis penetration penalty so that no two squares overlap and
all squares lie inside the container. Writes packing.json.
"""
import json
import numpy as np
from scipy.optimize import minimize

S = 3.877083590022  # s(11)
SCALE, OX, OY = 166.4, 152, 565  # pixel -> unit mapping of the reference figure


def px(x, y):
    return ((x - OX) / SCALE, S - (y - OY) / SCALE)


# tilted squares measured as 4 pixel vertices -> centre + angle
tilted_px = [
    [(531, 567), (658, 672), (549, 797), (426, 692)],
    [(383, 657), (507, 770), (401, 887), (277, 780)],
    [(507, 768), (631, 873), (526, 1000), (401, 887)],
    [(260, 771), (385, 880), (278, 1003), (153, 900)],
    [(385, 882), (510, 985), (404, 1114), (278, 1003)],
]
x0 = []
for quad in tilted_px:
    pts = np.array([px(*p) for p in quad])
    c = pts.mean(0)
    d = pts[1] - pts[0]
    x0 += [c[0], c[1], np.arctan2(d[1], d[0])]
# right column squares: only vertical position is free
x0 += [1.5, 2.5]
x0 = np.array(x0)


def square(cx, cy, a):
    u = np.array([np.cos(a), np.sin(a)]) / 2
    v = np.array([-np.sin(a), np.cos(a)]) / 2
    c = np.array([cx, cy])
    return np.array([c - u - v, c + u - v, c + u + v, c - u + v])


def axis_sq(x, y):
    return square(x + 0.5, y + 0.5, 0.0)


def squares(p):
    sq = [square(*p[3 * i:3 * i + 3]) for i in range(5)]
    sq += [
        axis_sq(0, S - 1),              # top-left
        axis_sq(0, 0),                  # bottom-left
        axis_sq(S - 2, 0),              # bottom-middle
        axis_sq(S - 1, 0),              # bottom-right
        axis_sq(S - 1, p[15] - 0.5),    # right, lower
        axis_sq(S - 1, p[16] - 0.5),    # right, upper
    ]
    return sq


def depth(A, B):
    best = np.inf
    for P in (A, B):
        for i in range(4):
            e = P[(i + 1) % 4] - P[i]
            n = np.array([-e[1], e[0]]) / np.hypot(*e)
            pa, pb = A @ n, B @ n
            o = min(pa.max(), pb.max()) - max(pa.min(), pb.min())
            best = min(best, o)
    return best


def penalty(p, margin=0.0):
    sq = squares(p)
    tot = 0.0
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            d = depth(sq[i], sq[j]) + margin
            if d > 0:
                tot += d * d
        V = sq[i]
        tot += np.sum(np.clip(-V + margin, 0, None) ** 2)
        tot += np.sum(np.clip(V - S + margin, 0, None) ** 2)
    return tot


# push squares apart with a small safety margin, then relax it to zero
p = x0
for m in (1e-3, 1e-5, 1e-7, 0.0):
    p = minimize(penalty, p, args=(m,), method="L-BFGS-B",
                 options={"ftol": 1e-30, "gtol": 1e-14, "maxiter": 5000}).x
sq = squares(p)
maxd = max(depth(sq[i], sq[j]) for i in range(11) for j in range(i + 1, 11))
print("penalty", penalty(p), "max penetration", maxd)
print("angles (deg)", [round(np.degrees(p[3 * i + 2]) % 90, 4) for i in range(5)])
json.dump({"side": S, "squares": [V.tolist() for V in sq], "tilted": 5}, open("design/packing.json", "w"), indent=1)
