# Conventions

File formats, frontmatter schemas, and state management for consistent, traceable artifacts.

---

## Directory Structure

```
project-root/
├── .pm/
│   ├── context.md              # Persistent project memory
│   ├── state.json              # Current phase, REQ counter, completed skills
│   ├── audit.log               # JSON lines: immutable history
│   └── scripts/                # Bash scripts (symlink to skill references)
│
├── specs/
│   ├── sources/                # Local copies of ingested source files
│   │   ├── SRS-v2.pdf          # Copied from original path at ingest time
│   │   └── meeting-notes.md    # Pasted text saved as file
│   ├── requirements.md         # Source of truth — all REQs
│   ├── srs/                    # Formal SRS (client sign-off)
│   │   └── srs.md
│   ├── journeys/               # User journey diagrams (client sign-off)
│   │   └── journey-<persona>.md
│   ├── design/                 # System design + sequence diagrams (client sign-off)
│   │   ├── system-design.md
│   │   └── sequence-diagrams.md
│   ├── test-plan/              # Consolidated test plan (client sign-off)
│   │   └── test-plan.md
│   ├── prd/                    # Product requirement documents
│   │   └── prd.md
│   ├── epics/                  # Epics and tasks
│   │   └── <feature-name>/
│   │       ├── epic.md
│   │       ├── 001.md          # Task files (named by sequence or issue number)
│   │       ├── 002.md
│   │       └── updates/        # Progress tracking
│   │           └── 001-progress.md
│   ├── personas/               # Proto-personas
│   ├── stories/                # User stories
│   │   └── us-001.md
│   └── deliverable-tracker.md  # PM tracking of external deliverables
```

---

## File Naming Conventions

### Requirements
- **Location:** `specs/requirements.md`
- **Format:** Single file, all requirements
- **IDs:** `REQ-001`, `REQ-002`, etc. (auto-assigned, monotonically increasing)

### Personas
- **Location:** `specs/personas/<name>.md`
- **Naming:** lowercase, hyphen-separated (e.g., `saas-admin.md`)

### PRDs
- **Location:** `specs/prd/<feature-name>.md`
- **Naming:** lowercase, hyphen-separated (e.g., `notification-system.md`)
- **One PRD per feature**

### Epics
- **Location:** `specs/epics/<feature-name>/epic.md`
- **One epic directory per feature**

### Tasks
- **Location:** `specs/epics/<feature-name>/<task-id>.md`
- **Task ID:** Three-digit sequence (001, 002, etc.) **OR** GitHub issue number after sync
- **After GitHub sync:** Renamed to `{issue-number}.md` (e.g., `1234.md`)

### User Stories
- **Location:** `specs/stories/us-<id>.md`
- **ID:** Three-digit number matching task (e.g., `us-001.md`)

---

## Frontmatter Schemas

Every artifact must have YAML frontmatter for consistency and traceability.

### PRD Frontmatter

**File:** `specs/prd/<feature-name>.md`

```yaml
---
name: <feature-name>              # kebab-case, matches filename
description: <one-liner>          # used in lists and summaries
status: backlog | active | completed
created: <ISO 8601>               # date -u +"%Y-%m-%dT%H:%M:%SZ"
updated: <ISO 8601>               # date -u +"%Y-%m-%dT%H:%M:%SZ"
requirements:                     # REQ IDs this PRD addresses
  - REQ-001
  - REQ-002
---
```

**Example:**
```yaml
---
name: notification-system
description: Multi-channel notification system with push, email, and in-app
status: active
created: 2026-03-30T14:22:31Z
updated: 2026-03-30T16:45:00Z
requirements:
  - REQ-001
  - REQ-005
  - REQ-012
---
```

---

### Epic Frontmatter

**File:** `specs/epics/<feature-name>/epic.md`

```yaml
---
name: <feature-name>
description: <one-liner>
status: backlog | in-progress | completed
created: <ISO 8601>
updated: <ISO 8601>
progress: 0%                      # auto-calculated from task completion
prd: specs/prd/<name>.md      # path to parent PRD
requirements:                     # REQ IDs this epic implements
  - REQ-001
github: https://github.com/<owner>/<repo>/issues/<N>  # set on sync
---
```

