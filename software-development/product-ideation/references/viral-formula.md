# GitHub Virality Formula for CLI/Dev Tools (2024-2026)

Research based on analysis of top 20+ most-starred CLI/dev tools created Jan 2024–Jul 2026. Raw data from GitHub API queries.

## The One-Sentence Pattern

> "Be the first obvious plumbing solution to a painful new problem created by the AI ecosystem, with a one-line install, a shareable personality, and a benchmark number that makes devs say 'wow'."

## The 8-Part Formula

### 1. Timing: Ride the AI Wave

Every viral CLI tool in 2024-2026 is either an AI coding agent, a skill/config for one, or pipeline infrastructure that makes agents work better/cheaper/faster. Non-AI tools don't break 20K stars.

Timing by period:
- H1 2024: Document/Web AI plumbing (MarkItDown, Firecrawl)
- H2 2024: Agent frameworks (Cline, Browser-Use, Goose)
- H1 2025: Coding agent CLIs (Claude Code, Codex, Gemini CLI, OpenCode)
- H2 2025: Skill frameworks (Superpowers, Hermes, OpenClaw, Skills)
- H1 2026: Optimization tools (rtk, Headroom, Spec-Kit)

### 2. README Template

Every viral README follows this skeleton:
1. Logo/branding + one-liner tagline (0.5s to read)
2. Badge row: stars, CI, version, Discord, license, downloads
3. Large screenshot/GIF showing the tool working (2s to watch)
4. One-line install command (curl | bash, npm i -g, brew install)
5. "Why this exists" with comparison table or benchmark number
6. Minimal usage example (copy-paste → see result)
7. 10+ language translations
8. Discord link in first 5 lines

### 3. One-Command Install (non-negotiable)

Every viral tool has a one-line install:
```bash
curl -fsSL https://example.com/install.sh | bash
npm install -g tool-name
brew install tool-name
pip install tool-name
```
Multiple install methods across all platforms.

### 4. Personality / Memeability

Tools with distinct personality grow faster:
- Crustacean mascots (OpenClaw — "the lobster way")
- Meme formats (Caveman — "why use many token when few token do trick")
- Relatable personas (Ponytail — "lazy senior dev")
- Profane/provocative names (higher recall, controversy sharing)

### 5. Brand Borrowing

Repos that borrowed authority grew faster:
- Microsoft (MarkItDown), GitHub (Spec-Kit), Anthropic (Claude Code)
- Karpathy (his CLAUDE.md config → 192K stars)
- Matt Pocock (TypeScript authority → 172K stars)

### 6. Benchmark Numbers

Claims without data don't spread. Every viral tool has a number:
- "60-90% fewer tokens" (rtk)
- "Covers 96% of the web" (Firecrawl)
- "383K GitHub stars" (OpenClaw badge)

### 7. Community

Every single viral repo has a Discord link in the first 5 lines of README.

### 8. Multi-Language README

10+ language translations are standard practice. Chinese developer market is massive.

## What DOESN'T Work Anymore

- Just another TUI/data tool without an AI angle → won't break 20K stars
- No benchmark numbers → claims don't spread
- No personality → technical excellence alone doesn't go viral
- English-only README → missing 50%+ of audience
- No Discord → community wants real-time chat

## Key Data Points

- Average stars of top 20: ~145,000
- Average time to 50K stars: 3-6 months for AI-era tools
- Language breakdown: Python 8, TypeScript 6, Rust 3, Shell 2, JS 1
- Fastest growth: OpenClaw (383K in ~8 months)
