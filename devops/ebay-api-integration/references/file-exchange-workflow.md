---
title: eBay File Exchange Workflow for Bulk Updates
---

# eBay File Exchange — Bulk Update Workflow

## Overview
File Exchange is eBay's native bulk listing tool. Use for bulk updates to weight/dimensions, SKUs, GTINs, and other fields that don't require GetItem/ReviseItem API calls.

## When to Use File Exchange vs API

| Task | Method |
|------|--------|
| Update weight/dimensions for 100+ listings | File Exchange |
| Update SKU for 100+ listings | File Exchange |
| Add GTIN/UPC/EAN/ISBN | File Exchange |
| Add/Update Item Specifics | File Exchange |
| Update Price/Quantity | File Exchange |
| Update Title/Description | File Exchange |
| End/Relist listings | API (ReviseItem/EndItem) |
| Fetch full listing details | API (GetItem) |
| Real-time inventory sync | API (Inventory API) |

## Download Active Inventory Template

1. Seller Hub → Tools → File Exchange
2. "Download Active Inventory" 
3. Choose "Active Listings" → "All sites" or specific site
4. Wait for email with download link
5. Download CSV → opens in Excel

## Template Columns (Key Fields)

| Column | Purpose | Example |
|--------|---------|---------|
| Action | "Revise" for updates | Revise |
| ItemID | eBay listing ID | 123456789012 |
| SKU | Your SKU | MY-SKU-001 |
| CustomLabel | Alternative SKU field | MY-SKU-001 |
| PackageLength | Length in cm | 55 |
| PackageWidth | Width in cm | 40 |
| PackageDepth | Depth in cm | 25 |
| MeasurementUnit | "Centimeters" | Centimeters |
| WeightMajor | Whole kg | 2 |
| WeightMinor | Grams (0-999) | 500 |
| WeightUnit | "Kilograms" | Kilograms |
| ProductID:UPC | UPC code | 012345678905 |
| ProductID:EAN | EAN code | 1234567890128 |
| ProductID:ISBN | ISBN | 978-3-16-148410-0 |
| ProductID:ePID | eBay Product ID | 123456789 |
| C:Professional Grader | Trading card grader | PSA |
| C:Grade | Trading card grade | Gem Mint 10 |
| C:Certification Number | Cert number | 12345678 |
| C:Card Condition | Card condition | Near Mint |

## Update Process

### 1. Prepare CSV
- Keep only rows you're updating
- Keep only columns you're changing + ItemID + SKU
- Remove reference columns (CURRENT_*, CATEGORY, etc.)
- Save as CSV (UTF-8)

### 2. Upload
- File Exchange → "Upload Inventory File"
- Select file → Upload
- Wait for processing email (15-60 minutes)

### 3. Verify
- Check processing report for errors
- Spot-check 5-10 listings in Seller Hub
- Verify shipping calculates correctly on listing page

## Weight/Dimensions Bulk Update Template

```csv
Action,ItemID,SKU,PackageLength,PackageWidth,PackageDepth,MeasurementUnit,WeightMajor,WeightMinor,WeightUnit
Revise,123456789012,SUIT-001,55,40,25,Centimeters,2,500,Kilograms
Revise,123456789013,GLOVES-001,30,20,10,Centimeters,0,500,Kilograms
```

## GTIN/UPC Bulk Update Template

```csv
Action,ItemID,SKU,ProductID:UPC
Revise,123456789012,SUIT-001,012345678905
Revise,123456789013,GLOVES-001,012345678906
```

## SKU Bulk Update Template

```csv
Action,ItemID,CustomLabel,SKU
Revise,123456789012,NEW-SKU-001,NEW-SKU-001
```

## Trading Card Specifics Update

```csv
Action,ItemID,SKU,C:Professional Grader,C:Grade,C:Certification Number,C:Card Condition
Revise,123456789012,CARD-001,PSA,Gem Mint 10,12345678,Near Mint
```

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Invalid weight" | WeightMajor + WeightMinor = 0 | Ensure at least one > 0 |
| "Invalid dimensions" | One dimension provided but not all 3 | Provide all 3 or none |
| "MeasurementUnit mismatch" | Unit doesn't match site | Use Centimeters + Kilograms |
| "ProductID not found" | GTIN not in eBay catalog | GTIN valid but not cataloged - still upload |
| "Item not found" | ItemID wrong or ended | Verify ItemID in Active Listings |
| "Shipping profile not found" | Profile name typo | Match exact name from Seller Hub |

## Safety Checklist

- [ ] Backup current data (export active inventory first)
- [ ] Test with 5-10 listings first
- [ ] Keep reference columns separate (don't upload)
- [ ] Verify ShippingProfileName matches exactly
- [ ] Don't change ItemID, Action=Revise
- [ ] Check processing report for errors
- [ ] Spot-check updated listings

## Rollback Procedure

If something breaks:
1. Re-download Active Inventory (current state)
2. Create rollback CSV from backup with original values
3. Upload rollback CSV with Action=Revise
4. Or manually edit in Seller Hub for small batches