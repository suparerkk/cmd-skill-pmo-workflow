# Generate Report — XLSX Project Status Export

Export the entire project state as a formatted Excel spreadsheet with 15 tabs covering every phase.

## When to Use

User says:
- "generate report"
- "export status"
- "create xlsx report"
- "export to spreadsheet"
- "I need a status report for the client"
- "export project to Excel"

## Behavior

### 1. Check Prerequisites

Verify openpyxl is installed:
```bash
python3 -c "import openpyxl; print('OK')" 2>/dev/null
```

If not installed:
```
⚠️  openpyxl is required for XLSX reports.
   Install: pip install openpyxl

   Or I can generate CSV files instead (no formatting).
```

### 2. Run Script

This is a **deterministic operation** — run the Python script directly, no LLM reasoning needed:

```bash
python3 .pm/scripts/generate-report.py
```

Custom filename:
```bash
python3 .pm/scripts/generate-report.py --output quarterly-review.xlsx
```

### 3. Output

```
✅ Report generated: specs/reports/status-report-2026-04-02.xlsx
   15 tabs | 2026-04-02 14:30

   Open in Excel or upload to Google Sheets.
```

## What's in the Report

| Tab | Content | Source |
|-----|---------|--------|
| Dashboard | Phase progress, key metrics, summary | `.pm/state.json`, `.pm/context.md` |
| Requirements | All REQs with ID, title, status, priority, source | `specs/requirements.md` |
| PRD Summary | Features from PRD with priority and REQ links | `specs/prd/prd.md` |
| Personas | All personas with type and linked REQ | `specs/personas/*.md` |
| Discovery & Strategy | Key decisions, open questions, strategy artifacts | `.pm/context.md`, `strategy/` |
| User Stories | All stories with acceptance criteria links | `specs/stories/us-*.md` |
| Epic & Tasks | All tasks with status, dependencies, effort | `specs/epics/*/` |
| Timeline | Tasks with created/started/completed dates and effort | `specs/epics/*/` |
| Deliverables | External deliverables with owner, due, status | `specs/deliverable-tracker.md` |
| Sign-Off Status | Client approval documents with status | `specs/srs/`, `specs/design/`, etc. |
| Risks & Blockers | Manual blocks + dependency blocks | `.pm/state.json`, task files |
| Traceability | REQ → PRD → Epic → Task mapping | All frontmatter |
| Ingestion Log | What was ingested, when, REQ IDs created | `.pm/ingestion-log.md` |
| Meeting Prep | Meeting topics, types, companies, attendees | `.pm/meeting-prep-*.md` |
| Activity Log | Last 50 actions from audit trail | `.pm/audit.log` |

## Formatting

- **Headers:** Dark gray background, white bold text, frozen row
- **Status cells:** Color-coded (green=done, blue=active, red=blocked, yellow=draft)
- **Alternating rows:** Light gray for readability
- **Column widths:** Pre-set per tab for readability without manual adjustment
- **Template-based:** Same layout every time for consistency across reports

## Key Design Decisions

1. **Script-based, not LLM-based** — runs as Python script, zero token cost
2. **Template consistency** — hardcoded column definitions ensure every report looks identical
3. **CSV fallback** — if openpyxl isn't installed, generates importable CSV files
4. **Date-stamped** — default filename includes generation date for versioning
5. **Google Sheets compatible** — xlsx format imports directly to Google Sheets
