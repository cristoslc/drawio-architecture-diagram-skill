#!/usr/bin/env bash
# Staging end-to-end check. The gate is the end-to-end check here: it
# renders a diagram from source and compares the artifact with that source.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${REPO_ROOT}/scripts/test.sh"
