# Phase 5: Track

Maintain transparent progress at every step.

## When to Use

User says:
- "standup"
- "what's our status"
- "what's blocked"
- "what's next"
- "search for X"
- "show progress"

## Behavior

**All tracking operations run as bash scripts** — deterministic, instant, no LLM token cost.

---

### Status Command

**Trigger:** "what's our status" / "show status"

**Action:**
```bash
bash references/scripts/status.sh
```

**Output:**
```
========================================
  Project Status
========================================

  Phase:       3 — Plan
  Current:     epic-breakdown-advisor
  Completed:   7 skills
  Blocked:     0 items

  Recent activity:
    [2] product-strategy-session → strategy/positioning.md
    [2] prd-development → specs/prd/prd.md
    [3] epic-hypothesis → specs/epics/notification-system/epic.md

========================================
```

**Script behavior:**
- Reads `.pm/state.json`
- Reads `.pm/audit.log` (last 5 entries)
- Calculates phase progress
- Lists blocked items
- **No LLM reasoning required**

---

### Standup Command

**Trigger:** "standup" / "daily standup"

**Action:**
```bash
bash references/scripts/standup.sh
```

**Output:**
```
## Standup — 2026-03-30

**Phase:** 3 — Plan

---

### ✅ Done

- Phase 1: discovery-process
  → specs/requirements.md
- Phase 1: problem-framing-canvas
  → discovery/problem-framing.md
- Phase 2: product-strategy-session
  → strategy/positioning.md, strategy/roadmap.md
- Phase 2: prd-development
  → specs/prd/prd.md
- Phase 3: epic-hypothesis
  → specs/epics/notification-system/epic.md
- Phase 3: epic-breakdown-advisor
  → specs/epics/notification-system/001.md, 002.md, 003.md

---

### 🚫 Blocked

- None

---

### ▶️ Next

- Run `/user-story-mapping-workshop` if workflow is complex
- Or start execution: "start working on task 001"
```

**Script behavior:**
- Reads `.pm/audit.log` (last 7 days)
- Groups by phase
- Reads blocked items from state
- Generates `.pm/standup.md`
- **No LLM reasoning required**

---

### Search Command

**Trigger:** "search for X" / "find X" / "where is X"

**Action:**
```bash
bash references/scripts/search.sh "<query>"
```

**Output:**
```
Searching for: authentication
========================================

📄 requirements.md:
  12: Users must authenticate via email/password
  45: Admin authentication required for dashboard

📁 All artifacts:
  specs/personas/admin.md
  specs/epics/auth-system/epic.md
  specs/stories/us-012.md

📜 Audit log:
  [1] discovery-process → specs/requirements.md
  [3] epic-hypothesis → specs/epics/auth-system/epic.md
```

**Script behavior:**
- Searches `specs/requirements.md`
- Searches all `.md` under `specs/`
- Searches `.pm/audit.log`
- **No LLM reasoning required**

---

### Blocked Command

**Trigger:** "what's blocked" / "show blockers"

**Action:**
```bash
python3 -c "
import json
state = json.load(open('.pm/state.json'))
blocked = state.get('blocked', [])
if not blocked:
    print('✅ No blocked items')
else:
    print('🚫 Blocked Items:\n')
    for item in blocked:
        print(f\"- {item.get('description', 'Unknown')}\")
        print(f\"  Since: {item.get('since', 'N/A')}\")
        print(f\"  Blocked by: {item.get('blocked_by', 'N/A')}\")
        print()
"
```

**Output:**
```
🚫 Blocked Items:

- discovery-interview-prep
  Since: 2026-03-28
  Blocked by: Waiting for interview transcripts
```

---

### Next Command

**Trigger:** "what's next" / "what should I work on"

