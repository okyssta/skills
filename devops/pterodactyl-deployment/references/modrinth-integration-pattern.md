# Modrinth Integration Pattern for Pterodactyl Panel

This document captures the pattern used to add a Modrinth plugin browser/installer to the Pterodactyl panel.

## Core Approach

1. **Frontend Component**: Created a new React component (`PluginsContainer.tsx`) that:
   - Uses Modrinth's public API (no auth required for read operations)
   - Implements debounced search (350ms) to avoid rate limiting
   - Shows plugin cards with install buttons + version pickers
   - Handles file upload via Pterodactyl's existing file API

2. **API Endpoints Used**:
   - Search: `GET https://api.modrinth.com/v2/search?query={term}&facets=[["project_type:plugin"]]&limit=24`
   - Project: `GET https://api.modrinth.com/v2/project/{id}`
   - Versions: `GET https://api.modrinth.com/v2/project/{id}/version`
   - Version files: Direct download from `version.files[].url`

3. **Installation Flow**:
   - User clicks install on a card/detail view
   - Component fetches latest compatible version (filtered by server versions: 1.21-1.22 and loaders: paper/spigot/bukkit/purpur/folia)
   - Downloads the primary JAR file from Modrinth as a blob
   - Uploads to server via Pterodactyl's `/api/client/servers/{uuid}/files/upload` endpoint
   - Files land in `/plugins/` directory by default

4. **Key Implementation Details**:
   - Uses axios for HTTP requests (already available in Panel)
   - Leverages existing `getFileUploadUrl` API helper
   - Reuses Button and Spinner components for UI consistency
   - Implements proper loading states and error handling
   - Uses inline styles for dynamic values (due to twin.macro limitations)
   - Version picker dropdown closes on outside click
   - Toasts success/error messages using existing flash system

5. **File Structure**:
   ```
   resources/scripts/
   └── components/
       └── server/
           └── plugins/
               └── PluginsContainer.tsx
   ```

6. **Routing**:
   - Added route in `resources/scripts/routers/routes.ts`
   - Path: `/plugins`
   - Permission: `file.*` (same as Files tab)
   - Component: `PluginsContainer`

7. **Build Process**:
   - Requires rebuilding the Panel Docker image after changes
   - Use `--no-cache` to ensure JS changes are picked up
   - Update docker-compose to use custom image: `pterodactyl/panel:custom`

## Pitfalls Specific to This Implementation

- **Modrinth search API returns `project_id`, NOT `id`**: This is the #1 gotcha. The search hits have `project_id` as the field name. If your TypeScript interface uses `id: string`, it will be `undefined` at runtime, causing version endpoint URLs like `/project/undefined/version` → 404. Always use `project.project_id` for API calls.
- **Modrinth API version filtering**: Must pass `loaders` and `game_versions` as JSON strings in query params
- **File upload**: Must use multipart/form-data with `directory` parameter set to `/plugins`
- **Version compatibility**: Always filter versions by your target server versions (we hardcoded 1.21-1.22)
- **Loader compatibility**: Some plugins only work with specific loaders (Fabric, Forge, etc.) - we default to Paper but allow selection
- **Rate limiting**: While Modrinth's API is generous, excessive searching could trigger limits - debounce helps
- **Blob handling**: Must set `responseType: 'blob'` when downloading JARs from Modrinth
- **File type**: Use `application/java-archive` as MIME type for JAR uploads

## Reference Implementation

The full implementation lives in:
`resources/scripts/components/server/plugins/PluginsContainer.tsx`

Key functions to study:
- `search()` - Modrinth search with facets
- `openDetail()` - fetches project + versions for detail view
- `CardInstallButton` - inline install + version picker on cards
- `DetailInstallButton` - install section on detail page
- `installVersion()` - core download/upload logic

## Testing Checklist

1. [ ] Search returns results with cards showing icon, title, description, stats
2. [ ] Clicking card opens detail view with full description and version list
3. [ ] Install button on card downloads latest compatible version
4. [ ] Version picker (▼) shows list of compatible Paper versions
5. [ ] Selecting a version from picker installs that specific version
6. [ ] Detail view install works with loader selector and version list
7. [ ] Success/error toasts appear and auto-clear
8. [ ] Uploaded JAR appears in server's `/plugins/` directory via file manager
9. [ ] Server restart loads the new plugin
10. [ ] Build process: `docker build --no-cache -t pterodactyl/panel:custom .` followed by `docker compose up -d --force-recreate panel`