# Plan: First release

**Date:** 2026-10-21
**Outcome:** a skill that draws an architecture diagram and ships it as a committed artifact the reader can edit

## Steps

1. Write the skill prose: the workflow in order, and the rules that carry the most weight.
2. Pin the house style: the palette, the type scale, the spacing, the container treatment and the edge rules, in one reference.
3. Pin the file format: the XML rules, the cell model and the style strings, in a second reference.
4. Bring the render script and the validator across from the survey that produced them, and adapt the validator to take a directory instead of a repository root.
5. Move the fixture corpus with them, so the comparison rules stay backed by evidence.
6. Draw the worked example with the style reference and commit the source and the artifact.
7. Write the decision record, the coverage matrix and the test gate.
8. Publish.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| The style reference is wrong and every diagram inherits the mistake | the example under `examples/` is drawn with it and is checked by eye |
| The validator is adapted and breaks a rule | the self-test over the fixtures and the damaged copies runs on every build |
| A consumer vendors the skill and the validator cannot find its fixtures | the self-test is a repository-level check, and the fixture lookup searches three locations and takes an environment override |
| The export is not reproducible | the export image is pinned by tag, and the render script fails loud rather than writing a broken artifact |

## Outcome

The skill, the two references, the two scripts, the fixture corpus, the worked example and the decision record are in place, and the gate is green. Two review rounds ran against the branch; every blocking finding they raised is fixed, and the fixes are in the history.

Two things changed the plan as it was written.

The example was redrawn against the style reference rather than carried over as it was. The reference and the example disagreed about the spacing, and a contract that its own worked example violates is not a contract. The reference now states the ranges the example measures.

The skill's commands are relative to the skill directory. The first version named paths that only resolved in this repository, which would have broken every consumer who copied the bundle. The repository's own paths are still in the developer workflow document, where a reader stands at the repository root.

## Deferred

- A house style drawn from a set of real diagrams rather than from a survey of existing skills.
- Dark-mode styling. The artifact paints a white canvas, so it reads on a dark page, but the diagram does not adapt its palette to the page.
