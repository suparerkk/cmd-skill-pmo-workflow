---
name: pm-workflow
description: Spec-driven project management with 5-phase discipline (Brainstorm → Document → Plan → Execute → Track). Enforces requirements traceability, uses deterministic bash scripts for status/standup/search, and detects intent from natural language.
---

# pm-workflow — Spec-Driven Project Management

A structured project management workflow that enforces spec-driven development with persistent context, deterministic bash scripts, and natural language intent detection.

## How It Works

This skill detects user intent from natural conversation and routes to the appropriate workflow phase. Unlike command-based systems, you just talk — the skill figures out what you mean.

### Intent Detection

When the user speaks, analyze their intent and route accordingly:

**Pre-Phase: Meeting Prep Intent**
The user has an upcoming meeting and wants to prepare questions, discussion points, or an agenda.
- "I have a client meeting about X"
- "help me prep for the X meeting"
- "what should I ask about X"
- "prepare questions for X discussion"
- "I'm meeting with <company> tomorrow about X"
- "I need questions ready for the X call"

→ **Route to:** `references/meeting-prep.md`

---

**Phase 1: Brainstorm Intent**
The user wants to explore an idea, define a problem, or start planning something new.
- "I want to build a notification system"
- "we need to add user authentication"
- "let's plan the new dashboard feature"
- "help me think through the payment integration"
- "I'm designing a reporting system"

→ **Route to:** `references/brainstorm.md`

---

**Phase 2: Document Intent**
The user wants to formalize requirements into a structured document, create a PRD, or define strategy.
- "create a PRD for notifications"
- "parse the notification requirements into a PRD"
- "document the authentication feature"
- "what's the product strategy for payments?"
- "write up the dashboard spec"

→ **Route to:** `references/document.md`

---

**Phase 3: Plan Intent**
The user wants to break down a feature into tasks, decompose an epic, or plan implementation.
- "break down the notification epic"
- "decompose authentication into tasks"
- "split payments into user stories"
- "plan the dashboard implementation"
- "what tasks do we need for reporting?"

→ **Route to:** `references/plan.md`

---

**Phase 4: Execute Intent**
The user wants to start building, implement something, or work on a specific task.
- "start working on the notification service"
- "implement the database schema"
- "build the auth API endpoints"
- "work on task 005"
- "begin implementing payments"

→ **Route to:** `references/execute.md`

---

**Phase 5: Track Intent**
The user wants status, standup, search, or to know what's blocked/next.
- "what's our status?"
- "standup"
- "what's blocked?"
- "what should I work on next?"
- "search for authentication requirements"
- "show me the project progress"
- "what are we waiting on?"

→ **Route to:** `references/track.md`

---

**Admin Intent**
The user wants to initialize, complete a skill, trace artifacts, or manage blockers.
- "/pm-workflow init"
- "/pm-workflow done"
- "/pm-workflow trace <file>"
- "/pm-workflow block <description>"
- "/pm-workflow unblock"

→ **Route to:** `references/admin.md`

---

## The 5-Phase Discipline

> **Every line of code must trace back to a specification.**

### Phase 1: 🧠 Brainstorm
Think deeper than comfortable. Ask the hard questions before writing specs.

**What happens:**
- Guided discovery using PM skills (discovery-process, problem-framing-canvas)
- Capture insights in `.pm/context.md`
- Generate `specs/requirements.md` with auto-assigned REQ IDs
- Ask about: problem, users, success criteria, constraints, out-of-scope

**Triggers:** "I want to build X", "let's plan X", "help me think through X"

---

### Phase 2: 📝 Document
Write specs that leave nothing to interpretation.

**What happens:**
- Run strategy skills (product-strategy-session, positioning-workshop)
- Create structured PRD at `specs/prd/prd.md`
- Generate personas in `specs/personas/`
- Full traceability to requirements

**Triggers:** "parse the X PRD", "create a PRD for X", "document X"

---

### Phase 3: 📐 Plan
Architect with explicit technical decisions.

**What happens:**
- Create epic with architecture decisions
- Decompose into tasks with dependencies
- Generate user stories with acceptance criteria
- Map effort estimates and parallelization

**Triggers:** "break down the X epic", "decompose X into tasks"

---

### Phase 4: ⚡ Execute
Build exactly what was specified.

**What happens:**
- Validate spec chain exists (REQ → PRD → Epic → Task)
- Check dependencies are complete
- Implement according to task specification
- Commit with REQ ID in message

**Triggers:** "start working on X", "implement X", "work on issue X"

---

### Phase 5: 📊 Track
Maintain transparent progress at every step.

**What happens:**
- Run deterministic bash scripts (status.sh, standup.sh, search.sh)
- No LLM token cost for tracking operations
- Append-only audit log
- Persistent context in `.pm/context.md`

