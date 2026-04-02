#!/usr/bin/env python3
"""
PM Workflow — Project Data Updater
CLI helper for structured writes to .pm/project-data.json.
Replaces fragile markdown parsing with direct JSON mutations.

Usage:
  python3 .pm/scripts/update-project-data.py init "My Project" "en"
  python3 .pm/scripts/update-project-data.py set 'phase' '2'
  python3 .pm/scripts/update-project-data.py set 'active_epic' 'notification-system'
  python3 .pm/scripts/update-project-data.py merge 'prd' '{"exists": true, "status": "draft", "requirements": ["REQ-001"]}'
  python3 .pm/scripts/update-project-data.py replace 'requirements' '[{"id":"REQ-001","title":"Auth","status":"active"}]'
  python3 .pm/scripts/update-project-data.py append 'personas' '{"name":"Admin","type":"internal"}'
  python3 .pm/scripts/update-project-data.py update-task '001' '{"status": "in-progress", "started": "2026-04-01"}'
  python3 .pm/scripts/update-project-data.py update-deliverable 'D-001' '{"status": "approved"}'
  python3 .pm/scripts/update-project-data.py update-signoff 'docs/prd.md' '{"status": "approved"}'
  python3 .pm/scripts/update-project-data.py link-stories
  python3 .pm/scripts/update-project-data.py recalc
  echo '[{"id":"REQ-001"}]' | python3 .pm/scripts/update-project-data.py replace 'requirements' -
"""

import json
import os
import sys
import fcntl
from datetime import datetime

DATA_FILE = ".pm/project-data.json"


# ============================================================
# Metrics recalculation
# ============================================================

def recalculate(data):
    """Recalculate all derived metrics from current data."""
    tasks = data.get("tasks", [])
    stories = data.get("stories", [])
    signoff = data.get("signoff", [])
    deliverables = data.get("deliverables", [])

    story_task_ids = {str(s.get("task", "")) for s in stories if s.get("task")}
    done_statuses = ("closed", "completed", "done")
    active_statuses = ("in-progress", "in_progress")

    done = sum(1 for t in tasks if t.get("status", "").lower() in done_statuses)
    total = len(tasks)

    data["metrics"] = {
        "total_reqs": len(data.get("requirements", [])),
        "total_tasks": total,
        "done_tasks": done,
        "active_tasks": sum(1 for t in tasks if t.get("status", "").lower() in active_statuses),
        "blocked": len(data.get("blockers", [])),
        "pct": round(done / total * 100) if total else 0,
        "orphan_tasks": sum(1 for t in tasks if t["id"] not in story_task_ids),
        "signoff_approved": sum(1 for s in signoff if s.get("status", "").lower() == "approved"),
        "signoff_total": len(signoff),
        "deliv_done": sum(1 for d in deliverables if d.get("status", "").lower() == "approved"),
        "deliv_total": len(deliverables),
        "personas": len(data.get("personas", [])),
        "stories": len(stories),
    }
    data["_synced_at"] = datetime.now().isoformat()
    data["_version"] = "2.0"


# ============================================================
# File I/O with locking and atomic write
# ============================================================

def read_data():
    """Read project-data.json with shared lock."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def write_data(data):
    """Write project-data.json atomically with exclusive lock."""
    os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    os.replace(tmp_path, DATA_FILE)


# ============================================================
# Helpers
# ============================================================

def parse_json_arg(value):
    """Parse a JSON argument from CLI arg or stdin (when value is '-')."""
    if value == "-":
        return json.loads(sys.stdin.read())
    return json.loads(value)


def auto_type(value):
    """Auto-detect scalar type: booleans, integers, else string."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def deep_merge(base, patch):
    """Recursively merge patch into base dict. Patch values win."""
    for key, val in patch.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            deep_merge(base[key], val)
        else:
            base[key] = val
    return base


def navigate_dotted(data, dotted_key):
    """Navigate into nested dicts by dotted key, returning (parent, last_key).
    Creates intermediate dicts as needed."""
    parts = dotted_key.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    return current, parts[-1]


