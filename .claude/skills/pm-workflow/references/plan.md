# Phase 3: Plan

Architect with explicit technical decisions.

## When to Use

User says:
- "break down the X epic"
- "decompose X into tasks"
- "plan X implementation"
- "split X into stories"

## Behavior

### 1. Read PRD

Read `specs/prd/prd.md` to understand the feature scope.

If PRD doesn't exist:
```
Output: "I need a PRD first. Run: parse the X PRD"
Exit
```

---

### 2. Create Epic

```
Run: /epic-hypothesis
```

Creates `specs/epics/<feature-name>/epic.md` with:

```markdown
---
trace:
  requirement: REQ-001
  prd: specs/prd/prd.md
  created_by: epic-hypothesis
phase: 3-plan
created: 2026-03-30
---

# Epic: <Feature Name>

## Hypothesis
We believe that <building this feature> for <user persona>
will result in <outcome>. We'll know this is true when <metric>.

## Architecture Decisions

### Decision 1: <Title>
**Context:** <Why this decision is needed>
**Options Considered:**
1. <Option A> — <pros/cons>
2. <Option B> — <pros/cons>

**Decision:** <chosen option>

**Consequences:**
- <impact on system>

### Decision 2: <Title>
...

---

## Technical Approach
<High-level implementation strategy>

## Task Preview
- Task 1: <name> (~2 days)
- Task 2: <name> (~3 days)
- Task 3: <name> (~1 day)

## Dependencies
- <external dependency 1>
- <external dependency 2>

## Risks
- <risk 1> — <mitigation>
- <risk 2> — <mitigation>
```

---

### 3. Decompose into Tasks

```
Run: /epic-breakdown-advisor
```

Creates task files `specs/epics/<feature-name>/001.md`, `002.md`, etc:

```markdown
---
trace:
  requirement: REQ-001
  epic: specs/epics/notification-system/epic.md
  created_by: epic-breakdown-advisor
phase: 3-plan
created: 2026-03-30
---

# Task 001: <Task Name>

## Description
<What this task accomplishes>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Technical Details
<Implementation guidance>

## Dependencies
- Depends on: <task ID or none>
- Blocks: <task IDs blocked by this>

## Parallelization
- parallel: true/false
- conflicts_with: [<task IDs that can't run concurrently>]

## Effort Estimate
- Size: S/M/L
- Days: <estimate>

## Files to Modify
- <file path 1>
- <file path 2>

## Testing Strategy
<How to verify this works>
```

---

### 4. Create User Stories

For each task that needs it:

```
Run: /user-story
```

Creates `specs/stories/us-001.md`:

```markdown
---
trace:
  requirement: REQ-001
  epic: specs/epics/notification-system/epic.md
  task: specs/epics/notification-system/001.md
  created_by: user-story
phase: 3-plan
created: 2026-03-30
---

# User Story: <Title>

**As a** <persona>
**I want** <goal>
**So that** <benefit>

## Acceptance Criteria (Gherkin)

```gherkin
Scenario: <scenario name>
  Given <context>
  When <action>
  Then <outcome>
```

## Notes
<Additional context>
```

---

### 5. Create System Design Document

Generate a system design document with Mermaid architecture and component diagrams.

**Output:** `specs/design/system-design.md`

**Structure:**

```markdown
---
trace:
  requirements: [REQ-001, REQ-002, ...]
  prd: specs/prd/prd.md
  epic: specs/epics/<feature-name>/epic.md
created_by: plan-phase
phase: 3-plan
created: 2026-03-30
status: draft | review | approved
approved_by: null
approved_date: null
---

# System Design Document: <Feature Name>

## 1. Overview
<What this system does and why — one paragraph>

## 2. Architecture Diagram

` ` `mermaid
graph TB
    subgraph Client Layer
        WEB[Web App]
        MOB[Mobile App]
    end

    subgraph API Layer
        GW[API Gateway]
        AUTH[Auth Service]
    end

    subgraph Service Layer
        NS[Notification Service]
        PS[Push Service]
        ES[Email Service]
    end

    subgraph Data Layer
        DB[(PostgreSQL)]
        CACHE[(Redis)]
        QUEUE[Job Queue]
    end

    WEB --> GW
    MOB --> GW
    GW --> AUTH
    GW --> NS
    NS --> PS
    NS --> ES
    NS --> QUEUE
    QUEUE --> PS
    QUEUE --> ES
    PS --> FCM[Firebase CM]
    ES --> SG[SendGrid]
    NS --> DB
    NS --> CACHE
