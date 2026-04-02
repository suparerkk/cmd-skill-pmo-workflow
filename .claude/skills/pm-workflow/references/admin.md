# Admin Operations

Setup, initialization, and utility commands.

## Commands

### `/pm-workflow init`

Initialize workspace structure and check/install prerequisites.

**Behavior:**

1. **Check prerequisites:**

   **Git:**
   ```bash
   git --version
   ```
   If missing: "❌ Git is required. Install from https://git-scm.com/"

   **Python 3:**
   ```bash
   python3 --version
   ```
   If missing:
   - macOS: `brew install python3`
   - Ubuntu/Debian: `sudo apt-get install python3`
   - Windows: Download from https://www.python.org/downloads/

   **Bash:**
   - Usually pre-installed on macOS/Linux
   - Windows: Install Git Bash or WSL

   **Product-Manager-Skills:**
   Check if installed:
   ```bash
   ls ~/.claude/skills/ 2>/dev/null | grep -i product
   # OR check in project
   ls .claude/skills/ 2>/dev/null | grep -i product
   ```

   If missing, prompt user:
   ```
   ⚠️  Product-Manager-Skills not found.

   Install now? (y/n)

   If yes:
   git clone https://github.com/deanpeters/Product-Manager-Skills.git /tmp/pm-skills
   cp -r /tmp/pm-skills/skills/* ~/.claude/skills/
   rm -rf /tmp/pm-skills

   ✅ Product-Manager-Skills installed
   ```

2. **Create directory structure:**
```
.pm/
├── context.md
├── state.json
├── audit.log
└── scripts/          # Create individual symlinks (see below)

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

2. **Symlink scripts to `.pm/scripts/`:**

Create `.pm/scripts/` directory and symlink each script individually using **correct relative paths**:

```bash
mkdir -p .pm/scripts
# From .pm/scripts/, project root is ../../
ln -sf ../../.claude/skills/pm-workflow/references/scripts/status.sh .pm/scripts/status.sh
ln -sf ../../.claude/skills/pm-workflow/references/scripts/standup.sh .pm/scripts/standup.sh
ln -sf ../../.claude/skills/pm-workflow/references/scripts/search.sh .pm/scripts/search.sh
ln -sf ../../.claude/skills/pm-workflow/references/scripts/cleanup.sh .pm/scripts/cleanup.sh
ln -sf ../../.claude/skills/pm-workflow/references/scripts/generate-report.py .pm/scripts/generate-report.py
ln -sf ../../.claude/skills/pm-workflow/references/scripts/dashboard-server.py .pm/scripts/dashboard-server.py
ln -sf ../../.claude/skills/pm-workflow/references/scripts/sync-project-data.py .pm/scripts/sync-project-data.py
ln -sf ../../.claude/skills/pm-workflow/references/scripts/update-project-data.py .pm/scripts/update-project-data.py
```

**Important:** The relative path must be `../../.claude/...` (2 levels up from `.pm/scripts/` to project root). Do NOT use `../../../` (3 levels).

3. **Ask for project name and language:**
```
📝 What's the project name?

📝 Default language for generated documents?
   1. English (default)
   2. Thai (ภาษาไทย)
```

The language sets the default for all generated documents (SRS, user journeys, system design, test plan, etc.). Users can still override per-document by saying "generate the SRS in Thai" or "in English".

4. Initialize `.pm/state.json`:
```json
{
  "project_name": "Notification System",
  "language": "en",
  "phase": 0,
  "phase_name": "Setup",
  "next_req_id": 1,
  "completed_skills": [],
  "current_skill": null,
  "blocked": []
}
```

After creating state.json, initialize `.pm/project-data.json`:

```bash
python3 .pm/scripts/update-project-data.py init '<project-name>' '<language>'
```

5. Create `.pm/context.md`:
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
🔍 Checking prerequisites...

✅ Git: 2.43.0
✅ Python 3: 3.11.5
✅ Bash: 5.2.15
✅ Product-Manager-Skills: Installed (12 skills found)

---
✅ Workspace initialized
✅ Created .pm/ directory
✅ Created specs/ directory
✅ Symlinked bash scripts

Next step:
Write your requirements in specs/requirements.md
Then say: "parse the requirements" or "I want to build X"
```

