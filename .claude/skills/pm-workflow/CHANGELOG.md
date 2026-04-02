# Changelog

All notable changes to the PM Workflow skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed
- **Broken symlinks in init** — `admin.md` now includes explicit `ln -sf` commands with correct relative path (`../../.claude/...`, 2 levels up from `.pm/scripts/`). Previously the AI guessed `../../../` (3 levels) which produced broken symlinks. Step numbering also fixed (was duplicate "3", now 1-5)
- **Dashboard tab persistence on refresh** — `dashboard-server.py` now stores the active tab in the URL hash (`#tasks`, `#requirements`, etc.). Refreshing the page restores the last viewed tab instead of resetting to Dashboard

### Added
- **Write-through architecture for project-data.json** — each workflow phase now writes structured data directly to `.pm/project-data.json` via `update-project-data.py` helper script. Eliminates fragile markdown frontmatter parsing. Dashboard and report read JSON directly with no sync needed. Updated: `admin.md`, `ingest.md`, `brainstorm.md`, `document.md`, `plan.md`, `execute.md`, `track.md`, `generate-document.md`
- **`update-project-data.py` helper script** — CLI tool with subcommands: `init`, `set`, `merge`, `replace`, `append`, `update-task`, `update-deliverable`, `update-signoff`, `link-stories`, `recalc`. Atomic writes, file locking, auto-metrics recalculation after every mutation
- **`sync-project-data.py --verify` flag** — compares rebuilt data against current `project-data.json` and reports mismatches. Script repurposed as recovery/rebuild tool
- **Document language selection** — users are asked which language (English/Thai) before generating any document (SRS, user journey, system design, test plan, etc.) in `generate-document.md` and `document.md`
- **Meeting prep PM skills** — `meeting-prep.md` now optionally runs `/company-research` (when company name provided), `/discovery-interview-prep` (for discovery/kickoff meetings), and `/jobs-to-be-done` (for discovery meetings) to sharpen question quality
- **Source file copying on ingest** — `ingest.md` now copies source files to `specs/sources/` before parsing, so traceability is never broken by moved/deleted originals. Traceability frontmatter includes both `source` (local copy) and `original_path`
- **`specs/sources/` directory** — added to `conventions.md` directory structure for ingested source file storage
- **`install.sh`** — simple copy script to install the skill into any project
- **Installation section in README.md** — added clone + install instructions
- **Story column in Tasks** — `dashboard-server.py` and `generate-report.py` now show Story linkage in the Epic & Tasks tab. `sync-project-data.py` builds a reverse lookup from stories to enrich each task with its linked story ID
- **Story in Traceability** — traceability chain now includes Story: REQ → PRD → Epic → **Story** → Task. Updated in `sync-project-data.py`, `dashboard-server.py`, and `generate-report.py`
- **Mandatory story per task** — `plan.md` Step 4 now requires one user story per task (no optional "for each task that needs it"). Includes validation check: count(tasks) must equal count(stories). Missing stories are created before proceeding
- **Orphan Tasks metric** — `sync-project-data.py` computes `orphan_tasks` (tasks with no linked story). Shown in dashboard metrics and XLSX report Dashboard tab as a data quality safety net

