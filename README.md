# Merchant Center supplemental feed

Supplemental product data for Google Merchant Center account 5862533694
(Thousand Islands Pharmacy). Merchant Center's primary source is the
automated "Found by Google" crawl of thousandislandspharmacy.com, which
carries no product type or custom labels. This feed adds them so Google
Ads Shopping campaigns can split and exclude products by price tier and
category.

**Feed URL (scheduled fetch in Merchant Center):**
`https://thousandislandspharmacy.github.io/merchant-feed/price-tiers.txt`

| column | value |
|---|---|
| `id` | Google's offer ID = Shopify variant SKU, lower-cased, every run of non-alphanumerics -> `-` (verified against Merchant Center: `WA 5098-31` -> `wa-5098-31`, `TMS 10.790.20` -> `tms-10-790-20`) |
| `product_type` | Shopify product type (Incontinence, Wound Care, OSTOMY, ...) |
| `custom_label_0` | price tier: `under60`, `60to119`, `120plus` |
| `custom_label_1` | product type slug |
| `custom_label_2` | `recurring` (incontinence, ostomy, wound care, compression, enteral, respiratory, diabetic) or `one-off` |

Rebuilt daily by the GitHub Actions workflow from the public
`/products.json` endpoint; Merchant Center fetches it daily. To rebuild by
hand: `python build_feed.py price-tiers.txt`, commit, push.

Unit-economics background: dropship fee ~CA$15 + CA$13.95 shipping under
CA$135 means orders under ~CA$60 cannot pay for a paid click, so the Ads
campaign excludes `custom_label_0 = under60`.
