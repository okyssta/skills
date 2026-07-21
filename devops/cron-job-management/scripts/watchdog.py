#!/usr/bin/env python3
"""
Watchdog Template - Script-only cron job (no_agent=True)
Runs a health check and exits with code 0 (OK) or 1 (CRITICAL).
Empty stdout = silent (watchdog pattern).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# ============ CONFIGURATION ============
# Override via environment variables
HEALTH_ENDPOINT = os.getenv("WATCHDOG_HEALTH_ENDPOINT", "http://localhost:8645/health")
CHECK_DISK = os.getenv("WATCHDOG_CHECK_DISK", "1") == "1"
CHECK_MEMORY = os.getenv("WATCHDOG_CHECK_MEMORY", "1") == "1"
DISK_WARNING_PCT = float(os.getenv("WATCHDOG_DISK_WARNING", "80"))
DISK_CRITICAL_PCT = float(os.getenv("WATCHDOG_DISK_CRITICAL", "90"))
MEMORY_WARNING_PCT = float(os.getenv("WATCHDOG_MEM_WARNING", "80"))
MEMORY_CRITICAL_PCT = float(os.getenv("WATCHDOG_MEM_CRITICAL", "90"))

LOG_DIR = Path(os.getenv("WATCHDOG_LOG_DIR", "/root/.hermes/cron/output/watchdog"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"watchdog_{datetime.utcnow().strftime('%Y%m%d')}.log"
# ========================================


def log(message: str):
    """Log to file and stdout."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    line = f"[{timestamp}] {message}"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    # Only print if not in silent mode
    if os.getenv("WATCHDOG_VERBOSE") == "1":
        print(line)


def check_http(endpoint: str) -> tuple[bool, dict]:
    """Check HTTP endpoint health."""
    try:
        req = urllib.request.Request(endpoint, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                try:
                    data = json.loads(resp.read().decode())
                except:
                    data = {"status": resp.status}
                return True, data
            return False, {"status": resp.status}
    except urllib.error.URLError as e:
        return False, {"error": str(e)}
    except Exception as e:
        return False, {"error": str(e)}


def check_disk() -> dict:
    """Check disk space."""
    try:
        stat = os.statvfs("/")
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        used_pct = ((total_gb - free_gb) / total_gb) * 100
        
        status = "healthy"
        if used_pct >= DISK_CRITICAL_PCT:
            status = "critical"
        elif used_pct >= DISK_WARNING_PCT:
            status = "warning"
            
        return {
            "status": status,
            "free_gb": round(free_gb, 1),
            "total_gb": round(total_gb, 1),
            "used_pct": round(used_pct, 1)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


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
            if used_pct >= MEMORY_CRITICAL_PCT:
                status = "critical"
            elif used_pct >= MEMORY_WARNING_PCT:
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
    log("=== Watchdog Check ===")
    
    overall_status = "healthy"
    issues = []
    
    # Check HTTP endpoint
    http_ok, http_data = check_http(HEALTH_ENDPOINT)
    if http_ok:
        log(f"HTTP endpoint: HEALTHY - {http_data}")
    else:
        log(f"HTTP endpoint: UNHEALTHY - {http_data}")
        overall_status = "critical"
        issues.append("HTTP endpoint down")
    
    # Check disk
    if CHECK_DISK:
        disk = check_disk()
        log(f"Disk: {disk['status'].upper()} - {disk.get('free_gb', '?')}GB free ({disk.get('used_pct', '?')}% used)")
        if disk["status"] == "critical":
            overall_status = "critical"
            issues.append("Disk critical")
        elif disk["status"] == "warning" and overall_status == "healthy":
            overall_status = "warning"
            issues.append("Disk warning")
    
    # Check memory
    if CHECK_MEMORY:
        mem = check_memory()
        log(f"Memory: {mem['status'].upper()} - {mem.get('available_gb', '?')}GB available ({mem.get('used_pct', '?')}% used)")
        if mem["status"] == "critical":
            overall_status = "critical"
            issues.append("Memory critical")
        elif mem["status"] == "warning" and overall_status == "healthy":
            overall_status = "warning"
            issues.append("Memory warning")
    
    # Summary
    if issues:
        log(f"Overall: {overall_status.upper()} - {', '.join(issues)}")
    else:
        log("Overall: HEALTHY")
    
    # Exit codes: 0 = OK/Warning (watchdog continues), 1 = Critical (alert)
    if overall_status == "critical":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()