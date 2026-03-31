#!/usr/bin/env python3
"""
PM Workflow — XLSX Report Generator
Generates a formatted project status report from project state files.
Runs locally with zero LLM token cost.

Usage:
  python3 .pm/scripts/generate-report.py
  python3 .pm/scripts/generate-report.py --output custom-name.xlsx

Requires: pip install openpyxl
Fallback: generates CSV files if openpyxl is not installed
"""

import json
import re
import os
import sys
import glob
from datetime import datetime, date

# ============================================================
# Configuration
# ============================================================

OUTPUT_DIR = "specs/reports"

def get_project_name():
    """Read project name from state.json, fallback to 'Project'."""
    state = read_json(".pm/state.json")
    return state.get("project_name", "Project")

def get_default_filename():
    """Generate filename using project name and date."""
    name = get_project_name().lower().replace(" ", "-")
    return f"{name}-status-{date.today().isoformat()}.xlsx"

# Column widths per tab (approx characters)
COL_WIDTHS = {
    "narrow": 12,
    "medium": 20,
    "wide": 35,
    "extra_wide": 50,
}

# Status colors (hex without #)
COLORS = {
    "header_bg": "1F2937",      # dark gray
    "header_font": "FFFFFF",    # white
    "done": "DCFCE7",           # green bg
    "active": "DBEAFE",         # blue bg
    "blocked": "FEE2E2",        # red bg
    "draft": "FEF3C7",          # yellow bg
    "approved": "DCFCE7",       # green bg
    "needs_decision": "FEF3C7", # yellow bg
    "row_alt": "F9FAFB",        # light gray alternating
    "white": "FFFFFF",
}

# ============================================================
# Helpers
# ============================================================

