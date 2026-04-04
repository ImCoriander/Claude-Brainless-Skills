#!/usr/bin/env python3
"""
Brainless PostCompact hook.
Fires after context compression — re-injects critical brain context
that Claude may have lost during compaction.

This is the most important recovery mechanism: when Claude's context
gets compressed, it loses memory of errors, solutions, and streak state.
This hook restores that awareness.

Install location: ~/.claude/brainless/hooks/post_compact.py
"""
import json
import os
import subprocess
import sys

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
STREAK_FILE = os.path.join(HOOKS_DIR, "_error_streak.json")
SESSION_ERRORS_FILE = os.path.join(HOOKS_DIR, "_session_errors.json")

sys.path.insert(0, HOOKS_DIR)
try:
    from trash_talk import get_line
except ImportError:
    def get_line(cat, **kw):
        return ""


def get_git_info():
    """Get repo name for project-aware search."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            return os.path.basename(result.stdout.strip())
    except Exception:
        pass
    return None


def main():
    talk = get_line("compact")
    print(f"[BRAINLESS] {talk}")

    cwd = os.getcwd()
    repo_name = get_git_info()

    # 1. Re-inject brain stats
    total = 0
    entries = []
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        total = cache.get("total", 0)
        entries = cache.get("entries", [])
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if total > 0:
        print(f"[BRAINLESS] Brain status: {total} entries available.")

    # 2. Re-inject project-specific entries
    if entries:
        project_name = (repo_name or os.path.basename(cwd)).lower()
        cwd_parts = set(
            p.lower() for p in cwd.replace("\\", "/").split("/")
            if len(p) >= 3
        )

        proj_matches = []
        for entry in entries:
            score = 0
            searchable = " ".join([
                entry.get("title", ""),
                " ".join(entry.get("tags", [])),
                entry.get("solution_hint", ""),
                entry.get("id", ""),
            ]).lower()

            if project_name and len(project_name) >= 3 and project_name in searchable:
                score += 5
            for tag in entry.get("tags", []):
                if tag.lower() in cwd_parts:
                    score += 3

            if score > 0:
                proj_matches.append((score, entry))

        proj_matches.sort(key=lambda x: -x[0])
        if proj_matches:
            print(f"[BRAINLESS] Known issues for '{repo_name or os.path.basename(cwd)}':")
            for _score, entry in proj_matches[:3]:
                title = entry.get("title", "?")
                hint = entry.get("solution_hint", "")
                print(f"  - {title}")
                if hint:
                    print(f"    Fix: {hint}")

    # 3. Re-inject streak state
    try:
        with open(STREAK_FILE, "r", encoding="utf-8") as f:
            streak = json.load(f)
        count = streak.get("count", 0)
        if count >= 2:
            errors = streak.get("errors", [])
            print(f"[BRAINLESS] WARNING: Error streak = {count} (still active!)")
            for err in errors[-3:]:
                print(f"  - [{err.get('tool', '?')}] {err.get('snippet', '')[:100]}")
            print("[BRAINLESS] Run /brain-search before continuing.")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 4. Re-inject unrecorded errors count
    try:
        if os.path.exists(SESSION_ERRORS_FILE):
            with open(SESSION_ERRORS_FILE, "r", encoding="utf-8") as f:
                errors = json.load(f)
            if errors:
                print(f"[BRAINLESS] Reminder: {len(errors)} unrecorded error(s) this session — /brain-dump when resolved.")
    except (json.JSONDecodeError, Exception):
        pass

    # 5. Re-inject behavioral rules
    print("[BRAINLESS] RULES REMINDER: (1) /brain-search on errors (2) /brain-dump after resolving (3) NEVER skip recording")


if __name__ == "__main__":
    main()