**Example:**
```yaml
---
name: notification-system
description: Push, email, and in-app notification delivery
status: in-progress
created: 2026-03-30T15:10:00Z
updated: 2026-03-31T09:00:00Z
progress: 28%
prd: specs/prd/notification-system.md
requirements:
  - REQ-001
  - REQ-005
github: https://github.com/automazeio/ccpm/issues/1234
---
```

**Progress Calculation:**
```bash
# In bash scripts
total=$(ls specs/epics/notification-system/*.md | grep -v epic.md | wc -l)
completed=$(grep -l "status: closed" specs/epics/notification-system/*.md | wc -l)
progress=$((completed * 100 / total))
```

---

### Task Frontmatter

**File:** `specs/epics/<feature-name>/<task-id>.md`

```yaml
---
name: <Task Title>
status: open | in-progress | closed
created: <ISO 8601>
updated: <ISO 8601>
github: https://github.com/<owner>/<repo>/issues/<N>  # set on sync
depends_on: []                    # issue numbers this must wait for
parallel: true                    # can run concurrently with non-conflicting tasks
conflicts_with: []                # issue numbers that touch the same files
effort:
  size: S | M | L
  days: 2
---
```

**Example:**
```yaml
---
name: Database schema for notifications
status: in-progress
created: 2026-03-30T16:00:00Z
updated: 2026-03-30T17:30:00Z
github: https://github.com/automazeio/ccpm/issues/1235
depends_on: []
parallel: false
conflicts_with: []
effort:
  size: S
  days: 1
---
```

**Dependency Examples:**
```yaml
# Sequential dependency
depends_on: [1235]              # Must wait for issue #1235
parallel: false

# Parallel execution
depends_on: []
parallel: true
conflicts_with: [1237]          # Can't run at same time as #1237 (file conflicts)

# Blocked
depends_on: [1235, 1236]
parallel: false
```

---

### Progress Frontmatter

**File:** `specs/epics/<feature-name>/updates/<task-id>-progress.md`

```yaml
---
issue: <N>                       # GitHub issue number
started: <ISO 8601>
last_sync: <ISO 8601>
completion: 0%                   # estimated or actual
blocked: false
blocked_reason: null
---
```

**Example:**
```yaml
---
issue: 1235
started: 2026-03-30T16:00:00Z
last_sync: 2026-03-30T18:30:00Z
completion: 75%
blocked: false
blocked_reason: null
---
```

---

### Persona Frontmatter

**File:** `specs/personas/<name>.md`

```yaml
---
name: <Persona Name>
type: primary | secondary
created: <ISO 8601>
requirement: REQ-001
---
```

**Example:**
```yaml
---
name: SaaS Admin
type: primary
created: 2026-03-30T14:30:00Z
requirement: REQ-001
---
```

---

### User Story Frontmatter

**File:** `specs/stories/us-<id>.md`

```yaml
---
name: <Story Title>
epic: specs/epics/<feature-name>/epic.md
task: specs/epics/<feature-name>/<task-id>.md
created: <ISO 8601>
status: open | in-progress | done
---
```

**Example:**
```yaml
---
name: Admin receives push notification
epic: specs/epics/notification-system/epic.md
task: specs/epics/notification-system/002.md
created: 2026-03-30T16:15:00Z
status: open
---
```

---

### SRS Frontmatter

**File:** `specs/srs/srs.md`

```yaml
---
trace:
  requirements: [REQ-001, REQ-002]    # All REQ IDs covered
  prd: specs/prd/prd.md               # Source PRD
created_by: document-phase
phase: 2-document
created: <ISO 8601>
updated: <ISO 8601>
status: draft | review | approved      # Sign-off status
approved_by: null                       # Name of approver
approved_date: null                     # Date of approval
---
```

---

### User Journey Frontmatter

**File:** `specs/journeys/journey-<persona>.md`

```yaml
---
trace:
  requirements: [REQ-001, REQ-002]
  persona: specs/personas/<name>.md
created_by: document-phase
phase: 2-document
created: <ISO 8601>
---
```

---

### System Design Frontmatter

**File:** `specs/design/system-design.md`

```yaml
---
trace:
  requirements: [REQ-001, REQ-002]
  prd: specs/prd/prd.md
  epic: specs/epics/<feature-name>/epic.md
created_by: plan-phase
phase: 3-plan
created: <ISO 8601>
updated: <ISO 8601>
status: draft | review | approved
approved_by: null
approved_date: null
---
```

