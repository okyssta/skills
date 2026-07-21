# Pterodactyl Panel Theming & Customization Reference

How to apply dark themes, add features (Monaco editor, Modrinth integration), and build a custom Panel Docker image. Discovered from Panel v1.x (Docker, July 2026).

## Frontend Architecture

Panel uses: **Tailwind CSS + twin.macro + styled-components + Webpack** (not Vite).

Key files for theming:
| File | Purpose |
|------|---------|
| `tailwind.config.js` | Color palette, fonts, spacing |
| `resources/scripts/assets/css/GlobalStylesheet.ts` | Body background, scrollbars, base styles |
| `resources/scripts/assets/tailwind.css` | Tailwind directives (@tailwind base/components/utilities) |
| `resources/scripts/components/App.tsx` | Root component, imports global styles |
| `resources/views/templates/wrapper.blade.php` | HTML wrapper (title, meta, body class) |
| `config/app.php` | `name` env var (Panel title) |

## twin.macro Limitations (Critical)

`twin.macro` does NOT support:
- **Template literals in `tw` tagged template**: `tw\`bg-${color}\`` → ERROR
- **Tailwind JIT arbitrary values**: `bg-[#0d1219]` → ERROR (use inline `style` prop)
- **Tailwind v3+ classes**: `w-fit` → ERROR (use `w-max` or `inline style`)
- **Dynamic class names**: Must be plain strings

**Workaround for dynamic values**: Use the `style` prop:
```tsx
// WRONG (twin.macro error)
<div css={tw`px-3 ${isActive ? 'bg-cyan-500' : 'bg-transparent'}`}>

// RIGHT (inline style for dynamic)
<div css={tw`px-3`} style={{ background: isActive ? '#06b6d4' : 'transparent' }}>
```

## Adding Monaco Editor

1. Add dependencies to `package.json`:
```json
"@monaco-editor/react": "^4.6.0",
"monaco-editor": "^0.45.0"
```

2. Create component at `resources/scripts/components/elements/MonacoEditor.tsx`
   - Use `@monaco-editor/react` with `theme="vs-dark"`
   - Match the interface of existing `CodemirrorEditor` (Props: mode, filename, initialContent, fetchContent, onContentSaved, onContentChanged, onModeChanged)

3. Modify `resources/scripts/components/server/files/FileEditContainer.tsx`:
   - Import MonacoEditor
   - Add `editorType` state (`'codemirror' | 'monaco'`)
   - Add toggle buttons (use inline styles for active state, NOT tw template literals)
   - Conditionally render CodemirrorEditor or MonacoEditor

## Building Custom Docker Image

The Dockerfile uses multi-stage build (Node for frontend, PHP for backend):

```bash
# Fix for legacy Docker builder (no buildx):
# Remove --platform=$TARGETOS/$TARGETARCH from FROM lines in Dockerfile

# Update lockfile after adding packages:
docker run --rm -v "$(pwd):/app" -w /app node:22-alpine sh -c "yarn install"

# Build:
docker build --tag pterodactyl/panel:custom .
```

**Important**: Remove `--frozen-lockfile` from yarn install in Dockerfile after adding new packages.

## Pitfalls

### NEVER modify theme/appearance unless explicitly requested
**This is the #1 rule.** The user explicitly said "dont fucking ever do anything thats not said." When asked to add a feature (like a Plugins tab), ONLY add that feature. Do NOT bundle theme changes, branding, color adjustments, or any other visual modifications. The default Pterodactyl theme (blue/white) must remain untouched unless the user specifically asks to change it. Bundling unsolicited changes — even if they look "better" — will infuriate the user.

### Docker cache silently skips frontend rebuilds
When adding new React components (new `.tsx` files), `docker build` with cached layers may skip the `yarn run build:production` step entirely. The new components won't appear in the JS bundles. **Always use `--no-cache`** when adding new frontend code:
```bash
docker build --no-cache -t pterodactyl/panel:custom .
```
Verify the new code is actually in the built image before deploying:
```bash
docker cp <container>:/app/public/assets /tmp/check
grep -rl "yourNewString" /tmp/check/*.js
```

### `--platform=$TARGETOS/$TARGETARCH` breaks legacy Docker builder
The default Pterodactyl Dockerfile uses `FROM --platform=$TARGETOS/$TARGETARCH` which fails on systems without Docker BuildKit/buildx. Remove these args:
```bash
sed -i 's|FROM --platform=$TARGETOS/$TARGETARCH |FROM |g' Dockerfile
```

## Adding Custom CSS

Create `resources/scripts/assets/css/custom-theme.css` and import in `App.tsx`:
```tsx
import '@/assets/css/custom-theme.css';
```

The CSS file can override any Panel styles using standard CSS selectors. Use `!important` for overrides that must beat styled-components.

## Branding Changes

