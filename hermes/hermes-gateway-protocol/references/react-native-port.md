# Porting the Hermes Gateway Client to React Native (Expo)

> How to build a Hermes Mobile app that connects to `hermes serve` remotely.
> Companion to the `hermes-gateway-protocol` skill — covers the React Native specific implementation details.

## Architecture

```
React Native (Expo)                  Remote Server (hermes serve)
┌──────────────────────────┐         ┌──────────────────────────────┐
│  GatewayClient (WS)      │ WebSocket│  /api/ws (JSON-RPC 2.0)     │
│  Zustand stores          │─────────│  /api/auth/login             │
│  React UI                │         │  /api/status                 │
│  expo-secure-store       │         │                              │
│  (tokens encrypted)      │         │  AIAgent + Tools + Skills    │
└──────────────────────────┘         └──────────────────────────────┘
```

**No Hermes agent runs on the phone.** The app is a thin WebSocket client — same pattern as the Hermes desktop app in remote mode.

## Stack Choices

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | React Native (Expo) | Desktop uses React + TypeScript. `@hermes/shared` is TypeScript — directly reusable. |
| State | Zustand | Lightweight, no boilerplate |
| WebSocket | Native WebSocket + custom JSON-RPC layer | Port `@hermes/shared`'s `JsonRpcGatewayClient` |
| Secure storage | `expo-secure-store` | Encrypted token persistence |
| Navigation | Expo Router (file-based) or React Navigation | Both work; use tabs for Chat / Dashboard / Settings |
| Markdown | `react-native-markdown-display` | GFM markdown for chat messages. **Requires `punycode` polyfill** (see below) |

## Porting @hermes/shared to React Native

The repo's `apps/shared/src/` contains three files that can be directly ported:

### 1. `json-rpc-gateway.ts` → `src/lib/gateway-client.ts`

The `JsonRpcGatewayClient` class uses only standard WebSocket API — no DOM or Node.js dependencies. Key changes when porting:

- Replace `WebSocket` imports with React Native's global `WebSocket` (available natively)
- Replace `addEventListener('message', ...)` with `onmessage = ...` (React Native uses the standard WebSocket API)
- Remove `requestIdPrefix` if not needed, or keep it for request tracing
- The 15-second connect timeout and 120-second request timeout are good defaults for mobile

Core implementation pattern (minimal):

```typescript
class GatewayClient {
  private socket: WebSocket | null = null
  private pending = new Map<string, PendingCall>()
  private nextId = 0

  async connect(url: string): Promise<void> {
    this.socket = new WebSocket(url)
    // Wait for open with timeout
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('connect timeout')), 15000)
      this.socket!.onopen = () => { clearTimeout(timer); resolve() }
      this.socket!.onerror = () => { clearTimeout(timer); reject(new Error('connect failed')) }
    })
  }

  call<T>(method: string, params: any = {}): Promise<T> {
    const id = `r${++this.nextId}`
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('timeout')), 120000)
      this.pending.set(id, { resolve, reject, timer })
      this.socket!.send(JSON.stringify({ jsonrpc: '2.0', id, method, params }))
    })
  }
}
```

### 2. `websocket-url.ts` → `src/lib/websocket-url.ts`

Replace `window.location` references with explicit host/protocol parameters since React Native has no `window`:

```typescript
// RN-compatible replacement
export function buildChatWsUrl(backendUrl: string, token: string): string {
  const base = backendUrl.replace(/\/+$/, '')
  const protocol = base.startsWith('https') ? 'wss:' : 'ws:'
  const host = base.replace(/^https?:\/\//, '')
  return `${protocol}//${host}/api/ws?token=${token}`
}
```

Keep `buildHermesWebSocketUrl()` for more complex scenarios (base paths, extra params).

### 3. Types → `src/types/gateway.ts`

Define all JSON-RPC types (GatewayEvent, JsonRpcFrame, ConnectionState, SessionInfo, ChatMessage) as plain TypeScript interfaces. No dependencies needed.

## Connection Flow (Mobile-Specific)

```
App Launch
  ↓
Load saved token from expo-secure-store
  ↓
[Token exists?]──No──→ Show Connect Screen
  ↓                       ↓
Verify token via          User enters URL + credentials
GET /api/status           ↓
  ↓                       POST /api/auth/login
