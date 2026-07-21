# JSON-LD Schema Templates for Directory / Benchmark Sites

## SoftwareApplication (AI Model Page)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Model Name Here",
  "applicationCategory": "AI Model",
  "description": "Short description of what this model does.",
  "operatingSystem": "API",
  "author": {
    "@type": "Organization",
    "name": "Developer Name"
  },
  "offers": {
    "@type": "Offer",
    "price": "1.00",
    "priceCurrency": "USD",
    "priceDescription": "per 1M input tokens"
  },
  "datePublished": "2026-07-09",
  "version": "1.0"
}
```

Variations:
- Use `author` for model creator, `offers` for pricing
- If multiple pricing tiers, use `offers` as array
- Set `applicationCategory` to describe the domain (`AI Model`, `Benchmark Tool`, `API Wrapper`)

## BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Category Name",
      "item": "https://example.com/category"
    }
  ]
}
```

Rules:
- Maximum of 4-5 items
- Each `position` must be sequential starting at 1
- Only the LAST item omits `item` (current page)
- Use absolute URLs (https, full domain)

## FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is [item name]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[concise answer]"
      }
    },
    {
      "@type": "Question",
      "name": "How much does [item name] cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Pricing starts at $X per [unit]."
      }
    }
  ]
}
```

Tips:
- 3–5 questions is optimal
- Questions should be natural language people type into search
- Answers should be 1-3 sentences, not paragraphs
- Pull content directly from visible page content (don't invent)

## WebSite (Site-wide, homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Site Name",
  "url": "https://example.com/",
  "description": "Site-wide description",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://example.com/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

## Organization (Brand)

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Brand Name",
  "url": "https://example.com/",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://twitter.com/handle",
    "https://github.com/org"
  ]
}
```

## DataCatalog (Listing / Directory Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "DataCatalog",
  "name": "Catalog Name",
  "description": "Description of the catalog",
  "dataset": [
    {
      "@type": "Dataset",
      "name": "Entry Name"
    }
  ]
}
```

## Combining into @graph

When a page needs multiple schemas, wrap them in `@graph`:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { /* SoftwareApplication */ },
    { /* BreadcrumbList */ },
    { /* FAQPage */ }
  ]
}
```

Only use `@graph` when you have 2+ schemas. Single schema types don't need it.

### Homepage combination: WebSite + SearchAction + Organization

This is the most common `@graph` usage — inject into `base.html` so every page gets the site-level schema:

**Flask/Jinja (base.html):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "{{ request.host_url }}#website",
      "url": "{{ request.host_url }}",
      "name": "Site Name",
      "description": "Site-wide tagline here.",
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "{{ request.host_url }}search?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "Organization",
      "@id": "{{ request.host_url }}#organization",
      "name": "Site Name",
      "url": "{{ request.host_url }}",
      "description": "Brief brand description.",
      "logo": "{{ request.host_url }}static/logo.png"
    }
  ]
}
</script>
```

**Django:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "{{ request.build_absolute_uri }}#website",
      "url": "{{ request.build_absolute_uri }}",
      "name": "Site Name",
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "{{ request.build_absolute_uri }}search?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "Organization",
      "@id": "{{ request.build_absolute_uri }}#organization",
      "name": "Site Name",
      "url": "{{ request.build_absolute_uri }}"
    }
  ]
}
</script>
```

The `@id` with fragment (`#website`, `#organization`) lets other schemas reference these entities later using the same `@id`. Place this BEFORE per-page `{% block head %}` blocks so the site-level schema is always present and per-page schemas (FAQPage, SoftwareApplication) can sit in child templates.

## Validation

```bash
# Check schema is present
curl -s https://yoursite.com/page | grep -c 'schema.org'
# View the schema block (strip to JSON for validator)
curl -s https://yoursite.com/page | grep -o '<script type="application/ld+json">.*</script>'
```
