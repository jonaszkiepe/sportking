---
project: sportking
type: moc
audience: both
updated: 2026-07-03
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

## Status (2026-07-03)
- **Plan pivot: full catalog reconstruction.** All existing PrestaShop products
  will be discarded; only the `sklep_veloking` Allegro listings survive. New
  catalog = whatever the physical warehouse count finds.
- Warehouse count in progress (user, barcode scanner). First batch analyzed:
  `products/list.xlsx` (79 scans) → `products/scan-report.csv` — 32 unique EANs
  (15 with legacy photos/names, 17 unknown to the old shop), 6 bad scans
  (serial/date codes, need re-scan).
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
