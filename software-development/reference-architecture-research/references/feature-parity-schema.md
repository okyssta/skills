# Feature Parity Database — Reference Example

A machine-readable YAML inventory cross-referencing features across reference
repositories and the target system. Each entry has structured fields for
priority, implementation strategy, source paths, and acceptance tests.

## Entry Schema

```yaml
- id: category.feature-name       # dotted hierarchy
  category: orchestration|agent|model|tool|memory|policy|observability|channels
  hermes: native|adapter|none     # reference repo 1
  openclaw: native|adapter|none   # reference repo 2
  roshi_target: native|p1|p2      # target system priority
  priority: p0|p1|p2
  implementation: clean-room|reuse-ariadne|adapter-via-mcp
  source_paths:                   # provenance — where the reference lives
    - references/hermes-agent/tools/delegate_tool.py
  acceptance_tests:               # pass/fail criteria — required for "shipped" status
    - "Spawn subagent with isolated context"
    - "Multiple subagents run concurrently"
  status: researched|designed|implementing|tested|benchmarked|shipped
```

## Categories Used

- agent: agent loop, streaming, tool calls, bounded execution, cancellation
- model: provider abstraction, provider adapters (OpenAI, Anthropic, etc.), usage accounting
- tool: registry, file ops, terminal, web, browser, MCP, send message
- memory: hybrid search, knowledge graph, scopes, shared surface, backup/restore
- orchestration: delegation, subagents, budget agent, workflow DAG, scheduling, triggers, artifact store, compilation, event sourcing
- policy: deny-by-default, approval gates, secret redaction, sandboxing, plugin isolation
- observability: traces, execution receipts, cost tracking
- channels: Telegram, Discord, Slack, WebChat
- skills: reusable procedures, hub
- plugin: system lifecycle, manifest
- cli: interactive, daemon, configuration, diagnostics
- session: persistence, search
- security: clarification, injection boundaries
- roshi-unique: intelligent router, token governor, change detection, verification confidence

## Real Output

See /root/docs/feature-parity.yaml for the full 67-entry database produced
during the Roshi Phase 0 architecture research.

Generated: 2026-07-18. Contains 67 features across 10 categories for 3
reference repos (Hermes Agent, OpenClaw, Ariadne) vs Roshi target.
