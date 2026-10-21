#!/usr/bin/env bash
# Render every Mermaid diagram this repository ships and fail on any error.
#
# The three diagrams in docs/ are inline fenced blocks, so there are no .mmd
# sources to render separately. Exit 0 means the diagram parsed and rendered;
# it does not mean the diagram reads well, which is a reviewer's job.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "FAIL: mmdc is not on PATH. Install @mermaid-js/mermaid-cli." >&2
  exit 127
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "FAIL: python3 is not on PATH." >&2
  exit 127
fi

exec python3 - "$REPO_ROOT" <<'PY'
import os
import re
import subprocess
import sys
import tempfile

root = sys.argv[1]
pattern = re.compile(r"^```mermaid[ \t]*$")

blocks = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [name for name in dirnames if name not in {".git", ".worktrees", "node_modules"}]
    for name in sorted(filenames):
        if not name.endswith(".md"):
            continue
        path = os.path.join(dirpath, name)
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        in_block = False
        body = []
        start_line = 0
        for number, line in enumerate(lines, start=1):
            if not in_block and pattern.match(line):
                in_block = True
                body = []
                start_line = number
                continue
            if in_block and line.strip() == "```":
                blocks.append((rel, start_line, "\n".join(body)))
                in_block = False
                continue
            if in_block:
                body.append(line)

failures = 0
checked = 0

with tempfile.TemporaryDirectory() as tmp:
    for rel, line_no, body in blocks:
        if not body.strip():
            print(f"FAIL  {rel}:{line_no} :: empty Mermaid block")
            failures += 1
            continue
        mmd = os.path.join(tmp, "diagram.mmd")
        svg = os.path.join(tmp, "diagram.svg")
        with open(mmd, "w", encoding="utf-8") as handle:
            handle.write(body)
        result = subprocess.run(["mmdc", "-i", mmd, "-o", svg], capture_output=True, text=True)
        if result.returncode == 0:
            checked += 1
            print(f"PASS  {rel}:{line_no}")
        else:
            failures += 1
            print(f"FAIL  {rel}:{line_no}")
            for line in result.stderr.strip().splitlines():
                print(f"      {line}")

total = checked + failures
print()
if failures:
    print(f"RESULT: {failures} of {total} Mermaid diagram(s) failed to render.")
    sys.exit(1)
print(f"RESULT: all {total} Mermaid diagram(s) rendered.")
PY
