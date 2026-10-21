#!/usr/bin/env bash
# Staging deploy. This project has no deployment pipeline: the skill is
# installed by copying its directory into a consumer repository, and the
# artifact it produces is a file the consumer commits.
set -euo pipefail

echo "Staging deploy: no deployment pipeline configured for this project."
echo "Branch: ${BRANCH:-$(git branch --show-current)}"
