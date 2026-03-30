#!/usr/bin/env python3
"""
Brainless PostToolUse hook for Edit|Write tools.
Logs activity and checks if modified files relate to known knowledge base entries.

Install location: ~/.claude/brainless/hooks/post_tool_logger.py
Hook config in settings.json:
  "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [{
    "type": "command",
    "command": "python ~/.claude/brainless/hooks/post_tool_logger.py",
    "timeout": 5
  }]}]
"""
import json
import os
import sys
from datetime import datetime

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
ACTIVITY_LOG = os.path.join(HOOKS_DIR, "activity.log")
MAX_LOG_SIZE = 1 * 1024 * 1024  # 1MB


def rotate_log():
    """Rotate activity.log if it exceeds MAX_LOG_SIZE."""
    try:
        if os.path.exists(ACTIVITY_LOG) and os.path.getsize(ACTIVITY_LOG) > MAX_LOG_SIZE:
            rotated = ACTIVITY_LOG + ".1"
            if os.path.exists(rotated):
                os.remove(rotated)
            os.rename(ACTIVITY_LOG, rotated)
    except Exception:
        pass


def log_activity(tool_name, file_path):
    """Append a one-line log entry."""
    try:
        os.makedirs(HOOKS_DIR, exist_ok=True)
        rotate_log()
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {tool_name}: {file_path}\n"
        with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def search_file_in_cache(file_path, cache):
    """Check if a file path matches any known entry in the knowledge base."""
    if not file_path or not cache:
        return []

    entries = cache.get("entries", [])
    if not entries:
        return []

    # Normalize path for matching
    file_basename = os.path.basename(file_path)
    file_lower = file_path.replace("\\", "/").lower()

    matches = []
    for entry in entries:
        score = 0

        # Check if filename appears in entry title
        title = entry.get("title", "").lower()
        if file_basename.lower() in title:
            score += 5

        # Check tags for file-related keywords
        for tag in entry.get("tags", []):
            tag_l = tag.lower()
            if file_basename.lower().rstrip(".py").rstrip(".go").rstrip(".lua") in tag_l:
                score += 3
            # Check file extension match (e.g., tag "go" matches .go files)
            ext = os.path.splitext(file_path)[1].lstrip(".")
            if ext and tag_l == ext:
                score += 1

        # Check solution_hint for file path references
        hint = entry.get("solution_hint", "").lower()
        if file_basename.lower() in hint:
            score += 4

        if score >= 3:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])
    return matches[:2]


def main():
    # Read JSON from stdin
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return

    # Extract tool info
    tool_name = data.get("tool_name", "unknown")
    tool_input = data.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, Exception):
            tool_input = {}

    # Get file path from tool input
    file_path = ""
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path", tool_input.get("filePath", ""))

    # Log the activity
    log_activity(tool_name, file_path or "(no path)")

    if not file_path:
        return

    # Search cache for related entries
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    matches = search_file_in_cache(file_path, cache)
    if matches:
        print(f"[BRAINLESS] File '{os.path.basename(file_path)}' relates to known entries:")
        for _score, entry in matches:
            title = entry.get("title", "?")
            hint = entry.get("solution_hint", "")
            entry_path = os.path.join(BRAINLESS_DIR, entry["id"] + ".md")
            print(f"  - {title}")
            if hint:
                print(f"    Hint: {hint}")
            print(f"    File: {entry_path}")


if __name__ == "__main__":
    main()
