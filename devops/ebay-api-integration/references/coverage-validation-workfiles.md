# Coverage Validation: Cross-Referencing Work Files Against eBay API Export

## Problem
A seller prepares weight/dimensions data in CSV/TSV files (single_variant, multi_variant, etc.) and wants to know: does this data cover ALL my flagged eBay listings, or are there gaps?

## Root Cause
- eBay API export (`all_products.csv`) uses full integer Item IDs
- Work files from spreadsheets use scientific notation (`1.47E+11`) or different column formats
- IDs may also be embedded in eBay URLs rather than in an ID column
- Different files use different delimiters (CSV vs TSV)

## Cross-Reference Workflow

### 1. Load eBay Master Export
```python
import csv

all_prods = list(csv.DictReader(open("all_products.csv")))
all_by_id = {r["Item ID"].strip(): r for r in all_prods if r["Item ID"].strip()}
flagged_ids = {r["Item ID"].strip() for r in all_prods
               if r.get("Missing Weight") == "YES" or r.get("Missing Dimensions") == "YES"}
```

### 2. Auto-Detect Delimiter Per File
```python
def load_workfile(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        first = f.readline()
        delim = "\t" if "\t" in first else ","
    return list(csv.DictReader(open(filepath, "r", encoding="utf-8-sig"), delimiter=delim))
```

### 3. Extract Item IDs from eBay URLs
eBay URL formats:
- `https://www.ebay.com.au/itm/TITLE-/123456789012` (trailing dash before ID)
- `https://www.ebay.com/itm/TITLE-123456789012` (no trailing dash)

```python
import re
def extract_ebay_id(url):
    """Extract Item ID from eBay product URL. Returns None if not found."""
    if not url:
        return None
    m = re.search(r'/(\d{9,})$', url)
    return m.group(1) if m else None
```

### 4. Build Coverage Map
```python
def extract_ids(rows, url_field="Product eBay URL"):
    ids = set()
    for r in rows:
        url = r.get(url_field, "") or ""
        iid = extract_ebay_id(url)
        if iid and len(iid) >= 9:
            ids.add(iid)
    return ids

# Load each work file
sv = load_workfile("single_variant.csv")
sv_master = load_workfile("single_variant_master.csv")
multi = load_workfile("multi_variant.csv")
unresolved = load_workfile("unresolved.csv")

# Extract IDs
sv_ids = extract_ids(sv)
multi_ids = extract_ids(multi)
unresolved_ids = extract_ids(unresolved)

# Combine
all_work_ids = set().union(sv_ids, multi_ids, unresolved_ids)
```

### 5. Find Gaps
```python
covered = flagged_ids & all_work_ids
uncovered = flagged_ids - all_work_ids

print(f"Flagged items: {len(flagged_ids)}")
print(f"Covered by work files: {len(covered)}")
print(f"Still uncovered: {len(uncovered)}")
```

### 6. Prioritize Gaps
For each uncovered item, check:
- **Site**: AU vs US vs UK vs unknown
- **Available Qty**: >0 = urgent (losing sales), =0 = can wait
- **Title**: helps identify which product it is

```python
for iid in sorted(uncovered):
    r = all_by_id[iid]
    site = r.get("Site", "?")
    qty = int(r.get("Available Qty", "0") or "0")
    title = r.get("Title", "")[:60]
    urgency = "URGENT" if qty > 0 else "LOW"
    print(f"  [{urgency}] {site:10s} Qty:{qty:>4d}  {title}")
```

## Real-World Example (Jul 2026, OZ ARMOUR Beekeeping)

| Metric | Count |
|--------|-------|
| Total listings | 561 |
| Flagged (missing wt+dims) | 169 |
| Covered by work files | 26 (all AU) |
| Still uncovered | 143 (100 US + 40 UK + 3 unknown) |
| Uncovered WITH stock (urgent) | ~140 |

**Key finding**: Weight/dimensions are **product-level**, not site-level. US/UK cross-lists of the same AU products should use the same weight/dims. The API shows them empty because cross-list shipping config doesn't auto-populate.

## Common File Patterns

| Filename | Delimiter | Content | ID Source |
|----------|-----------|---------|-----------|
| `all_products.csv` | Comma | eBay API export (all sites) | `Item ID` column |
| `single_variant*.csv` | Tab | Shopify-matched items with weight+dims | `Product eBay URL` |
| `multi_variant.csv` | Comma | Items with per-variant weights | `Product eBay URL` |
| `unresolved.csv` | Comma | Items with no Shopify match | `Product eBay URL` |

## Pitfalls
1. **Scientific notation in IDs**: `1.47E+11` → `147000000000` (wrong!). Always extract from URL.
2. **Mixed delimiters**: Never assume. Auto-detect per file.
3. **Multiple files with same IDs**: sv / sv_master / sv_final / sv_done all reference the same 83 items — de-duplicate before counting.
4. **Multi-variant nuance**: Items with per-variant weights may still show as flagged if listing-level Package Weight is empty. Apply the most common/heaviest variant weight as default.
5. **Unresolved items**: Products with "not found" Shopify URL or "no weight on Shopify" need manual attention.
