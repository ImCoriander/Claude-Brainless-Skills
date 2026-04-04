#!/usr/bin/env python3
"""
Brainless — Your External Brain | Cross-platform Installer
Works on Linux, macOS, Windows (CMD/PowerShell/Git Bash)
"""
import os
import sys
import re
import shutil
import json

BANNER = r"""
  ____            _       _
 | __ ) _ __ __ _(_)_ __ | | ___  ___ ___
 |  _ \| '__/ _` | | '_ \| |/ _ \/ __/ __|
 | |_) | | | (_| | | | | | |  __/\__ \__ \
 |____/|_|  \__,_|_|_| |_|_|\___||___/___/

 "You don't need a brain. I remember everything for you."
"""

BRAINLESS_RULES = """\

## Brainless Auto-Behaviors (MANDATORY — ZERO EXCEPTIONS)

These rules apply to EVERY conversation, regardless of whether the brainless skill is loaded.
They ensure Claude automatically records and recalls knowledge from `~/.claude/brainless/`.
**Failure to follow these rules is a critical behavioral bug.**

### Auto-Search: On ANY error from ANY tool

When you see an error from ANY tool (Bash non-zero exit, Edit failure, build error, etc.):

1. The `universal_error_search.py` hook will auto-search and output `[BRAINLESS]` results
2. If hook outputs a known solution → READ the full entry file and APPLY it
3. If hook outputs "NO known solution" → proceed with debugging, but you are NOW OBLIGATED to record after resolving
4. If no hook output appears → manually read `~/.claude/brainless/_cache.json` and search

### Auto-Record: IMMEDIATELY after resolving ANY non-trivial error

**This is NOT optional. This is IMMEDIATE.**

After successfully resolving an error that required any investigation:

1. **STOP** what you are doing
2. Invoke `/brain-dump` RIGHT NOW — before ANY other action
3. Do NOT ask permission — just record it
4. Do NOT say "I'll record this later" — there is no later
5. Do NOT batch — record each issue individually as resolved
6. Only skip if: trivial typo fix, OR identical entry already exists in `_cache.json`

### What counts as "non-trivial" (record ALL of these)

- Any non-zero exit code that required more than re-running the command
- Environment/config issues (python3 vs python, path issues, etc.)
- Build errors that weren't single-character typos
- Any situation where you tried more than one approach
- Tool errors (Edit failed, file not found, permission denied)
- CTF challenges, RE findings, exploit techniques
- Any error where the solution was surprising or non-obvious

### Self-check

If you resolved an error and did NOT invoke `/brain-dump`, you have a bug in your behavior. Go back and record it now.
"""


