#!/usr/bin/env python3
"""
Health Check Template - System/service health monitoring
For CRM-HEALTH-REPORT style cron jobs.
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path


# ============ CONFIGURATION ============
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
OUTPUT_DIR = Path(os.getenv("HEALTH_OUTPUT_DIR", "/opt/firecrawl/reports"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ========================================


def check_firecrawl() -> dict:
    """Check Firecrawl API health."""
    if not FIRECRAWL_API_URL:
        return {"service": "Firecrawl", "status": "not_configured", "details": "API key not set"}
    
    try:
        resp = requests.get(
            "https://api.firecrawl.dev/v1/health",
            headers={},
            timeout=10
        )
        return {
            "service": "Firecrawl",
            "status": "healthy" if resp.status_code == 200 else "degraded",
            "details": resp.json() if resp.status_code == 200 else f"HTTP {resp.status_code}"
        }
    except Exception as e:
        return {"service": "Firecrawl", "status": "unhealthy", "details": str(e)}


def check_github() -> dict:
    """Check GitHub API health."""
    try:
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
        resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            remaining = data.get("resources", {}).get("core", {}).get("remaining", 0)
            return {
                "service": "GitHub API",
                "status": "healthy" if remaining > 100 else "rate_limited",
                "details": f"Rate limit remaining: {remaining}"
            }
        return {"service": "GitHub API", "status": "degraded", "details": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"service": "GitHub API", "status": "unhealthy", "details": str(e)}


def check_discord() -> dict:
    """Check Discord webhook."""
    if not DISCORD_WEBHOOK:
        return {"service": "Discord Webhook", "status": "not_configured", "details": "Webhook URL not set"}
    
    try:
        resp = requests.post(
            DISCORD_WEBHOOK,
            json={"content": "🔍 Health check"},
            timeout=10
        )
        return {
            "service": "Discord Webhook",
            "status": "healthy" if resp.status_code == 204 else "degraded",
            "details": f"HTTP {resp.status_code}"
        }
    except Exception as e:
        return {"service": "Discord Webhook", "status": "unhealthy", "details": str(e)}


def check_disk() -> dict:
    """Check disk space."""
    try:
        stat = os.statvfs("/")
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        used_pct = ((total_gb - free_gb) / total_gb) * 100
        
        status = "healthy"
        if used_pct > 90:
            status = "critical"
        elif used_pct > 80:
            status = "warning"
            
        return {
            "service": "Disk Space",
            "status": status,
            "details": f"{free_gb:.1f}GB free of {total_gb:.1f}GB ({used_pct:.1f}% used)"
        }
    except Exception as e:
        return {"service": "Disk Space", "status": "error", "details": str(e)}


def check_memory() -> dict:
    """Check memory usage."""
    try:
        with open("/proc/meminfo") as f:
            meminfo = f.read()
        
        mem_total = 0
        mem_available = 0
        for line in meminfo.split("\n"):
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1]) * 1024
            elif line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1]) * 1024
        
        if mem_total > 0:
            used_pct = ((mem_total - mem_available) / mem_total) * 100
            status = "healthy"
            if used_pct > 90:
                status = "critical"
            elif used_pct > 80:
                status = "warning"
            return {
                "service": "Memory",
                "status": status,
                "details": f"{mem_available/1024**3:.1f}GB available of {mem_total/1024**3:.1f}GB ({used_pct:.1f}% used)"
            }
    except Exception as e:
        return {"service": "Memory", "status": "error", "details": str(e)}
    
    return {"service": "Memory", "status": "unknown", "details": "Could not read meminfo"}


def check_process(name: str, pattern: str) -> dict:
    """Check if process is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return {
            "service": name,
            "status": "healthy" if pids else "not_running",
            "details": f"PIDs: {', '.join(pids)}" if pids else "No processes found"
        }
    except Exception as e:
        return {"service": name, "status": "error", "details": str(e)}


def main():
    print(f"=== Health Report - {datetime.utcnow().isoformat()}Z ===\n")
    
    checks = [
        check_firecrawl(),
        check_github(),
        check_discord(),
        check_disk(),
        check_memory(),
        check_process("Hermes Agent", "hermes"),
        check_process("Hermes Gateway", "gateway"),
    ]
    
    healthy = 0
    warnings = 0
    critical = 0
    
    for check in checks:
        icon = {
            "healthy": "✅", "warning": "⚠️", "critical": "🔴",
            "degraded": "🟡", "rate_limited": "🟡", "not_configured": "⚪",
            "not_running": "🔴", "unhealthy": "🔴", "error": "❌", "unknown": "❓"
        }.get(check["status"], "❓")
        
        print(f"{icon} {check['service']}: {check['status'].upper()}")
        print(f"   {check['details']}\n")
        
        if check["status"] == "healthy":
            healthy += 1
        elif check["status"] in ("warning", "degraded", "rate_limited", "not_configured"):
            warnings += 1
        elif check["status"] in ("critical", "unhealthy", "not_running", "error"):
            critical += 1
    
    print("=" * 50)
    print(f"Summary: {healthy} healthy, {warnings} warnings, {critical} critical")
    
    # Save report
    report_file = OUTPUT_DIR / f"health_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": {"healthy": healthy, "warnings": warnings, "critical": critical},
        "checks": checks
    }, indent=2))
    
    print(f"\nReport saved to {report_file}")
    
    return 1 if critical > 0 else 0


if __name__ == "__main__":
    sys.exit(main())