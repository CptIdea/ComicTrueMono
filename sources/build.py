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
import fontforge, psMat, math, os

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
    (0xA75B, 0xA75B),   # r-rotunda
]
# These 14 are overridden from lilmayu (corrected caron / hacek).
CEU_ACCENT = [0x010C,0x010D,0x010E,0x011A,0x011B,0x0147,0x0148,
              0x0158,0x0159,0x0160,0x0161,0x0164,0x017D,0x017E]
LAMBDA = 0x03BB

def recenter(g):
    xmin, ymin, xmax, ymax = g.boundingBox()
    if xmax > xmin:
        g.transform(psMat.translate((CELL - (xmin + xmax)) / 2.0, 0))
    g.width = CELL

def refit_all(font):
    for g in font.glyphs():
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

def paste_glyph(dst, src, cp):
    src.selection.select(("unicode", None), cp)
    src.copy()
    dst.createChar(cp)
    dst.selection.select(("unicode", None), cp)
    dst.paste()
    recenter(dst[cp])

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

for src in (mc, lm, sr):        # flatten any composite references -> real contours
    src.selection.all()
    try: src.unlinkReferences()
    except Exception: pass

master = fontforge.open(VENDOR+"/ComicMono.ttf")
base_cps = {g.unicode for g in master.glyphs() if g.unicode and g.unicode > 0}  # already in Comic Mono
mc_cps = {g.unicode for g in mc.glyphs() if g.unicode and g.unicode > 0}
want = sorted({cp for a, b in IMPORT_RANGES for cp in range(a, b+1)} & mc_cps - base_cps)
for cp in want:
    paste_glyph(master, mc, cp)
for cp in CEU_ACCENT:           # override with lilmayu's corrected diacritics
    paste_glyph(master, lm, cp)
paste_glyph(master, gv, LAMBDA)
for cp in (0x0141, 0x0142):     # L-stroke / l-stroke from Serious Shanns (MIT)
    paste_glyph(master, sr, cp)
# Constructed (absent from every source — verified across all 17 files):
slash_through(master, 0x006F, 0x00F8, "oslash")   # o-slash
slash_through(master, 0x004F, 0x00D8, "Oslash")   # O-slash
raised_dot(master)                                 # middle dot
print(f"   added: {len(want)} by range + 14 lilmayu + lambda + L-stroke + constructed o/O-slash, middot")
for s in (mc, lm, gv, sr): s.close()
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
