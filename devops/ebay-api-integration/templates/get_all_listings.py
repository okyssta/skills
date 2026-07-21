"""
Fetch ALL eBay listings across all sites and save to CSV.

Talks to the eBay Trading API, lists every active listing,
fetches full details, and saves ALL of them regardless of
which marketplace they're on. Includes price, condition,
listing type, quantity, and shipping details.

Setup:
    Put your eBay user token in `ebay_tokens.txt` (same folder,
    one token per line; lines starting with # are ignored).

Run:
    python get_all_listings.py

Output:
    all_products.csv

Standard library only - no pip installs needed.
"""

import csv
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

API_URL = "https://api.ebay.com/ws/api.dll"
COMPAT_LEVEL = "1193"
NS = "urn:ebay:apis:eBLBaseComponents"
SITE_ID = "15"  # AU marketplace — still returns ALL sites
HERE = Path(__file__).resolve().parent
TOKENS_FILE = HERE / "ebay_tokens.txt"
OUTPUT_CSV = HERE / "all_products.csv"
DELAY_BETWEEN_CALLS = 0.25


def out(msg):
    print(msg, flush=True)


def tag(name):
    return f"{{{NS}}}{name}"


def build_request(call_name, inner_xml, token, auth_mode):
    credentials = ""
    if auth_mode == "authnauth":
        credentials = (
            "<RequesterCredentials>"
            f"<eBayAuthToken>{token}</eBayAuthToken>"
            "</RequesterCredentials>"
        )
    body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        f'<{call_name}Request xmlns="{NS}">'
        f"{credentials}{inner_xml}"
        f"</{call_name}Request>"
    )
    headers = {
        "X-EBAY-API-COMPATIBILITY-LEVEL": COMPAT_LEVEL,
        "X-EBAY-API-CALL-NAME": call_name,
        "X-EBAY-API-SITEID": SITE_ID,
        "Content-Type": "text/xml",
    }
    if auth_mode == "oauth":
        headers["X-EBAY-API-IAF-TOKEN"] = token
    return body.encode("utf-8"), headers


