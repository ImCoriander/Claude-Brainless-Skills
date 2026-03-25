---
name: brainless
description: "Brainless (没脑子) — ALWAYS ACTIVE. Your external brain. You don't need memory, I remember EVERYTHING for you. A persistent knowledge management system for errors, CTF challenges, reverse engineering, tricks, and tool usage. CRITICAL BEHAVIORAL RULES (enforce even when skill body is not loaded): (1) ON ANY non-zero exit code or unexpected error: IMMEDIATELY invoke /brain-search BEFORE attempting fixes — check if this problem was solved before; (2) AFTER resolving any non-trivial error (not a simple typo): IMMEDIATELY invoke /brain-dump to record the problem and solution BEFORE continuing to the next step — do NOT wait until the task is finished or the user asks; (3) NEVER batch recordings — record each issue individually as it is resolved. Also covers: CTF writeups (pwn/web/crypto/rev/misc), IDA/Ghidra reversing notes, useful tricks, tool techniques. Triggers: '/brain-dump', '/brain-search', '/brain-review', '/brain-cheatsheet', '/brain-stats', 'record this', 'have we seen this', any error/warning output, CTF problem solving, reverse engineering analysis."
---

# Brainless — Your External Brain

> *"You don't need a brain. I remember everything for you."*
> *"你不需要脑子。我帮你全记着。"*

A persistent, categorized knowledge base that records errors, solutions, CTF challenge writeups, reverse engineering notes, useful tricks, and tool techniques. Builds up automatically over time so that previously solved problems are never re-investigated from scratch.

**Philosophy:** Be brainless. Don't waste neurons remembering things that can be recorded. Offload your memory to me and focus on what matters — solving the next problem.

## Storage Location

All records are stored in `~/.claude/brainless/`:
- `INDEX.md` — master index with all entries organized by category
- `_cache.json` — lightweight JSON cache for fast search
- Category subdirectories (see below)
- Each entry is a single `.md` file in its category directory

## Categories

### Development Errors
| Category | Directory | Scope |
|----------|-----------|-------|
| `build` | `build/` | Compilation, linking, build system errors |
| `runtime` | `runtime/` | Crashes, panics, runtime exceptions |
| `config` | `config/` | Configuration, environment, settings issues |
| `network` | `network/` | Connection, timeout, DNS, API errors |
| `dependency` | `dependency/` | Package version conflicts, missing deps |
| `permission` | `permission/` | File/directory/system permission issues |
| `logic` | `logic/` | Business logic bugs, incorrect behavior |

### Security & RE
| Category | Directory | Scope |
|----------|-----------|-------|
| `ctf` | `ctf/` | CTF challenge writeups — pwn, web, crypto, reverse, misc, forensics |
| `reversing` | `reversing/` | IDA/Ghidra analysis notes, deobfuscation, unpacking, anti-debug bypass |
| `exploit` | `exploit/` | Exploit development techniques, shellcode, ROP, heap tricks |

### Knowledge & Techniques
| Category | Directory | Scope |
|----------|-----------|-------|
| `tricks` | `tricks/` | Useful non-obvious techniques worth remembering |
| `tools` | `tools/` | Tool usage tips — IDA, Ghidra, gdb, Wireshark, Burp, etc. |
| `other` | `other/` | Anything that doesn't fit above |

---

## Record Templates

### Template A: Error Record (build/runtime/config/network/dependency/permission/logic)

```markdown
---
title: [Concise error description]
type: error
category: [category]
tags: [tag1, tag2, tag3]
created: [YYYY-MM-DD]
last_hit: [YYYY-MM-DD]
hit_count: 1
severity: [low/medium/high/critical]
related: []
---

## Error Message
\```
[Exact error output]
\```

## Environment
- Project: [project name]
- Toolchain: [compiler/runtime version]
- OS: [operating system]

## Root Cause
[Brief explanation of why this error occurred]

## Solution
[Step-by-step fix]

## Related Files
- `path/to/file:line`

## Notes
[Any additional context, gotchas, or related issues]
```

### Template B: CTF Writeup (ctf)

