#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/../.claude/skills/pm-workflow"
PASS=0; FAIL=0; ERRORS=""

echo "========================================"
echo "  PM Workflow — Test Suite"
echo "========================================"
echo ""

for test in "$SCRIPT_DIR"/test-*.sh; do
  name=$(basename "$test" .sh)
  echo -n "  $name ... "
  if output=$(bash "$test" "$SKILL_DIR" 2>&1); then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
    ERRORS="$ERRORS\n--- $name ---\n$output\n"
  fi
done

echo ""
echo "========================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "========================================"

if [ $FAIL -gt 0 ]; then
  echo -e "\nFailures:\n$ERRORS"
  exit 1
fi
