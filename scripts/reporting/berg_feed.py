"""Parse the BERG dealer feed (products/dealers/berg-2026.xlsx) into a master.

load_master(path) -> dict keyed by EAN:
    { ean: {article, name, category, dealer_price_eur, status} }

Everything links on the **article number** (NN.NN.NN.NN), the stable id — EANs
drift between years, so keying purely on EAN loses data. Fields come from:
  - name, status  ← 'Mastersheet' (col P name, M status), keyed by article (A);
                    EAN sheet description as fallback.
  - dealer price  ← category pricelist sheets, col D "Dealerprice excl. VAT",
                    keyed by article. Blank for articles absent from the 2026
                    pricelist (i.e. discontinued for this year).
  - category      ← pricelist sheet name when the article is listed there
                    (authoritative); otherwise inferred from the article's
                    2-group prefix (e.g. 24.75 → Ride-Ons) via majority vote
                    learned from the pricelists.
  - full EAN coverage ← 'EAN' sheet (Item number | Description | Bar code).
"""
import re
from collections import Counter, defaultdict

from lib_xlsx import read_sheets

_ART = re.compile(r"\d\d\.\d\d\.\d\d\.\d\d")


def _prefix(article):
    return ".".join(article.split(".")[:2])  # e.g. "24.75.02.00" -> "24.75"


def _num(s):
    try:
        return round(float(s), 2)
    except (TypeError, ValueError):
        return ""


def load_master(path):
    sheets = read_sheets(path)

    # article -> name / status (Mastersheet is the authoritative per-article record)
    name_by_art, status_by_art = {}, {}
    for r in sheets.get("Mastersheet", []):
        art = r.get("A", "")
        if _ART.fullmatch(art or ""):
            name_by_art[art] = (r.get("P") or "").strip()
            status_by_art[art] = r.get("M", "")

    # pricelists: exact category + dealer price by article; learn prefix->category
    cat_by_art, price_by_art = {}, {}
    prefix_votes = defaultdict(Counter)
    for name in [n for n in sheets if "pricelist" in n.lower()]:
        cat = re.sub(r"\s*20\d\d$", "", name.split(" pricelist")[0].replace("Pricelist ", "")).strip()
        for r in sheets[name]:
            art = r.get("A", "")
            if not _ART.fullmatch(art or ""):
                continue
            cat_by_art[art] = cat
            price_by_art[art] = _num(r.get("D"))
            prefix_votes[_prefix(art)][cat] += 1
    cat_by_prefix = {p: c.most_common(1)[0][0] for p, c in prefix_votes.items()}

    def category(art):
        return cat_by_art.get(art) or cat_by_prefix.get(_prefix(art), "")

    # assemble ean -> record, full coverage from the EAN sheet + pricelist/master EANs
    master = {}

    def add(ean, art, fallback_name=""):
        ean = (ean or "").strip()
        if not ean or not _ART.fullmatch(art or "") or ean in master:
            return
        master[ean] = {
            "article": art,
            "name": name_by_art.get(art) or (fallback_name or "").strip(),
            "category": category(art),
            "dealer_price_eur": price_by_art.get(art, ""),
            "status": status_by_art.get(art, ""),
        }

    for r in sheets.get("EAN", []):
        add(r.get("C"), r.get("A"), r.get("B"))
    for r in sheets.get("Mastersheet", []):
        add(r.get("T"), r.get("A"))
    for name in [n for n in sheets if "pricelist" in n.lower()]:
        for r in sheets[name]:
            add(r.get("C"), r.get("A"), r.get("B"))
    return master
