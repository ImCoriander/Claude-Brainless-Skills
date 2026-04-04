#!/usr/bin/env python3
"""
Brainless PreToolUse hook — Consecutive Error Streak Reminder.
Fires BEFORE every tool call. If the error streak count >= 2,
injects an escalating warning into Claude's context to force
it to search the brain / change approach / record solutions.

Install location: ~/.claude/brainless/hooks/streak_reminder.py
Hook config in settings.json:
  "PreToolUse": [{ "hooks": [{
    "type": "command",
    "command": "python ~/.claude/brainless/hooks/streak_reminder.py",
    "timeout": 3
  }]}]
"""
import json
import os
import sys

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
sys.path.insert(0, os.path.join(BRAINLESS_DIR, "hooks"))
try:
    from trash_talk import get_line
except ImportError:
    def get_line(cat, **kw):
        return ""
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
STREAK_FILE = os.path.join(HOOKS_DIR, "_error_streak.json")


def load_streak():
    """Load the current error streak state."""
    try:
        with open(STREAK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"count": 0, "errors": [], "last_reset": ""}


def main():
    streak = load_streak()
    count = streak.get("count", 0)

    if count < 2:
        return

    errors = streak.get("errors", [])

    # Build error context summary
    error_lines = []
    for err in errors[-5:]:
        tool = err.get("tool", "?")
        snippet = err.get("snippet", "")[:120]
        error_lines.append(f"    [{tool}] {snippet}")
    error_context = "\n".join(error_lines)

    if count >= 4:
        # CRITICAL escalation
        talk = get_line("streak_critical", n=count)
        print(f"[BRAINLESS] {talk}")
        print("[BRAINLESS] STOP IMMEDIATELY. Do NOT repeat the same approach.")
        print("[BRAINLESS] MANDATORY ACTIONS:")
        print("[BRAINLESS]   1. Run /brain-search with keywords from these errors")
        print("[BRAINLESS]   2. READ the actual error messages below")
        print("[BRAINLESS]   3. CHANGE your approach — what you're doing is NOT working")
        print(f"[BRAINLESS] Error trail ({count}x):")
        print(error_context)
        print("[BRAINLESS] If you already RESOLVED an error along the way, run /brain-dump NOW.")
        print("[BRAINLESS] DO NOT PROCEED without searching the brain first.")
    elif count >= 2:
        # WARNING escalation
        talk = get_line("streak_warning", n=count)
        print(f"[BRAINLESS] {talk}")
        print("[BRAINLESS] STOP and think before your next action.")
        print(f"[BRAINLESS] Recent errors:")
        print(error_context)
        print("[BRAINLESS] DIRECTIVE: Run /brain-search with keywords from these errors BEFORE trying again.")
        print("[BRAINLESS] If you already resolved something, run /brain-dump NOW to record it.")


if __name__ == "__main__":
    main()
