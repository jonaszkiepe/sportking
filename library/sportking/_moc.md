---
project: sportking
type: moc
audience: both
updated: 2026-07-03
summary: Map of content for sportking.
---

# sportking

Online shop — **sportking.pl**, a PrestaShop store on a Hetzner VPS, integrated with
**BaseLinker** and through it with **Allegro** (Polish marketplace). Main partners /
suppliers: **BERG Toys** and **EXIT Toys** (names to confirm). Business is mostly
local and has been stale; current goal is to **revive it**.

## Notes
- [[architecture]] — **how it works**. The technical source of truth (early draft, mostly unverified).
- [[board]] — the plan (big features) · [[log]] — full history (everything, dated).

## Status (2026-07-03)
- Vault bootstrapped; baseline context captured. Partners confirmed: BERG + EXIT Toys.
- Plan: **audit current state first**. Public-site audit done (site live, brands
  present, TLS healthy) → [[architecture]]. Next: BaseLinker + Allegro audit —
  waiting on API token / access from the user.
- Live-system safety rules (backup-before-write, read-only default) →
  [[_meta/project-rules]].

## Key decisions
- (decisions worth remembering + the why)
