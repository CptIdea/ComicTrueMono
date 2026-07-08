# Vendored sources

Every font in this directory is used either as a build input or as a cited reference.
All are MIT-licensed **except Comic Relief, which is SIL OFL 1.1** — and that one OFL input is
why the released fonts ship under the OFL (see [`LICENSE`](../../LICENSE) and
[`OFL.txt`](../../OFL.txt)). The upstream copyright/permission notices are retained in `LICENSE`.

| File | Origin | Ref | License | Used for |
|---|---|---|---|---|
| `ComicMono.ttf`, `ComicMono-Bold.ttf` | [dtinth/comic-mono-font](https://github.com/dtinth/comic-mono-font) | master | MIT | monospace base (Regular/Bold) |
| `ComicRelief-Regular.ttf` | [loudifier/Comic-Relief](https://github.com/loudifier/Comic-Relief) | master | **OFL 1.1** | Cyrillic (94) + Greek (72), fitted to the mono cell |
| `SeriousShanns-Regular.otf`, `SeriousShanns-Italic.otf` | [kaBeech/serious-shanns](https://github.com/kaBeech/serious-shanns) | main | MIT | source of Ł ł |
| `gb-ComicMono.ttf`, `gb-ComicMono-Bold.ttf`, `gb-ComicMono-Italic.ttf`, `gb-ComicMono-BoldItalic.ttf` | [kaBeech/serious-shanns](https://github.com/kaBeech/serious-shanns) | `give-back` (PR dtinth/comic-mono-font#13) | MIT | λ + hand-drawn Italic/BoldItalic reference |
| `clsn-morechars-shanns2.ttf` | [clsn/comic-shanns](https://github.com/clsn/comic-shanns) | `morechars` | MIT | Æ æ Œ œ Þ þ ſ ƿ Ƿ ꝛ ∀ ∃ ∄ + European Latin |
| `clsn-thousands-shannsmono.ttf` | [clsn/comic-shanns](https://github.com/clsn/comic-shanns) | `thousands` | MIT | reference (digit-separating commas) |
| `lilmayu-shanns2.ttf` | [lilmayu/comic-shanns](https://github.com/lilmayu/comic-shanns) | `fix/czech-slovak-diacritics` | MIT | corrected caron/háček diacritics |
| `ComicShanns-v1.otf`, `ComicShanns-v2.otf`, `ComicShanns-v2.ttf` | [shannpersand/comic-shanns](https://github.com/shannpersand/comic-shanns) | master | MIT | root letterforms; comparison |
| `ComicShannsMono-Regular.otf`, `ComicShannsMono-Regular.ttf` | [jesusmgg/comic-shanns-mono](https://github.com/jesusmgg/comic-shanns-mono) | master | MIT | Braille + comparison (box-drawing) |

Every file above is MIT except Comic Relief (OFL 1.1). A Nerd-Fonts-patched Comic Mono was
reviewed during research but is **not vendored**: the ~10k patched-in icons carry the Nerd
Fonts project's mixed licenses (MIT / OFL / Apache-2.0 / CC-BY). If a Nerd Font variant is
built later, run the official patcher as a separate step and document those icon licenses there.

## Build inputs actually consumed by `sources/build.py`

`ComicMono.ttf`, `ComicMono-Bold.ttf`, `SeriousShanns-Regular.otf`,
`clsn-morechars-shanns2.ttf`, `lilmayu-shanns2.ttf`, `gb-ComicMono.ttf`,
`gb-ComicMono-Italic.ttf`, `gb-ComicMono-BoldItalic.ttf`, `ComicRelief-Regular.ttf`.

The rest are kept for provenance and for the comparison specimens.
