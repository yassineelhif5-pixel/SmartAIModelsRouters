#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_BIN=""
for candidate in python3.12 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    version="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    major="${version%%.*}"
    minor="${version##*.}"
    if (( major > 3 || (major == 3 && minor >= 12) )); then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Python 3.12 or newer is required." >&2
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[providers]"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env. Add authorized provider model IDs and API keys."
fi

echo
echo "HIF runtime installed in $REPO_ROOT/.venv"
echo "Configure .env, then test with:"
echo "  .venv/bin/hif --help"
echo "  .venv/bin/hif mcp"
echo
echo "For user-wide Claude Code MCP registration:"
echo "  claude mcp add --scope user --transport stdio hif -- $REPO_ROOT/.venv/bin/hif-mcp"
echo "  claude mcp list"
echo
echo "Gemini CLI user-scope MCP registration:"
echo "  gemini mcp add --scope user hif $REPO_ROOT/.venv/bin/hif-mcp"
echo "  gemini mcp list"
echo
echo "OpenAI Codex MCP registration:"
echo "  codex mcp add hif -- $REPO_ROOT/.venv/bin/hif-mcp"
echo "  codex mcp list"
echo "NOTE: This does not install a Windows Service or expose a remote HTTP gateway."
