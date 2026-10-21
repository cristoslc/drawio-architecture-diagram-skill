# Developer workflows

## Build

There is no build. The skill bundle is plain Markdown, Python and bash, and it is read as it sits in the repository.

```bash
bash scripts/test.sh
```

## Test

`bash scripts/test.sh` is the whole gate. It runs the validator's self-test over the fixture diagrams and over deliberately damaged copies of them, checks the committed example artifact against its source, and renders every Mermaid diagram this repository ships.

The render path needs Docker. It pulls a pinned image on first use and renders a diagram:

```bash
bash skills/drawio-architecture-diagram/scripts/render-drawio-svg.sh \
  examples/order-intake.drawio examples/order-intake.drawio.svg
```

The path to the render script is relative to the skill directory. In a repository that vendored the skill into `.opencode/skills/drawio-architecture-diagram/`, it is `.opencode/skills/drawio-architecture-diagram/scripts/render-drawio-svg.sh`.

The Mermaid check needs `mmdc` on the PATH. It renders each inline diagram to a temporary SVG and fails the run on a parse error. It proves the diagram parses, not that it reads well.

## Branch and commit

Work on a branch. A change to a diagram changes its source and its artifact in the same commit, because the gate compares them.

## Release

Tag the repository. A consumer vendors the skill directory into their own repository, so a tag is what they pin.
