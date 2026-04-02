# Phase 1: Brainstorm

Think deeper than comfortable. Ask the hard questions before writing specs.

## When to Use

User says:
- "I want to build X"
- "let's plan X"
- "help me think through X"
- "I need to design X"
- "we should create X"

## Behavior

### 1. Guided Discovery

Run the appropriate PM skill based on context:

**If no requirements exist yet:**
```
Run: /discovery-process
```

This conducts guided discovery across:
- **Problem**: What problem are we solving? For whom?
- **Users**: Who are the target users? What are their jobs-to-be-done?
- **Success criteria**: How do we know we've succeeded?
- **Constraints**: Time, budget, technical, team constraints
- **Out of scope**: What are we explicitly NOT doing?

**If problem is unclear:**
```
Run: /problem-framing-canvas
```

Uses MITRE's Problem Framing Canvas to clarify the problem space.

**If we need customer input:**
```
Run: /discovery-interview-prep
```

Prepares structured customer discovery interviews.

**If we have multiple opportunity areas:**
```
Run: /opportunity-solution-tree
```

Maps outcomes → opportunities → solutions → tests.

---

### 2. Capture Insights

Update `.pm/context.md` with:

```markdown
## Project Overview
<1-2 sentence summary of what we're building>

## Key Decisions
- YYYY-MM-DD: <decision made and why>

## Open Questions
- <questions that need resolution>
```

---

### 3. Generate Requirements

Create or update `specs/requirements.md` with structured requirements:

```markdown
# Requirements

## REQ-001: <Feature Name>

**Problem:** <What problem does this solve?>

**Users:** <Who are the users?>

**Functional Requirements:**
1. <requirement 1>
2. <requirement 2>

**Non-Functional Requirements:**
1. <performance/scalability/security requirement>

**Constraints:**
1. <time/budget/technical constraint>

**Out of Scope:**
- <what we're NOT doing>

**Success Criteria:**
- <how we measure success>

---
```

**REQ ID Assignment:**
- Read `.pm/state.json`
- Get `next_req_id` value
- Use as `REQ-{next_req_id}`
- Increment counter in state file

---

### 4. Log Completion

After skill completes:

1. **Update `.pm/state.json`:**
```json
{
  "phase": 1,
  "phase_name": "Brainstorm",
  "next_req_id": <incremented>,
  "completed_skills": ["discovery-process"],
  "current_skill": null
}
```

2. **Append to `.pm/audit.log`:**
```json
{"timestamp":"2026-03-30T14:22:31Z","phase":1,"skill":"discovery-process","req_id":"REQ-001","artifacts_created":["specs/requirements.md"]}
```

---

## Output

After brainstorming completes, output:

```
✅ Brainstorming complete
✅ Requirements created: specs/requirements.md (REQ-001)

Ready to document this as a structured PRD?
Say: "parse the <feature-name> PRD"
```

---

## Skills Used

**Always run one of these** based on context (Step 1 decides which):

| Context | Skill to Run | What It Does |
|---------|-------------|--------------|
| Starting from scratch, no requirements | `Run: /discovery-process` | Full guided discovery: problem, users, success criteria, constraints |
| Problem is unclear or too broad | `Run: /problem-framing-canvas` | MITRE canvas to clarify what the actual problem is |
| Need customer input before defining | `Run: /discovery-interview-prep` | Structured interview plan with goals and questions |
| Multiple opportunity areas competing | `Run: /opportunity-solution-tree` | Maps outcomes to opportunities to solutions to tests |

---

## Example

```
You: "I want to build a notification system — push, email, and in-app"

Claude: Let's start with brainstorming. I'll run /discovery-process...

        [Interactive Q&A session]
        - What problem are notifications solving?
        - Who are the users? (B2B admins, end users?)
        - What's the success criteria?
        - Any constraints? (budget, timeline, tech stack?)
        - What's out of scope? (SMS? In-app messaging?)

        ✅ Updated .pm/context.md with project overview
        ✅ Created specs/requirements.md with REQ-001

        Ready to create a structured PRD?
        Say: "parse the notification-system PRD"
```

---

## Transition to Next Phase

User triggers Phase 2 (Document) by saying:
- "parse the X PRD"
- "create a PRD for X"
- "document X"
