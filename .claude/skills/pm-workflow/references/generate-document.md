# Generate Document (Phase-Independent)

Generate or regenerate any sign-off document manually, regardless of current workflow phase.

## When to Use

User explicitly asks for a specific document by name:
- "generate the SRS"
- "create system design document"
- "draw sequence diagrams"
- "write the test plan"
- "create user journey for admin"
- "set up deliverable tracker"
- "update the SRS"
- "regenerate sequence diagrams"

## Behavior

### 1. Detect Which Document

Match user intent to a document type:

| Intent Keywords | Document | Output File |
|----------------|----------|-------------|
| SRS, software requirements specification | SRS | `specs/srs/srs.md` |
| user journey, journey map, journey diagram | User Journey | `specs/journeys/journey-<persona>.md` |
| system design, architecture diagram, component diagram | System Design | `specs/design/system-design.md` |
| sequence diagram, sequence flow, interaction diagram | Sequence Diagrams | `specs/design/sequence-diagrams.md` |
| test plan, test cases, UAT | Test Plan | `specs/test-plan/test-plan.md` |
| deliverable tracker, track deliverables | Deliverable Tracker | `specs/deliverable-tracker.md` |

---

### 2. Check Prerequisites

Each document has **minimum prerequisites**. If not met, tell the user what's needed — do NOT block silently.

| Document | Minimum Prerequisite | If Missing |
|----------|---------------------|------------|
| **SRS** | `specs/requirements.md` exists | "I need requirements first. Say: 'I want to build X' to start brainstorming, or 'ingest this document' to parse existing requirements." |
| **User Journey** | `specs/requirements.md` + at least one `specs/personas/*.md` | "I need requirements and at least one persona. Complete Phase 1 (brainstorm) and create personas first." |
| **System Design** | `specs/requirements.md` + `specs/prd/prd.md` or `specs/prd/*.md` | "I need requirements and a PRD to derive the architecture. Say: 'create a PRD for X' first." |
| **Sequence Diagrams** | `specs/design/system-design.md` exists | "I need a system design document first to know the components. Say: 'generate the system design' first." |
| **Test Plan** | `specs/requirements.md` exists | "I need requirements to build test cases against. Say: 'I want to build X' or 'ingest this document' first." |
| **Deliverable Tracker** | `specs/requirements.md` exists | "I need requirements to link deliverables to. Say: 'I want to build X' or 'ingest this document' first." |

**Important:** Prerequisites are checked but the current phase is NOT checked. The user can generate any document from any phase as long as the prerequisites exist.

---

### 3. Determine Language

**Priority order:**
1. **User specified in request** — "generate the SRS in Thai" or "สร้าง SRS เป็นภาษาไทย" → use that language, don't ask
2. **Project default** — read `language` from `.pm/state.json` → use it, confirm briefly:
   ```
   📝 Generating in Thai (ภาษาไทย) [project default]
      Say "in English" to override.
   ```
3. **No default set** — ask the user:
   ```
   📝 What language should this document be in?
      1. English (default)
      2. Thai (ภาษาไทย)
   ```

**Language rules:**
- **Document body** (headings, descriptions, requirements text, analysis) → write in the chosen language
- **Frontmatter keys** (YAML field names like `name`, `status`, `trace`) → always English (machine-readable)
- **REQ IDs, FR IDs, NFR IDs** → always English format (e.g., `REQ-001`, `FR-001`)
- **Mermaid diagram labels** → write in the chosen language
- **Table headers** → write in the chosen language
- **Sign-off table role names** → write in the chosen language

---

### 4. Generate or Update

**If the file does not exist:** Generate it fresh using the templates from:
- SRS → `references/document.md` (Step 5)
- User Journey → `references/document.md` (Step 6)
- System Design → `references/plan.md` (Step 5)
- Sequence Diagrams → `references/plan.md` (Step 6)
- Test Plan → `references/plan.md` (Step 7)
- Deliverable Tracker → `references/plan.md` (Step 8)

**If the file already exists:** Ask the user:
```
The [document] already exists at [path].
- **Update**: Regenerate with latest requirements/specs (overwrites current)
- **Review**: Open for manual edits

What would you like to do?
```

If user says "update" or "regenerate", re-read current requirements/PRD/epic and regenerate the document, preserving any `approved_by` / `approved_date` fields if the status was already `approved` (warn the user that regenerating an approved document will reset it to `draft`).

---

### 5. Update State

After generating:

