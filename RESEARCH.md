# Comic True Mono — survey of existing solutions

Goal: a monospaced "Comic Sans" with Cyrillic support. The project's aim is to build a
free (no-cost) monospaced version of Comic Sans with full Cyrillic support, which does
not currently exist.

Research date: 2026-07-07.

## Key takeaway

**Only the paid Comic Code supports Cyrillic out of the box.**
All the popular free Comic Sans monospace forks ship **without Cyrillic**.
→ The "monospaced Comic Sans + Cyrillic" free niche is empty right now. That gap is the
very reason for a new project.

## Overview of existing fonts

| Font | Monospaced | Cyrillic | License / price | Basis |
|---|---|---|---|---|
| **Comic Code** | yes | **yes** (+ Greek) | paid (~$59+, has a Coding Essentials pack) | original design by Toshi Omagari |
| **Comic Mono** | yes | no (Latin + accents/math) | MIT, free | patch of Comic Shanns v1 |
| **Comic Shanns Mono** | yes | no (Latin + diacritics, box-drawing, Braille) | free | Comic Shanns v2 |
| **Serious Shanns** | yes | no | free (MIT) | fork of Comic Mono |
| **Comic Shanns (v1/v2)** | no (proportional) | no (Latin + accents + math in v2) | free | Shannon Miwa |

Verified by reading each project's README/page directly — Cyrillic is nowhere claimed.
Comic Mono and Comic Shanns Mono are built on Comic Shanns, which has Latin + accents +
math symbols, but no Cyrillic.

## Verified against the facts (reading the cmap, not the README) — 2026-07-07

Downloaded into `sources/vendor/`, coverage checked with fonttools (`sources/tools/analyze.py`).
**None of them contains Cyrillic (U+0400–04FF)** — confirmed at the cmap table level:

| Font | glyphs in cmap | metric | coverage beyond Latin |
|---|---|---|---|
| Comic Mono / -Bold | 103 | mono (all 1116/2048) | Basic Latin + punctuation only |
| Serious Shanns | 98 | mono (all 548/1000) | Latin − almost = Comic Mono (−3 chars `` ` `` and others, +2 Ext-A, +1 Greek) |
| Comic Shanns v1 | 103 | **proportional** (3 widths) | = Comic Mono in composition, but not mono |
| Comic Shanns v2 | 316 | **proportional** (4 widths) | +Latin-1, +Ext-A (105), diacritics, arrows, math symbols |
| Comic Shanns Mono | 613 | **proportional in fact** (5 widths!) | everything from v2 +Braille (256) +Box Drawing (28) |
| JetBrains Mono (fallback) | 1363 | mono (600/1000) | **has Cyrillic: 122 codepoints** (Rus+Ukr+Bel) |

**How they differ from one another (the essentials):**
- **Comic Mono vs Serious Shanns** — nearly identical in character set (95 shared); these
  are the closest relatives (both monospaced forks of Comic Shanns v1). Serious Shanns is
  slightly poorer in ASCII symbols.
- **Comic Mono is genuinely monospaced** (a single width for every glyph), as is Serious Shanns.
- **Comic Shanns Mono, despite its name, has 5 different widths in the cmap** — here "Mono"
  refers to the style/lineage, and by metric it is not strictly monospaced (verify before
  using it as a base).
- **Comic Shanns v1 → v2** — v2 is three times larger (103→316): added Latin-1/Ext-A,
  diacritics, math symbols.
- **Richest of all in Latin + symbols** — Comic Shanns Mono (Braille + box-drawing), but
  still **without Cyrillic**.

The RESEARCH.md conclusion is confirmed at the glyph level: no free mono Comic Sans with
Cyrillic exists. Visual comparison tool: `specimens/specimen.html` (a single piece of Go code
with Cyrillic comments rendered in every font).

## What this means for the new project

- **Base for the fork:** Comic Mono (MIT) — the most widely used, with a clean monospaced
  metric, assembled by a Python patch script from Comic Shanns. Its license permits derivatives.
- **Where to source the Cyrillic glyph shapes:**
  - option A — draw/adapt Cyrillic in the Comic Sans style by hand (FontForge / Glyphs),
    fitting it to Comic Mono's monospaced width;
  - option B — take the Cyrillic from the Cyrillic version of Comic Sans MS and conform it
    to the monospaced metric (be careful with Microsoft's license — MS glyphs are
    proprietary and cannot be transferred directly into a free font; usable only as a
    visual reference, not as a source of outlines).
  - Recommendation: draw the Cyrillic ourselves from a reference — this is the only
    license-clean path to a free release.
- **Metric:** all glyphs must share the same width (as in Comic Mono — the width alignment
  is done by the original patch script). Draw the Cyrillic letters at that width from the start.
- **MVP coverage:** Russian Cyrillic (А–Я, а–я, Ё/ё), plus ideally Ukrainian/Belarusian
  (Ґ, Є, І, Ї, Ў) and the usual marks.

## Links

- Comic Code — https://tosche.net/fonts/comic-code
- Comic Code family (I Love Typography) — https://fonts.ilovetypography.com/fonts/tabular-type-foundry/comic-code
- Comic Mono — https://github.com/dtinth/comic-mono-font
- Comic Shanns Mono — https://github.com/jesusmgg/comic-shanns-mono
- Serious Shanns — https://github.com/kaBeech/serious-shanns (the ChaoticStowage fork was deleted)
- Comic Shanns (original) — referenced in the Comic Mono README
