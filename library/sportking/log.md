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
- User restructured: photo export now lives at `products/photos/<EAN>/` + `products/manifest.csv` (was `allegro-photos/`; old manual `photos/` deleted). Refs updated in [[_moc]], [[architecture]], [[board]]; manifest.csv now git-tracked, photos ignored.
- Plan pivot recorded: full catalog reconstruction — presta products discarded, only sklep_veloking listings stay, warehouse scanner count → EAN list incoming as source of truth → [[_moc]] (key decision), [[architecture]] (banner), [[board]] (cards).
- VPS access live (dedicated key). Read-only recon: PrestaShop 9.0.3 at /home/henrik/sportking (colleague-maintained, hands off), DB sportkingdbs. Exported all 1355 active-product images → `allegro-photos/<EAN>/NN.jpg` + manifest.csv (508 dirs; 38 no-EAN use name slugs, 7 dup-EAN split as `<ean>-dup-<id>`, 3 products imageless). Method: JSONL dump of ps_product/ps_image via PHP over SSH → rsync originals → build_tree.py; server untouched → [[architecture]].
- Access batch: enumerated BaseLinker order sources — 3 Allegro accounts (sklep_sportking 4448, sklep_Inkontor 26050, sklep_veloking 50219) + shop sportking_pr 30180 (product storage read-only) → [[architecture]]. Generated dedicated VPS key `~/.ssh/sportking_claude` (user's ssh-copy-id pending). Added VPS safety rules (no deploy script → backup-before-change, exact commands) → [[_meta/project-rules]]. Tracked library/workflow/.
- BaseLinker API token saved to `.env` (`baselinker_api`, git-ignored) and verified read-only: inventory "Sportking" id 4002 (pl, warehouse bl_5086) → [[architecture]].
- Public-site audit: sportking.pl live (Apache/Debian, LE cert fresh, ~1.1s TTFB), BERG/EXIT/Didakites/Gepetto catalog visible → [[architecture]]. Revival plan: audit-first; BaseLinker+Allegro access granted, token pending.
- Added live-system safety rules (read-only default, backup-before-write, dry-run confirm) → [[_meta/project-rules]].
- Captured baseline project context from the user (PrestaShop on Hetzner, BaseLinker, Allegro, BERG/EXIT partners) → [[_moc]], new [[architecture]] draft.
- Project bootstrapped from `~/ai-workflow` (vault skeleton, _meta symlinks, memory wiring).
