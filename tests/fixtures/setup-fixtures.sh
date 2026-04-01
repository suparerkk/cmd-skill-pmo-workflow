#!/usr/bin/env bash
# setup-fixtures.sh — Create a complete mock PM project for testing
#
# Usage: setup-fixtures.sh [target-dir] [skill-scripts-path]
#   target-dir         Optional. Directory to create the fixture in (default: mktemp -d)
#   skill-scripts-path Optional. Path to the skill's references/scripts/ dir for symlinking .pm/scripts/

set -euo pipefail

TARGET_DIR="${1:-$(mktemp -d)}"
SKILL_SCRIPTS="${2:-}"

mkdir -p "$TARGET_DIR"

# ── .pm directory ──────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/.pm"

cat > "$TARGET_DIR/.pm/state.json" << 'STATEEOF'
{
  "phase": 3,
  "phase_name": "Plan",
  "current_skill": "epic-breakdown-advisor",
  "project_name": "Notification System",
  "language": "en",
  "completed_skills": ["discovery-process", "product-strategy-session", "prd-development"],
  "active_epic": "notification-system",
  "blocked": [
    {"description": "Waiting for API credentials from client", "since": "2026-03-28", "blocked_by": "client-team"}
  ],
  "req_counter": 5
}
STATEEOF

cat > "$TARGET_DIR/.pm/audit.log" << 'AUDITEOF'
{"timestamp":"2026-03-25T10:00:00","phase":0,"skill":"ingest","action":"ingest","artifacts_created":["specs/requirements.md"],"req_id":"REQ-001"}
{"timestamp":"2026-03-26T11:00:00","phase":1,"skill":"discovery-process","action":"discovery","artifacts_created":["discovery/notes.md"]}
{"timestamp":"2026-03-27T12:00:00","phase":2,"skill":"product-strategy-session","action":"strategy","artifacts_created":["strategy/positioning.md"]}
{"timestamp":"2026-03-28T13:00:00","phase":2,"skill":"prd-development","action":"prd","artifacts_created":["specs/prd/prd.md"]}
{"timestamp":"2026-03-29T14:00:00","phase":3,"skill":"epic-breakdown-advisor","action":"plan","artifacts_created":["specs/epics/notification-system/epic.md"]}
AUDITEOF

cat > "$TARGET_DIR/.pm/context.md" << 'CTXEOF'
# Project Context — Notification System

## Key Decisions
- Use Firebase Cloud Messaging for push notifications
- REST API with rate limiting (100 req/min per user)
- PostgreSQL for notification storage

## Open Questions
- Should we support SMS as a channel?
- What is the retention policy for read notifications?
CTXEOF

cat > "$TARGET_DIR/.pm/ingestion-log.md" << 'INGEOF'
## Ingestion: 2026-03-25
**Source:** client-srs-v2.pdf
**Type:** SRS Document
**REQ IDs Created:** REQ-001 through REQ-005
INGEOF

cat > "$TARGET_DIR/.pm/meeting-prep-kickoff.md" << 'MTGEOF'
---
name: Project Kickoff
meeting_type: kickoff
company: Acme Corp
created: 2026-03-24
attendees: CTO, Tech Lead, PM
---

# Meeting Prep: Project Kickoff
MTGEOF

# ── specs directory ────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/specs"

cat > "$TARGET_DIR/specs/requirements.md" << 'REQEOF'
---
version: 5
last_updated: 2026-03-28
---

# Requirements

## REQ-001: Push Notification Service
**Priority:** High
**Source:** client-srs-v2.pdf
Push notifications via FCM for mobile and web clients.

## REQ-002: Email Notification Service
**Priority:** High
**Source:** client-srs-v2.pdf
Transactional email delivery with template support.

## REQ-003: In-App Notification Center
**Priority:** Medium
**Source:** client-srs-v2.pdf
Notification inbox with read/unread status.

## REQ-004: Notification Preferences
**Priority:** Medium
**Source:** client-srs-v2.pdf
User-configurable channel and frequency preferences.

## REQ-005: Rate Limiting
**Priority:** High
**Source:** discovery
**Status:** needs-decision
Rate limiting strategy for notification delivery.
REQEOF

# ── specs/prd ──────────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/specs/prd"

cat > "$TARGET_DIR/specs/prd/prd.md" << 'PRDEOF'
---
name: Notification System PRD
status: draft
created: 2026-03-28
created_by: PM
phase: Phase 2
requirements: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005]
---

# Notification System PRD

## Executive Summary
A multi-channel notification system supporting push, email, and in-app.

## Features

#### Push Notification Service
Real-time push via FCM.

#### Email Notification Service
Template-based transactional emails.

