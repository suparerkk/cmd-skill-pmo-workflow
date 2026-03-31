# Deliverables — What This Workflow Produces

Every phase creates specific artifacts with clear purposes and traceability.

---

## System Files (Persistent State)

These files are always present after `/pm-workflow init`:

### `.pm/state.json`
**Purpose:** Workflow state machine
**Updated:** Every phase transition
**Contains:**
- Current phase (0-5)
- Next REQ ID counter
- Completed skills list
- Blocked items
- Current skill being executed

**Example:**
```json
{
  "phase": 3,
  "phase_name": "Plan",
  "next_req_id": 15,
  "completed_skills": ["discovery-process", "prd-development"],
  "current_skill": null,
  "blocked": []
}
```

**Who reads it:** Bash scripts (status.sh, standup.sh), skill routing logic

---

### `.pm/context.md`
**Purpose:** Claude's persistent memory for this project
**Updated:** Every skill completion
**Contains:**
- Project overview
- Key decisions with dates
- Current state
- Open questions
- Constraints
- Success criteria

**Example:**
```markdown
# Project Context

## Project Overview
Building a notification system with push, email, and in-app channels.

## Key Decisions
- 2026-03-30: Using Firebase Cloud Messaging (cost + scalability)
- 2026-03-30: Target users are B2B SaaS admins

## Current State
- Phase: 3 Plan
- Working on: Epic breakdown

## Open Questions
- Should we support SMS in v1?
```

**Who reads it:** Claude at every session start (restores context)

---

### `.pm/audit.log`
**Purpose:** Immutable, append-only history
**Updated:** Every skill completion, task start/stop, block/unblock
**Format:** JSON lines (one JSON object per line)

**Example:**
```json
{"timestamp":"2026-03-30T14:22:31Z","phase":1,"skill":"discovery-process","req_id":"REQ-001","artifacts_created":["specs/requirements.md"]}
{"timestamp":"2026-03-30T17:00:00Z","phase":4,"action":"task_start","task":"specs/epics/notification-system/001.md"}
```

**Who reads it:** `standup.sh`, `search.sh`, trace commands

---

## Phase 0: Ingest — Deliverables

### `specs/requirements.md`
**Purpose:** Source of truth for all requirements
**Created by:** `ingest.md` or `brainstorm.md`
**Updated:** When new requirements are added

**Structure:**
```markdown
# Requirements

## REQ-001: User Notifications

**Source:** SRS-v2.pdf, Section 3.1 (Ingested 2026-03-30)

**Problem:** Users miss critical updates...

**Functional Requirements:**
1. Users can receive push notifications
2. Users can receive email notifications

**Non-Functional Requirements:**
1. Push delivery < 5 seconds

**Constraints:**
- Must support 10K concurrent users

**Out of Scope:**
- SMS notifications (v2)

---

## REQ-002: Admin Dashboard
...
```

**Frontmatter:** None (requirements.md is the source)

---

### `.pm/ingestion-log.md`
**Purpose:** Track what documents were ingested and what REQ IDs were created
**Created by:** `ingest.md`
**Updated:** Every ingestion

**Structure:**
```markdown
# Ingestion Log

## 2026-03-30: SRS-v2.pdf

**Source:** /documents/SRS-v2.pdf
**Type:** SRS (Software Requirements Specification)
**REQ IDs Created:** REQ-001 through REQ-015
**Sections Mapped:**
- Section 3.1: User Authentication → REQ-001
- Section 3.2: Password Reset → REQ-002
- ...

**Ambiguities Flagged:**
- REQ-005: "respond quickly" is not measurable → needs SLA definition

**Conflicts Detected:**
- REQ-012 conflicts with REQ-003 (session timeout vs remember me)

---

## 2026-03-29: Meeting Notes (Client Kickoff)

**Source:** /notes/2026-03-29-kickoff.md
**Type:** Meeting transcript
**REQ IDs Created:** None (decisions only, no formal requirements)
**Action Items Extracted:**
- Follow up on budget approval
- Schedule technical deep dive
```

