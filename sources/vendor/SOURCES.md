# Vendored sources

Every font in this directory is used either as a build input or as a cited reference.
**All are MIT-licensed.** The MIT copyright/permission notices are retained in the
top-level [`LICENSE`](../../LICENSE).

| File | Origin | Ref | License | Used for |
|---|---|---|---|---|
| `ComicMono.ttf`, `ComicMono-Bold.ttf` | [dtinth/comic-mono-font](https://github.com/dtinth/comic-mono-font) | master | MIT | monospace base (Regular/Bold) |
| `SeriousShanns-Regular.otf`, `SeriousShanns-Italic.otf` | [kaBeech/serious-shanns](https://github.com/kaBeech/serious-shanns) | main | MIT | source of Ł ł |
| `gb-ComicMono.ttf`, `gb-ComicMono-Bold.ttf`, `gb-ComicMono-Italic.ttf`, `gb-ComicMono-BoldItalic.ttf` | [kaBeech/serious-shanns](https://github.com/kaBeech/serious-shanns) | `give-back` (PR dtinth/comic-mono-font#13) | MIT | λ + hand-drawn Italic/BoldItalic reference |
| `clsn-morechars-shanns2.ttf` | [clsn/comic-shanns](https://github.com/clsn/comic-shanns) | `morechars` | MIT | Æ æ Œ œ Þ þ ſ ƿ Ƿ ꝛ ∀ ∃ ∄ + European Latin |
| `clsn-thousands-shannsmono.ttf` | [clsn/comic-shanns](https://github.com/clsn/comic-shanns) | `thousands` | MIT | reference (digit-separating commas) |
| `lilmayu-shanns2.ttf` | [lilmayu/comic-shanns](https://github.com/lilmayu/comic-shanns) | `fix/czech-slovak-diacritics` | MIT | corrected caron/háček diacritics |
| `ComicShanns-v1.otf`, `ComicShanns-v2.otf`, `ComicShanns-v2.ttf` | [shannpersand/comic-shanns](https://github.com/shannpersand/comic-shanns) | master | MIT | root letterforms; comparison |
| `ComicShannsMono-Regular.otf`, `ComicShannsMono-Regular.ttf` | [jesusmgg/comic-shanns-mono](https://github.com/jesusmgg/comic-shanns-mono) | master | MIT | comparison (box-drawing, Braille) |
| `nerd-ComicMonoNerdFont-Regular.ttf` | [symroe/comic-mono-font](https://github.com/symroe/comic-mono-font) | `nerd-font` (PR #17) | MIT + icon licenses | reference (Nerd Fonts patch of Comic Mono) |

## Build inputs actually consumed by `sources/build.py`

`ComicMono.ttf`, `ComicMono-Bold.ttf`, `SeriousShanns-Regular.otf`,
`clsn-morechars-shanns2.ttf`, `lilmayu-shanns2.ttf`, `gb-ComicMono.ttf`,
`gb-ComicMono-Italic.ttf`, `gb-ComicMono-BoldItalic.ttf`.

The rest are kept for provenance and for the comparison specimens.
