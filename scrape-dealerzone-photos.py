#!/usr/bin/env python3
"""Fetch BERG product photos from Dealerzone into an article-keyed library.

Dealerzone serves product images at a fully predictable, PUBLIC URL:
    https://www.dealerzone.net/product/image/<size>/<article>_<n>.jpg
sizes: small 120x90 | medium 400x300 | large 1024x768 (max). No login needed for
images (only prices are gated). So we build straight from the article numbers in
products/berg-master.csv — no page scraping.

  ./scrape-dealerzone-photos.py --inventory   # articles in the latest scan
  ./scrape-dealerzone-photos.py --all         # every article in berg-master.csv
  ./scrape-dealerzone-photos.py 24.75.02.00 ... # specific articles

Photos land in products/photos-berg/<article>/NN.jpg (store-agnostic, article-keyed).
Resolution is medium (1024px) — good enough to start listing; the BERG brand
portal (Marvia) remains the source for true high-res later.
"""
import csv, re, sys, time, socket, urllib.request
from pathlib import Path
socket.setdefaulttimeout(20)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
IMG = "https://www.dealerzone.net/product/image/large/{art}_{n}.jpg"
OUTDIR = ROOT / "products" / "photos-berg"
MASTER = ROOT / "products" / "berg-master.csv"
UA = {"User-Agent": "Mozilla/5.0 (sportking asset sync)"}
ART = re.compile(r"\d\d\.\d\d\.\d\d\.\d\d")
MAX_PER = 15  # images per article to probe (stop at first gap)


def fetch(url):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()
        return b if b[:2] == b"\xff\xd8" or b[:8] == b"\x89PNG\r\n\x1a\n" else None
    except urllib.error.HTTPError:
        return None
    except Exception as e:  # noqa
        print(f"  ! {url}: {e}")
        return None


def scrape(article):
    saved = 0
    for n in range(1, MAX_PER + 1):
        b = fetch(IMG.format(art=article, n=n))
        if b is None:
            break  # images are sequential from _1; first gap = done
        d = OUTDIR / article
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{n:02d}.jpg").write_bytes(b)
        saved += 1
        time.sleep(0.15)
    return saved


def inventory_articles():
    from lib_xlsx import read_sheets
    from berg_feed import load_master
    m = load_master(ROOT / "products" / "dealers" / "berg-2026.xlsx")
    scans = read_sheets(ROOT / "products" / "list.xlsx")
    codes = {c for sheet in scans.values() for row in sheet for cell in row.values()
             for c in (cell or "").split() if re.fullmatch(r"\d{8}|\d{12,14}", c)}
    return sorted({m[c]["article"] for c in codes if c in m})


def all_articles():
    with open(MASTER) as f:
        return sorted({r["article"] for r in csv.DictReader(f) if ART.fullmatch(r["article"] or "")})


def main():
    args = sys.argv[1:]
    if "--inventory" in args:
        articles = inventory_articles()
    elif "--all" in args:
        articles = all_articles()
    else:
        articles = [a for a in args if ART.fullmatch(a)]
    if not articles:
        sys.exit("pass --inventory, --all, or article numbers")

    print(f"scraping {len(articles)} articles from Dealerzone (large/1024px)...")
    with_photos = total = 0
    for i, art in enumerate(articles, 1):
        n = scrape(art)
        if n:
            with_photos += 1
            total += n
        if i % 25 == 0 or n:
            print(f"  [{i}/{len(articles)}] {art}: {n} imgs")
    print(f"\ndone: {with_photos}/{len(articles)} articles got photos, {total} images -> {OUTDIR.relative_to(ROOT)}")
    missing = [a for a in articles if not (OUTDIR / a).is_dir()]
    if missing:
        print(f"no photo on Dealerzone for {len(missing)}: {', '.join(missing[:12])}{' ...' if len(missing) > 12 else ''}")


if __name__ == "__main__":
    main()
