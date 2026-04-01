#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:?Usage: test-standup.sh <skill-dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup
PROJ_DIR=$(bash "$SCRIPT_DIR/fixtures/setup-fixtures.sh" "" "$SKILL_DIR" | tail -1)
trap "rm -rf '$PROJ_DIR'" EXIT
cd "$PROJ_DIR"

# Run standup
OUTPUT=$(bash .pm/scripts/standup.sh 2>&1)

# Verify output
echo "$OUTPUT" | grep -q "Standup" || { echo "FAIL: Missing Standup header"; exit 1; }
echo "$OUTPUT" | grep -q "Phase:" || { echo "FAIL: Missing Phase"; exit 1; }
echo "$OUTPUT" | grep -q "Done" || { echo "FAIL: Missing Done section"; exit 1; }
echo "$OUTPUT" | grep -q "Blocked" || { echo "FAIL: Missing Blocked section"; exit 1; }
echo "$OUTPUT" | grep -q "Next" || { echo "FAIL: Missing Next section"; exit 1; }

# Verify standup file was created
[ -f .pm/standup.md ] || { echo "FAIL: standup.md not created"; exit 1; }
