# Verified Asset Download Process

This reference document outlines the process for verifying and downloading truly free (CC0/public domain) game assets, particularly from sources like itch.io that use "name your own price" models.

## Core Verification Principle

Never trust "free" or "CC0" labels at face value. Always verify that you can actually download the asset for $0.

## Step-by-Step Verification Process

### 1. Initial Screening
- Look for assets tagged with `assets-cc0` on itch.io (not just `free`)
- Check the asset description for explicit CC0/public domain statements
- Be wary of assets that only say "free" in the title but show a price on the page

### 2. The $0 Test (Mandatory)
For any asset on itch.io or similar platforms:
1. Click "Download Now" or equivalent button
2. When prompted for payment, enter `0` in the price field
3. Confirm the download starts successfully
4. If it requires payment >$0 or fails, the asset is NOT free

### 3. Alternative Verification Methods
- **Kenney Assets**: All assets are CC0; their "name your own price" always accepts $0
- **OpenGameArt.org**: Check the license field explicitly states "CC0" or "Public Domain"
- **Direct Statements**: Look for clear phrases like "Released under CC0 1.0 Universal" or "Public Domain"

### 4. Documentation Requirements
When listing verified assets, always include:
- Direct download link (not just the item page)
- Confirmation that $0 download works
- License verification method used
- Any special notes about attribution requirements

## Common Pitfalls and How to Avoid Them

| Pitfall | How to Avoid |
|---------|--------------|
| "Free" title but $5 price | Always check the actual download price, not just the title |
| "Free" but requires account/payment after download | Test the full download process before recommending |
| CC-BY instead of CC0 | Verify the exact license; CC0 requires no attribution |
| Asset pack has mixed licenses | Check individual asset licenses if mixing content |
| Outdated "free" claims | Verify the current status; sometimes free assets become paid |

## Recommended Verification Workflow for Bulk Assets

1. Search using `assets-cc0` tag + relevant keywords (e.g., `assets-cc0 tag-16x16 tag-top-down tag-characters`)
2. Open each promising result in a new tab
3. For each tab:
   - Quick scan for obvious non-free indicators (price tags, "pro" labels)
   - If looks promising, proceed to $0 test
   - Document results in a spreadsheet: [Asset Name] | [Source] | [$0 Test: PASS/FAIL] | [License Verified: YES/NO] | [Notes]
4. Only proceed with assets that pass both tests
5. Provide direct download links in final documentation

## Special Cases

### Kenney Assets
All Kenney assets on `kenney-assets.itch.io` and `kenney.nl/assets` are CC0 and their "name your own price" always accepts $0. Still recommended to verify for consistency.

### RGS_Dev Assets
Assets from `rgsdev.itch.io` marked "Free CC0" have been verified to accept $0 downloads.

### Asset Bundles/Collections
When verifying asset bundles:
- Check if the bundle price is $0 (not just "name your own price")
- Or verify each individual asset in the bundle can be downloaded for $0
- Be wary of bundles where some assets are free and others are not

## Example Verification Entry

```
Asset: Free Pixel Character Base Pack (32x32) | Top-Down Animations
Source: https://kettoman.itch.io/free-pixel-character-base-pack-32x32-top-down-farmer-animations
$0 Test: PASS - Entered 0 in price field, download started immediately
License Verified: Explicitly states "Free to use in any game you create" and "Credit is not needed"
Notes: Includes idle and walk animations for farming-style character, adaptable for multiple hero classes
```

## Automation Considerations

While full automation of $0 testing is difficult due to CAPTCHAs and varying payment interfaces, you can:
- Bookmark known-good sources (Kenney, RGS_Dev, verified OpenGameArt collections)
- Create a personal whitelist of sources that consistently pass the $0 test
- Schedule quarterly re-verification of your asset library sources