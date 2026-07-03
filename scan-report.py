#!/usr/bin/env python3
"""Warehouse scan report — run after every scan session.

Reads  products/list.xlsx   (scanner output, one EAN per row)
Joins  products/manifest.csv (legacy shop names) + products/photos/<EAN>/ (photo counts)
Writes report/<YYYY-MM-DD_HH-MM-SS>.csv and prints a summary.

Pure stdlib — parses the .xlsx directly (works even while the file is open
in LibreOffice/Excel). Usage: ./scan-report.py
"""
import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
XLSX = ROOT / "products" / "list.xlsx"
MANIFEST = ROOT / "products" / "manifest.csv"
PHOTOS = ROOT / "products" / "photos"
REPORT_DIR = ROOT / "report"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_xlsx_column(path: Path) -> list[str]:
    """Return all non-empty cell values from the first sheet, as strings."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        sheet_name = next(n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
        root = ET.fromstring(z.read(sheet_name))
        values = []
        for c in root.iter(f"{{{NS['m']}}}c"):
            ctype = c.get("t", "n")
            if ctype == "inlineStr":
                v = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
            else:
                node = c.find("m:v", NS)
                if node is None or node.text is None:
                    continue
                v = shared[int(node.text)] if ctype == "s" else node.text
            v = v.strip()
            if v:
                # numeric cells may come out as "8.715839011975E12" or "123.0"
                if re.fullmatch(r"\d+(\.\d+)?([eE]\+?\d+)?", v) and ("." in v or "e" in v.lower()):
                    v = f"{float(v):.0f}"
                values.append(v)
        return values


def main() -> None:
    if not XLSX.exists():
        sys.exit(f"missing {XLSX}")
    scans = read_xlsx_column(XLSX)
    manifest = {r["ean"]: r for r in csv.DictReader(open(MANIFEST)) if r["ean"]}

    is_ean = lambda s: re.fullmatch(r"\d{8}|\d{12,14}", s)
    good = Counter(s for s in scans if is_ean(s))
    bad = Counter(s for s in scans if not is_ean(s))

    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / f"{datetime.now():%Y-%m-%d_%H-%M-%S}.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ean", "qty", "status", "name", "photos"])
        for ean, qty in sorted(good.items(), key=lambda x: (-x[1], x[0])):
            m = manifest.get(ean)
            nphotos = len(list((PHOTOS / ean).glob("*.jpg"))) if (PHOTOS / ean).is_dir() else 0
            w.writerow([ean, qty, "matched" if m else "unmatched", m["name"] if m else "", nphotos])
        for code, qty in sorted(bad.items()):
            w.writerow([code, qty, "BAD-SCAN (serial/date code, re-scan EAN)", "", 0])

    matched = sum(1 for e in good if e in manifest)
    print(f"report: {out.relative_to(ROOT)}")
    print(f"scans: {len(scans)}  units: {sum(good.values())}  unique EANs: {len(good)}")
    print(f"matched to legacy photos/names: {matched}  unmatched: {len(good) - matched}")
    if bad:
        print(f"\nBAD SCANS — re-scan the EAN barcode on these {sum(bad.values())} label(s):")
        for code, qty in sorted(bad.items()):
            print(f"  {code}" + (f"  (x{qty})" if qty > 1 else ""))


if __name__ == "__main__":
    main()