- **App title**: `config/app.php` → `'name' => env('APP_NAME', 'Kyssta Panel')`
- **Page title**: `resources/views/templates/wrapper.blade.php` → `<title>{{ config('app.name') }}</title>`
- **Favicon**: Place `favicon.svg` in `public/`, update `<link>` tags in wrapper.blade.php
- **Body background**: `wrapper.blade.php` body class → `bg-[#0a0e17]` (or use GlobalStylesheet)

## Adding a New Tab (Server Navigation)

Pterodactyl's server tabs are driven by a route array in `resources/scripts/routers/routes.ts`. Adding a tab = 2 steps:

### Step 1: Create the component

Place at `resources/scripts/components/server/<name>/<Name>Container.tsx`:

```tsx
import React from 'react';
import { ServerContext } from '@/state/server';
import ServerContentBlock from '@/components/elements/ServerContentBlock';

export default () => {
    const id = ServerContext.useStoreState((state) => state.server.data!.id);
    const uuid = ServerContext.useStoreState((state) => state.server.data!.uuid);

    return (
        <ServerContentBlock title={'MyTab'}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                {/* Your content */}
            </div>
        </ServerContentBlock>
    );
};
```

Key imports available:
- `ServerContext` — server `id`, `uuid`, `name`, data, actions
- `ServerContentBlock` — wraps page with `<ServerName> | <Title>` header
- `Button` from `@/components/elements/button/index`
- `Spinner` from `@/components/elements/Spinner`
- `httpErrorToHuman` from `@/api/http`
- `getFileUploadUrl` from `@/api/server/files/getFileUploadUrl` — returns presigned upload URL
- `axios` for HTTP (no extra install needed)

### Step 2: Register the route

In `resources/scripts/routers/routes.ts`:

```tsx
import MyContainer from '@/components/server/myfeature/MyContainer';

// Add to the `server` array (position determines tab order):
{
    path: '/myfeature',
    permission: 'file.*',  // or null for no permission check
    name: 'MyFeature',     // name = nav tab label; undefined = hidden route
    component: MyContainer,
},
```

The `ServerRouter.tsx` auto-renders all `routes.server` entries with `name` as `NavLink` tabs. No other files need editing.

### Deploy workflow

```bash
cd /opt/pterodactyl/panel-docker
docker build --no-cache -t pterodactyl/panel:custom .
# Update docker-compose.yml: image: pterodactyl/panel:custom
docker compose up -d --force-recreate panel
```

Verify new code is in the image: `docker cp <container>:/app/public/assets /tmp/check && grep -rl "yourstring" /tmp/check/*.js`

## Modrinth Plugin Browser (Reference Implementation)

A full Modrinth integration exists at `resources/scripts/components/server/plugins/PluginsContainer.tsx`. Key patterns:

### Modrinth API (no API key needed)

| Endpoint | Use |
|----------|-----|
| `GET /v2/search?query=...&facets=[["project_type:plugin"],["categories:paper"]]&limit=24` | Search |
| `GET /v2/project/{id}` | Full project details |
| `GET /v2/project/{id}/version?loaders=["paper"]&game_versions=["1.21.4"]` | Filtered versions |

### File upload to server plugins/ directory

```tsx
import getFileUploadUrl from '@/api/server/files/getFileUploadUrl';
import axios from 'axios';

const uploadUrl = await getFileUploadUrl(serverUuid);
const formData = new FormData();
formData.append('files', blob, 'plugin.jar');
await axios.post(uploadUrl, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params: { directory: '/plugins' },
});
```

### Implementation notes

- Loader dropdown: paper, spigot, bukkit, purpur, folia
- MC version filter: `['1.21', '1.21.1', ..., '1.22']`
- Uses pure inline `style` props (no twin.macro) to avoid template literal / JIT limitations
- Route: `path: '/plugins'`, `permission: 'file.*'`
- Downloads JAR from Modrinth → uploads via Pterodactyl file API (client-side proxy, no server-side code needed)

### CRITICAL: Modrinth API field naming

The Modrinth **search** API returns `project_id` (NOT `id`) in each hit object. If your TypeScript interface has `id: string`, it will be `undefined` at runtime because the JSON field is `project_id`. This causes `https://api.modrinth.com/v2/project/undefined/version` → 404.

**Correct interface:**
```typescript
interface ModrinthProject {
    slug: string;
    title: string;
    project_id: string;  // NOT `id` — the search API uses `project_id`
    // ...other fields
}
```

**Use `project.project_id` everywhere** when calling version/detail endpoints:
```typescript
axios.get(`${MODRINTH_API}/project/${project.project_id}/version`, ...)
```

The full project detail endpoint (`GET /v2/project/{id}`) accepts both the ID and slug, so `project.slug` also works there. But the version endpoint requires the actual `project_id` value.
