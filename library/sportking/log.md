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
- Allegro drafting: BaseLinker API can't create offers (panel-only) + no Allegro OAuth yet, so pivoting to direct Allegro REST API for `sklep_Inkontor` (26050, user's choice). Built `allegro_auth.py` (device-code OAuth: login/refresh/whoami; tokens git-ignored). Next: user registers Allegro app → client id/secret in .env → authorize → then category map + prices + unpublished draft offers (dry-run first) → [[architecture]], [[board]].
- Dealerzone photo pipeline built (`scrape-dealerzone-photos.py`). Findings: portal = ASP.NET (dealerzone.net), login works with quote-stripped creds from .env (UserName=email + antiforgery); **product images are PUBLIC** at `/product/image/large/<article>_<n>.jpg`, max res **1024×768** (no bigger size exists). Article-keyed, no page scraping. Batch 1: 6/19 from Dealerzone (older stock absent), 16/19 with a photo combined w/ legacy export. Wired both photo sources into scan-report counts. Brand-portal Marvia deferred for true high-res → [[architecture]], [[board]].
- BERG dealer feed (`products/dealers/berg-2026.xlsx`) integrated. Rewrote scan-report into an enriched **multi-page xlsx** report (Summary/Inventory/Unmatched/Bad scans) + persistent store-agnostic `products/berg-master.csv` (6023 products); new `berg_feed.py` (links on article no., category via pricelist+prefix inference, price from pricelist col D) and stdlib `lib_xlsx.py` (read+write, no openpyxl). Batch-1 now 19 matched (feed > dead-shop manifest). Feed has NO product images.
- Photos investigation: built `scrape-berg-photos.py` (Shopify products.json, article-keyed via variant.sku + filename). Dead end for now — us.bergtoys.com carries only 53 articles (0 of our older/discontinued inventory); global site moved to berg.com (non-Shopify). Conclusion: photo source = BERG **dealer media bank** (ask user) + existing shop export (15/19 scanned covered) + Allegro EAN auto-fill. Decision pending → [[board]].
- Diagnosed unmatched-EAN cause: EXIT products are modular (component boxes each with own EAN; sellable unit = assembly, keyed by EXIT article no. e.g. 46-15-10-00). Proved from scan batch: 8718469469215 base×7 + 8719874704397 backboard×7 = 7 complete Galaxy basketball sets. BL inventory 4002 nearly empty (17 products, none unmatched) → not a data source. Of 17 unmatched: ~10 EXIT-family (bundle case), 7 BERG (just not-in-old-shop). Proposed: EXIT/BERG dealer feed → EAN→article→set master + bundle map + scan-report roll-up → [[architecture]] (EXIT modular section). Awaiting user on feed availability.
- Built `scan-report.py` (repo root, stdlib-only xlsx parser): products/list.xlsx → `report/<date-time>.csv` per scan session; verified identical to the manual batch-1 analysis; replaces one-off products/scan-report.csv → [[architecture]] (Tooling).
- Analyzed first warehouse scan batch (`products/list.xlsx`, 79 rows) → `products/scan-report.csv`: 32 unique EANs / 73 units; 15 EANs matched to legacy photos+names, 17 unknown (mostly 8718469* = likely EXIT Toys, never in old shop); 6 bad scans are `YYMMDD-serial` production codes. Veloking-snapshot suggestion declined (for now). User will zero presta stock + sync from Allegro/BaseLinker himself → [[_moc]].
- User restructured: photo export now lives at `products/photos/<EAN>/` + `products/manifest.csv` (was `allegro-photos/`; old manual `photos/` deleted). Refs updated in [[_moc]], [[architecture]], [[board]]; manifest.csv now git-tracked, photos ignored.
- Plan pivot recorded: full catalog reconstruction — presta products discarded, only sklep_veloking listings stay, warehouse scanner count → EAN list incoming as source of truth → [[_moc]] (key decision), [[architecture]] (banner), [[board]] (cards).
- VPS access live (dedicated key). Read-only recon: PrestaShop 9.0.3 at /home/henrik/sportking (colleague-maintained, hands off), DB sportkingdbs. Exported all 1355 active-product images → `allegro-photos/<EAN>/NN.jpg` + manifest.csv (508 dirs; 38 no-EAN use name slugs, 7 dup-EAN split as `<ean>-dup-<id>`, 3 products imageless). Method: JSONL dump of ps_product/ps_image via PHP over SSH → rsync originals → build_tree.py; server untouched → [[architecture]].
- Access batch: enumerated BaseLinker order sources — 3 Allegro accounts (sklep_sportking 4448, sklep_Inkontor 26050, sklep_veloking 50219) + shop sportking_pr 30180 (product storage read-only) → [[architecture]]. Generated dedicated VPS key `~/.ssh/sportking_claude` (user's ssh-copy-id pending). Added VPS safety rules (no deploy script → backup-before-change, exact commands) → [[_meta/project-rules]]. Tracked library/workflow/.
- BaseLinker API token saved to `.env` (`baselinker_api`, git-ignored) and verified read-only: inventory "Sportking" id 4002 (pl, warehouse bl_5086) → [[architecture]].
- Public-site audit: sportking.pl live (Apache/Debian, LE cert fresh, ~1.1s TTFB), BERG/EXIT/Didakites/Gepetto catalog visible → [[architecture]]. Revival plan: audit-first; BaseLinker+Allegro access granted, token pending.
- Added live-system safety rules (read-only default, backup-before-write, dry-run confirm) → [[_meta/project-rules]].
- Captured baseline project context from the user (PrestaShop on Hetzner, BaseLinker, Allegro, BERG/EXIT partners) → [[_moc]], new [[architecture]] draft.
- Project bootstrapped from `~/ai-workflow` (vault skeleton, _meta symlinks, memory wiring).
