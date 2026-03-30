# Admin Operations

Setup, initialization, and utility commands.

## Commands

### `/pm-workflow init`

Initialize workspace structure.

**Behavior:**

1. Create directory structure:
```
.pm/
├── context.md
├── state.json
├── audit.log
└── scripts/ → symlink to references/scripts/

specs/
├── requirements.md
├── personas/
├── prd/
├── epics/
└── stories/

discovery/
strategy/
validation/
delivery/
```

2. Initialize `.pm/state.json`:
```json
{
  "phase": 0,
  "phase_name": "Setup",
  "next_req_id": 1,
  "completed_skills": [],
  "current_skill": null,
  "blocked": []
}
```

3. Create `.pm/context.md`:
```markdown
# Project Context

## Project Overview
<!-- Claude maintains this as persistent memory -->

## Key Decisions
<!-- Logged here when skills complete -->

## Current State
<!-- Updated on each workflow step -->

## Open Questions
<!-- Tracked across sessions -->
```

4. Create empty `.pm/audit.log`

5. Create `specs/requirements.md` template:
```markdown
# Requirements

<!-- Write your product requirements here. Be specific. -->

## Functional Requirements

<!-- Example: -->
<!-- 1. Users must be able to authenticate via email/password -->
<!-- 2. Admins need a dashboard to manage users -->

## Non-Functional Requirements

<!-- Example: -->
<!-- 1. Page load must be < 2 seconds -->
<!-- 2. Support 10,000 concurrent users -->

## Constraints

<!-- Example: -->
<!-- 1. Must launch by Q3 2026 -->
<!-- 2. Budget limited to $50K -->
```

**Output:**
```
✅ Workspace initialized
✅ Created .pm/ directory
✅ Created specs/ directory

Next step:
Write your requirements in specs/requirements.md
Then say: "parse the requirements"
```

---

### `/pm-workflow done [skill-name]`

Mark a skill as complete.

**Behavior:**

1. Read `.pm/state.json`

2. If no skill-name provided, use `state.current_skill`

3. Generate REQ ID: `REQ-{next_req_id}` and increment

4. Append to `.pm/audit.log`:
```json
{
  "timestamp": "2026-03-30T14:22:31Z",
  "phase": <current-phase>,
  "skill": "<skill-name>",
  "req_id": "REQ-XXX",
  "artifacts_created": []
}
```

5. Update `state.json`:
   - Add skill to `completed_skills`
   - Set `current_skill: null`
   - Increment `next_req_id`

6. Update `.pm/context.md` with completion summary

**Output:**
```
✅ Marked <skill> complete
✅ REQ-002 assigned

Run: "what's next" to continue
```

---

### `/pm-workflow trace <file-path>`

Show traceability chain for an artifact.

**Behavior:**

1. Read the artifact file

2. Extract frontmatter YAML

3. Parse `trace` section:
```yaml
trace:
  requirement: REQ-001
  epic: specs/epics/notification-system/epic.md
  task: specs/epics/notification-system/001.md
```

4. Follow the chain:
   - Read `specs/requirements.md`, find REQ-001
   - Read epic file
   - Read task file

5. Output tree:
```
REQ-001: "User notification system required"
  └─ PRD: specs/prd/prd.md
     └─ Epic: specs/epics/notification-system/epic.md
        └─ Task: specs/epics/notification-system/001.md
           "Implement push notification service"

Commits:
- abc1234: "REQ-001: add notifications table"
- def5678: "REQ-001: implement push delivery"
```

**Output:**
```
Traceability chain for: specs/epics/notification-system/001.md

REQ-001: User notification system required
  └─ PRD: specs/prd/prd.md
     └─ Epic: specs/epics/notification-system/epic.md
        └─ Task: 001.md: Database schema

✅ Full traceability verified
```

---

### `/pm-workflow block <description>`

Mark something as blocked.

**Behavior:**

1. Read `.pm/state.json`

2. Append to `blocked` array:
```json
{
  "skill": "<current-skill>",
  "description": "<user description>",
  "since": "2026-03-30",
  "blocked_by": "<external dependency>"
}
```

3. Update state file

**Output:**
```
🚫 Blocked: <description>
   Since: 2026-03-30

Run: "what's blocked" to see all blockers
```

---

### `/pm-workflow unblock`

Clear a blocker.

**Behavior:**

1. Read `.pm/state.json`

2. Remove item from `blocked` array

3. Append to audit log:
```json
{"timestamp":"2026-03-30T19:00:00Z","action":"unblock","description":"<blocker>","reason":"<resolved>"}
```

**Output:**
```
✅ Blocker cleared
Ready to continue: "what's next"
```

---

## State File Schema

`.pm/state.json`:

```json
{
  "phase": 3,
  "phase_name": "Plan",
  "next_req_id": 15,
  "completed_skills": [
    "discovery-process",
    "problem-framing-canvas",
    "discovery-interview-prep",
    "opportunity-solution-tree",
    "product-strategy-session",
    "positioning-workshop",
    "prioritization-advisor",
    "roadmap-planning",
    "prd-development",
    "proto-persona",
    "epic-hypothesis"
  ],
  "current_skill": "epic-breakdown-advisor",
  "blocked": [
    {
      "skill": "discovery-interview-prep",
      "description": "Waiting for interview transcripts",
      "since": "2026-03-28",
      "blocked_by": "Customer schedule"
    }
  ]
}
```

---

## Audit Log Format

`.pm/audit.log` — append-only JSON lines:

```json
{"timestamp":"2026-03-30T14:22:31Z","phase":1,"skill":"discovery-process","req_id":"REQ-001","artifacts_created":["specs/requirements.md"]}
{"timestamp":"2026-03-30T15:10:45Z","phase":2,"skill":"product-strategy-session","artifacts_created":["strategy/positioning.md","strategy/roadmap.md"]}
{"timestamp":"2026-03-30T16:00:00Z","phase":3,"skill":"epic-hypothesis","artifacts_created":["specs/epics/notification-system/epic.md"]}
{"timestamp":"2026-03-30T17:00:00Z","phase":4,"action":"task_start","task":"specs/epics/notification-system/001.md"}
{"timestamp":"2026-03-30T18:30:00Z","phase":4,"action":"task_complete","task":"specs/epics/notification-system/001.md","commits":["abc1234"]}
```

---

## Example Session

```
You: /pm-workflow init

Claude: ✅ Workspace initialized
        ✅ Created .pm/ and specs/ directories

        Next: Write requirements in specs/requirements.md
        Then: "parse the requirements"

---

You: /pm-workflow done discovery-process

Claude: ✅ Marked discovery-process complete
        ✅ REQ-001 assigned

        Run: "what's next" to continue

---

You: /pm-workflow trace specs/epics/notification-system/001.md

Claude: Traceability chain:
        REQ-001 → PRD → Epic → Task 001

        ✅ Full traceability verified
```
