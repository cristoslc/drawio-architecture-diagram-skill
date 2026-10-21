# Contribution guidelines (agents)

- Read `AGENTS.md` (hub) first: the scope guard, the style reference as a contract, and the test command.
- Run `bash scripts/test.sh` before every pull request. Green is a precondition.
- A change to a house style rule changes the reference, the example under `examples/` and the example's committed artifact in the same commit, because the example is drawn with those rules.
- A change to the skill's workflow changes `SKILL.md` and the reference it points at in the same commit.
- A change to a script changes its behaviour and the fixtures that cover it. The fixtures are the evidence the comparison's rules were derived from, so rewriting one needs operator confirmation.
- Fixes arrive with reproduction steps and a failing test written first.
- Worktrees live under `.worktrees/`, and the project root stays on `main`.
- Every pull request adds a `CHANGELOG.md` entry under Unreleased.
