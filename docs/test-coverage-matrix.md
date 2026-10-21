# Test coverage matrix

The master coverage matrix for this repository. One row per workflow path the skill exercises, one column per coverage class, and a weight that says how much the path matters when it breaks.

## Coverage classes

| Class | Meaning here |
|---|---|
| Happy | the diagram is authored, rendered and committed as it should be |
| Sad | a source and its artifact have drifted apart, and the build says so |
| Edge | a legitimate source that a naive comparison would call stale |
| Corner | a source or artifact so malformed that the check must name the real cause rather than crash |

## Blast radius

| Path | Touches | Weight |
|---|---|---|
| Diagram authoring, from a source to a committed artifact | Integrity | High |
| The staleness comparison between an artifact and its source | Integrity | High |
| The render path, from a source to an SVG | Integrity | High |

Integrity is the only category in play. A diagram that drifts from its source, or an artifact that fails to render, misleads every reader who sees it. Nothing here touches safety, security, money, privacy or availability.

## The matrix

| Path | Happy | Sad | Edge | Corner |
|---|---|---|---|---|
| Author and commit a diagram | A source plus its artifact, the artifact matching the source | A changed label, style, geometry, edge endpoint, edge waypoint, wrapper label, page name, page size, page background, page scale or label offset is reported as drift | A source that spells out a default attribute, holds a number in another notation, carries a compressed model, or nests a wrapper is read as equal | A source that is not XML, an artifact that is not well formed, an artifact with no embedded diagram, a compressed source that is not base64, or one that does not decompress is reported by name |
| The comparison itself | Every fixture diagram compares equal to the artifact the exporter produced | Every deliberate damage case is caught, and the report names the attribute that changed | Every fixture compares equal, which is what keeps the comparison from calling a legitimate source stale | Every broken input produces a message that names the cause rather than a traceback |

## What the fixtures are

`tests/fixtures/` holds one diagram per construct the exporter's behaviour was measured on, and the artifact the real exporter produced for it. Thirty-nine diagrams, each with its artifact. They are the evidence the comparison rules were derived from, so rewriting one needs operator confirmation.

The self-test runs over all of them, then over damaged copies of them, then over inputs that are broken on purpose. Sixty-three cases in total.

## Known gaps

- The rendered body of the SVG is not compared. The check reads the embedded diagram XML, not the shapes the exporter drew from it. The two come from the same model, so they cannot drift apart on their own, but a hand-edited SVG body would go unnoticed.
- The comparison covers the diagram and the page, not the export options. A diagram exported with a different border or a different font setting still compares equal, because those settings live in the export command and not in the file.
- The render script needs Docker and the pinned export image. A machine without them cannot regenerate an artifact, though it can still check one.
