#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "${1:?Usage: test-update-project-data.sh <skill-dir>}" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup temp dir with the script
PROJ_DIR=$(mktemp -d)
trap "rm -rf '$PROJ_DIR'" EXIT
cd "$PROJ_DIR"
mkdir -p .pm/scripts
cp "$SKILL_DIR/references/scripts/update-project-data.py" .pm/scripts/

# Test 1: init
python3 .pm/scripts/update-project-data.py init "Test Project" "en" > /dev/null
[ -f .pm/project-data.json ] || { echo "FAIL: init didn't create project-data.json"; exit 1; }

# Test 2: Verify init structure
python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
errors = []
if d.get("project_name") != "Test Project": errors.append(f"project_name: {d.get('project_name')}")
if d.get("language") != "en": errors.append(f"language: {d.get('language')}")
if d.get("phase") != 0: errors.append(f"phase: {d.get('phase')}")
if d.get("_version") != "2.0": errors.append(f"version: {d.get('_version')}")
if not isinstance(d.get("requirements"), list): errors.append("requirements not a list")
if not isinstance(d.get("tasks"), list): errors.append("tasks not a list")
if d.get("metrics", {}).get("total_reqs") != 0: errors.append("total_reqs not 0")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
EOF

# Test 3: append requirements
python3 .pm/scripts/update-project-data.py append 'requirements' '{"id":"REQ-001","title":"Auth","status":"active","priority":"High","source":"SRS"}' > /dev/null
python3 .pm/scripts/update-project-data.py append 'requirements' '{"id":"REQ-002","title":"Tasks","status":"active","priority":"High","source":"SRS"}' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
if d["metrics"]["total_reqs"] != 2:
    print(f"FAIL: total_reqs expected 2, got {d['metrics']['total_reqs']}")
    sys.exit(1)
if len(d["requirements"]) != 2:
    print(f"FAIL: requirements count expected 2, got {len(d['requirements'])}")
    sys.exit(1)
EOF

# Test 4: set scalar
python3 .pm/scripts/update-project-data.py set 'phase' '2' > /dev/null
python3 .pm/scripts/update-project-data.py set 'phase_name' 'Document' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
if d["phase"] != 2:
    print(f"FAIL: phase expected 2, got {d['phase']}")
    sys.exit(1)
if d["phase_name"] != "Document":
    print(f"FAIL: phase_name expected Document, got {d['phase_name']}")
    sys.exit(1)
EOF

# Test 5: merge PRD
python3 .pm/scripts/update-project-data.py merge 'prd' '{"exists":true,"status":"draft","created":"2026-04-01","requirements":["REQ-001","REQ-002"]}' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
prd = d.get("prd", {})
if not prd.get("exists"):
    print("FAIL: prd.exists not true")
    sys.exit(1)
if prd.get("status") != "draft":
    print(f"FAIL: prd.status expected draft, got {prd.get('status')}")
    sys.exit(1)
if len(prd.get("requirements", [])) != 2:
    print(f"FAIL: prd.requirements expected 2, got {len(prd.get('requirements', []))}")
    sys.exit(1)
EOF

# Test 6: replace array
python3 .pm/scripts/update-project-data.py replace 'tasks' '[{"id":"001","name":"DB Setup","status":"closed"},{"id":"002","name":"Push Service","status":"in-progress"},{"id":"003","name":"Email","status":"open"}]' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
if d["metrics"]["total_tasks"] != 3:
    print(f"FAIL: total_tasks expected 3, got {d['metrics']['total_tasks']}")
    sys.exit(1)
if d["metrics"]["done_tasks"] != 1:
    print(f"FAIL: done_tasks expected 1, got {d['metrics']['done_tasks']}")
    sys.exit(1)
if d["metrics"]["active_tasks"] != 1:
    print(f"FAIL: active_tasks expected 1, got {d['metrics']['active_tasks']}")
    sys.exit(1)
if d["metrics"]["pct"] != 33:
    print(f"FAIL: pct expected 33, got {d['metrics']['pct']}")
    sys.exit(1)
EOF

