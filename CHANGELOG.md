# Changelog

## v1.1.0 — 2026-07-08

### Added
- **Cyrillic (94: Russian + Ukrainian/Belarusian) and Greek (72, monotonic)**, imported from
  Comic Relief and fitted to the mono cell: uniform cap/x-height scale, per-glyph horizontal
  condensing for wide glyphs, and vertical-stem compensation so condensed letters keep an even
  weight. A global vertical lift matches Comic Relief's lighter stems to Comic Mono. Over-tall
  round/pointed caps (Δ Ω Ю) are pulled down to the cap line. This finally delivers the project's
  founding goal — a free monospaced Comic Sans with Cyrillic.
- Full weight range: 9 weights (Thin → Black) × upright + italic, all auto-generated
  from a single Regular master.
- Bold calibrated to the real Comic Mono Bold stem thickness (+32, stem 194 → 226).
- Auto-italic at −12.7° (matching kaBeech's angle) for every weight.
- Strict monospacing: every glyph normalized to a 1116-unit advance.
- Harvested community contributions from years-old unmerged pull requests (all MIT):
  λ (kaBeech), Æ æ Œ œ Þ þ ſ ƿ Ƿ ꝛ ∀ ∃ ∄ (clsn), corrected caron/háček diacritics
  (lilmayu), Ł ł (Serious Shanns), full European Latin (Comic Shanns v2).
- Constructed in-project (absent from every available source): ø, Ø (diagonal built
  from the `|` glyph, with the font's rounded terminals), · (raised middle dot).
- Reproducible build (`sources/build.py`) + specimen generators.

### Fixed
- Braille patterns (U+2800–28FF): scaled and centered onto the same line box the
  block/box-drawing glyphs fill. Imported ShannsMono braille was baseline-anchored at
  ~2/3 height, so it looked small and raised beside the full-height blocks; the dot grid
  now sits at the line-box center with rows on an even 1/8..7/8 grid, so braille art
  tiles cleanly and matches block size. Round dots preserved (uniform scale).
- HTML specimens: showcase, weight/bold comparison, coverage grid, base-font comparison,
  community-harvest demo.

### Changed
- **License: MIT → SIL OFL 1.1 for the fonts.** The Cyrillic/Greek source (Comic Relief) is
  OFL, and the OFL requires derivative fonts to stay OFL. Build scripts remain MIT. Font name
  tables now carry the OFL notice; see `OFL.txt` and `LICENSE`.

### Known gaps
- German eszett (ß, ẞ) — absent from all sources; to be commissioned.
- Comic Relief's horizontal strokes are natively heavier than Comic Mono's (~+15%); left as a
  source trait for now.