**If prerequisites missing:**
```
🔍 Checking prerequisites...

✅ Git: 2.43.0
✅ Python 3: 3.11.5
❌ Product-Manager-Skills: Not found

Install Product-Manager-Skills? (y/n)

[If yes]
⏳ Installing...
git clone https://github.com/deanpeters/Product-Manager-Skills.git
✅ Product-Manager-Skills installed (12 skills)

[Continue with workspace init...]
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

Also update `.pm/project-data.json`:
```bash
python3 .pm/scripts/update-project-data.py append 'audit' '<audit-entry-json>'
```

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

Also update `.pm/project-data.json`:
```bash
python3 .pm/scripts/update-project-data.py replace 'blockers' '<current-blockers-array-from-state.json>'
```

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

Also update `.pm/project-data.json`:
```bash
python3 .pm/scripts/update-project-data.py replace 'blockers' '<current-blockers-array-from-state.json>'
```

**Output:**
```
✅ Blocker cleared
Ready to continue: "what's next"
```

---

### `/pm-workflow replan <epic-name>`

Regenerate epic and tasks after requirements changed mid-execution.

**When to use:** After spec drift is detected (execute.md Step 3), after new requirements are ingested, or when the user says "replan the X epic".

**Behavior:**

1. Read current epic at `specs/epics/<epic-name>/epic.md`

2. Identify completed tasks (status: closed) — these are preserved

3. Re-read latest `specs/requirements.md` and `specs/prd/prd.md`

4. Run `/epic-breakdown-advisor` with context:
   - Current epic structure
   - Completed tasks (do not regenerate)
   - New/changed requirements since last plan
   - Existing task dependencies

5. Generate updated tasks:
   - **Completed tasks** — kept as-is, not modified
   - **In-progress tasks** — flagged for user review (may need scope adjustment)
   - **Open tasks** — regenerated based on latest requirements
   - **New tasks** — created for new requirements not covered by existing tasks

6. Update epic frontmatter:
   ```yaml
   updated: <now>
   replanned: true
   replanned_date: <now>
   replanned_reason: "New requirements REQ-018, REQ-019 added"
   ```

7. Append to `.pm/audit.log`:
   ```json
   {"timestamp":"2026-04-02T10:00:00Z","phase":4,"action":"replan","epic":"notification-system","reason":"spec drift","tasks_preserved":3,"tasks_regenerated":2,"tasks_added":2}
   ```

8. Update `.pm/context.md` with replan note

Also update `.pm/project-data.json`:
```bash
python3 .pm/scripts/update-project-data.py replace 'tasks' '<new-tasks-array>'
python3 .pm/scripts/update-project-data.py replace 'traceability' '<new-traceability-array>'
python3 .pm/scripts/update-project-data.py link-stories
```

**Output:**
```
🔄 Replanned: notification-system epic

  Preserved: 3 completed tasks (001, 002, 003)
  ⚠️  Review needed: 1 in-progress task (004 — scope may have changed)
  Regenerated: 2 open tasks (005, 006)
  New: 2 tasks added (007, 008) for REQ-018, REQ-019

  Say: "standup" to see updated task list
```

---

### `/pm-workflow reopen <task-id>`

Reopen a completed task that needs rework.

**When to use:** Implementation found to be defective, requirements changed after completion, or acceptance criteria weren't fully met.

**Behavior:**

1. Read task file at `specs/epics/<active-epic>/<task-id>.md`

2. Verify task is currently `status: closed` or `status: completed`
   - If task is already open: "Task <task-id> is already open."

3. Update task frontmatter:
   ```yaml
   status: open
   reopened: true
   reopened_date: <now>
   reopened_reason: "<user-provided reason>"
   completed: null
   ```

4. Recalculate epic progress (one fewer completed task)

5. Append to `.pm/audit.log`:
   ```json
   {"timestamp":"2026-04-02T14:00:00Z","phase":4,"action":"reopen","task":"specs/epics/notification-system/001.md","reason":"<user reason>"}
   ```

6. Update `.pm/context.md`

Also update `.pm/project-data.json`:
```bash
python3 .pm/scripts/update-project-data.py update-task '<task-id>' '{"status": "open", "completed": ""}'
```

**Output:**
```
🔄 Reopened: Task 001 (Database schema)
   Reason: Migration failed on production — schema needs adjustment
   Epic progress: 28% → 14% (2/7 → 1/7 complete)

   Say: "start working on task 001" to begin rework
```

---

### `/pm-workflow next-phase`

Validate prerequisites and advance to the next phase.

**Behavior:**

1. Read `.pm/state.json` to get current phase

2. Validate prerequisites for the **next** phase:

   | Current | Next | Prerequisites |
   |---------|------|---------------|
   | 0 Setup | 1 Brainstorm | `specs/requirements.md` exists (from ingest) OR user wants to start from scratch |
   | 1 Brainstorm | 2 Document | `specs/requirements.md` has at least 1 REQ |
   | 2 Document | 3 Plan | `specs/prd/prd.md` exists with `requirements` array |
   | 3 Plan | 4 Execute | `specs/epics/<name>/epic.md` exists with at least 1 task file |
   | 4 Execute | 5 Track | At least 1 task started (status: in-progress or closed) |

3. If prerequisites not met:
   ```
   ❌ Cannot advance to Phase 2 (Document)

   Missing:
   - specs/requirements.md has 0 REQs (need at least 1)

   To fix: "I want to build X" to brainstorm requirements
   ```

4. If prerequisites met, advance:
   - Update `state.json`: `phase` and `phase_name`
   - Also update `.pm/project-data.json`:
     ```bash
     python3 .pm/scripts/update-project-data.py set 'phase' '<new-phase-number>'
     python3 .pm/scripts/update-project-data.py set 'phase_name' '<new-phase-name>'
     ```
   - Append to `.pm/audit.log`:
     ```json
     {"timestamp":"2026-03-30T16:00:00Z","action":"phase_advance","from":1,"to":2,"from_name":"Brainstorm","to_name":"Document"}
     ```
   - Update `.pm/context.md` with phase transition

5. **Skip is allowed** — user can say "skip to Phase 3" to bypass a phase. Show a warning but don't block:
   ```
   ⚠️  Skipping Phase 2 (Document). Prerequisites not fully met:
      - No PRD created yet

   Proceeding to Phase 3 (Plan).
   You can return to Phase 2 later: "create a PRD for X"
   ```

**Output:**
```
✅ Advanced to Phase 2: Document

  Completed: Phase 1 (Brainstorm)
  - 15 requirements in specs/requirements.md
  - 2 personas created

  Next steps for Phase 2:
  - "create a PRD for X" — formalize requirements
  - "generate the SRS" — create client sign-off document
```

---

## State File Schema

`.pm/state.json`:

```json
{
  "project_name": "Notification System",
  "language": "en",
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
