#!/usr/bin/env python3
"""
PM Workflow — Live Dashboard Server
Real-time project status dashboard served locally.
Zero external dependencies — uses Python's built-in http.server.

Usage:
  python3 .pm/scripts/dashboard-server.py
  python3 .pm/scripts/dashboard-server.py --port 8080

Opens: http://localhost:3000
"""

import json, re, os, sys, glob, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 3000

# ============================================================
# Data Readers (same as generate-report.py)
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
    if not content.startswith("---"): return {}
    parts = content.split("---", 2)
    if len(parts) < 3: return {}
    fm = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            fm[key] = val
    return fm

def parse_requirements(content):
    reqs = []
    current = None
    for line in content.split("\n"):
        m = re.match(r"^## (REQ-\d+):\s*(.*)", line)
        if m:
            if current: reqs.append(current)
            current = {"id": m.group(1), "title": m.group(2), "lines": []}
        elif current:
            current["lines"].append(line)
    if current: reqs.append(current)
    return reqs

def get_all_data():
    """Read all project state and return as JSON-serializable dict."""
    state = read_json(".pm/state.json")
    reqs = parse_requirements(read_file("specs/requirements.md"))
    context = read_file(".pm/context.md")

    # Tasks
    active_epic = state.get("active_epic", "")
    epic_dir = f"specs/epics/{active_epic}" if active_epic else ""
    tasks = []
    if epic_dir and os.path.isdir(epic_dir):
        for f in sorted(glob.glob(f"{epic_dir}/[0-9]*.md")):
            fm = parse_frontmatter(read_file(f))
            fm["_file"] = os.path.basename(f)
            tasks.append(fm)
    if not tasks:
        for d in sorted(glob.glob("specs/epics/*/")):
            for f in sorted(glob.glob(f"{d}[0-9]*.md")):
                fm = parse_frontmatter(read_file(f))
                fm["_file"] = os.path.basename(f)
                tasks.append(fm)
            if tasks:
                active_epic = os.path.basename(d.rstrip("/"))
                break

    # Personas
    personas = []
    for f in sorted(glob.glob("specs/personas/*.md")):
        fm = parse_frontmatter(read_file(f))
        fm["_file"] = os.path.basename(f)
        personas.append(fm)

    # Stories
    stories = []
    for f in sorted(glob.glob("specs/stories/us-*.md")):
        fm = parse_frontmatter(read_file(f))
        fm["_file"] = os.path.basename(f)
        stories.append(fm)

    # Sign-off docs
    signoff = []
    for name, path in [("SRS", "specs/srs/srs.md"), ("System Design", "specs/design/system-design.md"),
                        ("Sequence Diagrams", "specs/design/sequence-diagrams.md"), ("Test Plan", "specs/test-plan/test-plan.md")]:
        if os.path.exists(path):
            fm = parse_frontmatter(read_file(path))
            signoff.append({"name": name, "status": fm.get("status", "draft"), "approved_by": fm.get("approved_by", ""), "updated": fm.get("updated", "")})
    for f in sorted(glob.glob("specs/journeys/journey-*.md")):
        fm = parse_frontmatter(read_file(f))
        signoff.append({"name": f"Journey: {os.path.basename(f).replace('journey-','').replace('.md','')}", "status": fm.get("status","draft"), "approved_by": fm.get("approved_by",""), "updated": fm.get("updated","")})

    # Deliverables
    deliverables = []
    in_table = header_seen = False
    for line in read_file("specs/deliverable-tracker.md").split("\n"):
        if "| ID |" in line: in_table, header_seen = True, False; continue
        if in_table and "|---" in line: header_seen = True; continue
        if in_table and header_seen and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 7:
                deliverables.append({"id": cols[0], "name": cols[1], "role": cols[2], "owner": cols[3], "reqs": cols[4], "due": cols[5], "status": cols[6]})
        elif in_table and header_seen and not line.startswith("|"): in_table = False

    # Audit log (last 30)
    audit = []
    for line in read_file(".pm/audit.log").strip().split("\n"):
        if line.strip():
            try: audit.append(json.loads(line))
            except: pass
    audit = audit[-30:]

    # Blockers
    blockers = state.get("blocked", [])

    # Compute metrics
    total_tasks = len(tasks)
    done = sum(1 for t in tasks if t.get("status","").lower() in ("closed","completed","done"))
    active = sum(1 for t in tasks if t.get("status","").lower() in ("in-progress","in_progress"))

    # Key decisions / open questions from context
    decisions, questions = [], []
    in_d = in_q = False
    for line in context.split("\n"):
        if "## Key Decisions" in line: in_d, in_q = True, False; continue
        if "## Open Questions" in line: in_q, in_d = True, False; continue
        if line.startswith("## "): in_d = in_q = False; continue
        if in_d and line.strip().startswith("- "): decisions.append(line.strip("- ").strip())
        if in_q and line.strip().startswith("- "): questions.append(line.strip("- ").strip())

    # Clean requirements for JSON
    clean_reqs = []
    for r in reqs:
        priority = status = source = ""
        for line in r.get("lines", []):
            if "priority" in line.lower() and ":" in line: priority = line.split(":",1)[1].strip()
            if "needs-decision" in line.lower(): status = "needs-decision"
            if "source" in line.lower() and ":" in line: source = line.split(":",1)[1].strip()
        clean_reqs.append({"id": r["id"], "title": r["title"], "status": status or "active", "priority": priority, "source": source})

    # Clean tasks for JSON
    clean_tasks = []
    for t in tasks:
        dep = t.get("depends_on", "")
        if isinstance(dep, list): dep = ", ".join(str(d) for d in dep)
        eff = t.get("effort", "")
        if isinstance(eff, dict): eff = eff.get("size", "")
        clean_tasks.append({"id": t["_file"].replace(".md",""), "name": t.get("name",""), "status": t.get("status","open"),
                           "depends_on": dep, "effort": eff, "created": t.get("created",""), "updated": t.get("updated","")})

    return {
        "project_name": state.get("project_name", "Project"),
        "phase": state.get("phase", 0),
        "phase_name": state.get("phase_name", "Setup"),
        "metrics": {"total_reqs": len(reqs), "total_tasks": total_tasks, "done_tasks": done, "active_tasks": active,
                    "blocked": len(blockers), "pct": round(done/total_tasks*100) if total_tasks else 0,
                    "signoff_approved": sum(1 for s in signoff if s["status"].lower()=="approved"), "signoff_total": len(signoff),
                    "deliv_done": sum(1 for d in deliverables if d["status"].lower()=="approved"), "deliv_total": len(deliverables),
                    "personas": len(personas)},
        "requirements": clean_reqs,
        "tasks": clean_tasks,
        "personas": [{"name": p.get("name", p["_file"]), "type": p.get("type",""), "req": p.get("requirement","")} for p in personas],
        "stories": [{"id": s["_file"].replace(".md",""), "name": s.get("name",""), "status": s.get("status","open")} for s in stories],
        "signoff": signoff,
        "deliverables": deliverables,
        "blockers": blockers,
        "audit": audit,
        "decisions": decisions,
        "questions": questions,
        "active_epic": active_epic,
        "prd_exists": os.path.exists("specs/prd/prd.md"),
        "timestamp": datetime.now().isoformat(),
    }

