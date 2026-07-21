# Routing Engine Pattern

The core of an LLM routing proxy is deciding which provider/model to use for each request.

## Architecture

```
Request content → Rule scoring → Best match → Fallback chain → Provider
                      ↓                    ↓              ↓
               all rules scored      highest score   try each in order
```

## Rule Model

```go
type Rule struct {
    Name      string   // human-readable label (logged)
    Condition string   // space-separated keywords
    Targets   []Target // ordered fallback chain
}

type Target struct {
    Provider string
    Model    string
}
```

## Scoring Algorithm

1. Extract keywords from condition string (strip stopwords, lowercase, keep words >2 chars)
2. For each keyword, check if it appears as substring in request content
3. Score = hits / total_keywords (0.0–1.0)
4. Rule with highest score wins

```go
func score(condition, content string) float64 {
    kw := keywords(condition)
    if len(kw) == 0 { return 0 }
    hits := 0
    for _, w := range kw {
        if strings.Contains(content, w) { hits++ }
    }
    return float64(hits) / float64(len(kw))
}
```

## Fallback Execution

When a request arrives:
1. Route content → get best-matching rule + its target chain
2. Try targets in order
3. If a target succeeds → cache and return
4. If all fail → return 502 with last error

```go
func (s *Server) handleChat(req) {
    result := s.router.Route(content)
    for _, target := range result.Targets {
        resp, err := provider.Chat(req)
        if err == nil {
            cache.Set(key, resp)
            return resp
        }
        log.Error(err) // try next
    }
    return 502
}
```

## Upgrade Path

- `ponytail:` naive keyword matcher. Add semantic matching (embedding similarity) when:
  - Users consistently override routing decisions manually
  - False-positive rate exceeds acceptable threshold
  - Provider cost savings from better routing would justify the infra

## Tests

Test three cases:
1. Content clearly matches a rule → expects that rule's targets
2. Content matches nothing → expects fallback chain
3. Edge conditions (empty content, no rules) → panics/errors handled
