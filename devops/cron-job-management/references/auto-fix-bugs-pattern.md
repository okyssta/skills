# AUTO-FIX-BUGS Cron Job Pattern (2026-07-04, updated 2026-07-11)

## Overview
This document captures the working pattern for an autonomous bug-fixing cron job that:
1. Fetches bug candidates from a repository (failing tests, TODO/FIXME comments, GitHub issues)
2. Uses an AI coding agent to fix up to 10 highest-priority bugs
3. Creates PRs for each successful fix
4. Posts PR links + 1-line descriptions to Discord via webhook

## Key Design Decisions

### 1. Script is a Candidate Fetcher, Not a Fixer
The Python script (`auto-fix-bugs.py`) only **fetches and outputs candidates as JSON**. The actual fixing is done by the AI agent (north-mini-code-free) driven by the cron job's prompt. This separation allows:
- The agent to reason about each bug and implement appropriate fixes
- The script to remain simple and deterministic
- Easy debugging: run script manually to see what candidates it finds

### 2. Agent-Directory Structure
```
/tmp/hermes-agent          # Script's ephemeral clone for scanning (issues, grep, pytest — recreated each run)
/root/hermes-agent         # Agent's persistent working clone with configured git remotes (fork + origin + upstream)
/tmp/bug_candidates.json   # JSON file with top 10 candidates for agent reference (written by script)
```

The script writes candidates to `/tmp/bug_candidates.json`. The agent implements fixes in the persistent `/root/hermes-agent` checkout which has fork remotes, git history, and `gh` CLI already configured.

### 3. Cron Job Configuration

**As of 2026-07-11:**
```yaml
name: AUTO-FIX-BUGS
schedule: "every 90m"
model: deepseek-v4-flash
provider: opencode-go
script: auto-fix-bugs.py
no_agent: false
deliver: origin
prompt: "You are AUTO-FIX-BUGS, an automated bug-fixing bot...
  [Full prompt with Discord webhook URL inline]"
```

