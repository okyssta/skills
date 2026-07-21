# Ariadne Memory Provider - Troubleshooting & Platform Notes

## ARM64 / Apple Silicon / ARM Server Issues

**Problem**: `sentence-transformers` pulls in `torch` which has compatibility issues on ARM:
- Bus errors on import (core dumped)
- ONNX Runtime / CUDA compatibility problems
- Missing wheels for some dependencies

**Root Cause**: PyTorch's ARM builds have issues with `tokenizers` (Rust) and ONNX Runtime on certain ARM kernels.

**Workarounds**:

### 1. Keyword-Only Mode (Recommended for ARM)
```python
# No embedder = FTS5 BM25 keyword search only (still fast!)
from arriadne import AriadneMemory
mem = AriadneMemory(db_path="memory.db")
mem.remember("deploy script lives in infra/deploy.sh")
results = mem.recall("deploy script", k=5)
```

### 2. Install CPU-Only Torch First
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
pip install "ariadne-memory[embeddings]"
```

### 3. Use Pre-Built Wheels (if available)
```bash
pip install --prefer-binary "ariadne-memory[embeddings]"
```

### 4. Docker Alternative
```dockerfile
FROM python:3.11-slim
RUN pip install "ariadne-memory[embeddings]"
# Works in x86_64 containers even on ARM hosts
```

## Plugin Issues

### Plugin Not Found
```
✗ Plugin directory not found: ~/.hermes/plugins/ariadne
```
**Fix**:
```bash
git clone https://github.com/kyssta-exe/Ariadne.git /tmp/ariadne-repo
cp -r /tmp/ariadne-repo/plugin ~/.hermes/plugins/ariadne
```

### Plugin Not Enabled
```
✗ Plugin not enabled
```
**Fix**:
```bash
hermes plugins enable ariadne
# Restart session: /reset (CLI) or /restart (Gateway)
```

### Config Not Set
```
✗ memory.provider not set to ariadne in config.yaml
```
**Fix**:
```bash
hermes config set memory.provider ariadne
# Or edit ~/.hermes/config.yaml manually
```

## Database Issues

### Database Locked
```
sqlite3.OperationalError: database is locked
```
**Causes**:
- Multiple Hermes processes using same DB
- WAL mode not working properly

**Fixes**:
```python
# Ensure WAL mode (default in Ariadne)
import sqlite3
conn = sqlite3.connect("memory.db")
conn.execute("PRAGMA journal_mode=WAL")
```

Or use separate DB paths per process:
```python
# Each agent gets its own DB
mem = AriadneMemory(db_path=f"memory-{os.getpid()}.db")
```

### Migration Needed
```
ariadne.storage: Database version X, current Y, migrating...
```
Normal on version upgrades. Let it complete.

## Performance Notes

### FAISS Index Auto-Upgrade
- Starts as `IndexFlatIP` (exact, O(N))
- Auto-upgrades to `IndexIVFFlat` (approximate, O(log N)) at `ivf_threshold` (default 10000)
- Rebuilt from DB on every open — never drifts

### Memory Retention Tuning
```python
config = AriadneConfig(
    retention_half_life=86400,      # 1 day default
    retention_growth_factor=1.5,    # Strengthen on recall
    max_retention_strength=10.0,    # Cap
)
```

### Deduplication Threshold
```python
config = AriadneConfig(
    dedup_threshold=0.8,   # MinHash Jaccard similarity (0-1)
)
```

## Common Errors

### ImportError: No module named 'transformers'
```bash
pip install transformers huggingface-hub torch scikit-learn
```

### ModuleNotFoundError: No module named 'faiss'
```bash
pip install faiss-cpu
```

### torch not compiled with CUDA
Not an error — FAISS CPU works fine. Only matters if you want GPU acceleration.

## Verification Checklist

Run the verification script:
```bash
python ~/.hermes/skills/software-development/hermes-ariadne-memory/scripts/verify-ariadne.py
```

Expected output for working keyword-only setup:
```
[Core Package] ✓ ariadne-memory installed: 0.11.0
[Dependencies] ✓ faiss: 1.14.3, numpy: 2.4.6, datasketch: 1.10.0
[Embeddings (optional)] ⚠ Embeddings not available (keyword-only mode)
[Hermes Plugin] ✓ Plugin directory exists
[Plugin Enabled] ✓ Plugin enabled: enabled  user  0.1.2  ariadne
[Config Set] ✓ memory.provider = ariadne in config.yaml
[Keyword Search] ✓ Keyword search working
[Knowledge Graph] ✓ Knowledge graph working

✓ All critical checks passed! Ariadne is ready for use.
```

## Links

- [Full Documentation](https://ariadne.mantes.net)
- [Hermes Integration Guide](https://ariadne.mantes.net/guide/hermes)
- [API Reference](https://ariadne.mantes.net/api/)
- [Benchmarks](https://ariadne.mantes.net/benchmarks)
- [GitHub Issues](https://github.com/kyssta-exe/Ariadne/issues)