def summary(data):
    """Return a short summary string of current state."""
    m = data.get("metrics", {})
    parts = []
    if m.get("total_reqs"):
        parts.append(f"{m['total_reqs']} reqs")
    if m.get("total_tasks"):
        done = m.get("done_tasks", 0)
        parts.append(f"{m['total_tasks']} tasks ({done} done, {m.get('pct', 0)}%)")
    if m.get("stories"):
        parts.append(f"{m['stories']} stories")
    if m.get("personas"):
        parts.append(f"{m['personas']} personas")
    if m.get("signoff_total"):
        parts.append(f"{m['signoff_approved']}/{m['signoff_total']} signoffs")
    if m.get("deliv_total"):
        parts.append(f"{m['deliv_done']}/{m['deliv_total']} deliverables")
    if m.get("blocked"):
        parts.append(f"{m['blocked']} blocked")
    return " | ".join(parts) if parts else "empty project"


# ============================================================
# Subcommands
# ============================================================

def cmd_init(args):
    """Create fresh project-data.json skeleton."""
    if len(args) < 2:
        print("Usage: init <project-name> <language>", file=sys.stderr)
        sys.exit(1)
    project_name, language = args[0], args[1]
    data = {
        "_synced_at": "",
        "_version": "2.0",
        "project_name": project_name,
        "language": language,
        "phase": 0,
        "phase_name": "Setup",
        "metrics": {
            "total_reqs": 0,
            "total_tasks": 0,
            "done_tasks": 0,
            "active_tasks": 0,
            "blocked": 0,
            "pct": 0,
            "orphan_tasks": 0,
            "signoff_approved": 0,
            "signoff_total": 0,
            "deliv_done": 0,
            "deliv_total": 0,
            "personas": 0,
            "stories": 0,
        },
        "requirements": [],
        "prd": None,
        "prd_features": [],
        "personas": [],
        "stories": [],
        "epics": [],
        "active_epic": "",
        "tasks": [],
        "signoff": [],
        "deliverables": [],
        "blockers": [],
        "ingestions": [],
        "meetings": [],
        "audit": [],
        "decisions": [],
        "questions": [],
        "strategy_files": [],
        "traceability": [],
    }
    recalculate(data)
    write_data(data)
    print(f"Initialized '{project_name}' ({language}) | metrics recalculated")


def cmd_set(args):
    """Set a scalar value at a dotted key path."""
    if len(args) < 2:
        print("Usage: set <dotted-key> <value>", file=sys.stderr)
        sys.exit(1)
    dotted_key, raw_value = args[0], args[1]
    data = read_data()
    parent, last_key = navigate_dotted(data, dotted_key)
    parent[last_key] = auto_type(raw_value)
    recalculate(data)
    write_data(data)
    print(f"Set {dotted_key} = {parent[last_key]} | metrics recalculated | {summary(data)}")


def cmd_merge(args):
    """Deep-merge a JSON object into a dotted key path."""
    if len(args) < 2:
        print("Usage: merge <dotted-key> <json-object>", file=sys.stderr)
        sys.exit(1)
    dotted_key, raw_json = args[0], args[1]
    patch = parse_json_arg(raw_json)
    data = read_data()
    if dotted_key == "":
        deep_merge(data, patch)
    else:
        parent, last_key = navigate_dotted(data, dotted_key)
        if last_key not in parent or parent[last_key] is None:
            parent[last_key] = {}
        if isinstance(parent[last_key], dict):
            deep_merge(parent[last_key], patch)
        else:
            parent[last_key] = patch
    recalculate(data)
    write_data(data)
    label = dotted_key if dotted_key else "root"
    print(f"Merged into {label} | metrics recalculated | {summary(data)}")


def cmd_replace(args):
    """Replace a top-level key's value entirely."""
    if len(args) < 2:
        print("Usage: replace <key> <json-value>", file=sys.stderr)
        sys.exit(1)
    key, raw_json = args[0], args[1]
    value = parse_json_arg(raw_json)
    data = read_data()
    data[key] = value
    recalculate(data)
    write_data(data)
    count = len(value) if isinstance(value, list) else 1
    print(f"Replaced {key} ({count} items) | metrics recalculated | {summary(data)}")


def cmd_append(args):
    """Append an object to an array key."""
    if len(args) < 2:
        print("Usage: append <key> <json-object>", file=sys.stderr)
        sys.exit(1)
    key, raw_json = args[0], args[1]
    item = parse_json_arg(raw_json)
    data = read_data()
    if key not in data or not isinstance(data[key], list):
        data[key] = []
    data[key].append(item)
    recalculate(data)
    write_data(data)
    print(f"Appended to {key} ({len(data[key])} total) | metrics recalculated | {summary(data)}")