[Valid?]──No──→ Clear     ↓
  ↓            token      Save token to SecureStore
  ↓                       ↓
Open WebSocket to         Open WebSocket
/api/ws?token=...
  ↓
● Connected — Chat UI active
```

### Connect Screen States

1. **URL input** — user enters `http://host:9119`
2. **Discover** — `GET /api/status` → detect auth providers
3. **Auth** — username/password form OR session token field
4. **Connect** — WebSocket open + RPC ready
5. **Error** — show error message, retry button

## Auth Implementation

### Username/Password
```typescript
// 1. Check server capabilities
const status = await fetch(`${backendUrl}/api/status`).then(r => r.json())
// → { auth_providers: ["basic"], ... }

// 2. Login
const auth = await fetch(`${backendUrl}/api/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password }),
}).then(r => r.json())
// → { token: "eyJ...", token_type: "bearer" }

// 3. Save encrypted
await SecureStore.setItemAsync('hermes_token', auth.token)

// 4. Connect
const wsUrl = buildChatWsUrl(backendUrl, auth.token)
```

### Token-Only Auth
For backends with `HERMES_DASHBOARD_SESSION_TOKEN` set:
```typescript
// Use the pre-shared token directly — no login step
const wsUrl = buildChatWsUrl(backendUrl, 'my-static-token')
```

## WebSocket Reconnection (Mobile)

Mobile networks drop WebSocket connections frequently. Implement:

```typescript
function startReconnect() {
  let attempt = 0
  const reconnect = async () => {
    attempt++
    const delay = Math.min(1000 * Math.pow(2, attempt), 30000)
    await sleep(delay)
    try {
      await client.connect(wsUrl)
      attempt = 0 // reset on success
    } catch {
      reconnect() // exponential backoff
    }
  }
  client.onState((state) => {
    if (state === 'closed' || state === 'error') reconnect()
  })
}
```

**Don't queue messages across app restarts** — the session may not exist anymore on the backend. Only queue during an active reconnection attempt within the same app session.

## Expo-Specific Notes

### expo-file-system (v57+ API)

The expo-file-system v57+ uses a **class-based API** (breaking change from earlier versions):

```typescript
import { Paths, File, DownloadTask } from 'expo-file-system'
import * as ExpoFileSystem from 'expo-file-system'
import * as IntentLauncher from 'expo-intent-launcher'

// OLD: FileSystem.cacheDirectory + DownloadResumable
// NEW:
const destination = new File(Paths.cache, 'update.apk')
const task = new DownloadTask(url, destination, {})

// Progress tracking:
task.addListener('progress', (progress: any) => {
  const pct = progress.totalBytes > 0
    ? Math.round((progress.bytesWritten / progress.totalBytes) * 100)
    : 0
})

// Execute:
const result = await task.downloadAsync()
const fileUri = result!.uri

// Install APK (Android):
const contentUri = await ExpoFileSystem.getContentUriAsync(fileUri)
await IntentLauncher.startActivityAsync(
  'android.intent.action.INSTALL_PACKAGE',
  { data: contentUri, flags: 1 }
)
```

### Metro Bundler Issues

**1. `punycode` not found**

`react-native-markdown-display` depends on `markdown-it` which imports `punycode`. This module was removed in Node.js 22.

**Fix:** `npm install punycode@2.3.1`

**2. Asset paths in Metro**

Require paths are relative to the source file, not the project root:
- `src/screens/ConnectScreen.tsx` → `require('../../assets/icon.png')`
- NOT `require('../assets/icon.png')` — this fails in Metro with "Unable to resolve module"

**3. Hermes bytecode on ARM64 Linux**

The `hermesc` binary in `node_modules/hermes-compiler/` ships only as x86_64. On ARM64 Linux (Apple Silicon, ARM64 VPS), Metro bundling with Hermes enabled fails.

**Fix options:**
- **For CI/CD (GH Actions):** Keep `hermesEnabled=true` in `gradle.properties` — they use x86_64 runners
- **For ARM64 local builds:** Set `hermesEnabled=false` in `gradle.properties` to fall back to JavaScriptCore
- **VPS workaround:** Install `qemu-user-static` to run x86_64 binaries, or build on x86_64 CI

## GitHub Actions CI/CD for APK Builds

### Workflow Template

```yaml
name: Build Android APK
on:
  push: { branches: [master] }
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4 { with: { node-version: '22' } }
      - uses: actions/setup-java@v4 { with: { distribution: 'temurin', java-version: '17' } }

      - run: npm ci
      - run: npx tsc --noEmit

      # Re-enable Hermes for CI (config defaults to disabled for ARM64)
      - run: sed -i 's/hermesEnabled=false/hermesEnabled=true/' android/gradle.properties

      # Build
      - run: cd android && ./gradlew assembleRelease --no-daemon

      # Capture APK
      - run: |
          APK=$(find android -name "app-release.apk" | head -1)
          cp "$APK" "HermesMobile-v0.0.1.apk"

      # Upload to GitHub Releases (avoids artifact storage quota)
      - run: |
          gh release create "v0.0.1-$(date +%Y%m%d)-${GITHUB_SHA::7}" \
            --title "Hermes Mobile v0.0.1" \
            --prerelease \
            "HermesMobile-v0.0.1.apk"
        env:
          GH_TOKEN: ${{ github.token }}
