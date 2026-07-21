# Job Recreation Checklist

Step-by-step procedure for recreating cron jobs from a summary document.

## Phase 1: Parse & Inventory

- [ ] Obtain cron summary document (cron-summary.txt)
- [ ] List all jobs with: name, ID, schedule, type, script/prompt, delivery
- [ ] Identify missing scripts vs embedded prompts
- [ ] Note all required credentials/environment variables
- [ ] Check for duplicate job IDs in summary

## Phase 2: Infrastructure Setup

- [ ] Create required directories:
  - [ ] `/opt/firecrawl/` (or other script directories)
  - [ ] `~/.hermes/scripts/`
  - [ ] Output directories under `~/.hermes/cron/output/`
- [ ] Install dependencies:
  - [ ] `pip install firecrawl-py croniter python-dotenv requests`
  - [ ] `gh auth login` (if GitHub operations needed)
  - [ ] Any other language-specific packages
- [ ] Verify existing infrastructure (WordPress site, Discord webhooks, etc.)

## Phase 3: Credentials Configuration

- [ ] Create/update `/root/.hermes/.env` with all required variables:
  - [ ] Discord webhook URLs
  - [ ] API keys (Firecrawl, OpenAI, OpenRouter, etc.)
  - [ ] Application passwords (WordPress, etc.)
  - [ ] HMAC secrets
- [ ] Verify each credential works:
  - [ ] Test Discord webhook: `curl -X POST <webhook> -d '{"content":"test"}'`
  - [ ] Test API keys with minimal request
  - [ ] Test `gh auth status`

## Phase 4: Script Creation

For each script-based job:
- [ ] Write script file to correct location (`/opt/...` or `~/.hermes/scripts/`)
- [ ] Add shebang (`#!/usr/bin/env python3` or `#!/usr/bin/env bash`)
- [ ] Add `load_dotenv('/root/.hermes/.env')` at top of Python scripts
- [ ] Implement exact functionality from "What it does" description
- [ ] Match output format of original (if known)
- [ ] Add proper error handling and exit codes
- [ ] Make executable: `chmod +x script.py`
- [ ] Test manually: `python3 /path/to/script.py`

## Phase 5: Cron Job Creation

For each job in summary:

### Agent-based jobs (AUTO-FIX-BUGS type):
```bash
cronjob create --name "JOB-NAME" \
  --schedule "every 90 minutes" \
  --prompt "Full prompt from summary..." \
  --deliver origin \
  --toolsets '["terminal", "file", "search"]' \
  --provider opencode-go \
  --model mimo-v2.5
```

### Script-based jobs (DAILY-FONEWORLD-BLOG, CRM-HEALTH-REPORT):
```bash
cronjob create --name "JOB-NAME" \
  --schedule "0 4 * * *" \
  --prompt "python3 /opt/firecrawl/script.py" \
  --deliver origin
```

### Script-only / watchdog jobs (P1-WEBHOOK):
```bash
cronjob create --name "JOB-NAME" \
  --schedule "every 120 minutes" \
  --script "script-name.py" \
  --no-agent true \
  --deliver local
```

### For each created job:
- [ ] Verify appears in `cronjob list`
- [ ] Check next run time is correct
- [ ] Verify delivery target matches summary

## Phase 6: Testing & Verification

- [ ] Run each job manually: `cronjob run <job_id>`
- [ ] Check output in `~/.hermes/cron/output/<job_id>/`
- [ ] Verify Discord delivery for origin-targeted jobs
- [ ] Check for errors in script output
- [ ] Verify state files created (blog state, PR tracker state, etc.)

## Phase 7: Post-Recreation Validation

- [ ] `cronjob list` shows all expected jobs
- [ ] `hermes cron status` shows scheduler healthy
- [ ] Next run times match original schedule
- [ ] No duplicate jobs
- [ ] All credentials loaded correctly
- [ ] Scripts handle missing credentials gracefully

## Phase 8: Documentation

- [ ] Update cron-summary.txt with new job IDs
- [ ] Document any deviations from original
- [ ] Note any credentials that need rotation
- [ ] Archive old summary if replaced

## Quick Reference Commands

```bash
# List all jobs
cronjob list

# Run job manually
cronjob run <job_id>

# Remove duplicate
cronjob remove <job_id>

# Check scheduler status
hermes cron status

# View job output
ls ~/.hermes/cron/output/<job_id>/
cat ~/.hermes/cron/output/<job_id>/latest.md

# Test script manually
python3 /opt/firecrawl/script.py
python3 ~/.hermes/scripts/script.py

# Check credentials
cat /root/.hermes/.env | grep -E "API_KEY|WEBHOOK|PASSWORD"
```

## Common Pitfalls to Avoid

| Pitfall | Prevention |
|---------|------------|
| Duplicate jobs | Always `cronjob list` before creating |
| Wrong script path | Use relative filename only for `--script` |
| Missing `.env` loading | Add `load_dotenv('/root/.hermes/.env')` to all scripts |
| Discord webhook 403 | Verify webhook URL and permissions |
| Firecrawl 401 | Use valid API key, correct endpoint |
| Unicode in prompts | Ensure ASCII-safe, no ellipsis `…` |
| Bash array issues | Use Python for JSON state handling |
| State file permissions | Scripts create own directories |
| Duplicate blog topics | Implement anti-repeat state file |