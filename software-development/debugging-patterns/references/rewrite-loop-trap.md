# Rewrite-Loop Trap

## The Pattern

Agent keeps editing source files after:
- `cargo check` / `cargo build` succeeds (0 errors)
- Multiple independent reviewers converge on "stop editing"
- The actual bugs are already fixed

## Symptoms
- Compulsive `patch`/`write_file` calls after green build
- Ignoring "build compiles, run the test" signals
- Rewriting working code instead of executing

## Root Cause

False productivity signal. Editing feels like progress; waiting for a test run feels like stalling. But once the compiler is happy, **the only way to find the next real bug is to run the system**.

## The Fix Protocol

When `cargo build` (or equivalent) succeeds:
1. **STOP EDITING** — put down the patch tool
2. **KILL ZOMBIES** — clean processes, sockets, DB files
3. **START PROCESSES** — memory worker, daemon, whatever the system needs
4. **RUN THE TEST** — the e2e/integration test, not unit tests
5. **READ THE OUTPUT** — the test tells you what's actually broken

## Session Evidence (Roshi v0.1)

- Build compiled clean at multiple timestamps
- Each time: 2-3 more edit cycles before finally running test
- References converged 4× with identical "stop editing" verdict
- When test finally ran: **16/16 PASS** on first clean execution
- The "bugs" the edits chased were phantoms; real bugs only appeared in test output

## Heuristic

> If you've made >2 edits since last green build without running the test, you're in the trap.

*Extracted from Roshi v0.1 gap-fill audit session, 2026-07-18*
