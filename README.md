# Hermes Skills Vault

**55 battle-tested skills** for [Hermes Agent](https://hermes-agent.nousresearch.com/) — built through real-world use, not synthetic tutorials.

These aren't docs you read once. They're repeatable workflows that survived actual debugging sessions, production deployments, and edge cases. Each skill catches real gotchas that only surface when you've run the thing end to end.

---

## What's inside

| Category | Skills | What you'll find |
|----------|--------|-----------------|
| **Creative** | 5 | Urdu poetry prosody (full Ilm-e-Arooz), indie game concept validation, Phaser 3 browser games, free CC0 game asset curation, Manim CE troubleshooting |
| **Data Science** | 1 | Fuzzy/partial CSV filtering with prefix matching |
| **DevOps** | 6 | Free-tier LLM setup, Docker auto-deploy pipelines, eBay Trading API integration, Pterodactyl panel deployment, Hermes gateway adapter dev, cron job management |
| **GitHub** | 2 | Fork-based PR workflows, GitHub automation patterns beyond basic PR lifecycle |
| **Go** | 1 | Production API gateway patterns (routing, middleware, LLM proxies) |
| **Hermes** | 3 | JSON-RPC gateway protocol spec, ModelHub dashboard operations, environment passthrough |
| **MLOps** | 3 | Building an LLM API provider business, distilling frontier models to 4-9B, wrapping web-only AI models as OpenAI-compatible APIs |
| **Productivity** | 2 | Project delivery playbook, docsify documentation site setup |
| **Research** | 4 | Multi-registry competitive landscape research, systematic product ideation, Steam API indie game validation, Pakistani university admissions |
| **Software Development** | 22 | Config propagation debugging, competitor-driven development, defensive programming patterns, Hermes CLI internals, open-source monorepo extraction, reference architecture research, service testing patterns, and more |
| **Testing** | 1 | Integration testing for daemon/service systems |
| **Web** | 5 | Stealth web scraping, web content reconnaissance, competitive SEO audit, web app SEO, WordPress SEO |

## Highlights

- **urdu-poetry** — The most comprehensive Urdu poetry reference in any AI skill library. Covers all 14 common poetic meters (bahrs) with full scansion, 21 types of metrical variation (zihaaf), the complete qafiya/radeef system, 17 poetic forms, and 10+ poetic devices with Urdu script examples.
- **stealth-web-scraping** — Battle-tested techniques to bypass bot detection. Covers CloakBrowser, undetected-chromedriver, and Firecrawl self-hosted. Not theory — these come from building production scrapers.
- **web-model-api-proxy** — Turn web-only AI models (Qwen, ChatGPT, Claude) into OpenAI-compatible API endpoints using browser automation. Full Playwright session management + anti-bot header capture pattern.
- **open-source-extraction** — Extract specific packages from large monorepos (OpenCode, etc.) for standalone use. Dependency mapping, cloud dep stripping, iterative build fixing.
- **competitor-driven-development** — Systematic methodology: clone → audit → feature parity → ADRs → clean-room rebuild. Includes real audit templates.
- **config-propagation-bugs** — The kind of bug that costs hours: silent data loss from incomplete model serialization, wholesale overwrites. Real debugging patterns.
- **indie-game-concept-design** — Generates original indie game concepts validated against Steam API + itch.io. Not guesswork — market-verified.
- **small-model-distillation** — Practical guide to distilling Claude/GPT/DeepSeek into 4-9B models for agentic tasks. Covers when it works, the playbook, and the hard parameter ceiling.
- **llm-api-provider** — Full blueprint for building an LLM API provider business: cost modeling, multi-provider routing, subscription billing.

## Why this exists

Hermes Agent learns from use. Every skill here started as a task, got refined through repetition, and crystallized into a reusable workflow. They're all **custom-written** — none are the vanilla skills that ship with Hermes.

If you're using Hermes Agent, these skills save you the 2-10 hours it took to figure each one out the first time.

---

## Structure

```
skills/
├── creative/urdu-poetry/
│   └── SKILL.md                  # The skill itself
├── devops/docker-auto-deploy/
│   ├── SKILL.md
│   ├── references/               # Deep dives, research notes
│   └── scripts/                  # Shell scripts, helpers
├── web/stealth-web-scraping/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
└── ...
```

Each skill directory has:
- `SKILL.md` — the reusable workflow: trigger conditions, step-by-step procedure, pitfalls, verification
- `references/` — research notes, architecture deep-dives, error diagnoses (where applicable)
- `scripts/` — automation scripts, templates (where applicable)

## Usage

1. Install [Hermes Agent](https://hermes-agent.nousresearch.com/)
2. Copy a skill to `~/.hermes/skills/<category>/<name>/`:
   ```bash
   git clone https://github.com/kyssta-exe/skills.git
   cp -r skills/creative/urdu-poetry ~/.hermes/skills/creative/
   ```
3. Load it in a session: `hermes` automatically picks up skills placed in the skills directory

Or load on demand: `skill_view(name='urdu-poetry')`

---

## License

MIT — use freely, adapt, share back.
