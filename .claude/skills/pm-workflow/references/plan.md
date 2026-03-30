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

### 5. Story Splitting (if needed)

If stories are too large:

```
Run: /user-story-splitting
```

Uses Humanizing Work split patterns to break into smaller deliverables.

---

### 6. Map Stories (optional)

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

### 7. Update State

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
    "epic-hypothesis",
    "epic-breakdown-advisor",
    "user-story"
  ],
  "current_skill": null
}
```

2. **Append to `.pm/audit.log`:**
```json
{"timestamp":"2026-03-30T16:00:00Z","phase":3,"skill":"epic-hypothesis","artifacts_created":["specs/epics/notification-system/epic.md"]}
{"timestamp":"2026-03-30T16:15:00Z","phase":3,"skill":"epic-breakdown-advisor","artifacts_created":["specs/epics/notification-system/001.md","specs/epics/notification-system/002.md","specs/epics/notification-system/003.md"]}
{"timestamp":"2026-03-30T16:20:00Z","phase":3,"skill":"user-story","artifacts_created":["specs/stories/us-001.md","specs/stories/us-002.md"]}
```

3. **Update `.pm/context.md`:**
```markdown
## Current State
- Phase: 3 Plan
- Epic: specs/epics/notification-system/epic.md
- Tasks: 7 total (5 parallel, 2 sequential)

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

        Ready to start implementation?
        Say: "start working on task 001"
```

---

## Transition to Next Phase

User triggers Phase 4 (Execute) by saying:
- "start working on X"
- "implement X"
- "work on issue X"
