# React Native (Expo) Hermes Client — Porting Guide

> How to build a Hermes mobile client in React Native (Expo), based on the Hermes Mobile app at github.com/kyssta-exe/hermes-mobile.

## Architecture

```
React Native (Expo)                  Remote Hermes Server
┌──────────────────────────┐       ┌────────────────────────┐
│  GatewayClient (WS)      │  WS   │  hermes serve           │
│  Zustand stores          │──────▶│  /api/ws (JSON-RPC)     │
│  React Navigation (tabs) │       │  /api/auth/login        │
│  expo-secure-store       │       │  /api/status            │
└──────────────────────────┘       └────────────────────────┘
```

**No Hermes agent runs on the phone.** The app is a thin WebSocket client to a remote `hermes serve` backend.

## Stack Choices

| Layer | Choice | Why |
|-------|--------|-----|
| Framework | Expo (React Native) | Desktop/web use React; shares @hermes/shared TypeScript types |
| Navigation | Custom bottom tab bar | Chat / Dashboard / Settings — keeps it simple without react-navigation |
| State | Zustand | Lightweight, matches desktop's nanostores pattern |
| WS Client | Ported @hermes/shared JsonRpcGatewayClient | Framework-agnostic, full event dispatch, reconnect |
| Secure Storage | expo-secure-store | Encrypted token persistence |
| Markdown | react-native-markdown-display | GFM rendering for chat messages |
| Theme | Custom token-based with 6 themes | Ported from Hermes web dashboard |
| CI/CD | GitHub Actions → gh release | Build APK, upload to Releases (avoids artifact quota) |
| Auto-Update | GitHub Releases API | Check latest release, download + install APK |

## Core Library: Porting @hermes/shared

The Hermes agent repo's `apps/shared/src/` has three files to port:

### 1. `json-rpc-gateway.ts` → `src/lib/gateway-client.ts`

The `JsonRpcGatewayClient` class needs minimal changes for React Native:
- Replace `WebSocketLike` type with React Native's built-in `WebSocket`
- Remove `DOMException` references (use `Error` instead, or keep `AbortError` if needed)
- Keep the `pending` Map, `eventHandlers` Map, `stateHandlers` Set pattern
- Connect timeout: 15s (matches desktop)
- Request timeout: 120s (tool calls can take long)

Key class structure:
```typescript
class GatewayClient {
  async connect(wsUrl: string): Promise<void>
  close(): void
  on(type: GatewayEventName, handler): () => void
  onState(handler): () => void
  request<T>(method, params, timeoutMs?): Promise<T>
  get connectionState(): ConnectionState
  get connected(): boolean
}
```

### 2. `websocket-url.ts` → `src/lib/websocket-url.ts`

Replace `window.location` references with explicit `host` parameter:
```typescript
export function buildHermesWebSocketUrl(options: {
  path: string       // "/api/ws"
  host: string       // "host:port"
  protocol?: string  // "http" or "https"
  authParam?: [string, string]  // ["token", value]
  params?: Record<string, string>
}): string
```

### 3. Types → `src/types/gateway.ts`

Define all protocol types: `GatewayEvent`, `GatewayEventName`, `ConnectionState`, `JsonRpcFrame`, `SessionInfo`, `ChatMessage`, `ToolCall`, etc.

## Project Structure

```
hermes-mobile/
├── App.tsx                 # Root: theme provider, connect check, tab navigation
├── app.json                # Expo config
├── src/
│   ├── lib/
│   │   ├── gateway-client.ts   # Ported JsonRpcGatewayClient
│   │   ├── websocket-url.ts    # WS URL builder
│   │   ├── auth.ts             # Login, status check, secure storage
│   │   └── update-checker.ts   # Auto-update via GitHub Releases
│   ├── stores/
│   │   ├── connection.ts       # Backend URL, token, WS state (Zustand)
│   │   └── chat.ts             # Sessions, messages, streaming (Zustand)
│   ├── hooks/
│   │   └── useGateway.ts       # Wire WS events → stores
│   ├── screens/
│   │   ├── ConnectScreen.tsx   # Server URL + auth form
│   │   ├── ChatScreen.tsx      # Streaming chat + session switcher
│   │   ├── DashboardScreen.tsx # Status, sessions, connection info
│   │   └── SettingsScreen.tsx  # Connection info, theme picker, disconnect
│   ├── components/
│   │   ├── TabBar.tsx          # Bottom tab nav (Chat|Dashboard|Settings)
│   │   ├── UpdatePrompt.tsx    # "Update Available" modal
│   │   ├── chat/
│   │   │   ├── MessageList.tsx # Markdown-rendered message bubbles
│   │   │   ├── Composer.tsx    # Text input + send button
│   │   │   └── SessionSwitcher.tsx  # Slide-out session drawer
│   │   └── ui/
│   │       └── Themed.tsx      # ThemedView, Card, ThemedButton, StatusBadge
│   └── theme/
│       ├── themes.ts           # 7 theme color palettes
│       └── ThemeProvider.tsx    # Zustand store + React context
```

## Connection Flow (ConnectScreen)

```typescript
// 1. On mount, try to restore saved connection
const saved = await loadConnection()
if (saved) {
  await connect(saved.backendUrl, saved.token) // auto-reconnect
}

// 2. User enters URL → tap "Check Server"
const status = await checkServerStatus(url)
// Shows: agent version, auth providers, gateway state

// 3. User selects auth mode (password or token) and enters credentials
if (mode === 'password') {
  await connectWithPassword(url, username, password)
} else {
  await connect(url, sessionToken)
}

// 4. connect() does:
await saveConnection({ backendUrl, token })
const wsUrl = buildChatWsUrl(backendUrl, token)
const client = new GatewayClient()
client.onState((state) => setConnectionState(state))
await client.connect(wsUrl)
```

