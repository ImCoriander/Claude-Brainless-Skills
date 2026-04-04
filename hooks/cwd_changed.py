#!/usr/bin/env python3
"""
Brainless CwdChanged hook.
Fires when working directory changes — reloads brain context
for the new project, like a mini session_start.

Install location: ~/.claude/brainless/hooks/cwd_changed.py
"""
import json
import os
import subprocess
import sys

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")

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

    new_cwd = data.get("cwd", os.getcwd())

    # Get repo name
    repo_name = None
    try:
        result = subprocess.run(
            ["git", "-C", new_cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            repo_name = os.path.basename(result.stdout.strip())
    except Exception:
        pass

    # Load cache
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    entries = cache.get("entries", [])
    if not entries:
        return

    # Search by new project context
    project_name = (repo_name or os.path.basename(new_cwd)).lower()
    keywords = {project_name}
    parent = os.path.basename(os.path.dirname(new_cwd)).lower()
    if parent and parent not in ("desktop", "home", "users", "documents", "projects"):
        keywords.add(parent)

    cwd_parts = set(
        p.lower() for p in new_cwd.replace("\\", "/").split("/")
        if len(p) >= 3
    )

    matches = []
    for entry in entries:
        score = 0
        searchable = " ".join([
            entry.get("title", ""),
            " ".join(entry.get("tags", [])),
            entry.get("solution_hint", ""),
            entry.get("id", ""),
        ]).lower()

        for kw in keywords:
            if len(kw) >= 3 and kw in searchable:
                score += 5
        for tag in entry.get("tags", []):
            if tag.lower() in cwd_parts:
                score += 3

        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])

    if matches:
        talk = get_line("cwd_changed")
        proj_label = repo_name or os.path.basename(new_cwd)
        print(f"[BRAINLESS] {talk}")
        print(f"[BRAINLESS] Known issues for '{proj_label}':")
        for _score, entry in matches[:5]:
            title = entry.get("title", "?")
            hint = entry.get("solution_hint", "")
            print(f"  - {title}")
            if hint:
                print(f"    Fix: {hint}")


if __name__ == "__main__":
    main()
