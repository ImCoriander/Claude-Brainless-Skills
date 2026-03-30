#!/usr/bin/env python3
"""Helper script to inject all brainless hooks into Claude Code settings.json."""
import json
import os
import sys

HOOKS_BASE = "~/.claude/brainless/hooks"

# All hooks brainless needs to register
BRAINLESS_HOOKS = {
    "SessionStart": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/session_start.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: loading brain context..."
                }
            ]
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/bash_error_search.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: checking knowledge base..."
                }
            ]
        },
        {
            "matcher": "Edit|Write",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/post_tool_logger.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: logging activity..."
                }
            ]
        }
    ],
    "Stop": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/session_end.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: saving session summary..."
                }
            ]
        }
    ]
}

# Markers to identify brainless-owned hooks
BRAINLESS_MARKERS = [
    "bash_error_search",
    "session_start",
    "post_tool_logger",
    "session_end",
]


def is_brainless_hook_entry(hook_entry):
    """Check if a hook entry belongs to brainless."""
    for hook in hook_entry.get("hooks", []):
        cmd = hook.get("command", "")
        for marker in BRAINLESS_MARKERS:
            if marker in cmd:
                return True
    return False


def main():
    claude_dir = os.path.join(os.path.expanduser("~"), ".claude")
    settings_file = os.path.join(claude_dir, "settings.json")

    # Load existing settings
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    hooks = settings.setdefault("hooks", {})

    # For each event type, remove old brainless hooks and add new ones
    for event_type, new_entries in BRAINLESS_HOOKS.items():
        existing = hooks.get(event_type, [])

        # Remove any existing brainless hooks
        cleaned = [h for h in existing if not is_brainless_hook_entry(h)]

        # Add new brainless hooks
        cleaned.extend(new_entries)
        hooks[event_type] = cleaned

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print("    All hooks configured in settings.json")
    print("    - SessionStart: brain context injection")
    print("    - PostToolUse(Bash): error auto-search")
    print("    - PostToolUse(Edit|Write): activity logging + file matching")
    print("    - Stop: session summary")


if __name__ == "__main__":
    main()
