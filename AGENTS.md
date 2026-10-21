# AGENTS.md — drawio-architecture-diagram-skill

This project holds the `drawio-architecture-diagram` agent skill: it authors professional architecture diagrams as draw.io XML and ships them as a committed `.drawio.svg` that renders inline in Markdown and still opens editable in draw.io. Read `PURPOSE.md` for the one-paragraph intent.

## Scope guard (project-defining constraint)

`skills/drawio-architecture-diagram/SKILL.md` states a workflow and a house style. It names no vendor service, no cloud provider, and no agent harness. The skill teaches how to draw an architecture diagram that reads, and how to ship it so a reader can fix it. Facts about any specific cloud, any specific drawing tool's internals, or any specific harness belong in that system's own docs, never here. The style reference names draw.io style attributes because the skill writes draw.io XML, and that is the one tool whose file format the skill commits to. The skill names the infrastructure-as-code formats it scans for, because the Analyse mode has to know what to look for, but it carries no catalogue of cloud services, no resource types, and no API details.

## The single source of truth: prose and scripts

The rule the skill enforces on a diagram is the rule this repository enforces on itself: the committed `.drawio.svg` and the `.drawio` source must agree, and a stale artifact fails the build. `skills/drawio-architecture-diagram/scripts/validate-drawio-svg.py` is the authority on that comparison. The skill prose points at the script rather than restating the comparison's rules, and the script's own docstring states the rules it follows.

## The style reference is the contract

`skills/drawio-architecture-diagram/references/house-style.md` pins the palette, the type scale, the spacing and the edge rules. `skills/drawio-architecture-diagram/references/xml-rules.md` pins the file format. The example diagram under `examples/` was drawn with those references and is checked against them by eye. When a rule changes, the reference, the example and the skill prose change in the same commit.

## Project structure

- `skills/drawio-architecture-diagram/SKILL.md` — the skill definition, the primary artifact
- `skills/drawio-architecture-diagram/references/` — house style and XML rules
- `skills/drawio-architecture-diagram/scripts/` — render script and validator
- `examples/` — the worked example, source and committed artifact
- `tests/fixtures/` — the diagrams the exporter's behaviour was measured on
- `docs/` — decisions, plans, retrospectives

## Test command

```bash
bash scripts/test.sh
```

Runs the validator's self-test over the fixture diagrams and over deliberately damaged copies, checks the committed example artifact against its source, and renders every Mermaid diagram in this repository. It is the whole gate.

## Test coverage matrix

Master coverage matrix: `docs/test-coverage-matrix.md`

## Intent mode additions

- Deleting or rewriting a committed fixture under `tests/fixtures/` requires operator confirmation. The fixtures are evidence of what the exporter does.
