#!/usr/bin/env python3
"""Build/refresh the manual pricing sheet for Allegro deployment.

Seeds products/prices.xlsx from products/list-filled.xlsx so you fill ONE column
(price_pln) by hand. **Merge-aware**: rerunning after a new scan adds new EANs
and PRESERVES prices/stock you already typed — it never clobbers your input.

The `deploy` column flags the safe first wave:
  catalog  — matched to Allegro's product catalog (source=allegro). Safe to draft
             now: Allegro supplies compliant photos + parameters, GPSR producer
             is registered. This is the ~56 wave.
  manual   — override / berg-feed only. Needs real photos (scraped ones carry
             other shops' watermarks → compliance + copyright risk) and hand-set
             parameters before it can go up. HOLD.

Columns: ean | qty | name | category | source | deploy | price_pln | stock | note
Fill price_pln (PLN, gross). Leave stock blank → the draft creator defaults it.
Then create unpublished drafts:  ./scripts/allegro/allegro_draft.py create

  ./scripts/allegro/build_price_sheet.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from lib_xlsx import read_sheets, write_xlsx

FILLED = ROOT / "products" / "list-filled.xlsx"
PRICES = ROOT / "products" / "prices.xlsx"
COLS = ["ean", "qty", "name", "category", "source", "deploy", "price_pln", "stock", "note"]


def load_existing():
    """{ean: {price_pln, stock}} from a prior prices.xlsx, to preserve edits."""
    if not PRICES.exists():
        return {}
    rows = next(iter(read_sheets(PRICES).values()))
    if not rows:
        return {}
    # map header letters -> names from row 0
    hdr = {v: k for k, v in rows[0].items()}
    keep = {}
    for r in rows[1:]:
        ean = r.get(hdr.get("ean", ""), "").strip()
        if ean:
            keep[ean] = {
                "price_pln": r.get(hdr.get("price_pln", ""), "").strip(),
                "stock": r.get(hdr.get("stock", ""), "").strip(),
            }
    return keep


def main():
    if not FILLED.exists():
        sys.exit(f"missing {FILLED} — run scripts/reporting/enrich.py first")
    filled = next(iter(read_sheets(FILLED).values()))
    hdr = {v: k for k, v in filled[0].items()}
    prior = load_existing()

    rows = [COLS]
    kept = new = 0
    for r in filled[1:]:
        ean = r.get(hdr["ean"], "").strip()
        if not ean:
            continue
        source = r.get(hdr["source"], "").strip()
        deploy = "catalog" if source == "allegro" else ("manual" if source else "dark")
        p = prior.get(ean, {})
        if p.get("price_pln"):
            kept += 1
        elif ean not in prior:
            new += 1
        rows.append([
            ean,
            r.get(hdr["qty"], ""),
            r.get(hdr["name"], ""),
            r.get(hdr["category"], ""),
            source,
            deploy,
            p.get("price_pln", ""),   # preserved
            p.get("stock", ""),       # preserved
            r.get(hdr["note"], ""),
        ])
    # catalog wave first, then manual, then dark — makes the safe rows easy to fill
    order = {"catalog": 0, "manual": 1, "dark": 2}
    body = sorted(rows[1:], key=lambda x: (order.get(x[5], 3), x[2]))
    write_xlsx(PRICES, [("Prices", [COLS] + body)])
    catalog = sum(1 for x in body if x[5] == "catalog")
    print(f"wrote {PRICES.relative_to(ROOT)}: {len(body)} products "
          f"({catalog} catalog-safe to deploy first) | preserved {kept} prices, {new} new rows")


if __name__ == "__main__":
    main()