**Key notes:**
- The model has changed from `north-mini-code-free`/`opencode-zen` to `deepseek-v4-flash`/`opencode-go` over time due to provider changes
- `deepseek-v4-flash` CAN create working PRs — validated with 3 real PRs on 2026-07-11 (#62439, #62440, #62441)
- The Discord webhook URL is embedded **directly in the prompt text** — not in an env var or config file
- The prompt must describe the **actual** JSON structure (fields: `number`, `title`, `body`, `url`, `type`, `priority`, `dedup_status`) — NOT the template's old `confidence_score`/`file_path`/`description` schema

### 4. Model Selection
- **north-mini-code-free** via **opencode-zen** (free, code-specialized, 256K context, reasoning=true, tools=true)
- Avoids OpenRouter/Nous provider drift issues (HTTP 401 errors)
- Pinned at job creation so global provider changes don't break it

### 5. Systematic Duplicate PR Prevention (Multi-Layer Dedup)

The `auto-fix-bugs.py` script implements a **four-layer dedup system** that prevents creating PRs for issues that already have fixes, whether from this cronjob, other contributors, or the upstream repo. This runs entirely in the data-fetching script — the agent never sees duplicates.

#### Layer 1: Open PR Cross-Reference

Before processing any candidates, the script fetches ALL open PRs (up to 100) and parses their titles and bodies for issue references:

```python
# Regex patterns for issue references
r'(?:Fixes|Closes|Resolves|Fix|Close|Resolve|#(\d+))\s+#(\d+)'  # "Fixes #123"
r'#(\d{3,})'  # Bare "#1234" in PR body
```

This catches both explicit linking keywords and bare issue-number mentions. Result: a dict mapping issue numbers to their existing PR info (number, title, URL).

**Known limitation — the regex can miss PRs that reference the issue only in the PR title (e.g. `fix(scope): description (#61212)`).** The script fetches PR bodies, but `gh pr list --json title,body` only surfaces the body text for the regex; titles are returned but may use a format the regex doesn't match (e.g. parenthetical `(#N)` at the end of a conventional-commit title, or issue numbers in branch names that are not in the title/body at all). In one run (2026-07-09), the script caught 10 out of 18 matching issue→PR relationships, missing 8 due to this title-vs-body gap. **The agent-level double-check in the prompt always catches these**, so this is a documentation gap in the script, not a reliability bug — the belt-and-suspenders design works as intended.

#### Layer 2: Issue State Check

Uses `gh issue view <N> --json state` to check if the issue is already **CLOSED** — if closed, someone already fixed it and the fix was merged.

#### Layer 3: Own-History Cache (`created_prs.json`)

Stored at `~/.hermes/cache/auto-fix-bugs/created_prs.json`, this tracks every PR this cronjob has ever created — issue number, PR number, PR title, PR URL, timestamp. Even after the PR is merged (and no longer appears in open PR search), this cache prevents re-creating it.

#### Layer 4: TODO/FIXME Dedup Cache (`seen_bugs.json`)

TODO/FIXME/BUG/XXX comments found via grep are hashed by `file:line:content` and cached. Once seen, they're never re-suggested. The cache keeps the last 200 entries to avoid unbounded growth.

#### How It Works: Output Tagging

Each candidate gets a `dedup_status` field:

```json
{
  "type": "github_issue",
  "number": 60841,
  "title": "CVEs survive pip-audit fix across reboots...",
  "dedup_status": "duplicate",
  "dedup_reason": "Already has open PR #60889",
  "existing_pr": {
    "number": 60889,
    "title": "fix: bump cryptography, starlette...",
    "url": "https://github.com/NousResearch/hermes-agent/pull/60889"
  }
}
```

Only candidates with `"dedup_status": "new"` are presented to the agent. The script also prints a clear `=== SKIPPED DUPLICATES ===` section so operators can see what was filtered.

#### Agent Prompt as Safety Net

The cronjob prompt reinforces: *"The script already checks for existing PRs. ONLY fix candidates with dedup_status: new. Before creating any PR, double-check with gh pr list."*

On output suppression: the prompt now explicitly says:
> *"Do NOT say [SILENT] if there are new candidates — always report what was done, skipped, or failed. Only say [SILENT] if the script produced NO new candidates at all."*

This override is critical — without it, the default cron wrapper's `[SILENT]` instruction can cause the agent to suppress delivery even when there ARE real candidates to act on.

This belt-and-suspenders approach ensures:
- Even if the API returns a stale issue that just got a PR 5 minutes ago, the script catches it
- Even if the script misses a reference, the agent double-checks
- When nothing is new, the cronjob makes no noise

### 6. Bug Candidate Sources (Priority Order)
1. **Failing tests** (high) - pytest output
2. **GitHub issues labeled "bug"** (high) - via `gh issue list`, filtered by `dedup_status: "new"`
3. **TODO/FIXME/BUG/XXX comments** (medium) - grep across *.py files, deduplicated by cache

### 7. Agent Workflow (Driven by Prompt)

**Phase 0 — Pre-flight: check for existing work.** The script already handles dedup, but the agent should still verify before starting work on any candidate:

```bash
# 1. Check issue state and labels
gh issue view <N> --json state,labels,title

# 2. Skip if already closed or if labels show it's not actionable
#    (e.g. 'needs-repro', 'wontfix', 'duplicate')

# 3. Double-check for existing PRs (belt-and-suspenders)
gh pr list --state open --search "<issue_number>" --json number,title,headRefName

# 4. Check if already fixed on main (merged)
git log --oneline upstream/main --grep="#<issue_number>" | head -5
```

**Skip** candidates that:
- Already have open PRs (even if dedup missed it)
- Are P3/P4 priority when harder P2 candidates are available (focus on highest-impact fixes)
- Have labels indicating they're blocked ('needs-repro', 'blocked', 'discussion')
- Require complex infrastructure changes you can't safely make in isolation

For each remaining candidate:
1. Create fix branch: `git checkout main && git checkout -b fix/<scope>-<description>`
2. Read affected files to understand the code, implement a minimal fix
3. Commit, push to fork, create PR via `gh pr create`
4. Post to Discord webhook with PR URL + 1-line summary
5. Return to main: `git checkout main`
6. Move to next candidate

### 7. Multi-PR Workflow (Stash → Branch → Apply → PR → Repeat)

When making multiple independent fixes in the same session and you want to apply ALL changes first then split into separate PRs:

1. Make ALL edits in the working tree (via patch/write_file tools) on a single branch
2. `git stash` — stash everything together
3. For each fix, create a fresh branch from main and apply only that fix's changes:
   ```bash
   git checkout main && git checkout -b fix/<scope>-<description>
   # Use the agent's `patch` tool to re-apply targeted edits on this branch
   # Only the files relevant to this fix should be modified
   git add <files> && git commit -m "fix(scope): description (Fixes #N)"
   git push fork HEAD && gh pr create ...
   git checkout main
   ```
4. `git stash drop` once all PRs are created
5. **Alternative (preferred for Hermes):** Instead of stashing, apply each fix individually on a fresh branch from main. Since Hermes patches are small and well-scoped, reapplying each fix via the `patch` tool on a clean branch is simpler and avoids stash management complexity.

### 8. Parallel Fix Pattern via delegate_task

When fixing up to 10 distinct bugs in one run, **dispatch subagents in parallel** using `delegate_task`:

1. **Research first** — Read the affected source files to understand each issue before dispatching. Gather all the context the subagent will need.
2. **Dispatch parallel subagents** — Group fixable issues into batches of up to max_concurrent_children (default 3). Each subagent gets full context: repo path, issue details, GH auth, Discord webhook URL.
3. **Each subagent owns its lifecycle** — Each independently: checks out main, creates branch, patches, commits, pushes, opens PR, posts webhook.
4. **Avoid branch collisions** — Each subagent uses a unique branch name per issue (e.g. `fix/<issue-num>-<short-description>`).
5. **VERIFY subagent results** — Subagents are self-reporting. After dispatch, ALWAYS verify:
   ```bash
   git branch -a | grep fix/<issue-num>          # branch exists?
   git log --oneline main..fix/<issue-num>        # has commits?
   git diff main..fix/<issue-num>                 # actual diff?
   git branch -r | grep fix/<issue-num>           # pushed to fork?
   gh pr list --repo <repo> --head fix/<issue-num> --state open --json number,url   # PR created?
   ```
6. **Subagent with no visible commits = fix failed** — Subagents can leave changes UNCOMMITTED. If the branch exists but `git log` shows no new commits, commit and push the changes yourself, then create the PR.
7. **Subagent that committed+pushed but didn't PR = partially complete** — Create the `gh pr create` call yourself.
8. **Handle max_concurrent_children limit** — If you have 4+ issues, send the first 3, wait for them to report back, then send the next batch.

### 9. Discord Webhook Format

For single-PR delivery, use the simple `content` format:
```json
{
  "content": "🤖 **Auto-fix PR Created**\n{pr_url}\n\n{one_line_summary}"
}
```

For multi-PR delivery (3+ PRs), use Discord **embeds** for clean structured output:
```json
{
  "embeds": [
    {
      "title": "Auto-Fix-Bugs: PRs Created",
      "color": 3066993,
      "fields": [
        {
          "name": "PR #N: fix(scope): short description",
          "value": "One-line problem description. Fixes #NNN",
          "inline": false
        }
      ],
      "footer": {"text": "Hermes auto-fix-bugs cron job • YYYY-MM-DD HH:MM UTC"}
    }
  ]
}
```

**Important:** Use a static JSON blob for the curl payload — inline shell variable expansion (`$()` inside JSON) produces invalid JSON. Write the JSON to a Python-generated file or use Python's `urllib.request` library instead.

**Webhook lifecycle (common failure modes):**
- **403 Forbidden** — the webhook URL was deleted or the token was revoked. This is common when the Discord server owner rotates the webhook. Log `webhook_status: "403"` in the tracker and continue; the PR work is still valid and the tracker preserves the record. The cron prompt should **not** treat Discord delivery failure as a task failure — the PR creation is the primary deliverable.
- **404 Not Found** — the webhook was deleted. Same handling as 403.
- **429 Too Many Requests** — rate limited. Retry with exponential backoff (1s, 2s, 4s). If still failing after 3 retries, log and continue.

Use Python's `urllib.request` to post (avoids shell quoting issues):

```python
import json, urllib.request

def post_discord_webhook(webhook_url: str, payload: dict) -> int:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code  # 403, 404, 429, etc.
    except Exception as e:
        return 0  # network error, timeout
```

After posting, log the status to the tracker and continue regardless of outcome.

### 10. Verification After PR Creation

`execution_success` is not enough — the agent can return without having actually created anything. Verify each step:
- [ ] `gh pr list --author @me --state open` shows the expected PRs
- [ ] Each PR's title/Fixes line references the issue number
- [ ] Each branch was pushed (`git branch -r | grep fix/`)
- [ ] Each branch has commits ahead of main (`git rev-list --count main..branch`)
- [ ] Discord webhook returned 204 or non-2xx logged to tracker (403/404 = webhook expired, not a task failure)
- [ ] Working directory is clean (`git status --short` shows nothing staged/modified)

## Prioritization Heuristics

When choosing among 10+ candidates:

1. **Prefer issues with a clear root cause and proposed fix** — the body text often describes exactly what line to change
2. **Prefer issues affecting core components** (agent loop, memory, tools) over platform-specific ones (WhatsApp, Discord, macOS TUI) which may be harder to test
3. **Skip issues that depend on upstream library releases** (aiohttp, pydantic, etc.) — those are waiting on external fixes
4. **Skip issues that require platform-specific hardware** (macOS Retina displays, Windows-only bugs)
5. **Prefer issues with a reproduce-able test path** — you can verify your fix by running the existing tests
6. **Check the branch's commit count before creating a PR** — `git rev-list --count main..HEAD` must be > 0. If zero, commit the changes first.
7. **When `gh pr create` returns "Head sha can't be blank, Base sha can't be blank, No commits"** — the branch has no commits. Commit staged changes with `git commit` and try again.

## Pitfalls & Lessons Learned

| Issue | Solution |
|-------|----------|
| Template had `implement_fix()` returning string only | Refactored to candidate-fetcher pattern; agent does the fixing |
| Syntax error in Discord post (double `encode()`) | Fixed in script |
| `datetime.utcnow()` deprecated | Use `datetime.now(timezone.utc)` |
| Agent tried to PR with no commits | Prompt must ensure fix is implemented before PR creation |
| Global provider drift broke jobs | Pin model+provider at job creation |
| Script used absolute paths | Use relative script name only (`auto-fix-bugs.py`) |
| **Subagent left changes uncommitted** | Always verify `git status --short` + `git log --oneline main..HEAD` before `gh pr create`. If subagent returned with no commits but changes are staged, commit and push yourself. |
| **`gh pr create` fails "Head sha can't be blank"** | Branch has no commits. Commit staged modifications first, or if the branch is empty, the subagent didn't actually apply any changes. |
| **Branch exists but no PR created** | Subagent committed+pushed but didn't complete the PR creation. Create the PR manually with `gh pr create`. |
| **Already-merged issues appear in candidates** | `gh issue list --label bug` returns issues ordered by last update, not by open/merged state. Check `git log --oneline --all --grep="#N"` for merged commits before working on a candidate. |
| **Existing PRs already cover an issue** | `gh pr list --state open --search "issue_number"` — always check before starting work. |
| **Schema sanitizer strips `required: []` causing HTTP 400** | When fixing schema validation errors on strict backends: (a) add `isinstance(required, list)` guard before iterating; (b) preserve empty `required: []` — only pop non-empty lists with invalid entries; (c) add `additionalProperties: false` to object schemas where missing. |
| **Push to fork, not origin** | The user has write access to their fork but not the upstream repo. Use: `git push -u fork <branch>` — not `origin`. |
| **Subagent modifies files across sibling branches** | When using `delegate_task`, subagents share the same working directory. One subagent's file writes can collide with another's or with the parent's stashed changes. After subagents complete, check `git diff` to see if changes from multiple issues are interleaved. |
| **Candidate from proprietary plugin** | Issues referencing paths like `agent-comms-core/`, `raft/`, or `bridge.lock` are often from proprietary plugins not in the open-source repo. Check if the referenced code exists before attempting a fix. |
| **Discord webhook returns 403 Forbidden** | The webhook URL was deleted or the token was revoked (common when Discord server owners rotate webhooks). **Do not treat this as a task failure.** Log `webhook_status: "403"` in the tracker, and continue — the PR creation is the primary deliverable. The cron prompt should not abort on webhook failure. |
| **Discord webhook returns 404 Not Found** | Same root cause as 403 — the webhook no longer exists. Log and continue. |
| **Discord webhook 429 Too Many Requests** | Rate limited. Retry with exponential backoff (1s, 2s, 4s). If still failing, log and continue. |
| **Prompt describes wrong data schema** | If the prompt says `confidence_score`, `file_path`, `description` but the script outputs `number`, `title`, `body`, `url`, the agent outputs `[SILENT]` because it can't find expected fields. Always verify the script's actual format matches what the prompt describes. See §11 below. |
| **Discord webhook URL only in env var / script** | The agent can only access URLs that are **in the prompt text**. If the webhook URL was in the original creation prompt but got overwritten during an update, the agent has no way to post results. Include the full webhook URL directly in the prompt. |
| **`[SILENT]` suppression not configured** | The default cron wrapper tells the agent to say `[SILENT]` if nothing new to report. If the agent says `[SILENT]` even when there ARE candidates, add: _"Do NOT say [SILENT] if there are new candidates — always report results."_ |

## Monitoring & Alerting

The auto-fix-bugs cron job has a **silent failure mode** where Discord delivery fails but the job otherwise completes. Without the Discord notification being received, no one knows PRs were created. Mitigations:

1. **Tracker file** (`/root/.hermes/auto-fix-tracker.json`) — the canonical record of what was created. Always append an entry after each run, even when Discord delivery fails.
2. **GitHub dashboard** — the agent's open PR list (`gh pr list --author @me --state open`) is the live truth. A quick glance shows whether new PRs exist.
3. **Run output** — the cron job's `deliver: origin` output file in `~/.hermes/cron/output/<job_id>/` contains the full report. Check this when Discord notifications stop arriving.

## Verification Checklist
After creating/updating the cron job:
- [ ] `cronjob list` shows AUTO-FIX-BUGS enabled, scheduled
- [ ] Manual test: `python3 /root/.hermes/scripts/auto-fix-bugs.py` outputs valid JSON candidates
- [ ] `hermes cron run AUTO-FIX-BUGS` executes without error
- [ ] Output appears in `~/.hermes/cron/output/edc94cfb2fc6/`
- [ ] Discord webhook receives test message (if triggered)
- [ ] GitHub PRs created for fixed issues

## Related Files
- `templates/auto-fix-bugs.py` — Candidate fetcher script
- `scripts/auto-fix-bugs.py` — Deployed copy at `~/.hermes/scripts/`
- `references/cron-recreation-patterns.md` — General cron recreation patterns

## 2026-07-11 Incident: Prompt-Script Schema Mismatch

### What Happened
The AUTO-FIX-BUGS cron job had been running every 90 minutes for **7 days** with `last_status: ok` but **producing zero PRs**. No deliveries to Discord, no output to the user. The agent was outputting `[SILENT]` on every run.

### Root Cause
The stored prompt (in `~/.hermes/cron/jobs.json`) was overwritten at some point with a broken template that described data fields that **don't exist** in the script output:

| Prompt expects | Script actually outputs |
|---|---|
| `confidence_score` (0–10) | `number`, `title`, `body`, `url` |
| `file_path` | No such field |
| `description` | No such field |
| — | `priority`, `type`, `source`, `dedup_status` |

The prompt told the agent: *"Read /tmp/bug_candidates.json. It contains candidates with `confidence_score`, `file_path`, and `description`."* But the actual JSON had `number`, `title`, `body`, `url`, `type`, `priority`, `dedup_status`. The agent couldn't find the expected fields, got confused, and responded `[SILENT]`.

Additionally, the **Discord webhook URL** was present in the original prompt but missing from the overwritten one — so even if the agent DID create PRs, it had no webhook to post to.

### Lessons
1. **Hybrid cron jobs have a data contract** between the script's stdout and the prompt's field descriptions. If they disagree, the agent fails silently. Always verify by comparing the script's actual output with the prompt's schema.
2. **The Discord webhook URL must be in the prompt text** — the agent cannot access env vars or config files.
3. **Explicitly override `[SILENT]`** in the prompt when there are candidates to act on. The default cron wrapper tells the agent to say `[SILENT]` if nothing new — but if the data format is wrong, the agent may say `[SILENT]` even when there ARE candidates.
4. **`deepseek-v4-flash` (via `opencode-go`) CAN create working PRs** — the first run with the fixed prompt created 3 real PRs (#62439, #62440, #62441) that are all OPEN in the hermes-agent repo. This validates that even a free-tier model can execute the full clone→fix→commit→push→PR→webhook pipeline when given clear instructions.

### Fix Applied
1. Rewrote the stored prompt to describe the **actual**  JSON structure (fields: `number`, `title`, `body`, `url`, `type`, `priority`, `dedup_status`)
2. Included the Discord webhook URL **directly in the prompt text**
3. Added explicit instructions to create PRs (branch, commit, push, `gh pr create`)
4. Added `"Do NOT say [SILENT] if there are new candidates — always report results"`
