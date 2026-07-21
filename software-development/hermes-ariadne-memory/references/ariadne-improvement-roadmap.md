# Ariadne improvement roadmap research

Use this reference when asked to improve Ariadne while preserving its core positioning: **local-first, zero infrastructure, single-file memory**.

## Current baseline

Ariadne already has a strong local-first core:

- SQLite WAL single-file storage.
- FAISS in-process vector search, auto FlatIP -> IVFFlat.
- SQLite FTS5 keyword/BM25 search.
- Reciprocal Rank Fusion hybrid search.
- Manual knowledge graph via SQLite recursive CTE traversal.
- MinHash LSH + SHA-256 duplicate detection.
- Ebbinghaus retention scoring and priority eviction.
- Hermes plugin exposing `ariadne_*` tools.
- Dashboard, backup/restore/export/import, addons system.

Verified during research: clean venv test run passed `166 passed in 18.06s`. Code metrics were roughly 88 scanned files, 8,642 code lines, 24 Python files / 5,399 Python code lines.

## Competitor signals worth copying locally

### Mem0

Relevant strengths:

- Strong benchmark posture: LoCoMo, LongMemEval, BEAM.
- Ingest -> Search -> Evaluate pipeline, not just storage.
- Multi-signal retrieval: semantic + keyword + entity matching.
- Fact extraction from raw conversation messages.
- Scoped memory organization: `user_id`, `agent_id`, `run_id`.
- Async API and memory history/audit trail.
- Optional rerankers.

Local-first Ariadne adaptations:

1. Add LoCoMo/LongMemEval/BEAM benchmark adapters.
2. Add deterministic entity matching as a retrieval signal.
3. Add indexed scopes/namespaces (`user_id`, `agent_id`, `run_id`, project/session).
4. Add async API parity.
5. Add change history/audit trail.
6. Optional local reranker hook, disabled by default.

### Zep / Graphiti

Relevant strengths:

- Temporal Context Graph.
- Non-lossy raw episodes plus extracted semantic entities/relations.
- Bi-temporal facts: validity periods and invalidation.
- Point-in-time queries.
- Hybrid search over time + full-text + semantic + graph.
- Fact invalidation instead of overwriting contradictory facts.
- Custom entity types and community graph organization.

Local-first Ariadne adaptations:

1. Add an `episodes` table for raw turns/messages/documents.
2. Add temporal fact/edge fields: `valid_from`, `valid_to`, `invalidated_at`, `source_episode_id`.
3. Implement fact supersession/invalidation.
4. Add point-in-time graph and recall filters.
5. Add optional local community detection / graph clustering.

### Letta / MemGPT

Relevant strengths:

- Agent state is first-class: memory blocks, messages, tool calls, runs, steps.
- Core/pinned memory blocks in context; archival memory outside context.
- Agents can edit memory through tools.
- Virtual context management and paging.

Local-first Ariadne adaptations:

1. Add memory tiers: `core`, `working`, `archival`, `superseded`.
2. Add structured profile blocks updated in-place.
3. Add token-budget-aware context packer.
4. Add memory operation log with runs/steps/session IDs.

### LangMem / LangGraph memory

Relevant strengths:

- Clear semantic / episodic / procedural types.
- Profiles vs collections distinction.
- Memory enrichment/consolidation balances inserts, updates, deletes.
- Namespaces by organization/user/application/context.
- Recall combines semantic similarity, importance, and memory strength.

Local-first Ariadne adaptations:

1. Namespaces as first-class indexed columns.
2. Profile schema support: `UserProfile`, `ProjectProfile`, `AgentProfile` JSON docs.
3. Better consolidation semantics; not just text concatenation.
4. Developer-supplied extraction/update policies that can run without cloud.

## P0 roadmap

1. **Automatic memory extraction pipeline**
   - Add `episodes` table.
   - Store raw turns as episodes, not truncated durable memories.
   - Extract facts/preferences/events separately.
   - Start with deterministic extractors; optional local LLM extractor later.

