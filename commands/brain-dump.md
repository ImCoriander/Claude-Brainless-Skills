Record the current error, CTF solution, reversing finding, exploit technique, trick, or tool usage to the Brainless knowledge base at `~/.claude/brainless/`. Use the appropriate template from the brainless skill.

IMPORTANT: This command should be invoked AUTOMATICALLY (not just manually) — immediately after resolving any non-trivial error, without waiting for the user to ask. If you just fixed a non-zero exit code, environment issue, build failure, or any unexpected problem, call /brain-dump NOW before moving on.

**Full recording workflow (ALL steps are MANDATORY — do NOT skip any):**

1. **Classify** — determine entry type and category from context
2. **Check duplicates** — read `~/.claude/brainless/_cache.json`, search for similar entries by tags/title. If duplicate found, UPDATE existing entry instead of creating new one
3. **Write the entry file** — `~/.claude/brainless/<category>/<slug>.md` using the appropriate template
4. **UPDATE `_cache.json`** — this is CRITICAL and must NOT be skipped:
   - Add new entry to `entries[]` array with fields: `id`, `title`, `category`, `tags`, `error_pattern`, `solution_hint`, `hit_count`, `last_hit`
   - Add all tags to `tags_index` (each tag maps to a list of entry IDs)
   - Increment `total` count
   - Update `updated` date to today
   - **If you skip this step, auto-search will NOT find the entry!**
5. **Update `<category>/_index.md`** — add one-line entry to the sub-index table
6. **Update `INDEX.md`** — increment the count for the category and total
7. **Confirm** — show the user what was recorded

**Common mistake:** Writing the .md file but forgetting to update `_cache.json`. This makes the entry invisible to auto-search. If you realize you forgot, run `/brain-rebuild` to fix indexes.
