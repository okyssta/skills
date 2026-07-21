# Fix for Raft Bridge Lock File Issue (BRIDGE_ALREADY_RUNNING)

## Problem
When running Hermes in Raft bridge mode, after an unclean shutdown (crash, force-kill, or restart), attempting to start the gateway fails with:
```
Error: raft agent bridge is already running for this profile/agent/adapter state.
Code: BRIDGE_ALREADY_RUNNING
Next action: Stop the existing bridge or use a different --adapter-instance. Lock: <profile path>/agent-comms-core/<agent-id>/default/bridge.lock
```

Even though no bridge process is actually running, the lock file prevents startup.

## Root Cause
The Raft adapter creates a lock file at `$HERMES_HOME/agent-comms-core/<agent-id>/default/bridge.lock` containing the PID of the bridge process. On unclean shutdown, this lock file is not cleaned up, causing subsequent starts to believe a bridge is still running.

## Solution
Implement stale lock file detection and cleanup in the Raft adapter's `_spawn_bridge` method:

### Implementation Details

1. **Locate the lock file**: Construct the path using the agent ID from the state manager
2. **Check if lock file exists**: If it does, read the PID from the file
3. **Validate the PID**: 
   - If the PID is not a valid number, the lock file is stale
   - If the PID is valid, check if the process is still running using `os.kill(pid, 0)`
4. **Remove stale lock files**: 
   - Delete the lock file if the process doesn't exist or PID is invalid
   - Preserve the lock file if the process is still running (to prevent conflicts)
5. **Log appropriate warnings** for debugging purposes

### Code Implementation
```python
def _spawn_bridge(self, port: int) -> None:
    raft_bin = shutil.which("raft")
    if not raft_bin:
        logger.warning("[raft] raft CLI not found in PATH; bridge not spawned")
        return

    profile = os.environ.get("RAFT_PROFILE", "")
    if not profile:
        logger.warning("[raft] RAFT_PROFILE not set; bridge not spawned")
        return

    # Check for and remove stale lock file
    try:
        from hermes_agent.hermes_state import state_manager
        agent_id = state_manager.agent_id
    except Exception:
        agent_id = None
    
    if agent_id:
        hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
        lock_dir = os.path.join(hermes_home, "agent-comms-core", agent_id, "default")
        lock_file = os.path.join(lock_dir, "bridge.lock")
        
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    try:
                        # Check if process is still alive (signal 0 doesn't kill)
                        os.kill(pid, 0)
                        # Process exists, we will not remove the lock file
                        logger.warning(f"[raft] Lock file {lock_file} exists with PID {pid}, which is still alive. Not removing.")
                    except OSError:
                        # Process does not exist, remove the lock file
                        os.remove(lock_file)
                        logger.warning(f"[raft] Removed stale lock file {lock_file} (PID {pid})")
                else:
                    # Invalid PID in lock file, remove it
                    os.remove(lock_file)
                    logger.warning(f"[raft] Removed lock file {lock_file} with invalid PID {pid_str}")
            except Exception as e:
                logger.warning(f"[raft] Failed to check lock file {lock_file}: {e}")
    
    # Continue with normal bridge spawning...
    endpoint = f"http://{self._host}:{port}{self._path}"
    # ... rest of the method
```

### Verification
1. **Normal operation**: When bridge is running normally, lock file is preserved
2. **Unclean shutdown**: After crash/kill, lock file is removed on next start
3. **Invalid lock file**: Corrupted lock files are cleaned up
4. **Edge cases**: Proper error handling for file I/O and permission issues

### Testing
- Simulate unclean shutdown by killing the bridge process
- Verify lock file is removed on subsequent start
- Confirm bridge starts successfully after cleanup
- Test with running bridge to ensure lock file is preserved

## Related Files
- `plugins/platforms/raft/adapter.py` - Contains the fixed `_spawn_bridge` method
- Issue reference: https://github.com/NousResearch/hermes-agent/issues/59259

## Prevention
This fix ensures automatic recovery from unclean shutdowns without requiring manual intervention to delete lock files.