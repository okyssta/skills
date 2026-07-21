---
title: eBay Trading API Common Error Codes
---

# Common eBay Trading API Error Codes

## Rate Limiting & Throttling
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 218050 | Rate limit exceeded | Too many calls per time window | Exponential backoff: 10s, 20s, 40s. Reduce MAX_WORKERS. |
| 21919165 | Concurrent request limit | Too many parallel connections | Reduce thread pool size. Add delay between submissions. |

## Authentication & Token Issues
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 931 | Auth token invalid | Token expired or revoked | Re-run OAuth flow. Check token format. |
| 932 | Auth token expired | Token past TTL (typically 18 months) | Get new token. |
| 21919024 | Invalid RuName | Redirect URI mismatch | Check RuName in developer dashboard matches OAuth redirect. |
| 21919025 | Invalid client credentials | App ID/Cert ID wrong | Verify keys in developer dashboard. |

## Listing Policy Violations
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 21920397 | Single-use plastic policy | Listing violates single-use plastic ban | Remove listing. Check product compliance. Relist if compliant. |
| 21916976 | Prohibited item | Item category banned | Review eBay prohibited items policy. |
| 21916977 | Restricted item | Item requires special approval | Apply for approval or change category. |
| 240 | Category not supported | Category ID invalid or deprecated | Use current category ID from GetCategories. |
| 21916989 | Item specifics required | Required item specifics missing | Add required NameValueList entries. |

## Data Validation Errors
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 21916990 | Invalid item specific | Name or value not allowed for category | Check valid specifics for category via GetCategorySpecifics. |
| 21916991 | Missing required specific | Required specific not provided | Add required specific. |
| 21916992 | Invalid condition ID | ConditionID not valid for category | Use GetCategoryFeatures to find valid conditions. |
| 21916993 | Invalid price | Price below minimum or format error | Check minimum price for category/format. |
| 21916994 | Invalid quantity | Quantity exceeds limits | Check category quantity limits. |
| 21916995 | Invalid SKU | SKU duplicate or format issue | Ensure unique SKU per listing. |

## Shipping Errors
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 21916996 | Shipping service invalid | Service not available for site/category | Use GeteBayDetails for valid services. |
| 21916997 | Package details required | Weight/dimensions missing for calculated shipping | Add ShippingPackageDetails. |
| 21916998 | Shipping profile not found | SellerShippingProfile ID invalid | Verify profile ID in Seller Hub. |

## Catalog / Product Errors
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 21916999 | ePID not found | ProductID doesn't exist | Verify ePID on eBay catalog. |
| 21917000 | GTIN invalid | UPC/EAN/ISBN format wrong | Validate checksum. Use GS1 database. |
| 21917001 | GTIN in use | GTIN already linked to different product | Contact eBay support or use different GTIN. |

## API Structure Errors
| Code | Name | Meaning | Resolution |
|------|------|---------|------------|
| 21917002 | XML parse error | Malformed request XML | Validate XML structure. Check namespace. |
| 21917003 | Missing required field | Required element absent | Check API documentation for required fields. |
| 21917004 | Invalid value | Value out of range or wrong type | Check field constraints. |

## Handling Strategy
```python
RETRY_CODES = {"218050", "21919165"}  # Rate limits
FATAL_CODES = {"931", "932", "21919024", "21919025"}  # Auth - need new token

def handle_errors(errors):
    codes = {e[0] for e in errors}
    if codes & RETRY_CODES:
        return "retry_with_backoff"
    if codes & FATAL_CODES:
        return "refresh_token"
    return "log_and_continue"
```

## Resources
- [eBay API Error Codes](https://developer.ebay.com/api-docs/static/error-codes.html)
- [Trading API Call Reference](https://developer.ebay.com/api-docs/sell/static/api-browse.html)