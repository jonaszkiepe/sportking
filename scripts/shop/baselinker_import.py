#!/usr/bin/env python3
"""Import scanned/drafted products into the BaseLinker catalog (inventory 4002),
keyed by EAN so BaseLinker matches them to the Allegro offers.

  ./scripts/shop/baselinker_import.py dryrun      # show exactly what would be added (no writes)
  ./scripts/shop/baselinker_import.py backup      # export current catalog to backups/ (read-only)
  ./scripts/shop/baselinker_import.py import --yes # backup, then addInventoryProduct for each

Default scope = the products drafted on Allegro (scanned EANs that match Allegro's
catalog). Pass --all to import every scanned product instead.
BaseLinker write rules: always backs up the catalog first; records created
product_ids in backups/ for rollback (deleteInventoryProduct).
"""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "reporting"))
sys.path.insert(0, str(ROOT / "scripts" / "allegro"))
from allegro_draft import scanned, match_product  # reuse scan + Allegro EAN match

INV = 4002
WAREHOUSE = "bl_5086"
BACKUP = ROOT / "library" / "sportking" / "backups"
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


def build_list(all_scanned):
    qty, master = scanned()
    rows = []
    for ean, q in sorted(qty.items(), key=lambda x: -x[1]):
        m = master.get(ean, {})
        p = match_product(ean)               # Allegro catalog product (or None)
        time.sleep(0.12)
        if not all_scanned and not p:
            continue
        # prefer the descriptive BERG-feed name, else Allegro's catalog name
        name = m.get("name") or (p or {}).get("name") or f"EAN {ean}"
        rows.append({"ean": ean, "sku": m.get("article", ""), "name": name,
                     "qty": q, "on_allegro": p is not None})
    return rows


def backup_catalog():
    BACKUP.mkdir(parents=True, exist_ok=True)
    lst = bl("getInventoryProductsList", {"inventory_id": INV}).get("products", {})
    ids = list(lst.keys())
    data = bl("getInventoryProductsData", {"inventory_id": INV, "products": ids}) if ids else {"products": {}}
    out = BACKUP / "2026-07-03-baselinker-catalog-before.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"backed up {len(ids)} existing catalog products -> {out.relative_to(ROOT)}")
    return set(ids)


def existing_eans():
    """EANs already in the catalog, to skip duplicates."""
    lst = bl("getInventoryProductsList", {"inventory_id": INV}).get("products", {})
    ids = list(lst.keys())
    if not ids:
        return set()
    d = bl("getInventoryProductsData", {"inventory_id": INV, "products": ids}).get("products", {})
    return {p.get("ean") for p in d.values() if p.get("ean")}


def cmd(action, all_scanned):
    rows = build_list(all_scanned)
    print(f"\n{'IMPORT' if action == 'import' else 'would import'} {len(rows)} products "
          f"into BaseLinker catalog {INV} ({'all scanned' if all_scanned else 'Allegro-drafted only'}):\n")
    print(f"  {'ean':<15}{'qty':>4}  {'sku':<13} name")
    for r in rows:
        print(f"  {r['ean']:<15}{r['qty']:>4}  {r['sku']:<13} {r['name'][:40]}")
    if action != "import":
        print("\ndry-run only. Re-run with:  ./baselinker_import.py import --yes")
        return
    have = existing_eans()
    created = []
    for r in rows:
        if r["ean"] in have:
            print(f"  skip (already in catalog): {r['ean']}")
            continue
        res = bl("addInventoryProduct", {
            "inventory_id": INV, "ean": r["ean"], "sku": r["sku"],
            "text_fields": {"name": r["name"]},
            "stock": {WAREHOUSE: int(r["qty"])}})
        pid = res.get("product_id")
        ok = res.get("status") == "SUCCESS"
        print(f"  {'OK ' if ok else 'ERR'} {r['ean']} -> product_id {pid}")
        if ok:
            created.append({"product_id": pid, "ean": r["ean"], "sku": r["sku"], "name": r["name"], "qty": r["qty"]})
        else:
            print("     ", str(res)[:160])
        time.sleep(0.4)
    rec = BACKUP / "2026-07-03-baselinker-imported.json"
    rec.write_text(json.dumps(created, indent=2, ensure_ascii=False))
    print(f"\ncreated {len(created)} catalog products; ids in {rec.relative_to(ROOT)} (rollback: deleteInventoryProduct)")


if __name__ == "__main__":
    a = sys.argv[1:]
    all_scanned = "--all" in a
    act = a[0] if a and a[0] in ("dryrun", "backup", "import") else "dryrun"
    if act == "backup":
        backup_catalog()
    elif act == "import" and "--yes" in a:
        backup_catalog()
        cmd("import", all_scanned)
    else:
        cmd("dryrun", all_scanned)