```markdown
---
title: [Challenge name — CTF competition name]
type: ctf
category: ctf
tags: [pwn/web/crypto/reverse/misc/forensics, difficulty, technique-keywords]
created: [YYYY-MM-DD]
last_hit: [YYYY-MM-DD]
hit_count: 1
difficulty: [easy/medium/hard/insane]
ctf_category: [pwn/web/crypto/reverse/misc/forensics]
solved: [true/false]
related: []
---

## Challenge Description
[Brief challenge description, what was given]

## Initial Analysis
[First observations, what tools were used to examine]

## Wrong Approaches (What Didn't Work)
1. [Approach 1] — why it failed
2. [Approach 2] — why it failed

## Solution
[Step-by-step solution that worked]

## Key Insight
[The critical "aha" moment — the non-obvious realization that led to the solve]

## Tools Used
- [tool1]: [how it was used]
- [tool2]: [how it was used]

## Flag
\```
[flag if applicable]
\```

## Lessons Learned
[What to remember for next time — patterns, techniques, gotchas]

## References
- [links to relevant resources, similar challenges]
```

### Template C: Reversing Note (reversing)

```markdown
---
title: [Concise description of the RE challenge/technique]
type: reversing
category: reversing
tags: [ida/ghidra, technique, binary-type, arch]
created: [YYYY-MM-DD]
last_hit: [YYYY-MM-DD]
hit_count: 1
target: [binary name or type]
arch: [x86/x64/arm/arm64/mips]
related: []
---

## Target
- Binary: [name/type]
- Protection: [packer, obfuscation, anti-debug methods]
- Architecture: [x86/x64/arm/...]

## Problem
[What was confusing or blocking analysis]

## Analysis Process
[Step-by-step analysis — what was examined, in what order]

## Key Findings
[Important structures, algorithms, patterns discovered]

## Solution / Technique
[How the problem was resolved — specific IDA/Ghidra operations, scripts, etc.]

## IDA/Ghidra Notes
- [Specific operations, scripts, or plugins used]
- [Struct definitions, type assignments that helped]

## Patterns to Recognize
[Signatures or patterns that identify similar problems in the future]

## Notes
[Additional context]
```

### Template D: Exploit Technique (exploit)

```markdown
---
title: [Exploit technique name]
type: exploit
category: exploit
tags: [pwn, technique-type, protection-bypass]
created: [YYYY-MM-DD]
last_hit: [YYYY-MM-DD]
hit_count: 1
difficulty: [easy/medium/hard]
related: []
---

## Technique
[Name and brief description]

## Prerequisites
[What conditions must be met — vulnerable function, leak primitive, etc.]

## Protection Bypasses
[What mitigations this bypasses — ASLR, NX, canary, PIE, etc.]

## Step-by-Step
1. [Step 1]
2. [Step 2]
...

## Code Snippet
\```python
[Exploit template / key snippet]
\```

## Gotchas
[Common mistakes, alignment issues, version-specific details]

## References
- [Links to papers, blog posts, similar exploits]
```

### Template E: Trick / Technique (tricks)

```markdown
---
title: [Concise trick description]
type: trick
category: tricks
tags: [domain, language, tool]
created: [YYYY-MM-DD]
last_hit: [YYYY-MM-DD]
hit_count: 1
related: []
---

## What
[What this trick does]

## When to Use
[Situation where this trick is useful]

## How
[Step-by-step or code snippet]

## Why It Works
[Brief explanation of the underlying mechanism]

## Notes
[Caveats, alternatives, related tricks]
```

### Template F: Tool Usage (tools)

```markdown
---
title: [Tool name — specific technique]
type: tool
category: tools
tags: [tool-name, use-case]
created: [YYYY-MM-DD]
last_hit: [YYYY-MM-DD]
hit_count: 1
tool: [tool name]
related: []
---

## Tool
[Tool name and version]

## Use Case
[When you'd need this]

## Command / Steps
\```bash
[Exact commands or steps]
\```

## Expected Output
[What to expect]

## Tips
[Non-obvious flags, options, or workflow details]

## Notes
[Gotchas, alternatives]
```

