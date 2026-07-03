(pulled: sportking/_moc + architecture — updating the plan to the reconstruction model)

New direction is clear — recording the reconstruction plan across the vault notes:

All references updated. Adding a log line and committing everything, including the now-tracked manifest:

Everything's updated and committed. Summary of what changed:

**Plan pivot recorded in the vault** — the _moc now carries it as a key decision ("reconstruct, don't revive"): all PrestaShop products discarded, only `sklep_veloking` listings survive, and the scanner EAN list becomes the source of truth for what gets listed. The architecture note got a warning banner marking all legacy-catalog facts as reference material, and the board has the pipeline as cards: warehouse count (in progress, you) → match EAN list against the manifest → create new Allegro listings via BaseLinker.

**Your restructure adopted** — I spotted that you moved the export to `products/photos/<EAN>/` with the manifest at `products/manifest.csv` and deleted the old `photos/` dir. All vault references now point to the new paths, `products/photos/` is git-ignored (177 MB of images), and **`products/manifest.csv` is now tracked in git** — it's the name/EAN/photo mapping and worth versioning.

For when the scanner list lands: drop it anywhere in `products/` (any format — CSV, plain EAN-per-line, whatever the scanner emits) and I'll diff it against the manifest to tell you which scanned items already have photos + names ready and which need new material. Two things to keep in mind for that step: 38 legacy products had no EAN (their photos live under name-slug dirs, so scanned items missing from the manifest might still have photos there), and 7 EANs were duplicated in the old shop — I flagged them in the manifest's `note` column.

One suggestion meanwhile: I could snapshot the current `sklep_veloking` listings read-only via BaseLinker into `library/sportking/backups/` — that's the "what stays" baseline, and having it before any reconstruction work starts is exactly the strong-backup pattern you asked for. Want me to?
