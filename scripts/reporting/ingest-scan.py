#!/usr/bin/env python3
"""Ingest a warehouse-scan paste at the repo root into the tracked pipeline.

Paste any new scan export (odc/ods/csv/xlsx — whatever the scanner app spits
out) into the repo root, then run this once:

  ./scripts/reporting/ingest-scan.py <file> --full      # a complete warehouse recount
  ./scripts/reporting/ingest-scan.py <file> --append    # new stock scanned on top of
                                                 # the current products/list.xlsx

--full REPLACES products/list.xlsx outright (this batch IS today's total).
--append CONCATENATES this batch's rows onto the existing list.xlsx (running
total grows — e.g. a delivery scanned on top of the last full count).

Either way: the batch is converted to xlsx and archived (dated + typed) to
products/scans/<date>-<full|append>.xlsx, the original paste is removed from
the repo root (the archive is its backup), and scan-report.py runs
automatically to produce the dated report/ workbook.
"""
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from lib_xlsx import read_sheets, write_xlsx

SCANS = ROOT / "products" / "scans"
LIST = ROOT / "products" / "list.xlsx"


def to_xlsx(src):
    if src.suffix.lower() == ".xlsx":
        return src
    tmp = SCANS / ".convert-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", str(tmp), str(src)],
                   check=True, capture_output=True)
    converted = tmp / (src.stem + ".xlsx")
    if not converted.exists():
        sys.exit(f"conversion failed: {src}")
    return converted


def archive_path(kind):
    date = datetime.now().strftime("%Y-%m-%d")
    dest = SCANS / f"{date}-{kind}.xlsx"
    n = 2
    while dest.exists():
        dest = SCANS / f"{date}-{kind}-{n}.xlsx"
        n += 1
    return dest


def sheet_rows(path):
    """First sheet's rows as lists of cell values, in column order."""
    sheets = read_sheets(path)
    first = next(iter(sheets.values()))
    return [[row[k] for k in sorted(row)] for row in first]


def main():
    args = sys.argv[1:]
    if len(args) != 2 or args[1] not in ("--full", "--append"):
        sys.exit(__doc__)
    src = Path(args[0]).resolve()
    kind = args[1].lstrip("-")
    if not src.exists():
        sys.exit(f"not found: {src}")

    SCANS.mkdir(parents=True, exist_ok=True)
    xlsx = to_xlsx(src)
    dest = archive_path(kind)
    shutil.copy(xlsx, dest)
    print(f"archived -> {dest.relative_to(ROOT)}")

    if kind == "full":
        shutil.copy(dest, LIST)
        print("products/list.xlsx REPLACED with this batch")
    else:
        existing = sheet_rows(LIST) if LIST.exists() else []
        new_rows = sheet_rows(dest)
        write_xlsx(LIST, [("Scans", existing + new_rows)])
        print(f"products/list.xlsx APPENDED: {len(existing)} existing + {len(new_rows)} new "
              f"= {len(existing) + len(new_rows)} rows")

    tmp = SCANS / ".convert-tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    src.unlink()
    print(f"removed original paste: {src}")
    sys.stdout.flush()

    subprocess.run([sys.executable, str(ROOT / "scripts" / "reporting" / "scan-report.py")], check=True)


if __name__ == "__main__":
    main()
