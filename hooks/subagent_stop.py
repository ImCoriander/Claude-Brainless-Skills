#!/usr/bin/env python3
"""
Brainless SubagentStop hook.
Fires when a subagent finishes — scans result for errors
and searches brain for relevant knowledge.

Install location: ~/.claude/brainless/hooks/subagent_stop.py
"""
import json
import os
import re
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

ERROR_KEYWORDS = [
    r"(?i)error[:\s]", r"(?i)failed", r"(?i)exception",
    r"(?i)traceback", r"(?i)panic:", r"(?i)fatal:",
    r"(?i)not found", r"(?i)permission denied",
]


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return

    agent_type = data.get("agent_type", "unknown")
    last_msg = data.get("last_assistant_message", "")

    if not last_msg:
        return

    # Check if subagent result contains errors
    has_error = False
    error_snippet = ""
    for pattern in ERROR_KEYWORDS:
        m = re.search(pattern, last_msg)
        if m:
            has_error = True
            # Extract context around the match
            start = max(0, m.start() - 20)
            end = min(len(last_msg), m.end() + 80)
            error_snippet = last_msg[start:end].strip()
            break

    if not has_error:
        return

    # Search brain for the error
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    entries = cache.get("entries", [])
    search_text = error_snippet.lower()
    matches = []

    for entry in entries:
        score = 0
        ep = entry.get("error_pattern", "")
        if ep:
            try:
                if re.search(ep, error_snippet, re.IGNORECASE):
                    score += 10
            except re.error:
                if ep.lower() in search_text:
                    score += 10
        for tag in entry.get("tags", []):
            if tag.lower() in search_text:
                score += 2
        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])

    talk = get_line("subagent_stop")
    print(f"[BRAINLESS] {talk}")

    if matches:
        print(f"[BRAINLESS] Subagent ({agent_type}) result has errors — brain has solutions:")
        for _score, entry in matches[:2]:
            entry_path = os.path.join(BRAINLESS_DIR, entry["id"] + ".md")
            print(f"  - {entry['title']}")
            print(f"    Solution: {entry.get('solution_hint', 'See full entry')}")
            print(f"    File: {entry_path}")
    else:
        print(f"[BRAINLESS] Subagent ({agent_type}) hit an error: {error_snippet[:120]}")
        print("[BRAINLESS] No known solution — record with /brain-dump after resolving.")


if __name__ == "__main__":
    main()
