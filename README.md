# Brainless — Your External Brain for Claude Code

<p align="center">
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/stargazers"><img src="https://img.shields.io/github/stars/ImCoriander/Claude-Brainless-Skills?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/releases"><img src="https://img.shields.io/github/downloads/ImCoriander/Claude-Brainless-Skills/total" alt="Downloads"></a>
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ImCoriander/Claude-Brainless-Skills" alt="License"></a>
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/issues"><img src="https://img.shields.io/github/issues/ImCoriander/Claude-Brainless-Skills" alt="Issues"></a>
</p>

> **[中文文档 / Chinese Documentation](./README_CN.md)**

---

```
  ____            _       _
 | __ ) _ __ __ _(_)_ __ | | ___  ___ ___
 |  _ \| '__/ _` | | '_ \| |/ _ \/ __/ __|
 | |_) | | | (_| | | | | | |  __/\__ \__ \
 |____/|_|  \__,_|_|_| |_|_|\___||___/___/

 "You don't need a brain. I remember everything for you."
```

---

## What is Brainless?

**Brainless** is a persistent knowledge management skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). It automatically records every error you encounter, every CTF challenge you solve, every reversing trick you discover — and recalls them instantly when you need them again.

**Stop re-debugging. Stop re-googling. Be brainless.**

---

## Why Brainless?

Every developer has experienced this:

- You hit an error. You spend 30 minutes debugging. You fix it.
- Three weeks later, the same error appears. You've forgotten how you fixed it.
- You Google it again. You try the same wrong approaches again. Another 30 minutes gone.

**Brainless breaks this cycle.** It gives Claude Code a persistent, structured memory that survives across sessions. Your AI assistant remembers what you've already solved — so you never waste time on the same problem twice.

---

## Features

### Lifecycle Hooks — True Automation

Brainless installs **10 hooks** across **10 Claude Code events**, covering the entire session lifecycle. These are real automations in `settings.json` — **no prompt instructions needed, works even if context is compressed.** All hooks include witty trash-talk one-liners (毒舌吐槽风).

| Hook Event | Script | What It Does |
|-----------|--------|-------------|
| **UserPromptSubmit** | `user_prompt_search.py` | **Proactive brain search** — when user sends a message, extracts keywords and searches brain BEFORE Claude starts working |
| **PreToolUse** (All tools) | `streak_reminder.py` | **Consecutive error escalation** — if 2+ errors in a row, injects WARNING; at 4+, CRITICAL alert forcing approach change |
| **SessionStart** | `session_start.py` | Injects brain context — total entries, project-specific known issues, recent entries, resets error streak |
| **PostToolUse** (All tools) | `universal_error_search.py` | **Universal error detection + streak tracking** — searches KB on errors, tracks streak, resets on action tool success |
| **PostToolUseFailure** (All tools) | `universal_error_search.py` | **Failure detection** — catches tool failures, writes to pending file for next PostToolUse to output |
| **PostToolUse** (Edit\|Write) | `post_tool_logger.py` | Logs file edits, checks if modified files relate to known KB entries |
| **PostCompact** | `post_compact.py` | **Memory restoration** — after context compression, re-injects project entries, streak state, unrecorded errors, and behavioral rules |
| **CwdChanged** | `cwd_changed.py` | **Project context reload** — when switching directories, searches brain for new project's known issues |
| **SubagentStop** | `subagent_stop.py` | **Subagent result scan** — when a subagent finishes, scans result for errors and searches brain |
| **StopFailure** | `stop_failure.py` | **API failure tracking** — records rate limits, auth failures, billing errors to session log |
| **Stop** | `session_end.py` | Session summary (duration, tool count, brain hits) + **alerts about unrecorded errors** |

```
UserPromptSubmit    PreToolUse(ALL)    SessionStart       PostToolUse(ALL)         PostToolUseFailure
     |                   |                 |                    |                        |
     v                   v                 v                    v                        v
 Extract keywords   Read streak        Load cache         1. Flush pending          Write to pending
 Search _cache      count < 2? skip    Search by cwd      2. Error in stdout?       (stdout not visible)
 Inject matches     count >= 2? WARN   Show known issues      |-- Yes → search       streak++
 + trash talk       count >= 4? CRIT   Reset streak           |-- No  → reset streak
                    + trash talk       + trash talk            + trash talk

PostCompact         CwdChanged         SubagentStop        StopFailure              Stop
     |                   |                  |                   |                      |
     v                   v                  v                   v                      v
 Re-inject brain    Search by new cwd  Scan result for     Track to session       Read _session_errors
 Project entries    Show known issues  errors → search     _errors.json           Unrecorded → warn
 Streak state       + trash talk       brain for matches   + trash talk           Log session summary
 Rules reminder                        + trash talk                               + trash talk
 + trash talk
```

> **v5 upgrade:** Added 5 new hooks (UserPromptSubmit, PostCompact, CwdChanged, SubagentStop, StopFailure) + trash talk system with witty one-liners. UserPromptSubmit pre-searches brain when user types. PostCompact restores brain memory after context compression. Total: 10 events hooked.
>
> **v4 upgrade:** Added `PreToolUse` hook for consecutive error streak tracking. Separated tools into ACTION (Bash/Edit/Write) vs INVESTIGATION (Read/Grep/Glob) — only action tools trigger error detection and streak reset.
>
> **v3 upgrade:** Pending file mechanism for PostToolUseFailure (stdout not visible to Claude).
>
> **v2 upgrade:** Universal error search replacing old Bash-only hook.

### Auto-Record — Zero Manual Effort

Every non-trivial problem you solve gets automatically saved. No commands needed. No manual tagging. Claude detects the resolution, classifies it, and writes a structured entry to your knowledge base — all in the background.

**Triggers automatically after:**
- Resolving any non-zero exit code (build errors, runtime crashes, config issues)
- Completing a CTF challenge (win or lose — failed attempts are valuable too)
- Figuring out a reversing technique in IDA/Ghidra
- Discovering a useful trick or non-obvious tool usage
- Any situation where multiple approaches were tried before finding the right one

### Auto-Search — Check Before You Debug

Before attempting to fix ANY error, Brainless searches the knowledge base first. If past-you already solved this, you get the answer in seconds instead of minutes.

### 13 Categories

| Category | Scope |
|----------|-------|
| `build` | Compilation, linking, build system errors |
| `runtime` | Crashes, panics, runtime exceptions |
| `config` | Configuration, environment, settings issues |
| `network` | Connection, timeout, DNS, API errors |
| `dependency` | Package version conflicts, missing deps |
| `permission` | File/directory/system permission issues |
| `logic` | Business logic bugs, incorrect behavior |
| `ctf` | CTF writeups — pwn, web, crypto, reverse, misc, forensics |
| `reversing` | IDA/Ghidra analysis, deobfuscation, unpacking, anti-debug |
| `exploit` | Exploit dev — shellcode, ROP, heap tricks |
| `tricks` | Useful non-obvious techniques worth remembering |
| `tools` | Tool usage tips — IDA, Ghidra, gdb, Wireshark, Burp, etc. |
| `other` | Everything else |

### 6 Specialized Templates

Each category type has its own optimized record template:

| Template | Used For | Key Fields |
|----------|----------|------------|
| **Error Record** | build/runtime/config/network/dependency/permission/logic | Error message, root cause, environment, step-by-step fix |
| **CTF Writeup** | CTF challenges | Wrong approaches, key insight, flag, lessons learned |
| **Reversing Note** | IDA/Ghidra RE analysis | Target info, protections, analysis process, patterns to recognize |
| **Exploit Technique** | Exploit development | Prerequisites, protection bypasses, code snippet, gotchas |
| **Trick** | Useful techniques | When to use, how, why it works |
| **Tool Usage** | Tool tips | Command/steps, expected output, non-obvious tips |

### 3-Level Token-Efficient Search

Brainless uses a hierarchical search strategy that reads only what's needed:

```
Level 1: _cache.json     →  Search metadata only    (~50 tokens)
Level 2: <cat>/_index.md →  Category sub-index      (~20 tokens)
Level 3: entry.md        →  Full content             (only on match)
```

**Scaling comparison:**

| KB Size | Naive (read all) | Brainless | Savings |
|---------|-----------------|-----------|---------|
| 10 entries | ~200 tokens | ~150 tokens | 25% |
| 100 entries | ~2,000 tokens | ~800 tokens | 60% |
| 500 entries | ~10,000 tokens | ~3,000 tokens | 70% |
| 1000 entries | ~20,000 tokens | ~5,000 tokens | 75% |

**Your knowledge base grows; your token cost barely moves.**

### Cross-Reference System

Entries automatically link to each other via `related: []` fields. When you view one entry, related entries appear as "See also". Knowledge compounds over time — solving one problem helps you find the next.

### Index Rebuild

`/brain-rebuild` scans all entry files and rebuilds `_cache.json` and all `_index.md` files from scratch. Use it when indexes get out of sync, after manual edits, or as a periodic health check.

### Weakness Analysis

`/brain-stats` doesn't just show counts — it analyzes your weak spots:
- Which CTF categories you fail most at
- Which error types keep recurring (high hit_count = recurring weakness)
- Which architectures give you trouble in RE
- Where your strengths are (solved once, never needed again)

### Spaced Repetition Review

`/brain-review` quizzes you on old entries to prevent knowledge decay:
- Old entries with low hit_count (might be forgotten)
- Unsolved CTF challenges worth revisiting
- High-value tricks worth periodically refreshing
- Random selection to surface unexpected connections

### Auto-Generated Cheat Sheets

`/brain-cheatsheet [category]` generates condensed quick-reference sheets from your accumulated knowledge, saved to `~/.claude/brainless/_cheatsheets/`.

### Duplicate Detection

Before writing any new entry, Brainless searches existing records. If a similar entry exists, it updates that entry instead of creating a duplicate. Your knowledge base stays clean.

### Hit Tracking

Every time a past solution is recalled, the entry's `hit_count` increments and `last_hit` updates. This data powers weakness analysis and review prioritization.

---

## Commands

| Command | Description |
|---------|-------------|
| `/brain-dump` | Record an entry to the knowledge base |
| `/brain-search` | Search the knowledge base |
| `/brain-stats` | View stats + weakness analysis |
| `/brain-review` | Spaced repetition review session |
| `/brain-cheatsheet [cat]` | Generate a cheat sheet for a category |
| `/brain-rebuild` | Rebuild all indexes from entry files (fix desync) |

---

## How It Works

```
  Session starts          BEFORE any tool call       AFTER any tool call          Session ends
       |                         |                         |                          |
       v                         v                         v                          v
 [SessionStart Hook]      [PreToolUse Hook]         [PostToolUse Hook]          [Stop Hook]
 Load brain context       Check error streak        Error detected?             Check unrecorded errors
 Show known issues        streak < 2? → silent       /        \                 Remind: /brain-dump
 Reset streak             streak >= 2? → WARN      Yes         No               Log session summary
       |                  streak >= 4? → CRIT        |           |
       v                  "SEARCH THE BRAIN"       Search KB   Reset streak
 Claude starts with                                streak++
 full brain awareness                               |
                                                  Match?
                                                 /      \
                                               Yes      No
                                                |        |
                                           Apply fix   Track + DIRECTIVE:
                                                       → /brain-dump after resolving
```

---

## Install

**All platforms (Linux / macOS / Windows):**
```bash
git clone https://github.com/ImCoriander/Claude-Brainless-Skills.git
cd Claude-Brainless-Skills
python install.py
```


**Requirements:**
- Claude Code installed (`~/.claude/` directory exists)
- Python 3 (for installer and auto-search hooks)

**What gets installed:**

```
~/.claude/
├── CLAUDE.md                    # Auto-behavior rules (appended)
├── settings.json                # Hook config (merged)
├── skills/brainless/SKILL.md    # Core skill definition
├── commands/
│   ├── brain-dump.md            # /brain-dump command
│   ├── brain-search.md          # /brain-search command
│   ├── brain-stats.md           # /brain-stats command
│   ├── brain-review.md          # /brain-review command
│   ├── brain-cheatsheet.md      # /brain-cheatsheet command
│   └── brain-rebuild.md         # /brain-rebuild command
└── brainless/                   # Knowledge base data
    ├── INDEX.md                 # Master index
    ├── _cache.json              # Fast search cache
    ├── hooks/
    │   ├── trash_talk.py               # Shared module — witty one-liners for all hooks
    │   ├── user_prompt_search.py       # UserPromptSubmit — proactive brain search
    │   ├── streak_reminder.py          # PreToolUse(ALL) — consecutive error escalation
    │   ├── session_start.py            # SessionStart — context injection + streak reset
    │   ├── universal_error_search.py   # PostToolUse + PostToolUseFailure(ALL) — error search + streak
    │   ├── post_tool_logger.py         # PostToolUse(Edit|Write) — activity log
    │   ├── post_compact.py             # PostCompact — re-inject brain after compression
    │   ├── cwd_changed.py              # CwdChanged — reload brain for new project
    │   ├── subagent_stop.py            # SubagentStop — scan subagent results
    │   ├── stop_failure.py             # StopFailure — track API errors
    │   └── session_end.py              # Stop — session summary + alerts
    └── <13 category dirs>/      # Category sub-indexes + entries
```

### Why does it modify CLAUDE.md?

Claude Code skills are only loaded when their triggers match. But auto-behaviors (search before fixing, record after resolving) need to be active in **every** conversation. `~/.claude/CLAUDE.md` is the only file **always** loaded into Claude's context — so the installer appends the behavioral rules there.

If you already have a `CLAUDE.md`, the installer **appends** the brainless section without touching your existing content. Re-running the installer updates the section in place.

### Why does it modify settings.json?

The installer registers **10 hooks** across 10 Claude Code events (UserPromptSubmit, PreToolUse, SessionStart, PostToolUse, PostToolUseFailure, PostCompact, CwdChanged, SubagentStop, StopFailure, Stop). These hooks provide true automation independent of prompt instructions — proactive brain search on user input, error streak escalation, context injection, universal error detection, memory restoration after compaction, project-aware context reloading, subagent result scanning, API failure tracking, and session summaries. The installer safely merges hooks into your existing settings without overwriting anything.

---

## Upgrade

Re-running `install.sh` updates the skill, commands, and hook while **preserving your existing knowledge base data**.

---

## Uninstall

**Quick (all platforms):**
```bash
python uninstall.py
```


**Manual — Important: Remove hooks from settings.json FIRST, before deleting files.** Otherwise hooks will fire and produce blocking errors because the scripts no longer exist.

```bash
# Step 1: Remove all brainless hooks from settings.json
python3 -c "
import json
MARKERS = ['bash_error_search', 'universal_error_search', 'session_start', 'post_tool_logger', 'session_end', 'streak_reminder', 'user_prompt_search', 'post_compact', 'cwd_changed', 'subagent_stop', 'stop_failure']
f = open('$HOME/.claude/settings.json', 'r'); s = json.load(f); f.close()
hooks = s.get('hooks', {})
for event in ['PreToolUse', 'UserPromptSubmit', 'SessionStart', 'PostToolUse', 'PostToolUseFailure', 'PostCompact', 'CwdChanged', 'SubagentStop', 'StopFailure', 'Stop']:
    entries = hooks.get(event, [])
    hooks[event] = [h for h in entries if not any(m in hk.get('command', '') for hk in h.get('hooks', []) for m in MARKERS)]
    if not hooks[event]: del hooks[event]
f = open('$HOME/.claude/settings.json', 'w'); json.dump(s, f, indent=2, ensure_ascii=False); f.close()
"

# Step 2: Remove the Brainless section from CLAUDE.md
python3 -c "
import re
f = open('$HOME/.claude/CLAUDE.md', 'r'); c = f.read(); f.close()
c = re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY[^)]*\).*?(?=\n## (?!Brainless)|$)', '', c, flags=re.DOTALL).strip()
f = open('$HOME/.claude/CLAUDE.md', 'w'); f.write(c + '\n'); f.close()
"

# Step 3: Remove files
rm -rf ~/.claude/skills/brainless
rm -rf ~/.claude/commands/brain-*.md
rm -rf ~/.claude/brainless
```

---

## Star History

<a href="https://star-history.com/#ImCoriander/Claude-Brainless-Skills&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ImCoriander/Claude-Brainless-Skills&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ImCoriander/Claude-Brainless-Skills&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ImCoriander/Claude-Brainless-Skills&type=Date" />
 </picture>
</a>

---

## License

MIT — Be brainless, be free.
