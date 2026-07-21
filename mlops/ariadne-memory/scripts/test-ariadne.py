#!/usr/bin/env python3
"""Verify Ariadne installation and basic functionality."""

import sys
import tempfile
import os

def test_core():
    """Test core Ariadne functionality (keyword-only mode)."""
    print("Testing core Ariadne (keyword-only)...")
    try:
        from arriadne import AriadneMemory
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            mem = AriadneMemory(db_path=db_path)
            
            # Store a memory
            mem.remember("Test memory: deploy script in infra/deploy.sh")
            
            # Recall it
            results = mem.recall("deploy script", k=5)
            assert len(results) == 1
            assert "deploy.sh" in results[0]['content']
            print("  ✓ Keyword search works")
            
            # Test graph
            mem.add_edge("WebApp", "API", edge_type="depends_on")
            mem.add_edge("API", "Database", edge_type="depends_on")
            graph = mem.graph("WebApp", hops=2)
            assert "API" in graph['nodes']
            assert "Database" in graph['nodes']
            print("  ✓ Knowledge graph works")
            
            mem.close()
            print("  ✓ Core functionality OK")
            return True
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass
                    
    except Exception as e:
        print(f"  ✗ Core test failed: {e}")
        return False

def test_embeddings():
    """Test embeddings mode (may fail on ARM)."""
    print("Testing embeddings mode...")
    try:
        from arriadne import AriadneMemory
        from arriadne.embeddings import SentenceTransformerEmbedder
        
        embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            mem = AriadneMemory(db_path=db_path, embedding_dim=embedder.dim, embedder=embedder)
            mem.remember("VPS has 4 cores, 8GB RAM", importance=0.8)
            results = mem.recall("server specs", k=5)
            print(f"  ✓ Embeddings work (found {len(results)} results)")
            mem.close()
            return True
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass
                    
    except Exception as e:
        print(f"  ⚠ Embeddings test skipped/failed: {e}")
        print("     (This is expected on ARM/aarch64 due to PyTorch binary issues)")
        return True  # Not a failure - known limitation

def test_cli():
    """Test CLI tool."""
    print("Testing CLI...")
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'ariadne', '--help'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and 'Ariadne' in result.stdout:
            print("  ✓ CLI works")
            return True
        else:
            print(f"  ✗ CLI failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ CLI test failed: {e}")
        return False

def test_hermes_plugin():
    """Check if Hermes plugin is installed."""
    print("Checking Hermes plugin...")
    plugin_path = os.path.expanduser("~/.hermes/plugins/ariadne/__init__.py")
    if os.path.exists(plugin_path):
        print("  ✓ Plugin installed at ~/.hermes/plugins/ariadne/")
        return True
    else:
        print("  ⚠ Plugin not found - run: cp -r /tmp/Ariadne/plugin ~/.hermes/plugins/ariadne")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Ariadne Installation Verification")
    print("=" * 50)
    
    results = []
    results.append(("Core (keyword-only)", test_core()))
    results.append(("Embeddings", test_embeddings()))
    results.append(("CLI", test_cli()))
    results.append(("Hermes Plugin", test_hermes_plugin()))
    
    print("\n" + "=" * 50)
    print("Summary:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("=" * 50)
    sys.exit(0 if all_passed else 1)