---

### Sequence Diagrams Frontmatter

**File:** `specs/design/sequence-diagrams.md`

```yaml
---
trace:
  requirements: [REQ-001, REQ-002]
  system_design: specs/design/system-design.md
  stories: [specs/stories/us-001.md]
created_by: plan-phase
phase: 3-plan
created: <ISO 8601>
---
```

---

### Test Plan Frontmatter

**File:** `specs/test-plan/test-plan.md`

```yaml
---
trace:
  requirements: [REQ-001, REQ-002]
  srs: specs/srs/srs.md
  epic: specs/epics/<feature-name>/epic.md
created_by: plan-phase
phase: 3-plan
created: <ISO 8601>
updated: <ISO 8601>
status: draft | review | approved
approved_by: null
approved_date: null
---
```

---

### Deliverable Tracker Frontmatter

**File:** `specs/deliverable-tracker.md`

```yaml
---
created: <ISO 8601>
updated: <ISO 8601>
---
```

---

## File Naming Conventions (Sign-Off Documents)

### SRS
- **Location:** `specs/srs/srs.md`
- **One SRS per project** (covers all features)

### User Journeys
- **Location:** `specs/journeys/journey-<persona>.md`
- **Naming:** `journey-` prefix + persona name (e.g., `journey-saas-admin.md`)
- **One file per persona per major workflow**

### System Design
- **Location:** `specs/design/system-design.md`
- **One system design per feature/epic**

### Sequence Diagrams
- **Location:** `specs/design/sequence-diagrams.md`
- **One file containing all sequence diagrams for the feature**

### Test Plan
- **Location:** `specs/test-plan/test-plan.md`
- **One consolidated test plan per feature**

### Deliverable Tracker
- **Location:** `specs/deliverable-tracker.md`
- **One tracker per project**

---

## Sign-Off Status Flow

```
draft → review → approved
```

Update via frontmatter `status` field. When approved:
- Set `approved_by` to the approver's name
- Set `approved_date` to the approval date

---

## State File Schema

**File:** `.pm/state.json`

```json
{
  "phase": 3,
  "phase_name": "Plan",
  "next_req_id": 15,
  "completed_skills": [
    "discovery-process",
    "product-strategy-session",
    "prd-development",
    "epic-hypothesis",
    "epic-breakdown-advisor"
  ],
  "current_skill": null,
  "active_epic": "notification-system",
  "blocked": [
    {
      "issue": 1238,
      "reason": "Waiting for API credentials",
      "since": "2026-03-28"
    }
  ]
}
```

### Phase Numbers

| Phase | Name | Number |
|-------|------|--------|
| Setup | Setup | 0 |
| Brainstorm | Brainstorm | 1 |
| Document | Document | 2 |
| Plan | Plan | 3 |
| Execute | Execute | 4 |
| Track | Track | 5 |

---

## Audit Log Format

**File:** `.pm/audit.log` — append-only JSON lines

### Skill Completion Entry

```json
{
  "timestamp": "2026-03-30T14:22:31Z",
  "phase": 1,
  "skill": "discovery-process",
  "req_id": "REQ-001",
  "artifacts_created": ["specs/requirements.md"],
  "artifacts_updated": []
}
```

### Task Start Entry

```json
{
  "timestamp": "2026-03-30T17:00:00Z",
  "phase": 4,
  "action": "task_start",
  "issue": 1235,
  "task": "specs/epics/notification-system/001.md",
  "req_id": "REQ-001"
}
```

### Task Complete Entry

```json
{
  "timestamp": "2026-03-30T18:30:00Z",
  "phase": 4,
  "action": "task_complete",
  "issue": 1235,
  "task": "specs/epics/notification-system/001.md",
  "req_id": "REQ-001",
  "commits": ["abc1234", "def5678"]
}
```

### Block Entry

```json
{
  "timestamp": "2026-03-30T10:00:00Z",
  "action": "block",
  "issue": 1238,
  "reason": "Waiting for API credentials",
  "blocked_by": "External dependency"
}
```

### Unblock Entry

```json
{
  "timestamp": "2026-03-30T19:00:00Z",
  "action": "unblock",
  "issue": 1238,
  "reason": "Credentials received"
}
```

