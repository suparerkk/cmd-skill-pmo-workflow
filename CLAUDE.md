# CLAUDE.md — Project Instructions

## Project Overview

This is the **pm-workflow** skill for Claude Code — a spec-driven project management workflow with 5-phase discipline. The skill lives in `.claude/skills/pm-workflow/`.

## Agent Directives: Mechanical Overrides

You are operating within a constrained context window and strict system prompts. To produce production-grade code, you MUST adhere to these overrides:

### Context Management

1. **SUB-AGENT SWARMING:** For tasks touching >5 independent files, you MUST launch parallel sub-agents (5-8 files per agent). Each agent gets its own context window. This is not optional - sequential processing of large tasks guarantees context decay.
2. **CONTEXT DECAY AWARENESS:** After 10+ messages in a conversation, you MUST re-read any file before editing it. Do not trust your memory of file contents. Auto-compaction may have silently destroyed that context and you will edit against stale state.
3. **FILE READ BUDGET:** Each file read is capped at 2,000 lines. For files over 500 LOC, you MUST use offset and limit parameters to read in sequential chunks. Never assume you have seen a complete file from a single read.
4. **TOOL RESULT BLINDNESS:** Tool results over 50,000 characters are silently truncated to a 2,000-byte preview. If any search or command returns suspiciously few results, re-run it with narrower scope (single directory, stricter glob). State when you suspect truncation occurred.

### Edit Safety

5. **EDIT INTEGRITY:** Before EVERY file edit, re-read the file. After editing, read it again to confirm the change applied correctly. The Edit tool fails silently when old_string doesn't match due to stale context. Never batch more than 3 edits to the same file without a verification read.
6. **NO SEMANTIC SEARCH:** You have grep, not an AST. When renaming or changing any function/type/variable, you MUST search separately for:
   - Direct calls and references
   - Type-level references (interfaces, generics)
   - String literals containing the name
   - Dynamic imports and require() calls
   - Re-exports and barrel file entries
   - Test files and mocks
     Do not assume a single grep caught everything.

### Project Rules

7. **ALWAYS UPDATE CHANGELOG:** Every time you make changes to any file under `.claude/skills/pm-workflow/`, you MUST also update `CHANGELOG.md`:
   - Add entries under an `## [Unreleased]` section at the top (create it if it doesn't exist)
   - Use Keep a Changelog format: `### Added`, `### Changed`, `### Removed`, `### Fixed`
   - Be specific about what changed and which file was affected
   - When the user is ready to release, move unreleased entries into a versioned section
8. **CROSS-FILE CONSISTENCY:** When making changes that affect multiple files (e.g., adding a field to state.json), update **all** files that reference the changed concept. Always grep to find all references before finishing.

## Skill File Structure

```
.claude/skills/pm-workflow/
├── SKILL.md              # Skill definition + intent routing
├── CHANGELOG.md          # Version history (KEEP UPDATED)
├── README.md             # User documentation
└── references/           # Phase implementation files
    ├── ingest.md         # Phase 0
    ├── meeting-prep.md   # Pre-Phase
    ├── brainstorm.md     # Phase 1
    ├── document.md       # Phase 2
    ├── plan.md           # Phase 3
    ├── execute.md        # Phase 4
    ├── track.md          # Phase 5
    ├── generate-document.md  # Phase-independent document generation
    ├── admin.md          # Admin commands
    ├── conventions.md    # File formats, schemas
    ├── deliverables.md   # Artifact catalog
    └── scripts/          # Bash scripts for deterministic ops
```
