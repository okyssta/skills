---
title: eBay Listing Weight & Dimension Estimates by Category
---

# Weight & Dimension Estimates for eBay Listings

## Quick Reference by Product Category

| Product Category | Typical Weight | Dimensions (L×W×H cm) | Notes |
|-----------------|----------------|----------------------|-------|
| **Beekeeping Suits/Jackets** | 1.5 - 3.5 kg | 55 × 40 × 25 | Folded in bag; ventilated suits lighter |
| **Gloves (cowhide/ventilated)** | 0.3 - 0.8 kg | 30 × 20 × 10 | Pair |
| **Veils (round hat/fencing)** | 0.2 - 0.5 kg | 30 × 25 × 15 | |
| **Hive Boxes (assembled)** | 5 - 15 kg | 55 × 45 × 30 | 8-frame ~5kg, 10-frame ~8kg |
| **Hive Boxes (flat-pack)** | 3 - 8 kg | 60 × 40 × 10 | Unassembled, flat |
| **Frames (10-pack assembled)** | 2 - 4 kg | 50 × 40 × 15 | Wax embedded adds weight |
| **Frames (flat-pack, 10)** | 1.5 - 3 kg | 50 × 10 × 5 | Unassembled |
| **Wax Foundation (sheet)** | 0.05 - 0.1 kg | 42 × 20 × 1 | Per sheet; 10 sheets ~0.5kg |
| **Honey Extractor (4-frame manual)** | 25 - 35 kg | 60 × 60 × 60 | Boxed |
| **Honey Extractor (9-frame electric)** | 45 - 60 kg | 70 × 70 × 80 | Boxed |
| **Creamer/Decrystallizer (150kg)** | 80 - 120 kg | 80 × 60 × 100 | Freight only |
| **Oxalic Acid Vaporizer** | 2 - 5 kg | 30 × 20 × 15 | Cordless ProVap ~3kg |
| **Uncapping Knife (electric)** | 0.5 - 1 kg | 30 × 10 × 5 | |
| **Hive Tools (J-tool, standard)** | 0.2 - 0.4 kg | 25 × 5 × 3 | |
| **Smokers (stainless)** | 0.8 - 1.5 kg | 25 × 15 × 15 | |
| **Bee Brush** | 0.1 - 0.2 kg | 25 × 5 × 3 | |
| **Frame Grip** | 0.3 - 0.5 kg | 20 × 15 × 5 | |
| **Queen Excluder (metal)** | 0.5 - 1 kg | 50 × 40 × 2 | |
| **Queen Excluder (plastic)** | 0.2 - 0.4 kg | 50 × 40 × 1 | |
| **Entrance Reducer** | 0.05 - 0.15 kg | 20 × 10 × 3 | |
| **Beetle Traps** | 0.1 - 0.3 kg | 15 × 10 × 3 | |
| **Varroa Test Kits** | 0.2 - 0.5 kg | 20 × 15 × 5 | Alcohol wash / sugar shake |
| **Honey Containers (1kg/800ml)** | 0.1 - 0.2 kg | 15 × 10 × 15 | Empty |
| **Labels (1000 pcs)** | 0.2 - 0.5 kg | 25 × 15 × 3 | |
| **Books (beekeeping)** | 0.3 - 1 kg | 25 × 19 × 3 | |
| **Starter Kits (suit + tools + hive)** | 8 - 20 kg | 60 × 45 × 40 | Multiple boxes |
| **Children's Suits** | 1 - 2 kg | 50 × 35 × 20 | Smaller |
| **T-Shirts/Apparel** | 0.2 - 0.4 kg | 30 × 25 × 3 | Folded |

## Weight Entry Format for File Exchange

| Actual Weight | WeightMajor | WeightMinor | WeightUnit |
|--------------|-------------|-------------|------------|
| 2.5 kg | 2 | 500 | Kilograms |
| 500 g | 0 | 500 | Kilograms |
| 1.2 kg | 1 | 200 | Kilograms |
| 3 kg | 3 | 0 | Kilograms |
| 0.05 kg (50g) | 0 | 50 | Kilograms |

**Rule**: WeightMajor + (WeightMinor/1000) = total kg. Both can be 0 but not both 0.

## Dimension Entry Format

| Actual Size | PackageLength | PackageWidth | PackageDepth | MeasurementUnit |
|------------|---------------|--------------|--------------|-----------------|
| 55×40×25 cm | 55 | 40 | 25 | Centimeters |
| 30×20×10 cm | 30 | 20 | 10 | Centimeters |

**Rule**: All three required if any provided. Use Centimeters for AU/UK/US sites.

## Shipping Profile Names (From Your Account)

Based on analysis, common profiles:
- `PKX - AU Variable Shipping Policy`
- `FREE SHIPPING AU(EXPRESS OPTIONAL) Copy`
- `PKX- UK Free Shipping / 6BEA / AU / Free/3d / A / FCA844D`
- `Extractor Bulky` (for large items)

**Important**: Use exact profile name from Seller Hub → Shipping → Shipping Profiles

## Priority Order for Updates

1. **Top 20 Revenue SKUs** (see TEMPLATE_TEST_Top20.csv)
2. **High-volume consumables** (WFFD-SHEETS, WSP-WF, WFUNDATIONS - 25+ sold)
3. **High-value items** (Extractors, Creamers, Starter Kits)
4. **US/UK listings** (international shipping broken without dims)
5. **Remaining AU listings**

## Verification After Upload

1. Wait for processing email
2. Check File Exchange → "View Results" for errors
3. Spot-check 5 listings:
   - Open listing → "Shipping and payments" section
   - Verify "Package dimensions" and "Package weight" show
   - Test "Calculate shipping" with US/UK zip codes
4. If errors: fix CSV → re-upload

## Common Dimension Mistakes to Avoid

| Mistake | Result | Fix |
|---------|--------|-----|
| Only Length provided | "Invalid dimensions" error | Provide all 3 or none |
| Inches instead of cm | Shipping calc wrong | Use Centimeters only |
| WeightMinor > 999 | "Invalid weight" | Carry to WeightMajor (1500g = 1kg 500g) |
| WeightUnit = "Grams" | Inconsistent | Use Kilograms for both fields |
| Profile name typo | "Shipping profile not found" | Copy exact name from Seller Hub |