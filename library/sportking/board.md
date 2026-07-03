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
- [ ] **Allegro drafts on sklep_Inkontor (26050)** via direct Allegro REST API (BaseLinker API can't create offers). In progress: `allegro_auth.py` device-flow OAuth built; waiting on user to register an Allegro app (client id/secret → .env) + authorize. Then: category map, selling prices, create unpublished draft offers (dry-run + confirm first).
- [ ] Decide fate of `sportking_pr` shop connection + `sklep_sportking` / `sklep_Inkontor` Allegro accounts

## In progress
- [ ] Warehouse count with scanner → EAN list (user; lands in this project soon)

## Done
- [ ] Access + audit groundwork: BaseLinker token, VPS SSH, legacy catalog audit, EAN-keyed photo export (2026-07-03)
