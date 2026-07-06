#!/usr/bin/env python3
"""Create price-less, UNPUBLISHED Allegro draft offers for scanned products.

Attaches each offer to Allegro's product catalog by EAN (which supplies category,
parameters and photos). Offers are created with publication.status=INACTIVE and
NO price -> they are drafts, never live. Only works for EANs Allegro already has
a catalog product for; the rest are reported as unmatched.

  ./scripts/allegro/allegro_draft.py match      # read-only: scanned EAN -> Allegro product match
  ./scripts/allegro/allegro_draft.py drafts     # read-only: list current INACTIVE draft offers
  ./scripts/allegro/allegro_draft.py create     # dry-run: show exactly what would be created
  ./scripts/allegro/allegro_draft.py create --yes   # actually create the drafts (records ids)

Reversible: every created offer id is appended to
library/sportking/backups/<date>-allegro-inkontor-drafts.json.
"""
import json, re, sys, time, urllib.request, urllib.error, urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "reporting"))
from lib_xlsx import read_sheets
from berg_feed import load_master

API = "https://api.allegro.pl"
OAUTH = "https://allegro.pl"
UA = "sportking-sync/v1.0 (+https://sportking.pl/sportking-app)"
TOKENS = ROOT / ".allegro_tokens.json"
BACKUP = ROOT / "library" / "sportking" / "backups"
env = {}
for l in open(ROOT / ".env"):
    if "=" in l and not l.startswith("#"):
        k, v = l.rstrip("\n").split("=", 1)
        env[k] = v.strip().strip('"').strip("'")


def _tok():
    return json.loads(TOKENS.read_text())["access_token"]


def _call(method, path, body=None, params=None, _retry=True):
    url = f"{API}{path}" + ("?" + urllib.parse.urlencode(params) if params else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {_tok()}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json",
        "User-Agent": UA})
    try:
        r = urllib.request.urlopen(req, timeout=40)
        raw = r.read()
        return r.status, (json.loads(raw) if raw.strip() else {})  # 204 = empty body
    except urllib.error.HTTPError as e:
        if e.code == 401 and _retry:
            _refresh()
            return _call(method, path, body, params, _retry=False)
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def _refresh():
    import base64
    t = json.loads(TOKENS.read_text())
    auth = base64.b64encode(f"{env['allegro_client_id']}:{env['allegro_client_secret']}".encode()).decode()
    req = urllib.request.Request(f"{OAUTH}/auth/oauth/token",
        data=urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": t["refresh_token"]}).encode(),
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA})
    new = json.load(urllib.request.urlopen(req, timeout=30))
    new["_saved"] = int(time.time())
    TOKENS.write_text(json.dumps(new, indent=2))


def scanned():
    """{ean: qty} for valid EANs in products/list.xlsx, plus BERG master names."""
    master = load_master(ROOT / "products" / "dealers" / "berg-2026.xlsx")
    sheets = read_sheets(ROOT / "products" / "list.xlsx")
    codes = [c for sh in sheets.values() for row in sh for cell in row.values()
             for c in (cell or "").split() if re.fullmatch(r"\d{8}|\d{12,14}", c)]
    qty = Counter(codes)
    return qty, master


def match_product(ean):
    code, d = _call("GET", "/sale/products", params={"phrase": ean, "language": "pl-PL"})
    prods = d.get("products", []) if isinstance(d, dict) else []
    # STRICT: only a product whose EAN parameter exactly equals this ean.
    # No top-hit fallback — never attach a draft to an unverified product.
    for p in prods:
        for par in p.get("parameters", []):
            if par.get("id") == "225693" or par.get("name", "").startswith("EAN"):
                if ean in (par.get("values") or []):
                    return p
    return None


def existing_draft_products():
    """product ids already used in INACTIVE offers, to avoid duplicates."""
    ids = set()
    code, d = _call("GET", "/sale/offers", params={"publication.status": "INACTIVE", "limit": 1000})
    for o in (d.get("offers", []) if isinstance(d, dict) else []):
        pid = (((o.get("productSet") or [{}])[0]).get("product") or {}).get("id")
        if pid:
            ids.add(pid)
    return ids


def cmd_match():
    qty, master = scanned()
    hit = miss = 0
    print(f"{'ean':<15}{'qty':>4}  {'match':<6} name")
    for ean, q in sorted(qty.items(), key=lambda x: -x[1]):
        p = match_product(ean)
        time.sleep(0.15)
        nm = (master.get(ean, {}).get("name") or (p or {}).get("name", "") or "")[:44]
        print(f"{ean:<15}{q:>4}  {'YES' if p else 'no':<6} {nm}")
        hit += bool(p); miss += (not p)
    print(f"\n{hit} of {hit + miss} scanned products match an Allegro catalog product (draftable this way)")


