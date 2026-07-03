On it. Full catalog is ~6,000 articles, so this is a long, request-heavy job against Dealerzone — let me first make the scraper gentle (a small delay on every request, not just saves) and resumable (skip articles already downloaded), so it can run in the background safely and survive interruападtion:

Full scrape is running in the background (6,023 articles). Let me confirm it's actually downloading before I leave it — waiting for the first progress checkpoint:

It's healthy and downloading real images (resuming past the 13 from the inventory run). At article 100/6,023 with a handful of hits — the dense ranges (go-karts `07.xx`, ride-ons `24.xx`, trampolines `35.xx`) come later, so the rate will climb. Let me commit the scraper improvements (the running job already has them loaded in memory):
