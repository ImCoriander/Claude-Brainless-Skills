#!/usr/bin/env python3
"""
Brainless — Cross-platform Uninstaller
Works on Linux, macOS, Windows (CMD/PowerShell/Git Bash)
"""
import os
import sys
import re
import json
import shutil


def main():
    print("Uninstalling Brainless...")

    claude_dir = os.path.join(os.path.expanduser("~"), ".claude")
    settings_file = os.path.join(claude_dir, "settings.json")
    claude_md = os.path.join(claude_dir, "CLAUDE.md")

    # [1/3] Remove all brainless hooks from settings.json FIRST
    print("[1/3] Removing hooks from settings.json...")
    if os.path.isfile(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except (json.JSONDecodeError, Exception):
            settings = {}

        markers = [
            "bash_error_search", "universal_error_search",
            "session_start", "post_tool_logger", "session_end",
            "streak_reminder", "user_prompt_search", "post_compact",
            "cwd_changed", "subagent_stop", "stop_failure",
        ]
        hooks = settings.get("hooks", {})
        modified = False

        for event in ["PreToolUse", "UserPromptSubmit", "SessionStart",
                      "PostToolUse", "PostToolUseFailure", "PostCompact",
                      "CwdChanged", "SubagentStop", "StopFailure", "Stop"]:
            entries = hooks.get(event, [])
            cleaned = []
            for entry in entries:
                is_brainless = False
                for hook in entry.get("hooks", []):
                    cmd = hook.get("command", "")
                    if any(m in cmd for m in markers):
                        is_brainless = True
                        break
                if not is_brainless:
                    cleaned.append(entry)
            if len(cleaned) != len(entries):
                modified = True
            if cleaned:
                hooks[event] = cleaned
            elif event in hooks:
                del hooks[event]
                modified = True

        if modified:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print("    All hooks removed")
        else:
            print("    No hooks found, skipping")
    else:
        print("    settings.json not found, skipping")

    # [2/3] Remove Brainless section from CLAUDE.md
    print("[2/3] Cleaning CLAUDE.md...")
    if os.path.isfile(claude_md):
        with open(claude_md, "r", encoding="utf-8") as f:
            content = f.read()

        if "Brainless Auto-Behaviors" in content:
            pattern = r"\n*## Brainless Auto-Behaviors \(MANDATORY[^)]*\).*?(?=\n## (?!Brainless)|$)"
            content = re.sub(pattern, "", content, flags=re.DOTALL).strip()
            with open(claude_md, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            print("    CLAUDE.md cleaned")
        else:
            print("    No brainless rules found, skipping")
    else:
        print("    CLAUDE.md not found, skipping")

    # [3/3] Remove files
    print("[3/3] Removing files...")

    skill_dir = os.path.join(claude_dir, "skills", "brainless")
    if os.path.isdir(skill_dir):
        shutil.rmtree(skill_dir)

    for cmd in ["brain-dump", "brain-search", "brain-stats", "brain-review",
                "brain-cheatsheet", "brain-rebuild"]:
        cmd_file = os.path.join(claude_dir, "commands", f"{cmd}.md")
        if os.path.isfile(cmd_file):
            os.remove(cmd_file)

    brainless_dir = os.path.join(claude_dir, "brainless")
    if os.path.isdir(brainless_dir):
        shutil.rmtree(brainless_dir)

    print("    Files removed")
    print()
    print("Brainless uninstalled. Your brain is on your own now.")


if __name__ == "__main__":
    main()
