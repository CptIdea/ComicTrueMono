#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure the native stroke weight of Comic Relief's Greek + Cyrillic glyphs.

Writes sources/tools/cr-stems.json = {"stems": {codepoint: weight}, "median": N}, consumed by
build.py so it knows how much stem a wide glyph loses to horizontal condensing (and can add it
back with embolden_x). Run with the venv that has fontTools:

    python3 sources/tools/measure_cr_stems.py sources/vendor/ComicRelief-Regular.ttf

The weight metric is dominant_stroke: the *mode* of filled horizontal run-widths sampled across
the glyph height. Not the minimum (which catches incidental hairline slivers — curve terminals,
tongue tips — and mis-ranks normal glyphs as thin), but the most common run width, which is the
vertical stem the eye actually reads.
"""
import sys, os, json, statistics
from collections import Counter
from fontTools.ttLib import TTFont
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.boundsPen import BoundsPen

def dominant_stroke(gs, gname, bucket=12):
    bp = BoundsPen(gs); gs[gname].draw(bp)
    if not bp.bounds:
        return None
    x0, y0, x1, y1 = bp.bounds
    h = y1 - y0
    if h <= 0:
        return None
    widths = []
    N = 52
    for i in range(2, N - 1):
        y = y0 + h * i / N
        prev = False; run_start = None; x = x0 - 3
        while x <= x1 + 3:
            p = PointInsidePen(gs, (x, y)); gs[gname].draw(p)
            inside = p.getResult()
            if inside and not prev:
                run_start = x
            if (not inside) and prev:
                w = x - run_start
                if w > 15:
                    widths.append(w)
            prev = inside; x += 3
        if prev:
            w = x - run_start
            if w > 15:
                widths.append(w)
    if not widths:
        return None
    counts = Counter(int(w // bucket) for w in widths)
    top = counts.most_common(1)[0][0]
    return round(statistics.median([w for w in widths if int(w // bucket) == top]))

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "sources/vendor/ComicRelief-Regular.ttf"
    t = TTFont(src); gs = t.getGlyphSet(); cmap = t.getBestCmap()
    stems = {}
    for cp in list(range(0x0370, 0x0400)) + list(range(0x0400, 0x0500)):
        gname = cmap.get(cp)
        if not gname:
            continue
        v = dominant_stroke(gs, gname)
        if v:
            stems[cp] = v
    median = round(statistics.median(list(stems.values())))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cr-stems.json")
    json.dump({"stems": {str(k): v for k, v in stems.items()}, "median": median},
              open(out, "w"))
    print(f"measured {len(stems)} Comic Relief glyphs; median native stem = {median}")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
