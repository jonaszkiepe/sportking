Three things — let me delete the drafts first, then answer the pricing question (which is a great one).

Adding a delete command and running it against the tracked draft ids:

The delete works server-side (204) but my `_call` helper choked trying to parse the empty 204 response — one draft got deleted (25→24), then it crashed. Let me fix `_call` to handle empty responses and re-run (already-deleted ones return 404, which I treat as done):

All 17 reported deleted, but the listing still shows `18730679187` — likely Allegro's offer listing lagging after deletion. Let me verify that specific offer directly and recount:

Confirmed gone — `18730679187` returns 404, and the count dropped to **7 INACTIVE drafts, all pre-existing account drafts (none of mine).** All 17 deleted cleanly. Now let me answer your pricing question by actually testing it — searching Allegro's public offers by EAN to pull competitor prices:

Now your new instruction: **delete every draft on the account** (including the 7 that were there before my work). These are the account's own drafts, so I'll **back up their full data first** (recoverable), then delete all. Adding a purge command:

7 deleted, but 2 more surfaced (listing lag or newly-visible). Let me handle those 2 with a separate backup (so I don't overwrite the 7-draft backup) and confirm zero remain:

**All drafts deleted — the account now has 0 INACTIVE drafts** (my 17 + the 7 pre-existing, all backed up to `backups/` first). The "2 remaining" was just Allegro's listing lag; the final count confirmed 0.

Let me record everything and commit, then give you the straight answer on competitor pricing:

Everything's committed. Here's the straight answer on competitor pricing — I tested it live rather than guessing.

## Can I scrape competitor EAN prices from Allegro? Not with the current access.

I tried the exact endpoint that would do it — Allegro's public offer search (`/offers/listing?phrase=<EAN>`, which returns all sellers' offers + prices for a product). It returns **403 AccessDenied**. And I confirmed it's **not a scope problem**: my token has every scope, and the product-catalog endpoint (`/sale/products`) works fine (200). It's an **app-level restriction** — Allegro gates its public "buyer" search/listing API, and standard seller apps don't get it by default.

So the query logic is written and ready (it's a clean call), it just hits a wall Allegro controls.

## The three ways to actually get competitor pricing

1. **Enable the offer-listing/buyer API access on your Allegro app** *(the clean path)*. In the Allegro developer portal, check whether the app `sportking-sync` can request/enable access to the offer listing (public REST API for buyers). Allegro grants this to approved apps. **If it's available, I flip it on and the price-scraper works immediately** — pull min/median/max competitor price per EAN across your whole catalog, in bulk.

2. **Allegro's built-in price suggestion at publish time** — this is the *"prices looked up from Allegro when publishing"* you mentioned. When you list a product by EAN, Allegro shows the going price range from existing offers. It works, but it's the panel feature with the caveats you already know: per-offer, manual, only where the product already has competitor offers.

3. **Scrape allegro.pl directly** (the website, not the API). Possible but I'd advise against it as a foundation — fragile HTML, rate limits, CAPTCHA risk, and against Allegro's terms for automated access.

**My recommendation:** check option 1 in the developer portal first. If the app can get listing access, bulk competitive pricing by EAN becomes trivial and I'll build it right away. If not, we lean on Allegro's publish-time suggestion (2) and I can help structure a pricing sheet around it.

Want me to look into what's required to enable that offer-listing access, or is that something you can toggle/apply for on the app?
