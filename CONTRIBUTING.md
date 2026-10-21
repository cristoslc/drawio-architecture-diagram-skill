# Contributing

This project ships one thing: a skill that draws architecture diagrams that read. Everything else supports it.

## The rule that matters

The committed `.drawio.svg` and its `.drawio` source must agree. `bash scripts/test.sh` is the whole gate and it fails when they drift apart. A pull request that changes a diagram changes both files in the same commit.

## Getting set up

The render script needs Docker and pulls a pinned image on first use. The validator needs Python 3 and nothing else.

```bash
git clone git@github.com:cristoslc/drawio-architecture-diagram-skill.git
cd drawio-architecture-diagram-skill
bash scripts/test.sh
```

## Making a change

- **The skill prose** (`skills/drawio-architecture-diagram/SKILL.md`) states the workflow. Change it when the workflow changes, and change the references it points at in the same commit.
- **A reference** (`skills/drawio-architecture-diagram/references/`) pins a rule. When a rule changes, the example under `examples/` changes with it, because the example is drawn with those rules.
- **A script** (`skills/drawio-architecture-diagram/scripts/`) is behaviour. A change needs a test, and the fixtures under `tests/fixtures/` are the evidence the rules were derived from, so rewriting one needs operator confirmation.

## Style

- One logical line per paragraph. No hard wrapping.
- No em dashes.
- British spelling.

## Pull requests

- One logical change per pull request, with the problem stated before the solution.
- `bash scripts/test.sh` output pasted in the body, green.
- A `CHANGELOG.md` entry under Unreleased.
- A decision record in `docs/adr/` when a decision changes, not just when code does.
