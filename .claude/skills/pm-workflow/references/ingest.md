# Ingest — Parse Existing Documents into Structured Requirements

Converts existing artifacts (SRS, PRD, meeting notes, designs, diagrams) into structured requirements with full traceability to source documents.

## When to Use

User says:
- "I have a PRD from another team"
- "parse this SRS"
- "ingest these meeting notes"
- "turn this Figma design into requirements"
- "extract requirements from this diagram"
- "I have a document that needs to become requirements"
- "convert this TOR into requirements"
- "here's our existing spec — make it structured"

---

## Behavior

### 1. Detect Input Type

First, determine what type of artifact the user is providing:

**Auto-detect by file extension:**
- `.pdf`, `.doc`, `.docx` → Formal document (SRS, PRD, TOR)
- `.txt`, `.md` (unstructured) → Meeting notes, raw ideas
- `.fig`, `.sketch`, image files → Visual design
- `.json`, `.csv` → Structured data (user story map, backlog)

**Ask if unclear:**
```
"What type of document is this?"
- SRS/PRD (formal specification)
- Meeting notes/transcript
- Visual design (Figma, screenshot)
- Architecture/flow diagram
- TOR/RFP (legal/procurement)
- Existing user stories/backlog
- Raw notes/ideas
```

---

### 2. Request Document

Ask the user to provide the document:

```
"Please share the document. You can:
- Paste the text directly
- Provide a file path (I can read local files)
- Upload the file

If it's a visual asset (Figma, diagram), provide:
- File path to the image
- Screenshot paste
- Figma link with public access"
```

---

### 3. Copy Source & Read Document

**First, copy the source file** into `specs/sources/` for safekeeping. Source files can move or get deleted — always keep a local copy.

```bash
mkdir -p specs/sources
```

**If text/paste:**
- Save pasted text to `specs/sources/<topic>-<date>.md` (e.g., `specs/sources/notification-system-2026-03-30.md`)
- Parse directly from the saved copy

**If file path:**
- Copy file: `cp <original-path> specs/sources/<filename>`
- Use Read tool to access the **local copy**
- Handle .pdf, .docx if needed (extract text)

**If image/visual:**
- Copy file: `cp <original-path> specs/sources/<filename>`
- Use Read tool on the **local copy** (supports images)
- Extract text via OCR
- Analyze visual structure

**Naming convention for copies:**
- Keep original filename when possible (e.g., `specs/sources/SRS-v2.pdf`)
- If filename is generic (e.g., `document.pdf`), prefix with topic: `specs/sources/notification-system-document.pdf`
- If multiple versions exist, keep all (e.g., `SRS-v1.pdf`, `SRS-v2.pdf`)

All subsequent references in REQ entries and traceability should point to `specs/sources/<filename>`, not the original path.

---

### 4. Parse Based on Type

#### SRS/PRD Parsing

**Strategy:** Section-based extraction

