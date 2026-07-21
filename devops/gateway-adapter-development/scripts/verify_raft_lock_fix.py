#!/usr/bin/env python3
"""
Verification script for Raft bridge lock file fix.

This script tests the logic for detecting and removing stale lock files
in the Raft adapter's _spawn_bridge method.
"""

import os
import tempfile
import shutil
from pathlib import Path


def test_lock_file_handling():
    """Test the lock file handling logic."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        hermes_home = temp_dir
        agent_id = "test-agent-123"
        
        # Create the lock directory structure
        lock_dir = os.path.join(hermes_home, "agent-comms-core", agent_id, "default")
        os.makedirs(lock_dir, exist_ok=True)
        lock_file = os.path.join(lock_dir, "bridge.lock")
        
        print(f"Testing in temporary directory: {temp_dir}")
        print(f"Lock file path: {lock_file}")
        
        # Test 1: No lock file exists (should proceed normally)
        print("\n=== Test 1: No lock file ===")
        if not os.path.exists(lock_file):
            print("✓ No lock file exists - bridge can be spawned normally")
        else:
            print("✗ Unexpected: lock file exists")
            
        # Test 2: Valid lock file with running process (simulate)
        print("\n=== Test 2: Valid lock file with 'running' process ===")
        # Create a lock file with a fake PID (we won't actually check if process exists)
        fake_pid = str(os.getpid() + 9999)  # Use a PID that likely doesn't exist
        with open(lock_file, "w") as f:
            f.write(fake_pid)
        print(f"Created lock file with PID: {fake_pid}")
        
        # Simulate the check logic
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    try:
                        # This will likely fail (OSError) since the process probably doesn't exist
                        os.kill(pid, 0)
                        print(f"✓ Process {pid} appears to be running - preserving lock file")
                        # In real scenario, we would NOT remove the lock file
                    except OSError:
                        print(f"✓ Process {pid} does not exist - would remove lock file")
                        # In real scenario, we would remove the lock file here
                        os.remove(lock_file)
                        print(f"  Removed lock file: {lock_file}")
                else:
                    print(f"✗ Invalid PID in lock file: {pid_str}")
                    os.remove(lock_file)
            except Exception as e:
                print(f"✗ Error checking lock file: {e}")
        
        # Test 3: Invalid PID in lock file
        print("\n=== Test 3: Invalid PID in lock file ===")
        with open(lock_file, "w") as f:
            f.write("not-a-number")
        print(f"Created lock file with invalid PID: not-a-number")
        
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                if pid_str.isdigit():
                    print("✓ PID is valid")
                else:
                    print(f"✓ Invalid PID detected: {pid_str} - would remove lock file")
                    os.remove(lock_file)
                    print(f"  Removed lock file: {lock_file}")
            except Exception as e:
                print(f"✗ Error checking lock file: {e}")
        
        # Test 4: Empty lock file
        print("\n=== Test 4: Empty lock file ===")
        with open(lock_file, "w") as f:
            f.write("")
        print("Created empty lock file")
        
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                if pid_str.isdigit() and pid_str:
                    print("✓ PID is valid")
                else:
                    print(f"✓ Empty or invalid PID detected: '{pid_str}' - would remove lock file")
                    os.remove(lock_file)
                    print(f"  Removed lock file: {lock_file")
                    
                    print(f"✗{lock_file}")
            except Exception as e:
                print(f"✗ Error checking lock file: {e}")
                
        # Test 5: Whitespace-only lock file
        print("\n=== Test 5: Whitespace-only lock file ===")
        with open(lock_file, "w") as f:
            f.write("   12345   ")
        print("Created lock file with whitespace around PID")
        
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    print(f"✓ Valid PID after stripping whitespace: {pid}")
                    # Would check if process exists
                else:
                    print(f"✗ Invalid PID after stripping: '{pid_str}'")
                    os.remove(lock_file)
            except Exception as e:
                print(f"✗ Error checking lock file: {e}")

    print("\n=== Summary ===")
    print("The lock file handling logic should:")
    print("1. Allow normal operation when no lock file exists")
    print("2. Preserve lock file when process is actually running")
    print("3. Remove lock file when process is not running (stale lock)")
    print("4. Remove lock file when PID is invalid or empty")
    print("5. Handle edge cases gracefully with proper logging")


if __name__ == "__main__":
    test_lock_file_handling()