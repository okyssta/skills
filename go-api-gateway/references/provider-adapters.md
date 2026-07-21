# Provider Adapter Pattern

Translate an internal chat request format to each provider's native API format and back.

## Interface

```go
type Adapter interface {
    Name() string
    Chat(ctx context.Context, req Request) (*Response, error)
    Models() []string
}
```

## Internal Format

```go
type Request struct {
    Model       string
    Messages    []Message  // {Role, Content}
    Temperature float64
    MaxTokens   int
}

type Response struct {
    ID      string
    Model   string
    Content string
    Usage   *Usage  // {Input, Output}
}
```

## OpenAI Adapter

- Base URL: `https://api.openai.com/v1`
- Auth: `Authorization: Bearer <key>`
- Request: `POST /chat/completions` with `{model, messages, temperature, max_tokens}`
- Response: choices[0].message.content, usage.prompt_tokens/completion_tokens
- 1:1 mapping with internal format (because internal is based on OpenAI)

## Anthropic Adapter (Format Translation)

Anthropic differs from OpenAI in several ways:

| Difference | OpenAI | Anthropic |
|-----------|--------|-----------|
| Auth header | `Authorization: Bearer` | `x-api-key` |
| API version | — | `anthropic-version: 2023-06-01` |
| System prompt | Message with role "system" | Separate `system` field |
| Endpoint | `/chat/completions` | `/messages` |
| Response content | `choices[0].message.content` | `content[0].text` |
| Extra field | — | `max_tokens` is required, not optional |

Translation steps:
1. Iterate messages: system → `req.System`, others → `req.Messages`
2. Set `anthropic-version` header
3. Parse response: extract text from content blocks, map usage
4. Set `max_tokens` to 4096 if not provided (Anthropic requires it)

## Adding a New Provider

1. Create `providers/<name>.go` implementing `Adapter`
2. Register in registry by provider name
3. Add test config to config.json defaults

## Shared HTTP Helper

```go
func doJSON(ctx context.Context, url string, reqBody, respBody interface{}, headers map[string]string) error {
    var buf bytes.Buffer
    json.NewEncoder(&buf).Encode(reqBody)
    req, _ := http.NewRequestWithContext(ctx, "POST", url, &buf)
    req.Header.Set("Content-Type", "application/json")
    for k, v := range headers { req.Header.Set(k, v) }
    resp, err := httpClient.Do(req)
    if err != nil { return err }
    defer resp.Body.Close()
    if resp.StatusCode >= 400 {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("status %d: %s", resp.StatusCode, body)
    }
    return json.NewDecoder(resp.Body).Decode(respBody)
}
```

## Pitfalls

- Anthropic `max_tokens` is **required** — OpenAI treats it as optional. Always set a default.
- Google Gemini uses different message roles and has no system field — needs its own adapter.
- Local providers (Ollama, vLLM) are OpenAI-compatible but may have different model naming.
- Rate limit errors come in different shapes — OpenAI returns JSON with error.type, Anthropic returns JSON with error.type too but different structure.