## Theme System

Port the 6 Hermes dashboard themes + Nous Blue as TypeScript objects:

```typescript
interface HermesTheme {
  id: string
  name: string
  dark: boolean
  colors: {
    background, foreground, primary, secondary, accent,
    muted, border, card, destructive, success, warning,
    textPrimary, textSecondary, textTertiary,
    chatBubbleUser, chatBubbleAssistant, toolCallBg,
    statusBarBg, inputBg
  }
  fonts: { ui: string; mono: string }
  spacing: number
  radius: { sm, md, lg, xl, full }
}
```

Store + Context pattern:
```typescript
// Zustand store persists to AsyncStorage
const useThemeStore = create(...)
// React context provides to all components
<ThemeProvider> → useTheme() → { theme, setTheme, themeId }
```

## Tab Navigation

Simple custom tab bar (no react-navigation needed):
```typescript
// App.tsx
const [activeTab, setActiveTab] = useState<'chat' | 'dashboard' | 'settings'>('chat')

// Connected? → show tabs
return (
  <View style={{flex: 1}}>
    {activeTab === 'chat' && <ChatScreen />}
    {activeTab === 'dashboard' && <DashboardScreen />}
    {activeTab === 'settings' && <SettingsScreen />}
    <TabBar activeTab={activeTab} onTabChange={setActiveTab} />
  </View>
)
```

Each screen is a full-height View — no nested navigators needed for v1.

## Auto-Update Checker

On app startup:
1. `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`
2. Parse version from tag (e.g. `v0.0.1-20260708-abc` → `0.0.1`)
3. Compare with `CURRENT_VERSION` using semver comparison
4. If newer and not skipped, show "Update Available" modal

Download + install:
```typescript
// 1. Download APK
const destination = new File(Paths.cache, 'HermesMobile-update.apk')
const task = new DownloadTask(downloadUrl, destination, {})
task.addListener('progress', (p: DownloadProgress) => updateProgress(p.percentage))
const result = await task.downloadAsync()

// 2. Install on Android
const contentUri = await ExpoFileSystem.getContentUriAsync(result.uri)
await IntentLauncher.startActivityAsync('android.intent.action.INSTALL_PACKAGE', {
  data: contentUri,
  flags: 1,  // FLAG_GRANT_READ_URI_PERMISSION
})
```

Track skipped versions in AsyncStorage under `hermes_skip_version` key.

## GitHub Actions CI/CD Pattern

```yaml
# .github/workflows/build-apk.yml
on:
  push: { branches: [master] }

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4 with node-version: '22'
      - uses: actions/setup-java@v4 with distribution: 'temurin' java-version: '17'
      - run: npm ci
      - run: npx tsc --noEmit
      - run: cd android && ./gradlew assembleRelease --no-daemon
      - run: |
          APK=$(find android -name "app-release.apk" -type f | head -1)
          cp "$APK" "HermesMobile-v0.0.1.apk"
      - run: |
          gh release create "v0.0.1-$(date +%Y%m%d)-${GITHUB_SHA::7}" \
            --prerelease "HermesMobile-v0.0.1.apk"
```

Key details:
- Use `temurin` JDK 17 (JDK 25 breaks native Android code)
- Enable Hermes: `sed -i 's/hermesEnabled=false/hermesEnabled=true/' android/gradle.properties` (because the committed gradle.properties has it disabled for ARM64 builds)
- The `android/` directory is committed from `npx expo prebuild` so CI doesn't need to run it
- Release storage is separate from artifact storage — use `gh release create` not `actions/upload-artifact`

## Common Pitfalls (React Native Specific)

### punycode module
`react-native-markdown-display` → `markdown-it` → `require('punycode')`.
In Node 22+, punycode is removed. Fix: `npm install punycode@2.3.1`.

### Hermes bytecode compiler on ARM64
`hermesc` in `node_modules/hermes-compiler/hermesc/linux64-bin/hermesc` is x86_64-only.
Code that works on GH Actions (x86_64) will fail on ARM64 VPS if Hermes is enabled.
Set `hermesEnabled=false` in `android/gradle.properties` for ARM64 builds.

### CMake native modules on ARM64
`expo-modules-core` and `react-native-screens` compile C++ code via CMake + NDK.
The NDK toolchains (`clang`, etc.) are x86_64-only. You cannot build these on ARM64
without qemu-user or a cross-compilation NDK. Use x86_64 CI runners always.

### expo-file-system v57+ API
The newer expo-file-system replaces the old function-based API:
- `FileSystem.cacheDirectory` → `Paths.cache` (returns `Directory`)
- `FileSystem.createDownloadResumable(...)` → `new DownloadTask(url, destination, options)`
- `FileSystem.DownloadProgressData` → `DownloadProgress`
- `FileSystem.getContentUriAsync()` still works but is now on the `ExpoFileSystem` named export

### GitHub Secrets in workflow `if:` conditions
GitHub Actions does NOT allow `secrets.*` in `if:` condition expressions.
To conditionally sign APK based on secret presence, use a step that checks
the env var set via `${{ secrets.MY_SECRET != '' && 'true' || 'false' }}`.

## See Also

- `hermes-client-development` skill (this umbrella) — full protocol, auth, setup docs
- `references/json-rpc-protocol.md` — full method/event catalog
- `references/connection-flow.md` — detailed connection sequence