def cmd_drafts():
    code, d = _call("GET", "/sale/offers", params={"publication.status": "INACTIVE", "limit": 100})
    offers = d.get("offers", []) if isinstance(d, dict) else []
    print(f"{len(offers)} INACTIVE draft offer(s) on the account:")
    for o in offers:
        print(f"  {o.get('id')}  {o.get('name','')[:50]}  stock={((o.get('stock') or {}).get('available'))}")


def load_prices():
    """{ean: {'price': float|None, 'stock': int|None}} from products/prices.xlsx.
    Only rows with a filled price_pln are returned. Empty file -> {}."""
    from lib_xlsx import read_sheets
    path = ROOT / "products" / "prices.xlsx"
    if not path.exists():
        return {}
    rows = next(iter(read_sheets(path).values()))
    if not rows:
        return {}
    hdr = {v: k for k, v in rows[0].items()}
    out = {}
    for r in rows[1:]:
        ean = r.get(hdr.get("ean", ""), "").strip()
        raw = r.get(hdr.get("price_pln", ""), "").strip().replace(",", ".")
        if not ean or not raw:
            continue
        try:
            price = float(raw)
        except ValueError:
            continue
        st = r.get(hdr.get("stock", ""), "").strip()
        out[ean] = {"price": price, "stock": int(float(st)) if st else None}
    return out


def cmd_create(do_it):
    """Create priced, UNPUBLISHED (INACTIVE) drafts for the catalog-safe wave:
    EANs that (a) match Allegro's catalog and (b) have a price in prices.xlsx."""
    qty, master = scanned()
    prices = load_prices()
    have = existing_draft_products() if do_it else set()
    plan, no_price = [], 0
    for ean, q in sorted(qty.items(), key=lambda x: -x[1]):
        if ean not in prices:            # skip: no price filled (or manual/dark tier)
            no_price += 1
            continue
        p = match_product(ean)           # require a catalog product (safe tier)
        time.sleep(0.15)
        if p and p["id"] not in have:
            plan.append((ean, q, p, prices[ean]))
    print(f"draftable now: {len(plan)} priced catalog products "
          f"({no_price} skipped: no price filled or not catalog-matched)\n")
    for ean, q, p, pr in plan:
        st = pr["stock"] if pr["stock"] is not None else q
        print(f"  {'CREATE' if do_it else 'would create'}: {ean} x{st}  {pr['price']:.2f} PLN  {p['name'][:38]}")
    if not do_it:
        print("\ndry-run only. Re-run with --yes to create these unpublished drafts.")
        return
    BACKUP.mkdir(parents=True, exist_ok=True)
    rec = BACKUP / "2026-07-03-allegro-inkontor-drafts.json"
    created = json.loads(rec.read_text()) if rec.exists() else []
    for ean, q, p, pr in plan:
        st = pr["stock"] if pr["stock"] is not None else q
        code, d = _call("POST", "/sale/product-offers", body={
            "productSet": [{"product": {"id": p["id"]}}],
            "sellingMode": {"format": "BUY_NOW",
                            "price": {"amount": f"{pr['price']:.2f}", "currency": "PLN"}},
            "stock": {"available": int(st)},
            "publication": {"status": "INACTIVE"}})
        ok = code in (200, 201, 202)
        oid = d.get("id") if isinstance(d, dict) else None
        print(f"  {'OK ' if ok else 'ERR'} {code}  {ean}  offer={oid}  {pr['price']:.2f}PLN  {p['name'][:30]}")
        if ok:
            created.append({"offerId": oid, "ean": ean, "qty": int(st), "price": pr["price"],
                            "productId": p["id"], "name": p.get("name")})
        else:
            print("     ", str(d)[:200])
        time.sleep(0.4)
    rec.write_text(json.dumps(created, indent=2, ensure_ascii=False))
    print(f"\nrecorded {len(created)} draft ids in {rec.relative_to(ROOT)} (delete-able for rollback)")