```

### Key Tips

- **Gradle first build is ~25 min** (downloads SDK components). Subsequent builds are faster with Gradle cache.
- **GitHub Actions artifact storage** has tight free-tier limits. Upload APKs to **Releases** instead (separate quota).
- **Node.js 20 deprecation warning** on GH Actions is cosmetic — the build still works.
- **`-e` flag on bash** in GH Actions causes the workflow to exit on first error, which is good but make sure your commands handle failure properly.

## Auto-Update via GitHub Releases

Check for updates on app launch:

```typescript
async function checkForUpdate(currentVersion: string): Promise<ReleaseInfo | null> {
  const response = await fetch(
    `https://api.github.com/repos/owner/hermes-mobile/releases/latest`,
    { headers: { 'User-Agent': 'HermesMobile/0.0.1' } }
  )
  if (!response.ok) return null

  const data = await response.json()
  const tagVersion = data.tag_name.replace(/^v/, '').split('-')[0]

  if (compareVersions(tagVersion, currentVersion) <= 0) return null

  return {
    version: tagVersion,
    assets: data.assets.map((a: any) => ({
      name: a.name,
      url: a.browser_download_url,
      size: a.size,
    })),
    body: data.body,
  }
}
```

Show an "Update Available" modal with:
- **"Update Now"** → download APK → trigger Android install intent
- **"Skip for now"** → dismiss, save skipped version to AsyncStorage

## Theme Porting

The Hermes dashboard has 6 built-in themes. Port them as a theme object with CSS-variable-like tokens:

```typescript
interface HermesTheme {
  id: string
  dark: boolean
  colors: {
    background: string
    foreground: string
    primary: string
    secondary: string
    accent: string
    muted: string
    border: string
    card: string
    destructive: string
    success: string
    warning: string
    // Semantic text colors
    textPrimary: string
    textSecondary: string
    textTertiary: string
    // Component-specific
    chatBubbleUser: string
    chatBubbleAssistant: string
    toolCallBg: string
  }
}
```

Use React Context + Zustand for state, persist to AsyncStorage.

## Pitfalls (Mobile-Specific)

- **Android NDK is x86_64-only.** You cannot build native Android code on ARM64 Linux without qemu-user or a prebuilt ARM64 NDK. Use GitHub Actions (x86_64 runners) for CI/CD builds.
- **expo-file-system API changed in v57** — the old `FileSystem.cacheDirectory` + `createDownloadResumable` API is replaced with class-based `Paths.cache`, `File`, `DownloadTask`. Check the Expo docs for your SDK version.
- **Metro bundler caches aggressively.** If you rename/move files, clear Metro cache: `npx expo start -c`
- **`addListener` on DownloadTask** — use `task.addListener('progress', handler)`, NOT `addProgressListener` (which doesn't exist in newer expo-file-system).
- **WebSocket close codes on mobile:** Expect frequent disconnects during network transitions (WiFi↔cellular). The client must reconnect transparently.
- **Don't block UI thread during connect.** Wrap WebSocket connection in a promise and show a loading state. The 15-second connect timeout prevents indefinite hangs.
