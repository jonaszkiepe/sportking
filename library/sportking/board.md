---
project: sportking
type: board
audience: user
updated: 2026-07-06
summary: Kanban board — big features only (the plan, not the log).
kanban-plugin: board
---

# sportking — board

## Backlog
- [ ] **Photos (interim)**: scraping Dealerzone (`scripts/scraping/scrape-dealerzone-photos.py`, public 1024px, article-keyed) — done for scan batch 1 (16/19 covered w/ legacy export). Next: run `--all` for a full library, decide with user on scope.
- [ ] **Photos (high-res, later)**: BERG brand portal (Marvia via `brandportal.berg.com`, Imagebank link in Dealerzone) — deferred until after selling starts, needs access enabled (marketing@bergtoys.com).
- [x] ~~Add EXIT dealer feed~~ — **EXIT ended the dealer relationship (2026-07-06); no feed/images ever coming.** Replaced by `enrich.py`: Allegro catalog (EAN→name/category/images) + committed `products/ean-overrides.csv` knowledge file. Other-brand feeds still possible via `berg_feed.py` per brand if a supplier offers one.
- [ ] Category map: BERG categories → Allegro / PrestaShop category trees
- [x] Allegro drafts on Inkontor: created 17 as proof-of-concept, then **deleted ALL account drafts** (2026-07-04, user request; 24 total incl. 7 pre-existing) — account now has 0 drafts. Backed up in backups/2026-07-04-inkontor-all-drafts-before-purge.json. Plan: re-list from BaseLinker catalog once grouped (article-keyed), not direct-to-Allegro.
- [ ] **Competitor pricing by EAN**: Allegro `/offers/listing` (buyer search) = 403 AccessDenied — app-level restriction, not scope. Needs Allegro to grant the app listing/buyer-API access, OR use Allegro's built-in price suggestion at publish time, OR website scraping (fragile/ToS-risky). BLOCKED via current API.
- [ ] Decide fate of `sportking_pr` shop connection + `sklep_sportking` / `sklep_Inkontor` Allegro accounts

## In progress
- [ ] **DECIDE (veloking stock): 12 of 18 surviving veloking offers source from presta products the zero-out set to 0.** Offer qty looks independent of presta stock (10≠7) so likely not at immediate risk. Options pending user: restore stock for those 12 / leave-and-watch / intended. Restore data ready in backups/2026-07-03-presta-stock-before.jsonl. Veloking offers backed up in backups/2026-07-03-veloking-offers.json.
- [ ] Warehouse count with scanner → EAN list (user; ongoing — batch 2 landed 2026-07-06, 229 scans/107 unique EANs, see [[log]])
- [ ] **Verify BaseLinker→presta stock sync actually pushes** scanned qty (catalog products must be LINKED to sportking_pr shop; test: Biky White presta 4 → should become scanned 5)
- [ ] Create the 17 not-in-presta scanned products (mostly EXIT) as presta products so they can carry stock

## Done
- [x] **Scanned-list enrichment: `scripts/reporting/enrich.py`** (2026-07-06). Fills name+category+images per EAN from `ean-overrides.csv` → Allegro catalog → BERG feed; leftovers to `dark-todo.csv`. Batch 2: 107 products, 106 identified (33 override / 56 Allegro / 17 feed), 1 dark, 349 images. Reusable & script-only — future runs just need an agent to resolve any new dark EANs into `ean-overrides.csv`.
- [ ] Access + audit groundwork: BaseLinker token, VPS SSH, legacy catalog audit, EAN-keyed photo export (2026-07-03)
- [x] Scripts reorganized into `scripts/` (concern-based subfolders: `allegro/`, `shop/`, `reporting/`, `scraping/`, `lib/` — separated from `products/`/`report/` data) + built `scripts/reporting/ingest-scan.py`: paste a raw scan at repo root, it archives to `products/scans/<date>-<full|append>.xlsx`, updates `products/list.xlsx` accordingly, and auto-runs the report (2026-07-06)
