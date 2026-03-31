#!/usr/bin/env python3
"""
PM Workflow — Corporate XLSX Report Generator
Reads from .pm/project-data.json (synced by sync-project-data.py).
Auto-syncs before generating.

Usage:
  python3 .pm/scripts/generate-report.py
  python3 .pm/scripts/generate-report.py --output custom-name.xlsx

Requires: pip install openpyxl
"""

import json, os, sys, csv, subprocess
from datetime import datetime, date

OUTPUT_DIR = "specs/reports"
DATA_FILE = ".pm/project-data.json"
SYNC_SCRIPT = ".pm/scripts/sync-project-data.py"

def read_json(path):
    try:
        with open(path, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def do_sync():
    try: subprocess.run([sys.executable, SYNC_SCRIPT], capture_output=True, timeout=10)
    except: pass

def generate_xlsx(output_path, d):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    NAVY, NAVY_LT, STEEL, SLATE = "1B2A4A", "2C3E6B", "4A5568", "2D3748"
    BORDER_C, BG_ALT, BG_SEC, BG_MET, WHITE = "CBD5E0", "F7FAFC", "EDF2F7", "EBF8FF", "FFFFFF"
    STATUS_MAP = {"done":("C6F6D5","22543D"),"complete":("C6F6D5","22543D"),"completed":("C6F6D5","22543D"),
        "closed":("C6F6D5","22543D"),"approved":("C6F6D5","22543D"),"active":("BEE3F8","2A4365"),
        "in-progress":("BEE3F8","2A4365"),"in_progress":("BEE3F8","2A4365"),"in progress":("BEE3F8","2A4365"),
        "in review":("E9D8FD","44337A"),"review":("E9D8FD","44337A"),"blocked":("FED7D7","742A2A"),
        "needs-decision":("FED7D7","742A2A"),"draft":("FEFCBF","744210"),"backlog":("FEFCBF","744210"),
        "open":("FEFCBF","744210"),"not started":("FEFCBF","744210")}

    bdr = Border(left=Side("thin",BORDER_C),right=Side("thin",BORDER_C),top=Side("thin",BORDER_C),bottom=Side("thin",BORDER_C))
    def F(bold=False,color=SLATE,size=10): return Font(bold=bold,color=color,size=size,name="Calibri")
    def BG(c): return PatternFill(start_color=c,end_color=c,fill_type="solid")
    def A(h="left",v="center",wrap=False): return Alignment(horizontal=h,vertical=v,wrap_text=wrap)
    def ss(val):
        s=str(val).lower().strip(); bg,fg=STATUS_MAP.get(s,(WHITE,SLATE))
        return BG(bg),F(bold=True,color=fg,size=9)

    def sheet(ws,title,headers,rows,widths,status_col=None):
        nc=len(headers)
        ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=nc)
        c=ws.cell(row=1,column=1,value=f"  {title}");c.font=F(True,WHITE,13);c.fill=BG(NAVY);c.alignment=A("left")
        ws.row_dimensions[1].height=36
        for ci in range(2,nc+1): ws.cell(row=1,column=ci).fill=BG(NAVY)
        ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=nc)
        c2=ws.cell(row=2,column=1,value=f"  {d.get('project_name','Project')}  |  {datetime.now().strftime('%B %d, %Y')}")
        c2.font=F(color=WHITE,size=9);c2.fill=BG(NAVY_LT);c2.alignment=A("left")
        ws.row_dimensions[2].height=22
        for ci in range(2,nc+1): ws.cell(row=2,column=ci).fill=BG(NAVY_LT)
        ws.row_dimensions[3].height=6
        hr=4; ws.row_dimensions[hr].height=28
        for ci,h in enumerate(headers,1):
            c=ws.cell(row=hr,column=ci,value=h.upper());c.font=F(True,WHITE,9);c.fill=BG(NAVY);c.alignment=A("center","center",True);c.border=bdr
        for ri,row in enumerate(rows):
            ar=hr+1+ri; ws.row_dimensions[ar].height=24
            for ci,val in enumerate(row,1):
                c=ws.cell(row=ar,column=ci,value=val);c.font=F(size=10);c.alignment=A("left","center",True);c.border=bdr
                if status_col and ci==status_col: sf,ff=ss(val);c.fill=sf;c.font=ff;c.alignment=A("center","center")
                else: c.fill=BG(BG_ALT) if ri%2==0 else BG(WHITE)
        for ci,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(ci)].width=w
        ws.freeze_panes=f"A{hr+1}"
        ws.page_setup.orientation="landscape"; ws.page_setup.fitToWidth=1

    # Dashboard
    ws1=wb.active; ws1.title="Dashboard"
    m=d.get("metrics",{})
    # (simplified dashboard — same data as before but from JSON)
    sheet(ws1,"Dashboard",["Metric","Value"],[
        ("Project",d.get("project_name","")),("Phase",f"Phase {d.get('phase',0)}: {d.get('phase_name','')}"),
        ("Requirements",m.get("total_reqs",0)),("Tasks",f"{m.get('done_tasks',0)}/{m.get('total_tasks',0)} complete ({m.get('pct',0)}%)"),
        ("Blocked",m.get("blocked",0)),("Sign-Off",f"{m.get('signoff_approved',0)}/{m.get('signoff_total',0)} approved"),
        ("Deliverables",f"{m.get('deliv_done',0)}/{m.get('deliv_total',0)} approved"),
        ("Personas",m.get("personas",0)),("Language",d.get("language","en")),
        ("Generated",datetime.now().strftime("%Y-%m-%d %H:%M")),
    ],[25,40])

    # Requirements
    ws2=wb.create_sheet("Requirements")
    sheet(ws2,"Requirements",["ID","Title","Status","Priority","Source"],
        [(r["id"],r["title"],r.get("status",""),r.get("priority",""),r.get("source","")) for r in d.get("requirements",[])] or [("—","No requirements","","","")],
        [12,45,14,12,35],status_col=3)

    # PRD
    ws3=wb.create_sheet("PRD Summary")
    sheet(ws3,"PRD Summary",["REQ ID","Feature"],
        [(f["id"],f["title"]) for f in d.get("prd_features",[])] or [("—","No PRD")],
        [14,50])

    # Personas
    ws4=wb.create_sheet("Personas")
    sheet(ws4,"Personas",["Name","Type","REQ","Created"],
        [(p["name"],p.get("type",""),p.get("requirement",p.get("req","")),p.get("created","")) for p in d.get("personas",[])] or [("—","No personas","","")],
        [28,14,14,20])

    # Discovery
    ws5=wb.create_sheet("Discovery & Strategy")
    rows5=[]
    for x in d.get("decisions",[]): rows5.append(("Decision",x))
    for x in d.get("questions",[]): rows5.append(("Open Question",x))
    for x in d.get("strategy_files",[]): rows5.append(("Artifact",x))
    sheet(ws5,"Discovery & Strategy",["Type","Details"],rows5 or [("—","No data")],[18,65])

    # Stories
    ws6=wb.create_sheet("User Stories")
    sheet(ws6,"User Stories",["ID","Title","Status","Epic"],
        [(s["id"],s.get("name",""),s.get("status",""),s.get("epic","")) for s in d.get("stories",[])] or [("—","No stories","","")],
        [14,40,14,35],status_col=3)

    # Tasks
    ws7=wb.create_sheet("Epic & Tasks")
    sheet(ws7,"Epic & Tasks",["ID","Name","Status","Depends On","Effort","Updated"],
        [(t["id"],t.get("name",""),t.get("status",""),t.get("depends_on",""),t.get("effort",""),t.get("updated","")) for t in d.get("tasks",[])] or [("—","No tasks","","","","")],
        [10,35,14,14,10,18],status_col=3)

    # Timeline
    ws8=wb.create_sheet("Timeline")
    sheet(ws8,"Timeline",["ID","Name","Status","Created","Started","Completed","Est. Days"],
        [(t["id"],t.get("name",""),t.get("status",""),t.get("created",""),t.get("started",""),t.get("completed",""),t.get("effort_days","")) for t in d.get("tasks",[])] or [("—","","","","","","")],
        [10,35,14,18,18,18,10],status_col=3)

    # Deliverables
    ws9=wb.create_sheet("Deliverables")
    sheet(ws9,"Deliverables",["ID","Name","Role","Owner","Due","Status"],
        [(x["id"],x["name"],x.get("role",""),x.get("owner",""),x.get("due",""),x.get("status","")) for x in d.get("deliverables",[])] or [("—","No deliverables","","","","")],
        [10,30,14,14,14,14],status_col=6)

    # Sign-off
    ws10=wb.create_sheet("Sign-Off Status")
    sheet(ws10,"Sign-Off Status",["Document","Status","Approved By","Approved Date","Updated"],
        [(s["name"],s.get("status",""),s.get("approved_by",""),s.get("approved_date",""),s.get("updated","")) for s in d.get("signoff",[])] or [("—","","","","")],
        [30,14,20,18,18],status_col=2)

    # Blockers
    ws11=wb.create_sheet("Risks & Blockers")
    rows11=[]
    for b in d.get("blockers",[]): rows11.append(("Manual Block",b.get("description",""),b.get("since",""),b.get("blocked_by","")))
    for t in d.get("tasks",[]):
        if t.get("status","").lower() in ("closed","completed","in-progress"): continue
        if t.get("depends_on"): rows11.append(("Dependency",f"Task {t['id']} waits on {t['depends_on']}","",t.get("depends_on","")))
    sheet(ws11,"Risks & Blockers",["Type","Description","Since","Blocked By"],rows11 or [("None","No blockers","","")],[16,45,14,25])

    # Traceability
    ws12=wb.create_sheet("Traceability")
    sheet(ws12,"Traceability Matrix",["REQ IDs","PRD","Epic","Task","Task Name","Status"],
        [(t.get("reqs",""),t.get("prd",""),t.get("epic",""),t.get("task_id",""),t.get("task_name",""),t.get("status","")) for t in d.get("traceability",[])] or [("","","","","No data","")],
        [14,25,22,10,30,14],status_col=6)

    # Ingestion
    ws13=wb.create_sheet("Ingestion Log")
    sheet(ws13,"Ingestion Log",["Date","Source","Type","REQ IDs"],
        [(i.get("date",""),i.get("source",""),i.get("type",""),i.get("reqs","")) for i in d.get("ingestions",[])] or [("—","No ingestions","","")],
        [18,40,25,25])

    # Meetings
    ws14=wb.create_sheet("Meeting Prep")
    sheet(ws14,"Meeting Prep",["Topic","Type","Company","Created","Attendees"],
        [(x.get("topic",""),x.get("type",""),x.get("company",""),x.get("created",""),x.get("attendees","")) for x in d.get("meetings",[])] or [("—","No meetings","","","")],
        [30,14,20,18,30])

    # Activity
    ws15=wb.create_sheet("Activity Log")
    sheet(ws15,"Activity Log",["Timestamp","Phase","Action","Artifacts","Details"],
        [(a.get("timestamp",""),f"Phase {a.get('phase','')}",a.get("action",a.get("skill","")),", ".join(a.get("artifacts_created",[])),a.get("req_id",a.get("reason",""))) for a in d.get("audit",[])[-50:]] or [("—","","No activity","","")],
        [22,10,25,40,25])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wb.save(output_path)
    return output_path

