#!/usr/bin/env python3
"""
AUTO-FIX-BUGS Candidate Fetcher
This script fetches bug candidates from a GitHub repository.
Filters out issues that already have open/merged PRs to avoid duplicates.
The AI agent uses this data to select and fix bugs.

Configuration: Set REPO below (default NousResearch/hermes-agent).
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.hermes/.env')

# Configuration — change these for your target repo
REPO = os.environ.get("AUTO_FIX_REPO", "NousResearch/hermes-agent")
BASE_BRANCH = "main"
CACHE_DIR = os.path.expanduser("~/.hermes/cache/auto-fix-bugs")
CACHE_FILE = f"{CACHE_DIR}/created_prs.json"
DEDUP_CACHE_FILE = f"{CACHE_DIR}/seen_bugs.json"
CANDIDATES_FILE = "/tmp/bug_candidates.json"


def ensure_cache_dir():
    """Ensure cache directory exists."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def run_cmd(cmd, cwd=None, capture=True, timeout=300):
    """Run shell command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=capture, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1


def load_created_prs():
    """Load history of PRs this cronjob has already created."""
    ensure_cache_dir()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {"prs": [], "issues_fixed": []}
    return {"prs": [], "issues_fixed": []}


def save_created_pr(issue_number, pr_number, pr_title, pr_url):
    """Save a newly created PR to the history cache."""
    ensure_cache_dir()
    history = load_created_prs()
    history["prs"].append({
        "issue_number": issue_number,
        "pr_number": pr_number,
        "pr_title": pr_title,
        "pr_url": pr_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    if str(issue_number) not in history["issues_fixed"]:
        history["issues_fixed"].append(str(issue_number))
    with open(CACHE_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"  [CACHE] Saved PR #{pr_number} for issue #{issue_number}")
    return history


def get_open_prs_by_issue():
    """
    Fetch all open PRs and map them by which issue number they reference.
    Returns (set_of_issue_numbers, dict_of_issue_number_to_pr_info).
    """
    print("  [DEDUP] Fetching open PRs to check for duplicates...")
    refs_by_issue = {}

    stdout, _, code = run_cmd(
        f"gh pr list --repo {REPO} --state open --json number,title,body,headRefName,url --limit 100",
        timeout=60
    )
    if code != 0 or not stdout:
        print("  [DEDUP] Warning: Could not fetch PR list")
        return set(), refs_by_issue

    try:
        prs = json.loads(stdout)
    except json.JSONDecodeError:
        print("  [DEDUP] Warning: Could not parse PR list JSON")
        return set(), refs_by_issue

    # Patterns for issue references in PR titles/bodies
    issue_ref_pattern = re.compile(
        r'(?:Fixes|Closes|Resolves|Fix|Close|Resolve|#(\d+))\s+#(\d+)', re.IGNORECASE
    )
    simple_hash_ref = re.compile(r'#(\d{3,})')

    for pr in prs:
        pr_title = pr.get("title", "")
        pr_body = pr.get("body", "") or ""
        pr_number = pr.get("number")
        pr_url = pr.get("url", "")
        combined_text = pr_title + " " + pr_body

        # Find explicit issue references (Fixes #123, Closes #456)
        for match in issue_ref_pattern.finditer(combined_text):
            issue_num = int(match.group(2))
            if issue_num not in refs_by_issue:
                refs_by_issue[issue_num] = {
                    "pr_number": pr_number,
                    "pr_title": pr_title[:80],
                    "pr_url": pr_url
                }

        # Also catch bare "#1234" references in body
        for match in simple_hash_ref.finditer(combined_text):
            num = int(match.group(1))
            if num != pr_number and num not in refs_by_issue:
                refs_by_issue[num] = {
                    "pr_number": pr_number,
                    "pr_title": pr_title[:80],
                    "pr_url": pr_url
                }

    issues_with_prs = set(refs_by_issue.keys())
    print(f"  [DEDUP] Found {len(issues_with_prs)} issues with existing open PRs")
    for issue_num in sorted(issues_with_prs):
        info = refs_by_issue[issue_num]
        print(f"    Issue #{issue_num} -> PR #{info['pr_number']}: {info['pr_title']}")

    return issues_with_prs, refs_by_issue


def check_issue_closed_or_has_pr(issue_number, open_pr_issues, open_pr_info):
    """
    Full dedup check for an issue:
    1. Has an open PR referencing it
    2. Issue is closed/merged
    3. We've already fixed it in a previous run

    Returns (is_duplicate: bool, reason: str, pr_info: dict | None)
    """
    # Layer 1: Open PR cross-reference
    if issue_number in open_pr_issues:
        pr_info = open_pr_info[issue_number]
        return True, f"Already has open PR #{pr_info['pr_number']}", pr_info

    # Layer 2: Our own history cache
    history = load_created_prs()
    if str(issue_number) in history.get("issues_fixed", []):
        for pr in history.get("prs", []):
            if str(pr.get("issue_number")) == str(issue_number):
                return True, f"Already fixed in PR #{pr['pr_number']} (our own)", pr

    # Layer 3: Check if issue is already closed (someone merged a fix)
    stdout, _, code = run_cmd(
        f"gh issue view {issue_number} --repo {REPO} --json state --jq '.state' 2>/dev/null",
        timeout=15
    )
    if code == 0 and stdout.strip() == "CLOSED":
        return True, "Issue is already closed", None

    return False, None, None


def find_bugs_to_fix():
    """Scan repository for bugs and fix candidates, with full dedup."""
    bugs = []
    checkout = "/tmp/hermes-agent"

    # Ensure repo exists and is up to date
    if not os.path.exists(checkout):
        run_cmd(f"git clone https://github.com/{REPO}.git {checkout}")
    run_cmd(f"cd {checkout} && git checkout {BASE_BRANCH} && git pull origin {BASE_BRANCH}")

    # Pre-fetch all open PRs for bulk dedup
    open_pr_issues, open_pr_info = get_open_prs_by_issue()

    # --- 1. Check for failing tests ---
    stdout, _, code = run_cmd(
        f"cd {checkout} && python -m pytest -x -v --tb=short 2>&1 | head -100"
    )
    if code != 0 and "FAILED" in stdout:
        bugs.append({
            "type": "failing_test",
            "details": stdout[:3000],
            "priority": "high",
            "source": "pytest",
            "dedup_status": "new"
        })

    # --- 2. Search for TODO/FIXME/BUG/XXX comments ---
    stdout, _, _ = run_cmd(
        f"cd {checkout} && grep -n -r -i -E 'TODO|FIXME|BUG|XXX' --include='*.py' | head -50"
    )

    # Load seen cache
    seen_bugs = set()
    if os.path.exists(DEDUP_CACHE_FILE):
        try:
            with open(DEDUP_CACHE_FILE, "r") as f:
                data = json.load(f)
                seen_bugs = set(data.get("seen_todos", []))
        except (json.JSONDecodeError, Exception):
            pass

    new_seen = set(seen_bugs)
    for line in stdout.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line in seen_bugs:
            continue  # Already seen in a previous run
        new_seen.add(line)
        bugs.append({
            "type": "code_comment",
            "details": line,
            "priority": "medium",
            "source": "grep",
            "dedup_status": "new"
        })

    # Persist updated seen cache (keep last 200)
    ensure_cache_dir()
    with open(DEDUP_CACHE_FILE, "w") as f:
        json.dump({"seen_todos": list(new_seen)[-200:]}, f, indent=2)

    # --- 3. Check GitHub issues labeled "bug" ---
    stdout, _, _ = run_cmd(
        f"gh issue list --repo {REPO} --label bug --state open --json number,title,url,body --limit 20",
        timeout=30
    )
    try:
        issues = json.loads(stdout)
        for issue in issues:
            issue_num = issue["number"]
            is_dup, reason, pr_info = check_issue_closed_or_has_pr(
                issue_num, open_pr_issues, open_pr_info
            )

            entry = {
                "type": "github_issue",
                "number": issue_num,
                "title": issue["title"],
                "url": issue["url"],
                "body": issue.get("body", "")[:2000],
                "priority": "high",
                "source": "github",
            }

            if is_dup:
                entry["dedup_status"] = "duplicate"
                entry["dedup_reason"] = reason
                if pr_info:
                    entry["existing_pr"] = {
                        "number": pr_info["pr_number"],
                        "title": pr_info["pr_title"],
                        "url": pr_info["pr_url"]
                    }
            else:
                entry["dedup_status"] = "new"

            bugs.append(entry)
    except json.JSONDecodeError:
        pass
    except Exception:
        pass

    return bugs


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching bug candidates...")

    bugs = find_bugs_to_fix()
    if not bugs:
        print("No bugs found to fix.")
        # Write empty result so agent knows there's nothing
        with open(CANDIDATES_FILE, "w") as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "new_candidates": [],
                "total_new": 0,
                "total_duplicates": 0,
                "total_all": 0,
                "duplicates_skipped": []
            }, f, indent=2)
        return 0

    # Sort: new items first, then by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    def sort_key(b):
        base = priority_order.get(b.get("priority", "low"), 2)
        dup = 0 if b.get("dedup_status") == "new" else 1
        return (dup, base)

    bugs.sort(key=sort_key)

    new_bugs = [b for b in bugs if b.get("dedup_status") != "duplicate"]
    dup_bugs = [b for b in bugs if b.get("dedup_status") == "duplicate"]

    # Report duplicates
    if dup_bugs:
        print(f"\n=== SKIPPED DUPLICATES ({len(dup_bugs)} issues already have PRs) ===")
        for bug in dup_bugs[:15]:
            reason = bug.get("dedup_reason", "Unknown")
            existing = bug.get("existing_pr", {})
            if existing:
                print(f"  #{bug['number']} - {bug['title'][:70]}")
                print(f"    -> {reason} - {existing.get('url', '')}")
            else:
                print(f"  #{bug['number']} - {bug['title'][:70]}")
                print(f"    -> {reason}")

    # Output new candidates
    print(f"\n=== BUG CANDIDATES (up to 10) ===")
    for i, bug in enumerate(new_bugs[:10]):
        print(f"\n--- Candidate {i+1} ---")
        print(json.dumps(bug, indent=2))

    # Save structured output for agent
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "new_candidates": new_bugs[:10],
        "total_new": len(new_bugs),
        "total_duplicates": len(dup_bugs),
        "total_all": len(bugs),
        "duplicates_skipped": [{
            "number": b.get("number"),
            "title": b.get("title", "")[:80],
            "reason": b.get("dedup_reason", ""),
            "existing_pr": b.get("existing_pr")
        } for b in dup_bugs[:20]]
    }
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nTotal: {len(new_bugs)} new, {len(dup_bugs)} duplicates skipped "
          f"(top {len(new_bugs[:10])} saved to {CANDIDATES_FILE})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
