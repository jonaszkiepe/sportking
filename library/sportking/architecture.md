---
project: sportking
type: note
audience: both
status: draft
updated: 2026-07-03
summary: How sportking works — stack, hosting, integrations. Early draft, mostly unverified.
---

# sportking — architecture

> Started from the user's description; public-site facts verified 2026-07-03.

## Stack & hosting
- **Storefront:** PrestaShop — https://sportking.pl (version not exposed publicly).
  Apache 2.4.67 on Debian; TLS via Let's Encrypt, auto-renewal working (cert issued
  2026-06-18). Homepage TTFB ~1.1 s (no page cache in front?).
- **Hosting:** Hetzner VPS at 95.217.191.184, alias `ssh sportking` (user jonasz,
  key `id_ed25519` — passphrase-protected, so Claude uses a dedicated key
  `~/.ssh/sportking_claude`, authorized 2026-07-03 pending user's ssh-copy-id).
  **No deploy script exists** — all server changes are live edits; see the VPS
  safety rules in [[_meta/project-rules]].

## Integrations
- **BaseLinker** — order/listing management hub, linked to the PrestaShop store.
  Writes gated by the safety rules in [[_meta/project-rules]] (backup-before-write).
  Order sources (verified 2026-07-03): shop `sportking_pr` (30180), Allegro
  accounts `sklep_sportking` (4448), `sklep_Inkontor` (26050), `sklep_veloking`
  (50219). External storage `shop_30180` (PrestaShop) is connected **read-only**
  for products (`write: false`) — BaseLinker can read but not push product data.
- **Allegro** — Polish marketplace channel, 3 accounts, all connected via
  BaseLinker (ids above). **Direct Allegro REST API being set up** for
  `sklep_Inkontor` (26050) — chosen 2026-07-03 as the account to list BERG on —
  because the BaseLinker API has **no offer-creation method** (listings are a
  panel-only operation there). OAuth via `allegro_auth.py` (device code flow);
  tokens in `.allegro_tokens.json` (git-ignored). Client id/secret in `.env`
  (`allegro_client_id`, `allegro_client_secret`) from an app the user registers
  at apps.developer.allegro.pl. Draft offers = POST /sale/product-offers left
  unpublished (safe: not live).
- **BERG dealer assets** — image databank is a **Marvia DAM** (getmarvia.com:
  product photos, logos, videos, brochures), reached via the **Dealerzone** B2B
  portal (login `bergtoys.outliner.me`, an Outliner B2B system). Image-bank
  access enabled per-dealer; requests via marketing@bergtoys.com. This is the
  chosen photo source (2026-07-03). Pricelist feed also comes from here.

## Catalog & business context
> **⚠ Reconstruction (decided 2026-07-03):** the existing PrestaShop catalog is
> legacy — all its products will be gone. Only `sklep_veloking` Allegro listings
> stay. The new catalog comes from the physical warehouse count (scanner → EAN
> list, incoming). Old-catalog facts below are reference material only.

- Outdoor/kids gear: trampolines, go-karts, swings, sandboxes, playhouses, kites,
  scooters, balance bikes, sports equipment, wooden toys/furniture.
- Brands: **BERG** and **EXIT Toys** (confirmed main partners), plus Didakites
  (kites), Gepetto (own-brand wooden toys), Buiten Speel. Polish/PLN only.
- Legacy catalog (audited 2026-07-03): 511 active products; photos + name/EAN
  data preserved in `products/photos/` + `products/manifest.csv` for reuse when creating
  the new listings.

### BERG data inconsistencies — group on ARTICLE NUMBER (2026-07-04)
Cross-checked dealer feed vs old shop vs veloking offers vs Allegro catalog.
- **Article number `NN.NN.NN.NN` is the ONLY consistent key** across all sources
  (0 EANs → >1 article in feed). EAN and name both drift → **join on article no.**
- **Feed names are multi-language** (~1915/6023 contain EN/DE/NL words, e.g.
  "Kettingkastdelen zwart", "Seitenschürzen-Set"). Polish names live only in the
  old shop / veloking data → don't use feed names for PL listings.
- **EAN drift**: feed EAN sheet vs pricelist use different EANs per article
  year-to-year; old shop had 7 duplicate-EAN groups.
- **3 scanned items not in 2026 feed** (discontinued): 24.30.13.00 Rubicon,
  24.75.31.00 Biky City Red, 24.30.07.00 Buzzy Galaxy — only in shop+veloking.
- **Price gaps**: only 2335/6023 priced; 260 ACTIVE have no price.
- **Status barely populated**: 5546 blank, 325 ACTIVE, 148 UNDER_CON, 4 ENDING.
- **Data error**: article 24.60.00.00 = "#BERG Rebl" in feed (only `#` name) but
  "Reppy Rider" in shop+Allegro.
- **No category column**: inferred from article prefix; ~6 ambiguous prefixes.

### EXIT products are modular (key catalog fact, 2026-07-03)
- Many EXIT items are **sets assembled from separately-boxed components**, each
  component box carrying its **own EAN**. The sellable product is the assembly.
  The stable product identifier is EXIT's **article number** (e.g. `46-15-10-00`
  = Galaxy portable basketball base-on-wheels), NOT the per-box EAN.
