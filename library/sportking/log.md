---
project: sportking
type: log
audience: both
updated: 2026-07-03
summary: Append-only activity log — every piece of work, one dated line, newest first.
---

# sportking — log

Every completed piece of work gets one line (newest first). Big features also live
on [[board]]; this is the full history.

## 2026-07-03
- BaseLinker API token saved to `.env` (`baselinker_api`, git-ignored) and verified read-only: inventory "Sportking" id 4002 (pl, warehouse bl_5086) → [[architecture]].
- Public-site audit: sportking.pl live (Apache/Debian, LE cert fresh, ~1.1s TTFB), BERG/EXIT/Didakites/Gepetto catalog visible → [[architecture]]. Revival plan: audit-first; BaseLinker+Allegro access granted, token pending.
- Added live-system safety rules (read-only default, backup-before-write, dry-run confirm) → [[_meta/project-rules]].
- Captured baseline project context from the user (PrestaShop on Hetzner, BaseLinker, Allegro, BERG/EXIT partners) → [[_moc]], new [[architecture]] draft.
- Project bootstrapped from `~/ai-workflow` (vault skeleton, _meta symlinks, memory wiring).
