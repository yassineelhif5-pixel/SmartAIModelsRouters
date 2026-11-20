#!/usr/bin/env bash
set -Eeuo pipefail
HOSTS="claude,codex,gemini,copilot"
while (($#)); do
  case "$1" in
    --hosts) [[ $# -ge 2 ]] || { echo "Missing --hosts value" >&2; exit 2; }; HOSTS="$2"; shift 2 ;;
    -h|--help) echo "Usage: bash scripts/install-hif-skills.sh [--hosts claude,codex,gemini,copilot]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
OLD_IFS="$IFS"
IFS=','
read -r -a HOST_LIST <<< "$HOSTS"
IFS="$OLD_IFS"
for raw_host in "${HOST_LIST[@]}"; do
  host="$(printf '%s' "$raw_host" | tr '[:upper:]' '[:lower:]' | xargs)"
  case "$host" in
    claude) DEST_ROOT="$HOME/.claude/skills" ;;
    codex) DEST_ROOT="$HOME/.agents/skills" ;;
    gemini) DEST_ROOT="$HOME/.gemini/skills" ;;
    copilot) DEST_ROOT="$HOME/.copilot/skills" ;;
    *) echo "Unsupported host: $host" >&2; exit 2 ;;
  esac
  mkdir -p "$DEST_ROOT"
  for skill in hif hifnode; do
    SOURCE="$REPO_ROOT/skills/$skill"
    TARGET="$DEST_ROOT/$skill"
    [[ -f "$SOURCE/SKILL.md" ]] || { echo "Missing $SOURCE/SKILL.md" >&2; exit 1; }
    if [[ -e "$TARGET" ]]; then
      BACKUP="$TARGET.backup.$TIMESTAMP"
      mv "$TARGET" "$BACKUP"
      echo "Backed up existing $host/$skill to $BACKUP"
    fi
    cp -a "$SOURCE" "$TARGET"
    echo "Installed $host/$skill => $TARGET"
  done
done
echo
echo "HIF skill instructions installed for: $HOSTS"
echo "Start a new assistant session to load the skills."
echo "NOTE: This installs skill instructions only, not the HIF orchestration backend or MCP gateway."