def cmd_dedupe(do_it):
    """Find products with >1 INACTIVE draft; delete the duplicates I created today
    (keep the oldest offer per product, never touch offers not created today)."""
    rec = BACKUP / "2026-07-03-allegro-inkontor-drafts.json"
    mine = {str(x["offerId"]) for x in (json.loads(rec.read_text()) if rec.exists() else [])}
    mine.add("18730679187")  # the inline test draft (Fiat 500)
    code, d = _call("GET", "/sale/offers", params={"publication.status": "INACTIVE", "limit": 1000})
    offers = d.get("offers", []) if isinstance(d, dict) else []
    by_prod = {}
    for o in offers:
        _, det = _call("GET", f"/sale/product-offers/{o['id']}")
        pid = (((det.get("productSet") or [{}])[0]).get("product") or {}).get("id")
        by_prod.setdefault(pid, []).append(o["id"])
        time.sleep(0.15)
    to_del = []
    for pid, ids in by_prod.items():
        if pid and len(ids) > 1:
            keep = min(ids, key=int)  # oldest stays
            for oid in ids:
                if oid != keep and str(oid) in mine:
                    to_del.append((oid, pid, keep))
    print(f"duplicate drafts I created: {len(to_del)}")
    for oid, pid, keep in to_del:
        print(f"  {'DELETE' if do_it else 'would delete'} {oid} (dup of kept {keep}, product {pid[:8]})")
    if not do_it:
        print("\ndry-run. Re-run with --yes to delete these."); return
    deleted = set()
    for oid, pid, keep in to_del:
        c, _ = _call("DELETE", f"/sale/offers/{oid}")
        ok = c in (200, 204)
        if ok:
            deleted.add(str(oid))
        print(f"  {'deleted' if ok else 'FAILED ' + str(c)} {oid}")
        time.sleep(0.3)
    if rec.exists() and deleted:  # only untrack what was actually removed
        kept = [x for x in json.loads(rec.read_text()) if str(x["offerId"]) not in deleted]
        rec.write_text(json.dumps(kept, indent=2, ensure_ascii=False))


def cmd_delete(do_it):
    """Delete every draft tracked in the backup file (the ones I created)."""
    rec = BACKUP / "2026-07-03-allegro-inkontor-drafts.json"
    mine = json.loads(rec.read_text()) if rec.exists() else []
    print(f"{'DELETING' if do_it else 'would delete'} {len(mine)} tracked drafts")
    if not do_it:
        for x in mine:
            print(f"  {x['offerId']}  {x.get('name', '')[:44]}")
        print("\ndry-run. Re-run with --yes")
        return
    deleted = []
    for x in mine:
        oid = str(x["offerId"])
        c, _ = _call("DELETE", f"/sale/offers/{oid}")
        ok = c in (200, 204, 404)  # 404 = already gone
        print(f"  {'deleted' if ok else 'FAILED ' + str(c)} {oid}  {x.get('name', '')[:36]}")
        if ok:
            deleted.append(oid)
        time.sleep(0.3)
    remaining = [x for x in mine if str(x["offerId"]) not in deleted]
    rec.write_text(json.dumps(remaining, indent=2, ensure_ascii=False))
    print(f"\ndeleted {len(deleted)}; {len(remaining)} still tracked")


def cmd_purge(do_it):
    """Back up, then delete EVERY INACTIVE draft on the account (incl. pre-existing)."""
    _, d = _call("GET", "/sale/offers", params={"publication.status": "INACTIVE", "limit": 1000})
    offers = d.get("offers", []) if isinstance(d, dict) else []
    print(f"{len(offers)} INACTIVE drafts on the account")
    backup = []
    for o in offers:
        _, det = _call("GET", f"/sale/product-offers/{o['id']}")
        backup.append(det if det else o)
        time.sleep(0.1)
    rec = BACKUP / "2026-07-04-inkontor-all-drafts-before-purge.json"
    rec.write_text(json.dumps(backup, indent=2, ensure_ascii=False))
    print(f"backed up {len(backup)} drafts -> {rec.relative_to(ROOT)}")
    if not do_it:
        for o in offers:
            print(f"  would delete {o['id']}  {o.get('name', '')[:44]}")
        print("\ndry-run. Re-run with --yes")
        return
    for o in offers:
        c, _ = _call("DELETE", f"/sale/offers/{o['id']}")
        print(f"  {'deleted' if c in (200, 204, 404) else 'FAIL ' + str(c)} {o['id']}  {o.get('name', '')[:36]}")
        time.sleep(0.3)
    _, d2 = _call("GET", "/sale/offers", params={"publication.status": "INACTIVE", "limit": 1000})
    print(f"\nremaining INACTIVE drafts: {len(d2.get('offers', []))}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "match": cmd_match()
    elif a[0] == "drafts": cmd_drafts()
    elif a[0] == "create": cmd_create("--yes" in a)
    elif a[0] == "dedupe": cmd_dedupe("--yes" in a)
    elif a[0] == "delete": cmd_delete("--yes" in a)
    elif a[0] == "purge": cmd_purge("--yes" in a)
    else: print(__doc__)
