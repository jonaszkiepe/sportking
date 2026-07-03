---
project: sportking
type: note
audience: both
status: draft
updated: 2026-07-03
summary: How sportking works — stack, hosting, integrations. Early draft, mostly unverified.
---

# sportking — architecture

> Draft from the user's description (2026-07-03). Nothing below verified hands-on yet.

## Stack & hosting
- **Storefront:** PrestaShop (version unknown) — https://sportking.pl
- **Hosting:** Hetzner VPS (access details TBD — no SSH/credentials on record)

## Integrations
- **BaseLinker** — order/listing management hub, linked to the PrestaShop store.
- **Allegro** — Polish marketplace channel, connected via BaseLinker.

## Business context
- Mostly local sales; the shop has been stale for a while — current goal is revival.
- Main partners/suppliers: **BERG Toys** and **EXIT Toys** (user said "Berktois" and
  "Exit" — spelling/identity to confirm). Both are Dutch outdoor-toys brands
  (go-karts, trampolines, playground equipment), which suggests the catalog focus.

## Unknowns / to verify
- PrestaShop version, PHP stack, theme/modules on the VPS
- How BaseLinker sync is configured (direction, stock/price source of truth)
- Allegro account state and active listings
- Where (if anywhere) custom code lives — this repo currently holds only the vault