def cmd_update_task(args):
    """Find task by id and merge patch fields. Update traceability if status changed."""
    if len(args) < 2:
        print("Usage: update-task <task-id> <json-patch>", file=sys.stderr)
        sys.exit(1)
    task_id, raw_json = args[0], args[1]
    patch = parse_json_arg(raw_json)
    data = read_data()
    tasks = data.get("tasks", [])

    found = False
    for task in tasks:
        if str(task.get("id", "")) == str(task_id):
            task.update(patch)
            found = True
            break

    if not found:
        print(f"Task '{task_id}' not found", file=sys.stderr)
        sys.exit(1)

    # Update matching traceability entry if status changed
    if "status" in patch:
        for entry in data.get("traceability", []):
            if str(entry.get("task", "")) == str(task_id):
                entry["status"] = patch["status"]

    recalculate(data)
    write_data(data)
    print(f"Updated task {task_id} | metrics recalculated | {summary(data)}")


def cmd_update_deliverable(args):
    """Find deliverable by id and merge patch fields."""
    if len(args) < 2:
        print("Usage: update-deliverable <deliverable-id> <json-patch>", file=sys.stderr)
        sys.exit(1)
    deliv_id, raw_json = args[0], args[1]
    patch = parse_json_arg(raw_json)
    data = read_data()

    found = False
    for deliv in data.get("deliverables", []):
        if str(deliv.get("id", "")) == str(deliv_id):
            deliv.update(patch)
            found = True
            break

    if not found:
        print(f"Deliverable '{deliv_id}' not found", file=sys.stderr)
        sys.exit(1)

    recalculate(data)
    write_data(data)
    print(f"Updated deliverable {deliv_id} | metrics recalculated | {summary(data)}")


def cmd_update_signoff(args):
    """Find signoff entry by path and merge patch fields."""
    if len(args) < 2:
        print("Usage: update-signoff <file-path> <json-patch>", file=sys.stderr)
        sys.exit(1)
    file_path, raw_json = args[0], args[1]
    patch = parse_json_arg(raw_json)
    data = read_data()

    found = False
    for entry in data.get("signoff", []):
        if entry.get("path", "") == file_path:
            entry.update(patch)
            found = True
            break

    if not found:
        print(f"Signoff entry for '{file_path}' not found", file=sys.stderr)
        sys.exit(1)

    recalculate(data)
    write_data(data)
    print(f"Updated signoff for {file_path} | metrics recalculated | {summary(data)}")


def cmd_link_stories(args):
    """For each story with a task field, set the corresponding task's story field."""
    data = read_data()
    stories = data.get("stories", [])
    tasks = data.get("tasks", [])
    traceability = data.get("traceability", [])

    # Build task lookup by id
    task_map = {str(t.get("id", "")): t for t in tasks}
    trace_map = {str(e.get("task", "")): e for e in traceability}

    linked = 0
    for story in stories:
        task_id = story.get("task")
        if not task_id:
            continue
        task_id_str = str(task_id)
        story_ref = story.get("id", story.get("name", ""))

        if task_id_str in task_map:
            task_map[task_id_str]["story"] = story_ref
            linked += 1

        if task_id_str in trace_map:
            trace_map[task_id_str]["story"] = story_ref

    recalculate(data)
    write_data(data)
    print(f"Linked {linked} stories to tasks | metrics recalculated | {summary(data)}")


def cmd_recalc(args):
    """Just recalculate metrics without any other mutation."""
    data = read_data()
    recalculate(data)
    write_data(data)
    print(f"Metrics recalculated | {summary(data)}")


# ============================================================
# Main dispatch
# ============================================================

COMMANDS = {
    "init": cmd_init,
    "set": cmd_set,
    "merge": cmd_merge,
    "replace": cmd_replace,
    "append": cmd_append,
    "update-task": cmd_update_task,
    "update-deliverable": cmd_update_deliverable,
    "update-signoff": cmd_update_signoff,
    "link-stories": cmd_link_stories,
    "recalc": cmd_recalc,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    cmd_name = sys.argv[1]
    if cmd_name not in COMMANDS:
        print(f"Unknown command: {cmd_name}", file=sys.stderr)
        print(f"Available: {', '.join(COMMANDS.keys())}", file=sys.stderr)
        sys.exit(1)

    COMMANDS[cmd_name](sys.argv[2:])


if __name__ == "__main__":
    main()