---

## Modes of Operation

### Mode 1: Brain Dump (`/brain-dump`)

Triggered when:
- User says: `/brain-dump`, "record this", "log this"
- AI resolves a non-trivial error (auto-record, see Mode 3)
- User finishes a CTF challenge or RE analysis

**Recording workflow:**

1. **Determine entry type** from context:
   - Command failed → Error record (Template A)
   - CTF challenge → CTF writeup (Template B)
   - IDA/Ghidra analysis → Reversing note (Template C)
   - Exploit technique → Exploit record (Template D)
   - Useful technique/trick → Trick (Template E)
   - Tool usage tip → Tool usage (Template F)

2. **Classify** into the appropriate category

3. **Assign tags** — free-form keywords relevant to the entry

4. **Check for existing entries** — search _cache.json and grep for similar entries. If a similar one exists, UPDATE it instead of creating a duplicate

5. **Generate slug filename** — lowercase, hyphen-separated, descriptive

6. **Write the file** using the appropriate template

7. **Scan for cross-references** — if the new entry references techniques, tools, or errors from other entries, add their filenames to the `related: []` frontmatter field, and add a back-reference in those entries too

8. **Update all indexes** (in this order):
   a. **`_cache.json`** — add entry to `entries[]`, add tags to `tags_index`, increment `total`, update `updated` date
   b. **`<category>/_index.md`** — add one-line entry to the sub-index
   c. **`INDEX.md`** — increment the count for the category, update total

9. **Confirm to user** — show what was recorded

### Mode 2: Brain Search (`/brain-search`) — 3-Level Strategy

Triggered when:
- User says: `/brain-search`, "have we seen this", "search kb"
- AI encounters an error (auto-search, see Mode 4)
- Encountering a CTF challenge similar to a previous one

**3-Level search strategy (from cheapest to most expensive):**

#### Level 1: JSON Cache (~50 tokens)
Read `~/.claude/brainless/_cache.json` and search:
- Match keywords against `title`, `summary`, `tags` fields in `entries[]`
- Use `tags_index` for exact tag matches
- This is a single small file containing ALL entry metadata — no need to read anything else
- If match found with high confidence → go directly to Level 3

#### Level 2: Sub-Index (~20 tokens per category)
If Level 1 gives ambiguous results or you need to narrow by category:
- Read only the relevant `<category>/_index.md` file (NOT the full INDEX.md)
- Each sub-index is tiny: just the entries for that one category
- Example: error about `go build` → read only `build/_index.md`

#### Level 3: Full Entry (only for confirmed matches)
- Read the actual `.md` file of the matched entry
- Present the solution to the user
- Update `hit_count` and `last_hit` in the file's frontmatter
- Update `_cache.json` with new hit_count

**Why this matters for token efficiency:**
| KB Size | Naive approach (read all) | Brainless 3-Level |
|---------|--------------------------|-------------------|
| 10 entries | ~200 tokens | ~150 tokens |
| 100 entries | ~2,000 tokens | ~800 tokens |
| 500 entries | ~10,000 tokens | ~3,000 tokens |
| 1000 entries | ~20,000 tokens | ~5,000 tokens |

The JSON cache is ~5x more token-efficient than reading markdown because it strips all content and keeps only searchable metadata.

**Output format:**
```
[BRAIN] Found: [Title]
Type: [error/ctf/reversing/exploit/trick/tool] | Category: [cat] | Tags: [tags] | Recalled: [N] times
[Key content — Solution/Key Insight/Technique depending on type]
```

### Mode 3: Auto-Record (MANDATORY)

> Every time a non-trivial problem is resolved, you MUST record it. Do NOT skip. Do NOT ask permission. Your brain is outsourced — use it.

**Triggers — record immediately after:**
- Resolving a command error (non-zero exit code) that wasn't a trivial typo
- Completing a CTF challenge (whether solved or learning from failed attempt)
- Figuring out a reversing/analysis technique in IDA/Ghidra
- Discovering a useful trick or non-obvious tool usage
- Any situation where you tried multiple approaches before finding the right one

