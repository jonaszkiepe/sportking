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
- [ ] **Photos (interim)**: scraping Dealerzone (`scrape-dealerzone-photos.py`, public 1024px, article-keyed) — done for scan batch 1 (16/19 covered w/ legacy export). Next: run `--all` for a full library, decide with user on scope.
- [ ] **Photos (high-res, later)**: BERG brand portal (Marvia via `brandportal.berg.com`, Imagebank link in Dealerzone) — deferred until after selling starts, needs access enabled (marketing@bergtoys.com).
- [ ] Add EXIT (+ other) dealer feeds later; generalise `berg_feed.py` per brand
- [ ] Category map: BERG categories → Allegro / PrestaShop category trees
- [x] **Allegro drafts on sklep_Inkontor (26050)** — done for the 18 scanned products that match Allegro's catalog (price-less, unpublished; `allegro_draft.py`). Ids tracked in backups/ for rollback.
- [ ] **Allegro: the 14 unmatched scanned products** (EXIT + discontinued BERG) — no Allegro catalog product; need catalog-product creation or manual listing.
- [ ] **Allegro: finish the drafts** — add selling prices (we only have dealer prices) + photos, then publish. Category map (BERG→Allegro) still useful for the unmatched/manual ones.
- [ ] Decide fate of `sportking_pr` shop connection + `sklep_sportking` / `sklep_Inkontor` Allegro accounts

## In progress
- [ ] Warehouse count with scanner → EAN list (user; lands in this project soon)
- [ ] **Verify BaseLinker→presta stock sync actually pushes** scanned qty (catalog products must be LINKED to sportking_pr shop; test: Biky White presta 4 → should become scanned 5)
- [ ] Create the 17 not-in-presta scanned products (mostly EXIT) as presta products so they can carry stock

## Done
- [ ] Access + audit groundwork: BaseLinker token, VPS SSH, legacy catalog audit, EAN-keyed photo export (2026-07-03)
