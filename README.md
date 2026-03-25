# Brainless — Your External Brain for Claude Code

<p align="center">
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/stargazers"><img src="https://img.shields.io/github/stars/ImCoriander/Claude-Brainless-Skills?style=social" alt="GitHub Stars"></a>
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

### Auto-Search Hook — True Automation

Brainless installs a **PostToolUse hook** in Claude Code's `settings.json`. Every time a Bash command fails (non-zero exit code), the hook automatically searches your knowledge base and injects matching solutions into Claude's context. **No prompt instructions needed — this works even if context is compressed.**

```
Bash fails → Hook fires → _cache.json searched → [BRAINLESS] solution shown → Claude applies fix
```

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
   Error occurs                      CTF challenge solved
        |                                   |
        v                                   v
  [Hook auto-searches brain]         [Auto-Record to Brain]
        |                                   |
   Found match?                      Write entry + update indexes
    /        \                        + cross-reference + _cache.json
  Yes         No
   |           |
Apply fix    Debug normally → Solved? → Auto-Record
```

---

## Install

**Linux / macOS / Git Bash:**
```bash
git clone https://github.com/ImCoriander/Claude-Brainless-Skills.git
cd Claude-Brainless-Skills
bash install.sh
```

**Windows (CMD / PowerShell):**
```cmd
git clone https://github.com/ImCoriander/Claude-Brainless-Skills.git
cd Claude-Brainless-Skills
install.bat
```

**Requirements:**
- Claude Code installed (`~/.claude/` directory exists)
- Python 3 (for auto-search hook)

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
    │   └── bash_error_search.py # Auto-search hook script
    └── <13 category dirs>/      # Category sub-indexes + entries
```

### Why does it modify CLAUDE.md?

Claude Code skills are only loaded when their triggers match. But auto-behaviors (search before fixing, record after resolving) need to be active in **every** conversation. `~/.claude/CLAUDE.md` is the only file **always** loaded into Claude's context — so the installer appends the behavioral rules there.

If you already have a `CLAUDE.md`, the installer **appends** the brainless section without touching your existing content. Re-running the installer updates the section in place.

### Why does it modify settings.json?

The installer adds a **PostToolUse hook** for the Bash tool. This hook runs a Python script that checks `_cache.json` whenever a command fails — providing true automation that doesn't depend on prompt instructions. The installer safely merges the hook into your existing settings without overwriting anything.

---

## Upgrade

Re-running `install.sh` updates the skill, commands, and hook while **preserving your existing knowledge base data**.

---

## Uninstall

**Quick:**
```bash
bash uninstall.sh
```

**Manual — Important: Remove the hook from settings.json FIRST, before deleting files.** Otherwise the hook will fire on every Bash command and produce blocking errors because the script no longer exists.

```bash
# Step 1: Remove hook from settings.json (use Python helper)
python3 -c "
import json
f = open('$HOME/.claude/settings.json', 'r'); s = json.load(f); f.close()
hooks = s.get('hooks', {}).get('PostToolUse', [])
s['hooks']['PostToolUse'] = [h for h in hooks if h.get('matcher') != 'Bash' or not any('bash_error_search' in hk.get('command', '') for hk in h.get('hooks', []))]
f = open('$HOME/.claude/settings.json', 'w'); json.dump(s, f, indent=2, ensure_ascii=False); f.close()
" 2>/dev/null || python -c "
import json
f = open('$HOME/.claude/settings.json', 'r'); s = json.load(f); f.close()
hooks = s.get('hooks', {}).get('PostToolUse', [])
s['hooks']['PostToolUse'] = [h for h in hooks if h.get('matcher') != 'Bash' or not any('bash_error_search' in hk.get('command', '') for hk in h.get('hooks', []))]
f = open('$HOME/.claude/settings.json', 'w'); json.dump(s, f, indent=2, ensure_ascii=False); f.close()
"

# Step 2: Remove the Brainless section from CLAUDE.md
python3 -c "
import re
f = open('$HOME/.claude/CLAUDE.md', 'r'); c = f.read(); f.close()
c = re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)', '', c, flags=re.DOTALL).strip()
f = open('$HOME/.claude/CLAUDE.md', 'w'); f.write(c + '\n'); f.close()
" 2>/dev/null || python -c "
import re
f = open('$HOME/.claude/CLAUDE.md', 'r'); c = f.read(); f.close()
c = re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)', '', c, flags=re.DOTALL).strip()
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