def call_api(call_name, inner_xml, token, auth_mode, retries=3):
    body, headers = build_request(call_name, inner_xml, token, auth_mode)
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(API_URL, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
        except (urllib.error.URLError, OSError) as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
            continue
        root = ET.fromstring(raw)
        ack = root.findtext(tag("Ack"), default="")
        if ack in ("Success", "Warning"):
            return root, None
        errors = []
        for err in root.iter(tag("Errors")):
            code = err.findtext(tag("ErrorCode"), default="")
            msg = err.findtext(tag("LongMessage"), default="") or err.findtext(
                tag("ShortMessage"), default=""
            )
            errors.append((code, msg))
        err_text = "; ".join(f"[{c}] {m}" for c, m in errors) or "Unknown API error"
        if any(c in ("218050", "21919165") for c, _ in errors):
            time.sleep(10 * (attempt + 1))
            last_err = err_text
            continue
        return root, err_text
    return None, str(last_err)


def detect_auth_mode(token):
    for mode in ("oauth", "authnauth"):
        root, err = call_api(
            "GetMyeBaySelling",
            "<ActiveList><Include>true</Include>"
            "<Pagination><EntriesPerPage>1</EntriesPerPage>"
            "<PageNumber>1</PageNumber></Pagination></ActiveList>",
            token, mode,
        )
        if root is not None and err is None:
            return mode
    return None


def get_all_active_item_ids(token, auth_mode):
    item_ids = []
    page = 1
    while True:
        inner = (
            "<ActiveList><Include>true</Include>"
            "<Pagination><EntriesPerPage>200</EntriesPerPage>"
            f"<PageNumber>{page}</PageNumber></Pagination></ActiveList>"
        )
        root, err = call_api("GetMyeBaySelling", inner, token, auth_mode)
        if err:
            out(f"  ERROR page {page}: {err}")
            break
        active = root.find(tag("ActiveList"))
        if active is None:
            break
        items = active.findall(f"{tag('ItemArray')}/{tag('Item')}")
        for it in items:
            iid = it.findtext(tag("ItemID"))
            if iid:
                item_ids.append(iid)
        total_pages = int(
            active.findtext(
                f"{tag('PaginationResult')}/{tag('TotalNumberOfPages')}", default="1"
            ) or 1
        )
        out(f"  page {page}/{total_pages}: {len(item_ids)} items so far")
        if page >= total_pages or not items:
            break
        page += 1
        time.sleep(DELAY_BETWEEN_CALLS)
    return item_ids


def text_with_unit(elem):
    if elem is None or elem.text is None:
        return None, None
    return elem.text.strip(), elem.get("unit", "")


def get_item_details(item_id, token, auth_mode):
    root, err = call_api("GetItem", f"<ItemID>{item_id}</ItemID>", token, auth_mode)
    if err:
        return {"item_id": item_id, "site": "", "title": "", "url": "",
                "start_price": "", "currency": "", "condition": "",
                "listing_type": "", "policy": f"ERROR: {err}",
                "weight": "", "dimensions": "", "available_qty": "",
                "quantity": "", "quantity_sold": ""}

    item = root.find(tag("Item"))
    if item is None:
        return {"item_id": item_id, "site": "", "title": "", "url": "",
                "start_price": "", "currency": "", "condition": "",
                "listing_type": "", "policy": "ERROR: no Item",
                "weight": "", "dimensions": "", "available_qty": "",
                "quantity": "", "quantity_sold": ""}

    site = item.findtext(tag("Site"), default="")
    title = item.findtext(tag("Title"), default="")
    url = item.findtext(f"{tag('ListingDetails')}/{tag('ViewItemURL')}", default="")
    policy = item.findtext(
        f"{tag('SellerProfiles')}/{tag('SellerShippingProfile')}/{tag('ShippingProfileName')}",
        default="",
    )
    start_price_el = item.find(tag("StartPrice"))
    start_price = start_price_el.text.strip() if start_price_el is not None and start_price_el.text else ""
    currency = start_price_el.get("currencyID", "") if start_price_el is not None else ""
    condition = item.findtext(f"{tag('ConditionDisplayName')}", default="")
    listing_type = item.findtext(tag("ListingType"), default="")

    pkg = item.find(tag("ShippingPackageDetails"))
    weight = ""
    dimensions = ""
    if pkg is not None:
        wmaj, wmaj_u = text_with_unit(pkg.find(tag("WeightMajor")))
        wmin, wmin_u = text_with_unit(pkg.find(tag("WeightMinor")))
        parts = []
        if wmaj and wmaj != "0":
            parts.append(f"{wmaj} {wmaj_u}".strip())
        if wmin and wmin != "0":
            parts.append(f"{wmin} {wmin_u}".strip())
        weight = " ".join(parts)
        length, len_u = text_with_unit(pkg.find(tag("PackageLength")))
        width, _ = text_with_unit(pkg.find(tag("PackageWidth")))
        depth, _ = text_with_unit(pkg.find(tag("PackageDepth")))
        dims = [d for d in (length, width, depth) if d]
        if dims:
            dimensions = " x ".join(dims) + (f" {len_u}" if len_u else "")

    qty_total = item.findtext(tag("Quantity"), default="")
    qty_sold = item.findtext(f"{tag('SellingStatus')}/{tag('QuantitySold')}", default="0")
    try:
        available = str(int(qty_total) - int(qty_sold))
    except (ValueError, TypeError):
        available = qty_total

    return {"item_id": item_id, "site": site, "title": title, "url": url,
            "start_price": start_price, "currency": currency,
            "condition": condition, "listing_type": listing_type,
            "policy": policy, "weight": weight, "dimensions": dimensions,
            "available_qty": available, "quantity": qty_total,
            "quantity_sold": qty_sold}


def main():
    if not TOKENS_FILE.exists():
        out(f"Token file not found: {TOKENS_FILE}")
        sys.exit(1)
    tokens = [l.strip() for l in TOKENS_FILE.read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.strip().startswith("#")]
    if not tokens:
        out("ebay_tokens.txt is empty.")
        sys.exit(1)
    token = tokens[0]

    auth_mode = detect_auth_mode(token)
    if auth_mode is None:
        out("ERROR: token rejected by eBay (expired or wrong account?).")
        sys.exit(1)
    out(f"auth mode: {auth_mode}")
    out("collecting active listing IDs...")
    item_ids = list(dict.fromkeys(get_all_active_item_ids(token, auth_mode)))
    out(f"total active listings returned: {len(item_ids)}")

    all_rows = []
    for i, iid in enumerate(item_ids, 1):
        d = get_item_details(iid, token, auth_mode)
        all_rows.append(d)
        if i % 25 == 0 or i == len(item_ids):
            out(f"  processed {i}/{len(item_ids)}")
        time.sleep(DELAY_BETWEEN_CALLS)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "Item ID", "Site", "Title", "Product URL",
            "Start Price", "Currency", "Condition", "Listing Type",
            "Postage Policy", "Package Weight", "Package Dimensions",
            "Quantity Total", "Quantity Sold", "Available Qty",
            "Missing Weight", "Missing Dimensions", "Make Out Of Stock"
        ])
        for r in all_rows:
            mw = r["weight"].strip() in ("", "0", "0.0")
            md = r["dimensions"].strip() == ""
            w.writerow([
                r["item_id"], r["site"], r["title"], r["url"],
                r["start_price"], r["currency"], r["condition"], r["listing_type"],
                r["policy"], r["weight"], r["dimensions"],
                r["quantity"], r["quantity_sold"], r["available_qty"],
                "YES" if mw else "no", "YES" if md else "no",
                "YES" if (mw or md) else "no"
            ])

    site_counts = {}
    for r in all_rows:
        s = r["site"] or "(unknown)"
        site_counts[s] = site_counts.get(s, 0) + 1

    out("")
    out("=" * 50)
    out("SUMMARY")
    out("=" * 50)
    flagged = sum(1 for r in all_rows if r["weight"].strip() in ("", "0", "0.0") or r["dimensions"].strip() == "")
    zero_qty = sum(1 for r in all_rows if r["available_qty"].strip() == "0")
    out(f"Total listings: {len(all_rows)}")
    out(f"Complete (weight + dims): {len(all_rows) - flagged}")
    out(f"Flagged (missing weight or dims): {flagged}")
    out(f"Out of stock (0 available): {zero_qty}")
    out(f"Saved -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
