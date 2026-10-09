#!/bin/bash
# SessionStart hook for Claude Code cloud (remote) sessions only.
# Installs the Python dependencies listed in requirements.txt.
# Idempotent: pip skips packages that are already satisfied.
set -euo pipefail

# Only run in remote/cloud sessions; local sessions are left alone.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR"

if [ ! -f requirements.txt ]; then
  exit 0
fi

python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt
