#!/usr/bin/env bash
# Brainless — Your External Brain | Installer
set -e

CLAUDE_DIR="$HOME/.claude"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cat << 'BANNER'

  ____            _       _
 | __ ) _ __ __ _(_)_ __ | | ___  ___ ___
 |  _ \| '__/ _` | | '_ \| |/ _ \/ __/ __|
 | |_) | | | (_| | | | | | |  __/\__ \__ \
 |____/|_|  \__,_|_|_| |_|_|\___||___/___/

 "You don't need a brain. I remember everything for you."

BANNER

if [ ! -d "$CLAUDE_DIR" ]; then
    echo "[!] Claude Code not found at $CLAUDE_DIR"; exit 1
fi

echo "[1/7] Creating brain structure..."
mkdir -p "$CLAUDE_DIR/skills/brainless" "$CLAUDE_DIR/commands" "$CLAUDE_DIR/brainless/hooks"
for cat in build runtime config network dependency permission logic ctf reversing exploit tricks tools other _cheatsheets; do
    mkdir -p "$CLAUDE_DIR/brainless/$cat"
done

echo "[2/7] Installing skill..."
cp "$SCRIPT_DIR/skills/brainless/SKILL.md" "$CLAUDE_DIR/skills/brainless/SKILL.md"

echo "[3/7] Installing commands..."
for cmd in brain-dump brain-search brain-review brain-cheatsheet brain-stats brain-rebuild; do
    cp "$SCRIPT_DIR/commands/$cmd.md" "$CLAUDE_DIR/commands/$cmd.md"
done

echo "[4/7] Installing hooks..."
for hook_file in bash_error_search.py session_start.py post_tool_logger.py session_end.py; do
    cp "$SCRIPT_DIR/hooks/$hook_file" "$CLAUDE_DIR/brainless/hooks/$hook_file"
done

# Inject all hooks into settings.json (install_hook.py handles idempotency)
python3 "$SCRIPT_DIR/hooks/install_hook.py" 2>/dev/null || python "$SCRIPT_DIR/hooks/install_hook.py"

echo "[5/7] Initializing knowledge base..."
if [ ! -f "$CLAUDE_DIR/brainless/INDEX.md" ]; then
    cp "$SCRIPT_DIR/brainless/INDEX.md" "$CLAUDE_DIR/brainless/INDEX.md"
    cp "$SCRIPT_DIR/brainless/_cache.json" "$CLAUDE_DIR/brainless/_cache.json"
    for cat in build runtime config network dependency permission logic ctf reversing exploit tricks tools other; do
        [ ! -f "$CLAUDE_DIR/brainless/$cat/_index.md" ] && cp "$SCRIPT_DIR/brainless/$cat/_index.md" "$CLAUDE_DIR/brainless/$cat/_index.md"
    done
    echo "    Fresh brain initialized — ready to absorb knowledge"
else
    echo "    Existing brain found — preserving memories, updating skill only"
fi

echo "[6/7] Injecting auto-behaviors into CLAUDE.md..."
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
MARKER="## Brainless Auto-Behaviors (MANDATORY)"

if [ -f "$CLAUDE_MD" ] && grep -qF "$MARKER" "$CLAUDE_MD"; then
    # Remove old brainless section and replace with new one
    python3 -c "
import re, sys
with open('$CLAUDE_MD', 'r') as f:
    content = f.read()
# Remove old brainless section (from marker to next ## or EOF)
pattern = r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)'
content = re.sub(pattern, '', content, flags=re.DOTALL).rstrip()
with open('$CLAUDE_MD', 'w') as f:
    f.write(content + '\n')
" 2>/dev/null || python -c "
import re, sys
with open('$CLAUDE_MD', 'r') as f:
    content = f.read()
pattern = r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)'
content = re.sub(pattern, '', content, flags=re.DOTALL).rstrip()
with open('$CLAUDE_MD', 'w') as f:
    f.write(content + '\n')
"
    echo "    Updated existing brainless rules in $CLAUDE_MD"
else
    echo "    Adding brainless rules to $CLAUDE_MD"
fi

# Append the brainless auto-behavior rules
cat >> "$CLAUDE_MD" << 'BRAINLESS_RULES'

## Brainless Auto-Behaviors (MANDATORY)

These rules apply to EVERY conversation, regardless of whether the brainless skill is loaded.
They ensure Claude automatically records and recalls knowledge from `~/.claude/brainless/`.

### Auto-Search: Before fixing ANY error
When encountering a non-zero exit code or unexpected error:
1. Read `~/.claude/brainless/_cache.json` FIRST
2. Search for matching keywords/tags in the entries
3. If a match is found, read the full entry and apply the known solution
4. Only if no match exists, proceed with normal debugging

### Auto-Record: After resolving ANY non-trivial error
After successfully resolving an error that was NOT a simple typo:
1. Immediately invoke `/brain-dump` to record the problem and solution
2. Do this BEFORE continuing to the next task
3. Do NOT ask permission — just record it
4. Do NOT batch recordings — record each issue individually as it is resolved
5. Skip ONLY if: it was a trivial typo, OR an identical entry already exists

### What counts as "non-trivial"
- Any non-zero exit code that required investigation
- Environment/config issues
- Build errors that weren't obvious typos
- Any situation where multiple approaches were tried
- CTF challenges, RE findings, exploit techniques
BRAINLESS_RULES

echo "    Done — auto-behaviors will now work in every conversation"

echo "[7/7] Verifying..."
echo "    Skill:    $CLAUDE_DIR/skills/brainless/SKILL.md"
echo "    Commands: brain-dump, brain-search, brain-stats, brain-review, brain-cheatsheet, brain-rebuild"
echo "    Hooks:    $CLAUDE_DIR/brainless/hooks/ (SessionStart + PostToolUse + Stop)"
echo "    Brain:    $CLAUDE_DIR/brainless/"

echo ""
echo "=== Brainless installed! ==="
echo ""
echo "Commands:   /brain-dump  /brain-search  /brain-stats  /brain-review  /brain-cheatsheet  /brain-rebuild"
echo "Categories: build runtime config network dependency permission logic"
echo "            ctf reversing exploit tricks tools"
echo ""
echo "Hooks:      SessionStart (context) | PostToolUse (search + log) | Stop (summary)"
echo "Auto: search brain before fixing | record after resolving"
echo "Optimization: 3-level search (JSON cache -> sub-index -> full entry)"
echo ""
echo "Now go be brainless. I'll remember everything for you."