---

## Context File Format

**File:** `.pm/context.md`

```markdown
# Project Context

## Project Overview
Building a notification system with push, email, and in-app channels for B2B SaaS admins.

## Key Decisions
- 2026-03-30: Using Firebase Cloud Messaging for push (cost + scalability)
- 2026-03-30: Target users are B2B SaaS admins, not end consumers
- 2026-03-30: In-app notifications delayed to v2 (scope reduction)

## Current State
- Phase: 4 Execute
- Active Epic: notification-system
- Working on: Issue #1236 (push notification service)
- Progress: 2/7 tasks complete (28%)

## Open Questions
- Should we support SMS notifications in v1?
- What's the fallback if push delivery fails?
- Do we need notification preferences UI in v1?

## Constraints
- Must launch by Q2 2026
- Budget: $50K
- Team: 2 backend, 1 frontend, 1 PM

## Success Criteria
- 95% notification delivery rate
- < 5 second push latency
- 80% admin engagement rate
```

---

## Commit Message Format

Every commit must include the REQ ID:

```
REQ-XXX: <short description>

<detailed bullet points of changes>

<optional footer>

Issue: #<issue-number>
```

### Example

```
REQ-001: implement push notification delivery

- Add Firebase Cloud Messaging client
- Create notification queue worker
- Add retry logic with exponential backoff
- Store notification metadata as JSONB

Issue: #1236
```

---

## Git Branch Naming

- **Features:** `feature/req-001-notification-system`
- **Tasks:** `task/1236-push-delivery` (issue number format)
- **Fixes:** `fix/1236-push-retry-logic`

---

## Dependency Matrix

Task dependencies are tracked in frontmatter:

```yaml
depends_on: [1235]              # This task requires #1235 to complete first
parallel: true                  # Can run concurrently with other parallel=true tasks
conflicts_with: [1237]          # Cannot run at same time as #1237 (file conflicts)
```

### Parallelization Rules

1. **`parallel: true`** + **no conflicts** → can run concurrently
2. **`depends_on`** must all be closed before starting
3. **`conflicts_with`** tasks cannot run simultaneously (file locks, DB migrations, etc.)

### Dependency Validation

Before starting a task:

```bash
# Check if all dependencies are closed
for dep in "${depends_on[@]}"; do
  status=$(grep "status:" specs/epics/$epic/$dep.md | awk '{print $2}')
  if [ "$status" != "closed" ]; then
    echo "❌ Blocked: Issue #$dep must be closed first"
    exit 1
  fi
done
```

---

## REQ ID Assignment

When `/pm-workflow done` is called:

1. Read `state.next_req_id`
2. Assign `REQ-{next_req_id}` to the skill's artifacts
3. Increment `next_req_id` in state
4. Write updated state

**REQ IDs are never reused** — monotonically increasing.

---

## Timestamps

All timestamps in ISO 8601 format:

```bash
# Generate timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ"
# Output: 2026-03-30T14:22:31Z
```

- **JSON fields:** `2026-03-30T14:22:31Z`
- **Frontmatter:** `2026-03-30T14:22:31Z`
- **Human-readable (in markdown body):** `March 30, 2026`

---

## Script Location

All bash scripts live in `references/scripts/`:

```
pm-workflow/
└── references/
    └── scripts/
        ├── status.sh
        ├── standup.sh
        └── search.sh
```

During `/pm-workflow init`, symlink to `.pm/scripts/`:

```bash
cd .pm
ln -s ../.claude/skills/pm-workflow/references/scripts scripts
```

Usage:

```bash
bash .pm/scripts/status.sh
bash .pm/scripts/standup.sh
bash .pm/scripts/search.sh "authentication"
```

---

## Validation Rules

### Phase Transitions

- Phase can only advance: 0 → 1 → 2 → 3 → 4 → 5
- Cannot skip phases
- Can return to earlier phases for new features

### Artifact Requirements

Before execution (Phase 4), validate artifact chain:

```bash
# Check if all artifacts exist
[ -f specs/requirements.md ] || echo "❌ Missing requirements"
[ -f specs/prd/$FEATURE.md ] || echo "❌ Missing PRD"
[ -f specs/epics/$FEATURE/epic.md ] || echo "❌ Missing epic"
[ -f specs/epics/$FEATURE/$TASK.md ] || echo "❌ Missing task"
```