**Triggers:** "standup", "what's blocked", "what's next", "search for X"

---

## Workspace Structure

```
project-root/
├── .pm/
│   ├── context.md              # Persistent project memory
│   ├── state.json              # Current phase, REQ counter, completed skills
│   ├── audit.log               # JSON lines: what was done, when, with what
│   └── scripts/                # Deterministic bash operations
│       ├── status.sh
│       ├── standup.sh
│       └── search.sh
└── specs/
    ├── requirements.md          # Source of truth — all REQs live here
    ├── personas/               # Proto-personas (trace to REQs)
    ├── prd/
    │   └── prd.md              # Product requirement document
    ├── epics/
    │   └── <feature-name>/
    │       ├── epic.md         # Technical epic with architecture decisions
    │       ├── 001.md          # Task files (named by REQ ID or issue number)
    │       └── ...
    └── stories/
        └── us-001.md           # User stories (trace to epics → REQs)
```

---

## Bash Scripts (Deterministic Operations)

All tracking operations run as bash scripts — **fast, consistent, no LLM token cost**.

- `bash references/scripts/status.sh` — instant project status
- `bash references/scripts/standup.sh` — daily standup report
- `bash references/scripts/search.sh <query>` — search requirements + artifacts

See `references/track.md` for details.

---

## Artifact Traceability

Every artifact has frontmatter linking back to requirements:

```yaml
---
trace:
  requirement: REQ-001
  epic: specs/epics/notification-system/epic.md
  created_by: epic-hypothesis
phase: 3-plan
created: 2026-03-30
---
```

Use `/pm-workflow trace <file>` to see the full chain.

---

## Requirements

- **Product-Manager-Skills** from https://github.com/deanpeters/Product-Manager-Skills/
- **Git** — workspace is version-controlled
- **Python 3** — for bash script JSON parsing
- **Bash** — for deterministic operations (status/standup/search)

---

## Design Philosophy

Inspired by **CCPM** (https://github.com/automazeio/ccpm):

- **Spec-driven**: No code without a spec
- **Deterministic ops**: Scripts for status/standup/search (no LLM cost)
- **5-phase discipline**: Brainstorm → Document → Plan → Execute → Track
- **Natural language**: Intent detection removes syntax burden
- **Traceability**: REQ → PRD → Epic → Task → Code → Commit
- **Persistent context**: `.pm/context.md` is Claude's memory for this project

---

## Example Conversation

```
You: I have a client meeting tomorrow about a notification system

Claude: [Detects: Meeting Prep intent]
        Reading references/meeting-prep.md...

        [Runs meeting prep flow, asks context questions]

        ✅ Created prioritized question list
        ✅ Saved to .pm/meeting-prep-notifications.md

        Take these to your meeting!
        Afterward, say: "I want to build the notification system"
        to start discovery with your meeting notes.

---

You: I want to build a notification system — push, email, and in-app

Claude: [Detects: Phase 1 Brainstorm intent]
        Let's start with brainstorming to think through this properly.
        Reading references/brainstorm.md...

        [Runs /discovery-process, asks clarifying questions]

        ✅ Created specs/requirements.md with REQ-001
        Updated .pm/context.md with project overview

        Ready to create a structured PRD?
        Just say: "parse the notification PRD"

---

You: parse the notification PRD

Claude: [Detects: Phase 2 Document intent]
        Reading references/document.md...

        [Runs /product-strategy-session, /prd-development]

        ✅ Created specs/prd/prd.md
        ✅ Created specs/personas/admin.md

        Ready to break into tasks?
        Say: "break down the notification epic"

---

You: break it down

Claude: [Detects: Phase 3 Plan intent]
        Reading references/plan.md...

        [Runs /epic-breakdown-advisor]

        ✅ Created specs/epics/notification-system/epic.md
        ✅ Created 7 tasks: 001.md through 007.md

        Ready to start implementation?
        Say: "start working on task 001"

---

You: standup

Claude: [Detects: Phase 5 Track intent]
        Running bash references/scripts/standup.sh...

        ## Standup — 2026-03-30

        **Phase:** 3 — Plan

        ### ✅ Done
        - Phase 1: discovery-process
        - Phase 2: product-strategy-session, prd-development
        - Phase 3: epic-breakdown-advisor

        ### 🚫 Blocked
        - None

        ### ▶️ Next
        - Start execution: "start working on task 001"
```

---

## Reference Files

- `references/brainstorm.md` — Phase 1: Discovery + requirements
- `references/document.md` — Phase 2: PRD + strategy
- `references/plan.md` — Phase 3: Epic + task decomposition
- `references/execute.md` — Phase 4: Implementation
- `references/track.md` — Phase 5: Status + standup + search
- `references/admin.md` — Init, done, trace commands
- `references/conventions.md` — File formats, frontmatter, state schema