### Changed
- **Centralized project-data.json** — all dashboard and report data now reads from `.pm/project-data.json` instead of parsing markdown files. `sync-project-data.py` scans all artifacts and rebuilds the JSON. Dashboard auto-syncs every 30s, report auto-syncs before generating. Eliminates fragile markdown regex parsing.
- **Default language setting** — `language` field in `state.json`, set during `/pm-workflow init`. Used as default for all document generation (SRS, user journeys, system design, etc.). Priority: user request override > project default > ask. Updated in admin.md, conventions.md, generate-document.md, document.md.
- **Project cleanup script** — `cleanup.sh` removes all project state (.pm/, specs/, discovery/, strategy/) so you can start fresh with `/pm-workflow init`. Requires double confirmation: first y/N, then type project name (or DELETE). Shows file count before deleting.
- **Live web dashboard (15 tabs)** — `dashboard-server.py` runs a local web server at http://localhost:3000 with auto-refresh every 5s. All 15 tabs match XLSX report: Dashboard, Requirements, PRD, Personas, Discovery & Strategy, User Stories, Tasks, Timeline, Deliverables, Sign-Off, Blockers, Traceability, Ingestion Log, Meetings, Activity. Search and filter on Requirements, Tasks, Stories, Deliverables. Zero external dependencies.
- **Project name** — `project_name` field added to `state.json`, set during `/pm-workflow init`. Used in XLSX report dashboard title and filename (e.g., `notification-system-status-2026-04-02.xlsx`). Updated in admin.md, conventions.md, and generate-report.py.
- **XLSX report generator (corporate template)** — `generate-report.py` script produces a formatted 15-tab Excel spreadsheet covering all phases (Dashboard, Requirements, PRD Summary, Personas, Discovery & Strategy, User Stories, Epic & Tasks, Timeline, Deliverables, Sign-Off Status, Risks & Blockers, Traceability, Ingestion Log, Meeting Prep, Activity Log). Template-based for consistency, runs locally with zero token cost, falls back to CSV if openpyxl not installed. Triggered by "generate report" or "export to spreadsheet".
- **`generate-report.md`** — reference doc for XLSX report generation with intent triggers
- **Fixed duplicate Step 5 in `document.md`** — removed premature "Update State" between Create Personas and Create SRS. Steps now flow: 1-Read, 2-Strategy, 3-PRD, 4-Personas, 5-SRS, 6-User Journey, 7-Update State
- **Fixed "5-phase" → "6-phase"** — corrected terminology across SKILL.md, README.md, CHANGELOG.md to accurately count all 6 phases (Ingest → Brainstorm → Document → Plan → Execute → Track)
- **README.md overhaul** — updated version to 1.1.0, fixed workspace structure to match `specs/` convention, added new features (spec drift, admin commands, language selection), removed duplicate Installation section, fixed sign-off reference from nonexistent `sign-off.md` to `generate-document.md`, updated all phase descriptions with new capabilities
- **Brainstorm skills table** — `brainstorm.md` Skills Used section replaced with explicit table showing which skill to run for each context (no more ambiguous "primary/secondary" listing)
- **Skip Phase 1 guidance after ingest** — `ingest.md` Transition section now assesses whether brainstorming is needed or can be skipped based on ingested document completeness
- **Empty personas handling** — `document.md` Step 4 now handles projects with no identifiable user types: offers default persona, skip option, or identify-users prompt
- **Meeting prep skills context note** — `meeting-prep.md` Step 2 clarifies that PM skills run best-effort with limited context during pre-phase meeting prep
- **Critical path analysis in blocked command** — `track.md` blocked output now flags tasks that are both blocked AND blocking others, showing upstream/downstream impact
- **Cross-epic dependency tracking** — `conventions.md` epic frontmatter now includes `depends_on_epic` field to declare that one epic requires another to complete first (e.g., Auth before Payment). Includes example and execution-time check note.
- **Ingest edge cases for large files and design links** — `ingest.md` now handles large binary files (>10MB) with extract-text option, design tool URLs (Figma/Miro) with screenshot + link reference approach, and `specs/sources/` cleanup guidance with `.gitignore` recommendations.
- **PRD-ready check in document.md** — Step 1 now validates requirements have minimum substance (3+ functional, 1+ non-functional, 1+ user type) before creating a PRD. Warns but doesn't block — user can continue with a lightweight PRD.
- **Ingested requirement frontmatter schema** — `conventions.md` now documents the frontmatter format for ingested requirements, including single source, multi-source (merged), superseded, and flagged (needs-decision) variants with field reference table.
- **Enhanced blocked command with dependency status** — `track.md` blocked command now shows both manual blocks (from `/pm-workflow block`) and task dependency blocks (tasks waiting on incomplete dependencies with their actual status: open/in-progress/etc.)
- **Deliverable tracker update command** — `track.md` now supports updating deliverable status, owner, and due date via natural language ("mark DT-001 as in progress", "assign DT-002 to Jane"). Also supports adding new deliverables.
- **`/pm-workflow next-phase`** — validates prerequisites for the next phase and advances. Shows what's missing if prerequisites aren't met. Allows skipping with warning. Supports natural language ("move to next phase", "skip to Phase 4").
- **`/pm-workflow replan <epic-name>`** — regenerates epic tasks after requirements change mid-execution. Preserves completed tasks, flags in-progress tasks for review, regenerates open tasks, adds new tasks for new REQs. Uses `/epic-breakdown-advisor`.
- **`/pm-workflow reopen <task-id>`** — reopens a completed task that needs rework. Updates status, recalculates epic progress, logs reason.
- **`execute.md` spec drift detection** — new Step 3 compares timestamps of requirements/PRD against epic to detect changes since planning. Warns about new/updated REQs, offers continue/replan/review options. Only blocks if drift affects current task's REQ IDs.
- **`execute.md` parallel execution awareness** — Step 4 now checks `parallel` and `conflicts_with` fields, shows status of each blocking dependency, warns on conflicting in-progress tasks. Completion output lists all parallel-ready tasks instead of suggesting only the next sequential one.

