#!/usr/bin/env python3
"""Compare each harvested artifact against its logical base:
added/removed codepoints and changed contours (over shared glyphs)."""
from fontTools.ttLib import TTFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V = ROOT + "/sources/vendor/"

def glyph_sig(font, glyphname):
    """Rough contour signature of a glyph: point coordinates + contour end flags."""
    glyf = font.get('glyf')
    if glyf is None or glyphname not in glyf:
        return None
    g = glyf[glyphname]
    try:
        coords, endPts, flags = g.getCoordinates(glyf)
        return (tuple(map(tuple, coords)), tuple(endPts))
    except Exception:
        return ('composite/empty',)

def cmap_and_sigs(path):
    f = TTFont(path)
    cmap = f.getBestCmap()
    hmtx = f['hmtx']
    widths = {hmtx[n][0] for n in cmap.values()}
    sigs = {cp: glyph_sig(f, name) for cp, name in cmap.items()}
    return f, cmap, sigs, widths

def compare(label, base_path, cand_path, note=""):
    _, cb, sb, wb = cmap_and_sigs(base_path)
    _, cc, sc, wc = cmap_and_sigs(cand_path)
    added = sorted(set(cc) - set(cb))
    removed = sorted(set(cb) - set(cc))
    changed = sorted(cp for cp in (set(cb) & set(cc)) if sb[cp] != sc[cp])
    def show(cps, n=200):
        return " ".join(f"{chr(c)}(U+{c:04X})" for c in cps[:n]) or "-"
    print("="*76)
    print(f"{label}   {note}")
    print(f"  base:      {base_path.split('/')[-1]}  (widths={len(wb)})")
    print(f"  candidate: {cand_path.split('/')[-1]}  (widths={len(wc)}, {'MONO' if len(wc)==1 else 'not mono'})")
    print(f"  + added ({len(added)}): {show(added)}")
    if removed: print(f"  - removed ({len(removed)}): {show(removed)}")
    print(f"  ~ changed contour ({len(changed)}): {show(changed)}")
    return {'added':added,'removed':removed,'changed':changed}

# 1. kaBeech give-back: edits to Comic Mono itself (Regular/Bold)
compare("give-back Regular vs our Comic Mono", V+"ComicMono.ttf", V+"gb-ComicMono.ttf")
compare("give-back Bold vs our Comic Mono Bold", V+"ComicMono-Bold.ttf", V+"gb-ComicMono-Bold.ttf")

# Italic/BoldItalic — no base to diff, just report characteristics
for f in ["gb-ComicMono-Italic.ttf", "gb-ComicMono-BoldItalic.ttf"]:
    ff, cm, sg, w = cmap_and_sigs(V+f)
    print("="*76); print(f"NEW STYLE: {f}  glyphs in cmap={len(cm)}  widths={len(w)} ({'MONO' if len(w)==1 else 'not mono'})")

# 2. lilmayu diacritics vs shannpersand v2
compare("lilmayu Czech/Slovak diacritics vs Comic Shanns v2", V+"ComicShanns-v2.ttf", V+"lilmayu-shanns2.ttf",
        note="(expect ~changes on caron letters + caron itself)")

# 3. clsn morechars vs shannpersand v2
compare("clsn 'critically-needed characters' vs Comic Shanns v2", V+"ComicShanns-v2.ttf", V+"clsn-morechars-shanns2.ttf")

# 4. clsn thousands vs comic-shanns-mono
compare("clsn 'digit-separating commas' vs Comic Shanns Mono", V+"ComicShannsMono-Regular.ttf", V+"clsn-thousands-shannsmono.ttf")
