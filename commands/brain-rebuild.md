Rebuild all Brainless indexes from existing entry files at `~/.claude/brainless/`. This fixes any desync between entry files and `_cache.json`/`_index.md` indexes.

**Workflow:**

1. Scan all category directories (`build/`, `runtime/`, `config/`, `network/`, `dependency/`, `permission/`, `logic/`, `ctf/`, `reversing/`, `exploit/`, `tricks/`, `tools/`, `other/`) for `.md` files (excluding `_index.md`)
2. For each entry file, read its YAML frontmatter to extract: `title`, `category`, `tags`, `hit_count`, `last_hit`, `severity`/`difficulty`
3. Rebuild `_cache.json` from scratch:
   - Set `total` to the number of entries found
   - Set `updated` to today's date
   - Populate `entries[]` with: `id` (category/filename without .md), `title`, `category`, `tags`, `error_pattern` (extract from "Error Message" code block if present), `solution_hint` (first line of "Solution" section), `hit_count`, `last_hit`
   - Rebuild `tags_index` mapping each tag to its entry IDs
4. Rebuild each `<category>/_index.md` with a table of entries in that category
5. Rebuild `INDEX.md` with correct counts per category and total
6. Report: how many entries found, any orphaned/broken entries, before vs after counts

Use this command when:
- `_cache.json` is empty but entry files exist
- Search isn't finding entries that you know exist
- After manual edits to entry files
- As a periodic health check