# ============================================================
# HTML Dashboard (Single Page App)
# ============================================================

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PM Dashboard</title>
<style>
:root {
  --navy: #1B2A4A; --navy-lt: #2C3E6B; --steel: #4A5568; --slate: #2D3748;
  --bg: #F7FAFC; --white: #FFFFFF; --border: #E2E8F0; --border-dk: #CBD5E0;
  --green: #C6F6D5; --green-dk: #22543D; --blue: #BEE3F8; --blue-dk: #2A4365;
  --red: #FED7D7; --red-dk: #742A2A; --yellow: #FEFCBF; --yellow-dk: #744210;
  --purple: #E9D8FD; --purple-dk: #44337A; --metric-bg: #EBF8FF;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--slate); }

/* Header */
.header { background: var(--navy); color: white; padding: 20px 32px; }
.header h1 { font-size: 24px; font-weight: 600; }
.header .sub { color: #A0AEC0; font-size: 13px; margin-top: 4px; }
.header .live { display: inline-block; width: 8px; height: 8px; background: #68D391; border-radius: 50%; margin-right: 6px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

/* Nav */
.nav { background: var(--navy-lt); padding: 0 32px; display: flex; gap: 0; overflow-x: auto; }
.nav button { background: none; border: none; color: #A0AEC0; padding: 12px 20px; font-size: 13px; cursor: pointer; white-space: nowrap; border-bottom: 2px solid transparent; transition: all 0.2s; }
.nav button:hover { color: white; background: rgba(255,255,255,0.05); }
.nav button.active { color: white; border-bottom-color: #63B3ED; }

/* Content */
.content { max-width: 1400px; margin: 0 auto; padding: 24px 32px; }

/* Search bar */
.search-bar { display: flex; gap: 12px; margin-bottom: 24px; align-items: center; }
.search-bar input { flex: 1; padding: 10px 16px; border: 1px solid var(--border-dk); border-radius: 8px; font-size: 14px; background: white; outline: none; }
.search-bar input:focus { border-color: var(--navy); box-shadow: 0 0 0 3px rgba(27,42,74,0.1); }
.search-bar select { padding: 10px 12px; border: 1px solid var(--border-dk); border-radius: 8px; font-size: 13px; background: white; }
.search-bar .count { color: var(--steel); font-size: 13px; white-space: nowrap; }

/* Metrics grid */
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
.metric-card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 20px; text-align: center; transition: box-shadow 0.2s; }
.metric-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.metric-card .value { font-size: 32px; font-weight: 700; color: var(--navy); }
.metric-card .label { font-size: 12px; color: var(--steel); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }

/* Phase pipeline */
.pipeline { display: flex; gap: 4px; margin-bottom: 24px; }
.pipeline .phase { flex: 1; text-align: center; padding: 12px 8px; border-radius: 8px; font-size: 12px; font-weight: 600; }
.pipeline .phase.done { background: var(--green); color: var(--green-dk); }
.pipeline .phase.current { background: var(--blue); color: var(--blue-dk); }
.pipeline .phase.upcoming { background: var(--border); color: var(--steel); }
.pipeline .phase .num { font-size: 10px; opacity: 0.7; }

/* Section */
.section { margin-bottom: 24px; }
.section-title { font-size: 14px; font-weight: 600; color: var(--navy); text-transform: uppercase; letter-spacing: 0.5px; padding: 12px 0; border-bottom: 2px solid var(--navy); margin-bottom: 16px; }

/* Table */
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
th { background: var(--navy); color: white; padding: 12px 16px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; text-align: left; font-weight: 600; }
td { padding: 10px 16px; border-bottom: 1px solid var(--border); font-size: 13px; }
tr:hover td { background: #EDF2F7; }
tr:nth-child(even) td { background: var(--bg); }
tr:nth-child(even):hover td { background: #EDF2F7; }

/* Status badge */
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.badge.done, .badge.completed, .badge.closed, .badge.approved { background: var(--green); color: var(--green-dk); }
.badge.active, .badge.in-progress { background: var(--blue); color: var(--blue-dk); }
.badge.blocked, .badge.needs-decision { background: var(--red); color: var(--red-dk); }
.badge.draft, .badge.open, .badge.backlog { background: var(--yellow); color: var(--yellow-dk); }
.badge.review, .badge.in-review { background: var(--purple); color: var(--purple-dk); }

/* Cards grid */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.card { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.card .card-title { font-weight: 600; color: var(--navy); margin-bottom: 8px; }
.card .card-meta { font-size: 12px; color: var(--steel); }
.card .card-body { font-size: 13px; margin-top: 8px; }

/* Detail pairs */
.details { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 24px; }
.detail { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; }
.detail .dl { font-size: 11px; color: var(--steel); text-transform: uppercase; }
.detail .dv { font-size: 14px; font-weight: 600; color: var(--slate); margin-top: 2px; }

/* Activity feed */
.feed-item { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.feed-item .time { color: var(--steel); font-size: 11px; white-space: nowrap; min-width: 140px; }
.feed-item .action { font-weight: 500; }

/* Tab panels */
.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* Responsive */
@media (max-width: 768px) {
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .details { grid-template-columns: 1fr; }
  .pipeline { flex-wrap: wrap; }
  .content { padding: 16px; }
}
</style>
</head>
<body>

<div class="header">
  <h1 id="project-name">Loading...</h1>
  <div class="sub"><span class="live"></span>Live Dashboard | <span id="last-update"></span></div>
</div>

<div class="nav" id="nav">
  <button class="active" data-tab="dashboard">Dashboard</button>
  <button data-tab="requirements">Requirements</button>
  <button data-tab="tasks">Tasks</button>
  <button data-tab="deliverables">Deliverables</button>
  <button data-tab="signoff">Sign-Off</button>
  <button data-tab="blockers">Blockers</button>
  <button data-tab="activity">Activity</button>
</div>

<div class="content">

  <!-- DASHBOARD -->
  <div class="tab-panel active" id="tab-dashboard">
    <div class="metrics" id="metrics"></div>
    <div class="section"><div class="section-title">Phase Progress</div><div class="pipeline" id="pipeline"></div></div>
    <div class="section"><div class="section-title">Project Details</div><div class="details" id="details"></div></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
      <div class="section"><div class="section-title">Key Decisions</div><div id="decisions"></div></div>
      <div class="section"><div class="section-title">Open Questions</div><div id="questions"></div></div>
    </div>
  </div>

  <!-- REQUIREMENTS -->
  <div class="tab-panel" id="tab-requirements">
    <div class="search-bar">
      <input type="text" id="req-search" placeholder="Search requirements...">
      <select id="req-filter"><option value="">All Status</option><option value="active">Active</option><option value="needs-decision">Needs Decision</option></select>
      <span class="count" id="req-count"></span>
    </div>
    <table><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Priority</th><th>Source</th></tr></thead><tbody id="req-table"></tbody></table>
  </div>

  <!-- TASKS -->
  <div class="tab-panel" id="tab-tasks">
    <div class="search-bar">
      <input type="text" id="task-search" placeholder="Search tasks...">
      <select id="task-filter"><option value="">All Status</option><option value="open">Open</option><option value="in-progress">In Progress</option><option value="closed">Closed</option><option value="blocked">Blocked</option></select>
      <span class="count" id="task-count"></span>
    </div>
    <table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Depends On</th><th>Effort</th><th>Updated</th></tr></thead><tbody id="task-table"></tbody></table>
  </div>

  <!-- DELIVERABLES -->
  <div class="tab-panel" id="tab-deliverables">
    <div class="search-bar">
      <input type="text" id="deliv-search" placeholder="Search deliverables...">
      <select id="deliv-filter"><option value="">All Status</option><option value="Not Started">Not Started</option><option value="In Progress">In Progress</option><option value="Approved">Approved</option></select>
      <span class="count" id="deliv-count"></span>
    </div>
    <table><thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Owner</th><th>Due</th><th>Status</th></tr></thead><tbody id="deliv-table"></tbody></table>
  </div>

  <!-- SIGN-OFF -->
  <div class="tab-panel" id="tab-signoff">
    <div class="cards" id="signoff-cards"></div>
  </div>

  <!-- BLOCKERS -->
  <div class="tab-panel" id="tab-blockers">
    <div id="blocker-list"></div>
  </div>

  <!-- ACTIVITY -->
  <div class="tab-panel" id="tab-activity">
    <div id="activity-feed"></div>
  </div>

</div>

<script>
let DATA = {};

// Tab switching
document.getElementById('nav').addEventListener('click', e => {
  if (e.target.tagName !== 'BUTTON') return;
  document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  e.target.classList.add('active');
  document.getElementById('tab-' + e.target.dataset.tab).classList.add('active');
});

function badge(status) {
  const s = (status||'').toLowerCase().replace(/[_ ]/g, '-');
  const cls = {'closed':'done','completed':'done','done':'done','approved':'done',
    'in-progress':'in-progress','active':'in-progress','in-review':'review','review':'review',
    'blocked':'blocked','needs-decision':'blocked','draft':'draft','open':'open','backlog':'draft','not-started':'draft'}[s] || 'draft';
  return `<span class="badge ${cls}">${status||'—'}</span>`;
}

function renderDashboard(d) {
  document.getElementById('project-name').textContent = d.project_name;
  document.title = d.project_name + ' — Dashboard';
  document.getElementById('last-update').textContent = new Date(d.timestamp).toLocaleString();

  const m = d.metrics;
  document.getElementById('metrics').innerHTML = [
    ['total_reqs','Requirements'], ['total_tasks','Total Tasks'], ['done_tasks','Completed'],
    ['active_tasks','In Progress'], ['blocked','Blocked'], ['pct','Completion %']
  ].map(([k,l]) => `<div class="metric-card"><div class="value">${k==='pct'?m[k]+'%':m[k]}</div><div class="label">${l}</div></div>`).join('');

  const phases = ['Ingest','Brainstorm','Document','Plan','Execute','Track'];
  document.getElementById('pipeline').innerHTML = phases.map((p,i) => {
    const cls = i < d.phase ? 'done' : (i === d.phase ? 'current' : 'upcoming');
    return `<div class="phase ${cls}"><div class="num">Phase ${i}</div>${p}</div>`;
  }).join('');

  document.getElementById('details').innerHTML = [
    ['Active Epic', d.active_epic||'None'], ['PRD', d.prd_exists?'Created':'Not created'], ['Personas', m.personas+' defined'],
    ['Sign-Off', m.signoff_approved+'/'+m.signoff_total+' approved'], ['Deliverables', m.deliv_done+'/'+m.deliv_total+' approved'], ['Phase', 'Phase '+d.phase+': '+d.phase_name],
  ].map(([l,v]) => `<div class="detail"><div class="dl">${l}</div><div class="dv">${v}</div></div>`).join('');

  document.getElementById('decisions').innerHTML = (d.decisions.length ? d.decisions.map(d => `<div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:13px">${d}</div>`).join('') : '<div style="color:var(--steel);font-size:13px">No decisions recorded</div>');
  document.getElementById('questions').innerHTML = (d.questions.length ? d.questions.map(q => `<div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:13px">${q}</div>`).join('') : '<div style="color:var(--steel);font-size:13px">No open questions</div>');
}

function renderTable(tbodyId, items, cols, countId, searchId, filterId, filterKey) {
  const search = document.getElementById(searchId)?.value.toLowerCase() || '';
  const filter = document.getElementById(filterId)?.value || '';
  let filtered = items.filter(item => {
    const text = cols.map(c => String(item[c]||'')).join(' ').toLowerCase();
    if (search && !text.includes(search)) return false;
    if (filter && (item[filterKey]||'').toLowerCase().replace(/[_ ]/g,'-') !== filter.toLowerCase().replace(/[_ ]/g,'-')) return false;
    return true;
  });
  document.getElementById(countId).textContent = filtered.length + ' of ' + items.length;
  document.getElementById(tbodyId).innerHTML = filtered.map(item =>
    '<tr>' + cols.map(c => {
      const v = item[c] || '—';
      return c === filterKey ? `<td>${badge(v)}</td>` : `<td>${v}</td>`;
    }).join('') + '</tr>'
  ).join('') || '<tr><td colspan="99" style="text-align:center;color:var(--steel)">No data</td></tr>';
}

function renderSignoff(docs) {
  document.getElementById('signoff-cards').innerHTML = docs.map(d =>
    `<div class="card"><div class="card-title">${d.name}</div><div>${badge(d.status)}</div>` +
    (d.approved_by ? `<div class="card-meta" style="margin-top:8px">Approved by: ${d.approved_by}</div>` : '') +
    (d.updated ? `<div class="card-meta">Updated: ${d.updated}</div>` : '') +
    '</div>'
  ).join('') || '<div style="color:var(--steel)">No sign-off documents</div>';
}

function renderBlockers(blockers, tasks) {
  let html = '';
  if (blockers.length) {
    html += '<div class="section-title">Manual Blocks</div>';
    html += blockers.map(b => `<div class="card" style="margin-bottom:12px;border-left:4px solid var(--red-dk)"><div class="card-title">${b.description||'Unknown'}</div><div class="card-meta">Since: ${b.since||'—'} | Blocked by: ${b.blocked_by||'—'}</div></div>`).join('');
  }
  const depBlocked = tasks.filter(t => t.status.toLowerCase() === 'open' && t.depends_on);
  if (depBlocked.length) {
    html += '<div class="section-title" style="margin-top:16px">Dependency Blocks</div>';
    html += depBlocked.map(t => `<div class="card" style="margin-bottom:12px;border-left:4px solid var(--yellow-dk)"><div class="card-title">Task ${t.id}: ${t.name}</div><div class="card-meta">Waiting on: ${t.depends_on}</div></div>`).join('');
  }
  if (!blockers.length && !depBlocked.length) html = '<div style="color:var(--steel);font-size:14px;padding:24px;text-align:center">No blockers</div>';
  document.getElementById('blocker-list').innerHTML = html;
}

function renderActivity(audit) {
  document.getElementById('activity-feed').innerHTML = audit.slice().reverse().map(a =>
    `<div class="feed-item"><span class="time">${a.timestamp||''}</span><span class="action">${a.action||a.skill||''}</span><span>${(a.artifacts_created||[]).join(', ')}</span></div>`
  ).join('') || '<div style="color:var(--steel)">No activity</div>';
}

function refresh() {
  fetch('/api/data').then(r => r.json()).then(d => {
    DATA = d;
    renderDashboard(d);
    renderTable('req-table', d.requirements, ['id','title','status','priority','source'], 'req-count', 'req-search', 'req-filter', 'status');
    renderTable('task-table', d.tasks, ['id','name','status','depends_on','effort','updated'], 'task-count', 'task-search', 'task-filter', 'status');
    renderTable('deliv-table', d.deliverables, ['id','name','role','owner','due','status'], 'deliv-count', 'deliv-search', 'deliv-filter', 'status');
    renderSignoff(d.signoff);
    renderBlockers(d.blockers, d.tasks);
    renderActivity(d.audit);
  }).catch(e => console.error('Refresh failed:', e));
}

// Event listeners for search/filter
['req-search','req-filter','task-search','task-filter','deliv-search','deliv-filter'].forEach(id => {
  document.getElementById(id)?.addEventListener('input', () => {
    renderTable('req-table', DATA.requirements, ['id','title','status','priority','source'], 'req-count', 'req-search', 'req-filter', 'status');
    renderTable('task-table', DATA.tasks, ['id','name','status','depends_on','effort','updated'], 'task-count', 'task-search', 'task-filter', 'status');
    renderTable('deliv-table', DATA.deliverables, ['id','name','role','owner','due','status'], 'deliv-count', 'deliv-search', 'deliv-filter', 'status');
  });
});

// Initial load + auto-refresh every 5s
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>"""


# ============================================================
# HTTP Server
# ============================================================

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(get_all_data(), default=str).encode())
        elif parsed.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # Suppress request logs


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    port = PORT
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    pname = read_json(".pm/state.json").get("project_name", "Project")

    print(f"""
  ┌─────────────────────────────────────────┐
  │  PM Dashboard — {pname:<23} │
  │                                         │
  │  http://localhost:{port:<24}│
  │                                         │
  │  Auto-refreshes every 5 seconds         │
  │  Press Ctrl+C to stop                   │
  └─────────────────────────────────────────┘
""")

    try:
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")
    except:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.server_close()
