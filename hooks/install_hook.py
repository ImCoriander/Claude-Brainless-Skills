#!/usr/bin/env python3
"""Helper script to inject brainless hook into Claude Code settings.json."""
import json
import os
import sys

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
    post_hooks = hooks.setdefault("PostToolUse", [])

    brainless_hook = {
        "type": "command",
        "command": "python ~/.claude/brainless/hooks/bash_error_search.py",
        "timeout": 5,
        "statusMessage": "Brainless: checking knowledge base..."
    }

    # Check if Bash matcher already exists
    bash_hook_exists = False
    for h in post_hooks:
        if h.get("matcher") == "Bash":
            hook_list = h.setdefault("hooks", [])
            already = any("bash_error_search" in hk.get("command", "") for hk in hook_list)
            if not already:
                hook_list.append(brainless_hook)
            bash_hook_exists = True
            break

    if not bash_hook_exists:
        post_hooks.append({
            "matcher": "Bash",
            "hooks": [brainless_hook]
        })

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print("    Hook configured in settings.json")

if __name__ == "__main__":
    main()
