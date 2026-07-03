Let me pin down the actual Marvia URL rather than hand-wave — searching and probing the likely addresses:

`bergtoys.marvia.com` responds — let me confirm it's the actual BERG image bank:

The Marvia portal is login-gated and JavaScript-rendered, so the direct URL only resolves once you're authenticated — probing from outside just returns the empty Marvia shell. Here's the reliable way in.

**Go through Dealerzone — that's BERG's official route to it:**

1. Log in to Dealerzone at **https://bergtoys.outliner.me/login** (the same portal the pricelist came from).
2. Once in, look for an **"Image bank"** / **"Media"** / **"Marketing"** link — that link hands you off into the Marvia portal, already scoped to your dealer rights. That's why going via Dealerzone is more reliable than a direct URL: it carries your login and country permissions through.

The Marvia portal itself most likely lives at a **`bergtoys.marvia.com`**-style address (that responded, but it's a login-gated single-page app so I can't confirm the exact one from outside — the Dealerzone link is the definitive entry).

**If there's no image-bank link in Dealerzone**, then image-bank access just isn't switched on for your account yet. BERG enables it per-dealer — email **marketing@bergtoys.com** with your name, email, and country to get it turned on (per BERG's own dealer docs).

Once you're inside the Marvia portal, that's where we pick the path from my last message: check for a **"select all → download"** (a zip is the easy win — drop it in `products/media-berg/` and I sort it by article number), and note whether the image bank asked for its own login or clicked straight through from Dealerzone (tells me how to handle auth if we build the scraper instead).
