# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The `drawio-architecture-diagram` skill: it authors draw.io XML under a pinned house style and ships the diagram as a committed `.drawio.svg` that renders inline in Markdown and reopens editable in draw.io.
- The house style reference, which pins the palette, the type scale, the spacing and the edge rules.
- The XML rules reference, which pins the file format, the cell model and the style strings.
- The render script, which runs the draw.io desktop CLI in a pinned container and writes the artifact with the diagram XML embedded.
- The validator, which compares a committed artifact against its source and fails the build when they drift apart, plus a self-test over thirty-nine fixture diagrams and the damaged copies of them.
- A Mermaid check in the gate, which renders every inline diagram this repository ships.
- A contributor spoke for agents, under `docs/agents-detail/`.

### Fixed

- The skill's own commands named paths that only resolved in this repository. They are relative to the skill directory now, so a consumer who vendored the bundle can run them.
- The house style and the worked example disagreed about the spacing, and the reference described a parent-child relationship the example does not use. The reference now states what the example measures, and the container style carries the font family the type rule promises.