**Action:**
```bash
python3 -c "
import json
state = json.load(open('.pm/state.json'))
phase = state.get('phase', 0)
current = state.get('current_skill')
completed = state.get('completed_skills', [])

if current:
    print(f'Current: /{current}')
else:
    # Logic to determine next skill based on phase + completed
    # (simplified version)
    if phase == 1:
        next_skill = 'discovery-process' if 'discovery-process' not in completed else 'problem-framing-canvas'
    elif phase == 2:
        next_skill = 'product-strategy-session'
    elif phase == 3:
        next_skill = 'epic-breakdown-advisor'
    elif phase == 4:
        # Check for incomplete tasks
        print('Check task status with: bash references/scripts/status.sh')
        exit()
    else:
        next_skill = 'unknown'

    print(f'Next: /{next_skill}')
"
```

**Output:**
```
Next: /epic-breakdown-advisor
```

---

## Mark Blocked

**Trigger:** "block X because Y" / "mark X as blocked"

**Action:**
Update `.pm/state.json`:

```json
{
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

## Clear Blocked

**Trigger:** "unblock X" / "resolved X blocker"

**Action:**
Remove from `state.blocked` array and append to audit log:

```json
{"timestamp":"2026-03-30T19:00:00Z","phase":1,"action":"unblock","skill":"discovery-interview-prep","reason":"Transcripts received"}
```

---

## Script Locations

All scripts live in `references/scripts/`:

```
pm-workflow/
├── SKILL.md
└── references/
    ├── brainstorm.md
    ├── document.md
    ├── plan.md
    ├── execute.md
    ├── track.md
    ├── admin.md
    ├── conventions.md
    └── scripts/
        ├── status.sh
        ├── standup.sh
        └── search.sh
```

---

## Benefits of Script-Based Tracking

| Traditional (LLM-based) | Script-Based (Deterministic) |
|-------------------------|------------------------------|
| $0.01-0.05 per status check | $0.00 — runs locally |
| 1-3 seconds latency | <100ms response |
| Inconsistent output | Exact same format every time |
| Uses context window | Zero context usage |
| Can hallucinate | Impossible to hallucinate |

---

## Audit Log Format

`.pm/audit.log` is append-only JSON lines:

```json
{"timestamp":"2026-03-30T14:22:31Z","phase":1,"skill":"discovery-process","req_id":"REQ-001","artifacts_created":["specs/requirements.md"]}
{"timestamp":"2026-03-30T15:10:45Z","phase":2,"skill":"product-strategy-session","artifacts_created":["strategy/positioning.md"]}
{"timestamp":"2026-03-30T16:00:00Z","phase":3,"skill":"epic-hypothesis","artifacts_created":["specs/epics/notification-system/epic.md"]}
{"timestamp":"2026-03-30T17:00:00Z","phase":4,"action":"task_start","task":"specs/epics/notification-system/001.md"}
{"timestamp":"2026-03-30T18:30:00Z","phase":4,"action":"task_complete","task":"specs/epics/notification-system/001.md","commits":["abc1234"]}
```

---

## Example Session

```
You: "standup"

Claude: [Runs bash references/scripts/standup.sh]

        ## Standup — 2026-03-30

        **Phase:** 4 — Execute

        ### ✅ Done
        - Phase 1: discovery-process
        - Phase 2: product-strategy-session, prd-development
        - Phase 3: epic-breakdown-advisor
        - Phase 4: Task 001 complete (database schema)

        ### 🚫 Blocked
        - None

        ### ▶️ Next
        - Task 002: push notification service

---

You: "search for notification"

Claude: [Runs bash references/scripts/search.sh "notification"]

        Searching for: notification
        ========================================

        📄 requirements.md:
          5: REQ-001: User Notification System
          12: Users can receive push notifications

        📁 All artifacts:
          specs/prd/prd.md
          specs/epics/notification-system/epic.md
          specs/epics/notification-system/001.md
          specs/epics/notification-system/002.md

---

You: "what's next"

Claude: [Runs bash scripts to determine next action]

        Next: Start working on Task 002
        Run: "start working on task 002"
```

---

## Transition Between Phases

Track phase doesn't transition — it's always available.

User can return to any phase:
- "brainstorm X" → Phase 1
- "document X" → Phase 2
- "plan X" → Phase 3
- "execute X" → Phase 4
- "standup" / "status" → Phase 5
