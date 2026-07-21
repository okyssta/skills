# Competitive SEO Audit — HuggingFace Models vs Together AI

**Date:** 2026-07-13
**Sites audited:** huggingface.co/models, together.ai/models
**Method:** curl HTML fetch + grep extraction + sitemap/robots.txt analysis

---

## Summary Table

| Factor | HuggingFace | Together AI |
|--------|-------------|-------------|
| Page Title | `org/model · Hugging Face` | `{Model Name} API \| Together AI` |
| Meta Description | ❌ Generic mission statement on ALL model pages | ✅ Model-specific (specs, benchmarks) |
| JSON-LD Schema | ❌ None | ❌ None |
| Breadcrumbs | ❌ None (no schema either) | ❌ None (no schema either) |
| Canonical | ✅ On detail pages ❌ Missing on `/models` | ✅ On both |
| OG tags | ✅ Present but generic | ✅ Present with model details |
| H1 | `org / model` | Clean model name |
| H2 Structure | Weak (SPA-rendered) | Clear sections |
| Sitemap | 7 sub-sitemaps (5,718 models indexed) | Single flat sitemap (~300 entries) |
| Robots.txt | Allow all | Blocks Google-Extended |
| Schema.org types | None | None |
| URL pattern | `/{org}/{model}` (hierarchical) | `/models/{slug}` (flat) |
| Pricing on page | No | Yes (inline on listing + detail) |
| Social proof | Downloads, likes | Provider badges |
| Generator | Not detected / custom SPA | Webflow |

## Raw Data: HuggingFace

### Homepage (`/models`)
- **Title:** `Models – Hugging Face`
- **Meta description:** `Explore machine learning models.`
- **Canonical:** ❌ NOT set
- **OG title:** `Models – Hugging Face`
- **OG description:** `Explore machine learning models.`
- **OG image:** `https://huggingface.co/front/thumbnails/models.png`
- **URL params for filtering:** `?pipeline_tag=X&library=Y&other=Z&inference_provider=W`
- **H1:** implied by context ("2,903,370" models listed)

### Model Detail Page (`/microsoft/phi-2`)
- **Title:** `microsoft/phi-2 · Hugging Face`
- **Meta description:** ❌ `We're on a journey to advance and democratize artificial intelligence through open source and open science.` — SAME across ALL models
- **Canonical:** ✅ `https://huggingface.co/microsoft/phi-2`
- **JSON-LD:** ❌ None (no `application/ld+json` blocks anywhere)
- **Microdata:** ❌ None (no `itemscope`, `itemtype`, `itemprop`)
- **Breadcrumbs:** ❌ No visible breadcrumbs, no schema
- **OG title:** `microsoft/phi-2 · Hugging Face`
- **OG description:** Same generic mission statement
- **OG image:** `https://cdn-thumbnails.huggingface.co/social-thumbnails/models/microsoft/phi-2.png`
- **Twitter:** `@huggingface`, `summary_large_image`
- **H1:** `microsoft / phi-2`
- **H2s:** "How to Get Started", "Model tree", "Spaces using..."
- **Internal links:** Same-org models (`/microsoft/phi-1.5`), spaces, dataset links, model files, license link
- **FB app ID:** `1321688464574422`

### Robots.txt
```
User-agent: *
Allow: /
Sitemap: https://huggingface.co/sitemap.xml
```
Minimal — allows all. No AI crawler block.

### Sitemap
Index at `/sitemap.xml` with 7 sub-sitemaps:
- `sitemap-static.xml` — 10 entries (main pages)
- `sitemap-doc.xml` — 52 docs pages
- `sitemap-blog.xml` — 823 blog posts
- `sitemap-models.xml` — 5,718 models (out of ~2.9M total — only trending/recent)
- `sitemap-datasets.xml` — 6,720 datasets
- `sitemap-spaces.xml` — 9,937 spaces
- `sitemap-papers.xml` — 10,000 papers

Model sitemap entries have `<loc>` + `<lastmod>`. No `<changefreq>` or `<priority>`.

