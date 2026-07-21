#!/usr/bin/env python3
"""
Parallel eBay Listings Analysis Script

Fetches all active listings via GetMyeBaySelling, then uses ThreadPoolExecutor
to fetch full details via GetItem in parallel. Outputs CSV with issue detection.

Usage:
    python fetch_all_listings.py

Requires:
    - ebay_tokens.txt in same directory (one OAuth token per line, # for comments)
    - Python 3.7+

Outputs:
    - all_listings_analysis.csv (full dataset)
    - listings_with_issues.csv (only problematic listings)
    - missing_sku.csv (listings without SKU)
    - out_of_stock.csv (active listings with 0 available qty)
    - trading_cards_analysis.csv (trading card subset)
"""

import csv
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ==================== CONFIGURATION ====================
API_URL = "https://api.ebay.com/ws/api.dll"
COMPAT_LEVEL = "1193"
NS = "urn:ebay:apis:eBLBaseComponents"
SITE_ID = "0"  # Use US site for GetMyeBaySelling to get all sites
MAX_WORKERS = 8
DELAY_BETWEEN_CALLS = 0.05

HERE = Path(__file__).resolve().parent
TOKENS_FILE = HERE / "ebay_tokens.txt"
OUTPUT_CSV = HERE / "all_listings_analysis.csv"

# Trading card category IDs
TC_CATEGORIES = {"27501", "27502", "261328", "261332", "261336", "183454", "261324", "261340"}

# ==================== HELPERS ====================
thread_local = threading.local()

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
            token,
            mode,
        )
        if root is not None and err is None:
            return mode
    return None

def safe_text(elem, xpath):
    if elem is None:
        return ""
    found = elem.find(xpath)
    return found.text if found is not None and found.text else ""

def get_all_active_item_ids(token, auth_mode):
    """Get all active ItemIDs from GetMyeBaySelling."""
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
            out(f"  ERROR listing page {page}: {err}")
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
            )
            or 1
        )
        out(f"  page {page}/{total_pages}: {len(item_ids)} items so far")
        if page >= total_pages or not items:
            break
        page += 1
        time.sleep(DELAY_BETWEEN_CALLS)
    return item_ids