def generate_csv_fallback(d):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR,"requirements.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["ID","Title","Status","Priority","Source"])
        for r in d.get("requirements",[]): w.writerow([r["id"],r["title"],r.get("status",""),r.get("priority",""),r.get("source","")])
    with open(os.path.join(OUTPUT_DIR,"tasks.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["ID","Name","Status","Depends On","Effort"])
        for t in d.get("tasks",[]): w.writerow([t["id"],t.get("name",""),t.get("status",""),t.get("depends_on",""),t.get("effort","")])
    print(f"CSV files saved to {OUTPUT_DIR}/. Install openpyxl for full XLSX: pip install openpyxl")

if __name__ == "__main__":
    # Sync first
    print("Syncing project data...")
    do_sync()
    d = read_json(DATA_FILE)

    pname = d.get("project_name","Project").lower().replace(" ","-")
    default_file = f"{pname}-status-{date.today().isoformat()}.xlsx"
    output = os.path.join(OUTPUT_DIR, default_file)
    if len(sys.argv) > 2 and sys.argv[1] == "--output":
        output = os.path.join(OUTPUT_DIR, sys.argv[2])

    try:
        import openpyxl
        result = generate_xlsx(output, d)
        print(f"Report generated: {result}")
        print(f"  15 tabs | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    except ImportError:
        print("openpyxl not installed. Generating CSV fallback...")
        generate_csv_fallback(d)
