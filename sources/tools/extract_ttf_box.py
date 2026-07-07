#!/usr/bin/env python
# Extract box-drawing glyph contours (U+2500-2570) from a built TTF into a flat JSON
# {codepoint: [contour, ...]} of on-curve points, for TTF-side geometry verification.
# Run: fontforge -lang=py -script sources/tools/extract_ttf_box.py <font.ttf> <out.json>
import fontforge, json, sys

font = fontforge.open(sys.argv[1])
out = {}
for g in font.glyphs():
    cp = g.unicode
    if cp is None or not (0x2500 <= cp <= 0x2570):
        continue
    contours = []
    for c in g.foreground:
        ring = [(round(p.x), round(p.y)) for p in c if p.on_curve]
        if len(ring) >= 3:
            contours.append(ring)
    if contours:
        out[str(cp)] = contours
json.dump(out, open(sys.argv[2], "w"))
print("extracted", len(out), "box glyphs from", sys.argv[1])
