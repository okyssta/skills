# Nectar v2 — OpenCode Dashboard Extraction & Rebrand

**Source:** anomalyco/opencode (183k stars, MIT, TypeScript monorepo)
**Target:** Standalone API provider dashboard (Nectar)
**Date:** July 8, 2026

## Key Commands Used

```bash
# Clone (shallow, single branch)
git clone --depth 1 --single-branch --branch dev https://github.com/anomalyco/opencode.git

# Copy packages efficiently (preserving structure)
SRC="/root/opencode-source"
DST="/root/nectar-v2/packages"
cd "$SRC/packages/$pkg" \
  && find . -not -path '*/node_modules/*' -type f -print \
  | cpio -pdm "$DST/packages/$pkg"
```

## Packages Extracted for Dashboard

| Package | Original Name | Purpose |
|---------|--------------|--------|
| console/app | @opencode-ai/console-app | Main dashboard (SolidJS SPA) |
| console/core | @opencode-ai/console-core | Business logic / DB schemas |
| console/mail | @opencode-ai/console-mail | Email templates |
| console/resource | @opencode-ai/console-resource | SST/Cloudflare adapter → replaced |
| ui | @opencode-ai/ui | Shared component library |
| solidjs-start-shim | (new) | Stub for @solidjs/start |

## Adaptations Made

1. **app.tsx** — FileRoutes → manual Route definitions (lazy loaded)
2. **auth.ts** — server session → API calls to Flask
3. **common.tsx** — "use server" functions → fetch() calls
4. **vite.config.ts** — SolidStart plugin removed; every shim subpath aliased separately
5. **resource.node.ts** — SST Resource proxy → env-based Proxy
6. **context.ts** — AsyncLocalStorage → simple global store
7. **index.html** — created Vite entry point
8. **package.json** — removed SolidStart/Nitro/Cloudflare deps

## Rebranding Stats

- ~1,722 text replacements across 19 i18n files
- ~600+ source files modified with sed
- 26 asset files renamed on disk
- 14 new SVG logos created from scratch
- 1 new theme JSON
- 3 manifest/metadata files updated

## Pitfalls Hit

1. **sed over-replacement** — `@opencode-ai/` → `@nectar-ai/` broke workspace resolution. Fix: second pass revert.
2. **Binary files can't be sed'd** — rename with `mv` on disk.
3. **Missing theme JSON** — imported but didn't exist in extract. Created it.
4. **Import/filename mismatch** — sed renamed import but actual file kept old name.
5. **Dist leaked old names** — hardcoded strings survived in bundled JS.
