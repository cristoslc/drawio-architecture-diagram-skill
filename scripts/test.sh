#!/usr/bin/env bash
# The project's whole gate.
#
# Two checks:
#   1. the validator's own self-test, over the fixture diagrams and over
#      deliberately damaged copies, so the comparison keeps its rules;
#   2. the committed example artifact against its source, so a stale
#      artifact fails the build.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_SCRIPTS="${REPO_ROOT}/skills/drawio-architecture-diagram/scripts"

python3 "${SKILL_SCRIPTS}/validate-drawio-svg.py" --self-test

python3 "${SKILL_SCRIPTS}/validate-drawio-svg.py" "${REPO_ROOT}/examples"
