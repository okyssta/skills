# Rust Async UDS Patterns — Debugging Reference

## tokio::net::UnixStream vs std::os::unix::net::UnixStream

**Symptom:** `set_read_timeout` not found on `UnixStream`

**Cause:** std blocking stream has `set_read_timeout`; tokio async stream does not.

**Fix:** Wrap reads in `tokio::time::timeout()` instead:

```rust
// BAD - tokio stream has no set_read_timeout
stream.set_read_timeout(Some(Duration::from_secs(5)))?;
stream.read_exact(&mut buf)?;

// GOOD - timeout wraps the whole read
tokio::time::timeout(Duration::from_secs(5), stream.read_exact(&mut buf))
    .await
    .map_err(|_| anyhow::anyhow!("read timeout"))?;
```

## JSON Framing over UDS (4-byte length prefix)

```rust
// Write
let body = serde_json::to_vec(&req)?;
let len = (body.len() as u32).to_be_bytes();
stream.write_all(&len).await?;
stream.write_all(&body).await?;
stream.flush().await?;

// Read
let mut len_buf = [0u8; 4];
stream.read_exact(&mut len_buf).await?;
let resp_len = u32::from_be_bytes(len_buf) as usize;
let mut resp_buf = vec![0u8; resp_len];
stream.read_exact(&mut resp_buf).await?;
let resp: Response = serde_json::from_slice(&resp_buf)?;
```

## MemoryClient Idempotency — Check Before INSERT

```rust
let existing = sqlx::query_as::<_, (String, String)>
    ("SELECT id, status FROM approvals WHERE run_id = ? AND step_id = ? ORDER BY created_at DESC LIMIT 1")
    .bind(run_id).bind(step_id)
    .fetch_optional(&db).await?;
```

Saves creating orphaned approval rows on retry.

## Verify Step: JSON Values vs Strings

**Bug:** `output.as_str()` returns `None` for JSON objects (all non-string outputs)

```rust
// BROKEN — only catches string outputs
let prior: Vec<&str> = steps.iter()
    .filter_map(|s| s.output.as_ref().and_then(|o| o.as_str()))
    .collect();

// FIXED — catches any non-null JSON
let count = steps.iter()
    .filter(|s| s.output.is_some() && !s.output.as_ref().unwrap().is_null())
    .count();
```

## Migration Safety: ALTER TABLE ADD COLUMN Without IF NOT EXISTS

**Problem:** `ALTER TABLE ADD COLUMN` crashes on restart if column exists (SQLite < 3.37.3 doesn't support `IF NOT EXISTS` on column add)

**Fix:** Use `pragma_table_info` runtime check:

```rust
let cols: Vec<(String,)> = sqlx::query_as("SELECT name FROM pragma_table_info('steps')")
    .fetch_all(&db).await?;
let names: HashSet<_> = cols.into_iter().map(|c| c.0).collect();

if !names.contains("step_def_id") {
    sqlx::query("ALTER TABLE steps ADD COLUMN step_def_id TEXT").execute(&db).await?;
}
```

## `read_exact` + `tokio::time::timeout` for Fixed-Size Buffers

`read_exact` is the correct method for reading a fixed-size buffer from a tokio stream. Pair with `tokio::time::timeout` to enforce deadlines since tokio's `UnixStream` has no `set_read_timeout`.

*Extracted from Roshi v0.1 executor debugging, 2026-07-18*