If any missing: block execution, prompt user to run appropriate phase.

---

## Complete Artifact Chain Example

```
specs/requirements.md
  └─ REQ-001: "User notification system"

specs/prd/notification-system.md
  └─ requirements: [REQ-001]
  └─ Feature: Push Notifications

specs/epics/notification-system/epic.md
  └─ requirements: [REQ-001]
  └─ prd: specs/prd/notification-system.md
  └─ progress: 28%

specs/epics/notification-system/001.md
  └─ name: Database schema
  └─ status: closed
  └─ github: #1235

specs/epics/notification-system/002.md
  └─ name: Push notification service
  └─ status: in-progress
  └─ depends_on: [1235]
  └─ github: #1236

Commits:
  └─ abc1234: "REQ-001: add notifications table (Issue: #1235)"
  └─ def5678: "REQ-001: add FCM integration (Issue: #1236)"
```

✅ All linked. Full traceability. Consistent format.

---

## Status Transitions

### Task Status Flow

```
open → in-progress → closed
  ↓         ↓
  └─────────┴→ blocked
```

### Epic Status Flow

```
backlog → in-progress → completed
```

### PRD Status Flow

```
backlog → active → completed
```

---

## Progress Calculation

Epic progress is auto-calculated from task completion:

```bash
#!/bin/bash
EPIC_DIR="specs/epics/notification-system"

total=$(find "$EPIC_DIR" -name "*.md" ! -name "epic.md" ! -path "*/updates/*" | wc -l)
closed=$(grep -l "status: closed" "$EPIC_DIR"/*.md 2>/dev/null | wc -l)

if [ $total -gt 0 ]; then
  progress=$((closed * 100 / total))
  echo "Progress: $progress% ($closed/$total tasks)"
else
  echo "Progress: 0% (no tasks)"
fi
```

---

## Frontmatter Field Types

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `name` | string | kebab-case or title | `notification-system` or `Database schema` |
| `description` | string | one-liner | `Multi-channel notification system` |
| `status` | enum | specific values | `open`, `in-progress`, `closed` |
| `created` | datetime | ISO 8601 | `2026-03-30T14:22:31Z` |
| `updated` | datetime | ISO 8601 | `2026-03-30T16:45:00Z` |
| `progress` | integer | percentage | `28` (stored as number, displayed as `28%`) |
| `github` | URL | full GitHub URL | `https://github.com/owner/repo/issues/1235` |
| `depends_on` | array | issue numbers | `[1235, 1236]` |
| `parallel` | boolean | true/false | `true` |
| `conflicts_with` | array | issue numbers | `[1237]` |
| `effort.size` | enum | S/M/L | `M` |
| `effort.days` | integer | days | `3` |
| `requirements` | array | REQ IDs | `[REQ-001, REQ-005]` |

---

## Common Patterns

### Epic with Parallel Tasks

```yaml
# Epic: notification-system (progress: 0%)

# Task 001: Database schema
depends_on: []
parallel: false          # Must run first (schema is foundation)

# Task 002: Push service
depends_on: [001]
parallel: true           # Can run with 003

# Task 003: Email service
depends_on: [001]
parallel: true           # Can run with 002
conflicts_with: [002]    # But not at exact same time (shared notification model)

# Task 004: API endpoints
depends_on: [002, 003]
parallel: false          # Needs both services complete
```

### Blocked Task

```yaml
# Task 005: SMS integration
status: in-progress
depends_on: [001]
blocked: true
blocked_reason: "Waiting for Twilio account approval"
```

### Completed Epic

```yaml
# Epic: user-authentication
status: completed
progress: 100%
updated: 2026-03-31T12:00:00Z

# All tasks:
# - 001.md: status: closed
# - 002.md: status: closed
# - 003.md: status: closed
```

---

## Validation Checklist

Before marking any artifact as `completed` or `closed`:

- [ ] All frontmatter fields are present and valid
- [ ] `updated` timestamp is current
- [ ] Dependencies are satisfied (for tasks)
- [ ] Progress is recalculated (for epics)
- [ ] Audit log entry is appended
- [ ] Context file is updated with decision/progress
- [ ] Commits reference REQ ID and issue number

---

This format ensures consistency, traceability, and machine-readability across all project artifacts.
