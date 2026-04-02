#!/usr/bin/env python3
"""
Recovery/rebuild tool. During normal workflow, project-data.json is updated
directly by each phase via update-project-data.py. Use this script to rebuild
from scratch or verify data integrity.

Usage:
  python3 .pm/scripts/sync-project-data.py           # Full rebuild
  python3 .pm/scripts/sync-project-data.py --verify   # Compare only
"""

import json, re, os, sys, glob
from datetime import datetime

OUTPUT = ".pm/project-data.json"

# ============================================================
# Readers
# ============================================================

def read_file(path):
    try:
        with open(path, "r") as f: return f.read()
    except FileNotFoundError: return ""

def read_json(path):
    try:
        with open(path, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def parse_frontmatter(content):
    """Parse flat YAML-like frontmatter between --- delimiters."""
    lines = content.split("\n")
    start = end = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if start == -1: start = i
            elif end == -1: end = i; break
    if start == -1 or end == -1 or end <= start + 1: return {}
    fm = {}
    for line in lines[start+1:end]:
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            fm[key] = val
    return fm

def parse_bold_fields(text):
    """Extract **Key:** Value pairs from markdown text."""
    fields = {}
    for line in text.split("\n"):
        m = re.match(r"\*\*(\w[\w\s&/]*):\*\*\s*(.*)", line)
        if m: fields[m.group(1).strip().lower()] = m.group(2).strip()
    return fields

def parse_markdown_table(content, header_match):
    """Parse a markdown table by matching a header string. Returns list of dicts."""
    rows, headers = [], []
    in_table = header_seen = False
    for line in content.split("\n"):
        if header_match.lower() in line.lower():
            headers = [h.strip().lower() for h in line.split("|")[1:-1]]
            in_table, header_seen = True, False; continue
        if in_table and "|---" in line: header_seen = True; continue
        if in_table and header_seen and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if cols and len(cols) >= len(headers):
                rows.append({headers[i]: cols[i] for i in range(len(headers))})
        elif in_table and header_seen and not line.startswith("|"): in_table = False
    return rows

# ============================================================
# Scanners — one per artifact type
# ============================================================

def scan_state():
    return read_json(".pm/state.json")

def scan_requirements():
    content = read_file("specs/requirements.md")
    fm = parse_frontmatter(content)
    reqs = []
    current = None
    for line in content.split("\n"):
        m = re.match(r"^#{2,4}\s+(REQ-\d+):\s*(.*)", line)
        if m:
            if current: reqs.append(current)
            current = {"id": m.group(1), "title": m.group(2), "text": ""}
        elif current:
            current["text"] += line + "\n"
    if current: reqs.append(current)

    result = []
    for r in reqs:
        fields = parse_bold_fields(r["text"])
        result.append({
            "id": r["id"],
            "title": r["title"],
            "status": "needs-decision" if "needs-decision" in r["text"].lower() else "active",
            "priority": fields.get("priority", ""),
            "source": fields.get("source", ""),
        })
    return {"frontmatter": fm, "items": result}

def scan_prd():
    content = read_file("specs/prd/prd.md")
    if not content: return None
    fm = parse_frontmatter(content)
    reqs = fm.get("requirements", [])
    if isinstance(reqs, str): reqs = [reqs]
    return {
        "exists": True,
        "status": fm.get("status", ""),
        "created": fm.get("created", ""),
        "created_by": fm.get("created_by", ""),
        "phase": fm.get("phase", ""),
        "requirements": reqs,
    }

def scan_personas():
    personas = []
    for f in sorted(glob.glob("specs/personas/*.md")):
        fm = parse_frontmatter(read_file(f))
        personas.append({
            "file": os.path.basename(f),
            "name": fm.get("name", os.path.basename(f).replace(".md", "")),
            "type": fm.get("type", ""),
            "requirement": fm.get("requirement", ""),
            "created": fm.get("created", ""),
        })
    return personas

def scan_epics_and_tasks():
    epics = []
    for epic_dir in sorted(glob.glob("specs/epics/*/")):
        epic_file = os.path.join(epic_dir, "epic.md")
        if not os.path.exists(epic_file): continue
        efm = parse_frontmatter(read_file(epic_file))
        epic_reqs = efm.get("requirements", [])
        if isinstance(epic_reqs, str): epic_reqs = [epic_reqs]

        tasks = []
        for tf in sorted(glob.glob(os.path.join(epic_dir, "[0-9]*.md"))):
            tfm = parse_frontmatter(read_file(tf))
            dep = tfm.get("depends_on", "")
            if isinstance(dep, list): dep = ", ".join(str(x) for x in dep)
            eff = tfm.get("effort", "")
            eff_days = ""
            if isinstance(eff, dict): eff_days = eff.get("days", ""); eff = eff.get("size", "")
            tasks.append({
                "id": os.path.basename(tf).replace(".md", ""),
                "name": tfm.get("name", ""),
                "status": tfm.get("status", "open"),
                "depends_on": dep,
                "parallel": tfm.get("parallel", ""),
                "conflicts_with": tfm.get("conflicts_with", ""),
                "effort": eff,
                "effort_days": eff_days,
                "created": tfm.get("created", ""),
                "updated": tfm.get("updated", ""),
                "started": tfm.get("started", ""),
                "completed": tfm.get("completed", ""),
            })

        epics.append({
            "name": os.path.basename(epic_dir.rstrip("/")),
            "status": efm.get("status", ""),
            "progress": efm.get("progress", ""),
            "prd": efm.get("prd", ""),
            "requirements": epic_reqs,
            "depends_on_epic": efm.get("depends_on_epic", []),
            "tasks": tasks,
        })
    return epics

def scan_stories():
    stories = []
    for f in sorted(glob.glob("specs/stories/us-*.md")):
        fm = parse_frontmatter(read_file(f))
        stories.append({
            "id": os.path.basename(f).replace(".md", ""),
            "name": fm.get("name", ""),
            "status": fm.get("status", "open"),
            "epic": fm.get("epic", ""),
            "task": fm.get("task", ""),
        })
    return stories

def scan_signoff():
    docs = []
    checks = [
        ("SRS", "specs/srs/srs.md"),
        ("System Design", "specs/design/system-design.md"),
        ("Sequence Diagrams", "specs/design/sequence-diagrams.md"),
        ("Test Plan", "specs/test-plan/test-plan.md"),
    ]
    for name, path in checks:
        if os.path.exists(path):
            fm = parse_frontmatter(read_file(path))
            docs.append({
                "name": name, "path": path,
                "status": fm.get("status", "draft"),
                "approved_by": fm.get("approved_by", ""),
                "approved_date": fm.get("approved_date", ""),
                "created": fm.get("created", ""),
                "updated": fm.get("updated", ""),
            })
    for f in sorted(glob.glob("specs/journeys/journey-*.md")):
        fm = parse_frontmatter(read_file(f))
        docs.append({
            "name": "Journey: " + os.path.basename(f).replace("journey-", "").replace(".md", ""),
            "path": f,
            "status": fm.get("status", "draft"),
            "approved_by": fm.get("approved_by", ""),
            "approved_date": fm.get("approved_date", ""),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
        })
    return docs

def scan_deliverables():
    content = read_file("specs/deliverable-tracker.md")
    if not content: return []
    items = []
    for row in parse_markdown_table(content, "| ID"):
        items.append({
            "id": row.get("id", ""),
            "name": row.get("name", ""),
            "role": row.get("role", ""),
            "owner": row.get("owner", ""),
            "reqs": row.get("req ids", row.get("reqs", "")),
            "due": row.get("due date", row.get("due", "")),
            "status": row.get("status", ""),
        })
    return items

def scan_ingestions():
    content = read_file(".pm/ingestion-log.md")
    if not content: return []
    ingestions = []
    cur = None
    for line in content.split("\n"):
        if line.startswith("## Ingestion:"):
            if cur: ingestions.append(cur)
            cur = {"date": line.replace("## Ingestion:", "").strip(), "source": "", "type": "", "reqs": ""}
        elif cur:
            if line.startswith("**Source:**"): cur["source"] = line.replace("**Source:**", "").strip()
            if line.startswith("**Type:**"): cur["type"] = line.replace("**Type:**", "").strip()
            if line.startswith("**REQ IDs Created:**"): cur["reqs"] = line.replace("**REQ IDs Created:**", "").strip()
    if cur: ingestions.append(cur)
    return ingestions

def scan_meetings():
    meetings = []
    for f in sorted(glob.glob(".pm/meeting-prep-*.md")):
        fm = parse_frontmatter(read_file(f))
        meetings.append({
            "file": os.path.basename(f),
            "topic": fm.get("name", os.path.basename(f).replace("meeting-prep-", "").replace(".md", "")),
            "type": fm.get("meeting_type", ""),
            "company": fm.get("company", ""),
            "created": fm.get("created", ""),
            "attendees": fm.get("attendees", ""),
        })
    return meetings

def scan_behavior_specs():
    specs = []
    for f in sorted(glob.glob("specs/behavior/REQ-*.md")):
        content = read_file(f)
        fm = parse_frontmatter(content)
        # Count Fields table rows
        fields_rows = parse_markdown_table(content, "| field")
        if not fields_rows:
            fields_rows = parse_markdown_table(content, "| name")
        fields_count = len(fields_rows)
        # Count Scenarios table rows by Type
        scenario_rows = parse_markdown_table(content, "| id")
        if not scenario_rows:
            scenario_rows = parse_markdown_table(content, "| scenario")
        uat = sit = e2e = 0
        for row in scenario_rows:
            type_val = (row.get("type", "") or "").upper()
            if "UAT" in type_val: uat += 1
            if "SIT" in type_val: sit += 1
            if "E2E" in type_val: e2e += 1
        total = len(scenario_rows)
        specs.append({
            "req_id": fm.get("req_id", os.path.basename(f).replace(".md", "")),
            "title": fm.get("title", ""),
            "status": fm.get("status", ""),
            "fields": fields_count,
            "uat": uat,
            "sit": sit,
            "e2e": e2e,
            "total": total,
            "updated": fm.get("updated", ""),
        })
    return specs

def scan_audit():
    entries = []
    for line in read_file(".pm/audit.log").strip().split("\n"):
        if line.strip():
            try: entries.append(json.loads(line))
            except: pass
    return entries[-50:]  # last 50

def scan_context():
    content = read_file(".pm/context.md")
    decisions, questions = [], []
    in_d = in_q = False
    for line in content.split("\n"):
        if "## Key Decisions" in line: in_d, in_q = True, False; continue
        if "## Open Questions" in line: in_q, in_d = True, False; continue
        if line.startswith("## "): in_d = in_q = False; continue
        if in_d and line.strip().startswith("- "): decisions.append(line.strip("- ").strip())
        if in_q and line.strip().startswith("- "): questions.append(line.strip("- ").strip())
    return {"decisions": decisions, "questions": questions}

# ============================================================
# Traceability — requirement-centric, shows all artifacts per REQ
# ============================================================

def build_traceability(reqs, prd, behavior, personas, epics, stories, tasks, story_by_task, signoff):
    """Build traceability rows — one per requirement, showing all linked artifacts."""
    # Build lookups
    prd_reqs = set(prd.get("requirements", [])) if prd else set()
    behavior_by_req = {b["req_id"]: b for b in behavior}
    persona_by_req = {}
    for p in personas:
        req = p.get("requirement", "")
        if req: persona_by_req.setdefault(req, []).append(p["name"])
    epic_by_req = {}
    for e in epics:
        for r in e.get("requirements", []):
            epic_by_req.setdefault(r, []).append(e["name"])
    task_by_req = {}
    story_by_req = {}
    for e in epics:
        for t in e.get("tasks", []):
            for r in e.get("requirements", []):
                task_by_req.setdefault(r, []).append({"id": t["id"], "name": t.get("name",""), "status": t.get("status","")})
                s = story_by_task.get(t["id"], "")
                if s: story_by_req.setdefault(r, set()).add(s)
    # Convert sets to sorted lists
    for r in story_by_req:
        story_by_req[r] = sorted(story_by_req[r])

    rows = []
    for req in reqs:
        rid = req["id"]
        bspec = behavior_by_req.get(rid)
        rows.append({
            "req_id": rid,
            "req_title": req.get("title", ""),
            "prd": "yes" if rid in prd_reqs else "",
            "behavior_spec": f"{bspec['total']} scenarios" if bspec else "",
            "persona": ", ".join(persona_by_req.get(rid, [])),
            "epic": ", ".join(epic_by_req.get(rid, [])),
            "stories": ", ".join(story_by_req.get(rid, [])),
            "tasks": len(task_by_req.get(rid, [])),
            "tasks_done": sum(1 for t in task_by_req.get(rid, []) if t["status"].lower() in ("closed","completed","done")),
        })
    return rows

# ============================================================
# Build & Write
# ============================================================

def build_project_data():
    state = scan_state()
    reqs_data = scan_requirements()
    prd = scan_prd()
    epics = scan_epics_and_tasks()
    context = scan_context()

    # Flatten tasks from active epic
    active_epic = state.get("active_epic", "")
    tasks = []
    for e in epics:
        if e["name"] == active_epic or (not active_epic and e["tasks"]):
            tasks = e["tasks"]
            if not active_epic: active_epic = e["name"]
            break

    # Build requirement lookup
    req_lookup = {r["id"]: r["title"] for r in reqs_data["items"]}

    # PRD features mapped from requirements
    prd_features = []
    if prd:
        for rid in prd.get("requirements", []):
            prd_features.append({"id": rid, "title": req_lookup.get(rid, rid)})

    # Build story-to-task reverse lookup (task_id → story_id)
    story_by_task = {}
    for s in scan_stories():
        if s.get("task"):
            story_by_task[str(s["task"])] = s["id"]

    # Enrich tasks with linked story
    for t in tasks:
        t["story"] = story_by_task.get(t["id"], "")

    # Metrics
    total_tasks = len(tasks)
    done = sum(1 for t in tasks if t["status"].lower() in ("closed", "completed", "done"))
    active = sum(1 for t in tasks if t["status"].lower() in ("in-progress", "in_progress"))
    signoff = scan_signoff()
    deliverables = scan_deliverables()
    personas = scan_personas()
    stories = scan_stories()
    behavior = scan_behavior_specs()

    return {
        "_synced_at": datetime.now().isoformat(),
        "_version": "1.0",

        "project_name": state.get("project_name", "Project"),
        "language": state.get("language", "en"),
        "phase": state.get("phase", 0),
        "phase_name": state.get("phase_name", "Setup"),

        "metrics": {
            "total_reqs": len(reqs_data["items"]),
            "total_tasks": total_tasks,
            "done_tasks": done,
            "active_tasks": active,
            "blocked": len(state.get("blocked", [])),
            "pct": round(done / total_tasks * 100) if total_tasks else 0,
            "orphan_tasks": sum(1 for t in tasks if not t.get("story")),
            "signoff_approved": sum(1 for s in signoff if s["status"].lower() == "approved"),
            "signoff_total": len(signoff),
            "deliv_done": sum(1 for d in deliverables if d["status"].lower() == "approved"),
            "deliv_total": len(deliverables),
            "personas": len(personas),
            "stories": len(stories),
            "behavior_specs_count": len(behavior),
            "behavior_scenarios_total": sum(b["total"] for b in behavior),
            "behavior_uat": sum(b["uat"] for b in behavior),
            "behavior_sit": sum(b["sit"] for b in behavior),
            "behavior_e2e": sum(b["e2e"] for b in behavior),
        },

        "requirements": reqs_data["items"],
        "prd": prd,
        "prd_features": prd_features,
        "personas": personas,
        "stories": stories,
        "epics": epics,
        "active_epic": active_epic,
        "tasks": tasks,
        "signoff": signoff,
        "deliverables": deliverables,
        "blockers": state.get("blocked", []),
        "ingestions": scan_ingestions(),
        "meetings": scan_meetings(),
        "audit": scan_audit(),
        "decisions": context["decisions"],
        "questions": context["questions"],
        "behavior_specs": behavior,
        "strategy_files": [f for f in ["strategy/positioning.md", "strategy/roadmap.md"] if os.path.exists(f)],
        "traceability": build_traceability(reqs_data["items"], prd, behavior, personas, epics, stories, tasks, story_by_task, signoff),
    }

def sync():
    data = build_project_data()
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return data

def verify():
    """Rebuild in memory and compare against current project-data.json."""
    rebuilt = build_project_data()
    current = read_json(OUTPUT)
    if not current:
        print("No existing project-data.json found — nothing to verify.")
        return 1

    checks = [
        ("requirements count", len(rebuilt.get("requirements", [])), len(current.get("requirements", []))),
        ("tasks count", len(rebuilt.get("tasks", [])), len(current.get("tasks", []))),
        ("personas count", len(rebuilt.get("personas", [])), len(current.get("personas", []))),
        ("stories count", len(rebuilt.get("stories", [])), len(current.get("stories", []))),
        ("signoff count", len(rebuilt.get("signoff", [])), len(current.get("signoff", []))),
        ("deliverables count", len(rebuilt.get("deliverables", [])), len(current.get("deliverables", []))),
        ("ingestions count", len(rebuilt.get("ingestions", [])), len(current.get("ingestions", []))),
        ("meetings count", len(rebuilt.get("meetings", [])), len(current.get("meetings", []))),
        ("phase", rebuilt.get("phase", 0), current.get("phase", 0)),
        ("project_name", rebuilt.get("project_name", ""), current.get("project_name", "")),
        ("total_reqs metric", rebuilt.get("metrics", {}).get("total_reqs", 0), current.get("metrics", {}).get("total_reqs", 0)),
        ("total_tasks metric", rebuilt.get("metrics", {}).get("total_tasks", 0), current.get("metrics", {}).get("total_tasks", 0)),
        ("done_tasks metric", rebuilt.get("metrics", {}).get("done_tasks", 0), current.get("metrics", {}).get("done_tasks", 0)),
        ("blocked metric", rebuilt.get("metrics", {}).get("blocked", 0), current.get("metrics", {}).get("blocked", 0)),
    ]

    mismatches = []
    for label, expected, actual in checks:
        if expected != actual:
            mismatches.append((label, expected, actual))

    if mismatches:
        print("MISMATCH — project-data.json is out of date:")
        for label, expected, actual in mismatches:
            print(f"  {label}: rebuilt={expected}, current={actual}")
        return 1
    else:
        print("OK — project-data.json matches rebuilt data.")
        return 0


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(verify())

    data = sync()
    reqs = len(data["requirements"])
    tasks = len(data["tasks"])
    print(f"Rebuilt .pm/project-data.json")
    print(f"  {reqs} requirements, {tasks} tasks, {len(data['personas'])} personas")
    print(f"  {len(data['signoff'])} sign-off docs, {len(data['deliverables'])} deliverables")
    print(f"  {len(data['ingestions'])} ingestions, {len(data['meetings'])} meetings")
    print(f"  {len(data['audit'])} audit entries")
