#!/usr/bin/env python3
"""
Generate File Exchange update templates and backup for weight/dimensions updates.
Run after fetch_all_listings.py to create ready-to-use CSV templates.

Usage:
    python create_update_files.py

Outputs:
    - BACKUP_listings_before_updates.csv (full backup of all listings)
    - TEMPLATE_ReviseInventory_ReviseInventory_WeightDims.csv (all 169 needing updates)
    - TEMPLATE_TEST_Top20.csv (top 20 revenue SKUs for safe testing)
    - INSTRUCTIONS_WeightDims_Update.txt (step-by-step guide)
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSIS_CSV = HERE.parent.parent.parent / "cache" / "documents" / "all_listings_analysis.csv"

def safe_int(v):
    try:
        return int(v) if v and v.isdigit() else 0
    except:
        return 0

def safe_float(v):
    try:
        return float(v) if v else 0.0
    except:
        return 0.0

def main():
    if not ANALYSIS_CSV.exists():
        print(f"Error: {ANALYSIS_CSV} not found. Run fetch_all_listings.py first.")
        return

    with open(ANALYSIS_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Add computed fields
    for r in rows:
        r['_revenue'] = safe_int(r['Sold Qty']) * safe_float(r['Current Price'])
        r['_has_weight'] = r['Package Weight'] and r['Package Weight'].strip() not in ('', '0', '0.0')
        r['_has_dims'] = r['Package Dimensions'] and r['Package Dimensions'].strip() != ''

    # Find listings missing weight and/or dimensions
    missing_both = [r for r in rows if not r['_has_weight'] and not r['_has_dims']]
    missing_weight = [r for r in rows if not r['_has_weight'] and r['_has_dims']]
    missing_dims = [r for r in rows if r['_has_weight'] and not r['_has_dims']]

    all_missing = missing_both + missing_weight + missing_dims
    seen = set()
    unique_missing = []
    for r in all_missing:
        if r['Item ID'] not in seen:
            seen.add(r['Item ID'])
            unique_missing.append(r)

    print(f"Missing both: {len(missing_both)}")
    print(f"Missing weight only: {len(missing_weight)}")
    print(f"Missing dims only: {len(missing_dims)}")
    print(f"Total unique: {len(unique_missing)}")

    # ---- 1. BACKUP ----
    backup_fields = [
        'ItemID', 'SKU', 'Title', 'Site', 'Current Price', 'Sold Qty', 'Available Qty',
        'Package Weight', 'Package Dimensions', 'WeightMajor', 'WeightMinor', 'WeightUnit',
        'PackageLength', 'PackageWidth', 'PackageDepth', 'MeasurementUnit',
        'ShippingProfile', 'Format', 'Category1ID', 'Category1Name'
    ]

    backup_path = HERE.parent.parent.parent / "cache" / "documents" / "BACKUP_listings_before_updates.csv"
    with open(backup_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=backup_fields)
        w.writeheader()
        for r in rows:
            # Parse existing weight
            w_major, w_minor, w_unit = '', '', ''
            pkg = r['Package Weight']
            if pkg:
                parts = pkg.split()
                for p in parts:
                    if 'kg' in p.lower():
                        w_major = p.replace('kg', '').replace('KG', '').strip()
                        w_unit = 'Kilograms'
                    elif 'gm' in p.lower() or 'g ' in p.lower():
                        w_minor = p.replace('gm', '').replace('g', '').strip()
                        if not w_unit:
                            w_unit = 'Grams'

            # Parse existing dims
            l, wd, d, m_unit = '', '', '', ''
            dims = r['Package Dimensions']
            if dims:
                parts = dims.replace('cm', '').split('x')
                if len(parts) >= 3:
                    l, wd, d = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    m_unit = 'Centimeters'

            w.writerow({
                'ItemID': r['Item ID'],
                'SKU': r['SKU'],
                'Title': r['Title'],
                'Site': r['Site'],
                'Current Price': r['Current Price'],
                'Sold Qty': r['Sold Qty'],
                'Available Qty': r['Available Qty'],
                'Package Weight': r['Package Weight'],
                'Package Dimensions': r['Package Dimensions'],
                'WeightMajor': w_major,
                'WeightMinor': w_minor,
                'WeightUnit': w_unit,
                'PackageLength': l,
                'PackageWidth': wd,
                'PackageDepth': d,
                'MeasurementUnit': m_unit,
                'ShippingProfile': r['Shipping Profile'],
                'Format': r['Format'],
                'Category1ID': r['Category 1 ID'],
                'Category1Name': r['Category 1 Name'],
            })

    print(f"✓ Backup: {backup_path}")

    # ---- 2. FULL TEMPLATE ----
    template_fields = [
        'Action', 'ItemID', 'SKU', 'Title',
        'PackageLength', 'PackageWidth', 'PackageDepth', 'MeasurementUnit',
        'WeightMajor', 'WeightMinor', 'WeightUnit',
        'ShippingProfileName',
        'CURRENT_Weight', 'CURRENT_Dims', 'CURRENT_ShippingProfile',
        'CURRENT_Site', 'CURRENT_Price', 'CATEGORY'
    ]

    full_template = HERE.parent.parent.parent / "cache" / "documents" / "TEMPLATE_ReviseInventory_WeightDims.csv"
    with open(full_template, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=template_fields)
        w.writeheader()
        for r in unique_missing:
            curr_w = r['Package Weight'] if r['Package Weight'] else 'MISSING'
            curr_d = r['Package Dimensions'] if r['Package Dimensions'] else 'MISSING'
            w.writerow({
                'Action': 'Revise',
                'ItemID': r['Item ID'],
                'SKU': r['SKU'] if r['SKU'] else '',
                'Title': r['Title'][:80],
                'PackageLength': '',
                'PackageWidth': '',
                'PackageDepth': '',
                'MeasurementUnit': 'Centimeters',
                'WeightMajor': '',
                'WeightMinor': '',
                'WeightUnit': 'Kilograms',
                'ShippingProfileName': r['Shipping Profile'] if r['Shipping Profile'] else '',
                'CURRENT_Weight': curr_w,
                'CURRENT_Dims': curr_d,
                'CURRENT_ShippingProfile': r['Shipping Profile'] if r['Shipping Profile'] else 'MISSING',
                'CURRENT_Site': r['Site'],
                'CURRENT_Price': r['Current Price'],
                'CATEGORY': r['Category 1 Name'][:50],
            })

    print(f"✓ Full template: {full_template} ({len(unique_missing)} rows)")

    # ---- 3. TOP 20 TEST TEMPLATE ----
    top20 = sorted(unique_missing, key=lambda x: x['_revenue'], reverse=True)[:20]
    test_template = HERE.parent.parent.parent / "cache" / "documents" / "TEMPLATE_TEST_Top20.csv"
    with open(test_template, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=template_fields)
        w.writeheader()
        for r in top20:
            curr_w = r['Package Weight'] if r['Package Weight'] else 'MISSING'
            curr_d = r['Package Dimensions'] if r['Package Dimensions'] else 'MISSING'
            w.writerow({
                'Action': 'Revise',
                'ItemID': r['Item ID'],
                'SKU': r['SKU'] if r['SKU'] else '',
                'Title': r['Title'][:80],
                'PackageLength': '',
                'PackageWidth': '',
                'PackageDepth': '',
                'MeasurementUnit': 'Centimeters',
                'WeightMajor': '',
                'WeightMinor': '',
                'WeightUnit': 'Kilograms',
                'ShippingProfileName': r['Shipping Profile'] if r['Shipping Profile'] else '',
                'CURRENT_Weight': curr_w,
                'CURRENT_Dims': curr_d,
                'CURRENT_ShippingProfile': r['Shipping Profile'] if r['Shipping Profile'] else 'MISSING',
                'CURRENT_Site': r['Site'],
                'CURRENT_Price': r['Current Price'],
                'CATEGORY': r['Category 1 Name'][:50],
            })

    print(f"✓ Test template (Top 20): {test_template}")

    # ---- 4. INSTRUCTIONS ----
    instructions = '''FILE EXCHANGE WEIGHT/DIMENSIONS UPDATE - INSTRUCTIONS
=========================================================

FILES CREATED:
1. BACKUP_listings_before_updates.csv - COMPLETE backup of all 561 listings
2. TEMPLATE_ReviseInventory_WeightDims.csv - Template for 169 listings needing updates
3. TEMPLATE_TEST_Top20.csv - Test template (top 20 revenue SKUs) - START HERE
4. INSTRUCTIONS_WeightDims_Update.txt - This file

HOW TO USE THE TEMPLATE:
-------------------------

1. OPEN TEMPLATE_TEST_Top20.csv in Excel/Google Sheets

2. FILL IN THE BLANK COLUMNS FOR EACH ROW:
   - PackageLength: Length in cm (e.g., 55)
   - PackageWidth: Width in cm (e.g., 40)  
   - PackageDepth: Depth/Height in cm (e.g., 25)
   - WeightMajor: Whole kilograms (e.g., 3 for 3kg)
   - WeightMinor: Grams (0-999) (e.g., 500 for 500g = 3.5kg total)
   
   EXAMPLES:
   - 3.5 kg suit: WeightMajor=3, WeightMinor=500
   - 500g tool: WeightMajor=0, WeightMinor=500
   - 1.2 kg item: WeightMajor=1, WeightMinor=200

3. KEEP THESE COLUMNS AS-IS (don't change):
   - Action = "Revise"
   - ItemID (must match exactly)
   - MeasurementUnit = "Centimeters"
   - WeightUnit = "Kilograms"
   - ShippingProfileName = your current profile (keeps shipping same)

4. DELETE THE REFERENCE COLUMNS BEFORE UPLOAD:
   - CURRENT_Weight
   - CURRENT_Dims
   - CURRENT_ShippingProfile
   - CURRENT_Site
   - CURRENT_Price
   - CATEGORY
   
   These are ONLY for your reference while filling in.

5. SAVE AS CSV (comma-delimited, UTF-8)

6. UPLOAD VIA FILE EXCHANGE:
   - Seller Hub → Tools → File Exchange
   - Choose "Upload Inventory File"
   - Select your filled CSV
   - Wait for processing email (15-60 minutes)

7. VERIFY:
   - Check File Exchange → "View Results" for errors
   - Spot-check 5 listings in Seller Hub
   - Verify "Package dimensions" and "Package weight" show
   - Test "Calculate shipping" with US/UK zip codes

SAFETY CHECKLIST:
-----------------
☐ Backup file saved (BACKUP_listings_before_updates.csv)
☐ Only filling PackageLength/Width/Depth, WeightMajor/Minor
☐ NOT changing ItemID, SKU, Title, Price, Format
☐ ShippingProfileName matches current (or leave blank to keep)
☐ Reference columns deleted before upload
☐ Test with 5-20 listings first (use TEMPLATE_TEST_Top20.csv)

COMMON WEIGHT/DIM ESTIMATES BY CATEGORY:
-----------------------------------------
Beekeeping Suit/Jacket:     1.5-3 kg,  55x40x25 cm
Gloves/Veils:               0.3-0.8 kg, 30x20x10 cm
Hive Box (assembled):       5-15 kg,   55x45x30 cm
Frames (10-pack):           2-4 kg,    50x40x15 cm
Wax Foundation (sheet):     0.05-0.1 kg, 42x20x1 cm
Honey Extractor (4-frame):  25-35 kg,  60x60x60 cm
Tools (hive tool, brush):   0.2-0.5 kg, 25x10x5 cm
Labels/Consumables:         0.1-0.5 kg, 25x15x5 cm

TROUBLESHOOTING:
----------------
- "Invalid weight": WeightMajor + WeightMinor must be > 0
- "Invalid dimensions": Provide all 3 or none
- "MeasurementUnit mismatch": Use "Centimeters" and "Kilograms" exactly
- "ProductID not found": GTIN valid but not in catalog - still upload
- "Item not found": ItemID wrong or listing ended
- "Shipping profile not found": Typo in profile name - copy exact from Seller Hub

ROLLBACK IF NEEDED:
-------------------
1. Open BACKUP_listings_before_updates.csv
2. Keep only: ItemID, PackageLength, PackageWidth, PackageDepth,
              WeightMajor, WeightMinor, MeasurementUnit, WeightUnit, ShippingProfile
3. Set Action=Revise
4. Upload via File Exchange
5. Or manually edit in Seller Hub for small batches

NEXT STEPS AFTER WEIGHT/DIMS:
-----------------------------
1. Add GTINs (UPC/EAN/ISBN) + ePIDs to top 50 revenue SKUs
2. Add missing SKUs to 162 listings
3. End 36 out-of-stock active listings
4. Add more photos to 258 listings with 1-2 images
5. Resolve 3 policy violation listings

Generated: July 2026 | 561 listings analyzed | 169 need weight/dims
'''

    instr_path = HERE.parent.parent.parent / "cache" / "documents" / "INSTRUCTIONS_WeightDims_Update.txt"
    with open(instr_path, 'w', encoding='utf-8') as f:
        f.write(instructions)

    print(f"✓ Instructions: {instr_path}")

if __name__ == '__main__':
    main()