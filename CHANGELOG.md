# Changelog

## Unreleased

### Added
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
- HTML specimens: showcase, weight/bold comparison, coverage grid, base-font comparison,
  community-harvest demo.

### Known gaps
- German eszett (ß, ẞ) — absent from all sources; to be commissioned.
