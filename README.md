# Comic True Mono

A monospaced **Comic Sans for code** — a stitched-together Frankenfont gathered from the
scattered forks of Comic Shanns / Comic Mono and their years-old unmerged pull requests, built
to finally ship a **free monospaced Comic Sans with full Cyrillic support** (which did not exist
anywhere). That goal is now met — plus Greek.

- **18 fonts**: 9 weights (Thin → Black) × upright + italic
- **881 glyphs** — full European Latin, **Cyrillic** (94: RU · UA · BY) and **Greek** (72,
  monotonic), symbols, arrows, math, box-drawing, Braille
- **Strictly monospaced**: every glyph is 1116 units wide (UPM 2048)
- **Free & libre** — fonts under the [SIL OFL 1.1](OFL.txt), build scripts MIT
  (see [SOURCES](sources/vendor/SOURCES.md))

> Status: **Latin, Cyrillic and Greek are complete.** New glyphs drop into all 18 fonts in a
> single build run. The German eszett (ß/ẞ) is the only Latin letter still missing.

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

## Releases

CI (GitHub Actions) rebuilds the whole family from source on every push and pull
request. To cut a release, push a `v*` tag:

```sh
git tag v1.0.0
git push origin v1.0.0
```

This rebuilds the fonts, packages them into `ComicTrueMono-v1.0.0.zip`, and publishes
a GitHub Release with the zip and the individual `.ttf` files attached.

## Repository layout

```
index.html            single-page landing / demo (served by GitHub Pages)
fonts/ttf/            built release binaries (the family)
sources/
  build.py            FontForge build pipeline (master → weights → italics)
  vendor/             vendored source fonts (see SOURCES.md)
  tools/              landing-page generator + analysis scripts
LICENSE               licensing overview + full upstream attribution chain
OFL.txt               SIL Open Font License 1.1 (the fonts)
```

## Demo

`index.html` is a single self-contained landing/demo page (and what GitHub Pages serves):
a live type tester, all nine weights, the full glyph grid, and the provenance story.
Open it in a browser, or generate it with `make site`.

## Credits & license

The **fonts** are licensed under the [SIL Open Font License 1.1](OFL.txt); the **build
scripts** are MIT. The switch from MIT to OFL happened for a reason: the only clean, comic-styled
Cyrillic and Greek in the free world lives in **Comic Relief** (Loudifier / Jeff Davis), which is
OFL — and the OFL asks derivative fonts to stay OFL.

Built on the work of Shannon Miwa (Comic Shanns), dtinth (Comic Mono), Kyle Beechly (Serious
Shanns), the `clsn` and `lilmayu` forks (all MIT), and Comic Relief (OFL) for Cyrillic & Greek.
See [`LICENSE`](LICENSE) for the full attribution chain and
[`sources/vendor/SOURCES.md`](sources/vendor/SOURCES.md) for a per-file provenance table.
