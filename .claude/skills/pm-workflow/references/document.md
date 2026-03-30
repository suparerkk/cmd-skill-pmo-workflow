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

### 5. Create SRS (Software Requirements Specification)

Generate a formal SRS document suitable for client sign-off.

**Language:** Before generating, ask the user:
```
📝 What language should the SRS be in?
   1. English (default)
   2. Thai (ภาษาไทย)
```

Skip asking if the user already specified the language in their request (e.g., "generate the SRS in Thai").

Write all document body content (headings, descriptions, requirement text, table headers, analysis) in the chosen language. Keep YAML frontmatter keys, REQ IDs, FR/NFR IDs in English.

**Output:** `specs/srs/srs.md`

**Structure:**

```markdown
---
trace:
  requirements: [REQ-001, REQ-002, ...]
  prd: specs/prd/prd.md
created_by: document-phase
phase: 2-document
created: 2026-03-30
status: draft | review | approved
approved_by: null
approved_date: null
---

# Software Requirements Specification

## 1. Introduction

### 1.1 Purpose
<What this document covers and who it's for>

### 1.2 Scope
<System name, what it does, benefits, objectives>

### 1.3 Definitions, Acronyms, and Abbreviations
| Term | Definition |
|------|-----------|
| <term> | <definition> |

### 1.4 References
- specs/requirements.md
- specs/prd/prd.md

### 1.5 Overview
<Document structure summary>

---

## 2. Overall Description

### 2.1 Product Perspective
<How this system fits in the larger context — interfaces, dependencies>

### 2.2 Product Functions
<Summary of major functions — derived from REQ IDs>

### 2.3 User Characteristics
<From specs/personas/ — who uses this and their skill level>

### 2.4 Constraints
<From requirements — technical, regulatory, business constraints>

### 2.5 Assumptions and Dependencies
<What we assume to be true, external dependencies>

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### FR-001: <Requirement Title> (REQ-001)
**Priority:** P0/P1/P2
**Input:** <what triggers this>
**Processing:** <what the system does>
**Output:** <what the user sees/gets>

#### FR-002: <Requirement Title> (REQ-002)
...

### 3.2 Non-Functional Requirements

#### NFR-001: Performance
<Response time, throughput, capacity requirements>

#### NFR-002: Security
<Authentication, authorization, data protection>

#### NFR-003: Reliability
<Availability, failure recovery, data integrity>

#### NFR-004: Usability
<Accessibility, learnability, error handling>

### 3.3 Interface Requirements

#### External Interfaces
<Third-party APIs, services, data feeds>

#### User Interfaces
<Screen/interaction requirements — reference wireframes if tracked>

#### Hardware Interfaces
<If applicable>

#### Software Interfaces
<Database, OS, libraries>

---

## 4. Appendices

### A. Traceability Matrix
| SRS ID | REQ ID | PRD Feature | Status |
|--------|--------|-------------|--------|
| FR-001 | REQ-001 | Push Notifications | Draft |
| FR-002 | REQ-002 | Email Notifications | Draft |

### B. Sign-Off
| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Manager | | | |
| Client Stakeholder | | | |
| Technical Lead | | | |
```

**Key rules:**
- Every FR must trace to a REQ ID
- Every NFR must have measurable acceptance criteria
- Constraints come directly from requirements + PRD
- Include traceability matrix as appendix
- Include sign-off table for client approval

---

### 6. Create User Journey Diagrams

Generate Mermaid-based user journey diagrams from personas and requirements.

**Language:** Same as SRS — ask the user which language before generating (skip if already specified in request). Write journey descriptions, stage names, touchpoint labels, and pain point text in the chosen language. Keep Mermaid syntax keywords in English.

**Output:** `specs/journeys/journey-<persona>.md` (one per persona)

**Structure:**

