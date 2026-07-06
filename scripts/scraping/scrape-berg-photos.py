#!/usr/bin/env python3
"""Fetch BERG product photos from bergtoys.com (Shopify) into an article-keyed library.

BERG's Shopify store exposes /products.json (all products, variants, images).
variant.sku == the BERG article number, and image filenames embed the article
number and EAN, so photos map to our master deterministically.

  ./scripts/scraping/scrape-berg-photos.py --index         # (re)build the index only, no downloads
  ./scripts/scraping/scrape-berg-photos.py --inventory     # download photos for scanned inventory
  ./scripts/scraping/scrape-berg-photos.py --all           # download the whole catalog
  ./scripts/scraping/scrape-berg-photos.py 24.75.02.00 ... # download specific articles

Photos land in products/photos-berg/<article>/NN.<ext>. Store-agnostic: keyed by
the stable article number, reusable for Allegro / PrestaShop / any channel.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = "https://us.bergtoys.com"   # US storefront; product shots are language-neutral
INDEX = ROOT / "products" / "dealers" / "berg-shopify-index.json"
OUTDIR = ROOT / "products" / "photos-berg"
MASTER = ROOT / "products" / "berg-master.csv"

ART = re.compile(r"\d\d\.\d\d\.\d\d\.\d\d")
UA = {"User-Agent": "Mozilla/5.0 (sportking photo sync)"}


def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)


def build_index():
    """article -> {name, eans:[...], images:[url,...]} from products.json pagination."""
    idx = {}
    page = 1
    while True:
        with _get(f"{STORE}/products.json?limit=250&page={page}") as r:
            products = json.load(r).get("products", [])
        if not products:
            break
        for p in products:
            skus = [v.get("sku") for v in p.get("variants", []) if ART.fullmatch(v.get("sku") or "")]
            srcs = [i["src"] for i in p.get("images", [])]
            for src in srcs:
                fname = src.split("/")[-1].split("?")[0]
                m = ART.search(fname)
                # assign image to the article in its filename; else to the product's sole sku
                targets = [m.group()] if m else (skus if len(skus) == 1 else [])
                for art in targets:
                    e = idx.setdefault(art, {"name": p.get("title", ""), "eans": set(), "images": []})
                    if src not in e["images"]:
                        e["images"].append(src)
                    for ean in re.findall(r"\d{13}", fname):
                        e["eans"].add(ean)
        page += 1
        time.sleep(0.3)
    for e in idx.values():
        e["eans"] = sorted(e["eans"])
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(idx, indent=0))
    return idx


def load_index():
    if not INDEX.exists():
        return build_index()
    return json.loads(INDEX.read_text())


def download(articles, idx):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    got = miss = 0
    for art in articles:
        entry = idx.get(art)
        if not entry or not entry["images"]:
            miss += 1
            continue
        dest = OUTDIR / art
        dest.mkdir(exist_ok=True)
        for n, src in enumerate(entry["images"], 1):
            url = ("https:" + src) if src.startswith("//") else src
            ext = src.split("?")[0].split(".")[-1].lower()
            ext = ext if ext in ("jpg", "jpeg", "png", "webp") else "jpg"
            out = dest / f"{n:02d}.{ext}"
            if out.exists():
                continue
            try:
                with _get(url) as r:
                    out.write_bytes(r.read())
                got += 1
                time.sleep(0.2)
            except Exception as ex:  # noqa
                print(f"  ! {art} img {n}: {ex}")
    return got, miss


def inventory_articles():
    import csv
    eans = set()
    # articles for EANs present in the newest scan report's master join = master rows we scanned;
    # simplest: use every article in the master that we have a photo folder OR was scanned.
    # Here: read scanned EANs from products/list.xlsx via the master mapping.
    sys.path.insert(0, str(ROOT / "scripts" / "lib"))
    sys.path.insert(0, str(ROOT / "scripts" / "reporting"))
    from lib_xlsx import read_sheets
    from berg_feed import load_master
    m = load_master(ROOT / "products" / "dealers" / "berg-2026.xlsx")
    scans = read_sheets(ROOT / "products" / "list.xlsx")
    flat = {(" ".join(row.values())).strip() for sheet in scans.values() for row in sheet}
    codes = {c for cell in flat for c in cell.split() if re.fullmatch(r"\d{8}|\d{12,14}", c)}
    return sorted({m[c]["article"] for c in codes if c in m})


def main():
    args = sys.argv[1:]
    idx = build_index() if "--index" in args else load_index()
    print(f"index: {len(idx)} articles with photos on bergtoys.com")
    if "--index" in args:
        total = sum(len(e["images"]) for e in idx.values())
        print(f"total images available: {total}")
        return
    if "--all" in args:
        articles = list(idx)
    elif "--inventory" in args:
        articles = inventory_articles()
    else:
        articles = [a for a in args if ART.fullmatch(a)]
    if not articles:
        print("nothing to download (pass --inventory, --all, or article numbers)")
        return
    covered = [a for a in articles if idx.get(a, {}).get("images")]
    print(f"requested {len(articles)} articles, {len(covered)} have photos online")
    got, miss = download(articles, idx)
    print(f"downloaded {got} images | {miss} articles with no online photo")


if __name__ == "__main__":
    main()
