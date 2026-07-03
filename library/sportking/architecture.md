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
- **Hosting:** Hetzner VPS (no SSH/credentials on record — user grants BaseLinker +
  Allegro access only for now)

## Integrations
- **BaseLinker** — order/listing management hub, linked to the PrestaShop store.
  Writes gated by the safety rules in [[_meta/project-rules]] (backup-before-write).
- **Allegro** — Polish marketplace channel, connected via BaseLinker.

## Catalog & business context (from public site, 2026-07-03)
- Outdoor/kids gear: trampolines, go-karts, swings, sandboxes, playhouses, kites,
  scooters, balance bikes, sports equipment, wooden toys/furniture.
- Brands: **BERG** and **EXIT Toys** (confirmed main partners), plus Didakites
  (kites), Gepetto (own-brand wooden toys), Buiten Speel. Polish/PLN only.
- Mostly local sales; shop has been stale — current goal is revival. A "-15%" kite
  promo spans 20+ products (freshness unknown).

## Unknowns / to verify
- PrestaShop version, PHP stack, theme/modules (needs SSH or back office)
- BaseLinker sync config (direction, stock/price source of truth) — pending API token
- Allegro account state and active listings — pending access
- Whether the -15% promo and stock levels are current
- Where (if anywhere) custom code lives — this repo currently holds only the vault