```markdown
---
trace:
  requirements: [REQ-001, REQ-002]
  persona: specs/personas/admin.md
created_by: document-phase
phase: 2-document
created: 2026-03-30
---

# User Journey: <Persona Name> — <Journey Title>

## Journey Overview
**Persona:** <name> (<role>)
**Goal:** <what the user is trying to accomplish>
**Trigger:** <what starts this journey>
**Success:** <how we know the journey succeeded>

## Journey Diagram

` ` `mermaid
journey
    title SaaS Admin sends push notification
    section Discovery
      Admin logs into dashboard: 5: Admin
      Admin navigates to notifications: 4: Admin
    section Configuration
      Admin selects target audience: 3: Admin
      Admin writes notification content: 4: Admin
      Admin sets delivery channel: 4: Admin
    section Delivery
      Admin previews notification: 5: Admin
      Admin confirms and sends: 5: Admin
      System delivers notification: 5: System
      Admin views delivery report: 4: Admin
` ` `

## Touchpoints

| Stage | Action | Emotion | Pain Point | Opportunity |
|-------|--------|---------|------------|-------------|
| Discovery | Logs in | Neutral | - | Single sign-on |
| Configuration | Selects audience | Frustrated | Complex filtering | Smart segments |
| Delivery | Views report | Satisfied | Delayed stats | Real-time dashboard |

## Key Moments of Truth
1. **First notification sent** — must feel effortless
2. **Delivery confirmation** — must be visible within 5 seconds
3. **Failure handling** — must suggest next action, not just error

## Pain Points → Requirements Mapping
| Pain Point | Severity | REQ ID | Resolution |
|------------|----------|--------|------------|
| Complex audience filtering | High | REQ-003 | Smart segment builder |
| Delayed delivery stats | Medium | REQ-007 | Real-time analytics |
```

**Key rules:**
- One journey file per persona per major workflow
- Mermaid `journey` diagram for visual flow
- Touchpoint table maps stages to emotions and opportunities
- Pain points trace back to REQ IDs
- Use the `/customer-journey-map` skill for complex journeys

---

### 7. Update State

1. **Update `.pm/state.json`:**
```json
{
  "phase": 2,
  "phase_name": "Document",
  "completed_skills": [
    "discovery-process",
    "product-strategy-session",
    "prd-development",
    "proto-persona",
    "srs-generation",
    "user-journey-diagrams"
  ],
  "current_skill": null
}
```

2. **Append to `.pm/audit.log`:**
```json
{"timestamp":"2026-03-30T15:10:45Z","phase":2,"skill":"product-strategy-session","artifacts_created":["strategy/positioning.md","strategy/roadmap.md"]}
{"timestamp":"2026-03-30T15:30:22Z","phase":2,"skill":"prd-development","artifacts_created":["specs/prd/prd.md"]}
{"timestamp":"2026-03-30T15:35:10Z","phase":2,"skill":"proto-persona","artifacts_created":["specs/personas/admin.md"]}
{"timestamp":"2026-03-30T15:45:00Z","phase":2,"skill":"srs-generation","artifacts_created":["specs/srs/srs.md"]}
{"timestamp":"2026-03-30T15:55:00Z","phase":2,"skill":"user-journey-diagrams","artifacts_created":["specs/journeys/journey-admin.md"]}
```

3. **Update `.pm/context.md`:**
```markdown
## Current State
- Phase: 2 Document
- PRD created: specs/prd/prd.md
- SRS created: specs/srs/srs.md (ready for client review)
- Personas: admin.md, developer.md
- User Journeys: journey-admin.md, journey-developer.md

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
✅ SRS created: specs/srs/srs.md (client sign-off ready)
✅ Personas created: admin.md, developer.md
✅ User Journeys created: journey-admin.md

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
- `customer-journey-map` — detailed journey mapping (for complex journeys)

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

        Generating formal SRS...

        ✅ Created specs/srs/srs.md (client sign-off ready)

        Generating user journey diagrams...

        ✅ Created specs/journeys/journey-admin.md

        Ready to break this into tasks?
        Say: "break down the notification-system epic"
```

---

## Transition to Next Phase

User triggers Phase 3 (Plan) by saying:
- "break down the X epic"
- "decompose X into tasks"
- "plan X implementation"