# Test 7: update-task
python3 .pm/scripts/update-project-data.py update-task '002' '{"status":"completed","completed":"2026-04-01"}' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
t002 = next((t for t in d["tasks"] if t["id"] == "002"), None)
if not t002 or t002["status"] != "completed":
    print(f"FAIL: task 002 status expected completed, got {t002.get('status') if t002 else 'missing'}")
    sys.exit(1)
if d["metrics"]["done_tasks"] != 2:
    print(f"FAIL: done_tasks expected 2 after update, got {d['metrics']['done_tasks']}")
    sys.exit(1)
EOF

# Test 8: stories + link-stories
python3 .pm/scripts/update-project-data.py replace 'stories' '[{"id":"us-001","name":"DB Story","status":"open","epic":"test","task":"001"},{"id":"us-002","name":"Push Story","status":"open","epic":"test","task":"002"},{"id":"us-003","name":"Email Story","status":"open","epic":"test","task":"003"}]' > /dev/null
python3 .pm/scripts/update-project-data.py link-stories > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
errors = []
for t in d["tasks"]:
    if not t.get("story"):
        errors.append(f"task {t['id']} has no story after link-stories")
if d["metrics"]["orphan_tasks"] != 0:
    errors.append(f"orphan_tasks expected 0, got {d['metrics']['orphan_tasks']}")
if d["metrics"]["stories"] != 3:
    errors.append(f"stories metric expected 3, got {d['metrics']['stories']}")
t001 = next((t for t in d["tasks"] if t["id"] == "001"), None)
if t001 and t001.get("story") != "us-001":
    errors.append(f"task 001 story expected us-001, got {t001.get('story')}")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
EOF

# Test 9: append deliverables + update-deliverable
python3 .pm/scripts/update-project-data.py replace 'deliverables' '[{"id":"DT-001","name":"SRS","status":"Not Started"},{"id":"DT-002","name":"API Docs","status":"Not Started"}]' > /dev/null
python3 .pm/scripts/update-project-data.py update-deliverable 'DT-001' '{"status":"Approved"}' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
dt001 = next((x for x in d["deliverables"] if x["id"] == "DT-001"), None)
if not dt001 or dt001["status"] != "Approved":
    print(f"FAIL: DT-001 status expected Approved, got {dt001.get('status') if dt001 else 'missing'}")
    sys.exit(1)
if d["metrics"]["deliv_done"] != 1:
    print(f"FAIL: deliv_done expected 1, got {d['metrics']['deliv_done']}")
    sys.exit(1)
EOF

# Test 10: stdin input
echo '[{"id":"REQ-001","title":"Auth v2","status":"active"}]' | python3 .pm/scripts/update-project-data.py replace 'requirements' - > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
if d["metrics"]["total_reqs"] != 1:
    print(f"FAIL: total_reqs expected 1 after stdin replace, got {d['metrics']['total_reqs']}")
    sys.exit(1)
if d["requirements"][0]["title"] != "Auth v2":
    print(f"FAIL: req title expected 'Auth v2', got {d['requirements'][0].get('title')}")
    sys.exit(1)
EOF

# Test 11: signoff + update-signoff
python3 .pm/scripts/update-project-data.py append 'signoff' '{"name":"SRS","path":"specs/srs/srs.md","status":"draft","approved_by":"","approved_date":""}' > /dev/null
python3 .pm/scripts/update-project-data.py update-signoff 'specs/srs/srs.md' '{"status":"approved","approved_by":"Client","approved_date":"2026-04-01"}' > /dev/null

python3 << 'EOF'
import json, sys
d = json.load(open(".pm/project-data.json"))
srs = next((s for s in d["signoff"] if s["path"] == "specs/srs/srs.md"), None)
if not srs or srs["status"] != "approved":
    print(f"FAIL: SRS signoff status expected approved")
    sys.exit(1)
if d["metrics"]["signoff_approved"] != 1:
    print(f"FAIL: signoff_approved expected 1, got {d['metrics']['signoff_approved']}")
    sys.exit(1)
EOF

echo "ALL TESTS PASSED"
