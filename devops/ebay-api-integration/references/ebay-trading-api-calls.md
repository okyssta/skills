---
title: eBay Trading API Key Calls Reference
---

# eBay Trading API — Key Calls for Listing Management

## GetMyeBaySelling
Retrieves seller's active, sold, and unsold listings.

### Request
```xml
<GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{token}</eBayAuthToken>
  </RequesterCredentials>
  <ActiveList>
    <Include>true</Include>
    <Pagination>
      <EntriesPerPage>200</EntriesPerPage>
      <PageNumber>1</PageNumber>
    </Pagination>
  </ActiveList>
  <SoldList>
    <Include>true</Include>
    <Pagination>
      <EntriesPerPage>200</EntriesPerPage>
      <PageNumber>1</PageNumber>
    </Pagination>
  </SoldList>
  <UnsoldList>
    <Include>true</Include>
    <Pagination>
      <EntriesPerPage>200</EntriesPerPage>
      <PageNumber>1</PageNumber>
    </Pagination>
  </UnsoldList>
  <DetailLevel>ReturnAll</DetailLevel>
</GetMyeBaySellingRequest>
```

### Key Response Fields
| Path | Description |
|------|-------------|
| `ActiveList/ItemArray/Item/ItemID` | Listing ID |
| `ActiveList/ItemArray/Item/Title` | Listing title |
| `ActiveList/ItemArray/Item/StartPrice` | Start price (attr: currencyID) |
| `ActiveList/ItemArray/Item/BuyItNowPrice` | BIN price (attr: currencyID) |
| `ActiveList/ItemArray/Item/Quantity` | Total quantity |
| `ActiveList/ItemArray/Item/SellingStatus/QuantitySold` | Sold count |
| `ActiveList/ItemArray/Item/SellingStatus/CurrentPrice` | Current price (attr: currencyID) |
| `ActiveList/ItemArray/Item/Site` | eBay site (Australia, UK, US, etc.) |
| `ActiveList/ItemArray/Item/ListingType` | Chinese, FixedPriceItem, etc. |
| `ActiveList/ItemArray/Item/ListingDetails/ViewItemURL` | Listing URL |
| `ActiveList/PaginationResult/TotalNumberOfPages` | Total pages |
| `ActiveList/PaginationResult/TotalNumberOfEntries` | Total items |

---

## GetItem
Retrieves full details for a single listing.

### Request
```xml
<GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{token}</eBayAuthToken>
  </RequesterCredentials>
  <ItemID>{item_id}</ItemID>
  <DetailLevel>ReturnAll</DetailLevel>
  <IncludeItemSpecifics>true</IncludeItemSpecifics>
</GetItemRequest>
```

### Key Response Fields
| Path | Description |
|------|-------------|
| `Item/ItemID` | Listing ID |
| `Item/SKU` or `Item/CustomLabel` | Seller SKU |
| `Item/Title` | Title |
| `Item/Site` | Site |
| `Item/ListingType` | Format |
| `Item/StartPrice` | Start price (attr: currencyID) |
| `Item/BuyItNowPrice` | BIN price (attr: currencyID) |
| `Item/ReservePrice` | Reserve (attr: currencyID) |
| `Item/Quantity` | Total qty |
| `Item/SellingStatus/QuantitySold` | Sold qty |
| `Item/SellingStatus/CurrentPrice` | Current price (attr: currencyID) |
| `Item/SellingStatus/WatchCount` | Watchers |
| `Item/SellingStatus/BidCount` | Bids |
| `Item/StartTime` | Start datetime |
| `Item/EndTime` | End datetime |
| `Item/PrimaryCategory/CategoryID` | Primary category ID |
| `Item/PrimaryCategory/CategoryName` | Primary category name |
| `Item/SecondaryCategory/CategoryID` | Secondary category ID |
| `Item/SecondaryCategory/CategoryName` | Secondary category name |
| `Item/ConditionID` | Condition ID (1000=New, 3000=Used, etc.) |
| `Item/ConditionDisplayName` | Condition name |
| `Item/ItemSpecifics/NameValueList` | Item specifics (Name + Value) |
| `Item/ProductID` | ePID (attr: type=ReferenceID) |
| `Item/SellerProfiles/SellerShippingProfile/ShippingProfileName` | Shipping policy |
| `Item/ShippingPackageDetails/WeightMajor` | Weight major (attr: unit) |
| `Item/ShippingPackageDetails/WeightMinor` | Weight minor (attr: unit) |
| `Item/ShippingPackageDetails/PackageLength` | Length (attr: unit) |
| `Item/ShippingPackageDetails/PackageWidth` | Width (attr: unit) |
| `Item/ShippingPackageDetails/PackageDepth` | Depth (attr: unit) |
| `Item/PictureDetails/PictureURL` | Image URLs (multiple) |
| `Item/PictureDetails/GalleryURL` | Gallery image |
| `Item/Variations` | Variation details (if multi-variation) |

---

## ReviseFixedPriceItem / ReviseItem
Updates an existing listing.

### Common Fields to Update
- `Item.ItemID` (required)
- `Item.SKU`
- `Item.Title`
- `Item.ItemSpecifics`
- `Item.ShippingPackageDetails`
- `Item.PictureDetails`

---

## AddFixedPriceItem
Creates a new fixed-price listing.

---

## EndFixedPriceItem / EndItem
Ends a listing early.

---

## RelistFixedPriceItem / RelistItem
Relists an ended item.

---

## Headers Required
```
X-EBAY-API-COMPATIBILITY-LEVEL: 1193
X-EBAY-API-CALL-NAME: GetMyeBaySelling
X-EBAY-API-SITEID: 0
Content-Type: text/xml
X-EBAY-API-IAF-TOKEN: {oauth_token}  # For OAuth
# OR
# RequesterCredentials/eBayAuthToken in XML body for Auth'n'Auth
```

---

## Site IDs
| Site | ID |
|------|-----|
| United States | 0 |
| Canada | 2 |
| United Kingdom | 3 |
| Australia | 15 |
| Austria | 16 |
| Belgium (French) | 23 |
| France | 71 |
| Germany | 77 |
| Italy | 101 |
| Belgium (Dutch) | 123 |
| Netherlands | 146 |
| Spain | 186 |
| Switzerland | 193 |
| Taiwan | 196 |
| Ireland | 205 |