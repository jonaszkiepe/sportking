---
project: sportking
type: note
audience: both
status: draft
updated: 2026-07-06
summary: Allegro listing rulebook + deploy workflow — offer states, images, fees, GPSR, delivery; how we push the scanned catalog to Inkontor as drafts.
---

# Allegro — listing rules & deploy workflow

Everything needed to put the scanned catalog on Allegro (account **`sklep_Inkontor`
26050**) safely. Rules researched 2026-07-06 (4 web agents, official Allegro/help +
developer docs); account state probed live via the REST API same day. Verify the
flagged points before scaling.

## Deploy in two waves (the key split)

The 107 scanned products (see [[log]], `enrich.py`) split by how they were identified:

- **Catalog-safe wave (~56)** — matched to Allegro's **product catalog** by EAN
  (`source=allegro` in `list-filled.xlsx`). Attaching an offer to the catalog card
  makes Allegro supply the **photos, parameters, category** — compliant *by
  construction* (the photos are Allegro's own shared gallery, not ours). Deploy
  these first.
- **Manual wave (~50)** — override + BERG-feed-only (`source=override`/`berg-feed`).
  **Not** in Allegro's catalog, so each needs a hand-built offer with **our own
  images**. Our web-scraped images are unsafe (see Images below) → these are on
  HOLD until real photos exist.
- **Dark (1)** — `8731869663717`, unidentified. Physical check ([[user-board]]).

## Workflow (script-only)

1. `scripts/reporting/enrich.py` → `products/list-filled.xlsx` (name/category/images).
2. `scripts/allegro/build_price_sheet.py` → `products/prices.xlsx` (merge-aware;
   catalog rows first). **User fills the `price_pln` column** (gross PLN). Prices
   persist across reruns.
3. `scripts/allegro/allegro_draft.py create` (dry-run) / `create --yes` — creates
   **priced, INACTIVE (unpublished) drafts** for catalog-matched EANs that have a
   price. Rows without a price or not in the catalog are skipped. Every created
   offer id is recorded in `library/sportking/backups/…-drafts.json` (rollback via
   `delete --yes`).
4. **Activate when genuinely ready to sell that item.** Activation (`publication.status:
   ACTIVE`, needs stock ≥1 + full data) is the go-live *and* the BaseLinker-import
   trigger — see below.

## Offer states & the 0-stock trap

- States: `INACTIVE` (draft) · `ACTIVATING` · `ACTIVE` · `ENDED`. Move via
  `PATCH /sale/product-offers/{id}` `publication.status`, or bulk
  `PUT /sale/offer-publication-commands`.
- **An active offer must have `stock.available ≥ 1`.** Set stock to 0 and Allegro
  **auto-ends the offer** (`endedBy: EMPTY_STOCK`). So *"active with 0 stock"* is
  impossible — a 0-stock offer is a dead ENDED listing. **Do not** try to park
  offers at 0 stock. (Confidence: high.)
- Safe "parked" state = **INACTIVE drafts** (zero sale risk). Go live by activating.
- Blocking-price trick (active + absurd price + stock 1) exists but risks a stray
  sale; a cancelled order dents a from-zero account — avoid for now.

## BaseLinker import

- BaseLinker "Import aukcji" pulls **ACTIVE** offers by default; **ENDED** only if
  you paste specific offer IDs; **INACTIVE drafts — likely NOT importable**
  (undocumented — **VERIFY with BaseLinker support** before relying on it).
- Practical consequence: offers reach BaseLinker when you **activate** them, not
  before. The user's belief "must be active for BaseLinker to pull them" holds.

## Images (rules the manual wave must meet)

- Main photo: **white background** (RGB 255,255,255), packshot; min 400 px long
  side, max 2560². Up to 16 photos.
- **Banned:** watermarks, any shop/seller logo (ours or a competitor's), added
  text, icons, frames, promo banners, contact data. **Allowed:** the
  **manufacturer's own** brand/logo on the product/packaging (BERG/EXIT branding
  is fine).
- **Scraped retailer images = double risk:** (1) they often carry the source
  shop's watermark → rule violation; (2) reusing their photos is **copyright**
  exposure (notice-and-takedown → offer pulled). Safe sources: Allegro catalog
  (by EAN), manufacturer official assets, or our own white packshots.
- Enforcement ladder: email warning → ostrzeżenie → feature limits → suspension →
  all-accounts block. Trademark report → removal + **180-day brand block**.

## GPSR (mandatory since 13 Dec 2024)

- Every offer needs **producer data** (name, address, email) + **safety info**
  (warnings/instructions). A separate **"responsible person" is only needed if the
  producer is outside the EU** — BERG & EXIT are Netherlands (EU), so producer data
  suffices.
- **Catalog does NOT supply GPSR** — set it in *Ustawienia sprzedaży → Dane
  producentów* and assign to offers (bulk via *Mój asortyment*; API
  `responsibleProducer` on the offer). Missing GPSR blocks *publishing/resuming*
  (doesn't end live offers).
- **Account already has producers registered: Berg, BS Toys, exit, Gepetto** (probed
  via `/sale/responsible-producers`). The 2026-07-03 POC EXIT draft carried
  `responsibleProducer` (exit) + `safetyInformation` — so this path works.

## Delivery / returns / warranty

- A **delivery price list** (cennik dostaw) attaches per offer; practically required
  to publish. Smart! needs a delivery-method mix (courier-to-address + point/locker
  + cash-on-delivery) and decent seller quality.
- Business seller must have: **14-day withdrawal** (return policy), **rękojmia**
  (implied warranty), and a **warranty** section filled (may state none).
- **Account already has all of these**: 16 shipping rates (InPost, One Fulfillment…),
  1 return policy (*Warunki zwrotów*), 1 warranty, 1 rękojmia (*Reklamacje*).

## Fees & pricing (avoid selling at a loss)

- **Commission** is the only mandatory fee (listing is free). Toys ~**5–12%**,
  Sport ~**8–11.5%**, tiered by price, charged on **price + buyer-paid delivery**
  (Smart free delivery not added to base). Exact %: verify live.
- **Smart!** = seller-funded per-parcel surcharge (~0.99–11.49 zł); buyer
  free-delivery threshold 49.90 zł. Seller still pays the real carrier cost.
- **The "price drops and I get refunded" mechanic = Allegro Ceny.** Allegro lowers
  your price for the buyer and **refunds you the difference** (default Allegro funds
  100%; you may opt to co-fund) → you net ~your set price. It is *not* a loss unless
  you opt into co-funding. Not to be confused with *zwrot prowizji* (commission
  refunded on returns/non-payment).
- **No Buy-Now price floor exists** — the API `minimalPrice` is only an *auction*
  reserve (10% fee). So pricing discipline is on us: set `price_pln` **≥ break-even**.
  Break-even (net, then ×1.23 VAT): `P_min = (COGS + Smart_surcharge + carrier +
  overhead + rate·delivery) / (1 − rate)`. Toys/sport mostly 23% VAT.

## Descriptions

- No contact data, no links to any off-Allegro purchase, no off-platform steering,
  no marketing fluff ("gratis/tanio/promocja/hit"). External links only if they add
  product info (manual, video), never sales. Auto-enforced — non-compliant won't
  publish.

## To verify (flagged low/med confidence)

- Whether BaseLinker imports **INACTIVE drafts** (docs say active + ended-by-ID only).
- Exact toy/sport commission % per subcategory (aggregator figures).
- 2026 Smart! surcharge amounts (recently changed) — check seller panel.
- Whether an Allegro draft can be saved with **no price at all**.

## Sources

help.allegro.com (zdjęcia, GPSR, opis, dostawa, prowizja), developer.allegro.pl
(offer management, product-offers, GPSR group edit), base.com/baselinker help
(import aukcji), allegro.pl/regulamin. Full URLs in the 2026-07-06 research
(scratch); re-run the agents to refresh.
