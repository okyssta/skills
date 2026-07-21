#!/usr/bin/env python3
"""
Verification script for Ariadne memory provider installation.
Run this to verify Ariadne is properly installed and configured for Hermes.
"""

import subprocess
import sys
import os

def run_cmd(cmd):
    """Run command and return (success, output)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)

def check_ariadne_core():
    """Check if ariadne-memory package is installed."""
    success, out, err = run_cmd("python3 -c \"import arriadne; print(arriadne.__version__)\"")
    if success:
        print(f"✓ ariadne-memory installed: {out}")
        return True
    else:
        print(f"✗ ariadne-memory not installed: {err}")
        return False

def check_dependencies():
    """Check core dependencies."""
    deps = ["faiss", "numpy", "datasketch"]
    all_ok = True
    for dep in deps:
        success, out, err = run_cmd(f"python3 -c \"import {dep}; print({dep}.__version__ if hasattr({dep}, '__version__') else 'ok')\"")
        if success:
            print(f"  ✓ {dep}: {out}")
        else:
            print(f"  ✗ {dep}: missing")
            all_ok = False
    return all_ok

def check_embeddings():
    """Check if embeddings work (optional)."""
    success, out, err = run_cmd("python3 -c \"from arriadne.embeddings import SentenceTransformerEmbedder; print('embeddings available')\"")
    if success:
        print("✓ Embeddings support available")
        return True
    else:
        print(f"⚠ Embeddings not available (keyword-only mode): {err[:80]}")
        return False

def check_plugin():
    """Check if Hermes plugin is installed."""
    plugin_dir = os.path.expanduser("~/.hermes/plugins/ariadne")
    if os.path.exists(plugin_dir):
        files = os.listdir(plugin_dir)
        print(f"✓ Plugin directory exists: {plugin_dir}")
        print(f"  Files: {files}")
        return True
    else:
        print(f"✗ Plugin directory not found: {plugin_dir}")
        return False

def check_plugin_enabled():
    """Check if plugin is enabled in Hermes."""
    success, out, err = run_cmd("hermes plugins list --plain 2>/dev/null | grep ariadne")
    if success and "enabled" in out:
        print(f"✓ Plugin enabled: {out.strip()}")
        return True
    else:
        print(f"✗ Plugin not enabled: {out or err}")
        return False

def check_config():
    """Check if memory.provider is set to ariadne."""
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            content = f.read()
        if "provider: ariadne" in content:
            print("✓ memory.provider = ariadne in config.yaml")
            return True
        else:
            print("✗ memory.provider not set to ariadne in config.yaml")
            return False
    else:
        print("✗ config.yaml not found")
        return False

def test_keyword_search():
    """Test basic keyword search functionality."""
    import tempfile
    import shutil
    
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    
    try:
        # Test import and basic operations
        from arriadne import AriadneMemory
        
        mem = AriadneMemory(db_path=db_path)
        mem.remember("Test memory for verification", importance=0.5)
        results = mem.recall("verification", k=5)
        mem.close()
        
        if len(results) == 1 and "verification" in results[0]["content"].lower():
            print("✓ Keyword search working")
            return True
        else:
            print(f"✗ Keyword search failed: got {len(results)} results")
            return False
    except Exception as e:
        print(f"✗ Keyword search error: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_knowledge_graph():
    """Test knowledge graph functionality."""
    import tempfile
    import shutil
    
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    
    try:
        from arriadne import AriadneMemory
        
        mem = AriadneMemory(db_path=db_path)
        mem.add_edge("A", "B", edge_type="relates_to")
        mem.add_edge("B", "C", edge_type="relates_to")
        graph = mem.graph("A", hops=2)
        mem.close()
        
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        if "A" in nodes and "B" in nodes and "C" in nodes and len(edges) == 2:
            print("✓ Knowledge graph working")
            return True
        else:
            print(f"✗ Knowledge graph failed: nodes={nodes}, edges={edges}")
            return False
    except Exception as e:
        print(f"✗ Knowledge graph error: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def main():
    print("=" * 60)
    print("Ariadne Memory Provider Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Core Package", check_ariadne_core),
        ("Dependencies", check_dependencies),
        ("Embeddings (optional)", check_embeddings),
        ("Hermes Plugin", check_plugin),
        ("Plugin Enabled", check_plugin_enabled),
        ("Config Set", check_config),
        ("Keyword Search", test_keyword_search),
        ("Knowledge Graph", test_knowledge_graph),
    ]
    
    results = {}
    for name, check in checks:
        print(f"\n[{name}]")
        results[name] = check()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    critical = ["Core Package", "Dependencies", "Hermes Plugin", "Plugin Enabled", "Config Set"]
    optional = ["Embeddings (optional)"]
    functional = ["Keyword Search", "Knowledge Graph"]
    
    all_critical = all(results.get(c, False) for c in critical)
    all_functional = all(results.get(f, False) for f in functional)
    
    for name in critical + optional + functional:
        status = "PASS" if results.get(name, False) else "FAIL"
        marker = "✓" if results.get(name, False) else "✗"
        print(f"  {marker} {name}: {status}")
    
    print()
    if all_critical and all_functional:
        print("✓ All critical checks passed! Ariadne is ready for use.")
        return 0
    elif all_critical:
        print("⚠ Critical checks passed but some functional tests failed.")
        print("  Keyword/graph features may not work. Check errors above.")
        return 1
    else:
        print("✗ Critical checks failed. Fix the issues above before using Ariadne.")
        return 2

if __name__ == "__main__":
    sys.exit(main())