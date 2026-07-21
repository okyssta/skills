# Pre-Pitch Validation Checklist

Run this before presenting ANY idea to the user. If any check fails, go back to research.

## Agent-Proof & Competitor Check

- [ ] Can an AI agent (like Hermes) replicate this with a single command/tool call? If yes → STOP. Do not pitch.
- [ ] The tool requires at least one of: persistent state, real-time/24/7 service, multi-user/social, public shareable pages, infrastructure (API/webhooks), or integration surface
- [ ] Verified the tool is not just a "prompt with a UI" or "AI wrapper" — agent displacement kills these instantly
- [ ] Searched for exact concept name — no direct competitors found
- [ ] Searched for adjacent categories — no dominant player owns the space
- [ ] Checked for free alternatives that do "80% of what you propose" — if one exists, don't pitch
- [ ] If a competitor exists: your version must be dramatically simpler (no auth, faster, free) — not just "better"

## Infra Leverage Check

- [ ] What server/infra does the user already pay for that could host this at $0 marginal cost?
- [ ] What API tokens/credentials do they already have (LLM providers, cloud, etc)?
- [ ] What existing codebase could be reused/adapted (routers, benchmarks, bots)?
- [ ] What domain expertise do they have that a generic dev doesn't?
- [ ] The idea leverages at least one of the above — not a generic startup idea

## Existence Check

- [ ] Searched GitHub for the exact name (not just "no results on first page", actually verified)
- [ ] Searched Firecrawl for the concept keywords
- [ ] Searched npm/PyPI/cargo for similar packages
- [ ] Checked against the saturated categories list
- [ ] Verified the "closest existing tool" is different enough

## Audience & Lane Check

- [ ] Confirmed which lane: UTILITY (useful tool) or CONSUMER/SOCIAL (viral/fun)? Pitch only the right lane
- [ ] If user said "useful" or "tool" — NOT pitching viral/fun concepts
- [ ] If user said "viral" or "social" — NOT pitching boring utility
- [ ] Developers would use this (daily? weekly?)
- [ ] Company owners would find value (saves money? reduces risk?)
- [ ] Regular users would benefit (non-technical people too?)
- [ ] If only one audience: the gap must be VERY large to justify

## Virality Check

- [ ] Solves an AI-era problem (or a universal human problem)
- [ ] Has a 10-second "holy shit" demo moment
- [ ] Can be demo'd in one GIF
- [ ] Has a shareable number/benchmark
- [ ] One-line install
- [ ] Meme-friendly / has personality hook
- [ ] Solves a DAILY pain (not weekly/monthly)

## Build Check (Ponytail)

- [ ] Can be built in <200 lines
- [ ] Stdlib can handle it (no exotic deps)
- [ ] Single file possible
- [ ] No cloud/server/account required
- [ ] Works cross-platform (Linux/Mac minimum)

## Presentation Check

- [ ] README has the structure: logo → badge → GIF → install → why → usage
- [ ] Comparison table vs closest alternatives ready
- [ ] Evidence of uniqueness (search results, star counts)
- [ ] Prototype exists and works
- [ ] **STOP after pitching if user rejects.** 3+ rejections = wrong lane. Do not pitch more. Re-assess filters.
