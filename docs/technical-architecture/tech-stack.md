# Tech stack

| Piece | Choice | Why |
|---|---|---|
| Skill bundle | Agent Skills format, a `SKILL.md` with YAML frontmatter | read by every agent harness without a plugin |
| Validator | Python 3 standard library | no dependencies, so the gate runs anywhere a checkout exists |
| Render script | POSIX bash | it shells out to a container and to Python, and needs nothing else |
| Export | the draw.io desktop CLI inside `rlespinasse/drawio-export:v4.60.0` | the only headless route to an SVG with the diagram XML embedded, pinned so the output is reproducible |
| Fixtures | draw.io XML and the exporter's own SVG output | the evidence the comparison rules were derived from |

Nothing in the toolchain needs an account, a key or a network call at validation time. The render needs Docker and pulls the export image once.