2. **First-class namespaces/scopes**
   - Add indexed columns: `namespace`, `user_id`, `agent_id`, `session_id`, `project_id`, `scope`.
   - Make Hermes plugin honor `scope`, `source`, `session_id`, and metadata filters.
   - Prevent cross-user/project recall bleed.

3. **Temporal graph/fact model**
   - Add fact validity fields and source provenance.
   - Implement supersession/invalidation instead of hard deletion or regex-only contradiction hints.
   - Add point-in-time graph and recall.

4. **Multi-signal retrieval**
   - Extend RRF beyond vector + FTS.
   - Add entity overlap, graph-neighborhood boost, temporal score, importance/retention tie-breaker.
   - Return score explanations, e.g. `score_parts`.

5. **Quality benchmark harness**
   - Add LoCoMo/LongMemEval/BEAM adapters.
   - Start with retrieval-only metrics: recall@k, MRR, nDCG, support hit rate, abstention/no-support accuracy.
   - Add optional local answerer/judge support later.

## P1/P2 roadmap

- `AsyncAriadneMemory` using `asyncio.to_thread` initially.
- Weighted FTS columns: content, summary, entities, tags.
- Query intent parser for time/entity/person/project hints.
- Type-aware consolidation policies.
- Fact-level contradiction handling with single-valued vs multi-valued predicates.
- Persistent FAISS cache/sidecar/BLOB with checksum fallback to reduce cold start.
- Optional encryption-at-rest and encrypted backups.
- Multi-process WAL/stress tests.
- Pinned/core context packer: `context_pack(query, token_budget=...)`.
- Structured profile table with schema-aware JSON updates.
- Entity alias/canonicalization layer.
- Multimodal metadata hooks.
- Dashboard review flows for timeline, temporal graph, duplicate/contradiction queue, benchmark comparisons.

## Implementation ticket sketches

### Namespace columns

Add columns to `memories`: `namespace`, `user_id`, `agent_id`, `session_id`, `project_id`, `scope`; add indexes; extend remember/recall/update/export/import. Default namespace should be `default` for backward compatibility.

### Episodes table

```sql
CREATE TABLE episodes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  namespace TEXT NOT NULL DEFAULT 'default',
  session_id TEXT,
  role TEXT,
  content TEXT NOT NULL,
  created_at REAL NOT NULL,
  metadata TEXT,
  source TEXT
);
```

Link extracted memories to source episodes via `source_episode_id`.

### Fact table

```sql
CREATE TABLE facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject_entity_id INTEGER NOT NULL,
  predicate TEXT NOT NULL,
  object_text TEXT NOT NULL,
  object_entity_id INTEGER,
  source_episode_id INTEGER,
  confidence REAL DEFAULT 1.0,
  valid_from REAL,
  valid_to REAL,
  invalidated_at REAL,
  created_at REAL NOT NULL,
  metadata TEXT
);
```

### Deterministic extractor v1

Patterns to cover first:

- Identity/preferences: `call me X`, `my name is X`, `I prefer X`, `I like/dislike X`, `I use X`.
- Project facts: repo/path/deployment/service/database facts.
- Assistant verified actions only when backed by tool evidence or explicit success.

### Multi-signal ranking

Keep explainable deterministic scoring:

```text
score = RRF(vector_rank, fts_rank, entity_rank, graph_rank)
      + alpha * importance
      + beta  * retention
      + gamma * temporal_match
      - delta * stale_or_invalidated_penalty
```

Return `score_parts` so dashboard/users can see why a memory matched.

## Benchmark pitfall

`benchmarks/run_benchmarks.py` can exceed a 600s tool timeout because it runs 1K/10K/50K loops. Before using it in CI or interactive work, add a `--quick` mode and `--sizes 1000,5000` style argument.