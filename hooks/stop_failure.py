#!/usr/bin/env python3
"""
Brainless StopFailure hook.
Fires when Claude's turn ends due to API error (rate limit, auth, billing).
Tracks these as operational issues.

Install location: ~/.claude/brainless/hooks/stop_failure.py
"""
import json
import os
import sys
from datetime import datetime

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
SESSION_ERRORS_FILE = os.path.join(HOOKS_DIR, "_session_errors.json")

sys.path.insert(0, HOOKS_DIR)
try:
    from trash_talk import get_line
except ImportError:
    def get_line(cat, **kw):
        return ""


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return

    error_type = data.get("error_type", "unknown")

    # Track to session errors
    try:
        os.makedirs(HOOKS_DIR, exist_ok=True)
        errors = []
        if os.path.exists(SESSION_ERRORS_FILE):
            with open(SESSION_ERRORS_FILE, "r", encoding="utf-8") as f:
                errors = json.load(f)

        errors.append({
            "context": f"API StopFailure: {error_type}",
            "error_snippet": f"Claude turn ended due to: {error_type}",
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        errors = errors[-50:]

        with open(SESSION_ERRORS_FILE, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False)
    except Exception:
        pass

    talk = get_line("stop_failure")
    print(f"[BRAINLESS] {talk}")
    print(f"[BRAINLESS] API error type: {error_type}")


if __name__ == "__main__":
    main()
