---
type: reference
audience: claude
updated: 2026-07-03
tags: [efficiency, workflow]
summary: "sportking-specific operating rules — build gates, shared libs, MCP servers, deploy. Pairs with the general claude-efficiency rules."
---

# sportking project rules

The project-specific half of [[claude-efficiency]] (general, lives in
`~/.ai`, symlinked here). Everything below is about *this* project.
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
6. **Consult heavily.** User re-mandated (2026-07-03): be *very* careful with
   BaseLinker calls — when any doubt exists about intent or blast radius, ask
   before calling, even for reads that look unusual.

## VPS safety (Hetzner, `ssh sportking`) — user-mandated
There is **no deploy script** — every change is a live edit on the production
server. Hard rules:

1. **Read-only recon freely; changes only with explicit user go-ahead** for the
   specific change, in this conversation.
2. **Backup before any change, and recommend it out loud.** Before touching a
   file: `cp <file> <file>.bak-$(date +%F)` (or a tarball of the dir); before DB
   changes: `mysqldump` the affected tables to a dated file. State where the
   backup landed and the exact restore command.
3. **Be specific.** Show the exact commands (and diffs where applicable) that
   will run, old → new, before running them. One change at a time; verify the
   site still responds after each.
4. **Claude's access:** dedicated key `~/.ssh/sportking_claude` (the user's own
   `id_ed25519` is passphrase-protected and stays theirs).

## Reuse before writing (shared libs)
- (list the project's shared helpers here — duplicated logic is the main bloat source)

## Verification
- Quick check: (typecheck command)
- Real gate: (build/test command + gotchas)

## Deploy & git
- Vault repo: Claude commits, never pushes. Code repo: commits stay the user's
  unless asked.
- (deploy runbook pointers)
