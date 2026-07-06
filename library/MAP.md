---
type: moc
audience: both
updated: 2026-07-06
summary: The index — every project and note with a one-line summary. Read this first.
---

# MAP — library index

Read this first; open only what a task needs. See [[_meta/workflow]] for the loop.
Scan every note's purpose at once: `grep -rh "^summary:" "/home/jonasz/sportking/library" --include=*.md`.

## Projects

| Project | Map | Board (plan) | Log (history) | What |
|---|---|---|---|---|
| sportking | [[sportking/_moc]] | [[sportking/board]] | [[sportking/log]] | PrestaShop shop sportking.pl (Hetzner VPS) + BaseLinker + Allegro; reviving a stale local business |

**Board = big features only (the plan). Log = everything (one dated line per work item).**

## Notes

### sportking
- [[sportking/architecture]] — **how it works** (early draft — stack, hosting, integrations; mostly unverified).
- [[sportking/user-board]] — personal kanban for things only the user can act on (separate from [[sportking/board]]).

## Meta
- [[_meta/workflow]] · [[_meta/conventions]] · [[_meta/claude-efficiency]] · [[_meta/prompt-rules]] · [[_meta/suggestions]] · [[_meta/project-rules]]
- General workflow env lives in the **`~/.ai`** repo, symlinked into `_meta/` + `_templates/`. Project-specific rules: [[_meta/project-rules]] (real file).
- `_meta/memories/` — Claude's auto-loaded memories (shared across projects; general facts only — see scope-routing).
