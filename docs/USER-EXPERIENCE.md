# User experience

## Install

```bash
mkdir -p .opencode/skills && cp -r skills/drawio-architecture-diagram .opencode/skills/
```

## What a reader gets

A diagram inside the Markdown, at the size it was drawn, that stays sharp on a retina screen. Clicking it opens the SVG, and the file can be dragged into draw.io and edited, because the diagram source travels inside it.

## What a maintainer gets

A `.drawio` file that diffs cleanly, a style that does not drift between diagrams, and a build that refuses to ship an artifact that no longer matches its source.

## Quality attributes

| Attribute | How it is met |
|---|---|
| Consistency | the house style is pinned in one reference and the example is drawn with it |
| Correctness | the committed artifact is compared against its source on every build |
| Editability | the reader receives a file that carries the diagram source |
| Reproducibility | the export runs a pinned image, so the same source renders the same artifact |