- Confirmed via warehouse scan batch 1: `8718469469215` (Galaxy base-on-wheels)
  ×7 + `8719874704397` (Galaxy backboard) ×7 = 7 complete portable-basketball
  sets, two boxes each. This is why component EANs don't match the old-shop
  manifest (which was keyed on the shop's set-level product, or never listed them).
- Consequence for reconstruction: need an EAN → article-number → sellable-set
  master (best source: EXIT dealer feed) + a bundle map so the scan report can
  roll component scans up into complete/partial sets. See [[log]] / [[board]].
- Scope note: of the 17 unmatched EANs in batch 1, only ~10 are EXIT-family
  (8718469/8719874/8719743); the other 7 are BERG (8715839) — ordinary products
  the old shop simply never carried, single EAN each, **not** a bundle issue.

## Server layout (verified 2026-07-03 via SSH, read-only)
- PrestaShop **9.0.3** at `/home/henrik/sportking/` (henrik = colleague who
  maintains the shop — **hands off PrestaShop code/config**, user-mandated).
- DB: MySQL `sportkingdbs`, prefix `ps_`, localhost; creds in
  `app/config/parameters.php` (read via PHP on the server, never copied out).
- Catalog: 511 active products, 473 with EAN (38 without, 7 duplicate-EAN
  groups), 1355 product images (`img/p/`, originals ~175 MB).
- Photo export: `~/sportking/products/photos/<EAN>/NN.jpg` (git-ignored) +
  `manifest.csv` — built 2026-07-03 for Allegro listing creation; rebuildable
  (scripts in session scratchpad, method in [[log]]).

## Tooling (repo root)
- **`scan-report.py`** — run after every warehouse scan session (`./scan-report.py`).
  Reads `products/list.xlsx` (scanner output; parses xlsx directly, safe while
  open in Excel/LibreOffice), enriches each EAN against the BERG dealer feed
  (article no., name, category, dealer price, ACTIVE status) + photo counts,
  writes a **multi-page** `report/<date-time>.xlsx` (Summary · Inventory ·
  Unmatched · Bad scans) and refreshes `products/berg-master.csv`.
- **`berg_feed.py`** — parses `products/dealers/berg-2026.xlsx` into a master
  keyed by EAN. Links everything on the **article number** (stable; EANs drift
  yearly). Category = exact pricelist sheet, else inferred from 2-group article
  prefix (majority vote). Dealer price = pricelist col D (blank = not in 2026
  range = discontinued). Name/status from Mastersheet.
- **`lib_xlsx.py`** — dependency-free xlsx read+write (stdlib), so scripts run
  without openpyxl and read files that are open in Excel.
- **`products/berg-master.csv`** — store-agnostic product master (article, ean,
  name, category, dealer_price, status), 6023 rows. The multi-store source of
  truth; regenerated on every scan-report run. Tracked in git.
- **`scrape-dealerzone-photos.py`** — the working photo source. Dealerzone serves
  product images at a **public**, predictable URL
  `dealerzone.net/product/image/large/<article>_<n>.jpg` (no login needed for
  images; only prices are gated). So it builds `products/photos-berg/<article>/`
  straight from article numbers in `berg-master.csv` — no page scraping.
  `--inventory` (scanned articles) / `--all` (whole master) / explicit articles.
  **Resolution ceiling: `large` = 1024×768** (sizes: small 120×90, medium
  400×300, large 1024×768; xlarge/zoom/original all 404). Medium quality — fine
  to start listing; brand-portal Marvia stays the high-res source for later.
  Coverage: current stock only — older/discontinued articles have no Dealerzone
  image (fall back to the legacy shop export). Scan batch 1: 6/19 from Dealerzone,
  16/19 with a photo once combined with the legacy export.
- **`scrape-berg-photos.py`** — earlier attempt via us.bergtoys.com Shopify;
  dead end (only 53 articles, 0 of our inventory). Kept for reference only.
- **`.env` note:** values are wrapped in double quotes; Python parsers must strip
  them (`.strip().strip('"')`) — an unstripped quote made the Dealerzone login
  send an invalid email. Shell `export $(… | xargs)` handles quotes already.

## Unknowns / to verify
- PHP stack details, theme/modules (low priority — PrestaShop stays henrik's)
- BaseLinker sync config (direction, stock/price source of truth) — token live
  (in `.env` as `baselinker_api`, git-ignored); API verified 2026-07-03: one
  inventory "Sportking" (id 4002, pl, warehouse bl_5086, 2 price groups)
- Allegro account state and active listings — accounts enumerated via BaseLinker;
  listing-level detail still unchecked
- Whether the -15% promo and stock levels are current
- Where (if anywhere) custom code lives — this repo currently holds only the vault
