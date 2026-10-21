# Domain model, level 2

The rules that hold at the detailed level.

## Invariants

1. **An artifact and its source carry the same diagram.** A committed `.drawio.svg` whose embedded XML differs from its `.drawio` sibling is drift, and the build fails.
2. **An artifact carries its source.** The root SVG element holds the diagram XML in a `content` attribute. Without it the file is a picture and the reader cannot edit it.
3. **A source is readable text.** Uncompressed XML, so a diff shows what changed.
4. **The comparison reads both sides the way draw.io reads a diagram.** A source that spells out a default attribute, or writes a number in another notation, is not drift.
5. **A rendered artifact is looked at.** Structural validity and readability are different properties, and only the second one needs an eye.
6. **The house style is a contract.** The example under `examples/` is drawn with the rules in `skills/drawio-architecture-diagram/references/house-style.md`, and a rule change moves both.

## Entities

| Entity | Identity | Notable state |
|---|---|---|
| Source | the `.drawio` file path | the diagram model, uncompressed |
| Artifact | the `.drawio.svg` file path | the rendered SVG plus the embedded model |
| Cell | its id within a diagram | its label, its style, its geometry, its endpoints |
| Fixture | its file name under `tests/fixtures/` | a construct the exporter's behaviour was measured on |
