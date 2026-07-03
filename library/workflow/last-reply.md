(pulled: board + manifest context from this session)

Got it — no veloking snapshot for now, and I'll treat the stock-zeroing/Allegro-update plan as yours to execute. Let me find and analyze `list.xlsx` against the manifest:

79 scans, one EAN per row (duplicates = multiple units, presumably). Analyzing: quantities per EAN, bad scans, and match against the manifest:

Analysis done — here's the picture from your first scan batch (`products/list.xlsx`, 79 rows):

**Inventory: 32 unique products, 73 units total.** The full breakdown is in **`products/scan-report.csv`** (committed): EAN, quantity, whether it matched the legacy shop data, name, and how many photos are ready in `products/photos/`.

- **15 EANs matched** legacy data — names + photos ready to go (e.g. BERG Sun breeze spoiler ×8, Biky biały balance bike ×5, Buzzy Rubicon ×4).
- **17 EANs are unknown** to the old shop — no name or photos on hand. Most start with `8718469…` which is EXIT Toys' prefix, so these are likely EXIT products the shop never listed. Good news for these: when creating offers by EAN, Allegro usually auto-matches its own product catalog and supplies title, photos, and parameters — so missing legacy data may cost nothing.
- **6 bad scans confirmed** — they're all `YYMMDD-serial` format (`230331-116754`, `210921-090586`, …): the scanner caught the **production/serial-number barcode** instead of the EAN. Five distinct items need a re-scan — look for the 13-digit barcode (usually labeled EAN) rather than the date-looking sticker.

Your stock plan (zero out presta stock, update from Allegro, replace shop products from BaseLinker) is recorded in the vault as yours to execute — I won't touch it. The veloking-snapshot suggestion is shelved per your call.

One practical note: the report is regenerable in seconds — when you finish scanning (I see `list.xlsx` is still open in LibreOffice), just say "re-run the scan report" and I'll refresh it against the updated file. And whenever you want to start listing, the 15 matched products are the easy first wave: photos, Polish names, and quantities are all sitting ready.
