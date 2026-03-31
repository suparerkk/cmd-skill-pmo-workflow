#!/bin/bash
# Install pm-workflow skill into current project
# Usage: cd /your/project && bash /path/to/skill-pm-workflow/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/.claude/skills/pm-workflow"
TARGET=".claude/skills/pm-workflow"

if [ ! -f "$SOURCE/SKILL.md" ]; then
  echo "Error: SKILL.md not found at $SOURCE"
  exit 1
fi

mkdir -p "$TARGET"
cp -r "$SOURCE/"* "$TARGET/"
echo "Installed pm-workflow to $TARGET"
echo "Restart Claude Code, then type /pm-workflow to verify."
