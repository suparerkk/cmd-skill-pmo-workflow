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
import json, glob, re, os

# 1. State-level blockers (manual blocks via /pm-workflow block)
state = json.load(open('.pm/state.json'))
blocked = state.get('blocked', [])

print('🚫 Blocked Items')
print('=' * 50)

if blocked:
    print('\n📌 Manual Blocks:\n')
    for item in blocked:
        print(f\"- {item.get('description', 'Unknown')}\")
        print(f\"  Since: {item.get('since', 'N/A')}\")
        print(f\"  Blocked by: {item.get('blocked_by', 'N/A')}\")
        print()

# 2. Task dependency blocks (tasks waiting on incomplete dependencies)
active_epic = state.get('active_epic')
if active_epic:
    epic_dir = f'specs/epics/{active_epic}'
    if os.path.isdir(epic_dir):
        task_files = sorted(glob.glob(f'{epic_dir}/[0-9]*.md'))
        dep_blocked = []
        for tf in task_files:
            with open(tf) as f:
                content = f.read()
            # Extract status
            status_match = re.search(r'^status:\s*(.+)', content, re.MULTILINE)
            status = status_match.group(1).strip() if status_match else 'unknown'
            if status in ('closed', 'completed', 'in-progress', 'in_progress'):
                continue
            # Extract depends_on
            dep_match = re.search(r'^depends_on:\s*\[([^\]]*)\]', content, re.MULTILINE)
            if not dep_match or not dep_match.group(1).strip():
                continue
            deps = [d.strip() for d in dep_match.group(1).split(',') if d.strip()]
            # Check each dependency status
            blocking = []
            for dep in deps:
                dep_file = f'{epic_dir}/{dep.zfill(3)}.md'
                if os.path.exists(dep_file):
                    with open(dep_file) as df:
                        dc = df.read()
                    ds = re.search(r'^status:\s*(.+)', dc, re.MULTILINE)
                    ds = ds.group(1).strip() if ds else 'unknown'
                    dn = re.search(r'^name:\s*(.+)', dc, re.MULTILINE)
                    dn = dn.group(1).strip() if dn else dep
                    if ds not in ('closed', 'completed'):
                        blocking.append({'id': dep, 'name': dn, 'status': ds})
            if blocking:
                name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
                task_name = name_match.group(1).strip() if name_match else os.path.basename(tf)
                dep_blocked.append({'file': tf, 'name': task_name, 'blocking': blocking})

        if dep_blocked:
            print('🔗 Dependency Blocks:\n')
            for item in dep_blocked:
                print(f\"- {os.path.basename(item['file'])}: {item['name']}\")
                print(f\"  Waiting on:\")
                for b in item['blocking']:
                    print(f\"    - Task {b['id']}: {b['name']} (status: {b['status']})\")
                print()

if not blocked and not (active_epic and dep_blocked):
    print('\n✅ No blocked items')
"
```

**Output:**
```
🚫 Blocked Items
==================================================

📌 Manual Blocks:

- Waiting for interview transcripts
  Since: 2026-03-28
  Blocked by: Customer schedule

🔗 Dependency Blocks:

- 004.md: API endpoints
  Waiting on:
    - Task 002: Push notification service (status: in-progress)
    - Task 003: Email notification service (status: open)

- 006.md: Integration tests
  Waiting on:
    - Task 004: API endpoints (status: open)

🔥 Critical Path (blocked AND blocking others):

- Task 004: API endpoints
  ⬆️ Blocked by: Task 002 (in-progress), Task 003 (open)
  ⬇️ Blocking: Task 006 (Integration tests)
  → Unblocking Task 004 will unblock 1 downstream task
```

The **Critical Path** section identifies tasks that are both waiting on dependencies AND have other tasks waiting on them. These are the highest-priority bottlenecks — unblocking them has the biggest cascade effect.

---

### Deliverables Command

**Trigger:** "deliverables status" / "track deliverables" / "what deliverables are pending"

**Action:**
```bash
python3 -c "
import re, os

tracker = 'specs/deliverable-tracker.md'
if not os.path.exists(tracker):
    print('No deliverable tracker found. Run Phase 3 (Plan) first.')
    exit()

with open(tracker) as f:
    content = f.read()

# Parse table rows
lines = content.split('\n')
in_table = False
header_seen = False
items = []
for line in lines:
    if '| ID |' in line:
        in_table = True
        header_seen = False
        continue
    if in_table and '|---' in line:
        header_seen = True
        continue
    if in_table and header_seen and line.startswith('|'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) >= 7:
            items.append({
                'id': cols[0], 'name': cols[1], 'role': cols[2],
                'owner': cols[3], 'reqs': cols[4], 'due': cols[5],
                'status': cols[6]
            })
    elif in_table and header_seen and not line.startswith('|'):
        in_table = False

if not items:
    print('No tracked deliverables found.')
    exit()

print('📋 Deliverable Tracker')
print('=' * 50)
for item in items:
    icon = {'Not Started': '⬜', 'In Progress': '🔵', 'In Review': '🟡', 'Approved': '✅', 'Blocked': '🔴'}.get(item['status'], '⬜')
    print(f\"{icon} {item['id']}: {item['name']}\")
    print(f\"   Owner: {item['role']} ({item['owner']})\")
    print(f\"   Due: {item['due']} | Status: {item['status']}\")
    print()

total = len(items)
done = sum(1 for i in items if i['status'] == 'Approved')
print(f'Progress: {done}/{total} approved')
"
```

**Output:**
```
📋 Deliverable Tracker
==================================================
⬜ DT-001: Wireframes / UI Mockups
   Owner: Designer (TBD)
   Due: TBD | Status: Not Started

⬜ DT-002: ER Diagram
   Owner: Developer (TBD)
   Due: TBD | Status: Not Started

⬜ DT-003: API Specification (OpenAPI)
   Owner: Developer (TBD)
   Due: TBD | Status: Not Started

Progress: 0/3 approved
```

---

### Deliverable Update Command

**Trigger:** "update deliverable DT-001" / "mark wireframes as in progress" / "assign DT-002 to John" / "set DT-003 due date to April 15"

**Action:** Read `specs/deliverable-tracker.md`, update the specified deliverable's fields, and write back.

**Supported updates:**
- **Status:** "mark DT-001 as in progress" / "DT-002 is approved"
  - Valid values: `Not Started`, `In Progress`, `In Review`, `Approved`, `Blocked`
- **Owner:** "assign DT-001 to Jane" / "DT-002 owner is John"
- **Due date:** "set DT-001 due April 15" / "DT-003 due 2026-04-20"
- **Multiple at once:** "DT-001 is in review, assigned to Jane, due April 10"

**Behavior:**

1. Read `specs/deliverable-tracker.md`
2. Find the row matching the deliverable ID or name
3. Update the specified fields in the markdown table
4. Update the `updated` timestamp in frontmatter
5. Append to `.pm/audit.log`:
   ```json
   {"timestamp":"2026-04-02T10:00:00Z","phase":5,"action":"deliverable_update","id":"DT-001","changes":{"status":"In Review","owner":"Jane"}}
   ```

**Update project data:**
```bash
python3 .pm/scripts/update-project-data.py update-deliverable '<deliverable-id>' '{"status":"<new-status>","owner":"<owner>","due":"<date>"}'
```

**Output:**
```
✅ Updated DT-001: Wireframes / UI Mockups
   Status: Not Started → In Review
   Owner: TBD → Jane
   Due: TBD → 2026-04-10

📋 Progress: 0/3 approved (1 in review)
```

**If deliverable not found:**
```
❌ Deliverable "DT-999" not found.
   Available: DT-001, DT-002, DT-003

   To add a new deliverable: "add deliverable <name>"
```

**Add new deliverable:**
```
Trigger: "add deliverable <name>" / "track a new deliverable"

Prompts for:
- Name (required)
- Role: Designer / Developer / PM / External
- Owner (optional)
- Related REQ IDs (optional)
- Due date (optional)

Appends a new row to the tracker table with auto-assigned ID (DT-004, etc.)
```

---

### Sign-Off Status Command

**Trigger:** "sign-off status" / "what needs client approval" / "approval status"

**Action:**
```bash
python3 -c "
import os, re

sign_off_files = []

# Check SRS
srs = 'specs/srs/srs.md'
if os.path.exists(srs):
    with open(srs) as f:
        content = f.read()
    status = 'draft'
    m = re.search(r'status:\s*(\w+)', content)
    if m: status = m.group(1)
    sign_off_files.append(('SRS', srs, status))

# Check System Design
sd = 'specs/design/system-design.md'
if os.path.exists(sd):
    with open(sd) as f:
        content = f.read()
    status = 'draft'
    m = re.search(r'status:\s*(\w+)', content)
    if m: status = m.group(1)
    sign_off_files.append(('System Design', sd, status))

# Check Test Plan
tp = 'specs/test-plan/test-plan.md'
if os.path.exists(tp):
    with open(tp) as f:
        content = f.read()
    status = 'draft'
    m = re.search(r'status:\s*(\w+)', content)
    if m: status = m.group(1)
    sign_off_files.append(('Test Plan', tp, status))

# Check User Journeys
jdir = 'specs/journeys'
if os.path.exists(jdir):
    for f in sorted(os.listdir(jdir)):
        if f.endswith('.md'):
            sign_off_files.append(('User Journey', os.path.join(jdir, f), 'draft'))

if not sign_off_files:
    print('No sign-off documents found yet. Complete Phase 2 and 3 first.')
    exit()

print('📝 Sign-Off Status')
print('=' * 50)
icons = {'draft': '📝', 'review': '🔍', 'approved': '✅'}
for name, path, status in sign_off_files:
    icon = icons.get(status, '📝')
    print(f'{icon} {name}: {status.upper()}')
    print(f'   File: {path}')
    print()

total = len(sign_off_files)
approved = sum(1 for _, _, s in sign_off_files if s == 'approved')
print(f'Approved: {approved}/{total}')
if approved < total:
    print(f'⚠️  {total - approved} document(s) still need client sign-off')
"
```

**Output:**
```
📝 Sign-Off Status
==================================================
📝 SRS: DRAFT
   File: specs/srs/srs.md

📝 System Design: DRAFT
   File: specs/design/system-design.md

📝 Test Plan: DRAFT
   File: specs/test-plan/test-plan.md

📝 User Journey: DRAFT
   File: specs/journeys/journey-admin.md

Approved: 0/4
⚠️  4 document(s) still need client sign-off
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

**Update project data:**
```bash
python3 .pm/scripts/update-project-data.py replace 'blockers' '<current-blockers-from-state.json>'
```

---

## Clear Blocked

**Trigger:** "unblock X" / "resolved X blocker"

**Action:**
Remove from `state.blocked` array and append to audit log:

```json
{"timestamp":"2026-03-30T19:00:00Z","phase":1,"action":"unblock","skill":"discovery-interview-prep","reason":"Transcripts received"}
```

**Update project data:**
```bash
python3 .pm/scripts/update-project-data.py replace 'blockers' '<current-blockers-from-state.json>'
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
