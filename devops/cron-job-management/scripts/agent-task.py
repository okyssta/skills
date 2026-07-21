#!/usr/bin/env python3
"""
Agent Task Template - Agent-based cron job with gh CLI operations
For tasks like PR monitoring, auto-fixing, repo maintenance.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


# ============ CONFIGURATION ============
GITHUB_REPO = os.getenv("AGENT_TASK_GITHUB_REPO", "NousResearch/hermes-agent")
GITHUB_AUTHOR = os.getenv("AGENT_TASK_GITHUB_AUTHOR", "kyssta-exe")
DISCORD_WEBHOOK = os.getenv("AGENT_TASK_DISCORD_WEBHOOK")
OUTPUT_DIR = Path(os.getenv("AGENT_TASK_OUTPUT_DIR", "/root/.hermes/cron/output/agent-task"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ========================================


def run_gh(args: list) -> tuple[str, str, int]:
    """Run gh CLI command."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1


def post_to_discord(content: str) -> bool:
    """Post to Discord webhook."""
    if not DISCORD_WEB_WEBHOOK:
        return False
    
    try:
        import urllib.request
        data = json.dumps({"content": content}).encode("utf-8")
        req = urllib.request.Request(
            DISCORD_WEBHOOK,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 204
    except Exception as e:
        print(f"Discord post failed: {e}", file=sys.stderr)
        return False


def get_prs(limit: int = 50) -> list:
    """Get PRs for the configured author/repo."""
    stdout, stderr, code = run_gh([
        "pr", "list",
        "--author", GITHUB_AUTHOR,
        "--repo", GITHUB_REPO,
        "--json", "number,title,state,url,updatedAt,headRefName,baseRefName,isDraft,reviewDecision",
        "--limit", str(limit)
    ])
    
    if code != 0:
        print(f"gh pr list failed: {stderr}", file=sys.stderr)
        return []
    
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        print(f"Failed to parse: {stdout}", file=sys.stderr)
        return []


def format_pr_summary(prs: list) -> str:
    """Format PRs for Discord delivery."""
    if not prs:
        return f"No PRs found for {GITHUB_AUTHOR} on {GITHUB_REPO}"
    
    lines = [f"📋 **PR Update** - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"]
    lines.append(f"Found {len(prs)} PR(s):\n")
    
    for pr in prs[:10]:  # Limit to 10 for Discord
        state_emoji = {"OPEN": "🟢", "CLOSED": "🔴", "MERGED": "🟣"}.get(pr.get("state", "").upper(), "⚪")
        draft = " 📝" if pr.get("isDraft") else ""
        review = pr.get("reviewDecision", "")
        review_emoji = " ✅" if review == "APPROVED" else " ⏳" if review == "CHANGES_REQUESTED" else ""
        
        lines.append(
            f"{state_emoji} **#{pr['number']}** {pr['title']}{draft}{review_emoji}\n"
            f"   `{pr['headRefName']}` → `{pr['baseRefName']}`\n"
            f"   {pr['url']}\n"
        )
    
    if len(prs) > 10:
        lines.append(f"\n... and {len(prs) - 10} more PRs")
    
    return "\n".join(lines)


def save_state(data: dict, filename: str = "state.json"):
    """Save state to output directory."""
    (OUTPUT_DIR / filename).write_text(json.dumps(data, indent=2))


def load_state(filename: str = "state.json") -> dict:
    """Load state from output directory."""
    path = OUTPUT_DIR / filename
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            pass
    return {}


def main():
    print(f"[{datetime.utcnow().isoformat()}] Starting agent task...")
    
    # Example: PR monitoring task
    prs = get_prs()
    summary = format_pr_summary(prs)
    
    print(summary)
    
    # Post to Discord if configured
    if DISCORD_WEBHOOK:
        post_to_discord(summary)
    
    # Save state for next run
    save_state({
        "last_run": datetime.utcnow().isoformat(),
        "pr_count": len(prs),
        "prs": {str(p["number"]): p for p in prs}
    })
    
    return 0


if __name__ == "__main__":
    sys.exit(main())