#!/usr/bin/env bash
# pm-workflow standup — Generate daily standup report
# Usage: bash .pm/scripts/standup.sh

set -euo pipefail

PM_DIR="${PM_DIR:-.pm}"
STATE="$PM_DIR/state.json"
AUDIT="$PM_DIR/audit.log"
STANDUP="$PM_DIR/standup.md"

if [[ ! -f "$STATE" ]]; then
  echo "Error: .pm/state.json not found. Run /pm-workflow init first."
  exit 1
fi

TODAY=$(date +"%Y-%m-%d")

# Extract state info
PHASE=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('phase', 0))")
PHASE_NAME=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('phase_name', 'Unknown'))")
CURRENT=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('current_skill', 'none'))")
BLOCKED_JSON=$(python3 -c "import json; d=json.load(open('$STATE')); print(json.dumps(d.get('blocked', [])))")

# Generate standup report
cat > "$STANDUP" << EOF
## Standup — $TODAY

**Phase:** $PHASE — $PHASE_NAME

---

### ✅ Done

EOF

# Add completed skills from audit log (last 7 days)
if [[ -f "$AUDIT" ]]; then
  python3 << 'PYEOF' >> "$STANDUP"
import json
from datetime import datetime, timedelta
import sys

audit_log = sys.argv[1] if len(sys.argv) > 1 else ".pm/audit.log"
cutoff = datetime.now() - timedelta(days=7)

try:
    with open(audit_log) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                if ts.replace(tzinfo=None) >= cutoff:
                    skill = entry.get('skill', 'unknown')
                    phase = entry.get('phase', '?')
                    artifacts = entry.get('artifacts_created', [])
                    print(f"- Phase {phase}: {skill}")
                    if artifacts:
                        print(f"  → {', '.join(artifacts)}")
            except:
                pass
except:
    print("- No activity recorded")
PYEOF
else
  echo "- No activity yet" >> "$STANDUP"
fi

cat >> "$STANDUP" << EOF

---

### 🚫 Blocked

EOF

# Add blocked items
python3 << PYEOF >> "$STANDUP"
import json
blocked = $BLOCKED_JSON
if blocked:
    for item in blocked:
        print(f"- {item.get('description', 'Unknown blocker')}")
else:
    print("- None")
PYEOF

cat >> "$STANDUP" << EOF

---

### ▶️ Next

EOF

# Add next action
if [[ "$CURRENT" != "none" && "$CURRENT" != "null" ]]; then
  echo "- Run \`/$CURRENT\`" >> "$STANDUP"
else
  echo "- Run \`/pm-workflow next\` to continue" >> "$STANDUP"
fi

echo "" >> "$STANDUP"

# Output to stdout as well
cat "$STANDUP"
