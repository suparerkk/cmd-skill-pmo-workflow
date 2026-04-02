#!/usr/bin/env python3
"""
PM Workflow — Change Report Generator (Git Diff)
Generates a markdown change report between two dates by reading git history.

Usage:
  python3 .pm/scripts/diff-report.py --from 2026-03-28 --to 2026-04-02
  python3 .pm/scripts/diff-report.py --from 2026-03-28  # to defaults to today
  python3 .pm/scripts/diff-report.py --days 7            # shortcut for "last 7 days"

Deterministic — no LLM needed. Reads git log + audit.log only.
"""

import argparse, os, re, subprocess, sys
from datetime import datetime, date, timedelta

OUTPUT_DIR = "specs/reports"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def run_git(*args):
    """Run a git command and return stdout (stripped). Returns None on error."""
    try:
        r = subprocess.run(["git"] + list(args), capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return None
        return r.stdout.strip()
    except Exception:
        return None


def is_git_repo():
    return run_git("rev-parse", "--is-inside-work-tree") == "true"


def commits_in_range(date_from, date_to):
    """Return list of commit hashes in date range (oldest first)."""
    # --before is exclusive of the date, so add 1 day
    before = (date_to + timedelta(days=1)).isoformat()
    after = date_from.isoformat()
    out = run_git("log", "--after=" + after, "--before=" + before, "--format=%H", "--reverse")
    if not out:
        return []
    return [h for h in out.split("\n") if h.strip()]


def diff_stat(oldest_hash, newest_hash, path=None):
    """Return git diff output between two commits for a path."""
    cmd = ["diff", oldest_hash + "^", newest_hash]
    if path:
        cmd += ["--", path]
    return run_git(*cmd)


def diff_name_status(oldest_hash, newest_hash, path=None):
    """Return list of (status, filepath) tuples. Status: A/M/D."""
    cmd = ["diff", "--name-status", oldest_hash + "^", newest_hash]
    if path:
        cmd += ["--", path]
    out = run_git(*cmd)
    if not out:
        return []
    results = []
    for line in out.split("\n"):
        parts = line.split("\t", 1)
        if len(parts) == 2:
            results.append((parts[0][0], parts[1]))  # first char of status
    return results


def file_at_commit(commit, path):
    """Return file contents at a specific commit, or None."""
    return run_git("show", commit + ":" + path)


def diff_lines_added(oldest_hash, newest_hash, path):
    """Return lines added (starting with +) between two commits for a path."""
    out = run_git("diff", "-U0", oldest_hash + "^", newest_hash, "--", path)
    if not out:
        return []
    return [l[1:] for l in out.split("\n") if l.startswith("+") and not l.startswith("+++")]


# ---------------------------------------------------------------------------
# Category analyzers
# ---------------------------------------------------------------------------

def analyze_requirements(oldest, newest, changes):
    """Analyze changes to specs/requirements.md."""
    info = {"added": [], "modified": [], "summary": "No change"}
    req_changes = [c for c in changes if c[1] == "specs/requirements.md"]
    if not req_changes:
        return info

    status = req_changes[0][0]
    if status == "A":
        # File was created — everything is new
        content = file_at_commit(newest, "specs/requirements.md") or ""
        reqs = re.findall(r"^## (REQ-\d+.*)", content, re.MULTILINE)
        info["added"] = reqs
        info["summary"] = f"{len(reqs)} added"
        return info

    # File was modified — check added lines for new REQ headings
    added = diff_lines_added(oldest, newest, "specs/requirements.md")
    new_reqs = [l.replace("## ", "") for l in added if l.startswith("## REQ-")]
    info["added"] = new_reqs

    # Any other changes count as modifications
    diff_out = run_git("diff", "-U0", oldest + "^", newest, "--", "specs/requirements.md") or ""
    existing_reqs_touched = set()
    current_req = None
    for line in diff_out.split("\n"):
        m = re.match(r"^@@.*\+(\d+)", line)
        if m:
            current_req = None
        if line.startswith("-") and not line.startswith("---"):
            req_m = re.search(r"(REQ-\d+)", line)
            if req_m:
                existing_reqs_touched.add(req_m.group(1))
    # Remove newly added from modified
    new_ids = set(re.search(r"(REQ-\d+)", r).group(1) for r in new_reqs if re.search(r"(REQ-\d+)", r))
    modified = [r for r in existing_reqs_touched if r not in new_ids]
    info["modified"] = modified

    parts = []
    if new_reqs:
        parts.append(f"{len(new_reqs)} added")
    if modified:
        parts.append(f"{len(modified)} modified")
    info["summary"] = ", ".join(parts) if parts else "Modified"
    return info


def analyze_prd(oldest, newest, changes):
    """Analyze changes to specs/prd/prd.md."""
    info = {"status": "No change", "sections": []}
    prd_changes = [c for c in changes if c[1] == "specs/prd/prd.md"]
    if not prd_changes:
        return info

    status = prd_changes[0][0]
    if status == "A":
        content = file_at_commit(newest, "specs/prd/prd.md") or ""
        req_links = len(re.findall(r"REQ-\d+", content))
        info["status"] = f"Created ({req_links} requirements linked)"
        return info

    # Modified — find which sections changed
    diff_out = run_git("diff", "-U3", oldest + "^", newest, "--", "specs/prd/prd.md") or ""
    sections = set()
    for line in diff_out.split("\n"):
        m = re.match(r"^@@.*@@\s*(##.*)", line)
        if m:
            sections.add(m.group(1).strip())
    info["status"] = "Modified"
    info["sections"] = list(sections)
    return info


def analyze_behavior_specs(oldest, newest, changes):
    """Analyze changes to specs/behavior/REQ-*.md."""
    info = {"new": [], "modified": [], "summary": "No change"}
    spec_changes = [c for c in changes if re.match(r"specs/behavior/REQ-.*\.md$", c[1])]
    if not spec_changes:
        return info

    for status, path in spec_changes:
        fname = os.path.basename(path)
        content = file_at_commit(newest, path) or ""
        scenario_count = len(re.findall(r"^\|\s*S", content, re.MULTILINE))
        entry = f"{fname.replace('.md', '')} ({scenario_count} scenarios)"
        if status == "A":
            info["new"].append(entry)
        elif status == "M":
            info["modified"].append(entry)

    total_scenarios = 0
    for entry in info["new"]:
        m = re.search(r"\((\d+) scenarios\)", entry)
        if m:
            total_scenarios += int(m.group(1))

    parts = []
    if info["new"]:
        parts.append(f"{len(info['new'])} new ({total_scenarios} scenarios)")
    if info["modified"]:
        parts.append(f"{len(info['modified'])} modified")
    info["summary"] = ", ".join(parts) if parts else "No change"
    return info


def analyze_personas(oldest, newest, changes):
    """Analyze changes to specs/personas/*.md."""
    info = {"created": [], "modified": [], "removed": [], "summary": "No change"}
    p_changes = [c for c in changes if re.match(r"specs/personas/.*\.md$", c[1])]
    if not p_changes:
        return info

    for status, path in p_changes:
        fname = os.path.basename(path).replace(".md", "")
        if status == "A":
            info["created"].append(fname)
        elif status == "M":
            info["modified"].append(fname)
        elif status == "D":
            info["removed"].append(fname)

    parts = []
    if info["created"]:
        parts.append(f"{len(info['created'])} created")
    if info["modified"]:
        parts.append(f"{len(info['modified'])} modified")
    if info["removed"]:
        parts.append(f"{len(info['removed'])} removed")
    info["summary"] = ", ".join(parts) if parts else "No change"
    return info


def analyze_epics_tasks(oldest, newest, changes):
    """Analyze changes to specs/epics/."""
    info = {"new_epics": [], "new_tasks": [], "status_changes": [], "summary": "0"}
    epic_changes = [c for c in changes if c[1].startswith("specs/epics/")]
    if not epic_changes:
        return info

    for status, path in epic_changes:
        fname = os.path.basename(path)
        if status == "A":
            if "task-" in fname.lower() or "/tasks/" in path:
                info["new_tasks"].append(fname.replace(".md", ""))
            else:
                info["new_epics"].append(fname.replace(".md", ""))
        elif status == "M":
            # Check for status changes in frontmatter
            old_content = file_at_commit(oldest, path) or ""
            new_content = file_at_commit(newest, path) or ""
            old_status = _extract_frontmatter_field(old_content, "status")
            new_status = _extract_frontmatter_field(new_content, "status")
            if old_status and new_status and old_status != new_status:
                info["status_changes"].append(f"{fname.replace('.md', '')}: {old_status} → {new_status}")

    parts = []
    if info["new_epics"]:
        parts.append(f"{len(info['new_epics'])} new epics")
    if info["new_tasks"]:
        parts.append(f"{len(info['new_tasks'])} new tasks")
    if info["status_changes"]:
        parts.append(f"{len(info['status_changes'])} status changes")
    info["summary"] = ", ".join(parts) if parts else "0"
    return info


def analyze_stories(oldest, newest, changes):
    """Analyze changes to specs/stories/us-*.md."""
    info = {"new": [], "modified": [], "summary": "No change"}
    s_changes = [c for c in changes if re.match(r"specs/stories/us-.*\.md$", c[1])]
    if not s_changes:
        return info

    for status, path in s_changes:
        fname = os.path.basename(path).replace(".md", "")
        if status == "A":
            info["new"].append(fname)
        elif status == "M":
            info["modified"].append(fname)

    parts = []
    if info["new"]:
        parts.append(f"{len(info['new'])} new")
    if info["modified"]:
        parts.append(f"{len(info['modified'])} modified")
    info["summary"] = ", ".join(parts) if parts else "No change"
    return info


def analyze_signoff(oldest, newest, changes):
    """Analyze changes to sign-off document directories."""
    dirs = {
        "specs/srs/": "SRS",
        "specs/design/": "Design",
        "specs/test-plan/": "Test Plan",
        "specs/journeys/": "Journeys",
    }
    info = {"items": [], "summary": "No change"}

    for prefix, label in dirs.items():
        dir_changes = [c for c in changes if c[1].startswith(prefix)]
        if not dir_changes:
            continue
        created = [c for c in dir_changes if c[0] == "A"]
        modified = [c for c in dir_changes if c[0] == "M"]

        # Check status in frontmatter of newest version
        statuses = set()
        for _, path in dir_changes:
            content = file_at_commit(newest, path) or ""
            s = _extract_frontmatter_field(content, "status")
            if s:
                statuses.add(s)

        status_str = ", ".join(sorted(statuses)) if statuses else ""

        if created:
            count = len(created)
            desc = f"{count} {label.lower()}" if count > 1 else label
            if status_str:
                desc += f" ({status_str})"
            info["items"].append(("Created", desc))
        if modified:
            count = len(modified)
            desc = f"{count} {label.lower()}" if count > 1 else label
            if status_str:
                desc += f" ({status_str})"
            info["items"].append(("Modified", desc))

    if info["items"]:
        parts = []
        for action, desc in info["items"]:
            parts.append(desc)
        info["summary"] = ", ".join(parts)
    return info


def analyze_deliverables(oldest, newest, changes):
    """Analyze changes to specs/deliverable-tracker.md."""
    info = {"changes": [], "summary": "No change"}
    dt_changes = [c for c in changes if c[1] == "specs/deliverable-tracker.md"]
    if not dt_changes:
        return info

    status = dt_changes[0][0]
    if status == "A":
        info["summary"] = "Created"
        return info

    # Parse table rows for status changes
    old_content = file_at_commit(oldest, "specs/deliverable-tracker.md") or ""
    new_content = file_at_commit(newest, "specs/deliverable-tracker.md") or ""
    old_rows = _parse_table_rows(old_content)
    new_rows = _parse_table_rows(new_content)

    changes_found = []
    for row_id, new_cols in new_rows.items():
        if row_id in old_rows:
            old_cols = old_rows[row_id]
            if old_cols != new_cols:
                changes_found.append(f"{row_id}: changed")
        else:
            changes_found.append(f"{row_id}: added")

    info["changes"] = changes_found
    info["summary"] = f"{len(changes_found)} updates" if changes_found else "Modified"
    return info


def analyze_state(oldest, newest, changes):
    """Analyze changes to .pm/state.json."""
    info = {"phase_change": None, "blockers": {"added": 0, "resolved": 0}, "summary": "No change"}
    s_changes = [c for c in changes if c[1] == ".pm/state.json"]
    if not s_changes:
        return info

    import json
    old_content = file_at_commit(oldest, ".pm/state.json")
    new_content = file_at_commit(newest, ".pm/state.json")

    try:
        old_state = json.loads(old_content) if old_content else {}
    except json.JSONDecodeError:
        old_state = {}
    try:
        new_state = json.loads(new_content) if new_content else {}
    except json.JSONDecodeError:
        new_state = {}

    old_phase = old_state.get("current_phase", "")
    new_phase = new_state.get("current_phase", "")
    if old_phase != new_phase:
        info["phase_change"] = f"{old_phase or 'none'} → {new_phase}"

    old_blockers = set(b.get("id", "") for b in old_state.get("blockers", []))
    new_blockers = set(b.get("id", "") for b in new_state.get("blockers", []))
    info["blockers"]["added"] = len(new_blockers - old_blockers)
    info["blockers"]["resolved"] = len(old_blockers - new_blockers)

    parts = []
    if info["phase_change"]:
        parts.append(f"Phase: {info['phase_change']}")
    ba, br = info["blockers"]["added"], info["blockers"]["resolved"]
    if ba or br:
        parts.append(f"Blockers: {ba} added, {br} resolved")
    info["summary"] = "; ".join(parts) if parts else "Modified"
    return info


def analyze_audit_log(date_from, date_to):
    """Parse .pm/audit.log for activity in date range."""
    info = {"count": 0, "actions": [], "summary": "No activity"}
    if not os.path.exists(".pm/audit.log"):
        return info

    import json
    actions = []
    try:
        with open(".pm/audit.log") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry.get("timestamp", entry.get("ts", ""))
                if not ts:
                    continue
                try:
                    entry_date = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
                except (ValueError, AttributeError):
                    # Try parsing just the date portion
                    try:
                        entry_date = date.fromisoformat(ts[:10])
                    except (ValueError, IndexError):
                        continue
                if date_from <= entry_date <= date_to:
                    skill = entry.get("skill", entry.get("action", entry.get("command", "unknown")))
                    output = entry.get("output", entry.get("artifact", entry.get("result", "")))
                    actions.append(f"{skill} → {output}" if output else skill)
    except Exception:
        return info

    info["count"] = len(actions)
    info["actions"] = actions
    info["summary"] = f"{len(actions)} actions" if actions else "No activity"
    return info


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_frontmatter_field(content, field):
    """Extract a field value from YAML frontmatter."""
    lines = content.split("\n")
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            if in_fm:
                return None
            in_fm = True
            continue
        if in_fm:
            m = re.match(rf"^{field}\s*:\s*(.+)", line)
            if m:
                return m.group(1).strip().strip("'\"")
    return None


def _parse_table_rows(content):
    """Parse markdown table rows into {first_col: row_text} dict."""
    rows = {}
    for line in content.split("\n"):
        if line.startswith("|") and "---" not in line:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if cols and cols[0] and not cols[0].startswith("**") and cols[0] != "ID":
                rows[cols[0]] = line.strip()
    return rows


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(date_from, date_to):
    """Generate the full change report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    hashes = commits_in_range(date_from, date_to)

    if not hashes:
        return f"# Change Report: {date_from} → {date_to}\n\n**No changes found between {date_from} and {date_to}.**\n"

    oldest = hashes[0]
    newest = hashes[-1]

    # Get all changed files
    changes = diff_name_status(oldest, newest)

    # Run all analyzers
    req = analyze_requirements(oldest, newest, changes)
    prd = analyze_prd(oldest, newest, changes)
    behavior = analyze_behavior_specs(oldest, newest, changes)
    personas = analyze_personas(oldest, newest, changes)
    epics = analyze_epics_tasks(oldest, newest, changes)
    stories = analyze_stories(oldest, newest, changes)
    signoff = analyze_signoff(oldest, newest, changes)
    deliverables = analyze_deliverables(oldest, newest, changes)
    state = analyze_state(oldest, newest, changes)
    audit = analyze_audit_log(date_from, date_to)

    # Build blockers summary
    ba = state["blockers"]["added"]
    br = state["blockers"]["resolved"]
    blocker_summary = f"{ba} added, {br} resolved"

    # Build report
    lines = []
    lines.append(f"# Change Report: {date_from} → {date_to}")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Commits in range:** {len(hashes)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Category | Changes |")
    lines.append("|----------|---------|")
    lines.append(f"| Requirements | {req['summary']} |")
    lines.append(f"| PRD | {prd['status']} |")
    lines.append(f"| Behavior Specs | {behavior['summary']} |")
    lines.append(f"| Personas | {personas['summary']} |")
    lines.append(f"| Epics & Tasks | {epics['summary']} |")
    lines.append(f"| User Stories | {stories['summary']} |")
    lines.append(f"| Sign-Off | {signoff['summary']} |")
    lines.append(f"| Deliverables | {deliverables['summary']} |")
    lines.append(f"| Blockers | {blocker_summary} |")
    lines.append("")
    lines.append("---")

    # Detailed sections
    if req["added"] or req["modified"]:
        lines.append("")
        lines.append("## Requirements")
        if req["added"]:
            lines.append(f"- **Added:** {', '.join(req['added'])}")
        if req["modified"]:
            lines.append(f"- **Modified:** {', '.join(req['modified'])}")

    if prd["status"] != "No change":
        lines.append("")
        lines.append("## PRD")
        lines.append(f"- **{prd['status'].split('(')[0].strip()}:** specs/prd/prd.md" +
                      (f" ({prd['status'].split('(')[1]}" if "(" in prd["status"] else ""))
        if prd["sections"]:
            lines.append(f"- **Sections changed:** {', '.join(prd['sections'])}")

    if behavior["new"] or behavior["modified"]:
        lines.append("")
        lines.append("## Behavior Specs")
        if behavior["new"]:
            lines.append(f"- **New:** {', '.join(behavior['new'])}")
        if behavior["modified"]:
            lines.append(f"- **Modified:** {', '.join(behavior['modified'])}")

    if personas["created"] or personas["modified"] or personas["removed"]:
        lines.append("")
        lines.append("## Personas")
        if personas["created"]:
            lines.append(f"- **Created:** {', '.join(personas['created'])}")
        if personas["modified"]:
            lines.append(f"- **Modified:** {', '.join(personas['modified'])}")
        if personas["removed"]:
            lines.append(f"- **Removed:** {', '.join(personas['removed'])}")

    if epics["new_epics"] or epics["new_tasks"] or epics["status_changes"]:
        lines.append("")
        lines.append("## Epics & Tasks")
        if epics["new_epics"]:
            lines.append(f"- **New epics:** {', '.join(epics['new_epics'])}")
        if epics["new_tasks"]:
            lines.append(f"- **New tasks:** {', '.join(epics['new_tasks'])}")
        if epics["status_changes"]:
            for sc in epics["status_changes"]:
                lines.append(f"- **Status:** {sc}")

    if stories["new"] or stories["modified"]:
        lines.append("")
        lines.append("## User Stories")
        if stories["new"]:
            lines.append(f"- **New:** {', '.join(stories['new'])}")
        if stories["modified"]:
            lines.append(f"- **Modified:** {', '.join(stories['modified'])}")

    if signoff["items"]:
        lines.append("")
        lines.append("## Sign-Off Documents")
        for action, desc in signoff["items"]:
            lines.append(f"- **{action}:** {desc}")

    if deliverables["changes"]:
        lines.append("")
        lines.append("## Deliverables")
        for ch in deliverables["changes"]:
            lines.append(f"- {ch}")

    if state["phase_change"] or state["blockers"]["added"] or state["blockers"]["resolved"]:
        lines.append("")
        lines.append("## Project State")
        if state["phase_change"]:
            lines.append(f"- **Phase:** {state['phase_change']}")
        if ba or br:
            lines.append(f"- **Blockers:** {blocker_summary}")

    if audit["count"] > 0:
        lines.append("")
        lines.append(f"## Activity Log ({audit['count']} actions)")
        for action in audit["actions"]:
            lines.append(f"- {action}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate a change report between two dates from git history.")
    parser.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="date_to", help="End date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--days", type=int, help="Shortcut: last N days (alternative to --from/--to)")
    args = parser.parse_args()

    if not is_git_repo():
        print("Error: not inside a git repository.", file=sys.stderr)
        sys.exit(1)

    today = date.today()

    if args.days:
        date_from = today - timedelta(days=args.days)
        date_to = today
    elif args.date_from:
        try:
            date_from = date.fromisoformat(args.date_from)
        except ValueError:
            print(f"Error: invalid --from date: {args.date_from}", file=sys.stderr)
            sys.exit(1)
        if args.date_to:
            try:
                date_to = date.fromisoformat(args.date_to)
            except ValueError:
                print(f"Error: invalid --to date: {args.date_to}", file=sys.stderr)
                sys.exit(1)
        else:
            date_to = today
    else:
        parser.print_help()
        sys.exit(1)

    report = generate_report(date_from, date_to)

    # Print to stdout
    print(report)

    # Save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"diff-{date_from}-to-{date_to}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(report)
    print(f"\n---\n*Saved to {filepath}*", file=sys.stderr)


if __name__ == "__main__":
    main()