def extract_item_data(item_elem):
    """Extract all relevant fields from a GetItem response Item element."""
    # Basic identifiers
    item_id = safe_text(item_elem, tag("ItemID"))
    sku = safe_text(item_elem, tag("SKU")) or safe_text(item_elem, tag("CustomLabel"))
    title = safe_text(item_elem, tag("Title"))
    
    # Site & URL
    site = safe_text(item_elem, tag("Site"))
    url = safe_text(item_elem, f"{tag('ListingDetails')}/{tag('ViewItemURL')}")
    
    # Format & pricing
    listing_type = safe_text(item_elem, tag("ListingType"))
    start_price_elem = item_elem.find(tag("StartPrice"))
    currency = start_price_elem.get("currencyID", "") if start_price_elem is not None else ""
    start_price = safe_text(item_elem, tag("StartPrice"))
    bin_price_elem = item_elem.find(tag("BuyItNowPrice"))
    bin_price = bin_price_elem.text if bin_price_elem is not None else ""
    if bin_price_elem is not None and not currency:
        currency = bin_price_elem.get("currencyID", "")
    reserve_price = safe_text(item_elem, tag("ReservePrice"))
    current_price_elem = item_elem.find(f"{tag('SellingStatus')}/{tag('CurrentPrice')}")
    current_price = current_price_elem.text if current_price_elem is not None else ""
    if current_price_elem is not None and not currency:
        currency = current_price_elem.get("currencyID", "")
    
    # Quantities
    qty_total = safe_text(item_elem, tag("Quantity"))
    qty_sold = safe_text(item_elem, f"{tag('SellingStatus')}/{tag('QuantitySold')}")
    try:
        available = str(int(qty_total) - int(qty_sold)) if qty_total and qty_sold else qty_total
    except (ValueError, TypeError):
        available = qty_total
    
    # Dates
    start_date = safe_text(item_elem, tag("StartTime"))
    end_date = safe_text(item_elem, tag("EndTime"))
    
    # Category
    cat1_name = safe_text(item_elem, f"{tag('PrimaryCategory')}/{tag('CategoryName')}")
    cat1_id = safe_text(item_elem, f"{tag('PrimaryCategory')}/{tag('CategoryID')}")
    cat2_name = safe_text(item_elem, f"{tag('SecondaryCategory')}/{tag('CategoryName')}")
    cat2_id = safe_text(item_elem, f"{tag('SecondaryCategory')}/{tag('CategoryID')}")
    
    # Condition
    condition_id = safe_text(item_elem, tag("ConditionID"))
    condition_name = safe_text(item_elem, tag("ConditionDisplayName"))
    
    # Item specifics
    specifics = {}
    for ns in item_elem.findall(f"{tag('ItemSpecifics')}/{tag('NameValueList')}"):
        name = safe_text(ns, tag("Name"))
        value = safe_text(ns, tag("Value"))
        if name:
            specifics[name] = value
    
    # Trading card specifics
    prof_grader = specifics.get("Professional Grader", "")
    grade = specifics.get("Grade", "")
    cert_number = specifics.get("Certification Number", "")
    card_condition = specifics.get("Card Condition", "")
    
    # Product identifiers
    epid = safe_text(item_elem, tag("ProductID"))
    upc = specifics.get("UPC", "") or specifics.get("UPC/EAN", "")
    ean = specifics.get("EAN", "")
    isbn = specifics.get("ISBN", "")
    
    # Shipping profile
    policy = safe_text(item_elem, f"{tag('SellerProfiles')}/{tag('SellerShippingProfile')}/{tag('ShippingProfileName')}")
    
    # Package details
    pkg = item_elem.find(tag("ShippingPackageDetails"))
    weight = ""
    dimensions = ""
    if pkg is not None:
        wmaj = safe_text(pkg, tag("WeightMajor"))
        wmin = safe_text(pkg, tag("WeightMinor"))
        wmaj_unit = pkg.find(tag("WeightMajor")).get("unit", "") if pkg.find(tag("WeightMajor")) is not None else ""
        wmin_unit = pkg.find(tag("WeightMinor")).get("unit", "") if pkg.find(tag("WeightMinor")) is not None else ""
        parts = []
        if wmaj and wmaj != "0":
            parts.append(f"{wmaj} {wmaj_unit}".strip())
        if wmin and wmin != "0":
            parts.append(f"{wmin} {wmin_unit}".strip())
        weight = " ".join(parts)
        
        length = safe_text(pkg, tag("PackageLength"))
        width = safe_text(pkg, tag("PackageWidth"))
        depth = safe_text(pkg, tag("PackageDepth"))
        len_unit = pkg.find(tag("PackageLength")).get("unit", "") if pkg.find(tag("PackageLength")) is not None else ""
        dims = [d for d in (length, width, depth) if d]
        if dims:
            dimensions = " x ".join(dims) + (f" {len_unit}" if len_unit else "")
    
    # Watchers, bids
    watchers = safe_text(item_elem, f"{tag('SellingStatus')}/{tag('WatchCount')}")
    bids = safe_text(item_elem, f"{tag('SellingStatus')}/{tag('BidCount')}")
    
    # Pictures
    pic_urls = item_elem.findall(f"{tag('PictureDetails')}/{tag('PictureURL')}")
    pic_count = len(pic_urls)
    gallery_url = safe_text(item_elem, f"{tag('PictureDetails')}/{tag('GalleryURL')}")
    
    # Issue detection
    issues = []
    if not title or len(title) < 15:
        issues.append("Short/Empty Title")
    if not sku:
        issues.append("Missing SKU")
    if not cat1_id:
        issues.append("Missing Category")
    if not condition_id:
        issues.append("Missing Condition")
    if not upc and not ean and not isbn:
        issues.append("Missing UPC/EAN/ISBN")
    if not epid:
        issues.append("Missing ePID")
    if not weight:
        issues.append("Missing Package Weight")
    if not dimensions:
        issues.append("Missing Package Dimensions")
    if not policy:
        issues.append("Missing Shipping Profile")
    if listing_type == "Chinese" and not bin_price:
        issues.append("Auction without BIN")
    if available == "0":
        issues.append("Out of Stock")
    if pic_count == 0:
        issues.append("No Images")
    elif pic_count < 3:
        issues.append(f"Few Images ({pic_count})")
    
    # Trading card specific issues
    if cat1_id in TC_CATEGORIES:
        if not prof_grader:
            issues.append("TC: Missing Professional Grader")
        if not grade:
            issues.append("TC: Missing Grade")
        if not cert_number:
            issues.append("TC: Missing Cert Number")
        if not card_condition:
            issues.append("TC: Missing Card Condition")
    
    return {
        "Item ID": item_id,
        "SKU": sku,
        "Title": title,
        "Site": site,
        "URL": url,
        "Format": listing_type,
        "Currency": currency,
        "Start Price": start_price,
        "BIN Price": bin_price,
        "Reserve Price": reserve_price,
        "Current Price": current_price,
        "Total Qty": qty_total,
        "Sold Qty": qty_sold,
        "Available Qty": available,
        "Start Date": start_date,
        "End Date": end_date,
        "Category 1 Name": cat1_name,
        "Category 1 ID": cat1_id,
        "Category 2 Name": cat2_name,
        "Category 2 ID": cat2_id,
        "Condition ID": condition_id,
        "Condition Name": condition_name,
        "Professional Grader": prof_grader,
        "Grade": grade,
        "Certification Number": cert_number,
        "Card Condition": card_condition,
        "ePID": epid,
        "UPC": upc,
        "EAN": ean,
        "ISBN": isbn,
        "Shipping Profile": policy,
        "Package Weight": weight,
        "Package Dimensions": dimensions,
        "Watchers": watchers,
        "Bids": bids,
        "Picture Count": pic_count,
        "Gallery URL": gallery_url,
        "Issues": "; ".join(issues) if issues else "OK",
        "Issue Count": len(issues),
    }

