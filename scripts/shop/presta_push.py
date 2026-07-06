#!/usr/bin/env python3
"""Push warehouse-scan stock to PrestaShop via BaseLinker: scanned products get
their scanned quantity, every other presta product is set to 0.

Source of truth = the warehouse scan (products/list.xlsx). Target = the sportking_pr
shop (BaseLinker external storage shop_30180). REFUSES to run unless BaseLinker's
write flag for that shop is enabled (Integrations -> sportking_pr -> allow stock
update). Uses the pre-captured backup as the product list + restore point.

  ./scripts/shop/presta_push.py dryrun       # show exactly what changes (no writes)
  ./scripts/shop/presta_push.py push --yes   # push (only if write is enabled)
"""
import json, re, sys, time, urllib.request, urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from lib_xlsx import read_sheets

STORAGE = "shop_30180"
BACKUP = ROOT / "library" / "sportking" / "backups" / "2026-07-03-presta-stock-before.jsonl"
env = {}
for l in open(ROOT / ".env"):
    if "=" in l and not l.startswith("#"):
        k, v = l.rstrip("\n").split("=", 1)
        env[k] = v.strip().strip('"').strip("'")


def bl(method, params):
    data = urllib.parse.urlencode({"method": method, "parameters": json.dumps(params)}).encode()
    req = urllib.request.Request("https://api.baselinker.com/connector.php",
                                 data=data, headers={"X-BLToken": env["baselinker_api"]})
    return json.load(urllib.request.urlopen(req, timeout=60))


def write_enabled():
    for s in bl("getExternalStoragesList", {}).get("storages", []):
        if s["storage_id"] == STORAGE:
            return bool(s.get("write"))
    return False


def scanned_qty():
    sheets = read_sheets(ROOT / "products" / "list.xlsx")
    codes = [c for sh in sheets.values() for row in sh for cell in row.values()
             for c in (cell or "").split() if re.fullmatch(r"\d{8}|\d{12,14}", c)]
    return Counter(codes)


def build_changes():
    """[[product_id, variant_id, target_qty], ...] for rows whose qty changes."""
    scan = scanned_qty()
    changes, to_scan, to_zero = [], 0, 0
    for l in open(BACKUP):
        r = json.loads(l)
        ean = (r.get("ean13") or "").strip()
        target = scan[ean] if ean in scan else 0
        if target == r["quantity"]:
            continue  # no change
        changes.append([int(r["id_product"]), int(r["id_product_attribute"]), int(target)])
        if target > 0:
            to_scan += 1
        else:
            to_zero += 1
    return changes, to_scan, to_zero


def main():
    a = sys.argv[1:]
    do_it = a and a[0] == "push" and "--yes" in a
    changes, to_scan, to_zero = build_changes()
    print(f"stock changes: {len(changes)}  ({to_scan} set to scanned qty, {to_zero} set to 0)")
    if not do_it:
        for c in changes[:8]:
            print(f"  product {c[0]} variant {c[1]} -> {c[2]}")
        print(f"  ... ({len(changes)} total)")
        print("\ndry-run only. To push:  ./presta_push.py push --yes")
        return
    if not write_enabled():
        sys.exit("REFUSING: BaseLinker write to sportking_pr is still OFF "
                 "(enable stock update on the connection first).")
    for i in range(0, len(changes), 1000):
        batch = changes[i:i + 1000]
        res = bl("updateExternalStorageProductsQuantity", {"storage_id": STORAGE, "products": batch})
        print(f"  pushed {i + len(batch)}/{len(changes)}  status={res.get('status')}")
        time.sleep(0.5)
    print("done. Verify a few products in presta, then set up the automatic sync.")


if __name__ == "__main__":
    main()
