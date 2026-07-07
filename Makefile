# Comic True Mono build
#
# Requires FontForge (with bundled Python) and fontTools (pip install -r requirements.txt).

FONTFORGE ?= fontforge
PYTHON    ?= python3

.PHONY: all fonts site clean

all: fonts site

# Build the release family into fonts/ttf/ from sources/vendor/.
fonts:
	$(FONTFORGE) -lang=py -script sources/build.py

# Regenerate the landing page (index.html) from the built fonts.
site:
	$(PYTHON) sources/tools/gen_landing.py

clean:
	rm -rf sources/.cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
