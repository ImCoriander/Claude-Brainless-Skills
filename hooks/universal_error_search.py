#!/usr/bin/env python3
"""
Brainless universal error search hook — Enhanced with streak tracking.
Runs on BOTH PostToolUse and PostToolUseFailure events for ALL tools.

Features:
- Detects errors from ANY tool type (Bash, Edit, Write, LSP, Agent, etc.)
- Searches _cache.json for known solutions
- Tracks consecutive error streak in _error_streak.json
- Resets streak on successful tool use (no error detected)
- Escalates messaging when streak >= 2

Key insight: PostToolUseFailure hook stdout is NOT injected into Claude's
conversation context. So when running under PostToolUseFailure, we write
results to a pending file. The next PostToolUse hook invocation picks up
and outputs the pending results (where stdout IS visible to Claude).
"""
import sys
import json
import re
import os
from datetime import datetime

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "brainless", "hooks"))
try:
    from trash_talk import get_line
except ImportError:
    def get_line(cat, **kw):
        return ""
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")
SESSION_ERRORS_FILE = os.path.join(HOOKS_DIR, "_session_errors.json")
PENDING_OUTPUT_FILE = os.path.join(HOOKS_DIR, "_pending_brainless_output.txt")
STREAK_FILE = os.path.join(HOOKS_DIR, "_error_streak.json")

# Patterns that indicate an error in tool output
ERROR_PATTERNS = [
    r"(?i)error[:\s]",
    r"(?i)failed",
    r"(?i)exception",
    r"(?i)traceback",
    r"(?i)panic:",
    r"(?i)fatal:",
    r"(?i)ENOENT",
    r"(?i)permission denied",
    r"(?i)not found",
    r"(?i)cannot find",
    r"(?i)no such file",
    r"(?i)syntax error",
    r"(?i)undefined reference",
    r"(?i)segmentation fault",
    r"(?i)compilation failed",
    r"(?i)build failed",
    r"(?i)command not found",
    r"(?i)module not found",
    r"(?i)import error",
    r"(?i)type error",
    r"(?i)value error",
    r"(?i)key error",
    r"(?i)attribute error",
    r"(?i)name error",
    r"(?i)runtime error",
    r"(?i)overflow",
    r"(?i)stack trace",
    r"(?i)assertion failed",
    r"(?i)abort",
    r"(?i)rejected",
    r"(?i)timed? ?out",
    r"(?i)connection refused",
    r"(?i)access denied",
    r"(?i)unauthorized",
]

# Tools that are "investigation" — their output containing "error" is NOT an error.
# These tools read/search code that naturally contains error-related keywords.
# Only PostToolUseFailure (the tool itself failing) should trigger for these.
INVESTIGATION_TOOLS = {
    "Read", "Grep", "Glob", "WebSearch", "WebFetch",
    "LSP",       # LSP responses may contain error-related symbols
    "Skill",     # Skill content often mentions errors
    "TaskGet", "TaskList", "TaskOutput",
}

# Tools that are "action" — success means real progress, resets error streak.
# Investigation tools succeeding does NOT mean the problem is resolved.
ACTION_TOOLS = {
    "Bash", "Edit", "Write", "NotebookEdit", "Agent",
}

# False positives to exclude — patterns that look like errors but aren't
FALSE_POSITIVE_PATTERNS = [
    r"(?i)error_pattern",       # our own cache field
    r"(?i)error_search",        # our own hook name
    r"(?i)error.md",            # our own template files
    r"(?i)no errors? found",
    r"(?i)0 errors?",
    r"(?i)fixed.*error",
    r"(?i)resolved.*error",
    r"(?i)error.*handling",
    r"(?i)error.*handler",
    r"(?i)on_error",
    r"(?i)if.*error",
    r"(?i)catch.*error",
]


def is_false_positive(text):
    """Check if the error detection is a false positive."""
    for pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


# ─── Streak management ──────────────────────────────────────────────
def load_streak():
    try:
        with open(STREAK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"count": 0, "errors": [], "last_reset": ""}


def save_streak(streak):
    try:
        os.makedirs(HOOKS_DIR, exist_ok=True)
        with open(STREAK_FILE, "w", encoding="utf-8") as f:
            json.dump(streak, f, ensure_ascii=False)
    except Exception:
        pass


