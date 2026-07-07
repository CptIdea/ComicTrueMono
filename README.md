# Comic True Mono

A monospaced **Comic Sans for code** — gathered from the scattered forks of Comic Shanns /
Comic Mono and their years-old unmerged pull requests, with the goal of finally shipping a
**free monospaced Comic Sans with full Cyrillic support** (which currently does not exist anywhere).

- **18 fonts**: 9 weights (Thin → Black) × upright + italic
- **318 glyphs** and counting — full European Latin, symbols, arrows, math
- **Strictly monospaced**: every glyph is 1116 units wide (UPM 2048)
- **100% MIT** — every outline comes from an MIT-licensed source (see [SOURCES](sources/vendor/SOURCES.md))

> Status: **Latin is complete.** New glyphs drop into all 18 fonts in a single build run.
> The German eszett (ß/ẞ) is the only Latin letter still missing.

## Weights

| Weight | Class | Stem | | Weight | Class | Stem |
|---|---|---|---|---|---|---|
| Thin | 100 | 164 | | Medium | 500 | 206 |
| ExtraLight | 200 | 174 | | SemiBold | 600 | 216 |
| Light | 300 | 184 | | Bold | 700 | 226 |
| Regular | 400 | 194 | | ExtraBold | 800 | 274 |
| | | | | Black | 900 | 304 |

Bold (+32) is calibrated to the stem thickness of the real Comic Mono Bold. Every
other weight, and every italic (−12.7° slant), is generated automatically from a
single Regular master, so new glyphs need to be drawn only once.

## Install

Grab the `.ttf` files from [`fonts/ttf/`](fonts/ttf) and install them (double-click on
macOS/Windows, or drop into `~/.local/share/fonts` on Linux). In your editor, set the
font family to **Comic True Mono**.

## Build from source

Requires [FontForge](https://fontforge.org) (with its bundled Python) and
[fontTools](https://github.com/fonttools/fonttools).

```sh
pip install -r requirements.txt   # fontTools (FontForge is a system dependency)
make                              # build fonts + regenerate specimens
```

- `make fonts` — build `fonts/ttf/ComicTrueMono-*.ttf` from `sources/vendor/`
- `make site` — regenerate the landing page `index.html`
- `make clean` — remove build cache

## Repository layout

```
index.html            single-page landing / demo (served by GitHub Pages)
fonts/ttf/            built release binaries (the family)
sources/
  build.py            FontForge build pipeline (master → weights → italics)
  vendor/             vendored MIT source fonts (see SOURCES.md)
  tools/              landing-page generator + analysis scripts
RESEARCH.md           survey of existing solutions and why this project exists
LICENSE               MIT, with the full upstream attribution chain
```

## Demo

`index.html` is a single self-contained landing/demo page (and what GitHub Pages serves):
a live type tester, all nine weights, the full glyph grid, and the provenance story.
Open it in a browser, or generate it with `make site`.

## Credits & license

Comic True Mono is MIT-licensed. It is built on the work of Shannon Miwa (Comic Shanns),
dtinth (Comic Mono), Kyle Beechly (Serious Shanns), and the `clsn` and `lilmayu` forks —
all MIT. See [`LICENSE`](LICENSE) for the full attribution chain and
[`sources/vendor/SOURCES.md`](sources/vendor/SOURCES.md) for a per-file provenance table.
