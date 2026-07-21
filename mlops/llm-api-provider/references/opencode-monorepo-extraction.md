# OpenCode Monorepo — Structure & Extraction Guide

Source: https://github.com/anomalyco/opencode (branch: `dev`, July 2026)
License: MIT
Stars: 183k, Commits: 14,835, Size: ~180MB
Language: TypeScript 71.7%, MDX 24.6%, CSS 3.2%
Runtime: Bun, Framework: SST (Ion) on AWS/Cloudflare

## Overview

The active OpenCode repo is an **enterprise-grade monorepo** with 25+ packages. It is **not a standalone app** — it deploys via SST (Ion) to AWS/Cloudflare infrastructure. However, several packages are useful for extraction into a separate project like Nectar.

## Relevant Packages

### 1. `packages/console/app` — Dashboard (HIGH VALUE)
- **Stack:** SolidJS + Vite + SolidJS Start + Nitro
- **Dependencies:** @opencode-ai/console-core, @opencode-ai/ui, @opencode-ai/console-mail, @opencode-ai/console-resource
- **Infrastructure deps:** SST/Cloudflare, Upstash Redis, Stripe, Cloudflare Auth
- **Contains:**
  - Landing page at `/` and `/zen`
  - **Workspace dashboard** at `/workspace/[id]/` — usage graphs, billing, API keys, members, settings
  - **Zen API proxy** at `/zen/v1/chat/completions` — the actual LLM routing backend (OpenAI-compatible)
  - **Go subscription** management UI
  - User auth with @openauthjs/openauth
  - Stripe checkout integration
  - Support ticket system

**What to extract:** The workspace routes (`routes/workspace/[id]/`), Zen API routes (`routes/zen/`), and shared components (header, footer, icons, dropdowns, modals). The auth system needs the most adaptation work.

**Dependency chain:** console/app → console-core → (sst → cloudflare/aws). The `console-core` package has deep SST infra coupling. You'll need to replace the SST Resource bindings and Upstash Redis with your own PostgreSQL + Redis.

### 2. `packages/ui` — UI Component Library (HIGH VALUE)
- **Stack:** SolidJS + Kobalte
- **Contains:**
  - Icons (file icons, app icons, custom SVG components)
  - Dialogs (dialog components with context)
  - Select, Checkbox, RadioGroup, Collapsible
  - Toast notifications
  - ScrollView, List, Accordion
  - TextShimmer, AnimatedNumber, ProgressCircle
  - Context: dialog, marked, i18n, worker-pool, file
  - **Full i18n translations** in 17 languages
  - Storybook stories for components

**What to extract:** Nearly everything is reusable. The `src/components/` directory is the core library. The `src/context/i18n.tsx` handles translations — copy the full i18n system.

**Portability:** Medium — depends only on SolidJS + Kobalte catalog. No SST infra deps.

### 3. `packages/tui` — Terminal UI (MEDIUM VALUE)
- **Stack:** Ink (React for terminal) + SolidJS
- **Contains:**
  - Terminal dialogs (model select, workspace, help, confirm, etc.)
  - Workspace management UI
  - Plugin system
  - Theme and editor context
  - Feature plugins (home, sidebar, system)

**Portability:** Lower — tightly integrated with OpenCode's SDK, core runtime, and plugin system.

### 4. `packages/app` — Desktop Workspace (MEDIUM-HIGH VALUE)
- **Stack:** SolidJS + Vite + Tailwind CSS
- **Contains:**
  - Session/Tab management UI
  - File tree (file-tree, file-tree-v2)
  - Terminal component
  - Prompt input with slash commands, drag overlay, context items
  - Titlebar with tab strip
  - Settings dialogs (models, providers, servers, keybinds)
  - Connect provider dialog
  - Command palette
  - Dialog system (fork, edit project, select directory/file, model selector)
  - Status popover

**Portability:** Medium — depends on @opencode-ai/core, schema, sdk, session-ui, ui.

### 5. `packages/web` — Marketing Site (LOW VALUE)
- **Stack:** Astro + Starlight
- **Contains:** Docs, blog, landing pages

## Infrastructure Dependencies (The Main Extraction Challenge)

| Service | Purpose | Replacement |
|---------|---------|-------------|
| Upstash Redis | Rate limiting, caching | Self-hosted Redis |
| Cloudflare Workers | Auth middleware | Flask/JWT auth |
| SST Resource bindings | Config injection | .env variables |
| Stripe | Payments | Stripe or Lemon Squeezy |

## Extraction Strategy

### Phase 1: Dashboard (Console App)
1. Copy `packages/console/app/src/routes/` — focus on workspace routes
2. Copy `packages/console/app/src/component/` — shared UI components
3. Copy `packages/console/app/src/context/` — i18n, auth context
4. Copy `packages/console/app/src/asset/` + `public/` — brand assets
5. Strip SST Resource bindings — replace with env vars + direct DB queries
6. Replace server functions (`"use server"`) with Flask API endpoints

### Phase 2: UI Library
1. Copy `packages/ui/src/components/` — all UI components
2. Copy `packages/ui/src/context/` — dialog context, i18n
3. Copy `packages/ui/src/i18n/` — translations (17 languages)

### Phase 3: Workspace UI (App)
1. Copy select components from `packages/app/src/components/`
2. Focus on: file-tree, terminal, prompt-input, session-ui, settings, dialogs

### Phase 4: TUI
1. Copy `packages/tui/src/` — terminal UI
2. Replace OpenCode-specific context providers with generic ones

## Key Files to Start With

### Dashboard (must-have)
```
routes/workspace/[id]/index.tsx              # Main workspace page
routes/workspace/[id]/usage/                 # Usage graphs + stats
routes/workspace/[id]/billing/               # Billing section
routes/workspace/[id]/keys/                  # API key management
routes/workspace/[id]/settings/              # Settings
routes/workspace/[id]/members/               # Team members
routes/workspace/[id]/go/                    # Go subscription
routes/workspace/common.tsx                  # Shared server functions
```

### API Proxy (Zen — the actual LLM backend, replaces LiteLLM)
```
routes/zen/v1/chat/completions.ts            # Chat completions API
routes/zen/v1/messages.ts                    # Messages API
routes/zen/v1/models.ts                      # Models list
routes/zen/util/                              # Rate limiters, providers, Redis
routes/zen/go/v1/                             # Go subscription API
```

### UI Components
```
packages/ui/src/components/icon.tsx           # Icon system
packages/ui/src/components/dialog.tsx         # Dialog system
packages/ui/src/components/select.tsx         # Select dropdown
packages/ui/src/components/toast.tsx          # Toast notifications
packages/ui/src/components/checkbox.tsx       # Checkbox
packages/ui/src/components/scroll-view.tsx    # Scroll view
```

## Important Notes

- The console app depends on **Nitro** (server engine) + **SolidJS Start** (meta-framework). For standalone deployment, replace Nitro with Express/Fastify and use SolidJS just for the client side.
- The `"use server"` directives in `common.tsx` are SolidJS Start server functions — they run on the server during SSR. For a decoupled backend, these need to become regular API calls to your Flask backend.
- The Zen API routes handle their own provider routing, fallback, rate limiting, and caching — they could replace LiteLLM entirely if you want a pure TypeScript proxy instead of Python-based LiteLLM.
- Total codebase is 180MB. A selective extraction of just the console, ui, and key app components is roughly 5-10MB of source code.
- The minimum viable extraction is: **console/app** for the dashboard UI + **ui** for components.
