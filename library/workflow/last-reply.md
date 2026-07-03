(pulled: project-rules — read-only recon is fine, this is a proposal question)

Good hunch, but let me ground it before proposing — I'll check what BaseLinker's inventory actually knows about those unmatched EANs (read-only), including whether any are set up as bundles. That tells us whether the fix is a data-source problem or a composition-mapping problem.

Now checking these against the BaseLinker inventory (read-only) — does the inventory know them, and are any flagged as bundles:

Nearly empty inventory (17 products, none of them the unmatched EANs), so BaseLinker isn't the reference here. Two things jump out that reshape your hypothesis — let me verify the brand/bundle nature of a couple of these EANs on the open web before I propose:

Confirmed — and the data is even more precise than your hunch. Let me record the finding, then give you the proposal.

Both of those EANs are **individual component boxes** of EXIT's modular basketball systems:
- `8718469469215` = EXIT Galaxy portable basketball base-on-wheels (article **46-15-10-00**, 23 kg) — scanned **×7**
- `8719874704397` = EXIT Galaxy backboard, Black Edition (113×74 cm, 6.5 kg) — scanned **×7**

A complete "Galaxy portable basketball" set = base-on-wheels **+** backboard, shipped as two boxes with two different EANs. You scanned 7 of each — that x7/x7 pairing is the bundle relationship showing up right in your scan counts.

Here's my read on the problem and how I'd solve it.

## The problem, precisely

"Unmatched" is actually two different problems mixed together, and only one is the bundle issue:

1. **True bundles (~10 of the 17, the EXIT-family EANs).** EXIT sells modular sets. The sellable product = several component boxes, each with its own EAN. You scan boxes; the "product" is the assembly. There's often **no single EAN for the whole set** — so no EAN lookup will ever find "the product," because one doesn't exist. The thing that ties components together is EXIT's **article number** (46-15-10-00), not an EAN.
2. **Just-not-in-the-old-shop (the other 7, all BERG `8715839`).** These are ordinary single-EAN products the old shop never carried. No bundle involved — they only look unmatched because the manifest is the *old shop's* catalog, which was never complete. During a full reconstruction, "unmatched" is expected and doesn't mean "broken."

So your hunch is right for the EXIT items, but the manifest was never going to be a complete reference regardless — matching against a dead shop is the wrong long-term key.

## What I propose (in order of leverage)

**1. Get the EXIT + BERG dealer feed — this is the real fix.** As a dealer you have portal access to a product data export (Excel/CSV/XML) that contains, per product: article number, component EANs, name, images, and set composition. One file resolves *every* unmatched EAN — names, photos, and crucially which boxes make which set. This beats reverse-engineering box-by-box from barcodes. **If you can export it, drop it in `products/` and I'll build an EAN → article-number → sellable-product master that supersedes the thin old-shop manifest.**

**2. A bundle map + smarter scan report.** Once composition is known, I add `products/bundles.csv` (set → component EANs and qty each) and extend `scan-report.py` to roll component scans up into sets and report **complete vs partial** — e.g. "7 Galaxy portable basketball sets complete" vs "3 backboards with no matching base → not sellable yet." That directly answers your real question: *how many sellable products do I have*, not how many boxes. It also tells you which physical boxes to pull together per Allegro order.

**3. Allegro does a lot of this for free at listing time.** You list the *set*, and Allegro's product catalog matches EXIT/BERG by EAN or article number and fills in title/photos/params. So the bundle map is mainly for your counting and picking; the listing itself often auto-resolves.

## The one decision I need from you

Can you get the EXIT (and BERG) dealer product feed? That single input determines the path:

- **Yes** → I build the EAN→article→set master + bundle roll-up in the scan report. Clean and authoritative.
- **Hard to get** → fallback: I enrich unmatched EANs by web lookup (like I just did for those two), which gets names + identifies components, but it's slower, per-EAN, and less reliable for composition.

I've recorded the EXIT-modular finding and this proposal in the vault. Want me to go the dealer-feed route (tell me if you can pull that file), or start with the web-enrichment fallback on the current 17?

Sources: [EXIT Galaxy base-on-wheels 46-15-10-00](https://www.exittoys.co.uk/exit-galaxy-portable-basketball-backboard-on-wheels-black-edition-46-15-10-00), [EXIT Galaxy backboard Black Edition](https://www.exittoys.de/exit-galaxy-basketballbrett-black-edition-46-41-10-00)
