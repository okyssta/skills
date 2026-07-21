#!/usr/bin/env python3
"""
Watchdog Script Template - Script-only cron job (no_agent=True)
Runs health checks and exits with appropriate code for cron watchdog pattern.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.hermes/.env')

# Configuration
WEBHOOK_PORT = int(os.getenv("P1_WEBHOOK_PORT", "8645"))
HEALTH_ENDPOINT = f"http://localhost:{WEBHOOK_PORT}/health"
LOG_PATH = Path(os.getenv("WATCHDOG_LOG", "/root/.hermes/cron/output/watchdog/watchdog.log"))

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_event(message: str):
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_line = f"[{timestamp}] {message}\n"
    with open(LOG_PATH, "a") as f:
        f.write(log_line)
    print(log_line.strip())


def check_webhook_server():
    """Check if the webhook server is responding."""
    try:
        req = urllib.request.Request(HEALTH_ENDPOINT, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return True, data
            return False, {"status": resp.status}
    except urllib.error.URLError as e:
        return False, {"error": str(e)}
    except Exception as e:
        return False, {"error": str(e)}


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
            "status": status,
            "free_gb": round(free_gb, 1),
            "total_gb": round(total_gb, 1),
            "used_pct": round(used_pct, 1)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


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
                "status": status,
                "available_gb": round(mem_available / (1024**3), 1),
                "total_gb": round(mem_total / (1024**3), 1),
                "used_pct": round(used_pct, 1)
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}
    
    return {"status": "unknown"}


def main():
    log_event("=== Watchdog Check ===")
    
    # Check webhook server
    webhook_ok, webhook_data = check_webhook_server()
    
    if webhook_ok:
        log_event(f"Webhook server: HEALTHY - {webhook_data}")
        webhook_status = "healthy"
    else:
        log_event(f"Webhook server: UNHEALTHY - {webhook_data}")
        webhook_status = "unhealthy"
    
    # Check system resources
    disk = check_disk_space()
    mem = check_memory()
    
    log_event(f"Disk: {disk['status'].upper()} - {disk.get('free_gb', '?')}GB free ({disk.get('used_pct', '?')}% used)")
    log_event(f"Memory: {mem['status'].upper()} - {mem.get('available_gb', '?')}GB available ({mem.get('used_pct', '?')}% used)")
    
    # Overall status
    overall = "healthy"
    if webhook_status == "unhealthy":
        overall = "critical"
    elif disk["status"] in ("warning", "critical") or mem["status"] in ("warning", "critical"):
        overall = "warning"
    
    log_event(f"Overall status: {overall.upper()}")
    
    # Exit with error code if critical
    if overall == "critical":
        log_event("CRITICAL: Webhook server down or resource exhaustion")
        sys.exit(1)
    elif overall == "warning":
        log_event("WARNING: Some resources under pressure")
        sys.exit(0)
    else:
        log_event("OK: All systems healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()