### Fixed
- **Standardized artifact paths** — all PRD/epic/task paths now use `specs/prd/` and `specs/epics/` instead of `.claude/prds/` and `.claude/epics/`. All artifacts live under `specs/` for consistency. Updated across: conventions.md, README.md, CHANGELOG.md, deliverables.md, generate-document.md
- **Requirements reconciliation on every ingest** — `ingest.md` Step 5 assigns temporary IDs, Step 6 reconciles against existing REQs (duplicate detection, conflict resolution, multi-source traceability), Step 7 assigns final REQ IDs. Uses `/problem-framing-canvas`, `/jobs-to-be-done`, and `/prioritization-advisor` when reconciliation reveals deeper issues

### Changed
- **`generate-document.md`** — added Step 3 (Ask Language) with rules for body vs frontmatter language; renumbered subsequent steps
- **`document.md`** — SRS (Step 5) and User Journey (Step 6) generation now ask for language before generating
- **`meeting-prep.md`** — added Step 2 (Run Optional PM Skills) with three conditional skills; renumbered Steps 3-7

### Removed
- **Project-level language setting** — removed `language` field from `state.json` schema, `/pm-workflow language` admin command, and Language Setting Intent from `SKILL.md`. Language is now per-document only.

---

## [1.0.0] - 2026-03-30

### Added - Initial Release

**Core Workflow System:**
- 6-phase workflow: Ingest → Brainstorm → Document → Plan → Execute → Track
- Natural language intent detection (no special syntax required)
- Persistent context via `.pm/context.md`
- Immutable audit log via `.pm/audit.log`
- State management via `.pm/state.json`

**Phase 0: Ingest**
- Parse SRS/PRD documents into structured requirements
- Extract requirements from meeting notes/transcripts
- Visual design (Figma/screenshot) parsing → UI requirements
- Architecture/flow diagram parsing → technical requirements
- TOR/RFP parsing → scope + constraints
- User story map/backlog parsing with structure preservation
- Auto-assign REQ IDs with traceability to source
- Create ingestion log for document tracking

**Pre-Phase: Meeting Prep**
- Generate tiered question lists (Must/Should/Nice to Ask)
- Domain-aware question generation
- Red flag detection for each question
- Save prioritized lists to `.pm/meeting-prep-<topic>.md`

**Phase 1: Brainstorm**
- Guided discovery using PM skills
- Problem framing canvas integration
- Discovery interview preparation
- Opportunity solution tree mapping
- Auto-generate `specs/requirements.md` with REQ IDs

**Phase 2: Document**
- PRD creation via `/prd-development`
- Proto-persona generation
- Product strategy session
- Positioning workshop
- Prioritization advisor
- Roadmap planning
- Output: `specs/prd/<name>.md`, `specs/personas/`, `strategy/`

**Phase 3: Plan**
- Epic hypothesis creation with architecture decisions
- Epic breakdown into executable tasks
- User story generation with Gherkin acceptance criteria
- User story splitting for large stories
- User story mapping workshop
- Dependency matrix (depends_on, parallel, conflicts_with)
- Output: `specs/epics/<name>/`, `specs/stories/`

**Phase 4: Execute**
- Spec chain validation (REQ → PRD → Epic → Task)
- Dependency checking before execution
- Implementation according to task specification
- Commit with REQ ID in message
- Progress tracking per task

**Phase 5: Track**
- Deterministic bash scripts for status/standup/search
- `references/scripts/status.sh` — instant project status
- `references/scripts/standup.sh` — daily standup report
- `references/scripts/search.sh` — search requirements + artifacts
- No LLM token cost for tracking operations

