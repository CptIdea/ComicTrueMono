#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the box-geometry invariants against a BUILT TTF (not the JSON), so integration
into the font is verified end to end. Contours are extracted from the font by
extract_ttf_box.py; here we test them with the NONZERO WINDING rule -- exactly what a
TrueType rasteriser uses -- so a pass means the real shipped glyphs are correct.

    fontforge -lang=py -script sources/tools/extract_ttf_box.py fonts/ttf/ComicTrueMono-Regular.ttf /tmp/ttf_box.json
    python3 sources/tools/test_box_ttf.py /tmp/ttf_box.json
"""
import json, sys, unicodedata

DATA = json.load(open(sys.argv[1]))
CELL = 1116; XC = 558.0; YC = 546.0; XL, XR = 0.0, CELL

def winding(x, y, contours):        # nonzero winding number at (x,y)
    w = 0
    for ring in contours:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]; x2, y2 = ring[(i+1) % n]
            if y1 <= y:
                if y2 > y and ((x2-x1)*(y-y1) - (x-x1)*(y2-y1)) > 0: w += 1
            else:
                if y2 <= y and ((x2-x1)*(y-y1) - (x-x1)*(y2-y1)) < 0: w -= 1
    return w
def black(x, y, c): return winding(x, y, c) != 0

def runs(c, axis, fixed, lo, hi, step=3.0):
    ink = []; t = lo
    while t <= hi:
        ink.append(black(t, fixed, c) if axis == 'x' else black(fixed, t, c)); t += step
    out = []; r = 0
    for b in ink:
        if b: r += step
        elif r: out.append(r); r = 0
    if r: out.append(r)
    return out

DIRW = {'LEFT': ['L'], 'RIGHT': ['R'], 'UP': ['U'], 'DOWN': ['D'],
        'HORIZONTAL': ['L', 'R'], 'VERTICAL': ['U', 'D']}
WEIGHT = {'LIGHT': 1, 'HEAVY': 2, 'DOUBLE': 3, 'SINGLE': 1}
def expected(cp):
    body = unicodedata.name(chr(cp)).replace('BOX DRAWINGS ', '').replace('ARC ', '')
    parsed = []
    for toks in [c.split() for c in body.split(' AND ')]:
        w = None; ds = []
        for t in toks:
            if t in WEIGHT: w = WEIGHT[t]
            elif t in DIRW: ds += DIRW[t]
        parsed.append((ds, w))
    default = next((w for _, w in parsed if w is not None), 1)
    res = {'L': 0, 'U': 0, 'R': 0, 'D': 0}
    for ds, w in parsed:
        for d in ds: res[d] = w if w is not None else default
    return (res['L'], res['U'], res['R'], res['D'])

def classify(rr):
    rr = sorted(round(r) for r in rr)
    if not rr: return 0
    if len(rr) == 1 and 125 <= rr[0] <= 175: return 1
    if len(rr) == 1 and 275 <= rr[0] <= 325: return 2
    if len(rr) == 2 and all(125 <= r <= 175 for r in rr): return 3
    return ('?', rr)

OFF, HALF = 400.0, 380.0
def arm(c, d):
    if   d == 'R': return classify(runs(c, 'y', XC+OFF, YC-HALF, YC+HALF))
    elif d == 'L': return classify(runs(c, 'y', XC-OFF, YC-HALF, YC+HALF))
    elif d == 'U': return classify(runs(c, 'x', YC+OFF, XC-HALF, XC+HALF))
    elif d == 'D': return classify(runs(c, 'x', YC-OFF, XC-HALF, XC+HALF))

fails = []
def check(cond, msg):
    if not cond: fails.append(msg)

cps = [cp for cp in (int(k) for k in DATA) if 0x2500 <= cp <= 0x2570]
for cp in sorted(cps):
    c = DATA[str(cp)]; exp = expected(cp)
    for i, d in enumerate('LURD'):
        m = arm(c, d)
        check(m == exp[i], "U+%04X %s: arm %s expected %d, TTF says %r" % (cp, chr(cp), d, exp[i], m))

for cp, axis in [(0x2550, 'x'), (0x2551, 'y')]:
    c = DATA.get(str(cp))
    if not c: check(False, "U+%04X missing from TTF" % cp); continue
    if axis == 'x': bricks = [t for t in range(int(XL), int(XR), 20) if black(t, YC, c)]
    else:           bricks = [t for t in range(int(YC-450), int(YC+450), 20) if black(XC, t, c)]
    check(not bricks, "U+%04X double straight has centerline ink (bricks)" % cp)

check(black(XC, YC, DATA['9532']), "U+253C light cross must be solid at center")
check(not black(XC, YC, DATA['9580']), "U+256C double cross must be hollow at center")
sv = sorted(round(r) for r in runs(DATA['9474'], 'x', YC, XC-250, XC+250))
dv = sorted(round(r) for r in runs(DATA['9553'], 'x', YC, XC-400, XC+400))
check(sv == [150], "U+2502 single width expected 150, got %r" % sv)
check(dv == [150, 150], "U+2551 double rails expected [150,150], got %r" % dv)
check(not black(XC+130, YC-130, DATA['9484']), "U+250C light corner should be empty at inner diagonal")
check(black(XC+130, YC-130, DATA['9581']), "U+256D rounded corner should bulge at inner diagonal")

print("TTF box glyphs checked:", len(cps))
if fails:
    print("\nFAIL (%d):" % len(fails))
    for m in fails: print("  -", m)
    sys.exit(1)
print("\nALL TTF BOX GEOMETRY TESTS PASSED")
