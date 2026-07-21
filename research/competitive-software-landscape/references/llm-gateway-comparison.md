# LLM Router / AI Gateway — Research Reference (condensed)

**Generated:** July 17, 2026
**Full document:** /root/llm-router-research.md
**Method:** GitHub API + raw.githubusercontent.com README extraction + direct curl to docs (Firecrawl was unavailable)

## Quick Reference

| Project | Stars | Lang | License | Best For |
|---------|-------|------|---------|----------|
| **LiteLLM** | 53.8k | Python | MIT | Enterprise multi-provider gateway, SSO/audit, MCP/A2A agents |
| **Portkey** | 12.4k | TypeScript | MIT | Ultra-low latency (<1ms, 122kb), edge deployment, 40+ guardrails |
| **Plano** | 6.8k | Rust/Envoy | Apache 2.0 | Agent orchestration, intent-based routing (4B param LLM), Envoy-based |
| **9Router** | 22.4k | JavaScript | MIT | Free/cheap AI coding, RTK token saver (20-40%), coding CLI tools |
| **OmniRoute** | 18.2k | TypeScript | MIT | Max token savings (15-95%, 10 engines), 90+ free providers, 18 routing strategies, MCP/A2A, desktop app. Fork of 9Router. |
| **CoAI** | 9.2k | TypeScript | Apache 2.0 | Running an AI SaaS (subscription + credit billing, file parsing, API distribution) |
| **VoidLLM** | 120 | Go | BSL 1.1 | Privacy-first (zero-knowledge), RBAC hierarchy, WASM Code Mode for MCP |
| **OmniRouter (Python)** | 17 | Python | — | Not production-ready. Reference architecture only. |

## Key Differentiators

- **LiteLLM** — only one with Terraform for production AWS/GCP. Python SDK is most mature. Largest provider count of mainstream projects (100+).
- **Portkey** — fastest proxy (<1ms), smallest footprint (122kb), Cloudflare Workers deployment.
- **Plano** — only one built on Envoy by its core contributors. Uses a purpose-built 4B LLM for routing.
- **9Router** — pioneered the "coding tool router with token saving" category. RTK token saver (20-40%).
- **OmniRoute** — most feature-dense. 18 routing strategies (no competitor has more than 3). 10 compression engines. Quota-Share for team subscription splitting. Only one with desktop + PWA + Termux.
- **CoAI** — only complete AI business platform with billing built in. Best for running a paid AI service.
- **VoidLLM** — only zero-knowledge proxy (never stores prompts). Code Mode (WASM-sandboxed JS) for MCP tool orchestration.

## OmniRoute vs 9Router Relationship

OmniRoute is a fork of 9Router that diverged significantly:
- 250 providers vs 40+
- 18 routing strategies vs 1
- MCP + A2A protocol support vs none
- Desktop (Electron), Termux, PWA vs web only
- 42 languages vs handful
- Active community: 280+ contributors, 21,000+ tests

## Firecrawl Bypass Technique

When both `web_search` and `web_extract` fail with "Insufficient credits":
1. GitHub search API (`api.github.com/search/repositories`) — discovery
2. GitHub repo API (`api.github.com/repos/OWNER/REPO`) — metadata
3. `raw.githubusercontent.com` — READMEs (try main branch, fallback master)
4. Direct `curl` to project docs sites — filter output with regex
5. Browser tool — last resort for JS-rendered SPAs
6. DuckDuckGo Python SDK (`duckduckgo-search`) — may silently return empty
