Nothing else is needed — the token alone authenticates every BaseLinker API call. Let me verify it works with a read-only request (per the project's read-only-by-default rule):

Token verified — now writing this back to the vault (architecture note + log) per the library workflow:

(pulled: _meta/project-rules — live-system safety rules; sportking/architecture)

**Nothing else is needed — the token is all BaseLinker requires, and I've verified it works.** A read-only `getInventories` call returned `SUCCESS`: your account has one inventory, **"Sportking"** (id 4002, Polish, warehouse `bl_5086`, two price groups, reservations enabled).

Two things I did alongside the check:

- **Added `.env` to `.gitignore`** — it wasn't ignored, and since I auto-commit this repo the token could have slipped into git history. It's now excluded (the earlier commit history is clean; the file was never committed).
- **Vault updated and committed** — architecture note's "pending API token" unknown resolved, log line added.

One heads-up: BaseLinker tokens are all-or-nothing (full write access), so the read-only-by-default and backup-before-write rules in project-rules are our only guardrails — I'll stick to those.

Natural next step whenever you want: a read-only audit of the sync setup — product count, stock/price sources, order sources (PrestaShop/Allegro connections) — to fill the remaining unknowns in the architecture note. Also noticed `library/workflow/` is sitting untracked in the repo — let me know if that should be committed or ignored.
