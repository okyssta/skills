# Browser-Safe Context (AsyncLocalStorage Replacement)

When extracting server-side code for a client-side SPA, `node:async_hooks` / `AsyncLocalStorage` is the most common Node.js API that breaks the browser build.

## Original (Node.js-dependent)

```typescript
import { AsyncLocalStorage } from "node:async_hooks"

export namespace Context {
  export class NotFound extends Error {}

  export function create<T>() {
    const storage = new AsyncLocalStorage<T>()
    return {
      use() {
        const result = storage.getStore()
        if (!result) throw new NotFound()
        return result
      },
      provide<R>(value: T, fn: () => R) {
        return storage.run(value, fn)
      },
    }
  }
}
```

## Browser-Safe Replacement

```typescript
export namespace Context {
  export class NotFound extends Error {}

  export function create<T>() {
    let store: T | undefined
    
    return {
      use() {
        if (!store) throw new NotFound()
        return store
      },
      provide<R>(value: T, fn: () => R) {
        const prev = store
        store = value
        try {
          return fn()
        } finally {
          store = prev
        }
      },
    }
  }
}
```

## Why This Works

- SPA context is single-request, so async storage isn't needed
- The synchronous closure pattern handles the SPA's simpler lifecycle
- No Node.js imports = no vite-browser-external errors
- Same API surface — no callers need changes
