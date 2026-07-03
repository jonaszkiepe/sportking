(pulled: _meta/project-rules, sportking/architecture — updating both as I go)

Working through the batch: commit `library/workflow`, read-only recon on the VPS, enumerate Allegro connections via BaseLinker, then tell you what's still needed.

Done — everything committed. Here's where each item stands:

**1. PrestaShop — what I need: just the SSH key authorized (item 3), nothing else.** Once I'm on the VPS I can read the PrestaShop version, PHP stack, theme, modules, and DB config directly from the filesystem — no back-office login needed for the audit. If we later want to change settings that only live in the admin panel, I'd ask for back-office access then.

**2. Allegro — no access needed right now.** All three accounts are already connected to BaseLinker and visible through the API token you gave me: `sklep_sportking` (4448), `sklep_Inkontor` (26050), `sklep_veloking` (50219). I can audit orders and listing state through BaseLinker read-only. Direct Allegro access (OAuth per account) is only worth setting up if BaseLinker's view turns out to be insufficient — I'll tell you if we hit that wall. Interesting find along the way: the PrestaShop↔BaseLinker product connection is **read-only** (`write: false`) — BaseLinker currently can't push product data to the shop. Worth confirming whether that's intentional.

**3. Hetzner VPS — one command needed from you.** Your `id_ed25519` key is passphrase-protected, so it works for you interactively but not for my non-interactive shell. I generated a dedicated key for this machine (`~/.ssh/sportking_claude`, same pattern as your veloking keys). To authorize it, run in your terminal (it'll ask for your usual passphrase once):

```
ssh-copy-id -i ~/.ssh/sportking_claude.pub sportking
```

Then tell me and I'll verify with a read-only probe. On safety, agreed and now written into project-rules as hard rules: since there's **no deploy script**, every server change is a live edit — so I'll always (a) recommend and take a backup first (`cp file file.bak-<date>` / `mysqldump` for DB, with the restore command stated), (b) show you the exact commands and old→new diff before running anything, (c) one change at a time, verifying the site responds after each. Recon stays read-only.

**4. library/workflow — now tracked** and included in the vault commits (it's the last-prompt/last-reply mirror, presumably from a hook).

Your BaseLinker heads-up is also captured: I added "consult heavily — ask before any call with unclear blast radius" to the safety rules. Backup tech proposal for when we get to writes: every write gets a before-image export to `library/sportking/backups/<date>-<what>.json`, committed to the vault *before* the write executes, so every change has a restorable snapshot in git history. If you want something stronger (e.g. a nightly full-inventory export as a standing safety net), say the word and I'll set it up.
