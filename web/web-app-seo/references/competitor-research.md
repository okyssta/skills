# Competitor SEO Research Template

## Research Brief Template

```
Goal: Understand what [competitor] does for SEO so we can outperform them.

Checklist per site:
  ☐ Page title + meta description pattern
  ☐ URL structure (hierarchical? flat? clean?)
  ☐ H1/H2/H3 hierarchy
  ☐ JSON-LD schema present? Which types?
  ☐ Open Graph / Twitter Card meta tags
  ☐ Canonical URLs
  ☐ Breadcrumbs (visible + schema)
  ☐ Image alt text quality
  ☐ Sitemap.xml (URL count, changefreq, lastmod)
  ☐ robots.txt
  ☐ Internal linking (model ↔ category ↔ detail cross-links)
  ☐ Framework (SSR vs CSR — view source for content)

Research methods:
  - curl -s URL | grep for quick schema/OG checks
  - web_extract for structured content extraction
  - View page source for JSON-LD blocks
  - Check /sitemap.xml and /robots.txt directly
  - Delegate parallel research across multiple sites
```

## Sites to Monitor (AI Model Directory Space)

| Site | Focus | URL Pattern | Notes |
|------|-------|-------------|-------|
| Artificial Analysis | Intelligence/coding/agentic benchmarks | `/models/model-name` | Next.js SSR, no JSON-LD |
| OpenRouter | Model pricing + providers | `/provider/model-name` | Next.js SSR, SoftwareApp schema |
| Models.dev | Open-source model DB | `/models/provider/model-name` | Server-rendered, no schema |
| HuggingFace Models | Largest model hub | `/org/model` | Django SSR, Dataset schema |
| LMSYS Arena | Chatbot leaderboard | `/leaderboard` | Rebranded to arena.ai |
| Together AI | Model catalog | `/models/slug` | Next.js SSR |
| LiveBench | Independent benchmarks | `/models/slug` | Static/SSR |

## Key Findings from July 2026 Research

### Structured Data Gap
**Most competitors have little to no JSON-LD.** Only OpenRouter (partial SoftwareApp schema) and HuggingFace (Dataset schema) have any. This is the single biggest SEO opportunity for a new entrant.

### URL Best Practices
- Artificial Analysis: `/models/gpt-5-6-sol` — clean, short, no provider prefix (best)
- OpenRouter: `/openai/gpt-4o` — provider/model pattern (good)
- ModelBench (post-fix): `/openai/gpt-5.6-luna` — provider/model pattern (good)

### Meta Title Patterns
- Artificial Analysis: `"Model Name - Intelligence, Performance & Price Analysis"` — targets metric-searchers
- OpenRouter: `"Model Name - API Pricing & Providers | Brand"` — targets developer intent
- Models.dev: `"Model Name pricing, providers, and specs | Brand"` — comprehensive

### Common Weaknesses (Opportunities)
- Few sites have FAQPage schema despite having Q&A content
- Image alt text is often empty or generic
- Open Graph images are mostly static (not per-page dynamic)
- BreadcrumbList schema is nearly universal in its absence
- Changelog/Blog content rarely gets individual article pages
