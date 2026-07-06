#!/usr/bin/env python3
"""Warehouse scan report — run after every scan session:  ./scripts/reporting/scan-report.py

Reads   products/list.xlsx              (scanner output, one EAN per row)
Enriches against products/dealers/berg-2026.xlsx (article no., name, category,
        dealer price, active status) and counts photos in products/photos/<EAN>/.
Writes  report/<YYYY-MM-DD_HH-MM-SS>.xlsx  — multi-page workbook:
          Summary | Inventory | Unmatched | Bad scans
Also refreshes products/berg-master.csv (store-agnostic product master).

Pure stdlib. Parses xlsx directly, so it works while list.xlsx is open in Excel.
"""
import csv
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_xlsx import read_sheets, write_xlsx
from berg_feed import load_master

LIST = ROOT / "products" / "list.xlsx"
FEED = ROOT / "products" / "dealers" / "berg-2026.xlsx"
PHOTOS = ROOT / "products" / "photos"          # legacy shop export, keyed by EAN
PHOTOS_BERG = ROOT / "products" / "photos-berg"  # Dealerzone/brand assets, keyed by article
MASTER_CSV = ROOT / "products" / "berg-master.csv"
REPORT_DIR = ROOT / "report"

IS_EAN = re.compile(r"\d{8}|\d{12,14}")


def read_scans(path):
    """Flatten every non-empty cell of the first sheet into a list of strings."""
    sheets = read_sheets(path)
    first = next(iter(sheets.values()))
    vals = []
    for row in first:
        for v in row.values():
            v = (v or "").strip()
            if not v:
                continue
            if re.fullmatch(r"\d+(\.\d+)?[eE]\+?\d+", v) or (v.replace(".", "", 1).isdigit() and "." in v):
                v = f"{float(v):.0f}"
            vals.append(v)
    return vals


def _count(d):
    return len(list(d.glob("*.jpg"))) if d.is_dir() else 0


def photo_count(ean, article=None):
    """Photos on hand = legacy EAN-keyed export + Dealerzone/brand article-keyed."""
    return _count(PHOTOS / ean) + (_count(PHOTOS_BERG / article) if article else 0)


def main():
    if not LIST.exists():
        sys.exit(f"missing {LIST}")
    scans = read_scans(LIST)
    master = load_master(FEED) if FEED.exists() else {}

    good = Counter(s for s in scans if IS_EAN.fullmatch(s))
    bad = Counter(s for s in scans if not IS_EAN.fullmatch(s))

    matched, unmatched = [], []
    for ean, qty in good.items():
        m = master.get(ean)
        if m:
            matched.append({"ean": ean, "qty": qty, "photos": photo_count(ean, m["article"]), **m})
        else:
            unmatched.append({"ean": ean, "qty": qty, "photos": photo_count(ean)})

    matched.sort(key=lambda r: (r["category"], r["name"]))
    unmatched.sort(key=lambda r: -r["qty"])

    # ---- persist store-agnostic master ----
    MASTER_CSV.parent.mkdir(exist_ok=True)
    with open(MASTER_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["article", "ean", "name", "category", "dealer_price_eur", "status"])
        for ean, m in sorted(master.items(), key=lambda kv: (kv[1]["category"], kv[1]["name"])):
            w.writerow([m["article"], ean, m["name"], m["category"], m["dealer_price_eur"], m["status"]])

    # ---- build report workbook ----
    units = sum(good.values())
    cat_counts = Counter()
    for r in matched:
        cat_counts[r["category"] or "(uncategorised)"] += r["qty"]
    photos_have = sum(1 for r in matched + unmatched if r["photos"] > 0)

    summary = [["metric", "value"],
               ["scans (rows)", len(scans)],
               ["units (valid EANs)", units],
               ["unique products", len(good)],
               ["matched to BERG feed", len(matched)],
               ["unmatched (need EXIT feed / discontinued)", len(unmatched)],
               ["bad scans (re-scan EAN)", sum(bad.values())],
               ["products with photos on hand", photos_have],
               ["", ""],
               ["units by category", ""]]
    for cat, n in cat_counts.most_common():
        summary.append([f"  {cat}", n])

    inv_header = ["category", "article", "ean", "name", "qty", "dealer_price_eur", "status", "photos"]
    inv_rows = [inv_header] + [[r["category"], r["article"], r["ean"], r["name"],
                               r["qty"], r["dealer_price_eur"], r["status"], r["photos"]]
                              for r in matched]
    unm_rows = [["ean", "qty", "photos", "note"]] + [[r["ean"], r["qty"], r["photos"],
                "not in BERG feed — EXIT or discontinued"] for r in unmatched]
    bad_rows = [["scanned_code", "count", "note"]] + [[c, q, "serial/date code — re-scan the EAN barcode"]
                for c, q in sorted(bad.items())]

    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / f"{datetime.now():%Y-%m-%d_%H-%M-%S}.xlsx"
    write_xlsx(out, [("Summary", summary), ("Inventory", inv_rows),
                     ("Unmatched", unm_rows), ("Bad scans", bad_rows)])

    print(f"report:  {out.relative_to(ROOT)}")
    print(f"master:  {MASTER_CSV.relative_to(ROOT)}  ({len(master)} BERG products)")
    print(f"scans {len(scans)} | units {units} | unique {len(good)} | "
          f"matched {len(matched)} | unmatched {len(unmatched)} | bad {sum(bad.values())}")
    if bad:
        print("re-scan EAN on:", ", ".join(sorted(bad)))


if __name__ == "__main__":
    main()
