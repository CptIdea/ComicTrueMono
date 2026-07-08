#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Comic True Mono — full automatic weight range.
Run: fontforge -lang=py -script sources/build.py

Pipeline (everything auto-derived from one master):
  1. Master Regular = plain Comic Mono + harvested community contributions
     (lambda, AE ae OE oe Thorn thorn, caron letters fixed by lilmayu, long-s, wynn,
      r-rotunda, math quantifiers, full European Latin, ...).
  2. Each weight = changeWeight(delta) from the master. Bold (+32) is calibrated to
     the real Comic Mono Bold stem thickness (measured on '|': 194 -> 226). ExtraBold = +80.
  3. Italic of every weight = 12.7 deg slant (same angle as kaBeech; the auto-italic is good).
  4. Advance width normalized to 1116 everywhere -> strict monospacing.
"""
import fontforge, psMat, math, os, json

# Paths are derived from the script location: sources/build.py -> repo root.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = ROOT + "/sources/vendor"          # vendored MIT source fonts
OUT    = ROOT + "/fonts/ttf"               # release binaries
CELL = 1116
EM = 2048
ITALIC_ANGLE = -12.7
FAMILY = "Comic True Mono"
os.makedirs(OUT, exist_ok=True)
SKEW = psMat.skew(math.radians(-ITALIC_ANGLE))   # forward slant of +12.7 deg

def outfn(style, italic):
    if italic:
        return "ComicTrueMono-Italic.ttf" if style == "Regular" else f"ComicTrueMono-{style}Italic.ttf"
    return f"ComicTrueMono-{style}.ttf"

# Weights: (name, os2-class, stem delta). delta = 0 is Regular (stem 194).
WEIGHTS = [
    ("Thin",       100, -30),
    ("ExtraLight", 200, -20),
    ("Light",      300, -10),
    ("Regular",    400,   0),
    ("Medium",     500,  12),
    ("SemiBold",   600,  22),
    ("Bold",       700,  32),   # = real Comic Mono Bold
    ("ExtraBold",  800,  80),
    ("Black",      900, 110),
]

# Glyphs harvested into the master (all from MIT sources).
# Imported by range from clsn-morechars (superset of Comic Shanns v2 + clsn additions), all MIT.
IMPORT_RANGES = [
    (0x00A0, 0x00FF),   # Latin-1 Supplement: accented Latin + degree, plus/minus, times, divide, ...
    (0x0100, 0x017F),   # Latin Extended-A: all of Central/Eastern Europe, OE oe, ligatures
    (0x0180, 0x024F),   # Latin Extended-B: wynn, etc.
    (0x2000, 0x206F),   # General Punctuation: dashes, quotes, dagger, ellipsis
    (0x20A0, 0x20BF),   # Currency: euro
    (0x2190, 0x21FF),   # Arrows: left up right down
    (0x2200, 0x22FF),   # Math Operators: for-all, exists, ...
    (0x02B0, 0x02FF),   # Spacing modifier letters: circumflex, breve, ring, ogonek, tilde, dbl-acute
    (0x1E00, 0x1EFF),   # Latin Extended Additional: Welsh W/Y with grave/acute/diaeresis
    (0xA75B, 0xA75B),   # r-rotunda
]
# These are overridden from lilmayu (corrected caron / hacek), incl. the standalone caron U+02C7.
CEU_ACCENT = [0x010C,0x010D,0x010E,0x011A,0x011B,0x0147,0x0148,
              0x0158,0x0159,0x0160,0x0161,0x0164,0x017D,0x017E,0x02C7]
LAMBDA = 0x03BB

def recenter(g):
    xmin, ymin, xmax, ymax = g.boundingBox()
    if xmax > xmin:
        g.transform(psMat.translate((CELL - (xmin + xmax)) / 2.0, 0))
    g.width = CELL

def refit_all(font):
    for g in font.glyphs():
        if g.unicode and (0x2800 <= g.unicode <= 0x28FF or 0x2500 <= g.unicode <= 0x257F):
            g.width = CELL          # grid glyphs (Braille, box): keep position, normalize advance
        else:
            recenter(g)

def open_src(path):
    f = fontforge.open(path)
    if f.em != EM:
        f.em = EM
    return f

def slash_through(font, base_cp, cp, name):
    """Slashed letter (o-slash / O-slash): base glyph + a diagonal drawn from the '|'
    glyph (so it inherits the font's rounded stroke terminals), rotated into a '/'."""
    g = font.createChar(cp, name)
    font.selection.select(("unicode", None), base_cp); font.copy()
    font.selection.select(("unicode", None), cp); font.paste()
    xmin, ymin, xmax, ymax = g.boundingBox()
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
    ext = 150                                       # how far the stroke overshoots the letter
    tmp = font.createChar(-1, "tmp_bar")            # temp glyph holding the stroke made from '|'
    font.selection.select(("unicode", None), 0x7C); font.copy()   # |
    font.selection.select("tmp_bar"); font.paste()
    bx0, by0, bx1, by1 = tmp.boundingBox()
    bcx, bcy = (bx0+bx1)/2, (by0+by1)/2
    bar_h = by1 - by0
    sy = ((ymax-ymin) + 2*ext) / bar_h              # stretch to span the letter's diagonal
    tmp.transform(psMat.translate(-bcx, -bcy))      # to origin
    tmp.transform(psMat.scale(1.0, sy))
    tmp.transform(psMat.rotate(math.radians(-22)))  # '/' slant
    tmp.transform(psMat.translate(cx, cy))          # to letter center
    font.selection.select("tmp_bar"); font.copy()
    font.selection.select(name); font.pasteInto()
    font.removeGlyph("tmp_bar")
    g.correctDirection(); g.removeOverlap(); g.correctDirection()
    recenter(g)

def raised_dot(font, cp=0x00B7, name="periodcentered"):
    """middle dot = the period raised to mid x-height."""
    g = font.createChar(cp, name)
    font.selection.select(("unicode", None), 0x2E); font.copy()   # period
    font.selection.select(("unicode", None), cp); font.paste()
    xmin, ymin, xmax, ymax = g.boundingBox()
    g.transform(psMat.translate(0, 380 - (ymin+ymax)/2))
    recenter(g)

# Source letters are drawn smaller than Comic Mono; scale imports up to match its size.
# (measured on H/O/o/x/n cap- and x-heights, ratios are uniform per source)
SCALE_SHANNS_V2 = 1.069   # clsn-morechars / lilmayu (Comic Shanns v2) are ~6.9% smaller
SCALE_SERIOUS   = 1.177   # Serious Shanns is ~17.7% smaller

def paste_glyph(dst, src, cp, scale=1.0):
    src.selection.select(("unicode", None), cp)
    src.copy()
    dst.createChar(cp)
    dst.selection.select(("unicode", None), cp)
    dst.paste()
    g = dst[cp]
    if scale != 1.0:
        g.transform(psMat.scale(scale, scale))   # scale about baseline; recenter fixes x
    recenter(g)

# Comic Relief (OFL) is proportional; fit each imported glyph into the mono cell the same
# way Comic Mono already condenses its own wide Latin (M->0.70, W->0.61 of the proportional
# width). SCALE_CR matches cap/x-height; wide glyphs then get a horizontal-only squeeze so
# their bbox fits MAXW (our own widest Latin sits ~1088, leaving small side bearings in 1116).
SCALE_CR = 0.9657   # median H/X/O/o/x/n/b/d/p height ratio ours/Comic-Relief
MAXW     = 1080     # max glyph bbox width kept inside CELL=1116
STEM_TARGET_FRAC = 0.80   # condensed glyphs: restore vertical stem to this fraction of the median
                          # native weight (kept below full weight because their tight counters
                          # already read darker). The global lift below then tops everyone up.
GLOBAL_LIFT = 14          # Comic Relief runs ~8% lighter than Comic Mono (Greek Ι stem 188 vs
                          # Latin I 205); add this weight to every imported glyph, in BOTH axes,
                          # so verticals AND horizontals match the Latin texture.
# Native stroke weight of each Comic Relief Greek/Cyrillic glyph (precomputed by
# sources/tools/measure_cr_stems.py -> cr-stems.json). Lets us know how much stem a wide
# glyph loses to horizontal condensing, so we can add it back.
_CRSTEMS   = json.load(open(ROOT + "/sources/tools/cr-stems.json"))
CR_STEM     = {int(k): v for k, v in _CRSTEMS["stems"].items()}
CR_STEM_MED = _CRSTEMS["median"]

def embolden(g, dx, dy):
    """All-directional weight: union the outline with an x-shifted and a y-shifted copy of
    itself. Vertical strokes thicken by dx, horizontal strokes by dy. Grows the bbox by
    (dx, dy) — callers re-fit width and clamp height afterwards."""
    if dx < 1 and dy < 1:
        return
    layer = g.foreground.dup()
    if dx >= 1:
        sx = g.foreground.dup(); sx.transform(psMat.translate(dx, 0.0)); layer += sx
    if dy >= 1:
        sy = g.foreground.dup(); sy.transform(psMat.translate(0.0, dy)); layer += sy
    g.foreground = layer
    g.removeOverlap()
    g.correctDirection()

# A few Comic Relief caps are drawn taller than this family's tiny cap overshoot (~1%), so
# they poke above the cap line. Bring just these round/pointed caps' top down to the cap line
# (uniform vertical scale about the baseline). NOT applied to lowercase (legit ascenders),
# accent marks (Й Ё Ў Ϊ Ϋ — meant to rise), or hook letters (Ґ — squishing the body is wrong).
VCLAMP  = {0x0394, 0x03A9, 0x038F, 0x042E}   # Δ Ω Ώ Ю
CAP_TOP = None                               # set from the master's 'H' before the import loop

def clamp_top(g, cp):
    if CAP_TOP is None or cp not in VCLAMP:
        return
    limit = CAP_TOP * 1.02
    y1 = g.boundingBox()[3]
    if y1 > limit:
        g.transform(psMat.scale(1.0, limit / y1))   # about baseline: top -> cap line

def paste_fit(dst, src, cp):
    src.selection.select(("unicode", None), cp)
    src.copy()
    dst.createChar(cp)
    dst.selection.select(("unicode", None), cp)
    dst.paste()
    g = dst[cp]
    g.transform(psMat.scale(SCALE_CR, SCALE_CR))     # match cap/x-height to the family
    x0, y0, x1, y1 = g.boundingBox()
    w = x1 - x0
    if w > MAXW:                                      # too wide: condense horizontally to fit
        native = CR_STEM.get(cp, CR_STEM_MED) * SCALE_CR   # this glyph's own stem after uniform scale
        target = CR_STEM_MED * SCALE_CR * STEM_TARGET_FRAC # uniform stem target for condensed glyphs
        k = native / w
        delta = (target - k * MAXW) / (1.0 - k) if k < 1.0 else 0.0
        delta = max(0.0, min(delta, 90.0))                 # cap the compensation
        g.transform(psMat.scale((MAXW - delta) / w, 1.0))  # leave room for the embolden
        embolden(g, delta, 0)                              # restore ONLY the vertical stem the
                                                           # x-squeeze thinned (horizontals were
                                                           # untouched by it)
    embolden(g, GLOBAL_LIFT, 0)                       # lift vertical weight to Comic Mono's (Comic
                                                      # Relief runs lighter on stems but already has
                                                      # heavier horizontals, so only the stems lift)
    x0, y0, x1, y1 = g.boundingBox()                  # emboldening grew the bbox — refit the width
    w2 = x1 - x0
    if w2 > MAXW:
        g.transform(psMat.scale(MAXW / w2, 1.0))
    clamp_top(g, cp)                                  # pull over-tall caps down to the cap line
    recenter(g)

# Grid glyphs (Braille, box-drawing): keep the design cell in place — uniform scale,
# NO recenter. Map ShannsMono's cell (src_cell @ em1000) exactly to CELL so lines tile.
def paste_grid(dst, src, cp, src_cell=549):
    src.selection.select(("unicode", None), cp)
    src.copy()
    dst.createChar(cp)
    dst.selection.select(("unicode", None), cp)
    dst.paste()
    g = dst[cp]
    g.transform(psMat.scale(CELL / (src_cell * (EM / 1000.0)),
                            CELL / (src_cell * (EM / 1000.0))))
    g.width = CELL
    return g

def add_rect(g, x0, y0, x1, y1):
    p = g.glyphPen(replace=False)
    p.moveTo((x0, y0)); p.lineTo((x1, y0)); p.lineTo((x1, y1)); p.lineTo((x0, y1)); p.closePath()

def make_junction(font, cp, line_cps, rects):
    """Build a box-drawing junction: copy full line glyphs + add stub rectangles,
    positioned on the exact stroke bands of the imported lines so everything tiles."""
    g = font.createChar(cp)
    for lc in line_cps:
        font.selection.select(("unicode", None), lc); font.copy()
        font.selection.select(("unicode", None), cp); font.pasteInto()
    for r in rects:
        add_rect(g, *r)
    g.correctDirection(); g.removeOverlap(); g.correctDirection()
    g.width = CELL
    return g

def brand(font, style, wclass, italic):
    name = style + (" Italic" if italic else "")
    font.familyname = FAMILY
    font.fontname = (FAMILY + "-" + name).replace(" ", "")
    font.fullname = FAMILY + " " + name
    font.appendSFNTName("English (US)", "Family", FAMILY)
    font.appendSFNTName("English (US)", "SubFamily", name)
    font.appendSFNTName("English (US)", "Fullname", font.fullname)
    # WWS / typographic names so apps group all weights under one family.
    font.appendSFNTName("English (US)", "Preferred Family", FAMILY)
    font.appendSFNTName("English (US)", "Preferred Styles", name)
    # Licensing (name IDs 0 / 13 / 14): fonts are OFL 1.1 because of the Comic Relief outlines.
    font.appendSFNTName("English (US)", "Copyright",
                        "Copyright 2026 The Comic True Mono Authors. "
                        "Portions copyright 2013 The Comic Relief Project Authors.")
    font.appendSFNTName("English (US)", "License",
                        "This Font Software is licensed under the SIL Open Font License, "
                        "Version 1.1. See OFL.txt or https://openfontlicense.org")
    font.appendSFNTName("English (US)", "License URL", "https://openfontlicense.org")
    font.os2_weight = wclass
    font.italicangle = ITALIC_ANGLE if italic else 0
    bits = 0
    if wclass >= 700: bits |= 0x01
    if italic: bits |= 0x02
    font.macstyle = bits
    fs = 0
    if wclass >= 700: fs |= 0x20
    if italic: fs |= 0x01
    if wclass < 700 and not italic: fs |= 0x40
    try: font.os2_stylemap = fs
    except Exception: pass

# ============================================================
# 1. MASTER Regular = Comic Mono + extras
# ============================================================
print(">>> Master Regular (Comic Mono + community contributions)")
mc = open_src(VENDOR+"/clsn-morechars-shanns2.ttf")
lm = open_src(VENDOR+"/lilmayu-shanns2.ttf")
gv = open_src(VENDOR+"/gb-ComicMono.ttf")
sr = open_src(VENDOR+"/SeriousShanns-Regular.otf")   # source of L-stroke / l-stroke (kaBeech, MIT)
sm = open_src(VENDOR+"/ComicShannsMono-Regular.ttf") # Braille source (jesusmgg, MIT)
cr = open_src(VENDOR+"/ComicRelief-Regular.ttf")     # Greek + Cyrillic source (Loudifier, OFL 1.1)

for src in (mc, lm, sr, cr):    # flatten any composite references -> real contours
    src.selection.all()
    try: src.unlinkReferences()
    except Exception: pass

master = fontforge.open(VENDOR+"/ComicMono.ttf")
base_cps = {g.unicode for g in master.glyphs() if g.unicode and g.unicode > 0}  # already in Comic Mono
mc_cps = {g.unicode for g in mc.glyphs() if g.unicode and g.unicode > 0}
want = sorted({cp for a, b in IMPORT_RANGES for cp in range(a, b+1)} & mc_cps - base_cps)
for cp in want:
    paste_glyph(master, mc, cp, SCALE_SHANNS_V2)
for cp in CEU_ACCENT:           # override with lilmayu's corrected diacritics
    paste_glyph(master, lm, cp, SCALE_SHANNS_V2)
paste_glyph(master, gv, LAMBDA)                       # give-back = Comic Mono size
for cp in (0x0141, 0x0142):     # L-stroke / l-stroke from Serious Shanns (MIT)
    paste_glyph(master, sr, cp, SCALE_SERIOUS)
# Constructed (absent from every source — verified across all vendored files):
slash_through(master, 0x006F, 0x00F8, "oslash")   # o-slash
slash_through(master, 0x004F, 0x00D8, "Oslash")   # O-slash
raised_dot(master)                                 # middle dot
sm_cps = {g.unicode for g in sm.glyphs() if g.unicode and g.unicode > 0}
braille = [cp for cp in range(0x2800, 0x2900) if cp in sm_cps]   # Braille Patterns (256)
for cp in braille:
    paste_grid(master, sm, cp)

# Align the Braille dot-grid to the same line box the block/box glyphs fill.
# ShannsMono's braille is baseline-anchored at ~2/3 height, so next to the
# full-height blocks/box-drawing it looks small and raised. Map the 4 dot rows
# onto 1/8..7/8 of the block line box (BB..BT below) and center the field in the
# cell: braille art now tiles vertically on an even grid and matches block size.
# Uniform scale (same factor on x and y) keeps the dots round; a single shared
# transform on all 256 patterns preserves the grid.
LINE_BB, LINE_BT = -512.0, 1536.0          # == block line box (BB, BT) defined below
def _dot_center(cp):
    x0, y0, x1, y1 = master[cp].boundingBox()
    return (x0 + x1) / 2.0, (y0 + y1) / 2.0
_tx, _ty = _dot_center(0x2801)             # top row, left column
_bx, _by = _dot_center(0x2840)             # bottom row (dot 7), left column
_rx, _ry = _dot_center(0x2808)             # top row, right column
src_cx, src_cy = (_tx + _rx) / 2.0, (_ty + _by) / 2.0
s = ((LINE_BT - LINE_BB) * 6.0 / 8.0) / (_ty - _by)   # row span -> 1/8..7/8 of line box
tgt_cx, tgt_cy = CELL / 2.0, (LINE_BB + LINE_BT) / 2.0
BR_T = psMat.compose(psMat.translate(-src_cx, -src_cy),
        psMat.compose(psMat.scale(s, s), psMat.translate(tgt_cx, tgt_cy)))
for cp in braille:
    master[cp].transform(BR_T)
    master[cp].width = CELL

# ---- Greek + Cyrillic from Comic Relief (OFL 1.1) ----
# Modern monotonic Greek (U+0370-03FF) + Cyrillic (U+0400-04FF), fitted to the mono cell.
# Skip codepoints already in the master (keeps the give-back lambda U+03BB, Comic Mono size).
CAP_TOP = master["H"].boundingBox()[3]          # cap line, for clamp_top
master_cps = {g.unicode for g in master.glyphs() if g.unicode and g.unicode > 0}
cr_cps = {g.unicode for g in cr.glyphs() if g.unicode and g.unicode > 0}
greek_cyr = sorted(cp for cp in cr_cps
                   if (0x0370 <= cp <= 0x03FF or 0x0400 <= cp <= 0x04FF)
                   and cp not in master_cps)
for cp in greek_cyr:
    paste_fit(master, cr, cp)
n_greek = sum(1 for cp in greek_cyr if cp <= 0x03FF)
n_cyr = len(greek_cyr) - n_greek
print(f"   Comic Relief: +{n_greek} Greek, +{n_cyr} Cyrillic (fitted to mono)")

# ---- Box drawing + block elements ----
# Straight, connecting parts are clean rectangles (tile seamlessly, no rounded/slanted
# seams); rounded corners ╭╮╰╯ keep a Comic arc. Per-side weight model: each of the four
# sides carries a weight 0/1/2/3 = none/light/heavy/double.
T1, T2 = 150, 300              # light / heavy stroke
DBW, DBG = 92, 150            # double line: bar thickness, gap from center to each bar
YC, XC = 546.0, CELL/2.0
YB, YT = YC-1600, YC+1600     # vertical tiling extent (overshoot)
XL, XR = 0.0, CELL
CO = 0                        # arms reach exactly to center — no overshoot past a crossing line
BB, BT = -512.0, 1536.0       # block-element cell bottom/top (~ one line box)

# ---- Box-drawing lines U+2500-2570: precomputed with shapely in sources/tools/gen_box.py
# -> box-glyphs.json (verified by sources/tools/test_box.py). Here we only stroke the
# contours; correctDirection() sets winding so hollow doubles cut correctly. Blocks / shades
# / diagonals are still constructed directly below.
_BOXJSON = json.load(open(ROOT + "/sources/tools/box-glyphs.json"))
for _cp, _polys in _BOXJSON.items():
    _g = master.createChar(int(_cp))
    _pen = _g.glyphPen()                     # replace=True -> starts empty
    for _poly in _polys:
        for _ring in _poly:
            _pts = []                            # drop consecutive dup points (int rounding can
            for _pt in _ring:                    # collapse neighbours -> zero-length segments)
                if not _pts or _pts[-1] != _pt:
                    _pts.append(_pt)
            if len(_pts) > 1 and _pts[0] == _pts[-1]:
                _pts.pop()
            if len(_pts) < 3:
                continue
            _pen.moveTo(tuple(_pts[0]))
            for _pt in _pts[1:]:
                _pen.lineTo(tuple(_pt))
            _pen.closePath()
    _pen = None                              # flush the pen
    _g.correctDirection()                    # winding by nesting -> holes cut correctly
    _g.width = CELL

# shades ░ ▒ ▓ — dithered grids of small squares
def shade(cp, keep):
    g = master.createChar(cp); cols, rows = 8, 14
    cw = (XR-XL)/cols; ch = (BT-BB)/rows
    for j in range(rows):
        for i in range(cols):
            if keep(i, j):
                add_rect(g, XL+i*cw, BB+j*ch, XL+i*cw+cw*0.6, BB+j*ch+ch*0.6)
    g.removeOverlap(); g.correctDirection(); g.width = CELL
shade(0x2591, lambda i,j: i%2==0 and j%2==0)          # ░ ~25%
shade(0x2592, lambda i,j: (i+j)%2==0)                 # ▒ ~50%
shade(0x2593, lambda i,j: not (i%2 and j%2))          # ▓ ~75%

# diagonals ╱ ╲ ╳
def diagonal(cp, up, down):
    g = master.createChar(cp); w = T1*0.85
    def bar(x0,y0,x1,y1):
        import math as _mm; dx,dy=x1-x0,y1-y0; L=_mm.hypot(dx,dy); nx,ny=-dy/L*w/2,dx/L*w/2
        p=g.glyphPen(replace=True) if False else g.glyphPen(replace=False)
        p.moveTo((x0+nx,y0+ny)); p.lineTo((x1+nx,y1+ny)); p.lineTo((x1-nx,y1-ny)); p.lineTo((x0-nx,y0-ny)); p.closePath()
    if up:   bar(XL,YB,XR,YT)     # ╱ bottom-left..top-right
    if down: bar(XL,YT,XR,YB)     # ╲ top-left..bottom-right
    g.removeOverlap(); g.correctDirection(); g.width = CELL
diagonal(0x2571,True,False); diagonal(0x2572,False,True); diagonal(0x2573,True,True)

# block elements (fractions of the cell); tile edge-to-edge
def block(cp, x0f, y0f, x1f, y1f):
    g = master.createChar(cp)
    add_rect(g, XL+(XR-XL)*x0f, BB+(BT-BB)*y0f, XL+(XR-XL)*x1f, BB+(BT-BB)*y1f)
    g.correctDirection(); g.width = CELL
block(0x2588,0,0,1,1)                # █ full
block(0x2580,0,0.5,1,1)              # ▀ upper half
block(0x2590,0.5,0,1,1)              # ▐ right half
block(0x2594,0,7/8,1,1)              # ▔ upper 1/8
block(0x2595,7/8,0,1,1)              # ▕ right 1/8
for i,cp in enumerate([0x2581,0x2582,0x2583,0x2584,0x2585,0x2586,0x2587], start=1):
    block(cp, 0,0,1,i/8)             # ▁▂▃▄▅▆▇ lower eighths (▄ = lower half)
for i,cp in enumerate([0x258F,0x258E,0x258D,0x258C,0x258B,0x258A,0x2589], start=1):
    block(cp, 0,0,i/8,1)             # ▏▎▍▌▋▊▉ left eighths (▌ = left half)

nbox = len(_BOXJSON) + 3 + 19
print(f"   added: {len(want)} range + 14 lilmayu + lambda + L-stroke + o/O-slash, middot"
      f" + {len(braille)} braille + box/blocks (light+heavy+double+rounded+diagonals+blocks)")
for s in (mc, lm, gv, sr, sm, cr): s.close()
BUILDTMP = ROOT + "/sources/.cache"; os.makedirs(BUILDTMP, exist_ok=True)
MASTER_PATH = BUILDTMP + "/_master-Regular.ttf"
master.generate(MASTER_PATH)
master.close()
print("   master:", MASTER_PATH)

# ============================================================
# 2+3. Full range: weight x {upright, italic}
# ============================================================
print(">>> Weight range x italic")
made = []
for style, wclass, delta in WEIGHTS:
    for italic in (False, True):
        f = fontforge.open(MASTER_PATH)
        if delta != 0:
            f.selection.all()
            try: f.changeWeight(delta, "auto")
            except Exception as e: print(f"   changeWeight({delta}) warn:", e)
        if italic:
            f.selection.all()
            f.transform(SKEW)
        refit_all(f)
        brand(f, style, wclass, italic)
        fn = outfn(style, italic)
        f.generate(OUT+"/"+fn)
        f.close()
        made.append(fn)
    print(f"   {style:11} (w{wclass}, d{delta:+d}) + Italic")

print(f">>> Done: {len(made)} range files in {OUT}")
