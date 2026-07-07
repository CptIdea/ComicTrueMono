#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for the box-drawing geometry in box-glyphs.json.

Ground truth is derived INDEPENDENTLY from the Unicode character names (so a wrong
weight in gen_box.py's W dict is caught, not rubber-stamped). The geometry is probed
by point-in-polygon on the JSON contours -- exactly the winding rule the font uses --
so a passing test means the real glyph ink is where it must be and absent where it
must not be. No third-party deps: run with any python3.

    python3 sources/tools/test_box.py      # exit 0 = all pass, 1 = failure

Invariants locked in:
  * arm topology + weight of every glyph matches its Unicode name
    (light=1 rail ~150u, heavy=1 rail ~300u, double=2 rails ~150u each);
  * absent arms carry ZERO ink (no phantom arm / no tail toward a missing exit);
  * straight double lines have an EMPTY centerline (no "brick" perpendiculars);
  * the light cross is solid at center, the double cross is hollow (woven) at center;
  * double rails are the same thickness as a single light stroke;
  * rounded corners ╭╮╰╯ sweep a visibly larger arc than the light corners.
"""
import json, os, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = json.load(open(ROOT + "/sources/tools/box-glyphs.json"))
CELL = 1116; XC = 558.0; YC = 546.0; XL, XR = 0.0, CELL

# ---- geometry probe: winding-rule point test on the JSON contours ----
def in_ring(x, y, ring):
    n = len(ring); inside = False; j = n - 1
    for i in range(n):
        xi, yi = ring[i]; xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside
def black(x, y, polys):
    return any(in_ring(x, y, r[0]) and not any(in_ring(x, y, h) for h in r[1:]) for r in polys)

def runs(polys, axis, fixed, lo, hi, step=3.0):
    """Ink run-lengths along `axis` ('x'/'y') at the other coord `fixed`."""
    ink = []
    t = lo
    while t <= hi:
        p = (t, fixed) if axis == 'x' else (fixed, t)
        ink.append(black(p[0], p[1], polys)); t += step
    out = []; run = 0
    for b in ink:
        if b: run += step
        elif run: out.append(run); run = 0
    if run: out.append(run)
    return out

# ---- expected (L,U,R,D) weights from the Unicode name (1 light, 2 heavy, 3 double) ----
DIRW = {'LEFT': ['L'], 'RIGHT': ['R'], 'UP': ['U'], 'DOWN': ['D'],
        'HORIZONTAL': ['L', 'R'], 'VERTICAL': ['U', 'D']}
WEIGHT = {'LIGHT': 1, 'HEAVY': 2, 'DOUBLE': 3, 'SINGLE': 1}
def expected(cp):
    body = unicodedata.name(chr(cp)).replace('BOX DRAWINGS ', '').replace('ARC ', '')
    chunks = [c.split() for c in body.split(' AND ')]
    parsed = []
    for toks in chunks:
        w = None; ds = []
        for t in toks:
            if t in WEIGHT: w = WEIGHT[t]
            elif t in DIRW: ds += DIRW[t]
        parsed.append((ds, w))
    default = next((w for _, w in parsed if w is not None), 1)
    res = {'L': 0, 'U': 0, 'R': 0, 'D': 0}
    for ds, w in parsed:
        for d in ds:
            res[d] = w if w is not None else default
    return (res['L'], res['U'], res['R'], res['D'])

def classify(rr):
    rr = sorted(round(r) for r in rr)
    if not rr: return 0
    if len(rr) == 1 and 125 <= rr[0] <= 175: return 1
    if len(rr) == 1 and 275 <= rr[0] <= 325: return 2
    if len(rr) == 2 and all(125 <= r <= 175 for r in rr): return 3
    return ('?', rr)

OFF, HALF = 400.0, 380.0
def measured_arm(polys, d):
    if   d == 'R': return classify(runs(polys, 'y', XC + OFF, YC - HALF, YC + HALF))
    elif d == 'L': return classify(runs(polys, 'y', XC - OFF, YC - HALF, YC + HALF))
    elif d == 'U': return classify(runs(polys, 'x', YC + OFF, XC - HALF, XC + HALF))
    elif d == 'D': return classify(runs(polys, 'x', YC - OFF, XC - HALF, XC + HALF))

fails = []
def check(cond, msg):
    if not cond: fails.append(msg)

# ---- 1. every glyph: arm topology + weight matches its Unicode name ----
box_cps = [cp for cp in (int(k) for k in DATA) if 0x2500 <= cp <= 0x2570]
for cp in sorted(box_cps):
    polys = DATA[str(cp)]
    exp = expected(cp)
    for i, d in enumerate('LURD'):
        m = measured_arm(polys, d)
        check(m == exp[i],
              "U+%04X %s (%s): arm %s expected weight %d, geometry says %r"
              % (cp, chr(cp), unicodedata.name(chr(cp)), d, exp[i], m))

# ---- 2. straight doubles: centerline empty (no bricks) ----
for cp, axis in [(0x2550, 'x'), (0x2551, 'y')]:
    polys = DATA[str(cp)]
    if axis == 'x':
        bricks = [t for t in range(int(XL), int(XR), 20) if black(t, YC, polys)]
    else:
        bricks = [t for t in range(int(YC-450), int(YC+450), 20) if black(XC, t, polys)]
    check(not bricks, "U+%04X double straight has ink on its centerline (bricks) at %r" % (cp, bricks[:6]))

# ---- 3. crosses: light solid at center, double hollow (woven) at center ----
check(black(XC, YC, DATA['9532']), "U+253C light cross must be solid at center")
check(not black(XC, YC, DATA['9580']), "U+256C double cross must be hollow (woven) at center")

# ---- 4. double rail thickness == single light stroke (150u) ----
single_v = sorted(round(r) for r in runs(DATA['9474'], 'x', YC, XC-250, XC+250))   # 2502 |
double_v = sorted(round(r) for r in runs(DATA['9553'], 'x', YC, XC-400, XC+400))   # 2551 ||
check(single_v == [150], "U+2502 single stroke width expected 150, got %r" % single_v)
check(double_v == [150, 150], "U+2551 double rails expected [150,150], got %r" % double_v)

# ---- 5. rounded corners sweep a larger arc than light corners ----
# 250C ┌ and 256D ╭ both join R+D. The big arc bulges into the inside of the bend, so a
# point just inside the corner (+130,-130 from centre) is INKED for the rounded glyph but
# EMPTY for the tight light corner. If someone reverts ╭ to a light-corner build, this trips.
px, py = XC + 130, YC - 130
check(not black(px, py, DATA[str(0x250C)]), "U+250C light corner should be empty at the inner diagonal")
check(black(px, py, DATA[str(0x256D)]), "U+256D rounded corner should bulge (ink) at the inner diagonal")

# ---- report ----
print("box glyphs checked:", len(box_cps), "| arm-topology assertions from Unicode names")
if fails:
    print("\nFAIL (%d):" % len(fails))
    for m in fails: print("  -", m)
    sys.exit(1)
print("\nALL BOX GEOMETRY TESTS PASSED")