---

## Pre-Phase: Meeting Prep — Deliverables

### `.pm/meeting-prep-<topic>.md`
**Purpose:** Prioritized question list for upcoming meeting
**Created by:** `meeting-prep.md`
**Disposable:** Yes (archive after meeting or delete)

**Structure:**
```markdown
# Meeting Prep: Notification System Discussion

**Meeting Date:** 2026-03-31
**Meeting Type:** Discovery
**Attendees:** Client PM, Tech Lead, Designer

---

## Must Ask (Deal-Breakers)

1. **"What's your notification volume per day?"**
   - Why: Determines infrastructure requirements
   - Red flag: "Not sure" → capacity planning impossible

2. **"What's your budget for notification services?"**
   - Why: Constrains vendor selection
   - Red flag: "Whatever it takes" → no budget discipline

---

## Should Ask (Scope-Shapers)

3. **"Do notifications need to comply with GDPR/CAN-SPAM?"**
   - Why: Legal requirements affect architecture
   - Red flag: "Not sure" for EU customers

---

## Nice to Ask (Clarity-Improvers)

4. **"What's the fallback channel if push fails?"**
   - Why: Resilience planning
   - Red flag: No fallback plan

---

**After Meeting:** Archive this file or update with answers and convert to requirements
```

---

## Phase 1: Brainstorm — Deliverables

### `specs/requirements.md` (if not created by ingest)
**Purpose:** Same as Phase 0
**Created by:** `brainstorm.md` via `/discovery-process`

---

### `discovery/` directory
**Purpose:** Discovery artifacts (problem frames, interview notes, opportunity trees)
**Created by:** Various PM skills

**Typical files:**
- `discovery/problem-framing.md` — From `/problem-framing-canvas`
- `discovery/interview-guide.md` — From `/discovery-interview-prep`
- `discovery/opportunity-tree.md` — From `/opportunity-solution-tree`

