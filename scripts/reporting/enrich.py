#!/usr/bin/env python3
"""Fill the scanned product list from every deterministic source we have.

Per EAN in products/list.xlsx, resolve name + category + images by precedence
(highest first):

  1. products/ean-overrides.csv  — curated file: manual entries + everything a
     past web lookup already resolved. This is our accumulated knowledge; once an
     EAN lands here it is NEVER looked up again. An override also wins over
     Allegro, so it doubles as a correction lever.
  2. Allegro catalog (live API)  — Allegro's Polish name, category and images,
     matched strictly by EAN. The channel we sell on; the bulk of coverage.
  3. BERG dealer feed            — name + category for BERG items Allegro lacks.

Anything none of the above identifies is written to products/dark-todo.csv —
the ONLY rows a human/agent must touch. dark-todo.csv shares ean-overrides.csv's
columns, so you fill the blanks and paste the rows straight into the overrides
file; next run folds them in with zero lookups.

Outputs:
  products/list-filled.xlsx  — ean|qty|name|category|source|images|photo_dir|confidence|note
  products/dark-todo.csv     — still-unidentified EANs, ready to fill

Images:
  Allegro   -> products/photos-allegro/<EAN>/NN.jpg  (downloaded here)
  overrides -> products/photos-web/<EAN>/NN.<ext>     (existing files reused; if
               the override row has an image_url and no file yet, it's fetched)

Read-only against Allegro (GET only). Rerunnable — skips images already on disk.
Pure stdlib. Run:  ./scripts/reporting/enrich.py
"""
import csv, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "allegro"))
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "reporting"))
import allegro_draft as A
from lib_xlsx import write_xlsx

OVERRIDES = ROOT / "products" / "ean-overrides.csv"
PHOTOS_ALLEGRO = ROOT / "products" / "photos-allegro"
PHOTOS_WEB = ROOT / "products" / "photos-web"
OUT = ROOT / "products" / "list-filled.xlsx"
DARK = ROOT / "products" / "dark-todo.csv"
COLS = ["ean", "qty", "name", "category", "image_url", "source_url", "confidence", "note"]
UA = "sportking-sync/v1.0 (+https://sportking.pl/sportking-app)"


def load_overrides():
    """{ean: {name, category, image_url, source_url, confidence, note}}."""
    if not OVERRIDES.exists():
        return {}
    out = {}
    with open(OVERRIDES, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ean = (row.get("ean") or "").strip()
            if ean and (row.get("name") or "").strip():
                out[ean] = {k: (row.get(k) or "").strip() for k in COLS}
    return out


def leaf_category(prod):
    path = (prod.get("category") or {}).get("path") or []
    names = [n.get("name") for n in path if n.get("name") and n.get("name") != "Allegro"]
    return names[-1] if names else ""


def _fetch(url, dest):
    """Download url -> dest (choosing .jpg/.png by content-type). Returns True on
    a plausible image (>2KB), else False. Never raises."""
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            r = urllib.request.urlopen(req, timeout=30)
            data = r.read()
            if len(data) < 2048:
                return False
            ext = "png" if "png" in (r.headers.get("Content-Type", "").lower()) else "jpg"
            final = dest.with_suffix("." + ext)
            final.write_bytes(data)
            time.sleep(0.1)
            return True
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            if attempt == 2:
                return False
            time.sleep(1)


def _dir_images(d):
    return sorted(p for p in d.iterdir() if p.is_file() and p.stat().st_size > 0) if d.exists() else []


def allegro_images(ean, prod):
    """Download Allegro originals into photos-allegro/<ean>/NN.jpg. Returns count."""
    urls = [im.get("url") for im in (prod.get("images") or []) if im.get("url")]
    d = PHOTOS_ALLEGRO / ean
    if urls:
        d.mkdir(parents=True, exist_ok=True)
        for i, url in enumerate(urls, 1):
            if not _dir_images(d) or not (d / f"{i:02d}.jpg").exists():
                _fetch(url, d / f"{i:02d}")
    n = len(_dir_images(d))
    return (f"products/photos-allegro/{ean}", n) if n else ("", 0)


def override_images(ean, image_url):
    """Reuse existing photos-web/<ean>/ files; else fetch image_url once."""
    d = PHOTOS_WEB / ean
    have = _dir_images(d)
    if not have and image_url:
        d.mkdir(parents=True, exist_ok=True)
        if _fetch(image_url, d / "01"):
            have = _dir_images(d)
    n = len(have)
    return (f"products/photos-web/{ean}", n) if n else ("", 0)


def main():
    qty, master = A.scanned()
    overrides = load_overrides()
    rows = [["ean", "qty", "name", "category", "source", "images", "photo_dir", "confidence", "note"]]
    dark = [COLS]
    n_over = n_alle = n_feed = n_dark = imgs = 0

    for ean in sorted(qty, key=lambda e: -qty[e]):
        q = qty[ean]
        if ean in overrides:                                   # tier 1: curated
            o = overrides[ean]
            photo_dir, n = override_images(ean, o["image_url"])
            rows.append([ean, q, o["name"], o["category"], "override", n, photo_dir,
                         o["confidence"], o["note"]])
            n_over += 1; imgs += n
            continue

        p = A.match_product(ean)                               # tier 2: Allegro
        time.sleep(0.15)
        if p:
            photo_dir, n = allegro_images(ean, p)
            note = "also in BERG feed" if ean in master else ""
            rows.append([ean, q, p.get("name", ""), leaf_category(p), "allegro", n,
                         photo_dir, "high", note])
            n_alle += 1; imgs += n
        elif ean in master:                                    # tier 3: BERG feed
            m = master[ean]
            rows.append([ean, q, m.get("name", ""), m.get("category", ""), "berg-feed",
                         0, "", "high", "BERG feed only — no Allegro catalog product"])
            n_feed += 1
        else:                                                  # dark
            rows.append([ean, q, "", "", "", 0, "", "", "DARK — resolve in ean-overrides.csv"])
            dark.append([ean, q, "", "", "", "", "", ""])
            n_dark += 1
        print(f"  {ean}  x{q:<3} {rows[-1][4] or 'DARK':<9} img={rows[-1][5]:<2} {rows[-1][2][:44]}")

    write_xlsx(OUT, [("Filled", rows)])
    with open(DARK, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(dark)
    print(f"\n{len(qty)} products | override {n_over} · allegro {n_alle} · feed {n_feed} · "
          f"dark {n_dark} | {imgs} images")
    print(f"wrote {OUT.relative_to(ROOT)}  and  {DARK.relative_to(ROOT)} ({n_dark} to resolve)")


if __name__ == "__main__":
    main()
