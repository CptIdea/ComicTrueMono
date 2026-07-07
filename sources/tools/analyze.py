#!/usr/bin/env python3
"""Analyze glyph coverage and metrics of the vendored free fonts.

For each font:
  - number of glyphs in the cmap,
  - whether it has Cyrillic (U+0400..U+04FF, U+0500..U+052F suppl., yo/Yo),
  - which Cyrillic codepoints are present,
  - monospacing (how many distinct advance widths),
  - main Unicode blocks covered.

Usage: python3 sources/tools/analyze.py <dir-with-fonts>
"""
import sys, glob, os
from fontTools.ttLib import TTFont

CYR_RANGES = [(0x0400, 0x04FF), (0x0500, 0x052F), (0x2DE0, 0x2DFF), (0xA640, 0xA69F)]

def in_cyr(cp):
    return any(a <= cp <= b for a, b in CYR_RANGES)

def block(cp):
    if cp < 0x80: return "Basic Latin"
    if cp < 0x100: return "Latin-1 Suppl"
    if cp < 0x180: return "Latin Ext-A"
    if cp < 0x250: return "Latin Ext-B"
    if 0x300 <= cp < 0x370: return "Combining diacritics"
    if 0x370 <= cp < 0x400: return "Greek"
    if 0x400 <= cp < 0x500: return "Cyrillic"
    if 0x500 <= cp < 0x530: return "Cyrillic Suppl"
    if 0x2000 <= cp < 0x2070: return "General Punctuation"
    if 0x2070 <= cp < 0x20D0: return "Super/Subscript+Currency"
    if 0x2100 <= cp < 0x2150: return "Letterlike"
    if 0x2150 <= cp < 0x2190: return "Number Forms"
    if 0x2190 <= cp < 0x2200: return "Arrows"
    if 0x2200 <= cp < 0x2300: return "Math Operators"
    if 0x2300 <= cp < 0x2400: return "Misc Technical"
    if 0x2500 <= cp < 0x2580: return "Box Drawing"
    if 0x2580 <= cp < 0x25A0: return "Block Elements"
    if 0x25A0 <= cp < 0x2600: return "Geometric Shapes"
    if 0x2600 <= cp < 0x2700: return "Misc Symbols"
    if 0x2800 <= cp < 0x2900: return "Braille"
    return f"U+{cp>>8:02X}xx"

def analyze(path):
    f = TTFont(path)
    cmap = f.getBestCmap()
    cps = sorted(cmap.keys())
    blocks = {}
    for cp in cps:
        blocks[block(cp)] = blocks.get(block(cp), 0) + 1
    cyr = [cp for cp in cps if in_cyr(cp)]
    hmtx = f['hmtx']
    widths = {}
    for name in cmap.values():
        w = hmtx[name][0]
        widths[w] = widths.get(w, 0) + 1
    upm = f['head'].unitsPerEm
    try:
        nm = f['name'].getDebugName(4) or f['name'].getDebugName(1)
    except Exception:
        nm = "?"
    return {
        'file': os.path.basename(path), 'name': nm, 'upm': upm,
        'nglyphs_total': f['maxp'].numGlyphs, 'ncmap': len(cps),
        'blocks': blocks, 'cyr': cyr, 'widths': widths, 'cps': set(cps),
    }

def fmt_cyr(cyr):
    if not cyr: return "NONE"
    return f"{len(cyr)} codepoints: " + " ".join(chr(c) for c in cyr[:80])

def main():
    files = sorted(glob.glob(sys.argv[1] + "/*.ttf") + glob.glob(sys.argv[1] + "/*.otf"))
    res = [analyze(p) for p in files]
    for r in res:
        print("="*72)
        print(f"{r['file']}  |  \"{r['name']}\"")
        print(f"  UPM={r['upm']}  glyphs(maxp)={r['nglyphs_total']}  in cmap={r['ncmap']}")
        ws = sorted(r['widths'].items(), key=lambda x:-x[1])
        mono = "MONOSPACED" if len([w for w in r['widths'] if w>0])==1 else f"proportional ({len(r['widths'])} distinct widths)"
        print(f"  metric: {mono}; top widths(units): " + ", ".join(f"{w}x{c}" for w,c in ws[:5]))
        print(f"  CYRILLIC: {fmt_cyr(r['cyr'])}")
        print(f"  blocks: " + ", ".join(f"{k}={v}" for k,v in sorted(r['blocks'].items(), key=lambda x:-x[1])))
    print("\n" + "#"*72)
    print("# Pairwise cmap-coverage comparison (characters that differentiate the fonts)")
    print("#"*72)
    for i in range(len(res)):
        for j in range(i+1, len(res)):
            a, b = res[i], res[j]
            only_a = a['cps'] - b['cps']
            only_b = b['cps'] - a['cps']
            print(f"\n{a['file']}  vs  {b['file']}:")
            print(f"  shared={len(a['cps']&b['cps'])}  only-in-1st={len(only_a)}  only-in-2nd={len(only_b)}")

if __name__ == '__main__':
    main()
