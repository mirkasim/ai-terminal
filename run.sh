#!/usr/bin/env bash
# Start ai-terminal. Any arguments are forwarded to the app.
#   ./run.sh "list all python files"   # one-shot
#   ./run.sh                            # interactive REPL
set -euo pipefail

cd "$(dirname "$0")"
exec uv run python main.py "$@"