1. **Identify sections:**
   - Look for numbered sections (1.0, 1.1, 2.0)
   - Look for headers (##, ###)
   - Map section structure

2. **Extract per section:**
   - **Section title** → REQ title
   - **"The system shall"** statements → Functional requirements
   - **"The system must"** statements → Non-functional requirements
   - **Constraints** → Constraints
   - **Assumptions** → Out of scope (if explicitly excluded)

3. **Create REQ entries:**

```markdown
## REQ-001: <Section Title>

**Source:** <document-name>, Section <X.Y>
**Original Text:**
> <quote from source>

**Extracted Requirements:**

**Functional:**
1. <the system shall...>
2. <the system shall...>

**Non-Functional:**
1. <the system must...>

**Constraints:**
1. <constraint from source>

**Open Questions:**
- <ambiguous points needing clarification>

---
```

---

#### Meeting Notes/Transcript Parsing

**Strategy:** Decision and action item extraction

1. **Identify:**
   - **Decisions made** → Requirements
   - **Action items** → Tasks (future)
   - **Open questions** → Open questions
   - **Mentioned constraints** → Constraints
   - **Stakeholder concerns** → Risks

2. **Extract requirements from decisions:**

```markdown
## REQ-001: <Decision Topic>

**Source:** Meeting notes (2026-03-28)
**Attendees:** <names if mentioned>

**Decision:**
<what was decided>

**Implications (Requirements):**
1. <requirement derived from decision>
2. <requirement derived from decision>

**Context:**
<relevant quotes>

**Open Questions:**
- <questions that weren't resolved>

---
```

---

#### Visual Design (Figma/Screenshot) Parsing

**Strategy:** UI → User flows → Requirements

1. **Analyze the visual:**
   - Identify UI components (forms, buttons, navigation)
   - Identify user flow (screens → actions → outcomes)
   - Identify data displayed (forms, tables, cards)

2. **Extract requirements:**

```markdown
## REQ-001: <Feature Name>

**Source:** Figma design - <file-name>
**Screen:** <screen name if identifiable>

**User Flow:**
1. User lands on <screen>
2. User fills <form fields>
3. User clicks <action>
4. System responds with <outcome>

**UI Requirements:**
1. Form must collect: <fields>
2. Actions available: <buttons>
3. Data displayed: <elements>

**Functional Requirements:**
1. System must validate <field>
2. System must save <data>
3. System must show <feedback>

**Open Questions:**
- Is this the final design or WIP?
- Are there error states designed?
- What's the mobile responsive behavior?

---
```

---

#### Architecture/Flow Diagram Parsing

**Strategy:** Visual flow → Technical + User requirements

1. **Parse diagram:**
   - Identify components/services
   - Identify data flow
   - Identify user touchpoints
   - Identify external dependencies

2. **Extract requirements:**

```markdown
## REQ-001: <System Component>

**Source:** Architecture diagram - <file-name>
**Diagram Type:** <system flow / data flow / sequence>

**Technical Requirements:**
1. <component> must integrate with <service>
2. Data must flow from <source> to <destination>
3. <external service> dependency

**User Requirements:**
1. User initiates flow at <touchpoint>
2. User expects <outcome> at <endpoint>

**Integration Points:**
1. <service A> → <service B>
2. <database> ← <service C>

**Constraints:**
- <technical constraint visible in diagram>

**Open Questions:**
- Is this the current state or target state?
- Are there failure scenarios documented?

---
```

---

#### TOR/RFP Parsing

**Strategy:** Legal/formal → Scope + Constraints

1. **Extract:**
   - **Scope of work** → Functional requirements
   - **Deliverables** → Milestones
   - **Constraints** → Constraints (budget, timeline, technical)
   - **Terms** → Legal/compliance requirements
   - **Exclusions** → Out of scope

2. **Create requirements:**

```markdown
## REQ-001: <Scope Item>

**Source:** TOR-<name>.pdf, Section <X>
**Contract Reference:** <clause if applicable>

**Deliverable:**
<what must be delivered>

**Requirements:**
1. <requirement from TOR>
2. <requirement from TOR>

**Constraints:**
1. <budget constraint>
2. <timeline constraint>
3. <compliance constraint>

**Out of Scope:**
- <explicit exclusions from TOR>

**Compliance:**
- <legal/regulatory requirements>

---
```

---

#### User Story Map/Backlog Parsing

**Strategy:** Preserve structure, assign REQ IDs

1. **Parse existing structure:**
   - Epics → Keep as epics
   - Stories → Map to REQ IDs
   - Acceptance criteria → Keep as criteria

2. **Create requirements:**

```markdown
## REQ-001: <Story Title>

**Source:** Backlog - <tool-name>
**Original ID:** <story-ID from backlog>
**Epic:** <epic name>

**As a** <persona>
**I want** <goal>
**So that** <benefit>

**Acceptance Criteria:**
- [ ] <criterion 1>
- [ ] <criterion 2>

**Story Points:** <if provided>
**Priority:** <if provided>

---
```

---

#### Raw Ideas/Notes Parsing

**Strategy:** Structure the unstructured

1. **Identify:**
   - Main themes → REQ categories
   - Bullet points → Individual requirements
   - Questions → Open questions
   - "Must have" vs "nice to have" → Priority

2. **Create requirements:**

```markdown
## REQ-001: <Theme>

**Source:** Raw notes (2026-03-28)

**Ideas Captured:**
1. <bullet point>
2. <bullet point>
3. <bullet point>

**Structured Requirements:**
1. <refined requirement from idea 1>
2. <refined requirement from idea 2>

**Priority:** Must have / Nice to have
**Category:** <theme>

**Open Questions:**
- <questions from notes>

---
```

---

### 5. Assign Temporary IDs

Assign temporary IDs to extracted requirements (e.g., `NEW-001`, `NEW-002`) before reconciliation. Final REQ IDs are assigned in Step 7 after duplicates and conflicts are resolved.

---

### 6. Reconcile with Existing Requirements

**Skip if:** This is the first ingest (`specs/requirements.md` doesn't exist or is empty).

**Run if:** `specs/requirements.md` already has REQs from a previous ingest.

#### 6.1 Read Existing Requirements

Read all current REQs from `specs/requirements.md` to build a comparison baseline.

#### 6.2 Detect Duplicates

Compare each new extracted requirement against every existing REQ:

- **Semantic match** — different words, same meaning (e.g., "user login" vs "user authentication")
- **Partial overlap** — new REQ covers part of an existing REQ or vice versa
- **Exact match** — same requirement from a different source

For each potential duplicate, ask the user:

```
🔄 Possible duplicate detected:

  NEW-003: "Users must be able to log in with email and password"
  (from: meeting-notes-2026-03-30.md)

  REQ-003: "The system shall authenticate users via email/password"
  (from: specs/sources/SRS-v2.pdf, Section 3.1)

  Options:
  1. Merge → keep REQ-003, add meeting notes as additional source
  2. Keep both → they're different enough to track separately
  3. Replace → NEW-003 supersedes REQ-003
```

#### 6.3 Detect Conflicts

Identify contradictions between new and existing requirements:

- **Numeric conflicts** — different thresholds (1,000 vs 10,000 users)
- **Scope conflicts** — one says "in scope", another says "out of scope"
- **Priority conflicts** — different priority levels for the same feature
- **Technical conflicts** — incompatible approaches (REST vs GraphQL)

For each conflict, ask the user:

```
⚠️  Conflict detected:

  NEW-005: "System must support 10,000 concurrent users"
  (from: meeting-notes-2026-03-30.md)

  REQ-005: "System must support 1,000 concurrent users"
  (from: specs/sources/SRS-v2.pdf, Section 4.2)

  Which is correct?
  1. Keep REQ-005 (1,000 users) — meeting notes were aspirational
  2. Update to NEW-005 (10,000 users) — SRS was outdated
  3. Flag for stakeholder decision — need clarification
```

#### 6.4 Enhance with PM Skills (optional)

Run PM skills when reconciliation reveals deeper issues:

**`/problem-framing-canvas`** — When duplicates suggest the problem isn't well-defined
- Trigger: 3+ duplicates cluster around the same theme but frame it differently
- Value: Clarifies what the actual problem is before locking in requirements
- Example: Multiple sources mention "notifications" but mean different things (admin alerts vs user notifications vs system monitoring)

```
Run: /problem-framing-canvas
```

**`/jobs-to-be-done`** — When it's unclear if duplicates are truly the same requirement
- Trigger: Two REQs look similar but might serve different user jobs
- Value: Reframes requirements around customer jobs to see if they're truly duplicates or separate needs
- Example: "export to CSV" (admin reporting job) vs "export to CSV" (user data portability job)

```
Run: /jobs-to-be-done
```

**`/prioritization-advisor`** — When merged requirements need consistent priority
- Trigger: Requirements from different sources have conflicting or missing priorities
- Value: Establishes a unified priority framework across all ingested sources
- Example: SRS has no priority, meeting notes say "P0", design implies "nice to have"

```
Run: /prioritization-advisor
```

**Skip PM skills if:** Reconciliation is straightforward (few duplicates, no conflicts, user resolves quickly).

#### 6.5 Apply Reconciliation

After user decisions:

1. **Merged REQs** — update existing REQ with additional source traceability:
   ```yaml
   trace:
     sources:
       - source: specs/sources/SRS-v2.pdf
         section: "3.1"
       - source: specs/sources/meeting-notes-2026-03-30.md
         merged_from: NEW-003
         merged_date: 2026-03-30
   ```

2. **Replaced REQs** — update existing REQ content, add superseded note:
   ```yaml
   trace:
     sources:
       - source: specs/sources/meeting-notes-2026-03-30.md
     supersedes:
       - source: specs/sources/SRS-v2.pdf
         section: "4.2"
         reason: "Updated requirement per client meeting"
   ```

3. **Flagged REQs** — mark as needing stakeholder decision:
   ```yaml
   status: needs-decision
   conflict:
     description: "User limit: 1,000 vs 10,000"
     sources: [specs/sources/SRS-v2.pdf, specs/sources/meeting-notes-2026-03-30.md]
   ```

4. **New unique REQs** — proceed to Step 7 for final REQ ID assignment

#### 6.6 Log Reconciliation

Append to `.pm/ingestion-log.md`:

```markdown
### Reconciliation: 2026-03-30

| Action | New ID | Existing REQ | Decision |
|--------|--------|-------------|----------|
| Merged | NEW-003 | REQ-003 | Same requirement, added meeting notes as source |
| Conflict | NEW-005 | REQ-005 | Updated to 10,000 users per client meeting |
| Flagged | NEW-007 | REQ-008 | Needs stakeholder decision on scope |
| New | NEW-001 | — | Assigned REQ-016 |
| New | NEW-004 | — | Assigned REQ-017 |

PM Skills used: /prioritization-advisor (resolved priority conflicts)
```

---

### 7. Assign Final REQ IDs

For each **new unique requirement** that survived reconciliation:

1. Read `.pm/state.json`
2. Get `next_req_id`
3. Assign `REQ-{next_req_id}`
4. Increment counter
5. Update state file

Merged and replaced requirements keep their existing REQ IDs.

---

### 8. Create Traceability

Each REQ entry includes:

**Source traceability in frontmatter** (always point to the local copy in `specs/sources/`):
```yaml
---
trace:
  source: specs/sources/SRS-v2.pdf
  original_path: /documents/SRS-v2.pdf
  source_section: "3.1"
  source_page: 12
  ingested: 2026-03-30
  method: ingest
phase: 1-brainstorm
---
```

---

### 9. Create Ingestion Log

Append to `.pm/ingestion-log.md`:

```markdown
## Ingestion: 2026-03-30

**Source:** specs/sources/SRS-v2.pdf (copied from /documents/SRS-v2.pdf)
**Type:** SRS (Software Requirements Specification)
**REQ IDs Created:** REQ-001 through REQ-015

### Section Mapping

| REQ ID | Source Section | Title |
|--------|---------------|-------|
| REQ-001 | 3.1 | User Authentication |
| REQ-002 | 3.2 | Password Reset |
| REQ-003 | 4.1 | Dashboard Display |
| ... | ... | ... |

### Extraction Stats

- Total sections: 12
- Functional requirements: 23
- Non-functional requirements: 7
- Constraints: 5
- Open questions: 4

### Manual Review Needed

- [ ] REQ-005: Ambiguous performance metric ("fast response time")
- [ ] REQ-012: Conflicts with REQ-003 (different user roles mentioned)
- [ ] REQ-015: Technical jargon needs clarification

---
```

---

### 10. Update Context

Update `.pm/context.md`:

```markdown
## Project Overview
<!-- Update with ingested document summary -->

## Key Decisions
- 2026-03-30: Ingested SRS-v2.pdf from Team Alpha
- 2026-03-30: 15 requirements extracted, 3 need manual review

## Current State
- Phase: 1 Brainstorm (ingestion complete)
- Source: SRS-v2.pdf (15 REQs)
- Open questions: 4

## Open Questions
- <questions that couldn't be resolved from document>
```

---

### 11. Append to Audit Log

Add to `.pm/audit.log`:

```json
{"timestamp":"2026-03-30T14:22:31Z","phase":1,"action":"ingest","source":"specs/sources/SRS-v2.pdf","original_path":"/documents/SRS-v2.pdf","type":"SRS","req_ids":["REQ-001","REQ-015"],"artifacts_created":["specs/sources/SRS-v2.pdf","specs/requirements.md",".pm/ingestion-log.md"]}
```

---

## Output

After ingestion completes:

**First ingest (no existing REQs):**
```
✅ Document ingested: SRS-v2.pdf
✅ Source copied to: specs/sources/SRS-v2.pdf
✅ Requirements created: 15 REQs (REQ-001 to REQ-015)
✅ Traceability: All REQs linked to source sections
✅ Ingestion log: .pm/ingestion-log.md

📊 Stats:
- Functional requirements: 23
- Non-functional requirements: 7
- Constraints: 5
- Open questions: 4

⚠️  Manual review needed:
- REQ-005: Ambiguous performance metric
- REQ-012: Conflicts with REQ-003
- REQ-015: Technical jargon

Next steps:
1. Review flagged requirements in specs/requirements.md
2. Validate with stakeholders: "help me validate these requirements"
3. Or proceed to document: "parse the requirements into a PRD"
```

**Subsequent ingest (with reconciliation):**
```
✅ Document ingested: meeting-notes-2026-03-30.md
✅ Source copied to: specs/sources/meeting-notes-2026-03-30.md
✅ Extracted: 5 requirements from meeting notes

🔄 Reconciliation against 15 existing REQs:
- 2 duplicates found → merged into REQ-003, REQ-007
- 1 conflict found → REQ-005 updated (1,000 → 10,000 users)
- 2 new unique REQs → REQ-016, REQ-017

📊 Requirements baseline: 17 REQs (clean, no duplicates)

Next steps:
1. Ingest more documents, or
2. Proceed to document: "parse the requirements into a PRD"
```

---

## Example Sessions

### Example 1: SRS Ingestion

```
You: I have an SRS from another team — can you parse it?

Claude: [Detects: Ingest intent]
        I'll parse that SRS into structured requirements.
        Reading references/ingest.md...

        Please share the SRS document:
        - Paste the text, OR
        - Provide file path, OR
        - Upload the file

You: /documents/SRS-v2.pdf

Claude: Copying to specs/sources/SRS-v2.pdf...
        Reading SRS-v2.pdf...
        ✅ Detected 12 sections
        Extracting requirements...

        Created:
        - REQ-001: User Authentication (Section 3.1)
        - REQ-002: Password Reset (Section 3.2)
        - REQ-003: Session Management (Section 3.3)
        ...
        - REQ-015: Audit Logging (Section 7.1)

        All requirements linked to source sections.
        Ingestion log saved to: .pm/ingestion-log.md

        ⚠️ 3 requirements need manual review (ambiguous/conflicting)

        Next: Validate with stakeholders or proceed to PRD?
```

---

### Example 2: Meeting Notes Ingestion

```
You: Here are the notes from yesterday's client meeting:
     [pastes unstructured notes]

Claude: [Detects: Ingest intent - meeting notes]
        Parsing meeting notes...

        Extracted:
        - 3 decisions → REQ-001, REQ-002, REQ-003
        - 7 action items → Saved for task planning
        - 2 open questions → Added to context

        Created:
        - REQ-001: Payment integration (Decision: Use Stripe)
        - REQ-002: Mobile-first design (Decision: iOS priority)
        - REQ-003: Launch date (Decision: Q3 2026)

        Saved to: specs/requirements.md

        Next: Fill gaps with "help me think through the missing pieces"
```

---

### Example 3: Figma Design Ingestion

```
You: Can you extract requirements from this Figma screen?
     /designs/dashboard.png

Claude: [Detects: Ingest intent - visual design]
        Analyzing dashboard.png...

        Identified:
        - User flow: Filter → Select → View details → Export
        - Form fields: Date range, Status, Category
        - Actions: Export CSV, Create Report, Refresh
        - Data displayed: Table with 6 columns

        Created:
        - REQ-001: Dashboard filtering
        - REQ-002: Data export functionality
        - REQ-003: Report generation

        Open questions:
        - Error states for failed export?
        - Mobile responsive behavior?
        - Real-time data refresh interval?

        Saved to: specs/requirements.md

        Next: Review the extracted requirements?
```

---

## Supported File Types

| Type | Extensions | Parsing Method |
|------|------------|----------------|
| Text documents | `.txt`, `.md` | Direct text parsing |
| PDFs | `.pdf` | Text extraction (Read tool) |
| Word docs | `.doc`, `.docx` | Text extraction |
| Images | `.png`, `.jpg`, `.jpeg` | OCR + visual analysis |
| Structured data | `.json`, `.csv` | Structure-aware parsing |
| Diagrams | `.svg`, `.png`, `.jpg` | Visual parsing |

---

## Edge Cases

### Document Too Large

If document is very large (>10,000 tokens):
```
"This SRS is large (15,000+ tokens). I'll process in sections:
- Processing Section 1-4 now...
- Then Section 5-8...
- Then Section 9-12...

Progress: 33% | 66% | 100%"
```

### Unparseable Format

If can't extract structured requirements:
```
⚠️ Unable to extract clear requirements from this format.

Suggestions:
1. Convert to text/markdown first
2. Provide section headings explicitly
3. Manually highlight requirement sections

Alternatively, use brainstorm mode: "help me think through this"
```

### Ambiguous Requirements

Flag for manual review:
```
⚠️ REQ-005 marked for review:
   "The system shall respond quickly"
   Issue: "quickly" is not measurable
   Suggestion: Define specific SLA (e.g., "< 200ms p95")
```

### Large Binary Files (>10MB)

For large PDFs, presentations, or image-heavy documents:

```
⚠️ Large file detected: SRS-complete.pdf (45MB)

Options:
1. Copy as-is — full file preserved in specs/sources/ (uses disk space)
2. Extract text only — save extracted text as .md, skip binary copy
3. Specific pages — "copy only pages 1-20"
```

**Recommendation:** For PDFs >10MB, extract text and save as `.md` in `specs/sources/` instead of copying the binary. The original path is preserved in traceability for reference.

### Design Tool Links (Figma, Miro, etc.)

For URLs to design tools that can't be copied as files:

1. **Screenshot the relevant screens** and save to `specs/sources/<name>.png`
2. **Save the URL** in a reference file: `specs/sources/<name>-link.md`
   ```markdown
   ---
   type: design-link
   url: https://www.figma.com/file/abc123/Dashboard
   captured: 2026-03-30
   screenshots: [specs/sources/dashboard-main.png, specs/sources/dashboard-detail.png]
   ---
   # Design Reference: Dashboard
   Figma link: https://www.figma.com/file/abc123/Dashboard
   Screenshots taken: 2026-03-30
   ```
3. Parse requirements from the screenshots, not the URL

### Sources Directory Cleanup

`specs/sources/` will grow over time. Guidance:

- **Never delete** source files that are referenced by active REQs (check `trace.source` fields)
- **Safe to archive** sources for completed/closed epics after project delivery
- **To check what's referenced:** `grep -r "specs/sources/" specs/requirements.md`
- **Add to `.gitignore`** if binary sources are too large for git:
  ```
  # Large binary source files (text extracts are tracked instead)
  specs/sources/*.pdf
  specs/sources/*.docx
  specs/sources/*.pptx
  ```

---

## Transition to Next Phase

After ingestion, user can:

1. **Fill gaps:** "help me think through what's missing"
   → Routes to `brainstorm.md`

2. **Validate:** "help me validate these requirements"
   → Runs `/discovery-interview-prep`

3. **Document:** "parse into a PRD"
   → Routes to `document.md`

4. **Review:** "show me the requirements that need review"
   → Lists flagged REQs from ingestion log

---

## Comparison: Ingest vs Brainstorm

| | Ingest | Brainstorm |
|---|---|---|
| **Input** | Existing document | Blank slate, idea |
| **Process** | Parse, extract, structure | Ask, discover, guide |
| **Speed** | Fast (minutes) | Slower (interactive) |
| **Quality** | Inherits document quality | Fresh perspective |
| **Best for** | Formal handoffs, migrations | New initiatives, vague ideas |
| **Traceability** | Links to source sections | Links to discovery process |

---

## Best Practices

1. **Ingest first, brainstorm second** — Start with what exists, then fill gaps
2. **Always review flagged items** — Ambiguous requirements will cause problems later
3. **Keep source link** — Never lose traceability to original document
4. **Note conflicts** — If REQ-012 conflicts with REQ-003, flag immediately
5. **Preserve original text** — Quote source in REQ entry for context
