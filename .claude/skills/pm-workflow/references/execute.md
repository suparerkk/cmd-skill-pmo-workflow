# Phase 4: Execute

Build exactly what was specified.

## When to Use

User says:
- "start working on X"
- "implement X"
- "work on issue X"
- "build X"

## Behavior

### 1. Read Task Specification

Read the task file from `specs/epics/<feature-name>/<task-id>.md`

If task doesn't exist:
```
Output: "I need a task specification first. Run: break down the X epic"
Exit
```

---

### 2. Validate Traceability

Verify the complete chain exists:
- `specs/requirements.md` → REQ ID
- `specs/prd/prd.md`
- `specs/epics/<name>/epic.md`
- `specs/epics/<name>/<task>.md`

If any link is missing:
```
Output: "Missing <file>. Run: <appropriate phase command>"
Exit
```

---

### 3. Detect Spec Drift

Check if requirements or PRD changed after the epic/tasks were created.

**How to detect:**

1. Read `updated` timestamp from the task's parent epic (`specs/epics/<name>/epic.md`)
2. Read `updated` timestamp from `specs/requirements.md` and `specs/prd/prd.md`
3. If requirements or PRD were updated **after** the epic was created/last updated → spec drift detected

**Also check:**

4. Read the task's `requirements` array from epic frontmatter
5. Verify those REQ IDs still exist in `specs/requirements.md` (not removed or renumbered)
6. Check if any new REQs were added since the epic was planned (compare REQ count or `next_req_id` in state vs epic's REQ list)

**If drift detected:**

```
⚠️  Spec drift detected:

  specs/requirements.md was updated on 2026-04-02
  specs/epics/notification-system/epic.md was last planned on 2026-03-30

  Changes since epic was planned:
  - REQ-018, REQ-019 added (not covered by current tasks)
  - REQ-005 was updated (user limit changed from 1,000 to 10,000)

  Options:
  1. Continue anyway — current task is unaffected
  2. Replan — "replan the notification-system epic" to update tasks
  3. Review — "show me what changed in requirements"
```

**If no drift:** Proceed silently — don't mention it.

**Important:** Only block execution if the drift directly affects the current task's REQ IDs. If new REQs were added but don't overlap with this task, warn but allow continuing.

---

### 4. Check Dependencies

Read task frontmatter:

```yaml
depends_on: [002, 003]
parallel: true
conflicts_with: []
```

If `depends_on` tasks aren't complete, show the status of each blocking dependency:
```
❌ Blocked: Task 006 depends on tasks that aren't complete yet.

   - Task 002: in-progress (started 2026-03-30)
   - Task 003: open (not started)

Say: "standup" to see overall status
```

If task has `conflicts_with` and a conflicting task is currently `in-progress`:
```
⚠️  Task 003 conflicts with Task 002 (both modify notification model).
   Task 002 is currently in-progress.

   Options:
   1. Wait for Task 002 to complete
   2. Start anyway (risk merge conflicts)
```

---

### 5. Scope Decision (if needed)

If task is large or has investment implications:

```
Run: /feature-investment-advisor
```

Evaluates:
- Revenue impact
- Cost structure
- ROI
- Strategic alignment

Only for major scope decisions, not routine implementation.

---

### 6. Begin Implementation

Follow the task specification exactly:

**From task file:**
- Acceptance criteria
- Technical details
- Files to modify
- Testing strategy

**Implementation discipline:**
1. Read acceptance criteria carefully
2. Implement each criterion
3. Write tests as specified
4. Verify against criteria
5. Commit with traceability

---

### 7. Commit with Traceability

Every commit must include REQ ID:

```bash
git commit -m "REQ-001: implement push notification service

- Add Firebase Cloud Messaging integration
- Create notification queue worker
- Add retry logic for failed deliveries

Closes #<issue-number>"
```

**Commit message format:**
```
REQ-XXX: <short description>

<detailed changes>

Trace: specs/epics/<name>/<task>.md
```

---

### 8. Update Task Status

When task starts:
```markdown
---
status: in_progress
started: 2026-03-30
---
```

When task completes:
```markdown
---
status: completed
started: 2026-03-30
completed: 2026-03-31
---
```

---

### 9. Log Progress

Append to `.pm/audit.log`:

**On start:**
```json
{"timestamp":"2026-03-30T17:00:00Z","phase":4,"action":"task_start","task":"specs/epics/notification-system/001.md","req_id":"REQ-001"}
```

**On completion:**
```json
{"timestamp":"2026-03-30T18:30:00Z","phase":4,"action":"task_complete","task":"specs/epics/notification-system/001.md","req_id":"REQ-001","commits":["abc1234"]}
```

---

### 10. Update Context

Update `.pm/context.md`:

```markdown
## Current State
- Phase: 4 Execute
- Working on: Task 001 (database schema)
- Completed: 0/7 tasks

## Key Decisions
- 2026-03-30: Using JSONB for notification metadata (flexibility)
```

---

## Output

**On start:**
```
✅ Task 001: Database schema
✅ Dependencies: none
✅ Traceability: REQ-001 → PRD → Epic → Task

Starting implementation...
```

**On completion:**
```
✅ Task 001 complete
✅ Commits: abc1234
✅ Tests: passing

Ready tasks (dependencies met):
  - Task 002: Push notification service (parallel: true)
  - Task 003: Email notification service (parallel: true)

Say: "start working on task 002" or "start working on task 003"
Tasks 002 and 003 can run in parallel.
```

---

## Skills Used

Primary:
- None (implementation is direct coding)

Secondary:
- `feature-investment-advisor` — for large scope decisions only

---

## Example

```
You: "start working on task 001"

Claude: Reading task specification...
        ✅ Task 001: Database schema
        ✅ Traceability: REQ-001 → PRD → Epic → Task
        ✅ Dependencies: none

        Implementation plan:
        1. Create notifications table
        2. Add indexes for user_id and created_at
        3. Write migration
        4. Add model + repository

        Starting implementation...

        [Implements according to spec]

        ✅ Created migration: add_notifications_table.rb
        ✅ Created model: app/models/notification.rb
        ✅ Tests passing

        Commit: abc1234 "REQ-001: add notifications table"

        Task 001 complete!

        Ready tasks (dependencies met):
          - Task 002: Push notification service (parallel: true)
          - Task 003: Email notification service (parallel: true)

        Say: "start working on task 002" or "start working on task 003"
        Tasks 002 and 003 can run in parallel.
```

---

## Blocked Tasks

If task is blocked by dependencies:

```
You: "start working on task 006"

Claude: ❌ Blocked: Task 006 depends on tasks that aren't complete yet.

        - Task 002: in-progress (started 2026-03-30)
        - Task 003: open (not started)

        Say: "standup" to see overall status
```

If task conflicts with an in-progress task:

```
You: "start working on task 003"

Claude: ⚠️  Task 003 conflicts with Task 002 (both modify notification model).
        Task 002 is currently in-progress.

        Options:
        1. Wait for Task 002 to complete
        2. Start anyway (risk merge conflicts)
```

---

## Transition to Next Phase

User triggers Phase 5 (Track) by saying:
- "standup"
- "what's our status"
- "what's blocked"
- "what's next"

Or continues execution with:
- "start working on task X"
