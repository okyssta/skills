# Internal Data Enrichment for eBay Listings

## Overview
Process for combining eBay export data with internal systems (Shopify, ERP, Excel) to create complete File Exchange updates.

## Workflow Steps

### 1. Export eBay Data
- Use GetMyeBaySelling/GetItem API OR File Exchange "Download Active Inventory"
- Minimum fields needed: ItemID, Title, current Package Weight/Dims (if any), Shipping Profile, Site, Available Qty

### 2. Prepare Internal Sources
Ensure your CSV/Excel contains:
- **Item ID column**: Either direct eBay Item ID, or derivable from:
  - Product eBay URL (extract digits after `/itm/`)
  - SKU/UPC (if mapped in a lookup table)
- **Update fields**: Package Length/Width/Depth (cm), Weight (kg or g), etc.
- Keep column headers clean and consistent

### 3. Normalize Identifiers (Critical Step)
Handle these common format mismatches:

**Scientific Notation** (common in Excel/CSV):
```
1.47E+11  →  147035768999
1.36856E+11 → 136855807282
```
Conversion: `'{:.0f}'.format(float(value))`

**URL Extraction**:
From: `https://www.ebay.com.au/itm/100kg-Honey-Creamer-without-Melting-/147035768999`
Extract: `147035768999`
Regex: `r'/itm/(\d+)'`

**Whitespace/Quotes**:
Strip whitespace, remove surrounding quotes if present.

### 4. Build Lookup Maps
```python
# Example: Build dict from internal CSV
internal_data = {}
for row in internal_rows:
    item_id = normalize_id(row['ID'] or extract_from_url(row['Product eBay URL']))
    if item_id:
        internal_data[item_id] = {
            'weight_kg': parse_weight(row['Weight']),
            'length_cm': parse_dimension(row['Length']),
            # ... other fields
        }
```

### 5. Merge Data
```python
for ebay_item in ebay_listings:
    item_id = ebay_item['ItemID']
    
    # Start with eBay's current values
    updates = {
        'length': ebay_item.get('PackageLength') or None,
        'width': ebay_item.get('PackageWidth') or None,
        'depth': ebay_item.get('PackageDepth') or None,
        'weight_major': ebay_item.get('WeightMajor') or None,
        'weight_minor': ebay_item.get('WeightMinor') or None,
        'weight_unit': ebay_item.get('WeightUnit') or None,
    }
    
    # Override with internal data if available and eBay value is missing/invalid
    if item_id in internal_data:
        internal = internal_data[item_id]
        for field in ['length', 'width', 'depth', 'weight_kg']:
            if not updates[field] and internal.get(field):
                updates[field] = internal[field]
    
    # Convert to eBay format
    # ...
```

### 6. Generate File Exchange CSV
Required columns:
- Action: "Revise"
- ItemID: [eBay Item ID]
- PackageLength: [cm, as string]
- PackageWidth: [cm, as string]
- PackageDepth: [cm, as string]
- MeasurementUnit: "Centimeters"
- WeightMajor: [integer part, as string]
- WeightMinor: [fractional part * 1000, as string, zero-padded]
- WeightUnit: "Kilograms" or "Grams"
- Quantity: [current stock]
- ShippingProfileName: [existing eBay profile name]

### 7. Validate Before Upload
- Check for empty required fields
- Validate weight/minor < 1000
- Ensure dimensions are positive numbers
- Confirm ItemID exists in eBay export

## Common Issues & Solutions

### Problem: "Item not found" errors after upload
- **Cause**: ItemID mismatch (formatting issues)
- **Fix**: Verify all IDs are plain numeric strings, no scientific notation

### Problem: Weight rejected as invalid
- **Cause**: WeightMinor >= 1000 or incorrect units
- **Fix**: 
  - If weight_major is empty but weight_minor >= 1000: 
    - weight_major = weight_minor // 1000
    - weight_minor = weight_minor % 1000
  - Ensure WeightUnit matches magnitude (Kilograms vs Grams)

### Problem: No change reflected after upload
- **Cause**: Submitted values identical to existing values
- **Fix**: Only include fields that actually need updating

## Example: Processing a Row from single_variant_FINAL.csv

**Input Row**:
- Product eBay URL: `https://www.ebay.com.au/itm/100kg-Honey-Creamer-without-Melting-/147035768999`
- ID: `1.47036E+11` 
- Weight: `125kg`
- Dimensions: `80 x 60 x 100 cm`
- Quantity: `19`

**Processing**:
1. Extract ID from URL: `147035768999` (or normalize ID: `147036000000` → use URL version as more accurate)
2. Parse weight: 125kg → major=125, minor=0, unit=Kilograms
3. Parse dimensions: 80x60x100cm → L=80, W=60, H=100, unit=Centimeters
4. Quantity: 19

**Output Row**:
```
Action,ItemID,PackageLength,PackageWidth,PackageDepth,MeasurementUnit,WeightMajor,WeightMinor,WeightUnit,Quantity,ShippingProfileName
Revise,147035768999,80,60,100,Centimeters,125,0,Kilograms,19,Extractor Bulky
```

## Automation Script
See `scripts/create_file_exchange_from_internal.py` for a complete implementation that:
- Reads eBay export CSV
- Reads internal source CSV(s)
- Normalizes IDs
- Performs merge
- Outputs File Exchange-ready CSV
- Generates missing-items report