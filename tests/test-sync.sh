#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:?Usage: test-sync.sh <skill-dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup
PROJ_DIR=$(bash "$SCRIPT_DIR/fixtures/setup-fixtures.sh" "" "$SKILL_DIR" | tail -1)
trap "rm -rf '$PROJ_DIR'" EXIT
cd "$PROJ_DIR"

# Run sync
python3 .pm/scripts/sync-project-data.py > /dev/null

# Verify output file exists
[ -f .pm/project-data.json ] || { echo "FAIL: project-data.json not created"; exit 1; }

# Verify JSON is valid and contains expected data
python3 << 'EOF'
import json, sys

d = json.load(open(".pm/project-data.json"))

errors = []

# Project basics
if d.get("project_name") != "Notification System": errors.append(f"project_name: expected 'Notification System', got '{d.get('project_name')}'")
if d.get("phase") != 3: errors.append(f"phase: expected 3, got {d.get('phase')}")
if d.get("language") != "en": errors.append(f"language: expected 'en', got '{d.get('language')}'")

# Requirements
reqs = d.get("requirements", [])
if len(reqs) != 5: errors.append(f"requirements count: expected 5, got {len(reqs)}")
req_ids = [r["id"] for r in reqs]
for expected in ["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"]:
    if expected not in req_ids: errors.append(f"missing requirement: {expected}")

# Check REQ-005 has needs-decision status
req5 = next((r for r in reqs if r["id"] == "REQ-005"), None)
if req5 and req5.get("status") != "needs-decision": errors.append(f"REQ-005 status: expected 'needs-decision', got '{req5.get('status')}'")

# Metrics
m = d.get("metrics", {})
if m.get("total_reqs") != 5: errors.append(f"total_reqs: expected 5, got {m.get('total_reqs')}")
if m.get("total_tasks") != 4: errors.append(f"total_tasks: expected 4, got {m.get('total_tasks')}")
if m.get("done_tasks") != 1: errors.append(f"done_tasks: expected 1, got {m.get('done_tasks')}")
if m.get("active_tasks") != 1: errors.append(f"active_tasks: expected 1, got {m.get('active_tasks')}")
if m.get("blocked") != 1: errors.append(f"blocked: expected 1, got {m.get('blocked')}")
if m.get("pct") != 25: errors.append(f"pct: expected 25, got {m.get('pct')}")
if m.get("personas") != 2: errors.append(f"personas: expected 2, got {m.get('personas')}")
if m.get("stories") != 2: errors.append(f"stories: expected 2, got {m.get('stories')}")

# Tasks
tasks = d.get("tasks", [])
if len(tasks) != 4: errors.append(f"tasks count: expected 4, got {len(tasks)}")
t001 = next((t for t in tasks if t["id"] == "001"), None)
if t001 and t001.get("status") != "closed": errors.append(f"task 001 status: expected 'closed', got '{t001.get('status')}'")
t002 = next((t for t in tasks if t["id"] == "002"), None)
if t002 and t002.get("status") != "in-progress": errors.append(f"task 002 status: expected 'in-progress', got '{t002.get('status')}'")
t004 = next((t for t in tasks if t["id"] == "004"), None)
if t004 and t004.get("depends_on") != "002, 003": errors.append(f"task 004 depends_on: expected '002, 003', got '{t004.get('depends_on')}'")

# PRD
prd = d.get("prd")
if not prd: errors.append("prd: missing")
elif not prd.get("exists"): errors.append("prd.exists: expected True")
elif prd.get("status") != "draft": errors.append(f"prd.status: expected 'draft', got '{prd.get('status')}'")

# PRD features
pf = d.get("prd_features", [])
if len(pf) != 5: errors.append(f"prd_features: expected 5, got {len(pf)}")

# Personas
personas = d.get("personas", [])
if len(personas) != 2: errors.append(f"personas count: expected 2, got {len(personas)}")

# Stories
stories = d.get("stories", [])
if len(stories) != 2: errors.append(f"stories count: expected 2, got {len(stories)}")

# Epics
epics = d.get("epics", [])
if len(epics) != 1: errors.append(f"epics count: expected 1, got {len(epics)}")

# Sign-off
signoff = d.get("signoff", [])
if len(signoff) != 1: errors.append(f"signoff count: expected 1, got {len(signoff)}")

# Deliverables
deliverables = d.get("deliverables", [])
if len(deliverables) != 3: errors.append(f"deliverables count: expected 3, got {len(deliverables)}")

# Ingestions
ingestions = d.get("ingestions", [])
if len(ingestions) != 1: errors.append(f"ingestions count: expected 1, got {len(ingestions)}")

# Meetings
meetings = d.get("meetings", [])
if len(meetings) != 1: errors.append(f"meetings count: expected 1, got {len(meetings)}")

# Audit
audit = d.get("audit", [])
if len(audit) != 5: errors.append(f"audit count: expected 5, got {len(audit)}")

# Context
decisions = d.get("decisions", [])
if len(decisions) != 3: errors.append(f"decisions count: expected 3, got {len(decisions)}")
questions = d.get("questions", [])
if len(questions) != 2: errors.append(f"questions count: expected 2, got {len(questions)}")

# Traceability
trace = d.get("traceability", [])
if len(trace) != 4: errors.append(f"traceability count: expected 4, got {len(trace)}")

# Strategy files
sf = d.get("strategy_files", [])
if len(sf) != 2: errors.append(f"strategy_files: expected 2, got {len(sf)}")

if errors:
    for e in errors: print(f"  FAIL: {e}")
    sys.exit(1)
EOF
