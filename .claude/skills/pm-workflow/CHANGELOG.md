# Changelog

All notable changes to the PM Workflow skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Document language selection** — users are asked which language (English/Thai) before generating any document (SRS, user journey, system design, test plan, etc.) in `generate-document.md` and `document.md`
- **Meeting prep PM skills** — `meeting-prep.md` now optionally runs `/company-research` (when company name provided), `/discovery-interview-prep` (for discovery/kickoff meetings), and `/jobs-to-be-done` (for discovery meetings) to sharpen question quality
- **Source file copying on ingest** — `ingest.md` now copies source files to `specs/sources/` before parsing, so traceability is never broken by moved/deleted originals. Traceability frontmatter includes both `source` (local copy) and `original_path`
- **`specs/sources/` directory** — added to `conventions.md` directory structure for ingested source file storage
- **`install.sh`** — simple copy script to install the skill into any project
- **Installation section in README.md** — added clone + install instructions
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
- Output: `.claude/prds/<name>.md`, `specs/personas/`, `strategy/`

**Phase 3: Plan**
- Epic hypothesis creation with architecture decisions
- Epic breakdown into executable tasks
- User story generation with Gherkin acceptance criteria
- User story splitting for large stories
- User story mapping workshop
- Dependency matrix (depends_on, parallel, conflicts_with)
- Output: `.claude/epics/<name>/`, `specs/stories/`

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

- **CCPM** (https://github.com/automazeio/ccpm) — Inspiration for deterministic bash scripts, 5-phase discipline, natural language triggers
- **Product-Manager-Skills** (https://github.com/deanpeters/Product-Manager-Skills/) — PM skill library
- **Claude Code** — Agent Skills harness
