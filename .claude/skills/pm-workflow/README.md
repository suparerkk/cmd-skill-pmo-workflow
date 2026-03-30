# PM Workflow — Spec-Driven Project Management for Claude Code

A structured project management skill that enforces spec-driven development with persistent context, deterministic bash scripts, and natural language intent detection.

**Version:** 1.0.0
**Author:** Suparerak
**License:** MIT
**Compatible with:** Claude Code, Claude Agent SDK

---

## Quick Start

Just talk naturally — the skill detects intent and routes accordingly.

```
"I have a client meeting tomorrow about notifications"
  → Generates prioritized question list

"I have an SRS from another team"
  → Parses into structured requirements

"I want to build a notification system"
  → Guided discovery → requirements

"parse the notification PRD"
  → Creates structured PRD

"break down the notification epic"
  → Decomposes into executable tasks

"start working on task 001"
  → Begins implementation

"standup"
  → Instant status report (bash script)
```

---

## The 6-Phase Workflow

> **Every line of code must trace back to a specification.**

### Phase 0: 📥 Ingest
Parse existing documents (SRS, PRD, notes, designs, diagrams) into structured requirements.

**Input:** SRS/PRD, meeting notes, Figma screens, architecture diagrams, TOR/RFP
**Output:** `specs/requirements.md` with REQ IDs + traceability to source
**Trigger:** "I have a PRD from another team", "parse this SRS", "ingest these notes"

**Reference:** `references/ingest.md`

---

### Pre-Phase: Meeting Prep
Generate prioritized question lists before client meetings.

