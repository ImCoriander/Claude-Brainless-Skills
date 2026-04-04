#!/usr/bin/env python3
"""Helper script to inject all brainless hooks into Claude Code settings.json."""
import json
import os
import sys

HOOKS_BASE = "~/.claude/brainless/hooks"

# All hooks brainless needs to register
BRAINLESS_HOOKS = {
    "PreToolUse": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/streak_reminder.py",
                    "timeout": 3,
                    "statusMessage": "Brainless: checking error streak..."
                }
            ]
        }
    ],
    "UserPromptSubmit": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/user_prompt_search.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: pre-searching brain..."
                }
            ]
        }
    ],
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
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/universal_error_search.py",
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
    "PostToolUseFailure": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/universal_error_search.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: checking knowledge base..."
                }
            ]
        }
    ],
    "PostCompact": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/post_compact.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: restoring brain after compaction..."
                }
            ]
        }
    ],
    "CwdChanged": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/cwd_changed.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: loading project context..."
                }
            ]
        }
    ],
    "SubagentStop": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/subagent_stop.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: scanning subagent result..."
                }
            ]
        }
    ],
    "StopFailure": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python {HOOKS_BASE}/stop_failure.py",
                    "timeout": 5,
                    "statusMessage": "Brainless: tracking API failure..."
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
    "universal_error_search",
    "session_start",
    "post_tool_logger",
    "session_end",
    "streak_reminder",
    "user_prompt_search",
    "post_compact",
    "cwd_changed",
    "subagent_stop",
    "stop_failure",
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

    print("    All hooks configured in settings.json (10 events)")
    print("    - PreToolUse: error streak reminder (ALL tools)")
    print("    - UserPromptSubmit: proactive brain search on user message")
    print("    - SessionStart: brain context injection + trash talk")
    print("    - PostToolUse(ALL): universal error search + streak tracking")
    print("    - PostToolUseFailure(ALL): error search for failed tool calls")
    print("    - PostToolUse(Edit|Write): activity logging + file matching")
    print("    - PostCompact: re-inject brain after context compression")
    print("    - CwdChanged: reload brain for new project directory")
    print("    - SubagentStop: scan subagent results for errors")
    print("    - StopFailure: track API errors")
    print("    - Stop: session summary + trash talk")


if __name__ == "__main__":
    main()
