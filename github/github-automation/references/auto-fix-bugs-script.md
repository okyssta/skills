# AUTO-FIX-BUGS Script Reference

**Script:** `/root/.hermes/scripts/auto-fix-bugs.py`
**Cron:** Every 90 minutes, `NousResearch/hermes-agent`

## Key Parameters (current values)

| Parameter | Value | Location in script |
|-----------|-------|--------------------|
| `gh issue list --label bug --limit` | `30` | Line ~266 |
| `new_bugs[:N]` output cap | `20` | Lines ~346, ~353 |
| `gh pr list --limit` (dedup) | `200` | Line ~83 |
| `grep` TODOs fetched | `50` | Line ~229 |
| `pytest` failure lines | `100` | Line ~218 |
| Cache dedup max entries | `200` | Line ~262 |

## Cache Files

- `~/.hermes/cache/auto-fix-bugs/created_prs.json` — PRs the bot has already created
- `~/.hermes/cache/auto-fix-bugs/seen_bugs.json` — already-seen TODO/FIXME markers
- `/tmp/bug_candidates.json` — latest output for the agent to process

## Run Log (most recent)

### 2026-07-14 — Sequential fix approach, 5 PRs

**Model:** `deepseek-v4-flash` via `opencode-go`
**New candidates:** 18, Duplicates skipped: 12, Total: 30
**PRs created:** 5

| Issue | Fix | PR |
|-------|-----|----|
| #63761 | fix(qqbot): handle GROUP_MESSAGE_CREATE event | #64119 |
| #63681 | fix(acp): preserve custom provider namespace | #64125 |
| #63273 | fix(oidc): add User-Agent to PyJWKClient for WAF compat | #64126 |
| #63225 | fix(local): remove redundant temp-file read in _update_cwd | #64128 |
| #63141 | fix(serve): bridge terminal.backend config to process env | #64130 |

**Skipped:** 13 — 8 platform-specific (macOS, Windows, WSL2, Electron), 3 complex/setup-dependent, 1 model behavior, 1 frontend SPA

**Approach:** Sequential (one fix at a time, not subagent dispatch). Each fix: read issue → find code → apply patch → update tests → commit → push → PR → Discord webhook → next.

**Discord webhook format used:**
```
🔧 **New PR** — fix(scope): short description
👉 https://github.com/NousResearch/hermes-agent/pull/64119
```
One `curl` call per PR, posted immediately after `gh pr create` succeeds. Webhook responded HTTP 204 for all 5 posts.

**Notable: `gh pr create --head` flag required.** When pushing from a fork (not the upstream repo), `gh pr create` requires `--head <fork-user>:<branch>` to identify the source repo. Without it, GitHub returns: `"No commits between NousResearch/hermes-agent:main and NousResearch/hermes-agent:<branch>"`. Always use:
```bash
gh pr create --repo <owner>/<repo> --head <your-username>:<branch> --base main
```

**Sequential approach validated:** For 5 fixes in a single session, processing them sequentially (not via `delegate_task`) kept the workflow clean — no race conditions, no branch collisions, no uncommitted changes from subagents. Each fix followed the same cycle: `checkout main → checkout -b fix/xxx → git add → commit → push → gh pr create --head fork:branch → curl Discord`. Took ~5-8 minutes per fix on average.

### 2026-07-13 — created_prs.json cache was empty, 1 PR
- New candidates: 17, Duplicates skipped: 13, Total: 30
- PR created: #63790 for issue #62849 (Dockerfile Podman compat)
- `created_prs.json` cache was empty — PR tracking may have been reset
- Pre-existing fix branches found on fork for #63161, #62825

### 2026-07-11 — First run after prompt-schema fix, 3 PRs
- New candidates: 18, Duplicates skipped: 12, Total: 30
- PRs: #62439, #62440, #62441
- Validated `deepseek-v4-flash` can execute full fix pipeline

## Tuning History

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-14 | N/A (ran as-is) | 18 new candidates, 5 PRs created — parameters sufficient |
| 2026-07-13 | issues 20→30, candidates 15→20, dedup 100→200 | User requested more PR output |
