# 0001: Ship the diagram as a committed .drawio.svg

**Date:** 2026-10-21
**Status:** accepted

## Context

A team writes architecture diagrams into Markdown documents that live in GitHub. Two facts shape the decision.

The first is what GitHub will render. Its Markdown pipeline passes an `img` element through and strips `iframe`, `script` and an inline `svg` element. So a diagram cannot be a live editor in the document. It has to be an image, or a link.

The second is what an image can carry. draw.io writes the diagram XML into the root `content` attribute of an exported SVG. The file renders as an image and reopens in draw.io with the diagram intact. A PNG cannot do that, because a PNG has nowhere to put an XML document.

The third fact is about the reader. A reader who spots a problem in a diagram should be able to fix it. A picture they cannot edit is a picture they can only complain about.

## Options considered

**Export a PNG and commit it.** The simplest thing that works. The reader gets a sharp picture. The reader cannot fix the diagram, and the source lives in a separate file that nobody opens.

**Serve the diagram from a rendering service.** A request goes out with the diagram in the URL and an image comes back. It works on any host that allows the request, and the artifact never has to be committed. Two things rule it out here. The whole diagram travels in the URL, compressed and base64 encoded, which puts it in every proxy log and every bookmark on the way. And the image that comes back carries no diagram XML, so the reader gets a picture and the editability is lost anyway.

**Link to a live editor in the document.** The best reading experience and the one the tooling is built for: the document holds an editor, the reader edits in place. GitHub strips the `iframe` this needs, so this cannot ship on the platform where the documents already live.

**Commit a `.drawio.svg`.** The document holds an ordinary image link. The file carries the diagram XML, so the reader who wants to change it downloads one file and opens it in draw.io. The source stays in the repository as plain XML and diffs cleanly.

## Decision

Commit a `.drawio.svg` beside its `.drawio` source, and keep both.

The pair travels together in one commit. A build compares the two, reading both the way draw.io reads a diagram, and fails when they have drifted apart. The comparison is what turns "regenerate the artifact when the source changes" from a habit into a build failure.

The skill owns the layout and pins a house style, because a diagram that is technically correct and visually inconsistent fails the reader in the same way a wrong diagram does.

## Consequences

**Good.** The reader gets a sharp picture that stays sharp on a retina screen, and a file they can edit if they need to. The maintainer gets a source that diffs cleanly and an artifact the build keeps honest. The delivery works on the platform the documents already live on, with no account, no key and no service.

**Bad.** Two files per diagram. The artifact must be regenerated when the source changes, which the build enforces rather than trusting. The render path needs Docker and a pinned export image, so a machine without them can check an artifact but not produce one.

**Worse.** The GitHub rendering claim rests on a community statement rather than the vendor's documentation, so it is the first thing to check when the repository is published. The style reference has one worked example behind it, the one in this repository, so the second real diagram drawn with the rules is the one that will show what they get wrong.
