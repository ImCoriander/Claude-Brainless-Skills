#!/usr/bin/env python3
"""
Brainless auto-search hook for Claude Code.
Triggered PostToolUse on Bash — searches _cache.json when exit code is non-zero.
Outputs matching entries so Claude sees them in context.

Install location: ~/.claude/brainless/hooks/bash_error_search.py
Hook config in settings.json:
  "PostToolUse": [{ "matcher": "Bash", "hooks": [{
    "type": "command",
    "command": "python ~/.claude/brainless/hooks/bash_error_search.py",
    "timeout": 5
  }]}]
"""
import sys
import json
import re
import os
from datetime import datetime

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
SESSION_ERRORS_FILE = os.path.join(HOOKS_DIR, "_session_errors.json")


def main():
    # Read JSON from stdin (Claude Code passes tool_input + tool_response)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return

    # Extract tool response — handle multiple possible formats
    tool_response = data.get("tool_response", data.get("response", {}))
    if isinstance(tool_response, str):
        try:
            tool_response = json.loads(tool_response)
        except (json.JSONDecodeError, Exception):
            tool_response = {"output": tool_response}

    # Detect non-zero exit code
    exit_code = None
    output_text = ""

    if isinstance(tool_response, dict):
        exit_code = tool_response.get("exitCode", tool_response.get("exit_code"))
        output_text = str(tool_response.get("output", tool_response.get("stderr", tool_response.get("stdout", ""))))
    elif isinstance(tool_response, str):
        output_text = tool_response

    # Try to detect "Exit code N" pattern in text if not found in struct
    if exit_code is None and output_text:
        m = re.search(r"Exit code (\d+)", output_text)
        if m:
            exit_code = int(m.group(1))

    # Extract command from tool_input for context
    tool_input = data.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, Exception):
            tool_input = {"command": tool_input}

    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")

    # Only trigger on non-zero exit codes
    if exit_code is None or exit_code == 0:
        return

    # Load cache
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    entries = cache.get("entries", [])
    if not entries:
        return

    # Search for matches
    search_text = f"{command} {output_text}".lower()
    matches = []

    for entry in entries:
        score = 0
        # Check error_pattern (regex or plain text)
        pattern = entry.get("error_pattern", "")
        if pattern:
            try:
                if re.search(pattern, output_text, re.IGNORECASE):
                    score += 10
            except re.error:
                if pattern.lower() in search_text:
                    score += 10

        # Check tags
        for tag in entry.get("tags", []):
            if tag.lower() in search_text:
                score += 2

        # Check title keywords
        title_words = entry.get("title", "").lower().split()
        for word in title_words:
            if len(word) > 3 and word in search_text:
                score += 1

        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])

    if matches:
        print("[BRAINLESS] Found matching knowledge for this error:")
        for _score, entry in matches[:3]:
            entry_path = os.path.join(BRAINLESS_DIR, entry["id"] + ".md")
            print(f"  - {entry['title']}")
            print(f"    Solution: {entry.get('solution_hint', 'See full entry')}")
            print(f"    File: {entry_path}")
        print("[BRAINLESS] Read the entry file(s) above for full solution details.")
    else:
        # No match found — track as unrecorded error for session summary
        _track_unrecorded_error(command, output_text, exit_code)


def _track_unrecorded_error(command, output_text, exit_code):
    """Record unmatched errors so session_end.py can remind about /brain-dump."""
    try:
        os.makedirs(HOOKS_DIR, exist_ok=True)
        errors = []
        if os.path.exists(SESSION_ERRORS_FILE):
            with open(SESSION_ERRORS_FILE, "r", encoding="utf-8") as f:
                errors = json.load(f)

        # Keep a short summary (avoid bloating the file)
        error_line = output_text.strip().split("\n")[0][:200] if output_text else ""
        errors.append({
            "command": command[:200],
            "error_snippet": error_line,
            "exit_code": exit_code,
            "time": datetime.now().strftime("%H:%M:%S"),
        })

        # Cap at 50 errors per session
        errors = errors[-50:]

        with open(SESSION_ERRORS_FILE, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False)
    except Exception:
        pass


if __name__ == "__main__":
    main()
