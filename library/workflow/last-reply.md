(pulled: architecture, project-rules — VPS rules apply; recon is read-only)

Key received — testing my dedicated key, then I'll do the read-only PrestaShop recon to build that EAN→photos mapping:

SSH works. The shop isn't in `/var/www/html` — checking Apache vhosts for the real docroot:

The shop lives at `/home/henrik/sportking/` (henrik = your colleague, presumably). Checking version and DB config:

175 MB of originals — small enough to just pull. Rsyncing them down (read-only on the server side), then building the EAN tree:

The shell was still cd'd into `photos/zdj` — retrying from the repo root:

All done. Here's the rundown:

**The deliverable — `~/sportking/allegro-photos/` is built** (177 MB, git-ignored):
- **`<EAN>/01.jpg, 02.jpg, …`** for the 473 products with an EAN — `01.jpg` is always the shop's cover image, rest follow shop ordering. Pulled fresh from the live DB + original images over SSH (server untouched, read-only).
- **38 products without EAN** got name-slug dirs (e.g. `gokart-na-pedaly-berg-buddy/`) per your fallback idea.
- **`manifest.csv`** at the root maps every dir → EAN, product id, reference, full Polish name, image count, and notes. For Allegro bulk-listing this file is the companion piece — you (or I) can work through it row by row.
- Two edge cases it flags: **7 duplicate EANs** — the same EAN is on two products in the shop, so the second product got a `<ean>-dup-<id>/` dir instead of silently mixing photos; worth a quick look since Allegro will reject duplicate-EAN offers anyway. And **3 active products have no images at all**.

**Your `photos/` dir**: found it after the fact — that's the manual export you meant in item 2. Mine supersedes it (correct UTF-8 names, EAN keys, originals only, no size-variant clutter), so `photos/` (334 MB) is yours to delete when ready. Both media dirs are git-ignored now.

**Keys question**: nothing to load — since you ran `ssh-copy-id`, my dedicated `sportking_claude` key works directly. Your `keys` alias (ssh-agent + passphrase) wouldn't help my session anyway: each command I run gets a fresh shell, so an agent unlocked in one command is gone by the next. The dedicated-key pattern is the right one; keep your own key as-is.

**PrestaShop stays hands-off** — noted in the vault that henrik maintains it; I only read (DB queries + image files). PrestaShop 9.0.3, DB `sportkingdbs`, docroot `/home/henrik/sportking/` — all recorded in the architecture note, everything committed.

Next step when you're ready: pick a first product (or small batch) from `manifest.csv` and I'll draft the Allegro offer flow through BaseLinker — dry-run first, per the safety rules.
