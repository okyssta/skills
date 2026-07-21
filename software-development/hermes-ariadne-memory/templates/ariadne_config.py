# Ariadne Configuration Template

Copy this file and customize for your project. Save as `ariadne_config.py` or integrate into your application.

```python
from arriadne import AriadneConfig, AriadneMemory

# =============================================================================
# CONFIGURATION PRESETS
# =============================================================================

# Minimal: Keyword search only (works everywhere, no torch)
MINIMAL_CONFIG = AriadneConfig(
    db_path="memory.db",
    # No embedding_dim, no embedder = keyword/FTS5 only
)

# Balanced: Semantic search with good default embedder
# Requires: pip install "ariadne-memory[embeddings]"
BALANCED_CONFIG = AriadneConfig(
    db_path="memory.db",
    embedding_dim=384,  # all-MiniLM-L6-v2 dimension
    faiss_type="auto",  # Auto Flat -> IVF at scale
    dedup_threshold=0.8,
    retention_half_life=86400,  # 1 day
)

# High-Recall: Larger embedder, more aggressive retention
# Requires: pip install "ariadne-memory[embeddings]"
HIGH_RECALL_CONFIG = AriadneConfig(
    db_path="memory.db",
    embedding_dim=768,  # all-mpnet-base-v2 dimension
    faiss_type="auto",
    dedup_threshold=0.75,  # More aggressive dedup
    retention_half_life=604800,  # 1 week
    retention_growth_factor=2.0,
    max_retention_strength=20.0,
)

# High-Precision: Strict dedup, fast eviction
HIGH_PRECISION_CONFIG = AriadneConfig(
    db_path="memory.db",
    embedding_dim=384,
    faiss_type="flat_ip",  # Force exact search
    dedup_threshold=0.9,   # Very strict dedup
    retention_half_life=43200,  # 12 hours
    eviction_threshold=0.3,     # Aggressive eviction
)

# Production: Balanced with custom paths
PRODUCTION_CONFIG = AriadneConfig(
    db_path="/var/lib/ariadne/memory.db",
    embedding_dim=384,
    faiss_type="auto",
    dedup_threshold=0.8,
    retention_half_life=86400,
    ivf_threshold=50000,  # Upgrade to IVF at 50k vectors
    nlist=1024,           # IVF clusters
)

# =============================================================================
# EMBEDDER SETUP
# =============================================================================

# Option 1: SentenceTransformer (recommended)
def get_sentence_transformer_embedder(model_name="all-MiniLM-L6-v2"):
    from arriadne.embeddings import SentenceTransformerEmbedder
    return SentenceTransformerEmbedder(model_name)

# Option 2: Custom embedder (any callable returning list[float] / np.array)
def get_custom_embedder(embed_fn, dim):
    from arriadne.embeddings import BaseEmbedder
    import numpy as np
    
    class CustomEmbedder(BaseEmbedder):
        def __init__(self, fn, dimension):
            self._fn = fn
            self._dim = dimension
        
        @property
        def dim(self):
            return self._dim
        
        def embed(self, texts):
            return [np.array(self._fn(t), dtype=np.float32) for t in texts]
        
        def embed_query(self, text):
            return np.array(self._fn(text), dtype=np.float32)
    
    return CustomEmbedder(embed_fn, dim)

# Option 3: No embedder (keyword only)
NO_EMBEDDER = None

# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_memory(config_preset=BALANCED_CONFIG, embedder=None):
    """
    Create an AriadneMemory instance with the given config and embedder.
    
    Args:
        config_preset: One of the CONFIG presets above, or custom AriadneConfig
        embedder: Embedder instance, or None for keyword-only
    
    Returns:
        AriadneMemory instance
    """
    if embedder is not None and config_preset.embedding_dim is None:
        # Auto-set dimension from embedder
        config_preset.embedding_dim = embedder.dim
    
    return AriadneMemory(config=config_preset, embedder=embedder)

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

# # Quick start - keyword only
# mem = create_memory(MINIMAL_CONFIG)
# mem.remember("Important fact")

# # Semantic search with default embedder
# embedder = get_sentence_transformer_embedder()
# mem = create_memory(BALANCED_CONFIG, embedder)

# # Custom embedder (e.g., from OpenAI API)
# import openai
# def openai_embed(text):
#     response = openai.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return response.data[0].embedding
# 
# embedder = get_custom_embedder(openai_embed, 1536)
# mem = create_memory(
#     AriadneConfig(db_path="memory.db", embedding_dim=1536),
#     embedder
# )

# # Always close when done
# mem.close()
```

## Quick Config Selection

| Use Case | Config | Embedder |
|----------|--------|----------|
| Quick test, ARM server, no GPU | `MINIMAL_CONFIG` | `None` |
| General purpose semantic memory | `BALANCED_CONFIG` | `all-MiniLM-L6-v2` |
| Long-term knowledge base | `HIGH_RECALL_CONFIG` | `all-mpnet-base-v2` |
| High-throughput, strict accuracy | `HIGH_PRECISION_CONFIG` | `all-MiniLM-L6-v2` |
| Production deployment | `PRODUCTION_CONFIG` | `all-MiniLM-L6-v2` |

## Embedder Models Quick Reference

| Model | Dim | Speed | Quality | Use Case |
|-------|-----|-------|---------|----------|
| `all-MiniLM-L6-v2` | 384 | Fast | Good | Default, balanced |
| `all-MiniLM-L12-v2` | 384 | Medium | Better | Higher quality |
| `all-mpnet-base-v2` | 768 | Slow | Best | Maximum quality |
| `text-embedding-3-small` | 1536 | API | Excellent | OpenAI (paid) |
| `text-embedding-3-large` | 3072 | API | Best | OpenAI (paid) |
| `bge-small-en-v1.5` | 384 | Fast | Good | BGE family |
| `bge-base-en-v1.5` | 768 | Medium | Better | BGE family |
| `bge-large-en-v1.5` | 1024 | Slow | Best | BGE family |

Install BGE models: `pip install sentence-transformers` (included in hub)