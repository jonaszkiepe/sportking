---
type: reference
audience: claude
updated: 2026-07-06
summary: Session-start orientation — auto-loaded via the repo-root CLAUDE.md symlink; the ONLY CLAUDE.md; routes to MAP + project-rules and inlines the always-on rules.
---

# CLAUDE.md (root — symlinked from `../../CLAUDE.md`)

Guidance for Claude Code at the **repo root**. Start sessions here — it's the
directory the shared memories and this file are wired to (start in a subdir and
they won't load). This is the **only** CLAUDE.md for sportking — no per-subdir
pointers; the few always-on rules live at the bottom of this note.

## Read the library first — pull, don't preload

Full docs live in **`library/`** (Obsidian vault). Don't preload it; **pull only
what the task needs**, starting at the index:

- **`library/MAP.md`** — the index. Read this first; open only what a task needs.
- Scan every note's purpose at once: `grep -rh "^summary:" library --include=*.md`
- **`library/_meta/project-rules.md`** — sportking operating rules (build gates,
  shared libs, MCP, deploy). Read before non-trivial work.

## Vault workflow (any session that touches the library)

- Begin replies that used the vault with `(pulled: <notes>)`.
- Write back as you go: a dated `…/log.md` line, bump touched notes' `updated:`,
  keep `MAP.md` / `_moc` in sync when notes are created or deleted.
- **Commit the vault unprompted; never push.** Code-repo commits stay the user's.
- Full loop: `library/_meta/workflow.md`. General working rules arrive as
  auto-loaded memories.

## Critical always-on rules (details in the library)

- (the few rules that must never be missed — keep this list short)

**Env:** before editing `~/ai-workflow`, take the `LOCK` (concurrent sessions) — `env-write-lock` memory.