## Raw Data: Together AI

### Homepage (`/models`)
- **Title:** `Build with leading AI models | Together AI`
- **Meta description:** `Browse 200+ models for text, image, video, code, and audio — available via a unified API with serverless pay-per-token pricing.`
- **Canonical:** ✅ `https://www.together.ai/models`
- **OG title:** `Build with leading AI models | Together AI`
- **OG description:** Same as meta description
- **OG image:** `https://cdn.prod.website-files.com/.../og-model-library.jpg`
- **Twitter card:** `summary_large_image`
- **Generator:** Webflow (`<meta name="generator" content="Webflow"/>`)
- **H1:** `Leading open models, ready for production`
- **Filter tabs:** All, Chat, Image, Vision, Video, Audio, Transcribe, Code, Embeddings, Rerank, Moderation
- **Pagination:** 12 pages, ~186 models shown, pagination via `?dac2a22c_page=N`

### Model Detail Page (`/models/deepseek-v4-pro`)
- **Title:** `DeepSeek V4 Pro API | Together AI`
- **Meta description:** ✅ `1.6T parameter (49B activated) MoE model with 512K token context, hybrid attention requiring only 27% inference FLOPs and 10% KV cache vs V3.2, three reasoning modes, and 93.5% LiveCodeBench.` — model-specific, includes specs and benchmarks
- **Canonical:** ✅ `https://www.together.ai/models/deepseek-v4-pro`
- **JSON-LD:** ❌ None
- **Microdata:** ❌ None
- **Breadcrumbs:** ❌ No visible breadcrumbs, no schema
- **OG title:** `DeepSeek V4 Pro API | Together AI`
- **OG description:** Same spec-rich description
- **OG image:** model-specific JPG from CDN
- **Twitter image:** Same as OG image
- **Generator:** Webflow
- **H1:** `DeepSeek V4 Pro`
- **H2s:** `About model`, `API usage`, `Model card`, `Prompting`, `Applications & use cases`, `Start building on Together AI`
- **Pricing shown inline:** Cached/1M, Input/1M, Output/1M with dollar amounts
- **Internal links:** Related models sidebar (MiniMax M3, Gemma 4 31B, GLM-5.2, Kimi K2.7 Code), "Model library" links, "Fine-tune top-open-source models" section, provider pages

### Sitemap
Single flat sitemap at `/sitemap.xml`. ~300+ entries including:
- Main pages (products, pricing, customers, about)
- Model detail pages: `/models/deepseek-v4-pro`, `/models/llama-4-maverick`, etc.
- Blog posts: `/blog/deepseek-v4-pro-now-available-on-together-ai`
- Provider pages: `/models-providers/meta`, `/models-providers/qwen`
- Customer pages, webinars, guides, GPU pages, event pages
- No sub-sitemap index

Also has `docs.together.ai/sitemap.xml` for documentation.

### Robots.txt
```
User-agent: *
Allow: /

User-agent: Google-Extended
Disallow: /

Sitemap: https://docs.together.ai/sitemap.xml
Sitemap: https://www.together.ai/sitemap.xml
```
Blocks AI training crawler (Google-Extended). Allows all others.

## Key Insights

1. **Neither site uses structured data (schema.org/JSON-LD).** This is the single biggest opportunity for a new entrant — Product, SoftwareApplication, AggregateRating (benchmark scores), BreadcrumbList, FAQPage schemas on every model page.

2. **HuggingFace's generic meta descriptions is a massive missed opportunity.** With 2.9M model pages all sharing the same one-line mission statement, Google has no per-page snippet to work with.

3. **Together AI's title pattern (`{Name} API | Together AI`) directly targets API integration search intent.** HuggingFace's title pattern (`org/model · Hugging Face`) is organizational, not goal-oriented.

4. **Sitemap coverage gap:** HuggingFace only indexes 5,718 of 2.9M models. Together AI indexes all model pages (186) and all blog posts.

5. **Cross-linking strategy differs.** HuggingFace links to same-org models + spaces. Together AI links to a curated set of "related models" regardless of org.
