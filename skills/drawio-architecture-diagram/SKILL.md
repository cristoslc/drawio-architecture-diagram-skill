---
name: drawio-architecture-diagram
description: "Author professional architecture diagrams as draw.io XML and ship them as a committed .drawio.svg that renders inline in Markdown and still opens editable in draw.io. Use this skill when the user asks for an architecture diagram, a service map, a system context picture, or wants infrastructure visualised from CloudFormation, CDK or Terraform. Skip it for a small diagram that belongs inside a paragraph, where Mermaid renders natively and keeps no artifact in sync."
license: MIT
compatibility: "Needs Docker for the render path. The validator needs Python 3 and nothing else."
metadata:
  short-description: Architecture diagrams as draw.io XML, shipped as an editable SVG
  author: cristoslc
  version: 1.0.0
---

# Draw.io architecture diagram

## What this skill produces

Two files, and always both of them:

| File | Who reads it | What it is |
|---|---|---|
| `<name>.drawio` | the maintainer | the source, plain XML, diffable in git |
| `<name>.drawio.svg` | the reader | the committed artifact, renders inline in Markdown, reopens in draw.io with the diagram intact |

The reader gets a picture. The maintainer gets a file they can edit. The SVG carries the diagram XML inside its root `content` attribute, so the artifact the repository ships is the artifact the reader can take away and change.

## When this skill is the wrong tool

- A small diagram that belongs inside a paragraph: write Mermaid. It renders natively in Markdown with no artifact to keep in sync.
- A diagram that has to survive somewhere SVG cannot be embedded, such as an email: export a PNG as well.

## The workflow, in order

Each step depends on the one before it. Skipping a step is how a diagram ends up technically valid and visually wrong.

### 1. Pick the mode

- **Analyse**: the infrastructure already exists in the repository. Scan for CloudFormation (`AWS::` templates), CDK (`cdk.json`, constructs) and Terraform (`resource "aws_*"`), then extract the services, the relationships and the network boundaries. Confirm the reading with the user before drawing.
- **Brainstorm**: the architecture is being designed. Ask what it must do, which parts talk to which, and where the trust boundaries sit, then propose the shape and draw it.

### 2. Apply the house style

Read `references/house-style.md` and follow it exactly. The palette, the type scale, the container treatment and the edge rules are pinned so that two diagrams made on different days look like the same product. A diagram that ignores the house style is a defect even when it is accurate.

### 3. Author the XML

Read `references/xml-rules.md` for the file format, the cell model and the style string anatomy. Author uncompressed `<mxfile>` XML with explicit coordinates for every shape and an explicit route for every edge that crosses a cluster. The agent owns the layout: nothing is left to an automatic arranger, because an automatic arranger picks the positions and the reader is the one who has to live with them.

A container is a band drawn behind the group it holds, not a draw.io parent, and every coordinate in the file is an absolute position on the canvas. `references/xml-rules.md` says why, and what a reader loses by it.

### 4. Validate

```bash
python3 scripts/validate-drawio-svg.py <directory holding the diagrams>
```

The check compares a committed `.drawio.svg` against its `.drawio` source and fails the build when they have drifted apart. It reads both sides the way draw.io reads a diagram, so a source that spells out a default attribute is not mistaken for a stale artifact.

The path `scripts/validate-drawio-svg.py` is relative to this skill's own directory. In a repository that holds the skill at `skills/drawio-architecture-diagram/`, that is `skills/drawio-architecture-diagram/scripts/validate-drawio-svg.py`. In a repository that vendored the skill into `.opencode/skills/drawio-architecture-diagram/`, it is `.opencode/skills/drawio-architecture-diagram/scripts/validate-drawio-svg.py`.

### 5. Render

```bash
bash scripts/render-drawio-svg.sh <source.drawio> <artifact.drawio.svg>
```

The render runs the draw.io desktop CLI inside a container and writes the SVG with the diagram XML embedded. It fails loudly and leaves the previous artifact untouched when it fails. The same relative-path rule applies: `scripts/render-drawio-svg.sh` sits beside this document.

### 6. Look at the render

Open the rendered SVG and actually look at it. A render that parses is not a render that reads. Check for the four failures that a validator cannot see: a label that overlaps another shape, an edge that runs through a shape, an arrowhead that lands on a title, and a label that reads backwards.

### 7. Correct

Fix the source, then render again. Loop until the render reads cleanly. A diagram that needs a reader to guess is not finished.

### 8. Commit both files

The source and the artifact travel together in one commit. The build compares them, so a stale artifact fails the gate rather than shipping.

## Rules that carry the most weight

- **Look at every render.** The validator checks structure. Only a reader's eye catches a collision.
- **Own the layout.** Place every shape and route every edge yourself. Never accept coordinates you did not choose.
- **Keep the cluster flat.** One level of grouping reads better than nesting.
- **Back every edge label.** A label with a background plate stays readable where it crosses a shape. The plate is pinned with the palette, so a diagram whose colours stop being pinned drops the plate with them.
- **Ship the editable artifact.** A PNG cannot be fixed by the reader who spots the problem. An SVG with the XML inside can.
- **Regenerate on every source change.** The gate will tell you if you forget.

## Where the details live

| Document | What it holds |
|---|---|
| `references/house-style.md` | the pinned palette, type scale, spacing, container treatment and edge rules |
| `references/xml-rules.md` | the file format, the cell model, and how to write a style string |
| `scripts/render-drawio-svg.sh` | renders a source into the committed artifact |
| `scripts/validate-drawio-svg.py` | compares a committed artifact against its source, and self-tests the comparison |

The worked example lives in the `examples/` directory of the repository that ships this skill, as a `.drawio` source beside its `.drawio.svg` artifact.