` ` `

## 3. Component Diagram

` ` `mermaid
graph LR
    subgraph Notification Service
        API[REST API]
        ORCH[Orchestrator]
        TMPL[Template Engine]
        PREF[Preference Manager]
    end

    API --> ORCH
    ORCH --> TMPL
    ORCH --> PREF
    ORCH --> QUEUE[Job Queue]
` ` `

## 4. Component Descriptions

### 4.1 <Component Name>
**Responsibility:** <what it does>
**Interfaces:** <what it exposes>
**Dependencies:** <what it needs>
**Technology:** <stack choice and why>

### 4.2 <Component Name>
...

## 5. Data Flow

` ` `mermaid
flowchart LR
    A[Admin creates notification] --> B[API validates request]
    B --> C{Channel selection}
    C -->|Push| D[Push Queue]
    C -->|Email| E[Email Queue]
    C -->|In-app| F[In-app Store]
    D --> G[Firebase CM]
    E --> H[SendGrid]
    F --> I[User inbox]
    G --> J[Delivery callback]
    H --> J
    J --> K[Update status in DB]
` ` `

## 6. Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| API | <tech> | <why> |
| Queue | <tech> | <why> |
| Database | <tech> | <why> |
| Cache | <tech> | <why> |

## 7. Non-Functional Design

### 7.1 Scalability
<How the system scales — horizontal, vertical, auto-scaling>

### 7.2 Reliability
<Failover, retry, circuit breaker patterns>

### 7.3 Security
<Auth, encryption, data protection>

### 7.4 Monitoring
<Observability, logging, alerting>

## 8. External Dependencies

| Dependency | Type | SLA | Fallback |
|-----------|------|-----|----------|
| Firebase CM | Push delivery | 99.9% | Retry queue |
| SendGrid | Email delivery | 99.95% | Queue + alert |

## 9. Deployment Architecture (optional)

` ` `mermaid
graph TB
    subgraph Production
        LB[Load Balancer]
        APP1[App Server 1]
        APP2[App Server 2]
        DB_P[(Primary DB)]
        DB_R[(Replica DB)]
    end
    LB --> APP1
    LB --> APP2
    APP1 --> DB_P
    APP2 --> DB_P
    DB_P --> DB_R
` ` `

## 10. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Technical Lead | | | |
| Product Manager | | | |
| Client Stakeholder | | | |
```

**Key rules:**
- Architecture decisions must trace to epic.md
- Every component must have a clear responsibility
- Use Mermaid diagrams (renderable in GitHub, Confluence, most modern tools)
- Include NFR design (scalability, reliability, security)
- Include sign-off table

---

### 6. Create Sequence Diagrams

Generate Mermaid sequence diagrams for key user flows and system interactions.

**Output:** `specs/design/sequence-diagrams.md`

**Structure:**

```markdown
---
trace:
  requirements: [REQ-001, REQ-002, ...]
  system_design: specs/design/system-design.md
  stories: [specs/stories/us-001.md, specs/stories/us-002.md]
created_by: plan-phase
phase: 3-plan
created: 2026-03-30
---

# Sequence Diagrams: <Feature Name>

## SD-001: <Flow Title> (REQ-001)

**Trigger:** <what starts this flow>
**Actors:** <who/what participates>
**Happy path result:** <what success looks like>

` ` `mermaid
sequenceDiagram
    actor Admin
    participant API as API Gateway
    participant NS as Notification Service
    participant Q as Job Queue
    participant PS as Push Service
    participant FCM as Firebase CM
    participant DB as Database

    Admin->>API: POST /notifications
    API->>API: Validate auth token
    API->>NS: Create notification
    NS->>DB: Store notification (status: pending)
    NS->>Q: Enqueue push job
    Q->>PS: Process push job
    PS->>DB: Get user device tokens
    PS->>FCM: Send push notification
    FCM-->>PS: Delivery confirmation
    PS->>DB: Update status (delivered)
    PS-->>NS: Job complete
    NS-->>API: 202 Accepted
    API-->>Admin: Notification queued
