#!/usr/bin/env bash
# Render a .drawio source into a committed .drawio.svg that carries the diagram
# XML inside the SVG root element.
#
# The committed file is the reader-facing artifact. GitHub renders it inline in
# Markdown, and draw.io reopens it with the diagram intact, so a reader can
# download the exact file the repository ships and keep editing it.
#
# The draw.io desktop application is not installed on this workstation, so the
# export runs the same desktop CLI inside the rlespinasse/drawio-export
# container. The -e flag is the --embed-diagram flag the AWS skill prescribes.
#
# Usage: bash scripts/render-drawio-svg.sh <input.drawio> <output.drawio.svg>
#
# The path above is relative to the directory this script sits in.

set -euo pipefail

IMAGE="rlespinasse/drawio-export:v4.60.0"
BORDER=24

if [ "$#" -ne 2 ]; then
  echo "Usage: bash scripts/render-drawio-svg.sh <input.drawio> <output.drawio.svg>" >&2
  exit 2
fi

INPUT="$1"
OUTPUT="$2"

if [ ! -f "$INPUT" ]; then
  echo "FAIL: input not found: $INPUT" >&2
  exit 1
fi

OUTPUT_DIR="$(dirname "$OUTPUT")"
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "FAIL: output directory does not exist: $OUTPUT_DIR" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "FAIL: docker is required to run the draw.io desktop CLI headlessly." >&2
  echo "      Install Docker, or install draw.io Desktop and export with:" >&2
  echo "      drawio -x -f svg -e --embed-svg-fonts false -b 24 -o <output> <input.drawio>" >&2
  exit 127
fi

# The container mounts a directory under the home directory, not a system
# temporary directory. Docker Desktop shares the home directory by default, so
# a mount under /var/folders resolves to an empty directory on the container
# side and the export fails with a path error that reads like a corrupt file.
# The work directory sits outside any repository so that rendering never
# leaves a scratch directory in the tree being drawn into.
WORK="${DRAWDIO_RENDER_WORK:-$HOME/.cache/drawio-architecture-diagram/render}"
rm -rf "$WORK"
mkdir -p "$WORK"

cleanup() {
  rm -rf "$WORK"
}
trap cleanup EXIT

cp "$INPUT" "$WORK/input.drawio"

# --embed-svg-fonts false keeps the labels as real SVG text elements. With
# fonts embedded, draw.io rasterises every HTML label into a base64 PNG
# inside the SVG, which measured seven times larger on the reference
# diagram and makes the text unsearchable. The border keeps an edge label
# that overhangs the leftmost shape from being cut off at the canvas edge.
export_svg() {
  docker run --rm -v "$WORK:/data" "$IMAGE" \
    -f svg \
    -e \
    --embed-svg-fonts false \
    --remove-page-suffix \
    -b "$BORDER" \
    --output out \
    /data/input.drawio
}

# The export runs inside a container, and a container occasionally reads a
# truncated copy of the mounted file. That failure reads like a corrupt
# source, so the run is repeated once before the error is reported.
if ! export_svg >"$WORK/export.log" 2>&1; then
  if ! export_svg >"$WORK/export.log" 2>&1; then
    echo "FAIL: the draw.io export failed. Container output:" >&2
    cat "$WORK/export.log" >&2
    if grep -q "must exist" "$WORK/export.log"; then
      echo "      The container could not read the mounted path. Check that" >&2
      echo "      $HOME is shared with Docker Desktop." >&2
    elif grep -q "can parse xml" "$WORK/export.log"; then
      echo "      The container could not parse the input as draw.io XML." >&2
    fi
    exit 1
  fi
fi

EXPORTED="$WORK/out/input.svg"
if [ ! -f "$EXPORTED" ]; then
  echo "FAIL: the draw.io export produced no file named out/input.svg." >&2
  echo "      The render script handles a single-page diagram." >&2
  cat "$WORK/export.log" >&2
  echo "      Files the export produced:" >&2
  find "$WORK/out" -type f 2>/dev/null | sed "s|^|        |" >&2
  echo "      A diagram with more than one page produces one file per page, and" >&2
  echo "      this script handles a single-page diagram only." >&2
  exit 1
fi

# A transparent canvas loses the diagram's dark strokes against a dark GitHub
# page, so the canvas is painted white unless the diagram set a background of
# its own. The embedded diagram XML is untouched either way.
#
# The result is written to a temporary path and moved into place, so a failed
# run never replaces the previous artifact with a broken one.
python3 - "$EXPORTED" "$WORK/output.svg" <<'PY'
import sys
import xml.etree.ElementTree as ET

source, target = sys.argv[1], sys.argv[2]
svg = open(source, encoding="utf-8").read()

try:
    root = ET.fromstring(svg)
except ET.ParseError as error:
    sys.exit(f"FAIL: the exported SVG is not well-formed XML: {error}")

if root.get("content") is None:
    sys.exit("FAIL: the exported SVG root carries no content attribute, so draw.io cannot recover the diagram.")

transparent = "background: transparent; background-color: transparent; color-scheme: light;"
if transparent in svg:
    # The export leaves the canvas transparent, and the diagram's dark strokes
    # disappear against a dark GitHub page. Paint it white.
    svg = svg.replace(
        transparent,
        "background: #FFFFFF; background-color: #FFFFFF; color-scheme: light;",
        1,
    )
elif "color-scheme: light;" not in svg:
    sys.exit("FAIL: the exported SVG has an unexpected root style attribute.")

if not svg.endswith("\n"):
    svg += "\n"

open(target, "w", encoding="utf-8").write(svg)
PY

mv "$WORK/output.svg" "$OUTPUT"

echo "rendered $INPUT -> $OUTPUT"
