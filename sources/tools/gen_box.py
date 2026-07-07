#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compute rounded box-drawing + block-element glyph outlines with shapely and write
them to sources/tools/box-glyphs.json (consumed by build.py). Runs under the venv
(shapely is not available in FontForge's bundled Python).

Method:
  - single/mixed lines  = union of per-arm skeleton buffers (round joins), then a
    morphological close to round the concave armpits -> every junction is soft.
  - double lines        = the boundary of the "corridor" (skeleton buffered by DBG),
    stroked by DBW -> the two rails weave around junctions (no straight crossing).
  - connecting ends stay flat and reach past the cell edge so lines tile seamlessly.
Run: python3 sources/tools/gen_box.py
"""
from shapely.geometry import LineString, box as sbox
from shapely.ops import unary_union
import json, os, math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = ROOT + "/sources/tools/box-glyphs.json"

CELL = 1116; XC = 558.0; YC = 546.0; XL, XR = 0.0, CELL
M = 260; VEXT = 1150                             # horiz overshoot; vertical half-arm (~one line
YT = YC + VEXT - M; YB = YC - VEXT + M            # box, so YT+M / YB-M reach exactly YC±VEXT and
#   verticals tile across rows WITHOUT spilling onto adjacent text lines (was ±1600 -> too tall)
T1, T2 = 150, 300                                # light / heavy stroke
DBG, DBW = 150, 150                              # double: rail-center offset, rail thickness (= single light)
RC = 78                                          # corner fillet radius
RRC = 300                                        # rounded-corner ╭╮╰╯ centerline arc radius

EXT = 170                       # how far arms reach past center (fills junctions, no notch)

def seg(d, into=0.0):
    return {'R': LineString([(XC-into, YC), (XR+M, YC)]),
            'L': LineString([(XL-M, YC), (XC+into, YC)]),
            'U': LineString([(XC, YC-into), (XC, YT+M)]),
            'D': LineString([(XC, YB-M), (XC, YC+into)])}[d]

def rnd(geom):
    return geom.buffer(RC, join_style=1).buffer(-RC, join_style=1)   # close -> round concave corners

def _corner_skeleton(dirs):     # connected L-path -> round join smooths the outer bend
    h = 'R' if 'R' in dirs else 'L'; v = 'U' if 'U' in dirs else 'D'
    hx = XR+M if h == 'R' else XL-M; vy = YT+M if v == 'U' else YB-M
    return LineString([(hx, YC), (XC, YC), (XC, vy)])

def _is_corner(dirs):
    return len(dirs) == 2 and any(d in 'LR' for d in dirs) and any(d in 'UD' for d in dirs)

def _corner_rect(h, v, thh, thv):   # mixed-weight corner: two rects meeting flush at the
    hx0, hx1 = (XC-thv, XR+M) if h == 'R' else (XL-M, XC+thv)   # junction box, no round-cap
    vy0, vy1 = (YC-thh, YT+M) if v == 'U' else (YB-M, YC+thh)   # overshoot -> clean entry
    return unary_union([sbox(hx0, YC-thh, hx1, YC+thh), sbox(XC-thv, vy0, XC+thv, vy1)])

def single(weights):            # weights: {dir: thickness}
    # No center overshoot: a tee/cross has a through-line that fills the junction, and a
    # corner is a connected path. Overshoot would poke a tail toward the missing 4th exit.
    dirs = list(weights)
    if _is_corner(dirs):
        h = 'R' if 'R' in dirs else 'L'; v = 'U' if 'U' in dirs else 'D'
        if len(set(weights.values())) == 1:      # equal weight: connected skeleton (soft bend)
            g = _corner_skeleton(dirs).buffer(weights[h]/2.0, join_style=1, cap_style=2)
        else:                                    # mixed weight: flush rectangles, then fillet
            g = _corner_rect(h, v, weights[h]/2.0, weights[v]/2.0)
    else:
        g = unary_union([seg(d).buffer(t/2.0, join_style=1, cap_style=2) for d, t in weights.items()])
    return rnd(g)

def double(sides):
    # thick single (black) minus thin single (white) of the same shape -> two rails.
    OUT, INN = 2*DBG + DBW, 2*DBG - DBW
    return single({d: OUT for d in sides}).difference(single({d: INN for d in sides}))

def mix_corner(wd):
    # dbl/single CORNERS ╒╓╕╖╘╙╛╜: single arm + the double arm's two rails (corridor outline).
    # Kept as the original approach -- the boolean mix() made these corners look blocky.
    singles = {d: TH[w] for d, w in wd.items() if w in (1, 2)}
    dsides  = [d for d, w in wd.items() if w == 3]
    rails = unary_union([seg(d) for d in dsides]).buffer(DBG, join_style=1, cap_style=2) \
                .boundary.buffer(DBW/2.0, join_style=1, cap_style=2)
    return rails if not singles else single(singles).union(rails)

def mix(wd):
    # double/single junction as clean boolean fills (no overlaid strokes -> no overlap):
    #   carve the double rails (rounded OUT corridor minus rounded INN gap -- rounded
    #   separately so the close doesn't seal the 150u gap), then paint the single arms back
    #   on top as solid bands so the single line stays continuous where it meets the double.
    OUT, INN = 2*DBG + DBW, 2*DBG - DBW
    singles = {d: TH[w] for d, w in wd.items() if w in (1, 2)}
    dsides  = [d for d, w in wd.items() if w == 3]
    solid = unary_union([seg(d).buffer(t/2.0, join_style=1, cap_style=2) for d, t in singles.items()]
                        + [seg(d).buffer(OUT/2.0, join_style=1, cap_style=2) for d in dsides])
    gap = unary_union([seg(d).buffer(INN/2.0, join_style=1, cap_style=2) for d in dsides])
    carved = rnd(solid).difference(rnd(gap))
    if singles:
        NEAR = DBG - DBW/2.0        # inner edge of the near rail: stubs stop here, no gap tab
        opp = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}
        stub_ln = {'R': LineString([(XC+NEAR, YC), (XR+M, YC)]), 'L': LineString([(XL-M, YC), (XC-NEAR, YC)]),
                   'U': LineString([(XC, YC+NEAR), (XC, YT+M)]), 'D': LineString([(XC, YB-M), (XC, YC-NEAR)])}
        sgeoms = []
        for d, t in singles.items():
            perp = ('U', 'D') if d in 'LR' else ('L', 'R')      # a single stub that dead-ends into a
            straight = perp[0] in dsides and perp[1] in dsides  # straight double bar stops at its near
            ln = stub_ln[d] if (straight and opp[d] not in singles) else seg(d)  # rail (else run through)
            sgeoms.append(ln.buffer(t/2.0, join_style=1, cap_style=2))
        carved = carved.union(unary_union(sgeoms))
    return carved

# ---- (L,U,R,D) weights: 1=light 2=heavy 3=double ----
W = {
 0x2500:(1,0,1,0),0x2501:(2,0,2,0),0x2502:(0,1,0,1),0x2503:(0,2,0,2),
 # corners (light/heavy, all four arm-weight combos)
 0x250C:(0,0,1,1),0x250D:(0,0,2,1),0x250E:(0,0,1,2),0x250F:(0,0,2,2),
 0x2510:(1,0,0,1),0x2511:(2,0,0,1),0x2512:(1,0,0,2),0x2513:(2,0,0,2),
 0x2514:(0,1,1,0),0x2515:(0,1,2,0),0x2516:(0,2,1,0),0x2517:(0,2,2,0),
 0x2518:(1,1,0,0),0x2519:(2,1,0,0),0x251A:(1,2,0,0),0x251B:(2,2,0,0),
 # tees
 0x251C:(0,1,1,1),0x251D:(0,1,2,1),0x251E:(0,2,1,1),0x251F:(0,1,1,2),
 0x2520:(0,2,1,2),0x2521:(0,2,2,1),0x2522:(0,1,2,2),0x2523:(0,2,2,2),
 0x2524:(1,1,0,1),0x2525:(2,1,0,1),0x2526:(1,2,0,1),0x2527:(1,1,0,2),
 0x2528:(1,2,0,2),0x2529:(2,2,0,1),0x252A:(2,1,0,2),0x252B:(2,2,0,2),
 0x252C:(1,0,1,1),0x252D:(2,0,1,1),0x252E:(1,0,2,1),0x252F:(2,0,2,1),
 0x2530:(1,0,1,2),0x2531:(2,0,1,2),0x2532:(1,0,2,2),0x2533:(2,0,2,2),
 0x2534:(1,1,1,0),0x2535:(2,1,1,0),0x2536:(1,1,2,0),0x2537:(2,1,2,0),
 0x2538:(1,2,1,0),0x2539:(2,2,1,0),0x253A:(1,2,2,0),0x253B:(2,2,2,0),
 # crosses
 0x253C:(1,1,1,1),0x253D:(2,1,1,1),0x253E:(1,1,2,1),0x253F:(2,1,2,1),
 0x2540:(1,2,1,1),0x2541:(1,1,1,2),0x2542:(1,2,1,2),0x2543:(2,2,1,1),
 0x2544:(1,2,2,1),0x2545:(2,1,1,2),0x2546:(1,1,2,2),0x2547:(2,2,2,1),
 0x2548:(2,1,2,2),0x2549:(2,2,1,2),0x254A:(1,2,2,2),0x254B:(2,2,2,2),
 # doubles + double/single mixes
 0x2550:(3,0,3,0),0x2551:(0,3,0,3),0x2554:(0,0,3,3),0x2557:(3,0,0,3),
 0x255A:(0,3,3,0),0x255D:(3,3,0,0),0x2560:(0,3,3,3),0x2563:(3,3,0,3),
 0x2566:(3,0,3,3),0x2569:(3,3,3,0),0x256C:(3,3,3,3),
 0x2552:(0,0,3,1),0x2553:(0,0,1,3),0x2555:(3,0,0,1),0x2556:(1,0,0,3),
 0x2558:(0,1,3,0),0x2559:(0,3,1,0),0x255B:(3,1,0,0),0x255C:(1,3,0,0),
 0x255E:(0,1,3,1),0x255F:(0,3,1,3),0x2561:(3,1,0,1),0x2562:(1,3,0,3),
 0x2564:(3,0,3,1),0x2565:(1,0,1,3),0x2567:(3,1,3,0),0x2568:(1,3,1,0),
 0x256A:(3,1,3,1),0x256B:(1,3,1,3),
 # rounded corners (same as light corners; already soft)
 0x256D:(0,0,1,1),0x256E:(1,0,0,1),0x256F:(1,1,0,0),0x2570:(0,1,1,0),
}
TH = {1: T1, 2: T2}
ROUNDED = {0x256D, 0x256E, 0x256F, 0x2570}

def _rounded_skeleton(dirs, Rc, n=20):
    # centerline follows a quarter-circle of radius Rc between the two straight arms, so the
    # whole stroke sweeps a big arc (visibly rounder than a light corner's tiny buffer fillet).
    h = 'R' if 'R' in dirs else 'L'; v = 'U' if 'U' in dirs else 'D'
    hx = XR+M if h == 'R' else XL-M;  vy = YT+M if v == 'U' else YB-M
    cx = XC+Rc if h == 'R' else XC-Rc         # arc centre: offset toward each present arm
    cy = YC+Rc if v == 'U' else YC-Rc
    a0 = math.atan2(YC-cy, 0.0)               # tangent point on the horizontal arm (x=cx)
    a1 = math.atan2(0.0, XC-cx)               # tangent point on the vertical arm   (y=cy)
    d = a1 - a0
    d = (d + math.pi) % (2*math.pi) - math.pi  # shortest sweep (a quarter turn)
    pts = [(hx, YC)]
    pts += [(cx + Rc*math.cos(a0 + d*i/n), cy + Rc*math.sin(a0 + d*i/n)) for i in range(n+1)]
    pts += [(XC, vy)]
    return LineString(pts)

def rounded(cp, dirs):
    return rnd(_rounded_skeleton(dirs, RRC).buffer(T1/2.0, join_style=1, cap_style=2))

def _ring(coords):
    r = []                                       # round to int, drop consecutive duplicates
    for x, y in coords:                          # (the morphological close emits dense ~2u
        pt = [round(x), round(y)]                #  vertices that collapse to zero-length
        if not r or r[-1] != pt:                 #  segments after rounding -> bad splines)
            r.append(pt)
    if len(r) > 1 and r[0] == r[-1]:
        r.pop()
    return r

def contours(geom):
    polys = geom.geoms if geom.geom_type.startswith("Multi") else [geom]
    out = []
    for p in polys:
        rings = []
        for coords in [p.exterior.coords] + [h.coords for h in p.interiors]:
            r = _ring(coords)
            if len(r) >= 3:
                rings.append(r)
        if rings:
            out.append(rings)
    return out

data = {}
for cp, (L, U, R, D) in W.items():
    wd = {d: w for d, w in (('L',L),('U',U),('R',R),('D',D)) if w}
    if cp in ROUNDED:
        geom = rounded(cp, list(wd))
    elif all(w == 3 for w in wd.values()):                 # pure double
        geom = double(list(wd))
    elif any(w == 3 for w in wd.values()):                 # double/single mix
        geom = mix_corner(wd) if len(wd) == 2 else mix(wd)  # 2-arm = corner; 3/4-arm = tee/cross
    else:                                                  # pure single/heavy
        geom = single({d: TH[w] for d, w in wd.items()})
    data[str(cp)] = contours(geom)

json.dump(data, open(OUT, "w"))
print("box-glyphs.json:", len(data), "glyphs")