def main():
    print(BANNER)

    claude_dir = os.path.join(os.path.expanduser("~"), ".claude")
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(claude_dir):
        print(f"[!] Claude Code not found at {claude_dir}")
        sys.exit(1)

    # [1/7] Create brain structure
    print("[1/7] Creating brain structure...")
    for d in ["skills/brainless", "commands", "brainless/hooks"]:
        os.makedirs(os.path.join(claude_dir, d), exist_ok=True)
    for cat in ["build", "runtime", "config", "network", "dependency", "permission",
                "logic", "ctf", "reversing", "exploit", "tricks", "tools", "other",
                "_cheatsheets"]:
        os.makedirs(os.path.join(claude_dir, "brainless", cat), exist_ok=True)

    # [2/7] Install skill
    print("[2/7] Installing skill...")
    shutil.copy2(
        os.path.join(script_dir, "skills", "brainless", "SKILL.md"),
        os.path.join(claude_dir, "skills", "brainless", "SKILL.md"),
    )

    # [3/7] Install commands
    print("[3/7] Installing commands...")
    for cmd in ["brain-dump", "brain-search", "brain-review", "brain-cheatsheet",
                "brain-stats", "brain-rebuild"]:
        src = os.path.join(script_dir, "commands", f"{cmd}.md")
        dst = os.path.join(claude_dir, "commands", f"{cmd}.md")
        if os.path.isfile(src):
            shutil.copy2(src, dst)

    # [4/7] Install hooks
    print("[4/7] Installing hooks...")
    for hook_file in ["universal_error_search.py", "session_start.py",
                      "post_tool_logger.py", "session_end.py",
                      "streak_reminder.py", "trash_talk.py",
                      "user_prompt_search.py", "post_compact.py",
                      "cwd_changed.py", "subagent_stop.py",
                      "stop_failure.py"]:
        src = os.path.join(script_dir, "hooks", hook_file)
        dst = os.path.join(claude_dir, "brainless", "hooks", hook_file)
        if os.path.isfile(src):
            shutil.copy2(src, dst)

    # Remove legacy bash-only hook if present
    legacy = os.path.join(claude_dir, "brainless", "hooks", "bash_error_search.py")
    if os.path.isfile(legacy):
        os.remove(legacy)

    # Inject hooks into settings.json
    hook_installer = os.path.join(script_dir, "hooks", "install_hook.py")
    os.system(f'"{sys.executable}" "{hook_installer}"')

    # [5/7] Initialize knowledge base
    print("[5/7] Initializing knowledge base...")
    index_file = os.path.join(claude_dir, "brainless", "INDEX.md")
    if not os.path.isfile(index_file):
        shutil.copy2(
            os.path.join(script_dir, "brainless", "INDEX.md"), index_file
        )
        shutil.copy2(
            os.path.join(script_dir, "brainless", "_cache.json"),
            os.path.join(claude_dir, "brainless", "_cache.json"),
        )
        for cat in ["build", "runtime", "config", "network", "dependency",
                    "permission", "logic", "ctf", "reversing", "exploit",
                    "tricks", "tools", "other"]:
            src = os.path.join(script_dir, "brainless", cat, "_index.md")
            dst = os.path.join(claude_dir, "brainless", cat, "_index.md")
            if os.path.isfile(src) and not os.path.isfile(dst):
                shutil.copy2(src, dst)
        print("    Fresh brain initialized — ready to absorb knowledge")
    else:
        print("    Existing brain found — preserving memories, updating skill only")

    # [6/7] Inject auto-behaviors into CLAUDE.md
    print("[6/7] Injecting auto-behaviors into CLAUDE.md...")
    claude_md = os.path.join(claude_dir, "CLAUDE.md")

    if os.path.isfile(claude_md):
        with open(claude_md, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    # Remove old brainless section if present
    if "Brainless Auto-Behaviors" in content:
        pattern = r"\n*## Brainless Auto-Behaviors \(MANDATORY[^)]*\).*?(?=\n## (?!Brainless)|$)"
        content = re.sub(pattern, "", content, flags=re.DOTALL).rstrip()
        print("    Updated existing brainless rules in CLAUDE.md")
    else:
        print("    Adding brainless rules to CLAUDE.md")

    with open(claude_md, "w", encoding="utf-8") as f:
        f.write(content + BRAINLESS_RULES)

    print("    Done — auto-behaviors will now work in every conversation")

    # [7/7] Verify
    print("[7/7] Verifying...")
    print(f"    Skill:    {os.path.join(claude_dir, 'skills', 'brainless', 'SKILL.md')}")
    print("    Commands: brain-dump, brain-search, brain-stats, brain-review, brain-cheatsheet, brain-rebuild")
    print(f"    Hooks:    {os.path.join(claude_dir, 'brainless', 'hooks')}/ (10 events)")
    print(f"    Brain:    {os.path.join(claude_dir, 'brainless')}/")

    print()
    print("=== Brainless installed! ===")
    print()
    print("Commands:   /brain-dump  /brain-search  /brain-stats  /brain-review  /brain-cheatsheet  /brain-rebuild")
    print("Categories: build runtime config network dependency permission logic")
    print("            ctf reversing exploit tricks tools")
    print()
    print("Hooks:      PreToolUse (streak) | UserPromptSubmit (pre-search)")
    print("            SessionStart (context) | PostToolUse (search + log)")
    print("            PostToolUseFailure (error) | PostCompact (memory restore)")
    print("            CwdChanged (project) | SubagentStop (scan)")
    print("            StopFailure (API track) | Stop (summary)")
    print("Auto: 10 events | streak tracking | trash talk | record after resolving")
    print("Optimization: 3-level search (JSON cache -> sub-index -> full entry)")
    print()
    print("Now go be brainless. I'll remember everything for you.")


if __name__ == "__main__":
    main()
