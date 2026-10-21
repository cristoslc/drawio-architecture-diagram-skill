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

The build of a new repository holding one agent skill: it authors architecture diagrams as draw.io XML and ships each diagram as a committed `.drawio.svg` that renders inline in Markdown and still opens editable in draw.io. Eleven commits, from `ad95c8b` to `3d1bc72`, then the publication and the checks that followed it.

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
- **The first publication answer was the wrong question.** The repository was about to be published before anyone asked which namespace it should live in. The question was eventually asked, and it went unanswered, so the publication followed the sibling-skill pattern into the operator's own account.

## What surfaced

- **A contract and its worked example have to be written together.** The style reference and the example were produced separately and disagreed. The house rule that fixes this, that a rule change moves the reference, the example and the artifact in one commit, is now in `AGENTS.md`.
- **The fixture corpus does not travel with the bundle.** A vendored copy of the skill runs the validator against its own diagrams, which is the job it has to do, and the self-test stays a repository-level check. The earlier claim that the bundle was self-contained was false, and the reviewer's reproduction of that made the fix unavoidable rather than optional.
- **The namespace question was asked and went unanswered.** The question went out with the operator's other questions and came back with no answer, so the publication went ahead on the pattern every sibling skill already follows: a public repository under the operator's own account, named after the skill. That is a guess with a cheap reversal, since a repository moves between accounts without anyone redoing the work.
- **The GitHub rendering claim was the weakest link in the evidence chain.** The vendor documents that the diagram XML lives in the SVG's `content` attribute, but the claim that GitHub renders such a file inline rested on a community extension's README. Both halves of the claim were checked against the published repository afterwards, and the checks are recorded below.

## Next actions

- Draw a second diagram with the house style. The first one was redrawn to fit the reference, which is not the same as a diagram drawn with the reference from the start, and the difference is where the reference's rules will show what they get wrong.
- Decide how the skill reaches the harnesses. The sibling skills are installed by copying a directory, and this one follows that pattern. The BB plugin marketplace is a different surface, for BB plugins distributed as npm packages, so the skill does not belong there without a different distribution decision.

## What was checked after publication

The repository is published at `github.com/cristoslc/drawio-architecture-diagram-skill`, public, with the GitHub remote named `gh` like its sibling skills.

Both halves of the delivery claim were then checked against the live repository rather than argued.

The rendering half: GitHub's Markdown pipeline turns the example's image link into an `img` element pointing at the file's raw route, that route answers `200` with the content type `image/svg+xml`, and a browser renders the response at its natural size with the diagram intact.

The editability half: handing the committed `.drawio.svg` to the draw.io desktop CLI, running in the pinned container, produces a render of the same diagram, so the CLI read the diagram out of the SVG's `content` attribute rather than out of the picture. Changing one label inside that attribute and rendering again produces a picture with the changed label.

The ADR's "Worse" note, which said the GitHub rendering claim was the first thing to check after publication, now records what the live repository showed. What is left open is not the delivery mechanism but the style reference, which still has only one diagram behind it.