**Admin Commands:**
- `/pm-workflow init` — scaffold workspace structure
- `/pm-workflow done` — mark skill complete, update state + audit
- `/pm-workflow trace` — show traceability chain for artifact
- `/pm-workflow block/unblock` — manage blockers

**On-Demand: Sign-Off Documents**
- Generate IEEE 830-style SRS
- System Design Document
- User Journey Diagrams (Mermaid)
- Sequence Diagrams (UML-style)
- API Specification (OpenAPI 3.0)
- Test Plan
- SLA Document
- Data Flow Diagrams

**File Conventions:**
- Detailed frontmatter schemas for all artifacts
- PRD, Epic, Task, Persona, User Story schemas
- Progress tracking frontmatter
- State file JSON schema
- Audit log JSON lines format
- Context file markdown format
- Commit message format with REQ IDs

**Deliverables Catalog:**
- Documented all artifacts produced by each phase
- Lifecycle and ownership for each artifact
- Traceability requirements

**Bash Scripts:**
- `status.sh` — reads state.json + audit.log
- `standup.sh` — generates daily standup
- `search.sh` — searches requirements + artifacts
- All scripts are deterministic (no LLM reasoning)

**Documentation:**
- README.md — comprehensive skill documentation
- CHANGELOG.md — this file
- All reference files for each phase

---

## [Unreleased]

### Planned Features

**Parallel Agent Execution (Future):**
- Multiple agents working on independent tasks
- Git worktree isolation
- Merge conflict resolution
- Parallel execution tracking

**GitHub Integration (Future):**
- Sync epics to GitHub Issues
- Sub-issue relationships
- Worktree creation per epic
- Issue comment progress updates
- PR linking to tasks

**Question Banks (Future):**
- Domain-specific question templates
- SaaS product questions
- Enterprise system questions
- API platform questions
- Integration/migration questions

**Validation Workflows (Future):**
- Requirement validation with stakeholders
- PRD review checklist
- Epic readiness checklist
- Task completeness validation

**Reporting (Future):**
- Velocity tracking
- Burn-down charts
- Epic progress visualization
- Dependency graph visualization

**Templates (Future):**
- Pre-built PRD templates
- Pre-built epic templates
- Pre-built test plan templates
- Industry-specific templates

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-03-30 | Initial release — 6-phase workflow with natural language intent detection |

---

## Upgrade Guide

### From [Unreleased] to 1.0.0

This is the initial release. No upgrade needed.

---

## Deprecation Policy

Features are deprecated with one major version notice:
- **Deprecated in vX.Y:** Still works, warnings logged
- **Removed in v(X+1).Y:** No longer available

---

## Security

### Reporting Security Issues

If you discover a security vulnerability, please:
1. Do not open a public issue
2. Contact the maintainer directly
3. Provide detailed reproduction steps
4. Allow 90 days for fix before disclosure

---

## Migration Guides

### Migrating from Manual PM Workflow

If you have existing PM artifacts:

1. **Run `/pm-workflow init`** to scaffold workspace
2. **Use ingest phase** to parse existing documents:
   ```
   "I have an existing PRD — can you parse it?"
   ```
3. **Validate extracted requirements**
4. **Continue from appropriate phase** (likely Phase 2 or 3)

---

## Known Issues

### v1.0.0

- **Large document ingestion:** Documents >10,000 tokens are processed in sections (not yet implemented)
- **Visual parsing:** OCR accuracy depends on image quality
- **Parallel execution:** Not yet implemented (single-threaded only)
- **GitHub sync:** Not yet implemented (local files only)

---

## Roadmap

### v1.1.0 (Planned)

- Question bank templates
- Enhanced validation workflows
- Improved error messages
- Performance optimizations

### v1.2.0 (Planned)

- GitHub Issues integration
- Worktree support
- Parallel agent execution

### v2.0.0 (Future)

- Web UI for status/standup
- Real-time collaboration
- Advanced reporting and analytics
- Custom phase workflows

---

## Contributing

See README.md for contribution guidelines.

---

## Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Documentation:** README.md + reference files

---

## Acknowledgments

- **CCPM** (https://github.com/automazeio/ccpm) — Inspiration for deterministic bash scripts, 6-phase discipline, natural language triggers
- **Product-Manager-Skills** (https://github.com/deanpeters/Product-Manager-Skills/) — PM skill library
- **Claude Code** — Agent Skills harness
