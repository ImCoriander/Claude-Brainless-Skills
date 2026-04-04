#!/usr/bin/env python3
"""
Brainless UserPromptSubmit hook.
Fires when the user sends a message — proactively searches brain
for relevant knowledge BEFORE Claude starts working.

Install location: ~/.claude/brainless/hooks/user_prompt_search.py
Hook config in settings.json:
  "UserPromptSubmit": [{ "hooks": [{
    "type": "command",
    "command": "python ~/.claude/brainless/hooks/user_prompt_search.py",
    "timeout": 5
  }]}]
"""
import json
import os
import re
import sys

BRAINLESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "brainless")
CACHE_FILE = os.path.join(BRAINLESS_DIR, "_cache.json")
HOOKS_DIR = os.path.join(BRAINLESS_DIR, "hooks")

# Import trash talk
sys.path.insert(0, HOOKS_DIR)
try:
    from trash_talk import get_line
except ImportError:
    def get_line(cat, **kw):
        return ""


def extract_keywords(prompt):
    """Extract meaningful keywords from user prompt."""
    # Remove common stop words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "about", "like",
        "through", "after", "over", "between", "out", "against", "during",
        "before", "after", "above", "below", "up", "down", "and", "but",
        "or", "nor", "not", "so", "yet", "both", "either", "neither",
        "this", "that", "these", "those", "it", "its", "my", "your",
        "his", "her", "our", "their", "what", "which", "who", "whom",
        "how", "when", "where", "why", "all", "each", "every", "some",
        "any", "no", "other", "just", "also", "very", "much", "more",
        "me", "you", "he", "she", "we", "they", "i", "im",
        # Chinese stop words
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
        "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
        "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它",
        "吗", "吧", "呢", "啊", "哦", "嗯", "把", "被", "让", "给",
        "帮", "帮我", "请", "能", "可以", "怎么", "什么", "为什么",
        "那个", "这个", "现在", "然后", "所以", "但是", "如果",
    }

    # Split on whitespace and punctuation
    words = re.findall(r'[a-zA-Z_][\w.-]*|[\u4e00-\u9fff]+', prompt.lower())
    keywords = [w for w in words if w not in stop_words and len(w) >= 2]
    return keywords[:10]  # Cap at 10 keywords


def search_brain(keywords):
    """Search brain cache by keywords."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    entries = cache.get("entries", [])
    if not entries or not keywords:
        return []

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
            if kw in searchable:
                score += 3
            # Partial match for longer keywords
            if len(kw) >= 4:
                for tag in entry.get("tags", []):
                    if kw in tag.lower() or tag.lower() in kw:
                        score += 2

        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda x: -x[0])
    return matches[:3]


def main():
    # Read stdin JSON
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return

    prompt = data.get("prompt", "")
    if not prompt or len(prompt) < 5:
        return

    keywords = extract_keywords(prompt)
    if not keywords:
        return

    matches = search_brain(keywords)

    if matches:
        talk = get_line("user_prompt")
        print(f"[BRAINLESS] {talk}")
        print(f"[BRAINLESS] Brain has relevant knowledge for this task:")
        for _score, entry in matches:
            entry_path = os.path.join(BRAINLESS_DIR, entry["id"] + ".md")
            title = entry.get("title", "?")
            hint = entry.get("solution_hint", "")
            print(f"  - {title}")
            if hint:
                print(f"    Hint: {hint}")
            print(f"    File: {entry_path}")
        print("[BRAINLESS] Read the entry file(s) above before starting work.")


if __name__ == "__main__":
    main()
