#!/usr/bin/env python3
"""
PM Workflow — Live Dashboard Server
Reads from .pm/project-data.json (synced by sync-project-data.py).
Auto-syncs on startup and every 30 seconds.

Usage:
  python3 .pm/scripts/dashboard-server.py
  python3 .pm/scripts/dashboard-server.py --port 8080
"""

import json, os, sys, subprocess, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse

PORT = 3000
DATA_FILE = ".pm/project-data.json"
SYNC_SCRIPT = ".pm/scripts/sync-project-data.py"

def read_json(path):
    try:
        with open(path, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def do_sync():
    """Run sync script to rebuild project-data.json."""
    try:
        subprocess.run([sys.executable, SYNC_SCRIPT], capture_output=True, timeout=10)
    except Exception as e:
        print(f"  Sync error: {e}")

def auto_sync_loop():
    """Background thread: re-sync every 30 seconds."""
    while True:
        time.sleep(30)
        do_sync()

# ============================================================
# HTML — same corporate dashboard, reads from /api/data
# ============================================================

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>PM Dashboard</title>
<style>
:root{--navy:#1B2A4A;--navy-lt:#2C3E6B;--steel:#4A5568;--slate:#2D3748;--bg:#F7FAFC;--white:#FFF;--border:#E2E8F0;--bdk:#CBD5E0;--green:#C6F6D5;--gdk:#22543D;--blue:#BEE3F8;--bdk2:#2A4365;--red:#FED7D7;--rdk:#742A2A;--yellow:#FEFCBF;--ydk:#744210;--purple:#E9D8FD;--pdk:#44337A;--met:#EBF8FF}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--slate)}
.hdr{background:var(--navy);color:#fff;padding:20px 32px}.hdr h1{font-size:22px;font-weight:600}.hdr .sub{color:#A0AEC0;font-size:12px;margin-top:4px}.hdr .live{display:inline-block;width:8px;height:8px;background:#68D391;border-radius:50%;margin-right:6px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.nav{background:var(--navy-lt);padding:0 24px;display:flex;gap:0;overflow-x:auto;white-space:nowrap}.nav button{background:none;border:none;color:#A0AEC0;padding:10px 14px;font-size:12px;cursor:pointer;border-bottom:2px solid transparent;transition:.2s}.nav button:hover{color:#fff;background:rgba(255,255,255,.05)}.nav button.active{color:#fff;border-bottom-color:#63B3ED}
.ct{max-width:1400px;margin:0 auto;padding:24px 32px}
.sb{display:flex;gap:12px;margin-bottom:20px;align-items:center}.sb input{flex:1;padding:8px 14px;border:1px solid var(--bdk);border-radius:6px;font-size:13px;background:#fff;outline:none}.sb input:focus{border-color:var(--navy);box-shadow:0 0 0 3px rgba(27,42,74,.1)}.sb select{padding:8px;border:1px solid var(--bdk);border-radius:6px;font-size:12px;background:#fff}.sb .cnt{color:var(--steel);font-size:12px;white-space:nowrap}
.mg{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:20px}.mc{background:#fff;border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center;transition:.2s}.mc:hover{box-shadow:0 4px 12px rgba(0,0,0,.08)}.mc .v{font-size:28px;font-weight:700;color:var(--navy)}.mc .l{font-size:11px;color:var(--steel);text-transform:uppercase;letter-spacing:.5px;margin-top:2px}
.pl{display:flex;gap:4px;margin-bottom:20px}.pl .ph{flex:1;text-align:center;padding:10px 6px;border-radius:6px;font-size:11px;font-weight:600}.pl .ph.done{background:var(--green);color:var(--gdk)}.pl .ph.cur{background:var(--blue);color:var(--bdk2)}.pl .ph.up{background:var(--border);color:var(--steel)}.pl .ph .n{font-size:9px;opacity:.7}
.sec{margin-bottom:20px}.st{font-size:13px;font-weight:600;color:var(--navy);text-transform:uppercase;letter-spacing:.5px;padding:10px 0;border-bottom:2px solid var(--navy);margin-bottom:12px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}th{background:var(--navy);color:#fff;padding:10px 14px;font-size:10px;text-transform:uppercase;letter-spacing:.5px;text-align:left;font-weight:600}td{padding:8px 14px;border-bottom:1px solid var(--border);font-size:12px}tr:hover td{background:#EDF2F7}tr:nth-child(even) td{background:var(--bg)}tr:nth-child(even):hover td{background:#EDF2F7}
.bd{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;text-transform:uppercase}
.bd.done,.bd.completed,.bd.closed,.bd.approved{background:var(--green);color:var(--gdk)}.bd.active,.bd.in-progress{background:var(--blue);color:var(--bdk2)}.bd.blocked,.bd.needs-decision{background:var(--red);color:var(--rdk)}.bd.draft,.bd.open,.bd.backlog,.bd.not-started{background:var(--yellow);color:var(--ydk)}.bd.review,.bd.in-review{background:var(--purple);color:var(--pdk)}
.cds{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}.cd{background:#fff;border:1px solid var(--border);border-radius:8px;padding:14px}.cd .ct2{font-weight:600;color:var(--navy);margin-bottom:6px;font-size:13px}.cd .cm{font-size:11px;color:var(--steel);margin-top:4px}
.dt{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px}.di{background:#fff;border:1px solid var(--border);border-radius:8px;padding:10px 14px}.di .dl{font-size:10px;color:var(--steel);text-transform:uppercase}.di .dv{font-size:13px;font-weight:600;color:var(--slate);margin-top:1px}
.fi{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:12px}.fi .tm{color:var(--steel);font-size:10px;white-space:nowrap;min-width:130px}.fi .ac{font-weight:500}
.tp{display:none}.tp.active{display:block}
.sync-info{text-align:right;font-size:10px;color:var(--steel);padding:4px 32px;background:#EDF2F7}
@media(max-width:768px){.mg{grid-template-columns:repeat(3,1fr)}.dt{grid-template-columns:1fr}.pl{flex-wrap:wrap}.ct{padding:16px}}
</style></head><body>
<div class="hdr"><h1 id="pn">Loading...</h1><div class="sub"><span class="live"></span>Live Dashboard | <span id="lu"></span></div></div>
<div class="sync-info">Data source: .pm/project-data.json | Synced: <span id="synced"></span></div>
<div class="nav" id="nav">
<button class="active" data-tab="dashboard">Dashboard</button>
<button data-tab="requirements">Requirements</button>
<button data-tab="prd">PRD</button>
<button data-tab="personas">Personas</button>
<button data-tab="discovery">Discovery</button>
<button data-tab="stories">Stories</button>
<button data-tab="tasks">Tasks</button>
<button data-tab="timeline">Timeline</button>
<button data-tab="deliverables">Deliverables</button>
<button data-tab="signoff">Sign-Off</button>
<button data-tab="blockers">Blockers</button>
<button data-tab="traceability">Traceability</button>
<button data-tab="ingestion">Ingestion</button>
<button data-tab="meetings">Meetings</button>
<button data-tab="activity">Activity</button>
</div>
<div class="ct">
<div class="tp active" id="tab-dashboard"><div class="mg" id="met"></div><div class="sec"><div class="st">Phase Progress</div><div class="pl" id="pip"></div></div><div class="sec"><div class="st">Project Details</div><div class="dt" id="det"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:20px"><div class="sec"><div class="st">Key Decisions</div><div id="dec"></div></div><div class="sec"><div class="st">Open Questions</div><div id="ques"></div></div></div></div>
<div class="tp" id="tab-requirements"><div class="sb"><input id="rs" placeholder="Search requirements..."><select id="rf"><option value="">All</option><option value="active">Active</option><option value="needs-decision">Needs Decision</option></select><span class="cnt" id="rc"></span></div><table><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Priority</th><th>Source</th></tr></thead><tbody id="rt"></tbody></table></div>
<div class="tp" id="tab-prd"><div class="dt" id="pm"></div><div class="sec" style="margin-top:16px"><div class="st">PRD Features</div><table><thead><tr><th>REQ ID</th><th>Feature</th></tr></thead><tbody id="pt"></tbody></table></div></div>
<div class="tp" id="tab-personas"><div class="cds" id="pc"></div></div>
<div class="tp" id="tab-discovery"><div class="sec"><div class="st">Strategy Artifacts</div><div id="sa"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:16px"><div class="sec"><div class="st">Key Decisions</div><div id="dd"></div></div><div class="sec"><div class="st">Open Questions</div><div id="dq"></div></div></div></div>
<div class="tp" id="tab-stories"><div class="sb"><input id="ss" placeholder="Search stories..."><select id="sf"><option value="">All</option><option value="open">Open</option><option value="in-progress">In Progress</option><option value="done">Done</option></select><span class="cnt" id="sc"></span></div><table><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Epic</th></tr></thead><tbody id="stb"></tbody></table></div>
<div class="tp" id="tab-tasks"><div class="sb"><input id="ts" placeholder="Search tasks..."><select id="tf"><option value="">All</option><option value="open">Open</option><option value="in-progress">In Progress</option><option value="closed">Closed</option></select><span class="cnt" id="tc"></span></div><table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Depends On</th><th>Effort</th><th>Updated</th></tr></thead><tbody id="tt"></tbody></table></div>
<div class="tp" id="tab-timeline"><table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Created</th><th>Started</th><th>Completed</th><th>Est. Days</th></tr></thead><tbody id="tlt"></tbody></table></div>
<div class="tp" id="tab-deliverables"><div class="sb"><input id="ds" placeholder="Search deliverables..."><select id="df"><option value="">All</option><option value="Not Started">Not Started</option><option value="In Progress">In Progress</option><option value="Approved">Approved</option></select><span class="cnt" id="dc"></span></div><table><thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Owner</th><th>Due</th><th>Status</th></tr></thead><tbody id="dt2"></tbody></table></div>
<div class="tp" id="tab-signoff"><div class="cds" id="soc"></div></div>
<div class="tp" id="tab-blockers"><div id="bl"></div></div>
<div class="tp" id="tab-traceability"><table><thead><tr><th>REQ IDs</th><th>PRD</th><th>Epic</th><th>Task</th><th>Task Name</th><th>Status</th></tr></thead><tbody id="trt"></tbody></table></div>
<div class="tp" id="tab-ingestion"><div class="cds" id="igc"></div></div>
<div class="tp" id="tab-meetings"><div class="cds" id="mtc"></div></div>
<div class="tp" id="tab-activity"><div id="af"></div></div>
</div>
<script>
let D={};
document.getElementById('nav').addEventListener('click',e=>{if(e.target.tagName!=='BUTTON')return;document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));document.querySelectorAll('.tp').forEach(p=>p.classList.remove('active'));e.target.classList.add('active');document.getElementById('tab-'+e.target.dataset.tab).classList.add('active')});
function bd(s){const c=(s||'').toLowerCase().replace(/[_ ]/g,'-');const m={'closed':'done','completed':'done','done':'done','approved':'done','in-progress':'in-progress','active':'in-progress','in-review':'review','review':'review','blocked':'blocked','needs-decision':'blocked','draft':'draft','open':'open','backlog':'draft','not-started':'draft'};return`<span class="bd ${m[c]||'draft'}">${s||'—'}</span>`}
function lst(items,empty){return items.length?items.map(i=>`<div style="padding:5px 0;border-bottom:1px solid var(--border);font-size:12px">${i}</div>`).join(''):`<div style="color:var(--steel);font-size:12px">${empty}</div>`}
function ftbl(tbId,items,cols,cntId,sId,fId,fk){const s=(document.getElementById(sId)?.value||'').toLowerCase(),f=document.getElementById(fId)?.value||'';let fi=items.filter(i=>{const t=cols.map(c=>String(i[c]||'')).join(' ').toLowerCase();return(!s||t.includes(s))&&(!f||(i[fk]||'').toLowerCase().replace(/[_ ]/g,'-')===f.toLowerCase().replace(/[_ ]/g,'-'))});document.getElementById(cntId).textContent=fi.length+' of '+items.length;document.getElementById(tbId).innerHTML=fi.map(i=>'<tr>'+cols.map(c=>c===fk?`<td>${bd(i[c])}</td>`:`<td>${i[c]||'—'}</td>`).join('')+'</tr>').join('')||'<tr><td colspan="99" style="text-align:center;color:var(--steel)">No data</td></tr>'}
function render(d){
  D=d; const m=d.metrics||{};
  document.getElementById('pn').textContent=d.project_name||'Project';
  document.title=(d.project_name||'Project')+' — Dashboard';
  document.getElementById('lu').textContent=new Date().toLocaleString();
  document.getElementById('synced').textContent=d._synced_at||'never';
  document.getElementById('met').innerHTML=[['total_reqs','Requirements'],['total_tasks','Total Tasks'],['done_tasks','Completed'],['active_tasks','In Progress'],['blocked','Blocked'],['pct','Completion %']].map(([k,l])=>`<div class="mc"><div class="v">${k==='pct'?(m[k]||0)+'%':(m[k]||0)}</div><div class="l">${l}</div></div>`).join('');
  document.getElementById('pip').innerHTML=['Ingest','Brainstorm','Document','Plan','Execute','Track'].map((p,i)=>`<div class="ph ${i<d.phase?'done':i===d.phase?'cur':'up'}"><div class="n">Phase ${i}</div>${p}</div>`).join('');
  document.getElementById('det').innerHTML=[['Active Epic',d.active_epic||'None'],['PRD',d.prd?'Created':'Not created'],['Personas',(m.personas||0)+' defined'],['Sign-Off',(m.signoff_approved||0)+'/'+(m.signoff_total||0)+' approved'],['Deliverables',(m.deliv_done||0)+'/'+(m.deliv_total||0)+' approved'],['Language',(d.language||'en')==='th'?'Thai':'English']].map(([l,v])=>`<div class="di"><div class="dl">${l}</div><div class="dv">${v}</div></div>`).join('');
  document.getElementById('dec').innerHTML=lst(d.decisions||[],'No decisions');
  document.getElementById('ques').innerHTML=lst(d.questions||[],'No questions');
  ftbl('rt',d.requirements||[],['id','title','status','priority','source'],'rc','rs','rf','status');
  const prd=d.prd||{};
  document.getElementById('pm').innerHTML=[['Status',prd.status||'—'],['Created',prd.created||'—'],['Created By',prd.created_by||'—'],['Phase',prd.phase||'—'],['Requirements',(prd.requirements||[]).length],['File',prd.exists!==false?'specs/prd/prd.md':'Not created']].map(([l,v])=>`<div class="di"><div class="dl">${l}</div><div class="dv">${v}</div></div>`).join('');
  document.getElementById('pt').innerHTML=(d.prd_features||[]).length?(d.prd_features||[]).map(f=>`<tr><td>${f.id}</td><td>${f.title}</td></tr>`).join(''):'<tr><td colspan="2" style="text-align:center;color:var(--steel)">No PRD features</td></tr>';
  document.getElementById('pc').innerHTML=(d.personas||[]).length?d.personas.map(p=>`<div class="cd"><div class="ct2">${p.name}</div><div class="cm">Type: ${p.type||'—'} | REQ: ${p.requirement||p.req||'—'}</div><div class="cm">Created: ${p.created||'—'}</div></div>`).join(''):'<div style="color:var(--steel)">No personas yet</div>';
  document.getElementById('sa').innerHTML=(d.strategy_files||[]).length?d.strategy_files.map(f=>`<div style="padding:4px 0;font-size:12px">${f}</div>`).join(''):'<div style="color:var(--steel);font-size:12px">No strategy artifacts yet</div>';
  document.getElementById('dd').innerHTML=lst(d.decisions||[],'No decisions');
  document.getElementById('dq').innerHTML=lst(d.questions||[],'No questions');
  ftbl('stb',d.stories||[],['id','name','status','epic'],'sc','ss','sf','status');
  ftbl('tt',d.tasks||[],['id','name','status','depends_on','effort','updated'],'tc','ts','tf','status');
  document.getElementById('tlt').innerHTML=(d.tasks||[]).length?d.tasks.map(t=>`<tr><td>${t.id}</td><td>${t.name||'—'}</td><td>${bd(t.status)}</td><td>${t.created||'—'}</td><td>${t.started||'—'}</td><td>${t.completed||'—'}</td><td>${t.effort_days||'—'}</td></tr>`).join(''):'<tr><td colspan="7" style="text-align:center;color:var(--steel)">No tasks yet</td></tr>';
  ftbl('dt2',d.deliverables||[],['id','name','role','owner','due','status'],'dc','ds','df','status');
  document.getElementById('soc').innerHTML=(d.signoff||[]).length?d.signoff.map(s=>`<div class="cd"><div class="ct2">${s.name}</div><div>${bd(s.status)}</div>${s.approved_by?`<div class="cm">Approved by: ${s.approved_by}</div>`:''}${s.updated?`<div class="cm">Updated: ${s.updated}</div>`:''}</div>`).join(''):'<div style="color:var(--steel)">No sign-off documents yet</div>';
  let bh='';
  if((d.blockers||[]).length){bh+='<div class="st">Manual Blocks</div>';bh+=d.blockers.map(b=>`<div class="cd" style="margin-bottom:10px;border-left:4px solid var(--rdk)"><div class="ct2">${b.description||'Unknown'}</div><div class="cm">Since: ${b.since||'—'} | Blocked by: ${b.blocked_by||'—'}</div></div>`).join('')}
  const db=(d.tasks||[]).filter(t=>t.status.toLowerCase()==='open'&&t.depends_on);
  if(db.length){bh+='<div class="st" style="margin-top:12px">Dependency Blocks</div>';bh+=db.map(t=>`<div class="cd" style="margin-bottom:10px;border-left:4px solid var(--ydk)"><div class="ct2">Task ${t.id}: ${t.name}</div><div class="cm">Waiting on: ${t.depends_on}</div></div>`).join('')}
  if(!(d.blockers||[]).length&&!db.length) bh='<div style="color:var(--steel);font-size:13px;padding:20px;text-align:center">No blockers</div>';
  document.getElementById('bl').innerHTML=bh;
  document.getElementById('trt').innerHTML=(d.traceability||[]).length?d.traceability.map(t=>`<tr><td>${t.reqs||'—'}</td><td>${t.prd||'—'}</td><td>${t.epic||'—'}</td><td>${t.task_id||'—'}</td><td>${t.task_name||'—'}</td><td>${bd(t.status)}</td></tr>`).join(''):'<tr><td colspan="6" style="text-align:center;color:var(--steel)">No traceability data yet</td></tr>';
  document.getElementById('igc').innerHTML=(d.ingestions||[]).length?d.ingestions.map(ig=>`<div class="cd"><div class="ct2">Ingestion: ${ig.date}</div><div class="cm">Source: ${ig.source||'—'}</div><div class="cm">Type: ${ig.type||'—'}</div><div class="cm">REQs: ${ig.reqs||'—'}</div></div>`).join(''):'<div style="color:var(--steel)">No ingestions yet</div>';
  document.getElementById('mtc').innerHTML=(d.meetings||[]).length?d.meetings.map(m=>`<div class="cd"><div class="ct2">${m.topic}</div><div class="cm">Type: ${m.type||'—'} | Company: ${m.company||'—'}</div><div class="cm">Date: ${m.created||'—'}</div></div>`).join(''):'<div style="color:var(--steel)">No meeting preps yet</div>';
  document.getElementById('af').innerHTML=(d.audit||[]).length?d.audit.slice().reverse().map(a=>`<div class="fi"><span class="tm">${a.timestamp||''}</span><span class="ac">${a.action||a.skill||''}</span><span>${(a.artifacts_created||[]).join(', ')}</span></div>`).join(''):'<div style="color:var(--steel)">No activity yet</div>';
}
['rs','rf','ts','tf','ds','df','ss','sf'].forEach(id=>{document.getElementById(id)?.addEventListener('input',()=>render(D))});
function refresh(){fetch('/api/data').then(r=>r.json()).then(render).catch(e=>console.error(e))}
refresh();setInterval(refresh,5000);
</script></body></html>"""

# ============================================================
# HTTP Server
# ============================================================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/api/data":
            # Read from project-data.json — no markdown parsing
            data = read_json(DATA_FILE)
            data["_served_at"] = datetime.now().isoformat()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())
        elif p == "/api/sync":
            do_sync()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "synced"}).encode())
        elif p in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        else:
            self.send_error(404)
    def log_message(self, *a): pass

if __name__ == "__main__":
    port = PORT
    if "--port" in sys.argv:
        i = sys.argv.index("--port")
        if i+1 < len(sys.argv): port = int(sys.argv[i+1])

    # Initial sync
    print("  Syncing project data...")
    do_sync()

    # Start background sync thread
    t = threading.Thread(target=auto_sync_loop, daemon=True)
    t.start()

    pname = read_json(".pm/state.json").get("project_name", "Project")
    print(f"\n  PM Dashboard — {pname}")
    print(f"  http://localhost:{port}")
    print(f"  Data: .pm/project-data.json (auto-syncs every 30s)")
    print(f"  Ctrl+C to stop\n")

    try:
        import webbrowser; webbrowser.open(f"http://localhost:{port}")
    except: pass
    try:
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
