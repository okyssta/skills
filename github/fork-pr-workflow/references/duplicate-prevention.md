# Pre-PR Duplicate Detection

Before creating a PR for a bug fix, check whether one already exists for the issue. This is critical for automated (cron-driven) triage where multiple sessions may target the same issue.

## Checking for Existing PRs

```bash
# Check if any open PR references a specific issue number
# "#N" searches both title and body for the bare issue reference
gh pr list --repo owner/repo --state open --search "#ISSUE_NUMBER" --json number,title,headRefName,url

# Example output when a PR exists:
# [{"headRefName":"fix/my-branch","number":12345,"title":"fix: the actual fix (#42)"}]
# → SKIP — a PR already exists for this issue

# Also check for closed/merged PRs (already fixed)
gh pr list --repo owner/repo --state merged --search "#ISSUE_NUMBER" --json number --limit 1

# Check if the issue itself is already closed
gh issue view ISSUE_NUMBER --repo owner/repo --json closed,closedAt

# For repos with multiple reference styles, broaden the search:
gh pr list --repo owner/repo --state open --search "\"fix(#ISSUE_NUMBER)\" OR \"#ISSUE_NUMBER\" OR \"issue #ISSUE_NUMBER\"" --json number,title,url
```

**Pitfall — search syntax matters:** `--search "#N"` (with the `#` symbol) is unreliable from the shell because `#` starts a comment. In a shell script, quote it: `--search "#N"`. When using `execute_code` / Python, pass it as a normal string since there's no shell involved.

**Pitfall — `--search "ISSUE_NUMBER in:body"` is too narrow:** Some PRs only reference the issue in the title, not the body. Always search both title and body by omitting the `in:` qualifier or using a bare `#ISSUE_NUMBER` which covers both.
```

## When to Skip

Skip creating a PR when any of these are true:

- **Open PR found** — someone else (or a previous cron run) already submitted a fix
- **Issue already closed** — the fix was already merged or the issue was resolved another way
- **Duplicate issue** — the issue was marked as a duplicate of another with an existing PR
- **Fix is trivial / not an improvement** — cosmetic changes, incomplete bug reports, or changes that make the code worse don't warrant a PR

## Multi-PR Workflow

When fixing multiple issues in one session, create each fix on its own branch and return to main between branches:

```bash
# After first PR
git checkout main && git pull origin main

# Branch for next fix
git checkout -b fix/another-issue

# Fix, commit, push, create PR — repeat
```

This keeps each PR focused on a single issue and avoids cross-contamination between unrelated changes.

## Batch Investigation Pattern

When triaging multiple issues from a batch (e.g. cron job output):

1. Read batch file (`/tmp/bug_candidates.json`)
2. For each candidate, check for existing PRs using the command above
3. For "new" candidates (no PR found), investigate the codebase:
   - Search relevant files: `search_files(file_glob="*.py", pattern="KEYWORD", path=".")`
   - Check git history for recent related changes: `git log --all --oneline --grep="KEYWORD"`
4. If root cause is found, create a branch, fix, commit, push, and create PR
5. Skip issues where the root cause is unclear or the fix is speculative

### Batch-check with execute_code

For cleaner batch checking across many candidates, use `execute_code` (no shell quoting issues):

```python
from hermes_tools import terminal
import json

issues = [61392, 61297, 61172]
for issue in issues:
    r = terminal(f'gh pr list --repo owner/repo --state open --search "#{issue}" --json number,title,url')
    data = json.loads(r['output'])
    if data:
        print(f"Issue #{issue} → EXISTING PR: {data[0]['url']}")
    else:
        print(f"Issue #{issue} → No open PR found — fixable")
```

Benefits over shell loop:
- No `#` comment character issues (shell quoting)
- JSON parsing is native, not `jq` dependent
- Can conditionally branch per issue (skip / investigate / fix)
- Error handling is just Python try/except

## Fork-Based Multi-Fix Workflow

When you don't have direct push permission to the upstream repo, the multi-fix pattern changes slightly. After cloning the upstream repo:

1. Create a fork with `gh repo fork owner/repo --clone=false` (idempotent)
2. Add the fork as a remote: `git remote add fork https://github.com/YOU/repo.git`
3. Per fix: checkout main, create branch, fix, commit, push to fork, create PR with `--repo owner/repo --head YOU:branch`

### End-to-end example (execute_code):

```python
from hermes_tools import terminal
import json

# Set up once
terminal("gh repo fork owner/repo --clone=false 2>&1 || true")
terminal("git remote add fork https://github.com/YOU/repo.git 2>/dev/null || git remote set-url fork https://github.com/YOU/repo.git")
terminal("git fetch origin main && git checkout main && git merge origin/main")

issues = [61296, 61421]
for num in issues:
    # Check for existing PR
    r = terminal(f'gh pr list --repo owner/repo --state open --search "#{num}" --json number')
    if json.loads(r['output']):
        print(f"#{num} → SKIP (PR exists)")
        continue
    # Create branch, fix, commit, push, PR
    branch = f"fix/issue-{num}-description"
    terminal(f"git checkout -b {branch}")
    # ... make code changes with patch/write_file ...
    terminal("git add . && git commit -m 'fix: description'")
    terminal(f"git push fork HEAD")
    r = terminal(f'gh pr create --repo owner/repo --head YOU:{branch} --base main --title "fix: description (#{num})" --body "Closes #{num}"')
    print(f"#{num} → PR: {r['output'].strip()}")
    terminal("git checkout main")
```