#### In-App Notification Center
Notification inbox with status tracking.
PRDEOF

# ── specs/epics/notification-system ───────────────────────────────────────

mkdir -p "$TARGET_DIR/specs/epics/notification-system"

cat > "$TARGET_DIR/specs/epics/notification-system/epic.md" << 'EPICEOF'
---
name: Notification System
status: in-progress
progress: 1/4
prd: specs/prd/prd.md
requirements: [REQ-001, REQ-002, REQ-003]
depends_on_epic: []
---

# Epic: Notification System
EPICEOF

cat > "$TARGET_DIR/specs/epics/notification-system/001.md" << 'T001EOF'
---
name: Database Schema Setup
status: closed
depends_on: []
effort: S
created: 2026-03-29
updated: 2026-03-30
started: 2026-03-29
completed: 2026-03-30
---

# Task 001: Database Schema Setup
T001EOF

cat > "$TARGET_DIR/specs/epics/notification-system/002.md" << 'T002EOF'
---
name: Push Notification Service
status: in-progress
depends_on: [001]
effort: M
created: 2026-03-29
updated: 2026-03-30
started: 2026-03-30
completed:
---

# Task 002: Push Notification Service
T002EOF

cat > "$TARGET_DIR/specs/epics/notification-system/003.md" << 'T003EOF'
---
name: Email Service Integration
status: open
depends_on: [001]
parallel: [002]
conflicts_with: []
effort: M
created: 2026-03-29
updated: 2026-03-29
started:
completed:
---

# Task 003: Email Service Integration
T003EOF

cat > "$TARGET_DIR/specs/epics/notification-system/004.md" << 'T004EOF'
---
name: In-App Notification Center
status: open
depends_on: [002, 003]
effort: L
created: 2026-03-29
updated: 2026-03-29
started:
completed:
---

# Task 004: In-App Notification Center
T004EOF

# ── specs/personas ────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/specs/personas"

cat > "$TARGET_DIR/specs/personas/admin.md" << 'PADEOF'
---
name: System Admin
type: internal
requirement: REQ-001
created: 2026-03-28
---

# Persona: System Admin
PADEOF

cat > "$TARGET_DIR/specs/personas/end-user.md" << 'PEUEOF'
---
name: End User
type: external
requirement: REQ-003
created: 2026-03-28
---

# Persona: End User
PEUEOF

# ── specs/stories ─────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/specs/stories"

cat > "$TARGET_DIR/specs/stories/us-001.md" << 'US1EOF'
---
name: Push Notification Story
status: in-progress
epic: notification-system
task: 002
---

# US-001: Push Notification Story
US1EOF

cat > "$TARGET_DIR/specs/stories/us-002.md" << 'US2EOF'
---
name: Email Notification Story
status: open
epic: notification-system
task: 003
---

# US-002: Email Notification Story
US2EOF

# ── specs/srs ─────────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/specs/srs"

cat > "$TARGET_DIR/specs/srs/srs.md" << 'SRSEOF'
---
status: draft
created: 2026-03-28
approved_by:
approved_date:
updated: 2026-03-28
---

# SRS: Notification System
SRSEOF

# ── specs/deliverable-tracker ─────────────────────────────────────────────

cat > "$TARGET_DIR/specs/deliverable-tracker.md" << 'DTEOF'
# Deliverable Tracker

| ID | Name | Role | Owner | REQ IDs | Due Date | Status |
|----|------|------|-------|---------|----------|--------|
| DT-001 | SRS Document | Client Sign-Off | PM | REQ-001 | 2026-04-15 | In Progress |
| DT-002 | API Documentation | Dev Team | Tech Lead | REQ-002 | 2026-04-20 | Not Started |
| DT-003 | Test Report | QA Sign-Off | QA Lead | REQ-003 | 2026-04-25 | Not Started |
DTEOF

# ── strategy directory ────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/strategy"
touch "$TARGET_DIR/strategy/positioning.md"
touch "$TARGET_DIR/strategy/roadmap.md"

# ── .pm/scripts symlink ──────────────────────────────────────────────────

if [[ -n "$SKILL_SCRIPTS" ]]; then
  # Accept either the skill root dir or the scripts dir directly
  if [[ -d "$SKILL_SCRIPTS/references/scripts" ]]; then
    ln -sfn "$SKILL_SCRIPTS/references/scripts" "$TARGET_DIR/.pm/scripts"
  elif [[ -d "$SKILL_SCRIPTS" ]]; then
    ln -sfn "$SKILL_SCRIPTS" "$TARGET_DIR/.pm/scripts"
  fi
fi

# ── Done ──────────────────────────────────────────────────────────────────

echo "$TARGET_DIR"
