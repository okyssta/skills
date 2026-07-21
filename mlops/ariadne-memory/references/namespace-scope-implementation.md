# Namespace / Scope Implementation Notes

Use this when improving Ariadne's local-first memory isolation, Hermes plugin integration, or regressions around duplicate detection and recall leakage.

## Why it matters

Ariadne should prevent memory bleed between users, projects, sessions, and shared/global surfaces while staying zero-infrastructure and SQLite-only. Namespaces are the first isolation boundary future features should respect.

## Durable implementation pattern

Add first-class fields to the `memories` table rather than hiding them only in JSON metadata:

- `namespace TEXT NOT NULL DEFAULT 'default'`
- `scope TEXT NOT NULL DEFAULT 'session'`
- `user_id TEXT`
- `agent_id TEXT`
- `session_id TEXT`
- `project_id TEXT`

Create indexes for each isolation field. Add SQLite migrations in `_create_schema()` using `PRAGMA table_info(memories)` and `ALTER TABLE ... ADD COLUMN ...` so existing single-file DBs upgrade in place.

## Retrieval and duplicate rules

- Exact `content_hash` duplicates must be scoped by `namespace`; identical content in different namespaces is valid.
- FTS/vector/hybrid recall should accept a namespace filter and apply it before returning results.
- Contradiction checks should query only inside the active namespace.
- MinHash near-duplicate detection should be per-namespace, not one global index with namespace text prepended. Prefixing text can pollute shingles and may make exact same content across namespaces appear duplicate due shared content shingles; separate `Deduplicator` instances by namespace are cleaner.
- Stats can report aggregate dedup index size across all namespace indexes.

## Hermes plugin pattern

When wiring Ariadne into Hermes:

- `ariadne_remember` should expose `namespace` and persist `source`, `scope`, and `session_id` metadata.
- `ariadne_recall` should expose `namespace`.
- Plugin prefetch and `sync_turn()` should use `namespace="session"` if the plugin's default recall also searches `session`; otherwise newly stored session turns will not be recalled.
- Shared memory should use a distinct namespace such as `shared` and `scope="global"`.

## Regression tests to add first

Follow TDD. Write these tests before implementation:

1. Identical content in two namespaces creates two rows, while same content in one namespace deduplicates.
2. `get_memory()` returns namespace/scope/user/agent/session/project fields.
3. FTS recall with `namespace="alpha"` does not return `namespace="beta"` rows.
4. `AriadneMemory.recall()` does not leak across namespaces.
5. Near-duplicate detection allows same content in separate namespaces but still flags duplicates inside one namespace.

## Verification commands

```bash
python3 -m py_compile src/arriadne/storage.py src/arriadne/interface.py plugin/__init__.py
pytest -q
ruff check src/arriadne/storage.py src/arriadne/interface.py plugin/__init__.py tests/test_storage.py tests/test_edge_cases.py
mypy --python-version 3.12 src/arriadne/storage.py src/arriadne/interface.py
```

If project config targets Python 3.10 while installed NumPy stubs require Python 3.12 syntax, verify touched files with `mypy --python-version 3.12` rather than recording a negative tool claim.