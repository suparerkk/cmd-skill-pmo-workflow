#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:?Usage: test-status.sh <skill-dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup
PROJ_DIR=$(bash "$SCRIPT_DIR/fixtures/setup-fixtures.sh" "" "$SKILL_DIR" | tail -1)
trap "rm -rf '$PROJ_DIR'" EXIT
cd "$PROJ_DIR"

# Run status
OUTPUT=$(bash .pm/scripts/status.sh 2>&1)

# Verify output contains expected info
echo "$OUTPUT" | grep -q "Phase:" || { echo "FAIL: Missing Phase in output"; exit 1; }
echo "$OUTPUT" | grep -q "3" || { echo "FAIL: Phase number not shown"; exit 1; }
echo "$OUTPUT" | grep -q "Plan" || { echo "FAIL: Phase name not shown"; exit 1; }
echo "$OUTPUT" | grep -q "Completed:" || { echo "FAIL: Missing Completed in output"; exit 1; }
echo "$OUTPUT" | grep -q "Blocked:" || { echo "FAIL: Missing Blocked in output"; exit 1; }
echo "$OUTPUT" | grep -q "Recent activity:" || { echo "FAIL: Missing recent activity"; exit 1; }
