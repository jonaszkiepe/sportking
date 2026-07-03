---
project: sportking
type: board
audience: user
updated: 2026-07-03
summary: Kanban board — big features only (the plan, not the log).
kanban-plugin: board
---

# sportking — board

## Backlog
- [ ] **Photos**: user chose **dealer media bank** (2026-07-03) — user exports BERG asset library from the dealer portal into `products/media-berg/`; Claude builds article-keyed `products/photos-berg/<article>/` from it, merging existing shop export. Awaiting the export file.
- [ ] Add EXIT (+ other) dealer feeds later; generalise `berg_feed.py` per brand
- [ ] Category map: BERG categories → Allegro / PrestaShop category trees
- [ ] Create new Allegro listings from the matched stock (via BaseLinker, dry-run + backup per safety rules)
- [ ] Decide fate of `sportking_pr` shop connection + `sklep_sportking` / `sklep_Inkontor` Allegro accounts

## In progress
- [ ] Warehouse count with scanner → EAN list (user; lands in this project soon)

## Done
- [ ] Access + audit groundwork: BaseLinker token, VPS SSH, legacy catalog audit, EAN-keyed photo export (2026-07-03)
