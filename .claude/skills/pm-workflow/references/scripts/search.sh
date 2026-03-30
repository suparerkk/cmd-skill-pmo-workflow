#!/usr/bin/env bash
# pm-workflow search — Search requirements and artifacts
# Usage: bash .pm/scripts/search.sh <query>

set -euo pipefail

PM_DIR="${PM_DIR:-.pm}"

if [[ $# -eq 0 ]]; then
  echo "Usage: bash .pm/scripts/search.sh <query>"
  exit 1
fi

QUERY="$1"
SPECS_DIR="specs"

echo "Searching for: $QUERY"
echo "========================================"
echo ""

# Search in requirements.md
if [[ -f "$SPECS_DIR/requirements.md" ]]; then
  echo "📄 requirements.md:"
  grep -i -n "$QUERY" "$SPECS_DIR/requirements.md" | head -5 || echo "  No matches"
  echo ""
fi

# Search in all markdown files under specs/
echo "📁 All artifacts:"
find "$SPECS_DIR" -name "*.md" -type f -exec grep -l -i "$QUERY" {} \; | head -10 || echo "  No matches"
echo ""

# Search audit log
if [[ -f "$PM_DIR/audit.log" ]]; then
  echo "📜 Audit log:"
  grep -i "$QUERY" "$PM_DIR/audit.log" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        print(f\"  [{d.get('phase','?')}] {d.get('skill','?')} → {', '.join(d.get('artifacts_created', []))}\")
    except: pass
  " | head -5 || echo "  No matches"
fi
