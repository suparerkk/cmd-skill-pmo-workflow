# Phase 2: Document

Write specs that leave nothing to interpretation.

## When to Use

User says:
- "what's the plan for X"
- "parse the X PRD"
- "create a PRD for X"
- "document X"
- "write specs for X"

## Behavior

### 1. Read Requirements

Read `specs/requirements.md` to understand the project scope.

If requirements don't exist:
```
Output: "I need requirements first. Run: I want to plan X"
Exit
```

---

### 2. Strategy Session

Run strategy skills:

```
Run: /product-strategy-session
```

This orchestrates:
- **Positioning**: `/positioning-workshop` — who is it for, what problem, why now
- **Prioritization**: `/prioritization-advisor` — what to build first
- **Roadmap**: `/roadmap-planning` — when to build what

Creates artifacts in `strategy/` directory.

---

### 3. Create PRD

```
Run: /prd-development
```

Generates `specs/prd/prd.md` with:

```markdown
# Product Requirements Document

## Overview
<Product summary from requirements>

## Problem Statement
<From requirements>

## Target Users

### Persona 1: <Name>
<From /proto-persona skill>

## Goals & Success Metrics
<From requirements>

## Features

### Feature 1: <Name>
**Priority:** P0/P1/P2
**REQ IDs:** REQ-001, REQ-002

**Description:**
<What it does>

**Acceptance Criteria:**
- <criterion 1>
- <criterion 2>

**Technical Notes:**
<implementation guidance>

---

## Non-Goals
<From requirements out-of-scope>

## Milestones
<From roadmap>

## Open Questions
<From .pm/context.md>
```

---

### 4. Create Personas

```
Run: /proto-persona
```

For each user type identified in requirements, create `specs/personas/<name>.md`:

```markdown
---
trace:
  requirement: REQ-001
  created_by: proto-persona
phase: 2-document
created: 2026-03-30
---

# Persona: <Name>

## Demographics
- Role: <job title>
- Experience: <beginner/expert>
- Organization: <startup/enterprise>

## Goals
1. <goal 1>
2. <goal 2>

## Pain Points
1. <pain 1>
2. <pain 2>

## Jobs to Be Done
- When <situation>, I want to <motivation>, so I can <outcome>

## Context
<Where/how they use the product>
```

---

### 5. Update State

1. **Update `.pm/state.json`:**
```json
{
  "phase": 2,
  "phase_name": "Document",
  "completed_skills": [
    "discovery-process",
    "product-strategy-session",
    "prd-development",
    "proto-persona"
  ],
  "current_skill": null
}
```

2. **Append to `.pm/audit.log`:**
```json
{"timestamp":"2026-03-30T15:10:45Z","phase":2,"skill":"product-strategy-session","artifacts_created":["strategy/positioning.md","strategy/roadmap.md"]}
{"timestamp":"2026-03-30T15:30:22Z","phase":2,"skill":"prd-development","artifacts_created":["specs/prd/prd.md"]}
{"timestamp":"2026-03-30T15:35:10Z","phase":2,"skill":"proto-persona","artifacts_created":["specs/personas/admin.md"]}
```

3. **Update `.pm/context.md`:**
```markdown
## Current State
- Phase: 2 Document
- PRD created: specs/prd/prd.md
- Personas: admin.md, developer.md

## Key Decisions
- 2026-03-30: Positioning as B2B SaaS admin tool (not end-user)
- 2026-03-30: P0 features: push + email notifications (in-app delayed to v2)
```

---

## Output

After documentation completes:

```
✅ Strategy session complete
✅ PRD created: specs/prd/prd.md
✅ Personas created: admin.md, developer.md

Ready to break this into actionable tasks?
Say: "break down the <feature-name> epic"
```

---

## Skills Used

Primary:
- `product-strategy-session` — main strategy workflow
- `prd-development` — PRD creation

Secondary:
- `positioning-workshop` — market positioning
- `prioritization-advisor` — feature prioritization
- `roadmap-planning` — timeline planning
- `proto-persona` — user persona creation

---

## Example

```
You: "parse the notification-system PRD"

Claude: I'll create a structured PRD from your requirements.
        Running /product-strategy-session...

        [Interactive positioning workshop]
        - Who is it for? B2B SaaS admins
        - What problem? Users miss critical updates
        - Why now? Competitors have it, customers asking

        ✅ Created strategy/positioning.md
        ✅ Created strategy/roadmap.md

        Running /prd-development...

        ✅ Created specs/prd/prd.md
        ✅ Created specs/personas/admin.md

        Ready to break this into tasks?
        Say: "break down the notification-system epic"
```

---

## Transition to Next Phase

User triggers Phase 3 (Plan) by saying:
- "break down the X epic"
- "decompose X into tasks"
- "plan X implementation"
