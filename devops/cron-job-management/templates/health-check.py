#!/usr/bin/env python3
"""
Health Check Template - System monitoring with Discord webhook
Checks multiple services and reports status via Discord.
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.hermes/.env')

# Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "«redacted:fc-…»")
REPORT_DIR = Path(os.getenv("HEALTH_REPORT_DIR", "/opt/firecrawl/reports"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def check_firecrawl_health():
    """Check Firecrawl service health."""
    try:
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"url": "https://example.com", "formats": ["markdown"]},
            timeout=10
        )
        return {
            "service": "Firecrawl",
            "status": "healthy" if response.status_code == 200 else "degraded",
            "details": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "service": "Firecrawl",
            "status": "unhealthy",
            "details": str(e)
        }


def check_github_health():
    """Check GitHub API health."""
    try:
        response = requests.get("https://api.github.com/rate_limit", timeout=10)
        if response.status_code == 200:
            data = response.json()
            remaining = data.get("resources", {}).get("core", {}).get("remaining", 0)
            return {
                "service": "GitHub API",
                "status": "healthy" if remaining > 100 else "rate_limited",
                "details": f"Rate limit remaining: {remaining}"
            }
        return {
            "service": "GitHub API",
            "status": "degraded",
            "details": f"Status code: {response.status_code}"
        }
    except Exception as e:
        return {
            "service": "GitHub API",
            "status": "unhealthy",
            "details": str(e)
        }


def check_discord_webhook():
    """Check Discord webhook connectivity."""
    if not DISCORD_WEBHOOK_URL:
        return {
            "service": "Discord Webhook",
            "status": "not_configured",
            "details": "DISCORD_WEBHOOK_URL not set"
        }
    
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": "🔍 Health Check - Webhook test"},
            timeout=10
        )
        return {
            "service": "Discord Webhook",
            "status": "healthy" if response.status_code == 204 else "degraded",
            "details": f"Status: {response.status_code}"
        }
    except Exception as e:
        return {
            "service": "Discord Webhook",
            "status": "unhealthy",
            "details": str(e)
        }


def check_disk_space():
    """Check available disk space."""
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
        return {
            "service": "Disk Space",
            "status": "unknown",
            "details": str(e)
        }


def check_memory():
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
        return {
            "service": "Memory",
            "status": "unknown",
            "details": str(e)
        }
    
    return {"service": "Memory", "status": "unknown", "details": "Could not read meminfo"}


def check_processes(process_names):
    """Check if specific processes are running."""
    checks = []
    for name in process_names:
        try:
            result = subprocess.run(
                ["pgrep", "-f", name],
                capture_output=True,
                text=True
            )
            pids = result.stdout.strip().split("\n") if result.stdout.strip() else []
            checks.append({
                "service": name,
                "status": "healthy" if pids else "not_running",
                "details": f"PIDs: {', '.join(pids)}" if pids else f"No {name} processes found"
            })
        except Exception as e:
            checks.append({
                "service": name,
                "status": "unknown",
                "details": str(e)
            })
    return checks


def main():
    print(f"=== Health Report - {datetime.now().isoformat()} ===\n")
    
    checks = []
    
    # External services
    checks.append(check_firecrawl_health())
    checks.append(check_github_health())
    checks.append(check_discord_webhook())
    
    # System resources
    checks.append(check_disk_space())
    checks.append(check_memory())
    
    # Process checks
    process_names = ["hermes", "gateway"]
    checks.extend(check_processes(process_names))
    
    # Print results
    healthy = 0
    warning = 0
    critical = 0
    
    for check in checks:
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "🔴",
            "degraded": "🟡",
            "rate_limited": "🟡",
            "not_configured": "⚪",
            "not_running": "🔴",
            "unknown": "❓"
        }.get(check["status"], "❓")
        
        print(f"{status_icon} {check['service']}: {check['status'].upper()}")
        print(f"   Details: {check['details']}\n")
        
        if check["status"] == "healthy":
            healthy += 1
        elif check["status"] in ("warning", "degraded", "rate_limited", "not_configured"):
            warning += 1
        elif check["status"] in ("critical", "unhealthy", "not_running"):
            critical += 1
    
    print("=" * 50)
    print(f"Summary: {healthy} healthy, {warning} warnings, {critical} critical")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {"healthy": healthy, "warning": warning, "critical": critical},
        "checks": checks
    }
    report_file = REPORT_DIR / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(report, indent=2))
    
    print(f"\nReport saved to {report_file}")
    
    # Exit with error code if critical issues
    return 1 if critical > 0 else 0


if __name__ == "__main__":
    sys.exit(main())