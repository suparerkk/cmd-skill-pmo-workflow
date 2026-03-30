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

### 3. Check Dependencies

Read task frontmatter:

```yaml
dependencies:
  depends_on: [002, 003]
  blocks: [006]
  parallel: true
  conflicts_with: []
```

If `depends_on` tasks aren't complete:
```
Output: "Blocked: Task 002 and 003 must complete first"
Suggest: "standup" to see status
Exit
```

---

### 4. Scope Decision (if needed)

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

### 5. Begin Implementation

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

### 6. Commit with Traceability

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

### 7. Update Task Status

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

### 8. Log Progress

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

### 9. Update Context

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

Next task: 002 (push notification service)
Say: "start working on task 002"
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
        Next: start working on task 002 (push notification service)
```

---

## Blocked Tasks

If task is blocked:

```
You: "start working on task 006"

Claude: ❌ Blocked: Task 006 depends on 002 and 003

        Current status:
        - Task 002: in_progress (50% complete)
        - Task 003: not started

        Say: "standup" to see overall status
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