def fetch_item_details(item_id, token, auth_mode):
    """Fetch single item details via GetItem."""
    root, err = call_api("GetItem", f"<ItemID>{item_id}</ItemID>", token, auth_mode)
    if err:
        return {
            "Item ID": item_id,
            "SKU": "", "Title": "", "Site": "", "URL": "",
            "Format": "", "Currency": "", "Start Price": "", "BIN Price": "",
            "Reserve Price": "", "Current Price": "", "Total Qty": "", "Sold Qty": "",
            "Available Qty": "", "Start Date": "", "End Date": "",
            "Category 1 Name": "", "Category 1 ID": "", "Category 2 Name": "", "Category 2 ID": "",
            "Condition ID": "", "Condition Name": "",
            "Professional Grader": "", "Grade": "", "Certification Number": "", "Card Condition": "",
            "ePID": "", "UPC": "", "EAN": "", "ISBN": "",
            "Shipping Profile": "", "Package Weight": "", "Package Dimensions": "",
            "Watchers": "", "Bids": "", "Picture Count": 0, "Gallery URL": "",
            "Issues": f"API ERROR: {err}", "Issue Count": 1,
        }
    item = root.find(tag("Item"))
    if item is None:
        return {
            "Item ID": item_id,
            "SKU": "", "Title": "", "Site": "", "URL": "",
            "Format": "", "Currency": "", "Start Price": "", "BIN Price": "",
            "Reserve Price": "", "Current Price": "", "Total Qty": "", "Sold Qty": "",
            "Available Qty": "", "Start Date": "", "End Date": "",
            "Category 1 Name": "", "Category 1 ID": "", "Category 2 Name": "", "Category 2 ID": "",
            "Condition ID": "", "Condition Name": "",
            "Professional Grader": "", "Grade": "", "Certification Number": "", "Card Condition": "",
            "ePID": "", "UPC": "", "EAN": "", "ISBN": "",
            "Shipping Profile": "", "Package Weight": "", "Package Dimensions": "",
            "Watchers": "", "Bids": "", "Picture Count": 0, "Gallery URL": "",
            "Issues": "API ERROR: No Item in response", "Issue Count": 1,
        }
    return extract_item_data(item)