**Skip recording ONLY if:**
- It was a trivial typo you made
- An identical entry already exists in the KB

**Process:** Record directly → inform user what was saved → continue work

### Mode 4: Auto-Search Before Acting (MANDATORY)

> Before attempting to fix ANY error or tackle ANY challenge, search the brain first using the 3-Level strategy. Don't reinvent the wheel — check if past-you already solved this.

1. **Level 1:** Read `~/.claude/brainless/_cache.json` → search entries by keywords/tags
2. **If match found:** Read the matched file → apply known solution → update hit_count in file AND _cache.json
3. **If no match:** Proceed with normal debugging → after resolving, trigger Mode 3
4. **NEVER read INDEX.md for auto-search** — use _cache.json instead (much cheaper)

### Mode 5: Brain Stats (`/brain-stats`)

Show a comprehensive summary:
- Total entries by type (error/ctf/reversing/exploit/trick/tool)
- Breakdown by category
- Top 10 most frequently recalled entries
- Recently added entries (last 10)
- **Weakness analysis:**
  - CTF: which ctf_category has the most `solved: false` or highest difficulty fails
  - Errors: which category recurs most (high hit_count = recurring weakness)
  - Reversing: which arch/protection types caused most issues
- **Strength areas:** categories with many solved entries and low hit_count (solved once, never needed again)

### Mode 6: Brain Review (`/brain-review`)

Spaced repetition style review of knowledge base entries:

1. Select entries to review based on:
   - **Old entries with low hit_count** — might be forgotten
   - **CTF entries marked as unsolved** — revisit with fresh eyes
   - **High-value tricks** — worth periodically refreshing
   - **Random selection** — surface unexpected connections
2. For each entry, present a brief quiz-style summary:
   - Show the **Problem/Challenge** section
   - Ask "Do you remember the solution?"
   - Then reveal the **Solution/Key Insight**
3. After review, offer to update or archive stale entries

### Mode 7: Brain Cheatsheet (`/brain-cheatsheet`)

Auto-generate condensed cheat sheets from accumulated entries:

```
/brain-cheatsheet [category]
```

**Examples:**
- `/brain-cheatsheet ctf` → CTF techniques cheat sheet grouped by category (pwn/web/crypto/rev)
- `/brain-cheatsheet reversing` → RE cheat sheet (common patterns, IDA shortcuts, anti-debug bypasses)
- `/brain-cheatsheet tools` → Tool quick reference
- `/brain-cheatsheet build` → Common build error fixes
- `/brain-cheatsheet all` → Full knowledge base summary

**Cheat sheet format:**
```markdown
# [Category] Cheat Sheet
> Auto-generated from Brainless on [date]. [N] entries.

## [Sub-group 1]
| Problem/Technique | Quick Solution | Tags |
|-------------------|---------------|------|
| [title] | [one-line solution] | [tags] |

## [Sub-group 2]
...
```

Save generated cheat sheets to `~/.claude/brainless/_cheatsheets/[category].md`

---

## Cross-Reference System

Entries can reference each other via the `related: []` frontmatter field:

```yaml
related: [ctf/pwn-stack-overflow-2024.md, tricks/rop-chain-gadget-finder.md]
```

**When recording a new entry:**
1. Scan existing entries for overlapping tags/topics
2. If related entries exist, add cross-references in both directions
3. When displaying an entry, show "Related entries:" at the bottom

**When searching:**
- If a match is found, also show its related entries as "See also:"

---

## Important Guidelines

- **Be aggressive about recording** — a rich brain is infinitely more useful than an empty one
- **Use the right template** — CTF writeups need different structure than build errors
- **Record failed attempts** — for CTF, "what didn't work" is as valuable as the solution
- **Keep solutions actionable** — someone reading should be able to apply it directly
- **Update, don't duplicate** — if a similar entry exists, enrich it
- **Cross-reference actively** — connections between entries multiply their value
- **Use consistent slugs** — `lowercase-hyphen-separated.md`
- **Preserve INDEX.md structure** — always update when adding/modifying entries
- **Tag generously** — more tags = better searchability
