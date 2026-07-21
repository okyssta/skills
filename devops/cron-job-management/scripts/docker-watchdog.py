#!/usr/bin/env python3
"""Docker container watchdog - auto-restarts crashed containers.

Install: Add to ~/.hermes/scripts/, make executable.
Schedule: hermes cron create --script docker-watchdog.py --name "DOCKER-WATCHDOG" --deliver local

Environment:
  WATCHDOG_INTERVAL - Check interval in seconds (default: 60)
  WATCHDOG_CRITICAL - Comma-separated container names to monitor (default: firecrawl-api)
"""

import subprocess, time, os, sys

def get_crashed_containers():
    """Return list of crashed containers matching CRITICAL_CONTAINERS."""
    result = subprocess.run(
        ["docker", "ps", "--filter", "status=exited", "--filter", "status=restarting",
         "--format", "{{.Names}} {{.Status}}"],
        capture_output=True, text=True
    )
    critical = [c.strip() for c in os.getenv("WATCHDOG_CRITICAL", "firecrawl-api").split(",")]
    crashed = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        name = line.split()[0] if line else ""
        for pattern in critical:
            if pattern.strip() and pattern.strip() in name:
                crashed.append(name)
    return crashed

def restart_container(name):
    """Attempt to restart a container, return True on success."""
    result = subprocess.run(["docker", "restart", name], capture_output=True, text=True)
    return result.returncode == 0

def main():
    crashed = get_crashed_containers()
    if not crashed:
        sys.exit(0)  # Silent OK - no problems
    
    for container in crashed:
        if restart_container(container):
            print(f"Restarted {container}")
        else:
            print(f"Failed to restart {container}", file=sys.stderr)

if __name__ == "__main__":
    main()