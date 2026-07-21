# Fix Details: Desktop File Browser Sidebar Crash (Issue #58718)

## Issue
File browser sidebar in Hermes Desktop crashes when displaying folders containing binary files with error:
```
AttributeError: 'NoneType' object has no attribute 'splitlines'
```

## Crash Path
1. User opens folder containing binary files (PDF, PPTX, XLS, etc.)
2. Sidebar calls `readTextPreview(filePath)` in `preview-file.tsx` line 218
3. `readDesktopFileText()` returns null (stale Electron preload / failed IPC)
4. `readTextPreview` returns null directly (no guard)
5. `LocalFilePreview` accesses `result.binary` → crash
6. If it gets past that, `chunkTextLines()` calls `text.split('\n')` on null → crash

## Key Files
- `apps/desktop/src/app/chat/right-rail/preview-file.tsx` — `readTextPreview()` (line 218), `LocalFilePreview` (line 556)
- `apps/desktop/src/components/chat/fixed-row-window.ts` — `chunkTextLines()` (line 43) calls `text.split('\n')`
- `apps/desktop/src/lib/desktop-fs.ts` — `readDesktopFileText()` (line 69) wraps Electron IPC
- `apps/desktop/src/global.d.ts` — `HermesReadFileTextResult` type (line 551) declares `text: string` non-optional
- `apps/desktop/electron/main.cjs` — `hermes:readFileText` IPC handler (line 6583)
- `hermes_cli/web_server.py` — `/api/fs/read-text` endpoint (line 1980) for remote mode

## Exact Code Fix
Replace lines 218-244 in `preview-file.tsx`:

```typescript
// BEFORE (broken):
async function readTextPreview(filePath: string) {
  try {
    return await readDesktopFileText(filePath)
  } catch (error) { ... }
}

// AFTER (fixed):
async function readTextPreview(filePath: string) {
  try {
    const result = await readDesktopFileText(filePath)
    if (result === null || typeof result === 'string') {
      const text = result === null ? '' : result
      return {
        binary: false,
        byteSize: 0,
        language: 'text',
        mimeType: 'text/plain',
        path: filePath,
        text,
        truncated: false
      }
    }
    return result
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    if (!message.includes("No handler registered for 'hermes:readFileText'")) {
      throw error
    }
    // Back-compat fallback via readFileDataUrl (existing code unchanged)
    const dataUrl = await window.hermesDesktop.readFileDataUrl(filePath)
    // ... rest of existing fallback
  }
}
```

## Verification
- `git diff HEAD -- apps/desktop/src/app/chat/right-rail/preview-file.tsx` confirms the change
- Binary files in folders show appropriate warning UI, not crash
- Text files display with syntax highlighting as before
- Image files and editor functionality unaffected