1. **Append to `.pm/audit.log`:**
```json
{"timestamp":"2026-03-30T18:00:00Z","phase":"manual","skill":"generate-document","document":"srs","artifacts_created":["specs/srs/srs.md"]}
```

2. **Update `.pm/context.md`** with note about manual generation:
```markdown
## Key Decisions
- 2026-03-30: SRS manually generated/updated (outside normal phase flow)
```

3. **Do NOT change `.pm/state.json` phase** — manual generation does not advance the phase.

**Update project data:**

If this is a NEW sign-off document:
```bash
python3 .pm/scripts/update-project-data.py append 'signoff' '{"name":"<doc-type>","path":"<file-path>","status":"draft","approved_by":"","approved_date":"","created":"<date>","updated":"<date>"}'
```

If this document already exists in signoff (regeneration):
```bash
python3 .pm/scripts/update-project-data.py update-signoff '<file-path>' '{"status":"draft","updated":"<date>"}'
```

For deliverable tracker, also:
```bash
python3 .pm/scripts/update-project-data.py replace 'deliverables' '[...]'
```

---

## Output

After generation:

```
✅ Generated: specs/srs/srs.md
   Language: Thai (ภาษาไทย)
   Status: DRAFT
   Prerequisites used: specs/requirements.md, specs/prd/prd.md
   REQ IDs covered: REQ-001 through REQ-015

   To mark for review: update the frontmatter status to "review"
   To track approval: say "sign-off status"
```

---

## Examples

### Generate SRS from Phase 4 (Execute)

```
You: "generate the SRS"

Claude: [Detects: Generate Document intent → SRS]
        Checking prerequisites...
        ✅ specs/requirements.md exists (15 REQs)
        ✅ specs/prd/prd.md exists

        Generating SRS...

        ✅ Generated: specs/srs/srs.md
           Status: DRAFT
           Covers: REQ-001 through REQ-015
           Sections: Introduction, Overall Description, Functional Requirements (15),
                     Non-Functional Requirements (4), Interface Requirements,
                     Traceability Matrix, Sign-Off Table
```

### Regenerate System Design after requirements change

```
You: "update the system design"

Claude: [Detects: Generate Document intent → System Design]

        The system design already exists at specs/design/system-design.md
        Current status: DRAFT

        - **Update**: Regenerate with latest requirements/specs
        - **Review**: Open for manual edits

        What would you like to do?

You: "update"

Claude: Re-reading requirements and PRD...
        ✅ Found 3 new REQs since last generation
        ✅ Regenerated: specs/design/system-design.md
           Added components for REQ-016, REQ-017, REQ-018
```

### Missing prerequisites

```
You: "generate sequence diagrams"

Claude: [Detects: Generate Document intent → Sequence Diagrams]
        Checking prerequisites...

        ❌ Missing: specs/design/system-design.md
        I need a system design document first to know the components and their interactions.

        Say: "generate the system design" first.
```

### Generate from Phase 0 (just ingested)

```
You: [just finished ingesting an SRS document]
You: "now generate the test plan"

Claude: [Detects: Generate Document intent → Test Plan]
        Checking prerequisites...
        ✅ specs/requirements.md exists (12 REQs)

        Generating test plan...

        ✅ Generated: specs/test-plan/test-plan.md
           Status: DRAFT
           Test cases: 12 (one per REQ)
           Note: UAT scenarios are basic — they'll improve after PRD and epic creation.
           You can regenerate later with: "update the test plan"
```

---

## Regeneration Quality

Documents generated earlier in the workflow will have less detail:

| When Generated | Quality | Recommendation |
|---------------|---------|----------------|
| After Phase 0 (Ingest only) | Basic — requirements only | Regenerate after Phase 2 |
| After Phase 1 (Brainstorm) | Good — requirements + discovery | Regenerate after PRD |
| After Phase 2 (Document) | Full — requirements + PRD + personas | Best for SRS, User Journey |
| After Phase 3 (Plan) | Complete — all artifacts available | Best for System Design, Sequence, Test Plan |

The skill will note this in output:
```
⚠️ Note: This [document] was generated with limited context (Phase 1 only).
   Regenerate after completing Phase 2/3 for a more complete version.
```

---

## Key Rules

1. **Never block on phase** — only block on missing prerequisites
2. **Always check prerequisites** — tell user exactly what's missing and how to fix it
3. **Preserve approval status** — warn before overwriting an approved document
4. **Don't advance phase** — manual generation is phase-independent
5. **Log everything** — append to audit.log with `"phase":"manual"`
6. **Quality degrades gracefully** — earlier generation = less detail, but still valid