def read_file(path):
    """Read file content, return empty string if not found."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def read_json(path):
    """Read JSON file, return empty dict if not found."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def parse_frontmatter(content):
    """Extract YAML frontmatter as dict (simple parser, no pyyaml needed)."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            fm[key] = val
    return fm

def parse_requirements(content):
    """Parse specs/requirements.md into list of REQ dicts."""
    reqs = []
    current = None
    for line in content.split("\n"):
        match = re.match(r"^## (REQ-\d+):\s*(.*)", line)
        if match:
            if current:
                reqs.append(current)
            current = {"id": match.group(1), "title": match.group(2), "lines": []}
        elif current:
            current["lines"].append(line)
    if current:
        reqs.append(current)
    return reqs

def parse_audit_log(path):
    """Parse .pm/audit.log JSON lines."""
    entries = []
    content = read_file(path)
    for line in content.strip().split("\n"):
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries

def get_task_files(epic_dir):
    """Get all task files (numbered .md files) from epic directory."""
    tasks = []
    for f in sorted(glob.glob(os.path.join(epic_dir, "[0-9]*.md"))):
        content = read_file(f)
        fm = parse_frontmatter(content)
        fm["_file"] = os.path.basename(f)
        fm["_path"] = f
        fm["_content"] = content
        tasks.append(fm)
    return tasks

def get_persona_files():
    """Get all persona files."""
    personas = []
    for f in sorted(glob.glob("specs/personas/*.md")):
        content = read_file(f)
        fm = parse_frontmatter(content)
        fm["_file"] = os.path.basename(f)
        fm["_content"] = content
        personas.append(fm)
    return personas

def get_story_files():
    """Get all user story files."""
    stories = []
    for f in sorted(glob.glob("specs/stories/us-*.md")):
        content = read_file(f)
        fm = parse_frontmatter(content)
        fm["_file"] = os.path.basename(f)
        fm["_content"] = content
        stories.append(fm)
    return stories

def get_meeting_preps():
    """Get all meeting prep files."""
    preps = []
    for f in sorted(glob.glob(".pm/meeting-prep-*.md")):
        content = read_file(f)
        fm = parse_frontmatter(content)
        fm["_file"] = os.path.basename(f)
        fm["_content"] = content
        preps.append(fm)
    return preps

def get_signoff_docs():
    """Get sign-off document status."""
    docs = []
    signoff_files = [
        ("SRS", "specs/srs/srs.md"),
        ("System Design", "specs/design/system-design.md"),
        ("Sequence Diagrams", "specs/design/sequence-diagrams.md"),
        ("Test Plan", "specs/test-plan/test-plan.md"),
    ]
    for name, path in signoff_files:
        if os.path.exists(path):
            content = read_file(path)
            fm = parse_frontmatter(content)
            docs.append({
                "name": name,
                "path": path,
                "status": fm.get("status", "draft"),
                "approved_by": fm.get("approved_by", ""),
                "approved_date": fm.get("approved_date", ""),
                "created": fm.get("created", ""),
                "updated": fm.get("updated", ""),
            })
    # Add user journey files
    for f in sorted(glob.glob("specs/journeys/journey-*.md")):
        content = read_file(f)
        fm = parse_frontmatter(content)
        docs.append({
            "name": f"User Journey: {os.path.basename(f).replace('journey-', '').replace('.md', '')}",
            "path": f,
            "status": fm.get("status", "draft"),
            "approved_by": fm.get("approved_by", ""),
            "approved_date": fm.get("approved_date", ""),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
        })
    return docs

def parse_deliverable_tracker():
    """Parse specs/deliverable-tracker.md table."""
    content = read_file("specs/deliverable-tracker.md")
    items = []
    in_table = False
    header_seen = False
    for line in content.split("\n"):
        if "| ID |" in line or "| id |" in line.lower():
            in_table = True
            header_seen = False
            continue
        if in_table and "|---" in line:
            header_seen = True
            continue
        if in_table and header_seen and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 7:
                items.append({
                    "id": cols[0], "name": cols[1], "role": cols[2],
                    "owner": cols[3], "reqs": cols[4], "due": cols[5],
                    "status": cols[6],
                })
        elif in_table and header_seen and not line.startswith("|"):
            in_table = False
    return items

def parse_ingestion_log():
    """Parse .pm/ingestion-log.md into ingestion entries."""
    content = read_file(".pm/ingestion-log.md")
    entries = []
    current = None
    for line in content.split("\n"):
        if line.startswith("## Ingestion:"):
            if current:
                entries.append(current)
            current = {"date": line.replace("## Ingestion:", "").strip(), "lines": []}
        elif current:
            current["lines"].append(line)
    if current:
        entries.append(current)
    return entries


# ============================================================
# XLSX Generation (openpyxl)
# ============================================================

def generate_xlsx(output_path):
    """Generate formatted XLSX report."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    # Style helpers
    header_font = Font(bold=True, color=COLORS["header_font"], size=11)
    header_fill = PatternFill(start_color=COLORS["header_bg"], end_color=COLORS["header_bg"], fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    wrap_align = Alignment(vertical="top", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )

    def status_fill(status):
        s = str(status).lower().strip()
        if s in ("done", "complete", "completed", "closed", "approved"):
            return PatternFill(start_color=COLORS["done"], end_color=COLORS["done"], fill_type="solid")
        if s in ("active", "in-progress", "in_progress", "in progress", "in review"):
            return PatternFill(start_color=COLORS["active"], end_color=COLORS["active"], fill_type="solid")
        if s in ("blocked", "needs-decision"):
            return PatternFill(start_color=COLORS["blocked"], end_color=COLORS["blocked"], fill_type="solid")
        if s in ("draft", "backlog", "not started"):
            return PatternFill(start_color=COLORS["draft"], end_color=COLORS["draft"], fill_type="solid")
        return PatternFill(start_color=COLORS["white"], end_color=COLORS["white"], fill_type="solid")

    def alt_fill(row_idx):
        if row_idx % 2 == 0:
            return PatternFill(start_color=COLORS["row_alt"], end_color=COLORS["row_alt"], fill_type="solid")
        return PatternFill(start_color=COLORS["white"], end_color=COLORS["white"], fill_type="solid")

    def write_sheet(ws, headers, rows, col_widths=None, status_col=None):
        """Write headers and rows to a worksheet with formatting."""
        # Headers
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        # Data rows
        for row_idx, row_data in enumerate(rows, 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.alignment = wrap_align
                cell.border = thin_border
                if status_col is not None and col_idx == status_col:
                    cell.fill = status_fill(value)
                else:
                    cell.fill = alt_fill(row_idx)

        # Column widths
        if col_widths:
            for col_idx, width in enumerate(col_widths, 1):
                ws.column_dimensions[get_column_letter(col_idx)].width = width

        # Freeze header row
        ws.freeze_panes = "A2"

    # ---- Load all project data ----
    state = read_json(".pm/state.json")
    context = read_file(".pm/context.md")
    reqs = parse_requirements(read_file("specs/requirements.md"))
    audit = parse_audit_log(".pm/audit.log")
    signoff = get_signoff_docs()
    deliverables = parse_deliverable_tracker()
    personas = get_persona_files()
    stories = get_story_files()
    meetings = get_meeting_preps()
    ingestions = parse_ingestion_log()

    # Find active epic and tasks
    active_epic = state.get("active_epic", "")
    epic_dir = f"specs/epics/{active_epic}" if active_epic else ""
    tasks = get_task_files(epic_dir) if epic_dir and os.path.isdir(epic_dir) else []

    # If no active epic, try to find any epic
    if not tasks:
        for d in sorted(glob.glob("specs/epics/*/")):
            t = get_task_files(d)
            if t:
                tasks = t
                epic_dir = d.rstrip("/")
                active_epic = os.path.basename(epic_dir)
                break

    # ============================================================
    # Tab 1: Dashboard
    # ============================================================
    ws = wb.active
    ws.title = "Dashboard"

    phase = state.get("phase", 0)
    phase_name = state.get("phase_name", "Setup")
    total_reqs = len(reqs)
    total_tasks = len(tasks)
    done_tasks = sum(1 for t in tasks if t.get("status", "").lower() in ("closed", "completed", "done"))
    blocked_count = len(state.get("blocked", []))
    signoff_approved = sum(1 for d in signoff if d.get("status", "").lower() == "approved")
    deliverables_done = sum(1 for d in deliverables if d.get("status", "").lower() == "approved")

    dashboard_data = [
        ("Project Phase", f"Phase {phase}: {phase_name}"),
        ("Phase Progress", f"{phase}/5 phases"),
        ("", ""),
        ("Requirements", f"{total_reqs} REQs"),
        ("PRD", "Exists" if os.path.exists("specs/prd/prd.md") else "Not created"),
        ("Personas", f"{len(personas)} created"),
        ("", ""),
        ("Active Epic", active_epic or "None"),
        ("Task Progress", f"{done_tasks}/{total_tasks} tasks complete ({round(done_tasks/total_tasks*100) if total_tasks else 0}%)"),
        ("Blocked Items", f"{blocked_count}"),
        ("", ""),
        ("Sign-Off Documents", f"{signoff_approved}/{len(signoff)} approved"),
        ("External Deliverables", f"{deliverables_done}/{len(deliverables)} approved"),
        ("", ""),
        ("Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
    ]

    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    project_name = state.get("project_name", "Project")

    title_font = Font(bold=True, size=14)
    ws.cell(row=1, column=1, value=f"{project_name} — Status Dashboard").font = title_font
    ws.merge_cells("A1:B1")

    for idx, (label, value) in enumerate(dashboard_data, 3):
        cell_a = ws.cell(row=idx, column=1, value=label)
        cell_b = ws.cell(row=idx, column=2, value=value)
        if label:
            cell_a.font = Font(bold=True)
        cell_a.border = thin_border
        cell_b.border = thin_border

    # ============================================================
    # Tab 2: Requirements
    # ============================================================
    ws2 = wb.create_sheet("Requirements")
    req_rows = []
    for r in reqs:
        # Extract priority and status from content lines
        priority = ""
        status = "active"
        source = ""
        for line in r.get("lines", []):
            if "priority" in line.lower() and ":" in line:
                priority = line.split(":", 1)[1].strip()
            if "status" in line.lower() and "needs-decision" in line.lower():
                status = "needs-decision"
            if "source" in line.lower() and ":" in line:
                source = line.split(":", 1)[1].strip()
        req_rows.append((r["id"], r["title"], status, priority, source))

    write_sheet(ws2,
        ["REQ ID", "Title", "Status", "Priority", "Source"],
        req_rows,
        col_widths=[12, 40, 15, 12, 35],
        status_col=3)

    # ============================================================
    # Tab 3: PRD Summary
    # ============================================================
    ws3 = wb.create_sheet("PRD Summary")
    prd_content = read_file("specs/prd/prd.md")
    prd_fm = parse_frontmatter(prd_content)
    prd_rows = []
    if prd_content:
        # Extract features from PRD
        for line in prd_content.split("\n"):
            match = re.match(r"^### Feature \d+:\s*(.*)", line)
            if not match:
                match = re.match(r"^### \d+\.\s*(.*)", line)
            if match:
                prd_rows.append((match.group(1), prd_fm.get("status", "active"), "", ""))
    if not prd_rows:
        prd_rows.append(("No PRD features found", "", "", ""))

    write_sheet(ws3,
        ["Feature", "Status", "Priority", "REQ IDs"],
        prd_rows,
        col_widths=[40, 15, 12, 25])

    # ============================================================
    # Tab 4: Personas
    # ============================================================
    ws4 = wb.create_sheet("Personas")
    persona_rows = []
    for p in personas:
        persona_rows.append((
            p.get("name", p["_file"]),
            p.get("type", ""),
            p.get("requirement", ""),
            p.get("created", ""),
        ))
    if not persona_rows:
        persona_rows.append(("No personas created", "", "", ""))

    write_sheet(ws4,
        ["Name", "Type", "Linked REQ", "Created"],
        persona_rows,
        col_widths=[25, 15, 15, 20])

    # ============================================================
    # Tab 5: Discovery & Strategy
    # ============================================================
    ws5 = wb.create_sheet("Discovery & Strategy")
    strategy_rows = []

    # Extract key decisions and open questions from context
    in_decisions = False
    in_questions = False
    for line in context.split("\n"):
        if "## Key Decisions" in line:
            in_decisions = True
            in_questions = False
            continue
        if "## Open Questions" in line:
            in_questions = True
            in_decisions = False
            continue
        if line.startswith("## "):
            in_decisions = False
            in_questions = False
            continue
        if in_decisions and line.strip().startswith("- "):
            strategy_rows.append(("Decision", line.strip("- ").strip()))
        if in_questions and line.strip().startswith("- "):
            strategy_rows.append(("Open Question", line.strip("- ").strip()))

    # Add positioning/strategy files if they exist
    for f in ["strategy/positioning.md", "strategy/roadmap.md"]:
        if os.path.exists(f):
            strategy_rows.append(("Strategy Artifact", f))

    if not strategy_rows:
        strategy_rows.append(("No discovery/strategy data yet", ""))

    write_sheet(ws5,
        ["Type", "Details"],
        strategy_rows,
        col_widths=[20, 60])

    # ============================================================
    # Tab 6: User Stories
    # ============================================================
    ws6 = wb.create_sheet("User Stories")
    story_rows = []
    for s in stories:
        story_rows.append((
            s["_file"].replace(".md", ""),
            s.get("name", ""),
            s.get("status", "open"),
            s.get("epic", ""),
            s.get("task", ""),
        ))
    if not story_rows:
        story_rows.append(("No user stories created", "", "", "", ""))

    write_sheet(ws6,
        ["Story ID", "Title", "Status", "Epic", "Task"],
        story_rows,
        col_widths=[12, 35, 12, 30, 30],
        status_col=3)

    # ============================================================
    # Tab 7: Epic & Tasks
    # ============================================================
    ws7 = wb.create_sheet("Epic & Tasks")
    task_rows = []
    for t in tasks:
        depends = t.get("depends_on", "")
        if isinstance(depends, list):
            depends = ", ".join(str(d) for d in depends)
        task_rows.append((
            t["_file"].replace(".md", ""),
            t.get("name", ""),
            t.get("status", "open"),
            depends,
            t.get("effort", {}).get("size", "") if isinstance(t.get("effort"), dict) else t.get("effort", ""),
            t.get("created", ""),
            t.get("updated", ""),
        ))
    if not task_rows:
        task_rows.append(("No tasks found", "", "", "", "", "", ""))

    write_sheet(ws7,
        ["Task ID", "Name", "Status", "Depends On", "Effort", "Created", "Updated"],
        task_rows,
        col_widths=[12, 35, 15, 15, 10, 20, 20],
        status_col=3)

    # ============================================================
    # Tab 8: Timeline
    # ============================================================
    ws8 = wb.create_sheet("Timeline")
    timeline_rows = []
    for t in tasks:
        timeline_rows.append((
            t["_file"].replace(".md", ""),
            t.get("name", ""),
            t.get("status", "open"),
            t.get("created", ""),
            t.get("started", t.get("created", "")),
            t.get("completed", ""),
            t.get("effort", {}).get("days", "") if isinstance(t.get("effort"), dict) else "",
        ))
    if not timeline_rows:
        timeline_rows.append(("No timeline data", "", "", "", "", "", ""))

    write_sheet(ws8,
        ["Task ID", "Name", "Status", "Created", "Started", "Completed", "Est. Days"],
        timeline_rows,
        col_widths=[12, 35, 15, 20, 20, 20, 10],
        status_col=3)

    # ============================================================
    # Tab 9: Deliverables
    # ============================================================
    ws9 = wb.create_sheet("Deliverables")
    del_rows = [(d["id"], d["name"], d["role"], d["owner"], d["reqs"], d["due"], d["status"]) for d in deliverables]
    if not del_rows:
        del_rows.append(("No deliverables tracked", "", "", "", "", "", ""))

    write_sheet(ws9,
        ["ID", "Name", "Role", "Owner", "REQ IDs", "Due Date", "Status"],
        del_rows,
        col_widths=[10, 30, 15, 15, 15, 15, 15],
        status_col=7)

    # ============================================================
    # Tab 10: Sign-Off Status
    # ============================================================
    ws10 = wb.create_sheet("Sign-Off Status")
    signoff_rows = [(d["name"], d["path"], d["status"], d["approved_by"], d["approved_date"], d["updated"]) for d in signoff]
    if not signoff_rows:
        signoff_rows.append(("No sign-off documents", "", "", "", "", ""))

    write_sheet(ws10,
        ["Document", "Path", "Status", "Approved By", "Approved Date", "Last Updated"],
        signoff_rows,
        col_widths=[25, 35, 12, 20, 15, 20],
        status_col=3)

    # ============================================================
    # Tab 11: Risks & Blockers
    # ============================================================
    ws11 = wb.create_sheet("Risks & Blockers")
    blocker_rows = []

    # Manual blocks
    for b in state.get("blocked", []):
        blocker_rows.append((
            "Manual Block",
            b.get("description", ""),
            b.get("since", ""),
            b.get("blocked_by", ""),
            "",
        ))

    # Dependency blocks from tasks
    for t in tasks:
        status = t.get("status", "").lower()
        if status in ("closed", "completed", "in-progress", "in_progress"):
            continue
        depends = t.get("depends_on", [])
        if isinstance(depends, str):
            depends = [d.strip() for d in depends.strip("[]").split(",") if d.strip()]
        for dep in depends:
            dep_file = os.path.join(epic_dir, f"{str(dep).zfill(3)}.md")
            if os.path.exists(dep_file):
                dep_fm = parse_frontmatter(read_file(dep_file))
                dep_status = dep_fm.get("status", "unknown")
                if dep_status.lower() not in ("closed", "completed"):
                    blocker_rows.append((
                        "Dependency Block",
                        f"Task {t['_file']} waiting on Task {dep}",
                        "",
                        f"Task {dep}: {dep_status}",
                        t.get("name", ""),
                    ))

    if not blocker_rows:
        blocker_rows.append(("None", "No blockers", "", "", ""))

    write_sheet(ws11,
        ["Type", "Description", "Since", "Blocked By", "Task"],
        blocker_rows,
        col_widths=[18, 40, 15, 25, 25],
        status_col=1)

    # ============================================================
    # Tab 12: Traceability
    # ============================================================
    ws12 = wb.create_sheet("Traceability")
    trace_rows = []
    for t in tasks:
        task_id = t["_file"].replace(".md", "")
        # Find linked REQ from epic
        epic_file = os.path.join(epic_dir, "epic.md") if epic_dir else ""
        epic_fm = parse_frontmatter(read_file(epic_file)) if epic_file else {}
        epic_reqs = epic_fm.get("requirements", [])
        if isinstance(epic_reqs, str):
            epic_reqs = [epic_reqs]
        prd_path = epic_fm.get("prd", "specs/prd/prd.md")

        trace_rows.append((
            ", ".join(epic_reqs) if epic_reqs else "",
            prd_path,
            f"{active_epic}/epic.md",
            task_id,
            t.get("name", ""),
            t.get("status", ""),
        ))
    if not trace_rows:
        trace_rows.append(("", "", "", "", "No traceability data", ""))

    write_sheet(ws12,
        ["REQ IDs", "PRD", "Epic", "Task ID", "Task Name", "Status"],
        trace_rows,
        col_widths=[15, 25, 25, 12, 30, 12],
        status_col=6)

    # ============================================================
    # Tab 13: Ingestion Log
    # ============================================================
    ws13 = wb.create_sheet("Ingestion Log")
    ingest_rows = []
    for entry in ingestions:
        source = ""
        req_range = ""
        for line in entry.get("lines", []):
            if "Source:" in line:
                source = line.split("Source:", 1)[1].strip()
            if "REQ IDs Created:" in line:
                req_range = line.split("REQ IDs Created:", 1)[1].strip()
        ingest_rows.append((entry.get("date", ""), source, req_range))
    if not ingest_rows:
        ingest_rows.append(("No ingestions", "", ""))

    write_sheet(ws13,
        ["Date", "Source", "REQ IDs Created"],
        ingest_rows,
        col_widths=[20, 45, 25])

    # ============================================================
    # Tab 14: Meeting Prep
    # ============================================================
    ws14 = wb.create_sheet("Meeting Prep")
    meeting_rows = []
    for m in meetings:
        meeting_rows.append((
            m.get("name", m["_file"]),
            m.get("meeting_type", ""),
            m.get("company", ""),
            m.get("created", ""),
            m.get("attendees", ""),
        ))
    if not meeting_rows:
        meeting_rows.append(("No meeting preps", "", "", "", ""))

    write_sheet(ws14,
        ["Topic", "Type", "Company", "Created", "Attendees"],
        meeting_rows,
        col_widths=[30, 15, 20, 20, 30])

    # ============================================================
    # Tab 15: Activity Log
    # ============================================================
    ws15 = wb.create_sheet("Activity Log")
    activity_rows = []
    for a in audit[-50:]:  # Last 50 entries
        activity_rows.append((
            a.get("timestamp", ""),
            f"Phase {a.get('phase', '')}",
            a.get("action", a.get("skill", "")),
            ", ".join(a.get("artifacts_created", [])),
            a.get("req_id", a.get("reason", "")),
        ))
    if not activity_rows:
        activity_rows.append(("No activity yet", "", "", "", ""))

    write_sheet(ws15,
        ["Timestamp", "Phase", "Action", "Artifacts", "Details"],
        activity_rows,
        col_widths=[22, 10, 25, 40, 25])

    # ============================================================
    # Save
    # ============================================================
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wb.save(output_path)
    return output_path


# ============================================================
# CSV Fallback
# ============================================================

def generate_csv_fallback():
    """Generate CSV files if openpyxl is not available."""
    import csv
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    state = read_json(".pm/state.json")
    reqs = parse_requirements(read_file("specs/requirements.md"))
    tasks = []
    active_epic = state.get("active_epic", "")
    if active_epic:
        tasks = get_task_files(f"specs/epics/{active_epic}")

    # Requirements CSV
    with open(os.path.join(OUTPUT_DIR, "requirements.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["REQ ID", "Title"])
        for r in reqs:
            w.writerow([r["id"], r["title"]])

    # Tasks CSV
    with open(os.path.join(OUTPUT_DIR, "tasks.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Task ID", "Name", "Status", "Depends On"])
        for t in tasks:
            w.writerow([t["_file"], t.get("name", ""), t.get("status", ""), t.get("depends_on", "")])

    print(f"CSV files saved to {OUTPUT_DIR}/")
    print("  - requirements.csv")
    print("  - tasks.csv")
    print("\nInstall openpyxl for full XLSX report: pip install openpyxl")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    output = os.path.join(OUTPUT_DIR, get_default_filename())
    if len(sys.argv) > 2 and sys.argv[1] == "--output":
        output = os.path.join(OUTPUT_DIR, sys.argv[2])

    try:
        import openpyxl
        result = generate_xlsx(output)
        print(f"✅ Report generated: {result}")
        print(f"   15 tabs | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"\n   Open in Excel or upload to Google Sheets.")
    except ImportError:
        print("⚠️  openpyxl not installed. Generating CSV fallback...")
        generate_csv_fallback()
