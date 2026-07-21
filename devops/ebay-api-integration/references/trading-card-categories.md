---
title: Trading Card Categories & Required Specifics
---

# eBay Trading Card Categories & Required Item Specifics

## Primary Trading Card Categories

| Category ID | Category Name | Parent |
|-------------|---------------|--------|
| 27501 | Trading Card Games | Collectibles:Collectible Card Games |
| 27502 | Sports Trading Cards | Collectibles:Sports Mem, Cards & Fan Shop |
| 261328 | CCG Individual Cards | Collectibles:Collectible Card Games |
| 261332 | Sports Cards | Collectibles:Sports Mem, Cards & Fan Shop |
| 261336 | Non-Sport Cards | Collectibles:Collectible Card Games |
| 183454 | Collectible Card Games | Collectibles |
| 261324 | CCG Sealed Products | Collectibles:Collectible Card Games |
| 261340 | Sports Card Singles | Collectibles:Sports Mem, Cards & Fan Shop |

## Required Item Specifics for Trading Cards

### Universal (All Trading Card Categories)
| Specific Name | Required | Values / Format | Notes |
|---------------|----------|-----------------|-------|
| Professional Grader | Yes* | PSA, BGS, CGC, SGC, HGA, Other, Ungraded | *Required for graded cards |
| Grade | Yes* | 10, 9.5, 9, 8.5, 8, 7.5, 7, 6, 5, 4, 3, 2, 1, Authentic, Altered | *Required for graded cards |
| Certification Number | Yes* | Alphanumeric (PSA: 8-10 digits, BGS: 10+ chars, CGC: 10 digits) | *Required for graded cards |
| Card Condition | Yes | Mint, Near Mint, Excellent, Very Good, Good, Fair, Poor | Required for ungraded |

### Trading Card Games (TCG) — Category 27501 / 261328
| Specific Name | Required | Values / Format | Notes |
|---------------|----------|-----------------|-------|
| Game | Yes | Magic: The Gathering, Pokémon, Yu-Gi-Oh!, etc. | |
| Set | Yes | Base Set, Jungle, Fossil, Modern Horizons, etc. | |
| Card Name | Yes | Charizard, Black Lotus, Blue-Eyes White Dragon | |
| Rarity | Yes | Common, Uncommon, Rare, Holo Rare, Ultra Rare, Secret Rare, etc. | |
| Card Number | No | 4/102, 001/198, SM123 | |
| Language | No | English, Japanese, French, German, Spanish, Italian, Korean, Chinese | |
| Edition | No | 1st Edition, Unlimited, Limited, Shadowless | |
| Foil | No | Yes, No | |

### Sports Trading Cards — Category 27502 / 261332 / 261340
| Specific Name | Required | Values / Format | Notes |
|---------------|----------|-----------------|-------|
| Sport | Yes | Baseball, Basketball, Football, Hockey, Soccer, Racing, etc. | |
| Player Name | Yes | LeBron James, Tom Brady, Mike Trout, Connor McDavid | |
| Team | Yes | Los Angeles Lakers, New York Yankees, etc. | |
| Year | Yes | 2023, 2024, 1986, etc. | |
| Set | Yes | Panini Prizm, Topps Chrome, Bowman, Donruss Optic, etc. | |
| Card Number | No | 1, 100, SP-1, RC-1 | |
| Parallel/Variety | No | Silver, Gold, Black, Red, Blue, Refractor, etc. | |
| Rookie Card | No | Yes, No | |
| Autograph | No | Yes, No | |
| Memorabilia | No | Yes, No | |

### Non-Sport Cards — Category 261336
| Specific Name | Required | Values / Format | Notes |
|---------------|----------|-----------------|-------|
| Franchise | Yes | Star Wars, Marvel, DC, Garbage Pail Kids, etc. | |
| Set | Yes | | |
| Character/Subject | Yes | Darth Vader, Spider-Man, etc. | |
| Card Number | No | | |
| Rarity | No | Common, Rare, Chase, etc. | |

## Condition ID Mapping
| Condition ID | Display Name | Use For |
|--------------|--------------|---------|
| 1000 | New | Sealed products, ungraded mint cards |
| 2750 | New with tags | Sealed boxes/packs |
| 3000 | Used - Like New | Ungraded Near Mint |
| 4000 | Used - Very Good | Ungraded Excellent |
| 5000 | Used - Good | Ungraded Very Good/Good |
| 6000 | Used - Acceptable | Ungraded Fair/Poor |
| 2750 | Graded — use ConditionID 2750 + ItemSpecifics for Grade/Grader/Cert | All graded cards |

## Validation Rules

### Graded Cards (Must Have All 3)
- `Professional Grader` ∈ {PSA, BGS, CGC, SGC, HGA, Other, Ungraded}
- `Grade` ∈ valid grade scale for that grader
- `Certification Number` = non-empty alphanumeric

### Ungraded Cards (Must Have)
- `Card Condition` ∈ {Mint, Near Mint, Excellent, Very Good, Good, Fair, Poor}

### Common Mistakes
1. **Listing graded card without Certification Number** — Policy violation
2. **Using wrong ConditionID for graded cards** — Must use 2750 + specifics
3. **Missing Game/Set for TCG** — Required for catalog matching
4. **Missing Sport/Player/Team for Sports** — Required for catalog matching
5. **Fake/Invalid Certification Numbers** — eBay validates against grader databases

## API Calls for Category Data
- `GetCategories` — Full category tree
- `GetCategorySpecifics` — Required/recommended specifics per category
- `GetCategoryFeatures` — Supported features (condition IDs, listing types, etc.)

## Example ItemSpecifics XML (Graded Pokémon)
```xml
<ItemSpecifics>
  <NameValueList>
    <Name>Professional Grader</Name>
    <Value>PSA</Value>
  </NameValueList>
  <NameValueList>
    <Name>Grade</Name>
    <Value>10</Value>
  </NameValueList>
  <NameValueList>
    <Name>Certification Number</Name>
    <Value>12345678</Value>
  </NameValueList>
  <NameValueList>
    <Name>Game</Name>
    <Value>Pokémon</Value>
  </NameValueList>
  <NameValueList>
    <Name>Set</Name>
    <Value>Base Set</Value>
  </NameValueList>
  <NameValueList>
    <Name>Card Name</Name>
    <Value>Charizard</Value>
  </NameValueList>
  <NameValueList>
    <Name>Rarity</Name>
    <Value>Holo Rare</Value>
  </NameValueList>
</ItemSpecifics>
```

## Example ItemSpecifics XML (Ungraded Sports)
```xml
<ItemSpecifics>
  <NameValueList>
    <Name>Card Condition</Name>
    <Value>Near Mint</Value>
  </NameValueList>
  <NameValueList>
    <Name>Sport</Name>
    <Value>Basketball</Value>
  </NameValueList>
  <NameValueList>
    <Name>Player Name</Name>
    <Value>LeBron James</Value>
  </NameValueList>
  <NameValueList>
    <Name>Team</Name>
    <Value>Los Angeles Lakers</Value>
  </NameValueList>
  <NameValueList>
    <Name>Year</Name>
    <Value>2023</Value>
  </NameValueList>
  <NameValueList>
    <Name>Set</Name>
    <Value>Panini Prizm</Value>
  </NameValueList>
  <NameValueList>
    <Name>Rookie Card</Name>
    <Value>Yes</Value>
  </NameValueList>
</ItemSpecifics>
```