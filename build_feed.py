"""Build the Merchant Center supplemental feed for Thousand Islands Pharmacy.

Reads every published product from the public storefront (products.json),
derives the offer ID exactly the way Google's "Found by Google" automated
source does (lower-case SKU, whitespace -> hyphen), and writes a TSV with:

  id              offer id (matches Merchant Center "Product ID" column)
  product_type    Shopify product type (lets Google Ads split by type)
  custom_label_0  price tier:  under60 | 60to119 | 120plus
  custom_label_1  product type slug (same as product_type, hyphenated)
  custom_label_2  recurring | one-off  (recurring-supply categories)

Usage:  python build_feed.py [out_path]
"""
import csv, json, re, sys, time, urllib.request

STORE = "https://thousandislandspharmacy.com/products.json?limit=250&page={}"
OUT = sys.argv[1] if len(sys.argv) > 1 else "price-tiers.txt"

RECURRING = {
    "Incontinence", "OSTOMY", "OSTOMY ACCESSORIES", "Wound Care",
    "Compression Socks", "Enteral Feeding", "Respiratory", "Diabetic",
}


def offer_id(sku: str) -> str:
    """Mirror Google's automated-feed ID derivation (verified against MC)."""
    s = sku.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def tier(price: str) -> str:
    p = float(price)
    if p < 60:
        return "under60"
    if p < 120:
        return "60to119"
    return "120plus"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "none"


def fetch_all():
    page = 1
    while True:
        req = urllib.request.Request(STORE.format(page), headers={"User-Agent": "Mozilla/5.0 feed-builder"})
        with urllib.request.urlopen(req, timeout=60) as r:
            prods = json.load(r).get("products", [])
        if not prods:
            return
        for p in prods:
            yield p
        page += 1
        time.sleep(0.3)


def main():
    rows, seen = [], set()
    for p in fetch_all():
        ptype = (p.get("product_type") or "").strip()
        for v in p["variants"]:
            sku = (v.get("sku") or "").strip()
            if not sku:
                continue
            oid = offer_id(sku)
            if oid in seen:
                continue
            seen.add(oid)
            rows.append({
                "id": oid,
                "product_type": ptype,
                "custom_label_0": tier(v["price"]),
                "custom_label_1": slug(ptype),
                "custom_label_2": "recurring" if ptype in RECURRING else "one-off",
            })
    rows.sort(key=lambda r: r["id"])
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "product_type", "custom_label_0", "custom_label_1", "custom_label_2"],
                           delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(f"wrote {len(rows)} rows to {OUT}")
    print("tiers:", dict(Counter(r["custom_label_0"] for r in rows)))
    print("recurring:", dict(Counter(r["custom_label_2"] for r in rows)))


if __name__ == "__main__":
    main()
