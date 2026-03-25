#!/usr/bin/env bash
# Brainless — Uninstaller
set -e

CLAUDE_DIR="$HOME/.claude"

echo "Uninstalling Brainless..."

# Step 1: Remove hook from settings.json FIRST (before deleting files)
echo "[1/3] Removing hook from settings.json..."
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
if [ -f "$SETTINGS_FILE" ] && grep -qF "bash_error_search" "$SETTINGS_FILE"; then
    python3 -c "
import json
with open('$SETTINGS_FILE', 'r') as f:
    s = json.load(f)
hooks = s.get('hooks', {}).get('PostToolUse', [])
s['hooks']['PostToolUse'] = [h for h in hooks if h.get('matcher') != 'Bash' or not any('bash_error_search' in hk.get('command', '') for hk in h.get('hooks', []))]
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
" 2>/dev/null || python -c "
import json
with open('$SETTINGS_FILE', 'r') as f:
    s = json.load(f)
hooks = s.get('hooks', {}).get('PostToolUse', [])
s['hooks']['PostToolUse'] = [h for h in hooks if h.get('matcher') != 'Bash' or not any('bash_error_search' in hk.get('command', '') for hk in h.get('hooks', []))]
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
"
    echo "    Hook removed"
else
    echo "    No hook found, skipping"
fi

# Step 2: Remove Brainless section from CLAUDE.md
echo "[2/3] Cleaning CLAUDE.md..."
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
if [ -f "$CLAUDE_MD" ] && grep -qF "Brainless Auto-Behaviors" "$CLAUDE_MD"; then
    python3 -c "
import re
with open('$CLAUDE_MD', 'r') as f:
    c = f.read()
c = re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)', '', c, flags=re.DOTALL).strip()
with open('$CLAUDE_MD', 'w') as f:
    f.write(c + '\n')
" 2>/dev/null || python -c "
import re
with open('$CLAUDE_MD', 'r') as f:
    c = f.read()
c = re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)', '', c, flags=re.DOTALL).strip()
with open('$CLAUDE_MD', 'w') as f:
    f.write(c + '\n')
"
    echo "    CLAUDE.md cleaned"
else
    echo "    No brainless rules found, skipping"
fi

# Step 3: Remove files
echo "[3/3] Removing files..."
rm -rf "$CLAUDE_DIR/skills/brainless"
rm -f "$CLAUDE_DIR/commands/brain-dump.md" \
      "$CLAUDE_DIR/commands/brain-search.md" \
      "$CLAUDE_DIR/commands/brain-stats.md" \
      "$CLAUDE_DIR/commands/brain-review.md" \
      "$CLAUDE_DIR/commands/brain-cheatsheet.md" \
      "$CLAUDE_DIR/commands/brain-rebuild.md"
rm -rf "$CLAUDE_DIR/brainless"
echo "    Files removed"

echo ""
echo "Brainless uninstalled. Your brain is on your own now."
