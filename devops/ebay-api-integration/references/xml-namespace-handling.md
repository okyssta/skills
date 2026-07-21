# XML Namespace Handling for eBay Trading API

## Problem
eBay Trading API responses use XML namespaces that must be handled correctly when parsing with ElementTree.

## Solution
Define a namespace helper function and use it consistently:

```python
import xml.etree.ElementTree as ET

API_URL = "https://api.ebay.com/ws/api.dll"
COMPAT_LEVEL = "1193"
NS = "urn:ebay:apis:eBLBaseComponents"
SITE_ID = "0"

def tag(name):
    """Return properly namespaced tag for eBay API XML elements"""
    return f"{{{NS}}}{name}"

def safe_text(elem, xpath):
    """Safely extract text from namespaced element"""
    if elem is None:
        return ""
    found = elem.find(xpath)
    return found.text if found is not None and found.text else ""
```

## Usage Examples

### Finding Elements
```python
item_id = item_elem.find(tag("ItemID"))
title = item_elem.find(tag("Title"))
```

### Accessing Attributes (Currency ID)
Price elements have currencyID as an attribute:
```python
start_price_elem = item_elem.find(tag("StartPrice"))
currency = start_price_elem.get("currencyID", "") if start_price_elem is not None else ""
start_price = start_price_elem.text if start_price_elem is not None else ""
```

### Handling ShippingPackageDetails
```python
pkg = item_elem.find(tag("ShippingPackageDetails"))
if pkg is not None:
    weight_major = pkg.find(tag("WeightMajor"))
    weight = ""
    if weight_major is not None:
        weight_val = weight_major.text or ""
        weight_unit = weight_major.get("unit", "")
        weight = f"{weight_val} {weight_unit}".strip()
```

## Common Pitfalls

### 1. Forgetting Namespaces
```python
# WRONG - will return None
item_id = item_elem.find("ItemID")

# CORRECT
item_id = item_elem.find(tag("ItemID"))
```

### 2. Misinterpreting Currency ID as Element
```python
# WRONG - looks for <currencyID>child</currencyID>
currency = item_elem.findtext(tag("StartPrice/currencyID"))

# CORRECT - currencyID is an attribute
start_price_elem = item_elem.find(tag("StartPrice"))
currency = start_price_elem.get("currencyID", "") if start_price_elem is not None else ""
```

### 3. Not Handling Missing Elements
```python
# Risky - AttributeError if element is None
weight = pkg.find(tag("WeightMajor")).text

# Safe
weight_major = pkg.find(tag("WeightMajor"))
weight = weight_major.text if weight_major is not None else ""
```

## Complete Example: Extracting Price with Currency
```python
def extract_price_info(item_elem):
    # Start Price
    start_price_elem = item_elem.find(tag("StartPrice"))
    start_price_currency = start_price_elem.get("currencyID", "") if start_price_elem is not None else ""
    start_price = start_price_elem.text if start_price_elem is not None else ""
    
    # Buy It Now Price
    bin_price_elem = item_elem.find(tag("BuyItNowPrice"))
    bin_price = bin_price_elem.text if bin_price_elem is not None else ""
    if bin_price_elem is not None and not start_price_currency:
        start_price_currency = bin_price_elem.get("currencyID", "")
    
    # Current Price
    current_price_elem = item_elem.find(f"{tag('SellingStatus')}/{tag('CurrentPrice')}")
    current_price = current_price_elem.text if current_price_elem is not None else ""
    if current_price_elem is not None and not start_price_currency:
        start_price_currency = current_price_elem.get("currencyID", "")
    
    return {
        "start_price": start_price,
        "start_price_currency": start_price_currency,
        "bin_price": bin_price,
        "current_price": current_price
    }
```