` ` `

**Error scenarios:**
- Invalid token → 401 Unauthorized
- No device tokens → skip push, log warning
- FCM failure → retry 3x with exponential backoff

---

## SD-002: <Flow Title> (REQ-002)

` ` `mermaid
sequenceDiagram
    ...
` ` `

---

## Diagram Index

| ID | Flow | REQ | User Story | Components Involved |
|----|------|-----|------------|-------------------|
| SD-001 | Send push notification | REQ-001 | US-001 | API, NS, Queue, Push, FCM |
| SD-002 | Send email notification | REQ-002 | US-002 | API, NS, Queue, Email, SendGrid |
| SD-003 | User taps notification | REQ-001 | US-003 | Mobile, API, NS, DB |
```

**Key rules:**
- One sequence diagram per major user flow
- Must trace to REQ ID and user story
- Include error scenarios below each diagram
- Include diagram index for quick reference
- Actors on left, external services on right

---

### 7. Create Test Plan

Generate a consolidated test plan from all task testing strategies.

**Output:** `specs/test-plan/test-plan.md`

**Structure:**

```markdown
---
trace:
  requirements: [REQ-001, REQ-002, ...]
  srs: specs/srs/srs.md
  epic: specs/epics/<feature-name>/epic.md
created_by: plan-phase
phase: 3-plan
created: 2026-03-30
status: draft | review | approved
approved_by: null
approved_date: null
---

# Test Plan: <Feature Name>

## 1. Overview

**Objective:** <what testing aims to verify>
**Scope:** <features in/out of scope for testing>
**Approach:** <testing strategy — unit, integration, E2E, manual>

## 2. Test Scope Matrix

| REQ ID | Feature | Unit | Integration | E2E | Manual | UAT |
|--------|---------|------|-------------|-----|--------|-----|
| REQ-001 | Push notifications | ✅ | ✅ | ✅ | | ✅ |
| REQ-002 | Email notifications | ✅ | ✅ | ✅ | | ✅ |
| REQ-003 | User preferences | ✅ | ✅ | | ✅ | |

## 3. Test Cases

### TC-001: <Test Case Title> (REQ-001, FR-001)

**Type:** Unit / Integration / E2E / Manual
**Priority:** P0 / P1 / P2
**Preconditions:**
- <condition 1>
- <condition 2>

**Steps:**
1. <step 1>
2. <step 2>
3. <step 3>

**Expected Result:** <what should happen>
**Actual Result:** <filled during execution>
**Status:** Not Run / Pass / Fail / Blocked

---

### TC-002: <Test Case Title> (REQ-001, FR-001)
...

## 4. Non-Functional Test Cases

### Performance Tests
| Test | Target | Method |
|------|--------|--------|
| Push delivery latency | < 5 seconds | Load test with 1K concurrent |
| API response time | < 200ms (p95) | Stress test |

### Security Tests
| Test | Criteria | Method |
|------|----------|--------|
| Auth bypass | No unauthorized access | Penetration test |
| Input validation | No injection | Automated scan |

## 5. UAT Scenarios

Scenarios for client User Acceptance Testing:

### UAT-001: <Scenario Title>
**Persona:** <from specs/personas/>
**Precondition:** <setup required>
**Steps:**
1. <user action>
2. <expected system response>
3. <user verification>

**Pass Criteria:** <what client signs off on>

## 6. Test Environment

| Environment | Purpose | Data |
|-------------|---------|------|
| Dev | Unit + integration tests | Seed data |
| Staging | E2E + performance tests | Anonymized production data |
| UAT | Client acceptance | Client-provided scenarios |

## 7. Entry / Exit Criteria

**Entry Criteria:**
- [ ] All code committed and deployed to test environment
- [ ] Test data prepared
- [ ] Test accounts created

**Exit Criteria:**
- [ ] All P0 test cases pass
- [ ] No critical or high severity defects open
- [ ] Performance targets met
- [ ] Client UAT sign-off received

## 8. Defect Management

| Severity | Response Time | Resolution Time |
|----------|--------------|-----------------|
| Critical | 1 hour | 4 hours |
| High | 4 hours | 1 business day |
| Medium | 1 business day | 3 business days |
| Low | 3 business days | Next sprint |

## 9. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | | | |
| Product Manager | | | |
| Client Stakeholder | | | |
```

