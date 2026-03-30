# CLAUDE.md — Project Instructions

## Project Overview

This is the **pm-workflow** skill for Claude Code — a spec-driven project management workflow with 5-phase discipline. The skill lives in `.claude/skills/pm-workflow/`.

## Rules

### Always Update CHANGELOG.md

Every time you make changes to any file under `.claude/skills/pm-workflow/`, you **must** also update `CHANGELOG.md`:

- Add entries under an `## [Unreleased]` section at the top (create it if it doesn't exist)
- Use Keep a Changelog format: `### Added`, `### Changed`, `### Removed`, `### Fixed`
- Be specific about what changed and which file was affected
- When the user is ready to release, move unreleased entries into a versioned section

### Skill File Structure

The skill is organized as:
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

### Consistency

When making changes that affect multiple files (e.g., adding a field to state.json), update **all** files that reference the changed concept. Always grep to find all references before finishing.
