---
project: sportking
type: moc
audience: both
updated: 2026-07-06
summary: Map of content for sportking.
---

# sportking

Online shop — **sportking.pl**, a PrestaShop store on a Hetzner VPS, integrated with
**BaseLinker** and through it with **Allegro** (Polish marketplace). Main partners /
suppliers: **BERG Toys** and **EXIT Toys** (names to confirm). Business is mostly
local and has been stale; current goal is to **revive it**.

## Notes
- [[architecture]] — **how it works**. The technical source of truth (early draft, mostly unverified).
- [[board]] — the plan (big features) · [[log]] — full history (everything, dated).
- [[user-board]] — personal kanban for things only the user can act on.

## Status (2026-07-06)
- **Plan pivot: full catalog reconstruction.** All existing PrestaShop products
  will be discarded; only the `sklep_veloking` Allegro listings survive. New
  catalog = whatever the physical warehouse count finds.
- Warehouse count in progress (user, barcode scanner), two full recounts so far
  (each supersedes the last — see `reporting/ingest-scan.py`): batch 1
  (2026-07-03, 79 scans, 32 unique EANs) and batch 2 (2026-07-06, 229 scans, 107
  unique EANs, 40 matched / 67 unmatched). Raw batches archived in
  `products/scans/<date>-<full|append>.xlsx`; reports in `report/`.
- User's stock plan (2026-07-03, user executes): zero out PrestaShop product
  stock, update products from Allegro, replace shop products from BaseLinker.
- Groundwork done: BaseLinker token + VPS access live, full audit of the old
  catalog (511 products), all product photos exported EAN-keyed to
  `products/photos/` + manifest — ready to match against the scanned EAN list.
- Live-system safety rules (backup-before-write, read-only default) →
  [[_meta/project-rules]].

## Key decisions
- **2026-07-03 — reconstruct, don't revive.** The stale PrestaShop catalog is
  not worth salvaging; rebuild from a physical warehouse count (scanner → EAN
  list). Only `sklep_veloking` Allegro listings stay. Old-catalog data (photos,
  names, EANs in `products/manifest.csv`) is reused as *material* for new
  listings, not migrated as-is.