**Key rules:**
- Every test case must trace to a REQ ID and FR/NFR ID
- Consolidate testing strategies from individual task files
- Include UAT scenarios for client acceptance
- Include entry/exit criteria for test phases
- Include sign-off table

---

### 8. Set Up Deliverable Tracker

Track external deliverables that the PM needs to follow up on but are produced by other roles.

**Output:** `specs/deliverable-tracker.md`

**Structure:**

```markdown
---
created: 2026-03-30
updated: 2026-03-30
---

# Deliverable Tracker

External deliverables that require PM follow-up. These are produced by designers, developers, or other stakeholders — not generated from requirements directly.

## Tracked Deliverables

| ID | Deliverable | Owner Role | Owner Name | REQ IDs | Due Date | Status | Location |
|----|------------|------------|------------|---------|----------|--------|----------|
| DT-001 | Wireframes / UI Mockups | Designer | TBD | REQ-001, REQ-003 | TBD | Not Started | - |
| DT-002 | ER Diagram | Developer | TBD | REQ-001 | TBD | Not Started | - |
| DT-003 | API Specification (OpenAPI) | Developer | TBD | REQ-001, REQ-002 | TBD | Not Started | - |

## Status Legend
- **Not Started** — deliverable not yet begun
- **In Progress** — owner is actively working on it
- **In Review** — ready for PM/client review
- **Approved** — signed off by stakeholders
- **Blocked** — waiting on something

## Notes
- PM is responsible for tracking these deliverables, not producing them
- Update this tracker during standups and status checks
- Link to actual files/URLs in the Location column once available
```

**Key rules:**
- PM tracks, does not produce these deliverables
- Each tracked item must link to REQ IDs
- Status is updated during standup/status checks
- Track.md scripts should read this file for status reporting

---

### 9. Story Splitting (if needed)

If stories are too large:

```
Run: /user-story-splitting
```

Uses Humanizing Work split patterns to break into smaller deliverables.

---

### 10. Map Stories (optional)

For complex workflows:

```
Run: /user-story-mapping-workshop
```

Creates story map with:
- Backbone activities
- User steps
- Task slices
- Release priorities

---

### 11. Update State

1. **Update `.pm/state.json`:**
```json
{
  "phase": 3,
  "phase_name": "Plan",
  "completed_skills": [
    "discovery-process",
    "product-strategy-session",
    "prd-development",
    "proto-persona",
    "srs-generation",
    "user-journey-diagrams",
    "epic-hypothesis",
    "epic-breakdown-advisor",
    "user-story",
    "system-design",
    "sequence-diagrams",
    "test-plan",
    "deliverable-tracker"
  ],
  "current_skill": null
}
```

