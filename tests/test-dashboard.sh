#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:?Usage: test-dashboard.sh <skill-dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup
PROJ_DIR=$(bash "$SCRIPT_DIR/fixtures/setup-fixtures.sh" "" "$SKILL_DIR" | tail -1)
SERVER_PID=""
trap 'kill $SERVER_PID 2>/dev/null || true; rm -rf "$PROJ_DIR"' EXIT
cd "$PROJ_DIR"

# Start dashboard on random port
PORT=$((9000 + RANDOM % 1000))
python3 .pm/scripts/dashboard-server.py --port $PORT &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Test HTML endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/")
[ "$HTTP_CODE" = "200" ] || { echo "FAIL: / returned $HTTP_CODE"; exit 1; }

# Test API endpoint
API_DATA=$(curl -s "http://localhost:$PORT/api/data")
echo "$API_DATA" | python3 -c "
import json, sys
d = json.load(sys.stdin)
errors = []
if d.get('project_name') != 'Notification System': errors.append('wrong project name')
if not d.get('requirements'): errors.append('no requirements')
if not d.get('tasks'): errors.append('no tasks')
if errors:
    for e in errors: print(f'FAIL: {e}')
    sys.exit(1)
"

# Test sync endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/api/sync")
[ "$HTTP_CODE" = "200" ] || { echo "FAIL: /api/sync returned $HTTP_CODE"; exit 1; }

# Verify tasks table has Story column and traceability has Story column
HTML=$(curl -s "http://localhost:$PORT/")
echo "$HTML" | grep -q '<th>Story</th>' || { echo "FAIL: Dashboard missing Story column"; exit 1; }

# Verify API data has story linkage on tasks
echo "$API_DATA" | python3 -c "
import json, sys
d = json.load(sys.stdin)
t002 = next((t for t in d.get('tasks',[]) if t['id']=='002'), None)
if not t002 or t002.get('story') != 'us-001':
    print(f'FAIL: task 002 story: expected us-001, got {t002.get(\"story\") if t002 else \"missing\"}')
    sys.exit(1)
tr = d.get('traceability', [])
tr002 = next((t for t in tr if t.get('task_id')=='002'), None)
if not tr002 or tr002.get('story') != 'us-001':
    print(f'FAIL: traceability 002 story: expected us-001, got {tr002.get(\"story\") if tr002 else \"missing\"}')
    sys.exit(1)
"

# Test 404
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/nonexistent")
[ "$HTTP_CODE" = "404" ] || { echo "FAIL: /nonexistent returned $HTTP_CODE, expected 404"; exit 1; }

kill $SERVER_PID 2>/dev/null || true
