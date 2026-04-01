#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:?Usage: test-search.sh <skill-dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup
PROJ_DIR=$(bash "$SCRIPT_DIR/fixtures/setup-fixtures.sh" "" "$SKILL_DIR" | tail -1)
trap "rm -rf '$PROJ_DIR'" EXIT
cd "$PROJ_DIR"

# Search for "push" — should find in requirements
OUTPUT=$(bash .pm/scripts/search.sh "push" 2>&1)
echo "$OUTPUT" | grep -q "requirements.md" || { echo "FAIL: search for 'push' didn't find requirements.md"; exit 1; }

# Search for "notification" — should find multiple files
OUTPUT=$(bash .pm/scripts/search.sh "notification" 2>&1)
echo "$OUTPUT" | grep -q "All artifacts" || { echo "FAIL: Missing artifacts section"; exit 1; }

# Search with no args should show usage
set +e
OUTPUT=$(bash .pm/scripts/search.sh 2>&1)
RC=$?
set -e
[ $RC -ne 0 ] || { echo "FAIL: search with no args should fail"; exit 1; }
echo "$OUTPUT" | grep -q "Usage" || { echo "FAIL: Missing usage message"; exit 1; }