2. **Append to `.pm/audit.log`:**
```json
{"timestamp":"2026-03-30T16:00:00Z","phase":3,"skill":"epic-hypothesis","artifacts_created":["specs/epics/notification-system/epic.md"]}
{"timestamp":"2026-03-30T16:15:00Z","phase":3,"skill":"epic-breakdown-advisor","artifacts_created":["specs/epics/notification-system/001.md","specs/epics/notification-system/002.md","specs/epics/notification-system/003.md"]}
{"timestamp":"2026-03-30T16:20:00Z","phase":3,"skill":"user-story","artifacts_created":["specs/stories/us-001.md","specs/stories/us-002.md"]}
{"timestamp":"2026-03-30T16:30:00Z","phase":3,"skill":"system-design","artifacts_created":["specs/design/system-design.md"]}
{"timestamp":"2026-03-30T16:40:00Z","phase":3,"skill":"sequence-diagrams","artifacts_created":["specs/design/sequence-diagrams.md"]}
{"timestamp":"2026-03-30T16:50:00Z","phase":3,"skill":"test-plan","artifacts_created":["specs/test-plan/test-plan.md"]}
{"timestamp":"2026-03-30T16:55:00Z","phase":3,"skill":"deliverable-tracker","artifacts_created":["specs/deliverable-tracker.md"]}
```

3. **Update `.pm/context.md`:**
```markdown
## Current State
- Phase: 3 Plan
- Epic: specs/epics/notification-system/epic.md
- Tasks: 7 total (5 parallel, 2 sequential)
- System Design: specs/design/system-design.md (client sign-off ready)
- Sequence Diagrams: specs/design/sequence-diagrams.md
- Test Plan: specs/test-plan/test-plan.md (client sign-off ready)
- Deliverable Tracker: 3 external items (wireframes, ER, API spec)

## Key Decisions
- 2026-03-30: Using Firebase Cloud Messaging for push (cost, reliability)
- 2026-03-30: Task 003 depends on 001 (database schema must exist first)
```

---

## Output

After planning completes:

```
✅ Epic created: specs/epics/notification-system/epic.md
✅ Tasks decomposed: 7 tasks (5 parallel, 2 sequential)
✅ User stories: specs/stories/us-001.md through us-007.md
✅ System Design: specs/design/system-design.md (client sign-off ready)
✅ Sequence Diagrams: specs/design/sequence-diagrams.md (3 flows)
✅ Test Plan: specs/test-plan/test-plan.md (client sign-off ready)
✅ Deliverable Tracker: 3 external items to track (wireframes, ER, API spec)

Ready to start implementation?
Say: "start working on task 001"
```

---

## Skills Used

Primary:
- `epic-hypothesis` — epic creation with hypothesis
- `epic-breakdown-advisor` — task decomposition
- `user-story` — user story creation
- `user-story-splitting` — split large stories

Secondary:
- `user-story-mapping-workshop` — story mapping for complex workflows

---

## Example

```
You: "break down the notification-system epic"

Claude: I'll decompose the PRD into executable tasks.
        Running /epic-hypothesis...

        [Interactive architecture decisions]
        - Push provider? Firebase (cost, scalability)
        - Email provider? SendGrid (existing contract)
        - Database? Add notifications table (PostgreSQL)

        ✅ Created specs/epics/notification-system/epic.md

        Running /epic-breakdown-advisor...

        ✅ Created 7 tasks:
           - 001.md: Database schema (~1 day)
           - 002.md: Push notification service (~3 days) [parallel]
           - 003.md: Email notification service (~2 days) [parallel]
           - 004.md: API endpoints (~2 days) [depends on 001]
           - 005.md: UI components (~3 days) [parallel]
           - 006.md: Webhook handlers (~2 days) [depends on 002,003]
           - 007.md: Testing suite (~2 days) [depends on all]

        Generating system design document...

        ✅ Created specs/design/system-design.md (Mermaid architecture diagrams)

        Generating sequence diagrams...

        ✅ Created specs/design/sequence-diagrams.md (3 interaction flows)

        Generating test plan...

        ✅ Created specs/test-plan/test-plan.md (UAT scenarios included)

        Setting up deliverable tracker...

        ✅ Created specs/deliverable-tracker.md
           - DT-001: Wireframes (Designer) — Not Started
           - DT-002: ER Diagram (Developer) — Not Started
           - DT-003: API Specification (Developer) — Not Started

        Ready to start implementation?
        Say: "start working on task 001"
```

---

## Transition to Next Phase

User triggers Phase 4 (Execute) by saying:
- "start working on X"
- "implement X"
- "work on issue X"
