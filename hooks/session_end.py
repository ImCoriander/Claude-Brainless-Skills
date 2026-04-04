#!/usr/bin/env python3
"""
Brainless Stop (SessionEnd) hook.
Fires when a session ends — writes session summary to session.log.

Install location: ~/.claude/brainless/hooks/session_end.py
Hook config in settings.json:
  "Stop": [{ "hooks": [{
    "type": "command",
    "command": "python ~/.claude/brainless/hooks/session_end.py",
    "timeout": 5
  }]}]
"""
import json
import os
import re
import sys
from datetime import datetime

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
sys.path.insert(0, os.path.join(BRAINLESS_DIR, "hooks"))
try:
    from trash_talk import get_line
except ImportError:
    def get_line(cat, **kw):
        return ""
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
SESSION_LOG = os.path.join(HOOKS_DIR, "session.log")
ACTIVITY_LOG = os.path.join(HOOKS_DIR, "activity.log")
SESSION_ERRORS_FILE = os.path.join(HOOKS_DIR, "_session_errors.json")


def count_activity():
    """Count tool uses and brain hits from current session's activity log."""
    tool_count = 0
    brain_hits = 0
    try:
        with open(ACTIVITY_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                tool_count += 1
    except FileNotFoundError:
        pass

    # Count brain hits from session log (lines with [BRAINLESS] Found)
    try:
        with open(SESSION_LOG, "r", encoding="utf-8") as f:
            content = f.read()
        # Find the last SESSION START marker
        starts = list(re.finditer(r"--- SESSION START: (.+?) ---", content))
        if starts:
            last_start = starts[-1]
            session_section = content[last_start.start():]
            brain_hits = session_section.count("[BRAINLESS]")
    except FileNotFoundError:
        pass

    return tool_count, brain_hits


def get_session_duration():
    """Try to compute session duration from session.log."""
    try:
        with open(SESSION_LOG, "r", encoding="utf-8") as f:
            content = f.read()
        starts = list(re.finditer(r"--- SESSION START: (.+?) ---", content))
        if starts:
            start_str = starts[-1].group(1)
            start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            duration = datetime.now() - start_time
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            return f"{minutes}m{seconds}s"
    except Exception:
        pass
    return "unknown"


def get_unrecorded_errors():
    """Read unrecorded errors tracked by universal_error_search.py."""
    try:
        if os.path.exists(SESSION_ERRORS_FILE):
            with open(SESSION_ERRORS_FILE, "r", encoding="utf-8") as f:
                errors = json.load(f)
            return errors if isinstance(errors, list) else []
    except (json.JSONDecodeError, Exception):
        pass
    return []


def cleanup_session_files():
    """Remove temporary session tracking files."""
    try:
        if os.path.exists(SESSION_ERRORS_FILE):
            os.remove(SESSION_ERRORS_FILE)
    except Exception:
        pass


def main():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    duration = get_session_duration()
    tool_count, brain_hits = count_activity()
    unrecorded = get_unrecorded_errors()

    os.makedirs(HOOKS_DIR, exist_ok=True)

    # Write summary to session log
    try:
        with open(SESSION_LOG, "a", encoding="utf-8") as f:
            f.write(f"--- SESSION END: {timestamp} ---\n")
            f.write(f"  Duration: {duration}\n")
            f.write(f"  Tool uses: {tool_count}\n")
            f.write(f"  Brain hits: {brain_hits}\n")
            f.write(f"  Unrecorded errors: {len(unrecorded)}\n")
            if unrecorded:
                for err in unrecorded[:10]:
                    f.write(f"    - [{err.get('time', '?')}] exit={err.get('exit_code', '?')}: {err.get('error_snippet', '')[:100]}\n")
            f.write("\n")
    except Exception:
        pass

    # Print brief summary to stdout
    talk = get_line("session_end")
    print(f"[BRAINLESS] {talk}")
    print(f"[BRAINLESS] Session ended | Duration: {duration} | Tools: {tool_count} | Brain hits: {brain_hits}")

    # Alert about unrecorded errors — nudge to /brain-dump
    if unrecorded:
        print(f"[BRAINLESS] WARNING: {len(unrecorded)} error(s) had NO match in knowledge base!")
        print("[BRAINLESS] These errors were new — consider running /brain-dump to record them:")
        for err in unrecorded[:5]:
            cmd_short = err.get("command", "?")[:80]
            snippet = err.get("error_snippet", "")[:100]
            print(f"  - `{cmd_short}` → {snippet}")
        if len(unrecorded) > 5:
            print(f"  ... and {len(unrecorded) - 5} more")

    # Cleanup temp files
    cleanup_session_files()


if __name__ == "__main__":
    main()