**Input:** Meeting context (type, attendees, what's at stake)
**Output:** Tiered question list (Must Ask, Should Ask, Nice to Ask) with red flags
**Trigger:** "I have a client meeting about X", "help me prep for the X meeting"

**Reference:** `references/meeting-prep.md`

---

### Phase 1: 🧠 Brainstorm
Think deeper than comfortable. Ask the hard questions before writing specs.

**Input:** Blank slate idea or gap-filling after ingest
**Output:** `specs/requirements.md` with REQ IDs
**Trigger:** "I want to build X", "help me think through X"

**Skills used:**
- `discovery-process` (main workflow)
- `problem-framing-canvas`
- `discovery-interview-prep`
- `opportunity-solution-tree`

**Reference:** `references/brainstorm.md`

---

### Phase 2: 📝 Document
Write specs that leave nothing to interpretation.

**Input:** `specs/requirements.md`
**Output:**
- `.claude/prds/<name>.md` — Structured PRD
- `specs/personas/*.md` — Proto-personas
- `strategy/positioning.md` — Market positioning
- `strategy/roadmap.md` — Timeline planning

**Trigger:** "create a PRD for X", "document X", "what's the product strategy?"

**Skills used:**
- `product-strategy-session`
- `prd-development`
- `positioning-workshop`
- `prioritization-advisor`
- `roadmap-planning`
- `proto-persona`

**Reference:** `references/document.md`

---

### Phase 3: 📐 Plan
Architect with explicit technical decisions.

**Input:** `.claude/prds/<name>.md`
**Output:**
- `.claude/epics/<name>/epic.md` — Technical epic with architecture decisions
- `.claude/epics/<name>/*.md` — Task files with dependencies
- `specs/stories/us-*.md` — User stories with Gherkin criteria

**Trigger:** "break down the X epic", "decompose X into tasks"

**Skills used:**
- `epic-hypothesis`
- `epic-breakdown-advisor`
- `user-story` + `user-story-splitting`
- `user-story-mapping-workshop`

**Reference:** `references/plan.md`

---

### Phase 4: ⚡ Execute
Build exactly what was specified.

**Input:** Task file from `.claude/epics/<name>/<task>.md`
**Output:** Code commits with REQ ID in message
**Trigger:** "start working on X", "implement X", "work on task X"

**Validation:**
- Checks spec chain exists (REQ → PRD → Epic → Task)
- Validates dependencies are complete
- Implements according to task specification

**Reference:** `references/execute.md`

---

### Phase 5: 📊 Track
Maintain transparent progress at every step.

**Input:** `.pm/state.json` + `.pm/audit.log`
**Output:** Instant status reports, standups, search results
**Trigger:** "standup", "what's blocked", "what's next", "search for X"

**Operations:** All run as **bash scripts** — deterministic, no LLM token cost
- `bash references/scripts/status.sh`
- `bash references/scripts/standup.sh`
- `bash references/scripts/search.sh <query>`

**Reference:** `references/track.md`

---

### On-Demand: Sign-Off Documents
Generate client-facing formal deliverables when needed.

**Trigger:** "generate SRS", "create system design doc", "prepare API spec"

**Deliverables:**
- SRS (Software Requirements Specification) — IEEE 830 format
- System Design Document — Technical architecture
- User Journey Diagrams — Mermaid visual flows
- Sequence Diagrams — UML-style interaction flows
- API Specification — OpenAPI 3.0 YAML
- Test Plan — Formal QA strategy
- SLA Document — Service level agreements

**Reference:** `references/sign-off.md`

---

## Workspace Structure

```
project-root/
├── .pm/
│   ├── context.md              # Persistent project memory
│   ├── state.json              # Current phase, REQ counter, completed skills
│   ├── audit.log               # JSON lines: immutable history
│   ├── ingestion-log.md        # Track ingested documents
│   └── scripts/                # Symlink to references/scripts/
│
├── .claude/
│   ├── prds/                   # Product requirement documents
│   │   └── <feature-name>.md
│   └── epics/                  # Epics and tasks
│       └── <feature-name>/
│           ├── epic.md
│           ├── 001.md          # Task files
│           ├── 002.md
│           └── updates/        # Progress tracking
│               └── 001-progress.md
│
├── specs/
│   ├── requirements.md         # Source of truth — all REQs
│   ├── personas/               # Proto-personas
│   │   └── <name>.md
│   └── stories/                # User stories
│       └── us-001.md
│
├── discovery/                  # Phase 1 artifacts
├── strategy/                   # Phase 2 artifacts
├── validation/                 # Phase 4 artifacts
└── delivery/                   # Phase 5 artifacts
```

---

## Key Features

### 1. Natural Language Intent Detection
No special syntax required. The skill detects intent from conversation and routes to the appropriate workflow phase.

### 2. Persistent Context
`.pm/context.md` serves as Claude's memory for the project — restored at every session start.

### 3. Spec-Driven Development
Every artifact traces back to a requirement. No orphaned deliverables.

**Traceability chain:**
```
REQ-001 → PRD → Epic → Task → Code → Commit
```

**Trace command:**
```bash
/pm-workflow trace .claude/epics/notification-system/001.md
```

### 4. Deterministic Operations (Bash Scripts)
Status, standup, and search run as bash scripts — **fast, consistent, no LLM token cost**.

### 5. Auto-Generated REQ IDs
Requirements are automatically assigned monotonically increasing IDs (REQ-001, REQ-002, etc.) — never reused.

### 6. Audit Trail
`.pm/audit.log` is append-only JSON lines — immutable history of every action.

### 7. 5-Phase Discipline
Enforced workflow: Brainstorm → Document → Plan → Execute → Track

### 8. Client Sign-Off Ready
Generate formal IEEE 830-style SRS, UML diagrams, OpenAPI specs, and test plans on demand.

---

## Installation

### Prerequisites
- **Claude Code** or compatible Agent Skills harness
- **Product-Manager-Skills** from https://github.com/deanpeters/Product-Manager-Skills/
- **Git** — workspace is version-controlled
- **Python 3** — for bash script JSON parsing
- **Bash** — for deterministic operations

### Setup

1. **Clone or copy the skill:**
   ```bash
   # If using as standalone
   cp -r pm-workflow/ /path/to/your/project/.claude/skills/
   ```

2. **Initialize workspace:**
   ```
   /pm-workflow init
   ```

3. **Start using:**
   ```
   "I want to build a notification system"
   ```

---

## Usage Examples

### Starting from Existing Document

```
You: I have an SRS from another team — can you parse it?

Claude: [Detects: Ingest intent]
        I'll parse that SRS into structured requirements.

        Please share the document (paste text, file path, or upload)

You: [pastes SRS content]

Claude: ✅ Detected 12 requirement sections
        ✅ Created REQ-001 through REQ-012
        ✅ Saved to specs/requirements.md
        ✅ Ingestion log updated

        Ready to create a structured PRD?
        Say: "parse the notification-system PRD"
```

---

### Preparing for Client Meeting

```
You: I have a client meeting tomorrow about a notification system

Claude: [Detects: Meeting Prep intent]
        Let me prepare a tailored question list.

        Quick context:
        - What type of meeting? (discovery, pitch, check-in)
        - Who's in the room?
        - What's at stake?

You: Discovery meeting, CTO and Tech Lead, $50K budget decision

Claude: ✅ Created prioritized question list

        ## Must Ask (Deal-Breakers)
        1. "What's your notification volume per day?"
           - Why: Infrastructure requirements
           - Red flag: "Not sure"

        ...

        Saved to: .pm/meeting-prep-notification-system.md

        Bring this to your meeting!
```

---

### Full Project Workflow

```
You: I want to build a notification system — push, email, and in-app

Claude: [Detects: Brainstorm intent]
        Let's start with discovery...

        [Runs /discovery-process]
        [Asks clarifying questions]

        ✅ Created specs/requirements.md (REQ-001)

You: parse the notification PRD

Claude: [Detects: Document intent]
        [Runs /product-strategy-session]
        [Runs /prd-development]

        ✅ Created .claude/prds/notification-system.md
        ✅ Created specs/personas/admin.md

You: break down the notification epic

Claude: [Detects: Plan intent]
        [Runs /epic-breakdown-advisor]

        ✅ Created .claude/epics/notification-system/epic.md
        ✅ Created 7 tasks

You: start working on task 001

Claude: [Detects: Execute intent]
        ✅ Validated spec chain: REQ-001 → PRD → Epic → Task 001
        ✅ Dependencies: none

        Starting implementation...

        [Implements according to spec]

        Commit: abc1234 "REQ-001: add notifications table"

You: standup

Claude: [Detects: Track intent]
        [Runs bash references/scripts/standup.sh]

        ## Standup — 2026-03-30

        ### ✅ Done
        - Phase 1: discovery-process
        - Phase 2: product-strategy-session, prd-development
        - Phase 3: epic-breakdown-advisor
        - Phase 4: Task 001 complete

        ### ▶️ Next
        - Task 002: Push notification service
```

---

## Reference Files

| File | Purpose |
|------|---------|
| `references/ingest.md` | Phase 0: Parse documents into requirements |
| `references/meeting-prep.md` | Pre-Phase: Client meeting question preparation |
| `references/brainstorm.md` | Phase 1: Discovery + requirements |
| `references/document.md` | Phase 2: PRD + strategy |
| `references/plan.md` | Phase 3: Epic + task decomposition |
| `references/execute.md` | Phase 4: Implementation |
| `references/track.md` | Phase 5: Status + standup + search |
| `references/admin.md` | Init, done, trace commands |
| `references/conventions.md` | File formats, frontmatter, state schema |
| `references/deliverables.md` | What each phase produces (artifact catalog) |
| `references/sign-off.md` | Generate client-facing formal deliverables |

---

## Bash Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `references/scripts/status.sh` | Project status | `bash .pm/scripts/status.sh` |
| `references/scripts/standup.sh` | Daily standup | `bash .pm/scripts/standup.sh` |
| `references/scripts/search.sh` | Search artifacts | `bash .pm/scripts/search.sh "auth"` |

**Note:** During `/pm-workflow init`, these are symlinked to `.pm/scripts/` for easy access.

---

## Design Philosophy

Inspired by **CCPM** (https://github.com/automazeio/ccpm):

- **Spec-driven:** No code without a spec
- **Deterministic ops:** Scripts for status/standup/search (no LLM cost)
- **5-phase discipline:** Brainstorm → Document → Plan → Execute → Track
- **Natural language:** Intent detection removes syntax burden
- **Traceability:** REQ → PRD → Epic → Task → Code → Commit
- **Persistent context:** `.pm/context.md` is Claude's memory for this project

---

## Troubleshooting

### "I ran a skill but it didn't update state"
Make sure to run `/pm-workflow done` after completing a skill:
```
/pm-workflow done discovery-process
```

### "I can't see project status"
Run the status script:
```bash
bash .pm/scripts/status.sh
```

### "My context is lost between sessions"
Read `.pm/context.md` at the start of each session to restore context.

### "I need to see the full traceability chain"
Use the trace command:
```
/pm-workflow trace .claude/epics/notification-system/001.md
```

### "I want to generate a formal SRS for the client"
```
"generate SRS from requirements"
```

---

## Contributing

This skill is designed to be modular and extensible. To add new capabilities:

1. Create a new reference file in `references/`
2. Add intent detection pattern to `SKILL.md`
3. Update this README.md with the new phase/capability
4. Test thoroughly with real PM workflows

---

## Changelog

See `CHANGELOG.md` for version history.

---

## License

MIT License — Use freely, modify as needed, attribution appreciated.

---

## Credits

- **Inspired by:** CCPM (https://github.com/automazeio/ccpm)
- **PM Skills:** Product-Manager-Skills (https://github.com/deanpeters/Product-Manager-Skills/)
- **Built for:** Claude Code and Agent Skills ecosystem
