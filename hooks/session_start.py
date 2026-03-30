#!/usr/bin/env python3
"""
Brainless SessionStart hook.
Fires on every session start — injects brain context into Claude's awareness
and logs session start to session.log.

Install location: ~/.claude/brainless/hooks/session_start.py
Hook config in settings.json:
  "SessionStart": [{ "hooks": [{
    "type": "command",
    "command": "python ~/.claude/brainless/hooks/session_start.py",
    "timeout": 5
  }]}]
"""
import json
import os
import subprocess
import sys
from datetime import datetime

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
SESSION_LOG = os.path.join(HOOKS_DIR, "session.log")
ACTIVITY_LOG = os.path.join(HOOKS_DIR, "activity.log")
SESSION_ERRORS_FILE = os.path.join(HOOKS_DIR, "_session_errors.json")


def get_git_info():
    """Get git branch and repo name."""
    branch = None
    repo_name = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            repo_name = os.path.basename(result.stdout.strip())
    except Exception:
        pass
    return branch, repo_name


def search_project_entries(entries, cwd, repo_name):
    """Search KB entries related to current project/directory."""
    if not entries:
        return []

    # Build search keywords from project context
    project_name = os.path.basename(cwd).lower()
    keywords = {project_name}
    if repo_name:
        keywords.add(repo_name.lower())
    # Add parent dir name (often the project group)
    parent = os.path.basename(os.path.dirname(cwd)).lower()
    if parent and parent not in ("desktop", "home", "users", "documents", "projects"):
        keywords.add(parent)

    matches = []
    for entry in entries:
        score = 0
        # Search in title, tags, solution_hint, id
        searchable = " ".join([
            entry.get("title", ""),
            " ".join(entry.get("tags", [])),
            entry.get("solution_hint", ""),
            entry.get("id", ""),
        ]).lower()

        for kw in keywords:
            if len(kw) >= 3 and kw in searchable:
                score += 5

        # Also check if entry tags match directory components
        cwd_parts = set(
            p.lower() for p in cwd.replace("\\", "/").split("/")
            if len(p) >= 3
        )
        for tag in entry.get("tags", []):
            if tag.lower() in cwd_parts:
                score += 3

        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])
    return matches[:5]


def main():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    cwd = os.getcwd()
    branch, repo_name = get_git_info()

    # Ensure hooks dir exists
    os.makedirs(HOOKS_DIR, exist_ok=True)

    # Reset session tracking files for new session
    try:
        with open(ACTIVITY_LOG, "w", encoding="utf-8") as f:
            f.write(f"# Session started: {timestamp}\n")
    except Exception:
        pass
    try:
        if os.path.exists(SESSION_ERRORS_FILE):
            os.remove(SESSION_ERRORS_FILE)
    except Exception:
        pass

    # Log session start
    try:
        with open(SESSION_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n--- SESSION START: {timestamp} ---\n")
            f.write(f"  CWD: {cwd}\n")
            if repo_name:
                f.write(f"  Repo: {repo_name}\n")
            if branch:
                f.write(f"  Branch: {branch}\n")
    except Exception:
        pass

    # Load cache for context injection
    total = 0
    categories = {}
    entries = []

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        total = cache.get("total", 0)
        entries = cache.get("entries", [])

        for entry in entries:
            cat = entry.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Output context for Claude
    if total == 0:
        print("[BRAINLESS] Brain loaded: empty. Start recording with /brain-dump!")
        return

    # Stats summary
    top_cats = sorted(categories.items(), key=lambda x: -x[1])[:5]
    cat_str = ", ".join(f"{cat}({n})" for cat, n in top_cats)
    print(f"[BRAINLESS] Brain loaded: {total} entries | Top: {cat_str}")

    # Project-aware search: find entries related to current working directory
    project_matches = search_project_entries(entries, cwd, repo_name)
    if project_matches:
        proj_label = repo_name or os.path.basename(cwd)
        print(f"[BRAINLESS] Known issues for '{proj_label}':")
        for _score, entry in project_matches:
            title = entry.get("title", "?")
            hint = entry.get("solution_hint", "")
            entry_path = os.path.join(BRAINLESS_DIR, entry["id"] + ".md")
            print(f"  - {title}")
            if hint:
                print(f"    Fix: {hint}")
            print(f"    File: {entry_path}")
    else:
        # No project matches — show recent entries as fallback
        sorted_entries = sorted(
            entries,
            key=lambda e: e.get("last_hit", "1970-01-01"),
            reverse=True
        )
        recent = sorted_entries[:3]
        if recent:
            print("[BRAINLESS] Recent entries:")
            for entry in recent:
                title = entry.get("title", "?")
                tags = ", ".join(entry.get("tags", [])[:3])
                hits = entry.get("hit_count", 0)
                print(f"  - {title} [{tags}] (recalled {hits}x)")

    # Working directory hint
    if branch:
        proj_label = repo_name or os.path.basename(cwd)
        print(f"[BRAINLESS] Project: {proj_label} (branch: {branch})")


if __name__ == "__main__":
    main()
