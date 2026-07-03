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
  BaseLinker (ids above). Direct Allegro REST access not set up (would need OAuth
  per account) — only needed if BaseLinker's view proves insufficient.

## Catalog & business context (from public site, 2026-07-03)
- Outdoor/kids gear: trampolines, go-karts, swings, sandboxes, playhouses, kites,
  scooters, balance bikes, sports equipment, wooden toys/furniture.
- Brands: **BERG** and **EXIT Toys** (confirmed main partners), plus Didakites
  (kites), Gepetto (own-brand wooden toys), Buiten Speel. Polish/PLN only.
- Mostly local sales; shop has been stale — current goal is revival. A "-15%" kite
  promo spans 20+ products (freshness unknown).

## Server layout (verified 2026-07-03 via SSH, read-only)
- PrestaShop **9.0.3** at `/home/henrik/sportking/` (henrik = colleague who
  maintains the shop — **hands off PrestaShop code/config**, user-mandated).
- DB: MySQL `sportkingdbs`, prefix `ps_`, localhost; creds in
  `app/config/parameters.php` (read via PHP on the server, never copied out).
- Catalog: 511 active products, 473 with EAN (38 without, 7 duplicate-EAN
  groups), 1355 product images (`img/p/`, originals ~175 MB).
- Photo export: `~/sportking/allegro-photos/<EAN>/NN.jpg` (git-ignored) +
  `manifest.csv` — built 2026-07-03 for Allegro listing creation; rebuildable
  (scripts in session scratchpad, method in [[log]]).

## Unknowns / to verify
- PHP stack details, theme/modules (low priority — PrestaShop stays henrik's)
- BaseLinker sync config (direction, stock/price source of truth) — token live
  (in `.env` as `baselinker_api`, git-ignored); API verified 2026-07-03: one
  inventory "Sportking" (id 4002, pl, warehouse bl_5086, 2 price groups)
- Allegro account state and active listings — accounts enumerated via BaseLinker;
  listing-level detail still unchecked
- Whether the -15% promo and stock levels are current
- Where (if anywhere) custom code lives — this repo currently holds only the vault