**Structure:** Skill-dependent (follows each PM skill's output format)

---

## Phase 2: Document — Deliverables

### `specs/srs/srs.md` (**CLIENT SIGN-OFF**)
**Purpose:** Formal Software Requirements Specification for client approval
**Created by:** `document.md` (auto-generated from requirements + PRD)
**Sign-off ready:** Yes — includes traceability matrix and sign-off table

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
### 1.1 Purpose / 1.2 Scope / 1.3 Definitions / 1.4 References / 1.5 Overview

## 2. Overall Description
### 2.1 Product Perspective / 2.2 Product Functions / 2.3 User Characteristics / 2.4 Constraints / 2.5 Assumptions

## 3. Specific Requirements
### 3.1 Functional Requirements (FR-001, FR-002, ...)
### 3.2 Non-Functional Requirements (NFR-001, NFR-002, ...)
### 3.3 Interface Requirements

## 4. Appendices
### A. Traceability Matrix (SRS ID → REQ ID → PRD Feature)
### B. Sign-Off Table (Role, Name, Date, Signature)
```

**Who reads it:** Client stakeholders, technical leads, QA team

---

### `specs/journeys/journey-<persona>.md` (**CLIENT SIGN-OFF**)
**Purpose:** Visual user journey diagrams with Mermaid notation
**Created by:** `document.md` (from personas + requirements)
**Sign-off ready:** Yes — shows user flow, emotions, pain points

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

# User Journey: <Persona> — <Journey Title>

## Journey Diagram (Mermaid)
<journey diagram with stages, actions, satisfaction scores>

## Touchpoints Table
<Stage, Action, Emotion, Pain Point, Opportunity>

## Key Moments of Truth
<Critical interaction points>

## Pain Points → Requirements Mapping
<Pain Point, Severity, REQ ID, Resolution>
```

**Who reads it:** Client stakeholders, UX designers, product team

---

### `specs/prd/<feature-name>.md`
**Purpose:** Structured PRD for a single feature
**Created by:** `document.md` via `/prd-development`
**Frontmatter:** Yes (see conventions.md)

**Structure:**
```yaml
---
name: notification-system
description: Multi-channel notification system
status: active
created: 2026-03-30T14:22:31Z
requirements:
  - REQ-001
  - REQ-005
---

# Product Requirements Document: Notification System

## Overview
<System description>

## Problem Statement
<From requirements>

## Target Users

### Persona: SaaS Admin
<From specs/personas/admin.md>

## Goals & Success Metrics
<From requirements>

## Features

### Feature 1: Push Notifications
**Priority:** P0
**REQ IDs:** REQ-001

**Description:**
Real-time push notifications via Firebase Cloud Messaging

**Acceptance Criteria:**
- [ ] User receives push notification within 5 seconds
- [ ] Notification displays title, body, and icon
- [ ] Tapping notification opens app to relevant screen

**Technical Notes:**
- Use Firebase Cloud Messaging SDK
- Store device tokens in users table
- Implement retry logic with exponential backoff

---

## Non-Goals
- SMS notifications (v2)
- In-app notification center (v2)

## Milestones
- M1 (Q2 2026): Push + Email notifications
- M2 (Q3 2026): In-app center + SMS

## Open Questions
- What's the fallback if push fails?
```

---

### `specs/personas/<name>.md`
**Purpose:** Proto-personas for user understanding
**Created by:** `document.md` via `/proto-persona`
**Frontmatter:** Yes

**Structure:**
```yaml
---
trace:
  requirement: REQ-001
created_by: proto-persona
phase: 2-document
created: 2026-03-30
---

# Persona: SaaS Admin

## Demographics
- Role: Product Manager or Admin
- Experience: 3-5 years
- Organization: B2B SaaS company

## Goals
1. Keep users engaged with product updates
2. Drive feature adoption
3. Reduce churn

## Pain Points
1. Users miss critical updates buried in email
2. No visibility into notification effectiveness
3. Can't target specific user segments

## Jobs to Be Done
- When a critical security update is released, I want to notify affected users immediately, so I can ensure compliance

## Context
Uses product 5-10 times per day during work hours
```

---

### `strategy/positioning.md`
**Purpose:** Market positioning statement
**Created by:** `document.md` via `/positioning-workshop`

**Structure:**
```markdown
# Positioning: Notification System

**For:** B2B SaaS companies with 100-10,000 users
**Who:** Need to keep users informed and engaged
**The <product>** is a multi-channel notification system
**That:** Delivers push, email, and in-app notifications in < 5 seconds
**Unlike:** SendGrid, OneSignal, Firebase alone
**Our product:** Provides unified API with delivery guarantees and analytics at 10x lower cost

## Key Differentiators
1. Multi-channel orchestration (not just push OR email)
2. 99.9% delivery SLA
3. Built-in A/B testing for notification copy
```

---

### `strategy/roadmap.md`
**Purpose:** Timeline and milestone planning
**Created by:** `document.md` via `/roadmap-planning`

**Structure:**
```markdown
# Roadmap: Notification System

## Q2 2026 (MVP)
**Theme:** Core delivery infrastructure
- Push notifications (P0)
- Email notifications (P0)
- Basic analytics (P1)

## Q3 2026 (v1.5)
**Theme:** User experience + targeting
- In-app notification center (P1)
- User segmentation (P1)
- A/B testing (P2)

## Q4 2026 (v2)
**Theme:** Scale + compliance
- SMS notifications (P2)
- GDPR/CCPA compliance tools (P1)
- Advanced analytics (P1)
```

---

## Phase 3: Plan — Deliverables

### `specs/design/system-design.md` (**CLIENT SIGN-OFF**)
**Purpose:** System architecture and component design with Mermaid diagrams
**Created by:** `plan.md` (from epic architecture decisions + PRD)
**Sign-off ready:** Yes — includes architecture, component, data flow diagrams and sign-off table

**Structure:**
```markdown
---
trace:
  requirements: [REQ-001, ...]
  prd: specs/prd/prd.md
  epic: specs/epics/<feature-name>/epic.md
created_by: plan-phase
phase: 3-plan
created: 2026-03-30
status: draft | review | approved
approved_by: null
approved_date: null
---

# System Design Document

## 1. Overview
## 2. Architecture Diagram (Mermaid graph TB)
## 3. Component Diagram (Mermaid graph LR)
## 4. Component Descriptions (responsibility, interfaces, dependencies, technology)
## 5. Data Flow (Mermaid flowchart)
## 6. Technology Stack (table with justifications)
## 7. Non-Functional Design (scalability, reliability, security, monitoring)
## 8. External Dependencies (table with SLA + fallback)
## 9. Deployment Architecture (optional Mermaid diagram)
## 10. Sign-Off Table
```

**Who reads it:** Client technical stakeholders, architects, developers

---

### `specs/design/sequence-diagrams.md` (**CLIENT SIGN-OFF**)
**Purpose:** Interaction flow diagrams for key user scenarios
**Created by:** `plan.md` (from user stories + system design)
**Sign-off ready:** Yes — traces to REQ IDs and user stories

**Structure:**
```markdown
---
trace:
  requirements: [REQ-001, ...]
  system_design: specs/design/system-design.md
  stories: [specs/stories/us-001.md, ...]
created_by: plan-phase
phase: 3-plan
created: 2026-03-30
---

# Sequence Diagrams

## SD-001: <Flow Title> (REQ-001)
<Mermaid sequenceDiagram with actors, services, messages>
<Error scenarios>

## SD-002: <Flow Title> (REQ-002)
...

## Diagram Index
<Table: ID, Flow, REQ, User Story, Components Involved>
```

**Who reads it:** Developers, architects, QA team

---

### `specs/test-plan/test-plan.md` (**CLIENT SIGN-OFF**)
**Purpose:** Consolidated test plan with UAT scenarios for client acceptance
**Created by:** `plan.md` (from task testing strategies + requirements)
**Sign-off ready:** Yes — includes UAT scenarios and sign-off table

**Structure:**
```markdown
---
trace:
  requirements: [REQ-001, ...]
  srs: specs/srs/srs.md
  epic: specs/epics/<feature-name>/epic.md
created_by: plan-phase
phase: 3-plan
created: 2026-03-30
status: draft | review | approved
approved_by: null
approved_date: null
---

# Test Plan

## 1. Overview (objective, scope, approach)
## 2. Test Scope Matrix (REQ → Unit/Integration/E2E/Manual/UAT)
## 3. Test Cases (TC-001, TC-002, ... with steps + expected results)
## 4. Non-Functional Test Cases (performance, security)
## 5. UAT Scenarios (client acceptance scenarios)
## 6. Test Environment (dev, staging, UAT)
## 7. Entry / Exit Criteria
## 8. Defect Management (severity → response time)
## 9. Sign-Off Table
```

**Who reads it:** QA lead, client stakeholders, product manager

---

### `specs/deliverable-tracker.md` (**PM TRACKING**)
**Purpose:** Track external deliverables produced by other roles (designer, developer)
**Created by:** `plan.md`
**Sign-off ready:** No — PM oversight tool

**Structure:**
```markdown
# Deliverable Tracker

## Tracked Deliverables
| ID | Deliverable | Owner Role | Owner Name | REQ IDs | Due Date | Status | Location |
|DT-001| Wireframes / UI Mockups | Designer | TBD | REQ-001 | TBD | Not Started | - |
|DT-002| ER Diagram | Developer | TBD | REQ-001 | TBD | Not Started | - |
|DT-003| API Specification (OpenAPI) | Developer | TBD | REQ-001 | TBD | Not Started | - |
```

**Who reads it:** PM (for follow-up), standup/status scripts

---

### `specs/epics/<feature-name>/epic.md`
**Purpose:** Technical epic with architecture decisions
**Created by:** `plan.md` via `/epic-hypothesis`
**Frontmatter:** Yes

**Structure:**
```yaml
---
name: notification-system
description: Push, email, and in-app notification delivery
status: in-progress
created: 2026-03-30T15:10:00Z
progress: 0%
prd: specs/prd/notification-system.md
requirements:
  - REQ-001
---

# Epic: Notification System

## Hypothesis
We believe that building a multi-channel notification system for SaaS admins will result in 30% higher user engagement. We'll know this is true when notification open rates exceed 40%.

## Architecture Decisions

### Decision 1: Notification Provider
**Context:** Need reliable push notification delivery
**Options Considered:**
1. Firebase Cloud Messaging — free, reliable, Google ecosystem
2. Amazon SNS — paid, AWS ecosystem
3. OneSignal — freemium, easy integration

**Decision:** Firebase Cloud Messaging
**Consequences:**
- ✅ Free for unlimited messages
- ✅ High reliability (99.9% SLA)
- ⚠️ Vendor lock-in to Google ecosystem

### Decision 2: Notification Queue
**Context:** Need reliable delivery with retries
**Decision:** Sidekiq with Redis
**Consequences:**
- ✅ Built-in retry logic
- ✅ Job monitoring
- ⚠️ Requires Redis infrastructure

## Technical Approach
- Microservice architecture with dedicated notification service
- PostgreSQL for notification metadata
- Redis + Sidekiq for job queue
- Firebase Cloud Messaging for push
- SendGrid for email

## Task Preview
1. Database schema (2 days)
2. Push notification service (3 days) [parallel]
3. Email notification service (2 days) [parallel]
4. API endpoints (2 days)
5. UI components (3 days) [parallel]
6. Webhook handlers (2 days)
7. Testing suite (2 days)

## Dependencies
- Firebase project setup
- SendGrid API key
- Redis cluster provisioning

## Risks
- Firebase rate limits — mitigate with batching
- Email deliverability — mitigate with sender reputation warming
```

---

### `specs/epics/<feature-name>/<task-id>.md`
**Purpose:** Executable task with acceptance criteria
**Created by:** `plan.md` via `/epic-breakdown-advisor`
**Frontmatter:** Yes

**Structure:**
```yaml
---
name: Database schema
status: open
created: 2026-03-30T16:00:00Z
updated: 2026-03-30T16:00:00Z
github: https://github.com/owner/repo/issues/1235
depends_on: []
parallel: false
conflicts_with: []
---

# Task 001: Database Schema

## Description
Create PostgreSQL tables for storing notification metadata, user preferences, and delivery history.

## Acceptance Criteria
- [ ] `notifications` table created with JSONB metadata column
- [ ] `notification_preferences` table for user opt-in/opt-out
- [ ] `notification_deliveries` table for tracking delivery status
- [ ] Indexes on `user_id`, `created_at`, `status`
- [ ] Migration file committed
- [ ] Model + repository layer implemented

## Technical Details

**Schema:**
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  channel VARCHAR(20) NOT NULL, -- 'push', 'email', 'in_app'
  title VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW(),
  delivered_at TIMESTAMP,
  INDEX idx_user_created (user_id, created_at DESC),
  INDEX idx_status (status)
);
```

## Dependencies
- None (this is the foundation task)

## Blocks
- Task 002 (needs notifications table)
- Task 003 (needs notifications table)

## Effort Estimate
- Size: S
- Days: 1-2

## Files to Modify
- `db/migrations/20260330120000_add_notifications.rb`
- `app/models/notification.rb`
- `app/repositories/notification_repository.rb`

## Testing Strategy
- Unit tests for model validations
- Integration tests for repository CRUD operations
- Migration rollback test
```

---

### `specs/stories/us-<id>.md`
**Purpose:** User story with Gherkin acceptance criteria
**Created by:** `plan.md` via `/user-story`
**Frontmatter:** Yes

**Structure:**
```yaml
---
trace:
  requirement: REQ-001
  epic: specs/epics/notification-system/epic.md
  task: specs/epics/notification-system/002.md
created_by: user-story
phase: 3-plan
created: 2026-03-30
---

# User Story: Push Notification Delivery

**As a** SaaS admin
**I want** to send push notifications to my users
**So that** they receive time-sensitive updates instantly

## Acceptance Criteria (Gherkin)

```gherkin
Scenario: Successful push notification delivery
  Given a user has enabled push notifications
  And the user has a valid device token
  When the system sends a push notification
  Then the notification is delivered within 5 seconds
  And the notification appears on the user's device
  And the delivery status is recorded as "delivered"

Scenario: Push notification fails with retry
  Given a user has enabled push notifications
  And the user's device token is invalid
  When the system sends a push notification
  Then the delivery fails
  And the system retries delivery 3 times with exponential backoff
  And the delivery status is recorded as "failed" after 3 attempts

Scenario: User taps notification
  Given a user received a push notification
  When the user taps the notification
  Then the app opens to the relevant screen
  And the notification is marked as "read"
```

## Notes
- Use Firebase Cloud Messaging SDK
- Handle both iOS and Android tokens
- Store device tokens in `user_devices` table
```

---

## Phase 4: Execute — Deliverables

### Code Commits
**Purpose:** Implementation artifacts
**Created by:** Direct development work
**Format:** Git commits with REQ ID

**Commit Message Format:**
```
REQ-001: add notifications table

- Create notifications table with JSONB metadata
- Add indexes on user_id and created_at
- Implement notification model and repository
- Add unit and integration tests

Trace: specs/epics/notification-system/001.md
Closes #1235
```

---

### `specs/epics/<feature-name>/updates/<task-id>-progress.md`
**Purpose:** Track implementation progress for a task
**Created by:** `execute.md` (optional, for long-running tasks)
**Frontmatter:** Yes

**Structure:**
```yaml
---
issue: 1235
started: 2026-03-30T17:00:00Z
last_sync: 2026-03-30T18:30:00Z
completion: 80%
---

# Progress: Task 001 - Database Schema

## Started: 2026-03-30 17:00

## Current Status: 80% complete

### Completed
- [x] Created migration file
- [x] Implemented schema with JSONB column
- [x] Added indexes
- [x] Created model + repository

### In Progress
- [ ] Writing integration tests

### Blocked
- None

## Commits
- abc1234: REQ-001: add notifications table
- def5678: REQ-001: add notification model and repository

## Next
- Complete integration tests
- Run migration in staging
- Mark task as closed
```

---

## Phase 5: Track — Deliverables

### `.pm/standup.md`
**Purpose:** Daily standup report (auto-generated)
**Created by:** `bash references/scripts/standup.sh`
**Disposable:** Yes (regenerated daily)

**Structure:**
```markdown
## Standup — 2026-03-30

**Phase:** 3 — Plan

---

### ✅ Done

- Phase 1: discovery-process
  → specs/requirements.md
- Phase 2: product-strategy-session
  → strategy/positioning.md, strategy/roadmap.md
- Phase 2: prd-development
  → specs/prd/notification-system.md
- Phase 3: epic-hypothesis
  → specs/epics/notification-system/epic.md
- Phase 3: epic-breakdown-advisor
  → 7 task files

---

### 🚫 Blocked

- None

---

### ▶️ Next

- Start execution: "start working on task 001"
```

---

## Summary: Artifact Lifecycle

```
Phase 0: Ingest
├─ specs/requirements.md (source of truth)
└─ .pm/ingestion-log.md (traceability)

Pre-Phase: Meeting Prep
└─ .pm/meeting-prep-<topic>.md (disposable)

Phase 1: Brainstorm
├─ specs/requirements.md (if not ingested)
└─ discovery/*.md (artifacts from PM skills)

Phase 2: Document
├─ specs/prd/<name>.md (PRD)
├─ specs/personas/*.md (user personas)
├─ strategy/*.md (positioning, roadmap)
├─ specs/srs/srs.md (SRS — CLIENT SIGN-OFF)
└─ specs/journeys/journey-*.md (user journeys — CLIENT SIGN-OFF)

Phase 3: Plan
├─ specs/epics/<name>/epic.md (technical epic)
├─ specs/epics/<name>/*.md (tasks)
├─ specs/stories/us-*.md (user stories)
├─ specs/design/system-design.md (system design — CLIENT SIGN-OFF)
├─ specs/design/sequence-diagrams.md (sequence diagrams — CLIENT SIGN-OFF)
├─ specs/test-plan/test-plan.md (test plan — CLIENT SIGN-OFF)
└─ specs/deliverable-tracker.md (external deliverable tracking)

Phase 4: Execute
├─ Code commits (with REQ ID)
└─ specs/epics/<name>/updates/*-progress.md (optional)

Phase 5: Track
├─ .pm/standup.md (auto-generated, disposable)
├─ Deliverables status (from deliverable-tracker.md)
└─ Sign-off status (from sign-off documents)

Always Present:
├─ .pm/state.json (workflow state)
├─ .pm/context.md (persistent memory)
└─ .pm/audit.log (immutable history)
```

---

## Client Sign-Off Documents

Documents with sign-off tables that can be presented to clients for formal approval:

| Document | Phase | File | Format |
|----------|-------|------|--------|
| SRS | 2 | `specs/srs/srs.md` | IEEE 830-inspired with traceability matrix |
| User Journey | 2 | `specs/journeys/journey-*.md` | Mermaid journey diagrams + touchpoint tables |
| System Design | 3 | `specs/design/system-design.md` | Mermaid architecture/component/data flow diagrams |
| Sequence Diagrams | 3 | `specs/design/sequence-diagrams.md` | Mermaid sequence diagrams per user flow |
| Test Plan | 3 | `specs/test-plan/test-plan.md` | Test cases + UAT scenarios + entry/exit criteria |

## PM-Tracked External Deliverables

Items the PM tracks but does not produce:

| Deliverable | Owner Role | Tracked In |
|-------------|-----------|------------|
| Wireframes / UI Mockups | Designer | `specs/deliverable-tracker.md` |
| ER Diagram | Developer | `specs/deliverable-tracker.md` |
| API Specification (OpenAPI) | Developer | `specs/deliverable-tracker.md` |

---

## Artifact Ownership

| Artifact | Created By | Updated By | Read By | Sign-Off |
|----------|------------|------------|---------|----------|
| `specs/requirements.md` | ingest / brainstorm | Any phase adding REQs | All phases | No |
| `specs/srs/srs.md` | document | document | client, QA, dev | **Yes** |
| `specs/journeys/journey-*.md` | document | document | client, UX, PM | **Yes** |
| `specs/prd/<name>.md` | document | document (rarely) | plan, execute | No |
| `specs/design/system-design.md` | plan | plan | client, architect, dev | **Yes** |
| `specs/design/sequence-diagrams.md` | plan | plan | dev, architect, QA | **Yes** |
| `specs/test-plan/test-plan.md` | plan | plan, execute | client, QA, PM | **Yes** |
| `specs/deliverable-tracker.md` | plan | track (status updates) | PM, standup | No |
| `specs/epics/<name>/epic.md` | plan | execute (progress) | execute, track | No |
| `specs/epics/<name>/<task>.md` | plan | execute (status) | execute, track | No |
| `.pm/state.json` | admin (init) | All phases | All phases | No |
| `.pm/context.md` | admin (init) | All phases | All phases (Claude) | No |
| `.pm/audit.log` | admin (init) | All phases (append) | track | No |

---

This ensures every deliverable has a clear purpose, creator, and consumer.
