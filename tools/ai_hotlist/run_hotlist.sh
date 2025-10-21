#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Use system python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3.8+" >&2
  exit 1
fi

# Install deps
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# Run
python3 -m tools.ai_hotlist.main "$@"
