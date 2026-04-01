#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:?Usage: test-report.sh <skill-dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup
PROJ_DIR=$(bash "$SCRIPT_DIR/fixtures/setup-fixtures.sh" "" "$SKILL_DIR" | tail -1)
trap "rm -rf '$PROJ_DIR'" EXIT
cd "$PROJ_DIR"

# Run report generator
python3 .pm/scripts/generate-report.py > /dev/null 2>&1

# Check if report was generated (XLSX or CSV)
if python3 -c "import openpyxl" 2>/dev/null; then
  # XLSX should exist
  XLSX=$(find specs/reports -name "*.xlsx" 2>/dev/null | head -1)
  [ -n "$XLSX" ] || { echo "FAIL: No XLSX file generated"; exit 1; }

  # Validate XLSX has 15 sheets
  python3 << PYEOF
import sys
from openpyxl import load_workbook
import glob

xlsx = glob.glob("specs/reports/*.xlsx")[0]
wb = load_workbook(xlsx)
sheets = wb.sheetnames
if len(sheets) != 15:
    print(f"FAIL: Expected 15 sheets, got {len(sheets)}: {sheets}")
    sys.exit(1)

expected = ["Dashboard", "Requirements", "PRD Summary", "Personas", "Discovery & Strategy",
            "User Stories", "Epic & Tasks", "Timeline", "Deliverables", "Sign-Off Status",
            "Risks & Blockers", "Traceability", "Ingestion Log", "Meeting Prep", "Activity Log"]
for e in expected:
    if e not in sheets:
        print(f"FAIL: Missing sheet '{e}'. Got: {sheets}")
        sys.exit(1)

# Verify Epic & Tasks sheet has Story column
ws_tasks = wb["Epic & Tasks"]
task_headers = [cell.value for cell in ws_tasks[4] if cell.value]
if "STORY" not in task_headers:
    print(f"FAIL: Epic & Tasks missing STORY column. Headers: {task_headers}")
    sys.exit(1)

# Verify Traceability sheet has Story column
ws_trace = wb["Traceability"]
trace_headers = [cell.value for cell in ws_trace[4] if cell.value]
if "STORY" not in trace_headers:
    print(f"FAIL: Traceability missing STORY column. Headers: {trace_headers}")
    sys.exit(1)
PYEOF
else
  # CSV fallback
  [ -f specs/reports/requirements.csv ] || { echo "FAIL: CSV fallback not created"; exit 1; }
  [ -f specs/reports/tasks.csv ] || { echo "FAIL: tasks.csv not created"; exit 1; }
fi