def increment_streak(tool_name, error_snippet):
    """Increment error streak and return new count."""
    streak = load_streak()
    streak["count"] = streak.get("count", 0) + 1
    errors = streak.get("errors", [])
    errors.append({
        "tool": tool_name,
        "snippet": error_snippet[:200],
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    # Keep last 10 errors
    streak["errors"] = errors[-10:]
    save_streak(streak)
    return streak["count"]


def reset_streak():
    """Reset error streak on successful tool use."""
    streak = load_streak()
    if streak.get("count", 0) > 0:
        streak["count"] = 0
        streak["errors"] = []
        streak["last_reset"] = datetime.now().isoformat()
        save_streak(streak)


# ─── Error detection ─────────────────────────────────────────────────
def detect_error(data):
    """
    Detect if a tool response indicates an error.
    Handles PostToolUse (has tool_response) and
    PostToolUseFailure (has error field, no tool_response).
    Returns (is_error: bool, error_text: str, context: str, tool_name: str)
    """
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Normalize tool_input
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except Exception:
            tool_input = {"raw": tool_input}

    # PostToolUseFailure: error is in "error" field, no tool_response
    # This means the TOOL ITSELF failed — always detect, even for investigation tools
    hook_event = data.get("hook_event_name", "")
    if hook_event == "PostToolUseFailure":
        error_text = str(data.get("error", ""))
        if error_text:
            context = f"Tool: {tool_name}"
            if isinstance(tool_input, dict):
                command = tool_input.get("command", tool_input.get("file_path", ""))
                if command:
                    context = f"Command: {command}" if tool_name == "Bash" else f"File: {command}"
            return True, error_text, context, tool_name

        return False, "", "", tool_name

    # Investigation tools: their OUTPUT containing "error" is normal (reading code,
    # searching logs). Only detect errors when the tool itself fails (above).
    if tool_name in INVESTIGATION_TOOLS:
        return False, "", "", tool_name

    tool_response = data.get("tool_response", data.get("response", {}))

    # Normalize tool_response
    if isinstance(tool_response, str):
        try:
            tool_response = json.loads(tool_response)
        except Exception:
            tool_response = {"output": tool_response}

    # --- Bash tool: check exit code or error content ---
    if tool_name == "Bash":
        exit_code = None
        output_text = ""

        if isinstance(tool_response, dict):
            exit_code = tool_response.get("exitCode",
                        tool_response.get("exit_code"))
            stdout = str(tool_response.get("stdout", ""))
            stderr = str(tool_response.get("stderr", ""))
            output_text = stdout + "\n" + stderr if stderr else stdout
            if not output_text.strip():
                output_text = str(tool_response.get("output", ""))
        elif isinstance(tool_response, str):
            output_text = tool_response

        # Try to find exit code in text
        if exit_code is None and output_text:
            for pattern in [r"Exit code (\d+)", r"exit code[:\s]+(\d+)",
                            r"exit[:\s]+(\d+)", r"exited with (\d+)"]:
                m = re.search(pattern, output_text, re.IGNORECASE)
                if m:
                    exit_code = int(m.group(1))
                    break

        if exit_code and exit_code != 0:
            command = ""
            if isinstance(tool_input, dict):
                command = tool_input.get("command", "")
            return True, output_text, f"Command: {command}", tool_name

        return False, "", "", tool_name

    # --- Edit/Write tool: check for error in response ---
    if tool_name in ("Edit", "Write"):
        resp_str = json.dumps(tool_response) if isinstance(tool_response, dict) else str(tool_response)

        if any(kw in resp_str.lower() for kw in ["error", "failed", "not found", "no such file"]):
            if not is_false_positive(resp_str):
                file_path = ""
                if isinstance(tool_input, dict):
                    file_path = tool_input.get("file_path", tool_input.get("filePath", ""))
                return True, resp_str[:500], f"File: {file_path}", tool_name

        return False, "", "", tool_name

    # --- LSP tool: check for error ---
    if tool_name == "LSP":
        resp_str = json.dumps(tool_response, default=str) if isinstance(tool_response, dict) else str(tool_response)
        if any(kw in resp_str.lower() for kw in ["error", "failed", "not found", "no server"]):
            if not is_false_positive(resp_str):
                operation = tool_input.get("operation", "") if isinstance(tool_input, dict) else ""
                file_path = tool_input.get("filePath", "") if isinstance(tool_input, dict) else ""
                return True, resp_str[:500], f"LSP {operation}: {file_path}", tool_name
        return False, "", "", tool_name

    # --- Agent tool: check for failure indication ---
    if tool_name == "Agent":
        resp_str = json.dumps(tool_response, default=str) if isinstance(tool_response, dict) else str(tool_response)
        if any(kw in resp_str.lower() for kw in ["error", "failed", "exception", "could not"]):
            if not is_false_positive(resp_str):
                desc = tool_input.get("description", "") if isinstance(tool_input, dict) else ""
                return True, resp_str[:500], f"Agent: {desc}", tool_name
        return False, "", "", tool_name

    # --- Generic tool: pattern-match for errors in response ---
    resp_str = ""
    if isinstance(tool_response, dict):
        resp_str = json.dumps(tool_response, default=str)
    elif isinstance(tool_response, str):
        resp_str = tool_response

    if not resp_str:
        return False, "", "", tool_name

    for pattern in ERROR_PATTERNS:
        if re.search(pattern, resp_str):
            if is_false_positive(resp_str):
                return False, "", "", tool_name
            context_info = f"Tool: {tool_name}"
            if isinstance(tool_input, dict):
                for key in ["command", "file_path", "filePath", "pattern", "url"]:
                    if key in tool_input:
                        context_info += f", {key}: {tool_input[key]}"
                        break
            return True, resp_str[:500], context_info, tool_name

    return False, "", "", tool_name


# ─── Cache search ────────────────────────────────────────────────────
def search_cache(error_text, context_text):
    """Search the brainless cache for matching entries."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    entries = cache.get("entries", [])
    if not entries:
        return []

    search_text = f"{context_text} {error_text}".lower()
    matches = []

    for entry in entries:
        score = 0

        pattern = entry.get("error_pattern", "")
        if pattern:
            try:
                if re.search(pattern, error_text, re.IGNORECASE):
                    score += 10
            except re.error:
                if pattern.lower() in search_text:
                    score += 10

        for tag in entry.get("tags", []):
            if tag.lower() in search_text:
                score += 2

        title_words = entry.get("title", "").lower().split()
        for word in title_words:
            if len(word) > 3 and word in search_text:
                score += 1

        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])
    return matches[:3]


def track_unrecorded_error(context, error_text):
    """Track errors with no known solution for session summary."""
    try:
        os.makedirs(HOOKS_DIR, exist_ok=True)
        errors = []
        if os.path.exists(SESSION_ERRORS_FILE):
            with open(SESSION_ERRORS_FILE, "r", encoding="utf-8") as f:
                errors = json.load(f)

        error_line = error_text.strip().split("\n")[0][:200] if error_text else ""
        errors.append({
            "context": context[:200],
            "error_snippet": error_line,
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        errors = errors[-50:]

        with open(SESSION_ERRORS_FILE, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False)
    except Exception:
        pass


# ─── Output building ─────────────────────────────────────────────────
def build_output(matches, context, error_text, streak_count):
    """Build brainless output lines with streak-aware escalation."""
    lines = []
    if matches:
        talk = get_line("error_matched")
        lines.append(f"[BRAINLESS] {talk}")
        for _score, entry in matches:
            entry_path = os.path.join(BRAINLESS_DIR, entry["id"] + ".md")
            lines.append(f"  - {entry['title']}")
            lines.append(f"    Solution: {entry.get('solution_hint', 'See full entry')}")
            lines.append(f"    Full entry: {entry_path}")
        lines.append("[BRAINLESS] Apply the known solution above.")
    else:
        track_unrecorded_error(context, error_text)
        talk = get_line("error_no_match")
        lines.append(f"[BRAINLESS] {talk}")
        lines.append(f"[BRAINLESS] Error context: {context}")
        lines.append(f"[BRAINLESS] Error snippet: {error_text[:150]}")
        lines.append("[BRAINLESS] DIRECTIVE: After resolving this error, you MUST invoke /brain-dump to record the problem and solution.")

    # ── Streak escalation ──
    if streak_count >= 4:
        lines.append("")
        lines.append(f"[BRAINLESS] !!!CRITICAL!!! STREAK = {streak_count} consecutive errors!")
        lines.append("[BRAINLESS] You are stuck in a failure loop. CHANGE YOUR APPROACH.")
        lines.append("[BRAINLESS] MANDATORY: Run /brain-search NOW before ANY other action.")
        lines.append("[BRAINLESS] If you resolved a previous error without recording, run /brain-dump FIRST.")
    elif streak_count >= 2:
        lines.append("")
        lines.append(f"[BRAINLESS] WARNING: {streak_count} consecutive errors — you may be going in circles.")
        lines.append("[BRAINLESS] Consider: /brain-search to check for known solutions.")
        lines.append("[BRAINLESS] Remember: /brain-dump after resolving to prevent re-investigation.")

    return "\n".join(lines)


def flush_pending():
    """Output any pending results from a previous PostToolUseFailure run."""
    if os.path.exists(PENDING_OUTPUT_FILE):
        try:
            with open(PENDING_OUTPUT_FILE, "r", encoding="utf-8") as f:
                pending = f.read().strip()
            os.remove(PENDING_OUTPUT_FILE)
            if pending:
                print(pending)
        except Exception:
            pass


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return

    hook_event = data.get("hook_event_name", "")

    # On any PostToolUse, first flush pending output from prior failures
    if hook_event == "PostToolUse":
        flush_pending()

    is_error, error_text, context, tool_name = detect_error(data)

    if not is_error:
        # Only reset streak on ACTION tool success (= real progress).
        # Investigation tools (Read, Grep, Glob...) succeeding does NOT
        # mean the error is resolved — Claude might still be debugging.
        if tool_name in ACTION_TOOLS:
            reset_streak()
        return

    # Error detected — increment streak and search
    error_snippet = error_text.strip().split("\n")[0][:200] if error_text else context
    streak_count = increment_streak(tool_name, error_snippet)

    matches = search_cache(error_text, context)
    output = build_output(matches, context, error_text, streak_count)

    if hook_event == "PostToolUseFailure":
        # stdout not visible — append to pending file for next PostToolUse
        # (append mode so consecutive failures don't overwrite each other)
        try:
            os.makedirs(HOOKS_DIR, exist_ok=True)
            with open(PENDING_OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(output + "\n")
        except Exception:
            pass
        # Also try stderr — may be visible in some Claude Code versions
        print(output, file=sys.stderr)
    else:
        # PostToolUse — stdout is visible to Claude
        print(output)


if __name__ == "__main__":
    main()
