#!/usr/bin/env bash
# pm-workflow status — Deterministic project status report
# Usage: bash .pm/scripts/status.sh

set -euo pipefail

PM_DIR="${PM_DIR:-.pm}"
STATE="$PM_DIR/state.json"
AUDIT="$PM_DIR/audit.log"

if [[ ! -f "$STATE" ]]; then
  echo "Error: .pm/state.json not found. Run /pm-workflow init first."
  exit 1
fi

# Extract current state
PHASE=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('phase', 0))")
PHASE_NAME=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('phase_name', 'Unknown'))")
CURRENT=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('current_skill', 'none'))")
COMPLETED=$(python3 -c "import json; d=json.load(open('$STATE')); print(len(d.get('completed_skills', [])))")
TOTAL=$(python3 -c "
import json
d=json.load(open('$STATE'))
skills = d.get('completed_skills', [])
print(len(skills))
")
BLOCKED=$(python3 -c "
import json
d=json.load(open('$STATE'))
blocked = d.get('blocked', [])
print(len(blocked))
")

# Phase names
PHASE_NAMES=("Setup" "Discovery" "Strategy" "PRD Development" "Validation" "Delivery")

echo "========================================"
echo "  Project Status"
echo "========================================"
echo ""
echo "  Phase:       ${PHASE} — ${PHASE_NAME}"
echo "  Current:     ${CURRENT}"
echo "  Completed:   ${COMPLETED} skills"
echo "  Blocked:     ${BLOCKED} items"
echo ""

# Show completed skills by phase
if [[ -f "$AUDIT" ]]; then
  echo "  Recent activity:"
  tail -5 "$AUDIT" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        print(f\"    [{d.get('phase','?')}] {d.get('skill','?')} → {', '.join(d.get('artifacts_created', []))}\")
    except: pass
  "
fi

echo ""
echo "========================================"