def write_csv(rows, path, fieldnames):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    if not TOKENS_FILE.exists():
        out(f"Token file not found: {TOKENS_FILE}")
        sys.exit(1)
    tokens = [
        l.strip()
        for l in TOKENS_FILE.read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    if not tokens:
        out("ebay_tokens.txt is empty.")
        sys.exit(1)
    token = tokens[0]

    auth_mode = detect_auth_mode(token)
    if auth_mode is None:
        out("ERROR: token rejected by eBay (expired or wrong account?).")
        sys.exit(1)
    out(f"auth mode: {auth_mode}")

    # Step 1: Get all ItemIDs
    out("Fetching all active ItemIDs...")
    item_ids = get_all_active_item_ids(token, auth_mode)
    out(f"Total active listings: {len(item_ids)}")

    # Step 2: Parallel GetItem calls
    out(f"Fetching details for {len(item_ids)} listings with {MAX_WORKERS} workers...")
    all_rows = []
    completed = 0
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {executor.submit(fetch_item_details, iid, token, auth_mode): iid for iid in item_ids}
        for future in as_completed(future_to_id):
            result = future.result()
            all_rows.append(result)
            completed += 1
            if completed % 50 == 0 or completed == len(item_ids):
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (len(item_ids) - completed) / rate if rate > 0 else 0
                out(f"  {completed}/{len(item_ids)} ({rate:.1f}/sec, ETA: {eta:.0f}s)")

    out(f"\nCompleted {len(all_rows)} listings in {time.time() - start_time:.1f}s")

    # Write outputs
    fieldnames = list(all_rows[0].keys())
    
    # Full dataset
    write_csv(all_rows, OUTPUT_CSV, fieldnames)
    out(f"Saved full data -> {OUTPUT_CSV}")

    # Issues only
    issues_only = [r for r in all_rows if r["Issue Count"] > 0]
    if issues_only:
        write_csv(issues_only, HERE / "listings_with_issues.csv", fieldnames)
        out(f"Issues-only CSV -> {HERE / 'listings_with_issues.csv'} ({len(issues_only)} rows)")

    # Missing SKU
    missing_sku = [r for r in all_rows if not r.get("SKU")]
    if missing_sku:
        write_csv(missing_sku, HERE / "missing_sku.csv", fieldnames)
        out(f"Missing SKU: {len(missing_sku)} -> {HERE / 'missing_sku.csv'}")

    # Out of stock
    oos = [r for r in all_rows if r.get("Available Qty") == "0"]
    if oos:
        write_csv(oos, HERE / "out_of_stock.csv", fieldnames)
        out(f"Out of Stock: {len(oos)} -> {HERE / 'out_of_stock.csv'}")

    # Trading cards
    tc_rows = [r for r in all_rows if r.get("Category 1 ID") in TC_CATEGORIES]
    if tc_rows:
        write_csv(tc_rows, HERE / "trading_cards_analysis.csv", fieldnames)
        tc_issues = sum(1 for r in tc_rows if r["Issue Count"] > 0)
        out(f"Trading Cards: {len(tc_rows)} listings, {tc_issues} with issues -> {HERE / 'trading_cards_analysis.csv'}")

    # Summary
    total = len(all_rows)
    with_issues = sum(1 for r in all_rows if r["Issue Count"] > 0)
    by_format = {}
    by_site = {}
    by_category = {}
    issue_counts = {}
    
    for r in all_rows:
        by_format[r.get("Format", "Unknown")] = by_format.get(r.get("Format", "Unknown"), 0) + 1
        by_site[r.get("Site", "Unknown")] = by_site.get(r.get("Site", "Unknown"), 0) + 1
        cat = r.get("Category 1 ID", "Unknown") or "Unknown"
        by_category[cat] = by_category.get(cat, 0) + 1
        if r.get("Issues", "OK") != "OK":
            for issue in r["Issues"].split("; "):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

    out(f"\n=== SUMMARY ===")
    out(f"Total listings: {total}")
    out(f"With issues: {with_issues} ({with_issues/total*100:.1f}%)")
    out(f"Clean: {total - with_issues} ({(total-with_issues)/total*100:.1f}%)")
    out(f"\nBy Format: {by_format}")
    out(f"\nBy Site: {by_site}")
    out(f"\nTop Categories: {dict(sorted(by_category.items(), key=lambda x: -x[1])[:15])}")
    out(f"\nTop Issues:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:25]:
        out(f"  {issue}: {count}")

if __name__ == "__main__":
    main()