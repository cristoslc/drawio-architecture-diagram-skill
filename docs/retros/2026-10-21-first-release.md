---
title: "Retro: the drawio architecture diagram skill, first release"
period: "2026-10-21 — 2026-10-21"
created: 2026-10-21
scope: "The build of the skill repository, from an empty directory to a green gate and a reviewable tree."
parleyed: false
---

# Retro: the drawio architecture diagram skill, first release

## Period

2026-10-21 — 2026-10-21

## Scope

The build of a new repository holding one agent skill: it authors architecture diagrams as draw.io XML and ships each diagram as a committed `.drawio.svg` that renders inline in Markdown and still opens editable in draw.io. Eight commits, from `ad95c8b` to `ecb404d`.

## What happened

The survey that motivated this repository had already answered the delivery question: a draw.io diagram can be committed as an SVG that carries its own XML, and a build gate can keep the artifact and its source in agreement. This repository turned that answer into something a team installs.

Most of the weight was in the validator and the fixtures. The validator compares a committed artifact against its source by reading both sides the way draw.io reads a diagram, because the exporter re-serialises the model and the two sides never match as text. Thirty-nine fixture diagrams and the artifact the real exporter produced for each of them are what pin those rules down.

Two review rounds ran against the tree. The first round found the skill's own commands pointed at paths that only resolved inside this repository, so the skill would have failed the moment anyone copied the bundle. It also found that the house style and the worked example disagreed about spacing, and that the XML rules described a parent-child relationship the example does not use. The second round confirmed every fix held and left four non-blocking items, all now fixed.

## What worked

- **Deriving the comparison's rules from renders, not from theory.** Every rule in the validator came from rendering a hand-built diagram through the pinned export image and diffing what came back. That is why the rules handle compressed sources, wrapper cells, defaulted attributes and alternate number notations without special cases in the prose.
- **Keeping the fixtures as committed evidence.** They are the corpus the rules were derived from, so a later change to the comparison has to justify itself against them. `tests/fixtures/` is the reason the validator is trustworthy rather than plausible.
- **Making the render reproducible.** The committed artifact is byte-identical to a fresh render through the pinned image, which is what lets the gate treat a difference as drift rather than as noise.
- **Letting the example be the contract's evidence.** When the review found the spacing table and the example disagreeing, the example won and the table was rewritten around what it measures. A style reference that its own worked example violates is not a reference.

## What didn't

- **The skill's commands were written from the repository's point of view.** Both the validate and render steps named `skills/drawio-architecture-diagram/scripts/...`, which is exactly the path a vendored copy does not have. The skill had to be corrected to skill-relative paths after the fact. A skill is read by an agent standing in a consumer's repository, and that is the position the commands should have been written from.
- **The first draft of the house style was written from a survey, not from a diagram.** It described a clean spacing table with no diagram behind it, so it drifted from the example the moment the example existed. The reference would have been easier to write from a drawn diagram in the first place.
- **The gate did not check the Mermaid diagrams the repository ships.** Three diagrams sat in `docs/` with nothing rendering them. A rule in the house style says every diagram is validated, and the repository broke its own rule until the check was added.
- **The first publication answer was the wrong question.** The repository was about to be published before anyone asked which namespace it should live in.

## What surfaced

- **A contract and its worked example have to be written together.** The style reference and the example were produced separately and disagreed. The house rule that fixes this, that a rule change moves the reference, the example and the artifact in one commit, is now in `AGENTS.md`.
- **The fixture corpus does not travel with the bundle.** A vendored copy of the skill runs the validator against its own diagrams, which is the job it has to do, and the self-test stays a repository-level check. The earlier claim that the bundle was self-contained was false, and the reviewer's reproduction of that made the fix unavoidable rather than optional.
- **The GitHub rendering claim is the weakest link in the evidence chain.** The vendor documents that the diagram XML lives in the SVG's `content` attribute, but the claim that GitHub renders such a file inline rests on a community extension's README. ADR 0001 records this as the first thing to check after publication.

## Next actions

- Publish the repository under the namespace the operator names, then check the inline rendering on GitHub and close the ADR's "Worse" note with what the live page shows.
- Add the skill to the operator's plugin marketplace once the repository is public, the way `image-convergence-skill` and the other skills are listed.
- Draw a second diagram with the house style. The first one was redrawn to fit the reference, which is not the same as a diagram drawn with the reference from the start, and the difference is where the reference's rules will show what they get wrong.
