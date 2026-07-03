---
type: reference
audience: claude
updated: 2026-07-03
tags: [efficiency, workflow]
summary: "sportking-specific operating rules — build gates, shared libs, MCP servers, deploy. Pairs with the general claude-efficiency rules."
---

# sportking project rules

The project-specific half of [[claude-efficiency]] (general, lives in
`~/ai-workflow`, symlinked here). Everything below is about *this* project.
Fill sections as facts are learned; delete ones that never apply.

## Environment
- MCP servers: (none yet)
- Hooks currently live: (none yet)
- Cheap vault scan: `grep -rh "^summary:" "/home/jonasz/sportking/library" --include=*.md`.

## Live-system safety (BaseLinker / Allegro / shop) — user-mandated
The user granted BaseLinker API + Allegro access on the condition of backup logic
so "no mistakes happen from bad prompts or misunderstanding". Hard rules:

1. **Read-only by default.** Any API session starts and stays read-only unless the
   user explicitly asked for a change *in this conversation*.
2. **Backup before write.** Before ANY write (product, price, stock, listing,
   order status): export the current state of every affected record to
   `library/sportking/backups/<date>-<what>.json` and commit the vault, so every
   change has a restorable before-image.
3. **Dry-run list first.** Show the user the exact records + fields that will
   change (old → new) and get a yes before executing. Never bulk-write from an
   inferred instruction; ambiguity = ask, not act.
4. **No deletes / no order-state changes** (cancel, refund, ship) without the user
   naming the specific record.
5. **Log every write** in [[sportking/log]] with what changed and where the backup is.

## Reuse before writing (shared libs)
- (list the project's shared helpers here — duplicated logic is the main bloat source)

## Verification
- Quick check: (typecheck command)
- Real gate: (build/test command + gotchas)

## Deploy & git
- Vault repo: Claude commits, never pushes. Code repo: commits stay the user's
  unless asked.
- (deploy runbook pointers)
